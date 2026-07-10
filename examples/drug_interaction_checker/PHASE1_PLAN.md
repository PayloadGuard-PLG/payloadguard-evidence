# Drug-Drug Interaction Checker — Phase 1 (Specification & Foundation)

Status: **Gate 1a (clinical source audit) done. Gate 1b (spec-skeleton
design decisions) recorded below. Gate 1c (internal consistency and
completeness audit) not yet performed — that's the next step, not
skipped.** Mirrors `examples/renal_adjustment/PHASE1_PLAN.md`'s
structure; read that file for the general pattern this one follows.

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
| REQ-DDI-1 | The checker returns one of a fixed set of outcome kinds — `NoInteractionExpected`, `Caution`, `Avoid`, `Contraindicated`, `DoseReductionAdvised`, `NotCovered` — never a bare boolean. `NotCovered` is distinct from `NoInteractionExpected`: digoxin gets an explicit stated negative ("No interactions are expected between digoxin and DOACs"); an agent never mentioned on the source page (e.g. apixaban+dronedarone, see REQ-DDI-2) gets `NotCovered`, not an assumed negative. | `sources/sps-doac-interactions-2024.md`, digoxin entry + scope statement. |
| REQ-DDI-2 | `CheckInteraction(doac: DOAC, agent: Agent): Outcome` — a total, hardcoded pairwise lookup (mirrors `GStage`'s hardcoded boundary table in `renal_adjustment.dfy`) covering 14 of the source's 17 named entries: Amiodarone, Digoxin, Diltiazem, Dronedarone (incl. the apixaban `NotCovered` gap), Verapamil, Clarithromycin, Erythromycin(systemic), Other-DOAC/heparin/warfarin, Fluconazole, Itraconazole, Ketoconazole, Aspirin/Clopidogrel/Ticagrelor (antiplatelets), Ciclosporin, Tacrolimus, Ibuprofen/Naproxen (NSAIDs), Levetiracetam/valproate. Each cell's outcome kind is per-DOAC where the source differentiates (e.g. dabigatran=`Contraindicated` with itraconazole/ketoconazole, apixaban/rivaroxaban=`Avoid`... — see the source doc for every cell) — **not** a single outcome per agent regardless of DOAC. | `sources/sps-doac-interactions-2024.md`, per-drug sections. |
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

**Sketch:**

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

datatype Outcome =
    NoInteractionExpected | Caution | Avoid | Contraindicated
  | DoseReductionAdvised | NotCovered

function CheckInteraction(doac: DOAC, agent: Agent,
                           hasOtherBleedingRiskFactors: bool): Outcome
{
  match (doac, agent)
  case (_, Amiodarone) => Caution
  case (_, Digoxin) => NoInteractionExpected
  case (_, Diltiazem) => Caution
  case (Dabigatran, Dronedarone) => Avoid
  case (Rivaroxaban, Dronedarone) => Avoid
  case (Edoxaban, Dronedarone) => DoseReductionAdvised
  case (Apixaban, Dronedarone) => NotCovered   // real source gap, not assumed
  // ... remaining cells per sources/sps-doac-interactions-2024.md
  case (Dabigatran, SSRIOrSNRI) =>
    if hasOtherBleedingRiskFactors then DoseReductionAdvised else Caution
  case (_, SSRIOrSNRI) => Caution
}
```

This is a sketch, not the committed spec — full case coverage (all 14
v1 agents × the DOACs each one differentiates on) still needs writing
out completely and verifying against Dafny 4.11.0, matching
`renal_adjustment`'s Gate 1b→C1 discipline (skeleton first, real capture
before treating any of it as evidence).

## Still open — for Gate 1c to check, not resolved here

1. Whether every one of REQ-DDI-2's ~14×(1-4 DOACs each) cells has been
   transcribed correctly from `sources/sps-doac-interactions-2024.md`
   into the eventual `.dfy` file — Gate 1c's actual job, same as it was
   for `renal_adjustment`'s `GStage`-misapplication finding.
2. Whether `DoseReductionAdvised` should carry the outcome-kind payload
   differently once REQ-DDI-6 (v2) is built, or whether a same-named
   companion function returning the numeric target is cleaner — a Gate
   1b-level design call better made once v1 is real and verified, not
   guessed at now.
3. REQ-DDI-5's indication axis: if it's ever built, does it become a
   third parameter on `CheckInteraction` or a separate function layered
   on top? Not needed to decide before v1.

## Documentation set updated so far

- `sources/sps-doac-interactions-2024.md` (this Phase 1's primary
  citation extract).
- This file.

Not yet updated (deliberately — nothing built yet to describe):
`SYSTEM_BLUEPRINT.md`, `KNOWN_LIMITATIONS.md`, `HANDOFF.md`, `DEVLOG.md`.
Those get real entries once Gate 1c closes and Gate C1 (spec + capture)
actually exists, same discipline `renal_adjustment` followed — no
provisional entries for work that doesn't exist yet.
