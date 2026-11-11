from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from collections.abc import AsyncGenerator, Mapping, MutableMapping
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic
from types import ModuleType
from typing import Protocol, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response as HttpxResponse

from lintel.build import generated_roots, prepare_api, prepare_api_v2
from lintel.build import prepare as prepare_module
from lintel.build.errors import PreparationError
from lintel.graphql import create_router
from lintel.node_id import PROFILE, PreparedRoots, StringKeyNodeCodec
from lintel.ports import ElementRef, NodeKey, NodeValue, RequestScope
from lintel.ports.protocols import RequestSession
from lintel.ports.values import Arguments, CommandResult, ConnectionPage, OperationRef
from lintel.projection import AdmittedPreparedApi, TrustedPreparedRef, load_prepared_api
from lintel.projection.records import records_from_json


class _TypedTestClient(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, object] | None = None,
        content: str | None = None,
    ) -> HttpxResponse: ...


ROOT = Path(__file__).parents[1]
SOURCE = (ROOT / "src/lintel/examples/task-board/task-board.umf.json").read_bytes()
HOST = json.loads((ROOT / "src/lintel/examples/task-board/host-profile.json").read_bytes())
EXPOSURE = {
    "format": "lintel.exposure/1",
    "application": "task-board-demo",
    "identityNamespace": "demo.task-board.identity-v1",
    "records": [
        {
            "record": {"module": "board", "element": "Task"},
            "key": "primary",
            "typeName": "Task",
            "lookup": {"module": "board", "id": "lookupTasks", "kind": "table"},
            "fields": [
                {"field": {"module": "board", "element": "title"}, "name": "title"},
                {"field": {"module": "board", "element": "estimate"}, "name": "estimate"},
            ],
            "relationships": [],
        }
    ],
    "connections": [],
    "mutations": [],
}
BINDING = "fabricated-binding/1"
CAPS = {
    "lintel.execution": "1",
    "node.refetch": "1",
    "read.consistency": "request-snapshot-1",
    "identity.codec": "fabricated-node/1",
    "binding.profile": BINDING,
    "scalar.codec.profile": "lintel.scalars/1",
    "operation.binding/board/lookupTasks/table": BINDING,
    "lintel.execution.binding.profile": BINDING,
    "node.refetch.binding.profile": BINDING,
    "read.consistency.binding.profile": BINDING,
    "identity.codec.binding.profile": BINDING,
    "scalar.codec.profile.binding.profile": BINDING,
}
for _name, _value in HOST["limits"].items():
    CAPS[f"limit.{_name}"] = str(_value)
    CAPS[f"limit.{_name}.binding.profile"] = BINDING


def _artifact() -> bytes:
    return prepare_api(
        SOURCE,
        (),
        json.dumps(EXPOSURE, separators=(",", ":")).encode(),
        CAPS,
        HOST,
        "lintel.scalars/1",
    )


def _admit(raw: bytes | None = None) -> AdmittedPreparedApi:
    contents = _artifact() if raw is None else raw
    artifact = json.loads(contents)
    limits = tuple(tuple(pair) for pair in artifact["hostProfile"]["limits"])
    pin = TrustedPreparedRef(
        artifact_sha256=hashlib.sha256(contents).hexdigest(),
        artifact_digest=artifact["artifactDigest"],
        application=artifact["application"],
        api_digest=artifact["apiDigest"],
        exposure_sha256=artifact["exposureSha256"],
        sources=tuple((source["identity"], source["sha256"]) for source in artifact["sources"]),
        capabilities=tuple(tuple(pair) for pair in artifact["capabilities"]),
        binding_profile=artifact["bindingProfile"],
        scalar_codec_profile=artifact["scalarCodecProfile"],
        limits=limits,
    )
    return load_prepared_api(contents, pin)


