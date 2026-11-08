"""FastAPI ingress for the production keyed-refetch GraphQL subset."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from inspect import isawaitable
from typing import Any, cast

import graphql
from fastapi import APIRouter, Request, Response
from graphql import ExecutionResult, GraphQLError, build_schema, parse, validate
from graphql.execution.values import VariableValues, get_variable_values
from graphql.language import OperationDefinitionNode

from lintel.graphql.preflight import BudgetFailure, collect_connection_intents, preflight
from lintel.graphql.resolvers import (
    install_resolvers,
    integer_limits,
    limit,
    mount,
    uses_introspection,
)
from lintel.node_id import StringKeyNodeCodec
from lintel.ports.errors import ExecutionError
from lintel.ports.protocols import ExecutionPort, NodeCodec, PlannedExecutionPort, RequestSession
from lintel.ports.values import ElementRef, RequestScope
from lintel.projection.prepared import AdmittedPreparedApi, PreparedRecord

_EXECUTE_ATTRIBUTE = "execute"
ResolveScope = Callable[[Any, str], Awaitable[RequestScope]]


def create_router(
    prepared: AdmittedPreparedApi,
    executor: ExecutionPort,
    node_codec: NodeCodec,
    resolve_context: ResolveScope,
) -> Any:
    """Build a POST endpoint using only the host's authenticated request context."""
    if type(prepared) is not AdmittedPreparedApi:
        raise ValueError("API_MISMATCH")
    _check_runtime_profiles(prepared, executor, node_codec)
    if prepared.version in {"lintel.prepared-api/3", "lintel.prepared-api/4"} and not callable(
        getattr(executor, "session_planned", None)
    ):
        raise ValueError("API_MISMATCH")
    router = APIRouter()
    records = {record.source: record for record in prepared.records}
    fields = {record.type_name: {f.name: f for f in record.fields} for record in prepared.records}
    schema = build_schema(prepared.sdl)
    install_resolvers(schema, prepared, records, fields, node_codec)
    route_mount = mount(prepared)

    @router.post(route_mount)
    async def graphql_endpoint(request: Request) -> Response:
        return await _handle_request(request, prepared, executor, resolve_context, schema, records)

    return router


def _check_runtime_profiles(
    prepared: AdmittedPreparedApi, executor: ExecutionPort, codec: NodeCodec
) -> None:
    caps = dict(prepared.capabilities)
    if codec.profile() != caps.get("identity.codec"):
        raise ValueError("API_MISMATCH")
    if prepared.version in {
        "lintel.prepared-api/2",
        "lintel.prepared-api/3",
        "lintel.prepared-api/4",
    } and (type(codec) is not StringKeyNodeCodec or not codec.registry_matches(prepared)):
        raise ValueError("API_MISMATCH")
    if dict(executor.capabilities()) != dict(prepared.capabilities):
        raise ValueError("API_MISMATCH")


async def _handle_request(
    request: Request,
    prepared: AdmittedPreparedApi,
    executor: ExecutionPort,
    resolve_scope: ResolveScope,
    schema: Any,
    records: Mapping[ElementRef, PreparedRecord],
) -> Response:
    body, error = await _read_request(request, prepared)
    if error is not None:
        return error
    scope, error = await _request_scope(request, body, prepared, resolve_scope)
    if error is not None:
        return error
    return await _execute_request(body, scope, prepared, executor, schema, records)


async def _read_request(
    request: Request, prepared: AdmittedPreparedApi
) -> tuple[dict[str, Any], Response | None]:
    error = _media_error(request)
    raw = bytearray()
    body: dict[str, Any] = {}
    if error is None:
        request_limit = limit(prepared, "requestBytes")
        async for chunk in request.stream():
            if len(raw) + len(chunk) > request_limit:
                error = _json_response(_safe_error("LIMIT_EXCEEDED"), 413)
                break
            raw.extend(chunk)
    if error is None:
        body, error = _decode_request(bytes(raw))
    if error is None:
        error = _check_document_size(body, prepared)
    return body, error


def _media_error(request: Request) -> Response | None:
    if (
        request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        != "application/json"
    ):
        return Response(status_code=415)
    accepted = (None, "*/*", "application/graphql-response+json", "application/json")
    return Response(status_code=406) if request.headers.get("accept") not in accepted else None


def _decode_request(raw: bytes) -> tuple[dict[str, Any], Response | None]:
    def pairs_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        decoded: dict[str, object] = {}
        for key, value in pairs:
            if key in decoded:
                raise ValueError("duplicate key")
            decoded[key] = value
        return decoded

    try:
        body = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=pairs_hook,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return {}, _json_response(_safe_error("INVALID"), 400)
    if not isinstance(body, dict):
        return {}, _json_response(_safe_error("INVALID"), 400)
    typed_body = cast(dict[str, Any], body)
    if set(typed_body) - {"query", "operationName", "variables", "extensions"}:
        return {}, _json_response(_safe_error("INVALID"), 400)
    return (
        (typed_body, None)
        if isinstance(typed_body.get("query"), str)
        else ({}, _json_response(_safe_error("INVALID"), 400))
    )


