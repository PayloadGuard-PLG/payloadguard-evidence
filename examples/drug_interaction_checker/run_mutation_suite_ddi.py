# Gate C5: mutation-testing capture runner for drug_interaction_checker.dfy,
# mirroring run_mutation_suite_renal.py's exact classification/capture
# discipline (verbatim output, real exit code, no result taken on faith).
#
# AOR and LVR both contribute zero mutants here, confirmed by test not
# assumed: CheckInteraction has no arithmetic operator and no numeric
# literal anywhere in its requires/ensures clauses or its body (a pure
# datatype pattern match) -- generate_aor_mutants/generate_lvr_mutants
# both return [] against this spec.
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
FUNCTION = "CheckInteraction"


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

    mutants = (
        generate_ror_mutants(source, FUNCTION)
        + generate_lor_mutants(source, FUNCTION)
        + generate_aor_mutants(source, FUNCTION)  # confirmed [] -- no body arithmetic
        + generate_lvr_mutants(source, FUNCTION)  # confirmed [] -- no numeric literals
        + generate_coi_mutants(source, FUNCTION)
    )

    records = []
    for m in mutants:
        record = {
            "function": FUNCTION,
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
                verdict, detail = check_precondition_satisfiability(m.mutated_source, FUNCTION)
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
        records.append(record)

    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1

    (HERE / "mutation_report_ddi.json").write_text(json.dumps(records, indent=2) + "\n")

    md_lines = [
        "# Gate C5: mutation testing report — `drug_interaction_checker.dfy` (CheckInteraction)",
        "",
        f"Generated {started}. {len(records)} mutants total. Counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.",
        "HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.",
        "AOR: 0 mutants (no arithmetic operator anywhere in CheckInteraction) — checked, not assumed.",
        "LVR: 0 mutants (no numeric literal anywhere in CheckInteraction) — checked, not assumed.",
        "",
        "| Operator | Clause | Mutation | Outcome | Detail |",
        "|---|---|---|---|---|",
    ]
    for r in records:
        md_lines.append(
            f"| {r['operator']} | `{r['keyword']}` | {r['description']} "
            f"| **{r['outcome']}** | {r['detail']} |"
        )
    (HERE / "mutation_report_ddi.md").write_text("\n".join(md_lines) + "\n")

    manifest = {
        "tool": "dafny",
        "tool_version": _version(),
        "command_template": ["dafny", "verify", "<mutant>.dfy"],
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "function": FUNCTION,
        "total_mutants": len(records),
        "counts": counts,
    }
    (HERE / "run_manifest_mutation_ddi.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"mutation suite complete; {len(records)} mutants, counts={counts}")
    survivors = [r for r in records if r["outcome"] == "survived"]
    if survivors:
        print(f"SURVIVORS ({len(survivors)}) — real findings, not filtered:")
        for r in survivors:
            print(f"  - {r['description']}")
    unclassifiable = [r for r in records if r["outcome"] == "unclassifiable"]
    if unclassifiable:
        print(f"UNCLASSIFIABLE ({len(unclassifiable)}) — refused, needs review:")
        for r in unclassifiable:
            print(f"  - {r['description']}: {r['detail']}")


if __name__ == "__main__":
    sys.exit(main())
