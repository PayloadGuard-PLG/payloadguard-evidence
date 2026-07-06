"""Gate 5 fixtures (roadmap Phase B): a requirement carrying only ONE
evidence type must appear in exactly one of variant C's two artifacts.

The committed dataset cannot exercise this — every requirement carries both
evidence types (RECONCILIATION finding 4) — so these fixtures supply
single-evidence-type requirements in memory and drive the real variant C
builder with the real Sample A manifest. Committed metadata and artifacts
are unchanged.

Symbolic-only was always constructible (a requirement with no `evidence`
list falls back to C's original unconditional symbolic binding).
Concrete-only was NOT constructible until the Gate 5 fix (2026-07-06):
`_bind_self_describing` used to bind a symbolic record to every
requirement regardless of what it declared. Now a requirement whose
`evidence` list names only `concrete_test` (no `crosshair` entry) gets no
symbolic record — see `evidence/render/matrix_variants.py`.
"""

import json
import pathlib
import sys

import jsonschema

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _base_device():
    return {
        "name": "Gate 5 fixture",
        "safety_classification": "B",
        "classification_rationale": "DECLARED - test fixture only, not a device claim.",
    }


def _base_toolchain():
    return {
        "crosshair_bounds": {
            "per_condition_timeout_s": 30,
            "max_iterations": 100000,
            "seed": 1,
        }
    }


def _symbolic_only_metadata():
    return {
        "device": _base_device(),
        "requirements": [
            {
                "id": "REQ-FIX-SYMONLY-001",
                "text": "Fixture requirement with symbolic evidence only (no concrete case names this id).",
                "implementation": "dosage.py::calculate_hourly_dose",
                "intended_method": "BOUNDED_CHECKED",
            }
        ],
        "toolchain": _base_toolchain(),
    }


def _concrete_only_metadata():
    return {
        "device": _base_device(),
        "requirements": [
            {
                "id": "REQ-FIX-CONONLY-001",
                "text": "Fixture requirement with concrete evidence only (no crosshair entry declared).",
                "implementation": "dosage.py::calculate_hourly_dose",
                "intended_method": "EXAMPLE_CHECKED",
                "evidence": [
                    {"method": "concrete_test", "test_id": "fixture_case"}
                ],
            }
        ],
        "toolchain": _base_toolchain(),
    }


def test_symbolic_only_fixture_validates_against_schema_c():
    schema = json.loads(
        (REPO_ROOT / "evidence/schema/metadata.schema.c.json").read_text()
    )
    jsonschema.validate(_symbolic_only_metadata(), schema)


def test_concrete_only_fixture_validates_against_schema_c():
    schema = json.loads(
        (REPO_ROOT / "evidence/schema/metadata.schema.c.json").read_text()
    )
    jsonschema.validate(_concrete_only_metadata(), schema)


def test_symbolic_only_requirement_appears_in_exactly_one_artifact():
    metadata = _symbolic_only_metadata()
    manifest = json.loads((ART_DIR / "run_manifest.json").read_text())
    empty_store = {"cases": []}

    symbolic, _ = build_matrix("c-symbolic", metadata, manifest, empty_store)
    concrete, _ = build_matrix("c-concrete", metadata, manifest, empty_store)

    sym_ids = [r["requirement_id"] for r in symbolic["rows"]]
    con_ids = [r["requirement_id"] for r in concrete["rows"]]
    assert sym_ids == ["REQ-FIX-SYMONLY-001"]
    assert con_ids == []
    # The property under test, stated directly: present in exactly one view.
    appearances = ("REQ-FIX-SYMONLY-001" in sym_ids) + ("REQ-FIX-SYMONLY-001" in con_ids)
    assert appearances == 1

    # Intent is requirement-scoped over the FULL model (R1): the symbolic
    # record realizes the intended BOUNDED_CHECKED, so both views carry true.
    assert symbolic["rows"][0]["intent_ok"] is True


def test_concrete_only_requirement_appears_in_exactly_one_artifact():
    """The Gate 5 fix itself: a requirement declaring only concrete_test
    evidence gets no symbolic record, so it must NOT appear in the
    symbolic artifact at all - previously impossible (every requirement
    got an unconditional symbolic record regardless of declaration)."""
    metadata = _concrete_only_metadata()
    manifest = json.loads((ART_DIR / "run_manifest.json").read_text())
    store = {
        "cases": [
            {
                "test_id": "fixture_case",
                "requirement_id": "REQ-FIX-CONONLY-001",
                "function": "dosage.py::calculate_hourly_dose",
                "inputs": {},
                "expected": 0.0,
                "observed": 0.0,
                "passed": True,
            }
        ]
    }

    symbolic, _ = build_matrix("c-symbolic", metadata, manifest, store)
    concrete, _ = build_matrix("c-concrete", metadata, manifest, store)

    sym_ids = [r["requirement_id"] for r in symbolic["rows"]]
    con_ids = [r["requirement_id"] for r in concrete["rows"]]
    assert sym_ids == []
    assert con_ids == ["REQ-FIX-CONONLY-001"]
    appearances = ("REQ-FIX-CONONLY-001" in sym_ids) + ("REQ-FIX-CONONLY-001" in con_ids)
    assert appearances == 1

    # Intent is requirement-scoped over the FULL model (R1): the concrete
    # record realizes the intended EXAMPLE_CHECKED, so both views carry true.
    assert concrete["rows"][0]["intent_ok"] is True
