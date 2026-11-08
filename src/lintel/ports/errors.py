"""Safe fixed errors exposed across the neutral execution boundary."""

from typing import Literal

ExecutionErrorCode = Literal[
    "INVALID",
    "DENIED",
    "CONFLICT",
    "PRECONDITION_FAILED",
    "CONFIRMATION_REQUIRED",
    "UNSUPPORTED",
    "API_MISMATCH",
    "INVALID_CURSOR",
    "TOO_MANY_ROWS",
    "LIMIT_EXCEEDED",
    "BUSY",
    "NOT_YET_CURRENT",
]

_CODES = frozenset(
    {
        "INVALID",
        "DENIED",
        "CONFLICT",
        "PRECONDITION_FAILED",
        "CONFIRMATION_REQUIRED",
        "UNSUPPORTED",
        "API_MISMATCH",
        "INVALID_CURSOR",
        "TOO_MANY_ROWS",
        "LIMIT_EXCEEDED",
        "BUSY",
        "NOT_YET_CURRENT",
    }
)


class ExecutionError(Exception):
    """An execution refusal with a fixed public code and optional safe reference."""

    __slots__ = ("code", "safe_reference")

    code: ExecutionErrorCode
    safe_reference: str | None

    def __init__(self, code: ExecutionErrorCode, safe_reference: str | None = None) -> None:
        if code not in _CODES:
            raise ValueError("invalid execution error code")
        if safe_reference is not None and (not safe_reference or "\x00" in safe_reference):
            raise ValueError("invalid safe reference")
        self.code = code
        self.safe_reference = safe_reference
        super().__init__(code)

    def __str__(self) -> str:
        return self.code
