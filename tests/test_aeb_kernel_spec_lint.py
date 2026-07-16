"""Phase D, Gate C3: applying the shared vectors 1-2 spec-lint machinery
(evidence/dafny_spec_lint.py) to the real, committed aeb_kernel.dfy spec,
mirroring tests/test_renal_adjustment_spec_lint.py's real-spec-application
pattern.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_spec_lint import (  # noqa: E402
    check_precondition_satisfiability,
    scan_weak_postconditions,
)

SPEC = (REPO_ROOT / "examples" / "aeb_kernel" / "aeb_kernel.dfy").read_text()

ALL_FUNCTIONS = (
    "FCWRequiredActive",
    "AEBRequiredActive",
    "IsSubjectVehicleBrakingOnset",
    "IsLeadVehicleBrakingOnset",
    "IsBrakePedalApplicationOnset",
    "IsFalseActivationCompliant",
)


# ------------------------------------------------- vector 1: satisfiability

def test_every_function_precondition_is_satisfiable():
    """None of the six functions' requires clauses are vacuous - a Dafny
    'clean pass' on aeb_kernel.dfy proves what it appears to prove, not
    something trivially true because no input could ever satisfy the
    precondition."""
    for name in ALL_FUNCTIONS:
        verdict, detail = check_precondition_satisfiability(SPEC, name)
        assert verdict == "sat", f"{name}: {detail}"


# --------------------------------------------- vector 2: weak postconditions

def test_no_function_has_weak_postcondition_warnings():
    """Every ensures clause in aeb_kernel.dfy is a bi-implication (<==>),
    not a bare one-way ==> - each function's postcondition pins its result
    exactly for every input, not just in one direction. Unlike
    renal_adjustment.dfy's GStage/SelectFormula/AssessRenalFunction (which
    genuinely need one-way ==> to dispatch across branches), every
    aeb_kernel.dfy function is a single boolean predicate, so a full <==>
    is both possible and the tighter spec. Confirmed empirically (all six
    functions return 0 warnings), not assumed from the source reading
    biconditional - scan_weak_postconditions treats any clause containing
    <==> as strong regardless of an outer one-way ==> guard (see that
    function's own docstring), which is exactly FCWRequiredActive/
    AEBRequiredActive's shape (`target == X ==> (result <==> ...)`)."""
    for name in ALL_FUNCTIONS:
        warnings = scan_weak_postconditions(SPEC, name)
        assert warnings == [], f"{name}: {warnings}"
