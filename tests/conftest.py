# content of conftest.py
from ovsdb.application import OVSDBClient
import threading
import pytest
import socketserver
import os
import random
from typing import Callable, Union

from string import ascii_letters,  digits
from random import choice


class RequestHandler(socketserver.BaseRequestHandler):
    bufsize = 1024

    def handle(self):
        data = b""
        chunk = self.request.recv(self.bufsize)
        while len(chunk) > 0:
            data += chunk
            chunk = self.request.recv(self.bufsize)
        self.request.sendall(data)


class ThreadedServer:
    """This class aims to provide a basic start/stop server
    in a detached thread.
    """

    def __init__(self, server: Union[socketserver.TCPServer, socketserver.UnixStreamServer]) -> None:
        self.__server__ = server
        self.__thread__ = threading.Thread(target=server.serve_forever,
                                           daemon=True)
        self.server_address = server.server_address

    def start(self) -> None:
        """
        Start the server in a background thread
        """
        self.__thread__.start()

    def stop(self) -> None:
        """
        Stop the server
        """
        self.__server__.shutdown()
        self.__thread__.join()


@pytest.fixture
def random_payload() -> Callable:
    # return a callable
    return lambda size: "".join(choice(ascii_letters + digits)
                                for x in range(size)).encode()


@pytest.fixture
def high_port() -> int:
    return random.randint(40000, 60000)


@pytest.fixture
def server_request_handler() -> Callable:
    return random_payload


@pytest.fixture
def unix_server(tmpdir):
    endpoint = os.path.join(tmpdir, "unix_server.socket")
    server = socketserver.UnixStreamServer(endpoint, RequestHandler)
    return ThreadedServer(server=server)


@pytest.fixture
def tcp_server(high_port) -> ThreadedServer:
    server = socketserver.TCPServer(("127.0.0.1", high_port),
                                    RequestHandler)
    return ThreadedServer(server=server)


@pytest.fixture
def ovn_northd_socket() -> str:
    return "/run/ovn/ovnnb_db.sock"


@pytest.fixture
def ovn_northd_client(ovn_northd_socket) -> OVSDBClient:
    return OVSDBClient(f"unix://{ovn_northd_socket}")
