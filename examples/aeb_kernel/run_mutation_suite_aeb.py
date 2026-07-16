# Phase D, Gate C5: mutation-testing capture runner for aeb_kernel.dfy,
# mirroring examples/renal_adjustment/run_mutation_suite_renal.py's exact
# classification/capture discipline (verbatim output, real exit code, no
# result taken on faith).
#
# Real structural note for this spec, checked not assumed: all six
# functions are pure comparison/match logic in their bodies - no +, -, *,
# or / operator anywhere (confirmed by reading aeb_kernel.dfy directly).
# So AOR/LVR body-level mutation (the function_name= argument in
# generate_aor_mutants/generate_lvr_mutants) has nothing to target for any
# of the six - function_name stays None throughout, and only the
# requires/ensures CLAUSE-level generators (ROR/LOR/AOR-on-clauses/
# LVR-on-clauses/COI) run. This differs from renal_adjustment.dfy, which
# had two functions with real body arithmetic (RoundHalfUp,
# CockcroftGaultCrClMlPerMin).
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
TARGET = HERE / "aeb_kernel.dfy"

FUNCTIONS = (
    "FCWRequiredActive",
    "AEBRequiredActive",
    "IsSubjectVehicleBrakingOnset",
    "IsLeadVehicleBrakingOnset",
    "IsBrakePedalApplicationOnset",
    "IsFalseActivationCompliant",
)


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


_PARSE_ERROR_RE = re.compile(r"^.*: Error: .*$", re.MULTILINE)


def _classify(raw_output, exit_code):
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

    records = []
    for func_name in FUNCTIONS:
        mutants = (
            generate_ror_mutants(source, func_name)
            + generate_lor_mutants(source, func_name)
            + generate_aor_mutants(source, func_name)
            + generate_coi_mutants(source, func_name)
        )
        try:
            mutants += generate_lvr_mutants(source, func_name)
        except SystemExit as e:
            records.append({
                "function": func_name,
                "operator": "LVR",
                "keyword": "requires/ensures",
                "original_clause": None,
                "mutated_clause": None,
                "description": f"LVR generation for {func_name} could not proceed",
                "outcome": "blocked_lvr_clause_literal",
                "detail": str(e),
            })

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
                verdict, detail = check_precondition_satisfiability(m.mutated_source, func_name)
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

    (HERE / "mutation_report_aeb.json").write_text(json.dumps(records, indent=2) + "\n")

    md_lines = [
        "# Gate C5: mutation testing report — `aeb_kernel.dfy` (all 6 functions)",
        "",
        f"Generated {started}. {len(records)} mutants total. Counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.",
        "HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.",
        "AOR/LVR body mutation: NOT APPLICABLE to any function's own body — "
        "all six are pure comparison/match logic with no +, -, *, or / "
        "operator in any function body (confirmed by reading aeb_kernel.dfy "
        "directly); clause-level ROR/LOR/AOR/LVR/COI (on requires/ensures) "
        "still run for all six.",
        "",
        "| Function | Operator | Clause | Mutation | Outcome | Detail |",
        "|---|---|---|---|---|---|",
    ]
    for r in records:
        md_lines.append(
            f"| {r['function']} | {r['operator']} | `{r['keyword']}` | {r['description']} "
            f"| **{r['outcome']}** | {r['detail']} |"
        )
    (HERE / "mutation_report_aeb.md").write_text("\n".join(md_lines) + "\n")

    manifest = {
        "tool": "dafny",
        "tool_version": _version(),
        "command_template": ["dafny", "verify", "<mutant>.dfy"],
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "functions": list(FUNCTIONS),
        "total_mutants": len(records),
        "counts": counts,
    }
    (HERE / "run_manifest_mutation_aeb.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"mutation suite complete; {len(records)} mutants, counts={counts}")
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
