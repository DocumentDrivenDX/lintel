from __future__ import annotations

import base64
import json

import pytest

from lintel.node_id import PROFILE, StringKeyNodeCodec
from lintel.ports.values import ElementRef, NodeKey, OperationRef
from lintel.projection.prepared_v2 import PreparedGeneratedRoot


def test_string_key_codec_round_trips_canonical_utf8_identity() -> None:
    codec = StringKeyNodeCodec()
    key = NodeKey(ElementRef("mód", "Record"), "primary", ({"string": "välue"},))

    encoded = codec.encode("app.namespace", key)

    assert codec.profile() == PROFILE
    assert "=" not in encoded
    assert codec.decode("app.namespace", encoded) == key
    payload = json.loads(base64.urlsafe_b64decode(encoded + "=="))
    assert payload == [PROFILE, "app.namespace", "mód", "Record", "primary", ["välue"]]


@pytest.mark.parametrize(
    ("namespace", "key"),
    [
        ("", NodeKey(ElementRef("m", "R"), "k", ({"string": "x"},))),
        ("n", NodeKey(ElementRef("m", "R"), "k", (None,))),
        ("n", NodeKey(ElementRef("m", "R"), "k", ({"string": "x", "extra": 1},))),
        ("n", NodeKey(ElementRef("m", "R"), "k", ({"string": "\ud800"},))),
        ("n", NodeKey(ElementRef("m", "R"), "k", ({"string": "nul\x00value"},))),
        ("n", NodeKey(ElementRef("m", "R"), "k", tuple({"string": str(i)} for i in range(17)))),
    ],
)
def test_string_key_codec_refuses_unsupported_encode_values(namespace: str, key: NodeKey) -> None:
    with pytest.raises(ValueError):
        StringKeyNodeCodec().encode(namespace, key)


@pytest.mark.parametrize("value", ["=", "abc=", "!!!!", "e30", "eyAiYSI6MX0"])
def test_string_key_codec_refuses_malformed_and_noncanonical_ids(value: str) -> None:
    with pytest.raises(ValueError):
        StringKeyNodeCodec().decode("namespace", value)


def test_string_key_codec_refuses_noncanonical_json_bytes() -> None:
    raw = json.dumps([PROFILE, "namespace", "m", "R", "k", ["x"]], separators=(", ", ": ")).encode()
    value = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    with pytest.raises(ValueError):
        StringKeyNodeCodec().decode("namespace", value)


def test_string_key_codec_binds_namespace_and_enforces_byte_cap() -> None:
    codec = StringKeyNodeCodec()
    key = NodeKey(ElementRef("m", "R"), "k", ({"string": "x"},))
    token = codec.encode("namespace", key)
    with pytest.raises(ValueError):
        codec.decode("other", token)
    too_large = NodeKey(ElementRef("m", "R"), "k", ({"string": "x" * 3000},))
    with pytest.raises(ValueError):
        codec.encode("namespace", too_large)


def test_string_key_codec_registry_binds_exact_prepared_root_and_validates_facets() -> None:
    root = PreparedGeneratedRoot(
        OperationRef("demo", "Note", "record"),
        "1" * 64,
        "2" * 64,
        "3" * 64,
        "4" * 64,
        "5" * 64,
        "primary",
    )

    class Prepared:
        version = "lintel.prepared-api/2"
        generated_roots = (root,)

    def validate_key(
        module: str, record: str, key_id: str, components: tuple[object, ...]
    ) -> tuple[object, ...]:
        assert (module, record, key_id) == ("demo", "Note", "primary")
        if components != ({"string": "fixture-note-1"},):
            raise ValueError("issued Key codec rejected value")
        return ("fixture-note-1",)

    codec = StringKeyNodeCodec.for_prepared_api(
        Prepared(), {(ElementRef("demo", "Note"), "primary"): validate_key}
    )
    key = NodeKey(ElementRef("demo", "Note"), "primary", ({"string": "fixture-note-1"},))
    encoded = codec.encode("fixture.demo.v1", key)
    assert codec.registry_matches(Prepared())
    assert codec.decode("fixture.demo.v1", encoded) == key
    bad_key = NodeKey(ElementRef("demo", "Note"), "primary", ({"string": "invalid"},))
    with pytest.raises(ValueError):
        codec.encode("fixture.demo.v1", bad_key)
    with pytest.raises(ValueError):
        StringKeyNodeCodec.for_prepared_api(Prepared(), {})
    with pytest.raises(ValueError):
        StringKeyNodeCodec.for_prepared_api(
            Prepared(),
            {
                (ElementRef("demo", "Note"), "primary"): validate_key,
                (ElementRef("demo", "Other"), "primary"): validate_key,
            },
        )
