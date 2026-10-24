import random
import string
from copy import deepcopy
from typing import Any, Literal, overload

from ovn.ovsdb import DefaultOVSDBClient, OVSDBClient
from ovn.schema import DatabaseSchema

DB_NAME = "OVN_Northbound"

# Schema fetches are expensive (a blocking round-trip over the socket) and the
# OVN NB schema is stable for the lifetime of a server. Cache it per endpoint so
# that constructing many OVNClients (e.g. one per model Manager) hits the wire
# only once.
_SCHEMA_CACHE: dict[str, DatabaseSchema] = {}


Record = dict[str, Any]

# A 3-element JSON array of the form [<column>, <function>, <value>]
# that represents a test on a column value.  Except as otherwise
# specified below, <value> MUST have the same type as <column>.  The
# meaning depends on the type of <column>
Condition = tuple[str, str, str | tuple[Literal["uuid", "named-uuid"], str]]


Mutator = Literal["+=", "-=", "*=", "/=", "%=", "insert", "delete"]
# A 3-element JSON array of the form [<column>, <mutator>, <value>]
# that represents a change to a column value.  Except as otherwise
# specified below, <value> must have the same type as <column>.  The
# meaning depends on the type of <column>:
Mutation = tuple[str, Mutator, Any]


def random_id(length: int = 8) -> str:
    """
    Generate a random string of fixed length
    """
    # <id> has the following format: [a-zA-Z_][a-zA-Z0-9_]*
    out = random.choice(string.ascii_letters)
    return out + "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length - 1)
    )


class OperationComposer:
    """Object to concatenate several db operations"""

    def __init__(self, operations: list[dict[str, Any]] | None = None):
        self.__operations__ = operations if operations is not None else []

    def clear(self):
        self.__operations__.clear()

    def select(
        self,
        table: str,
        where: list[Condition] | None = None,
        columns: list[str] | None = None,
    ) -> "OperationComposer":
        operation = {"op": "select", "where": where or [], "table": table}
        if columns is not None:
            operation["columns"] = columns

        self.__operations__.append(operation)
        return self

    def insert(
        self, table: str, row: Record | None = None, uuid_name: str | None = None
    ) -> "OperationComposer":
        """
        Insert a new row in the database and return its uuid
        """
        operation = {"op": "insert", "table": table, "row": row or {}}
        if uuid_name:
            operation["uuid-name"] = uuid_name
        self.__operations__.append(operation)
        return self

    def delete(self, table: str, uuid: str) -> "OperationComposer":
        operation = {
            "op": "delete",
            "where": [
                ["_uuid", "==", ["uuid", uuid]],
            ],
            "table": table,
        }
        self.__operations__.append(operation)
        return self

    def update(
        self,
        table: str,
        where: list[Condition] | None = None,
        row: Record | None = None,
    ) -> "OperationComposer":
        operation = {
            "op": "update",
            "table": table,
            "where": where or [],
            "row": row or {},
        }
        self.__operations__.append(operation)
        return self

    def mutate(
        self,
        table: str,
        where: list[Condition] | None = None,
        mutations: list[Mutation] | None = None,
    ) -> "OperationComposer":
        operation = {
            "op": "mutate",
            "table": table,
            "where": where or [],
            "mutations": mutations or [],
        }
        self.__operations__.append(operation)
        return self

    def wait(
        self,
        table: str,
        where: list[Condition] | None = None,
        columns: list[str] | None = None,
        until: Literal["==", "!="] = "!=",
        rows: list[Record] | None = None,
        timeout: int | None = None,
    ):
        operation: dict[str, Any] = {
            "op": "wait",
            "table": table,
            "where": where or [],
            "columns": columns or [],
            "until": until,
            "rows": rows or [],
        }
        if timeout:
            operation["timeout"] = timeout

        self.__operations__.append(operation)
        return self

    def operations(self) -> list[dict[str, Any]]:
        """Return all the operations and flush the internal state"""
        out = deepcopy(self.__operations__)
        self.clear()
        return out


