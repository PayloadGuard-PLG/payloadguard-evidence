"""Cross-artifact reconciliation: normalized fact extraction and the
fact-equality gate (Turn 2.0 B2).

Ruling encoded: variant artifacts are never required to be byte-identical —
shape divergence is design — but they ARE required to be fact-identical
under the normalization below. Fact divergence is a defect that stops
generation; it is never "documented" instead of fixed.

A cross-artifact property cannot live inside any single generator (a
generator comparing against sibling files mid-regeneration would race stale
artifacts), so the gate runs in two places: the sanctioned regeneration
entrypoint (examples/dosage_calculator/regenerate_all.py, after all
generators complete) and the test suite (tests/test_fact_equality.py, over
the committed artifacts). The base Phase A matrix is frozen (ruling R2c)
and participates as the symbolic-subset legacy view.

VARIANT_ARTIFACTS gained traceability_matrix.formal.json (2026-07-07,
Gate 2/C2-C4 wiring extended to variants A/B): when the formal view first
landed (variant C only), it deliberately stayed OUT of this tuple and a
separate, narrower check (run_formal_check, since removed) verified a
real, temporary, named divergence against variants A/B (which didn't yet
bind dafny evidence). Now that A and B bind the same real dafny evidence
declared in metadata.a.yaml/metadata.b.yaml, that divergence is closed -
traceability_matrix.formal.json is a full peer in the same strict
all-must-match check as A/B/symbolic/concrete, with no carve-out. facts_c
is now the union of symbolic, concrete, AND formal - the three-way split
that constitutes variant C's total claim, compared against A's and B's
single-artifact totality.
"""

import json
import pathlib

VARIANT_ARTIFACTS = (
    "traceability_matrix.a.json",
    "traceability_matrix.b.json",
    "traceability_matrix.symbolic.json",
    "traceability_matrix.concrete.json",
    "traceability_matrix.formal.json",
)
BASE_ARTIFACT = "traceability_matrix.json"
FORMAL_ARTIFACT = "traceability_matrix.formal.json"


def _fact(requirement_id, record):
    """Normalized fact tuple:
    (requirement_id, method, record_key, result_status, strength)."""
    return (
        requirement_id,
        record["method"],
        record.get("test_id") or "SYMBOLIC",
        record["result_status"],
        record["strength"],
    )


def normalize_facts(matrix):
    """Reduce any matrix shape (base, A, B, C views) to its fact set.
    Variant A rows carry an evidence list; all other shapes are
    one-record-per-row. Variant B shadow rows normalize to their parent.
    GAP records are excluded: a GAP is the explicit rendering of ABSENT
    evidence (claims discipline: gap = absence), so it is not a fact and
    must not count toward fact equality."""
    facts = set()
    for row in matrix["rows"]:
        if "evidence" in row:
            for rec in row["evidence"]:
                if rec["strength"] == "GAP":
                    continue
                facts.add(_fact(row["requirement_id"], rec))
        else:
            if row["strength"] == "GAP":
                continue
            requirement = row.get("parent_requirement") or row["requirement_id"]
            facts.add(_fact(requirement, row))
    return facts


def extract_intent(matrix):
    """Requirement-scoped intent_ok per base requirement. Raises if a single
    artifact is internally inconsistent (would violate ruling R1)."""
    intent = {}
    for row in matrix["rows"]:
        requirement = row.get("parent_requirement") or row["requirement_id"]
        if requirement in intent and intent[requirement] != row["intent_ok"]:
            raise AssertionError(
                f"intent_ok not uniform within one artifact for {requirement}"
            )
        intent[requirement] = row["intent_ok"]
    return intent


def run_gate(artifact_dir):
    """The fact-equality gate. Raises AssertionError on any divergence;
    returns a small summary dict on success."""
    d = pathlib.Path(artifact_dir)
    variants = {n: json.loads((d / n).read_text()) for n in VARIANT_ARTIFACTS}
    base = json.loads((d / BASE_ARTIFACT).read_text())

    facts_a = normalize_facts(variants["traceability_matrix.a.json"])
    facts_b = normalize_facts(variants["traceability_matrix.b.json"])
    facts_c = (
        normalize_facts(variants["traceability_matrix.symbolic.json"])
        | normalize_facts(variants["traceability_matrix.concrete.json"])
        | normalize_facts(variants[FORMAL_ARTIFACT])
    )
    if not (facts_a == facts_b == facts_c):
        raise AssertionError(
            "fact-equality gate failed: A/B/C fact sets differ; "
            f"A^B={sorted(facts_a ^ facts_b)} A^C={sorted(facts_a ^ facts_c)}"
        )

    symbolic_subset = {f for f in facts_a if f[1] == "crosshair"}
    base_facts = normalize_facts(base)
    if base_facts != symbolic_subset:
        raise AssertionError(
            "fact-equality gate failed: base matrix diverges from the "
            f"symbolic subset; delta={sorted(base_facts ^ symbolic_subset)}"
        )

    intents = {n: extract_intent(variants[n]) for n in VARIANT_ARTIFACTS}
    reference = intents[VARIANT_ARTIFACTS[0]]
    for name, values in intents.items():
        # Subset comparison, not strict dict equality: traceability_matrix.formal.json
        # (2026-07-07, Gate 2/C2-C4 wiring) only ever renders rows for
        # requirements that actually declare dafny evidence - REQ-DOSE-003
        # is permanently, deliberately out of dosage.dfy's scope (see the
        # spec's own header comment), so formal.json will never have an
        # opinion about it. That's a legitimate "doesn't cover this
        # requirement" absence, not a divergence - every requirement a
        # view DOES have an opinion about must still agree with the
        # reference exactly, and a requirement id the reference has never
        # heard of at all is still a hard failure.
        mismatched = {
            req: (reference[req], val)
            for req, val in values.items()
            if req in reference and reference[req] != val
        }
        unknown = sorted(set(values) - set(reference))
        if mismatched or unknown:
            raise AssertionError(
                f"fact-equality gate failed: intent_ok differs in {name}: "
                f"mismatched={mismatched} unknown_requirements={unknown}"
            )

    blocks = [variants[n]["bounds"] for n in VARIANT_ARTIFACTS]
    if not all(b == blocks[0] for b in blocks):
        raise AssertionError(
            "fact-equality gate failed: bounds block differs across views"
        )

    return {"facts": len(facts_a), "intent": reference}
