import logging
import queue
import threading
import random

import lib.constants as cte
from lib.constants import Action
from lib.packet import Packet
from lib.window import Window
from lib.priority_queue import PQueue as PriorityQueue


class UDPConnection:

    def __init__(self, socket, address, action_queue, window_size):
        self.logger = logging.getLogger(__name__)
        self.socket = socket
        self.address = address

        self.in_packet_queue = PriorityQueue()  # queue para los paquetes entrantes
        self.out_packet_queue = PriorityQueue()  # queue para los paquetes salientes
        self.action_queue = action_queue  # queue para avisar al cliente/servidor de acciones que deba realizar
        self.delivery_queue = queue.Queue()  # queue para entregarle paquetes en orden al cliente/servidor en caso de download/upload

        self.threads = []
        self.window_size = window_size
        self.window = Window(window_size, socket, address)
        self.seq_num = 0  # sequence number para asignar a paquetes salientes
        self.ack_num = None  # ack number para asignar a paquete ack saliente
        self.expd_seq_num = 0  # sequence number esperado de prox paquete entrante

        self.waiting_synack = False # solo se setea true en la connection del cliente download
        self.sending_to_client = False
        self.recving_from_client = False

    # data: bytes paquete entrante
    def enqueue_in_data(self, data: bytes):
        p = Packet.from_bytes(data)
        self.in_packet_queue.put_low(p)

    # data: bytes payload paquete
    def enqueue_out_data(self, data: bytes, upload=False, download=False, fin=False):
        if upload:
            p = Packet(self.seq_num, self.ack_num, 0, 0, 1, 0, 1, data)
        elif download:
            p = Packet(self.seq_num, self.ack_num, 0, 0, 1, 0, 0, data)
            self.waiting_synack = True
        elif fin:
            p = Packet(self.seq_num, self.ack_num, 0, 0, 0, 1, 0, data)
        else:
            p = Packet(self.seq_num, self.ack_num, 0, 0, 0, 0, 0, data)
        self.next_seq_num()
        self.out_packet_queue.put_low(p)

    def start(self):
        self.start_thread(self.consume_in_queue, ())
        self.start_thread(self.consume_out_queue, ())

    # leer paquetes entrantes a esta connection
    def consume_in_queue(self):
        while True:
            try:
                packet = self.in_packet_queue.get(timeout=cte.SOCKET_TIMEOUT)
                if not packet:
                    break
                self.process_in_packet(packet)
            except queue.Empty: # timeout
                self.action_queue.put_high((Action.CLOSE, self.address))
                break

    # los paquetes no ack salen por aca, usando protocolo gbn/saw
    # los paquetes ack salen directo por socket
    def consume_out_queue(self):
        while True:
            packet = self.out_packet_queue.get()
            if not packet:
                break
            self.window.put(packet)

    def process_in_packet(self, packet: Packet):
        # simular perdida
        # if random.randint(0, 10) == 0:
        #     return

        # print(f"Recv: {packet}")

        # llega un paquete desordenado que no es syn (los syn desordenados necesitan trato especial)
        if packet.seq_num != self.expd_seq_num and not packet.syn:
            # si ya se recibio algun paquete antes, ack_num != None, envio ack del ultimo recibido
            if self.ack_num is not None:
                self.send_ack(0, 0, 0)
            return

        # llega syn upload, soy server
        if packet.syn and not packet.ack and packet.upload:
            self.ack_num = packet.seq_num
            self.send_ack(1, 0, 1)
            # es el primer syn upload que me llega de ese cliente
            if not self.recving_from_client:
                self.action_queue.put_low((Action.RECV_FILE, self.address, packet.data))
                self.next_expd_seq_num()
                self.recving_from_client = True
            return
        
        # llega syn download, soy server
        if packet.syn and not packet.ack and not packet.upload:
            self.ack_num = packet.seq_num
            # sea el primer syn que manda o no, seq_num es 0, igual es el seq_num de un ack, no deberia mirarse siquiera
            self.send_ack(1, 0, 0, seq_num=0)
            # es el primer syn download que me llega de ese cliente
            if not self.sending_to_client:
                self.action_queue.put_low((Action.SEND_FILE, self.address, packet.data))
                self.next_expd_seq_num()
                self.sending_to_client = True
            return
        
        # llega syn ack, soy cliente upload
        if packet.syn and packet.ack and packet.upload:
            self.window.recv_ack(packet.ack_num)
            if not packet.saw:
                self.window.stop()
                self.window_size = cte.GBN_WINDOW_SIZE
                self.window = Window(cte.GBN_WINDOW_SIZE, self.socket, self.address)
            self.action_queue.put_low((Action.SEND_FILE,))
            return

        # llega syn ack, soy cliente download
        if packet.syn and packet.ack and not packet.upload:
            self.window.recv_ack(packet.ack_num)
            self.waiting_synack = False
            self.action_queue.put_low((Action.RECV_FILE,))
            return
        
        # soy cliente download, ya envie syn, estoy esperando synack
        if self.waiting_synack:
            return
        
        # llega fin
        if packet.fin and not packet.ack:
            self.ack_num = packet.seq_num
            self.send_ack(0, 1, 0)
            self.next_expd_seq_num()
            self.action_queue.put_high((Action.CLOSE, self.address))
            return
        
        # llega fin ack
        if packet.fin and packet.ack:
            self.action_queue.put_high((Action.CLOSE, self.address))
            return
        
        # llega ack normal
        if packet.ack:
            self.window.recv_ack(packet.ack_num)
        # llega paquete normal de data (todas las flags en 0)
        else:
            self.next_expd_seq_num()
            self.ack_num = packet.seq_num
            self.send_ack(0, 0, 0)
            self.delivery_queue.put(packet.data)
            # se recibio el ultimo paquete
            if packet.data == b"":
                self.enqueue_out_data(b"", fin=True)

    def send_ack(self, syn, fin, up, seq_num=None):
        if seq_num is None:
            seq_num = self.seq_num
        saw = self.window_size == cte.SAW_WINDOW_SIZE
        ack_packet = Packet(seq_num, self.ack_num, saw, 1, syn, fin, up, b"")
        self.socket.sendto(ack_packet.to_bytes(), self.address)
        # print(f"Sent: {ack_packet}")

    def next_seq_num(self):
        self.seq_num += 1
        if self.seq_num == 2**16:
            self.seq_num = 0

    def next_expd_seq_num(self):
        self.expd_seq_num += 1
        if self.expd_seq_num == 2**16:
            self.expd_seq_num = 0

    def start_thread(self, target, args):
        t = threading.Thread(target=target, args=args)
        self.threads.append(t)
        t.start()

    # joinea threads spawneados por la clase
    def shutdown(self):
        self.window.stop()
        self.in_packet_queue.put_high(0)
        self.out_packet_queue.put_low(0)
        for t in self.threads:
            t.join()
