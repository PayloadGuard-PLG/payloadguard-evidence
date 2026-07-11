# Drug-Drug Interaction Checker — Audit-Trail Record

Third, independent proof-of-concept for the PayloadGuard evidence
layer: checking a specific DOAC (direct oral anticoagulant) and
co-prescribed agent against a known interactions table, and returning
an outcome/risk-direction pair — verified with the same Gate C1–C6
Dafny/Z3 pipeline built for `dosage_calculator/` and
`renal_adjustment/`, on a UK-jurisdiction clinical example (NHS
Specialist Pharmacy Service) chosen specifically to stress
set/list-membership logic (a bounded pairwise lookup table), distinct
from `dosage.dfy`'s arithmetic clamping and `renal_adjustment.dfy`'s
lookup-table/conditional-branching shape.

This file is the fixed audit-trail record — source citations,
interpretive-call caveats, and dated amendments. For **current, living
status** (what's built vs. open, the concrete next step), see
`PHASE1_PLAN.md` and the repository root's `HANDOFF.md`; this file
doesn't duplicate that and isn't kept in lockstep with it turn by turn.

## Source documents

| Document | Role |
|---|---|
| NHS Specialist Pharmacy Service (SPS), "Managing interactions with direct oral anticoagulants (DOACs)." Published 5 January 2024, last updated 20 June 2025. `https://www.sps.nhs.uk/articles/managing-interactions-with-direct-oral-anticoagulants-doacs/` | Every requirement (`REQ-DDI-1` through `REQ-DDI-6`) — the sole primary source, chosen over BNF Appendix 1 / MHRA Drug Safety Update after direct comparison (publicly fetchable with no login wall; genuinely bounded, 4 DOACs × ~17 named agents, not an open-ended database; versioned in this repo's own citation style; states its own scope boundary explicitly). Fetched directly (raw HTML via `curl`, not an AI-summarized pass) and cross-checked against an earlier WebFetch summarization pass — see the amendment below for what that earlier pass missed. Archived verbatim: `sources/sps-doac-interactions-2024.md`. |

## Requirement-to-source mapping

| ID | Requirement | Built? |
|---|---|---|
| `REQ-DDI-1` | The checker returns an `InteractionResult(outcome, direction)` pair, never a bare boolean. `outcome` is one of `NoInteractionExpected`, `Caution`, `CautionLowRelevance`, `Avoid`, `Contraindicated`, `DoseReductionAdvised`, `NotCovered`; `direction` is `BleedingRisk \| ThrombosisRisk \| NoRisk \| UnknownRisk`. | `CheckInteraction` — proven |
| `REQ-DDI-2` | A total, hardcoded pairwise lookup over 15 of the source's 17 named sections in v1 (14 uniform + SSRIs/SNRIs, `REQ-DDI-3`'s own row), with a precondition excluding the two still-deferred apixaban cells (`REQ-DDI-5`) as a provable impossibility rather than a silent gap. | `CheckInteraction` — proven |
| `REQ-DDI-3` | SSRIs/SNRIs: dabigatran's dose-reduction advice is conditional on a caller-supplied `hasOtherBleedingRiskFactors: bool` — both branches proven, not just the one exercised first. Same trust-boundary shape as `renal_adjustment.dfy`'s `REQ-RENAL-8`. | `CheckInteraction` — proven |
| `REQ-DDI-4` | Fail-safe: any `(doac, agent)` pair outside the source's named set — including within-source gaps like apixaban+dronedarone — returns `NotCovered`, never silently `NoInteractionExpected`. Same "never default to the safe-looking answer on missing data" principle as `renal_adjustment.dfy`'s `REQ-RENAL-4`. | `CheckInteraction` — proven |
| `REQ-DDI-5` | Rifampicin and carbamazepine/phenytoin/phenobarbital make apixaban's outcome depend on a third axis, clinical indication (AF-stroke-prevention/DVT-PE-recurrence-prevention vs. other indications) — genuinely new modeling (a `TreatmentIndication` caller input), not a cheap flag addition. | Prose only — not built in v1, named and deferred |
| `REQ-DDI-6` | The `DoseReductionAdvised` outcome *kind* is proven in v1; the specific numeric dose-reduction target (e.g. dabigatran→110 mg BD with verapamil) is v1 informational text only, not a proven output. | Not built — staged v2, per direct instruction ("both but in order of difficulty") |

**Explicit non-goal, not deferred:** allergy/cross-sensitivity checking
(e.g. penicillin-class cross-reactivity) is a related but distinct
clinical concern from pharmacokinetic drug-drug interaction and is out
of scope for this example entirely — same pattern as
`renal_adjustment`'s per-drug numeric dose-reduction-factor exclusion.

Full requirement text and per-row source citations: `PHASE1_PLAN.md`'s
requirements table.

## Interpretive-call caveats

1. **This proof establishes correct outcome lookup *given* a
   correctly-classified `Agent` value — not that a real-world drug name
   actually belongs to the class/agent category the caller supplies**
   (e.g. "is drug X actually an SSRI"). Same trust boundary
   `REQ-RENAL-8` draws for `SelectFormula`'s classification flags in
   `renal_adjustment.dfy` — a permanent, deliberate one, not a proof
   gap awaiting future formalization.
2. **The outcome taxonomy's risk-direction axis (`BleedingRisk` vs.
   `ThrombosisRisk`) was not in the first draft — Gate 1c Finding 1
   caught it.** `Caution`/`Avoid`/`Contraindicated` alone describe *how
   strongly* to act, not *which direction* the risk runs; rifampicin
   and carbamazepine/phenytoin/phenobarbital are both agents that
   *decrease* DOAC levels (thrombosis risk), the opposite clinical
   concern from most other interactions on the source page (bleeding
   risk). Resolved by adding the `direction` field, not by treating the
   stronger-outcome axis as sufficient on its own.
