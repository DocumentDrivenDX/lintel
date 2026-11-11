from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from lintel.experimental.projection import ProjectionError, project
from lintel.experimental.schema import build_probe_schema, export_sdl

SOURCE = Path(__file__).resolve().parents[1] / "src/lintel/examples/task-board/task-board.umf.json"
FIELDS = {("board", "title"): "title", ("board", "estimate"): "estimate", ("board", "note"): "note"}


def model() -> dict[str, Any]:
    return json.loads(SOURCE.read_text())


def test_direct_umf_export_is_deterministic_and_preserves_source() -> None:
    # Partial evidence for US-001-AC1; not production activation conformance.
    text = SOURCE.read_text()
    plan = project(text, ("board", "Task"), "Task", FIELDS)
    row = {"title": "Fabricated", "estimate": "9007199254740993.01", "note": None}
    schema = build_probe_schema(plan, row)
    reverse = project(text, ("board", "Task"), "Task", dict(reversed(list(FIELDS.items()))))
    assert export_sdl(schema) == export_sdl(build_probe_schema(reverse, row))
    result = schema.execute_sync("{ probe { title estimate note } }")
    assert not result.errors
    assert result.data == {"probe": row}
    assert plan.source_text == text
    assert "nativeId" not in export_sdl(schema)


@pytest.mark.parametrize(
    ("optional", "expected"),
    [
        ({}, {"omitted": True, "explicit_null": False}),
        ({"note": None}, {"omitted": False, "explicit_null": True}),
        ({"note": "hello"}, {"omitted": False, "explicit_null": False}),
    ],
)
def test_omission_and_null_survive_dynamic_inputs(
    optional: dict[str, object], expected: dict[str, bool]
) -> None:
    plan = project(SOURCE.read_text(), ("board", "Task"), "Task", FIELDS)
    schema = build_probe_schema(plan, {})
    result = schema.execute_sync(
        "mutation($input: TaskInput!) { echo(input: $input) { omitted explicit_null } }",
        variable_values={"input": {"title": "X", "estimate": "9007199254740993.01", **optional}},
    )
    assert not result.errors
    assert result.data == {"echo": expected}


@pytest.mark.parametrize(
    ("value", "literal", "accepted"),
    [
        ("9007199254740993.01", '"9007199254740993.01"', True),
        ("1e-100", '"1e-100"', True),
        ("-0.00", '"-0.00"', True),
        (1.5, "1.5", False),
        ("NaN", '"NaN"', False),
        ("01", '"01"', False),
    ],
)
def test_decimal_variables_and_literals_use_same_exact_codec(
    value: object,
    literal: str,
    accepted: bool,
) -> None:
    plan = project(SOURCE.read_text(), ("board", "Task"), "Task", FIELDS)
    schema = build_probe_schema(plan, {})
    variable_result = schema.execute_sync(
        "mutation($input: TaskInput!) { echo(input: $input) { omitted } }",
        variable_values={"input": {"title": "X", "estimate": value}},
    )
    literal_result = schema.execute_sync(
        'mutation { echo(input: {title: "X", estimate: ' + literal + "}) { omitted } }",
    )
    assert (not variable_result.errors) is accepted
    assert (not literal_result.errors) is accepted


def test_uuid_is_read_from_umf_not_handwritten_graphql_type() -> None:
    data = model()
    data["modules"][0]["elements"][0]["scalarType"] = "uuid"
    plan = project(json.dumps(data), ("board", "Task"), "Task", {("board", "taskKey"): "nativeId"})
    value = "123e4567-e89b-12d3-a456-426614174000"
    schema = build_probe_schema(plan, {"nativeId": value})
    assert "nativeId: UUID!" in export_sdl(schema)
    result = schema.execute_sync("{ probe { nativeId } }")
    assert not result.errors
    assert result.data == {"probe": {"nativeId": value}}
    result = schema.execute_sync('mutation { echo(input: {nativeId: "not-a-uuid"}) { omitted } }')
    assert result.errors


@pytest.mark.parametrize(
    "change", ["selected-unknown", "collision", "relay-id", "not-member", "container"]
)
def test_unsupported_selection_refuses_without_source_mutation(change: str) -> None:
    # Partial evidence for US-001-AC2/AC4; incomplete semantics fail closed.
    data = model()
    fields = dict(FIELDS)
    if change == "selected-unknown":
        data["modules"][0]["elements"][2]["futureConstraint"] = {"opaque": True}
    elif change == "collision":
        fields[("board", "estimate")] = "title"
    elif change == "relay-id":
        fields[("board", "title")] = "id"
    elif change == "not-member":
        fields[("board", "displayName")] = "personName"
    else:
        data["modules"][0]["elements"][2]["cardinality"] = "many"
    text = json.dumps(data)
    with pytest.raises((ProjectionError, ValueError)):
        project(text, ("board", "Task"), "Task", fields)
    assert json.dumps(data) == text


def test_invalid_core_is_rejected_by_existing_umf_validation() -> None:
    data = model()
    data["modules"][0]["elements"][2]["scalarType"] = "made-up"
    with pytest.raises((ProjectionError, ValueError)):
        project(json.dumps(data), ("board", "Task"), "Task", FIELDS)


def test_qualified_references_do_not_merge_same_named_fields() -> None:
    data = model()
    data["modules"].append(
        {
            "id": "other",
            "namespace": "example.other",
            "elements": [
                {
                    "id": "title",
                    "name": "title",
                    "kind": "field",
                    "scalarType": "boolean",
                    "cardinality": "one",
                    "nullability": "required",
                    "extensions": {},
                }
            ],
            "relationships": [],
            "extensions": {},
        }
    )
    plan = project(json.dumps(data), ("board", "Task"), "Task", {("board", "title"): "title"})
    assert plan.fields[0].source == ("board", "title")
    assert "title: String!" in export_sdl(build_probe_schema(plan, {"title": "Exact record"}))
    with pytest.raises(ProjectionError, match="not a record member"):
        project(json.dumps(data), ("board", "Task"), "Task", {("other", "title"): "title"})


@pytest.mark.parametrize("name", ["class", "from", "snake_case", "camelCase"])
def test_graphql_names_are_independent_of_python_identifiers(name: str) -> None:
    plan = project(SOURCE.read_text(), ("board", "Task"), "Task", {("board", "title"): name})
    schema = build_probe_schema(plan, {name: "Faithful name"})
    result = schema.execute_sync("{ probe { " + name + " } }")
    assert not result.errors
    assert result.data == {"probe": {name: "Faithful name"}}


@pytest.mark.parametrize(
    ("property_name", "value"),
    [
        ("nullability", None),
        ("nullability", "unspecified"),
        ("nullability", "future"),
        ("cardinality", None),
        ("cardinality", "unspecified"),
        ("scalarType", None),
    ],
)
def test_unasserted_meaning_never_becomes_a_required_scalar(
    property_name: str,
    value: str | None,
) -> None:
    data = model()
    field = data["modules"][0]["elements"][2]
    if value is None:
        field.pop(property_name)
    else:
        field[property_name] = value
    with pytest.raises(ProjectionError, match="UNSUPPORTED"):
        project(json.dumps(data), ("board", "Task"), "Task", FIELDS)
