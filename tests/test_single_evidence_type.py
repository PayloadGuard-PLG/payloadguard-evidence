"""Gate 5 fixture (roadmap Phase B): a requirement carrying only ONE
evidence type must appear in exactly one of variant C's two artifacts.

The committed dataset cannot exercise this — every requirement carries both
evidence types (RECONCILIATION finding 4) — so this fixture supplies a
symbolic-only requirement in memory and drives the real variant C builder
with the real Sample A manifest. Committed metadata and artifacts are
unchanged.

Scope note: under the current C builder a symbolic record is bound to every
requirement unconditionally, so a concrete-only requirement is not
constructible pre-Gate-2; that observation is recorded in
KNOWN_LIMITATIONS.md as Gate 2 binder design input.
"""

import json
import pathlib
import sys

import jsonschema

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import build_matrix  # noqa: E402

ART_DIR = REPO_ROOT / "examples" / "dosage_calculator"


def _fixture_metadata():
    return {
        "device": {
            "name": "Gate 5 fixture - symbolic-only requirement",
            "safety_classification": "B",
            "classification_rationale": "DECLARED - test fixture only, not a device claim.",
        },
        "requirements": [
            {
                "id": "REQ-FIX-SYMONLY-001",
                "text": "Fixture requirement with symbolic evidence only (no concrete case names this id).",
                "implementation": "dosage.py::calculate_hourly_dose",
                "intended_method": "BOUNDED_CHECKED",
            }
        ],
        "toolchain": {
            "crosshair_bounds": {
                "per_condition_timeout_s": 30,
                "max_iterations": 100000,
                "seed": 1,
            }
        },
    }


def test_fixture_validates_against_schema_c():
    schema = json.loads(
        (REPO_ROOT / "evidence/schema/metadata.schema.c.json").read_text()
    )
    jsonschema.validate(_fixture_metadata(), schema)


def test_single_evidence_type_requirement_appears_in_exactly_one_artifact():
    metadata = _fixture_metadata()
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
