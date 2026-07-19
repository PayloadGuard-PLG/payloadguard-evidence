"""Unit tests for evidence/dafny_isolate.py's single-function isolation
(Gate C5 caller-confound fix). Pure structural logic - no Dafny
invocation (the real-Dafny confirmation that isolated units verify clean
and that the confounded mutants flip to SURVIVED is captured once by the
mutation runner, mirroring test_dafny_mutate.py's own no-Dafny
convention)."""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.dafny_isolate import (  # noqa: E402
    _parse_decls,
    _referenced_funcs,
    _strip_comments,
    isolate_function,
)

RENAL = (REPO_ROOT / "examples" / "renal_adjustment" / "renal_adjustment.dfy").read_text()


def test_parse_decls_finds_every_renal_function_and_datatype():
    datatypes, funcs = _parse_decls(_strip_comments(RENAL))
    assert set(funcs) == {
        "RoundHalfUp", "GStage", "SelectFormula", "ComposedCeiling",
        "AssessRenalFunction", "CockcroftGaultCrClMlPerMin",
        "AssessRenalFunctionFromInputs",
    }
    assert [name for name, _text in datatypes] == [
        "GStageCategory", "Formula", "RenalAssessment",
    ]


def test_leaf_function_isolates_to_itself_plus_datatypes_no_callers():
    iso = isolate_function(RENAL, "RoundHalfUp")
    assert "function RoundHalfUp" in iso
    # every caller is excluded
    assert "function AssessRenalFunction" not in iso
    assert "function AssessRenalFunctionFromInputs" not in iso
    # datatypes are always carried
    assert "datatype GStageCategory" in iso


def test_non_leaf_includes_transitive_callees_excludes_callers():
    """AssessRenalFunction calls GStage and RoundHalfUp (callees, kept)
    and is called by AssessRenalFunctionFromInputs (a caller, dropped)."""
    iso = isolate_function(RENAL, "AssessRenalFunction")
    assert "function AssessRenalFunction(" in iso
    assert "function GStage" in iso
    assert "function RoundHalfUp" in iso
    assert "function AssessRenalFunctionFromInputs" not in iso
    # an unrelated sibling that AssessRenalFunction doesn't call is dropped
    assert "function SelectFormula" not in iso


def test_full_down_closure_for_the_top_orchestrator():
    """AssessRenalFunctionFromInputs calls SelectFormula, AssessRenalFunction,
    CockcroftGaultCrClMlPerMin - transitively pulling in GStage and
    RoundHalfUp too. It has no callers, so nothing is dropped."""
    iso = isolate_function(RENAL, "AssessRenalFunctionFromInputs")
    for fn in [
        "AssessRenalFunctionFromInputs", "SelectFormula", "AssessRenalFunction",
        "CockcroftGaultCrClMlPerMin", "GStage", "RoundHalfUp",
    ]:
        assert f"function {fn}" in iso, fn


def test_self_reference_does_not_seed_the_closure():
    """A function names itself in its own ensures clauses; that must not
    be treated as a call that pulls anything extra in."""
    _datatypes, funcs = _parse_decls(_strip_comments(RENAL))
    refs = _referenced_funcs(funcs["RoundHalfUp"], "RoundHalfUp", set(funcs))
    assert refs == set()  # RoundHalfUp calls nothing but itself


def test_isolate_refuses_unknown_function():
    with pytest.raises(SystemExit, match="no function or method named"):
        isolate_function(RENAL, "NoSuchFunction")


def test_synthetic_caller_is_excluded_even_when_it_shares_a_datatype():
    source = """
    datatype T = A | B
    function Callee(x: int): int
      requires x >= 0
      ensures Callee(x) >= 0
    { x }
    function Caller(y: int): int
      requires y >= 0
      ensures Caller(y) >= 0
    { Callee(y) }
    """
    iso = isolate_function(source, "Callee")
    assert "function Callee" in iso
    assert "function Caller" not in iso
    assert "datatype T" in iso
