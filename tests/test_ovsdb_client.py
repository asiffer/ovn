import os
import socket
import uuid
from typing import Any

from ovn.client import DB_NAME, OperationComposer
from ovn.ovsdb import OVSDBClient
from ovn.ovsdb.errors import BaseError, OVSDBError, TransactionError
from ovn.ovsdb.ovsdb_client import DefaultOVSDBClient


def test_ovn_echo(ovsdb_client: OVSDBClient):
    ovsdb_client.echo()


def test_ovn_list_dbs(ovsdb_client: OVSDBClient):
    dbs = ovsdb_client.list_dbs()
    assert "OVN_Northbound" in dbs
    assert "_Server" in dbs


def test_ovn_get_schema(ovsdb_client: OVSDBClient):
    schema = ovsdb_client.get_schema("OVN_Northbound")
    for k in ["cksum", "name", "version", "tables"]:
        assert k in schema


def test_ovn_add_logical_switch(ovsdb_client: OVSDBClient):
    # {"id":4,"method":"transact","params":["OVN_Northbound",{"uuid-name":"row7cb59701_d626_421e_aa4e_02b095b1bc2b","row":{},"op":"insert","table":"Logical_Switch"}
    operation = {
        "uuid-name": "row7cb59701_d626_421e_aa4e_02b095b1bc2b",
        "row": {},
        "op": "insert",
        "table": "Logical_Switch",
    }
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)
    assert len(result) > 0
    assert "uuid" in result[0]


def test_ovn_list_logical_switch(ovsdb_client: OVSDBClient):
    operation = {
        "op": "select",
        "where": [],
        "columns": ["_uuid"],
        "table": "Logical_Switch",
    }
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)
    rows = result.pop()["rows"]
    for r in rows:
        uuid = r.pop("_uuid")[-1]
        print(uuid)


def test_ovn_delete_all_logical_switch(ovsdb_client: OVSDBClient):
    operation = {"op": "delete", "where": [], "table": "Logical_Switch"}
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)
    print(result)


def test_ovn_add_then_delete_logical_switch(ovsdb_client: OVSDBClient):
    #
    # Add switch
    #
    operation: dict[str, Any] = {
        "op": "insert",
        "table": "Logical_Switch",
        "row": {},
    }
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)

    #
    # List switch
    #
    operation = {
        "op": "select",
        "where": [],
        "columns": ["_uuid"],
        "table": "Logical_Switch",
    }
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)

    rows = result.pop()["rows"]
    nb_logical_switch = len(rows)
    assert nb_logical_switch > 0, f"{result}"

    #
    # Delete switch
    #
    uuid = rows[0]["_uuid"][-1]
    operation = {
        "op": "delete",
        "where": [
            ["_uuid", "==", ["uuid", uuid]],
        ],
        "table": "Logical_Switch",
    }
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)

    #
    # Re-list switch
    #
    operation = {
        "op": "select",
        "where": [],
        "columns": ["_uuid"],
        "table": "Logical_Switch",
    }
    result = ovsdb_client.transact(db_name="OVN_Northbound", operations=operation)

    rows = result.pop()["rows"]
    assert len(rows) == nb_logical_switch - 1, f"{result}"


def test_singleton():
    server_addr = "tcp:127.0.0.1:6501"
    env_key = "OVN_NB_DB"
    # save current env variable
    save = os.environ.get(env_key)
    # modify it
    os.environ[env_key] = server_addr
    client = DefaultOVSDBClient()
    assert client.endpoint == ("127.0.0.1", 6501)
    assert client.family == socket.AF_INET
    del os.environ[env_key]
    # restore
    if save is not None:
        os.environ[env_key] = save
    else:
        del os.environ[env_key]


def test_ovsdb_error():
    client = DefaultOVSDBClient()
    try:
        client.send_auto("transact", [])
    except BaseError as err:
        print(f"{err}")
        assert isinstance(err, OVSDBError)


def test_transact_error():
    client = DefaultOVSDBClient()
    composer = OperationComposer().insert(
        table="Unknown", row={}, uuid_name=uuid.uuid4().__str__()
    )
    try:
        client.transact(db_name=DB_NAME, operations=composer.operations())
    except BaseError as err:
        print(f"{err}")
        assert isinstance(err, TransactionError)