class OVNClient:
    """
    OVNClient is a wrapper of OVSDBClient. It exposes
    some helpers to query the OVN northbound database
    """

    def __init__(self, client_or_url: str | OVSDBClient | None = None):
        if client_or_url is None:
            # not provided -> use default
            client: OVSDBClient = DefaultOVSDBClient()
        elif isinstance(client_or_url, str):
            # string -> create new client with this connection parameters
            client = OVSDBClient(client_or_url)
        else:
            assert isinstance(client_or_url, OVSDBClient), (
                f"Cannot accept parameter of type '{type(client_or_url)}'"
            )
            # we assume a OVSDBClient
            client = client_or_url

        assert isinstance(client, OVSDBClient), (
            f"Cannot get or build a client to the database from {client}"
        )

        self.client = client
        self.schema = self.import_schema()

    def import_schema(self) -> DatabaseSchema:
        key = str(self.client.endpoint)
        schema = _SCHEMA_CACHE.get(key)
        if schema is None:
            obj = self.client.get_schema(DB_NAME)
            schema = DatabaseSchema.model_validate(obj)
            schema.complete()
            _SCHEMA_CACHE[key] = schema
        return schema

    @overload
    def serialize(self, table: str, records: Record) -> Record: ...
    @overload
    def serialize(self, table: str, records: list[Record]) -> list[Record]: ...
    def serialize(
        self, table: str, records: Record | list[Record]
    ) -> Record | list[Record]:
        if not isinstance(records, list):
            return self.schema.tables[table].serialize(records)
        return [self.schema.tables[table].serialize(r) for r in records]

    @overload
    def unserialize(self, table: str, records: Record) -> Record: ...
    @overload
    def unserialize(self, table: str, records: list[Record]) -> list[Record]: ...
    def unserialize(
        self, table: str, records: Record | list[Record]
    ) -> Record | list[Record]:
        if not isinstance(records, list):
            return self.schema.tables[table].unserialize(records)
        return [self.schema.tables[table].unserialize(r) for r in records]

    def select(
        self,
        table: str,
        where: list[Condition] | None = None,
        columns: list[str] | None = None,
    ) -> list[Record]:
        composer = OperationComposer().select(table, where or [], columns)
        result = self.transact(composer)
        assert len(result) == 1, f"The results involve more than one response: {result}"
        rows: list[Record] = result.pop().get("rows")
        return self.unserialize(table, rows)

    def get(self, table: str, uuid: str) -> Record:
        rows = self.select(table=table, where=[("_uuid", "==", ("uuid", uuid))])
        return rows[0] if rows else {}

    def get_by_name(self, table: str, name: str) -> Record:
        rows = self.select(table=table, where=[("name", "==", name)])
        return rows[0] if rows else {}

    def insert(
        self, table: str, row: Record | None = None, uuid_name: str | None = None
    ):
        """
        Insert a new row in the database and return its uuid
        """
        composer = OperationComposer().insert(table, row or {}, uuid_name)
        result = self.transact(composer)
        return self.unserialize(table, result)

    def create(self, table: str, row: Record | None = None):
        name = random_id()
        serialized: Record = self.schema.tables[table].serialize(row or {})
        composer = OperationComposer()
        composer.insert(table, serialized, uuid_name=name)
        composer.select(table, where=[("_uuid", "==", ("named-uuid", name))])
        result = self.transact(composer)
        # first result is an obscure uuid
        # second result is our row
        rows = result[1]["rows"]
        return self.unserialize(table, rows)

    def delete(self, table: str, uuid: str):
        composer = OperationComposer().delete(table, uuid)
        return self.transact(composer)

    def update(
        self,
        table: str,
        where: list[Condition] | None = None,
        row: Record | None = None,
    ):
        serialized: Record = self.schema.tables[table].serialize(row or {})
        composer = OperationComposer().update(table, where or [], serialized)
        return self.transact(composer)

    def mutate(self, table: str, where: list[Condition], mutations: list[Mutation]):
        composer = OperationComposer().mutate(table, where, mutations)
        return self.transact(composer)

    def create_and_bind(
        self,
        table_create: str,
        row_create: Record,
        table_bind: str,
        attr_bind: str,
        where_bind: list[Condition],
    ) -> tuple[Record, Record]:
        """
        Create a new row in the database and bind it to another table
        Return first the created object and then the bound object
        """
        # create the row
        name = random_id()
        composer = OperationComposer()
        # 0. create the row
        composer.insert(
            table=table_create,
            row=self.schema.tables[table_create].serialize(row_create),
            uuid_name=name,
        )
        # 1. bind it to the other table
        composer.mutate(
            table=table_bind,
            where=where_bind,
            mutations=[(attr_bind, "insert", ["set", [["named-uuid", name]]])],
        )
        # 2.return the created row
        composer.select(
            table=table_create,
            where=[("_uuid", "==", ("named-uuid", name))],
        )
        # 3. return the bound row
        composer.select(
            table=table_bind,
            where=where_bind,
        )
        result = self.transact(composer)
        created_row: Record = result[2]["rows"][0]
        bound_row: Record = result[3]["rows"][0]
        return self.unserialize(table_create, created_row), self.unserialize(
            table_bind, bound_row
        )

    def set(self, table: str, uuid: str, row: Record) -> None:
        result = self.update(
            table=table,
            where=[("_uuid", "==", ("uuid", uuid))],
            row=row,
        )
        # check the result
        assert len(result) == 1, f"Result is weird: {result}"
        assert result[0]["count"] == 1, f"Result is weird: {result}"

    def wait_and_get(self, table: str, uuid: str, version: str) -> Record:
        where: list[Condition] = [("_uuid", "==", ("uuid", uuid))]
        composer = OperationComposer()
        composer.wait(
            table,
            where,
            columns=["_version"],
            until="!=",
            rows=[{"_version": ["uuid", version]}],
        )
        composer.select(table, where)
        result = self.transact(composer)
        # the first operation is the wait
        rows: list[Record] = result[1]["rows"]
        return self.unserialize(table, rows)[0]

    def transact(self, composer: OperationComposer):
        """Run the operations accumulated in the given composer."""
        # calling operations() also clears the composer
        return self.client.transact(
            db_name=DB_NAME,
            operations=composer.operations(),
        )
