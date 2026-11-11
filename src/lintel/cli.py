"""``lintel example | prepare | serve`` command line."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from importlib import resources
from pathlib import Path

from lintel import __version__

EXAMPLES = ("task-board",)
EXAMPLE_FILES = ("task-board.umf.json", "exposure.json", "host-profile.json", "records.json")


def _example(args: argparse.Namespace) -> int:
    source = resources.files("lintel").joinpath("examples", args.name)
    target = Path(args.directory)
    target.mkdir(parents=True, exist_ok=True)
    for name in EXAMPLE_FILES:
        (target / name).write_bytes(source.joinpath(name).read_bytes())
        print(target / name)
    return 0


def _prepare(args: argparse.Namespace) -> int:
    try:
        from lintel.build import prepare_api  # noqa: PLC0415
        from lintel.build.errors import PreparationError  # noqa: PLC0415
    except ImportError:
        print(
            'lintel prepare needs the build extra: pip install "lintel-api[build]"', file=sys.stderr
        )
        return 2
    from lintel.memory import SCALAR_PROFILE, capabilities_for  # noqa: PLC0415

    exposure = Path(args.exposure).read_bytes()
    host = json.loads(Path(args.host).read_bytes())
    caps = capabilities_for(json.loads(exposure), host)
    try:
        artifact = prepare_api(
            Path(args.umf).read_bytes(), (), exposure, caps, host, SCALAR_PROFILE
        )
    except (PreparationError, ValueError) as error:
        print(f"prepare failed: {error}", file=sys.stderr)
        return 1
    Path(args.output).write_bytes(artifact)
    print(f"wrote {args.output}")
    print(f"x-lintel-api: {json.loads(artifact)['apiDigest']}")
    return 0


def _serve(args: argparse.Namespace) -> int:
    try:
        import uvicorn  # noqa: PLC0415
    except ImportError:
        print(
            'lintel serve needs the serve extra: pip install "lintel-api[serve]"', file=sys.stderr
        )
        return 2
    from lintel.app import create_memory_app  # noqa: PLC0415

    try:
        app, prepared = create_memory_app(args.artifact, args.records, args.expect_digest)
    except (OSError, ValueError) as error:
        print(f"serve failed: {error}", file=sys.stderr)
        return 1
    print(f"x-lintel-api: {prepared.api_digest}", flush=True)
    print(f"POST http://{args.host}:{args.port}/graphql", flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="lintel", description="UMF document in, prepared GraphQL API out."
    )
    root.add_argument("--version", action="version", version=f"lintel {__version__}")
    commands = root.add_subparsers(dest="command", required=True)

    example = commands.add_parser("example", help="write the example input files")
    example.add_argument("name", choices=EXAMPLES)
    example.add_argument("directory")
    example.set_defaults(run=_example)

    prepare = commands.add_parser("prepare", help="build a prepared API artifact from UMF")
    prepare.add_argument("umf", help="UMF document (JSON)")
    prepare.add_argument("--exposure", required=True, help="exposure file")
    prepare.add_argument("--host", required=True, help="host profile file")
    prepare.add_argument("-o", "--output", required=True, help="artifact to write")
    prepare.set_defaults(run=_prepare)

    serve = commands.add_parser("serve", help="serve an artifact over the in-memory port")
    serve.add_argument("artifact")
    serve.add_argument("--records", required=True, help="records JSON file")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--expect-digest", help="refuse the artifact unless its apiDigest matches")
    serve.set_defaults(run=_serve)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return int(args.run(args))


if __name__ == "__main__":
    raise SystemExit(main())
