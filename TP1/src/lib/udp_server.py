import logging
import threading
from socket import *
from pathlib import Path

import lib.constants as cte
from lib.constants import Action
from lib.packet import Packet
from lib.udp_connection import UDPConnection
import lib.utils as utils
from lib.priority_queue import PQueue as PriorityQueue

class UDPServer:
    """This class will receive packets from its socket and pass them through a queue
    to the threads handling each client's connection"""

    def __init__(self, host, port, storage_path, rdt_protocol):
        self.host = host
        self.port = port
        self.storage_path = storage_path
        self.window_size = utils.get_window_size(rdt_protocol)
        self.logger = logging.getLogger(__name__)

        self.connections = {}
        self.connection_action_queue = PriorityQueue()
        self.threads = []

        self.udp_server_socket = None
        self.stopping = False

    def start(self):
        self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.
        self.udp_server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 10)
        self.udp_server_socket.bind((self.host, self.port))
        self.udp_server_socket.settimeout(1) # en realidad se ignora el timeout de server, ponerlo en 1 es solo para no estar bloqueado siempre y poder hacer ctrlC
        self.logger.info(f"The server is ready. Host:{self.host} Port:{self.port}")

    def run(self):
        self.logger.info("Server is running")
        self.start_thread(self.handle_action, ())
        while True:
            try:
                datagram, address = self.udp_server_socket.recvfrom(cte.MAX_DATAGRAM_SIZE)
            except timeout:
                continue
            except ConnectionResetError:
                continue
            self.handle_packet(datagram, address)

    def handle_packet(self, datagram, address):
        if address not in self.connections:
            if Packet.from_bytes(datagram).syn:
                self.handle_new_client(datagram, address)
        else:
            self.connections[address].enqueue_in_data(datagram)

    def handle_new_client(self, datagram, address):
        new_connection = UDPConnection(self.udp_server_socket, address, self.connection_action_queue, self.window_size)
        self.connections[address] = new_connection
        self.logger.info(f"New connection from {address}")
        self.connections[address].enqueue_in_data(datagram)
        new_connection.start()

    def recv_file_from_client(self, client_address, file_name):
        conn = self.connections[client_address]

        path = Path(__file__).parent.parent / self.storage_path / file_name
        with path.open("wb+") as f:
            while True:
                if (client_address not in self.connections) or self.stopping:
                    break
                chunk = conn.delivery_queue.get()
                if chunk == b"":
                    break

                written = f.write(chunk)
                if written != len(chunk):
                    pass  # manejar error

    def send_file_to_client(self, client_address, file_name):
        conn = self.connections[client_address]

        path = Path(__file__).parent.parent / self.storage_path / file_name
        with path.open("rb") as f:
            while True:
                if (client_address not in self.connections) or self.stopping:
                    break
                chunk = f.read(2043)
                conn.enqueue_out_data(chunk)
                if chunk == b"":
                    break

    def handle_action(self):
        while True:
            action = self.connection_action_queue.get()
            action_type = action[0]
            client_address = action[1]

            if client_address:
                self.logger.info(f"Handling action {action_type} from client {client_address}")
            else:
                self.logger.info(f"Handling action {action_type}")

            if action_type == Action.RECV_FILE:
                file_name = action[2].decode()
                self.start_thread(self.recv_file_from_client, (client_address, file_name))
            if action_type == Action.SEND_FILE:
                file_name = action[2].decode()
                self.start_thread(self.send_file_to_client, (client_address, file_name))
            if action_type == Action.CLOSE:  # en este caso el cliente inicio el cierre
                self.connections[client_address].shutdown()
                self.connections.pop(client_address)
            if action_type == Action.STOP:
                break

    def start_thread(self, target, args):
        t = threading.Thread(target=target, args=args)
        self.threads.append(t)
        t.start()

    # Ctrl C entra aca
    def stop(self):
        self.stopping = True
        clients = list(self.connections.keys())
        for address in clients:
            self.connections[address].shutdown()
            self.connections.pop(address)

        self.udp_server_socket.close()
        self.connection_action_queue.put_high((Action.STOP, ""))

        for t in self.threads:
            t.join()
