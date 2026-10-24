import socket
from typing import Any


class Connection:
    """
    The database wire protocol is implemented in JSON-RPC 1.0 [JSON-RPC].
    While the JSON-RPC specification allows a range of transports,
    implementations of this specification SHOULD operate directly over
    TCP.
    """

    def __init__(
        self,
        endpoint: str | tuple[Any, ...],
        family: socket.AddressFamily = socket.AF_UNIX,
        timeout=5,
        bufsize: int = 2048,
    ):
        self.family = family
        self.endpoint = endpoint
        self.bufsize = bufsize
        self.timeout = timeout

    def connect(self):
        self.__socket__ = socket.socket(family=self.family, type=socket.SOCK_STREAM)
        self.__socket__.settimeout(self.timeout)
        self.__socket__.connect(self.endpoint)

    def close(self):
        self.__socket__.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def sendall(self, data: bytes) -> None:
        self.__socket__.sendall(data)

    def recvall(self) -> bytes:
        buffer = b""
        try:
            chunk = self.__socket__.recv(self.bufsize)
            while len(chunk) > 0:
                buffer += chunk
                chunk = self.__socket__.recv(self.bufsize)
        except TimeoutError:
            pass
        return buffer

    def query(self, data: bytes) -> bytes:
        self.__socket__.sendall(data)
        self.__socket__.shutdown(socket.SHUT_WR)
        return self.recvall()
