"""Phase C, Gate C5: the sanctioned mutation-testing runner.

`evidence/dafny_mutate.py` generates mutants and `evidence/dafny_isolate.py`
isolates a function from its callers, but a trustworthy kill/survive
count needs them composed: every mutant of a function must be verified
against that function *in isolation* (its own callees and datatypes,
never its callers), or a kill can be silently mis-attributed to the
mutated function when it was actually a downstream caller failing to
discharge the mutated precondition - the caller-confound documented in
`evidence/dafny_isolate.py`'s module docstring, reproduced against
`RoundHalfUp` (whole-file said more kills than the function's own
contract earns; three of the difference were `AssessRenalFunction`'s
failures, not `RoundHalfUp`'s).

This module is that composition, and it is deliberately the *only*
sanctioned way to produce a Gate C5 kill/survive count: `mutants_with_outcomes`
always isolates - there is no whole-file mode to forget to turn on. Any
code that calls `dafny_mutate.generate_mutants` directly and verifies the
resulting full (non-isolated) `mutated_source` for a function with
in-file callers is re-introducing exactly the bug this runner exists to
prevent; point Gate C5 at this module instead.

The per-mutant pipeline (generate across all five operator classes ->
static-filter -> vacuous-precondition filter -> isolate -> real Dafny
verify -> classify) is extracted verbatim from
`examples/renal_adjustment/run_mutation_suite_renal.py`, which now calls
`mutants_with_outcomes`; the two therefore cannot drift. Extending Gate
C5 to another example is a matter of calling this runner, not copying a
loop.
"""

import pathlib
import re
import subprocess
import tempfile

from evidence.dafny_adapter import _INCOMPLETE_MARKERS, _SUMMARY_RE
from evidence.dafny_isolate import (
    _parse_decls,
    _referenced_funcs,
    _strip_comments,
    isolate_function,
)
from evidence.dafny_mutate import (
    generate_aor_mutants,
    generate_coi_mutants,
    generate_lor_mutants,
    generate_lvr_mutants,
    generate_ror_mutants,
)
from evidence.dafny_spec_lint import check_precondition_satisfiability

_PARSE_ERROR_RE = re.compile(r"^.*: Error: .*$", re.MULTILINE)


def dafny_version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return r.stdout.strip() or r.stderr.strip()


def _classify(raw_output, exit_code):
    """Map a captured `dafny verify` run to an outcome. `exit_code`
    outside {0, 4} with an Error line is a parse-level rejection
    (unclassifiable), not a semantic kill - e.g. the `&&`/`||` ambiguity
    Dafny refuses to parse. A clean summary line with 0 errors is a
    survivor (the mutation went undetected); >0 errors is a kill."""
    matches = list(_SUMMARY_RE.finditer(raw_output))
    if exit_code not in (0, 4):
        parse_error = _PARSE_ERROR_RE.search(raw_output)
        if parse_error:
            detail = re.sub(r"^\S+\.dfy", "<mutant>.dfy", parse_error.group().strip())
        else:
            detail = f"unexpected exit_code={exit_code}"
        return "unclassifiable", detail
    if not matches:
        return "unclassifiable", "no verifier summary line in captured output"
    if len(matches) > 1:
        return "unclassifiable", f"{len(matches)} summary lines, ambiguous"
    verified_count, error_count, tail = (
        int(matches[0].group(1)),
        int(matches[0].group(2)),
        matches[0].group(3),
    )
    marker = next((m for m in _INCOMPLETE_MARKERS if m in tail.lower()), None)
    if marker is not None:
        return "unclassifiable", f"incomplete run ({marker!r} in summary line)"
    if error_count == 0:
        return "survived", f"{verified_count} verified, {error_count} errors"
    return "killed", f"{verified_count} verified, {error_count} errors"


def _real_verify(mutated_source):
    """Run the real Dafny verifier against `mutated_source` (an isolated,
    self-contained unit) in a scratch directory. Returns
    (outcome, detail, exit_code)."""
    with tempfile.TemporaryDirectory() as d:
        tmp_path = pathlib.Path(d) / "mutant.dfy"
        tmp_path.write_text(mutated_source)
        proc = subprocess.run(
            ["dafny", "verify", str(tmp_path)], capture_output=True, text=True
        )
        raw = (proc.stdout or "") + (proc.stderr or "")
        outcome, detail = _classify(raw, proc.returncode)
        return outcome, detail, proc.returncode


def _filtered_outcome(reason):
    if reason.startswith("chain-direction incompatible"):
        return "filtered_chain_incompatible"
    if reason.startswith("arithmetic-operator group incompatible"):
        return "filtered_ar_group_incompatible"
    if reason.startswith("magnitude-implied"):
        return "filtered_magnitude_implied"
    return "filtered_static"


