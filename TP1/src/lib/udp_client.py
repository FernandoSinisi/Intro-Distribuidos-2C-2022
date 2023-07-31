import logging
import threading
from pathlib import Path
from socket import *

import lib.constants as cte
from lib.constants import Action
from lib.udp_connection import UDPConnection
from lib.priority_queue import PQueue as PriorityQueue


class UDPClient:

    def __init__(self, host, port, file_path, file_name, upload):
        self.host = host
        self.port = port
        self.file_path = file_path
        self.file_name = file_name
        self.window_size = cte.SAW_WINDOW_SIZE
        self.upload = upload
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.action_queue = PriorityQueue()
        self.threads = []

        self.udp_client_socket = None
        self.stopping = False

    def start(self):
        self.udp_client_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_client_socket.settimeout(1) # se maneja en connection eltimeout, asi puedo ctrlc rapido
        self.connection = UDPConnection(self.udp_client_socket, (self.host, self.port), self.action_queue,
                                        self.window_size)

    def run(self):
        self.start_thread(self.handle_action, ())
        self.connection.start()

        if self.upload:
            self.connection.enqueue_out_data(self.file_name.encode(), upload=True)
        else:
            self.connection.enqueue_out_data(self.file_name.encode(), download=True)

        while True:
            if self.stopping:
                break
            try:
                packet = self.udp_client_socket.recvfrom(cte.MAX_DATAGRAM_SIZE)
            except timeout:
                continue
            self.connection.enqueue_in_data(packet[0])

    def recv_file_from_server(self):
        path = Path(__file__).parent.parent / self.file_path
        with path.open("wb+") as f:
            while True:
                if self.stopping:
                    break
                chunk = self.connection.delivery_queue.get()
                if chunk == b"":
                    break

                written = f.write(chunk)
                if written != len(chunk):
                    pass  # manejar error

    def send_file_to_server(self):
        path = Path(__file__).parent.parent / self.file_path
        with path.open("rb+") as f:
            while True:
                if self.stopping:
                    break
                chunk = f.read(2043)
                self.connection.enqueue_out_data(chunk)
                if chunk == b"":
                    break

    def handle_action(self):
        self.logger.info("Action handling thread started")
        while True:
            action = self.action_queue.get()[0]
            self.logger.info(f"Handling action {action}")

            if action == Action.CLOSE:  # en este caso el servidor inicio el cierre
                self.connection.shutdown()
                self.stopping = True
                break
            
            if action == Action.STOP:  # esta accion es para detener este thread cuando el cliente inicia el cierre
                break

            if action == Action.SEND_FILE:
                self.start_thread(self.send_file_to_server, ())

            if action == Action.RECV_FILE:
                self.start_thread(self.recv_file_from_server, ())

    def start_thread(self, target, args):
        t = threading.Thread(target=target, args=args)
        self.threads.append(t)
        t.start()

    # Ctrl C entra aca
    def stop(self):
        self.stopping = True
        self.connection.shutdown()
        self.udp_client_socket.close()
        self.action_queue.put_high((Action.STOP, None))  # para que termine el thread de handle_action
        for t in self.threads:
            t.join()
