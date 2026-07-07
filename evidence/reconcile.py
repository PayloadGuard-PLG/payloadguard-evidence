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

VARIANT_ARTIFACTS is deliberately unchanged by the 2026-07-07 Gate 2/C2-C4
wiring: traceability_matrix.formal.json (variant C's third partition,
real Dafny-sourced PROVEN evidence) is NOT in this tuple, and run_gate()
below is NOT touched. Passing dafny_store into variants A and B is an
explicitly deferred follow-up (Steven: "can we post hoc verify A and B
after C variant is proven") - until it lands, A/B's own intent_ok for
REQ-GIP-1-4-12/REQ-GIP-1-8-1 stays False (no dafny binding there), while
the formal view's is True. That is a REAL, NAMED, TRACKED divergence,
not a bug - run_formal_check() below verifies it is exactly that
divergence and no other, the same "fail loudly on anything unexpected"
discipline the main gate already applies. See KNOWN_LIMITATIONS.md.
"""

import json
import pathlib

VARIANT_ARTIFACTS = (
    "traceability_matrix.a.json",
    "traceability_matrix.b.json",
    "traceability_matrix.symbolic.json",
    "traceability_matrix.concrete.json",
)
BASE_ARTIFACT = "traceability_matrix.json"
FORMAL_ARTIFACT = "traceability_matrix.formal.json"

# The only requirements allowed to diverge between the formal view and
# the A/B/symbolic/concrete reference, and only in the True direction
# (newly proven via dafny evidence) - named and tracked here rather than
# silently permitted. Remove this carve-out (and tighten
# run_formal_check to a plain equality) once variant A/B's own dafny
# wiring lands and their intent_ok catches up to match.
KNOWN_FORMAL_INTENT_DIVERGENCE = frozenset({"REQ-GIP-1-4-12", "REQ-GIP-1-8-1"})


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
    facts_c = normalize_facts(variants["traceability_matrix.symbolic.json"]) | (
        normalize_facts(variants["traceability_matrix.concrete.json"])
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
        if values != reference:
            raise AssertionError(
                f"fact-equality gate failed: intent_ok differs in {name}: "
                f"{values} != {reference}"
            )

    blocks = [variants[n]["bounds"] for n in VARIANT_ARTIFACTS]
    if not all(b == blocks[0] for b in blocks):
        raise AssertionError(
            "fact-equality gate failed: bounds block differs across views"
        )

    return {"facts": len(facts_a), "intent": reference}


def run_formal_check(artifact_dir, reference_intent):
    """Checks variant C's third partition (traceability_matrix.formal.json,
    real Dafny-sourced evidence) against the A/B/symbolic/concrete
    reference intent (run_gate()'s own return value - callers pass it
    straight through rather than recomputing it, keeping this a check
    ABOUT run_gate()'s result, not a second independent source of truth).

    Deliberately separate from run_gate() and from VARIANT_ARTIFACTS: the
    formal view is real, new, and not yet reconciled with variants A/B
    (that wiring is an explicitly deferred follow-up), so folding it into
    the strict all-must-match gate above would either hard-fail on a
    known, expected divergence or (worse) require softening that gate
    for everyone. Instead: every requirement's intent_ok must match the
    reference EXACTLY, except the named, tracked set in
    KNOWN_FORMAL_INTENT_DIVERGENCE, which must specifically be True (not
    just "different") - proving dafny evidence closed the intent gap it
    was meant to close, not just that something changed. Raises
    AssertionError on any unexpected or wrong-direction divergence;
    returns a small summary dict on success."""
    d = pathlib.Path(artifact_dir)
    formal = json.loads((d / FORMAL_ARTIFACT).read_text())
    formal_intent = extract_intent(formal)

    unexpected = {
        req: (reference_intent.get(req), formal_intent[req])
        for req in formal_intent
        if req not in KNOWN_FORMAL_INTENT_DIVERGENCE
        and formal_intent[req] != reference_intent.get(req)
    }
    if unexpected:
        raise AssertionError(
            f"formal-view intent check failed: unexpected divergence from "
            f"the A/B/symbolic/concrete reference: {unexpected}"
        )

    wrong_direction = {
        req: formal_intent[req]
        for req in KNOWN_FORMAL_INTENT_DIVERGENCE
        if req in formal_intent and formal_intent[req] is not True
    }
    if wrong_direction:
        raise AssertionError(
            "formal-view intent check failed: expected "
            f"{sorted(wrong_direction)} to be newly proven (intent_ok=True) "
            f"via dafny evidence, got {wrong_direction}"
        )

    return {
        "formal_requirements_checked": len(formal_intent),
        "known_divergence": sorted(KNOWN_FORMAL_INTENT_DIVERGENCE & formal_intent.keys()),
    }
