# Phase C, Gate C5: mutation-testing capture runner. Generates every
# mutant evidence.dafny_mutate can produce for CalculateHourlyDose,
# filters out statically-trivial and vacuous-precondition mutants (passes
# 1-2), and real-verifies every survivor against the installed Dafny
# binary (pass 3) - mirroring run_verify_dafny.py's capture discipline
# (verbatim output, real exit code, no result taken on faith).
#
# Mutant .dfy files are NOT committed individually (they are mechanically
# derived, one text substitution from the base spec - unlike the STP
# suites, which are hand-authored artifacts worth auditing on their own).
# What IS committed is this script, the real outcome of every mutant
# (mutation_report.json/.md), and one aggregate manifest
# (run_manifest_mutation.json) - the report's job is to make every real
# capture's outcome auditable without needing 30+ near-duplicate raw
# files.
import datetime
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from evidence.dafny_adapter import _INCOMPLETE_MARKERS, _SUMMARY_RE
from evidence.dafny_mutate import generate_mutants
from evidence.dafny_spec_lint import check_precondition_satisfiability

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage.dfy"
METHOD = "CalculateHourlyDose"
FUNCTION = "ExpectedDose"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


_PARSE_ERROR_RE = re.compile(r"^.*: Error: .*$", re.MULTILINE)


def _classify(raw_output, exit_code):
    """Same real-capture discipline dafny_adapter.parse_dafny_capture
    uses for a committed spec capture, applied per-mutant: never trust a
    bare exit code, always require exactly one summary line, and treat
    any incomplete-run marker as unclassifiable rather than a result."""
    matches = list(_SUMMARY_RE.finditer(raw_output))
    if exit_code not in (0, 4):
        # exit_code == 2 is a real, observed case (a chained comparison
        # like `0.0 <= dose <= max` mutated on only one side produces a
        # direction-incompatible chain, e.g. `0.0 >= dose <= max`).
        # Confirmed against the Dafny Reference Manual (Sec 5.2.1-5.2.2)
        # and dafny.org/latest/HowToFAQ/Errors, not just this repo's own
        # empirical observation: chained relational operators must stay
        # "same direction" (equality mixes freely into either direction;
        # </=/<= cannot chain with >/>=). This produces a genuine PARSER
        # rejection, not a verifier failure; relay Dafny's own error line
        # rather than a bare code, since this is a mutation-engine gap
        # (it doesn't yet model chain-direction compatibility - a real,
        # scoped follow-up: restrict each chain link's mutation
        # candidates to direction-compatible operators, eliminating this
        # by construction - see gate_c5_mutation_testing_research_findings.md),
        # not a spec finding.
        parse_error = _PARSE_ERROR_RE.search(raw_output)
        if parse_error:
            # Strip the temp file's generated name/path so the committed
            # report is deterministic across regenerations - the file
            # path is an artifact of this run, not of the finding.
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
    """Distinguish WHY a mutant was filtered before real verification -
    four different reasons, four different outcome buckets, so a reader
    never has to parse the detail text to know which applies."""
    if reason.startswith("chain-direction incompatible"):
        return "filtered_chain_incompatible"
    if reason.startswith("arithmetic-operator group incompatible"):
        return "filtered_ar_group_incompatible"
    if reason.startswith("magnitude-implied"):
        return "filtered_magnitude_implied"
    return "filtered_static"


def main():
    source = TARGET.read_text()
    mutants = generate_mutants(source, METHOD, function_name=FUNCTION)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    records = []
    for m in mutants:
        record = {
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
            verdict, detail = check_precondition_satisfiability(m.mutated_source, METHOD)
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

    (HERE / "mutation_report.json").write_text(json.dumps(records, indent=2) + "\n")

    md_lines = [
        "# Gate C5: mutation testing report — `dosage.dfy::CalculateHourlyDose`",
        "",
        f"Generated {started}. {len(records)} mutants total. Counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.",
        "HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.",
        "AOR: 0 mutants against this spec's requires/ensures clauses (no arithmetic in any "
        "clause) + 3 against ExpectedDose's function body (its one `*` operator), restricted "
        "per MutDafny's own group rule (+/-/* freely interchange; never introduce `/`, "
        "eliminating the division-by-zero false-kill risk by construction).",
        "LVR: every numeric literal in this spec is exactly `0.0` (7 sites: 5 clause-level, "
        "2 in ExpectedDose's function body); each mutated to `+/- 0.01` (the clinical-"
        "precision floor). Clause-level LT/LE/GT/GE-adjacent literals are filtered per the "
        "requires/ensures magnitude-implication principle; EQ/NE-adjacent and all "
        "function-body literals are never filtered.",
        "",
        "| Operator | Clause | Mutation | Outcome | Detail |",
        "|---|---|---|---|---|",
    ]
    for r in records:
        md_lines.append(
            f"| {r['operator']} | `{r['keyword']}` | {r['description']} "
            f"| **{r['outcome']}** | {r['detail']} |"
        )
    (HERE / "mutation_report.md").write_text("\n".join(md_lines) + "\n")

    manifest = {
        "tool": "dafny",
        "tool_version": _version(),
        "command_template": ["dafny", "verify", "<mutant>.dfy"],
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "method": METHOD,
        "total_mutants": len(records),
        "counts": counts,
    }
    (HERE / "run_manifest_mutation.json").write_text(json.dumps(manifest, indent=2) + "\n")

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
