# Drug-Drug Interaction Checker — Phase 1 (Specification & Foundation)

Status: **Gate 1a done. Gate 1c performed 2026-07-10, all three
findings resolved — see `GATE_1C_AUDIT.md`. Gate C1 (spec + capture)
built 2026-07-10, `drug_interaction_checker.dfy` verifies clean. Gate
C4 (STPs) also built 2026-07-10, and found a real spec gap far larger
than Gate C1's own — see below and `KNOWN_LIMITATIONS.md`'s "Phase E
Gate C4" section for the full account.** Gate C1's three original
`ensures` clauses were only ever a stopgap, not left as the final
state: real IronSpec-style ACCEPT lemmas restating just those three
clauses **failed to prove the correct value for any cell they didn't
directly mention** — confirmed empirically, not assumed
(`drug_interaction_checker_stp_suite_against_underconstrained.dfy`, a
genuinely failing captured run: `0 verified, 3 errors`). Fixed by
restating all 63 match arms as explicit pinning `ensures` clauses
(`drug_interaction_checker.dfy`, re-verified clean), then a real
ACCEPT/REJECT STP suite (`drug_interaction_checker_stp_suite.dfy`, `22
verified, 0 errors`) covering the established worked examples plus
REJECT lemmas for the three `Contraindicated` cells. **Gate C3 (spec
lint) also built 2026-07-10** — and, unlike `renal_adjustment`'s own
Gate C3 (a narrowing fix), required genuinely extending
`evidence/dafny_spec_lint.py`'s Z3 translator: `CheckInteraction`'s
precondition compares `doac`/`agent` directly against datatype
constructors, a case the translator had never needed to model before
(confirmed to refuse first: `unsupported Dafny parameter type 'DOAC'`).
Fixed by representing simple (zero-argument-constructor) Dafny
datatypes as a Z3 `EnumSort`, plus a fix for an independent, real
EnumSort name-collision bug caught while testing it. **Gate C2 (PROVEN
exclusivity) also confirmed 2026-07-10** — the first time since
`dosage_calculator` (2026-07-07) that `evidence/render/matrix_variants.py`'s
`dafny_record()`/`assert_no_realized_proven` (ruling R3) has been
exercised against an independently-authored spec's real capture;
`renal_adjustment` never reached this point (no `metadata.yaml` was
ever built for it). No new gap, no shared-code change — a real,
genuine confirmation the mechanism generalizes, not busywork: run for
real against the actual committed capture, plus two negative-case
checks (wrong method, incomplete verifier status) confirming R3 still
independently refuses tampered records shaped exactly like this
example's real one. **Gate C5 (mutation testing) also built
2026-07-10** — 962 mutants (ROR/LOR/COI; AOR/LVR both confirmed
contributing zero, no arithmetic or numeric literal anywhere in this
spec), found and fixed a real crash bug in Gate C3's own `EnumSort`
extension along the way (a ROR mutant introducing `<=`/`>=` between two
datatype values crashed the Z3 translator with a raw Python `TypeError`
instead of refusing cleanly), then 7 real survivors and 2 unclassifiable
(genuine Dafny type errors, not a parser ambiguity like
`renal_adjustment`'s) — all explained and categorized, none silently
absorbed. **Gate C6 (NL-dialogue confirmation) also built 2026-07-10** —
`evidence/dafny_nl_summary.py` refused outright on first attempt:
`CheckInteraction`'s one `requires` clause is the first genuinely
multi-line clause this repo has pointed the summary generator at (every
clause in `dosage.dfy`/`renal_adjustment.dfy` happened to be one line).
Unlike `renal_adjustment`'s equivalent gap (two multi-line `ensures`
clauses, fixed by reformatting them to single-line, since that spec had
no other gate's captures riding on their exact formatting yet), this
spec already had committed Gate C1/C4/C5 captures bound to its current
formatting — so the tool was extended instead, to genuinely support
multi-line clauses (ending accumulation at a blank line, a standalone
comment line, or the next clause keyword, so a free-floating block
comment between two clauses is never misattributed as either one's
citation). Presented for Steven's sign-off in
`nl_confirmation_drug_interaction_checker_dfy.md` — **pending**, not yet
confirmed, matching this repo's standing discipline of never
rubber-stamping a Gate C6 document in the same pass that generated it.
See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C2"/"Phase E Gate
C3"/"Phase E Gate C5"/"Phase E Gate C6" sections for the full account.
Mirrors `examples/renal_adjustment/PHASE1_PLAN.md`'s structure; read
that file for the general pattern this one follows.

## Objective

Third worked example, PayloadGuard-Evidence's third independent
proof-of-concept: demonstrate the Gate C1–C6 pipeline generalizes to
**set/list-membership logic** — checking whether a specific pairing
belongs to a known, bounded set and, if so, what outcome it maps to —
distinct from `dosage.dfy`'s arithmetic clamping and
`renal_adjustment.dfy`'s lookup-table/conditional-branching shape.
UK-jurisdiction, consistent with `renal_adjustment`'s convention
(MHRA/NICE/KDIGO): sourced from NHS Specialist Pharmacy Service (SPS)
guidance on direct oral anticoagulant (DOAC) interactions.

## Gate 1a — Clinical source audit & requirements extraction

Single primary source for v1, chosen over BNF Appendix 1 / MHRA Drug
Safety Update after a direct comparison: publicly fetchable with no
login wall (confirmed — fetched twice, once via WebFetch, once via raw
`curl`, see `sources/sps-doac-interactions-2024.md`), genuinely bounded
(4 DOACs × ~17 named agents, not an open-ended database), versioned in
this repo's own style (published/last-updated dates, per-section update
history), and the source states its own scope boundary explicitly
("not comprehensive for all potential interactions with DOACs") —
giving a citable basis for a `NotCovered` outcome rather than having to
assert one.

