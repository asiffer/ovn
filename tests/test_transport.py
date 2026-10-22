import socket
from typing import Callable

import pytest

from ovn.ovsdb.transport import Connection

from .conftest import ThreadedServer


@pytest.mark.parametrize("size", [500, 1000, 2000, 3000, 5000])
def test_connection_tcp(
    tcp_server: ThreadedServer, random_payload: Callable, size: int
):
    tcp_server.start()

    with Connection(endpoint=tcp_server.server_address, family=socket.AF_INET) as conn:

        payload = random_payload(size)
        response = conn.query(payload)
        assert len(response) == len(
            payload
        ), f"Bad size response, {size} was expected, got {len(response)}"
        assert response == payload, f"Error with payload size: {size}"

    tcp_server.stop()


@pytest.mark.parametrize("size", [500, 1000, 2000, 3000, 5000])
def test_connection_unix(
    unix_server: ThreadedServer, random_payload: Callable, size: int
):
    unix_server.start()

    with Connection(endpoint=unix_server.server_address, family=socket.AF_UNIX) as conn:

        payload = random_payload(size)
        response = conn.query(payload)
        assert len(response) == len(
            payload
        ), f"Bad size response, {size} was expected, got {len(response)}"
        assert response == payload, f"Error with payload size: {size}"

    unix_server.stop()
