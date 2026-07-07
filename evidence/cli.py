"""Gate 2 CLI: a vocabulary-agnostic command-line entry point wrapping
build_matrix() (evidence/render/matrix_variants.py).

Unlike generate_matrix_a/b/c.py, which hardcode paths to
examples/dosage_calculator, this takes metadata/manifest/concrete-store/
schema paths as arguments - so it can build a traceability matrix for any
evidence set matching one of the four schema shapes, not just the worked
example. This is the "vocabulary-agnostic" half of Gate 2's binder work
made reachable from outside a Python script.

Usage:
    python -m evidence.cli build --variant a \
        --metadata examples/dosage_calculator/metadata.a.yaml \
        --manifest examples/dosage_calculator/run_manifest.json \
        --concrete examples/dosage_calculator/concrete_results.json \
        --out-json /tmp/out.json --out-md /tmp/out.md

Must be run from the repository root (this repo has no packaging/install
step yet - `python -m` needs the `evidence` package importable from the
current directory, the same constraint every other script here already
has via its own REPO_ROOT/sys.path handling).

--schema is optional: if omitted, it defaults to
evidence/schema/metadata.schema.<a|b|c>.json for the given --variant -
a convenience, not a hardcoded requirement. Pass --schema explicitly for
a metadata shape that lives elsewhere.

--dafny-captures is optional (2026-07-07, Gate 2/C2-C4 wiring, extended
to variants A/B the same day): a path to a small JSON "index" file
mapping "{spec_target}::{dafny_method}" keys to paths (relative to the
index file's own directory) for the three real inputs a dafny_record()
call needs - spec_source_path (the .dfy source), raw_output_path (the
verbatim capture text), manifest_path (the run manifest JSON) - plus the
dafny_method name itself. Example:
    {
      "dosage.dfy::CalculateHourlyDose": {
        "spec_source_path": "dosage.dfy",
        "raw_output_path": "raw_dafny_output.txt",
        "manifest_path": "run_manifest_dafny.json",
        "dafny_method": "CalculateHourlyDose"
      }
    }
Paths-of-paths rather than inlined file content, so the index stays a
small, readable, hand-maintainable file instead of embedding multi-line
Dafny source and raw capture text inside JSON string escapes. Required
whenever the target metadata declares any `method: dafny` evidence
(variants A/B unconditionally; variant C's symbolic/concrete views only
need it for intent_ok consistency, not rendering - see
_bind_self_describing's docstring in matrix_variants.py) - build_matrix()
itself refuses with a clear message if it's missing and needed.

Exit codes: 0 on success. A Tier-1 failure (schema validation, Gate 2
CONFLICT Type 1 - folded into build_matrix() itself, see
matrix_variants.py - or the structural PROVEN check) exits non-zero with
a message on stderr, not a raw traceback, matching this repo's
convention for Tier-1 stops (REVIEW_PROTOCOL.md).
"""

import argparse
import json
import pathlib
import sys

import jsonschema
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix  # noqa: E402

_SCHEMA_SUFFIX_BY_VARIANT = {
    "a": "a",
    "b": "b",
    "c-symbolic": "c",
    "c-concrete": "c",
    "c-formal": "c",
}


def _default_schema_path(variant):
    suffix = _SCHEMA_SUFFIX_BY_VARIANT[variant]
    return REPO_ROOT / "evidence" / "schema" / f"metadata.schema.{suffix}.json"


def _load_dafny_store(index_path):
    """Read a --dafny-captures index file and assemble the real dafny_store
    dict build_matrix() expects, reading each referenced file relative to
    the index file's own directory."""
    index_path = pathlib.Path(index_path)
    index = json.loads(index_path.read_text())
    base = index_path.parent
    store = {}
    for key, entry in index.items():
        store[key] = {
            "spec_source": (base / entry["spec_source_path"]).read_text(),
            "raw_output": (base / entry["raw_output_path"]).read_text(),
            "manifest": json.loads((base / entry["manifest_path"]).read_text()),
            "dafny_method": entry["dafny_method"],
        }
    return store


