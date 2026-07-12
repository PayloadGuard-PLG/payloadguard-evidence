# Gate 1c — Internal consistency and completeness audit

Status: **performed 2026-07-10.** Hand-traces every `REQ-DDI-*` and the
Gate 1b sketch in `PHASE1_PLAN.md` against
`sources/sps-doac-interactions-2024.md`. Per Gate 1c's own stated
purpose (`renal_adjustment/GATE_1C_AUDIT.md`) — catch conceptual gaps at
the cheapest possible point, before any Dafny code exists — **this
audit found three real findings, not zero.** Named here rather than
smoothed over so Gate 1 can be marked closed. **All three now resolved
by explicit decision — see the 2026-07-10 addendum below. Gate 1 is
closeable.** See "Exit criteria assessment" at the end for the original
(now superseded) assessment.

## Total coverage check

Every one of the source's 17 named sections carries an explicit
**risk-direction subheading** — confirmed by grepping the raw extracted
text, not assumed: `Increased risk of bleeding` / `Theoretical increased
risk of bleeding` / `No interaction` / `Risk of thrombosis` / `Theoretical
risk of thrombosis`, one per section, no exceptions. `PHASE1_PLAN.md`'s
Gate 1b `Outcome` datatype (`NoInteractionExpected | Caution | Avoid |
Contraindicated | DoseReductionAdvised | NotCovered`) has no field for
this at all — see Finding 1.

Cross-checking `PHASE1_PLAN.md`'s REQ-DDI-2 row against the Gate 1b
`Agent` datatype it's supposed to describe: the row's prose says "14 of
the source's 17 named entries" and lists 14 — but the `Agent` datatype
two paragraphs later includes `SSRIOrSNRI` as a constructor, and the
`CheckInteraction` sketch has explicit match arms for
`(Dabigatran, SSRIOrSNRI)` and `(_, SSRIOrSNRI)`. REQ-DDI-3 separately
and correctly says SSRIs/SNRIs **are** in v1 scope. The "14" in REQ-DDI-2
is simply wrong arithmetic in the document itself (14 "plain" sections +
SSRI/SNRI = 15 in v1; + Rifampicin + Carbamazepine/phenytoin/
phenobarbital deferred = 17 total, which does add up) — a plain
documentation bug, not a design question, **fixed directly in this
commit** (see the diff to `PHASE1_PLAN.md`). Flagged here rather than
silently corrected with no record, since Gate 1c's job is exactly to
surface this kind of thing, not just design gaps.

## Finding 1: the `Outcome` taxonomy drops the source's own risk-direction axis

`Caution`/`Avoid`/`Contraindicated` describe *how strongly* to act; they
say nothing about *which direction* the risk runs. The source treats
this as load-bearing information, not a footnote — it's the first thing
stated in every section, before the management advice. Concretely,
**Rifampicin** and **Carbamazepine/phenytoin/phenobarbital** are both
labeled `Risk of thrombosis` (these agents *decrease* DOAC blood levels,
under-anticoagulating the patient), while almost everything else
(`Amiodarone`, `Dronedarone`, `Verapamil`, `Macrolides`, `Ciclosporin`,
etc.) is `Increased risk of bleeding` (over-anticoagulating). A
downstream consumer of `CheckInteraction`'s `Caution` result cannot tell
these apart from the outcome alone, even though the correct monitoring
action is different in each direction (watch for bleeding signs vs.
watch for clot/thrombosis signs) — the source's own management text
says exactly this ("Monitor for anaemia and signs of bleeding" vs.
"monitor for signs of thrombosis").

A secondary, smaller version of the same drop: three sections (Diltiazem,
part of Fluconazole, Levetiracetam/valproate) qualify their risk as
**theoretical** rather than confirmed — evidence-quality information the
current taxonomy also discards.

**Not resolved here — two ways to fix it, real tradeoff, Steven's call:**

- **(a) Add a `RiskDirection` field to `Outcome`** (or a parallel
  `direction: BleedingRisk | ThrombosisRisk | NoRisk` return alongside
  the outcome kind) — captures what the source actually structures every
  row around, at the cost of touching every match arm in `CheckInteraction`
  a second time.
