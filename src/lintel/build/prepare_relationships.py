"""Join selected one-hop fields to their exact authored UMF declaration."""

from collections.abc import Mapping
from typing import Any, cast

from lintel.build.errors import PreparationError
from lintel.build.prepare import json_object
from lintel.projection.relationships import PreparedRelationship


def validate_relationships(source: bytes, selected: tuple[PreparedRelationship, ...]) -> None:
    if not selected:
        return
    document = json_object(source, "INVALID_EXPOSURE")
    inventory: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for module in document["modules"]:
        for relationship in module.get("relationships", ()):
            inventory.setdefault((module["id"], relationship["id"]), []).append(relationship)
    for route in selected:
        matches = inventory.get(route.relationship, [])
        if len(matches) != 1 or not _matches(matches[0], route):
            raise PreparationError("UNSUPPORTED", "/records/relationships")


def _matches(declared: Mapping[str, Any], route: PreparedRelationship) -> bool:
    source: object = declared.get("source")
    target: object = declared.get("target")
    if type(target) is not list:
        return False
    targets = cast(list[object], target)
    if len(targets) != 1 or type(targets[0]) is not dict:
        return False
    target_ref = cast(dict[str, object], targets[0])
    return (
        source == [{"module": route.source.module, "element": route.source.element}]
        and target_ref.get("module") == route.target.module
        and target_ref.get("element") == route.target.element
        and declared.get("directed") is True
        and declared.get("targetLifecycle") == "independent"
        and declared.get("targetMultiplicity") in ({"min": 0, "max": 1}, {"min": 1, "max": 1})
    )
