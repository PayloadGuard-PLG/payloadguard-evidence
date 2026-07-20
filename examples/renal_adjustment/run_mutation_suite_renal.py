# Phase D, Gate C5: mutation-testing capture runner for renal_adjustment.dfy,
# mirroring examples/dosage_calculator/run_mutation_suite.py's exact
# classification/capture discipline (verbatim output, real exit code, no
# result taken on faith) - see that file's own header comment for why
# mutants are generated, not committed individually.
#
# Real structural difference from dosage.dfy, named rather than papered
# over: dosage.dfy has one `method` (the trusted implementation) plus one
# companion `function` (ExpectedDose, the pinning spec) - AOR/LVR mutate
# only the function's body, never the method's. renal_adjustment.dfy has
# no method at all: all seven declarations are `function`s, each its own
# proof target, several calling several others rather than one calling one
# companion. So this script runs the FULL five-operator-class suite
# independently against each of the seven functions, and additionally
# mutates a function's OWN body (AOR/LVR) for the two functions whose
# bodies actually contain arithmetic (RoundHalfUp, CockcroftGaultCrClMlPerMin)
# - the other five have no arithmetic operator or literal in their bodies
# at all (confirmed by inspection: SelectFormula/GStage/ComposedCeiling are
# pure comparison/branch logic; AssessRenalFunction/AssessRenalFunctionFromInputs
# only call other functions), so body-mutation would contribute nothing for
# them, not a coverage gap.
#
# Four real gaps in the shared engine found applying it here (2026-07-09),
# each fixed or named rather than worked around - see evidence/dafny_mutate.py:
#   1. Its lexical tokenizer had no DOT or QUESTION token, so RoundHalfUp's
#      body `(x + 0.5).Floor` and AssessRenalFunction's ensures clauses
#      (`.EGFRAssessment?`/`.CrClAssessment?`, this repo's first use of a
#      built-in member-access call or a datatype discriminator in a
#      mutated body/clause) raised "unsupported syntax" - fixed, a small
#      extension of the same class as the existing COMMA/SEMI tolerance.
#   2. LVR always formatted a mutated literal as a decimal (`90.01`),
#      breaking Dafny's static typing for the many INT-typed boundary
#      literals in this spec (`roundedEgfr >= 90`, `ageYears < 140`, ...)
#      - dosage.dfy's own literals were all already real-typed (`0.0`),
#      so this never surfaced before. Fixed: a literal's own lexical form
#      (decimal point present or not) now determines whether its mutant
#      stays an int (+/-1) or a real (+/-0.01).
#   3. Two functions' ensures clauses have a literal embedded in
#      arithmetic rather than directly adjacent to a comparison operator
#      - RoundHalfUp (`(RoundHalfUp(x) as real) - 0.5 <= x < ...`) and
#      CockcroftGaultCrClMlPerMin (140/88.4/72.0/0.85, deep inside the
#      pinning equality's RHS). The LVR clause-literal locator originally
#      refused these outright. FIXED 2026-07-19 (dafny_mutate.py fixes
#      4a/4b): arithmetic-embedded literals are now a distinct,
#      never-statically-filtered LVR category (their narrowing/widening
#      direction can't be inferred from adjacency, so they always go to
#      real verification), and a literal comparison-adjacent on one side
#      but arithmetic-adjacent on the other is no longer mis-filtered as
#      a bare operand (a former silent false-pass). So both functions now
#      get real LVR coverage; the former "blocked_lvr_clause_literal"
#      placeholder outcome no longer occurs. The five generators are
#      still called individually (not via generate_mutants) so a future
#      refusal in one class doesn't drop another's coverage - the
#      defensive except-branch below is kept for that reason.
#   4. SelectFormula's ensures clause antecedent is a flat, unparenthesized
#      run of six `||` terms; LOR mutating any one `||` to `&&` produces
#      Dafny's own genuine "Ambiguous use of && and ||" parser rejection.
#      Unlike ROR's analogous, already-fixed chain-direction problem, this
#      was NOT built into a static pre-filter here - real new engineering
#      (grouping same-paren-depth &&/|| runs), not a bounded fix. Recorded
#      as "unclassifiable" (10 mutants, all SelectFormula/LOR) - named in
#      tests/test_renal_mutation_report.py, not silently absorbed.
#
# Every mutant is verified against the mutated function in ISOLATION
# (evidence/dafny_isolate.py: the function plus its own transitive
# callees and datatypes, never its callers) so a kill is attributable to
# the function's own contract, not a downstream caller failing to
# discharge the mutated precondition. Without this, whole-file
# verification over-reported kills for any function with in-file callers
# (RoundHalfUp's `requires x >= 0.0` widenings were scored KILLED
# whole-file, but the failure was inside AssessRenalFunction, a caller;
# in isolation they SURVIVE unless RoundHalfUp's own contract catches
# them - which, after the `ensures RoundHalfUp(x) >= 0` tightening, it
# now does).
#
# 53 real survivors resulted from this run - all explained, categorized,
# and locked in as regression assertions in
# tests/test_renal_mutation_report.py and examples/renal_adjustment/README.md's
# Gate C5 amendment, not an undifferentiated pile: (1) ROR/LVR mutations
# narrowing a one-way `==>` clause's antecedent, which can never be
# killed regardless of spec correctness (a structural blind spot of this
# technique against guard-style clauses - Gate C4's STP suite pins
# these); (2) requires-clause weakenings not load-bearing for the
# specific ensures clauses currently proven (real, but not a defect -
# note ComposedCeiling's and RoundHalfUp's qualitative precondition
# weakenings are NO LONGER here: the two spec tightenings made those
# preconditions load-bearing, so they now kill at the function's own
# contract); (3) RoundHalfUp's one AOR survivor, a coincidental numeric
# fact about its self-referential postcondition; (4) RoundHalfUp's two
# ensures-LVR rounding-tolerance widenings (`0.5 -> 0.51`), now generated
# by the fixed LVR locator - a looser tolerance still holds for the exact
# round-half-up body. Categories (3) and (4) are independently pinned by
# Gate C4's STP suite regardless.
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

