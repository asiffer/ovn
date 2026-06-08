import json
import socket
from random import choice
from string import ascii_letters, digits
from typing import Any, Dict, List, Optional, Tuple, Union

from ovn.ovsdb.errors import OVSDBError, TransactionError
from ovn.ovsdb.transport import Connection
from ovn.settings import Settings


def parse_server_address(
    s: str,
) -> Tuple[Union[Tuple[str, int], str], socket.AddressFamily]:
    split = s.split(":")
    proto = split[0]
    if proto.lower() == "unix":
        return split[1], socket.AF_UNIX
    return (split[1], int(split[2])), socket.AF_INET


def random_json_id(size: int = 12) -> str:
    """
    A JSON string matching [a-zA-Z_][a-zA-Z0-9_]*. <id>s that begin
    with _ are reserved to the implementation and MUST NOT be used by
    the user.
    """
    if size <= 0:
        raise ValueError("The size must be a strictly positive integer")
    prefix = choice(ascii_letters)
    suffix = "".join([choice(ascii_letters + digits + "_") for _ in range(size - 1)])
    return prefix + suffix


class OVSDBClient:
    endpoint: Union[str, Tuple[str, int]]
    family: socket.AddressFamily

    def __init__(self, server_address: str):
        self.endpoint, self.family = parse_server_address(server_address)
        # self.transport = Connection(*parse_server_address(server_address))
        self.id_history: List[str] = []

    def set_server_address(self, server_address: str):
        self.endpoint, self.family = parse_server_address(server_address)

    def __check_transact_errors(self, results: Optional[List[Dict[str, Any]]]):
        if results is None:
            return
        for r in results:
            if "error" in r:
                raise TransactionError(
                    error=r.pop("error"), details=r.pop("details"), issue=r
                )

    def send(
        self,
        method: str,
        params: List[Union[str, Dict[str, Any]]],
        id: Optional[str],
    ) -> Any:
        payload = {"method": method, "params": params, "id": id}
        # json-rpc
        with Connection(self.endpoint, self.family) as conn:
            # save the id within the internal history
            if id:
                self.id_history.append(id)
            # query
            # print("P:", payload)
            raw = conn.query(json.dumps(payload).encode())
            if raw == b"":
                return None
            # print("R:", raw)
            result = json.loads(raw)
        # check empty response
        if result is None:
            raise Exception(f"Error while requesting method '{method}': no response")
        # check the id
        assert result["id"] == id, (
            f"Incorrect response id, expect {id}, got {result['id']}"
        )
        # check errors
        if result["error"] is not None:
            raise OVSDBError(
                method=method,
                error=result["error"],
                id=id,
                result=result.get("result"),
            )
        return result["result"]

    def send_auto(self, method: str, params: List[Union[str, Dict[str, Any]]]) -> Any:
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

    def transact(
        self,
        db_name: str,
        operations: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> Any:
        """
        This RPC method causes the database server to execute a series of
        operations in the specified order on a given database.
        """
        if not isinstance(operations, list):
            operations = [operations]

        results = self.send_auto(method="transact", params=[db_name, *operations])
        # check errors
        self.__check_transact_errors(results=results)
        # return results if everything is ok
        return results

    def cancel(self, id: str) -> Any:
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
            # no error is triggered if the operation is completed
            return self.send(method="cancel", params=[id], id=None)
        except OVSDBError as err:
            # the error is triggered when the operation is canceled
            # i.e. it won't be completed
            if err.error == "canceled":
                # return the id
                return err.id
            # otherwise re-raise
            raise err


# default client -----------------


class DefaultOVSDBClient(OVSDBClient):
    """Global ovsdb client. It is configured through the
    pydantic settings and especially the OVN_NB_DB env variable
    that must point to the OVN Northbound database.
    """

    __instance__ = None

    def __init__(self):
        return super().__init__(server_address=Settings().ovn_northbound)

    def __new__(cls):
        if cls.__instance__ is None:
            cls.__instance__ = super(DefaultOVSDBClient, cls).__new__(cls)
        return cls.__instance__
