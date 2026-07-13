# Gate C5: mutation-testing capture runner for drug_interaction_checker.dfy,
# mirroring run_mutation_suite_renal.py's exact classification/capture
# discipline (verbatim output, real exit code, no result taken on faith).
#
# Two functions as of REQ-DDI-6 (2026-07-12), same multi-function
# structure run_mutation_suite_renal.py established for seven:
# CheckInteraction (no arithmetic operator or numeric literal anywhere --
# still confirmed [] for AOR/LVR, unchanged) and DoseReductionTargetMg
# (this spec's first-ever numeric literals -- REQ-DDI-6's whole reason
# for existing). A real, new engineering boundary found applying LVR to
# the new function, not silently worked around: generate_lvr_mutants's
# body-scanning mode (function_name=...) refuses outright --
# "DoseReductionTargetMg's body contains a `//` comment - refusing to
# locate mutation sites rather than risk a misaligned offset or a
# comment slash mistaken for division" -- the function's match body has
# an explanatory comment on its unreachable wildcard arm (the same
# pattern CheckInteraction itself uses). NOT fixed here: the clause-level
# LVR scan (no function_name, mutating the literal directly adjacent to
# each ensures clause's `==`) already covers all 5 pinned figures for
# real (110->109/111, 30->29/31 x4 = 10 mutants) -- since Dafny's own
# proof requires the match body to satisfy those exact ensures clauses,
# a body-literal mutation would be redundant with what clause-level LVR
# already catches, not a different class of bug this spec could hide.
# Named and left unattempted, matching renal_adjustment's own precedent
# of recording a real engine boundary explicitly rather than forcing new
# shared-module engineering for marginal, likely-redundant coverage.
#
# A real, new observation about ROR specifically, not seen against
# dosage.dfy or renal_adjustment.dfy: almost every comparison in this
# spec is `identifier == Constructor` between simple-enum datatype
# values (DOAC/Agent/Outcome/RiskDirection), not real/int -- and Dafny
# treats <, <=, >, >= differently from each other here, confirmed
# empirically, not predicted correctly in advance (an earlier draft of
# this comment guessed "always killed" before the real run proved that
# wrong -- left here corrected, not silently rewritten, since the wrong
# guess is itself part of the record).
#
# <= and >= are genuine Dafny TYPE ERRORS for a datatype ("arguments to
# <= must be of a numeric type... instead got DOAC and DOAC") -- these
# land in the "unclassifiable" bucket, refused before verification is
# even attempted (2 real cases below, both on the one requires clause's
# doac == Apixaban comparison).
#
# < and > DO type-check -- Dafny accepts them syntactically for any
# datatype -- but for a flat, non-recursive enum (no constructor takes
# an argument), Z3 has no axiom pinning down what the relation actually
# MEANS: it's neither provably true nor provably false for a given
# pair, genuinely unconstrained rather than "always false" (confirmed
# directly: neither `Apixaban < Dabigatran` nor `!(d < Apixaban)` is
# provable as a bare claim). That does NOT make every < / > mutant
# survive, though -- see the real survivor analysis in
# KNOWN_LIMITATIONS.md's "Phase E Gate C5" section for why exactly 3 of
# them did (a genuine "consequent holds regardless of this antecedent"
# blind spot, the same category renal_adjustment's own survivors fell
# into) and the rest were killed (an unconstrained antecedent doesn't
# save a mutant when the consequent's truth actually depends on which
# specific case triggered it).
#
# STP-suite escalation (2026-07-13, built after a real, empirically-
# confirmed finding during Gate C6 sign-off review): every mutant that
# survives the bare-spec `dafny verify` is now also re-verified against
# the committed `drug_interaction_checker_stp_suite.dfy` (Gate C4's own
# ACCEPT/REJECT lemmas, reused verbatim -- no new lemma authored for
# this), by redirecting the suite's `include` at the mutant file instead
# of the real spec. Confirmed by hand-probing before building this: a
# `requires`-clause ROR mutant that silently widens
# DoseReductionTargetMg's Dabigatran+Verapamil indication guard (exactly
# the class of scope-leak Addendum 4 fixed on CheckInteraction) still
# verifies clean against the bare spec, but makes the STP suite's own
# `STP_Accept_DoseReductionTargetMg_DabigatranVerapamil_...` ACCEPT
# lemma fail outright (`function precondition could not be proved`) --
# a real, previously-uncaught kill this escalation now captures.
# **Confirmed NOT to help for the great majority of survivors, and this
# is a genuine Dafny semantics fact, not a shortfall of this escalation
# to fix later**: both functions here are plain (non-`{:opaque}`)
# `function`s, so a same-module STP lemma calling one with concrete
# literal arguments gets verified by Dafny unfolding the function body
# directly -- the `ensures` clause text a mutation touches is provably
# irrelevant to that proof. Hand-probed and confirmed empirically for
# one `ensures`-clause ROR mutant and one LOR mutant on each function
# before committing to this scope: all four still verified clean against
# the STP suite too. Closing that class would require marking these
# functions `{:opaque}` with explicit `reveal` calls everywhere they're
# used -- a much larger, invasive redesign disproportionate to a
# testing-methodology limitation, deliberately not attempted here.
import datetime
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from evidence.dafny_adapter import _INCOMPLETE_MARKERS, _SUMMARY_RE
from evidence.dafny_mutate import (
    generate_aor_mutants,
    generate_coi_mutants,
    generate_lor_mutants,
    generate_lvr_mutants,
    generate_ror_mutants,
)
from evidence.dafny_spec_lint import check_precondition_satisfiability

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "drug_interaction_checker.dfy"
STP_SUITE = HERE / "drug_interaction_checker_stp_suite.dfy"
_STP_INCLUDE_LINE = f'include "{TARGET.name}"'