**Full extraction, with verbatim quotes and per-row detail:**
`sources/sps-doac-interactions-2024.md`. That document also records
what a first-pass AI-summarized fetch got directionally right but
missed in precision (per-DOAC downgrades, indication-dependent branches,
a real source gap on apixaban+dronedarone) — the requirements below are
built from the raw re-fetch, not the summary.

| ID | Requirement | Source |
|---|---|---|
| REQ-DDI-1 | The checker returns an `InteractionResult(outcome, direction)` pair, never a bare boolean. `outcome` is one of `NoInteractionExpected`, `Caution`, `CautionLowRelevance`, `Avoid`, `Contraindicated`, `DoseReductionAdvised`, `NotCovered`. `CautionLowRelevance` added 2026-07-10 (Gate 1c Finding 3, resolved by explicit decision) — distinct from plain `Caution`, for the two cells where the source hedges ("unlikely to be clinically relevant") without ever giving digoxin's clean, unqualified negative; distinct from `NoInteractionExpected` too, since the source never actually states a negative for those two cells the way it does for digoxin. `direction` is `BleedingRisk \| ThrombosisRisk \| NoRisk \| UnknownRisk`, added 2026-07-10 (Gate 1c Finding 1, resolved by explicit decision) — every one of the source's 17 sections is headed by exactly this distinction, and it's clinically load-bearing (the correct thing to monitor for differs). `NotCovered` is distinct from `NoInteractionExpected`: digoxin gets an explicit stated negative; an agent never mentioned on the source page (e.g. apixaban+dronedarone, see REQ-DDI-2) gets `NotCovered`, not an assumed negative. | `sources/sps-doac-interactions-2024.md`, digoxin entry + scope statement; `GATE_1C_AUDIT.md`'s Findings 1 and 3. |
| REQ-DDI-2 | `CheckInteraction(doac: DOAC, agent: Agent, hasOtherBleedingRiskFactors: bool): InteractionResult` — a total, hardcoded pairwise lookup (mirrors `GStage`'s hardcoded boundary table in `renal_adjustment.dfy`) covering 14 of the source's 17 named sections with no extra caller input needed, plus SSRIs/SNRIs (REQ-DDI-3, its own row) = 15 of 17 in v1. **As of 2026-07-10 (Gate 1c Finding 2, resolved by explicit decision), the function also carries `requires !(doac == Apixaban && agent in {Rifampicin, Carbamazepine, Phenytoin, Phenobarbital})`** — recovering 6 of those two agents' 8 total DOAC cells as real, provable v1 cells (dabigatran/edoxaban/rivaroxaban for both), while making their still-blocked apixaban cells (REQ-DDI-5, the indication axis) a provable precondition violation rather than a silently undefined match arm. 17 of 17 named sections now have *something* defined for every cell they can have defined without REQ-DDI-5 — the only true gaps left are the 2 apixaban cells the precondition explicitly excludes, and the 1 real source gap (apixaban+dronedarone, `NotCovered`). Each cell's outcome is per-DOAC where the source differentiates — **not** a single outcome per agent regardless of DOAC. | `sources/sps-doac-interactions-2024.md`, per-drug sections; `GATE_1C_AUDIT.md`'s Finding 2. |
| REQ-DDI-3 | SSRIs/SNRIs are in v1 scope despite carrying an extra factor: dabigatran's dose-reduction advice is conditional on a **caller-supplied** `hasOtherBleedingRiskFactors: bool` — "consider a dose reduction... if the individual also has other risk factors for bleeding." Same trust-boundary shape as `renal_adjustment.dfy`'s `REQ-RENAL-8` (caller-supplied classification flags): the proof establishes correct branching given the flag, not the correctness of the flag's clinical determination. Cheap enough to include in v1 rather than deferred, unlike REQ-DDI-5 below. | `sources/sps-doac-interactions-2024.md`, SSRIs/SNRIs entry. |
| REQ-DDI-4 | Fail-safe: any `(doac, agent)` pair not present in the source's named set — including within-source gaps like apixaban+dronedarone — returns `NotCovered`, never silently `NoInteractionExpected`. Same "never default to the safe-looking answer on missing data" principle as `renal_adjustment.dfy`'s `REQ-RENAL-4`. | Design invariant, same category as `REQ-RENAL-4`; grounded in REQ-DDI-1's `NotCovered`/`NoInteractionExpected` distinction. |
| REQ-DDI-5 (**named, deferred — not built in v1**) | Rifampicin and Carbamazepine/phenytoin/phenobarbital both make apixaban's outcome depend on a third axis, clinical indication (AF-stroke-prevention/DVT-PE-recurrence-prevention vs. other indications) — genuinely new modeling (a `TreatmentIndication` caller input), not a cheap flag addition like REQ-DDI-3. Same pattern as `renal_adjustment`'s combined creatinine-cystatin-C eGFR: named as a real, sourced, feasible extension, not built because it doesn't change whether the core pipeline generalizes. | `sources/sps-doac-interactions-2024.md`, rifampicin + carbamazepine/phenytoin/phenobarbital entries. |
| REQ-DDI-6 (**staged v2, per direct instruction — "both but in order of difficulty"**) | The `DoseReductionAdvised` outcome kind is proven in v1; the *specific numeric target* (e.g. dabigatran→110mg BD with verapamil, edoxaban→30mg OD/daily with dronedarone/erythromycin/ketoconazole/ciclosporin) is v1 informational text only, not a proven output. v2 extends the same lookup to prove the correct numeric target per `(doac, agent)` where the source states one. Explicitly staged, not dropped — the harder half comes after the classify-only core is real. | `sources/sps-doac-interactions-2024.md`, per-drug dose-reduction cells. |

**Explicit non-goal.** Allergy/cross-sensitivity checking (e.g.
penicillin-class cross-reactivity) is a related but distinct clinical
concern from pharmacokinetic drug-drug interaction and is out of scope
for this example entirely, not deferred — same pattern as
`renal_adjustment`'s per-drug numeric dose-reduction-factor exclusion.

**Trust boundary, stated once rather than per-row (applies to every
`Agent` case in REQ-DDI-2/3, not just the class-labeled ones):** this
proof establishes correct outcome lookup *given* a correctly-classified
`Agent` value — it does not establish that a specific real-world drug
name actually belongs to the class/agent category the caller supplies
(e.g. "is drug X actually an SSRI"). Same trust boundary `REQ-RENAL-8`
drew for `SelectFormula`'s classification flags, applied here to the
`Agent` datatype's construction rather than to boolean flags.

## Gate 1b — Formal specification skeleton (structure, not code)

**A real, useful finding: v1's design needs no `set`/`seq` Dafny types at
all, and therefore no new Z3-translator engineering in Gate C3.** The
original scoping session flagged Gate C3's Z3 translator as refusing
non-`real`/`int`/`nat`/`bool`/`datatype` parameter types, and named
set/seq support as a real, moderate engineering gap. That gap is real
**if** the design were "a `set<string>` of drug names checked for
membership." It is not needed here: `DOAC` and `Agent` are enumerated
`datatype`s (finite, closed, known at spec-authoring time — mirroring
`renal_adjustment.dfy`'s own `Formula`/`RenalAssessment` datatypes,
already proven to work through Gate C1/C3/C6 unmodified), and
`CheckInteraction` is a total pattern-match function over them, exactly
like `GStage`'s hardcoded boundary lookup. **Where `set`/`seq` and
quantifier support would genuinely become necessary: checking a new
drug against an entire, open, caller-supplied medication list** ("does
this interact with *anything* the patient is already on") rather than a
single hardcoded pairwise lookup — that's a real v3-or-later candidate,
distinct from both REQ-DDI-5 and REQ-DDI-6, and is exactly the
quantifier-refusal boundary `dafny_spec_lint.py`'s vector 1 currently
draws on purpose. Staying pairwise-only for v1/v2 avoids that engineering
entirely; it isn't required to demonstrate set-membership logic
generalizes, since "does this specific pair belong to the known set" is
itself the set-membership question, whether checked via `set<T>.Contains`
or a total pattern match over a closed enumeration is an implementation
choice, not a difference in what's being proven.

**Sketch, redesigned 2026-07-10 to resolve all three Gate 1c findings:**

```dafny
datatype DOAC = Apixaban | Dabigatran | Edoxaban | Rivaroxaban

datatype Agent =
    Amiodarone | Digoxin | Diltiazem | Dronedarone | Verapamil
  | Clarithromycin | ErythromycinSystemic
  | Rifampicin
  | OtherDOACOrHeparinOrWarfarin
  | SSRIOrSNRI
  | Fluconazole
  | Itraconazole | Ketoconazole
  | Aspirin | Clopidogrel | Ticagrelor
  | Carbamazepine | Phenytoin | Phenobarbital
  | LevetiracetamOrValproateContaining
  | Ciclosporin
  | Tacrolimus
  | Ibuprofen | Naproxen

// Finding 1 (resolved): every source section is headed by exactly this
// distinction -- Outcome alone can't tell a reader which way to monitor.
datatype RiskDirection = BleedingRisk | ThrombosisRisk | NoRisk | UnknownRisk

// Finding 3 (resolved): CautionLowRelevance is distinct from both Caution
// and NoInteractionExpected -- honest about the source's own hedge
// ("unlikely to be clinically relevant") rather than forcing a choice
// between two options that both misrepresent it.
datatype Outcome =
    NoInteractionExpected | Caution | CautionLowRelevance | Avoid
  | Contraindicated | DoseReductionAdvised | NotCovered

datatype InteractionResult = InteractionResult(outcome: Outcome, direction: RiskDirection)

// Finding 2 (resolved): the precondition makes Rifampicin/Carbamazepine/
// Phenytoin/Phenobarbital's still-blocked apixaban cell a provable
// exclusion, not a silently undefined match arm -- while their other
// 3 DOAC cells each (6 cells total) are now real, defined, v1 cells.
function CheckInteraction(doac: DOAC, agent: Agent,
                           hasOtherBleedingRiskFactors: bool): InteractionResult
  requires !(doac == Apixaban && agent in
             {Rifampicin, Carbamazepine, Phenytoin, Phenobarbital})
{
  match (doac, agent)
  case (_, Amiodarone) => InteractionResult(Caution, BleedingRisk)
  case (_, Digoxin) => InteractionResult(NoInteractionExpected, NoRisk)
  case (_, Diltiazem) => InteractionResult(Caution, BleedingRisk)
  case (Dabigatran, Dronedarone) => InteractionResult(Avoid, BleedingRisk)
  case (Rivaroxaban, Dronedarone) => InteractionResult(Avoid, BleedingRisk)
  case (Edoxaban, Dronedarone) => InteractionResult(DoseReductionAdvised, BleedingRisk)
  case (Apixaban, Dronedarone) => InteractionResult(NotCovered, UnknownRisk)   // real source gap, not assumed
  case (Dabigatran, Verapamil) => InteractionResult(DoseReductionAdvised, BleedingRisk)
  case (Rivaroxaban, Verapamil) => InteractionResult(CautionLowRelevance, BleedingRisk)   // Finding 3, was the unresolved hand-trace example
  case (Apixaban, Verapamil) => InteractionResult(CautionLowRelevance, BleedingRisk)      // Finding 3
  case (Edoxaban, Verapamil) => InteractionResult(Caution, BleedingRisk)
  case (Dabigatran, Rifampicin) => InteractionResult(Avoid, ThrombosisRisk)               // now defined -- Finding 2's recovered cell
  case (Edoxaban, Rifampicin) => InteractionResult(Caution, ThrombosisRisk)               // Finding 2's recovered cell
  case (Rivaroxaban, Rifampicin) => InteractionResult(Caution, ThrombosisRisk)            // Finding 2's recovered cell
  // (Apixaban, Rifampicin) excluded by the precondition above -- REQ-DDI-5, not yet built
  // ... remaining cells per sources/sps-doac-interactions-2024.md
  case (Dabigatran, SSRIOrSNRI) =>
    if hasOtherBleedingRiskFactors
    then InteractionResult(DoseReductionAdvised, BleedingRisk)
    else InteractionResult(Caution, BleedingRisk)
  case (_, SSRIOrSNRI) => InteractionResult(Caution, BleedingRisk)
}
```

This is a sketch, not the committed spec — full case coverage (all 15
v1 agents × the DOACs each one differentiates on, plus the 6 recovered
Rifampicin/Carbamazepine/Phenytoin/Phenobarbital cells) still needs
writing out completely and verifying against Dafny 4.11.0, matching
`renal_adjustment`'s Gate 1b→C1 discipline (skeleton first, real capture
before treating any of it as evidence).

## Still open — performed in Gate 1c, not resolved there

Superseded by `GATE_1C_AUDIT.md`'s three named findings (risk-direction
axis, `CheckInteraction` non-totality over the two deferred agents, the
two ambiguous "clinically-not-relevant" cells) and its own "Open
judgment calls" section — see that file for the current, complete list
rather than this one, which predates the audit. Retained below only for
the one item the audit didn't independently re-raise:

