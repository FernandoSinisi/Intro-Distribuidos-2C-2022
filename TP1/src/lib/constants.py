from enum import Enum

DEFAULT_SERVER_IP = "localhost"
DEFAULT_SERVER_PORT = 8080
DEFAULT_SERVER_DIRPATH = "../files/server-files"

DEFAULT_FILEPATH = "../files/client-files/file.txt"
DEFAULT_FILENAME = "file.txt"

SERVER_LOG_FILE = "logs/server.log"
UPLOAD_CLIENT_LOG_FILE = "logs/upload.log"
DOWNLOAD_CLIENT_LOG_FILE = "logs/download.log"

MAX_DATAGRAM_SIZE = 2048
SOCKET_TIMEOUT = 30  # timeout para cerrar conexion
PACKET_TIMEOUT = 0.1   # timeout para reenvio de paquete

GBN_WINDOW_SIZE = 25
SAW_WINDOW_SIZE = 1

HIGH_PRIO = 1
LOW_PRIO = 2


class Protocol(Enum):
    UDP_SAW = "udp-saw"
    UDP_GBN = "udp-gbn"


class Action(Enum):
    CLOSE = "CLOSE",
    STOP = "STOP",
    SEND_FILE = "SEND FILE",
    RECV_FILE = "RECV FILE"
