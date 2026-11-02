"""Dynamic Strawberry construction from a direct UMF scalar projection.

The query and echo mutation are laboratory probes, not admitted UMF operations.
They must never be mounted as a production API.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, NewType
from uuid import UUID

import strawberry
from graphql import lexicographic_sort_schema, print_schema
from strawberry.schema.config import StrawberryConfig

from spikes.direct_umf.projection import Projection

DecimalText = NewType("DecimalText", str)
UUIDText = NewType("UUIDText", str)


def decimal_text(value: object) -> DecimalText:
    if not isinstance(value, str) or not re.fullmatch(
        r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", value
    ):
        raise ValueError("Decimal requires exact finite JSON-number text")
    return DecimalText(value)


def uuid_text(value: object) -> UUIDText:
    if not isinstance(value, str) or str(UUID(value)) != value:
        raise ValueError("UUID requires canonical lowercase hyphenated text")
    return UUIDText(value)


SCALARS: dict[str, Any] = {
    "string": str,
    "boolean": bool,
    "decimal": DecimalText,
    "uuid": UUIDText,
}


def build_probe_schema(plan: Projection, row: Mapping[str, object]) -> strawberry.Schema:
    """No native I/O or executable imports selected by UMF content."""
    annotations: dict[str, Any] = {}
    input_body: dict[str, Any] = {"__annotations__": {}}
    output_body: dict[str, Any] = {"__annotations__": annotations}
    slots = [("field_" + str(i), field) for i, field in enumerate(plan.fields)]
    for slot, field in slots:
        value_type = SCALARS[field.scalar]
        annotation = value_type | None if field.optional else value_type
        annotations[slot] = annotation
        input_body["__annotations__"][slot] = annotation
        output_body[slot] = strawberry.field(name=field.name)
        input_body[slot] = (
            strawberry.field(name=field.name, default=strawberry.UNSET)
            if field.optional
            else strawberry.field(name=field.name)
        )
    output_type = strawberry.type(type(plan.name, (), output_body))
    input_type = strawberry.input(type(plan.name + "Input", (), input_body))

    def probe() -> Any:
        return output_type(
            **{slot: row.get(f.name) if f.optional else row[f.name] for slot, f in slots}
        )

    def echo(input: Any) -> PresenceProbe:
        # Omission remains distinct from explicit null before the executor boundary.
        return PresenceProbe(
            omitted=any(getattr(input, slot) is strawberry.UNSET for slot, _ in slots),
            explicit_null=any(getattr(input, slot) is None for slot, _ in slots),
        )

    probe.__annotations__["return"] = output_type
    echo.__annotations__["input"] = input_type
    query = strawberry.type(type("Query", (), {"probe": strawberry.field(resolver=probe)}))
    mutation = strawberry.type(type("Mutation", (), {"echo": strawberry.mutation(resolver=echo)}))
    return strawberry.Schema(
        query,
        mutation=mutation,
        config=StrawberryConfig(auto_camel_case=False),
        scalar_overrides={
            DecimalText: strawberry.scalar(
                name="Decimal", serialize=decimal_text, parse_value=decimal_text
            ),
            UUIDText: strawberry.scalar(name="UUID", serialize=uuid_text, parse_value=uuid_text),
        },
    )


@strawberry.type
class PresenceProbe:
    omitted: bool
    explicit_null: bool


def export_sdl(schema: strawberry.Schema) -> str:
    # Public graphql-core schema construction from public Strawberry SDL.
    from graphql import build_schema

    return print_schema(lexicographic_sort_schema(build_schema(schema.as_str()))).rstrip() + "\n"