1. Whether `DoseReductionAdvised` should carry the outcome-kind payload
   differently once REQ-DDI-6 (v2) is built, or whether a same-named
   companion function returning the numeric target is cleaner — a Gate
   1b-level design call better made once v1 is real and verified, not
   guessed at now.

## Documentation set updated so far

- `sources/sps-doac-interactions-2024.md` (this Phase 1's primary
  citation extract).
- This file.
- `GATE_1C_AUDIT.md` (Gate 1c, performed 2026-07-10).
- `SYSTEM_BLUEPRINT.md`, `KNOWN_LIMITATIONS.md`, `HANDOFF.md`, `DEVLOG.md`
  (Gates C1, C4, C3, C2, C5, then C6, all 2026-07-10 —
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C1"/"Phase E Gate C4"/"Phase E
  Gate C3"/"Phase E Gate C2"/"Phase E Gate C5"/"Phase E Gate C6" sections
  have the full account of each).
- `evidence/dafny_spec_lint.py` (Gate C3's real extension, then a real
  crash fix found by Gate C5's mutation testing — see its updated
  module docstring) and its test files, `tests/test_dafny_spec_lint.py`
  (extended twice) and `tests/test_drug_interaction_checker_spec_lint.py`
  (new).
- `tests/test_drug_interaction_checker_dafny_wiring.py` (new, Gate C2).
- `run_mutation_suite_ddi.py`, `mutation_report_ddi.json`/`.md`,
  `run_manifest_mutation_ddi.json` (new, Gate C5) and
  `tests/test_drug_interaction_checker_mutation_report.py` (new).
- `evidence/dafny_nl_summary.py` (Gate C6's real multi-line-clause
  extension — see its updated module docstring) and its test file,
  `tests/test_dafny_nl_summary.py` (extended: one obsolete refusal test
  rewritten to reflect the new correct behavior, two new tests added).
  `nl_confirmation_drug_interaction_checker_dfy.md` (new, Gate C6 — the
  actual sign-off deliverable, currently **pending** Steven's review).

Not yet updated: nothing — all six Gate C1–C6 pipeline steps have now
been built or confirmed for this example. Remaining, explicitly named,
not built: `REQ-DDI-5`/`REQ-DDI-6` (v2, staged), and Gate C6's own
Decision section (pending Steven's actual sign-off, not yet closed).
