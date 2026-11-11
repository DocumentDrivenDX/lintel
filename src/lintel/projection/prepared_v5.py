"""Version-selected `/8` connection metadata codec for prepared API five."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from lintel.projection.prepared_v2 import PreparedGeneratedRoot
from lintel.projection.prepared_v3 import (
    PreparedConnection,
)
from lintel.projection.prepared_v3 import (
    generated_connections_from_json as _generated_connections_from_json,
)
from lintel.projection.prepared_v3 import (
    join_generated_connections as _join_generated_connections,
)

if TYPE_CHECKING:
    from lintel.projection.prepared import PreparedRecord

READ_PROFILE = "weft.generated-read-algebra/8"


def generated_connections_from_json(
    value: object, *, expected_read_profile: str = READ_PROFILE
) -> tuple[PreparedConnection, ...]:
    return _generated_connections_from_json(value, expected_read_profile=expected_read_profile)


def join_generated_connections(
    records: Sequence[PreparedRecord],
    roots: Sequence[PreparedGeneratedRoot],
    connections: Sequence[PreparedConnection],
    sources: Sequence[tuple[str, str]],
    scalar_codec_profile: str,
    *,
    expected_read_profile: str = READ_PROFILE,
) -> None:
    _join_generated_connections(
        records,
        roots,
        connections,
        sources,
        scalar_codec_profile,
        expected_read_profile=expected_read_profile,
    )
