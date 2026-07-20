"""Unit tests for evidence/gate_c5_runner.py - the sanctioned Gate C5
runner that composes mutation generation with caller-isolation.

No real Dafny invocation (mirroring test_dafny_mutate.py /
test_dafny_isolate.py): the mutation generators, the isolation slicer,
and the Z3-backed precondition check all run for real (they are fast and
Dafny-free), and the single Dafny-verify step is monkeypatched so the
composition - filtering, the vacuous-precondition filter, unconditional
isolation, and the tally - is exercised without shelling out to the
verifier. The real end-to-end numbers are locked in against committed
captures by tests/test_renal_mutation_report.py, which the renal runner
regenerates through this very module."""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence import gate_c5_runner  # noqa: E402
from evidence.gate_c5_runner import in_file_callers, mutants_with_outcomes, run_gate_c5  # noqa: E402

RENAL = REPO_ROOT / "examples" / "renal_adjustment" / "renal_adjustment.dfy"
RENAL_SRC = RENAL.read_text()

# A tiny self-contained spec: Leaf has one in-file caller (Caller); Caller
# has none. Small enough that the generators produce a handful of mutants.
SYNTHETIC = """
function Leaf(x: int): int
  requires x >= 0
  ensures Leaf(x) >= 0
{ x }
function Caller(y: int): int
  requires y >= 0
  ensures Caller(y) >= 0
{ Leaf(y) }
"""


def test_in_file_callers_reverse_lookup_matches_the_real_spec():
    # ComposedCeiling is called by nothing; the two called functions are
    # reached from AssessRenalFunction / AssessRenalFunctionFromInputs.
    assert in_file_callers(RENAL_SRC, "ComposedCeiling") == set()
    assert in_file_callers(RENAL_SRC, "RoundHalfUp") >= {"AssessRenalFunction"}
    assert in_file_callers(RENAL_SRC, "CockcroftGaultCrClMlPerMin") == {
        "AssessRenalFunctionFromInputs"
    }
    assert in_file_callers(RENAL_SRC, "AssessRenalFunctionFromInputs") == set()


def test_in_file_callers_refuses_unknown_function():
    with pytest.raises(SystemExit, match="no function or method named"):
        in_file_callers(RENAL_SRC, "NoSuchFunction")


def test_every_verified_mutant_is_isolated(monkeypatch):
    """The hard constraint: anything that reaches real verification is
    verified in isolation - there is no whole-file path. With the verify
    step stubbed, every non-filtered record must still carry
    isolation_status == 'isolated'."""
    calls = {"n": 0}

    def fake_verify(source):
        calls["n"] += 1
        # The source handed to the verifier must be the ISOLATED unit -
        # Leaf's caller must never appear in it.
        assert "Caller" not in source
        return "survived", "1 verified, 0 errors", 0

    monkeypatch.setattr(gate_c5_runner, "_real_verify", fake_verify)
    records = mutants_with_outcomes(SYNTHETIC, "Leaf")
    verified = [r for r in records if r["outcome"] in ("killed", "survived", "unclassifiable")]
    assert verified, "expected some mutants to reach verification"
    assert calls["n"] == len(verified)
    for r in verified:
        assert r.get("isolation_status") == "isolated", r["description"]


def test_filtered_mutants_never_reach_verification(monkeypatch):
    """Statically filtered and vacuous-precondition mutants are tallied
    without a verify call and carry no isolation_status."""
    monkeypatch.setattr(
        gate_c5_runner, "_real_verify",
        lambda s: ("survived", "1 verified, 0 errors", 0),
    )
    records = mutants_with_outcomes(SYNTHETIC, "Leaf")
    filtered = [r for r in records if r["outcome"].startswith("filtered")]
    assert filtered, "the synthetic spec should produce at least one static-filtered mutant"
    for r in filtered:
        assert "isolation_status" not in r


def test_run_gate_c5_summary_shape_and_tally(monkeypatch, tmp_path):
    monkeypatch.setattr(
        gate_c5_runner, "_real_verify",
        lambda s: ("survived", "1 verified, 0 errors", 0),
    )
    spec = tmp_path / "s.dfy"
    spec.write_text(SYNTHETIC)
    summary = run_gate_c5(str(spec), "Leaf")

    assert summary["function"] == "Leaf"
    assert summary["isolation_used"] is True
    assert summary["had_in_file_callers"] is True
    assert summary["in_file_callers"] == ["Caller"]
    # tally self-consistency
    assert summary["tested"] == summary["killed"] + summary["survived"] + summary["unclassifiable"]
    assert summary["generated"] >= summary["filtered"] + summary["tested"]
    # every survivor row carries the reporting fields, no internals
    for s in summary["survivors"]:
        assert set(s) == {"operator", "keyword", "original_clause", "mutated_clause", "description"}


def test_run_gate_c5_reports_no_callers_for_a_leaf(monkeypatch, tmp_path):
    monkeypatch.setattr(
        gate_c5_runner, "_real_verify",
        lambda s: ("killed", "0 verified, 1 error", 1),
    )
    spec = tmp_path / "s.dfy"
    spec.write_text(SYNTHETIC)
    summary = run_gate_c5(str(spec), "Caller")
    assert summary["had_in_file_callers"] is False
    assert summary["in_file_callers"] == []
    assert summary["survived"] == 0  # every verified mutant "killed" under the stub
