import builtins
import re
from collections.abc import Callable
from typing import Any, ClassVar, get_args, get_origin

from ovn.manager import Manager


def class_to_table(name: str) -> str:
    """Convert the name of a class to a possible name of
    the corresponding OVN Northbound table.
    Ex: LogicalSwitch -> Logical_Switch
    Ex: DHCPOptions -> DHCP_Options
    """
    r1 = re.compile(r"([A-Z][a-z])")
    r2 = re.compile(r"([a-z])([A-Z])")
    return r2.sub(r"\1_\2", r1.sub(r"_\1", name)).strip("_")


def need_uuid(func: Callable):
    def wrapper(obj, *args, **kwargs):
        assert hasattr(obj, "_uuid"), (
            f"Cannot interact with the database since "
            f"the object has no uuid (method: {getattr(func, '__name__', func)})"
        )
        return func(obj, *args, **kwargs)

    return wrapper


class Model:
    objects: ClassVar[Any]
    # "_uuid": This column, which contains exactly one UUID value, is
    # initialized to a random value by the database engine when it
    # creates a row.  It is read-only, and its value never changes
    # during the lifetime of a row.
    _uuid: str
    # "_version": Like "_uuid", this column contains exactly one UUID
    # value, initialized to a random value by the database engine
    # when it creates a row, and it is read-only.  However, its value
    # changes to a new random value whenever any other field in the
    # row changes.  Furthermore, its value is ephemeral: when the
    # database is closed and reopened, or when the database process
    # is stopped and then started again, each "_version" also changes
    # to a new random value.
    _version: str

    @classmethod
    def _table(cls) -> str:
        """Return the name of the OVN table that
        corresponds to the class"""
        table = cls.__dict__.get("__table__")
        if isinstance(table, str):
            return table
        return class_to_table(cls.__name__)

    @classmethod
    def list(cls) -> list["Model"]:
        """List all the rows of the table as model instances"""
        return cls.objects.list()

    @property
    def fields(self) -> builtins.list[str]:
        return self.objects._attributes

    def __str__(self):
        attrs = ", ".join(f"{a}={getattr(self, a, None)}" for a in self.fields)
        return f"{self.__class__.__name__}({attrs})"

    def __repr__(self):
        return self.__str__()

    def __init__(self, **kwargs):
        # Validate against the (lazily fetched) column list rather than
        # __annotations__, so constructing a model only contacts the DB if it
        # has not already cached the schema -- never at import time.
        valid = self.objects._attributes
        for k, v in kwargs.items():
            if k not in valid:
                raise AttributeError(
                    f"Attribute {k} is not an attribute of class {self.__class__}. "
                    f"Valid attributes are: {valid}"
                )

            setattr(self, k, v)

    def __init_subclass__(cls):
        """Attach a Manager to the subclass.

        This is intentionally free of any database access: the Manager is lazy
        and fetches the schema only on first use, so importing the models never
        requires a reachable OVN NB database.
        """
        if "objects" in cls.__annotations__:
            # a subclass may re-define the manager type (e.g. to enrich it)
            manager = cls.__annotations__["objects"]
            if get_origin(manager) is ClassVar:
                manager = get_args(manager)[0]
            cls.objects = manager(cls)
        else:
            cls.objects = Manager(cls)
            cls.__annotations__["objects"] = Manager[cls]  # ty: ignore[invalid-type-form]

    def as_row(self) -> dict[str, Any]:
        """Return a record with the mutable attributes and their values"""
        out = {}
        # build the dict
        for c in self.objects._mutable_attributes:
            if hasattr(self, c):
                out[c] = getattr(self, c)
        return out

    @need_uuid
    def delete(self) -> None:
        """Remove an object"""
        self.objects.delete(self._uuid)

    @need_uuid
    def refresh_from_db(self):
        """Fills the object with what is stored in the database"""
        result = self.objects.get_raw(uuid=self._uuid)
        if result is None:
            raise ValueError(f"Object with uuid {self._uuid} not found in the database")
        # fill with attributes
        for k, v in result.items():
            setattr(self, k, v)

    def fetch(self) -> "Model":
        """Reload the object from the database and return it"""
        self.refresh_from_db()
        return self

    def save(self):
        """Sync the object with the database"""
        if not hasattr(self, "_uuid") or self._uuid is None:
            # the result returns only the uuid
            result = self.objects.create_raw(**self.as_row())

        else:
            result = self.objects.set_and_get_raw(
                self._uuid,
                self._version,
                **self.as_row(),
            )
        for k, v in result.items():
            setattr(self, k, v)