3. **`CheckInteraction`'s precondition, excluding `(Apixaban,
   {Rifampicin, Carbamazepine, Phenytoin, Phenobarbital})`, is an
   indication-dependent scope exclusion, not a source gap.** The source
   *does* address apixaban for these four agents ("use apixaban with
   caution") but only for two named indications, an explicit
   branch `REQ-DDI-5` doesn't model in v1 — genuinely different from
   the apixaban+dronedarone cell, where the source never mentions
   apixaban at all (a real, sourced silence, correctly labeled
   `NotCovered`). An earlier draft of the Gate C6 sign-off document
   conflated these two; caught and corrected during Steven's own review
   — see the Gate C6 sign-off amendment below.
4. **The two `CautionLowRelevance` cells (rivaroxaban+verapamil,
   rivaroxaban+fluconazole) are a genuine three-way ambiguity in the
   primary source, not a gap in reading it.** The source hedges
   ("unlikely to be clinically relevant") without ever giving digoxin's
   clean, unqualified negative ("No interactions are expected") —
   distinct from both `Caution` and `NoInteractionExpected`, resolved
   by adding a fourth outcome case rather than forcing a choice between
   the two existing ones.
5. **No `set`/`seq` Dafny types are used anywhere in this spec.**
   `DOAC`/`Agent` are enumerated closed `datatype`s (15 v1-scoped
   agents), which sidesteps a Z3-translator engineering gap for
   set/sequence membership checking that was originally flagged as a
   risk for this example. That gap would only become load-bearing for
   checking a new drug against an entire, open, caller-supplied
   medication list — named as a real v3-or-later candidate, not built
   here.

## Amendment 2026-07-10 — Gate 1c audit: three real findings, all resolved by explicit decision

Full trace: `GATE_1C_AUDIT.md`. Every one of the source's 17 sections
carries an explicit risk-direction subheading, confirmed by grepping
the raw extracted text, not assumed. Three findings, each given an
actual decision (unlike `renal_adjustment`'s own Finding 1, which was
deliberately left open):

1. **Outcome taxonomy dropped the source's risk-direction axis**
   (caveat 2, above). Fixed by adding a `direction` field.
2. **`CheckInteraction` was not total over its own declared `Agent`
   type.** `Rifampicin`/`Carbamazepine`/`Phenytoin`/`Phenobarbital`
   constructors exist for all four DOACs, but `REQ-DDI-5` only defers
   each agent's *apixaban* cell — the other three DOACs' cells for
   each of these four agents are real, well-defined v1 claims. Fixed
   with a type-level exclusion precondition
   (`requires !(doac == Apixaban && agent in {...})`) rather than
   removing all four agents from `Agent` until `REQ-DDI-5` is built.
3. **Two source cells had no committed outcome-kind mapping**
   (caveat 4, above). Fixed by adding `CautionLowRelevance`.

Six worked-example hand-traces re-derived against the redesigned spec
to confirm the fix introduced no new inconsistency, including the exact
cell Finding 3 originally flagged as unresolved
(`(Rivaroxaban, Verapamil)` → `CautionLowRelevance`) and a new one
exercising Finding 2's precondition
(`(Apixaban, Rifampicin)` → excluded, "a provable impossibility rather
than a silently wrong or undefined answer").

## Amendment 2026-07-10 — Gate C1: a real false-clean result caught before committing

An early draft of `drug_interaction_checker.dfy` with no `ensures`
clauses at all reported `Dafny program verifier finished with 0
verified, 0 errors` — not a pass with nothing to disprove, but zero
verification tasks generated in the first place, since
match-exhaustiveness is a resolve-time syntax check, not an SMT proof.
Fixed by adding three real pinning `ensures` clauses (a
`NotCovered`-implies-the-one-real-source-gap pin, a
`Contraindicated`-implies-`Dabigatran` pin, a `Digoxin`-always-safe
pin) before committing anything. Re-verified clean: `1 verified, 0
errors`, real resource cost 113,039. Capture:
`raw_dafny_output_ddi.txt`, `run_manifest_dafny_ddi.json`.

## Amendment 2026-07-10 — Gate C4 found the Gate C1 fix was itself only a stopgap, far larger than `renal_adjustment`'s equivalent gap

A hand-derived prediction, checked before building: would a real
IronSpec ACCEPT lemma restating just the three `ensures` clauses added
above prove `(Dabigatran, Ketoconazole)` is `Contraindicated`? It did
not — `0 verified, 1 error`, a genuine failing capture, preserved as
`drug_interaction_checker_stp_suite_against_underconstrained.dfy`
(`raw_dafny_output_ddi_stp_suite_against_underconstrained.txt`, `0
verified, 3 errors` across all three probe lemmas). Unlike
`renal_adjustment`'s own Gate C4 finding (postconditions *bounded* a
result without *pinning* it), most of the 60 unpinned match arms here
had **no constraint at all** — the match body's correctness was never
actually a signature-level claim.

Fixed by restating all 63 match arms as explicit pinning `ensures`
clauses on `CheckInteraction` itself. Re-verified clean: `1 verified, 0
errors`, resource cost 358,399 (up from 113,039 pre-fix, still
completing in well under a second) — the heaviest single verification
task recorded across all three worked examples. The real STP suite
(`drug_interaction_checker_stp_suite.dfy`) then adds 7 ACCEPT lemmas
(6 established worked-example cells, including both branches of the
caller-supplied-flag SSRI/SNRI case) plus 4 REJECT lemmas (3 for the
`Contraindicated` cells — the highest-stakes rows in the table,
proving a plausible-but-wrong weaker `Caution` candidate is genuinely
excluded — plus one re-testing Finding 3's original ambiguity) — **11
lemmas total.** Dafny's own capture reads `22 verified, 0 errors`
(`raw_dafny_output_ddi_stp_suite.txt`) — confirmed empirically that
this counts roughly two verification tasks per lemma, not a 1:1 lemma
count; several of this repo's own docs previously misread that figure
as "22 lemmas," corrected in place 2026-07-10.

## Amendment 2026-07-10 — Gate C3 required genuinely extending shared tooling, not just applying it

`evidence/dafny_spec_lint.py::check_precondition_satisfiability`
refused `CheckInteraction`'s precondition outright on first attempt
(`unsupported Dafny parameter type 'DOAC'`) — `doac == Apixaban`
compares a datatype value directly, a case the shared Z3 translator had
never needed to model, since `renal_adjustment`'s one datatype-typed
parameter was never referenced by any precondition. Fixed by
representing simple, zero-argument-constructor Dafny datatypes as a Z3
`EnumSort` (`_parse_enum_datatypes`, new). A second, independent,
generally-applicable bug caught while testing the extension: Z3
registers `EnumSort` names globally per process, not per call, so two
callers modeling a same-named type collide
(`enumeration sort name is already declared`) — fixed with a monotonic
per-call disambiguating tag. Verified against the real spec: the
precondition is `sat` (real Z3 model: `agent = Naproxen, doac =
Dabigatran`); vector 2 flags all 60 pinning `ensures` clauses, exactly
as many as exist — expected, independently STP-covered by Gate C4.

## Amendment 2026-07-10 — Gate C2 confirmed, no new gap

The PROVEN-exclusivity binder
(`evidence/render/matrix_variants.py::dafny_record()` /
`assert_no_realized_proven`) had never been run against an
independently-authored spec's real capture before —
`renal_adjustment` never reached this point (no `metadata.yaml` was
ever built for it at the time). Run for real: produces a genuine
`{"method": "dafny", "strength": "PROVEN",
"verifier_completion_status": "completed"}` record, accepted cleanly.
Two negative-case checks (tampered `method="crosshair"`, tampered
`verifier_completion_status="incomplete"`) confirm the rule still
independently refuses, not just trusting the binder's own diligence.

## Amendment 2026-07-10 — Gate C5: 962 mutants, a real crash bug fixed mid-run, then 7 explained survivors

`run_mutation_suite_ddi.py`, ROR/LOR/COI against `CheckInteraction`'s
one `requires` clause and 60 `ensures` clauses; AOR and LVR both
confirmed contributing **zero** mutants — no arithmetic operator or
numeric literal anywhere in this spec, checked, not assumed.

**A real crash, not a Dafny finding, caught mid-run:** a ROR mutant
introducing `<=`/`>=` between two `DOAC` datatype operands crashed
`evidence/dafny_spec_lint.py`'s Z3 translator with a raw Python
`TypeError` — Z3's Python bindings don't overload ordering operators
for `DatatypeRef`. Fixed in `_apply_cmp` (a `z3.is_arith` guard,
refusing cleanly via `SystemExit` instead of crashing) — a
shared-module fix, shipped as its own PR before the full mutation run
could even complete.

**Final real run: 962 mutants — 564 killed, 389 filtered_static, 7
survived, 2 unclassifiable.** The 2 unclassifiable are genuine Dafny
type errors on `<=`/`>=` between `DOAC` values (`"arguments to <= must
be of a numeric type... instead got DOAC and DOAC"`) — a materially
different failure mode from `renal_adjustment`'s own unclassifiable
case (a parser ambiguity, not a type error). An earlier draft's
prediction that `<`/`>` between datatype values would be "always
killed" was wrong — corrected in place in `run_mutation_suite_ddi.py`'s
own comments, left visible rather than silently rewritten, once two
direct Dafny probes disproved it.

