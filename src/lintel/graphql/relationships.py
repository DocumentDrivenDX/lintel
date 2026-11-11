"""Collect relationship lookups only within one GraphQL request."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from typing import cast

from graphql import GraphQLError, GraphQLObjectType, GraphQLResolveInfo, GraphQLSchema

from lintel.ports import ElementRef, NodeKey, NodeValue, RequestSession
from lintel.projection.prepared import AdmittedPreparedApi, PreparedRecord
from lintel.projection.relationships import PreparedRelationship

ResolveInfo = GraphQLResolveInfo[dict[str, object]]
_Select = Callable[[ResolveInfo, PreparedRecord], tuple[ElementRef, ...]]
_BatchKey = tuple[PreparedRelationship, tuple[ElementRef, ...]]
_Pending = list[tuple[NodeKey, asyncio.Future[NodeValue | None]]]


def install_relationships(
    schema: GraphQLSchema,
    prepared: AdmittedPreparedApi,
    records: Mapping[ElementRef, PreparedRecord],
    select: _Select,
    maximum: int,
) -> None:
    for route in prepared.relationships:
        source = records[route.source]
        target = records[route.target]
        parent = cast(GraphQLObjectType, schema.get_type(source.type_name))
        parent.fields[route.name].resolve = _resolver(route, target, select, maximum)


def _resolver(
    route: PreparedRelationship, target: PreparedRecord, select: _Select, maximum: int
) -> Callable[..., object]:
    async def resolve(parent: NodeValue, info: ResolveInfo) -> NodeValue | None:
        if type(parent) is not NodeValue or parent.key.record != route.source:
            raise _error("API_MISMATCH")
        fields = select(info, target)
        pending = cast(
            dict[_BatchKey, _Pending], info.context.setdefault("relationship_batches", {})
        )
        identity = (route, fields)
        queue = pending.get(identity)
        future = asyncio.get_running_loop().create_future()
        if queue is not None:
            if len(queue) >= maximum:
                raise _error("LIMIT_EXCEEDED")
            queue.append((parent.key, future))
            return await future

        queue = [(parent.key, future)]
        pending[identity] = queue
        try:
            await asyncio.sleep(0)
            pending.pop(identity, None)
            values = await _dispatch(info, route, target, fields, tuple(key for key, _ in queue))
        except BaseException as error:
            pending.pop(identity, None)
            _reject_waiters(queue[1:], error)
            raise
        for (_, waiting), value in zip(queue[1:], values[1:], strict=True):
            if not waiting.done():
                waiting.set_result(value)
        return values[0]

    return resolve


def _reject_waiters(queue: _Pending, error: BaseException) -> None:
    for _, waiting in queue:
        if waiting.done():
            continue
        if isinstance(error, Exception):
            waiting.set_exception(error)
        else:
            waiting.cancel()


async def _dispatch(
    info: ResolveInfo,
    route: PreparedRelationship,
    target: PreparedRecord,
    fields: tuple[ElementRef, ...],
    keys: tuple[NodeKey, ...],
) -> tuple[NodeValue | None, ...]:
    session = cast(RequestSession, info.context["session"])
    gate = cast(asyncio.Semaphore, info.context["dispatch_semaphore"])
    async with gate:
        values = await session.related_many(route.operation, keys, route.target, fields)
    if len(values) != len(keys) or any(
        value is not None
        and (
            type(value) is not NodeValue
            or value.key.record != route.target
            or value.key.key_id != target.key_id
            or len(value.key.components) != len(target.key_fields)
            or set(value.fields) != set(fields)
        )
        for value in values
    ):
        raise _error("UNSUPPORTED")
    return values


def _error(code: str) -> GraphQLError:
    return GraphQLError(code, extensions={"code": code})
