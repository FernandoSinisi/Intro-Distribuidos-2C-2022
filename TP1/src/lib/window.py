
import time
from queue import *
from socket import *
import threading
from lib.packet import Packet
import lib.constants as cte


class Window:
    def __init__(self, size, socket: socket, address):
        self.size = size
        self.socket = socket
        self.address = address

        # estructuras consistentes, se necesita comportamiento de queue pero tambien acceder a elementos
        self.packet_queue = Queue(maxsize=self.size)
        self.packet_list = list(self.packet_queue.queue)

        self.lock = threading.Lock()
        self.timer_thread = None
        self.timer_event = None
        self.timer_running = False

        self.stopped = False

    # coloca paquete en la ventana de envio, bloquea si ventana llena
    def put(self, p: Packet):
        self.packet_queue.put(p)
        self.packet_list = list(self.packet_queue.queue)
        if self.stopped:
            return
        self.socket.sendto(p.to_bytes(), self.address)
        # if p.seq_num % 100 == 0:
        #     print(f"Sent: {p}")
        if not self.timer_running:
            self.start_timer()

    def reset(self):
        with self.lock:
            self.packet_queue.queue.clear()
            for p in self.packet_list.copy():
                self.packet_queue.put(p)
                if not self.stopped:
                    self.socket.sendto(p.to_bytes(), self.address)
                    # print(f"Resent: {p}")
                    if not self.timer_running:
                        self.start_timer()

    # se recibio un ack para el paquete seq_number entonces ese paquete
    # y los anteriores en la ventana se consideran ackd y la ventana avanza
    def recv_ack(self, seq_number):
        try:
            with self.lock:
                adv = [p.seq_num for p in self.packet_list].index(seq_number)
                self.advance_window(adv + 1)
        except ValueError:
            pass

    def advance_window(self, n):
        for _ in range(n):
            self.packet_queue.get()
        self.packet_list = list(self.packet_queue.queue)
        if len(self.packet_list) == 0:
            self.stop_timer()

    def start_timer(self):
        self.timer_event = threading.Event()
        self.timer_thread = threading.Thread(target=self.run_timer, args=(cte.PACKET_TIMEOUT,))
        self.timer_thread.start()
        self.timer_running = True

    def run_timer(self, to):
        timeout = not self.timer_event.wait(timeout=to)
        self.timer_running = False
        if timeout:
            self.reset()

    def stop_timer(self):
        if self.timer_running:
            self.timer_event.set()
            self.timer_running = False
    
    def stop(self):
        with self.lock:
            self.stop_timer()
            self.stopped = True
