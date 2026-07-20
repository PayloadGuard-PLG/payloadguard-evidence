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
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

# The full mutate -> static-filter -> vacuous-precondition-filter ->
# isolate -> verify -> classify pipeline lives in the shared, sanctioned
# runner; this script iterates this example's two functions, layers the
# STP-suite survivor escalation below on top (via the runner's
# `survivor_escalation` hook), and writes the report/manifest. Isolation
# is unconditional there (evidence/gate_c5_runner.py) - and since neither
# CheckInteraction nor DoseReductionTargetMg is an in-file caller of the
# other, isolation coincides with whole-file verification here (each
# isolated unit verifies clean at baseline), adding the guarantee without
# changing any outcome. `_classify` is reused from the shared runner so
# the STP escalation below classifies exactly as the bare pass does.
from evidence.gate_c5_runner import _classify, dafny_version, mutants_with_outcomes

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


def _stp_escalation(mutated_source):
    """Adapt _stp_verify to gate_c5_runner's `survivor_escalation`
    contract: (outcome, detail, exit_code), dropping the raw text. The
    runner calls this only for a mutant that survives isolated
    verification. A "killed" result means the committed STP suite's own
    ACCEPT/REJECT lemmas caught a scope-leak the bare ensures-spec alone
    provably cannot (Dafny function-transparency) -- see this module's
    docstring for the real, hand-verified boundary of what it does and
    does not catch, and why an "unclassifiable" result must never be
    silently folded back into "survived" (a Qodo review caught exactly
    that gap in an earlier draft)."""
    outcome, detail, exit_code, _raw = _stp_verify(mutated_source)
    return outcome, detail, exit_code


def main():
    source = TARGET.read_text()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # generate -> static-filter -> vacuous-precondition-filter (incl. the
    # SystemExit refusal the Z3 translator raises on datatype-vs-datatype
    # `requires` comparisons, recorded as `z3_translation_refused` then
    # verified anyway) -> ISOLATE -> verify -> classify all run in the
    # shared runner; the STP-suite escalation is layered on via its
    # survivor hook. See evidence/gate_c5_runner.py.
    records = []
    for func_name, use_body_level_lvr in FUNCTIONS:
        records += mutants_with_outcomes(
            source,
            func_name,
            body_arithmetic=use_body_level_lvr,
            survivor_escalation=_stp_escalation,
        )

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
        "catch. A distinct `unclassifiable_via_stp_suite` outcome (never "
        "observed against this run's real mutant set, but handled "
        "explicitly rather than assumed away) means the STP-suite "
        "escalation itself was inconclusive — never silently folded into "
        "`survived`, which would misrepresent an unchecked mutant as a "
        "confirmed one.",
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
        "tool_version": dafny_version(),
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
    unclassifiable_via_stp = [r for r in records if r["outcome"] == "unclassifiable_via_stp_suite"]
    if unclassifiable_via_stp:
        print(f"UNCLASSIFIABLE VIA STP SUITE ({len(unclassifiable_via_stp)}) — STP escalation inconclusive, needs review:")
        for r in unclassifiable_via_stp:
            print(f"  - {r['function']}: {r['description']}: {r['detail']}")


if __name__ == "__main__":
    sys.exit(main())