The 7 survivors fall into the same two structural categories
`renal_adjustment`'s own Gate C5 already established — no new category
of finding:

1. **4 survivors** mutate the one `requires` clause's `doac ==
   Apixaban` comparison — none of the 60 `ensures` clauses makes any
   claim about the `(Apixaban, {Rifampicin, Carbamazepine, Phenytoin,
   Phenobarbital})` region specifically, so no proof depends on the
   exact shape of this exclusion.
2. **3 survivors** mutate the `(Dabigatran, SSRIOrSNRI,
   !hasOtherBleedingRiskFactors)` ensures clause's `doac == Dabigatran`
   antecedent — `Caution`/`BleedingRisk` is already separately
   guaranteed for `Apixaban`/`Edoxaban`/`Rivaroxaban`+`SSRIOrSNRI` by
   three other, unconditional `ensures` clauses, so the consequent
   holds regardless of what this specific antecedent's mutation
   matches.

Full report: `mutation_report_ddi.json`/`.md`,
`run_manifest_mutation_ddi.json`.

## Amendment 2026-07-10 — Gate C6: genuinely extended the shared NL-summary generator, a different call than `renal_adjustment`'s own equivalent gap

`evidence/dafny_nl_summary.py::summarize_method` refused outright on
first attempt: `CheckInteraction`'s one `requires` clause spans three
physical lines — the first genuinely multi-line clause this repo has
pointed the summary generator at (every clause in
`dosage.dfy`/`renal_adjustment.dfy` happened to be one line).
`renal_adjustment` hit an equivalent gap and that time the fix was to
**reformat** the offending clauses to single-line rather than extend
the tool. This time the call went the other way, for a concrete
reason: this spec already had committed Gate C1/C4/C5 captures bound
to its current formatting, so a cosmetic reformat would have meant
re-running and re-committing all three for a change with zero semantic
content. Fixed instead by making `_extract_annotated_clauses`
accumulate a clause across multiple physical lines, ending accumulation
at a blank line, a standalone `//`-comment line, or the next clause
keyword — so a free-floating block comment between two clauses (this
spec has several) is never misattributed as either one's citation. The
original single-line regex is preserved unchanged, since
`evidence/dafny_mutate.py` imports it for a different, byte-precise
need this extension didn't touch.