# The full mutate -> isolate -> verify -> classify pipeline lives in the
# shared, sanctioned runner; this script only iterates this example's
# seven functions and writes the report/manifest. Isolation is applied
# unconditionally there (see evidence/gate_c5_runner.py) - there is no
# whole-file path to forget.
from evidence.gate_c5_runner import dafny_version, mutants_with_outcomes

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "renal_adjustment.dfy"

# (function_name, has_body_arithmetic) - see module docstring for why only
# two of the seven get body-level AOR/LVR mutation.
FUNCTIONS = (
    ("RoundHalfUp", True),
    ("GStage", False),
    ("SelectFormula", False),
    ("ComposedCeiling", False),
    ("AssessRenalFunction", False),
    ("CockcroftGaultCrClMlPerMin", True),
    ("AssessRenalFunctionFromInputs", False),
)


def main():
    source = TARGET.read_text()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    records = []
    for func_name, has_body_arithmetic in FUNCTIONS:
        records += mutants_with_outcomes(source, func_name, has_body_arithmetic)

    counts = {}
    for r in records:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1

    (HERE / "mutation_report_renal.json").write_text(json.dumps(records, indent=2) + "\n")

    md_lines = [
        "# Gate C5: mutation testing report — `renal_adjustment.dfy` (all 7 functions)",
        "",
        f"Generated {started}. {len(records)} mutants total. Counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
        "SOR: 0 mutants (no set-typed operations in this spec) — NOT APPLICABLE, checked.",
        "HOR: 0 mutants (no heap/object state, old()/reads/modifies) — NOT APPLICABLE, checked.",
        "AOR/LVR body mutation applied only to RoundHalfUp and "
        "CockcroftGaultCrClMlPerMin — the only two functions with arithmetic "
        "operators or numeric literals in their own bodies; the other five "
        "are pure comparison/branch/call logic with nothing to mutate there.",
        "",
        "| Function | Operator | Clause | Mutation | Outcome | Detail |",
        "|---|---|---|---|---|---|",
    ]
    for r in records:
        md_lines.append(
            f"| {r['function']} | {r['operator']} | `{r['keyword']}` | {r['description']} "
            f"| **{r['outcome']}** | {r['detail']} |"
        )
    (HERE / "mutation_report_renal.md").write_text("\n".join(md_lines) + "\n")

    manifest = {
        "tool": "dafny",
        "tool_version": dafny_version(),
        "command_template": ["dafny", "verify", "<mutant>.dfy"],
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "functions": [f for f, _ in FUNCTIONS],
        "total_mutants": len(records),
        "counts": counts,
    }
    (HERE / "run_manifest_mutation_renal.json").write_text(json.dumps(manifest, indent=2) + "\n")

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
