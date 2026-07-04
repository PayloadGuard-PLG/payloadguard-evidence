# T4-C generator: validates metadata.c.yaml against metadata.schema.c.json,
# then renders TWO independent artifacts from the identical evidence via the
# single method-filter-parametrised variant C builder:
#   traceability_matrix.symbolic.json/.md  (method filter: crosshair)
#   traceability_matrix.concrete.json/.md  (method filter: concrete_test)
import json
import pathlib
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix_variant_c  # noqa: E402


def main():
    schema = json.loads((REPO_ROOT / "evidence/schema/metadata.schema.c.json").read_text())
    metadata = yaml.safe_load((HERE / "metadata.c.yaml").read_text())
    jsonschema.validate(metadata, schema)

    manifest = json.loads((HERE / "run_manifest.json").read_text())
    concrete_store = json.loads((HERE / "concrete_results.json").read_text())
    tool_versions = {"crosshair": manifest["tool_version"]}

    for method, stem in (
        ("crosshair", "traceability_matrix.symbolic"),
        ("concrete_test", "traceability_matrix.concrete"),
    ):
        matrix, markdown = build_matrix_variant_c(
            metadata, manifest, concrete_store, method, tool_versions=tool_versions
        )
        (HERE / f"{stem}.json").write_text(json.dumps(matrix, indent=2) + "\n")
        (HERE / f"{stem}.md").write_text(markdown)
        print(f"wrote {stem}.json/.md ({len(matrix['rows'])} rows)")


if __name__ == "__main__":
    main()
