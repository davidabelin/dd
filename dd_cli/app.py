"""Argparse-driven command-line interface for Double-digits."""

from __future__ import annotations

import argparse
from typing import Any

from dd_core.constants import LEVELS, OPERATORS, SINGLE_LEVEL
from dd_core.export import export_example_batch, export_visualization_payload, summarize_examples
from dd_visuals.explain import VISUALIZATION_KINDS
from dd_web import default_app_config
from dd_web.runtime import DoubleDigitsService
from dd_web.serve import DEFAULT_DEBUG, DEFAULT_HOST, DEFAULT_PORT, run_local_server

from dd_cli.formatting import (
    dump_json,
    format_example_detail,
    format_example_list,
    format_generation,
    format_inference,
    format_visualization,
)


def main(argv: list[str] | None = None) -> int:
    """Run the Double-digits CLI and return a process exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "examples":
            return _handle_examples(args)
        if args.command == "infer":
            payload = _build_service().infer(_payload_from_args(args))
            _emit(payload, as_json=args.as_json, formatter=format_inference)
            return 0
        if args.command == "visualize":
            service = _build_service()
            query = _payload_from_args(args)
            visualization = service.visualization(args.kind, query)
            export = None
            if args.write_dir:
                export = export_visualization_payload(args.kind, visualization, args.write_dir)
            payload = {
                "level": query["level"],
                "kind": visualization["kind"],
                "visualization": visualization,
                "export": export,
            }
            _emit(payload, as_json=args.as_json, formatter=format_visualization)
            return 0
        if args.command == "serve":
            run_local_server(host=args.host, port=args.port, debug=args.debug)
            return 0
    except (KeyError, ValueError) as exc:
        parser.exit(status=1, message=f"{exc}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the root argparse parser for the Double-digits CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m dd_cli",
        description="Interact with the Double-digits lab from a regular command line.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    examples_parser = subparsers.add_parser("examples", help="List, inspect, or generate level examples.")
    examples_subparsers = examples_parser.add_subparsers(dest="examples_command", required=True)

    list_parser = examples_subparsers.add_parser("list", help="List curated examples for one level.")
    _add_level_argument(list_parser)
    list_parser.add_argument("--count", type=_positive_int, default=None, help="Limit the number of listed examples.")
    list_parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")

    show_parser = examples_subparsers.add_parser("show", help="Show one curated or structured example.")
    _add_example_selector_arguments(show_parser)
    show_parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")

    generate_parser = examples_subparsers.add_parser("generate", help="Generate and export a labeled example batch.")
    _add_level_argument(generate_parser)
    generate_parser.add_argument("--count", type=_positive_int, required=True, help="Number of examples to generate.")
    generate_parser.add_argument("--out", required=True, help="Directory where the generated batch will be written.")
    generate_parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")

    infer_parser = subparsers.add_parser("infer", help="Run baseline inference on one example or structured input.")
    _add_example_selector_arguments(infer_parser)
    infer_parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")

    visualize_parser = subparsers.add_parser("visualize", help="Build visualization payloads for one example.")
    _add_example_selector_arguments(visualize_parser)
    visualize_parser.add_argument("--kind", required=True, choices=VISUALIZATION_KINDS, help="Visualization kind to build.")
    visualize_parser.add_argument("--write-dir", help="Optional directory for exported visualization PNGs.")
    visualize_parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")

    serve_parser = subparsers.add_parser("serve", help="Run the local Flask app.")
    serve_parser.add_argument("--host", default=DEFAULT_HOST, help="Bind host for the local server.")
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port for the local server.")
    serve_parser.add_argument("--debug", dest="debug", action="store_true", default=DEFAULT_DEBUG, help="Run Flask in debug mode.")
    serve_parser.add_argument("--no-debug", dest="debug", action="store_false", help="Disable Flask debug mode.")

    return parser


def _handle_examples(args: argparse.Namespace) -> int:
    """Dispatch the `examples` command family."""

    service = _build_service()
    catalog = service.runtime.examples

    if args.examples_command == "list":
        listing = service.list_examples(level=args.level, count=args.count)
        payload = {
            "level": listing["level"],
            "count": len(listing["examples"]),
            "examples": summarize_examples(listing["examples"]),
        }
        _emit(payload, as_json=args.as_json, formatter=format_example_list)
        return 0

    if args.examples_command == "show":
        example = _resolve_example_from_args(service, args)
        payload = {
            "level": example.level,
            "image_shape": list(example.image.shape),
            "example": example.to_summary(),
        }
        _emit(payload, as_json=args.as_json, formatter=format_example_detail)
        return 0

    if args.examples_command == "generate":
        examples = catalog.generate_examples(args.level, args.count)
        payload = export_example_batch(examples, args.out)
        _emit(payload, as_json=args.as_json, formatter=format_generation)
        return 0

    raise ValueError(f"Unsupported examples command: {args.examples_command}")


def _build_service() -> DoubleDigitsService:
    """Create the shared runtime service using the same config defaults as the Flask app."""

    config = default_app_config()
    return DoubleDigitsService(
        models_dir=str(config["DOUBLEDIGITS_MODELS_DIR"]),
        cache_artifact=bool(config["DOUBLEDIGITS_ARTIFACT_CACHE"]),
    )


def _emit(payload: dict[str, Any], *, as_json: bool, formatter) -> None:
    """Print one CLI payload in JSON or formatted text form."""

    text = dump_json(payload) if as_json else formatter(payload)
    print(text)


def _add_level_argument(parser: argparse.ArgumentParser) -> None:
    """Add the standard level selector to a parser."""

    parser.add_argument("--level", required=True, choices=LEVELS, help="Guided-lab level to target.")


def _add_example_selector_arguments(parser: argparse.ArgumentParser) -> None:
    """Add shared example-id and structured-input arguments to a parser."""

    _add_level_argument(parser)
    parser.add_argument("--example-id", help="Curated example id to load instead of structured arguments.")
    parser.add_argument("--digit", type=int, help="Single-digit value for structured single-level input.")
    parser.add_argument("--variant", type=int, default=0, help="Single-digit variant index for structured single-level input.")
    parser.add_argument("--left", type=int, help="Left digit for structured double or arithmetic input.")
    parser.add_argument("--right", type=int, help="Right digit for structured double or arithmetic input.")
    parser.add_argument("--left-variant", type=int, default=0, help="Variant index for the left digit.")
    parser.add_argument("--right-variant", type=int, default=1, help="Variant index for the right digit.")
    parser.add_argument("--operator", choices=tuple(OPERATORS), help="Arithmetic operator for structured arithmetic input.")


def _payload_from_args(args: argparse.Namespace) -> dict[str, Any]:
    """Build one inference/visualization payload from parsed CLI arguments."""

    payload: dict[str, Any] = {"level": args.level}
    if args.example_id:
        payload["example_id"] = args.example_id
        return payload

    if args.level == SINGLE_LEVEL:
        if args.digit is None:
            raise ValueError("Provide --example-id or --digit for single-level commands.")
        payload["digit"] = args.digit
        payload["variant"] = args.variant
        return payload

    if args.left is None or args.right is None:
        raise ValueError("Provide --example-id or both --left and --right for double and arithmetic commands.")

    payload["left"] = args.left
    payload["right"] = args.right
    payload["left_variant"] = args.left_variant
    payload["right_variant"] = args.right_variant

    if args.level == "arithmetic":
        if args.operator is None:
            raise ValueError("Provide --example-id or --operator for arithmetic commands.")
        payload["operator"] = args.operator
    return payload


def _resolve_example_from_args(service: DoubleDigitsService, args: argparse.Namespace):
    """Resolve one example object from CLI arguments."""

    payload = _payload_from_args(args)
    if "example_id" in payload:
        return service.runtime.examples.example_from_id(payload["level"], payload["example_id"])
    return service.runtime.examples.structured_example(payload["level"], payload)


def _positive_int(raw: str) -> int:
    """Parse a strictly positive integer for CLI arguments."""

    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError("Expected a positive integer.")
    return value