Verified end-to-end: all 60 `ensures` clauses and the one multi-line
`requires` clause reconstruct byte-for-byte correctly. **A real,
notable fact this summary surfaces, not a defect:** none of
`CheckInteraction`'s 60 `ensures` clauses carry an inline `//
REQ-DDI-*` citation — unlike `dosage.dfy`/`renal_adjustment.dfy`'s
per-clause style, this spec is validated against
`sources/sps-doac-interactions-2024.md` as a whole lookup table (Gate
1a/1c), not REQ-ID by REQ-ID, so every `*(no requirement cited)*` in
the generated summary is accurate. Presented for sign-off in
`nl_confirmation_drug_interaction_checker_dfy.md`.

## Amendment 2026-07-10 — Gate C6 sign-off confirmed by Steven, and it caught a real doc-accuracy bug in the sign-off document's own text

Not a rubber stamp: Steven checked all four flagged items in
`nl_confirmation_drug_interaction_checker_dfy.md` against
`sources/sps-doac-interactions-2024.md` directly. Item 1 (the
precondition's exact scope) had been mislabeled in an earlier draft as
apixaban's "real source gap" — that phrase belongs specifically to the
apixaban+dronedarone cell, where the source never mentions apixaban at
all (caveat 3, above). The precondition's actual exclusion
(`Apixaban` + `{Rifampicin, Carbamazepine, Phenytoin, Phenobarbital}`)
is indication-dependent, not silence — confirmed verbatim against
source lines 80–84 (rifampicin) and 135–136
(carbamazepine/phenytoin/phenobarbital): "use apixaban with caution"
for two named indications, an explicit branch v1 doesn't model
(`REQ-DDI-5`). Fixed in the sign-off document — the precondition itself
was always correct, only the rationale needed tightening. Every other
flagged item (the flag-conditional SSRI/SNRI pair, the two
`Contraindicated` cells, the citation-free `ensures` clauses)
independently re-verified against the real source, not taken on faith.

A programmatic cross-reference, not just a re-read, confirmed the 60
`ensures` clauses, the NL summary, and the STP suite's 11 lemmas are
mutually consistent — no drift found. **All six Gate C1–C6 pipeline
steps are now built and confirmed for this example.**

## Amendment 2026-07-11 — Phase 3 (evidence packaging) built

`metadata.a.yaml`, `dafny_captures_index.json`, and
`traceability_matrix.a.json`/`.md` committed — 6 requirement rows.
`REQ-DDI-1`/`2`/`3`/`4` all bind to the exact same
`dafny_captures_index.json` entry (`CheckInteraction`) — the first time
this repo's matrix binder has exercised a genuine
many-requirements-to-one-proof shape (every `dosage_calculator`/
`renal_adjustment` requirement is 1:1 with its own function).
`REQ-DDI-5`/`REQ-DDI-6` render as honest GAP rows, `intended_method:
PROVEN` (both are named, staged v2 candidates, not permanent
trust-boundary decisions the way `renal_adjustment`'s `REQ-RENAL-8`
is).

Building this against a Dafny-only metadata file (zero
crosshair/concrete_test evidence anywhere) — built first, ahead of
`renal_adjustment`'s own Phase 3, as the simpler single-capture shape —
found and fixed three real gaps in shared code (`evidence/cli.py`'s
hard-required `--manifest`/`--concrete` flags, the metadata schema's
hard-required `toolchain.crosshair_bounds`, the schema's
lowercase-rejecting `id` pattern), plus one independent latent bug
(`evidence/conflict.py::symbolic_binding_conflicts` missing a `.dfy`
skip its sibling function already had). Full account:
`KNOWN_LIMITATIONS.md`'s "Phase 3 — evidence packaging" section.

## Fixture and capture formats

Mirrors `dosage_calculator/`'s and `renal_adjustment/`'s discipline:
every capture below is the verbatim output of a real, installed Dafny
4.11.0 / Z3 run — none is hand-typed. No crosshair or concrete-test
fixtures exist for this example (Dafny-only, `metadata.a.yaml`'s
`toolchain: {}`).

- **`drug_interaction_checker.dfy`** — the committed spec: one
  function, `CheckInteraction`, 63 match arms across 15 v1-scoped
  agents, 60 pinning `ensures` clauses plus the one `requires` clause
  excluding two agents' still-deferred apixaban cells. Captured by
  `run_verify_ddi.py` → `raw_dafny_output_ddi.txt` /
  `run_manifest_dafny_ddi.json`.
- **`drug_interaction_checker_underconstrained.dfy`** — Gate C4
  honesty exhibit: the pre-fix spec (Gate C1's original 3 `ensures`
  clauses only), preserved verbatim, never updated after the fix.
- **`drug_interaction_checker_stp_suite.dfy`** /
  **`drug_interaction_checker_stp_suite_against_underconstrained.dfy`**
  — Spec-Testing Proofs. The first (11 lemmas: 7 ACCEPT + 4 REJECT)
  passes against the fixed spec; the second (a 3-lemma probe suite,
  same REJECT-style claims, included against the preserved original)
  genuinely fails — both captured for real, not asserted. Runners:
  `run_verify_dafny_stp_suite_ddi.py`,
  `run_verify_dafny_stp_suite_against_underconstrained_ddi.py`.
- **`nl_confirmation_drug_interaction_checker_dfy.md`** — Gate C6:
  plain-English summaries generated by `evidence/dafny_nl_summary.py`,
  presented for and confirmed by Steven's sign-off — see the amendment
  above for the real doc-accuracy bug the review itself caught.
- **`run_mutation_suite_ddi.py`** / **`mutation_report_ddi.json`/`.md`**
  / **`run_manifest_mutation_ddi.json`** — Gate C5: capture runner and
  the real, committed outcome of every one of the 962 mutants above.
- **`GATE_1C_AUDIT.md`** — the internal-consistency audit that found
  the three Gate 1c findings above, including the six worked-example
  hand-traces re-derived against the redesigned spec.
- **`metadata.a.yaml`**, **`dafny_captures_index.json`**,
  **`traceability_matrix.a.json`/`.md`** — Phase 3: the real,
  CLI-generated evidence-packaging output described in the amendment
  above.

## Open questions

Not resolved here — named, not guessed at, per this repo's discipline:

1. **`REQ-DDI-5`** (the indication-dependent third axis for two
   agents' apixaban cells) is a real, sourced, feasible extension, not
   built because it doesn't change whether the core pipeline
   generalizes — genuinely new modeling (a `TreatmentIndication` caller
   input), not a cheap flag addition.
2. **`REQ-DDI-6`** (the specific numeric dose-reduction targets) is
   staged v2, per direct instruction ("both but in order of
   difficulty") — `DoseReductionAdvised` the outcome *kind* is proven;
   the exact mg/frequency target per `(doac, agent)` is v1
   informational text only.
3. **Whether `DoseReductionAdvised` should carry the outcome-kind
   payload differently once `REQ-DDI-6` is built, or whether a
   same-named companion function returning the numeric target is
   cleaner** — a design call better made once v1 is real and verified,
   not guessed at now.
4. **Allergy/cross-sensitivity checking** is an explicit non-goal, not
   a deferred item — a related but clinically distinct concern from
   pharmacokinetic drug-drug interaction, out of scope for this example
   entirely.
