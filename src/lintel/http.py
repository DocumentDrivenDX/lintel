"""JSON:API and named command ingress over the host's admitted execution port."""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable, Mapping
from types import MappingProxyType
from typing import cast
from urllib.parse import urlencode

from fastapi import APIRouter, Request, Response
from graphql import GraphQLError

from lintel.graphql.commands import (
    CommandParameter,
    check_control,
    command_argument,
    command_outcome,
    rejected_command,
)
from lintel.graphql.resolvers import decode_node_key, encode_node_key, limit, scalar_value
from lintel.graphql.router import check_runtime_profiles, reject_constant, valid_scope
from lintel.ports import (
    ConnectionIntent,
    ElementRef,
    ExecutionError,
    NodeKey,
    NodeValue,
    RequestScope,
)
from lintel.ports.protocols import (
    ExecutionPort,
    NodeCodec,
    PlannedExecutionPort,
    PlannedRequestSession,
    RequestSession,
)
from lintel.projection.prepared import AdmittedPreparedApi, PreparedField, PreparedRecord
from lintel.projection.prepared_commands import PreparedTableCommand
from lintel.projection.prepared_v3 import PreparedConnection
from lintel.projection.relationships import PreparedRelationship

Json = dict[str, object]
ResolveScope = Callable[[Request, str], Awaitable[RequestScope]]
Handler = Callable[[Request, RequestScope], Awaitable[Json]]
JSON_API = "application/vnd.api+json"