- **(b) Leave it out of the proof, document it only in the informational
  report text** — same trust-boundary move as REQ-DDI-6 deferring the
  numeric dose target: the *lookup* is proven, the *narrative detail*
  isn't. Lower engineering cost, but means the proof is silent on
  something the source treats as primary, not incidental.

**Recommendation, not a decision:** (a) — unlike REQ-DDI-6's numeric
dose figures (genuinely a harder, separate proof obligation) or
REQ-DDI-5's indication axis (needs a whole new caller-supplied
parameter), this is "one more enum field, populated directly from
information already being transcribed row by row" — closer in cost to
adding a column to a table already being built than to a new proof
target.

## Finding 2: `CheckInteraction` is not actually total over its own declared `Agent` type

The Gate 1b `Agent` datatype includes `Rifampicin`, `Carbamazepine`,
`Phenytoin`, and `Phenobarbital` as constructors. REQ-DDI-5 defers
**only** the apixaban cell for each of these (the indication-dependent
branch) — but a Dafny `datatype` constructor, once declared, is
constructible for *every* DOAC, not just the three well-defined ones.
As written, nothing stops a future caller writing
`CheckInteraction(Apixaban, Rifampicin, false)`, and the skeleton's own
`// ... remaining cells` ellipsis never says what that call should
return. This is the same shape as `renal_adjustment`'s Finding 1 (a gap
that "fell out silently from decomposing the skeleton") — the
difference is 3 of each deferred agent's 4 DOAC cells are actually
well-defined and citable right now:

- Rifampicin: dabigatran = `Avoid` (unconditional), edoxaban/rivaroxaban
  = monitor-for-thrombosis-if-unavoidable (unconditional). Only apixaban
  needs the indication.
- Carbamazepine/phenytoin/phenobarbital: same shape — dabigatran =
  `Avoid` (with an evidence-quality caveat for phenobarbital
  specifically, itself an instance of Finding 1's theoretical-qualifier
  point), edoxaban/rivaroxaban = monitor-for-thrombosis-if-unavoidable.
  Only apixaban needs the indication.

**Not resolved here — two options:**

- **(a) Type-level exclusion, mirroring `renal_adjustment`'s Finding 2
  fix:** add `requires !(doac == Apixaban && agent in {Rifampicin,
  Carbamazepine, Phenytoin, Phenobarbital})` to `CheckInteraction`,
  making the exact gap a provable precondition violation rather than a
  silently-wrong return value, while still proving the other 3×2 = 6
  well-defined cells now rather than deferring all 8 cells across both
  agents.
- **(b) Simpler, more conservative: remove all four agents from `Agent`
  entirely until REQ-DDI-5 is built**, same as this plan's current
  framing implicitly assumed but didn't actually implement. Loses the 6
  well-defined cells for now; regains them when REQ-DDI-5 is built,
  same moment the apixaban cells become answerable.

**Recommendation, not a decision:** (a) — the six well-defined cells are
real, sourced, and provable today; deferring them along with the two
genuinely-blocked ones understates what Gate 1a's research actually
found.

## Finding 3: two cells have no committed `Outcome`-kind mapping — the source itself is ambiguous, not just unmodeled

Verapamil's rivaroxaban/apixaban cells: "This is unlikely to be
clinically relevant interaction for rivaroxaban and apixaban" — but the
same section's management text ("Monitor for anaemia and signs of
bleeding") is never explicitly narrowed to exclude them. Fluconazole's
rivaroxaban cell: "This is not considered to be clinically relevant for
rivaroxaban" — same shape. Both read as weaker than the base `Caution`
level for that section, but the source never states an unqualified
negative for them the way it does for **digoxin** ("No interactions are
expected between digoxin and DOACs" — no hedge, no clinical-relevance
caveat). Collapsing these two cells to `NoInteractionExpected` would
overstate the source; leaving them at plain `Caution` (identical to
every other DOAC on the same row) understates the source's own explicit
downgrade. **A genuine three-way ambiguity in the primary source, not a
gap in this document's reading of it** — worth a fourth `Outcome` case
(e.g. `CautionLowRelevance`) rather than forcing a choice between two
options that both misrepresent the source, but that's itself a call
worth naming rather than making silently.

## REQ-by-REQ trace

