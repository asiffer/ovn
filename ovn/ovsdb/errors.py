from typing import Any, Dict, List, Optional


class OVSDBError(Exception):
    """
    Error during the communication with the database
    """

    method: str
    error: str
    id: Optional[str]
    result: List[Any]

    def __init__(
        self, method: str, error: str, id: Optional[str], result: List[Any]
    ) -> None:
        self.method = method
        self.error = error
        self.id = id
        self.result = result

    def __str__(self) -> str:
        msg = f"Error while requesting method '{self.method}': {self.error}\n"
        msg += f"Raw response: {self.result}"
        return msg


class TransactionError(Exception):
    error: str
    issue: Dict[str, str]
    details: str

    def __init__(self, error: str, details: str, issue: Dict[str, str] = {}) -> None:
        self.error = error
        self.details = details
        self.issue = issue

    def __str__(self) -> str:
        msg = f"Error during transaction '{self.error}':{self.issue} ({self.details})\n"
        return msg
