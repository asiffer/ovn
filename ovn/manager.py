from functools import cached_property
from typing import TYPE_CHECKING, Any, TypeVar

from ovn.client import OVNClient

if TYPE_CHECKING:
    from ovn.models.base import Model

    T = TypeVar("T", bound=Model)
else:
    T = TypeVar("T", bound="Model")


class Manager[T: "Model"]:
    """The manager handles the interaction with the database"""

    def __init__(self, model_cls: type[T]) -> None:
        # Nothing here touches the database: the table name is a pure string
        # transform of the class name. The schema (and the socket round-trip it
        # needs) is fetched lazily on first real use via the cached properties
        # below, so importing the models never blocks on a reachable DB.
        self.model_cls = model_cls
        self._table = model_cls._table()

    @cached_property
    def client(self) -> OVNClient:
        return OVNClient()

    @cached_property
    def _attributes(self) -> list[str]:
        return list(self.client.schema.tables[self._table].columns.keys())

    @cached_property
    def _mutable_attributes(self) -> list[str]:
        return [
            k
            for k, v in self.client.schema.tables[self._table].columns.items()
            if v.mutable
        ]

    def list(self) -> list[T]:
        """List all the objects"""
        return [self.model_cls(**r) for r in self.client.select(table=self._table)]

    def get(self, uuid: str) -> T | None:
        """Query object by uuid"""
        raw = self.get_raw(uuid)
        if raw is None:
            return None
        return self.model_cls(**raw)

    def set_and_get_raw(self, uuid: str, version: str, **kwargs):
        """Set the attributes of an object and return the updated
        raw object"""
        self.client.set(
            table=self._table,
            uuid=uuid,
            row=kwargs,
        )
        return self.client.wait_and_get(self._table, uuid, version)

    def get_raw(self, uuid: str) -> dict[str, Any] | None:
        """Query object by uuid. Return the raw object"""
        r = self.client.get(table=self._table, uuid=uuid)
        if len(r) == 0:
            return None
        return r

    def create_raw(self, **kwargs) -> dict[str, Any]:
        """Insert a new row in the database and
        return the raw object (its atrtributes basically)"""
        r = self.client.create(table=self._table, row=kwargs)
        return r[0]

    def create(self, **kwargs) -> T:
        """Create a new indstance of the object in the database
        and return the python object"""
        return self.model_cls(**self.create_raw(**kwargs))

    def get_by_name(self, name: str) -> T | None:
        """Query object by name (when relevant)"""
        if "name" not in self._mutable_attributes:
            raise AttributeError(
                f'"name" is not an attribute of class {self.model_cls}'
            )
        r = self.client.get_by_name(table=self._table, name=name)
        if len(r) == 0:
            return None
        return self.model_cls(**r)

    def delete(self, uuid: str) -> None:
        """Remove an object"""
        self.client.delete(self._table, uuid)
