"""Gate 2 vocabulary-agnostic binder, Step 1 correctness proof.

build_matrix() in evidence/render/matrix_variants.py is a literal
extraction/reassembly of build_matrix_variant_a/b/c's existing logic into
a declarative binder+shape dispatch. This is the check that the
extraction didn't silently change anything: every variant's old and new
output must be equal - dict equality AND JSON-serialized string equality
(to also catch key-order drift, which dict `==` alone would miss) - over
the real committed inputs, timestamps aside.

Nothing is cut over yet: generate_matrix_a.py etc. still call the
original build_matrix_variant_a/b/c functions, untouched. This test is
the gate that must pass before that cutover is even considered.
"""

import json
import pathlib
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import (  # noqa: E402
    build_matrix,
    build_matrix_variant_a,
    build_matrix_variant_b,
    build_matrix_variant_c,
)

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _load(name):
    text = (ART_DIR / name).read_text()
    return yaml.safe_load(text) if name.endswith(".yaml") else json.loads(text)


def _strip_ts(matrix):
    m = dict(matrix)
    m["generated_utc"] = "TIMESTAMP"
    return m


def _strip_ts_md(md):
    return "\n".join(
        "Generated (UTC): TIMESTAMP" if line.startswith("Generated (UTC):") else line
        for line in md.splitlines()
    )


def _assert_equivalent(old, new):
    old_matrix, old_md = old
    new_matrix, new_md = new
    old_stripped, new_stripped = _strip_ts(old_matrix), _strip_ts(new_matrix)
    assert old_stripped == new_stripped
    # Stronger than dict equality: also proves key-insertion order matches,
    # which is what would make a future generator cutover produce a
    # byte-identical committed JSON file, not just equivalent content.
    assert json.dumps(old_stripped, indent=2) == json.dumps(new_stripped, indent=2)
    assert _strip_ts_md(old_md) == _strip_ts_md(new_md)


def test_variant_a_equivalence():
    metadata = _load("metadata.a.yaml")
    manifest = _load("run_manifest.json")
    concrete_store = _load("concrete_results.json")
    _assert_equivalent(
        build_matrix_variant_a(metadata, manifest, concrete_store),
        build_matrix("a", metadata, manifest, concrete_store),
    )


def test_variant_b_equivalence():
    metadata = _load("metadata.b.yaml")
    manifest = _load("run_manifest.json")
    concrete_store = _load("concrete_results.json")
    _assert_equivalent(
        build_matrix_variant_b(metadata, manifest, concrete_store),
        build_matrix("b", metadata, manifest, concrete_store),
    )


def test_variant_c_symbolic_equivalence():
    metadata = _load("metadata.c.yaml")
    manifest = _load("run_manifest.json")
    concrete_store = _load("concrete_results.json")
    _assert_equivalent(
        build_matrix_variant_c(metadata, manifest, concrete_store, "crosshair"),
        build_matrix("c-symbolic", metadata, manifest, concrete_store),
    )


def test_variant_c_concrete_equivalence():
    metadata = _load("metadata.c.yaml")
    manifest = _load("run_manifest.json")
    concrete_store = _load("concrete_results.json")
    _assert_equivalent(
        build_matrix_variant_c(metadata, manifest, concrete_store, "concrete_test"),
        build_matrix("c-concrete", metadata, manifest, concrete_store),
    )


def test_unknown_variant_key_is_a_hard_error():
    metadata = _load("metadata.a.yaml")
    manifest = _load("run_manifest.json")
    concrete_store = _load("concrete_results.json")
    try:
        build_matrix("nonexistent", metadata, manifest, concrete_store)
        assert False, "expected KeyError for an unknown variant key"
    except KeyError:
        pass