def _check_document_size(body: Mapping[str, Any], prepared: AdmittedPreparedApi) -> Response | None:
    query = body["query"]
    document_limit = limit(prepared, "documentBytes")
    return (
        _json_response(_safe_error("LIMIT_EXCEEDED"), 413)
        if len(query.encode("utf-8")) > document_limit
        else None
    )


async def _request_scope(
    request: Request,
    body: Mapping[str, Any],
    prepared: AdmittedPreparedApi,
    resolve_scope: ResolveScope,
) -> tuple[RequestScope | None, Response | None]:
    error: Response | None = _valid_request_metadata(body)
    scope: RequestScope | None = None
    if error is None:
        try:
            scope = await resolve_scope(request, prepared.api_digest)
        except Exception:
            error = Response(status_code=403)
    if error is None and (scope is None or not _valid_scope(scope, prepared)):
        error = Response(status_code=403)
    if error is None and request.headers.get("x-lintel-api") != prepared.api_digest:
        error = _json_response(_safe_error("API_MISMATCH"), 412)
    return scope if error is None else None, error


def _valid_request_metadata(body: Mapping[str, Any]) -> Response | None:
    for name, expected in (("variables", dict), ("operationName", str), ("extensions", dict)):
        value = body.get(name)
        if value is not None and not isinstance(value, expected):
            return _json_response(_safe_error("INVALID"), 400)
    if body.get("extensions"):
        return _json_response(_safe_error("INVALID"), 400)
    return None


def _reject_constant(value: str) -> object:
    raise ValueError("invalid JSON constant: " + value)


def _valid_scope(scope: RequestScope, prepared: AdmittedPreparedApi) -> bool:
    return (
        scope.application == prepared.application
        and scope.api_digest == prepared.api_digest
        and scope.authority is not None
        and bool(scope.request_id)
        and scope.deadline_monotonic > time.monotonic()
    )


async def _execute_request(
    body: Mapping[str, Any],
    scope: RequestScope | None,
    prepared: AdmittedPreparedApi,
    executor: ExecutionPort,
    schema: Any,
    records: Mapping[ElementRef, PreparedRecord],
) -> Response:
    assert scope is not None
    document, operation, variables, error = _parse_operation(body, prepared, schema)
    if error is not None:
        return error
    assert document is not None and operation is not None and variables is not None
    kind = "mutation" if operation.operation.value == "mutation" else "query"
    scope = scope._replace(kind=kind)
    try:
        intents = collect_connection_intents(schema, document, operation, variables, prepared)
    except BudgetFailure as error:
        return _json_response(_safe_error(error.code), 400)
    if intents:
        if not hasattr(executor, "session_planned"):
            raise ExecutionError("API_MISMATCH")
        session_manager: AbstractAsyncContextManager[RequestSession] = cast(
            PlannedExecutionPort, executor
        ).session_planned(scope, intents)
    else:
        session_manager = executor.session(scope)
    try:
        async with session_manager as session:
            consumed: set[str] = set()
            execute_graphql = cast(
                Callable[..., Awaitable[ExecutionResult] | ExecutionResult],
                getattr(graphql, _EXECUTE_ATTRIBUTE),
            )
            result = execute_graphql(
                schema,
                document,
                variable_values=variables.coerced,
                operation_name=body.get("operationName"),
                context_value={
                    "session": session,
                    "scope": scope,
                    "variables": variables,
                    "dispatch_semaphore": asyncio.Semaphore(
                        limit(prepared, "maxConcurrentDispatch")
                    ),
                    "connection_intents": {intent.response_key: intent for intent in intents},
                    "consumed_connection_intents": consumed,
                },
            )
            if isawaitable(result):
                result = await result
            if len(consumed) != len(intents):
                raise ExecutionError("API_MISMATCH")
            response = _result_response(result, prepared)
        return response
    except ExecutionError as error:
        return _json_response(_safe_error(error.code), 200)
    except GraphQLError as error:
        return _json_response({"errors": [_public_graphql_error(error)]}, 400)
    except Exception:
        return _json_response(_safe_error("INTERNAL"), 500)


