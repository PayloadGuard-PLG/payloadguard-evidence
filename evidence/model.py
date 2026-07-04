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

@dataclass
class RequirementBinding:
    requirement_id: str
    requirement_text: str
    code_location: str
    result: Optional[VerificationResult]
    intended_method: str
    intent_matches_reality: bool = True
    notes: list = field(default_factory=list)