| ID | Enforced by | Status |
|---|---|---|
| REQ-DDI-1 (outcome taxonomy) | `Outcome` datatype | Six cases sketched; **incomplete per Finding 1** (no risk-direction field) and **Finding 3** (no case for the two "clinically-not-relevant" cells) |
| REQ-DDI-2 (v1 pairwise lookup) | `CheckInteraction` | Sketch only, not yet written out to full case coverage or verified against real Dafny; **REQ-DDI-2's own entry count was wrong — fixed this commit (Total coverage check, above)** |
| REQ-DDI-3 (SSRI/SNRI conditional flag) | `CheckInteraction`'s `hasOtherBleedingRiskFactors` parameter | Sketched and present in the match arms shown; not yet verified |
| REQ-DDI-4 (`NotCovered` fail-safe) | `CheckInteraction`'s total-match requirement + the apixaban+dronedarone example cell | Sketched, one real example present; not yet verified as actually total (Dafny would refuse to compile a non-exhaustive `match` — this is the one piece of REQ-DDI-4 that's structurally self-checking once real code exists, not just a convention) |
| REQ-DDI-5 (indication axis) | Not built — explicitly deferred | **Finding 2 sharpens this**: 6 of the 8 cells nominally "blocked" by this deferral are actually answerable now; only the 2 apixaban cells are genuinely blocked |
| REQ-DDI-6 (numeric dose targets, v2) | Not built — explicitly staged | Unchanged from `PHASE1_PLAN.md`; no new finding here |
| *(unnumbered)* | Risk-direction axis | **New gap, Finding 1 — not covered by the current `Outcome` datatype at all** |

> **Update 2026-07-12**: REQ-DDI-5 and REQ-DDI-6 are now both built —
> see `PHASE1_PLAN.md`'s current REQ-DDI-5/REQ-DDI-6 rows and
> `KNOWN_LIMITATIONS.md`'s "Phase E REQ-DDI-5/6" section for the full
> account. The two rows above are left as-is, a frozen record of this
> audit's state on 2026-07-10; they are no longer the current status.

## Worked-example hand-traces

1. **`(Dabigatran, Ketoconazole)`** → per source: "contraindicated with
   dabigatran." Sketch/table agree: `Contraindicated`. No dose figure (v1
   scope, correctly — the 30mg edoxaban figure is a different DOAC).
2. **`(Edoxaban, Ciclosporin)`** → per source: "use... cautiously...
   Reduce the edoxaban dose to 30mg daily with ciclosporin." v1 correctly
   returns `DoseReductionAdvised` as the outcome *kind*; the "30mg daily"
   figure itself is v2 territory (REQ-DDI-6), consistent with the plan.
3. **`(Apixaban, Dronedarone)`** → per source: apixaban is never
   mentioned in the dronedarone section at all. `NotCovered` is correct
   per REQ-DDI-4 — and this is a real, sourced example of the fail-safe
   actually firing, not a hypothetical one.
4. **`(Dabigatran, SSRIOrSNRI, hasOtherBleedingRiskFactors=true)`** →
   `DoseReductionAdvised`; **`(..., false)`** → `Caution`. Matches the
   sketch's own match arms and REQ-DDI-3's stated conditional. No dose
   figure in the source for this row at all (it defers to the SmPC), so
   even REQ-DDI-6's v2 extension won't have a citable number to add here
   without a further source.
