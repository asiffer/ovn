from os import error
import socket
from ovsdb.transport import Connection
from typing import Tuple, Union, List, Dict, Any
import json
from random import choice
from string import ascii_letters, digits


def parse_server_address(s: str) -> Tuple[Union[str, Tuple[str, Union[int, str]]], int]:
    proto, address = s.split('://')
    if proto.lower() == "unix":
        return address, socket.AF_UNIX
    return address.split(':'), socket.AF_INET


def random_json_id(size: int = 12) -> str:
    """
    A JSON string matching [a-zA-Z_][a-zA-Z0-9_]*. <id>s that begin
    with _ are reserved to the implementation and MUST NOT be used by
    the user.
    """
    if size <= 0:
        raise ValueError("The size must be a strictly positive integer")
    prefix = choice(ascii_letters)
    suffix = "".join([choice(ascii_letters+digits+'_') for _ in range(size-1)])
    return prefix + suffix


class OVSDBError(Exception):
    """
    Error during the communication with the database
    """

    def __init__(self, method: str, error: str, id: str, result: List[Any]) -> None:
        self.method = method
        self.error = error
        self.id = id
        self.result = result

    def __str__(self) -> str:
        msg = f"Error while requesting method '{self.method}': {self.error}\n"
        msg += f"Raw response: {self.result}"


class OVSDBClient:
    def __init__(self, server_address: str):
        self.transport = Connection(*parse_server_address(server_address))
        self.id_history = []

    def send(self, method: str, params: List[Dict[str, Any]], id: str) -> Any:
        payload = {"method": method, "params": params, "id": id}
        # json-rpc
        with self.transport as conn:
            # save the id within the internal history
            self.id_history.append(id)
            # query
            result = json.loads(conn.query(json.dumps(payload).encode()))
        # check empty response
        if result is None:
            raise Exception(
                f"Error while requesting method '{method}': no response")
        # check the id
        assert result["id"] == id, f"Incorrect response id, expect {id}, got {result['id']}"
        # check errors
        if result["error"] != None:
            raise OVSDBError(method=method, error=result['error'],
                             id=id, result=result["result"])
        return result["result"]

    def send_auto(self, method: str, params: List[Dict[str, Any]]) -> Any:
        """
        An id is randomly assigned
        """
        return self.send(method=method, params=params, id=random_json_id())

    def list_dbs(self):
        """
        This operation retrieves an array whose elements are the names of the
        databases that can be accessed over this management protocol
        connection.
        """
        return self.send_auto(method="list_dbs", params=[])

    def get_schema(self, db_name: str):
        return self.send_auto(method="get_schema", params=[db_name])

    def echo(self):
        """
        The "echo" method can be used by both clients and servers to verify
        the liveness of a database connection. It MUST be implemented by
        both clients and servers
        """
        self.send_auto(method="echo", params=[])

    def transact(self, db_name: str, operations: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """
        This RPC method causes the database server to execute a series of
        operations in the specified order on a given database.
        """
        if not isinstance(operations, list):
            operations = [operations]
        return self.send_auto(method="transact", params=[db_name, *operations])

    def cancel(self, id: str) -> str:
        """
        The "cancel" method is a JSON-RPC notification, i.e., no matching
        response is provided. It instructs the database server to
        immediately complete or cancel the "transact" request whose "id" 
        is the same as the notification's "params" value.

        If the "transact" request can be completed immediately, then the
        server sends a response in the form described for "transact".
        Otherwise, the server sends a JSON-RPC error
        response of the following form:

            {
                "result": null,
                "error": "canceled",
                "id": the "id" member of the canceled request,
            }

        The "cancel" notification itself has no reply.
        """
        try:
            self.send(method="cancel", params=[id], id=None)
        except OVSDBError as err:
            if err.error == "canceled":
                # return tht id
                return error.id
            # otherwise re-raise
            raise err
