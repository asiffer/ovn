from enum import Enum
from typing import Annotated, Any, Literal

import pydantic
from pydantic import Field, ValidationError, field_validator
from pydantic.main import BaseModel

NoneSingleton = ["set", []]


class Unlimited(str, Enum):
    unlimited = "unlimited"


class RefType(str, Enum):
    strong = "strong"
    weak = "weak"


class OVNAtomicType(str, Enum):
    """
    One of the strings "integer", "real", "boolean", "string", or
    "uuid", representing the specified scalar type.
    """

    integer = "integer"
    real = "real"
    boolean = "boolean"
    string = "string"
    uuid = "uuid"

    def unserialize(self, value: Any) -> str | int | float | bool:
        if self == OVNAtomicType.string:
            return str(value)
        if self == OVNAtomicType.integer:
            return int(value)
        if self == OVNAtomicType.boolean:
            return bool(value)
        if self == OVNAtomicType.real:
            return float(value)
        if self == OVNAtomicType.uuid:
            # here we assume that the value is ['uuid', '<value>']
            return str(value[-1])
        raise TypeError(f"Cannot unserialize value {value}")

    def serialize(self, value: Any) -> Any:
        if self == OVNAtomicType.uuid:
            return ["uuid", str(value)]
        if self == OVNAtomicType.boolean:
            return value
        return str(value)

    def as_python_type(self) -> type:
        if self == OVNAtomicType.string:
            return str
        if self == OVNAtomicType.integer:
            return int
        if self == OVNAtomicType.boolean:
            return bool
        if self == OVNAtomicType.real:
            return float
        if self == OVNAtomicType.uuid:
            return str
        raise TypeError(f"Cannot unserialize value {self}")


# JsonID = pydantic.constr[regex=r"[a-zA-Z_][a-zA-Z0-9_]*"]

JsonID = Annotated[str, Field(pattern=r"[a-zA-Z_][a-zA-Z0-9_]*")]


MinInteger = Annotated[int, Field(ge=0, le=1, strict=True)]


class OVNBaseType(BaseModel):
    """
    The type of a key or value in a database column.
    """

    type: OVNAtomicType
    enum: set[str] | None = None
    minInteger: int | None = None
    maxInteger: int | None = None
    minReal: float | None = None
    maxReal: float | None = None
    minLength: int | None = None
    maxLength: int | None = None
    refTable: JsonID | None = None
    refType: RefType | None = None

    @field_validator("enum", mode="before")
    def check_enum(cls, v):
        if isinstance(v, str):
            return [v]
        return v[-1]

    def unserialize(self, value: Any) -> str | int | float | bool:
        return self.type.unserialize(value)

    def serialize(self, value: Any) -> Any:
        return self.type.serialize(value)

    def as_python_type(self) -> Any:
        if self.enum is not None:
            # sorted() keeps the rendering deterministic (enum is a set) and
            # tuple(...) is the 3.10-safe spelling of Literal[*self.enum].
            return Literal[tuple(sorted(self.enum))]  # type: ignore
        return self.type.as_python_type()


class OVNType(BaseModel):
    """
    The type of a database column
    """

    key: OVNBaseType | OVNAtomicType
    value: OVNBaseType | OVNAtomicType | None = None
    min: MinInteger = 1
    max: pydantic.PositiveInt | Unlimited = 1

    @field_validator("max")
    def check_min_max_order(cls, v):
        if v == "unlimited":
            return v
        if v < 1:
            raise ValidationError("max must be >=1")
        if v < cls.min:
            raise ValidationError("We must have max >= min")
        return v

    def is_map(self) -> bool:
        """
        If "min" and "max" are both 1 and "value" is not specified, the
        type is the scalar type specified by "key".

        If "min" is not 1 or "max" is not 1, or both, and "value" is not
        specified, the type is a set of scalar type "key".

        -> if value is set, it is a map
        """
        return self.value is not None

    def is_set(self) -> bool:
        return (
            (self.value is None)
            and (self.min == 0 or self.min == 1)
            and (isinstance(self.max, Unlimited))
        )

    def is_atomic_type(self) -> bool:
        return isinstance(self.key, OVNAtomicType)

    def is_singleton(self) -> bool:
        return (self.min == 0 or self.min == 1) and (self.max == 1)

    def unserialize(self, value: Any) -> Any:
        if self.is_singleton() and (value == NoneSingleton):
            return None
        if self.is_set():
            if value[0] == "set":
                return set(map(self.key.unserialize, value.pop(1)))
            # sometimes we have the single object (not wrapped in a set)
            return {self.key.unserialize(value)}
        if self.is_map():
            return dict(value.pop(1))
        return self.key.unserialize(value)

    def serialize(self, value: Any) -> Any:
        if self.is_singleton() and (value is None):
            return NoneSingleton
        if self.is_set():
            # A bare scalar is accepted in place of a one-element set (OVN is
            # lenient about this, and unserialize already does the reverse).
            items = value if isinstance(value, (set, list, tuple)) else [value]
            return ["set", [self.key.serialize(v) for v in items]]
        if self.is_map():
            # here we know that value is not None
            assert self.value is not None
            m = []
            for k, v in value.items():
                m.append([self.key.serialize(k), self.value.serialize(v)])
            return ["map", m]
        return self.key.serialize(value)

    def as_python_type(self) -> Any:
        # Order matters: a set/map of "uuid" still has an *atomic* key, so the
        # cardinality (map -> set -> singleton) must be checked before falling
        # back to the scalar key type.
        # These build runtime typing special forms (Dict/Set/unions) from
        # values computed at runtime, which static checkers cannot model as
        # type expressions -- hence the ignores.
        key_type = self.key.as_python_type()
        if self.is_map():
            assert self.value is not None
            return dict[key_type, self.value.as_python_type()]  # type: ignore
        if self.is_set():
            return set[key_type]  # type: ignore
        if self.is_singleton() and self.min == 0:
            return key_type | None
        return key_type


