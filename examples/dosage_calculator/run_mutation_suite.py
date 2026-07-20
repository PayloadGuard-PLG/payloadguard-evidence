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
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

# The full mutate -> static-filter -> vacuous-precondition-filter ->
# isolate -> verify -> classify pipeline lives in the shared, sanctioned
# runner. This example mutates `method CalculateHourlyDose`'s clauses and
# `function ExpectedDose`'s body (the method+companion shape), passed to
# `mutants_with_outcomes` as clause target + `body_function`. Isolation is
# applied unconditionally there: the isolated unit is CalculateHourlyDose
# plus its callee ExpectedDose (the pin `dose == ExpectedDose(...)` stays
# in the unit, so a mutated body is still caught) and never a caller - and
# CalculateHourlyDose has no in-file callers, so isolation coincides with
# whole-file verification here, adding the guarantee without changing any
# outcome. See evidence/gate_c5_runner.py.
from evidence.gate_c5_runner import dafny_version, mutants_with_outcomes

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage.dfy"
METHOD = "CalculateHourlyDose"
FUNCTION = "ExpectedDose"


def main():
    source = TARGET.read_text()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    records = mutants_with_outcomes(source, METHOD, body_function=FUNCTION)

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
        "tool_version": dafny_version(),
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
