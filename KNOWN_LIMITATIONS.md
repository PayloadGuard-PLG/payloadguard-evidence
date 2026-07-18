# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-18 (`SYSTEM_REFERENCE.md` adopted, a new root
current-state-only reference doc verified against the live repo before
commit — no new limitation surfaced by that verification pass beyond
what's already recorded below. `evidence/polish_lint.py` added
alongside it as a new self-consistency mechanism, keeping that new
document from drifting toward narrative language. Full account:
`DEVLOG.md`'s 2026-07-18 entry.)
Prior header, preserved: Last updated 2026-07-16 (later still — `HAZARD_REGISTER.md` built for
`aeb_kernel`, 10 hazard entries, one per `REQ-AEB-*`. Preceded by
sourcing ISO 26262-3's Table 4 and Clause 6.4.4 verbatim for free
(`sources/iso-26262-3-2018-table4-and-6.4.4.md`) after a pasted
secondary-source ASIL matrix and a follow-up "resolution" message were
both checked and found wrong — full account in `DEVLOG.md`'s two
2026-07-16 (later)/(even later) entries. **New, doubly-blocked gap,
distinct from the three ISO 14971 registers' single clinical-SME gap**:
this register's Severity/Exposure/Controllability/ASIL fields are `GAP`
because BOTH no named automotive-safety reviewer exists AND the HARA
methodology clause (§ 6.4.2) that defines how to derive Exposure/
Controllability from an operational situation is still unsourced —
only Table 4's lookup mechanism and § 6.4.4's safety-goal rules are.
`HAZ-AEB-10` (malfunction/degradation going undetected) named as the
highest-priority formalization candidate, same fail-open reasoning as
`renal_adjustment`'s `HAZ-RENAL-4`. No code/spec change. 265 tests
pass, unchanged.)
Prior header, preserved: Last updated 2026-07-16 (fourth worked example built:
`examples/aeb_kernel/`, a Generic AEB kernel, sourced directly from
NHTSA FMVSS No. 127 (§ 571.127) — the first example outside the
medical-device domain. All six Gate C1-C6 steps plus Phase 3 built end
to end in one session, all shared tooling (`evidence.cli`,
`dafny_spec_lint.py`, `dafny_nl_summary.py`, `dafny_mutate.py`) reused
unmodified. Two new named findings, same discipline as
`renal_adjustment`'s ledger entries below:

- **Gate C5 real finding:** 4 survivors, all
  `IsFalseActivationCompliant`'s `requires peakAdditionalDecelG >= 0.0`
  precondition weakened (ROR to `<=`/`!=`/`<`, LVR to `-0.01`) — real,
  but not load-bearing for the function's single ensures clause (the
  biconditional `... <==> peakAdditionalDecelG < 0.25` holds regardless
  of sign). Same category as `renal_adjustment`'s "requires-clause
  weakenings not load-bearing" survivors — the precondition still
  correctly documents a real physical fact (deceleration magnitude is
  non-negative), it just isn't proof-necessary for what's currently
  established.
- **Gate C5 real, named shared-tooling gap:** 4 unclassifiable mutants,
  all COI (negate ensures clause) on `FCWRequiredActive`/
  `AEBRequiredActive`'s `target == X ==>` guard clauses — Dafny rejects
  the mutated form with "invalid UnaryExpression" (negating a one-way
  implication whose antecedent is itself an equality comparison). A
  real gap in `evidence/dafny_mutate.py`'s COI generator, same class as
  `renal_adjustment`'s documented `||`-chain ambiguity limitation — not
  fixed here (real new engineering, not a bounded fix), named instead.