class ColumnSchema(BaseModel):
    # The "type" specifies the type of data stored in this column.
    type: OVNType | OVNAtomicType

    # If "ephemeral" is specified as true, then this column's values are
    # not guaranteed to be durable; they may be lost when the database
    # restarts.  A column whose type (either key or value) is a strong
    # reference to a table that is not part of the root set is always
    # durable, regardless of this value.  (Otherwise, restarting the
    # database could lose entire rows.)
    ephemeral: bool = False
    # mutable" is specified as false, then this column's values may
    # not be modified after they are initially set with the "insert"
    # operation.
    mutable: bool = True

    def unserialize(self, value: Any) -> Any:
        return self.type.unserialize(value)

    def serialize(self, value: Any) -> Any:
        return self.type.serialize(value)

    def as_python_type(self) -> type:
        return self.type.as_python_type()


class TableSchema(BaseModel):
    columns: dict[str, ColumnSchema]
    maxRows: int | None = None
    # The "isRoot" boolean is used to determine whether rows in the
    # table require strong references from other rows to avoid garbage
    # collection.  (See the discussion of "strong" and "weak" references
    # below in the description of <base-type>.)  If "isRoot" is
    # specified as true, then rows in the table exist independent of any
    # references (they can be thought of as part of the "root set" in a
    # garbage collector).  If "isRoot" is omitted or specified as false,
    # then any given row in the table may exist only when there is at
    # least one reference to it, with refType "strong", from a different
    # row (in the same table or a different table).  This is a
    # "deferred" action: unreferenced rows in the table are deleted just
    # before transaction commit.
    # For compatibility with schemas created before "isRoot" was
    # introduced, if "isRoot" is omitted or false in every
    # <table-schema> in a given <database-schema>, then every table is
    # part of the root set.
    isRoot: bool = False

    # If "indexes" is specified, it must be an array of zero or more
    # <column-set>s.  A <column-set> is an array of one or more strings,
    # each of which names a column.  Each <column-set> is a set of
    # columns whose values, taken together within any given row, must be
    # unique within the table.  This is a "deferred" constraint,
    # enforced only at transaction commit time, after unreferenced rows
    # are deleted and dangling weak references are removed.  Ephemeral
    # columns may not be part of indexes.
    indexes: list[set[str]] | None = None

    def unserialize(self, record: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = dict.fromkeys(record.keys())
        for col, value in record.items():
            column = self.columns.get(col, self.columns.get("_" + col))
            if column is None:
                raise KeyError(f"Unknown column {col!r}")
            out[col] = column.unserialize(value)
        return out

    def serialize(self, row: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = dict.fromkeys(row.keys())
        for col, value in row.items():
            column = self.columns.get(col, self.columns.get("_" + col))
            if column is None:
                raise KeyError(f"Unknown column {col!r}")
            out[col] = column.serialize(value)
        return out

    def attributes(self):
        pass

    def complete(self):
        """
        Every table has the following columns whose definitions are not
        included in the schema:

            "_uuid": This column, which contains exactly one UUID value, is
            initialized to a random value by the database engine when it
            creates a row.  It is read-only, and its value never changes
            during the lifetime of a row.

            "_version": Like "_uuid", this column contains exactly one UUID
            value, initialized to a random value by the database engine
            when it creates a row, and it is read-only.  However, its value
            changes to a new random value whenever any other field in the
            row changes.  Furthermore, its value is ephemeral: when the
            database is closed and reopened, or when the database process
            is stopped and then started again, each "_version" also changes
            to a new random value.
        """

        uuid = ColumnSchema(type=OVNAtomicType.uuid, mutable=False)

        version = ColumnSchema(type=OVNAtomicType.uuid, mutable=False, ephemeral=True)

        self.columns["_uuid"] = uuid
        self.columns["_version"] = version


class DatabaseSchema(BaseModel):
    # The "name" identifies the database as a whole.  It must be
    # provided to most JSON-RPC requests to identify the database being
    # operated on.
    name: JsonID
    # The "version" reports the version of the database schema.  It is
    # REQUIRED to be present.  Open vSwitch semantics for "version" are
    # described in [DB-SCHEMA].  Other schemas may use it differently.
    version: str
    # The "cksum" optionally reports an implementation-defined checksum
    # for the database schema.  Its use is primarily as a tool for
    # schema developers, and clients SHOULD ignore it.
    cksum: str | None
    # The value of "tables" is a JSON object whose names are table names
    # and whose values are TableSchemas
    tables: dict[JsonID, TableSchema]

    def complete(self):
        """Complete all the tables with uuid and version"""
        for table in self.tables.values():
            table.complete()

    def classes(self) -> dict[str, type]:
        raise NotImplementedError
