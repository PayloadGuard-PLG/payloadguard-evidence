"""Component B wiring: every PROVEN Dafny row in the committed matrices
carries a proof_content qualifier (definitional | property) derived from
evidence/spec_impl_gap.py, with the matching caveat text.

test_spec_impl_gap.py pins the classifier itself; this pins that the
classification actually reaches the rendered traceability matrices - the
honest reclassification the "PROVEN != meaningful" work exists to make."""

import json
import pathlib

from evidence.model import PROOF_CONTENT_CAVEAT

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EX = REPO_ROOT / "examples"

# Per-requirement expected proof-content, rolled up (property if any dafny
# evidence record on the row is property, else definitional). Matches the
# by-hand analysis: aeb/ddi are definitional predicate/lookup specs;
# dosage/renal carry real arithmetic property content.
EXPECTED = {
    "aeb_kernel": {
        "REQ-AEB-1": "definitional", "REQ-AEB-2": "definitional",
        "REQ-AEB-3": "definitional", "REQ-AEB-4": "definitional",
        "REQ-AEB-5": "definitional", "REQ-AEB-6": "definitional",
        "REQ-AEB-7": "definitional", "REQ-AEB-8": "definitional",
    },
    "dosage_calculator": {
        "REQ-GIP-1-4-12": "property", "REQ-GIP-1-8-1": "property",
    },
    "drug_interaction_checker": {
        "REQ-DDI-1": "definitional", "REQ-DDI-2": "definitional",
        "REQ-DDI-3": "definitional", "REQ-DDI-4": "definitional",
        "REQ-DDI-5": "definitional", "REQ-DDI-6": "definitional",
    },
    "renal_adjustment": {
        "REQ-RENAL-1a": "property", "REQ-RENAL-5": "property",
    },
}


def _rows(example):
    path = EX / example / "traceability_matrix.a.json"
    return json.loads(path.read_text())["rows"]


def _roll_up(row):
    pcs = [
        rec.get("proof_content")
        for rec in (row.get("evidence") or [])
        if rec.get("method") == "dafny" and rec.get("strength") == "PROVEN"
    ]
    if not pcs:
        return None
    return "property" if "property" in pcs else "definitional"


def test_committed_matrices_carry_expected_proof_content():
    for example, expected in EXPECTED.items():
        by_req = {r.get("requirement_id"): r for r in _rows(example)}
        for req, want in expected.items():
            assert req in by_req, (example, req)
            assert _roll_up(by_req[req]) == want, (example, req)


def test_every_proven_dafny_record_has_a_valid_proof_content_and_caveat():
    """No PROVEN Dafny row may be left unclassified on the real specs, and
    the caveat text must match the qualifier (the two can't drift apart)."""
    for example in EXPECTED:
        for row in _rows(example):
            for rec in (row.get("evidence") or []):
                if rec.get("method") == "dafny" and rec.get("strength") == "PROVEN":
                    pc = rec.get("proof_content")
                    assert pc in ("definitional", "property"), (example, rec)
                    assert rec.get("proof_content_caveat") == PROOF_CONTENT_CAVEAT[pc]


def test_aeb_and_ddi_are_entirely_definitional_dosage_and_renal_carry_property():
    """The headline honest finding: the two predicate/lookup specs prove
    only definitions; the two arithmetic specs prove real properties."""
    def kinds(example):
        out = set()
        for row in _rows(example):
            r = _roll_up(row)
            if r:
                out.add(r)
        return out

    assert kinds("aeb_kernel") == {"definitional"}
    assert kinds("drug_interaction_checker") == {"definitional"}
    assert kinds("dosage_calculator") == {"property"}
    assert kinds("renal_adjustment") >= {"property"}
