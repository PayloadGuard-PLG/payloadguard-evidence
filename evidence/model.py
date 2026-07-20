from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# Phase-B Dafny parser note (do not lose before Phase B): the committed Dafny
# verification log's load-bearing line is, verbatim:
#     Dafny program verifier finished with N verified, 0 errors
# Known failure mode: a false-zero bug exists in some Dafny versions — the
# parser must assert the literal substring "0 errors" is present in the log,
# not merely trust a zero exit code.

class Strength(str, Enum):
    PROVEN = "PROVEN"                    # Dafny proof / discharged Z3 VC
    BOUNDED_CHECKED = "BOUNDED_CHECKED"  # CrossHair pass within recorded bounds
    TESTED = "TESTED"                    # concrete test cases executed
    EXAMPLE_CHECKED = "EXAMPLE_CHECKED"  # specific recorded input/output pairs executed
    DECLARED = "DECLARED"                # human assertion, no tool evidence
    GAP = "GAP"                          # nothing established; human input needed

CAVEAT = {
    Strength.PROVEN: "Formally proven against the stated specification.",
    Strength.BOUNDED_CHECKED: "No counterexample found within the recorded bounds; this is a bounded search, not a proof.",
    Strength.TESTED: "Exercised on the recorded test cases only.",
    Strength.EXAMPLE_CHECKED: "Holds for the specific recorded inputs only; no claim of generality beyond them.",
    Strength.DECLARED: "Asserted by the author; not established by any tool.",
    Strength.GAP: "Not established. Human input required.",
}

# Proof-content qualifier on a PROVEN Dafny row (Gate C3 vector 3, derived
# mechanically by evidence.spec_impl_gap). PROVEN stays literally true - Dafny
# did discharge the spec - but "Formally proven against the stated
# specification" reads as "we proved the requirement holds," which overclaims
# for a spec that merely restates its own implementation. These qualifiers say
# plainly what the proof does and does not certify. `None` = not applicable
# (no result-constraining postcondition to classify).
PROOF_CONTENT_CAVEAT = {
    "definitional": (
        "Definitional proof: the postcondition restates the implementation "
        "(ensures is equivalent to the body), so the proof obligation is a "
        "tautology discharged by reflexivity. Certified: totality, "
        "type-safety, match-exhaustiveness, and the literal boundary "
        "structure of the definition. NOT certified: an independent property "
        "beyond the definition, or fidelity to the source requirement."
    ),
    "property": (
        "Property proof: the postcondition is strictly weaker than the "
        "implementation (the body implies it but not conversely), so the "
        "proof establishes content beyond the definition - a wrong "
        "implementation could satisfy the body's shape yet violate it. Still "
        "does not certify fidelity of the numbers/modeling to the source."
    ),
}

@dataclass
class VerificationResult:
    method: str
    code_location: str
    raw_status: str
    strength: Strength
    run_id: str
    timestamp: str
    bounds: Optional[dict] = None
    counterexample: Optional[str] = None
    # Phase C, Gate C1: whether the verifier actually completed a run
    # ("completed") vs. produced no summary line at all - a crash, a
    # timeout, or a tool that "did not attempt verification" (confirmed
    # real: `dafny audit` reports exactly that on some inputs). Distinct
    # from a completed run that reports errors (that's strength=GAP with
    # raw_status carrying the error count, not an incomplete run). Only
    # meaningful for adapter-produced results so far (evidence/dafny_adapter.py);
    # None for CrossHair/pytest-backed records, which have no equivalent
    # ambiguity to guard against.
    verifier_completion_status: Optional[str] = None

@dataclass
class RequirementBinding:
    requirement_id: str
    requirement_text: str
    code_location: str
    result: Optional[VerificationResult]
    intended_method: str
    intent_matches_reality: bool = True
    notes: list = field(default_factory=list)
