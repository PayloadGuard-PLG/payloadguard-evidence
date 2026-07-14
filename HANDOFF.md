# Handoff — read this first

For a new session picking this repo up cold. Answers "what is this,
what's actually done, and what's the very next thing to do" without
requiring you to reconstruct it from `DEVLOG.md`'s full history.
Updated at the end of a work session, not continuously — check its own
"Last updated" line against `DEVLOG.md`'s top entry; if `DEVLOG.md` has
newer entries this file doesn't reflect, trust `DEVLOG.md` and update
this file to match before relying on it further.

**Last updated:** 2026-07-14 — **`RISK_MANAGEMENT_PLAN.md` landed for
`dosage_calculator` — third and final risk-management-plan artifact;
all three worked examples now have one.** Mirrors the other two plans'
structure and already-verified ISO 14971:2019 clause citations. Real
differences surfaced honestly rather than glossed over: this device is
the only one with three evidence types per requirement (CrossHair
`BOUNDED_CHECKED`, concrete `EXAMPLE_CHECKED`, Dafny `PROVEN`) —
REQ-DOSE-003 specifically has no Dafny proof, only the first two,
stated plainly; REQ-GIP-1-4-12's existing `kernel_scope`/`system_scope`
split (2026-07-05 Gate 1 review) became Section 1's real life-cycle
scoping, not invented for this plan; the existing STRIDE threat model
was named as a related-but-distinct artifact, not conflated with the
still-missing clinical hazard register. Gate C5's residual is
genuinely cleaner than the other two examples: 56 mutants, **0
survivors, 0 unclassifiable**. Gate C6 — confirmed 2026-07-07 by
Steven ("it's good for the spec as is") — was in fact the very first
Gate C6 sign-off recorded anywhere in this repo, preceding the other
two by several days. Sections requiring clinical judgment left as
explicit GAPs, matching `classification_rationale`'s `DECLARED`
status. 216 tests pass, no spec/code change. **Next step: not yet
instructed.** All three plans point at the same missing artifact — an
actual hazard register, risk evaluation results, and risk management
report per ISO 14971:2019 clause 4.5 — that's the natural next piece
if wanted, but await explicit instruction rather than assuming it.
**Prior update, preserved below** — 2026-07-14 — **`RISK_MANAGEMENT_PLAN.md`
landed for `renal_adjustment` too — second real ISO 14971 risk-management-plan
artifact, same day as the first.** Mirrors
`drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`'s structure and
already-verified ISO 14971:2019 clause citations (not re-verified per
device — the citations describe the standard, not the device). Landed
at `examples/renal_adjustment/RISK_MANAGEMENT_PLAN.md`. Sections
1/3/6 filled with real, committed evidence: `metadata.a.yaml`'s
intended-use text, real Gate C1–C6 references for the 5 `PROVEN`
requirement rows, honest `GAP` rows for REQ-RENAL-3/4/6/7 (named,
sourced, unformalized) and REQ-RENAL-8 (permanent trust boundary, open
operational question), the Gate C5 residual (51 survivors, all three
categories explained, not silently carried), Gate C6's closed status
(2026-07-11). Sections 2/4 (roles, severity/probability, acceptance
matrix) left as explicit GAPs, matching `classification_rationale`'s
`DECLARED` status. **A real, pre-existing staleness bug found and
fixed along the way**: `examples/renal_adjustment/README.md`'s own
"Open questions" item 4 still said Gate C6's sign-off was "still
pending" — it was actually confirmed and closed 2026-07-11, the same
day that sentence was written; the 2026-07-11 documentation audit had
fixed the equivalent claim in the top-level `README.md` but missed
this per-example copy. Fixed in place, not deleted. 216 tests pass, no
spec/code change. **Next step: not yet instructed** — likely candidates
are the same plan for `dosage_calculator`, or starting the actual
hazard register both plans point at; await explicit instruction.
**Prior update, preserved below** — 2026-07-14 — **`RISK_MANAGEMENT_PLAN.md`
landed for `drug_interaction_checker` — first real ISO 14971 risk-management-plan
artifact in this repo.** Preceded by reading the real ISO 14971:2019
standard directly (clauses 1–7.1 verbatim, via `pdftoppm`/poppler-utils
installed for this session — `apt-get install -y poppler-utils`, not
present before) and cross-checking a provisional, externally-supplied
template against it clause by clause. Found one real, minor citation
slip: the template attributed "this plan is part of the risk
management file" to clause 4.5; that sentence is verbatim in clause 4.4
(immediately before the a–g list), and 4.5 is the separate requirement
for what the risk management *file* itself must trace. Every other
citation (4.4a–g; clause 1's exclusions for clinical-procedure
decisions and business risk management) verified accurate. Fixed and
landed at `examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`.
Sections 1/3/6 (scope, review triggers, verification activities) filled
with real, already-committed facts — `metadata.a.yaml`'s intended-use
text, real Gate C1–C6 evidence references for all six REQ-DDI-* rows,
the current Gate C5 mutation-testing residual (44 survivors, explained
not silently carried), Gate C6's closed status. Sections 2 and 4 (roles,
severity/probability bands, acceptance matrix) left as explicit `GAP`s,
not fabricated — no clinical SME assigned yet, matching
`metadata.a.yaml`'s own `classification_rationale` (`B`, `DECLARED`,
"requires a manufacturer-specific ISO 14971 risk file" — this is the
start of that file, not its completion). Documentation ripple done in
`examples/drug_interaction_checker/README.md` (new Amendment section).
**Next step: not yet instructed.** This is a genuinely new document
type for the repo (no prior precedent to extend) — likely next moves
are either building out the same plan for `renal_adjustment`/
`dosage_calculator`, or starting the actual hazard register Section 6
points at, but neither is confirmed; await explicit instruction.
**Prior update, preserved below** — 2026-07-14 — **ISO 14971:2019 read
directly and cross-checked against the provisional
`riskmanagementplantemplate.md` (uploaded, not yet committed to the
repo)** — superseded by the entry above, which completed this work.
**Prior update, preserved below** — 2026-07-13 — **Gate C6
confirmed and closed for `drug_interaction_checker.dfy`, against the
raw sources directly.** A
full, independent, line-by-line review (all 68 `CheckInteraction`
postconditions + all 5 `DoseReductionTargetMg` postconditions, cross-
checked against every one of `sources/sps-doac-interactions-2024.md`'s
17 sections plus `sources/emc-smpc-dabigatran-indications-2025.md` for
the indication-scoping cells) found no discrepancy. Live re-verification:
`2 verified, 0 errors` (main spec), `25 verified, 0 errors` / 21 real
lemmas (STP suite). Two drafts of an externally-produced "Gate C
Technical Review Report" were independently cross-checked before being
trusted — the first had four real errors (a lemma-count/task-count
miscount, a reversed requires-clause-removal causality claim, a wrong
attribution of the multi-line-clause fix, and a conflation of two
unrelated concepts — "unclassifiable" static failures vs. "survived"
function-transparency limits); the corrected draft fixed all four,
verified precisely, with one further precision point preserved rather
than merged away (the established three-way distinction between
vacuous-antecedent, redundant-consequent, and requires-domain-
restriction survivor mechanisms, only the last of which "function
transparency" actually names). **Decision — Confirmed, 2026-07-13, by
Steven.** Recorded in `nl_confirmation_drug_interaction_checker_dfy.md`'s
final "Decision" section. **All six Gate C1–C6 pipeline steps are now
built AND confirmed for `drug_interaction_checker` — Gate C6 is
closed.** 216 tests pass. **Prior update, preserved below** —
2026-07-13 — **A pre-sign-off numbering-currency
review of the C6 doc caught a stale claim, fixed (Addendum 5).** The
"Summary presented, regenerated 2026-07-13 (current spec, both
functions)" section still asserted its postcondition numbering
"matched exactly" after Addendum 4 shifted three of the four
apixaban+inducer `Caution` clauses (48→49, 52→54, 56→59). Addendum 1's
own numbering claim had already been corrected when Addendum 4 was
written, but this earlier, more dangerously-placed copy (sitting
directly above the actual block, not deferred to a cross-reference)
was missed. Independently re-verified live before fixing: re-ran the
NL summary generator against the real spec, confirmed 27/28, 49/50,
54/55, 59/60 exactly. Fixed: section marked `— SUPERSEDED, historical
record only`, a new paragraph explaining the stale claim inserted, the
original left in place unedited (this document's own established
discipline) with a "do not rely on this" flag. No spec content
affected — documentation-currency only. 216 tests pass. **Prior
update, preserved below** — 2026-07-13 — **Gate C5 extended to re-verify the
committed STP suite against every mutation-testing survivor, not just
the bare spec — caught a real, previously-latent scope-leak class before
it could ever become a regression.** Asked, during Gate C6 sign-off
review, whether `drug_interaction_checker`'s 50 survivors could be
reduced under current constraints. Hand-probed before building: applying
one of the 6 `DoseReductionTargetMg` requires-clause indication-guard
survivor mutations to a scratch copy and re-verifying the already-
committed STP suite (`drug_interaction_checker_stp_suite.dfy`) against it
showed the suite's own ACCEPT lemma fails — the mutation widens the
requires clause to admit the orthopaedic indication (the exact class of
scope-leak the entry below fixed on `CheckInteraction`) while excluding
the lemma's own witness call. Also hand-probed one `ensures`-clause ROR
mutant and one LOR mutant on each function: confirmed the STP suite does
**not** help there, since both functions are plain (non-`{:opaque}`)
Dafny `function`s and same-module STP lemmas get verified by Dafny
unfolding the body directly, making mutated `ensures`-clause text
provably irrelevant — a genuine Dafny-semantics limit, not a shortfall
to fix (closing it would need an invasive `{:opaque}`/`reveal` redesign,
disproportionate here). **Built**: `run_mutation_suite_ddi.py` now
re-verifies the committed STP suite (reused verbatim, no new lemma
authored) against every bare-spec survivor, reclassifying any it catches
to a new, distinct `killed_via_stp_suite` outcome. Real run: 1342
mutants — 744 killed, 522 filtered_static, **44 survived** (down from
50), 26 unclassifiable, **6 killed_via_stp_suite** (exactly the 6
hand-predicted mutants). `tests/test_drug_interaction_checker_mutation_report.py`
updated with a new test and updated counts. 215 tests pass (up from
214). **Prior update, preserved below** — 2026-07-13 — **A second Qodo
review, run against PR
#40 after it merged, found a real scope-leak bug in `CheckInteraction`'s
own apixaban rows — fixed, all six gates re-run for real.** PR #40 (the
entry immediately below) merged with `TreatmentIndication` gaining its
third constructor, `OrthopaedicVTEProphylaxis`, for `DoseReductionTargetMg`'s
own indication guard. That change had a silent side effect on a sibling
function nobody had touched for this reason: `CheckInteraction`'s four
apixaban+inducer match arms (Rifampicin, Carbamazepine, Phenytoin,
Phenobarbital) computed `Caution` unconditionally, never actually
inspecting `treatmentIndication`, so calling any of them with the new
`OrthopaedicVTEProphylaxis` indication returned a fabricated `Caution`
instead of the honest `NotCovered` this repo's `(Apixaban, Dronedarone)`
silent-cell convention calls for. Independently re-verified directly
against the merged `.dfy` source (not the review's word) before fixing —
an unambiguous bug, not a design fork, so fixed directly rather than
raised as a question. **Fixed**: each of the four match arms now
branches on `treatmentIndication`, matching `(Apixaban, Dronedarone)`'s
pattern; four new `ensures` clauses pin `NotCovered` for the orthopaedic
indication. All six gates re-run for real: C1 `2 verified, 0 errors`;
C4/STP `25 verified, 0 errors` (up from 23); C3 weak-postcondition count
for `CheckInteraction` now 68 (up from 64); C5 **1342 mutants — 744
killed, 522 filtered_static, 50 survived, 26 unclassifiable**
(`CheckInteraction`'s own survivors dropped sharply, 31 → 7, once the
guard became load-bearing; `DoseReductionTargetMg`'s 43 survivors
unaffected). Phase 3 regenerated: still 6/6 `PROVEN`, no GAP rows. Full
account: `examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`'s
"Addendum 4." Gate C6 sign-off is still open — every finding across
Addenda 3 and 4 is resolved, but Steven's actual review of the current
spec shape (a recorded human decision) still hasn't happened. 214 tests
pass. **Prior update, preserved
below** — 2026-07-13 — **Gate C6 review's real spec-scope
finding resolved: `TreatmentIndication` gained a third constructor,
`DoseReductionTargetMg` is now indication-scoped where the source
requires it.** Continuing the same day's earlier work (an externally-
supplied review found two doc defects, fixed, plus one genuine
spec-scope finding left open — see the prior entry below for that
account): the open question was primary-sourced first
(`sources/emc-smpc-dabigatran-indications-2025.md`, real eMC SmPC,
revision 16 January 2025), which confirmed dabigatran genuinely has a
third, current, UK-licensed indication (primary VTE prophylaxis after
elective hip/knee replacement) that the verapamil interaction row is
silent on — a real gap, not a false alarm. Presented to Steven via
`AskUserQuestion`, not resolved by an assistant: decided to add the
third constructor now. **Implemented**: `TreatmentIndication` gained
`OrthopaedicVTEProphylaxis`; `DoseReductionTargetMg` gained a
`treatmentIndication` parameter and an indication guard on its
Dabigatran+Verapamil cell (matching the guard `CheckInteraction`'s own
apixaban rows already carry); a new STP lemma
(`DoseTargetDomainAgreesWithCheckInteraction`) proves this function's
domain exactly equals "CheckInteraction says DoseReductionAdvised"
minus the SSRI and orthopaedic-indication exclusions — apixaban's
absence is now a proven theorem, not a grep-verified observation.
**A second, independent finding surfaced while building this, caught
before trusting the result**: writing the new clauses across multiple
physical lines silently truncated `evidence/dafny_mutate.py`'s
mutation-testing coverage of them at the first line — a real regression
in test coverage that neither Dafny (still verified clean) nor pytest's
pinned-count-only assertions caught on their own; diagnosed directly
(every truncated clause read exactly `'(doac == Dabigatran && agent ==
Verapamil'`) and fixed by reformatting both clauses to single lines,
matching `renal_adjustment.dfy`'s own established precedent for this
exact class of gap rather than extending the tool. All six gates
re-run for real: C1 `2 verified, 0 errors`; C4/STP `23 verified, 0
errors` (up from 20); C3 unchanged; C5 (after the truncation fix)
1250 mutants — 668 killed, 482 filtered_static, 74 survived, 26
unclassifiable (every count's jump reflects real, previously-missing
coverage, not a new finding class — CheckInteraction's own 31
survivors unchanged, DoseReductionTargetMg's 43 survivors and 26
unclassifiable results are the same two already-named categories, now
correctly counted at full scale). Phase 3 regenerated: still 6/6
`PROVEN` rows, no GAP rows. **The sign-off document is now genuinely
ready for Steven's actual review** — Addendum 3 states this
explicitly — but that review (a recorded human decision) still hasn't
happened; this session cannot do it on his behalf. Full account:
`examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`'s
"Addendum 3." 214 tests pass. **Prior update, preserved below** —
2026-07-13 — **Gate C6 review found real defects in
the REQ-DDI-5/REQ-DDI-6 sign-off document; two fixed, one genuine
spec-scope finding left open, in progress.** An externally-supplied
review of `nl_confirmation_drug_interaction_checker_dfy.md`'s two
2026-07-12 addenda (written before Steven's sign-off, catching this
pre-rubber-stamp) found three defects, each independently re-verified
against the real committed artifacts before acting — not accepted on
the review's word alone. **Fixed**: (1) the addenda's own "Summary
presented" block was the stale pre-REQ-DDI-5/6 generation (3-arg
signature, 60 postconditions, no `DoseReductionTargetMg` at all) —
regenerated for real via `evidence.dafny_nl_summary.summarize_method`
and inserted as a new dated block, the old one marked superseded and
left as a frozen historical record; (2) Addendum 2 never mentioned the
Qodo-driven `assert false` fix to `DoseReductionTargetMg`'s wildcard arm
(PR #39, merged) despite it being the function's most recently changed
line with the largest measured effect on Gate C5 — added as a new
review item. **Left open, deliberately not resolved by an assistant**:
`sources/sps-doac-interactions-2024.md` lines 57-65 scope the
dabigatran+verapamil 110mg figure to specific indications ("AF-stroke-
prevention and DVT/PE-prevention-and-treatment... specifically"), the
same shape REQ-DDI-5 built a whole new axis to model for the apixaban
rows — but the archived source's own editorial layer dismisses that
scoping in the same sentence ("this doesn't need an indication axis to
model correctly"), and `DoseReductionTargetMg` (already merged, PROVEN
in the traceability matrix) was built exactly per that dismissal: no
indication parameter, proving the figure unconditionally. Confirmed
directly against the source text, not just the review's summary — real
finding, not a false alarm. Not currently a soundness bug (both
existing `TreatmentIndication` constructors fall within the source's
stated scope for this row), but the claim's scope is provably wider
than the sentence it cites, and nothing in the function's signature or
clauses records that an indication axis was ever considered for this
cell. Full account:
`examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`'s
"Addendum 3." 214 tests pass (no regression; doc-only + one sign-off
doc change this pass). **Prior update, preserved below** —
2026-07-12 — **REQ-DDI-5 and REQ-DDI-6 built for
real**, closing the two v2 items `drug_interaction_checker` had left
explicitly staged. Added `datatype TreatmentIndication =
AFStrokePrevention | RecurrentVTEPrevention` (closed to exactly the two
indications the interaction source names — a real scoping decision,
confirmed via `AskUserQuestion` before building) as `CheckInteraction`'s
fourth parameter; since both named indications give the identical
sourced outcome, every constructible `TreatmentIndication` value is now
provable, so `CheckInteraction`'s previous `requires` clause is removed
entirely, not narrowed — the function is now total (REQ-DDI-5). Added a
new companion function `DoseReductionTargetMg(doac, agent): int`
(requires-gated bare-`int`, matching `renal_adjustment.dfy`'s
`SelectFormula` precedent rather than introducing this repo's first
`Option<int>` pattern), pinning the five real sourced mg figures;
apixaban never appears in its precondition — a direct, confirmed
consequence of `CheckInteraction` never producing `DoseReductionAdvised`
for apixaban, not a hand-written exclusion (REQ-DDI-6). Both functions
verify clean (`2 verified, 0 errors`). All six gates re-run for real for
both requirements — C1 (re-capture), C6 (two new sign-off addenda,
explicitly marked "not yet confirmed — pending review," not
self-signed-off), C4 (6 new STP lemmas, `20 verified, 0 errors`), C3
(spec lint — `TreatmentIndication` got `EnumSort` treatment for free,
weak-postcondition count 60→64), and C5 (mutation testing restructured
to a multi-function loop: 1178 mutants, first run 634 killed, 472
filtered_static, 68 survived — all in 3 named categories, none new — 4
unclassifiable, a real, expected reappearance of the datatype-ordering
type-error category REQ-DDI-5 had made disappear, since
`DoseReductionTargetMg`'s own new `requires` clause reintroduces a
datatype comparison). A real engineering boundary named, not fixed: the
mutation engine's body-scanning mode refuses on a `//` comment in
`DoseReductionTargetMg`'s body — worked around with clause-level-only
LVR (equivalent coverage, no new shared-module engineering needed),
named explicitly in `run_mutation_suite_ddi.py`'s docstring. **A Qodo
code-review finding on the resulting PR (#39) then improved the proof
itself**: the wildcard match arm's bare `0` fallback (a reliability risk
if this spec were ever compiled and called from unverified code with the
precondition violated) was replaced with `case _ => (assert false; 0)`,
verified to still compile and verify cleanly — and it made the 7
requires-clause survivors from the first C5 run genuinely unprovable
(killed) instead of silently surviving, since a mutated requires clause
can now admit a pair that falls into the wildcard arm, defeating the
`assert false`. **Re-run: 1178 mutants, 641 killed, 472 filtered_static,
61 survived, 4 unclassifiable** — `DoseReductionTargetMg` now contributes
exactly 30 survivors (ensures-only, no requires-clause survivors left).
**Phase 3 regenerated**: `metadata.a.yaml`/`dafny_captures_index.json`/
`traceability_matrix.a.json`/`.md` all rebuilt via the real CLI (never
hand-edited) — all 6 requirement rows in this example now render real
`PROVEN` evidence, no GAP rows remain. Full account:
`KNOWN_LIMITATIONS.md`'s "Phase E REQ-DDI-5/REQ-DDI-6" section;
`DEVLOG.md`'s top 2026-07-12 entry. 214 tests pass. **Prior update,
preserved below** — Verified an external REQ-DDI-5/6 scoping
document ("Can Apixaban Indication-Dependent Dosing and Numeric
Dose-Reduction Rules Be Built From Public, Citable Sources?") against
primary sources before any build decision — direct instruction: "verify
first, then we'll consider the solutions." Ran the document's claimed
quotes against `sources/sps-doac-interactions-2024.md` (already
committed) through `evidence/citation_gate.py`: all five real claims
CONFIRMED, and a deliberate false control ("apixaban decreased by 50%,"
which the document itself says does not exist in UK sources) correctly
returned NOT_FOUND. Fetched and verbatim-verified three new external
sources: both eMC apixaban SmPCs (products 2878/4756, confirming the
NVAF "2-of-3" dose-reduction rule, that it's NVAF-only, the hip/knee
VTE-prophylaxis regimen, and — independently — that apixaban interaction
dosing is qualitative-only even on the legal SmPC itself), the MHRA DSU
vol 16 iss 10 renal table (confirming the same indication-branching
pattern generalizes beyond drug interactions to renal dosing), and the
US FDA ELIQUIS label §7.1 (confirming the genuine UK/US divergence — the
US states a numeric 50% interaction reduction UK sources never state).
**Central finding: the research document's spine holds.** REQ-DDI-5
(indication-dependent branching) and REQ-DDI-6 (numeric dose-reduction
targets) are buildable from public UK sources; apixaban's absent
numeric interaction rule is a genuine, correctly-identified gap, not an
oversight or an incomplete search. Archived the three new sources under
`sources/`, per the folder's own convention (dates, URLs, fetch
provenance, verbatim extracts, explicit confirms/extends notes — the
FDA one flagged explicitly as a non-UK contrast source, never a
substitute for UK guidance). `PHASE1_PLAN.md`'s REQ-DDI-5/6 rows now
point to this verified material. **No code changed, no requirement
built, no matrix regenerated** — per direct instruction, this session
stopped at verification and archival; the build/scoping decision is a
deliberately separate, later conversation. Full account: `DEVLOG.md`'s
top 2026-07-12 entry. 205 tests pass (no code touched, confirmed
unaffected). **Prior update, preserved below** — Scoped `REQ-RENAL-8`
(classification-flag provenance) and made the honest framing refinement
its scoping implied.
Structural finding worth knowing: as the system stands, REQ-RENAL-8 can
only ever be a GAP — the schema's evidence-method enum is
`['crosshair', 'concrete_test', 'dafny']` with no `declared` method, and
no binder produces a *realized* `DECLARED` record, so `DECLARED` is only
ever an intent. Steven's decision: leave the row an explicit GAP while
he gathers the real-world process data (who populates the flags —
clinician form / EHR lookup / static list) by talking to people; don't
build DECLARED-evidence machinery yet. The only change made was a
framing fix (no code): the docs had called this "permanent, nobody ever
intends to resolve," conflating the trust boundary (permanently never a
Dafny proof — true) with the provenance answer (being actively gathered
— so "parked pending data," not "permanent"). Refined across
`metadata.a.yaml` (+ matrix regenerated), `KNOWN_LIMITATIONS.md`,
`renal_adjustment/README.md`, `PHASE1_PLAN.md`, this file, and the matrix
test's docstrings. Full account: `DEVLOG.md`'s top 2026-07-11 entry. 205
tests pass. **Prior update, preserved below** — Two named-not-fixed
items closed, both
surfaced (but deliberately left open) by the documentation audit further
below. **`dosage_calculator/artifact_index.json`'s stale provenance
hashes for `dosage.dfy`/`run_manifest_dafny.json` are fixed** — root
cause was a real, legitimate `dosage.dfy` edit (commit `0dc2715`,
2026-07-07) whose otherwise-thorough doc sweep never re-ran
`generate_artifacts.py`'s provenance-index stage; fixed by running that
sanctioned entrypoint, not by hand-editing the index.
**`examples/drug_interaction_checker/README.md` now exists**, mirroring
`dosage_calculator`'s and `renal_adjustment`'s audit-trail structure,
built entirely from that example's own already-committed record
(`PHASE1_PLAN.md`, `GATE_1C_AUDIT.md`, the Gate C6 sign-off doc, the raw
Dafny/mutation captures) — every quoted number cross-checked directly
against its source capture file before being written. Full account:
`DEVLOG.md`'s 2026-07-11 "Two named-not-fixed items closed" entry
(above the Documentation audit entry below). 205 tests pass throughout,
no regressions. **Prior update, preserved below — Documentation audit:
every main doc
(`README.md`, this file, `OPERATIONS_MANUAL.md`, `SYSTEM_BLUEPRINT.md`,
`KNOWN_LIMITATIONS.md`, `REVIEW_PROTOCOL.md`, plus
`examples/dosage_calculator/RECONCILIATION.md`) checked against the
actual repo state and fixed where wrong, not just re-dated. Real finds:
an arithmetic bug ("9 new tests" next to a correct "205 total, up from
190" in three places — 9+6 is 15, not 9), two docs (`README.md`,
`SYSTEM_BLUEPRINT.md`) still describing `renal_adjustment`/Phase C as
incomplete or in-progress after they'd actually closed, two docs
(`REVIEW_PROTOCOL.md`, `RECONCILIATION.md`) still citing the Gate 4
binding-authorship question as open five weeks after it was resolved,
and `OPERATIONS_MANUAL.md`'s component map missing
`drug_interaction_checker` entirely with a 154-test count untouched
across several sessions' worth of example-adding work. Full account:
`DEVLOG.md`'s 2026-07-11 "Documentation audit" entry. PR #33, merged
same day; 205 tests pass throughout, no
regressions. **Prior update, preserved below — Phase 3 (evidence
packaging) built for
`renal_adjustment` and `drug_interaction_checker`, the two examples
whose Phase 2 (Gate C1-C6) closed the same day. `dosage_calculator`'s
existing pipeline (`metadata.yaml` → `evidence.cli` →
`traceability_matrix.a.json/.md`) was the template, but had never faced
a Dafny-only metadata file (zero crosshair/concrete_test evidence) —
running it for real surfaced three genuine gaps in shared code, all
fixed rather than worked around: `evidence/cli.py`'s
`--manifest`/`--concrete` were hard-required all the way down to a
crosshair-manifest `effective_bounds` lookup, now optional
(`manifest=None` mirrors `dafny_store`'s own already-established `None`
convention, never fabricated fake bounds data); the schema's
`toolchain.crosshair_bounds` was unconditionally required, now optional;
the schema's `id` pattern rejected `REQ-RENAL-1a`'s lowercase suffix —
the same class of gap already fixed once in `dafny_nl_summary.py`
(2026-07-08), now found independently in the schema too. A fourth,
unrelated bug fixed in the same pass:
`evidence/conflict.py::symbolic_binding_conflicts` never skipped a
`.dfy`-targeted implementation, a real gap for any future mixed
crosshair+dafny example. Every change reverified against zero
regression — `dosage_calculator`'s real artifacts regenerated and
diffed byte-for-byte (timestamps aside) before and after each fix, every
time. Both new examples' real matrices are now committed: 9 requirement
rows for `renal_adjustment` (including the first-ever dual-cited
evidence binding and two genuinely different flavors of honest GAP row
— `PROVEN`-intended for real future formalization candidates vs.
`DECLARED`-intended for a permanent trust-boundary decision), 6 rows for
`drug_interaction_checker` (the first many-requirements-to-one-proof
binding this repo's matrix binder has exercised). 15 new tests (9 for
`renal_adjustment`, 6 for `drug_interaction_checker`), 205 total (up
from 190). Full account: `KNOWN_LIMITATIONS.md`'s "Phase 3 —
evidence packaging" section. A separate, pre-existing, unrelated finding
surfaced during regression testing and deliberately not touched here:
`dosage_calculator/artifact_index.json`'s committed hash for `dosage.dfy`
is stale relative to its current content — named, not fixed in passing.

**Prior update, preserved: 2026-07-11** — `renal_adjustment.dfy`'s Gate
C6 sign-off
is now confirmed and closed. Steven reviewed the six checkpoints from
`nl_confirmation_renal_adjustment_dfy.md` (RoundHalfUp's tie-break
framing, GStage's boundaries, SelectFormula's BMI thresholds, the Gate
C4 pinning fixes, and the eGFR/CrCl split's forced asymmetry) against
the raw KDIGO/MHRA sources directly — every checkable claim
independently re-verified against the real committed source files and
live Dafny re-runs (both Pow-expressiveness probes re-run: still fail /
still verify exactly as established; the STP suite re-run: `52 verified,
0 errors`, unchanged) before being recorded. **One citation flagged, not
silently absorbed**: a supporting claim about "Sheffield and BSW"
clinical calculator sources corroborating the 88.4 conversion factor
could not be verified — no such source exists anywhere in this
repository. Not treated as confirmed; the underlying claim it was
attached to didn't depend on it and was already independently
established via a direct MHRA source re-fetch in an earlier session. See
`nl_confirmation_renal_adjustment_dfy.md`'s Decision section for the
full account. **`renal_adjustment` now has all six Gate C1–C6 pipeline
steps both built and confirmed** — the only remaining items are the
named, deliberately unbuilt requirements (`REQ-RENAL-3`, `REQ-RENAL-4`,
`REQ-RENAL-6`, `REQ-RENAL-7`; `REQ-RENAL-8`'s classification-flag
provenance question, reclassified as a Phase 3 concern).

**Prior update, preserved: 2026-07-10**, while walking through Gate C6's
actual sign-off review with Steven. Before confirming, he pushed on
whether the
closing claim for Gate 1c Finding 1 ("eGFR caller-supplied because
Dafny/Z3 can't express it") was actually earned by the evidence, not
just asserted — it wasn't: the prior "confirmed" was circular between
`GATE_1C_AUDIT.md` and a sources doc, neither containing a real test.
Tested for the first time with two committed probes
(`examples/renal_adjustment/run_verify_pow_probes.py`): Dafny has no
real-exponentiation primitive at all, and the obvious axiom workaround
verifies trivially even for an absurd, wrong claim about it — see
`GATE_1C_AUDIT.md`'s 2026-07-10 addendum. **This is the pattern to
repeat: before signing off Gate C6 on any spec, check whether every
claim the spec's comments make was actually tested, not just carried
forward as reasoning that sounded right the first time.** Gate C6
sign-off itself is still open pending Steven's read-through of
`nl_confirmation_renal_adjustment_dfy.md` — this strengthened the
evidence behind one of its closing claims, it didn't close the gate.

**Same-day addendum:** two follow-up items closed. `SYSTEM_BLUEPRINT.md`
and `KNOWN_LIMITATIONS.md` had themselves drifted behind this exact
2026-07-10 entry (still said 2026-07-09) — fixed with a real content
review, plus a new mechanical test
(`tests/test_docs_current_with_devlog.py`) so that specific drift can't
recur silently. A pytest CI job (`.github/workflows/tests.yml`) was also
added, alongside the existing PayloadGuard scan — see the "Working
conventions" section below, which was itself corrected at the same time
(it still said "no CI is configured on this repo").

**Second same-day addendum: a third worked example started.**
`examples/drug_interaction_checker/` (NHS SPS DOAC-interaction
guidance, testing whether the pipeline generalizes to set/list-
membership logic) went through Gate 1a (sourced), Gate 1c (three real
findings — a dropped risk-direction axis, a `CheckInteraction` function
non-total over its own declared `Agent` type, two genuinely ambiguous
source cells — all resolved by explicit decision, none deferred), and
Gate C1 (spec + capture, verifies clean). **Gate C1 caught a real
false-clean result before it was committed:** an early draft with no
`ensures` clauses reported "0 verified, 0 errors" — not a pass, a sign
Dafny had nothing to actually prove (match-exhaustiveness is a
resolve-time syntax check, not an SMT proof). Fixed by adding three
real `ensures` clauses before committing anything. See
`examples/drug_interaction_checker/PHASE1_PLAN.md`,
`GATE_1C_AUDIT.md`, and `KNOWN_LIMITATIONS.md`'s "Phase E Gate C1"
section for the full account.

**Third same-day addendum: Gate C4 found the Gate C1 fix was itself
only a stopgap, then Gate C3 required real engineering, not just
application.** Gate C4 (STPs): a real IronSpec ACCEPT lemma restating
just the 3 `ensures` clauses Gate C1 added failed to prove the correct
value for cells they didn't directly mention — confirmed with a real
failing capture (`0 verified, 3 errors`), preserved as a proper honesty
exhibit before fixing anything. Fixed with 60 comprehensive pinning
`ensures` clauses plus a real 11-lemma ACCEPT/REJECT STP suite (Dafny's
own capture reads `22 verified, 0 errors` — ~2 verification tasks per
lemma, not a 1:1 lemma count, corrected 2026-07-10 after this line and
several other docs previously misread it as "22 lemmas"). Gate
C3: `CheckInteraction`'s precondition compares `doac`/`agent` directly
against datatype constructors — `evidence/dafny_spec_lint.py`'s Z3
translator genuinely refused this (a real gap, not renal_adjustment's
narrower "unreferenced parameter" one) until extended to model simple
Dafny datatypes as a Z3 `EnumSort`. Caught a second, independent,
generally-applicable bug while testing the extension: Z3 registers
`EnumSort` names globally per process, so two callers modeling a
same-named type collide — fixed with a per-call disambiguating tag.
Full accounts: `KNOWN_LIMITATIONS.md`'s "Phase E Gate C4"/"Phase E Gate
C3" sections.

**Fourth same-day addendum: Gate C2 confirmed, no new gap.** Unlike
C3/C4, this one found nothing broken — it confirmed
`evidence/render/matrix_variants.py::dafny_record()`/
`assert_no_realized_proven` (built 2026-07-07, tested thoroughly
against `dosage_calculator`) actually works against an independently-
authored spec's real capture, the first time since `dosage_calculator`
itself (`renal_adjustment` never reached this point — no `metadata.yaml`
was ever built for it). Run for real: produces a genuine PROVEN record,
accepted cleanly by R3; two negative-case checks (tampered `method`,
tampered `verifier_completion_status`) confirm R3 still independently
refuses, not just trusting the binder's own diligence. See
`KNOWN_LIMITATIONS.md`'s "Phase E Gate C2" section. Gates C5/C6 not
started yet.

**Fifth same-day addendum: Gate C5 built, found and fixed a real crash
bug in Gate C3's own code, then 7 real survivors.** 962 mutants
(ROR/LOR/COI; AOR/LVR both confirmed contributing zero — no arithmetic
operator or numeric literal anywhere in `CheckInteraction`). **A real
crash, not a Dafny finding, caught mid-run**: a ROR mutant introducing
`<=`/`>=` between two `DOAC` datatype operands crashed
`evidence/dafny_spec_lint.py`'s Z3 translator with a raw Python
`TypeError` — Z3's Python bindings don't overload ordering operators for
`DatatypeRef` the way they do for `==`/`!=`. Fixed in `_apply_cmp` (a
`z3.is_arith` guard, refusing cleanly via `SystemExit` instead of
crashing) — a shared-module fix, shipped as its own PR before the full
mutation run could even complete. Final real run: **564 killed, 389
filtered_static, 7 survived, 2 unclassifiable.** The 2 unclassifiable
are genuine Dafny type errors on `<=`/`>=` between `DOAC` values — a
materially different failure mode from `renal_adjustment`'s own
unclassifiable case (a parser ambiguity, not a type error). The 7
survivors fall into the same two structural categories
`renal_adjustment`'s own Gate C5 already established — no new category
of finding: 4 mutate the one `requires` clause's `doac == Apixaban`
comparison (not load-bearing for any of the 60 `ensures` clauses); 3
mutate one `ensures` clause's `doac == Dabigatran` antecedent (the
consequent is independently guaranteed for the other three DOACs by
sibling clauses, confirmed directly against the real spec text). An
earlier draft's prediction that ordering comparisons on datatype values
would be "always killed" was wrong — corrected in place in
`run_mutation_suite_ddi.py`'s own comments, left visible rather than
silently rewritten. See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C5"
section. Gate C6 is the only gate left unbuilt for this example.

**Sixth same-day addendum: Gate C6 built, genuinely extended the shared
NL-summary generator — a different call than `renal_adjustment`'s own
equivalent gap.** `evidence/dafny_nl_summary.py::summarize_method`
refused outright on first attempt: `CheckInteraction`'s one `requires`
clause spans three physical lines, the first genuinely multi-line clause
this repo has pointed the summary generator at (every clause in
`dosage.dfy`/`renal_adjustment.dfy` happened to be one line).
`renal_adjustment` hit an equivalent gap for two `ensures` clauses and
that time the fix was to reformat them to single-line rather than extend
the tool ("a formatting choice that was mine, not a genuine spec need").
**This time the call went the other way, for a concrete reason**: this
spec already had committed Gate C1/C4/C5 captures bound to its current
formatting, so a cosmetic reformat would have meant re-running and
re-committing all three for a change with zero semantic content. Fixed
instead by making `_extract_annotated_clauses` accumulate a clause
across multiple physical lines — ending accumulation at a blank line, a
standalone `//`-comment line, or the next clause keyword, so a
free-floating block comment between two clauses (this spec has several)
is never misattributed as either clause's citation. The original
single-line regex is preserved unchanged, since `dafny_mutate.py`
imports it for a different, byte-precise need this extension didn't
touch. The safety net is unchanged in spirit: still cross-checks against
`dafny_spec_lint`'s canonical extractor and refuses on any mismatch — a
comment sitting on its own line *inside* a multi-line clause (as opposed
to between two clauses) still correctly refuses, genuinely ambiguous,
confirmed by a new regression test. Verified end-to-end: all 60
`ensures` clauses and the one multi-line `requires` clause reconstruct
byte-for-byte correctly. **A real, notable fact this summary surfaces,
not a defect**: none of `CheckInteraction`'s 60 `ensures` clauses carry
an inline `REQ-DDI-*` citation — unlike `dosage.dfy`/`renal_adjustment.dfy`'s
per-clause style, this spec is validated as a whole lookup table, so
every `*(no requirement cited)*` is accurate, flagged explicitly for
Steven to confirm at sign-off. Presented in
`examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`.
3 new/changed
tests in `tests/test_dafny_nl_summary.py`, 190 total (up from 188). See
`KNOWN_LIMITATIONS.md`'s "Phase E Gate C6" section.

**Seventh same-day addendum: Gate C6 sign-off confirmed by Steven —
against the raw source directly, and it caught a real doc-accuracy bug
in the sign-off document's own text along the way.** Not a rubber
stamp: Steven checked the sign-off document's four numbered items
against `sources/sps-doac-interactions-2024.md` directly and found item
1 mislabeled the precondition's exclusion as apixaban's "real source
gap" — that phrase belongs to a different, genuinely-silent cell
(apixaban+dronedarone), already correctly labeled that way in both the
`.dfy` spec and the STP suite. The precondition's actual exclusion
(`Apixaban` + `{Rifampicin, Carbamazepine, Phenytoin, Phenobarbital}`)
is indication-dependent, not silence — confirmed verbatim against source
lines 80-84/135-136: "use apixaban with caution" for two named
indications, an explicit branch v1 doesn't model (`REQ-DDI-5`). Fixed in
the sign-off document (no `.dfy` change needed — the precondition was
always correct, only the rationale needed tightening). Every other
sign-off item was independently re-verified against the real source, not
taken on faith, and a programmatic cross-reference confirmed the 60
`ensures` clauses, the NL summary, and the STP suite's 11 lemmas are
mutually consistent. Full account: `KNOWN_LIMITATIONS.md`'s "Phase E
Gate C6 sign-off" section. **All six Gate C1–C6 pipeline steps have now
been built AND confirmed for this example — Gate C6 is closed.** What
remains is only the explicitly out-of-scope v2 items
(`REQ-DDI-5`/`REQ-DDI-6`).

## What this repo is, in one paragraph

Turns real verification tool output (CrossHair, Dafny/Z3) plus authored
metadata into IEC 62304/FDA §524B traceability artifacts, where every
claim is bound to a committed, replayable evidence record of honestly-
labeled strength — `PROVEN` can never appear unless a real, completed
Dafny proof produced it. Full explanation: `README.md` (plain-English)
and `OPERATIONS_MANUAL.md` (technical reference — read this one if
you're about to build something, not just read about the system).

## Current state of all three worked examples

**`examples/dosage_calculator/` — complete.** Every requirement carried
through source citation → formal spec → mathematical proof → mutation
testing → recorded human sign-off. Nothing pending here. Don't touch it
unless something new demands it — it's the reference implementation the
second example was built to prove the pipeline generalizes to.

**`examples/renal_adjustment/` — Phase 2 done: all six Gates C1–C6
built AND confirmed. Phase 3 (evidence packaging) also built,
2026-07-11.** Read `examples/renal_adjustment/PHASE1_PLAN.md`
top to bottom before touching this example — it's the living status
document for this example specifically and is kept current, unlike this
handoff file's example-agnostic summary. As of this writing:

- Gate 1 (clinical sourcing, spec skeleton, consistency audit) is
  closed under one remaining named, deliberately provisional fallback
  assumption (the CrCl/eGFR one below is now closed for Cockcroft-Gault)
  — see `PHASE1_PLAN.md`'s "Closed under named fallback assumptions"
  section.
- `renal_adjustment.dfy` exists, is committed, and verifies (`7
  verified, 0 errors`) — seven functions: `RoundHalfUp`, `GStage`,
  `SelectFormula`, `ComposedCeiling`, `AssessRenalFunction`,
  `CockcroftGaultCrClMlPerMin`, `AssessRenalFunctionFromInputs`.
- **Gate C6 (NL confirmation) confirmed and closed, 2026-07-11.** The
  sign-off document (`nl_confirmation_renal_adjustment_dfy.md`) — three
  amendments (two functions fixed 2026-07-09, two functions added
  2026-07-09) plus the original seven-function summary — was reviewed
  by Steven against the raw KDIGO/MHRA sources directly, not rubber-
  stamped: every checkable claim independently re-verified against the
  real source files and live Dafny re-runs before being recorded. One
  unverifiable supporting citation ("Sheffield and BSW" sources) was
  flagged, not silently absorbed — see the Decision section for the
  full account.
- Gate C4 (STPs) is built and found + fixed two real gaps for real
  (`ComposedCeiling`, `AssessRenalFunction` both needed pinning
  clauses) — see `gate_c4_stp_plan.md` and the `_underconstrained`/
  `_stp_suite_against_underconstrained` honesty-exhibit files. Extended
  2026-07-09 with real ACCEPT/REJECT lemma coverage for the two new
  functions below (`52 verified, 0 errors`, up from 44).
- **Gate C3 (spec lint) built 2026-07-09** — all seven functions pass
  vector 1 (satisfiable preconditions); five have expected vector 2
  warnings (one-way `==>` clauses, all STP-covered). Found and fixed a
  real gap: the checker used to build a Z3 symbol for every declared
  parameter regardless of use, refusing on `AssessRenalFunction`'s
  unused `Formula`-typed parameter — narrowed to only model referenced
  parameters.
- **Gate C5 (mutation testing) built 2026-07-09** — 450 mutants across
  all seven functions, 51 survivors, all explained and categorized (not
  a proof gap — see `examples/renal_adjustment/README.md`'s Gate C5
  amendment for the three named categories), plus two named engine
  limitations (a `||`-chain ambiguity, two arithmetic-embedded LVR
  literals) deliberately not fixed — real new engineering, and Gate C4's
  STPs already cover what they'd add. Four real engine gaps found and
  fixed along the way (missing tokenizer chars, int/real literal typing)
  — see `run_mutation_suite_renal.py`'s module docstring.
- **All six Gate C1–C6 pipeline steps are now built and confirmed —
  this example's Phase 2 is done.** The named, deliberately unbuilt
  requirements (`REQ-RENAL-3`, `REQ-RENAL-4`, `REQ-RENAL-6`,
  `REQ-RENAL-7`) and `REQ-RENAL-8`'s classification-flag provenance
  question remain unbuilt, but are no longer blocking anything — see
  Phase 3 below.
- **Phase 3 (evidence packaging) built, 2026-07-11.**
  `metadata.a.yaml`/`dafny_captures_index.json`/`traceability_matrix.a.json`/`.md`
  committed — 9 requirement rows: REQ-RENAL-1/1a/2/5 with real dafny
  evidence (`AssessRenalFunction` dual-cited to both REQ-RENAL-1 and
  REQ-RENAL-2, matching the `.dfy` file's own inline citation),
  REQ-RENAL-3/4/6/7 as honest GAP rows intending `PROVEN` (real future
  formalization candidates), REQ-RENAL-8 as a GAP row intending
  `DECLARED` (a permanent trust-boundary decision, not a proof target —
  a deliberately different treatment, not the same gap category). Built
  against a Dafny-only metadata file — the first time this repo's
  evidence-packaging pipeline has faced zero crosshair/concrete_test
  evidence, which found and fixed three real gaps in shared code (see
  `KNOWN_LIMITATIONS.md`'s "Phase 3" section). 9 new tests,
  `tests/test_renal_adjustment_matrix.py`.

**`examples/drug_interaction_checker/` — Phase 2 done, all six
Gates C1–C6 built and confirmed. Phase 3 also built, 2026-07-11;
REQ-DDI-5/REQ-DDI-6 built 2026-07-12, no GAP rows remain.** Read
`examples/drug_interaction_checker/PHASE1_PLAN.md` top to bottom before
touching this example. Third worked example, testing whether the
pipeline generalizes to **set/list-membership logic** — sourced from
NHS SPS's DOAC-interaction guidance, UK-jurisdiction like
`renal_adjustment`. As of this writing:

- Gate 1a (clinical sourcing) closed: single primary source, chosen
  after direct comparison against BNF/MHRA DSU (bounded, versioned,
  publicly fetchable, states its own scope boundary explicitly).
- Gate 1c (consistency audit) closed: three real findings — a dropped
  risk-direction axis, a `CheckInteraction` function non-total over its
  own declared `Agent` type, two genuinely ambiguous source cells — all
  resolved by explicit decision, none deferred (unlike `renal_adjustment`'s
  own Finding 1, which was deliberately left open).
- `drug_interaction_checker.dfy` exists, is committed, and verifies (`1
  verified, 0 errors`) — `CheckInteraction`, 63 match arms across 15 v1
  agents, 60 pinning `ensures` clauses (one per match arm).
- **Gate C1's first draft had a real false-clean result, caught before
  committing:** an early version with no `ensures` clauses reported "0
  verified, 0 errors" — Dafny had generated zero verification tasks,
  not zero problems.
- **Gate C4 then found the fix was itself only a stopgap, and this time
  the gap was real and much bigger — confirmed with a genuinely failing
  captured run, not just predicted.** The 3 `ensures` clauses Gate C1
  first added didn't pin almost anything: a real IronSpec ACCEPT lemma
  restating just those 3 clauses failed to prove the correct value for
  `(Dabigatran, Ketoconazole)` — and 3 more such lemmas, preserved
  against `drug_interaction_checker_underconstrained.dfy`, genuinely
  fail as a committed capture (`0 verified, 3 errors`). Fixed for real
  by pinning all 63 cells explicitly, then building a real 11-lemma
  ACCEPT/REJECT STP suite (`22 verified, 0 errors` — ~2 verification
  tasks per lemma, not a 1:1 count) with REJECT coverage for the three
  `Contraindicated` cells specifically. See `KNOWN_LIMITATIONS.md`'s
  "Phase E Gate C1"/"Phase E Gate C4" sections for the full account —
  worth reading before assuming a clean `dafny verify` pass on any
  future function means something was actually checked, or that adding
  *some* `ensures` clauses means enough were added.
- **Gate C3 then required genuinely extending shared tooling, not just
  running it.** `evidence/dafny_spec_lint.py`'s Z3 translator refused
  `CheckInteraction`'s precondition outright (`doac == Apixaban`
  compares a datatype value directly — a real gap this repo's earlier
  worked examples never hit, since `renal_adjustment`'s one
  datatype-typed parameter was never referenced by any precondition).
  Fixed by modeling simple, zero-argument-constructor Dafny datatypes as
  a Z3 `EnumSort` — a real, if narrower-than-originally-feared,
  extension. Caught a second, independent bug while testing it: Z3
  registers `EnumSort` names globally per process, not per call, so two
  callers modeling a same-named type collide — fixed with a per-call
  disambiguating tag that protects every future caller, not just this
  one. See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C3" section.
- **Gate C2 confirmed, no new gap this time.** The PROVEN-exclusivity
  binder (`dafny_record()`/`assert_no_realized_proven`, built
  2026-07-07) had never been run against anything but
  `dosage_calculator`'s captures — `renal_adjustment` never got a
  `metadata.yaml`, so it never exercised this path at all. Run for real
  against this example's capture: produces a genuine PROVEN record,
  accepted cleanly; two negative-case checks confirm R3 still
  independently refuses tampered records shaped like this one, not just
  trusting the binder. See `KNOWN_LIMITATIONS.md`'s "Phase E Gate C2"
  section.
- **Gate C5 (mutation testing) built** — 962 mutants (ROR/LOR/COI; AOR/
  LVR confirmed contributing zero). Found and fixed a real crash bug in
  `evidence/dafny_spec_lint.py`'s `_apply_cmp` along the way (ordering
  operators on datatype/`EnumSort` operands weren't modeled by Z3's
  Python bindings, crashed instead of refusing cleanly) — shipped as its
  own PR. Final: 564 killed, 389 filtered_static, 7 survived (both
  explained categories already established by `renal_adjustment`'s own
  Gate C5), 2 unclassifiable (genuine Dafny type errors, a different
  failure mode from `renal_adjustment`'s parser-ambiguity case). See
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C5" section.
- **Gate C6 (NL-dialogue confirmation) built.** Refused on first
  attempt — `CheckInteraction`'s one `requires` clause is the first
  genuinely multi-line clause this repo has pointed
  `evidence/dafny_nl_summary.py::summarize_method` at. Fixed by
  genuinely extending the tool to accumulate a clause across multiple
  physical lines (a deliberately different call than `renal_adjustment`'s
  own equivalent gap, which was fixed by reformatting the spec instead —
  this spec already had Gate C1/C4/C5 captures bound to its current
  formatting, so reformatting would have meant re-committing all three
  for a cosmetic change). Verified end-to-end against the real spec;
  presented for sign-off in
  `nl_confirmation_drug_interaction_checker_dfy.md` — **confirmed by
  Steven, against the raw source directly**, which caught and fixed a
  real doc-accuracy bug in the sign-off document's own text (item 1
  mislabeled an indication-dependent precondition exclusion as apixaban's
  "source gap" — the precondition itself was always correct). See
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C6 sign-off" section.
- **All six Gate C1–C6 pipeline steps built AND confirmed for this
  example, as of 2026-07-13 (later) — Gate C6 is closed.** See the
  2026-07-13 "Last updated" entry at the top of this file for the full
  final-review and sign-off account. Both
  previously out-of-scope v2 items are built (2026-07-12) and refined
  (2026-07-13): `REQ-DDI-5` (the `TreatmentIndication` axis for the two
  apixaban+inducer cells — `CheckInteraction`'s `requires` clause
  removed entirely, the function is now total) and `REQ-DDI-6` (the
  numeric dose-reduction targets, proven by `DoseReductionTargetMg`,
  which as of 2026-07-13 also carries an indication guard on its own
  Dabigatran+Verapamil cell). See the 2026-07-13 "Last updated" entry at
  the top of this file for the full account.
- **Gate C6 review, 2026-07-13: all four findings resolved.** A
  pre-sign-off review of the two 2026-07-12 addenda
  (`nl_confirmation_drug_interaction_checker_dfy.md`) found three real
  defects, all independently re-verified against the actual committed
  artifacts before acting: (1) a stale "Summary presented" block —
  **fixed**, regenerated for real, twice (once after the initial finding,
  again after the constructor fix below changed the signature again);
  (2) a missing review item for the Qodo-driven `assert false` fix —
  **fixed**, added; (3) `DoseReductionTargetMg(Dabigatran, Verapamil) ==
  110` proven unconditionally when the source scopes it to specific
  indications — **fixed**, on Steven's decision after primary-source
  verification confirmed dabigatran genuinely has a third, current,
  UK-licensed indication (`sources/emc-smpc-dabigatran-indications-2025.md`)
  the SPS interaction row is silent on: `TreatmentIndication` gained
  `OrthopaedicVTEProphylaxis`, `DoseReductionTargetMg` gained the
  indication parameter and guard. A fourth, independent finding surfaced
  while building the fix — `evidence/dafny_mutate.py`'s clause locator
  silently truncated the new multi-line clauses, a real coverage
  regression neither Dafny nor pytest's pinned counts caught on their
  own — **fixed** by reformatting to single lines (matching
  `renal_adjustment.dfy`'s own precedent for this exact class of gap).
  All six gates re-run for real: C4/STP `23 verified, 0 errors` (up from
  20, a new domain-coherence lemma proving apixaban's absence as a
  theorem); C5 1250 mutants — 668 killed, 482 filtered_static, 74
  survived, 26 unclassifiable (every count's jump is real, previously-
  missing coverage, not a new finding class). Phase 3 regenerated: still
  6/6 `PROVEN`, no GAP rows. Full account:
  `examples/drug_interaction_checker/
  nl_confirmation_drug_interaction_checker_dfy.md`'s "Addendum 3."
- **Gate C6 review, 2026-07-13 (later, after PR #40 merged): a second
  Qodo review found a real scope-leak bug — fixed.** `CheckInteraction`'s
  four apixaban+inducer match arms computed `Caution` unconditionally,
  never inspecting `treatmentIndication` — harmless while that type had
  only two constructors, but silently wrong once
  `OrthopaedicVTEProphylaxis` (added for `DoseReductionTargetMg`'s own
  guard, same PR) made a third value constructible. Independently
  re-verified against the merged source before fixing; each arm now
  branches on `treatmentIndication`, returning `NotCovered` for the
  orthopaedic indication (matching `(Apixaban, Dronedarone)`'s
  convention). All six gates re-run: C4/STP `25 verified, 0 errors` (up
  from 23); C3 weak-postcondition count 68 (up from 64); C5 1342
  mutants — 744 killed, 522 filtered_static, 50 survived, 26
  unclassifiable (`CheckInteraction`'s own survivors dropped 31 → 7).
  Phase 3 regenerated: still 6/6 `PROVEN`. Full account:
  `nl_confirmation_drug_interaction_checker_dfy.md`'s "Addendum 4." Gate
  C6 sign-off still open — all findings across both Addenda 3 and 4 are
  resolved, but Steven's actual review of the current spec shape (a
  recorded human decision) still hasn't happened.
- **Gate C5 extended, 2026-07-13 (later): re-verifies the STP suite
  against every mutation-testing survivor, catching a real latent gap.**
  Hand-probed before building: the STP suite's own ACCEPT lemmas (reused
  verbatim) catch the 6 `DoseReductionTargetMg` requires-clause
  indication-guard survivors — the same class of scope-leak the entry
  above fixed on `CheckInteraction`, here caught as a latent gap before
  it could ever become a real regression. Confirmed the escalation does
  NOT help for the other 44 survivors (both functions are plain,
  non-`{:opaque}` Dafny `function`s, so same-module STP lemmas verify by
  Dafny unfolding the body directly, making mutated `ensures`-clause
  text provably irrelevant — a genuine semantics limit, not a shortfall).
  Real run: 1342 mutants — 744 killed, 522 filtered_static, **44
  survived** (down from 50), 26 unclassifiable, **6
  killed_via_stp_suite**. 215 tests pass (up from 214).
- **Phase 3 (evidence packaging) built, 2026-07-11; regenerated
  2026-07-12 after REQ-DDI-5/6.**
  `metadata.a.yaml`/`dafny_captures_index.json`/`traceability_matrix.a.json`/`.md`
  committed — 6 requirement rows: REQ-DDI-1/2/3/4/5 all sharing the SAME
  one `dafny_captures_index.json` entry (the first
  many-requirements-to-one-proof binding this repo's matrix binder has
  ever been exercised against — confirmed working end to end, not
  assumed from the schema allowing it in principle), REQ-DDI-6 binding
  its own separate `DoseReductionTargetMg` capture (the first time this
  repo's matrix binder has bound two different Dafny methods from the
  same spec file across two requirements in one metadata file). **No GAP
  rows remain in this example as of 2026-07-12** — every requirement now
  has real, bound `PROVEN` evidence. Originally built first (the
  simpler, single-capture shape), ahead of `renal_adjustment`'s own
  Phase 3 build — this is where the three real shared-code gaps
  (`--manifest`/`--concrete` hard-required, schema's `crosshair_bounds`
  hard-required, schema's `id` pattern rejecting lowercase) were
  actually found and fixed, before `renal_adjustment`'s own build
  benefited from the already-fixed pipeline. See `KNOWN_LIMITATIONS.md`'s
  "Phase 3" and "Phase E REQ-DDI-5/REQ-DDI-6" sections.
  `tests/test_drug_interaction_checker_matrix.py`.

## One thing explicitly left open, not forgotten

1. **Classification-flag provenance** (`REQ-RENAL-8`): who sets
   `SelectFormula`'s caller-supplied boolean flags, by what process.
   The trust boundary itself is permanent and will never be a Dafny
   proof target; the open part is only the operational process
   (clinician form / EHR lookup / static versioned list). Scoped
   2026-07-11: **Steven is actively gathering that real-world process
   data** (talking to the relevant people), so the Phase 3 matrix row is
   deliberately parked as an explicit `DECLARED`-intent GAP until it's
   in hand — parked, not abandoned. When the answer lands it will be a
   DECLARED process fact packaged as evidence, not a proof. No code
   change was made or needed to leave the GAP honest; see
   `KNOWN_LIMITATIONS.md`'s "Phase 3 — evidence packaging" section.

**Closed, 2026-07-09 — CrCl/eGFR value computation** (Gate 1c "Finding
1"): Cockcroft-Gault CrCl is now computed
(`CockcroftGaultCrClMlPerMin`/`AssessRenalFunctionFromInputs`, both
verified and STP-covered). CKD-EPI eGFR stays caller-supplied — Steven's
framing, confirmed correct: "if we have to tie to specific software then
if we physically cannot at the moment, then the choice is made for us"
— Dafny/Z3 genuinely cannot express CKD-EPI's real-valued fractional
exponents on a variable base, so that half was never actually a choice.
**This was only an asserted claim until 2026-07-10** — direct challenge
before Gate C6 sign-off ("can we actually make this claim with the
evidence we have?") found the prior "confirmed" was circular between
two docs, neither containing a real test. Now empirically demonstrated:
`examples/renal_adjustment/run_verify_pow_probes.py` shows Dafny has no
real-exponentiation primitive at all, and that the obvious axiom
workaround verifies trivially even for an absurd, wrong claim — see
`GATE_1C_AUDIT.md`'s 2026-07-10 addendum.
Closing this also re-verified the MHRA and NICE NG203 source URLs
(both unchanged since 2026-07-08) and caught a real, minor attribution
error along the way: earlier notes called the derived 1.23/1.04
multiplier "MHRA's constants" when MHRA's page states no formula or
constant at all — see `GATE_1C_AUDIT.md`'s 2026-07-09 addendum and
`sources/mhra-renal-formula-selection-2019.md`'s amendment.

## A standing discipline, learned the hard way more than once this build

- **Verify empirically before trusting a claim, including your own
  claims and this repo's own prior claims.** The infrastructure plan
  predicted Gate C6's tooling "generalizes for free" to
  `renal_adjustment.dfy` — it didn't; `_find_method_header` only
  matched Dafny's `method` keyword, never `function`, because the first
  worked example always had both and the gap was untested until the
  second example actually exercised it. Small real fixes to shared code
  are normal and expected when a second example stresses a different
  shape — that's the point of having a second example.
- **External "research findings" documents have contained fabricated
  citations, more than once, including a repeat of the same fabrication
  across two separate documents.** Use `evidence/citation_gate.py`
  (built specifically for this) to mechanically check any claimed quote
  against real source text before trusting it — it won't catch
  everything (it can't fetch sources itself, and it just had its own
  real false-positive bug fixed — see `DEVLOG.md`'s 2026-07-09 audit
  entry), but it's a real, tested first line of defense, not a
  suggestion.
- **A clean `dafny verify` pass proves the spec is internally
  consistent, not that it says what you think it says.** Both real gaps
  Gate C4 found in `renal_adjustment.dfy` verified perfectly clean
  before being caught — the postconditions bounded a result without
  pinning it to an exact value. Write the STP before trusting a clean
  pass at face value.
- **"0 verified, 0 errors" is not the same claim as "N verified, 0
  errors" for N > 0 — check which one a capture actually says before
  calling a gate built.** `drug_interaction_checker.dfy`'s first draft
  had no `ensures` clauses and reported exactly this: zero errors
  because there was nothing to disprove, since Dafny generates zero
  verification tasks for a function with no postconditions
  (match-exhaustiveness is a resolve-time syntax rule, not an SMT
  proof). Caught before committing by actually reading the count, not
  just the "0 errors" half of the line.
- **Adding *some* `ensures` clauses isn't the same as adding *enough* —
  Gate C4 exists precisely to test that, and it found a real gap even
  right after Gate C1's own fix above.** The 3 clauses added to fix the
  "0 verified" problem were real, but only covered 3 of 63 match arms;
  a genuine IronSpec ACCEPT lemma restating just those 3 as premises
  still failed for every other cell, confirmed with a real committed
  failing capture (`0 verified, 3 errors`), not assumed from the fact
  that the main file itself verified clean. A clean `dafny verify` on
  the function being specified says nothing about whether cells outside
  its `ensures` clauses are actually guaranteed — only Gate C4's
  spec-only lemmas test that directly.
- **Hand-derive a prediction before building, especially for mutation
  testing and STPs.** Every extension in this repo's history that did
  this caught something real or confirmed its own reasoning explicitly,
  rather than discovering after the fact whether the approach worked.
- **Never hand-edit a generated artifact.** If a traceability matrix or
  report looks wrong, the metadata or capture it came from is wrong —
  fix that, regenerate.
- **A generator that happily produces a mutant doesn't mean the
  translator underneath can actually evaluate it.** Gate C5's ROR
  generator has no reason to know `evidence/dafny_spec_lint.py`'s Z3
  translator can't handle an ordering operator between two datatype
  values — it generated the mutant anyway, and the translator crashed
  with a raw Python `TypeError` instead of refusing cleanly like every
  other unsupported construct. Mutation testing exercises shared tooling
  in combinations its own test suite never tried; treat a crash found
  this way as a real bug in the shared module, not a mutation-suite
  quirk to work around locally.
- **Full review discipline:** `REVIEW_PROTOCOL.md`. **Full known-gap
  ledger:** `KNOWN_LIMITATIONS.md`. **Full dated history:** `DEVLOG.md`
  — this handoff file is a summary, not a replacement for it.

## Working conventions specific to this environment

- Tests: `python -m pytest tests/ -q` — must pass before any commit.
  214 as of this writing.
- Dafny 4.11.0 / Z3 are installed; `dafny verify <file>.dfy` works
  directly.
- Branch workflow used this session: create a `claude/<topic>` branch
  off `main`, commit there, open a PR. **Two CI checks now run on every
  PR into `main` (added 2026-07-10, both real — this line was stale
  before that and said "no CI is configured," "0 checks"):**
  `.github/workflows/tests.yml` (`python -m pytest tests/ -q`) and
  `.github/workflows/payloadguard.yml` (third-party pre-merge scan —
  see `KNOWN_LIMITATIONS.md`'s "PayloadGuard CI gate" entry). **Branch
  protection now requires human approval before merge** — open the PR,
  let both checks run, then stop and wait; don't auto-merge even once
  CI is green. `main` is the live, current state; feature branches are
  short-lived and not meant to accumulate.
- Every real tool run (Dafny, CrossHair, pytest) gets its raw output
  and a manifest committed verbatim — never re-typed, never smoothed
  over if the result is unexpected.