def in_file_callers(source, function_name):
    """The set of functions/methods in `source` that reference
    `function_name` (its in-file callers) - the reverse of
    `dafny_isolate._referenced_funcs`. Informational: isolation is
    applied regardless, so this only records whether the confound *could*
    have arisen for this function under whole-file verification."""
    _datatypes, funcs = _parse_decls(_strip_comments(source))
    if function_name not in funcs:
        raise SystemExit(
            f"gate_c5_runner: no function or method named {function_name!r} "
            f"in source (declared: {sorted(funcs)})"
        )
    all_names = set(funcs)
    return {
        name
        for name in funcs
        if name != function_name
        and function_name in _referenced_funcs(funcs[name], name, all_names)
    }


def mutants_with_outcomes(source, function_name, body_arithmetic=False):
    """Every mutant of `function_name` (all five operator classes; body
    AOR/LVR too when `body_arithmetic` is set), each carried through
    static filtering, the vacuous-precondition filter, and - for anything
    that reaches real verification - ISOLATED Dafny verification. Returns
    a list of record dicts. Isolation is unconditional: there is no
    whole-file path here (see module docstring)."""
    body_fn = function_name if body_arithmetic else None
    mutants = (
        generate_ror_mutants(source, function_name)
        + generate_lor_mutants(source, function_name)
        + generate_aor_mutants(source, function_name, function_name=body_fn)
        + generate_coi_mutants(source, function_name)
    )
    records = []
    try:
        mutants += generate_lvr_mutants(source, function_name, function_name=body_fn)
    except SystemExit as e:
        # Defensive: the current generator covers arithmetic-embedded
        # literals, so this no longer fires for this repo's specs, but a
        # future spec shape could still trip a Tier-1 refusal - recorded,
        # never silently dropped.
        records.append({
            "function": function_name,
            "operator": "LVR",
            "keyword": "requires/ensures",
            "original_clause": None,
            "mutated_clause": None,
            "description": f"LVR generation for {function_name} could not proceed",
            "outcome": "blocked_lvr_clause_literal",
            "detail": str(e),
        })

    for m in mutants:
        record = {
            "function": function_name,
            "operator": m.operator,
            "keyword": m.keyword,
            "original_clause": m.original_clause,
            "mutated_clause": m.mutated_clause,
            "description": m.description,
        }
        if m.filtered_reason:
            record["outcome"] = _filtered_outcome(m.filtered_reason)
            record["detail"] = m.filtered_reason
            records.append(record)
            continue

        if m.keyword == "requires":
            # The Z3 precondition translator refuses (raises SystemExit)
            # rather than crashes on clause shapes it doesn't model - e.g. a
            # ROR mutant introducing a comparison between two datatype
            # operands, which Dafny accepts via its own structural rank
            # ordering but dafny_spec_lint only models for arithmetic sorts.
            # This is an expected path for datatype-heavy specs (the DDI
            # runner has caught it since PR #26); the sanctioned runner must
            # match that robustness or reuse on such a spec aborts the whole
            # Gate C5 run on the first untranslatable requires mutant. The
            # refusal says nothing about whether the mutant survives, so it
            # is recorded and the mutant still goes to real isolated
            # verification.
            try:
                verdict, detail = check_precondition_satisfiability(m.mutated_source, function_name)
            except SystemExit as e:
                record["precondition_check_outcome"] = "z3_translation_refused"
                record["precondition_check_detail"] = str(e)
            else:
                if verdict == "unsat":
                    record["outcome"] = "filtered_vacuous"
                    record["detail"] = detail
                    records.append(record)
                    continue

        isolated_source = isolate_function(m.mutated_source, function_name)
        outcome, detail, exit_code = _real_verify(isolated_source)
        record["outcome"] = outcome
        record["detail"] = detail
        record["exit_code"] = exit_code
        record["isolation_status"] = "isolated"
        records.append(record)

    return records


def run_gate_c5(filepath, function_name, body_arithmetic=False):
    """Sanctioned single-function Gate C5 entry point: read the .dfy at
    `filepath`, mutation-test `function_name` with unconditional
    isolation, and return a summary dict (with the surviving mutants
    enumerated). `isolation_used` is always true - that is the point."""
    source = pathlib.Path(filepath).read_text()
    callers = in_file_callers(source, function_name)
    records = mutants_with_outcomes(source, function_name, body_arithmetic)

    def _count(pred):
        return sum(1 for r in records if pred(r))

    killed = _count(lambda r: r["outcome"] == "killed")
    survived = _count(lambda r: r["outcome"] == "survived")
    unclassifiable = _count(lambda r: r["outcome"] == "unclassifiable")
    filtered = _count(
        lambda r: r["outcome"].startswith("filtered")
        or r["outcome"] == "blocked_lvr_clause_literal"
    )
    survivors = [
        {k: r[k] for k in ("operator", "keyword", "original_clause", "mutated_clause", "description")}
        for r in records
        if r["outcome"] == "survived"
    ]
    return {
        "function": function_name,
        "file": str(filepath),
        "had_in_file_callers": bool(callers),
        "in_file_callers": sorted(callers),
        "isolation_used": True,
        "generated": len(records),
        "filtered": filtered,
        "tested": killed + survived + unclassifiable,
        "killed": killed,
        "survived": survived,
        "unclassifiable": unclassifiable,
        "survivors": survivors,
    }