def _build(args):
    schema_path = pathlib.Path(args.schema) if args.schema else _default_schema_path(args.variant)
    schema = json.loads(schema_path.read_text())
    metadata = yaml.safe_load(pathlib.Path(args.metadata).read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads(pathlib.Path(args.manifest).read_text())
    concrete_store = json.loads(pathlib.Path(args.concrete).read_text())
    # Derived from the manifest's own declared tool name rather than a
    # hardcoded "crosshair" key, so a differently-tooled evidence set
    # (Phase C's Dafny/Z3 adapters) doesn't need this CLI changed.
    tool_versions = {manifest["tool"]: manifest["tool_version"]} if "tool" in manifest else {}

    dafny_store = None
    if args.dafny_captures:
        dafny_store = _load_dafny_store(args.dafny_captures)
        # Advertise dafny's own tool version too, same as
        # generate_matrix_a/b/c.py do - but ONLY for the variants that
        # actually RENDER a dafny row (a, b, c-formal). c-symbolic/
        # c-concrete need dafny_store passed for their own intent_ok
        # computation (see _bind_self_describing's docstring) but their
        # rendered rows never include a dafny record, so their
        # tool_versions header stays crosshair-only, matching the
        # committed artifacts exactly.
        if args.variant not in ("c-symbolic", "c-concrete"):
            any_capture = next(iter(dafny_store.values()), None)
            if any_capture is not None and "tool_version" in any_capture["manifest"]:
                tool_versions["dafny"] = any_capture["manifest"]["tool_version"]

    matrix, markdown = build_matrix(
        args.variant,
        metadata,
        manifest,
        concrete_store,
        tool_versions=tool_versions,
        dafny_store=dafny_store,
    )

    # JSON to stdout when --out-json is omitted, so the CLI composes with
    # other tools (e.g. `| jq`). Markdown is never printed to stdout - it
    # only appears if --out-md is given explicitly, to keep stdout parsing
    # as JSON unambiguous either way.
    wrote = []
    if args.out_json:
        pathlib.Path(args.out_json).write_text(json.dumps(matrix, indent=2) + "\n")
        wrote.append(args.out_json)
    else:
        print(json.dumps(matrix, indent=2))

    if args.out_md:
        pathlib.Path(args.out_md).write_text(markdown)
        wrote.append(args.out_md)

    if wrote:
        print(f"wrote {', '.join(wrote)}", file=sys.stderr)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="python -m evidence.cli",
        description="Gate 2 vocabulary-agnostic traceability matrix builder.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build_parser = sub.add_parser(
        "build", help="Build one variant's traceability matrix."
    )
    build_parser.add_argument(
        "--variant", required=True, choices=sorted(_SCHEMA_SUFFIX_BY_VARIANT)
    )
    build_parser.add_argument("--metadata", required=True)
    build_parser.add_argument("--manifest", required=True)
    build_parser.add_argument("--concrete", required=True)
    build_parser.add_argument(
        "--schema",
        default=None,
        help="Defaults to evidence/schema/metadata.schema.<a|b|c>.json for --variant.",
    )
    build_parser.add_argument(
        "--dafny-captures",
        default=None,
        help="Path to a dafny_store index JSON file - required if the "
        "target metadata declares any method: dafny evidence.",
    )
    build_parser.add_argument("--out-json", default=None)
    build_parser.add_argument("--out-md", default=None)
    build_parser.set_defaults(func=_build)

    return parser


def main(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except SystemExit:
        raise
    except jsonschema.ValidationError as e:
        # e.message is the short, human-readable line ("'device' is a
        # required property"); str(e) dumps the entire schema, which is
        # useless noise for a CLI user.
        raise SystemExit(f"schema validation failed: {e.message}")
    except AssertionError as e:
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
