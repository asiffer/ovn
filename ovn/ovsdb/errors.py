from typing import Any


class BaseError(Exception):
    pass


class OVSDBError(BaseError):
    """
    Error during the communication with the database
    """

    method: str
    error: str
    id: str | None
    result: list[Any]

    def __init__(
        self, method: str, error: str, id: str | None, result: list[Any]
    ) -> None:
        self.method = method
        self.error = error
        self.id = id
        self.result = result

    def __str__(self) -> str:
        msg = f"Error while requesting method '{self.method}': {self.error}\n"
        msg += f"Raw response: {self.result}"
        return msg


class TransactionError(BaseError):
    error: str
    issue: dict[str, str]
    details: str

    def __init__(
        self,
        error: str,
        details: str,
        issue: dict[str, str] | None = None,
    ) -> None:
        self.error = error
        self.details = details
        self.issue = issue or {}

    def __str__(self) -> str:
        msg = f"Error during transaction '{self.error}':{self.issue} ({self.details})\n"
        return msg


class EmptyResultError(BaseError):
    """
    Error when the result of a query is empty
    """

    def __init__(self, method: str | None = None) -> None:
        self.method = method

    def __str__(self) -> str:
        if self.method:
            return f"Method '{self.method}' returns no result"
        return "No result returned"