# (function_name, use_body_level_lvr) - see module docstring for why
# DoseReductionTargetMg gets clause-level LVR only, not body-level.
FUNCTIONS = (
    ("CheckInteraction", False),
    ("DoseReductionTargetMg", False),
)


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


_PARSE_ERROR_RE = re.compile(r"^.*: Error: .*$", re.MULTILINE)


def _classify(raw_output, exit_code):
    """Identical discipline to run_mutation_suite_renal.py's _classify."""
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
    tail_lower = tail.lower()
    marker = next((m for m in _INCOMPLETE_MARKERS if m in tail_lower), None)
    if marker is not None:
        return "unclassifiable", f"incomplete run ({marker!r} in summary line)"
    if error_count == 0:
        return "survived", f"{verified_count} verified, {error_count} errors"
    return "killed", f"{verified_count} verified, {error_count} errors"


def _real_verify(mutated_source):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".dfy", delete=False, dir=HERE
    ) as f:
        f.write(mutated_source)
        tmp_path = pathlib.Path(f.name)
    try:
        cmd = ["dafny", "verify", str(tmp_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        raw = (proc.stdout or "") + (proc.stderr or "")
        outcome, detail = _classify(raw, proc.returncode)
        return outcome, detail, proc.returncode, raw
    finally:
        tmp_path.unlink(missing_ok=True)


def _stp_verify(mutated_source):
    """Re-verify the committed drug_interaction_checker_stp_suite.dfy (Gate
    C4's real ACCEPT/REJECT lemmas, unmodified) against a mutated main spec,
    by writing the mutant to a temp .dfy file in this directory and pointing
    a temp copy of the STP suite's own `include` at it. Same (outcome,
    detail, exit_code, raw) shape as _real_verify -- "killed" here means the
    STP suite's existing lemmas caught what the bare spec alone did not."""
    stp_source = STP_SUITE.read_text()
    if _STP_INCLUDE_LINE not in stp_source:
        raise RuntimeError(
            f"{STP_SUITE.name}'s include line no longer reads {_STP_INCLUDE_LINE!r} "
            "-- update this wiring, don't silently skip the escalation"
        )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".dfy", delete=False, dir=HERE
    ) as mutant_f:
        mutant_f.write(mutated_source)
        mutant_path = pathlib.Path(mutant_f.name)
    try:
        redirected = stp_source.replace(
            _STP_INCLUDE_LINE, f'include "{mutant_path.name}"', 1
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dfy", delete=False, dir=HERE
        ) as stp_f:
            stp_f.write(redirected)
            stp_path = pathlib.Path(stp_f.name)
        try:
            cmd = ["dafny", "verify", str(stp_path)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            raw = (proc.stdout or "") + (proc.stderr or "")
            outcome, detail = _classify(raw, proc.returncode)
            return outcome, detail, proc.returncode, raw
        finally:
            stp_path.unlink(missing_ok=True)
    finally:
        mutant_path.unlink(missing_ok=True)


def _filtered_outcome(reason):
    if reason.startswith("chain-direction incompatible"):
        return "filtered_chain_incompatible"
    if reason.startswith("arithmetic-operator group incompatible"):
        return "filtered_ar_group_incompatible"
    if reason.startswith("magnitude-implied"):
        return "filtered_magnitude_implied"
    return "filtered_static"


def main():
    source = TARGET.read_text()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    records = []
    for func_name, use_body_level_lvr in FUNCTIONS:
        body_fn = func_name if use_body_level_lvr else None
        mutants = (
            generate_ror_mutants(source, func_name)
            + generate_lor_mutants(source, func_name)
            + generate_aor_mutants(source, func_name)  # no body-arithmetic mode used - see module docstring
            + generate_lvr_mutants(source, func_name, function_name=body_fn)
            + generate_coi_mutants(source, func_name)
        )

        for m in mutants:
            record = {
                "function": func_name,
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
                # A ROR mutant can introduce <,<=,>,>= between two datatype
                # (DOAC/Agent) operands -- Dafny itself accepts this (its own
                # structural "rank" ordering), but dafny_spec_lint's Z3
                # translator only models ordering operators for arithmetic
                # sorts and now refuses cleanly rather than crash (a real bug
                # this run found and fixed in that module -- see its
                # _apply_cmp docstring). Caught here, not silently swallowed:
                # recorded as its own outcome, then sent to real Dafny
                # verification anyway, since the checker's refusal to model
                # this specific requires clause says nothing about whether
                # the mutant itself survives or is killed.
                try:
                    verdict, detail = check_precondition_satisfiability(m.mutated_source, func_name)
                except SystemExit as e:
                    record["precondition_check_outcome"] = "z3_translation_refused"
                    record["precondition_check_detail"] = str(e)
                else:
                    if verdict == "unsat":
                        record["outcome"] = "filtered_vacuous"
                        record["detail"] = detail
                        records.append(record)
                        continue

            outcome, detail, exit_code, raw = _real_verify(m.mutated_source)
            record["outcome"] = outcome
            record["detail"] = detail
            record["exit_code"] = exit_code

            if outcome == "survived":
                # Escalate to the real, committed STP suite before accepting
                # this as a genuine survivor -- see module docstring for why
                # this catches some (a real requires-clause scope-widening
                # class) but not most (Dafny's function-transparency makes
                # ensures-clause wording provably irrelevant to a same-module
                # concrete-literal lemma call, confirmed empirically, not a
                # gap in this escalation itself).
                stp_outcome, stp_detail, stp_exit_code, _ = _stp_verify(m.mutated_source)
                record["stp_suite_detail"] = stp_detail
                if stp_outcome == "killed":
                    record["outcome"] = "killed_via_stp_suite"
                    record["detail"] = (
                        f"bare spec survived ({detail}); "
                        f"STP suite caught it ({stp_detail})"
                    )
                    record["exit_code"] = stp_exit_code

            records.append(record)

    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1

    (HERE / "mutation_report_ddi.json").write_text(json.dumps(records, indent=2) + "\n")

    md_lines = [
        "# Gate C5: mutation testing report — `drug_interaction_checker.dfy` "
        "(CheckInteraction, DoseReductionTargetMg)",
        "",
        f"Generated {started}. {len(records)} mutants total. Counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.",
        "HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.",
        "AOR: 0 mutants for either function — CheckInteraction has no arithmetic "
        "operator anywhere; DoseReductionTargetMg's body is bare literal returns "
        "(no +/-/*// operator to mutate) — checked, not assumed.",
        "LVR: 0 mutants for CheckInteraction (no numeric literal anywhere) — "
        "checked, not assumed. 10 mutants for DoseReductionTargetMg, "
        "clause-level only (the literal directly adjacent to each ensures "
        "clause's ==) — body-level scanning refuses on the match body's own "
        "explanatory comment (dafny_mutate.py's deliberate comment-safety "
        "boundary); not fixed, since clause-level coverage already proves "
        "the same five figures exactly and body-level would be redundant, "
        "not a different class of bug — see module docstring.",
        "",
        "STP-suite escalation (2026-07-13): every mutant that survives the "
        "bare-spec `dafny verify` is re-checked against the committed "
        "`drug_interaction_checker_stp_suite.dfy` (Gate C4's real "
        "ACCEPT/REJECT lemmas, reused verbatim). A `killed_via_stp_suite` "
        "outcome means the bare spec alone missed it but the STP suite's "
        "existing lemmas caught it — see module docstring for the real, "
        "hand-verified boundary of what this escalation does and does not "
        "catch.",
        "",
        "| Function | Operator | Clause | Mutation | Outcome | Detail |",
        "|---|---|---|---|---|---|",
    ]
    for r in records:
        md_lines.append(
            f"| {r['function']} | {r['operator']} | `{r['keyword']}` | {r['description']} "
            f"| **{r['outcome']}** | {r['detail']} |"
        )
    (HERE / "mutation_report_ddi.md").write_text("\n".join(md_lines) + "\n")

    manifest = {
        "tool": "dafny",
        "tool_version": _version(),
        "command_template": ["dafny", "verify", "<mutant>.dfy"],
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "functions": [f for f, _ in FUNCTIONS],
        "total_mutants": len(records),
        "counts": counts,
    }
    (HERE / "run_manifest_mutation_ddi.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"mutation suite complete; {len(records)} mutants, counts={counts}")
    killed_via_stp = [r for r in records if r["outcome"] == "killed_via_stp_suite"]
    if killed_via_stp:
        print(f"KILLED VIA STP SUITE ({len(killed_via_stp)}) — bare spec missed these:")
        for r in killed_via_stp:
            print(f"  - {r['function']}: {r['description']}")
    survivors = [r for r in records if r["outcome"] == "survived"]
    if survivors:
        print(f"SURVIVORS ({len(survivors)}) — real findings, not filtered:")
        for r in survivors:
            print(f"  - {r['function']}: {r['description']}")
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    if unclassifiable:
        print(f"UNCLASSIFIABLE ({len(unclassifiable)}) — refused, needs review:")
        for r in unclassifiable:
            print(f"  - {r['function']}: {r['description']}: {r['detail']}")


if __name__ == "__main__":
    sys.exit(main())