5. **`(Rivaroxaban, Verapamil)`** → **this is exactly Finding 3's
   ambiguity, hand-traced for real**: the sketch's ellipsis never
   committed to an answer, and per the source text alone there isn't a
   clean one — `Caution` (matching the section's general management
   advice) or something weaker (matching the "unlikely to be clinically
   relevant" qualifier) are both defensible, and picking one silently
   would be exactly the kind of undocumented judgment call Gate 1c exists
   to surface instead of hide.

## Open judgment calls (named, not guessed) — resolved, see 2026-07-10 addendum below

1. **Risk-direction axis (Finding 1)** — add a field to `Outcome`, or
   leave it as informational-only text outside the proof. Recommendation
   offered, not decided.
2. **`Agent` totality for the two deferred agents (Finding 2)** — a
   type-level precondition excluding just the two blocked apixaban cells
   (recovering 6 real, sourced, provable cells now), or removing all four
   agents from `Agent` until REQ-DDI-5 lands. Recommendation offered, not
   decided.
3. **The two "clinically-not-relevant" cells (Finding 3)** — a fourth
   `Outcome` case, or a forced choice between the two existing
   over/understating options. Not decided; genuinely ambiguous in the
   primary source itself, not just in this document's reading of it.

## Exit criteria assessment (original, superseded — see addendum below)

Per `renal_adjustment`'s own precedent for what Gate 1 exit requires
("specification skeleton has no undefined input regions... audit
document names every open judgment call rather than resolving them
implicitly"): **Gate 1c is now performed, but Gate 1 is not yet fully
closeable** — this audit found the skeleton has an incomplete output
type (Finding 1), a non-total function over its own declared input type
(Finding 2), and a real, sourced ambiguity with no committed resolution
(Finding 3). All three are named, not resolved, per this repo's
discipline. Phase 2 remains blocked until Steven decides all three.

## Addendum 2026-07-10 — all three findings resolved by explicit decision

Steven's direction on all three, asked directly rather than assumed:
Finding 1 → add the `RiskDirection` field (option (a)). Finding 2 →
type-level exclusion (option (a)). Finding 3 → add a fourth `Outcome`
case, `CautionLowRelevance`. `PHASE1_PLAN.md`'s Gate 1b sketch has been
redesigned to match — `RiskDirection`, `Outcome` (now including
`CautionLowRelevance`), and `InteractionResult(outcome, direction)` as
`CheckInteraction`'s return type; the function gained
`requires !(doac == Apixaban && agent in {Rifampicin, Carbamazepine,
Phenytoin, Phenobarbital})`.

**Every worked-example hand-trace above re-derived against the new
design, to confirm the redesign is actually consistent with this
audit's own earlier findings, not just declared fixed:**

1. `(Dabigatran, Ketoconazole)` → `InteractionResult(Contraindicated,
   BleedingRisk)`. Direction correct: the itraconazole/ketoconazole
   section is headed "Increased risk of bleeding." Matches the original
   trace's outcome exactly, now with a direction attached.
2. `(Edoxaban, Ciclosporin)` → `InteractionResult(DoseReductionAdvised,
   BleedingRisk)`. Ciclosporin's section is also "Increased risk of
   bleeding." Matches.
3. `(Apixaban, Dronedarone)` → `InteractionResult(NotCovered,
   UnknownRisk)`. Still a real, sourced gap, not excluded by Finding 2's
   new precondition (Dronedarone isn't one of the four
   indication-dependent agents) — the two gaps are independent and
   don't collide.
4. `(Dabigatran, SSRIOrSNRI, true/false)` →
   `InteractionResult(DoseReductionAdvised, BleedingRisk)` /
   `InteractionResult(Caution, BleedingRisk)`. SSRIs/SNRIs' section is
   "Increased risk of bleeding" both ways. Matches.
5. `(Rivaroxaban, Verapamil)` → **this was the exact cell the original
   hand-trace flagged as unresolved (Finding 3).** Now
   `InteractionResult(CautionLowRelevance, BleedingRisk)` — the
   ambiguity has an actual answer, not just a decision to eventually
   pick one.
6. **New, demonstrating Finding 2's fix directly:**
   `(Dabigatran, Rifampicin)` → `InteractionResult(Avoid,
   ThrombosisRisk)` — one of the 6 cells the precondition redesign
   recovers; direction correctly flips to `ThrombosisRisk` (rifampicin
   decreases DOAC levels, the opposite failure mode from most of this
   table). `(Apixaban, Rifampicin)` — excluded by the precondition;
   attempting this call is a precondition violation, a provable
   impossibility rather than a silently wrong or undefined answer,
   exactly mirroring how `renal_adjustment`'s Finding 2 turned a
   category error into a type-level impossibility rather than a
   documented convention.

All six traces are consistent with the redesigned sketch and with this
audit's own original findings — no new inconsistency introduced by the
fix itself.

**Gate 1 status: closeable.** Unlike `renal_adjustment`'s Finding 1
(CrCl/eGFR computation scope), nothing here was deferred — all three
findings got an actual decision, not a named-but-open item. The next
step is Gate C1: write out `CheckInteraction`'s full case coverage (all
15 v1 agents, including the 6 recovered Rifampicin/Carbamazepine/
Phenytoin/Phenobarbital cells) and verify it for real against Dafny
4.11.0 — the sketch above is illustrative, not complete, same
distinction `renal_adjustment`'s Gate 1b→C1 transition drew.