def _parse_operation(
    body: Mapping[str, Any], prepared: AdmittedPreparedApi, schema: Any
) -> tuple[Any, OperationDefinitionNode | None, VariableValues | None, Response | None]:
    document: Any = None
    operation: OperationDefinitionNode | None = None
    variable_values: VariableValues | None = None
    error: Response | None = None
    try:
        document = parse(body["query"])
    except GraphQLError as parse_error:
        error = _json_response({"errors": [_public_graphql_error(parse_error)]}, 400)
    if error is None:
        errors = validate(schema, document)
        if errors:
            error = _json_response(
                {"errors": [_public_graphql_error(item) for item in errors]}, 400
            )
    if error is None:
        operation, error = _select_operation(document, body, prepared)
    if error is None and operation is not None:
        variable_values, error = _resolve_variables(body, schema, operation)
    if error is None and operation is not None and variable_values is not None:
        error = _preflight_error(schema, document, operation, variable_values, prepared)
    return document, operation, variable_values, error


def _resolve_variables(
    body: Mapping[str, Any],
    schema: Any,
    operation: OperationDefinitionNode,
) -> tuple[VariableValues | None, Response | None]:
    raw_variables = body.get("variables")
    if raw_variables is None:
        raw_variables = {}
    if not isinstance(raw_variables, dict):
        return None, _json_response(_safe_error("INVALID"), 400)
    evaluated = get_variable_values(
        schema,
        operation.variable_definitions or (),
        cast(dict[str, Any], raw_variables),
        max_errors=8,
    )
    if isinstance(evaluated, list):
        return None, _json_response(
            {"errors": [_public_graphql_error(item) for item in evaluated]}, 400
        )
    return evaluated, None


def _preflight_error(
    schema: Any,
    document: Any,
    operation: OperationDefinitionNode,
    variables: VariableValues,
    prepared: AdmittedPreparedApi,
) -> Response | None:
    try:
        connection_fields = frozenset(route.name for route in prepared.generated_connections)
        preflight(
            schema,
            document,
            operation,
            variables,
            integer_limits(prepared),
            connection_fields,
        )
    except BudgetFailure as error:
        return _json_response(_safe_error(error.code), 400)
    return None


def _select_operation(
    document: Any, body: Mapping[str, Any], prepared: AdmittedPreparedApi
) -> tuple[OperationDefinitionNode | None, Response | None]:
    if not prepared.host_profile["introspection"] and uses_introspection(document):
        return None, _json_response(_safe_error("DENIED"), 400)
    operation = _selected_operation(document, body.get("operationName"))
    if operation is None:
        return None, _json_response(_safe_error("INVALID"), 400)
    return operation, None


def _result_response(result: Any, prepared: AdmittedPreparedApi) -> Response:
    payload: dict[str, object] = {}
    if result.data is not None:
        payload["data"] = result.data
    if result.errors:
        payload["errors"] = [_public_graphql_error(error) for error in result.errors]
    maximum = int(limit(prepared, "responseBytes"))
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    chunks: list[bytes] = []
    total = 0
    for chunk in encoder.iterencode(payload):
        encoded_chunk = chunk.encode("utf-8")
        total += len(encoded_chunk)
        if total > maximum:
            return _json_response(_safe_error("LIMIT_EXCEEDED"), 200)
        chunks.append(encoded_chunk)
    encoded = b"".join(chunks)
    return Response(encoded, status_code=200, media_type="application/graphql-response+json")


def _selected_operation(document: Any, name: str | None) -> OperationDefinitionNode | None:
    operations = [
        node for node in document.definitions if isinstance(node, OperationDefinitionNode)
    ]
    if name is not None:
        return next((node for node in operations if node.name and node.name.value == name), None)
    return operations[0] if len(operations) == 1 else None


def _public_graphql_error(error: GraphQLError) -> dict[str, object]:
    code = error.extensions.get("code") if error.extensions else None
    if isinstance(error.original_error, ExecutionError):
        code = error.original_error.code
    if code not in {
        "INVALID",
        "DENIED",
        "UNSUPPORTED",
        "API_MISMATCH",
        "LIMIT_EXCEEDED",
        "INVALID_CURSOR",
        "CONFLICT",
        "PRECONDITION_FAILED",
        "BUSY",
        "NOT_YET_CURRENT",
        "TOO_MANY_ROWS",
        "CONFIRMATION_REQUIRED",
    }:
        code = "INVALID"
    payload: dict[str, object] = {"message": code, "extensions": {"code": code}}
    if error.locations:
        payload["locations"] = [{"line": loc.line, "column": loc.column} for loc in error.locations]
    if error.path:
        payload["path"] = error.path
    return payload


def _safe_error(code: str) -> dict[str, object]:
    return {"errors": [{"message": code, "extensions": {"code": code}}]}


def _json_response(payload: Mapping[str, object], status: int) -> Any:
    return Response(
        json.dumps(payload, separators=(",", ":")),
        status_code=status,
        media_type="application/graphql-response+json",
    )
