import argparse
import lib.constants as cte


def parent(serv: str):
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "-verbose", help="increase output verbosity",
        action="store_const", default=20, const=10, dest="verbosity"
    )
    group.add_argument(
        "-q", "-quiet", help="decrease output verbosity",
        action="store_const", default=20, const=30, dest="verbosity"
    )
    parser.add_argument(
        "-H", "--host", metavar="", default=cte.DEFAULT_SERVER_IP, help="%s IP address" % serv
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        metavar="",
        default=cte.DEFAULT_SERVER_PORT,
        help="%s port" % serv,
    )

    return parser


def server():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH] [-P PROTOCOL]",
        description="FTP over UDP server",
        parents=[parent("service")],
    )

    parser.add_argument(
        "-s", "--storage", metavar="", default=cte.DEFAULT_SERVER_DIRPATH, help="storage dir path"
    )

    parser.add_argument(
        "-P",
        "--protocol",
        metavar="",
        required=False,
        default=cte.Protocol.UDP_SAW.value,
        choices=[cte.Protocol.UDP_SAW.value, cte.Protocol.UDP_GBN.value],
        help="rdt protocol to use",
    )

    return parser


def upload():
    parser = argparse.ArgumentParser(
        usage=usage() % "s",
        description="FTP over UDP upload client",
        parents=[parent("server")],
    )
    # parser.add_argument("-s", "--src", help="source file path", metavar="PATH", dest="filepath")
    # parser.add_argument("-n", "--name", help="filename", metavar="name", dest="filename")
    parser.add_argument(
        "-s",
        "--src",
        metavar="",
        default=cte.DEFAULT_FILEPATH,
        help="source file path",
    )
    parser.add_argument(
        "-n", "--name", metavar="", default=cte.DEFAULT_FILENAME, help="file name"
    )

    return parser


def download():
    parser = argparse.ArgumentParser(
        usage=usage() % "d",
        description="FTP over UDP download client",
        parents=[parent("server")],
    )
    parser.add_argument(
        "-d",
        "--dst",
        metavar="",
        default=cte.DEFAULT_FILEPATH,
        help="destination file path",
    )
    parser.add_argument(
        "-n", "--name", metavar="", default=cte.DEFAULT_FILENAME, help="file name"
    )

    return parser


def usage():
    return "%%(prog)s [-h] [-v | -q] [-H ADDR] [-p PORT] [-%c FILEPATH] [-n FILENAME]"
