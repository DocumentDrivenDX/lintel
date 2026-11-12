"""Pin the contract generated for selected records and declared commands."""

from typing import Any, cast

from jsonschema import Draft202012Validator

from lintel.build import http_projection
from lintel.ports import ElementRef, OperationRef
from lintel.projection.prepared import PreparedField, PreparedRecord
from lintel.projection.prepared_commands import PreparedTableCommand, TableCommandParameter


def test_http_contract_tracks_exposed_field_names_and_command_phases() -> None:
    ref = ElementRef("board", "Task")
    key = ElementRef("board", "taskKey")
    amount = ElementRef("board", "amount")
    lookup = OperationRef("board", "Task", "record")
    command = PreparedTableCommand(
        "completeTask",
        OperationRef("board", "completeTask", "table"),
        (TableCommandParameter("task", "string", True),),
    )

    def project(field: str) -> tuple[dict[str, object], ...]:
        record = PreparedRecord(
            ref,
            "primary",
            (key,),
            "Task",
            lookup,
            (PreparedField(amount, field, "decimal", False),),
        )
        _, operations = http_projection._project(  # pyright: ignore[reportPrivateUsage]
            (record,), (), (command,), 10, "digest"
        )
        return operations

    read, invoke, observe = project("estimate")
    renamed, _, _ = project("renamedEstimate")
    assert [item["name"] for item in (read, invoke, observe)] == [
        "get_task",
        "complete_task",
        "observe_complete_task",
    ]
    payload = {
        "data": {"type": "Task", "id": "opaque", "attributes": {"estimate": "9007199254740993.01"}}
    }
    assert _valid(read["outputSchema"], payload)
    assert not _valid(renamed["outputSchema"], payload)
    arguments = {"task": "t1", "invocationKey": "request", "confirmation": "approval"}
    assert _valid(invoke["inputSchema"], arguments)
    assert not _valid(observe["inputSchema"], arguments)
    del arguments["confirmation"]
    assert _valid(observe["inputSchema"], arguments)


def _valid(schema: object, value: object) -> bool:
    validator = cast(Any, Draft202012Validator(cast(dict[str, Any], schema)))
    return cast(bool, validator.is_valid(value))
