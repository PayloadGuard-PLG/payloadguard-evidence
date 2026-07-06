# T4-C generator: validates metadata.c.yaml against metadata.schema.c.json,
# then renders TWO independent artifacts from the identical evidence via
# Gate 2's vocabulary-agnostic build_matrix() (cut over 2026-07-06, proven
# byte-identical to build_matrix_variant_c by
# tests/test_binder_equivalence.py):
#   traceability_matrix.symbolic.json/.md  (variant key: c-symbolic)
#   traceability_matrix.concrete.json/.md  (variant key: c-concrete)
# build_matrix_variant_c still exists in evidence/render/matrix_variants.py
# as a fallback - swap the import and call below back if a problem ever
# surfaces - and is deleted only in a later, separate cleanup step once
# this cutover has proven stable.
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
    schema = json.loads((REPO_ROOT / "evidence/schema/metadata.schema.c.json").read_text())
    metadata = yaml.safe_load((HERE / "metadata.c.yaml").read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())
    tool_versions = {"crosshair": manifest["tool_version"]}

    for variant_key, stem in (
        ("c-symbolic", "traceability_matrix.symbolic"),
        ("c-concrete", "traceability_matrix.concrete"),
    ):
        matrix, markdown = build_matrix(
            variant_key, metadata, manifest, concrete_store, tool_versions=tool_versions
        )
        (HERE / f"{stem}.json").write_text(json.dumps(matrix, indent=2) + "\n")
        (HERE / f"{stem}.md").write_text(markdown)
        print(f"wrote {stem}.json/.md ({len(matrix['rows'])} rows)")


if __name__ == "__main__":
    main()
