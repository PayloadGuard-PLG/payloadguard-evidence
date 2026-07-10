"""Phase E, Gate C3: applying the shared vectors 1-2 spec-lint machinery
(evidence/dafny_spec_lint.py) to the real, committed
drug_interaction_checker.dfy spec, mirroring
tests/test_renal_adjustment_spec_lint.py's real-spec application.

Real gap found applying this (2026-07-10): CheckInteraction's precondition
directly compares its `doac`/`agent` parameters against datatype
constructors (`doac == Apixaban`, `agent == Rifampicin`, ...) - genuinely
different from renal_adjustment's own Gate C3 gap (a datatype-typed
parameter never referenced by any requires clause). Confirmed to refuse
before this extension existed: `check_precondition_satisfiability` only
modeled real/int/nat/bool parameter types, with no representation for a
Dafny datatype at all, referenced or not. Fixed in dafny_spec_lint.py by
modeling simple (zero-argument-constructor) datatypes as a Z3 EnumSort -
see that module's docstring and test_dafny_spec_lint.py's new regression
tests for the extension itself. This file is the real-spec application
that surfaced it and confirms it holds for the real, committed spec.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_spec_lint import (  # noqa: E402
    check_precondition_satisfiability,
    scan_weak_postconditions,
)

SPEC = (REPO_ROOT / "examples" / "drug_interaction_checker" / "drug_interaction_checker.dfy").read_text()


# ------------------------------------------------- vector 1: satisfiability

def test_check_interaction_precondition_is_satisfiable():
    """CheckInteraction's requires clause -- excluding the two agents'
    still-blocked apixaban cells (Gate 1c Finding 2) -- is not vacuous: a
    Dafny 'clean pass' on this spec proves what it appears to prove, not
    something trivially true because no (doac, agent) pair could ever
    satisfy the precondition."""
    verdict, detail = check_precondition_satisfiability(SPEC, "CheckInteraction")
    assert verdict == "sat", detail


def test_check_interaction_no_longer_refused_for_its_datatype_comparisons():
    """Named regression for the real gap this file's module docstring
    describes: CheckInteraction's requires clause directly compares
    doac/agent (both simple-enum datatypes) against named constructors --
    the check must model this, not refuse on it."""
    verdict, _ = check_precondition_satisfiability(SPEC, "CheckInteraction")
    assert verdict == "sat"


# --------------------------------------------- vector 2: weak postconditions

def test_check_interaction_weak_postcondition_count_matches_the_real_spec():
    """Every one of CheckInteraction's 60 pinning ensures clauses uses a
    one-way ==> -- expected, not a regression, same pattern already
    established for renal_adjustment's GStage/SelectFormula/
    AssessRenalFunction: each clause dispatches on an exhaustive,
    mutually-exclusive antecedent (one Agent, or one (DOAC, Agent) pair),
    and Gate C4's real STP suite (22 verified, 0 errors) independently
    proves a representative set of them pinning, not just satisfied -- a
    stronger, proof-based check than this heuristic lint provides on its
    own. The function's clean Dafny verification (1 verified, 0 errors)
    is itself only possible because Dafny proved all 60 implications hold
    given the match body, which structurally requires every antecedent to
    correctly correspond to a reachable match arm -- a transcription
    mismatch between a match guard and its ensures antecedent would have
    made that proof fail, not just triggered this heuristic. Pinned exact
    count so a future change to any ensures clause is caught, not
    silently absorbed."""
    warnings = scan_weak_postconditions(SPEC, "CheckInteraction")
    assert len(warnings) == 60, len(warnings)
