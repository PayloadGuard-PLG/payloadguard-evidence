# T4-B generator: validates metadata.b.yaml against metadata.schema.b.json,
# binds the shared evidence (Sample A CrossHair capture for base
# requirements; concrete_results cases for shadow pseudo-requirements), and
# renders traceability_matrix.b.json/.md via the variant B builder.
import json
import pathlib
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix_variant_b  # noqa: E402


def main():
    schema = json.loads((REPO_ROOT / "evidence/schema/metadata.schema.b.json").read_text())
    metadata = yaml.safe_load((HERE / "metadata.b.yaml").read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())

    matrix, markdown = build_matrix_variant_b(
        metadata,
        manifest,
        concrete_store,
        tool_versions={"crosshair": manifest["tool_version"]},
    )
    (HERE / "traceability_matrix.b.json").write_text(json.dumps(matrix, indent=2) + "\n")
    (HERE / "traceability_matrix.b.md").write_text(markdown)
    print("wrote traceability_matrix.b.json and traceability_matrix.b.md")


if __name__ == "__main__":
    main()
