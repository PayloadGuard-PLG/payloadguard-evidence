# T4-B generator: validates metadata.b.yaml against metadata.schema.b.json,
# binds the shared evidence (Sample A CrossHair capture for base
# requirements; concrete_results cases and the real Dafny capture,
# 2026-07-07, for shadow pseudo-requirements), and renders
# traceability_matrix.b.json/.md via Gate 2's vocabulary-agnostic
# build_matrix() (evidence/render/matrix_variants.py).
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
    schema = json.loads((REPO_ROOT / "evidence/schema/metadata.schema.b.json").read_text())
    metadata = yaml.safe_load((HERE / "metadata.b.yaml").read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())
    dafny_store, dafny_manifest = _dafny_store()

    matrix, markdown = build_matrix(
        "b",
        metadata,
        manifest,
        concrete_store,
        tool_versions={
            "crosshair": manifest["tool_version"],
            "dafny": dafny_manifest["tool_version"],
        },
        dafny_store=dafny_store,
    )
    (HERE / "traceability_matrix.b.json").write_text(json.dumps(matrix, indent=2) + "\n")
    (HERE / "traceability_matrix.b.md").write_text(markdown)
    print("wrote traceability_matrix.b.json and traceability_matrix.b.md")


if __name__ == "__main__":
    main()
