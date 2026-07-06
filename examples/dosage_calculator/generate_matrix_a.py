# T4-A generator: validates metadata.a.yaml against metadata.schema.a.json,
# binds the shared evidence (Sample A CrossHair capture + concrete_results
# from T4-0), and renders traceability_matrix.a.json/.md via Gate 2's
# vocabulary-agnostic build_matrix() (cut over 2026-07-06, proven
# byte-identical to build_matrix_variant_a by
# tests/test_binder_equivalence.py). build_matrix_variant_a still exists in
# evidence/render/matrix_variants.py as a fallback - swap the import and
# call below back if a problem ever surfaces - and is deleted only in a
# later, separate cleanup step once this cutover has proven stable.
import json
import pathlib
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix  # noqa: E402


def main():
    schema = json.loads((REPO_ROOT / "evidence/schema/metadata.schema.a.json").read_text())
    metadata = yaml.safe_load((HERE / "metadata.a.yaml").read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())

    matrix, markdown = build_matrix(
        "a",
        metadata,
        manifest,
        concrete_store,
        tool_versions={"crosshair": manifest["tool_version"]},
    )
    (HERE / "traceability_matrix.a.json").write_text(json.dumps(matrix, indent=2) + "\n")
    (HERE / "traceability_matrix.a.md").write_text(markdown)
    print("wrote traceability_matrix.a.json and traceability_matrix.a.md")


if __name__ == "__main__":
    main()