def operation_name(value: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", value).lower()


def create_router(
    prepared: AdmittedPreparedApi,
    executor: ExecutionPort,
    codec: NodeCodec,
    resolve_scope: ResolveScope,
) -> APIRouter:
    """Mount under the same authenticated ingress as the GraphQL router."""
    if type(prepared) is not AdmittedPreparedApi or prepared.version != "lintel.prepared-api/5":
        raise ValueError("API_MISMATCH")
    check_runtime_profiles(prepared, executor, codec)
    if not callable(getattr(executor, "session_planned", None)):
        raise ValueError("API_MISMATCH")
    api = _Api(prepared, executor, codec)
    if any(
        {"id", "type", "lid"} & {field.name for field in record.fields}
        for record in api.records.values()
    ):
        raise ValueError("API_MISMATCH")
    router = APIRouter()
    for record in api.records.values():
        router.add_api_route(
            f"/records/{record.type_name}/{{id}}",
            _endpoint(api, resolve_scope, api.get(record), "GET"),
            methods=["GET"],
            include_in_schema=False,
        )
    by_lookup = {record.lookup: record for record in api.records.values()}
    for route in cast(tuple[PreparedConnection, ...], prepared.generated_connections):
        router.add_api_route(
            f"/collections/{route.name}",
            _endpoint(api, resolve_scope, api.page(by_lookup[route.lookup], route), "GET"),
            methods=["GET"],
            include_in_schema=False,
        )
    names: set[str] = set()
    for command in cast(tuple[PreparedTableCommand, ...], prepared.commands):
        for observe in (False, True):
            name = ("observe_" if observe else "") + operation_name(command.name)
            if name in names:
                raise ValueError("API_MISMATCH")
            names.add(name)
            router.add_api_route(
                f"/operations/{name}",
                _endpoint(
                    api, resolve_scope, api.command(command, observe), "POST", mutation=not observe
                ),
                methods=["POST"],
                include_in_schema=False,
            )
    return router


def _endpoint(
    api: _Api,
    resolve: ResolveScope,
    handle: Handler,
    method: str,
    *,
    mutation: bool = False,
) -> Callable[[Request], Awaitable[Response]]:
    async def endpoint(request: Request) -> Response:
        media = JSON_API if method == "GET" else "application/json"
        prepared = api.prepared
        try:
            scope = await resolve(request, prepared.api_digest)
        except Exception:
            scope = None
        if scope is None or not valid_scope(scope, prepared):
            return Response(status_code=403)
        if request.headers.get("x-lintel-api") != prepared.api_digest:
            return _error(media, 412, "API_MISMATCH")
        try:
            value = await handle(request, scope._replace(kind="mutation" if mutation else "query"))
            body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
            if len(body) > limit(prepared, "responseBytes"):
                raise ExecutionError("LIMIT_EXCEEDED")
            return Response(body, media_type=media, headers={"cache-control": "no-store"})
        except _MissingResource:
            return _error(media, 404, "NOT_FOUND")
        except ExecutionError as error:
            status = {"DENIED": 403, "BUSY": 503, "LIMIT_EXCEEDED": 413}.get(error.code, 400)
            return _error(media, status, error.code)
        except GraphQLError:
            return _error(media, 503, "BUSY")

    return endpoint


def _error(media: str, status: int, code: str) -> Response:
    return Response(
        json.dumps({"errors": [{"status": str(status), "code": code}]}),
        status_code=status,
        media_type=media,
        headers={"cache-control": "no-store"},
    )


class _MissingResource(Exception):
    pass


class _Api:
    def __init__(self, prepared: AdmittedPreparedApi, executor: ExecutionPort, codec: NodeCodec):
        self.prepared, self.executor, self.codec = prepared, executor, codec
        records = cast(tuple[PreparedRecord, ...], prepared.records)
        self.records = {record.source: record for record in records}
        self.relationships = cast(tuple[PreparedRelationship, ...], prepared.relationships)

    def encode(self, key: NodeKey) -> str:
        return encode_node_key(self.codec, self.prepared, key)

    def get(self, record: PreparedRecord) -> Handler:
        async def handle(request: Request, scope: RequestScope) -> Json:
            include = self.include(record, request, {"include"})
            key = decode_node_key(
                self.codec, self.prepared, request.path_params["id"], self.records
            )
            if key is None or key.record != record.source:
                raise _MissingResource
            async with self.executor.session(scope) as session:
                rows = await session.get_many(record.lookup, (key,), _refs(record.fields))
                if len(rows) != 1 or (rows[0] is not None and rows[0].key != key):
                    raise ExecutionError("UNSUPPORTED")
                if rows[0] is None:
                    raise _MissingResource
                resources, included = await self.resources(
                    session, record, record.fields, (rows[0],), include
                )
                return _document(resources[0], included, include)

        return handle

    def page(self, record: PreparedRecord, route: PreparedConnection) -> Handler:
        async def handle(request: Request, scope: RequestScope) -> Json:
            include = self.include(record, request, {"page[size]", "page[after]", "include"})
            query = request.query_params
            first = query.get("page[size]", "")
            after = query.get("page[after]")
            if not first.isascii() or not first.isdecimal() or len(first) > 6:
                raise ExecutionError("INVALID")
            count = int(first)
            if not 1 <= count <= limit(self.prepared, "maxPage"):
                raise ExecutionError("LIMIT_EXCEEDED")
            if after is not None:
                check_control(after, limit(self.prepared, "cursorBytes"))
            fields = tuple(field for field in record.fields if field.source in route.field_refs)
            intent = ConnectionIntent(
                route.name,
                route.name,
                route.lookup,
                MappingProxyType({}),
                count,
                after,
                _refs(fields),
            )
            port = cast(PlannedExecutionPort, self.executor)
            async with port.session_planned(scope, (intent,)) as session:
                page = await cast(PlannedRequestSession, session).planned_connection(intent)
                if len(page.edges) > count or (page.has_next_page and not page.edges):
                    raise ExecutionError("UNSUPPORTED")
                resources, included = await self.resources(
                    session, record, fields, tuple(edge.node for edge in page.edges), include
                )
                cursor = page.edges[-1].cursor if page.has_next_page else None
                if cursor is not None:
                    check_control(cursor, limit(self.prepared, "cursorBytes"))
                next_link = (
                    request.url.path + "?" + urlencode(dict(query) | {"page[after]": cursor})
                    if cursor is not None
                    else None
                )
                return _document(resources, included, include) | {"links": {"next": next_link}}

        return handle

    def include(
        self, record: PreparedRecord, request: Request, keys: set[str]
    ) -> PreparedRelationship | None:
        params = request.query_params.multi_items()
        if len(params) != len({key for key, _ in params}) or any(
            key not in keys for key, _ in params
        ):
            raise ExecutionError("INVALID")
        name = request.query_params.get("include")
        if name is None:
            return None
        for route in self.relationships:
            if route.name == name and route.source == record.source:
                return route
        raise ExecutionError("INVALID")

    async def resources(
        self,
        session: RequestSession,
        record: PreparedRecord,
        fields: tuple[PreparedField, ...],
        rows: tuple[NodeValue, ...],
        include: PreparedRelationship | None,
    ) -> tuple[list[Json], list[Json]]:
        resources = [self.resource(record, fields, row) for row in rows]
        if include is None or not rows:
            return resources, []
        if len(rows) > limit(self.prepared, "relationshipBatch"):
            raise ExecutionError("LIMIT_EXCEEDED")
        target = self.records[include.target]
        children = await session.related_many(
            include.operation, tuple(row.key for row in rows), include.target, _refs(target.fields)
        )
        if len(children) != len(rows):
            raise ExecutionError("UNSUPPORTED")
        included: dict[object, Json] = {}
        for parent, child in zip(resources, children, strict=True):
            link = None
            if child is not None:
                resource = self.resource(target, target.fields, child)
                included[resource["id"]] = resource
                link = {"type": resource["type"], "id": resource["id"]}
            cast(Json, parent["relationships"])[include.name] = {"data": link}
        return resources, list(included.values())

    def resource(
        self, record: PreparedRecord, fields: tuple[PreparedField, ...], row: NodeValue
    ) -> Json:
        if (
            type(row) is not NodeValue
            or row.key.record != record.source
            or row.key.key_id != record.key_id
            or len(row.key.components) != len(record.key_fields)
            or set(row.fields) != set(_refs(fields))
        ):
            raise ExecutionError("UNSUPPORTED")
        attrs = {
            field.name: (
                None
                if field.nullable and row.fields[field.source] is None
                else scalar_value(row, field.source, field.scalar)
            )
            for field in fields
        }
        resource: Json = {"type": record.type_name, "id": self.encode(row.key), "attributes": attrs}
        if any(route.source == record.source for route in self.relationships):
            resource["relationships"] = {}
        return resource

    def command(self, command: PreparedTableCommand, observe: bool) -> Handler:
        async def handle(request: Request, scope: RequestScope) -> Json:
            value = await _body(request, limit(self.prepared, "requestBytes"))
            key, approval = _command_controls(value, command, observe)
            args = {
                p.name: command_argument(
                    CommandParameter(p.name, p.scalar), value[p.name], lambda _: None
                )
                for p in command.parameters
                if p.name in value
            }
            try:
                async with self.executor.session(scope) as session:
                    result = (
                        await session.observe(command.operation, args, key)
                        if observe
                        else await session.invoke(command.operation, args, key, approval)
                    )
                    outcome = command_outcome(result, key, self.encode, observe)
            except ExecutionError as error:
                outcome = (
                    {"__typename": "CommandUnknown", "invocationKey": key}
                    if not observe and error.code in {"BUSY", "NOT_YET_CURRENT"}
                    else rejected_command(key, error)
                )
            return _command_document(outcome)

        return handle


def _command_document(outcome: Mapping[str, object]) -> Json:
    status = {
        "CommandApplied": "applied",
        "CommandRecovered": "recovered",
        "CommandUnknown": "unknown",
        "CommandRejected": "rejected",
        "CommandNotObserved": "not-observed",
    }[cast(str, outcome["__typename"])]
    durability = cast(str, outcome.get("durability", "UNKNOWN" if status == "unknown" else "NONE"))
    return {
        "status": status,
        "invocationKey": outcome["invocationKey"],
        "durability": durability.lower().replace("_", "-"),
        "receipt": outcome.get("receipt"),
        "affectedIds": outcome.get("affectedIds", []),
        "code": outcome.get("code"),
        "confirmation": outcome.get("confirmation"),
    }


def _command_controls(
    value: Json, command: PreparedTableCommand, observe: bool
) -> tuple[str, str | None]:
    permitted = {p.name for p in command.parameters} | {"invocationKey"}
    if not observe:
        permitted.add("confirmation")
    if set(value) - permitted or any(
        p.required and value.get(p.name) is None for p in command.parameters
    ):
        raise ExecutionError("INVALID")
    key, confirmation = value.get("invocationKey"), value.get("confirmation")
    if not isinstance(key, str) or (confirmation is not None and not isinstance(confirmation, str)):
        raise ExecutionError("INVALID")
    check_control(key, 128)
    if confirmation is not None:
        check_control(confirmation, 2048)
    return key, confirmation


async def _body(request: Request, maximum: int) -> Json:
    if request.headers.get("content-type", "").split(";", 1)[0] != "application/json":
        raise ExecutionError("INVALID")
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > maximum:
            raise ExecutionError("LIMIT_EXCEEDED")
        data.extend(chunk)
    try:
        value: object = json.loads(
            data.decode("utf-8"), object_pairs_hook=_unique, parse_constant=reject_constant
        )
    except ValueError as error:
        raise ExecutionError("INVALID") from error
    if not isinstance(value, dict):
        raise ExecutionError("INVALID")
    return cast(Json, value)


def _unique(pairs: list[tuple[str, object]]) -> Json:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON member")
    return result


def _refs(fields: tuple[PreparedField, ...]) -> tuple[ElementRef, ...]:
    return tuple(field.source for field in fields)


def _document(data: object, included: list[Json], include: PreparedRelationship | None) -> Json:
    return {"data": data, "included": included} if include is not None else {"data": data}
