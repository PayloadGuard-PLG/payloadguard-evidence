# Turn B4: end-to-end artifact generation pipeline.
#
# One command from committed inputs to the full verified artifact set:
#   stage 1  validate all four metadata files against their schemas
#   stage 2  verify capture integrity (captures are committed evidence and
#            are NEVER re-run here - re-running evidence inside a generation
#            pipeline would be re-rolling)
#   stage 3  Gate 2 CONFLICT gate, Type 1 (identity mismatch) - top-down
#            metadata bindings vs. bottom-up evidence-store claims must
#            agree on target identity (evidence/conflict.py)
#   stage 4  regenerate the three variant matrices + fact-equality gate
#            (delegates to regenerate_all.py, the B2-sanctioned path; the
#            base matrix stays frozen per ruling R2c)
#   stage 5  final structural PROVEN sweep over every artifact incl. base
#   stage 6  write artifact_index.json - SHA-256 provenance binding inputs
#            to outputs, with per-gate results
#
# Any stage failure stops the pipeline (Tier 1, REVIEW_PROTOCOL.md): fix at
# the layer at fault, never by editing a generated artifact.
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.conflict import run_conflict_gate  # noqa: E402
from evidence.reconcile import BASE_ARTIFACT, VARIANT_ARTIFACTS  # noqa: E402
from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

SCHEMA_PAIRS = (
    ("evidence/schema/metadata.schema.json", "metadata.yaml"),
    ("evidence/schema/metadata.schema.a.json", "metadata.a.yaml"),
    ("evidence/schema/metadata.schema.b.json", "metadata.b.yaml"),
    ("evidence/schema/metadata.schema.c.json", "metadata.c.yaml"),
)

# Direct inputs to the generated matrices, hashed for provenance.
INPUTS = (
    "dosage.py",
    "metadata.yaml",
    "metadata.a.yaml",
    "metadata.b.yaml",
    "metadata.c.yaml",
    "run_manifest.json",
    "raw_crosshair_output.txt",
    "concrete_results.json",
)
INPUT_SCHEMAS = tuple(pair[0] for pair in SCHEMA_PAIRS)

OUTPUTS = tuple(VARIANT_ARTIFACTS) + (
    "traceability_matrix.a.md",
    "traceability_matrix.b.md",
    "traceability_matrix.symbolic.md",
    "traceability_matrix.concrete.md",
)

# Committed evidence that the pipeline depends on but never regenerates.
FROZEN = (
    BASE_ARTIFACT,
    "traceability_matrix.md",
    "raw_crosshair_output_broken.txt",
    "run_manifest_broken.json",
    "raw_crosshair_output_naive_widening.txt",
    "run_manifest_naive_widening.json",
    "exhibit_pin_naive_widening.json",
    "raw_crosshair_output_overflow_probe.txt",
    "run_manifest_overflow_probe.json",
    "exhibit_pin_overflow_probe.json",
)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage_validate():
    for schema_rel, meta_name in SCHEMA_PAIRS:
        schema = json.loads((REPO_ROOT / schema_rel).read_text())
        metadata = yaml.safe_load((HERE / meta_name).read_text())
        jsonschema.validate(metadata, schema)
    print(f"stage 1 schema validation: PASS ({len(SCHEMA_PAIRS)} metadata files)")


def stage_capture_integrity():
    manifest = json.loads((HERE / "run_manifest.json").read_text())
    if manifest["exit_code"] != 0:
        raise SystemExit("capture integrity: Sample A manifest exit_code != 0")
    if "effective_bounds" not in manifest:
        raise SystemExit("capture integrity: Sample A manifest lacks effective_bounds")
    if not (HERE / "raw_crosshair_output.txt").read_text().strip():
        raise SystemExit("capture integrity: Sample A raw output is empty")
    broken = json.loads((HERE / "run_manifest_broken.json").read_text())
    if broken["exit_code"] != 1:
        raise SystemExit("capture integrity: Sample B manifest exit_code != 1")
    store = json.loads((HERE / "concrete_results.json").read_text())
    if store["pytest_exit_code"] != 0 or not all(c["passed"] for c in store["cases"]):
        raise SystemExit("capture integrity: concrete results not a clean pass")
    print("stage 2 capture integrity: PASS (Sample A, Sample B, concrete store)")


def stage_conflict_check():
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())
    manifest = json.loads((HERE / "run_manifest.json").read_text())
    checked = 0
    for meta_name in ("metadata.yaml", "metadata.a.yaml", "metadata.b.yaml", "metadata.c.yaml"):
        metadata = yaml.safe_load((HERE / meta_name).read_text())
        result = run_conflict_gate(metadata, concrete_store, manifest)
        checked += result["bindings_checked"]
    print(
        "stage 3 CONFLICT gate (Type 1, identity mismatch): PASS "
        f"({checked} bindings checked across 4 metadata files)"
    )


def stage_generate():
    subprocess.run(
        [sys.executable, str(HERE / "regenerate_all.py")], check=True, cwd=HERE
    )
    print("stage 4 regeneration + fact-equality gate: PASS")


def stage_proven_sweep():
    for name in tuple(VARIANT_ARTIFACTS) + (BASE_ARTIFACT,):
        assert_no_realized_proven(json.loads((HERE / name).read_text()))
    print("stage 5 structural PROVEN sweep: PASS (4 variants + frozen base)")


def stage_index():
    index = {
        "artifact": "PayloadGuard evidence artifact index",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pipeline": "generate_artifacts.py (Turn B4)",
        "gates": {
            "schema_validation": "PASS",
            "capture_integrity": "PASS",
            "conflict_check_type1": "PASS",
            "fact_equality": "PASS",
            "structural_proven": "PASS",
        },
        "inputs": {
            **{name: _sha256(HERE / name) for name in INPUTS},
            **{rel: _sha256(REPO_ROOT / rel) for rel in INPUT_SCHEMAS},
        },
        "outputs": {name: _sha256(HERE / name) for name in OUTPUTS},
        "frozen_evidence": {name: _sha256(HERE / name) for name in FROZEN},
    }
    (HERE / "artifact_index.json").write_text(json.dumps(index, indent=2) + "\n")
    print("stage 6 provenance index: wrote artifact_index.json")


def main():
    stage_validate()
    stage_capture_integrity()
    stage_conflict_check()
    stage_generate()
    stage_proven_sweep()
    stage_index()
    print("end-to-end artifact generation: COMPLETE")


if __name__ == "__main__":
    main()
