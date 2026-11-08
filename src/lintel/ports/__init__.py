"""Public neutral execution ports for host-owned Lintel request execution.

This package defines types and protocols only. It does not construct schemas,
acquire native resources, authorize operations, or execute UMF declarations.
"""

from lintel.ports.errors import ExecutionError, ExecutionErrorCode
from lintel.ports.protocols import (
    ExecutionPort,
    NodeCodec,
    PlannedExecutionPort,
    PlannedRequestSession,
    RequestSession,
)
from lintel.ports.values import (
    Arguments,
    CommandResult,
    ConnectionIntent,
    ConnectionPage,
    CoreLiteral,
    Edge,
    ElementRef,
    NodeKey,
    NodeValue,
    OperationRef,
    RequestScope,
)

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
    "NodeCodec",
    "PlannedExecutionPort",
    "PlannedRequestSession",
    "NodeKey",
    "NodeValue",
    "OperationRef",
    "RequestScope",
    "RequestSession",
]
