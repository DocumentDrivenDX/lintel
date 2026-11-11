"""Lintel GraphQL projection and neutral host-owned execution ports."""

from importlib.metadata import PackageNotFoundError, version

from lintel import ports
from lintel.node_id import StringKeyNodeCodec
from lintel.ports import (
    Arguments,
    CommandResult,
    ConnectionIntent,
    ConnectionPage,
    CoreLiteral,
    Edge,
    ElementRef,
    ExecutionError,
    ExecutionErrorCode,
    ExecutionPort,
    NodeCodec,
    NodeKey,
    NodeValue,
    OperationRef,
    PlannedExecutionPort,
    PlannedRequestSession,
    RequestScope,
    RequestSession,
)

try:
    __version__ = version("lintel-api")
except PackageNotFoundError:  # source tree without installed metadata
    __version__ = "0+unknown"

__all__ = [
    "Arguments",
    "CommandResult",
    "ConnectionPage",
    "ConnectionIntent",
    "CoreLiteral",
    "Edge",
    "ElementRef",
    "ExecutionError",
    "ExecutionErrorCode",
    "ExecutionPort",
    "PlannedExecutionPort",
    "PlannedRequestSession",
    "NodeCodec",
    "NodeKey",
    "NodeValue",
    "OperationRef",
    "RequestScope",
    "RequestSession",
    "StringKeyNodeCodec",
    "ports",
]