def _admit_v2_fixture() -> AdmittedPreparedApi:
    contents = (ROOT / "tests/fixtures/prepared-api-v2-build-proof.json").read_bytes()
    artifact = json.loads(contents)
    roots_bytes = json.dumps(
        artifact["generatedRoots"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    pin = TrustedPreparedRef(
        artifact_sha256=hashlib.sha256(contents).hexdigest(),
        artifact_digest=artifact["artifactDigest"],
        application=artifact["application"],
        api_digest=artifact["apiDigest"],
        exposure_sha256=artifact["exposureSha256"],
        sources=tuple((source["identity"], source["sha256"]) for source in artifact["sources"]),
        capabilities=tuple(tuple(pair) for pair in artifact["capabilities"]),
        binding_profile=artifact["bindingProfile"],
        scalar_codec_profile=artifact["scalarCodecProfile"],
        limits=tuple(tuple(pair) for pair in artifact["hostProfile"]["limits"]),
        generated_roots_sha256=hashlib.sha256(roots_bytes).hexdigest(),
    )
    return load_prepared_api(contents, pin)


def test_build_artifact_is_deterministic_and_runtime_admission_is_pinned() -> None:
    first = _artifact()
    second = _artifact()
    assert first == second
    admitted = _admit(first)
    assert admitted.application == "task-board-demo"
    assert admitted.api_digest == json.loads(first)["apiDigest"]
    with pytest.raises(AttributeError):
        admitted.application = "other"
    with pytest.raises(TypeError):
        cast(MutableMapping[str, object], admitted.host_profile)["mount"] = "/open/graphql"
    limits = cast(MutableMapping[str, str], admitted.host_profile["limits"])
    with pytest.raises(TypeError):
        limits["maxLookup"] = "100000000"


def test_missing_operation_profile_and_artifact_tampering_refuse() -> None:
    incomplete = {
        key: value for key, value in CAPS.items() if not key.startswith("operation.binding/")
    }
    with pytest.raises(ValueError, match="UNSUPPORTED"):
        prepare_api(
            SOURCE,
            (),
            json.dumps(EXPOSURE).encode(),
            incomplete,
            HOST,
            "lintel.scalars/1",
        )
    valid = _artifact()
    original = json.loads(valid)
    admitted = _admit(valid)
    pin = TrustedPreparedRef(
        artifact_sha256=hashlib.sha256(valid).hexdigest(),
        artifact_digest=original["artifactDigest"],
        application=original["application"],
        api_digest=original["apiDigest"],
        exposure_sha256=original["exposureSha256"],
        sources=tuple((source["identity"], source["sha256"]) for source in original["sources"]),
        capabilities=tuple(tuple(pair) for pair in original["capabilities"]),
        binding_profile=original["bindingProfile"],
        scalar_codec_profile=original["scalarCodecProfile"],
        limits=tuple(tuple(pair) for pair in original["hostProfile"]["limits"]),
    )
    tampered = valid.replace(b"task-board-demo", b"other-board-demo")
    assert admitted.application == "task-board-demo"
    with pytest.raises(ValueError, match="API_MISMATCH"):
        load_prepared_api(tampered, pin)


def test_v1_keeps_record_roots_out_of_table_and_action_lookups() -> None:
    exposure = json.loads(json.dumps(EXPOSURE))
    exposure["records"][0]["lookup"] = {
        "module": "board",
        "id": "Task",
        "kind": "record",
    }
    capabilities = dict(CAPS)
    capabilities["operation.binding/board/Task/record"] = BINDING
    with pytest.raises(PreparationError):
        prepare_api(
            SOURCE,
            (),
            json.dumps(exposure, separators=(",", ":")).encode(),
            capabilities,
            HOST,
            "lintel.scalars/1",
        )
    prepared = json.loads(_artifact())
    prepared["records"][0]["lookup"]["kind"] = "record"
    with pytest.raises(ValueError, match="API_MISMATCH"):
        records_from_json(prepared["records"])


def test_v2_refuses_caller_created_generated_roots() -> None:
    exposure = json.loads(json.dumps(EXPOSURE))
    exposure["format"] = "lintel.exposure/2"
    exposure["records"][0]["lookup"] = {
        "module": "board",
        "id": "Task",
        "kind": "record",
    }
    capabilities = dict(CAPS)
    capabilities["identity.codec"] = "lintel.node-id.string-key/1"
    capabilities.pop("operation.binding/board/lookupTasks/table")
    capabilities["operation.binding/board/Task/record"] = BINDING
    wrong_codec = dict(capabilities)
    wrong_codec["identity.codec"] = "fabricated-node/1"
    with pytest.raises(PreparationError) as codec_raised:
        prepare_api_v2(
            SOURCE,
            (),
            json.dumps(exposure, separators=(",", ":")).encode(),
            wrong_codec,
            HOST,
            "lintel.scalars/1",
            {},
            {},
            {},
            {},
        )
    assert codec_raised.value.code == "UNSUPPORTED"
    with pytest.raises(PreparationError) as raised:
        prepare_api_v2(
            SOURCE,
            (),
            json.dumps(exposure, separators=(",", ":")).encode(),
            capabilities,
            HOST,
            "lintel.scalars/1",
            {},
            {},
            {},
            {},
        )
    assert raised.value.code in {"API_MISMATCH", "UNSUPPORTED"}


def test_v2_rejects_generated_read_profile_v3(monkeypatch: pytest.MonkeyPatch) -> None:
    package = ModuleType("umf_access_generated_executor")
    for name in (
        "GeneratedManifest",
        "GeneratedFiles",
        "TrustedArtifactRef",
        "TargetBinding",
    ):
        setattr(package, name, object)

    class _LegacyExecutor:
        read_profile = "weft.generated-read-algebra/3"

    def prepare_generated(
        manifest: object, files: object, trusted: object, target: object
    ) -> object:
        return _LegacyExecutor()

    prepare_name = "prepare_generated"
    setattr(package, prepare_name, prepare_generated)

    def import_module(_name: str) -> ModuleType:
        return package

    monkeypatch.setattr(generated_roots.importlib, "import_module", import_module)
    with pytest.raises(PreparationError) as raised:
        generated_roots.verify_generated_roots(
            object(), object(), object(), object(), "model", "0" * 64, "binding", ()
        )
    assert raised.value.code == "UNSUPPORTED"


def test_v2_reader_refuses_unknown_extension_warning_at_unqualified_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Document:
        def to_dict(self) -> dict[str, object]:
            return {"id": "model", "modules": [{"id": "demo", "elements": []}]}

    class _Diagnostic:
        code = "UNKNOWN_EXTENSION"
        severity = "warning"
        path = "/modules/0/extensions/other"

    class _Validation:
        valid = True
        complete = False
        diagnostics = (_Diagnostic(),)

    def read_document(_source: str) -> _Document:
        return _Document()

    def validate_document(_document: _Document) -> _Validation:
        return _Validation()

    monkeypatch.setattr(prepare_module, "read_document", read_document)
    monkeypatch.setattr(prepare_module, "validate_document", validate_document)
    with pytest.raises(PreparationError) as raised:
        prepare_module.read_umf(b"{}", allow_unknown_extensions=True)
    assert raised.value.code == "UNSUPPORTED"


class _Session:
    def __init__(self) -> None:
        self.key = NodeKey(ElementRef("board", "Task"), "primary", ({"string": "task-1"},))
        self.calls: list[tuple[ElementRef, ...]] = []
        self.decimal_value: Mapping[str, object] = {"decimalToken": "9007199254740993.01"}

    async def get_many(
        self,
        operation: OperationRef,
        keys: tuple[NodeKey, ...],
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        assert operation.id == "lookupTasks"
        self.calls.append(fields)
        available = {
            ElementRef("board", "title"): {"string": "Fabricated"},
            ElementRef("board", "estimate"): self.decimal_value,
        }
        value = NodeValue(self.key, {field: available[field] for field in fields})
        return tuple(value if key == self.key else None for key in keys)

    async def connection(
        self,
        operation: OperationRef,
        arguments: Arguments,
        first: int,
        after: str | None,
        fields: tuple[ElementRef, ...],
    ) -> ConnectionPage:
        raise NotImplementedError

    async def related_many(
        self,
        operation: OperationRef,
        parents: tuple[NodeKey, ...],
        target: ElementRef,
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        raise NotImplementedError

    async def invoke(
        self,
        operation: OperationRef,
        arguments: Arguments,
        invocation_key: str,
        confirmation: str | None,
    ) -> CommandResult:
        raise NotImplementedError

    async def observe(
        self, operation: OperationRef, arguments: Arguments, invocation_key: str
    ) -> CommandResult:
        raise NotImplementedError


class _Port:
    def __init__(self) -> None:
        self.session_value = _Session()
        self.closed = False

    def capabilities(self) -> Mapping[str, str]:
        return CAPS

    @asynccontextmanager
    async def session(self, scope: RequestScope) -> AsyncGenerator[RequestSession, None]:
        assert scope.authority == "trusted-host-handle"
        try:
            yield cast(RequestSession, self.session_value)
        finally:
            self.closed = True


class _Codec:
    def profile(self) -> str:
        return "fabricated-node/1"

    def encode(self, namespace: str, key: NodeKey) -> str:
        return namespace + ":task-1"

    def decode(self, namespace: str, value: str) -> NodeKey:
        if value != namespace + ":task-1":
            raise ValueError("invalid")
        return NodeKey(ElementRef("board", "Task"), "primary", ({"string": "task-1"},))


class _V2Session:
    def __init__(self) -> None:
        self.dispatched: list[tuple[NodeKey, ...]] = []

    async def get_many(
        self,
        operation: OperationRef,
        keys: tuple[NodeKey, ...],
        fields: tuple[ElementRef, ...],
    ) -> tuple[NodeValue | None, ...]:
        assert operation.kind == "record"
        assert fields == (ElementRef("demo", "owner"),)
        self.dispatched.append(keys)
        return tuple(
            NodeValue(key, {ElementRef("demo", "owner"): {"string": "owner-value"}}) for key in keys
        )


class _V2Port:
    def __init__(self, prepared: AdmittedPreparedApi) -> None:
        self.session_value = _V2Session()
        self._capabilities = dict(prepared.capabilities)

    def capabilities(self) -> Mapping[str, str]:
        return self._capabilities

    @asynccontextmanager
    async def session(self, scope: RequestScope) -> AsyncGenerator[RequestSession, None]:
        assert scope.authority == "trusted-host-handle"
        yield cast(RequestSession, self.session_value)


def _app(port: _Port) -> tuple[FastAPI, AdmittedPreparedApi]:
    prepared = _admit()

    async def resolve_context(_request: object, digest: str) -> RequestScope:
        return RequestScope(
            "task-board-demo", digest, "query", "trusted-host-handle", "request-1", monotonic() + 60
        )

    app = FastAPI()
    app.include_router(create_router(prepared, port, _Codec(), resolve_context))
    return app, prepared


def test_operation_capability_identity_uses_escaped_json_pointer_segments() -> None:
    exposure = json.loads(json.dumps(EXPOSURE))
    exposure["records"][0]["lookup"] = {
        "module": "board/one",
        "id": "lookup~Tasks",
        "kind": "table",
    }
    capabilities = dict(CAPS)
    del capabilities["operation.binding/board/lookupTasks/table"]
    capabilities["operation.binding/board~1one/lookup~0Tasks/table"] = BINDING
    artifact = json.loads(
        prepare_api(
            SOURCE,
            (),
            json.dumps(exposure).encode(),
            capabilities,
            HOST,
            "lintel.scalars/1",
        )
    )
    assert artifact["records"][0]["lookup"] == {
        "module": "board/one",
        "id": "lookup~Tasks",
        "kind": "table",
    }


def test_nodes_ignores_issued_codec_invalid_key_without_poisoning_valid_batch() -> None:
    prepared = _admit_v2_fixture()
    port = _V2Port(prepared)

    def validate_key(
        module: str, record: str, key_id: str, components: tuple[object, ...]
    ) -> tuple[object, ...]:
        assert (module, record, key_id) == ("demo", "Note", "primary")
        if components != ({"string": "fixture-note-1"},):
            raise ValueError("issued get_many Key codec rejected value")
        return ("fixture-note-1",)

    codec = StringKeyNodeCodec.for_prepared_api(
        cast(PreparedRoots, prepared),
        {(ElementRef("demo", "Note"), "primary"): validate_key},
    )
    valid = codec.encode(
        prepared.identity_namespace,
        NodeKey(ElementRef("demo", "Note"), "primary", ({"string": "fixture-note-1"},)),
    )
    malformed_key_bytes = json.dumps(
        [PROFILE, prepared.identity_namespace, "demo", "Note", "primary", ["invalid"]],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    invalid = base64.urlsafe_b64encode(malformed_key_bytes).rstrip(b"=").decode("ascii")

    async def resolve_context(_request: object, digest: str) -> RequestScope:
        return RequestScope(
            prepared.application,
            digest,
            "query",
            "trusted-host-handle",
            "request-v2",
            monotonic() + 60,
        )

    app = FastAPI()
    app.include_router(create_router(prepared, port, codec, resolve_context))
    response = cast(_TypedTestClient, TestClient(app)).post(
        "/graphql",
        headers={"content-type": "application/json", "x-lintel-api": prepared.api_digest},
        json={
            "query": "query($ids:[ID!]!){ nodes(ids:$ids){ ... on Note { id owner } } }",
            "variables": {"ids": [valid, invalid, valid]},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "errors" not in body
    assert body["data"]["nodes"][0]["owner"] == "owner-value"
    assert body["data"]["nodes"][1] is None
    assert body["data"]["nodes"][2]["owner"] == "owner-value"
    assert port.session_value.dispatched == [
        (
            NodeKey(ElementRef("demo", "Note"), "primary", ({"string": "fixture-note-1"},)),
            NodeKey(ElementRef("demo", "Note"), "primary", ({"string": "fixture-note-1"},)),
        )
    ]


def test_router_rejects_lookalike_prepared_api_before_reading_fields() -> None:
    async def resolve_context(_request: object, digest: str) -> RequestScope:
        return RequestScope("task-board-demo", digest, "query", object(), "req", monotonic() + 1)

    with pytest.raises(ValueError, match="API_MISMATCH"):
        create_router(cast(AdmittedPreparedApi, object()), _Port(), _Codec(), resolve_context)


def test_router_uses_host_scope_and_executes_graphql_to_neutral_port() -> None:
    port = _Port()
    app, prepared = _app(port)
    response = cast(_TypedTestClient, TestClient(app)).post(
        "/graphql",
        headers={"x-lintel-api": prepared.api_digest, "content-type": "application/json"},
        json={
            "query": (
                'query { node(id: "demo.task-board.identity-v1:task-1") { id ...TaskTitle } } '
                "fragment TaskTitle on Node { ... on Task { title estimate } }"
            )
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "node": {
                "id": "demo.task-board.identity-v1:task-1",
                "title": "Fabricated",
                "estimate": "9007199254740993.01",
            }
        }
    }
    assert port.session_value.calls == [
        (ElementRef("board", "estimate"), ElementRef("board", "title"))
    ]
    assert port.closed
    port.session_value.decimal_value = {"decimal": "9007199254740993.01"}
    invalid = cast(_TypedTestClient, TestClient(app)).post(
        "/graphql",
        headers={"x-lintel-api": prepared.api_digest, "content-type": "application/json"},
        json={
            "query": (
                'query { node(id: "demo.task-board.identity-v1:task-1") { '
                "... on Task { estimate } } }"
            )
        },
    )
    assert invalid.status_code == 200
    assert invalid.json()["errors"][0]["message"] == "UNSUPPORTED"
    assert invalid.json()["errors"][0]["extensions"] == {"code": "UNSUPPORTED"}
    assert port.session_value.calls[-1] == (ElementRef("board", "estimate"),)


def test_variable_skip_controls_exact_selected_fields_before_dispatch() -> None:
    port = _Port()
    app, prepared = _app(port)
    response = cast(_TypedTestClient, TestClient(app)).post(
        "/graphql",
        headers={"x-lintel-api": prepared.api_digest, "content-type": "application/json"},
        json={
            "query": (
                'query ($skip: Boolean!) { node(id: "demo.task-board.identity-v1:task-1") { id '
                "... on Task { title @skip(if: $skip) } } }"
            ),
            "variables": {"skip": True},
        },
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"node": {"id": "demo.task-board.identity-v1:task-1"}}}
    assert port.session_value.calls == [()]


def test_build_rejects_duplicate_json_keys_and_open_exposure_objects() -> None:
    with pytest.raises(ValueError, match="INVALID_EXPOSURE"):
        prepare_api(
            SOURCE, (), b'{"application":"one","application":"two"}', CAPS, HOST, "lintel.scalars/1"
        )
    altered = json.loads(json.dumps(EXPOSURE))
    altered["records"][0]["fields"][0]["unexpected"] = True
    with pytest.raises(ValueError, match="INVALID_EXPOSURE"):
        prepare_api(
            SOURCE,
            (),
            json.dumps(altered).encode(),
            CAPS,
            HOST,
            "lintel.scalars/1",
        )
    altered = json.loads(json.dumps(EXPOSURE))
    altered["application"] = 4
    with pytest.raises(ValueError, match="INVALID_EXPOSURE"):
        prepare_api(
            SOURCE,
            (),
            json.dumps(altered).encode(),
            CAPS,
            HOST,
            "lintel.scalars/1",
        )


def test_request_rejects_duplicate_json_keys_nonfinite_numbers_and_extensions() -> None:
    app, prepared = _app(_Port())
    client = cast(_TypedTestClient, TestClient(app))
    headers = {"x-lintel-api": prepared.api_digest, "content-type": "application/json"}
    duplicate = client.post(
        "/graphql", headers=headers, content='{"query":"{ __typename }","query":"{ __typename }"}'
    )
    nonfinite = client.post(
        "/graphql", headers=headers, content='{"query":"{ __typename }","variables":{"x":NaN}}'
    )
    extension = client.post(
        "/graphql", headers=headers, json={"query": "{ __typename }", "extensions": {"x": 1}}
    )
    assert duplicate.status_code == 400
    assert nonfinite.status_code == 400
    assert extension.status_code == 400


def test_runtime_imports_without_umf_or_build_package() -> None:
    script = """
import importlib.abc, sys
class DenyBuild(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('umf', 'lintel.build') or fullname.startswith(('umf.', 'lintel.build.')):
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, DenyBuild())
import lintel.graphql
import lintel.projection
import lintel.app
import lintel.memory
import lintel.trust
"""
    result = subprocess.run(
        [sys.executable, "-c", script], check=False, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
