# T4-C generator: validates metadata.c.yaml against metadata.schema.c.json,
# then renders THREE independent artifacts from the identical evidence via
# Gate 2's vocabulary-agnostic build_matrix() (evidence/render/matrix_variants.py):
#   traceability_matrix.symbolic.json/.md  (variant key: c-symbolic)
#   traceability_matrix.concrete.json/.md  (variant key: c-concrete)
#   traceability_matrix.formal.json/.md    (variant key: c-formal - Gate
#                                           2/C2-C4 wiring, 2026-07-07:
#                                           real Dafny-sourced PROVEN
#                                           evidence, gated by Z3
#                                           precondition satisfiability
#                                           and the false-zero guard)
import json
import pathlib
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix  # noqa: E402


def _dafny_store():
    """Assembled the same way concrete_store/manifest already are: real
    committed files read and parsed here, not re-run (captures are never
    re-rolled inside a generation pipeline). Keyed by
    "{spec_target}::{dafny_method}" to match metadata.c.yaml's declared
    evidence entries."""
    manifest = json.loads((HERE / "run_manifest_dafny.json").read_text())
    return {
        "dosage.dfy::CalculateHourlyDose": {
            "spec_source": (HERE / "dosage.dfy").read_text(),
            "raw_output": (HERE / "raw_dafny_output.txt").read_text(),
            "manifest": manifest,
            "dafny_method": "CalculateHourlyDose",
        }
    }, manifest


def main():
    schema = json.loads((REPO_ROOT / "evidence/schema/metadata.schema.c.json").read_text())
    metadata = yaml.safe_load((HERE / "metadata.c.yaml").read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())
    tool_versions = {"crosshair": manifest["tool_version"]}
    dafny_store, dafny_manifest = _dafny_store()

    for variant_key, stem in (
        ("c-symbolic", "traceability_matrix.symbolic"),
        ("c-concrete", "traceability_matrix.concrete"),
        ("c-formal", "traceability_matrix.formal"),
    ):
        # dafny_store is passed to ALL THREE calls (2026-07-07, extended
        # when variants A/B were wired the same day) - not just
        # "c-formal". Symbolic/concrete's RENDERED rows are unaffected
        # (their shape filters to crosshair/concrete_test only), but
        # their internal derive_intent() computation needs the same
        # complete evidence picture as variants A/B now have, or their
        # own intent_ok for REQ-GIP-1-4-12/REQ-GIP-1-8-1 would silently
        # stay False while A/B/formal say True - breaking the
        # fact-equality gate's intent comparison for real, not just in
        # theory. Only the formal view's header advertises the dafny
        # tool version, since only it actually renders a dafny row.
        tv = dict(tool_versions)
        if variant_key == "c-formal":
            tv["dafny"] = dafny_manifest["tool_version"]
        matrix, markdown = build_matrix(
            variant_key,
            metadata,
            manifest,
            concrete_store,
            tool_versions=tv,
            dafny_store=dafny_store,
        )
        (HERE / f"{stem}.json").write_text(json.dumps(matrix, indent=2) + "\n")
        (HERE / f"{stem}.md").write_text(markdown)
        print(f"wrote {stem}.json/.md ({len(matrix['rows'])} rows)")


if __name__ == "__main__":
    main()
