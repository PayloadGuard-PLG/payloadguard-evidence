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
| `REQ-DDI-2` | A total, hardcoded pairwise lookup over all 17 of the source's named sections as of REQ-DDI-5 (2026-07-12) — no precondition at all: the four apixaban+inducer cells that used to be excluded as a provable impossibility are now provable for every constructible `TreatmentIndication` value, so the exclusion was removed rather than kept as dead code. | `CheckInteraction` — proven |
| `REQ-DDI-3` | SSRIs/SNRIs: dabigatran's dose-reduction advice is conditional on a caller-supplied `hasOtherBleedingRiskFactors: bool` — both branches proven, not just the one exercised first. Same trust-boundary shape as `renal_adjustment.dfy`'s `REQ-RENAL-8`. | `CheckInteraction` — proven |
| `REQ-DDI-4` | Fail-safe: any `(doac, agent)` pair outside the source's named set — including within-source gaps like apixaban+dronedarone — returns `NotCovered`, never silently `NoInteractionExpected`. Same "never default to the safe-looking answer on missing data" principle as `renal_adjustment.dfy`'s `REQ-RENAL-4`. | `CheckInteraction` — proven |
| `REQ-DDI-5` | Rifampicin and carbamazepine/phenytoin/phenobarbital make apixaban's outcome depend on a third axis, clinical indication — `TreatmentIndication` (`AFStrokePrevention \| RecurrentVTEPrevention \| OrthopaedicVTEProphylaxis`, the third constructor added 2026-07-13 for `REQ-DDI-6`'s own scoping, not apixaban's). Apixaban's own rows are unaffected and still guard on exactly the first two indications the interaction source names for these rows. Both named indications give apixaban the identical "use with caution" outcome, so once the type is closed to exactly those two values (for apixaban's cells), every constructible input is provable — `CheckInteraction`'s precondition (`REQ-DDI-2`) is removed entirely as a result. | `CheckInteraction` — proven, built 2026-07-12 |
| `REQ-DDI-6` | The `DoseReductionAdvised` outcome *kind* is proven by `CheckInteraction` itself; `DoseReductionTargetMg` proves the specific numeric mg figure for the five real cells the source states one for: Dabigatran+Verapamil (110mg BD, indication-scoped as of 2026-07-13 — see below), Edoxaban+{Dronedarone, ErythromycinSystemic, Ketoconazole, Ciclosporin} (30mg each, deliberately indication-free). Dabigatran+SSRIOrSNRI deliberately excluded, permanently — the source gives no mg figure for that cell. Apixaban never appears in this function's precondition — a direct consequence of `CheckInteraction` never producing `DoseReductionAdvised` for apixaban anywhere in its match arms, not a hand-written exclusion. | `DoseReductionTargetMg` — proven, built 2026-07-12, indication-scoped 2026-07-13 |

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
3. **`CheckInteraction`'s v1 precondition, which used to exclude
   `(Apixaban, {Rifampicin, Carbamazepine, Phenytoin, Phenobarbital})`,
   was an indication-dependent scope exclusion, not a source gap — now
   resolved, not just correctly labeled.** The source *does* address
   apixaban for these four agents ("use apixaban with caution") for two
   named indications; `REQ-DDI-5` (built 2026-07-12) models that axis
   directly via `TreatmentIndication`, so the precondition is gone
   entirely rather than staying a documented exclusion. This remains
   genuinely different from the apixaban+dronedarone cell, where the
   source never mentions apixaban at all (a real, sourced silence,
   correctly labeled `NotCovered`, unaffected by REQ-DDI-5). An earlier
   draft of the Gate C6 sign-off document conflated these two; caught
   and corrected during Steven's own review — see the Gate C6 sign-off
   amendment below.
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

## Amendment 2026-07-12 — REQ-DDI-5 and REQ-DDI-6 built for real; no GAP rows remain

Preceded the same day by full source verification of an externally-
supplied scoping document: `sources/sps-doac-interactions-2024.md`'s
claims checked via `evidence/citation_gate.py` (including a deliberate
false control, correctly `NOT_FOUND`), plus three newly-fetched,
verbatim-verified sources (both eMC apixaban SmPCs, the MHRA DSU renal
table, the US FDA ELIQUIS label as a non-UK contrast) — confirmed both
requirements are buildable from public UK sources before any code
changed. Full account: `KNOWN_LIMITATIONS.md`'s 2026-07-12 entries.

**REQ-DDI-5.** Added `datatype TreatmentIndication = AFStrokePrevention
| RecurrentVTEPrevention` as `CheckInteraction`'s fourth parameter,
deliberately closed to exactly the two indications the interaction
source names for the rifampicin/carbamazepine/phenytoin/phenobarbital
rows — not a third VTE-prophylaxis case that exists only in the
posology sources, with no stated interaction outcome here (a real
scoping decision, confirmed via `AskUserQuestion` before building).
Both named indications give apixaban the identical sourced outcome, so
every constructible `TreatmentIndication` value is now provable —
`CheckInteraction`'s previous `requires` clause (caveat 3, above) is
removed entirely, not narrowed. Four previously-unreachable match arms
become real, reachable arms; `ensures` clause count 60→64.

**REQ-DDI-6.** New companion function `DoseReductionTargetMg(doac,
agent): int`, requires-gated bare-`int` (matching `renal_adjustment.dfy`'s
`SelectFormula`/`AssessRenalFunction` precedent rather than introducing
this repo's first `Option<int>` pattern), pinning the five real sourced
mg figures — see the requirement table above for the exact pairs and
values. Apixaban never appears in this function's precondition — a
direct, confirmed consequence of `CheckInteraction` never producing
`DoseReductionAdvised` for apixaban anywhere in its match arms, not a
hand-written exclusion. Both functions verify together in one
invocation: `2 verified, 0 errors`.

**A real engineering boundary named, not fixed:**
`evidence/dafny_mutate.py`'s body-scanning AOR/LVR generators refuse
outright on a `//` comment inside `DoseReductionTargetMg`'s body (the
wildcard match arm's `// unreachable` comment) — clause-level LVR alone
(omitting `function_name`) already gave equivalent coverage (10 real
mutants across the five pinned figures, all killed), used instead of
new shared-module engineering; named explicitly in
`run_mutation_suite_ddi.py`'s own docstring.

**All six gates re-run for real, for both requirements:** C1
re-verified/re-captured (one invocation now covers both functions); C6
gained two new addenda in `nl_confirmation_drug_interaction_checker_dfy.md`,
each explicitly marked "not yet confirmed — pending review"; C4 added 6
new STP lemmas (`drug_interaction_checker_stp_suite.dfy`, `20 verified,
0 errors`, up from 14); C3 confirmed `TreatmentIndication` gets `EnumSort`
treatment automatically (weak-postcondition count 60→64,
`DoseReductionTargetMg`'s precondition confirmed satisfiable); C5's
mutation suite was restructured to a multi-function loop (mirroring
`run_mutation_suite_renal.py`'s precedent) — first real run: **1178
mutants — 634 killed, 472 filtered_static, 68 survived, 4
unclassifiable.** `CheckInteraction`'s own 31 survivors are byte-for-byte
the same set REQ-DDI-5 alone already established (28 a new "redundant
guard" category on the `treatmentIndication` disjunction, 3 the
pre-existing SSRIOrSNRI category, unchanged). `DoseReductionTargetMg`
contributed 37 new survivors (7 requires-clause + 30 ensures-clause,
the same guard-antecedent-weakening shape `CheckInteraction`'s own
now-removed `requires` clause used to fall into) and all 4
unclassifiable results — a real, expected reappearance of the
datatype-ordering type-error category REQ-DDI-5 had made disappear,
since `DoseReductionTargetMg`'s own new `requires` clause reintroduces a
datatype comparison. All 10 LVR mutants on the five pinned figures
killed, none survived.

**Refined the same day, via a Qodo code-review finding on PR #39:** the
wildcard match arm's bare `0` fallback (a reliability risk if this spec
were ever compiled and called from unverified code with the precondition
violated) was replaced with `case _ => (assert false; 0)`, verified
empirically to still compile and verify cleanly. This had a real,
positive side effect on Gate C5: a mutated requires clause can now admit
a pair that falls into the wildcard arm, defeating the `assert false` —
so the 7 requires-clause ROR survivors from the first run are now ALL
KILLED. **Re-run: 1178 mutants — 641 killed, 472 filtered_static, 61
survived, 4 unclassifiable** (`filtered_static`/`unclassifiable`
unchanged); `DoseReductionTargetMg` now contributes exactly 30 survivors,
ensures-only.

**Phase 3 regenerated, not hand-edited.** `metadata.a.yaml`: REQ-DDI-5
now binds the same `CheckInteraction` capture as REQ-DDI-1–4 (a fifth
requirement sharing one proof); REQ-DDI-6 binds its own
`DoseReductionTargetMg` capture — the first time this repo's matrix
binder has bound two different Dafny methods from the same spec file
across two requirements in one metadata file.
`traceability_matrix.a.json`/`.md` regenerated via the real CLI: **all 6
rows now render real `PROVEN` evidence — no GAP rows remain in this
example.** `assert_no_realized_proven` (R3) independently re-checked.
Full account: `KNOWN_LIMITATIONS.md`'s "Phase E REQ-DDI-5/REQ-DDI-6"
section.

## Amendment 2026-07-13 — Gate C6 review: a real spec-scope gap found and fixed, plus an independent mutation-testing tooling gap

A pre-sign-off review of the REQ-DDI-5/REQ-DDI-6 sign-off document's two
addenda found a real spec-scope gap: `DoseReductionTargetMg(Dabigatran,
Verapamil) == 110` was proven unconditionally, but
`sources/sps-doac-interactions-2024.md` scopes that figure to specific
indications ("AF-stroke-prevention and DVT/PE-prevention-and-treatment
... specifically") the same way `REQ-DDI-5` was built to model for the
apixaban rows — the archived source's own editorial layer dismissed
that scoping rather than a further primary source doing so.
Independently re-verified against the real source text before acting,
not accepted on the review's word alone.

**Primary source fetched and archived** (`sources/emc-smpc-dabigatran-indications-2025.md`,
eMC SmPC for Pradaxa, revision 16 January 2025) confirmed the finding
was real: dabigatran has a genuine, current, UK-licensed third
indication (primary VTE prevention after elective hip/knee replacement,
a once-daily regimen) that `TreatmentIndication` didn't represent, and
that the verapamil interaction row is confirmed silent on. Presented to
Steven via `AskUserQuestion`, not resolved by an assistant: decided to
add the third constructor now.

**Implemented**: `TreatmentIndication` gained `OrthopaedicVTEProphylaxis`
(apixaban's own `REQ-DDI-5` rows unaffected — they still guard on only
the first two constructors). `DoseReductionTargetMg` gained a
`treatmentIndication` parameter and the same indication guard
`CheckInteraction`'s apixaban rows already carry, on its
Dabigatran+Verapamil cell only — the four Edoxaban cells stay
deliberately indication-free, matching the source's own uneven shape. A
new STP lemma, `DoseTargetDomainAgreesWithCheckInteraction`, proves
`DoseReductionTargetMg`'s domain exactly equals "`CheckInteraction` says
`DoseReductionAdvised`" minus the SSRI and orthopaedic-indication
exclusions — apixaban's absence is now a proven theorem, not a
grep-verified observation. **The originally-proposed lemma text
(predating the third constructor) would NOT have verified once it
existed** — `CheckInteraction`'s own Dabigatran+Verapamil clause claims
`DoseReductionAdvised` unconditionally for every indication, since the
outcome *kind* doesn't depend on indication, only the mg figure does —
caught by hand-deriving and independently verifying the corrected claim
in a standalone probe before editing the real suite.

**A second, independent finding, not part of the original review**:
writing the new clauses across multiple physical lines silently
truncated `evidence/dafny_mutate.py`'s clause-site locator at the first
line — a real mutation-testing coverage regression (1178 mutants
dropped to 1171 with entire disjuncts missing), caught before trusting
the result, not by Dafny (still verified clean) or by pytest's
pinned-count-only assertions. Fixed by reformatting both clauses to
single lines, matching `renal_adjustment.dfy`'s own established
precedent for this exact class of gap.

**Final re-run, all six gates**: C1 `2 verified, 0 errors`; C4/STP `23
verified, 0 errors` (up from 20); C3 unchanged; C5 **1250 mutants — 668
killed, 482 filtered_static, 74 survived, 26 unclassifiable** — every
count's jump reflects real, previously-missing coverage of the full
5-disjunct requires clause and the full indication-guarded ensures
clause, not a new class of finding. `CheckInteraction`'s own 31
survivors unchanged throughout; `DoseReductionTargetMg` contributes 43
survivors (6 requires-clause indication-guard + 37 ensures-clause
guard-antecedent, both the same "never load-bearing" category) and all
26 unclassifiable results (24 ROR datatype-ordering type errors + 2 LOR
parser-ambiguity refusals, both already-established categories now
correctly counted at full scale). Phase 3 regenerated: still 6/6
`PROVEN`, no GAP rows. Full account:
`nl_confirmation_drug_interaction_checker_dfy.md`'s "Addendum 3" — the
sign-off document is now ready for Steven's actual review, which still
hasn't happened.

## Fixture and capture formats

Mirrors `dosage_calculator/`'s and `renal_adjustment/`'s discipline:
every capture below is the verbatim output of a real, installed Dafny
4.11.0 / Z3 run — none is hand-typed. No crosshair or concrete-test
fixtures exist for this example (Dafny-only, `metadata.a.yaml`'s
`toolchain: {}`).

- **`drug_interaction_checker.dfy`** — the committed spec: two
  functions as of 2026-07-12, extended 2026-07-13. `CheckInteraction`,
  63 match arms across 15 v1-scoped agents, 64 pinning `ensures`
  clauses, no `requires` clause (REQ-DDI-5 made the four
  apixaban+inducer cells provable for every `TreatmentIndication` value
  the source names for them, so the prior exclusion was removed).
  `DoseReductionTargetMg` (REQ-DDI-6), requires-gated bare-`int`, 5
  pinned mg figures, gained a `treatmentIndication` parameter and an
  indication guard on its Dabigatran+Verapamil cell 2026-07-13.
  `TreatmentIndication` itself has three constructors as of 2026-07-13
  (`AFStrokePrevention | RecurrentVTEPrevention | OrthopaedicVTEProphylaxis`
  — the third added for `DoseReductionTargetMg`'s own scoping, not
  apixaban's). Both functions verify together: `2 verified, 0 errors`.
  Captured by `run_verify_ddi.py` → `raw_dafny_output_ddi.txt` /
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
  the real, committed outcome of every mutant — 962 originally
  (2026-07-10, `CheckInteraction` alone), 1250 as of the current
  committed capture (2026-07-13, both functions — see the 2026-07-13
  amendment above for the full count history).
- **`GATE_1C_AUDIT.md`** — the internal-consistency audit that found
  the three Gate 1c findings above, including the six worked-example
  hand-traces re-derived against the redesigned spec.
- **`metadata.a.yaml`**, **`dafny_captures_index.json`**,
  **`traceability_matrix.a.json`/`.md`** — Phase 3: the real,
  CLI-generated evidence-packaging output described in the amendment
  above.

## Open questions

Not resolved here — named, not guessed at, per this repo's discipline:

1. **Allergy/cross-sensitivity checking** is an explicit non-goal, not
   a deferred item — a related but clinically distinct concern from
   pharmacokinetic drug-drug interaction, out of scope for this example
   entirely.

**Resolved, 2026-07-12** (previously listed here as open):
`REQ-DDI-5` (the `TreatmentIndication` axis) and `REQ-DDI-6` (the
numeric dose-reduction targets, via the `DoseReductionTargetMg`
companion function — the design question of "same function vs.
companion function" resolved in favor of a companion function) are both
built — see the 2026-07-12 amendment above. No requirement in this
example remains unbuilt.