Also worth recording as a positive structural finding, not a
limitation: § 571.127's core performance requirements (S5) are entirely
speed-envelope/deceleration-threshold based, not wall-clock-timing
based — the standard's millisecond-level timing figures are confined to
its test-conduct procedures (S7/S8), not its requirements. So unlike
`dosage_calculator`'s IEEE-754 gap or `renal_adjustment`'s `Pow`-
exponent gap, this domain hit no Dafny/Z3 structural expressiveness
limit at all. Full record: `examples/aeb_kernel/README.md`,
`examples/aeb_kernel/PHASE1_PLAN.md`, `SYSTEM_BLUEPRINT.md` Section 9.
265 tests pass (up from 253).)
Prior header, preserved: Last updated 2026-07-15 (yet later still — Finding 6 fully closed:
IEC 60601-2-24:1998 clause 51.102 read directly (58 pages, cover
through Annex ZB), confirming GIP's citation is near-verbatim (GIP
omits only "which may cause a SAFETY HAZARD"). This closes the "IEC
standard's own text remains unread" gap the prior entry below left
open. `sources/iec-60601-2-24-1998.pdf` archived — this repo's first
direct read of any IEC 60601-2-24 edition. Updated:
`HAZARD_REGISTER.md`, `metadata.yaml`/`.a`/`.b`/`.c.yaml`,
`RISK_MANAGEMENT_FINDINGS.md`, `sources/README.md`. Matrices
regenerated, all Tier 1 gates passed. 253 tests pass, unchanged.)
Prior entry, preserved: Last updated 2026-07-15 (yet later — Finding 6
resolved: a real
wording drift found in `HAZ-GIP-1.14`'s "verbatim" GIP citation.
Steven independently researched the IEC 601-2-24/60601-2-24 citation,
found a secondary source whose rendering of GIP Safety Requirement
1.8.1 disagreed with this repo's own transcription, then obtained the
actual GIP v1.0 PDF directly from the University of Pennsylvania to
settle it. This repo's own citation had drifted, not the secondary
source — fixed to the verbatim primary text across all six places it
appeared (`sources/gip-v1.0-hazard-analysis.md`,
`metadata.yaml`/`.a`/`.b`/`.c.yaml`, `HAZARD_REGISTER.md`); traceability
matrices regenerated via the real pipeline, all Tier 1 gates passed
clean. Byproduct: GIP v1.0's hazard tables carry no severity column for
any hazard, confirmed directly. Still open: the IEC standard's own
text remains unread. `sources/gip-v1.0-full-2009.pdf` archived. 253
tests pass, unchanged. Full account: `RISK_MANAGEMENT_FINDINGS.md`
Finding 6.) Prior entry, preserved: Last updated 2026-07-15 (later —
real severity scoring recorded for
`dosage_calculator`'s 5 hazards. Direct instruction: "start on the
severity values for the 5 hazards." Steven, the named Clinical SME,
scored every hazard `S3 — Serious` via `AskUserQuestion`, one hazard at
a time, against `RISK_MANAGEMENT_PLAN.md` §4.1's real consequence-only
bands and each hazard's own documented harm text — not proposed,
defaulted, or inferred by this repo's assistant. Mechanically applying
§4.3's already-specified matrix (a lookup, not a new judgment call):
`HAZ-GIP-1.14`/`1.2`/`1.3`/`HAZ-DOSE-003` evaluate `Unacceptable`
(P5 × S3); `HAZ-GIP-1.2b` stays an evaluation `GAP`, blocked by
Finding 5's still-open Probability-side question, not its now-known
Severity. This device's overall residual risk is now `Unacceptable` —
a real, computed result, not the placeholder `GAP` R3's model-only fix
left standing. Resolving it needs real field/usage data or a recorded
ALARP determination from Steven, per `RISK_MANAGEMENT_PLAN.md`'s "Path
to sign-off" section — both still open. Full record:
`RISK_MANAGEMENT_FINDINGS.md` Finding 3, `HAZARD_REGISTER.md`,
`RISK_MANAGEMENT_PLAN.md` §4.1/§4.3/Section 5. No code/spec/test
change; 253 tests pass, unchanged.) Prior entry, preserved: Last
updated 2026-07-15 (Three real Qodo findings on PR #55 fixed, each
independently re-verified against the real committed code before
acting: (1) `run_verify_dosage_differential.py` claimed "Gate C1
discipline" but only checked `proc.returncode`, never the verifier
summary line - the one Dafny capture in this repo with no false-zero-
guard path at all, since it sits outside the `dafny_captures_index.json`
matrix pipeline where `evidence.dafny_adapter.parse_dafny_capture`
normally gets applied (Gate C2). Fixed by calling it directly; re-ran
against the real Dafny 4.11.0 toolchain, still 9/9 matched. (2)
`_dafny_real_literal()` converted scientific-notation floats through
bare `int(value)` - lossless today only because the two real vectors
that hit it (`1e10`, `1e308`) are already integer-valued; confirmed
`int(1e-5) == 0`, a latent silent-corruption bug for any future
fractional vector. Hardened to raise instead of guessing, 2 new
regression tests. (3) `dosage_differential_vectors.py`'s own docstring
contradicted itself, claiming "every vector" keeps `raw_dose` finite
two sentences before describing the one that overflows Python's
`float` - reworded to scope the claim correctly. No evidence content
changed (re-capture identical except timestamp). 253 tests pass (up
from 251). See DEVLOG.md's 2026-07-15 entry for the full account.)
Prior entry, preserved: Last updated 2026-07-15 (R5 resolved:
differential-testing harness
built between `dosage.py`/`dosage.dfy` (9 shared vectors, all matched)
after direct verification confirmed the equivalence claim within
Dafny's representable (finite-`raw_dose`) domain. Real finding
surfaced by that verification, not previously flagged: `dosage.py`'s
docstring postcondition (`>= 0`) had silently drifted from
`dosage.dfy`'s own strict-`>` tightening, three months stale — fixed,
CrossHair re-verified clean, full artifact pipeline regenerated.
Confirmed `dafny run` executes concretely in this environment before
recommending the differential-testing option, not assumed. Scope
caveat, checked mechanically: one vector mirrors an existing overflow
test case and agrees, but via different reasoning, not a REQ-DOSE-003
equivalence claim (structurally impossible in Dafny's `real` type).
Also fixed a stale claim in root `README.md`'s "Risk management"
section, found while cross-checking this device's status. No
open-item changes to Finding 5, matrix naming, or R3's per-hazard
severity-scoring blocker. 251 tests pass. See DEVLOG.md's 2026-07-15
entry for the full account.) Prior entry, preserved: Last updated
2026-07-15 (Finding 3/R3 resolved: `dosage_calculator`'s
severity model rebuilt consequence-only, Option 3 (hybrid) chosen by
Steven over Option 1 (`AskUserQuestion`); Option 2 eliminated on
textual grounds (TR 24971 §5.5.4) before he was asked. Real, cascading
consequence: every hazard's severity is now an explicit `GAP`, not a
regression — the old evidence-strength values below (S1-S4, "3 of 4
Unacceptable") were never a valid consequence measurement, so this
device's overall residual risk is now `GAP`, not `Unacceptable`. The
concrete next item is real severity values for the 5 hazards in
`HAZARD_REGISTER.md` — Steven's clinical call, not an abstract model
question. Other open items (Finding 5, matrix naming, R5) unchanged.
No spec/test change; 236 tests pass. See DEVLOG.md's 2026-07-15 entry.)
Prior entry, preserved: Last updated 2026-07-15 (Two repo self-consistency lints built,
`evidence/hazard_id_lint.py` and `evidence/citation_registry.py`,
direct follow-up to PR #50: that PR needed a second fix round because
a hand-edit collapsed `HAZ-GIP-1.2`/`1.3` into one row, silently
dropping `HAZ-GIP-1.3`'s identity, caught only by an external reviewer
— the same root cause (a fact restated across many files with no
mechanical cross-check) as the original Annex D citation error these
docs already record. Not itself a new limitation to track here — it's
a preventive mechanism against the *class* of error this ledger's own
2026-07-15 DEVLOG entry describes, confirmed via a regression test
that runs against the real repo (`tests/test_hazard_id_lint.py`,
`tests/test_citation_registry.py`), currently zero findings. Every
open item below is untouched: nothing in this entry resolves R3, Finding
5, or the matrix-naming question. No spec/example content changed;
229 tests pass. See DEVLOG.md's 2026-07-15 entry for the full account.)
Prior entry, preserved: Last updated 2026-07-14 ("Path to sign-off" section added to
`examples/dosage_calculator/RISK_MANAGEMENT_PLAN.md`, between Sections 5 and 6.
Real finding: 2 of the 3 `Unacceptable` hazards have no more buildable
evidence at all, not merely unbuilt — `HAZ-DOSE-003`'s finiteness
postcondition can never reach `PROVEN` (Dafny's `real` type has no
IEEE-754 overflow/NaN semantics, confirmed empirically and already
documented in `dosage.dfy`'s own comment; same class of permanent
limit as `renal_adjustment`'s CKD-EPI `Pow` gap), and the
`system_scope` alarm-signal gap requires an integrated pump system
outside this POC's scope by design. Only two real paths remain: real
field/usage probability data (doesn't exist pre-market), or a genuine
ALARP determination from Steven as named Clinical SME — a policy
judgment, not more spec work, not pre-drafted here. No spec/test
change; 216 tests pass. See DEVLOG.md's 2026-07-14 entry for the full
account.) Prior entry, preserved: Last updated 2026-07-14
(Clinical SME assigned; draft severity/
probability proposal built for `dosage_calculator` and applied to its
hazard register. Direct instruction: "assign a clinical SME and start
the severity/probability tables" — declined to fabricate a name or
invent clinical data, used `AskUserQuestion` instead (same category as
every Gate C6 sign-off). **Steven** is now the named Clinical/SME for
`dosage_calculator`, by his own explicit choice; he asked for one
device drafted first. Built real severity bands (S1-S4) tied to this
kernel's actual proven/bounded-checked guarantees, a standard 5-level
probability scale defaulting every hazard to P5 (worst-case, no field
data exists) per this plan's own already-established policy, and a
3-region acceptance matrix. Real finding: none of the 4 hazards
reaches S3/S4 given what's proven; 3 of 4 evaluate provisionally
`Unacceptable` under the mandated worst-case default, making this
device's proposed overall residual risk `Unacceptable` today. Every
value marked `DRAFT` throughout — a starting proposal for Steven's
review, not a self-declared sign-off. No spec/test change; 216 tests
pass. See DEVLOG.md's 2026-07-14 entry for the full account.) Prior
entry, preserved: Last updated 2026-07-14
(`HAZARD_REGISTER.md` landed for
`drug_interaction_checker` too — third and final hazard-register
artifact; all three worked examples now have both a risk-management
plan and a hazard register. Like `renal_adjustment`, no published
hazard table exists for this device; unlike either prior register,
this spec's own Gate C6 addenda already contained a real, closed
hazard incident (Addendum 4, 2026-07-13) to draw on directly. 6 hazard
entries, one per `REQ-DDI-*`, all currently `PROVEN`. `HAZ-DDI-4`
(fail-safe on unknown pairings) flagged as the one hazard fully closed
by proof already — contrast with `renal_adjustment`'s still-open
equivalent. `HAZ-DDI-5`/`HAZ-DDI-6` document two real, closed
indication-scoping bugs in full (apixaban+inducer's fabricated
`Caution`; Dabigatran+Verapamil's unscoped 110mg figure). Gate C5
residual (44 survivors, explained) and Gate C6's closed status cited
directly. Severity/probability/evaluation left explicit `GAP`s.
`RISK_MANAGEMENT_PLAN.md` Section 8 updated. Two real bugs Qodo caught
on the renal register (PR #47) fixed along the way: `HAZ-RENAL-1`'s
citation of two lemmas/"11 verified" existing only in a historical
sketch, not the committed spec (fixed to cite the real 7-verified
capture), and an "eight" vs "nine" `REQ-RENAL-*` count inconsistency
(fixed: 8 hazard entries covering 9 requirement IDs). No spec/test
change; 216 tests pass. See DEVLOG.md's 2026-07-14 entry for the full
account.) Prior entry, preserved: Last updated 2026-07-14
(`HAZARD_REGISTER.md` landed for
`renal_adjustment` too — second real hazard-register artifact,
extending the approach from `dosage_calculator` with a genuinely
different construction: no published hazard table exists for this
device, so 8 hazard entries (one per `REQ-RENAL-*`) are built from
`metadata.a.yaml`'s sourced requirement text and `GATE_1C_AUDIT.md`'s
own hand-trace findings. `HAZ-RENAL-1` incorporates Gate 1c Finding 2
(CrCl/eGFR type-confusion, closed by a type-safety redesign);
`HAZ-RENAL-2` incorporates Finding 1's still-open half (CKD-EPI eGFR
computation caller-supplied, a confirmed Dafny/Z3 expressiveness
limit); `HAZ-RENAL-4` flagged as highest-priority among the 4
prose-only requirements (fail-open on missing data); `HAZ-RENAL-5`
documents a hazard Gate C4 already caught and closed itself. A
"explicitly out of scope" section distinguishes genuine exclusions
from in-scope-but-unbuilt GAP rows. Severity/probability/evaluation
left explicit GAPs. `RISK_MANAGEMENT_PLAN.md` Section 8 updated. No
spec/test change; 216 tests pass. No PR opened yet. See DEVLOG.md's
2026-07-14 entry for the full account.) Prior entry, preserved: Last
updated 2026-07-14 (`HAZARD_REGISTER.md` landed for
`dosage_calculator` — first real hazard-register artifact in this
repo. Chosen as easiest of the three examples because its primary
source, `sources/gip-v1.0-hazard-analysis.md`, is itself a formal
published hazard analysis (GIP v1.0, 2009) already partially cited in
this device's own STRIDE threat model — unlike the other two examples'
clinical-guideline sources. Four hazard entries: `HAZ-GIP-1.2/1.3/1.14`
(GIP-sourced, cross-referenced against this kernel's real risk control
measures and evidence) plus `HAZ-DOSE-003` (no GIP source, stated
plainly, weaker `BOUNDED_CHECKED` evidence). An explicit "out of scope"
section names representative hazards from GIP's ~85-row table this
narrow kernel doesn't address, so the register isn't misread as
covering the full pump. Severity, probability, and risk-acceptability
evaluation left as explicit `GAP`s — hazard identification (clause 5.4)
is real; estimation/evaluation (clauses 5.5/6/8) still need a clinical
SME. `RISK_MANAGEMENT_PLAN.md` Section 8 updated accordingly. Branch
restarted from latest `main` first, since PR #45 had already merged.
No spec/test change; 216 tests pass. Opened as PR #46; two real bugs
Qodo caught in review were fixed before merge — a mischaracterized
non-finite-overflow hazard (the value is clamped, not propagated) and
a stale "FRN tag undecoded" claim (resolved 2026-07-05, both the
register and a pre-existing `RISK_MANAGEMENT_PLAN.md` line from PR #45
now cite the real resolution). Awaiting the user's evaluation of this
first result before extending to the other two examples. See
DEVLOG.md's 2026-07-14 entry for the full account.)
Prior entry, preserved: Last updated 2026-07-14
(`RISK_MANAGEMENT_PLAN.md` landed for
`dosage_calculator` — third and final risk-management-plan artifact;
all three worked examples now have one. Mirrors the other two plans'
structure and clause citations. Two real device-specific distinctions
surfaced honestly: this is the only example with three evidence types
per requirement (CrossHair `BOUNDED_CHECKED`, concrete
`EXAMPLE_CHECKED`, Dafny `PROVEN`) — REQ-DOSE-003 has no Dafny proof at
all, stated plainly; and REQ-GIP-1-4-12's existing `kernel_scope`/
`system_scope` split (2026-07-05 Gate 1 review) became Section 1's real
life-cycle scoping, with the existing STRIDE threat model named as a
related-but-distinct artifact, not a substitute for the still-missing
clinical hazard register. Gate C5 residual: 56 mutants, 0 survivors, 0
unclassifiable — the cleanest of the three. Gate C6 confirmed
2026-07-07 by Steven, the first Gate C6 sign-off recorded anywhere in
this repo. Sections needing clinical judgment left as explicit `GAP`s.
No spec/test change; 216 tests pass. See DEVLOG.md's 2026-07-14 entry
for the full account.) Prior entry, preserved: Last updated 2026-07-14
(`RISK_MANAGEMENT_PLAN.md` landed for
`renal_adjustment` too — second real ISO 14971 risk-management-plan
artifact, same day as the first. Mirrors the `drug_interaction_checker`
plan's structure and already-verified clause citations. Filled with
this repo's own real evidence: `metadata.a.yaml`'s intended-use text,
Gate C1-C6 references for the 5 `PROVEN` rows, honest `GAP` rows for
REQ-RENAL-3/4/6/7 (named, sourced, unformalized) and REQ-RENAL-8
(permanent trust boundary), the Gate C5 residual (51 survivors, all
three categories already explained, not silently carried), and Gate
C6's closed status (2026-07-11). Sections needing clinical judgment
left as explicit `GAP`s, matching `classification_rationale`'s
`DECLARED` status. A real, pre-existing staleness bug found and fixed
along the way: `examples/renal_adjustment/README.md`'s own "Open
questions" item 4 still said Gate C6 sign-off was "still pending" —
actually closed 2026-07-11, the same day that sentence was written;
the 2026-07-11 documentation audit had fixed the equivalent claim in
the top-level `README.md` but missed this per-example copy. Fixed in
place, not deleted. No spec/test change; 216 tests pass. See DEVLOG.md's
2026-07-14 entry for the full account.) Prior entry, preserved: Last
updated 2026-07-14 (`RISK_MANAGEMENT_PLAN.md` landed for
`drug_interaction_checker` — first real ISO 14971 risk-management-plan
artifact in this repo. Preceded by reading the real ISO 14971:2019
standard directly, clauses 1-7.1 verbatim, and cross-checking a
provisional, externally-supplied template against it before trusting
its clause citations. Found one real, minor citation slip — the
template attributed "this plan is part of the risk management file" to
clause 4.5; that sentence is verbatim in clause 4.4, and 4.5 is the
separate requirement for what the risk management *file* itself must
trace. Every other citation (4.4a-g; clause 1's exclusions) verified
accurate. Fixed and landed at
`examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md` with
Sections 1/3/6 (scope, review triggers, verification activities)
filled from this repo's own real, committed evidence — all six
REQ-DDI-* rows, the Gate C5 mutation-testing residual (44 survivors,
already explained, not silently carried), and Gate C6's closed status.
Sections 2 and 4 (roles; severity/probability bands; acceptance
matrix) deliberately left as explicit `GAP`s, not fabricated — no
clinical SME assigned yet, matching `metadata.a.yaml`'s own
`classification_rationale` naming the `B` safety classification as
`DECLARED`, not sourced, pending exactly this kind of file. No spec or
test-suite change; 216 tests still pass. See DEVLOG.md's 2026-07-14
entry for the full account.) Prior entry, preserved: Last updated
2026-07-13 (Gate C6 confirmed and closed for
`drug_interaction_checker.dfy`, against the raw sources directly — a
full, independent, line-by-line review of all 68 `CheckInteraction`
postconditions and all 5 `DoseReductionTargetMg` postconditions against
every one of `sources/sps-doac-interactions-2024.md`'s 17 sections,
plus `sources/emc-smpc-dabigatran-indications-2025.md` for the
indication-scoping cells, found no discrepancy. Two drafts of an
externally-produced technical review report were independently
cross-checked against the real artifacts — the first had four real
errors, all confirmed by direct inspection; the corrected draft fixed
all four, with one further precision point preserved (the established
three-way distinction between vacuous-antecedent, redundant-consequent,
and requires-domain-restriction mutation-survivor mechanisms, only the
last of which "function transparency" actually names). **Decision —
Confirmed, 2026-07-13, by Steven.** All six Gate C1–C6 pipeline steps
are now built AND confirmed for this example. See the "Gate C6
confirmed and closed" section near the end of this file for the full
account.) Prior entry, preserved: Last updated 2026-07-13 (Gate C5
extended for `drug_interaction_checker`
to re-verify the committed STP suite against every mutation-testing
survivor, not just the bare spec — a real, hand-verified engineering
change, not just a re-run. Hand-probed before building: the STP suite's
existing ACCEPT lemmas (reused verbatim) catch the 6
`DoseReductionTargetMg` requires-clause indication-guard survivors, the
same class of scope-leak bug the entry below fixed on `CheckInteraction`
— caught here as a latent gap before it could ever become a real
regression. Confirmed by hand-probing that the escalation does NOT help
the other 44 survivors, for a genuine Dafny-semantics reason (both
functions are plain, non-`{:opaque}` `function`s, so same-module STP
lemmas verify by unfolding the body directly). Real run: 1342 mutants —
744 killed, 522 filtered_static, 44 survived (down from 50), 26
unclassifiable, 6 killed_via_stp_suite. See the "Gate C5 extended:
STP-suite escalation, 2026-07-13" section near the end of this file for
the full account. Prior entry, preserved: Last updated 2026-07-13 (a
second Qodo review, run against PR #40 after
it merged, found a real scope-leak bug in `CheckInteraction`'s own
apixaban rows — the four apixaban+inducer match arms computed `Caution`
unconditionally, never inspecting `treatmentIndication`, silently
fabricating an outcome once `OrthopaedicVTEProphylaxis` made a third
indication value constructible. Fixed: each arm now returns `NotCovered`
for the orthopaedic indication, matching this repo's own
`(Apixaban, Dronedarone)` silent-cell convention. All six gates re-run
for real; Phase 3 regenerated, still 6/6 PROVEN rows. See the "Gate C6
review (second, post-merge), 2026-07-13" section near the end of this
file for the full account. Prior entry, preserved: Last updated
2026-07-13 (all four Gate C6 review findings on the
REQ-DDI-5/REQ-DDI-6 sign-off document resolved — `TreatmentIndication`
gained a third constructor, `DoseReductionTargetMg` gained an
indication guard on its Dabigatran+Verapamil cell, per Steven's
decision after primary-source verification confirmed the finding was
real; a second, independent tooling gap in `evidence/dafny_mutate.py`
found and fixed along the way. All six gates re-run for real; Phase 3
regenerated, still 6/6 PROVEN rows. See the "Gate C6 review, 2026-07-13"
section near the end of this file for the full account. Prior entry,
preserved: Last updated 2026-07-12 (REQ-DDI-5/REQ-DDI-6 built for real, all six
Gate C1–C6 steps re-run, both requirements now render as real PROVEN
matrix rows with no GAP rows remaining in `drug_interaction_checker` —
see the "Phase E REQ-DDI-5/6" section at the end of this file for the
full account. Prior entry, preserved: Last updated 2026-07-12 (an
externally-supplied REQ-DDI-5/6 scoping
document was verified against primary sources before any build
decision, per direct instruction — "verify first, then we'll consider
the solutions." All claimed quotes against the already-committed
`sources/sps-doac-interactions-2024.md` passed
`evidence/citation_gate.py`, including a deliberate false control that
correctly returned NOT_FOUND. Three new sources fetched, verbatim-
verified, and archived — both eMC apixaban SmPCs, the MHRA DSU renal
table, and the US FDA ELIQUIS label (flagged as a non-UK contrast
source) — see `sources/README.md`'s 2026-07-12 entries for the full
account. Finding: REQ-DDI-5/REQ-DDI-6 are buildable from public UK
sources; apixaban's absent numeric interaction rule is a genuine,
sourced gap, not an oversight. No code changed, no requirement built —
this is a sourcing-only update, not a new gate. Prior entry, preserved:
Last updated 2026-07-11 (Phase 3 — evidence packaging — built for
`renal_adjustment` and `drug_interaction_checker`, the first two
Dafny-only examples to reach this stage; `dosage_calculator` remains the
only example with a full three-evidence-type packaging. Found and fixed
three real, generally-applicable gaps in shared code along the way, not
worked around locally: `evidence/cli.py`'s `--manifest`/`--concrete`
flags were hard-required everywhere, all the way down to
`derive_bounds_block()` demanding a crosshair manifest's
`effective_bounds` — extended to treat "no crosshair evidence declared"
as a legitimate `None` state, mirroring `dafny_store`'s own established
precedent, rather than fabricate fake bounds data (which would have
falsely implied a search happened); the metadata schema's
`toolchain.crosshair_bounds` was unconditionally required even for
Dafny-only metadata — relaxed to optional in all three schema files;
the schema's `id` pattern excluded lowercase letters, rejecting
`REQ-RENAL-1a` — the same class of gap already fixed once in
`dafny_nl_summary.py`'s `_REQ_ID_RE` (2026-07-08), now found
independently in a second place and fixed the same way. Confirmed zero
regression against `dosage_calculator`'s real, existing pipeline by
regenerating its real artifacts before and after every change and
diffing byte-for-byte (timestamps aside). See the "Phase 3 — evidence
packaging" section below for the full account. Prior entry, preserved:
Last updated 2026-07-11 (`renal_adjustment.dfy`'s Gate C6 sign-off
confirmed and closed — six checkpoints independently re-verified
against the raw KDIGO/MHRA sources directly and live Dafny re-runs, one
unverifiable supporting citation flagged rather than absorbed; see the
"Phase D Gate C6 sign-off" section below. `renal_adjustment` now has all
six Gate C1–C6 pipeline steps both built and confirmed, matching
`drug_interaction_checker`'s status). Prior entry, preserved: Last
updated 2026-07-10 (PayloadGuard CI gate and pytest CI job entries
added — see their own table rows; a third worked example,
`drug_interaction_checker` (Phase E), had all six Gates C1–C6 built or
confirmed the same day — Gate C4 found a real spec gap larger than Gate
C1's own, Gate C3 required real, non-trivial extension to
`evidence/dafny_spec_lint.py` itself (a shared module, not just this
example's own files) to model Dafny datatype comparisons, Gate C2
confirmed the PROVEN-exclusivity binder generalizes to a real capture
for the first time since `dosage_calculator`, Gate C5's mutation run
found and fixed a real crash bug in Gate C3's own extension (ordering
operators on datatype/`EnumSort` operands weren't modeled by Z3's Python
bindings) before producing 7 real, explained survivors, and Gate C6
genuinely extended `evidence/dafny_nl_summary.py` to support multi-line
clauses for the first time (a deliberately different call than
`renal_adjustment`'s equivalent gap, which was fixed by reformatting the
spec instead) — its sign-off document was **confirmed by Steven the same
day**, closing Gate C6 for this example; the sign-off itself caught and
fixed a real doc-accuracy bug in the sign-off document's own text (an
item mislabeling an indication-dependent exclusion as "source gap"),
corrected before recording the decision. See their table rows and the
"Phase E Gate C1"/"Phase E Gate C4"/"Phase E Gate C3"/"Phase E Gate
C2"/"Phase E Gate C5"/"Phase E Gate C6" sections below. Phase
B/C entries below (Gate 2/C2-C4 wiring extended to variants A/B, etc.)
date to 2026-07-07 and are historical, not stale — the ledger below is
append-only and each entry is dated individually. The renal-adjustment
second worked example (Phase D) has its own extensive entries further
down this file, current as of its Gate C6 sign-off confirmation on
2026-07-11. For
current status rather than full history, see `HANDOFF.md`; for the
dated build-by-build narrative, see `DEVLOG.md`.

| Gate | Status | Summary |
|---|---|---|
| Gate 2 — CONFLICT rule + binder | **COMPLETE** | `evidence/conflict.py` implements both CONFLICT sub-types (12 tests). `build_matrix()` (`evidence/render/matrix_variants.py`) is the sole implementation across all four variants, running Type 1 internally on every call; Type 2 stays standalone (whole-manifest-set check, not per-variant). `evidence/cli.py` wraps it for any metadata/manifest/concrete-store path. The Step 2 fallback functions (`build_matrix_variant_a/b/c`) and `tests/test_binder_equivalence.py` (which existed solely to check against them) are deleted — git history holds them if ever needed again. Details below. |
| Gate 3 — bounds enforcement via CrossHair API | **DECIDED 2026-07-06: stay-CLI** | Real behavioral test executed (not just a technique writeup) — findings below. |
| Gate 4 — binding authorship | **DECIDED: option 3 (both, cross-checked); Type 1 now implements this for all three metadata shapes, incl. variant C** | Decision and mechanism below. |
| Gate 5 — single-evidence-type fixture for variant C, extended to a third partition | **FULLY RESOLVED (2026-07-06); EXTENDED 2026-07-07** | `tests/test_single_evidence_type.py`: both symbolic-only AND concrete-only in-memory fixtures now appear in exactly one variant-C artifact each. The concrete-only case was impossible until today: `_bind_self_describing` bound a symbolic record to every requirement unconditionally, regardless of what it declared. **Extension (2026-07-07):** the dual-matrix pattern (symbolic/concrete) is now a triple: `traceability_matrix.formal.json`, method-filtered to `dafny`, carries this repository's first-ever real, rendered PROVEN rows. Details below. |
| Gate 6 — FRN pump-type tag | **RESOLVED** | `FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725); within the GIP taxonomy, general-purpose volumetric infusion pumps (peristaltic mechanism, cassette-based administration set), distinct from `All`. Full trail in `sources/README.md`. Well-supported (NotebookLM extraction of the full source PDF, cross-checked against independent FDA-registry research landing on the same code) but not yet independently re-verified against the raw Sec 2.4.1 text — noted, not hidden. |
| Phase C Gate C1 — Dafny adapter | **BUILT 2026-07-07; spec strengthened 2026-07-07 by Gate C4** | Real Dafny 4.11.0 spec for the dosage kernel (`examples/dosage_calculator/dosage.dfy`, verifies clean: `2 verified, 0 errors` — an `ExpectedDose` function plus the method, since Gate C4's fix) plus a deliberately broken variant (`dosage_broken.dfy`, fails for real: `0 verified, 2 errors`, exit 4); a capture runner pair (`run_verify_dafny.py` / `run_verify_dafny_broken.py`) mirroring `run_verify.py`'s discipline, with real committed captures; and `evidence/dafny_adapter.py::parse_dafny_capture`, implementing the false-zero guard via regex on the verifier's own summary line (never a substring match, never bare exit code), refusing on nonzero exit, missing summary line, or nonzero error count. Six tests in `tests/test_dafny_adapter.py`, including a substring-trap regression and a check that `assert_no_realized_proven` still blocks this adapter's PROVEN output from ever reaching a matrix row. REQ-DOSE-003 is explicitly scoped out of the Dafny spec (Dafny `real` has no IEEE overflow concept — confirmed empirically). |
| Phase C Gate C2 — PROVEN exclusivity migration | **BUILT 2026-07-07; wired end-to-end 2026-07-07** | Ruling **R3** (supersedes R2): `assert_no_realized_proven` (`evidence/render/matrix_variants.py`) now permits PROVEN as a realized strength only when a record's `method == "dafny"` AND `verifier_completion_status == "completed"`; every other method — including a record with no method at all — is still hard-blocked, exactly as under R2. 8 new tests in `tests/test_proven_exclusivity.py`: a positive case (a real Dafny PROVEN record, produced the same way Gate C1's adapter produces it, is accepted), explicit negatives for crosshair and concrete_test records forced to claim PROVEN (checked explicitly, not by omission), a missing-method case, two defense-in-depth cases (a `method == "dafny"` record without a completed status is still refused), the row-level-cell shape (variant B/C), and a regression check that all four committed matrix artifacts — none of which contain a dafny record today — still pass unchanged. **Wiring (2026-07-07):** R3's positive branch is no longer only proven correct in isolation — `traceability_matrix.formal.json` is a real artifact where it fires for real, verified by the structural PROVEN sweep in `generate_artifacts.py`. |
| Gate 2 / C2-C4 wiring — real Dafny evidence reaches a live matrix row | **BUILT 2026-07-07 (variant C); EXTENDED 2026-07-07 (variants A/B)** | The first real PROVEN row ever rendered in this repository. Scope ratified with Steven before building (variant C only, then explicitly extended: "go ahead and extend variant A and B now"; Z3 gate inside the binder; metadata declares dafny evidence explicitly). `intent_ok` is `True` for REQ-GIP-1-4-12/REQ-GIP-1-8-1 in EVERY variant artifact now — the temporary A/B divergence tracked when C landed first is closed and its carve-out mechanism retired. See the detailed section below for the full design. |
| Phase C Gate C3 — Dafny output-parsing hardening | **BUILT for vectors 1–3 (2026-07-07); vector 4 BLOCKED, named** | **Vector 1 (vacuous preconditions):** `evidence/dafny_spec_lint.py::check_precondition_satisfiability` extracts a method's `requires` clauses and asks Z3 for real satisfiability, via a small hand-written expression translator (booleans, comparisons incl. chaining, arithmetic, real/int/nat/bool — anything else, e.g. quantifiers, refused outright). Proven against a real committed fixture, `examples/dosage_calculator/vacuous_precondition_probe.dfy`: Dafny itself reports a clean pass (`1 verified, 0 errors`) on a method whose precondition (`x > 0 && x < 0`) can never hold; the checker correctly reports `unsat`. **Vector 2 (weak postconditions, best-effort heuristic, not a proof):** `scan_weak_postconditions` flags `ensures` clauses using a one-way `==>` without a matching `<==>`, tested against a synthetic weak clause (flagged) and both the real dosage.dfy spec and a `<==>` clause (correctly not flagged). **Vector 3 (timeout/resource-limit masking):** real finding on the installed 4.11.0 binary — `dafny verify --resource-limit=1` on the real dosage.dfy spec produces `Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource` — an "errors" count of 0 alongside an incomplete run. Confirmed the real capture's exit_code is 4 (nonzero), so Gate C1's exit-code check already refuses it (an earlier suspicion of an exit-0 false-zero here was a shell-piping artifact in this session's own probing, corrected before being reported as a finding); the summary-line parser in `evidence/dafny_adapter.py` was still hardened to refuse independently on `"out of resource"`/`"out of memory"`/`"timed out"` markers and on more than one summary line in a capture, as defense in depth. **Vector 4 (specification stripping): still BLOCKED, named** — the source material describing this fourth vector was cut off before detail was captured; needs a follow-up read of the original document before it can be scoped at all, not inferred from the name. **Vector 1's translator extended 2026-07-10** for `drug_interaction_checker.dfy`'s Gate C3 — see the "Phase E Gate C3" section below for the real gap this surfaced and the EnumSort fix. |
| Phase C interface: `verifier_completion_status` on VerificationResult | **RESOLVED via Gate C1 + C2** | The field exists on `VerificationResult` (`evidence/model.py`), is set by Gate C1's adapter, and is now load-bearing in Gate C2's R3 check — PROVEN requires it to equal `"completed"`, not just a matching method label. Strength-assignment stays adapter-scoped, so PROVEN remains structurally impossible for CrossHair/pytest-backed requirements. |
| Phase C Gate C4 — Spec-Testing Proofs (STPs) | **BUILT 2026-07-07; found and fixed a real spec gap** | IronSpec methodology: prove specific input/output pairs are accepted or rejected by the SPECIFICATION alone, independent of any implementation. Applied to dosage.dfy, an STP lemma revealed the original postcondition (bounds + reverse-flow-zero only) never pinned `dose` to the actual clamped value — a wrong candidate value could not be proven excluded, meaning a broken implementation could have satisfied the spec undetected. **Fixed for real:** `dosage.dfy` gained an `ExpectedDose` function and a pinning `ensures dose == ExpectedDose(...)` clause; re-verified clean (`2 verified, 0 errors`); the real committed capture was re-run honestly (`raw_dafny_output.txt` / `run_manifest_dafny.json` now reflect the fixed spec). The original weak spec is preserved verbatim as `dosage_underconstrained.dfy` (an honesty exhibit, same rationale as `dosage_naive_widening.py`). Two STP suites prove both directions for real: `dosage_stp_suite.dfy` (6 lemmas across the 3 logical branches — normal in-range, ceiling-clamped, reverse-flow — `include`s the fixed spec, all verify: `10 verified, 0 errors`) and `dosage_stp_suite_against_underconstrained.dfy` (the 2 REJECT lemmas for the branches that actually had a gap, `include`s the preserved weak spec, both genuinely fail: `0 verified, 2 errors`, exit 4 — a real negative capture, not smoothed over). 6 new tests in `tests/test_dafny_stp_suite.py`, including a regression on a self-caught mistake (an early REJECT-lemma draft used an out-of-bounds wrong value that the weak spec already excluded trivially, giving a false pass that didn't test the real gap — caught and corrected before committing). Neither STP suite is wired into `build_matrix()` or any generator; matches Gates C1–C3's scope discipline. |
| Phase C Gate C5 — Mutation testing (MutDafny-style) | **BUILT 2026-07-07, extended twice same day (chain/AOR from research, then LVR); 56 mutants, zero survivors, zero unclassifiable** | `evidence/dafny_mutate.py` generates mutants (ROR/LOR/AOR/LVR/COI); `examples/dosage_calculator/run_mutation_suite.py` real-verifies every one against the installed Dafny 4.11.0 binary. History: an initial v1 run (39 mutants, ROR/LOR/AOR/COI) found 2 real survivors (REQ-GIP-1-8-1's `>=` boundary, **fixed** by tightening to `>` on Steven's decision) and 4 unclassifiable results (chain-direction parse errors). External research then produced chain-direction-aware ROR and function-body AOR (42 mutants, zero survivors/unclassifiable) — see the row below for the LVR extension built after that, same day, from its own scoped sub-plan. SOR/HOR remain not implemented, checked not assumed (no set or heap syntax anywhere in the spec, confirmed by test). **Final combined real run across all five operator classes: 56 mutants — 41 killed, 6 filtered_static, 4 filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 4 filtered_magnitude_implied — zero survived, zero unclassifiable.** 33 tests total (`tests/test_dafny_mutate.py`, 25 — fast, pure generation/filter logic, no Dafny invocations; `tests/test_mutation_report.py`, 8 — validates the committed real capture). Full detail below. |
| Phase C Gate C5 LVR extension — Literal Value Replacement | **BUILT 2026-07-07; real run matched every hand-derived prediction exactly, zero survivors** | `evidence/dafny_mutate.py::generate_lvr_mutants` mutates every numeric literal in `dosage.dfy`'s requires/ensures clauses and `ExpectedDose`'s function body — all 7 are exactly `0.0` — to `original ± 0.01` (the clinical-precision floor sourced in the Gate C5 research; the first place that guidance has an actual application). `_lvr_trivial` generalizes ROR's requires/ensures polarity principle from operator-implication to magnitude-implication for LE/LT/GE/GT-adjacent literals (4 filtered as `filtered_magnitude_implied`); EQ-adjacent and all function-body literals have no such filter, sent straight to real verification. Real run: **14 mutants — 10 real-verified, all 10 genuinely killed, zero survivors** — matching the scoping session's hand-worked prediction exactly, site by site (e.g. why widening `concentrationMgPerMl > 0.0` to `> -0.01` fails via `ExpectedDose`'s own unchanged precondition at the pinning clause's call site). 7 new tests. Combined with the rest of Gate C5: **56 mutants total — 41 killed, 6 filtered_static, 4 filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 4 filtered_magnitude_implied — zero survived, zero unclassifiable.** The clinical-precision-floor-vs-exact-zero-requirement tension named in scoping is unresolved — REQ-GIP-1-8-1's function-body zero-literal mutant (site 7) was killed at the ±0.01 granularity, so the tension didn't need resolving to get a clean result here, but the underlying judgment call (is ±0.01 the right test for an exact-zero safety requirement) is still open. Full detail below. |
| Phase C Gate C6 — NL-dialogue confirmation | **BUILT and SIGNED OFF 2026-07-07** | Process-control gate aimed directly at recurrence of Gate 1's original finding: a spec/requirement-text mismatch caught only at review, not at authoring time. `evidence/dafny_nl_summary.py::summarize_method` mechanically extracts each requires/ensures clause verbatim, plus any REQ-ID cited in a trailing comment, alongside a best-effort operator-substitution English gloss labeled as a reading aid, not comprehension — deliberately not a natural-language generator. Only single-line clauses are supported; the function cross-checks its own line-based, comment-preserving extraction against `dafny_spec_lint`'s canonical, already-tested multi-line-capable extractor and refuses (`SystemExit`) on any content mismatch. That refusal check's first draft compared clause counts, not content, and missed a real case — a synthetic multi-line clause produced the same count under both extractors while the line-based scan had silently truncated it, dropping the continuation; caught in manual testing before the test suite was even written, fixed by comparing normalized clause text instead of counts, with a regression test added. 7 tests in `tests/test_dafny_nl_summary.py`. The gate's actual deliverable is not this code but the recorded human decision it feeds: `examples/dosage_calculator/nl_confirmation_dosage_dfy.md` records Steven's sign-off ("it's good for the spec as is") on the generated summary for `dosage.dfy::CalculateHourlyDose`, plus a next-phase item (adapting the spec and explaining downstream analysis by different software, for a regulatory submission) he explicitly scoped out as separate follow-up work, not part of this gate. |
| Gate C6 next-phase adaptation work | **BLOCKED, named 2026-07-07 — asked, not guessed** | Full note in `payloadguard-evidence-roadmap-phaseB-to-C.md`'s "Gate C6 next-phase adaptation work" section. Trigger condition ("a defensible artifact to build it on top of") is now met — the full evidence chain (Gates C1/C4/C5/C6) exists. But the only description of this work anywhere in the repo is one sentence from the original Gate C6 sign-off, repeated verbatim in every place it's mentioned, never elaborated — checked directly (grepped the whole repo, including `PayloadGuard-Evidence-Blueprint-1.md`'s cited FDA guidance URLs), not assumed. Three concrete unknowns block real scoping: what "adapting the spec" means, what "different downstream software" refers to, and which regulatory pathway (510(k)/De Novo/PMA/other) this targets. Matches Gate C3 vector 4's own precedent (stayed BLOCKED, named, rather than inferred from its name alone) — resolved by asking directly rather than guessing a concrete plan from one sentence. |
| PayloadGuard CI gate — third-party pre-merge scan | **WIRED 2026-07-10 — unverified-claim caveats named, not blanket-trusted** | `.github/workflows/payloadguard.yml` runs a third-party GitHub Action (`PayloadGuard-PLG/payload-consequence-analyser`, pinned to a commit SHA) on every PR into `main`, discovered and wired after a real CI failure surfaced a mutable-tag risk this repo doesn't accept elsewhere. Its exit-code contract was confirmed by reading `analyze.py` directly, not by trusting the wrapper `action.yml`'s shell logic or the tool's own `--help` epilog (which itself underspecifies the CAUTION verdict): exit 0 covers SAFE, REVIEW, and CAUTION alike (none block merge), exit 1 is an analysis error, exit 2 is DESTRUCTIVE — only 1 and 2 are gated on. The tool's own composite-action wrapper labels its `verdict` output "SAFE" for any exit-0 result even when the real finding was REVIEW/CAUTION, a real wrapper quirk this repo's workflow works around by gating on `${EXIT_CODE}` directly, never on `${VERDICT}` — noted in `payloadguard.yml` itself so it isn't "fixed" the wrong way later. Full detail below. |
| pytest CI job | **ADDED 2026-07-10** | `.github/workflows/tests.yml` runs `python -m pytest tests/ -q` on every PR into `main`, closing a real gap: until now, `main` had no automated check that the test suite itself still passes — `HANDOFF.md`'s own working-conventions section said "no CI is configured on this repo" (stale, now corrected) and relied entirely on the local run before each commit. Installs from a new `requirements.txt` (pytest/jsonschema/PyYAML/z3-solver, pinned to exact versions, not floated). No Dafny/Z3 *binary* toolchain install in the job — confirmed before adding it, not assumed, by grepping `tests/` and `evidence/` for `subprocess` usage: the suite reads committed verification captures, it never shells out to a live `dafny`/`crosshair` invocation; the one real subprocess use in `tests/` drives this repo's own `evidence.cli`, not an external verifier. `z3-solver` is Z3's Python binding, needed by `evidence/dafny_spec_lint.py`'s own precondition-satisfiability translator — a different thing from the Dafny verifier binary, and sufficient on its own for every test to pass. |
| Phase E Gate C1 — `drug_interaction_checker.dfy` spec + capture | **BUILT 2026-07-10 — a real false-clean result caught before committing** | Third worked example, testing whether Gate C1–C6 generalizes to set/list-membership logic. `CheckInteraction(doac, agent, hasOtherBleedingRiskFactors): InteractionResult` — 63 match arms across 15 v1 agents, a `requires` clause excluding two agents' still-blocked apixaban cells (Gate 1c Finding 2's resolution) — verifies clean (`1 verified, 0 errors`). **An early draft with no `ensures` clauses reported "0 verified, 0 errors"** — Dafny generated zero verification tasks, since match-exhaustiveness is a resolve-time syntax check, not an SMT proof, and a function with no postconditions has nothing else to prove; that "0 verified, 0 errors" would have been a false-clean result if committed as-is, exactly the class of overclaim this repo's whole discipline exists to catch. Fixed by adding three real `ensures` clauses (a `NotCovered`-implies-the-one-real-source-gap pin, a `Contraindicated`-implies-`Dabigatran` pin, a `Digoxin`-always-safe pin), matching how every other function in this repo (`GStage`, `SelectFormula`, `ComposedCeiling`) commits to a real claim in its own signature rather than leaving the match body as the only content. `evidence/dafny_adapter.py::parse_dafny_capture` parses the real capture unmodified (`Strength.PROVEN`, `verifier_completion_status == "completed"`) — the third confirmation this parser generalizes across worked examples with zero changes. Full per-cell pinning of all 63 match arms is deferred to Gate C4 (STP lemmas), matching this repo's established division of labor, not duplicated inline. |
| Phase E Gate C4 — `drug_interaction_checker.dfy` STPs | **BUILT 2026-07-10 — found a real spec gap larger than Gate C1's own** | IronSpec methodology applied to `CheckInteraction`. Gate C1's original 3 `ensures` clauses turned out to be only a stopgap: a genuine ACCEPT lemma restating just those 3 clauses as premises **failed to prove the correct value for any cell they didn't directly mention** — e.g. `(Dabigatran, Ketoconazole)`, which should be `Contraindicated`, was provably *not forced* to any value at all by the declared spec. Confirmed with a real committed failing capture, not just predicted: `drug_interaction_checker_stp_suite_against_underconstrained.dfy` (3 ACCEPT lemmas restating the preserved original's 3 clauses) genuinely fails — `0 verified, 3 errors`. **Unlike `renal_adjustment`'s own Gate C4 finding** (postconditions *bounded* a result without *pinning* it, so ACCEPT proofs succeeded on loose bounds while REJECT proofs failed to exclude wrong values), most cells here had **no constraint at all**, bound or pin — the match body's correctness was never actually a signature-level claim, only an artifact of the implementation happening to be right. **Fixed** by restating all 63 match arms as explicit pinning `ensures` clauses on `CheckInteraction` itself (`drug_interaction_checker.dfy`, re-verified clean: `1 verified, 0 errors`, resource cost 358,399 — the heaviest single verification task recorded across all three worked examples, still completing in well under a second). The real STP suite (`drug_interaction_checker_stp_suite.dfy`) then covers the established Gate 1c worked examples as 7 ACCEPT lemmas (6 cells, including both branches of the caller-supplied-flag-conditional SSRI/SNRI case) plus 4 REJECT lemmas — 3 for the `Contraindicated` cells, the highest-stakes rows in the table, proving a plausible-but-wrong weaker `Caution` candidate is genuinely excluded, not just absent from the match arm by accident, plus one more REJECT lemma re-testing Gate 1c Finding 3's specific ambiguity (`Rivaroxaban`+`Verapamil` is provably not the unqualified negative digoxin gets) — **11 lemmas total (7 ACCEPT + 4 REJECT).** Dafny's real capture reads `22 verified, 0 errors` — confirmed empirically (`--progress Symbol`) that this counts roughly 2 verification tasks per lemma, not 1:1; several of this repo's own docs previously misread that figure as "22 lemmas," corrected 2026-07-10 (see this section's own narrative below for the full account). Not exhaustive by design — restating all 60 pinning clauses as separate lemmas would be near-pure duplication, since each `ensures` clause already is its own cell's ACCEPT proof; the STP suite adds value on top of that (worked-example continuity, safety-critical REJECT coverage), not underneath it. |
| Phase E Gate C3 — `drug_interaction_checker.dfy` spec lint | **BUILT 2026-07-10 — extended the shared vector-1 translator for real, not just applied it** | Vector 1 (`check_precondition_satisfiability`) on `CheckInteraction`'s precondition **refused outright before this gate was built**: `requires !(doac == Apixaban && ...)` compares `doac`/`agent` directly, and both are Dafny `datatype`s (`DOAC`, `Agent`) — a type `evidence/dafny_spec_lint.py`'s translator had never needed to model, since renal_adjustment's own Gate C3 gap (a datatype parameter unreferenced by its precondition) never required actually representing one. Genuinely different, harder gap. **Fixed**: `_parse_enum_datatypes` (new) finds every `datatype Name = C1 \| C2 \| ...` declaration whose constructors are ALL zero-argument (multi-line declarations handled — confirmed against `Agent`'s own multi-line form) and `build_symbol_table` now represents each as a Z3 `EnumSort`, with constructor names (`Apixaban`, `Rifampicin`, ...) becoming resolvable symbols the same way `true`/`false` already did — no parser changes needed. A parameterized constructor (`InteractionResult(outcome: ..., direction: ...)`) is still refused, unchanged — `EnumSort` can't represent fields at all. **A second, independent bug caught while building the test suite, not by inspection**: Z3 registers `EnumSort` names globally per context, not per call — two separate `build_symbol_table()` calls modeling a same-named type (a real collision hit by two of this session's own test fixtures, both named `Formula`) raised `enumeration sort name is already declared`. Fixed with a monotonic per-call tag on the registered sort name. Verified against the real spec: `CheckInteraction`'s precondition is `sat` (real Z3 model: `agent = Naproxen, doac = Dabigatran`); vector 2 flags all 60 pinning `ensures` clauses (expected — same "exhaustive, mutually-exclusive dispatch" pattern already established for `renal_adjustment`'s `GStage`/`SelectFormula`, independently backed by Gate C4's real STP proofs, not just asserted benign). 5 new tests in `tests/test_dafny_spec_lint.py` (the extension itself) + 3 in `tests/test_drug_interaction_checker_spec_lint.py` (the real-spec application, mirroring `test_renal_adjustment_spec_lint.py`'s pattern) — one pre-existing test (`test_referenced_unsupported_type_parameter_still_refuses`) updated in place: its original fixture (a simple two-constructor enum) is now a *supported* case, not a refused one, so it was rewritten to use a parameterized constructor instead, preserving the original regression-protection intent. Vector 3 unaffected (already universal, confirmed working at Gate C1). Vector 4 unchanged, still BLOCKED. **Follow-up 2026-07-10**: Gate C5's mutation testing of this same spec found and fixed a real crash bug in this translator's `_apply_cmp` (ordering operators on `EnumSort` operands raised a raw Python `TypeError` instead of refusing cleanly) — see the "Phase E Gate C5" row below for the fix. |
| Phase E Gate C2 — PROVEN exclusivity, confirmed for `drug_interaction_checker` | **CONFIRMED 2026-07-10 — no new gap, first real generalization test since `dosage_calculator`** | `evidence/render/matrix_variants.py::dafny_record()`/`assert_no_realized_proven` (ruling R3) had never been exercised against an independently-authored spec's real capture before — `renal_adjustment` never reached this point (no `metadata.yaml` was ever built for it, so its captures never flowed through this binder at all). Run for real against `drug_interaction_checker`'s actual committed capture (not a synthetic fixture): `dafny_record()` produces a genuine `{"method": "dafny", "strength": "PROVEN", "verifier_completion_status": "completed"}` record, exercising both of its documented gates for real — Gate C3 vector 1 (now able to model `CheckInteraction`'s datatype comparisons, per the same-day Gate C3 extension) and Gate C1's false-zero guard. `assert_no_realized_proven` accepts the real record cleanly. Two negative-case checks confirm R3 still doesn't just trust `dafny_record()`'s own diligence, per that function's own documented claim — a hand-tampered copy of the same real record with `method="crosshair"` and another with `verifier_completion_status="incomplete"` are both independently refused, matching the exact assertion messages the generic `test_proven_exclusivity.py` fixtures already established, now confirmed against this example's own real record shape rather than only a synthetic one. 4 new tests, `tests/test_drug_interaction_checker_dafny_wiring.py` — deliberately narrower in scope than `test_dafny_wiring.py` (which tests the full `metadata.yaml`/`build_matrix()`/CLI/fact-equality pipeline): this example has no traceability matrix yet (Phase 2, not Phase 3), so there's no full pipeline to test against, only the binder itself — a real, honest scope boundary, not an oversight. |
| Phase E Gate C5 — `drug_interaction_checker.dfy` mutation testing | **BUILT 2026-07-10 — found and fixed a real crash bug in Gate C3's own extension, then 7 real survivors, all explained** | 962 mutants (ROR/LOR/COI against `CheckInteraction`'s one `requires` clause and 60 `ensures` clauses; AOR and LVR both confirmed contributing **zero** mutants — no arithmetic operator or numeric literal anywhere in this spec, checked not assumed). **A real crash, not a Dafny finding, caught mid-run**: a ROR mutant introducing `<=`/`>=` between two datatype (`DOAC`) operands crashed `evidence/dafny_spec_lint.py`'s Z3 translator with a raw Python `TypeError` ("'<=' not supported between instances of 'DatatypeRef' and 'DatatypeRef'") — Z3's Python bindings don't overload ordering operators for `DatatypeRef`. Fixed in that module (`_apply_cmp` now checks `z3.is_arith` before applying `LE`/`GE`/`LT`/`GT`, refusing cleanly instead of crashing) before the mutation run could even complete — see the standalone entry below. **Final real run: 962 mutants — 564 killed, 389 filtered_static, 7 survived, 2 unclassifiable.** The 2 unclassifiable are genuine Dafny type errors (`<=`/`>=` between two `DOAC` values: "arguments to <= must be of a numeric type... instead got DOAC and DOAC") — a materially different failure mode from `renal_adjustment`'s own unclassifiable case (a parser ambiguity, not a type error) — while `<`/`>` between datatype values DO type-check (Dafny accepts them for any datatype; for a flat, non-recursive enum Z3 has no axiom pinning down what the relation means, genuinely unconstrained rather than "always false" — an earlier draft's prediction that all such mutants would be trivially killed was wrong, corrected in `run_mutation_suite_ddi.py`'s own comments rather than silently rewritten). **All 7 survivors fall into two categories, both already-established patterns from `renal_adjustment`'s own Gate C5, not a new class of finding:** (A) 4 survivors mutate the one `requires` clause's `doac == Apixaban` comparison (`!=`, `<`, `>`, and one LOR `&&`→`\|\|`) — none of the 60 `ensures` clauses makes any claim about the `(Apixaban, {Rifampicin, Carbamazepine, Phenytoin, Phenobarbital})` region specifically, so no proof depends on the exact shape of this exclusion ("requires-clause weakenings not load-bearing," `renal_adjustment`'s own category 2). (B) 3 survivors mutate the `(Dabigatran, SSRIOrSNRI, !hasOtherBleedingRiskFactors)` ensures clause's `doac == Dabigatran` antecedent (`!=`, `<`, `>`) — `Caution`/`BleedingRisk` is already separately guaranteed for `Apixaban`/`Edoxaban`/`Rivaroxaban`+`SSRIOrSNRI` by three other, unconditional ensures clauses, confirmed directly against the real spec text, not just argued — so the consequent holds regardless of what this specific antecedent's mutation matches ("a structural blind spot against guard-style `==>` clauses whose consequent happens to be broadly true," `renal_adjustment`'s own largest category, 39 of 51). 4 new tests, `tests/test_drug_interaction_checker_mutation_report.py`, pinning the exact counts and asserting both survivor categories directly against the real spec text (not just the report), mirroring `test_renal_mutation_report.py`'s discipline. |
| Phase E Gate C6 — `drug_interaction_checker.dfy` NL-dialogue confirmation | **BUILT 2026-07-10 — genuinely extended the shared summary generator, a different call than renal_adjustment's own equivalent gap** | `evidence/dafny_nl_summary.py::summarize_method` refused outright on first attempt: `CheckInteraction`'s one `requires` clause spans three physical lines — the first genuinely multi-line clause this repo has pointed the summary generator at (every clause in `dosage.dfy`/`renal_adjustment.dfy` happened to be one line). `renal_adjustment` hit an equivalent gap for two `ensures` clauses in `AssessRenalFunctionFromInputs` and that time the call was to **reformat** them to single-line rather than extend the tool ("a formatting choice that was mine, not a genuine spec need") — this time the call went the other way, for a concrete reason: this spec already had committed Gate C1/C4/C5 captures bound to its current formatting, so a cosmetic reformat would have meant re-running and re-committing all three for a change with no semantic content. **Fixed**: `_extract_annotated_clauses` now accumulates a clause across multiple physical lines, ending accumulation at a blank line, a standalone `//`-comment line, or the next clause keyword — so a free-floating block comment between two clauses (this spec has several) is never misattributed as either clause's citation. The original single-line regex (`_CLAUSE_LINE_RE`) is preserved unchanged and still exported, since `evidence/dafny_mutate.py::_locate_clause_sites` imports it for a different purpose (byte-precise single-line mutation-site offsets) that this extension didn't need to touch. The existing safety net is unchanged in spirit: `summarize_method` still cross-checks its line-based extraction against `evidence.dafny_spec_lint`'s canonical multi-line-capable extractor and refuses (`SystemExit`, Tier 1) on any mismatch — a comment sitting on its own line *inside* a multi-line boolean expression (as opposed to between two clauses) still correctly refuses, since that shape is genuinely ambiguous, confirmed by a new regression test. Verified end-to-end against the real spec: all 60 `ensures` clauses and the one multi-line `requires` clause reconstruct byte-for-byte correctly, none dropped or truncated. **A real, notable fact this summary surfaces, not a defect**: none of `CheckInteraction`'s 60 `ensures` clauses carry an inline `// REQ-DDI-*` citation, unlike `dosage.dfy`/`renal_adjustment.dfy`'s per-clause style — this spec is validated against its source as a whole lookup table (Gate 1a/1c), not REQ-ID by REQ-ID, so every `*(no requirement cited)*` in the generated summary is accurate, not a gap. 3 new/changed tests in `tests/test_dafny_nl_summary.py` (one obsolete blanket-refusal test rewritten in place to reflect the new correct behavior, preserving its original regression-protection intent; one new test for the still-refusing mid-clause-comment case; one new end-to-end test against the real committed spec). Presented for sign-off in `nl_confirmation_drug_interaction_checker_dfy.md` — **confirmed by Steven the same day**, closing Gate C6 for this example (see the standalone follow-up entry below: the sign-off itself caught and fixed a real doc-accuracy bug in the sign-off document's own text before the decision was recorded). 190 tests pass (up from 188). |
| Phase 3 — evidence packaging, `renal_adjustment` and `drug_interaction_checker` | **BUILT 2026-07-11 — found and fixed three real gaps in shared code, none worked around locally** | `dosage_calculator`'s Phase 3 pipeline (`metadata.yaml` → `evidence.cli build` → `traceability_matrix.a.json/.md`) had never been pointed at a Dafny-only metadata file (zero crosshair/concrete_test evidence). Three real, generally-applicable gaps found: (1) `evidence/cli.py`'s `--manifest`/`--concrete` were hard-required, and `evidence/render/matrix_variants.py::derive_bounds_block()` unconditionally demanded a crosshair manifest's `effective_bounds` even when nothing in the metadata references crosshair evidence at all — fixed by treating `manifest=None`/omitted `--manifest` as a legitimate "no crosshair evidence declared" state, mirroring `dafny_store`'s own already-established `None` convention exactly, rather than fabricate fake bounds data (which would have falsely implied a search happened); `--concrete` defaults to an honest, real `{"cases": []}` instead, since an empty test list is a genuine state, not a fabrication, unlike invented bounds would be. `evidence/conflict.py::run_conflict_gate` skips `symbolic_binding_conflicts` entirely when `manifest is None`, same pattern. (2) The schema's `toolchain.crosshair_bounds` was unconditionally required in all three schema files (`metadata.schema.a/b/c.json`) even for a metadata file with no crosshair evidence — relaxed to optional. (3) The schema's `id` pattern (`^REQ-[A-Z0-9-]+$`) rejected `REQ-RENAL-1a` — the exact same lowercase-suffix gap already fixed once in `dafny_nl_summary.py`'s `_REQ_ID_RE` (2026-07-08), now found independently in the schema itself and fixed the same way (`[A-Za-z0-9-]`). **A fourth, independent bug fixed in the same pass, not required by the two new examples but found while reading the code closely**: `symbolic_binding_conflicts` never skipped a `.dfy`-targeted `implementation` the way `_declared_concrete_bindings` already did — a real gap for any future mixed example (some requirements crosshair-backed, others dafny-backed) that would have false-flagged a dafny requirement's implementation against the crosshair manifest's target file. Every change verified against zero regression: `dosage_calculator`'s real artifacts regenerated before and after each change and diffed byte-for-byte (timestamps aside) — confirmed identical every time. `renal_adjustment`: `metadata.a.yaml`, 9 requirement rows — REQ-RENAL-1/1a/2/5 with real dafny evidence (`AssessRenalFunction` dual-cited to both REQ-RENAL-1 and REQ-RENAL-2, mirroring the `.dfy` file's own inline citation; the unnumbered CrCl-computation functions attached under REQ-RENAL-2 rather than given a new ID), REQ-RENAL-3/4/6/7 as honest GAP rows (`intended_method: PROVEN` — real future Dafny-formalization candidates), REQ-RENAL-8 as a GAP row with `intended_method: DECLARED` (a permanent trust boundary, never a future proof target — genuinely different from the other four gaps; its provenance question is parked pending real-world process data Steven is gathering, and will resolve to a DECLARED process fact, not a proof). `drug_interaction_checker`: `metadata.a.yaml`, 6 requirement rows — REQ-DDI-1/2/3/4 all sharing the SAME one `dafny_captures_index.json` entry (the first many-requirements-to-one-proof binding this repo's matrix binder has ever been exercised against — confirmed working, not assumed), REQ-DDI-5/6 as honest GAP rows. Both matrices pass `assert_no_realized_proven` (R3). 15 new tests, `tests/test_renal_adjustment_matrix.py` (9) and `tests/test_drug_interaction_checker_matrix.py` (6) — 205 tests pass (up from 190). |
| Phase E REQ-DDI-5/REQ-DDI-6 — indication axis + numeric dose-reduction targets | **BUILT 2026-07-12 — both requirements built for real, all six gates re-run, no GAP rows remain in this example. Gate C6 sign-off NOT yet closed for either requirement — see "Gate C6 review, 2026-07-13" row below.** | Preceded by full source verification (2026-07-12, earlier the same day): an externally-supplied scoping document's claims were checked against `sources/sps-doac-interactions-2024.md` via `evidence/citation_gate.py` (including a deliberate false control, correctly NOT_FOUND) plus three newly-fetched, verbatim-verified, archived primary sources (both eMC apixaban SmPCs, the MHRA DSU renal table, the US FDA ELIQUIS label as a non-UK contrast) — confirmed both requirements are buildable from public UK sources before any code was written. **REQ-DDI-5**: added `datatype TreatmentIndication = AFStrokePrevention \| RecurrentVTEPrevention`, deliberately closed to exactly the two indications the interaction source names for these cells (not a third VTE-prophylaxis case that exists only in the posology sources, with no stated interaction outcome here — a real scoping decision, confirmed with Steven via AskUserQuestion before building). Added as `CheckInteraction`'s fourth parameter; since both named indications give the identical sourced outcome, every constructible `TreatmentIndication` value is now provable, so the function's previous `requires` clause (excluding the four apixaban+inducer cells) is removed entirely, not narrowed — `CheckInteraction` is now total. Four previously-unreachable match arms become real, reachable arms; 4 new `ensures` clauses added (60→64). **REQ-DDI-6**: new companion function `DoseReductionTargetMg(doac, agent): int`, `requires`-gated bare-`int` (matching `renal_adjustment.dfy`'s `SelectFormula`/`AssessRenalFunction` precedent, deliberately not introducing this repo's first `Option<int>` pattern — resolved in `PHASE1_PLAN.md`'s "Still open" section), pinning the five real sourced figures: Dabigatran+Verapamil→110mg, Edoxaban+{Dronedarone, ErythromycinSystemic, Ketoconazole, Ciclosporin}→30mg each. Apixaban never appears in this function's precondition — a direct, confirmed consequence of `CheckInteraction` never producing `DoseReductionAdvised` for apixaban anywhere in its match arms, not a hand-written exclusion. **A real engineering boundary named, not fixed**: `evidence/dafny_mutate.py`'s `generate_aor_mutants`/`generate_lvr_mutants` body-scanning mode refused outright on `DoseReductionTargetMg`'s body (a `//` comment on the wildcard match arm — "refusing to locate mutation sites rather than risk a misaligned offset or a comment slash mistaken for division"); clause-level LVR alone (omitting `function_name`) gave 10 real mutants covering all 5 pinned figures exactly, all killed — equivalent coverage without new shared-module engineering, named in `run_mutation_suite_ddi.py`'s own docstring rather than silently worked around. All six gates re-run for real for both requirements: **C1** re-verified clean (`2 verified, 0 errors` across both functions, one capture). **C6** two new addenda drafted in `nl_confirmation_drug_interaction_checker_dfy.md`, each explicitly marked "not yet confirmed — pending review," never self-signed-off in the same pass that generated them. **C4** `drug_interaction_checker_stp_suite.dfy` gained 6 new lemmas (2 ACCEPT + 1 REJECT per requirement), all 11 pre-existing `CheckInteraction` calls updated with a placeholder 4th argument; `20 verified, 0 errors`. **C3** spec lint re-run: `TreatmentIndication` got `EnumSort` treatment automatically (no code change needed, confirmed empirically); weak-postcondition count bumped 60→64; `DoseReductionTargetMg`'s precondition confirmed satisfiable. **C5** mutation testing restructured to a multi-function loop (`run_mutation_suite_ddi.py`'s `FUNCTIONS` tuple, mirroring `run_mutation_suite_renal.py`'s established precedent) — first real run: **1178 mutants — 634 killed, 472 filtered_static, 68 survived, 4 unclassifiable.** `CheckInteraction`'s own 31 survivors are byte-for-byte the same set REQ-DDI-5 alone already established (confirmed, not assumed): 28 are a new category (REQ-DDI-5's `treatmentIndication` disjunction — a redundant guard, since both named indications give the identical outcome and the match arm doesn't inspect the value at all for these cells), 3 are the pre-existing SSRIOrSNRI antecedent category (unaffected). `DoseReductionTargetMg` contributed 37 new survivors (7 requires-clause + 30 ensures-clause guard-antecedent mutations, same "weakening not load-bearing" shape `CheckInteraction`'s own now-removed requires clause used to fall into — confirmed via byte-identical-consequent check, not assumed) and all 4 unclassifiable results (a real, expected REAPPEARANCE of the datatype-vs-datatype ROR type-error category REQ-DDI-5 had made disappear entirely, since `DoseReductionTargetMg`'s new requires clause reintroduces a `doac`/`agent` datatype comparison — structural, not a regression). All 10 LVR mutants on the five pinned mg figures killed, none survived — proof the figures are exact, not just roughly right. **Refined the same day via a Qodo code-review finding on PR #39**: the wildcard match arm's bare `0` literal (a reliability risk if this spec were ever compiled and called from unverified code with the precondition violated) was replaced with `case _ => (assert false; 0)`, verified empirically to still compile and verify cleanly. This had a real, positive side effect on Gate C5: the 7 requires-clause ROR survivors are now ALL KILLED — a mutated requires clause can admit a pair that falls into the wildcard arm, and Dafny can no longer prove `assert false` there, so the previously-silent "requires-clause weakening not load-bearing" category is now a genuine, caught verification failure. **Re-run: 1178 mutants — 641 killed, 472 filtered_static, 61 survived, 4 unclassifiable** (`filtered_static`/`unclassifiable` unchanged, confirming a real strengthening, not a shift in unrelated mutant classes); `DoseReductionTargetMg` now contributes exactly 30 survivors (ensures-only). **Phase 3 regenerated**: `metadata.a.yaml` gained real `implementation`/`evidence` blocks for REQ-DDI-5 (reusing the `CheckInteraction` capture, a fifth requirement sharing one proof) and REQ-DDI-6 (binding `DoseReductionTargetMg`, the first time this repo's matrix binder has bound two different Dafny methods from the same spec file across two requirements in one metadata file); `dafny_captures_index.json` gained a second key pointing at the same physical capture files. `traceability_matrix.a.json`/`.md` regenerated via the real CLI (not hand-edited) — all 6 rows now `intent_ok: true` with real `PROVEN` evidence, no GAP rows remain in this example; `assert_no_realized_proven` re-checked directly. Test suite updated in place across `tests/test_drug_interaction_checker_spec_lint.py`, `tests/test_drug_interaction_checker_mutation_report.py` (rewritten twice, once per requirement — final: `test_report_total_and_outcome_counts`, two named survivor-category tests, an unclassifiable-category test, `test_all_survivors_are_accounted_for_by_the_three_named_categories`), `tests/test_dafny_nl_summary.py` (the now-obsolete "multiline requires clause" test rewritten to assert "(none declared)," since REQ-DDI-5 removed the clause it was testing — the underlying multi-line-reconstruction capability stays separately protected by its own synthetic fixture test), and `tests/test_drug_interaction_checker_matrix.py` (the old "deferred requirements render as honest gaps" test replaced with real PROVEN-row assertions per requirement plus a no-GAP-rows-remain check). |
| Gate C6 review, 2026-07-13 — `drug_interaction_checker` REQ-DDI-5/REQ-DDI-6 sign-off document | **ALL FOUR FINDINGS RESOLVED — sign-off document ready for Steven's actual review, which still hasn't happened** | A pre-sign-off review of `nl_confirmation_drug_interaction_checker_dfy.md`'s two 2026-07-12 addenda (deliberately conducted before Steven's confirmation) found three defects, each independently re-verified against the real committed artifacts before acting, not accepted on the review's word alone. **Fixed**: (1) the addenda's own "Summary presented" block was still the stale 2026-07-10 generation (3-arg `CheckInteraction`, its now-removed `requires` clause, 60 not 64 postconditions, no `DoseReductionTargetMg` at all) — a reviewer following Addendum 1's own instruction to check "Postcondition 27/48/52/56" against it would land on four unrelated pre-REQ-DDI-5 clauses. Fixed by regenerating for real via `evidence.dafny_nl_summary.summarize_method` and inserting a new dated "Summary presented, regenerated 2026-07-13" block for both functions; the stale block is marked superseded and left as a frozen historical record (matching `GATE_1C_AUDIT.md`'s convention), not rewritten. Confirmed the existing postcondition numbering (27/48/52/56) Addendum 1 already cited matches the real regenerated summary exactly — no renumbering needed. (2) Addendum 2 never mentioned the Qodo-driven `assert false` fix to `DoseReductionTargetMg`'s wildcard arm (PR #39, merged) — the function's most recently changed line, with the largest measured effect on Gate C5's own results (7 survivors converted to kills). Fixed by adding it as Addendum 2's item 5. **Left open, deliberately not resolved here**: `sources/sps-doac-interactions-2024.md` lines 57-65 state the dabigatran+verapamil 110mg figure applies "for AF-stroke-prevention and DVT/PE-prevention-and-treatment indications specifically" — the source treats this row as indication-scoped, the same shape REQ-DDI-5 was built to model for the apixaban+inducer rows. But the archived source file's own editorial layer immediately dismisses that scoping in the same sentence ("this doesn't need an indication axis to model correctly... the dose reduction just applies whenever dabigatran is used for either") — a design judgment baked into `sources/`'s own verbatim-extraction layer at archive time, not itself a further primary-source quote, and REQ-DDI-6 faithfully inherited it: `DoseReductionTargetMg` takes no `treatmentIndication` parameter and proves the 110mg figure unconditionally, a claim provably wider in scope than the sentence it cites. Independently re-verified directly against the archived source text 2026-07-13, not accepted on the review's word — the quoted text and the editorial dismissal both appear exactly as described. **Not currently a soundness bug**: `TreatmentIndication` has only two constructors and both are within the source's stated scope for this row, so the proof is correct for every currently-representable input — but nothing in `DoseReductionTargetMg`'s signature, clauses, or comments records that an indication axis was ever considered and dropped for this cell, so the gap is invisible rather than named. Whether `RecurrentVTEPrevention` (named for the rifampicin row's "recurrent deep vein thrombosis (DVT) and pulmonary embolism (PE)" prevention) actually contains the verapamil row's differently-worded "DVT/PE-prevention-and-treatment" scope is a real clinical-licensing question — dabigatran (Pradaxa) is UK/EU-licensed for at least three distinct indications (NVAF stroke prevention; DVT/PE treatment-and-recurrence-prevention; primary VTE prophylaxis after elective hip/knee replacement, a once-daily regimen structurally different from the twice-daily rule the 110mg figure presupposes) — requiring primary-source verification (dabigatran's own SmPC/EMA product information, archived under `sources/` per the established convention) before it can be answered either way. Gate C6 is not closed for REQ-DDI-6 (nor, pending the same verification, definitively closed for REQ-DDI-5's own scope choice) until this resolves. **Primary source fetched and archived the same day**: `sources/emc-smpc-dabigatran-indications-2025.md` (Pradaxa eMC SmPC, both 110mg and 150mg products, revision date 16 January 2025). Confirms two things directly: `RecurrentVTEPrevention` DOES correctly cover the verapamil row's "DVT/PE-prevention-and-treatment" phrase (both it and the rifampicin row's phrasing refer to the same single eMC-licensed indication category, not two different ones — no new constructor needed for that specific naming worry); and dabigatran genuinely has a third, current, UK-licensed indication (orthopaedic VTE prophylaxis, once-daily regimen) that `TreatmentIndication` doesn't represent, confirmed source-silent for verapamil (the real SmPC states the dose-reduction instruction only under the two twice-daily indications). **Decided by Steven, via `AskUserQuestion`, not resolved by an assistant**: add the third constructor now, and leave the merged REQ-DDI-6 matrix row as its prior PROVEN state until the fix landed rather than caveat it in the interim. **Implemented and re-verified the same day**: `TreatmentIndication` gained `OrthopaedicVTEProphylaxis`; `DoseReductionTargetMg` gained a `treatmentIndication` parameter and an indication guard on its Dabigatran+Verapamil cell (`requires`/`ensures` both updated); a new STP lemma (`DoseTargetDomainAgreesWithCheckInteraction`, `drug_interaction_checker_stp_suite.dfy`) proves this function's domain exactly equals "CheckInteraction says DoseReductionAdvised" minus the SSRI exclusion minus the new orthopaedic-indication exclusion — apixaban's absence and the new orthopaedic exclusion are both proven theorems now, not grep-verified observations (Fix 2B). **A second, independent finding surfaced while building this, caught before trusting the first re-run**: writing the new clauses across multiple physical lines silently truncated `evidence/dafny_mutate.py`'s clause-site locator at the first line — a real regression in mutation-testing coverage (the Edoxaban disjuncts and the ensures clause's own consequent were entirely missing from requires-clause coverage), not caught by Dafny (still verified clean) or by the pinned-count-only pytest assertions. Fixed by reformatting both clauses to single lines, matching `renal_adjustment.dfy`'s own established precedent for this exact class of gap, rather than extending the tool. All six gates re-run for real: **C1** `2 verified, 0 errors`; **C4/STP** `23 verified, 0 errors` (up from 20); **C3** precondition still satisfiable, weak-postcondition counts unchanged; **C5** real run (after the truncation fix): **1250 mutants — 668 killed, 482 filtered_static, 74 survived, 26 unclassifiable** — every count's jump reflects real, previously-missing coverage of the full 5-disjunct requires clause and the full indication-guarded ensures clause, not a new class of finding (CheckInteraction's own 31 survivors unchanged; DoseReductionTargetMg's 43 survivors and 26 unclassifiable results are all the same two already-named categories — guard-antecedent-not-load-bearing, datatype-ordering type error — now correctly counted at full scale). Phase 3 regenerated via the real CLI: all 6 rows remain `PROVEN`, no GAP rows. `tests/test_drug_interaction_checker_mutation_report.py` rewritten to match. Full account: `nl_confirmation_drug_interaction_checker_dfy.md`'s "Addendum 3" (now closed out — the sign-off document itself states it's ready for Steven's actual review) and `sources/emc-smpc-dabigatran-indications-2025.md`. |

## Gate 2 — CONFLICT rule: Types 1 and 2 BUILT (2026-07-06)

Blocked since Turn B4: the term appears nowhere in
PayloadGuard-Evidence-Blueprint-1 (0 case-insensitive occurrences,
committed copy in-repo) nor in SYSTEM_BLUEPRINT.md (a single to-do
mention, not a definition). Per standing rule, semantics were not
inferred from the name — the definition below was drafted against two
candidate test cases from the 2026-07-05 roadmap, refined in discussion
to add a third, and explicitly ratified by Steven before being recorded
here as decided (not just proposed).

### Definition

**Precondition (shared by both sub-types):** CONFLICT is only checked
between two claims that purport to describe **the same thing** — the
same `(requirement_id, scope)` *and* the same underlying verification
act (same tool, same target, same invocation). Two independent evidence
types legitimately bound to one requirement — e.g. REQ-GIP-1-4-12's
`kernel_scope` carrying both a CrossHair capture *and* a concrete test —
are not comparable under this rule; they corroborate, they don't
compete. That shape is normal and stays normal (it's exactly how variant
A's `evidence[]` array is meant to work).

- **Type 1 — Binding-identity conflict (dual-authorship).** Two claims
  about the *same declared binding* disagree on what physical target it
  points to: a top-down, metadata-authored contract says `(file F,
  method M)`; a bottom-up, evidence-store-carried assertion says `(file
  F', method M')`, and F≠F' or M≠M'. This is Gate 4's exact
  cross-check trigger.
- **Type 2 — Evidence-outcome conflict (result inconsistency).** Two
  claims agree on target identity — same tool, same file/method, same
  invocation/bounds — but disagree on what that identical verification
  act produced (one manifest reports exit 0/no counterexample, another
  manifest for the same run reports exit 1/counterexample).

Both types are Tier-1 hard generation failures per Gate 4's decision —
they differ only in which half of the `(identity, outcome)` pair
disagrees. Neither type is triggered by `intent_ok` mismatches
(declared `intended_method` vs. realized strength): that's one binding
compared against its own stated aspiration, not two independent claims
about the same fact, and already has its own mechanism (R1). CONFLICT
must not be reinterpreted to cover it.

### Test cases

1. **Positive, Type 1 (identity mismatch).** Metadata declares REQ-X
   bound to `dosage.py::calculate_hourly_dose`; the evidence-store
   entry for that same binding actually targets
   `dosage_broken.py::calculate_hourly_dose`. Target identity differs →
   **CONFLICT**. This is the original Gate 4/roadmap trigger case.
2. **Negative (GAP, not CONFLICT).** REQ-GIP-1-4-12's `system_scope` has
   zero claims — no evidence exists, rendered as an explicit named GAP.
   The precondition (two claims about the same thing) is never met, for
   either type. **Not a CONFLICT** — this is a documented absence, and
   must keep rendering as a GAP.
3. **Positive, Type 2 (outcome mismatch) — the subfinding this
   refinement was added to cover.** Not a hypothetical abstraction: this
   repository already documents that CrossHair's model-fidelity channel
   is "unreliably sampled and sharply complexity-dependent" (the Sample
   C / overflow-probe honesty exhibits prove the *same* invocation can
   land differently depending on internal solver state). If a future
   re-capture of the identical target/tool/bounds as an already-committed
   manifest ever produced a different exit code — one manifest says
   no-counterexample, a second manifest for the same target says
   counterexample-found — that's Type 2, and nothing catches it today.

### Status

**Type 1 — built (2026-07-06).** `evidence/conflict.py`:
`concrete_binding_conflicts()` cross-checks metadata's top-down concrete
bindings (variant A's per-requirement `evidence` list; variant B's
shadow-pseudo-requirement `implementation`-suffix form) against
`concrete_results.json`'s self-declared `requirement_id`;
`symbolic_binding_conflicts()` cross-checks each requirement's declared
`implementation` file against the crosshair manifest's actual `target`.
`run_conflict_gate()` combines both and raises on any mismatch — Tier 1,
matching the fact-equality and structural-PROVEN gates' behavior. Wired
into `generate_artifacts.py` as stage 3 (runs after capture integrity,
before regeneration), checked against all four metadata files (24
bindings checked on the current committed dataset, 0 conflicts).

**Variant C's asymmetry closed (2026-07-06).** Gate 4 had flagged that C
declared no top-down concrete binding at all, so Type 1 had nothing to
compare there. Per Gate 4 option 3, `metadata.schema.c.json` gained an
optional `evidence` property (identical shape to variant A's) and
`metadata.c.yaml` now declares it on all three requirements, matching the
real bindings already in `concrete_results.json`. This is
cross-checking-only: `build_matrix_variant_c` still never reads
`evidence` — C's actual binding stays evidence-store-carried, unchanged
(confirmed: regenerating C's artifacts after this change produced a
byte-identical diff except `generated_utc`). C now contributes 7 checked
bindings (4 concrete + 3 symbolic) instead of 0.

**Type 2 — built (2026-07-06).** `evidence/conflict.py`:
`outcome_conflicts()` groups manifests by identity (tool, target,
enforced `per_condition_timeout_s` — deliberately excluding the raw
argv, which embeds an environment-specific absolute path, and
`started_utc`, which never matches); any group reporting more than one
distinct `exit_code` is a conflict. `run_outcome_gate()` raises on any
mismatch. Wired into `generate_artifacts.py` as stage 4, run against all
four committed manifests (Sample A, Sample B, the naive-widening exhibit,
the overflow probe): 4 manifests, 4 distinct verification acts, 0
conflicts — a real, honest zero, since each committed manifest targets a
genuinely different file and none collide. `tests/test_conflict_check.py`
covers the real-data clean pass plus two synthetic cases (a positive
mismatch, and a same-outcome-different-target case confirming Type 2
doesn't over-fire on unrelated targets) — matching the established
convention (`test_single_evidence_type.py`) of driving real code with an
in-memory fixture when the committed dataset can't exercise a property.

`tests/test_conflict_check.py` now has 11 tests total, covering all
three ratified test cases across all three metadata shapes plus Type 2.

### Vocabulary-agnostic binder — Step 2 done (2026-07-06): cut over, with an explicit fallback

The remaining piece of Gate 2 — one implementation driving all four
schema-variant shapes, replacing `generate_matrix_a.py` / `_b.py` /
`_c.py` — is a genuine architectural refactor (unlike Types 1/2, which
were additive extensions of an existing pattern), so it's being done in
its own small steps rather than folded into the CONFLICT work above.

**What was built:** `evidence/render/matrix_variants.py` gained
`build_matrix(variant_key, metadata, manifest, concrete_store,
tool_versions=None)` — a single entry point replacing
`build_matrix_variant_a/b/c`. It is a **literal extraction**, not a
reimplementation: every existing variant's record-assembly logic
("binder": `_bind_declared` for A, `_bind_shadow` for B,
`_bind_self_describing` for C) and row-rendering logic ("shape":
`_shape_evidence_array`, `_shape_flattened_shadow`,
`_shape_method_partitioned`) was lifted verbatim into named functions,
dispatched through a declarative table (`_VARIANT_SPECS`) instead of
three separate top-level functions. Binding strategy and row shape are
split as the two real axes of variation, so a future fifth shape can
reuse an existing strategy (or vice versa) instead of requiring a whole
new function.

**Correctness proof:** `tests/test_binder_equivalence.py` (5 tests) runs
both the old function and `build_matrix()` against the identical real
committed inputs for all four variant keys, and asserts equality two
ways — dict equality AND `json.dumps()` string equality (the second
catches key-insertion-order drift that dict `==` alone would miss, which
matters for a future generator cutover producing byte-identical files,
not just equivalent-content ones). All pass.

**Step 2 (2026-07-06): cut over.** Steven approved proceeding with an
explicit request to keep a fallback available. `generate_matrix_a.py` /
`_b.py` / `_c.py` now import and call `build_matrix("a"/"b"/"c-symbolic"/
"c-concrete", ...)` instead of the original per-variant functions.
**Fallback, by design, not an afterthought:** `build_matrix_variant_a/b/c`
are deliberately left in `evidence/render/matrix_variants.py`, fully
intact and unused — if a problem with `build_matrix()` ever surfaces,
each generator's import + call can be reverted to the corresponding
original function in one line, or this cutover commit can be
`git revert`ed outright. They are deleted only in a later, separate
cleanup step once the cutover has proven stable — not bundled into the
cutover itself.

**Verification, not assumption:** the full pipeline was re-run end to
end post-cutover, and every regenerated artifact was diffed against the
pre-cutover committed versions — differs only by `generated_utc`, exactly
as the Step 1 equivalence proof predicted. Full suite: 33 passed
(unchanged from Step 1 — this step changed which function each generator
calls, not any logic).

**Step 3 (2026-07-06): fold CONFLICT Type 1 into build_matrix() itself —
and confirm Type 2 has no per-variant home.** Re-examined the plan
before implementing: Type 1 is inherently per-variant (it's about one
metadata file's declared bindings vs. the evidence store), so it fits
naturally inside `build_matrix()`. Type 2 is NOT per-variant — it
compares raw manifests across the whole dataset regardless of which
variant is being built, so folding it into `build_matrix()` would mean
re-running the identical whole-dataset check on every one of the four
variant calls for no reason. It stays a standalone stage, the same way
the fact-equality gate does (both are properties of the artifact/input
*set*, not of any single generation call).

`build_matrix()` now calls `run_conflict_gate(metadata, concrete_store,
manifest)` as its first step, before assembling any record — Tier 1,
and it runs no matter how `build_matrix()` is invoked (full pipeline, a
single generator script run alone, or a test), closing a real gap: Type
1 previously only ran inside the `generate_artifacts.py` pipeline stage,
so running e.g. `generate_matrix_a.py` alone would have bypassed it
entirely (the individual generators are documented to bypass the
fact-equality gate the same way — Type 1 had the identical exposure
until now).

The frozen base matrix (`metadata.yaml`, via `manual_matrix.py`, ruling
R2c) never calls `build_matrix()`, so it keeps its own explicit check:
`generate_artifacts.py::stage_base_conflict_check` (renamed from the
old, broader `stage_conflict_check`, now scoped to just the base file —
3 symbolic bindings, since base declares no concrete evidence at all).

**Proven, not assumed:** `tests/test_conflict_check.py` gained
`test_build_matrix_folds_in_type1_check`, which drives `build_matrix()`
directly with a conflicting in-memory fixture and confirms it raises
before assembling a single record — proof of the fold-in itself, not
just of the underlying check function. Full pipeline re-run end to end;
every regenerated artifact still differs only by `generated_utc`. Suite:
34 passed (33 prior + 1 new).

**Note on the fallback:** `build_matrix_variant_a/b/c` (Step 2's
fallback) do NOT have Type 1 folded in — only `build_matrix()` does. If
the fallback is ever used in an emergency, Type 1's per-call check is
temporarily lost along with it; that's an accepted, documented tradeoff
of restoring known-good behavior quickly, not a silent regression.

**Still open:** deleting the fallback functions once the cutover has
proven stable (Step 4) — see "What's left for Gate 2" below.

### CLI — built (2026-07-06)

Requested explicitly before Step 4 (deleting the Step 2 fallback), so
the fallback stays available while new capability lands rather than
being removed first.

`evidence/cli.py`: `python -m evidence.cli build --variant {a|b|
c-symbolic|c-concrete} --metadata PATH --manifest PATH --concrete PATH
[--schema PATH] [--out-json PATH] [--out-md PATH]`. This is the
"vocabulary-agnostic" half of Gate 2 made reachable from outside a
Python script: unlike `generate_matrix_a/b/c.py`, which hardcode paths
to `examples/dosage_calculator`, the CLI takes every input as an
argument, so it can build a matrix for a different device's evidence set
matching one of the four schema shapes, not just the worked example.

- Schema validation runs first (`--schema` defaults to
  `evidence/schema/metadata.schema.<a|b|c>.json` for the given
  `--variant`, overridable for a schema that lives elsewhere).
- `tool_versions` is now keyed by the manifest's own declared `tool`
  field (`manifest["tool"]`) rather than a hardcoded `"crosshair"`
  string — a small genuine generalization, since a future Dafny/Z3
  manifest won't need this CLI changed.
- Tier-1 failures (schema validation, CONFLICT Type 1 — folded into
  `build_matrix()` since Step 3) exit non-zero with a short message on
  stderr, not a raw traceback or (for schema errors) jsonschema's full
  schema dump — an actual bug caught and fixed during this build: the
  first version printed the entire JSON Schema on every validation
  failure; fixed to use `ValidationError.message` instead of `str(e)`.
- JSON prints to stdout when `--out-json` is omitted (composes with
  other tools, e.g. `| jq`); markdown is only ever written where
  `--out-md` explicitly says to, never to stdout — an early version
  printed both JSON and markdown to stdout when no output paths were
  given, producing invalid combined output; caught by
  `tests/test_cli.py` and fixed before commit.

**Proven, not assumed:** `tests/test_cli.py` (10 tests) drives the CLI
via subprocess (the way a real user would invoke it) for all four
variants and asserts the output is byte-identical (timestamp aside) to
the corresponding committed artifact, plus covers both clean-exit error
paths and the stdout/file output modes. Full pipeline re-run
independently confirms the CLI's addition changed nothing about the
existing generator scripts. Suite: 44 passed (34 prior + 10 new).

### Step 4 — DONE (2026-07-06): fallback deleted

Requested last, deliberately after the CLI landed. `build_matrix_variant_a`,
`build_matrix_variant_b`, and `build_matrix_variant_c` are deleted from
`evidence/render/matrix_variants.py` — their shared markdown renderers
(`_markdown_variant_a/b/c`) and helpers stayed, since `build_matrix()`
already used those, not the deleted functions. `tests/test_binder_equivalence.py`
is deleted too: its entire purpose was proving old-function output equals
`build_matrix()` output, which is moot once the old functions don't
exist. `tests/test_single_evidence_type.py` (Gate 5's fixture test) was
migrated from calling `build_matrix_variant_c` directly to calling
`build_matrix("c-symbolic"/"c-concrete", ...)` — it's the one other place
in the suite that had called a fallback function directly. The
comments in `generate_matrix_a/b/c.py` and the module-level banner in
`matrix_variants.py` that described the now-gone fallback were updated
to stop referencing it.

**Verified, not assumed:** full suite (39 passed — 44 minus the 5 deleted
equivalence tests), full pipeline re-run (every regenerated artifact
still differs only by `generated_utc`), and the CLI re-checked
independently against a committed artifact post-deletion, all after the
deletion, not just before it. Git history holds the deleted functions
and test if a fallback is ever needed again — that was the entire point
of doing Steps 2-4 in this order rather than deleting immediately.

**Gate 2 is now structurally complete.** The only open item left
anywhere in Gate 2's scope is the CONFLICT rule's own definition, which
is already ratified (see above) — there is no remaining build work.

## Gate 3 — DECIDED 2026-07-06: stay-CLI (crosshair-tool 0.0.107)

Original investigation (2026-07-05) confirmed against the installed
package: `per_condition_timeout` is CLI-enforceable (already enforced
since Turn 2.0 B1); `max_iterations` is not exposed by the CLI but is
exposed by the Python API; `seed` is hard-coded by the tool. A follow-up
roadmap proposed a corrected seed-override technique and a script to test
it behaviorally rather than assume. That script was run for real — three
more errors turned up only by executing it, and the actual result
contradicts the "pending" framing this gate carried before:

**Corrections found by running the script, beyond the roadmap's own
technique fixes (target function `make_default_solver`, hyphenated Z3
param names):**
1. The roadmap's claimed API call, `AnalysisOptions(max_iterations=...,
   per_condition_timeout=...)`, raises `TypeError: missing 9 required
   positional arguments` on the installed 0.0.107 — `AnalysisOptions` has
   no defaults. `analyze_function`'s real second parameter type is
   `AnalysisOptionSet` (the defaultable/partial sibling), confirmed
   against `crosshair/options.py` and `crosshair/core.py`. This matches
   what the original 2026-07-05 investigation already had right.
2. Importing `analyze_function` from bare `crosshair.core` raises
   `CrossHairInternal("Opcode patches haven't been loaded yet.")` the
   moment `.analyze()` is called — the opcode-level tracing patches are
   only installed as a side effect of importing
   `crosshair.core_and_libs`. Must import from there instead.
3. `analyze_function` alone only parses source into `Checkable` objects
   (one per postcondition); it does not run the solver. Each `Checkable`
   needs `.analyze()` called explicitly to execute the real symbolic
   search and yield `AnalysisMessage`s. The uncorrected script silently
   "passed" in under a second by never calling this — a false read that
   would have looked like a completed test.

**Real result, after all corrections, run twice per target
(`CROSSHAIR_SOLVER_SEED=1` vs `=2`):**
- `dosage.py::calculate_hourly_dose` (Sample A, no counterexample either
  way): both seeds returned two `MessageType.CANNOT_CONFIRM` / "Not
  confirmed." messages at the same two lines — byte-identical.
- `dosage_broken.py::calculate_hourly_dose` (has real counterexamples, a
  stronger discriminator): both seeds returned the exact same two
  counterexamples — `calculate_hourly_dose(1.0, 1.0, 0.5, 0.25)` → `0.5`
  and `calculate_hourly_dose(0.5, 0.25, -0.125, 0.125)` → `-0.03125` —
  matching the values already on file in `raw_crosshair_output_broken.txt`
  under the CLI's own hard-coded seed 42.

**Decision:** stay-CLI. The seed-override patch installs without error
but produced no observable behavioral difference on either target
tested; falling back per the pre-agreed criterion. `seed` remains a
documented tool-version limitation — the declared `seed: 1` in
`metadata.yaml` cannot be demonstrated on 0.0.107, and the tool's own
hard-coded seed is 42 (`crosshair/statespace.py`, `make_default_solver()`
— not `StateSpace.__init__` directly, and the real params are hyphenated:
`solver.set("random-seed", 42)`, `solver.set("smt.random-seed", 42)`).
`max_iterations` is confirmed enforceable via the API
(`AnalysisOptionSet`) independent of this decision, should a future
change revisit the CLI-vs-API tradeoff for reasons other than seed.
Verification script committed at
`examples/dosage_calculator/gate3_seed_patch_test.py`; no re-capture
performed — Gate 1's committed captures are untouched.

**Caveat on strength of evidence:** both test targets have simple,
shallow constraint structure; Z3's random-seed parameter mainly affects
tie-breaking in larger search spaces, so "no observed difference" here is
real but not a proof that the parameter can never matter on any target —
only that it didn't move the needle on the two targets this repository
actually uses. Documented as-is, not oversold. (This same non-determinism
concern is what motivates Gate 2's Type 2 CONFLICT test case above.)

Also flagged and closed as a non-issue: CrossHair's latest *tagged*
GitHub release is v0.0.106, while both the toolchain pin and the actually
installed package are 0.0.107 (`pip show crosshair-tool` confirmed
0.0.107 in this environment) — consistent with each other; a PyPI release
can exist ahead of its git tag.

## Gate 4 — decided: option 3, both models cross-checked (mechanism specified 2026-07-05)

Three options were on file; option 3 is now the decision on record:

1. **Metadata-authored everywhere (A/B model):** the binder consumes only
   bindings declared in metadata; C's evidence-store `requirement_id`
   channel is dropped. Pro: single review surface, authorship errors live
   in one place. Con: evidence stores stop being self-describing;
   concrete evidence must be double-entered (in CASES and in metadata).
2. **Evidence-store-carried everywhere (C model):** bindings live with the
   evidence (each record names its requirement). Pro: no duplication;
   evidence is portable. Con: binding errors move into test/capture files
   that regulatory reviewers are less likely to read; metadata no longer
   shows the full evidence picture.
3. **DECIDED — both, with precedence + cross-check:** metadata
   declarations are authoritative where present; store-carried ids are
   validated against them, and a disagreement is a hard generation
   failure (Tier 1). Keeps A/B's review surface and C's portability while
   turning the asymmetry into a consistency check. This is now backed by
   Gate 2's Type 1 CONFLICT definition, so "disagreement" has a concrete,
   ratified meaning rather than an open semantic question.

**Mechanism (dual-authorship cross-check via verified code-location
match), from 2026-07-05 external research:**
- **Top-down contract:** the system/QA-authored master traceability
  config states "REQ-X is verified by the proof/test at file F, method
  M."
- **Bottom-up contract:** the source-embedded assertion (a decorator,
  structured comment, or in Dafny's case an `ensures`/`invariant` clause)
  states "this method verifies REQ-X."
- **Intersection check:** at generation time, extract both, and flag
  non-compliant if the physical file/method/hash doesn't match between
  them — this is Gate 2's Type 1 CONFLICT, exactly.

Design input from Gate 5 work: the original C builder bound a symbolic
record to every requirement by construction and didn't verify the
requirement's `implementation` against the capture manifest's `target`.
**Status: decision, mechanism, and build all done.** The verification
half (Type 1) is built in `evidence/conflict.py`, folded into
`build_matrix()`. The binding half (whether symbolic evidence binds at
all) was fixed as part of closing Gate 5 (below) — `_bind_self_describing`
now consults the same `evidence` declaration Type 1 checks against.

## Gate 5 — single-evidence-type fixture for variant C: FULLY RESOLVED (2026-07-06)

Originally resolved only for the constructible half: a symbolic-only
fixture requirement (no `evidence` list declared) correctly appeared in
exactly one of variant C's two artifacts. A concrete-only fixture was
named as impossible: `_bind_self_describing` bound a symbolic record to
*every* requirement regardless of what it declared, so nothing could
ever be concrete-only.

**Fix:** `_bind_self_describing` (`evidence/render/matrix_variants.py`)
now checks each requirement's declared `evidence` list before binding
symbolic evidence — a requirement declaring only `concrete_test` entries
(no `crosshair` entry) gets no symbolic record. When `evidence` is
absent entirely, the original unconditional behavior is preserved
(backward-compatible with metadata that doesn't use the declaration
style — including the existing symbolic-only fixture, which relies on
exactly this fallback). Concrete binding is untouched either way — it
stays fully self-describing via `concrete_results.json`'s own
`requirement_id` field, per Gate 4's decision for variant C.

**No effect on committed data:** every real requirement in
`metadata.c.yaml` declares a `crosshair` entry (added when Gate 4's
asymmetry was closed), so this changes nothing observable — confirmed
by regenerating and diffing (differs only by `generated_utc`).

**Proven, not assumed:** `tests/test_single_evidence_type.py` now has
two fixtures instead of one: the existing symbolic-only case (unchanged
behavior, still passes) and a new concrete-only case (a requirement
declaring `evidence: [{method: concrete_test, test_id: ...}]`, no
`crosshair` entry) — confirmed to appear in exactly the concrete
artifact and not at all in the symbolic one, the property that was
previously impossible. 4 tests total (2 fixtures × validation + binding
behavior). Suite: 41 passed.

## Gate 6 — FRN pump-type tag: RESOLVED (2026-07-05)

`FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725). Within the
GIP v1.0 taxonomy specifically, denotes general-purpose volumetric
infusion pumps (peristaltic mechanism, cassette-based administration
set), distinct from the `All` tag used elsewhere in the source's hazard
tables. Resolved via NotebookLM's extraction of the full source PDF,
cross-checked against independent FDA-registry research landing on the
same product code — well-supported, but **not yet independently
re-verified against the raw Sec 2.4.1 text** of the source document
itself; that re-verification is named here rather than silently assumed
done. Full trail, citations, and the prior failed resolution attempts are
recorded in `sources/README.md` and
`examples/dosage_calculator/README.md`.

## Phase C Gate C1 — Dafny toolchain (2026-07-06) and adapter build (2026-07-07)

Researched directly rather than settling for the apt package or asking
Steven to make an under-informed call. Every claim below was checked
against the real, running tool, not documentation.

**GitHub is genuinely blocked, confirmed via the proxy itself, not
assumed.** `curl https://github.com` returns 400/403 depending on the
request; the proxy's own status endpoint
(`curl $HTTPS_PROXY/__agentproxy/status`) and its README are explicit
that 403/407 from the proxy is an organization egress-policy denial —
"do not retry or route around it." So no GitHub release, mirror, or
workaround was attempted. Two channels already permitted turned out to
be enough:

- `api.nuget.org` → 200 (reachable).
- `dot.net` / `dotnet.microsoft.com` → 301/302 (normal redirects,
  reachable).
- apt has `dotnet-sdk-8.0` directly (Ubuntu's own package, not a
  Microsoft add-on repo) — installed cleanly as 8.0.128 after
  `apt-get update` refreshed a stale package index that had been
  pointing at a version no longer on the mirror.

**Dafny installed via `dotnet tool install --global dafny`** (pulls from
NuGet, the same channel already confirmed reachable) — no GitHub
involvement anywhere in the chain. Result: **Dafny 4.11.0** (full
version string `4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2`) — a
real, current release, not the ~2015-era `2.3.0+dfsg-0.1` Mono-based
package apt offers directly. That apt package is no longer relevant to
Gate C1 at all.

**Verified against the running binary, three real checks:**
1. **Clean pass:** a valid `Clamp` method (mirrors the dosage kernel's
   clamping shape) verified with output `Dafny program verifier
   finished with 1 verified, 0 errors`, exit code 0 — this is an
   **exact match** to the false-zero note already committed in
   `evidence/model.py`. That note was written from documentation/prior
   knowledge; it's now confirmed accurate against the real 4.11.0
   binary, not just assumed to still hold.
2. **Failure path:** a deliberately broken `Clamp` (returns the raw
   input, unclamped) produced two per-line error blocks plus the
   summary `Dafny program verifier finished with 0 verified, 2 errors`
   — **exit code 4**, not 1. New finding: Dafny's exit codes are not a
   simple 0/success, 1/failure pair the way CrossHair's are — Gate C1's
   capture-integrity check needs `exit_code != 0` (already generically
   correct) but should not assume a specific nonzero value means
   anything beyond "not clean."
3. **The vacuous-precondition vulnerability (Gate C3, vector 1) is real
   on this binary, not speculative:** `requires x > 0 && x < 0` (an
   unsatisfiable precondition) against `ensures r == 999999` with
   `r := 0` in the body verified clean — `1 verified, 0 errors` — even
   though the postcondition is obviously false whenever the method
   could run. Confirms the concern Gate C3 named is a real, reproducible
   false-positive class on the actual tool, not a hypothetical.

**`dafny audit` does not help with vector 1 — checked, not assumed.**
Dafny 4.x ships an `audit` subcommand ("report issues that might limit
the soundness claims of verification"). Ran it against the vacuous
example: `0 findings`. Its help text confirms its actual scope —
un-annotated `assume`/axioms, non-determinism, unverified externs — not
general precondition satisfiability. Gate C3's originally-planned
mitigation (a dedicated Z3 satisfiability check on the extracted
precondition) is still necessary, not optional, and is technically
provable now: `z3.Solver()` correctly reports `unsat` for the
contradictory precondition and `sat` for a real one (e.g.
`0 <= x <= 200`) — confirmed by direct test in this environment.

**Net effect on the Gate C1–C3 plan:** no alteration needed. If
anything the plan is now on firmer ground than when it was written —
the false-zero note holds exactly as documented, the vacuous-precondition
risk is empirically confirmed rather than theoretical, and the Z3-based
mitigation is confirmed feasible with tools already present. The one
concrete addition: capture the exit code as-is (don't assume it's 1 on
failure) and don't rely on `dafny audit` for vector 1.

**Not yet done, as of the toolchain research (2026-07-06):** no capture
runner existed yet, no real Dafny spec had been written for `dosage.py`,
and nothing was committed to the repository from that investigation (the
probe `.dfy` files lived only in the scratch directory).

**Built the following day (2026-07-07), on this same toolchain:**

- `examples/dosage_calculator/dosage.dfy` — a real Dafny method,
  `CalculateHourlyDose`, mirroring the dosage kernel's clamping shape
  (`requires concentrationMgPerMl > 0.0`, `requires maxSafeDoseMgPerHr >
  0.0`, `ensures 0.0 <= dose <= maxSafeDoseMgPerHr`, `ensures
  infusionRateMlPerHr >= 0.0 || dose == 0.0`). Verifies clean against the
  real 4.11.0 binary: `Dafny program verifier finished with 1 verified, 0
  errors`, exit code 0. **REQ-DOSE-003 (finite-result-under-overflow) is
  explicitly excluded from this spec** — confirmed empirically that
  Dafny's `real` type is exact/arbitrary-precision with no IEEE
  overflow/infinity/NaN concept at all (`y := x / 0.0` on a `real` is
  itself a flagged verification error, not a silent `inf`), so there is
  no faithful way to state "finite result under overflow" as a Dafny
  postcondition. Named here as a deliberate scope exclusion, not a silent
  gap. `weight_kg` is also intentionally omitted (it's an unused
  precondition-only guard in the Python original).
- `examples/dosage_calculator/dosage_broken.dfy` — the Sample-B-equivalent
  broken variant (clamp removed). Fails for real against the same binary:
  `Dafny program verifier finished with 0 verified, 2 errors`, **exit
  code 4** (not 1 — confirms the exit-code finding from the toolchain
  research above, now exercised on the actual dosage spec rather than a
  probe).
- `run_verify_dafny.py` / `run_verify_dafny_broken.py` — capture runners
  mirroring `run_verify.py` / `run_verify_broken.py` exactly: subprocess
  the real `dafny verify` command, write the verbatim stdout+stderr and a
  run manifest (tool, tool_version, command, exit_code, started_utc,
  target). Both were run for real, producing genuine committed captures:
  `raw_dafny_output.txt`, `run_manifest_dafny.json`,
  `raw_dafny_output_broken.txt`, `run_manifest_dafny_broken.json` — no
  fabricated output anywhere.
- `evidence/dafny_adapter.py::parse_dafny_capture(raw_output, manifest)`
  — the false-zero guard itself. Checks, in order: (1) `exit_code != 0`
  → refuse, cheapest and most definitive signal, checked first; (2) no
  regex match for `Dafny program verifier finished with (\d+) verified,
  (\d+) errors?` anywhere in the output → refuse (a crash, a timeout, or
  a Dafny subcommand that "did not attempt verification" — confirmed
  real behavior of `dafny audit` on some inputs — must not be silently
  treated as success just because exit_code happens to be 0); (3) parsed
  error count != 0 → refuse. Only when all three pass does it construct a
  `VerificationResult(strength=Strength.PROVEN, verifier_completion_status="completed", ...)`.
  Never a blind `"0 errors" in raw_output` substring check, which a
  printed error message could coincidentally contain.
- `evidence/model.py` gained `verifier_completion_status: Optional[str] =
  None` on `VerificationResult` — purely additive, doesn't disturb any
  existing construction site.
- `tests/test_dafny_adapter.py` — six tests, all passing: parses the real
  committed clean capture to PROVEN; refuses the real committed broken
  capture (on `exit_code=4`, before the summary line is ever parsed);
  refuses a synthetic nonzero-exit manifest; refuses a synthetic
  missing-summary-line capture (mimicking `dafny audit`'s "did not
  attempt verification"); and the load-bearing regression —
  **`test_false_zero_guard_is_not_fooled_by_a_substring_trap`** —
  constructs raw output containing the literal substring `"0 errors"` in
  an unrelated sentence *plus* a real summary line reporting `3 verified,
  2 errors`, and confirms the parser correctly refuses (a blind substring
  check would have wrongly passed this exact input). A sixth test,
  **`test_producing_a_proven_result_does_not_reopen_the_matrix_gate`**,
  builds a fake matrix row using this adapter's real `Strength.PROVEN`
  value and confirms `assert_no_realized_proven`
  (`evidence/render/matrix_variants.py`) still hard-blocks it — proving
  this adapter cannot itself reopen the PROVEN-exclusivity boundary; only
  Gate C2 (still unbuilt) could do that.
- **Explicitly not done here, and not this module's job:** `dafny_adapter.py`
  is not called from `build_matrix()`, any `generate_matrix_*.py` script,
  or the CLI. Wiring a Dafny-sourced PROVEN result into the matrix
  pipeline — including deciding how `verifier_completion_status`
  surfaces in a rendered row — is Gate C2's job by name (the
  PROVEN-exclusivity migration), not an incidental side effect of this
  build.

**Made reproducible for future sessions (2026-07-06):** the toolchain
research above only holds for this session's container — a fresh
session starts from a clean clone with none of it installed. Added
`.claude/hooks/session-start.sh` (registered via `.claude/settings.json`)
to install it automatically: Python deps (`crosshair-tool`, `jsonschema`,
`pyyaml`, `pytest`), the .NET 8 SDK via apt, and **Dafny pinned to
4.11.0** via `dotnet tool install --global dafny --version 4.11.0` —
pinned explicitly, matching the `crosshair-tool 0.0.107` discipline, so
a future session doesn't silently pick up a different Dafny version
with different output conventions than the ones verified above. The
hook is idempotent (checked installed versions before reinstalling) and
runs synchronously (session start waits for it, trading startup latency
for guaranteeing the toolchain is ready before any command runs).
Validated by running it directly in this session (exit 0, ~1.4s on the
already-provisioned path) and confirming `dafny --version` and the full
test suite (41 passed) both work immediately after.

## Phase C Gate C2 — PROVEN's exclusivity migration: BUILT (2026-07-07)

Requested directly: "start gate C2." The roadmap's design for this gate
was already fully specified (`payloadguard-evidence-roadmap-phaseB-to-C.md`,
Gate C2 section) before this build — this session implemented that
ratified design rather than inventing a new one.

**The rule (ruling R3, supersedes R2):** `assert_no_realized_proven`
(`evidence/render/matrix_variants.py`) previously hard-failed if ANY
record anywhere claimed PROVEN, full stop, no exceptions. It now permits
PROVEN as a realized strength under exactly one condition: the record's
`method` field equals `"dafny"` **and** its `verifier_completion_status`
field equals `"completed"`. Both conditions are required — a record
naming `method="dafny"` alone is not enough; a hand-assembled or
corrupted record that skipped the adapter's own checks is still refused.
Every other method — `crosshair`, `concrete_test`, or a row/record with
no method at all (e.g. a scope-GAP row) — remains permanently,
unconditionally excluded from PROVEN, exactly as under R2.

**Why the completion-status check is real defense-in-depth, not
redundant paranoia:** `evidence/dafny_adapter.py::parse_dafny_capture` is
already structurally incapable of returning a PROVEN
`VerificationResult` unless its own exit-code, summary-line, and
false-zero checks all passed — so in the adapter's own output, `method
== "dafny"` and `verifier_completion_status == "completed"` are always
both true together. R3 re-checks both anyway, at the matrix boundary,
because `assert_no_realized_proven` has no way to know whether a future
binder assembled a given record through the adapter or by hand; the
check must hold regardless of how the record got there, not just for
today's one call site.

**8 new tests, `tests/test_proven_exclusivity.py`** — the roadmap named
two required cases (a positive and a negative); this build has both plus
additional defense-in-depth and shape coverage:
1. **Positive:** a real Dafny PROVEN record, produced via
   `parse_dafny_capture` against the real committed clean capture (the
   same one Gate C1 verified), is accepted by `assert_no_realized_proven`
   without raising.
2. **Negative, crosshair:** a `method="crosshair"` record with
   `strength="PROVEN"` and a completed status is refused — checked
   explicitly with a real fixture, not inferred from the absence of a
   binder that would produce one.
3. **Negative, concrete_test:** same property, the other permanently-
   excluded method.
4. **Negative, missing method:** a record with no `method` key at all
   (mirrors a scope-GAP row's actual shape) is refused, not silently
   accepted because there's nothing to compare against `"dafny"`.
5. **Negative, dafny method without completed status:** a record naming
   `method="dafny"` but `verifier_completion_status=None` is still
   refused — the method label alone is not trusted.
6. **Negative, dafny method with an explicit incomplete status:** same
   property with a non-`None`, non-`"completed"` value.
7. **Row-level shape:** variant B/C's rows carry `strength`/`method`
   directly on the row (not nested in an `evidence` list) — confirmed
   the same rule applies to that shape too.
8. **Regression:** all four committed matrix artifacts (none of which
   contain a dafny record today) still pass `assert_no_realized_proven`
   unchanged — R3 does not alter behavior for the live, all-CrossHair/
   concrete-test dataset.

**Existing structural tests unaffected, verified not assumed:**
`tests/test_structural_proven_check.py`'s corruption cases (a
`crosshair`-method record forced to `PROVEN`) still raise under R3 with
the identical error-message substring (`"realized strength PROVEN"`) —
its assertions needed no changes, confirming R3 is a strict relaxation
for one specific, checked case rather than a broadening of the rule in
general. Full suite re-run after this build: 55 passed (47 prior + 8
new). The full `generate_artifacts.py` pipeline was also re-run,
producing zero observable change to any committed matrix artifact beyond
`generated_utc` timestamps — confirming R3 has no effect on the live
pipeline today, since no binder yet produces a dafny-method record.

**Explicitly not done here, and not this gate's job:** no binder in
`evidence/render/matrix_variants.py` (`_bind_declared`, `_bind_shadow`,
`_bind_self_describing`) was changed to actually assemble a Dafny-sourced
record into a live matrix row. R3 makes that *possible* without
violating the structural gate; it does not make it *happen*. Per the
roadmap's own suggested build order, wiring a real Dafny record into the
matrix pipeline belongs alongside Gate C4 (Spec-Testing Proofs,
"alongside the first real spec"), and trusting a live PROVEN claim in
earnest still waits on Gate C3's parser hardening. Gate C2's job was
narrowly the structural rule change — done.

## Phase C Gate C3 — Dafny output-parsing hardening: vectors 1–3 BUILT, vector 4 BLOCKED (2026-07-07)

Requested directly: "start gate c3." The roadmap named four distinct
failure modes; this build addresses the three that were actually
scopeable and leaves the fourth named rather than guessed at.

### Vector 1 — vacuous proofs from contradictory preconditions: BUILT

A `requires` clause that can never be true makes every postcondition
hold vacuously — Dafny reports a clean pass with no hint anything is
wrong. `evidence/dafny_spec_lint.py::check_precondition_satisfiability`
extracts a method's `requires` clauses (via `_find_method_header` /
`extract_requires_clauses`, a small header-scanning routine that tracks
paren depth to find the body's opening brace, then splits on clause
keywords) and asks Z3 whether their conjunction is satisfiable —
independent of whatever Dafny itself reported.

A small, explicitly-scoped hand-written expression translator
(`_tokenize` + the `_Parser` recursive-descent class) handles exactly
the subset of Dafny expressions this repo's specs actually use:
`&&`/`||`/`!`/`==>`/`<==>`, chained comparisons (`0.0 <= dose <=
maxSafeDoseMgPerHr`), arithmetic, and `real`/`int`/`nat`/`bool`
identifiers and literals. `nat` parameters get their implicit `>= 0`
Dafny semantics as an added constraint (checked: `requires n < 0` on a
`nat` parameter is correctly `unsat`). Anything outside that subset —
quantifiers (`forall`/`exists`), `old(...)`, unknown parameter types
(e.g. `array2<int>`), unparseable trailing tokens — raises `SystemExit`
outright, Tier 1: refused, never mistranslated or silently dropped.

**Proven against a real committed fixture, not a synthetic string only:**
`examples/dosage_calculator/vacuous_precondition_probe.dfy` — a tiny,
dedicated, committed Dafny file with `requires x > 0 && x < 0` and
`ensures r == 999999`. Verified for real against Dafny 4.11.0: **`1
verified, 0 errors`, exit 0 — a genuine clean pass** on a method whose
postcondition is obviously unreachable-but-unfalsifiable. The Z3 checker
correctly reports `unsat` on the same method's extracted precondition —
catching, mechanically, exactly what the verifier's own clean-pass
report missed. A true-negative companion check confirms the real
dosage.dfy kernel's actual precondition (`concentrationMgPerMl > 0.0 &&
maxSafeDoseMgPerHr > 0.0`) is correctly reported `sat` — the checker
doesn't cry wolf on a legitimate spec.

### Vector 2 — weak postconditions: BUILT (heuristic, best-effort, named as such)

A one-way implication (`==>`) in an `ensures` clause can let a broken
implementation vacuously satisfy the spec whenever the antecedent is
false, where a bi-implication (`<==>`) would have pinned down both
directions. `evidence/dafny_spec_lint.py::scan_weak_postconditions`
flags every `ensures` clause containing `==>` without also containing
`<==>`, returning warning strings for human review — **not a hard
block and not a full proof**, exactly as the roadmap scoped it: this
heuristic cannot and does not decide whether a bi-implication was
actually *needed* for a given spec, only that a one-way implication is
present and worth a second look.

Tested against the real dosage.dfy kernel (zero warnings — its ensures
clauses use `<=`/`==`/`||`, never `==>`, a true negative), a synthetic
one-way-implication clause (`ensures valid ==> r2 == r`, flagged with
the clause text quoted verbatim), and a synthetic `<==>` clause (not
flagged, another true negative).

### Vector 3 — timeout/resource-limit masking: BUILT, with a real empirical finding

**A genuine finding on the installed Dafny 4.11.0 binary, not a
hypothetical:** `dafny verify --resource-limit=1` on the real,
committed `dosage.dfy` spec produces

    Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource

— an `"errors"` count of **0** on a run that did **not** complete.
Committed for real via a new capture runner,
`run_verify_dafny_resource_limited.py`, producing genuine
`raw_dafny_output_resource_limited.txt` /
`run_manifest_dafny_resource_limited.json` (no fabricated output).

**Checked, not assumed, whether this is actually exploitable via
exit_code alone:** the real captured `exit_code` is **4** (nonzero), so
Gate C1's existing `exit_code != 0` check already refuses this capture
before the summary line is ever parsed — this vector does *not* silently
bypass exit-code protection in this Dafny version. (An earlier
suspicion in this same session that the exit code was 0 for this case
turned out to be a shell-scripting artifact — a piped command whose
`$?` was `tail`'s exit status, not `dafny`'s — caught and corrected by
re-running the check without the pipe, in the same "verify, don't
assume" spirit this repo applies to the tool itself, applied here to my
own probing too.)

**Hardened anyway, as real defense in depth, not just because the risk
is proven live today:** `evidence/dafny_adapter.py`'s summary-line
regex now captures the tail of the summary line after the error count
and refuses if it contains `"out of resource"`, `"out of memory"`, or
`"timed out"` (case-insensitive) — independent of the exit-code check,
so the false-zero guard doesn't rely on exit-code correctness alone. Of
these three markers, only `"out of resource"` was independently
reproduced end-to-end against the real binary this session; `"out of
memory"` and `"timed out"` are the confirmed sibling vocabulary in the
same Boogie/Dafny summary-formatting code path (verified by extracting
UTF-16 string literals directly from the installed `Boogie.
ExecutionEngine.dll` / `DafnyDriver.dll` — `", {0} out of memory"`, `",
{0} out of resource"`, `"timed out"` all appear as parallel fragments)
but were not independently forced to reproduce in this session — named
as such, not overclaimed as separately verified.

Also hardened: the parser now refuses if a capture contains **more than
one** summary-line match, rather than trusting `.search()`'s first
match — checked empirically that a normal `dafny verify` invocation
with multiple target files still emits exactly one aggregate summary
line, so this closes a theoretical ambiguity without changing behavior
for any real single-target capture in this repo.

**8 new tests, `tests/test_dafny_timeout_masking.py`:** the real
resource-limited capture is refused (via the exit-code check); synthetic
cases prove the summary-line hardening fires independently for all
three markers even with a forced `exit_code: 0`; an ambiguous
two-summary-line capture is refused; and the real Gate C1 clean capture
still parses to PROVEN unchanged (no regression on the happy path).

### Vector 4 — specification stripping: still BLOCKED, named

No new source material surfaced this session either. The fourth vector
referenced an LLM-self-healing-loop scenario in the original planning
document, cut off before detail was captured. Still needs a follow-up
read of that original document before it can be scoped at all — not
inferred from the name, not guessed at, exactly as it was left after
Gate C1/C2.

**Test count:** 11 new tests in `tests/test_dafny_spec_lint.py` (vectors
1–2) plus 6 in `tests/test_dafny_timeout_masking.py` (vector 3) — full
suite now 72 passed (55 prior + 17 new). Full `generate_artifacts.py`
pipeline re-run: zero observable change beyond `generated_utc`
timestamps — none of this gate's mechanisms are wired into
`build_matrix()` or any generator; they're standalone, tested
capabilities, exactly matching Gate C1's own scope.

**Explicitly not done here:** neither the Z3 precondition check nor the
weak-postcondition heuristic is invoked automatically anywhere in the
capture or generation pipeline — they exist as tested, callable modules,
not as a gate that runs on every capture. Wiring them into the capture
workflow (so every future Dafny spec gets both checks run against it as
a matter of course) is a natural follow-up but wasn't asked for and
isn't implied by "start gate C3" — named here rather than silently
assumed done.

## Phase C Gate C4 — Spec-Testing Proofs (STPs): BUILT, and found a real spec gap (2026-07-07)

Requested directly: "start gate C4." IronSpec's methodology — prove
that specific, manually chosen input/output pairs are correctly accepted
or rejected *by the specification itself*, independent of whether any
implementation is ever called — was applied to the one Dafny spec that
exists in this repo, `dosage.dfy` (Gate C1). It found a real gap on the
first attempt, not a synthetic one built to demonstrate the mechanism.

### The finding: the original postcondition never pinned the dose value

Before this gate, `CalculateHourlyDose`'s ensures clauses were exactly
two: `0.0 <= dose <= maxSafeDoseMgPerHr` (bounds) and
`infusionRateMlPerHr >= 0.0 || dose == 0.0` (reverse-flow-zero). Neither
clause relates `dose` to the actual product of rate and concentration in
the normal or ceiling-clamped cases. Checked directly, not assumed: a
Dafny lemma stating "if these inputs are fixed and `dose` satisfies both
ensures clauses, then `dose` must equal the one correct clamped value"
**failed to verify** — Dafny could not prove it, because the postcondition
genuinely does not force it. A method that always returned `0.0` for any
non-negative-rate input would have satisfied the exact same spec Gate C1
verified as a clean pass. This is the identical bug CLASS Gate 1 found by
hand for REQ-GIP-1-4-12 (spec/evidence not matching the requirement
text) — recurring, independently, in this session's own new Dafny spec,
caught mechanically this time rather than by manual review.

### The fix

`examples/dosage_calculator/dosage.dfy` gained a `function ExpectedDose(
concentrationMgPerMl, infusionRateMlPerHr, maxSafeDoseMgPerHr): real`
computing the exact clamped value (same three-way branch as the method
body), and a new `ensures dose == ExpectedDose(...)` clause pinning the
method's output to it exactly. The two original ensures clauses stay,
unchanged, for direct per-requirement traceability (REQ-GIP-1-4-12,
REQ-GIP-1-8-1) — now implied by, not contradicting, the pinning clause.
Re-verified for real: `2 verified, 0 errors` (the function plus the
method), exit 0. **The real committed capture was re-run honestly, not
patched:** `raw_dafny_output.txt` / `run_manifest_dafny.json` now reflect
this fixed spec (previously `1 verified, 0 errors` for the method alone).
`tests/test_dafny_adapter.py`'s assertion on the exact `raw_status`
string was updated to match, with a comment explaining why the count
changed.

### The preserved exhibit and the two-sided proof

`examples/dosage_calculator/dosage_underconstrained.dfy` preserves the
ORIGINAL weak spec byte-for-byte — same rationale as
`dosage_naive_widening.py`: a defect that "looks fine" (verifies cleanly
on its own — confirmed for real, `1 verified, 0 errors`) is kept, named,
rather than quietly replaced with no trace. Two STP suites prove the gap
existed and is now closed, both `include`-ing the relevant spec rather
than duplicating it:

- **`dosage_stp_suite.dfy`** (`include "dosage.dfy"`, the fixed spec):
  six lemmas across the three logically distinct branches of
  `CalculateHourlyDose` — normal in-range, ceiling-clamped, and
  reverse-flow. Each of the first two gets one ACCEPT lemma (the correct
  value is provably forced) and one REJECT lemma (a wrong candidate
  value is provably excluded — `ensures false` proved from a
  contradiction). The reverse-flow branch gets only an ACCEPT lemma; it
  was never a gap, even in the weak spec (see below). All six verify
  cleanly against the fixed spec: `10 verified, 0 errors`, exit 0.
- **`dosage_stp_suite_against_underconstrained.dfy`** (`include
  "dosage_underconstrained.dfy"`, the preserved original): the *same two*
  REJECT lemmas, run against the weak spec instead. Both **fail to
  verify** — `0 verified, 2 errors`, exit 4 — a genuinely negative
  capture, not smoothed over, mirroring `dosage_broken.dfy`'s honesty
  discipline. This is the mechanized proof that the gap was real: the
  identical lemma that succeeds against the fix cannot be proved against
  the original.
- **Why the reverse-flow branch has no REJECT lemma against the weak
  spec:** `infusionRateMlPerHr >= 0.0 || dose == 0.0` already forces
  `dose` to exactly `0` whenever the rate is negative — that branch was
  never under-constrained, checked rather than assumed identical to the
  other two.

### A mistake caught during this build, corrected before committing

An early draft of the ceiling-clamped REJECT lemma used `dose == 500.0`
(the raw, unclamped product) as the "wrong" value. That lemma verified
even against the **weak** spec — not because the weak spec pins the
correct value, but because `500.0` already violates the weak spec's own
`0.0 <= dose <= maxSafeDoseMgPerHr` bound directly, so excluding it
proves nothing about the actual gap (whether the spec forces the
*correct in-bounds* value, `100.0`, rather than some other in-bounds
value). Caught by checking the lemma's behavior against the weak spec
directly rather than assuming the chosen wrong-value was a good test;
corrected to `dose == 50.0` (in-bounds, still wrong) in both suites,
re-verified, and a regression test
(`test_reject_lemmas_target_in_bounds_wrong_values_not_out_of_bounds_ones`)
added to `tests/test_dafny_stp_suite.py` to guard against silently
reintroducing the weaker, false-passing value.

### Tests and verification

`tests/test_dafny_stp_suite.py` — 6 tests, checking the real committed
captures directly (not via `evidence.dafny_adapter.parse_dafny_capture`,
since an STP suite's capture is a proof about the spec's tightness, not
itself a requirement's verification evidence — matching Gate C1–C3's
precedent of standalone, non-wired capabilities): the underconstrained
spec still verifies alone; the STP suite passes against the fix; the
same suite fails against the preserved weak spec; the 50.0-vs-500.0
regression; and two direct source-text checks confirming the fixed spec
has the pinning clause and the preserved exhibit does not. Full suite
after this gate: **78 passed** (72 prior + 6 new). Full
`generate_artifacts.py` pipeline re-run: zero observable change beyond
`generated_utc` timestamps.

**Explicitly not done here:** neither STP suite is wired into
`build_matrix()` or any generator, and no automated mechanism runs STPs
against future Dafny specs as a matter of course — this gate authored
one STP suite for the one spec that exists, per its stated scope ("every
Dafny spec written for Phase C gets a small STP suite alongside it,
authored by whoever writes the spec"), not a generic STP-generation
tool.

## Phase C Gate C5 — Mutation testing: BUILT, extended from research findings, zero survivors/unclassifiable (2026-07-07)

Requested directly: "build it and be careful with Dafny. just. we can
consider floating points later..it's a known but solvable issue" —
following up on the scoping session earlier the same day. Read as: build
the core (ROR/LOR/COI on requires/ensures clauses) now; the
floating-point-adjacent risk named in the scoping doc (AOR's `/` mutant
possibly failing via Dafny's own division-by-zero check rather than the
postcondition) can wait. A later message added: "we can consider
bounding floating points within the terms of accuracy... if we're
dealing with an integer 1e10, we don't have to be any more accurate than
accuracy requires" — recorded here as guidance for that follow-up (bound
any future real-valued mutant to the accuracy the dosage calculation
actually needs, not to Dafny's unbounded exact-`real` precision), not
acted on in this build.

### What was built

`evidence/dafny_mutate.py`: `generate_ror_mutants`/`generate_lor_mutants`/
`generate_aor_mutants`/`generate_coi_mutants` (+ `generate_mutants`,
aggregating all four). Reuses `dafny_nl_summary._CLAUSE_LINE_RE` (the
single-line clause convention Gate C6 established) and
`dafny_spec_lint._find_method_header` to locate clause spans; a local,
span-preserving tokenizer extends `dafny_spec_lint`'s token grammar with
one addition (a COMMA token, so a clause containing a function call like
the pinning clause's `ExpectedDose(a, b, c)` can be lexically scanned) -
safe here specifically because mutation only ever relocates an
operator's TEXT, it never needs to understand what the expression means
the way Z3 translation does, so tolerating syntax the Z3 translator
correctly refuses does not risk mistranslating anything.

**Pass 1 (static triviality filter), the design point worth stating
explicitly:** a mutant is skipped before spending a real Dafny
invocation on it when it's guaranteed uninteresting from a fixed,
context-free relational-operator implication table alone — but the
DIRECTION that's "trivial" flips by clause role, and getting this
backwards would have silently filtered out the informative mutants
instead of the uninteresting ones:
- For an **ensures** clause, weakening is trivial: if the original
  clause `P` already provably holds, and the mutant `P'` is a universal
  logical consequence of `P` (e.g. `==` weakened to `<=`), then `P'`
  trivially still holds — no new verification needed, and testing it
  would tell you nothing.
- For a **requires** clause, *strengthening* is trivial: if a mutant `Q'`
  is a universal logical consequence that makes the precondition
  *narrower* (e.g. `>=` tightened to `>`), then the original proof
  (which worked under the wider hypothesis `Q`) still trivially applies
  under `Q'` — testing it would also tell you nothing. The informative
  direction for a requires clause is *weakening* it (admitting states the
  original proof never had to handle).

Verified against a synthetic spec independent of `dosage.dfy`'s specific
content (`test_ror_polarity_flips_between_requires_and_ensures`), not
just against the one real spec, since this is the least obvious part of
the design and the one most likely to be silently wrong in one direction
without a targeted test.

**Passes 2-3, reuse over reinvention, as scoped:** pass 2 (vacuity
filtering for `requires` mutants) calls `dafny_spec_lint.check_precondition_satisfiability`
directly against the mutated full source — no new Z3 code. Pass 3
(re-verification) is `examples/dosage_calculator/run_mutation_suite.py`,
mirroring `run_verify_dafny.py`'s capture discipline (real subprocess,
verbatim output, real exit code) and reusing `dafny_adapter`'s
`_SUMMARY_RE`/`_INCOMPLETE_MARKERS` for the same never-trust-a-bare-exit-
code parsing rigor, per-mutant.

### Real run against `dosage.dfy::CalculateHourlyDose`: 39 mutants

29 killed, 4 filtered_static (pass 1), **2 survived**, **4 unclassifiable**.
Mutant `.dfy` files are not committed individually (mechanically derived,
one text substitution — unlike the STP suites' hand-authored artifacts);
what's committed is the generator, the runner, and the real per-mutant
outcome: `examples/dosage_calculator/mutation_report.json`/`.md` and
`run_manifest_mutation.json`.

**The 2 survivors — a real, understood finding, reported then fixed on
Steven's decision, not silently changed.** Both were
`infusionRateMlPerHr >= 0.0 || dose == 0.0` (REQ-GIP-1-8-1) with the
first disjunct's `>=` mutated to `!=` or `>`; both still verified
(`2 verified, 0 errors`), confirmed by direct re-run, not a fluke. Root
cause, worked out by hand and checked against the real numbers: at
`infusionRateMlPerHr == 0.0` exactly, real multiplication gives
`rawDose == 0.0 * concentrationMgPerMl == 0.0` exactly, which is neither
`< 0.0` nor `> maxSafeDoseMgPerHr` (since `maxSafeDoseMgPerHr > 0.0` by
precondition), so `dose == rawDose == 0.0` — meaning the clause's second
disjunct (`dose == 0.0`) already holds at that single boundary point
regardless of which comparison operator the first disjunct uses. The
postcondition's `>=` at that exact point wasn't independently load-
bearing given how the implementation clamps.

**Not silently changed — reported first, fixed on explicit decision:**
`dosage.dfy` is the spec Steven signed off on in Gate C6 ("it's good for
the spec as is") the same day, so this finding was reported for his
decision rather than acted on unilaterally. **Decision: "go ahead and
tighten REQ-GIP-1-8-1 to `>`."** `dosage.dfy` changed accordingly,
re-verified clean (`2 verified, 0 errors`, unchanged — the tightening
didn't cost anything), and the mutation suite re-run in full to confirm
the fix rather than just asserting it: **zero survivors remain.** The
two former survivor mutations (`> -> >=`, `> -> !=`) are now correctly
recognized by pass 1's static filter as trivially uninteresting *before*
Dafny is even invoked — a proof of `x > 0` universally implies both
`x >= 0` and `x != 0` — which is itself a clean, mechanical confirmation
that the boundary is now tight (filtered_static rose from 4 to 6; killed
stayed exactly 29; unclassifiable stayed exactly 4 and is unrelated).
`examples/dosage_calculator/nl_confirmation_dosage_dfy.md` gained an
amendment recording the decision, the regenerated plain-English summary,
and the re-confirmation. `dosage.dfy`'s header comment documents the fix
inline, alongside the Gate C4 fix comment it sits next to.

**The 4 unclassifiable results — a real gap in the mutation engine, not
in the spec.** All 4 come from mutating exactly one side of the chained
`0.0 <= dose <= maxSafeDoseMgPerHr` clause to a descending operator
(`>=` or `>`) while leaving the other `<=` unchanged, e.g.
`0.0 >= dose <= maxSafeDoseMgPerHr`. Confirmed by direct re-run: Dafny's
own PARSER rejects this (`this operator chain cannot continue with an
ascending/descending operator`, exit code 2) — a real Dafny language
rule (chained comparisons must stay direction-consistent) that the
mutation engine doesn't yet model. Correctly refused rather than
misclassified: `run_mutation_suite.py._classify` only accepts exit codes
0/4 as classifiable results, and relays Dafny's own error line (with the
generated temp filename scrubbed for determinism) as the detail rather
than guessing. **Not fixed in this pass** — a real, scoped follow-up
(teach the generator Dafny's chain-direction compatibility rule, or skip
generating direction-incompatible chain mutants) would remove this
category; named here rather than left unexplained.

### Explicitly out of v1 scope, checked not assumed

**SOR/HOR:** not implemented at all. `test_sor_and_hor_not_applicable_confirmed_by_absence_of_syntax`
greps `dosage.dfy` for set-typed syntax (`set<`, `iset<`, `multiset<`,
`seq<`) and heap/object-state syntax (`old(`, `fresh(`, `allocated(`,
`reads `, `modifies `) and asserts none are present — "not applicable"
is a tested fact about this spec, not an assumption.

**AOR:** implemented and exercised (`generate_aor_mutants` runs against
the real spec and is asserted to return `[]`, not just left untested) —
but the one arithmetic operator in `dosage.dfy`
(`infusionRateMlPerHr * concentrationMgPerMl`) lives inside
`ExpectedDose`'s function body, outside this v1's clause-level mutation
scope, so it correctly contributes zero mutants today. Mutating it would
need a separate function-body extractor (not built) and would revive the
named division-by-zero attribution risk from the scoping session, plus
the newer guidance to bound any real-valued mutant to the dosage
calculation's actual required accuracy rather than Dafny's unbounded
exact-`real` precision — both deferred together as one follow-up, not
solved piecemeal here.

### Tests

`tests/test_dafny_mutate.py` (11 tests) — pure generation/filter logic,
no Dafny invocations, fast: real-spec ROR/LOR/AOR/COI counts and
filtering (updated post-fix: 6 filtered, not 4); the SOR/HOR
non-applicability check; a byte-level check that a mutation changes
exactly the targeted operator and nothing else; the requires/ensures
polarity-flip test described above; tokenizer function-call and
unknown-syntax handling. `tests/test_mutation_report.py` (5 tests) —
validates the COMMITTED real capture rather than re-running 39 Dafny
invocations on every test pass (matches this repo's established pattern
for other real captures): total/outcome counts (0 survivors, post-fix),
a regression confirming the two former survivor mutations are now
`filtered_static` (so a future regeneration can't let a survivor
quietly reappear without a test failing), the four unclassifiable
entries all attributed to the chain-direction parse error, and that no
recorded mutant ever touches the method's own implementation body. Full
suite after this gate: **121 passed** (105 prior + 16 new).

### Research findings and a correction (2026-07-07)

External research into the two open questions this gate's build raised
(sent out via `gate-c5-research-prompt.md`, results recorded in full in
`examples/dosage_calculator/gate_c5_mutation_testing_research_findings.md`)
produced one correction worth stating plainly: **this gate's own label,
"MutDafny/IronSpec-style," was wrong.** IronSpec's actual mutation
technique is a directional, implication-lemma-based approach, distinct
from what this module does (brute verify/observe, matching MutDafny).
Corrected in `evidence/dafny_mutate.py`'s module docstring and
throughout this repo's docs; Gate C4's own IronSpec attribution (STPs)
is unaffected and correct. The research also gave the Problem-A survivor
finding a name with real precedent — **masking**, the MC/DC term for a
sibling condition making a boundary's exact operator unobservable,
FAA/DO-178C-accepted in the adjacent aerospace safety-critical field.

### Extension, same day: chain-direction-aware ROR and function-body AOR

Requested directly ("build both") following the research above. Two
concrete follow-ups it identified were built the same day:

**1. Chain-direction-aware ROR.** Confirmed the chained-comparison
direction rule against the Dafny Reference Manual (Sec 5.2.1–5.2.2)
directly, not just this repo's own empirical observation. New helpers
`_chain_group_ids` (partitions a clause's tokens into groups that never
cross a boolean-connective or parenthesis boundary — a conservative
approximation of Dafny's actual chain-scoping rule) and
`_chain_incompatible` (a chain link's candidate operator is incompatible
if it would mix an ascending relation with a descending one against its
chain siblings; `==`/`!=` are always compatible) are wired into
`_generate_token_mutants` via a new `chain_aware` parameter, used only
by `generate_ror_mutants` (`&&`/`||`/arithmetic operators have no
analogous chaining rule). Result: the 4 mutants that used to reach real
Dafny invocation and come back `unclassifiable` (a genuine parse error)
are now filtered before generation ever reaches verification — a new
`filtered_chain_incompatible` outcome bucket, distinct from pass 1's
`filtered_static` (a different reason: syntactic invalidity, not
semantic redundancy). MutDafny itself does not do this (its own
pipeline buckets these post-hoc as `Invalid`) — a genuine improvement
over the published state of the art, not parity with it.

**2. Function-body AOR, MutDafny-restricted.** `generate_aor_mutants`
gained an optional `function_name` parameter; when given, also scans
that function's BODY for arithmetic operators via two new helpers:
`_find_function_body_span` (brace-matched, mirroring
`dafny_spec_lint._find_method_header`'s depth-tracking but returning the
body content rather than the header preceding it) and
`_locate_function_body_arithmetic_sites` (refuses outright, rather than
risk a misaligned offset, if the body contains a `//` comment — none
does today, checked). `_TOKEN_SPAN_RE` gained `ASSIGN` (`:=`) and `SEMI`
(`;`) token kinds, needed for body statements
(`var rawDose := infusionRateMlPerHr * concentrationMgPerMl;`) but never
present in requires/ensures clauses. `_ar_group_incompatible` applies
MutDafny's own restriction directly (Amaral, Mendes & Campos 2025):
`+`/`-`/`*` freely interchange; `/` only interchanges with `%` (absent
from this spec), so a mutation can never introduce `/` where the
original had none — the division-by-zero false-kill risk named when AOR
was originally deferred is eliminated by construction, not by post-hoc
failure-reason attribution. `generate_mutants` gained the same
`function_name` parameter, and the real caller
(`run_mutation_suite.py`) now passes `"ExpectedDose"`.

**Real re-run against `dosage.dfy::CalculateHourlyDose`, both
extensions active: 42 mutants — 31 killed, 6 filtered_static, 4
filtered_chain_incompatible, 1 filtered_ar_group_incompatible, zero
survived, zero unclassifiable.** The 3 new function-body AOR mutants:
`* -> +` and `* -> -` both real-verified and genuinely **killed**
(confirming `*` is load-bearing — mutating it breaks the pinning
clause's proof, exactly as expected since the method body's own,
unmutated computation of `rawDose` then diverges from the mutated
`ExpectedDose`'s); `* -> /` filtered before verification, as designed.
The chain-incompatible mutants that used to be `unclassifiable`: gone,
replaced by 4 `filtered_chain_incompatible` records, same underlying
mutants, correctly attributed pre-verification now instead of post-hoc.

**Then built the same day:** the ≥0.01 mL/hr clinical-precision-floor
guidance from the same research — it bounds literal-value-replacement
(LVR) mutants specifically (a *magnitude* concept), a mutation class
Gate C5's original six-operator scope never included. See the LVR
extension section below.

**Tests:** `tests/test_dafny_mutate.py` grew from 11 to 19 (new:
chain-direction filtering on the real spec, a direct synthetic
tokenizer test for `:=`/`;`, direct unit tests of
`_chain_incompatible`/`_ar_group_incompatible` against hand-derived
cases independent of the real spec, function-body AOR generation and
its division-free restriction, `_locate_function_body_arithmetic_sites`
finds exactly the one `*`). `tests/test_mutation_report.py` grew from 5
to 7 (replaced the "4 unclassifiable, all chain-direction" regression
with "zero survivors AND zero unclassifiable," added a direct check on
the function-body AOR outcomes). Full suite: **131 passed** (105 +
Gate C5 v1's 16 + this extension's 10).

### LVR extension, same day: every hand-derived prediction confirmed exactly

Requested directly: "scope out Gate C5's LVR extension," then "go" once
the sub-plan (payloadguard-evidence-roadmap-phaseB-to-C.md's "Gate C5
LVR extension" section) was written. Tests whether a comparison's
LITERAL CONSTANT is load-bearing, not just its operator (ROR) or the
arithmetic combining it (AOR). Every numeric literal in `dosage.dfy`'s
requires/ensures clauses and `ExpectedDose`'s function body was
enumerated by running the real tokenizer — **all 7 are exactly `0.0`**;
no other numeric constant exists anywhere in the spec.

**Value-selection strategy:** exactly `original ± 0.01` per site — the
clinical-precision floor from the earlier research, finally applied (it
was always scoped to literal perturbation specifically). Deliberately
the sharpest possible test, not an open-ended range: if a proof survives
the smallest clinically-distinguishable nudge, it survives a larger one
too; if it's killed by the smallest nudge, that's the tightest possible
confirmation.

**Static filter, generalizing ROR's polarity principle from
operator-implication to magnitude-implication:** `_lvr_trivial`
normalizes every comparison to whether increasing the literal narrows
(strengthens) or widens (weakens) the constraint — `expr > L`/`expr >=
L` (literal on the right) narrows as L increases; so does `L <=
expr`/`L < expr` (literal on the left, an equivalent "expr >= L"
constraint); the other two operator/side combinations widen as L
increases. From there, ROR's own rule applies unchanged: narrowing is
trivial for `requires` (skip), widening is trivial for `ensures` (skip).
**EQ/NE literals have no such filter at all** — changing an equality's
target value is neither a superset nor subset of the original in either
direction — always sent to real verification. **Function-body literals
have no requires/ensures role to apply the principle to at all** — sent
straight to verification unfiltered, mirroring AOR's function-body
precedent.

**Real run matched the scoping session's hand-derived prediction exactly,
site by site:** 14 raw mutants (7 sites × 2 candidates), 4 filtered as
`filtered_magnitude_implied`, 10 sent to real verification — **all 10
genuinely killed, zero survivors.** Confirmed examples: widening
`concentrationMgPerMl > 0.0` to `> -0.01` is killed via `ExpectedDose`'s
own unchanged `requires > 0.0` at the pinning clause's call site (a
precondition-call violation, not a postcondition failure — still a
correct, real kill); narrowing `0.0 <= dose <= maxSafeDoseMgPerHr`'s
first literal to `0.01 <= dose` is killed since the implementation
genuinely produces `dose == 0.0` exactly on reverse flow; both
function-body literal mutants (the `< 0.0` comparison threshold and the
bare `then 0.0` return value) are killed because any mismatch between
`ExpectedDose`'s mutated definition and the method body's unchanged,
actual computation breaks the pinning clause for some input in the
perturbed range. The one named, unresolved tension from scoping (whether
the clinical floor is the right test for REQ-GIP-1-8-1's *exact-zero*
safety requirement specifically) didn't need resolving to get a clean
result here — the function-body zero-literal mutant was killed at the
±0.01 granularity regardless — but the underlying judgment call remains
open for whenever a different domain or requirement makes it matter.

**Combined final state across all five operator classes:** 56 mutants —
41 killed, 6 filtered_static, 4 filtered_chain_incompatible, 1
filtered_ar_group_incompatible, 4 filtered_magnitude_implied — **zero
survived, zero unclassifiable.**

**Tests:** `tests/test_dafny_mutate.py` grew from 19 to 25 (new:
literal-site location with correct comparison-operand/side tracking on
the real spec, a refusal test for a hypothetical non-adjacent literal,
function-body literal-site location, a direct unit test of
`_lvr_trivial` against hand-derived cases independent of the real spec,
a check that the generation-time half of the prediction — 14 raw, 4
filtered — matches, and a byte-level check that mutation changes exactly
the targeted literal). `tests/test_mutation_report.py` grew from 7 to 8
(a direct check that all 10 real-verified LVR candidates are killed,
locking in the real-verification half of the prediction against the
committed capture). Full suite: **138 passed** (131 + 7 new).

## Phase C Gate C6 — NL-dialogue confirmation: BUILT and SIGNED OFF (2026-07-07)

### What this gate is for

Per the roadmap, Gate C6 is a process-control fix aimed directly at
recurrence of Gate 1's original finding: a spec/requirement-text mismatch
that was caught only at review time, not authoring time. The fix is to
generate a plain-English summary of what a Dafny method's contract
actually asserts and get explicit human sign-off that the summary matches
intent, at the time the spec is authored. The roadmap is explicit that
"the actual artifact is a recorded decision... not a database entry" —
the summary generator is a means to that end, not the deliverable itself.

### What was built

`evidence/dafny_nl_summary.py::summarize_method(source, method_name)`
does two honest, mechanical things and nothing more:

1. Extracts each requires/ensures clause verbatim (ground truth), plus
   any `REQ-ID` cited in a trailing `//` comment, exactly as authored —
   never inferred from the method name or surrounding prose.
2. Produces a best-effort English "gloss" of each clause via a small,
   fixed operator-substitution table (`&&`/`||`/`==>`/`<==>`/comparisons
   → words). Labeled explicitly as a template, not comprehension — the
   raw clause is always shown first and is the authoritative artifact.

Reuses `evidence/dafny_spec_lint.py`'s existing, already-tested Gate C3
parsing surface (`_find_method_header`, `_parse_params`,
`extract_requires_clauses`, `extract_ensures_clauses`) rather than
reimplementing Dafny parsing. Citation extraction needed a separate,
comment-preserving line-based scan (`_extract_annotated_clauses`), since
the existing extractors strip comments before this module ever sees the
text.

### Scope boundary, checked not assumed

Only single-line requires/ensures clauses are supported — true of every
real clause in this repo today. A multi-line clause would silently break
the citation-association logic if unnoticed, so `summarize_method()`
cross-checks its own line-based extraction against `dafny_spec_lint`'s
canonical, multi-line-capable extractor and refuses (`SystemExit`, Tier
1) on any mismatch, rather than risk a dropped or misattributed citation.

**Self-caught bug:** the first draft of that refusal check compared
clause *counts* between the two extractors, not content. Manual testing
against a synthetic multi-line `requires x > 0\n  && x < 100` clause
found this didn't raise — both extractors happened to return the same
count (1) even though the line-based scan had silently truncated to just
`x > 0`, dropping the `&& x < 100` continuation, while the canonical
extractor correctly joined the whole clause. Same count, silently wrong
content. Fixed by comparing whitespace-normalized clause text instead of
counts; re-verified the multi-line case now raises correctly and the real
`dosage.dfy` spec still summarizes correctly. Caught and corrected before
the test suite was even written, matching this repo's established
"verify empirically, don't assume" discipline (e.g. Gate C4's self-caught
500.0-vs-50.0 wrong-value mistake).

### Tests and verification

`tests/test_dafny_nl_summary.py` — 7 tests: parameters and preconditions
listed correctly against the real `dosage.dfy` spec; each postcondition
cites the right requirement (or explicitly "no requirement cited" for the
pinning clause, which cites none) — the load-bearing property, since a
wrong citation here is exactly the defect class this gate exists to
catch; common operators glossed to words; the multi-line refusal
regression described above; a method with no requires/ensures still
summarizes cleanly; and output is byte-identical across repeated calls
(no timestamps or randomness, since this feeds a committed artifact).
Full suite after this gate: **105 passed** (98 prior + 7 new).

### The sign-off itself

`examples/dosage_calculator/nl_confirmation_dosage_dfy.md` records the
actual deliverable: the generated summary for
`dosage.dfy::CalculateHourlyDose` was presented to Steven, who confirmed
it 2026-07-07 ("it's good for the spec as is"). He also flagged a
next-phase item at sign-off time — adapting the spec and explaining, for
a regulatory submission, how results get analyzed by downstream software
— which he explicitly scoped out as separate follow-up work, not part of
this gate's deliverable.

**Explicitly not done here:** this gate is not wired into
`build_matrix()`, `generate_artifacts.py`, or any other generator, and no
automated mechanism forces future Dafny specs through it — it is a
process habit applied by whoever authors a spec, matching the roadmap's
own framing ("no technical dependency on any other Gate C item... adopt
it as a habit"). The next-phase adaptation/regulatory-analysis work
Steven flagged is not started and is not part of this gate.

## Gate 2 / C2-C4 wiring — real Dafny evidence reaches a live matrix row (2026-07-07)

Requested directly: "we need z3 integration and invocation in order to
reach PROVEN status, in concurrence with gate 5 extension." Before
building, three genuinely consequential design decisions were confirmed
with Steven rather than guessed at — this is the single highest-stakes
change to this repository's structural guarantees since ruling R1 itself
(the first time PROVEN would ever appear in a live rendered row):

1. **Scope: variant C only, for now.** "hmm. can we post hoc verify A
   and B after C variant is proven?" — variants A and B are deliberately,
   explicitly deferred. This creates a real, temporary cross-variant
   divergence (below), named and tracked, not silently permitted.
2. **The Z3 gate lives inside the binder itself** (`dafny_record()`),
   not as a separate pipeline stage — mirrors how `symbolic_record`/
   `concrete_record` already refuse on failed captures internally.
3. **Metadata declares the dafny evidence explicitly** (`evidence:
   [{method: dafny, spec_target: ..., dafny_method: ...}]`), consistent
   with Gate 4/5's existing declaration pattern, cross-checked by a new
   Gate 2 CONFLICT Type 1 sub-check rather than bound unconditionally.

### What was built

- **`metadata.schema.c.json`**: `method: dafny` added to the evidence
  enum, with `spec_target` and `dafny_method` required together (via a
  new `allOf` conditional, alongside the existing `concrete_test`/
  `test_id` one).
- **`metadata.c.yaml`**: `evidence: [{method: dafny, spec_target:
  "dosage.dfy", dafny_method: "CalculateHourlyDose"}]` added to
  REQ-GIP-1-4-12 and REQ-GIP-1-8-1 — exactly the two requirements
  `intended_method: "PROVEN"` has named since Phase A/B, and exactly the
  two `dosage.dfy`'s own header comment scopes itself to.
- **`evidence/conflict.py::dafny_binding_conflicts`**: Type 1 identity
  check for dafny evidence — does the declared `spec_target` match the
  file the captured Dafny manifest actually verified? Deliberately a
  no-op when `dafny_store is None` (not merely falsy) — a symbolic/
  concrete build_matrix() call that never intended to bind dafny
  evidence must not be penalized for metadata that also declares it for
  the third view. `run_conflict_gate` gained an optional `dafny_store`
  parameter, defaulting to None everywhere except the new "c-formal"
  call.
- **`evidence/render/matrix_variants.py::dafny_record()`**: the wiring
  itself. Gates PROVEN on two independent, real checks before ever
  constructing a record: (1) `evidence.dafny_spec_lint.check_precondition_satisfiability`
  (Gate C3 vector 1) — refuses if unsat; (2)
  `evidence.dafny_adapter.parse_dafny_capture` (Gate C1) — refuses on
  any non-clean signal, already covering the false-zero guard and the
  Gate C3 vector 3 hardening. `assert_no_realized_proven`'s ruling R3
  still independently re-checks `method`/`verifier_completion_status` at
  the matrix boundary — this function satisfying both today doesn't
  change that; R3 doesn't trust this function's own diligence, by
  design.
- **`_bind_self_describing`** gained an optional `dafny_store` parameter
  (default `None` — "this call doesn't bind dafny evidence at all",
  declared entries silently ignored, not an error — vs. an explicit dict,
  even empty, meaning "this call does bind dafny evidence, and an
  unresolved declared entry is a real refusal"). This `is not None`
  vs. truthiness distinction is what keeps `c-symbolic`/`c-concrete`
  byte-behaviorally unchanged (aside from one new, always-null field,
  below) while enabling `c-formal`.
- **`_shape_method_partitioned`** gained a `dafny` method-filter branch
  and now always carries `verifier_completion_status` on every rendered
  row (previously absent) — load-bearing for R3's row-level check on
  variant C's shape; a harmless `null` no-op for crosshair/concrete_test
  rows, since R3 only inspects it when `strength == "PROVEN"`.
- **`_VARIANT_SPECS`/`_ARTIFACT_TITLES`/`_MARKDOWN_RENDERERS`** gained
  `"c-formal"` entries. `build_matrix()` gained an optional `dafny_store`
  parameter, threaded through to both the binder and the conflict gate.
- **`generate_matrix_c.py`** now renders THREE artifacts
  (`traceability_matrix.formal.json/.md` alongside the existing
  symbolic/concrete pair), assembling `dafny_store` from the real,
  already-committed Gate C1 capture (`dosage.dfy`, `raw_dafny_output.txt`,
  `run_manifest_dafny.json`) — no re-running evidence inside the
  generation pipeline, same discipline as every other capture in this
  repo. Only the formal call's `tool_versions` gains a `"dafny"` key;
  symbolic/concrete's stays exactly as before (confirmed by diff — this
  matters for `tests/test_cli.py`'s byte-comparison, which is unaffected
  since the CLI was deliberately NOT extended with a `"c-formal"` variant
  choice this session — named as a deferred scope decision, matching the
  same phased spirit as variants A/B, not an oversight).

### The result: REQ-GIP-1-4-12 and REQ-GIP-1-8-1 are formally proven, for real

`traceability_matrix.formal.json` — 3 rows: two real PROVEN rows
(`method: "dafny"`, `verifier_completion_status: "completed"`,
`intent_ok: true`) and the pre-existing `system_scope` GAP row for
REQ-GIP-1-4-12 (unchanged in kind, still correctly deferred to
integration testing — a kernel-level Dafny proof says nothing about
whether an integrated system raises the physical alarm signal).
`intent_ok` flips from `False` to `True` for both requirements in this
view — the first time since Phase A that `intended_method: "PROVEN"` has
actually been realized, not just declared.

### The temporary variant A/B divergence — named, tracked, not silently permitted

Since variants A and B don't (yet) bind dafny evidence, their own
`intent_ok` for these two requirements stays `False` — a REAL divergence
from the formal view's `True`, exactly as expected given the phased
scope decision above. The existing fact-equality gate
(`evidence/reconcile.py::run_gate`, `VARIANT_ARTIFACTS`) is deliberately
**unchanged** — `traceability_matrix.formal.json` is not in
`VARIANT_ARTIFACTS` and never touches that gate, so the pre-existing,
strict A==B==symbolic==concrete check keeps passing exactly as before
(confirmed: `intent {'REQ-GIP-1-4-12': False, 'REQ-GIP-1-8-1': False,
'REQ-DOSE-003': True}` — byte-identical to before this wiring).

A new, separate, narrowly-scoped check —
`evidence/reconcile.py::run_formal_check` — verifies the formal view's
divergence is EXACTLY the expected one and no other:
`KNOWN_FORMAL_INTENT_DIVERGENCE = frozenset({"REQ-GIP-1-4-12",
"REQ-GIP-1-8-1"})`. Any OTHER requirement diverging is still a hard
failure (`unexpected divergence`); either named requirement diverging in
the WRONG direction (i.e. not `True`) is also a hard failure (`expected
... to be newly proven`) — defense against a corrupted regeneration
silently passing. Wired into `regenerate_all.py` right after the main
fact-equality gate, printing its own PASS line. This carve-out is meant
to be temporary: once variant A/B's own dafny wiring lands, it should be
removed and `run_formal_check` tightened to plain equality (or folded
into `run_gate` outright) — tracked here as the explicit follow-up, not
assumed to happen automatically.

### Tests and verification

`tests/test_dafny_wiring.py` — 15 tests: the real formal artifact has
exactly the two expected PROVEN rows, each satisfying R3; the real
formal artifact passes `assert_no_realized_proven` for real (not a
synthetic fixture); symbolic/concrete/A/B are confirmed completely
unaffected (regression); `dafny_record` refuses an unsatisfiable
precondition and a broken capture (both gates independently exercised);
`dafny_record` accepts the real committed capture; `dafny_binding_conflicts`
catches a spec_target mismatch, a missing capture, and correctly no-ops
when `dafny_store is None`; the real metadata + dafny store combination
has zero conflicts; `run_formal_check` passes on the real committed
artifacts and correctly rejects both an unnamed divergence and a
wrong-direction divergence of a named one; and an end-to-end
`build_matrix("c-formal", ...)` call matches the committed artifact
byte-for-byte. Full suite after this wiring: **93 passed** (78 prior +
15 new). Full `generate_artifacts.py` pipeline re-run end to end,
including the new formal-view check: **PASS**, with the structural
PROVEN sweep (stage 6) now explicitly sweeping
`traceability_matrix.formal.json` too — proving ruling R3 accepts this
real row inside the actual pipeline, not just when
`generate_matrix_c.py` happens to be run standalone.

### Explicitly not done here (as of the variant-C-only build; SUPERSEDED for A/B — see below)

- ~~Variants A and B don't bind dafny evidence at all — deliberately
  deferred, per the ratified scope decision.~~ **Done same day** — see
  "Gate 2/C2-C4 wiring extended to variants A and B" below.
- ~~The CLI was not extended with a `"c-formal"` variant choice or a way
  to supply a `dafny_store` from the command line.~~ **Done same day** —
  `--dafny-captures` landed as part of the A/B extension (it turned out
  not to be optional: once metadata.a.yaml/metadata.b.yaml declared
  dafny evidence, the CLI genuinely could not build those variants
  without it — see below).
- **No generic "wire any future Dafny spec into the matrix" tooling.**
  Still true: this built the ONE wiring path for the ONE spec that
  exists (`dosage.dfy`), the same scope discipline every other Gate C
  mechanism in this repository has followed.

### Gate 2/C2-C4 wiring extended to variants A and B (2026-07-07)

Requested directly, same day as the variant-C-only build: "go ahead and
extend variant A and B now." Confirms the "post hoc" framing from the
scope decision that shipped C first — this is that follow-up landing.

**Declarations.** `metadata.a.yaml` gained `- method: dafny, spec_target:
"dosage.dfy", dafny_method: "CalculateHourlyDose"` in REQ-GIP-1-4-12 and
REQ-GIP-1-8-1's `evidence` lists — the same declaration style Gate 4/5
already established for crosshair/concrete_test.
`evidence/schema/metadata.schema.a.json` gained the matching `dafny`
enum value and `spec_target`/`dafny_method` conditional (identical fix
to what schema.c.json got when C was wired). `metadata.b.yaml` gained
two new shadow pseudo-requirements, `REQ-GIP-1-4-12.formal-1` and
`REQ-GIP-1-8-1.formal-1`, with `implementation: "dosage.dfy::CalculateHourlyDose"` -
the SAME shadow pattern concrete evidence already uses
(`parent_requirement` + implementation), but distinguished as a dafny
shadow by the `.dfy` file extension rather than a separate declared
field. `evidence/schema/metadata.schema.b.json`'s shadow-id pattern was
extended from `\.concrete-[0-9]+` to `\.(concrete|formal)-[0-9]+` to
allow it.

**Binders.** `_bind_declared` (variant A) and `_bind_shadow` (variant B)
both gained an optional `dafny_store` parameter and the same dafny-
record construction `_bind_self_describing` already had — but with a
different default-None behavior, deliberately: variant A/B have no
concept of "a view that legitimately excludes dafny evidence" the way
C's symbolic/concrete sub-views do (their single artifact renders every
declared evidence type together), so a requirement declaring dafny
evidence with no `dafny_store` provided at all is refused outright
(`SystemExit`), not silently skipped. `_bind_shadow` distinguishes a
dafny shadow from a concrete one by checking whether the implementation
file ends in `.dfy` — no new declared field needed, since the file
extension is already meaningfully informative (a real, existing
convention, not a new hack). `_shape_flattened_shadow` (variant B's row
shape) gained the same `verifier_completion_status` field
`_shape_method_partitioned` already carries, load-bearing for ruling
R3's row-level check.

**CONFLICT Type 1 generalized, not duplicated.** `_declared_concrete_bindings`
(the existing generator unifying variant A's evidence-list declarations
and variant B's shadow rows for concrete evidence) needed a real fix: it
previously treated EVERY shadow row's implementation suffix as a
concrete test_id unconditionally, which would have mis-parsed a dafny
shadow's `dafny_method` as a bogus test_id and crashed with a false
"declared test_id not found" error. Fixed to skip `.dfy`-suffixed shadow
rows (now correctly recognized as dafny bindings, not concrete ones). A
new, parallel generator, `_declared_dafny_bindings`, unifies dafny's own
two declaration shapes (A/C's evidence list, B's `.dfy`-suffixed shadow
rows) the same way — `dafny_binding_conflicts` was rewritten to use it,
so Type 1 now genuinely covers variant B's dafny bindings too, not just
A/C's.

**Intent parity required extending dafny_store to symbolic/concrete too,
not just formal.** `generate_matrix_c.py` now passes `dafny_store` to
ALL THREE of its `build_matrix()` calls, not only `"c-formal"` — a real,
necessary consequence of extending A/B: since `derive_intent()` runs
inside each `build_matrix()` call using that call's own bound records,
`c-symbolic`/`c-concrete` would otherwise keep computing `intent_ok =
False` for the two now-proven requirements while A/B (and formal) say
`True`, breaking the fact-equality gate for real. Their RENDERED rows
are unaffected either way (the shape function still filters to
crosshair/concrete_test only) — only their internal intent computation
changes. Only `"c-formal"`'s header advertises the dafny tool version;
symbolic/concrete's stays crosshair-only, since only formal actually
renders a dafny row (verified by diff).

**The fact-equality gate itself required two real changes, not zero.**
`evidence/reconcile.py::VARIANT_ARTIFACTS` now includes
`traceability_matrix.formal.json` as a full fifth member — no longer
carved out. `facts_c` is now the union of symbolic, concrete, AND formal
(previously symbolic ∪ concrete only), representing variant C's true
three-way total claim against A's and B's single-artifact totality. The
intent comparison changed from strict dict equality to **subset
comparison**: `traceability_matrix.formal.json` will *permanently* lack
an opinion about REQ-DOSE-003 (dosage.dfy's own header comment
explicitly excludes it — this is not a temporary gap, it's a real,
durable scope boundary), so requiring its intent dict to be identical to
A's (which always has an opinion about every requirement) was never
going to hold. The new rule: every requirement a view DOES have an
opinion about must still match the reference exactly; a view is free to
have no opinion about a requirement it doesn't cover; a requirement id
the reference has never heard of at all is still a hard failure. The
temporary carve-out mechanism (`run_formal_check`,
`KNOWN_FORMAL_INTENT_DIVERGENCE`) built for the C-only phase is now
retired — deleted from `evidence/reconcile.py`, its call removed from
`regenerate_all.py` — since the divergence it tracked is closed.

**The CLI needed `--dafny-captures`, and this was not optional.** Once
`metadata.a.yaml`/`metadata.b.yaml` declared dafny evidence,
`python -m evidence.cli build --variant a ...` genuinely broke
(`build_matrix()` refuses without a `dafny_store`) — this is a real
regression the A/B extension would otherwise have introduced, not a
nice-to-have. `evidence/cli.py` gained `--dafny-captures <index.json>`:
a small JSON file mapping `"{spec_target}::{dafny_method}"` keys to
*paths* (relative to the index file's own directory) for the spec
source, raw output, and manifest, rather than embedding the actual file
content inline (keeps the index small and hand-readable).
`examples/dosage_calculator/dafny_captures_index.json` is the real,
committed index for the worked example. `"c-formal"` was also added to
the CLI's variant choices (deferred in the C-only build; needed now that
the CLI is being extended anyway).

**The result:** every variant artifact — A, B, C-symbolic, C-concrete,
C-formal — now reports `intent_ok: true` for both REQ-GIP-1-4-12 and
REQ-GIP-1-8-1. `run_gate()`'s facts count is **9**, not 7. Full test
suite: **98 passed** (added `test_reconcile_intent_comparison_is_subset_not_strict_equality`,
`test_variant_a_has_dafny_evidence_and_a_proven_record`,
`test_variant_b_has_dafny_shadow_rows_and_a_proven_record`,
`test_cli_build_matches_committed_with_dafny_captures`,
`test_cli_refuses_variant_a_without_dafny_captures`, and more, in
`tests/test_dafny_wiring.py`; updated `tests/test_cli.py` and
`tests/test_fact_equality.py` for the new committed reality). Full
`generate_artifacts.py` pipeline re-run end to end: PASS.

**Explicitly not done here:** no generic "wire any future Dafny spec
into the matrix" tooling — this extended the ONE wiring path to the
existing metadata for the ONE spec that exists.

## What's left for Gate 2

- CONFLICT rule Type 1: **built AND folded into `build_matrix()`**
  (`evidence/conflict.py`; runs on every `build_matrix()` call, tested
  across all three metadata shapes including variant C, plus a dedicated
  fold-in proof). The frozen base matrix keeps its own explicit check
  (`generate_artifacts.py::stage_base_conflict_check`, since it never
  calls `build_matrix()`).
- CONFLICT rule Type 2: **built**, standalone stage
  (`generate_artifacts.py`, `evidence/conflict.py`) — confirmed to have
  no per-variant home (it's a whole-manifest-set check, like
  fact-equality), so it correctly stays outside `build_matrix()`.
- Binding authorship (Gate 4): decided (option 3) and now implemented
  for all three metadata shapes — variant C's asymmetry is closed.
- Vocabulary-agnostic binder: **Steps 1–4 done.** `build_matrix()` is
  the sole implementation across all four variants, runs CONFLICT Type 1
  internally, and all three generator scripts plus the CLI call it. The
  Step 2 fallback functions (`build_matrix_variant_a/b/c`) and the
  equivalence test that existed to check against them
  (`tests/test_binder_equivalence.py`) are deleted, per Steven's
  direction to get the CLI landed first — git history holds them if
  ever needed again.
- CLI: **built** (`evidence/cli.py`, `python -m evidence.cli build`) —
  proven byte-identical to committed artifacts across all four variants,
  plus Tier-1 error-path coverage (`tests/test_cli.py`, 10 tests).
- **Nothing remains for Gate 2's build.** The only open item in Gate 2's
  scope at all is the CONFLICT rule definition, and that's already
  ratified (see above) — Gate 2 is done.

## Session-scope note (2026-07-05, Turn B4)

The Phase B v3 prompt's Turn B4/B5 spec bodies arrived as placeholder
text; the companion roadmap was supplied separately and is committed as
`payloadguard-evidence-roadmap-phaseB-to-C.md` — its Gate 1 section defines
Turn B4's scope (minimal pipeline, four real variant artifacts as ground
truth, reviewed by Steven before Gate 2 starts). "Four real files" is read
as the four variant JSON artifacts (a / b / symbolic / concrete, each with
its Markdown sibling); the base matrix remains the frozen legacy symbolic
subset per ruling R2c, as the roadmap's own verified-state section records.

## Renal Function Dose Adjustment POC — Phase 1 non-goals and exclusions (2026-07-08, updated same day)

Second, independent proof-of-concept (`examples/renal_adjustment/`,
Phase 1 plan committed as `examples/renal_adjustment/PHASE1_PLAN.md`,
Gate C1 signature sketches in `examples/renal_adjustment/gate_c1_sketch.md`,
Gate 1c audit in `examples/renal_adjustment/GATE_1C_AUDIT.md`),
demonstrating the Gate C1–C6 pipeline generalizes from arithmetic
clamping (`dosage.dfy`) to lookup-table and conditional-branching logic.
Gate 1a and 1b are closed; **Gate 1c performed, found two real gaps, and
closed under two named fallback assumptions (2026-07-08) — Gate 1 is
now closed and Phase 2 has started.** All five core proof functions
(`RoundHalfUp`, `GStage`, `SelectFormula`, `ComposedCeiling`,
`AssessRenalFunction`) are committed to a real `renal_adjustment.dfy`
(Gate C1 equivalent) and verify together for real: `dafny verify`
reports `5 verified, 0 errors`, captured via
`run_verify_renal.py`/`raw_dafny_output_renal.txt`/
`run_manifest_dafny_renal.json` mirroring `dosage.dfy`'s own capture
discipline exactly. `evidence/dafny_adapter.py::parse_dafny_capture`
confirmed to work unmodified against this new capture (not assumed) —
`strength=PROVEN`, `verifier_completion_status='completed'`, the
infrastructure plan's first real end-to-end confirmation for this POC.
**Gate C6 built, and later confirmed 2026-07-11** (NL-dialogue
confirmation, moved earlier per its own recommendation —
`nl_confirmation_renal_adjustment_dfy.md`; see the "Phase D Gate C6
sign-off" section below for the confirmation itself). Building it found
and fixed two real bugs in shared
tooling that dosage.dfy's one method/spec never exercised:
`_find_method_header` (`dafny_spec_lint.py`, shared with `dafny_mutate.py`
and `dafny_nl_summary.py`) only matched `method`, never `function` —
`renal_adjustment.dfy` is the first all-function spec in this repo;
and `_REQ_ID_RE`'s character class silently truncated `REQ-RENAL-1a` to
`REQ-RENAL-1` (no lowercase letters in its pattern), a real citation-
accuracy defect. Both fixed, both regression-tested; 142 tests passing
(up from 138). **Correction, 2026-07-09** — direct challenge on Gate
C6's sign-off review surfaced a self-inconsistent overclaim: `RoundHalfUp`'s
round-half-up tie-break rule had been presented as "KDIGO's own
convention" in `gate_c1_sketch.md` and this spec's header comment, in
the same paragraph that also stated KDIGO specifies no tie-breaking
rule at all. KDIGO's base rounding requirement ("rounded to the nearest
whole number") remains well-sourced; the tie-break choice specifically
is a named, deliberate design decision, not a cited fact — an
authoritative search found the opposite of support (NKF Laboratory
Engagement Working Group guidance, Miller et al., *Clin Chem*
2022;68(4):511-520, PMID 34918062, explicitly defers this to each lab's
own software). Corrected in `sources/kdigo-2024-gfr-staging.md`,
`gate_c1_sketch.md`, `renal_adjustment.dfy`'s header comment, and
`PHASE1_PLAN.md`'s requirements table — no code change, `RoundHalfUp`'s
body is unchanged and still verifies (`5 verified, 0 errors`); only the
sourcing claim was wrong.

**Gate C4 built 2026-07-09 (Spec-Testing Proofs) — both hand-derived
predictions confirmed for real, then fixed for real, not worked
around.** `renal_adjustment_stp_suite.dfy` was run against the original
spec first: REJECT lemmas assuming a wrong candidate value for
`ComposedCeiling` and `AssessRenalFunction` genuinely **failed** to
verify (`0 verified, 4 errors`), confirming both predicted gaps
mechanically — the same under-constrained-postcondition defect class as
`dosage.dfy`'s own original Gate C4 finding. The original spec is
preserved as `renal_adjustment_underconstrained.dfy`; the genuinely
failing capture is
`renal_adjustment_stp_suite_against_underconstrained.dfy`
(`raw_dafny_output_stp_suite_against_underconstrained_renal.txt`),
mirroring `dosage_stp_suite_against_underconstrained.dfy`'s honesty-
exhibit pattern exactly. Fixed with proper pinning `ensures` clauses —
`ComposedCeiling` gained a clause forcing its result to equal one of
its two inputs (which, combined with the existing `<=` bounds, pins it
to their minimum exactly); `AssessRenalFunction` gained two clauses
referencing its own composition (`GStage(RoundHalfUp(...))` /
`RoundHalfUp(...)`), the same self-referential pattern `ExpectedDose`
uses in `dosage.dfy`. Re-verified: `renal_adjustment.dfy` still `5
verified, 0 errors`; the full STP suite now `44 verified, 0 errors`.
`RoundHalfUp`, `GStage`, and `SelectFormula` were confirmed genuinely
tight on the first run — no fix needed for those three. Gate C6's
sign-off document amended for the two changed functions'
postconditions.
Named limitations/exclusions and open gaps, per this repo's "name it,
don't guess it" discipline:

- **No function computes the actual CKD-EPI eGFR numeric value —
  remains caller-supplied, confirmed as a toolchain limit, not a scope
  preference.** Cockcroft-Gault CrCl, by contrast, is now computed:
  **RESOLVED for Cockcroft-Gault, 2026-07-09** — `CockcroftGaultCrClMlPerMin`
  and `AssessRenalFunctionFromInputs` are committed in
  `renal_adjustment.dfy` (`7 verified, 0 errors`, up from 5) and STP-covered
  (`52 verified, 0 errors`, up from 44) — see `GATE_1C_AUDIT.md`'s
  2026-07-09 addendum and `PHASE1_PLAN.md`'s "Verification" section.
  CKD-EPI eGFR stays caller-supplied because Dafny/Z3 cannot express its
  real-valued fractional exponents on a variable base (`Scr^-1.200`,
  `Scr^-0.302`, etc.) — a genuine toolchain expressiveness gap. **Actually
  tested empirically for the first time 2026-07-10**, not just carried
  forward as domain-informed reasoning: the 2026-07-09 entry below
  claimed this was "checked a second time," but that check was
  circular — `GATE_1C_AUDIT.md` deferred to this file's sourcing
  document, which explicitly says the toolchain question is out of its
  scope and defers back. Neither ever ran Dafny against the actual
  claim. Caught by direct challenge; two real probes committed
  (`examples/renal_adjustment/run_verify_pow_probes.py`): Dafny has no
  real-exponentiation primitive at all (`unresolved identifier: Pow`),
  and the obvious workaround — declaring it an unproven axiom — verifies
  trivially even for an absurd, wrong claim about it (`2 verified, 0
  errors` for a lemma asserting `Pow` always returns `0.0`), confirming
  that path would be a DECLARED assumption wearing PROVEN's clothing,
  not a real fix. Full detail: `GATE_1C_AUDIT.md`'s 2026-07-10 addendum.
  A proposed lookup-table workaround doesn't eliminate the trust
  boundary either, only relocates it (the LUT itself would need
  independent verification against the formula). Source re-verification
  for the Cockcroft-Gault closure also
  caught a real, minor attribution error: earlier notes (this file's
  prior entry, `GATE_1C_AUDIT.md`'s NHS SPS hand-trace, `sources/README.md`)
  called the derived 1.23/1.04 multiplier "MHRA's constants" — a direct
  re-fetch of the MHRA source page confirmed MHRA states no formula or
  constant at all; the figures are standard unit-conversion arithmetic
  (88.4 µmol/L per mg/dL) applied to the sourced 1976 Cockcroft-Gault
  formula, not an MHRA-specific number.  `renal_adjustment.dfy` uses the
  unrounded exact fraction, not the rounded 1.23/1.04, so no unsourced
  rounding decision is baked into a proven artifact.
- **`evidence/dafny_nl_summary.py` only supports single-line `requires`/
  `ensures` clauses — a real, named tooling constraint, found 2026-07-09.**
  Discovered when `AssessRenalFunctionFromInputs`'s first draft used
  multi-line `ensures` (the only such clauses in this repo's Dafny
  specs); the tool correctly refused to summarize rather than guess a
  citation association, per the same discipline behind its two Gate C6
  fixes on 2026-07-08 (`_find_method_header`, `_REQ_ID_RE`). Not fixed in
  the tool — the function was reformatted to single-line `ensures` to
  match every other function in this repo's spec files, which was
  already the established convention this function had accidentally
  broken from, not a genuine spec need for multi-line clauses. If a
  future spec genuinely needs a multi-line clause, this constraint will
  need real engineering, not another reformat.
- **`GStage` must not be applied to a Cockcroft-Gault CrCl value —
  RESOLVED 2026-07-08.** Its boundaries are derived from KDIGO's
  eGFR-specific G1–G5 table; CrCl isn't BSA-normalized and isn't staged
  the same way clinically. Found via hand-tracing the NHS SPS example
  (CrCl 37 vs. eGFR 53, the same divergence that motivates
  REQ-RENAL-2's formula-selection branch). Fixed by a dispatcher
  function, `AssessRenalFunction`, whose tagged-union return type
  (`EGFRAssessment` vs. `CrClAssessment`) makes the category error a
  type-level impossibility rather than a calling convention — see
  `gate_c1_sketch.md` section 5 and `GATE_1C_AUDIT.md`'s addendum.

- **Per-drug numeric dose-reduction factors are not sourced or proven.**
  BNF/SPC/Renal Drug Handbook disagree at the individual-drug level.
  Scoped as a versioned, human-signed-off configuration input (Gate
  C6-style), mirroring how `dosage.dfy` treats `maxSafeDoseMgPerHr` as a
  parameter, not a baked-in constant. The proof establishes correct,
  monotonic, bounded *application* of a supplied factor, not the
  clinical correctness of the factor's numeric value.
- **Paediatric renal dosing is out of scope for v1 — settled, not just
  assumed.** No free UK paediatric renal-dosing standard exists at the
  level of the adult sources used here; explicit adult-only precondition.
- **Combined creatinine-cystatin C eGFR (eGFRcr-cys) is settled as named,
  not built.** A closed-form 2021 CKD-EPI creatinine-cystatin-C equation
  exists and is fully provable (Inker et al., *NEJM* 2021;385(19):1737–
  1749, PMID 34554658, verified directly against PubMed) — not a
  feasibility gap — but cystatin C isn't routinely measured in UK
  practice, making the branch near-permanently unreachable with real
  data. Documented as a future extension.
- **`REQ-RENAL-3`'s original "unstable renal function" framing was never
  independently corroborated** by any source fetched, and has been
  merged into `REQ-RENAL-6` (AKI reassessment) rather than kept as a
  separately-sourced claim — see `sources/kdigo-2024-gfr-staging.md` and
  `PHASE1_PLAN.md`'s requirements table.
- **New: `SelectFormula`'s drug-classification flags (`REQ-RENAL-8`) are
  caller-supplied, and their provenance is explicitly parked pending
  real-world process data.** The proof establishes correct branching
  given the flags, not that a given real-world drug was correctly
  classified — MHRA's own drug lists are illustrative, not closed, so
  hardcoding them would embed a false-completeness claim inside a
  formally "proven" artifact. Who sets the flags and by what process
  (clinician form / EHR lookup / static versioned list) is a named,
  deferred item — as of 2026-07-11 Steven is actively gathering that
  data by talking to the relevant people, and the row is deliberately
  left an explicit GAP until it's in hand. Its resolution will be a
  DECLARED process fact, never a Dafny proof — see `PHASE1_PLAN.md`'s
  "Still open" section.

## Phase D Gate C3/C5 — renal_adjustment.dfy spec lint and mutation testing (BUILT 2026-07-09)

**Gate C3 (spec lint):** all seven functions `sat` on vector 1
(satisfiable preconditions, no vacuous proofs); five have expected
vector 2 warnings (one-way `==>` clauses used for exhaustive branch
dispatch, all independently STP-covered by Gate C4). Found and fixed a
real gap: `check_precondition_satisfiability` built a Z3 symbol for
every declared parameter regardless of use, refusing on
`AssessRenalFunction`'s unused `Formula`-typed parameter — narrowed to
only model parameters actually referenced by a `requires` clause; a
referenced unsupported-type parameter still refuses, unchanged. Full
detail: `tests/test_renal_adjustment_spec_lint.py`.

**Gate C5 (mutation testing):** 450 mutants across all seven functions
(no single top-level `method` here, unlike `dosage.dfy` — each function
is its own independent proof target) — 250 killed, 137 filtered
pre-verification, 51 survived, 10 unclassifiable, 2 blocked. Four real
gaps found and fixed in the shared `evidence/dafny_mutate.py` engine:
(1) its lexical tokenizer had no `DOT`/`QUESTION` tokens, so
`RoundHalfUp`'s `.Floor` and `AssessRenalFunction`'s
`.EGFRAssessment?`/`.CrClAssessment?` raised "unsupported syntax" —
fixed, the same class of extension as the existing COMMA/SEMI tolerance;
(2) LVR always formatted mutated literals as decimals, breaking Dafny's
static typing on this spec's many int-typed boundary literals
(`roundedEgfr >= 90`, `ageYears < 140`) — `dosage.dfy`'s own literals
were all already real-typed, so this never surfaced before; fixed so a
literal's own lexical form (decimal point or not) determines whether its
mutant stays int (+/-1) or real (+/-0.01).

Two real engine gaps found and **named, deliberately not fixed**:
`RoundHalfUp` and `CockcroftGaultCrClMlPerMin` each have an ensures
clause literal embedded in arithmetic rather than directly adjacent to a
comparison operator (the LVR clause-literal locator's documented Tier-1
scope boundary) — recorded as `blocked_lvr_clause_literal` (2 mutants);
`SelectFormula`'s flat, unparenthesized six-term `||` chain makes any
`||`→`&&` LOR mutation a genuine Dafny "Ambiguous use of && and ||"
parser rejection — recorded as `unclassifiable` (10 mutants). Both are
real new engineering (chain-grouping for `&&`/`||`, arithmetic-aware
literal-role inference), not bounded fixes, and Gate C4's STP suite
already independently proves what either extension would additionally
cover.

**All 51 survivors are explained, not an undifferentiated pile** — three
named categories (full derivation in
`examples/renal_adjustment/README.md`'s Gate C5 amendment,
locked in as regression assertions in
`tests/test_renal_mutation_report.py`): (1) **33** ROR/LVR mutations
narrowing a one-way `==>` clause's antecedent — mathematically
guaranteed to survive regardless of spec correctness, a structural blind
spot of this technique against guard-style clauses, not a proof gap; (2)
**17** `requires`-clause weakenings Dafny can still satisfy because the
specific `ensures` clauses currently proven don't depend on them (e.g.
`ComposedCeiling`'s pinning postconditions hold for any real
`existingCeiling`/`renalCeiling` pair, not just positive ones) — not a
defect, the preconditions still correctly document real domain facts,
just aren't proof-necessary for what's currently established; (3) **1**
coincidental numeric survivor on `RoundHalfUp`'s self-referential
postcondition, independently resolved by Gate C4's STP suite regardless.

**Gate C6's sign-off is now the only thing left before this example's
Phase 2 is done.**

## PayloadGuard CI gate — third-party pre-merge scan (wired 2026-07-10)

`.github/workflows/payloadguard.yml` runs
`PayloadGuard-PLG/payload-consequence-analyser` (pinned to a commit SHA,
`fe6833887f34e77e53cf7e1dcf73c37297f5fea3`, tag `v1.3.0` — not a mutable
tag) on every pull request into `main`. Discovered and wired after a
real CI failure on an earlier PR surfaced that the composite action's
own `action.yml`, as published, resolves several of its own steps
(`actions/setup-python`, `actions/github-script`) by tag rather than
SHA — the same mutable-reference risk this repo pins against everywhere
else. `payloadguard.yml` itself pins `actions/checkout` to a SHA
(`11bd71901bbe5b1630ceea73d27597364c9af683`, v4.2.2); the third-party
action's own internal tag references are outside this repo's control
and are named here, not silently trusted.

**Exit-code contract, confirmed by reading `analyze.py` directly, not by
trusting the wrapper's shell logic or the tool's own `--help` epilog**
(which itself underspecifies the CAUTION verdict): `main()` exits 0 for
SAFE, REVIEW, or CAUTION alike — none of these three block merge — exits
1 when the analysis itself errored, and exits 2 only for a DESTRUCTIVE
verdict. `payloadguard.yml`'s "Enforce verdict" step gates on exit code
1 or 2, matching this contract; blocking on exit 1 (not just 2) is a
deliberate choice beyond the tool's own contract — a scan that couldn't
complete is treated as fail-closed here, not as an automatic pass. The
four-way SAFE/REVIEW/CAUTION/DESTRUCTIVE distinction itself lives only
in the markdown report the action posts as a PR comment, not in the
exit code — that comment is the actual finding to read, this gate only
answers "did the scan run clean and non-destructive."

**One real, minor wrapper quirk, not a gating bug:** the composite
action's own `Run PayloadGuard` step labels its `verdict` output
`"SAFE"` for any exit-0 result, even a true REVIEW or CAUTION internally
(`action.yml`'s `case $EXIT` only special-cases 0 and 2, mapping
everything else including a real REVIEW/CAUTION to the `"SAFE"` label).
`payloadguard.yml`'s enforcement step gates on `${EXIT_CODE}` directly,
never on `${VERDICT}`, so it isn't affected — but the quirk is real and
is called out explicitly in that workflow file's own comments so a
future edit doesn't "simplify" the gate by trusting `${VERDICT}`
instead.

**What this entry does not claim:** this is scrutiny of the wiring and
the documented contract, not an independent audit of the scanner's
detection logic itself — whether PayloadGuard actually catches the
classes of destructive change its README claims to is unverified here.
A sibling repo, `payloadguard-test-harness` (PayloadGuard's own
41-case adversarial/validation suite across five tracks), was located
and its README read, but its actual test contents and pass/fail history
were not — checked via `WebFetch` only under a tooling restriction that
blocked cloning it, so its claims about PayloadGuard's own detection
accuracy are named here as unverified, not relied upon. `runtime-mode`
(the eBPF process-killing agent) and `auto-remediate` (the tag-to-SHA
auto-PR feature) are both left at their safe defaults (`disabled`/
`false`) in `payloadguard.yml`, deliberately, per the comments in that
file — turning either on is a materially bigger blast-radius decision
this entry does not make on its own.

## Phase D Gate C6 sign-off — `renal_adjustment.dfy` confirmed and closed, against the raw KDIGO/MHRA sources directly (2026-07-11)

Gate C6's mechanical build for `renal_adjustment.dfy` (all seven
functions summarized, two tooling gaps found and fixed, two documented
amendments — Gate C4's pinning fixes, then the Cockcroft-Gault
computation addition) had sat with its Decision section reading
"Pending" since 2026-07-08/09. Before recording an actual decision, the
existing artifact was re-verified for drift, not assumed still accurate
just because nothing had touched it recently: `summarize_method()`
re-run fresh for all seven functions and diff-checked against the
committed `nl_confirmation_renal_adjustment_dfy.md` — byte-identical,
no drift (confirming the multi-line-clause extension built the same day
for `drug_interaction_checker`'s own Gate C6 didn't silently change
behavior for `renal_adjustment`'s single-line clauses). `dafny verify
renal_adjustment.dfy` and `dafny verify renal_adjustment_stp_suite.dfy`
both re-run live: `7 verified, 0 errors` and `52 verified, 0 errors`
respectively, matching the committed captures exactly.

**The actual sign-off review checked every claim against the real
source, not the confident tone it was presented in.** Six checkpoints,
each independently re-verified against the primary source files
already committed in `sources/`:

1. **`RoundHalfUp`'s tie-break framing** — confirmed against
   `sources/kdigo-2024-gfr-staging.md` line 51 (KDIGO's own text: only
   "rounded to the nearest whole number," no tie-break specified) and
   line 137 (no single authoritative source specifies round-half-up
   over round-half-even). The spec's own framing — base rounding is
   KDIGO-sourced, the round-half-up tie-break specifically is a named,
   uncited design decision — is accurate, not overclaimed.
2. **`GStage`'s boundaries** — confirmed exact against
   `sources/kdigo-2024-gfr-staging.md` line 31 onward: G1 ≥90, G2
   60–89, G3a 45–59, G3b 30–44, G4 15–29, G5 <15, matching all six
   `ensures` clauses verbatim.
3. **`SelectFormula`'s BMI thresholds** — confirmed against verbatim
   MHRA wording, `sources/mhra-renal-formula-selection-2019.md` line 31
   ("patients at extremes of muscle mass (BMI <18 kg/m2 or >40
   kg/m2)") and line 33 (strict inequality confirmed directly — exactly
   18.0 or 40.0 does not trigger Cockcroft-Gault), matching `bmi <
   18.0 || bmi > 40.0` exactly. All five formula-selection conditions
   (lines 14-17) present and matching, including "aged 75 and older"
   correctly mapping to the spec's inclusive `ageYears >= 75`.
4. **`ComposedCeiling`/`AssessRenalFunction`'s Gate C4 pinning fixes** —
   confirmed matching intent via the live STP suite re-run above
   (`52 verified, 0 errors`, unchanged) plus a direct logical check: the
   third `ComposedCeiling` clause combined with its two `<=` bounds
   forces the result to the minimum by cases; `AssessRenalFunction`'s
   two new clauses pin the exact composed value while its original two
   constructor-only clauses still preserve Gate 1c Finding 2's
   type-safety guarantee.
5. **The eGFR/CrCl split's forced asymmetry** — confirmed by re-running
   both Pow-expressiveness probes live:
   `dafny_pow_expressiveness_probe.dfy` still genuinely fails to
   resolve (no real-exponentiation primitive in Dafny),
   `dafny_pow_axiom_trap_probe.dfy` still verifies cleanly (`2 verified,
   0 errors`) even for an absurd axiom-backed claim — both match the
   established 2026-07-10 finding exactly, not just cited from memory.
6. **The document's own open question** ("does 'CrCl computed, eGFR
   still caller-supplied' match what was meant by closing Finding 1 'for
   Cockcroft-Gault only'?") — confirmed yes: "for Cockcroft-Gault only"
   scopes the closure precisely to the branch where the maths is
   actually expressible, leaving the other branch explicitly open, not
   silently hedged.

**One supporting citation flagged, not silently absorbed.** A claim
that "Sheffield and BSW" clinical-calculator sources corroborate the
88.4 µmol/L conversion factor was checked and could not be verified —
no such source document exists anywhere in this repository's `sources/`
directory, and neither name appears in any committed source file. Not
recorded as confirmed. The underlying claim it was attached to (88.4 is
standard unit-conversion arithmetic, not an MHRA-specific number) does
not depend on the unverified citation — it was already independently
established via a direct MHRA source re-fetch in this file's own
2026-07-09 amendment (see `sources/mhra-renal-formula-selection-2019.md`).
Consistent with this repo's standing discipline: an external claim gets
checked against a real primary source before it's trusted, not accepted
on the strength of how confidently or thoroughly it's presented — the
same discipline that caught a real mislabeling in this session's own
`drug_interaction_checker` Gate C6 sign-off the day before (see "Phase E
Gate C6 sign-off" below).

**Gate C6's Decision section recorded, closing the gate.**
`renal_adjustment` now has all six Gate C1–C6 pipeline steps both built
and confirmed, matching `drug_interaction_checker`'s status. Remaining
work on this example: the named, deliberately unbuilt requirements
(`REQ-RENAL-3`, `REQ-RENAL-4`, `REQ-RENAL-6`, `REQ-RENAL-7`) and
`REQ-RENAL-8`'s classification-flag provenance question, already
reclassified as a Phase 3 concern, not a Phase 2 blocker.

No `.dfy` file or code changed — docs-only. 190 tests unchanged.

## Phase E Gate C1 — `drug_interaction_checker.dfy` spec + capture: BUILT (2026-07-10)

Third worked example, `examples/drug_interaction_checker/`, testing
whether Gate C1–C6 generalizes to set/list-membership logic — distinct
from `dosage.dfy`'s arithmetic clamping and `renal_adjustment.dfy`'s
lookup-table/conditional-branching shape. Gate 1a (sourced from NHS
SPS's DOAC-interaction guidance) and Gate 1c (three real findings, all
resolved by explicit decision) preceded this build — see
`examples/drug_interaction_checker/PHASE1_PLAN.md` and
`GATE_1C_AUDIT.md`.

**The spec:** `DOAC`/`Agent`/`RiskDirection`/`Outcome`/`InteractionResult`
datatypes; `CheckInteraction(doac, agent, hasOtherBleedingRiskFactors):
InteractionResult` — 63 match arms covering all 15 v1-scoped agents
(11 uniform across all four DOACs, 13 per-DOAC-differentiated, one
conditional on the caller-supplied bleeding-risk flag). A `requires`
clause (`!(doac == Apixaban && agent in {Rifampicin, Carbamazepine,
Phenytoin, Phenobarbital})`) makes the two agents' still-blocked
apixaban cells a provable exclusion at every call site rather than a
silently undefined match arm — Gate 1c Finding 2's resolution, written
as an explicit boolean disjunction rather than a set literal, to stay
within syntax already confirmed supported by Gate C3's
precondition-satisfiability translator (set-literal membership hasn't
been verified against that translator and wasn't assumed to work).
Verifies clean against real Dafny 4.11.0: `1 verified, 0 errors`,
`run_manifest_dafny_ddi.json`.

**A real false-clean result, caught before committing, not after.** An
early draft had no `ensures` clauses at all — `dafny verify` reported
"0 verified, 0 errors." That is not a vacuous pass to be read as
"nothing wrong, nothing to check" — it means Dafny generated **zero**
verification tasks for the function, because match-exhaustiveness is
enforced by the resolver at parse/type-check time (a syntax rule, not
an SMT proof), and a function with no postconditions has no correctness
claim for Z3 to discharge. Confirmed empirically (`dafny verify
--progress Symbol` still reported 0 verified for the no-ensures draft;
`dafny resolve` separately confirmed the file parses and type-checks
fine — the absence of verification tasks was real, not a tooling
glitch). Committing that result as "Gate C1 built, verifies clean"
would have been exactly the kind of overstated evidence this repo's
whole discipline exists to refuse. Fixed by adding three real `ensures`
clauses before committing anything:

1. `CheckInteraction(...).outcome == NotCovered ==> (doac == Apixaban
   && agent == Dronedarone)` — pins REQ-DDI-4's fail-safe: the *only*
   way to reach `NotCovered` is the one real, sourced gap in the source
   page itself, not a silent catch-all.
2. `CheckInteraction(...).outcome == Contraindicated ==> doac ==
   Dabigatran` — every `Contraindicated` cell in this table happens to
   be a dabigatran cell; now a checked fact, not an incidental pattern
   nobody verified.
3. `agent == Digoxin ==> CheckInteraction(...) == InteractionResult(
   NoInteractionExpected, NoRisk)` — pins the one section with a clean,
   explicit negative in the source.

Re-verified after the fix: `1 verified, 0 errors`, real resource cost
113,039 (`--log-format csv`, well under any timeout concern — the
heaviest single verification task recorded across all three worked
examples so far, still completing in well under a second, **until Gate
C4 substantially raised that bar again the same day — see the "Phase E
Gate C4" section below.** Full per-cell pinning of the remaining 60
match arms, originally deferred to Gate C4 here, is now built — not
duplicated as inline `ensures` clauses in this Gate C1 write-up; see
below for what that actually found.

**`evidence/dafny_adapter.py::parse_dafny_capture` parses the real
capture unmodified** — `Strength.PROVEN`, `verifier_completion_status
== "completed"` — the third time this parser has generalized across an
independently-authored worked example with zero code changes (after
`dosage.dfy` and `renal_adjustment.dfy`).

**Gates C2/C3/C5/C6 not yet started** (Gate C4 built the same day, see
below). Two items named, not built: `REQ-DDI-5` (an indication-dependent
third axis for two agents' apixaban cells, needs a `TreatmentIndication`
caller input) and `REQ-DDI-6` (proving the specific numeric
dose-reduction targets, staged as v2 per direct instruction — "both
but in order of difficulty"). Not wired into the metadata/capture/generate
pipeline — same status `renal_adjustment` had at this point in its own
build.

## Phase E Gate C4 — `drug_interaction_checker.dfy` STPs: BUILT, found a real spec gap larger than Gate C1's own (2026-07-10)

IronSpec methodology (`renal_adjustment`'s Gate C4 methodology,
generalized) applied to `CheckInteraction`. Hand-derived prediction
before building anything, per this repo's standing discipline: since
Gate C1's `ensures` clauses only covered 3 of `CheckInteraction`'s 63
match arms, a real IronSpec-style ACCEPT lemma restating just those 3
clauses as premises should **fail** to prove the correct value for any
cell they don't directly mention.

**Confirmed empirically, not just predicted.** A probe lemma for
`(Dabigatran, Ketoconazole)` — which should be `Contraindicated` —
restating only the 3 original clauses as premises, genuinely failed to
verify (`0 verified, 1 error`, "a postcondition could not be proved").
Preserved as a proper honesty exhibit, same discipline as
`dosage_underconstrained.dfy`/`renal_adjustment_underconstrained.dfy`:
`drug_interaction_checker_underconstrained.dfy` (the original Gate C1
spec, byte-for-byte) plus
`drug_interaction_checker_stp_suite_against_underconstrained.dfy` (3
ACCEPT lemmas, one per Gate 1c finding for narrative continuity —
Rifampicin/`ThrombosisRisk`, `CautionLowRelevance`, a plain dose
reduction — genuinely fail: `0 verified, 3 errors`, a real committed
failing capture, not smoothed over).

**This is a materially different, and materially larger, finding than
`renal_adjustment`'s own Gate C4 gap.** There, `ComposedCeiling` and
`AssessRenalFunction`'s postconditions *bounded* a result without
*pinning* it — ACCEPT proofs succeeded against the loose bounds, only
REJECT proofs (excluding a wrong candidate) failed, revealing the gap.
Here, most of `CheckInteraction`'s 60 unpinned cells had **no
constraint at all**, bound or pin — not even an ACCEPT proof of the
*correct* value was possible from the declared spec alone. The match
body's correctness was never actually a claim the function's signature
made; it was purely an artifact of the implementation happening to
compute the right thing.

**Fixed for real**, not just documented as a known gap:
`drug_interaction_checker.dfy` gained 60 explicit pinning `ensures`
clauses, one per match arm (replacing the original 3, which are now
strictly subsumed) — verbose, deliberately: an honest reflection of
this function's actual shape (a flat 63-cell lookup table with no clean
range partition to exploit, unlike `GStage`'s six boundary clauses).
Re-verified clean: `1 verified, 0 errors`, resource cost 358,399 (up
from 113,039 pre-fix, still completing in 0.42s — nowhere near the 30s
default timeout).

**The real STP suite**, `drug_interaction_checker_stp_suite.dfy`:
7 ACCEPT lemmas covering 6 worked examples already established in
`GATE_1C_AUDIT.md`'s hand-traces (`(Dabigatran, SSRIOrSNRI)` gets two
lemmas, one per branch of the caller-supplied
`hasOtherBleedingRiskFactors` conditional — every other cell gets one),
plus 4 REJECT lemmas: 3 — one per `Contraindicated` cell (`Ketoconazole`,
`Itraconazole`, `Ciclosporin`, all dabigatran-specific), proving a
plausible-but-wrong weaker `Caution` candidate is genuinely excluded,
not just absent from the match arm by accident of how it happened to be
written — plus one more REJECT re-testing Gate 1c Finding 3's specific
ambiguity directly (`Rivaroxaban`+`Verapamil` is provably **not** the
unqualified negative digoxin gets). **11 lemmas total.**

**A real documentation-accuracy bug, found and fixed 2026-07-10**: this
suite's real, reproducible Dafny capture reads `22 verified, 0 errors`
(`raw_dafny_output_ddi_stp_suite.txt`) — and several of this repo's own
docs (this section included, before this fix) had misread that number
as "22 lemmas," rather than checking what it actually counts. It does
not count lemmas: re-run with `dafny verify ... --progress Symbol`
shows `Verified 0/11 symbols` counting up to `10/11` before the final
`22 verified, 0 errors` line — Dafny's own internal unit here is roughly
2 verification tasks per lemma (11 lemmas × 2 = 22), not 1:1. The raw
capture number was never wrong; the prose describing it was. Fixed here
and in `SYSTEM_BLUEPRINT.md`, `HANDOFF.md`, `DEVLOG.md`,
`nl_confirmation_drug_interaction_checker_dfy.md`, and `PHASE1_PLAN.md`
— everywhere this suite's size was stated as "22 lemmas" now correctly
says 11 (7 ACCEPT + 4 REJECT), with the real `22 verified, 0 errors`
capture figure kept but no longer conflated with a lemma count.

**Scope stated explicitly, not left implicit:** this suite does not
restate all 60 pinning clauses as individual lemmas — each `ensures`
clause already *is* the ACCEPT proof for its own cell, so a
one-to-one restatement would be near-pure duplication. The STP suite's
job is to add value the ensures clauses alone don't provide: narrative
continuity with Gate 1c's worked examples, and safety-focused REJECT
coverage for the highest-stakes rows.

`evidence/dafny_adapter.py::parse_dafny_capture` was not re-tested
against this capture specifically (already confirmed generalizing
against Gate C1's capture, above) — the STP suite, like every other
worked example's, is not wired into the metadata/capture/generate
pipeline; matches `renal_adjustment`'s own Gate C4 scope discipline
exactly ("Neither STP suite is wired into `build_matrix()` or any
generator").

## Phase E Gate C3 — `drug_interaction_checker.dfy` spec lint: BUILT, required extending the shared translator (2026-07-10)

`renal_adjustment`'s own Gate C3 gap was a datatype-typed parameter no
`requires` clause ever mentioned — narrowing to "only model referenced
parameters" was enough. `drug_interaction_checker.dfy`'s `CheckInteraction`
is different: its precondition *directly compares* `doac`/`agent`
against named datatype constructors
(`!(doac == Apixaban && agent in {Rifampicin, ...})`, written as an
explicit disjunction in the real source), so narrowing alone doesn't
help — the referenced parameters genuinely need a Z3 representation
`evidence/dafny_spec_lint.py` never had. Confirmed empirically before
touching anything: `check_precondition_satisfiability` refused with
`unsupported Dafny parameter type 'DOAC'`.

**Fixed by extending `_TYPE_MAP`'s coverage, not working around it.**
`DOAC`, `Agent`, `Outcome`, and `RiskDirection` are all *simple* Dafny
datatypes — every constructor takes zero arguments, a finite
enumeration Z3 can represent natively via `EnumSort`. A new
`_parse_enum_datatypes` function finds every such declaration in the
source (handling the multi-line form `Agent`'s own declaration
actually uses, not just a hypothetical), and `build_symbol_table` now
builds one `EnumSort` per referenced enum type, adding each constructor
name as a resolvable symbol alongside the parameter itself — reusing
the parser's existing symbol-lookup path unchanged, the same mechanism
that already resolves `true`/`false`. `InteractionResult`
(`InteractionResult(outcome: Outcome, direction: RiskDirection)`, one
parameterized constructor) is correctly excluded from what
`_parse_enum_datatypes` finds — `EnumSort` has no way to represent
fields, and this module still refuses on it exactly as before, not
mis-modeled.

**A second, independent real bug, caught while building the regression
suite, not by inspection.** Z3 registers `EnumSort` names globally per
process context, not per call — two of this session's own new test
fixtures both happened to declare `datatype Formula = A \| B`, and
running them in the same pytest session raised `z3.z3types.Z3Exception:
enumeration sort name is already declared`. This is a real, generally-
applicable footgun for any future caller of `build_symbol_table`, not
specific to this spec — fixed with a monotonic per-call counter
appended to every registered sort's Z3 name (the human-readable Dafny
type name is preserved as the prefix; only the internal Z3 registration
key is disambiguated).

**Verified against the real, committed spec**, not just the
extension's own synthetic fixtures: `CheckInteraction`'s precondition
is `sat` (`agent = Naproxen, doac = Dabigatran` is one real Z3 model) —
confirming Gate C1's `1 verified, 0 errors` isn't vacuous. Vector 2
flags all 60 pinning `ensures` clauses, exactly as many as exist — the
same "exhaustive, mutually-exclusive dispatch" pattern already
established for `renal_adjustment`'s `GStage`/`SelectFormula`, and
independently backed here by Gate C4's real ACCEPT/REJECT proofs, not
just asserted benign the way the heuristic alone would leave it.

**Test coverage**: `tests/test_dafny_spec_lint.py` gained 5 new tests
for the extension itself (a real-spec true-positive, an unsat case
confirming EnumSort comparisons can still correctly fail, a multi-line
declaration parse, and a parameterized-constructor exclusion test) and
had one pre-existing test rewritten in place —
`test_referenced_unsupported_type_parameter_still_refuses`'s original
fixture (a plain two-constructor enum) became a *supported* case by
this extension, so it was changed to use a parameterized constructor
instead, preserving the original regression-protection intent rather
than deleting it. `tests/test_drug_interaction_checker_spec_lint.py`
(new) is the real-spec application, mirroring
`test_renal_adjustment_spec_lint.py`'s structure exactly.

Vector 3 (timeout/resource masking) needed no per-spec work — already
universal via `evidence/dafny_adapter.py`, confirmed working against
this example's own capture at Gate C1. Vector 4 (specification
stripping) remains BLOCKED, unchanged — not a decision this gate's
build could affect either way.

## Phase E Gate C2 — PROVEN exclusivity confirmed for `drug_interaction_checker` (2026-07-10)

Unlike Gates C3 and C4, this gate found no new gap and required no
shared-code change — its value is confirming an already-built mechanism
actually generalizes, not discovering it doesn't. Worth recording for
exactly that reason: `evidence/render/matrix_variants.py::dafny_record()`
(the only place in the codebase that can produce a dafny-method PROVEN
record) and `assert_no_realized_proven` (ruling R3) were built
2026-07-07 and tested thoroughly against `dosage_calculator`'s real
captures — but never against anything else. `renal_adjustment` never
exercised this path at all; its captures were never wired into a
`metadata.yaml`.

Run for real against `drug_interaction_checker`'s actual committed
capture: `dafny_record(capture, "drug_interaction_checker.dfy::CheckInteraction")`
produces `{"method": "dafny", "strength": "PROVEN",
"verifier_completion_status": "completed"}` — exercising Gate C3's Z3
precondition check (now able to model the datatype comparison, per the
same-day extension) and Gate C1's `parse_dafny_capture` false-zero
guard for real, both against a spec neither was originally written for.
`assert_no_realized_proven` accepts the record cleanly.

**Two negative-case checks, not just the positive one.** `dafny_record()`'s
own docstring makes an explicit claim: "R3 does not trust this
function's own diligence." Tested directly against this example's real
record shape rather than assuming the claim holds because it holds for
`dosage_calculator`'s fixtures — a tampered copy with `method =
"crosshair"` and another with `verifier_completion_status =
"incomplete"` are both independently refused by `assert_no_realized_proven`,
with the same assertion messages `test_proven_exclusivity.py`'s generic
fixtures already established.

**Scope, stated explicitly:** `tests/test_drug_interaction_checker_dafny_wiring.py`
(4 tests) tests the binder and R3 directly, not the full pipeline
`test_dafny_wiring.py` covers for `dosage_calculator` (metadata
declaration, `build_matrix()`, the CLI, fact-equality across variants)
— this example has no traceability matrix yet, Phase 2 not Phase 3, so
there's no fuller pipeline to test against. A real scope boundary, not
an oversight.

## Phase E Gate C5 — `drug_interaction_checker.dfy` mutation testing: BUILT, found and fixed a real crash bug in Gate C3's own code (2026-07-10)

Third worked example testing whether MutDafny-style mutation testing
(`evidence/dafny_mutate.py`'s ROR/LOR/AOR/LVR/COI generators,
`run_mutation_suite_ddi.py` mirroring `run_mutation_suite_renal.py`'s
exact capture/classification discipline) generalizes to a spec whose
comparisons are almost entirely `identifier == Constructor` between
simple-enum Dafny datatype values (`DOAC`, `Agent`, `Outcome`,
`RiskDirection`), not real/int — a genuinely different shape from both
`dosage.dfy` (arithmetic) and `renal_adjustment.dfy` (mostly arithmetic
with one enum). 962 mutants generated against `CheckInteraction`'s one
`requires` clause and 60 `ensures` clauses. AOR and LVR both confirmed
contributing exactly zero mutants — checked directly, not assumed: the
generators themselves return `[]` against this spec, since there is no
arithmetic operator and no numeric literal anywhere in `CheckInteraction`'s
clauses or body (a pure datatype pattern match).

**A real crash, found mid-run, fixed before the run could complete.** A
ROR mutant introducing `<=`/`>=` between two `DOAC` operands (from the
one `requires` clause's `doac == Apixaban` comparison) crashed
`evidence/dafny_spec_lint.py`'s Z3 precondition-satisfiability
translator with a raw Python `TypeError`
(`'<=' not supported between instances of 'DatatypeRef' and 'DatatypeRef'`)
— Z3's Python bindings simply don't overload ordering operators for
`DatatypeRef` the way they do for `==`/`!=` (Z3's generic equality is
universal across sorts; ordering is not). This is a real, generally
applicable gap in a *shared* module, not something specific to this
example: any future spec with a datatype comparison, mutated by ROR
into an ordering operator, would have hit the same crash. **Fixed** in
`_apply_cmp` (changed from a `@staticmethod` to an instance method) by
adding a `z3.is_arith(a) and z3.is_arith(b)` guard before applying
`LE`/`GE`/`LT`/`GT`, raising a clean `SystemExit` instead of crashing —
matching every other unsupported-construct refusal already in that
module. `run_mutation_suite_ddi.py` was updated to catch this
`SystemExit` around its precondition pre-filter call, recording
`"precondition_check_outcome": "z3_translation_refused"` and still
falling through to real Dafny verification for that mutant, rather than
losing the result. One new regression test,
`test_ordering_operator_on_enum_datatype_refuses_cleanly_not_a_crash`,
in `tests/test_dafny_spec_lint.py`. Shipped as its own PR, independent
of this gate's full report, since the fix stands on its own regardless
of what the rest of the mutation run found.

**Final real run (re-run clean after the fix): 962 mutants — 564
killed, 389 filtered_static, 7 survived, 2 unclassifiable.**

The 2 unclassifiable results are both the `<=`/`>=` case above (`==` →
`<=` and `==` → `>=` on the same `doac == Apixaban` comparison) — Dafny
itself genuinely refuses these with a real type error ("arguments to
`<=` must be of a numeric type... instead got `DOAC` and `DOAC`"), not
a parser ambiguity like `renal_adjustment`'s own unclassifiable case. A
materially different failure mode, correctly distinguished rather than
lumped together.

**A correction made and left visible, not silently edited away.** `<`
and `>` between two datatype values, unlike `<=`/`>=`, DO type-check —
Dafny accepts them syntactically for any datatype via a structural
"rank" ordering it uses for termination metrics. An earlier draft of
this gate's own runner-script comments predicted every such mutant
would therefore be "always killed" (guessing the relation was
unconditionally false for a flat, non-recursive enum). Two direct Dafny
probes disproved this: neither `Apixaban < Dabigatran` nor
`!(d < Apixaban)` is provable as a bare claim — for a flat enum with no
recursive constructor argument, Z3 has no axiom pinning the relation
down at all, genuinely unconstrained rather than false. The wrong
prediction was corrected in place in `run_mutation_suite_ddi.py`'s
header comment, left visible with an explicit note that it was wrong
before the real run proved it wrong, rather than rewritten as if the
right answer had been known from the start — matching this repo's
standing discipline of treating incorrect predictions as part of the
record.

**All 7 survivors, explained, falling into the same two structural
categories `renal_adjustment`'s own Gate C5 already established** (no
new category of finding):

- **Category A (4 survivors)** — mutations to the one `requires`
  clause's `doac == Apixaban` comparison (`==`→`!=`, `==`→`<`, `==`→`>`,
  and one LOR `&&`→`\|\|`). None of the 60 `ensures` clauses makes any
  claim about the `(Apixaban, {Rifampicin, Carbamazepine, Phenytoin,
  Phenobarbital})` region specifically — the region this `requires`
  clause excludes — so no proof's provability depends on the exact
  shape of the exclusion. Same category as `renal_adjustment`'s own
  requires-clause survivors: "weakenings not load-bearing for the
  specific ensures clauses currently proven."
- **Category B (3 survivors)** — mutations to the
  `(doac == Dabigatran && agent == SSRIOrSNRI && !hasOtherBleedingRiskFactors)
  ==> ... InteractionResult(Caution, BleedingRisk)` ensures clause's
  `doac == Dabigatran` antecedent (`==`→`!=`, `==`→`<`, `==`→`>`).
  Confirmed directly against the real spec text, not just argued:
  `Caution`/`BleedingRisk` is already separately, unconditionally
  guaranteed for `Apixaban`/`Edoxaban`/`Rivaroxaban`+`SSRIOrSNRI` by
  three sibling ensures clauses — so whatever set of `DOAC` values the
  mutated antecedent ends up matching, the consequent holds regardless.
  Same category as `renal_adjustment`'s own largest survivor group (39
  of 51): "a structural blind spot against guard-style `==>` clauses
  whose consequent happens to be broadly true across cases."

4 new tests, `tests/test_drug_interaction_checker_mutation_report.py`,
pinning the exact 962-mutant outcome-count distribution and directly
asserting both survivor categories against the real spec text (not just
trusting the report's own labels), mirroring
`tests/test_renal_mutation_report.py`'s discipline.

## Phase E Gate C6 — `drug_interaction_checker.dfy` NL-dialogue confirmation: BUILT, genuinely extended the shared summary generator (2026-07-10)

Third worked example testing whether Gate C6's plain-English summary
generator (`evidence/dafny_nl_summary.py::summarize_method`) generalizes
to a spec shape neither `dosage.dfy` nor `renal_adjustment.dfy` ever
presented it with: a genuinely multi-line `requires`/`ensures` clause.

**The refusal, on first attempt, was correct — the point of building
this gate the way it was built.** `CheckInteraction`'s one `requires`
clause:

```dafny
requires !(doac == Apixaban &&
           (agent == Rifampicin || agent == Carbamazepine ||
            agent == Phenytoin || agent == Phenobarbital))
```

spans three physical lines. `summarize_method`'s own design (see its
module docstring, as it stood before this gate) cross-checks its
line-based extraction (needed to preserve trailing `// REQ-ID` citation
comments, which `dafny_spec_lint`'s canonical extractor strips before
this module ever sees the text) against that canonical extractor, and
refuses on any mismatch rather than risk silently dropping or
misattributing a continuation. It refused here, correctly — this is
exactly the first real multi-line clause it had ever been asked to
handle.

**A real decision point, with a documented precedent pointing the other
way.** `renal_adjustment.dfy` hit an equivalent gap for two `ensures`
clauses in `AssessRenalFunctionFromInputs` (see its own
`nl_confirmation_renal_adjustment_dfy.md`), and that time the call was
to **reformat** those two clauses to single-line rather than extend the
tool — reasoning explicitly recorded at the time: "a formatting choice
that was mine, not a genuine spec need," not a tool bug. Reformatting is
free when nothing else has been captured against the file yet.

That precondition didn't hold here. By the time Gate C6 was reached for
`drug_interaction_checker.dfy`, this exact spec already had a committed
Gate C1 capture, an 11-lemma Gate C4 STP suite, and a 962-mutant Gate C5
mutation report — all captured against the file *as currently
formatted*. Reformatting the `requires` clause, even purely
cosmetically (Dafny doesn't care about line breaks; the semantics are
identical either way), would have meant re-running and re-committing
every one of those three artifacts to keep them honestly bound to the
source they claim to verify, for a change with zero semantic content.
**So the tool was extended instead** — the opposite call from
`renal_adjustment`'s, made for a concrete, checkable reason (downstream
artifact cost), not inconsistency.

**Fixed**: `_extract_annotated_clauses` now accumulates a clause across
multiple physical lines. A continuation line is any non-blank line that
isn't a standalone `//`-comment line and doesn't itself open a new
`requires`/`ensures`/`modifies`/`reads`/`decreases` clause; a standalone
comment line (or a blank line) always ends the clause currently being
accumulated. This matters concretely for this spec: a large free-floating
block comment sits between `CheckInteraction`'s `requires` clause and its
first `ensures` clause (explaining the Gate C4 finding that led to the
60 pinning clauses below it) — without the "standalone comment ends
accumulation" rule, that entire comment block would have been swept in
as part of the `requires` clause's own continuation, and worse, silently
searched for a `// REQ-ID` citation that was never meant for it. Any
inline `// ...` trailing comment is still preserved from whichever
physical line it appears on, concatenated in source order if a clause
carries more than one, so nothing is silently dropped either way.

**The original single-line-only regex is preserved, not deleted.**
`_CLAUSE_LINE_RE` is still exported unchanged, because
`evidence/dafny_mutate.py::_locate_clause_sites` imports it by name for
a genuinely different need: byte-precise absolute offsets of a mutation
site within one physical line (Gate C5's ROR/LOR mutants are located and
applied at the character level, not reconstructed as a full logical
clause the way Gate C6's citation-preserving summary needs). This is why
Gate C5's own mutation report could already mutate the `doac ==
Apixaban` comparison inside this same multi-line `requires` clause
successfully (it sits on the clause's first physical line) even before
Gate C6's fix existed — the two modules had different, independently
correct notions of "clause" for their different purposes, and only one
of them needed to change.

**The safety net itself is unchanged in spirit, only what it accepts got
broader.** `summarize_method` still cross-checks its extraction against
`dafny_spec_lint`'s canonical extractor and refuses (`SystemExit`, Tier
1) on any mismatch. A comment sitting on its own line *inside* a
multi-line boolean expression (as opposed to between two clauses) still
correctly refuses: the "standalone comment ends accumulation" rule
orphans the continuation lines after it, producing a truncated clause
that no longer matches canonical extraction — genuinely ambiguous
(which side of the comment does an inline citation belong to?), so
refusing rather than guessing is still the right behavior, confirmed by
a new regression test
(`test_standalone_comment_inside_a_multiline_clause_still_refuses`).

**Verified end-to-end against the real, committed spec**: all 60
`ensures` clauses and the one multi-line `requires` clause reconstruct
byte-for-byte correctly — cross-checked directly against
`summarize_method`'s own output, not just visually inspected, before
being embedded in the sign-off document.

**A real, notable fact this summary surfaces, not a defect.** None of
`CheckInteraction`'s 60 `ensures` clauses carry an inline `//
REQ-DDI-*` citation — every one of the 60 postconditions in the
generated summary reads `*(no requirement cited)*`. Unlike
`dosage.dfy`'s and `renal_adjustment.dfy`'s per-clause `REQ-ID` citation
style, this spec's correctness is validated against
`sources/sps-doac-interactions-2024.md` as a whole lookup table (Gate
1a/1c), not `REQ-ID` by `REQ-ID` — so this is accurate, not a citation
gap, but it's flagged explicitly in the sign-off document for Steven to
confirm is the right traceability model for this shape of spec, rather
than let a reader used to the other two worked examples mistake it for
one.

3 new/changed tests in `tests/test_dafny_nl_summary.py`:
`test_multiline_clause_is_summarized_correctly_not_refused` (replaces
the now-obsolete blanket single-line-only refusal test, rewritten in
place to preserve its original regression-protection intent — a dropped
or truncated continuation still fails this test, it just no longer does
so via a blanket refusal), `test_standalone_comment_inside_a_multiline_clause_still_refuses`
(confirms the narrower, still-genuine refusal case above), and
`test_real_ddi_spec_multiline_requires_clause_summarizes_correctly`
(end-to-end, against the real committed spec). 190 tests pass (up from
188).

**Gate C6's actual deliverable — the recorded human decision, not the
mechanical summary — is presented in
`examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`,
and its Decision section was confirmed by Steven the same day.** See
the standalone follow-up entry below for the real doc-accuracy bug the
sign-off review itself caught before the decision was recorded.

## Phase E Gate C6 sign-off — confirmed, and a real doc-accuracy bug caught in the sign-off document's own text (2026-07-10)

Steven's actual Gate C6 review (not a rubber stamp) checked the sign-off
document's four numbered "worth Steven's attention" items directly
against `sources/sps-doac-interactions-2024.md`, and found a real
mislabeling in item 1's own text — not in the `.dfy` spec, which was
already correct, and not in the STP suite, which was also already
correct.

**What was actually wrong, and where.** The precondition
`!(doac == Apixaban && agent in {Rifampicin, Carbamazepine, Phenytoin,
Phenobarbital})` excludes six cells. The main spec's own comment
(`drug_interaction_checker.dfy`, above the precondition) already
correctly describes this as `"clinical indication (REQ-DDI-5, not built
in v1)"`, and the STP suite's own `"real source gap"` comment is
correctly reserved for a different cell entirely (`ApixabanDronedarone`,
where the source never mentions apixaban at all). The bug was narrower
than first suspected: item 1 of the sign-off document's own "worth
Steven's attention" list called the precondition's exclusion apixaban's
"real source gap" — conflating it with the genuinely-silent Dronedarone
case, both of which happen to justify v1 exclusion but for materially
different reasons. Confirmed verbatim against
`sources/sps-doac-interactions-2024.md` lines 80-84 (rifampicin) and
135-136 (carbamazepine/phenytoin/phenobarbital): the source *does*
address apixaban here — `"use apixaban with caution"` — but only for two
named indications (AF stroke prevention; recurrent DVT/PE prevention),
an explicit indication-dependent branch the source itself flags as
sharing "the same indication-dependent structure" across both rows —
not silence. Fixed in place in the sign-off document, left visible as a
correction rather than silently rewritten, consistent with this repo's
standing practice for a wrong prior claim.

**The precondition itself was never wrong** — both reasons (indication-
dependence, or genuine silence) independently justify the same v1
exclusion; only the sign-off document's own rationale needed
tightening. No `.dfy` file changed.

**Every other sign-off item was independently re-verified against the
real source, not taken on faith**: the `CautionLowRelevance` cells
(verapamil+rivaroxaban, verapamil+apixaban, fluconazole+rivaroxaban)
confirmed verbatim against source lines 57-58 and 104-111 ("unlikely to
be clinically relevant" / "not considered to be clinically relevant");
the two `Contraindicated` cells confirmed against lines 113-121; the
whole-table (not per-clause `REQ-ID`) validation model confirmed correct
against the source's own explicit scope statement (line 26: "not
comprehensive for all potential interactions").

**A programmatic cross-reference check, not just a re-read**: `CheckInteraction`'s
60 `ensures` clauses, the NL summary, and the STP suite's 11 lemmas were
checked against each other with a short script, not by eye — every one
of the 7 ACCEPT lemmas' claimed outcome matches exactly one real
`ensures` clause; every one of the 4 REJECT lemmas' claimed (wrong)
outcome is confirmed genuinely absent from the real `ensures` clause for
that cell. All three artifacts mutually consistent; no drift found.

## Phase 3 — evidence packaging for renal_adjustment and drug_interaction_checker: BUILT, three real gaps found and fixed in shared code (2026-07-11)

Both `renal_adjustment` and `drug_interaction_checker` had Phase 2 (Gate
C1-C6) fully built and confirmed by 2026-07-11, but neither had reached
Phase 3 — the `metadata.yaml` -> `evidence.cli` -> traceability-matrix
pipeline that turns proof captures into the actual regulator-facing
artifact. `dosage_calculator` already had this fully built and served
as the template — but its pipeline had never been pointed at a
Dafny-only metadata file (both new examples have zero crosshair or
concrete_test evidence, having no companion Python/CrossHair
implementation at all).

**Real risk named in the scoping plan, confirmed and resolved for real,
not assumed away.** Running `evidence.cli build --variant a` against a
draft `drug_interaction_checker` metadata file (deliberately built
first, the simpler one-capture shape) surfaced the predicted gap at
three real depths, not just the CLI argparse level the plan anticipated:

1. `evidence/cli.py`'s `--manifest`/`--concrete` flags were hard
   `required=True`, and reading further down the call chain,
   `evidence/render/matrix_variants.py::derive_bounds_block()`
   unconditionally required `manifest["effective_bounds"]` to exist,
   `_header()` and `build_matrix()` both unconditionally indexed
   `metadata["toolchain"]["crosshair_bounds"]`, and
   `evidence/conflict.py::symbolic_binding_conflicts()` unconditionally
   indexed `manifest["target"]` — five separate hard dependencies on a
   crosshair run existing, none of which apply to a Dafny-only spec.
   **Fixed, not worked around**: `manifest=None` (an omitted
   `--manifest`) is now treated as a legitimate "no crosshair evidence
   declared anywhere in this metadata" state throughout the call chain
   — `derive_bounds_block()` returns `declared=effective=None` rather
   than raising or fabricating zero/empty bounds (fabricating bounds
   data would falsely imply a crosshair search happened, exactly the
   kind of overclaim this whole system exists to prevent);
   `run_conflict_gate()` skips `symbolic_binding_conflicts()` entirely
   when `manifest is None`, mirroring `dafny_binding_conflicts()`'s own
   already-established `dafny_store is None` no-op precedent exactly,
   not inventing a new convention. `--concrete` (an omitted
   `--concrete`) defaults to a real, honest `{"cases": []}` instead of
   `None` — an empty test list is a genuine state every binder's
   `concrete_store["cases"]` lookup already handles correctly, not a
   fabrication the way invented bounds data would be, so no code change
   was needed on that side beyond the CLI default itself.
2. The metadata schema's `toolchain.crosshair_bounds` was unconditionally
   `required` in all three schema files (`metadata.schema.a.json`,
   `.b.json`, `.c.json`) — relaxed to optional in all three, a real,
   backward-compatible schema change (existing `dosage_calculator`
   metadata still declares the field, so relaxing "required" to
   "optional" changes nothing for it).
3. The schema's `id` pattern, `^REQ-[A-Z0-9-]+$`, rejected
   `REQ-RENAL-1a` outright — the exact same lowercase-suffix gap already
   found and fixed once this session in `dafny_nl_summary.py`'s
   `_REQ_ID_RE` (2026-07-08), now found completely independently in a
   second, unrelated module (the JSON Schema itself) that happened to
   make the identical assumption. Fixed the same way
   (`[A-Za-z0-9-]`), in all four schema files that declare an `id` or
   `parent_requirement` pattern.

**A fourth, independent bug caught while reading the code closely for
the fix above, not required by either new example but real and worth
fixing anyway**: `symbolic_binding_conflicts()` never had the
`.dfy`-extension skip that `_declared_concrete_bindings()` already
carried for exactly this situation — a future *mixed* example (some
requirements crosshair-backed, others dafny-backed, in the same
metadata file, with a real `--manifest` provided) would have had its
dafny-backed requirements' `.dfy` implementation paths incorrectly
compared against the crosshair manifest's Python target file and
false-flagged as a Type 1 identity-mismatch CONFLICT. Fixed by adding
the same `.dfy`-extension skip, mirroring the existing sibling function
exactly.

**Every change re-verified against zero regression, not assumed safe
from reading the code.** `dosage_calculator`'s real, committed artifacts
were regenerated (`python examples/dosage_calculator/generate_artifacts.py`)
before and after each shared-code change and diffed content-for-content
(the `generated_utc` timestamp field, which changes on every run by
design, excluded) — byte-for-byte identical every single time, across
all five variants (a/b/symbolic/concrete/formal). A pre-existing, wholly
unrelated finding surfaced during this regression testing and
deliberately NOT touched here: `dosage_calculator/artifact_index.json`'s
committed SHA-256 hash for `dosage.dfy` and `run_manifest_dafny.json`
does not match the files' current on-disk content, reproducible even
with every change in this entry fully reverted — a genuine, pre-existing
provenance-index staleness bug (`dosage.dfy` was evidently edited at
some point after the index was last regenerated), unrelated to Phase 3,
named here rather than silently fixed in passing or silently ignored.
**Fixed, 2026-07-11 (same day, on direct instruction):** root cause
confirmed via git history — commit `0dc2715` (2026-07-07) legitimately
tightened `dosage.dfy`'s postcondition and re-verified it for real, but
never re-ran `generate_artifacts.py`'s stage 7 (provenance index)
afterward. Fixed by running that sanctioned entrypoint rather than
hand-editing the index; this also picked up the metadata schema files'
real content changes from this same Phase 3 work, which had gone stale
in the index the same way. `python -m pytest tests/ -q`: 205 passed.

**`renal_adjustment`'s real packaging** (`metadata.a.yaml`,
`dafny_captures_index.json`, `traceability_matrix.a.json`/`.md`): 9
requirement rows total. REQ-RENAL-1 (`GStage`), REQ-RENAL-1a
(`RoundHalfUp`), REQ-RENAL-2 (`SelectFormula`), and REQ-RENAL-5
(`ComposedCeiling`) each bind real dafny evidence directly; REQ-RENAL-1
and REQ-RENAL-2 additionally bind `AssessRenalFunction`'s evidence too,
mirroring that function's own real, existing dual `// REQ-RENAL-1,
REQ-RENAL-2` inline citation in the `.dfy` file itself — the metadata
does not invent a citation the spec doesn't already carry. The two
unnumbered CrCl-computation functions
(`CockcroftGaultCrClMlPerMin`/`AssessRenalFunctionFromInputs`, which
carry no REQ-ID citation in the `.dfy` file at all) are attached as
additional evidence under REQ-RENAL-2 rather than given an invented new
requirement ID, per the scoping plan's own recommendation. The
remaining five requirements render as honest GAP rows, in two
deliberately different categories, not the same treatment applied
uniformly: REQ-RENAL-3/4/6/7 (Cockcroft-Gault reliability, missing-data
fail-safe, AKI reassessment, BSA de-normalization) are prose-only, real
candidates for future Dafny formalization, given `intended_method:
PROVEN` so their gap note correctly reads "intended PROVEN, realized
GAP" — an honest signal of unmet ambition. REQ-RENAL-8
(classification-flag provenance) is structurally different: its trust
boundary (the flags are caller-supplied, never computed or proven
inside the spec) is permanent and will never be a Dafny proof, but the
*provenance* question underneath it — who populates the flags, by what
process — is not permanently unresolvable, it is a real-world process
decision currently being gathered (Steven talking to the relevant
people, 2026-07-11), deliberately parked as an explicit GAP until that
data is in hand. Given `intended_method: DECLARED` (not `PROVEN`),
because even once that data lands it will be a DECLARED process fact,
not a proof — so its note correctly reads "intended DECLARED, realized
GAP" rather than falsely implying a future *proof* is coming. Distinct
from REQ-RENAL-3/4/6/7 (which do await Dafny formalization) on the
proof axis, and distinct from a closed-forever item on the provenance
axis — parked, not abandoned.

**`drug_interaction_checker`'s real packaging** (`metadata.a.yaml`,
`dafny_captures_index.json`, `traceability_matrix.a.json`/`.md`): 6
requirement rows. REQ-DDI-1/2/3/4 all bind to the exact same one
`dafny_captures_index.json` entry (`CheckInteraction`) — the first time
this repo's matrix binder has ever been exercised with a genuine
many-requirements-to-one-proof shape (every `dosage_calculator`/
`renal_adjustment` requirement is 1:1 with its own function); confirmed
working end to end by actually running the real pipeline, not assumed
from the schema's shape allowing it in principle. REQ-DDI-5/6 (the
indication-axis extension, the numeric dose-reduction targets) render
as honest GAP rows, `intended_method: PROVEN` (both are named, staged v2
candidates per `PHASE1_PLAN.md`, not permanent trust-boundary decisions
like `renal_adjustment`'s REQ-RENAL-8).

Both matrices pass `assert_no_realized_proven` (R3) — re-checked
directly against the committed artifact in each example's own test
file, not just trusted because `build_matrix()` calls it internally at
generation time. `evidence/render/matrix_variants.py::_md_head()` was
also improved (2026-07-11, same pass): a `None` bounds block now
renders as an explicit "N/A (no crosshair evidence in this metadata)"
in the generated Markdown, rather than a bare "None" that a reader could
misread as a data gap rather than the honest "not applicable" it
actually is — a small, real readability fix for the first artifact ever
to exercise this path.

15 new tests: `tests/test_renal_adjustment_matrix.py` (9 tests — CLI
round-trip with `--manifest`/`--concrete` genuinely omitted, per-row
evidence-binding checks including the dual-citation and multi-evidence
cases, the two distinct GAP categories, and the structural PROVEN
check) and `tests/test_drug_interaction_checker_matrix.py` (6 tests —
same CLI round-trip, the many-requirements-to-one-proof binding, the
GAP rows, the bounds-block rendering, and the structural PROVEN check).
205 tests pass (up from 190).

## Phase E REQ-DDI-5/REQ-DDI-6 — `drug_interaction_checker.dfy` extended with the indication axis and numeric dose-reduction targets: BUILT, all six gates re-run (2026-07-12)

Both requirements had been named-but-deferred since Gate 1c (2026-07-10):
`REQ-DDI-5` because two apixaban+inducer cells (rifampicin;
carbamazepine/phenytoin/phenobarbital) depend on a clinical-indication
axis v1 didn't model, `REQ-DDI-6` because `DoseReductionAdvised`'s exact
numeric mg figure was only v1 informational text. An externally-supplied
research document's claim that both were buildable from public UK
sources without non-public clinical knowledge was verified first,
against five independent primary sources (`sources/README.md`'s
2026-07-12 entries), before any build decision — see the prior
`KNOWN_LIMITATIONS.md` entry above (2026-07-12, sourcing-only).

**REQ-DDI-5 built**: `datatype TreatmentIndication = AFStrokePrevention
| RecurrentVTEPrevention` (closed to exactly the two indications the
interaction source names) added as `CheckInteraction`'s fourth
parameter. Both named indications give apixaban the identical
"use with caution" outcome, so every constructible
`TreatmentIndication` value is provable — the function's previous
`requires` clause (excluding all four apixaban+inducer cells outright)
is removed entirely, not narrowed; `CheckInteraction` is now total.

**REQ-DDI-6 built**: new companion function `DoseReductionTargetMg(doac,
agent): int`, requires-gated bare-`int` (matching
`renal_adjustment.dfy`'s `SelectFormula` precedent rather than
introducing this repo's first `Option<int>` pattern), pinning the five
real cells the source states a number for: Dabigatran+Verapamil
(110mg), Edoxaban+{Dronedarone, ErythromycinSystemic, Ketoconazole,
Ciclosporin} (30mg each, sourced individually). Apixaban never appears
in this function's precondition — a direct, confirmed structural
consequence of `CheckInteraction` never producing `DoseReductionAdvised`
for apixaban anywhere in its match arms, not a hand-written exclusion.

**All six gates re-run for real, both requirements**: C1 re-captured
(`2 verified, 0 errors`, both functions); C6 — two new sign-off addenda
written, explicitly marked "not yet confirmed — pending review," never
self-signed-off (see the Gate C6 review sections below); C4 — 6 new STP
lemmas, `20 verified, 0 errors` (up from 11 lemmas / 22 verified pre-
extension, a different function count); C3 — `TreatmentIndication` got
`EnumSort` treatment for free (no code change), weak-postcondition count
60 → 64; C5 — mutation testing restructured to a multi-function loop:
1178 mutants, first run 634 killed, 472 filtered_static, 68 survived (3
named categories, none new), 4 unclassifiable (the datatype-ordering
type-error category reappearing, since `DoseReductionTargetMg`'s own new
`requires` clause reintroduces a datatype comparison REQ-DDI-5 alone had
made disappear). A real engineering boundary named, not fixed: the
mutation engine's body-scanning mode refuses on a `//` comment inside
`DoseReductionTargetMg`'s body — worked around with clause-level-only
LVR coverage (equivalent, no new shared-module engineering needed),
documented in `run_mutation_suite_ddi.py`'s own docstring.

**A Qodo code-review finding on the resulting PR (#39) then improved the
proof itself**: the wildcard match arm's bare `0` fallback (a
reliability risk if this spec were ever compiled and called from
unverified code with the precondition violated) was replaced with
`case _ => (assert false; 0)`, verified to still compile and verify
cleanly — Dafny proves that branch genuinely unreachable given the
`requires` clause. This also converted the 7 requires-clause mutation
survivors from the first run into kills, since a mutated requires clause
can now admit a pair that falls into the wildcard arm, defeating the
`assert false`. Re-run: 1178 mutants, 641 killed, 472 filtered_static,
61 survived, 4 unclassifiable — `DoseReductionTargetMg` now contributes
exactly 30 survivors, ensures-only, no requires-clause survivors left.

**Phase 3 regenerated via the real CLI, never hand-edited**:
`metadata.a.yaml`/`traceability_matrix.a.json`/`.md` rebuilt — all 6
requirement rows in this example now render real `PROVEN` evidence, no
GAP rows remain. 214 tests pass (up from 205).

## Gate C6 review, 2026-07-13 — pre-sign-off review of the REQ-DDI-5/REQ-DDI-6 addenda found four real defects, all resolved

Before Steven's sign-off could happen, a review of the two 2026-07-12
Gate C6 addenda (`nl_confirmation_drug_interaction_checker_dfy.md`)
found three defects — each independently re-verified against the real
committed artifacts before acting, not accepted on the review's word
alone — plus a fourth found independently while fixing the third:

1. **Stale NL summary — fixed.** The addenda's own "Summary presented"
   block was still the pre-REQ-DDI-5/6, 2026-07-10 generation (3-arg
   signature, 60 postconditions, no `DoseReductionTargetMg` at all).
   Regenerated for real via `evidence.dafny_nl_summary.summarize_method`;
   the stale block marked superseded and left as a frozen historical
   record (matching `GATE_1C_AUDIT.md`'s convention), not rewritten.
2. **Missing wildcard-arm review item — fixed.** Addendum 2 never
   mentioned the Qodo-driven `assert false` fix to
   `DoseReductionTargetMg`'s wildcard arm (PR #39) despite it being the
   function's most recently changed line with the largest measured
   effect on Gate C5. Added as a new review item.
3. **A real spec-scope gap — fixed, on Steven's decision.**
   `sources/sps-doac-interactions-2024.md` scopes the
   dabigatran+verapamil 110mg figure to specific indications, but
   `DoseReductionTargetMg` proved it unconditionally — a claim provably
   wider than the source's own stated scope, though not a soundness bug
   (both existing `TreatmentIndication` constructors fell within scope).
   `sources/emc-smpc-dabigatran-indications-2025.md` (new primary source,
   eMC SmPC, fetched and archived before any decision) confirmed
   dabigatran genuinely has a third, current, UK-licensed indication
   (orthopaedic VTE prophylaxis) the verapamil row is silent on. Steven
   decided (via `AskUserQuestion`, not resolved by an assistant): add a
   third `TreatmentIndication` constructor, `OrthopaedicVTEProphylaxis`,
   now. Implemented: `DoseReductionTargetMg` gained a `treatmentIndication`
   parameter and an indication guard on its Dabigatran+Verapamil cell; a
   new STP lemma (`DoseTargetDomainAgreesWithCheckInteraction`) proves
   this function's domain exactly equals "`CheckInteraction` says
   `DoseReductionAdvised`" minus the SSRI and orthopaedic exclusions.
4. **A multi-line-clause mutation-testing truncation bug — found and
   fixed, not part of the original review.** Writing the new Fix-2A
   clauses across multiple physical lines silently truncated
   `evidence/dafny_mutate.py`'s clause-site locator at the first
   physical line — a real coverage regression (1178 → 1171 mutants) not
   caught by Dafny (still verified clean) or by pytest's pinned counts
   alone. Fixed by reformatting both clauses to single lines, matching
   `renal_adjustment.dfy`'s own established precedent for this exact
   class of gap, rather than extending the tool.

**All six gates re-run for real after the fix**: C1 `2 verified, 0
errors`; C4/STP `23 verified, 0 errors` (up from 20); C3 unchanged
(precondition still satisfiable); C5 1250 mutants — 668 killed, 482
filtered_static, 74 survived, 26 unclassifiable (every count's jump
reflects real, previously-missing coverage, not a new finding class).
Phase 3 regenerated: still 6/6 `PROVEN`, no GAP rows. Full account:
`nl_confirmation_drug_interaction_checker_dfy.md`'s "Addendum 3."

## Gate C6 review (second, post-merge), 2026-07-13 — a Qodo review of merged PR #40 found a real scope-leak in `CheckInteraction`'s own apixaban rows: FIXED

PR #40 (the fix above) merged externally. A second Qodo code review, run
against the merged code, found a real, independently-verified bug in a
sibling function to the one PR #40 was written for: `CheckInteraction`'s
four apixaban+inducer match arms (Rifampicin, Carbamazepine, Phenytoin,
Phenobarbital) computed `Caution` unconditionally — the match body never
inspected `treatmentIndication` at all, even though the paired `ensures`
clause explicitly guarded on `treatmentIndication == AFStrokePrevention
|| treatmentIndication == RecurrentVTEPrevention`. Harmless while
`TreatmentIndication` had only those two constructors (the guard was
always true for every constructible value); adding
`OrthopaedicVTEProphylaxis` (for `DoseReductionTargetMg`'s own guard,
same PR) silently reopened the gap — calling `CheckInteraction` with the
new indication returned a fabricated `Caution` rather than the honest
`NotCovered` this repo's own `(Apixaban, Dronedarone)` silent-cell
convention calls for. Exactly the general risk Finding 3/4 above already
named (widening a match statement's input domain without re-checking
every existing arm against it), caught here on a different function.

Independently re-verified against the actual merged `.dfy` source
directly (not the review's word) before fixing — an unambiguous bug, not
a design fork, so fixed directly rather than raised as a question, per
this repo's own "if you feel confident in how to resolve an event...
push the fix" discipline for PR-activity events.

**Fix**: each of the four match arms now branches on
`treatmentIndication`, returning `NotCovered` for the orthopaedic
indication (matching `(Apixaban, Dronedarone)`'s pattern exactly). Four
new `ensures` clauses pin the `NotCovered` outcome per inducer.

**All six gates re-run for real, on a branch restarted from
`origin/main` post-merge** (new work on already-merged code, not a
reopening of PR #40's own change): C1 `2 verified, 0 errors`; C4/STP two
new lemmas, `25 verified, 0 errors` (up from 23); C3 weak-postcondition
count for `CheckInteraction` now 68 (up from 64); C5 real re-run — 1342
mutants: 744 killed, 522 filtered_static, 50 survived, 26 unclassifiable.
`CheckInteraction`'s own survivors dropped sharply, 31 → 7 (the four
REQ-DDI-5 indication-disjunction survivors collapsed from a broad
"redundant guard" pattern to a narrower LOR-vacuity case now that the
guard is load-bearing; the 3 pre-existing SSRIOrSNRI survivors are
unchanged). `DoseReductionTargetMg`'s own 43 survivors are unaffected —
this fix didn't touch that function. Phase 3 regenerated: still 6/6
`PROVEN`, no GAP rows. Full account:
`nl_confirmation_drug_interaction_checker_dfy.md`'s "Addendum 4." Gate
C6 sign-off remains open — not because a finding is unresolved (every
finding across Addenda 3 and 4 is resolved), but because Steven's
actual review of the current spec shape, a recorded human decision,
still hasn't happened.

## Gate C5 extended: STP-suite escalation for `drug_interaction_checker`, 2026-07-13 — caught a real latent gap before it could ever become a regression

Asked, during Gate C6 sign-off review, whether `drug_interaction_checker`'s
50 mutation-testing survivors could be reduced under current
constraints (not extending tooling where a real change is genuinely
impossible to make, but not leaving a real, closeable gap either).
Diagnosed all 50 by category first, before touching anything —
`CheckInteraction`'s 7 (3 SSRIOrSNRI "consequent independently proven"
+ 4 LOR-vacuity on the REQ-DDI-5 indication disjunction) and
`DoseReductionTargetMg`'s 43 (6 `requires`-clause indication-guard ROR
+ 37 `ensures`-clause guard-antecedent) — all matching this repo's
already-established survivor taxonomy, no new category found by
inspection alone.

**Hand-probed empirically before building, per this repo's own standing
discipline of testing a prediction rather than trusting it.** Applied
one of the 6 `requires`-clause survivor mutations
(`treatmentIndication == AFStrokePrevention` → `!=`, inside
`DoseReductionTargetMg`'s Dabigatran+Verapamil disjunct) to a scratch
copy of the spec, then re-verified the already-committed STP suite
(`drug_interaction_checker_stp_suite.dfy`) against it by redirecting
the suite's own `include` at the mutant file:

- The mutant still verifies clean against the bare spec (confirmed —
  matches "survived").
- The STP suite's own `STP_Accept_DoseReductionTargetMg_...
  AFStrokePrevention` ACCEPT lemma **fails**
  (`function precondition could not be proved`) — the mutation
  simultaneously widens the requires clause to admit the orthopaedic
  indication (exactly the class of scope-leak bug the "Gate C6 review
  (second, post-merge)" section above fixed on `CheckInteraction`)
  while excluding the lemma's own witness call.

Also hand-probed one `ensures`-clause ROR mutant and one LOR mutant on
*each* function (4 probes total) to check whether the same escalation
would help there too: **confirmed it does not** — all four still
verified clean against the STP suite. Root cause, confirmed directly
rather than assumed: both `CheckInteraction` and `DoseReductionTargetMg`
are plain (non-`{:opaque}`) Dafny `function`s, so a same-module STP
lemma calling one with concrete literal arguments gets verified by
Dafny unfolding the function body directly — the mutated `ensures`-
clause text is provably irrelevant to that proof. A genuine Dafny
semantics fact, not a shortfall of this escalation to fix later;
closing it would require marking these functions `{:opaque}` with
explicit `reveal` calls added everywhere they're used throughout the
spec and its STP suite — a much larger, invasive redesign
disproportionate to a testing-methodology limitation, deliberately not
attempted.

**Built**: `run_mutation_suite_ddi.py` gained a new `_stp_verify`
helper — re-verifies the committed STP suite (reused verbatim, no new
lemma authored) against every mutant that survives the bare-spec check,
by writing the mutant to a temp file and redirecting a temp copy of the
STP suite's `include` at it. A mutant the STP suite catches is
reclassified from `survived` to a new, distinct `killed_via_stp_suite`
outcome — kept separate from ordinary `killed` so the report stays
honest about which check actually caught each one, not merged silently
into the existing category.

**Real run**: 1342 mutants (unchanged) — 744 killed, 522
filtered_static, **44 survived** (down from 50), 26 unclassifiable,
**6 killed_via_stp_suite** — exactly the 6 hand-predicted requires-
clause indication-guard mutants, confirmed directly against the report.
`CheckInteraction`'s 7 survivors and `DoseReductionTargetMg`'s remaining
37 ensures-clause survivors are unaffected, matching the hand-probe's
prediction. `tests/test_drug_interaction_checker_mutation_report.py`
updated: a new test for the `killed_via_stp_suite` category, existing
survivor-count assertions updated, a new "Run 5" section added to the
module docstring. Full suite: 215 passed (up from 214).

## Gate C6 confirmed and closed for `drug_interaction_checker.dfy`, against the raw sources directly (2026-07-13)

A full, independent, line-by-line review was performed at Steven's
request — not a re-read of prior summaries. Every one of
`sources/sps-doac-interactions-2024.md`'s 17 sections (Amiodarone,
Digoxin, Diltiazem, Dronedarone, Verapamil, Macrolides, Rifampicin,
Other-DOACs/heparin/warfarin, SSRIs/SNRIs, Fluconazole,
Itraconazole/Ketoconazole, Antiplatelets,
Carbamazepine/Phenytoin/Phenobarbital, Levetiracetam/Valproate,
Ciclosporin, Tacrolimus, NSAIDs) was cross-checked directly against its
corresponding `ensures` clause(s) and match arm(s) in the current spec
— all 68 `CheckInteraction` postconditions, all 5
`DoseReductionTargetMg` postconditions. No discrepancy found. The two
most recently changed cells (the four `OrthopaedicVTEProphylaxis` →
`NotCovered` clauses; `DoseReductionTargetMg`'s indication guard on
Dabigatran+Verapamil) were checked specifically against both
`sources/sps-doac-interactions-2024.md` and
`sources/emc-smpc-dabigatran-indications-2025.md` and confirmed
correct.

**Live re-verification, not from memory**: `dafny verify
drug_interaction_checker.dfy` → `2 verified, 0 errors`; `dafny verify
drug_interaction_checker_stp_suite.dfy` → `25 verified, 0 errors` (21
real lemmas, confirmed via `grep -c "^lemma "`). All 21 lemmas
spot-checked against their corresponding `ensures` clauses, including
the two newest (`STP_Accept_..._OrthopaedicVTEProphylaxis_NotCovered`
and its REJECT counterpart).

**Two drafts of an externally-produced "Gate C Technical Review Report"
were then independently cross-checked against the real artifacts before
either was trusted, not accepted on the report's word.** The first
draft had four real errors:

1. **"25 lemmas"** — conflates Dafny's verification-task count with the
   real lemma count (21, confirmed via direct `grep`). The same class
   of mistake this document's own history already caught and corrected
   once, for the same file, on 2026-07-10.
2. **Reversed causality**: claimed the third `TreatmentIndication`
   constructor's addition "allowed for the removal of the requires
   clause." The real chronology (confirmed against `DEVLOG.md` and the
   `.dfy`'s own comments) is the reverse — the requires clause was
   removed 2026-07-12 with only two constructors; the third, added a
   day later for `DoseReductionTargetMg`'s own scoping, *caused* the
   scope-leak bug rather than enabling anything.
3. **Wrong tooling attribution**: claimed `evidence/dafny_mutate.py` was
   "updated to accumulate clauses across multiple physical lines" to
   fix the truncation bug. Checked directly — no such logic exists in
   that file (`grep` for multiline/accumulate returns nothing); the
   real fix was reformatting the affected clauses to single physical
   lines, the tool left untouched, matching this document's own
   "not by extending the tool" account.
4. **Conflated concepts**: attributed the 26 `unclassifiable` mutants to
   "Dafny function transparency limits." The real report data shows all
   26 are static type errors (`"arguments to <= must be of a numeric
   type"`) and parser ambiguities — unrelated to function transparency,
   a real but separate concept in this codebase.

A second, corrected draft fixed all four precisely — each re-verified
directly again, not assumed fixed because the report said so. **One
further precision point was raised and preserved, not merged away**:
the corrected draft's claim that the 44 `survived` mutants uniformly
"represent a genuine limitation of Dafny function transparency" is
accurate as an explanation of why the Gate C5 STP-suite escalation
can't help any of them (confirmed by the real, exhaustive re-run, and
consistent with hand-probing done before that escalation was built) —
but it is not a complete account of why they survive the *bare-spec*
check to begin with. This document's own established categorization
keeps three distinct mechanisms deliberately separate:
`CheckInteraction`'s 4 LOR survivors are a **vacuous-antecedent** case
(the mutated `||`→`&&` makes the indication guard unsatisfiable for any
single value, unrelated to function opacity); its 3 SSRIOrSNRI ROR
survivors are a **redundant-consequent** case (the outcome is
independently proven by sibling `ensures` clauses for the other DOACs);
only `DoseReductionTargetMg`'s 37 are the **requires-domain-restriction
plus body-obliviousness** pattern "function transparency" actually
names. Recorded, kept explicit, in
`nl_confirmation_drug_interaction_checker_dfy.md`'s final "Decision"
section.

**Decision — Confirmed, 2026-07-13, by Steven.** Every finding raised
against this spec across Addenda 1–5 and this final review is resolved.
**All six Gate C1–C6 pipeline steps are now built AND confirmed for
`drug_interaction_checker` — Gate C6 is closed.** 216 tests pass.
