"""Exercise source-derived command admission and GraphQL schema generation."""

import json
from pathlib import Path
from typing import Any

import pytest
from graphql import GraphQLInputObjectType, build_schema

from lintel.build.errors import PreparationError
from lintel.build.prepare import read_umf
from lintel.build.prepare_commands import prepare_table_commands
from lintel.projection.prepared_commands import admitted_commands, command_sdl


def test_selected_command_uses_declared_parameters_and_requires_observation_capability() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "src/lintel/examples/task-board/task-board.umf.json"
    document: dict[str, Any] = json.loads(path.read_bytes())
    _, fields = read_umf(path.read_bytes())
    declaration: dict[str, object] = {
        "version": "umf.table-operation/0.1",
        "id": "completeTask",
        "replay": "caller-key-required",
        "consistency": "transaction",
        "parameters": [
            {"id": "task", "field": {"module": "board", "element": "taskKey"}},
            {"id": "note", "field": {"module": "board", "element": "note"}},
        ],
        "body": {"kind": "update", "maxRows": 1},
    }
    document["modules"][0]["extensions"]["umf.tables"] = {"commands": [declaration]}
    selected = [
        {
            "name": "completeTask",
            "operation": {"module": "board", "id": "completeTask", "kind": "table"},
        }
    ]
    rows = prepare_table_commands(json.dumps(document).encode(), selected, fields)
    artifact: dict[str, object] = {"version": "lintel.prepared-api/5", "commands": list(rows)}
    capabilities = {
        "binding.profile": "test",
        "command.outcome": "1",
        "command.outcome.binding.profile": "test",
        "command.observe": "1",
        "command.observe.binding.profile": "test",
    }
    commands = admitted_commands(artifact, {"mutations": selected}, capabilities)
    schema = build_schema(
        command_sdl("type Query { health: Boolean }", commands, has_decimal=False)
    )
    assert schema.mutation_type is not None
    assert str(schema.mutation_type.fields["completeTask"].type) == "CommandOutcome!"
    assert schema.query_type is not None
    assert str(schema.query_type.fields["observeCompleteTask"].type) == "CommandObservation!"
    input_type = schema.get_type("ObserveCompleteTaskInput")
    assert isinstance(input_type, GraphQLInputObjectType)
    assert set(input_type.fields) == {"task", "note", "invocationKey"}
    assert [(p.name, p.scalar, p.required) for p in commands[0].parameters] == [
        ("task", "string", True),
        ("note", "string", False),
    ]
    capabilities.pop("command.observe")
    with pytest.raises(ValueError, match="API_MISMATCH"):
        admitted_commands(artifact, {"mutations": selected}, capabilities)
    declaration["replay"] = "unsupported"
    with pytest.raises(PreparationError, match="UNSUPPORTED"):
        prepare_table_commands(json.dumps(document).encode(), selected, fields)
