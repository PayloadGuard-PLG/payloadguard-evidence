# SYSTEM_BLUEPRINT — payloadguard-evidence

Last updated: 2026-07-14 (`HAZARD_REGISTER.md` landed for
`dosage_calculator`, at `examples/dosage_calculator/HAZARD_REGISTER.md`
— first real hazard-register artifact in this repo, chosen as easiest
because its primary source (`sources/gip-v1.0-hazard-analysis.md`) is
itself a formal published hazard analysis, already partially cited in
this device's STRIDE threat model. Four hazard entries — 3 GIP-sourced,
1 not, stated plainly — plus an explicit out-of-scope section so the
register isn't misread as covering the full pump. Severity/probability/
evaluation left explicit `GAP`s; hazard identification only. No
component, gate, or data-flow change. Branch restarted from latest
`main` first (PR #45 merged). See `KNOWN_LIMITATIONS.md`'s 2026-07-14
entry and `DEVLOG.md` for the full account.) Prior header, preserved:
Last updated 2026-07-14 (`RISK_MANAGEMENT_PLAN.md` landed for
`dosage_calculator` too, at
`examples/dosage_calculator/RISK_MANAGEMENT_PLAN.md` — third and final
risk-management-plan artifact; all three worked examples now covered.
Real device-specific content, not boilerplate: the only example with
three evidence types per requirement (CrossHair/concrete/Dafny, mixed
strength — REQ-DOSE-003 has no Dafny proof, stated plainly); the
existing `kernel_scope`/`system_scope` split on REQ-GIP-1-4-12 became
Section 1's real life-cycle scoping; the existing STRIDE threat model
named as related-but-distinct from the still-missing clinical hazard
register. Gate C5 residual: 0 survivors, 0 unclassifiable — cleanest of
the three. Gate C6 (2026-07-07, Steven) was in fact the first Gate C6
sign-off recorded anywhere in this repo. No component, gate, or
data-flow change. See `KNOWN_LIMITATIONS.md`'s 2026-07-14 entry and
`DEVLOG.md` for the full account.) Prior header, preserved: Last
updated 2026-07-14 (`RISK_MANAGEMENT_PLAN.md` landed for
`renal_adjustment` too, at `examples/renal_adjustment/RISK_MANAGEMENT_PLAN.md`
— second real ISO 14971 risk-management-plan artifact, same day as the
first, mirroring its structure and already-verified clause citations.
Verification-activities section wires into the 5 real `PROVEN`
REQ-RENAL-* rows plus honest `GAP` rows for REQ-RENAL-3/4/6/7/8;
sections requiring clinical judgment left explicit `GAP`s, not
fabricated. A real, pre-existing staleness bug in
`examples/renal_adjustment/README.md` (a "Gate C6 still pending" claim,
actually closed 2026-07-11) found and fixed along the way. No
component, gate, or data-flow change. See `KNOWN_LIMITATIONS.md`'s
2026-07-14 entry and `DEVLOG.md` for the full account.) Prior header,
preserved: Last updated 2026-07-14 (`RISK_MANAGEMENT_PLAN.md` landed for
`drug_interaction_checker` at
`examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md` — the
first real ISO 14971 risk-management-plan artifact in this repo, not
just a template. Built by reading the real ISO 14971:2019 standard
directly and cross-checking a provisional, externally-supplied
template against it (one real citation slip found and fixed: the
"part of the risk management file" claim belongs to clause 4.4, not
4.5 as the template had it). Its verification-activities section wires
directly into this repo's existing evidence — all six REQ-DDI-* rows
cite real Gate C1-C6 capture files, not placeholders. Sections
requiring clinical judgment (roles, severity/probability bands,
acceptance matrix) are explicit `GAP`s, not fabricated. No component,
gate, or data-flow change — a new documentation artifact only. See
`KNOWN_LIMITATIONS.md`'s 2026-07-14 entry and DEVLOG.md for the full
account.) Prior header, preserved: Last updated 2026-07-13 (Gate C5
extended for `drug_interaction_checker`:
`run_mutation_suite_ddi.py` now re-verifies the committed STP suite
against every mutation-testing survivor, not just the bare spec.
Hand-probed empirically before building: this catches the 6
`DoseReductionTargetMg` requires-clause indication-guard survivors (the
same class of scope-leak bug fixed on `CheckInteraction` below, caught
here as a latent gap before it could ever become a real regression), but
NOT the other 44 (both functions are plain, non-`{:opaque}` `function`s,
so same-module STP lemmas verify by Dafny unfolding the body directly —
a genuine semantics limit, confirmed by hand-probing, not a shortfall).
Mutants the STP suite catches get a new, distinct `killed_via_stp_suite`
outcome, kept separate from ordinary `killed`. Real run: 1342 mutants —
744 killed, 522 filtered_static, 44 survived (down from 50), 26
unclassifiable, 6 killed_via_stp_suite. See `KNOWN_LIMITATIONS.md`'s
"Gate C5 extended: STP-suite escalation, 2026-07-13" section for the
full account; the updated `drug_interaction_checker` component-map entry
below reflects this. Prior header, preserved: Last updated 2026-07-13 (a
second Qodo review, run against PR #40 after
it merged, found a real scope-leak bug: `CheckInteraction`'s four
apixaban+inducer match arms computed `Caution` unconditionally, never
inspecting `treatmentIndication`, silently fabricating an outcome once
`OrthopaedicVTEProphylaxis` made a third indication value constructible.
Independently re-verified against the merged source before fixing; each
arm now branches on `treatmentIndication`, returning `NotCovered` for
the orthopaedic indication (matching this repo's own
`(Apixaban, Dronedarone)` silent-cell convention). All six gates re-run
for real: STP suite `25 verified, 0 errors` (up from 23, two new
lemmas); weak-postcondition count for `CheckInteraction` now 68 (up from
64); mutation suite 1342 mutants — 744 killed, 522 filtered_static, 50
survived, 26 unclassifiable (`CheckInteraction`'s own survivors dropped
31 → 7). Phase 3 regenerated, still 6/6 PROVEN. See
`KNOWN_LIMITATIONS.md`'s "Gate C6 review (second, post-merge),
2026-07-13" section for the full account; the updated
`drug_interaction_checker` component-map entries below reflect this.
Prior header, preserved: Last updated 2026-07-13 (a Gate C6 review's
real spec-scope finding
resolved: `TreatmentIndication` gained a third constructor,
`OrthopaedicVTEProphylaxis`, for dabigatran's real, current, UK-licensed
third indication (confirmed via `sources/emc-smpc-dabigatran-indications
-2025.md`), and `DoseReductionTargetMg` gained a `treatmentIndication`
parameter with an indication guard on its Dabigatran+Verapamil cell —
decided by Steven, not an assistant, after primary-source verification.
A second, independent finding surfaced while building this:
`evidence/dafny_mutate.py`'s clause-site locator silently truncated the
new multi-line clauses, a real mutation-testing coverage regression;
fixed by reformatting to single lines, matching `renal_adjustment.dfy`'s
own precedent. All six gates re-run for real; STP suite `23 verified, 0
errors` (up from 20, a new domain-coherence lemma); mutation suite 1250
mutants — 668 killed, 482 filtered_static, 74 survived, 26
unclassifiable. Phase 3 regenerated, still 6/6 PROVEN. See
`KNOWN_LIMITATIONS.md`'s "Gate C6 review, 2026-07-13" section for the
full account; the updated `drug_interaction_checker` component-map
entries below reflect this. Prior header, preserved: Last updated
2026-07-13 (a pre-sign-off review of REQ-DDI-5/REQ-DDI-6's Gate C6
addenda found two real doc defects — a stale NL summary, a missing
review item — both fixed, plus one genuine spec-scope finding left
open, later resolved as described above). Prior header, preserved: Last
updated 2026-07-12 (REQ-DDI-5
and REQ-DDI-6 built for real —
`TreatmentIndication` datatype and `DoseReductionTargetMg` companion
function added to `drug_interaction_checker.dfy`, all six Gate C1–C6
steps re-run for both requirements, Phase 3 regenerated: all 6
requirement rows in this example now render as real PROVEN evidence, no
GAP rows remain. See `KNOWN_LIMITATIONS.md`'s "Phase E REQ-DDI-5/6"
section for the full account; the updated `drug_interaction_checker`
component-map entries and summary table row below reflect the built
state. Prior header, preserved: Last updated 2026-07-12 (three new
sources added under `sources/` —
`emc-smpc-apixaban-posology-2024.md`, `mhra-dsu-doac-renal-dosing-2023.md`,
`fda-eliquis-label-interactions-2016.md` — verifying an externally-
supplied REQ-DDI-5/6 scoping document against primary sources before
any build decision. No requirement built, no code changed; see the
updated `sources/` component-map entries below and
`KNOWN_LIMITATIONS.md`'s 2026-07-12 header for the full account. Prior
header, preserved: Last updated 2026-07-11 (Phase 3 — evidence
packaging — built for
`renal_adjustment` and `drug_interaction_checker`, the first two
Dafny-only examples to reach this stage. Running `evidence.cli build`
against a metadata file with zero crosshair/concrete_test evidence
found and fixed three real gaps in shared code: `evidence/cli.py`'s
`--manifest`/`--concrete` were hard-required all the way down to
`derive_bounds_block()`'s unconditional `effective_bounds` lookup, now
optional; the metadata schema's `toolchain.crosshair_bounds` was
unconditionally required in `metadata.schema.a/b/c.json`, now optional;
the schema's `id` pattern rejected `REQ-RENAL-1a`'s lowercase suffix,
widened in all four schema files. A fourth, independent bug
(`evidence/conflict.py::symbolic_binding_conflicts` missing a `.dfy`
skip) was fixed in the same pass. `renal_adjustment`: 9 requirement
rows (REQ-RENAL-1/1a/2/5 with real dafny evidence, REQ-RENAL-3/4/6/7
as GAP rows intending `PROVEN`, REQ-RENAL-8 as a GAP row intending
`DECLARED`). `drug_interaction_checker`: 6 requirement rows
(REQ-DDI-1/2/3/4 sharing one proof, REQ-DDI-5/6 as GAP rows intending
`PROVEN`). Both matrices are the first in this repo with real GAP rows.
15 new tests, 205 total (up from 190). See `KNOWN_LIMITATIONS.md`'s
"Phase 3 — evidence packaging" section for the full account; component-
map entries for both examples' `schema/`, `conflict.py`, `cli.py`, and
`render/matrix_variants.py` below are updated accordingly). Prior
header, preserved: Last updated 2026-07-11 (`renal_adjustment.dfy`'s
Gate C6 sign-off
confirmed and closed — Steven checked all six checkpoints
(RoundHalfUp's tie-break framing, GStage's boundaries, SelectFormula's
BMI thresholds, the Gate C4 pinning fixes, the eGFR/CrCl split) against
the raw KDIGO/MHRA sources directly, with every claim independently
re-verified against the real source files and live Dafny re-runs before
being recorded. One supporting citation ("Sheffield and BSW" sources)
was flagged as unverifiable, not silently absorbed — no such source
exists in this repository. `renal_adjustment` now has all six Gate
C1–C6 pipeline steps both built and confirmed, matching
`drug_interaction_checker`'s status. See
`examples/renal_adjustment/nl_confirmation_renal_adjustment_dfy.md`'s
Decision section for the full account, and Section 7 below for its
status-block update). Prior header, preserved: Last updated 2026-07-10
(a third worked example,
`examples/drug_interaction_checker/`, was scoped and had all six Gates
C1–C6 built or confirmed — see the new Section 8 and its component-map
entry below. Gate C4 found a real spec gap larger than Gate C1's own
first-draft finding: the original 3-clause `ensures` set didn't pin
almost anything; fixed with 60 comprehensive pinning clauses plus a
real ACCEPT/REJECT STP suite. Gate C3 required extending
`evidence/dafny_spec_lint.py` itself — a shared module, not just this
example's own files — to model Dafny datatype comparisons via Z3
`EnumSort`, plus a fix for a real, generally-applicable EnumSort
name-collision bug caught along the way. Gate C2 confirmed the
PROVEN-exclusivity binder generalizes to a real, independently-authored
capture for the first time since `dosage_calculator` — no new gap, a
real generalization confirmation. Gate C5's mutation run (962 mutants)
found and fixed a real crash bug in Gate C3's own `_apply_cmp` (ordering
operators on datatype/`EnumSort` operands weren't modeled by Z3's Python
bindings, and crashed instead of refusing cleanly), then produced 7 real
survivors and 2 unclassifiable results, all explained. Gate C6 genuinely
extended `evidence/dafny_nl_summary.py` to support multi-line clauses
for the first time — a deliberately different call than
`renal_adjustment`'s own equivalent gap (fixed there by reformatting the
spec instead), made because this spec already had Gate C1/C4/C5
captures bound to its current formatting; its sign-off document was
then confirmed by Steven the same day, against the raw source directly
— which caught and fixed a real doc-accuracy bug in the sign-off
document's own text (an item mislabeling an indication-dependent
precondition exclusion as a source "gap"), closing Gate C6 for this
example. See
`KNOWN_LIMITATIONS.md`'s "Phase E Gate C5"/"Phase E Gate C6 sign-off"
sections. A real content
review earlier the
same day, not a bare date
bump: Gate 1c Finding 1's eGFR/Dafny-expressiveness half is now
empirically tested, not asserted — see Section 7 and
`GATE_1C_AUDIT.md`'s 2026-07-10 addendum; a PayloadGuard pre-merge CI
scan, a pytest CI job (`tests.yml`/`requirements.txt`), and a
`dashboards/` directory were also added — all new component-map entries
below; full narrative in `DEVLOG.md`/`HANDOFF.md` as always). Prior
header, preserved: Last updated 2026-07-09 (Phase D component-map/status
entries added —
see Section 7 and the 2026-07-09 addendum a few lines below; original
Gate C5 narrative preserved as history). Prior header, preserved: Last
updated 2026-07-07 (Gate C5, mutation testing, BUILT then EXTENDED
TWICE same day: evidence/dafny_mutate.py + examples/dosage_calculator/
run_mutation_suite.py. v1 build (ROR/LOR/COI on requires/ensures
clauses) found 2 real REQ-GIP-1-8-1 survivors, FIXED by Steven ("go
ahead and tighten REQ-GIP-1-8-1 to >") rather than silently changed,
plus 4 unclassifiable chain-direction parse errors. External research
(gate_c5_mutation_testing_research_findings.md) produced a correction
(mislabeled "MutDafny/IronSpec-style," corrected to MutDafny-style) and
two follow-ups on "build both": chain-direction-aware ROR (eliminates
the 4 unclassifiable mutants by construction) and function-body AOR on
ExpectedDose (MutDafny's own +/-/* <-> /,% group restriction eliminates
the division-by-zero false-kill risk by construction) - 42 mutants,
zero survived, zero unclassifiable at that point. Then, on "scope out
Gate C5's LVR extension" followed by "go": LVR (Literal Value
Replacement) - every numeric literal in the spec is exactly 0.0 (7
sites, audited empirically), mutated to +/-0.01 (the clinical-precision
floor from the same research, finally applied). A new magnitude-
implication filter generalizes ROR's requires/ensures polarity
principle. Real run matched the scoping session's hand-derived
prediction exactly: 14 mutants, 4 filtered, 10 real-verified, all 10
genuinely killed. **Final combined real run across all five operator
classes: 56 mutants - 41 killed, 6 filtered_static, 4
filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 4
filtered_magnitude_implied - zero survived, zero unclassifiable.** 33
new tests across all three builds; full suite 138 passed. Earlier the
same week: Gate C6,
NL-dialogue confirmation, BUILT and SIGNED OFF: evidence/dafny_nl_summary.py
mechanically summarizes a Dafny method's requires/ensures clauses in
plain English, cross-checked against dafny_spec_lint's canonical
extractor and refusing on any multi-line clause it can't safely
associate a citation with. The gate's actual deliverable,
examples/dosage_calculator/nl_confirmation_dosage_dfy.md, records
Steven's sign-off on the generated summary for CalculateHourlyDose. 7
new tests; full suite was 105 passed at that point. Earlier the
same week: Gate 2/C2-C4 wiring EXTENDED TO VARIANTS A/B - every schema
variant now binds the same real Dafny evidence for
REQ-GIP-1-4-12/REQ-GIP-1-8-1 - metadata.a.yaml's evidence list,
metadata.b.yaml's new .formal-N shadow rows, and
traceability_matrix.formal.json (variant C's third partition, built
first). intent_ok is True for both requirements in EVERY variant
artifact now (was a named, temporary A/B divergence when C landed
first; that carve-out mechanism, run_formal_check, is retired).
evidence/reconcile.py::run_gate()'s intent comparison is now subset-
based (formal.json permanently lacks an opinion about REQ-DOSE-003,
out of dosage.dfy's scope by design). evidence/cli.py gained
--dafny-captures, now required to build variant A/B at all. Gate C4
and Gates C1-C3 were built earlier the same week - see
payloadguard-evidence-roadmap-phaseB-to-C.md and KNOWN_LIMITATIONS.md).

**2026-07-09 addendum, kept deliberately short:** a second, independent
worked example (`examples/renal_adjustment/`) was built after the above
— see the new component-map entry below and Section 7 ("Phase D") for
its current state. A citation-verification module
(`evidence/citation_gate.py`) was also added. Full narrative for both
lives in `DEVLOG.md` (dated, append-only) and `HANDOFF.md` (current
status, cold-start summary) — **this header will not keep growing with
full session narrative going forward**; that growth pattern (the
paragraph above is a single week's worth of history retold inline) made
this file worse at its actual job, which is describing current
structure, not re-narrating how it got there. Component-map and
data-flow sections below are kept current; historical detail is
deliberately not duplicated here anymore.

Derived from the codebase; when in doubt, the code wins. Update this file in
the same commit as any structural change (new module, new generation path,
new evidence source, schema change) — update the STRUCTURE sections
(component map, data flow, invariants), not by appending another
paragraph of narrative to this header.

## 1. Purpose

Turn verification captures plus authored metadata into IEC 62304 / FDA §524B
traceability artifacts whose every row is bound to a committed, replayable
evidence record of known strength. The system never infers strength and
never lets declared intent leak into realized results.

## 2. Component map

```
payloadguard-evidence/
├── README.md                    Repository overview (this system, end to end)
├── SYSTEM_BLUEPRINT.md          This file — structure and data flow
├── DEVLOG.md                    Dated session log, append-only
├── .github/workflows/
│   ├── tests.yml                 pytest CI job (added 2026-07-10) — runs
│                                 `python -m pytest tests/ -q` on every
│                                 PR into main via a pinned
│                                 actions/checkout + actions/setup-python
│                                 (both by commit SHA); installs from
│                                 requirements.txt. No Dafny/Z3 *binary*
│                                 toolchain install — confirmed by
│                                 grepping tests/ and evidence/ for
│                                 subprocess calls that the suite only
│                                 reads committed verification captures,
│                                 never shells out to a live dafny/
│                                 crosshair run; z3-solver (Python
│                                 bindings, used by dafny_spec_lint.py's
│                                 own translator) is the only Z3-named
│                                 dependency this job needs
│   └── payloadguard.yml         PayloadGuard pre-merge CI scan (added
│                                 2026-07-10) — runs PayloadGuard-PLG/
│                                 payload-consequence-analyser (pinned to
│                                 a commit SHA, not a mutable tag) on
│                                 every PR into main; blocks merge on
│                                 exit code 1 (analysis error) or 2
│                                 (destructive verdict), not on 0 (which
│                                 covers safe/review/caution alike — the
│                                 four-way verdict distinction lives in
│                                 the tool's posted PR comment, not in
│                                 this exit code). A third-party gate,
│                                 not part of this repo's own evidence
│                                 pipeline — see KNOWN_LIMITATIONS.md's
│                                 "PayloadGuard CI gate" entry for the
│                                 caveats that come with trusting it
├── requirements.txt              Pinned exact versions (added
│                                 2026-07-10, for tests.yml): pytest,
│                                 jsonschema, PyYAML, z3-solver — the
│                                 same discipline this repo already
│                                 applies to GitHub Actions (pin exact,
│                                 don't float) extended to Python deps
├── dashboards/                  Static HTML dashboards (added
│                                 2026-07-10), read-only views over
│                                 committed evidence — not generated by
│                                 evidence/cli.py, hand-authored against
│                                 the real artifacts
│   ├── README.md                What each dashboard shows and how it
│                                 was built
│   ├── blueprint.html           Rendered view of this file
│   ├── status-findings.html     Gate-by-gate status + findings summary
│   └── phase-c-closure-review.html  Gate C6 closure-review walkthrough
├── evidence/                    Reusable core (domain-free by design)
│   ├── model.py                 Strength enum + CAVEAT map + dataclasses
│   │                            (VerificationResult, RequirementBinding);
│   │                            carries the Phase-B Dafny false-zero note
│   ├── reconcile.py             Normalized fact extraction + cross-artifact
│   │                            fact-equality gate (Turn 2.0 B2).
│   │                            VARIANT_ARTIFACTS includes
│   │                            traceability_matrix.formal.json as a
│   │                            full 5th member (2026-07-07, once
│   │                            variants A/B were extended to match) -
│   │                            the intent comparison is subset-based,
│   │                            not strict dict equality, since formal.json
│   │                            permanently lacks an opinion about
│   │                            REQ-DOSE-003 (out of dosage.dfy's scope
│   │                            by design). The temporary carve-out
│   │                            mechanism used while C was ahead of A/B
│   │                            (run_formal_check,
│   │                            KNOWN_FORMAL_INTENT_DIVERGENCE) is retired
│   ├── conflict.py              Gate 2 CONFLICT rule, both ratified
│   │                            sub-types: Type 1 (identity mismatch,
│   │                            top-down metadata vs. bottom-up
│   │                            evidence-store, now incl.
│   │                            dafny_binding_conflicts /
│   │                            _declared_dafny_bindings for dafny
│   │                            evidence across all three metadata
│   │                            shapes, 2026-07-07) and Type 2 (outcome
│   │                            mismatch across manifests); Tier 1.
│   │                            Extended 2026-07-11 (Phase 3 for the
│   │                            first Dafny-only examples):
│   │                            run_conflict_gate skips
│   │                            symbolic_binding_conflicts entirely when
│   │                            manifest is None (mirrors
│   │                            dafny_binding_conflicts' own dafny_store
│   │                            is None precedent exactly); a separate,
│   │                            real bug also fixed in the same pass -
│   │                            symbolic_binding_conflicts never skipped
│   │                            a .dfy-targeted implementation the way
│   │                            _declared_concrete_bindings already did,
│   │                            so a future mixed example (some
│   │                            requirements crosshair, others dafny)
│   │                            would have false-flagged a dafny
│   │                            requirement's implementation against the
│   │                            crosshair manifest's target file
│   ├── cli.py                   Gate 2 CLI (`python -m evidence.cli
│   │                            build`): vocabulary-agnostic wrapper
│   │                            around build_matrix() - takes metadata/
│   │                            manifest/concrete/schema as arguments,
│   │                            not hardcoded to examples/dosage_calculator.
│   │                            --dafny-captures (2026-07-07, required
│   │                            once metadata.a.yaml/b.yaml declared
│   │                            dafny evidence) points at a small JSON
│   │                            index of paths (not inlined content) for
│   │                            the real dafny_store the CLI assembles.
│   │                            --manifest/--concrete both made optional
│   │                            2026-07-11 (Phase 3 for renal_adjustment/
│   │                            drug_interaction_checker, both Dafny-only
│   │                            - no crosshair or concrete_test evidence
│   │                            exists for either): omitting --manifest
│   │                            passes None through, mirroring
│   │                            --dafny-captures' own established
│   │                            convention; omitting --concrete passes
│   │                            an empty-but-honest {"cases": []}, not
│   │                            None, since concrete_store["cases"] is
│   │                            dereferenced unconditionally by every
│   │                            binder. dosage_calculator's own real
│   │                            evidence unaffected either way -
│   │                            confirmed by regenerating its real
│   │                            artifacts before/after and diffing
│   │                            byte-for-byte
│   ├── schema/
│   │   ├── metadata.schema.json     Base metadata contract (draft 2020-12).
│   │   │                            id pattern widened 2026-07-11 to
│   │   │                            allow lowercase (REQ-RENAL-1a is the
│   │   │                            first lowercase-suffixed REQ-ID this
│   │   │                            schema was ever validated against -
│   │   │                            same class of gap as the
│   │   │                            dafny_nl_summary.py _REQ_ID_RE fix
│   │   │                            from 2026-07-08, now found in a
│   │   │                            second, independent place)
│   │   ├── metadata.schema.a.json   T4-A: evidence[] per requirement,
│   │   │                            + dafny method (2026-07-07, same fix
│   │   │                            as schema.c.json). toolchain.crosshair_bounds
│   │   │                            made optional 2026-07-11 (a metadata
│   │   │                            file with zero crosshair evidence
│   │   │                            anywhere has nothing to declare
│   │   │                            bounds for); id pattern widened,
│   │   │                            same as base schema above
│   │   ├── metadata.schema.b.json   T4-B: shadow ids + parent_requirement;
│   │   │                            shadow-id pattern extended to allow
│   │   │                            .formal-N (2026-07-07) alongside
│   │   │                            .concrete-N, for dafny shadow rows
│   │   │                            distinguished by a .dfy implementation.
│   │   │                            Same crosshair_bounds/id-pattern
│   │   │                            widening as schema.a.json, 2026-07-11
│   │   └── metadata.schema.c.json   T4-C: base shape, dual-matrix notes,
│   │                            + dafny evidence entries (spec_target,
│   │                            dafny_method required together), 2026-07-07.
│   │                            Same crosshair_bounds/id-pattern
│   │                            widening as schema.a.json, 2026-07-11
│   └── render/
│       ├── manual_matrix.py     Base binder/renderer (Phase A, hand-reviewed)
│       └── matrix_variants.py   build_matrix() - Gate 2's vocabulary-
│                                agnostic dispatch, the SOLE
│                                implementation across all four variants
│                                (all three generators + the CLI call
│                                it); folds in CONFLICT Type 1 as its
│                                first step, before assembling any
│                                record; derive_intent (R1);
│                                assert_no_realized_proven (R3, Phase C
│                                Gate C2 - supersedes R2: PROVEN permitted
│                                only for method=="dafny" records with
│                                verifier_completion_status=="completed";
│                                every other method stays permanently
│                                excluded). The original per-variant
│                                functions and the test that checked
│                                build_matrix() against them are deleted
│                                (Step 4) - git history holds them if ever
│                                needed again. dafny_record() (2026-07-07,
│                                Gate 2/C2-C4 wiring) is the mechanism
│                                that lets a real Dafny capture ever
│                                satisfy R3 - gates PROVEN on Z3
│                                precondition satisfiability AND the
│                                false-zero guard inside the binder
│                                itself, before assert_no_realized_proven
│                                ever re-checks it. build_matrix(),
│                                _bind_self_describing() (variant C),
│                                _bind_declared() (variant A), and
│                                _bind_shadow() (variant B) all gained an
│                                optional dafny_store parameter (default
│                                None = "don't bind dafny evidence at
│                                all", not "bind zero captures" -
│                                is-not-None, not truthiness). A/B's
│                                binders refuse outright if dafny evidence
│                                is declared with no dafny_store at all
│                                (unlike C's symbolic/concrete sub-views,
│                                they have no "legitimately excludes
│                                dafny" concept - a single artifact
│                                renders every evidence type together).
│                                _bind_shadow() distinguishes a dafny
│                                shadow row from a concrete one by
│                                checking whether the implementation file
│                                ends in .dfy - no new declared field.
│                                Extended 2026-07-11 (Phase 3 for the
│                                first Dafny-only worked examples,
│                                renal_adjustment/drug_interaction_checker):
│                                derive_bounds_block()/_header()/
│                                build_matrix() all use .get() instead of
│                                [...] for toolchain.crosshair_bounds, and
│                                derive_bounds_block() returns
│                                declared=effective=None (never fabricated
│                                zero/empty bounds) when either the
│                                metadata declares no crosshair_bounds or
│                                manifest is None - a metadata file with
│                                zero crosshair evidence anywhere has no
│                                "effective bounds" to report, and
│                                inventing one would falsely imply a
│                                search happened. _md_head() renders this
│                                as an explicit "N/A (no crosshair
│                                evidence in this metadata)" rather than a
│                                bare "None" that could misread as a data
│                                gap. dosage_calculator's own real
│                                crosshair-backed matrices are unaffected
│                                - confirmed by regenerating them and
│                                diffing byte-for-byte (timestamps aside)
│                                before and after this extension
│   ├── dafny_adapter.py         Gate C1 (+ C3 vector 3 hardening):
│                                 parse_dafny_capture() - the false-zero
│                                 guard, regex on the verifier's own
│                                 summary line, never a substring match or
│                                 bare exit_code. Also refuses on an
│                                 "out of resource"/"out of memory"/"timed
│                                 out" marker in the summary tail (real
│                                 finding, Gate C3) and on more than one
│                                 summary line in a capture. Called from
│                                 build_matrix() as of 2026-07-07 (Gate
│                                 2/C2-C4 wiring), via matrix_variants.py's
│                                 dafny_record() - the "c-formal" variant
│                                 key is what actually assembles a
│                                 dafny-method record into a live matrix
│                                 row today; every other variant_key is
│                                 unaffected
│   └── dafny_spec_lint.py       Gate C3 vectors 1-2: lints Dafny SOURCE
│                                 TEXT (not captured output, that's
│                                 dafny_adapter.py's job). vector 1 -
│                                 check_precondition_satisfiability():
│                                 extracts requires clauses, asks Z3 for
│                                 real satisfiability via a small scoped
│                                 expression translator (refuses on
│                                 quantifiers/unsupported syntax rather
│                                 than mistranslating) - extended
│                                 2026-07-10 (drug_interaction_checker's
│                                 Gate C3) to model simple, zero-argument-
│                                 constructor Dafny datatypes as a Z3
│                                 EnumSort via _parse_enum_datatypes, once
│                                 a real precondition (CheckInteraction's)
│                                 compared datatype-typed parameters
│                                 directly rather than merely declaring
│                                 them unreferenced. vector 2 -
│                                 scan_weak_postconditions(): heuristic,
│                                 best-effort flag of one-way ==> ensures
│                                 clauses without a matching <==>. Neither
│                                 is wired into the capture/generation
│                                 pipeline - standalone, tested modules
│   └── dafny_nl_summary.py      Gate C6: NL-dialogue confirmation.
│                                 summarize_method() mechanically extracts
│                                 each requires/ensures clause verbatim
│                                 plus any REQ-ID cited in a trailing
│                                 comment, alongside a best-effort
│                                 operator-substitution English gloss
│                                 (template, not comprehension - the raw
│                                 clause is always shown first). Reuses
│                                 dafny_spec_lint.py's Gate C3 parsing
│                                 surface. Extended 2026-07-10 (drug_
│                                 interaction_checker's Gate C6) to
│                                 genuinely support multi-line clauses -
│                                 CheckInteraction's one requires clause
│                                 was the first real one this repo built
│                                 against; a continuation line is any
│                                 non-blank, non-comment-only line that
│                                 doesn't itself open a new clause, so a
│                                 free-floating block comment between two
│                                 clauses (common in that spec) is never
│                                 misattributed as either one's citation.
│                                 The original single-line regex
│                                 (_CLAUSE_LINE_RE) is preserved and still
│                                 exported - dafny_mutate.py's
│                                 _locate_clause_sites imports it for a
│                                 different, byte-precise need this
│                                 extension didn't touch. Still
│                                 cross-checks its own line-based
│                                 extraction against dafny_spec_lint's
│                                 canonical extractor by CONTENT (not just
│                                 count - an earlier count-only draft
│                                 missed a real silently-truncated case)
│                                 and refuses (SystemExit) on mismatch -
│                                 a comment sitting on its own line INSIDE
│                                 a multi-line clause (as opposed to
│                                 between two clauses) still correctly
│                                 refuses, genuinely ambiguous. Not wired
│                                 into the capture/generation pipeline -
│                                 a process habit, not an automated gate
│   └── dafny_mutate.py          Gate C5: mutation testing (mutant
│                                 generation only - real re-verification
│                                 lives in the capture script below).
│                                 generate_ror/lor/aor/coi_mutants() +
│                                 generate_mutants(). Reuses
│                                 dafny_nl_summary's clause-line regex +
│                                 dafny_spec_lint's header-finder; a
│                                 local, span-preserving tokenizer extends
│                                 dafny_spec_lint's grammar with commas
│                                 (function-call clauses) and, since the
│                                 2026-07-07 extension, ASSIGN/SEMI (`:=`,
│                                 `;`, needed for function-body scanning).
│                                 Pass-1 static filter (skip mutants a
│                                 fixed relational-implication table
│                                 proves uninteresting) flips direction by
│                                 clause role - weakening is trivial for
│                                 ensures, strengthening is trivial for
│                                 requires - tested against a synthetic
│                                 spec independent of dosage.dfy. SOR/HOR
│                                 not implemented (no set/heap syntax in
│                                 this spec, confirmed by test).
│                                 Chain-direction-aware ROR
│                                 (_chain_group_ids/_chain_incompatible,
│                                 2026-07-07): restricts each chained-
│                                 comparison link's candidates to
│                                 direction-compatible operators per the
│                                 Dafny Reference Manual's own chaining
│                                 rule - eliminates stillborn mutants by
│                                 construction, ahead of MutDafny itself.
│                                 Function-body AOR (_find_function_body_span/
│                                 _locate_function_body_arithmetic_sites/
│                                 _ar_group_incompatible, 2026-07-07):
│                                 generate_aor_mutants(..., function_name=...)
│                                 scans a companion function's body (never
│                                 the target method's own trusted
│                                 implementation), restricted to MutDafny's
│                                 own +/-/* <-> /,% group rule so a
│                                 mutation never introduces `/` where the
│                                 original had none. LVR
│                                 (generate_lvr_mutants/_lvr_trivial/
│                                 _locate_clause_numeric_literal_sites/
│                                 _locate_function_body_numeric_literal_sites,
│                                 2026-07-07): mutates every numeric
│                                 literal (all 7 in this spec are exactly
│                                 0.0) to +/-0.01, the clinical-precision
│                                 floor; _lvr_trivial generalizes ROR's
│                                 requires/ensures polarity from operator-
│                                 to magnitude-implication for LT/LE/GT/
│                                 GE-adjacent literals; EQ/NE and
│                                 function-body literals unfiltered
│   └── citation_gate.py         Citation gate (2026-07-09): mechanical,
│                                 deterministic check that a claimed
│                                 quote appears in a source document's
│                                 text - normalized substring matching,
│                                 not an LLM judgment call, so an
│                                 automated citation drafter and its
│                                 checker can't share the same failure
│                                 mode. verify_citation()/
│                                 verify_citations() return a
│                                 CONFIRMED/NOT_FOUND verdict (asymmetric
│                                 by design, mirroring evidence/model.py's
│                                 Strength vocabulary: NOT_FOUND is never
│                                 presented as proof of fabrication,
│                                 since PDF extraction can be lossy).
│                                 Domain-free, not wired into the
│                                 generation pipeline - a standalone tool,
│                                 same scope discipline as the Gate C3/C5/
│                                 C6 modules. Regression-tested against
│                                 two real fabricated citations this
│                                 session caught by hand (a NICE NG203
│                                 misquote repeated across two supplied
│                                 documents, and a KDIGO recommendation
│                                 cited with the wrong number and wrong
│                                 content) - not synthetic fixtures
├── examples/dosage_calculator/  Worked example + all committed evidence
│   ├── dosage.py                Kernel under verification (contracts in
│   │                            docstring; negative rate = fault model)
│   ├── dosage_broken.py         Clamp removed — failure-path fixture source
│   ├── dosage_naive_widening.py Preserved review artifact (wrong branch
│   │                            order; documents why ordering is load-bearing)
│   ├── dosage.dfy               Gate C1: real Dafny spec of the dosage
│   │                            kernel's clamping shape; verifies clean
│   │                            (2 verified, 0 errors - an ExpectedDose
│   │                            function + the method, since Gate C4's
│   │                            fix pinned dose == ExpectedDose(...)).
│   │                            REQ-DOSE-003 excluded by name (Dafny
│   │                            real has no IEEE overflow concept -
│   │                            confirmed empirically). Gate C5
│   │                            (2026-07-07): REQ-GIP-1-8-1's ensures
│   │                            clause tightened >= -> > after mutation
│   │                            testing found the >= boundary wasn't
│   │                            independently load-bearing; still
│   │                            verifies clean (2 verified, 0 errors,
│   │                            unchanged)
│   ├── dosage_broken.dfy        Gate C1: Sample-B-equivalent broken variant
│   │                            (clamp removed); fails for real (0 verified,
│   │                            2 errors, exit code 4)
│   ├── dosage_underconstrained.dfy  Gate C4 honesty exhibit: Gate C1's
│   │                            ORIGINAL dosage.dfy postcondition,
│   │                            byte-for-byte, before the ExpectedDose
│   │                            fix - verifies clean on its own (the bug
│   │                            is a spec weakness, not a verification
│   │                            failure); same rationale as
│   │                            dosage_naive_widening.py
│   ├── dosage_stp_suite.dfy     Gate C4: 6 Spec-Testing Proof lemmas
│   │                            (IronSpec methodology) against the FIXED
│   │                            dosage.dfy (include'd) - ACCEPT + REJECT
│   │                            pairs for the normal/ceiling-clamped
│   │                            branches, ACCEPT-only for reverse-flow;
│   │                            all verify (10 verified, 0 errors)
│   ├── dosage_stp_suite_against_underconstrained.dfy  Gate C4: the same
│   │                            2 REJECT lemmas, include'ing the
│   │                            preserved weak spec instead - both
│   │                            genuinely FAIL (0 verified, 2 errors,
│   │                            exit 4), the mechanized "before" proof
│   ├── vacuous_precondition_probe.dfy  Gate C3 vector 1 fixture: a real,
│   │                            committed Dafny file with an
│   │                            unsatisfiable precondition
│   │                            (x > 0 && x < 0) - Dafny itself verifies
│   │                            it clean (1 verified, 0 errors),
│   │                            confirming the false-positive is real;
│   │                            dafny_spec_lint.py's Z3 check correctly
│   │                            reports unsat on the same method
│   ├── overflow_probe.py        Domain-free model-fidelity probe
│   ├── run_verify*.py           Capture runners (one per target + concrete)
│   ├── run_verify_dafny(_broken).py  Gate C1: capture runners mirroring
│   │                            run_verify.py exactly, targeting
│   │                            dosage.dfy / dosage_broken.dfy
│   ├── run_verify_dafny_resource_limited.py  Gate C3 vector 3: real
│   │                            capture of dosage.dfy under
│   │                            --resource-limit=1, producing the real
│   │                            "0 verified, 0 errors, 1 out of resource"
│   │                            finding (exit_code=4, already caught by
│   │                            the exit-code check; hardened anyway)
│   ├── run_verify_dafny_underconstrained.py  Gate C4: real capture of
│   │                            dosage_underconstrained.dfy standalone
│   ├── run_verify_dafny_stp_suite(_against_underconstrained).py  Gate
│   │                            C4: real captures of the two STP
│   │                            suites (fixed spec passes; weak spec
│   │                            genuinely fails)
│   ├── gate3_seed_patch_test.py Gate 3 investigation script (not part of
│   │                            the evidence-capture path): behaviorally
│   │                            tests a make_default_solver seed-override
│   │                            patch; result documented in
│   │                            KNOWN_LIMITATIONS.md, no capture changed
│   ├── nl_confirmation_dosage_dfy.md  Gate C6: the actual deliverable -
│   │                            a recorded human decision, not code. The
│   │                            generated plain-English summary for
│   │                            CalculateHourlyDose, plus Steven's
│   │                            sign-off ("it's good for the spec as
│   │                            is", 2026-07-07) and a next-phase item
│   │                            he explicitly scoped out as separate
│   │                            follow-up work
│   ├── run_mutation_suite.py    Gate C5: real re-verification harness.
│   │                            Generates every mutant via
│   │                            evidence/dafny_mutate.py, filters
│   │                            statically-trivial (pass 1) and vacuous-
│   │                            precondition (pass 2, reusing
│   │                            dafny_spec_lint.check_precondition_
│   │                            satisfiability) mutants, real-verifies
│   │                            every survivor against the installed
│   │                            Dafny binary (pass 3). Mutant .dfy files
│   │                            are NOT committed individually
│   │                            (mechanically derived); writes
│   │                            mutation_report.json/.md +
│   │                            run_manifest_mutation.json instead
│   ├── mutation_report.json/.md  Gate C5: real captured outcome of all
│   │                            56 mutants against dosage.dfy::
│   │                            CalculateHourlyDose (+ExpectedDose's
│   │                            function body), across all five
│   │                            operator classes (ROR/LOR/AOR/LVR/COI)
│   │                            after every same-day fix and extension -
│   │                            41 killed, 6 filtered_static, 4
│   │                            filtered_chain_incompatible, 1
│   │                            filtered_ar_group_incompatible, 4
│   │                            filtered_magnitude_implied, ZERO
│   │                            survived, ZERO unclassifiable. History:
│   │                            2 real survivors found and fixed same day
│   │                            (REQ-GIP-1-8-1's `>=` tightened to `>` on
│   │                            Steven's decision); 4 unclassifiable
│   │                            chain-direction parse errors then closed
│   │                            by teaching the generator Dafny's own
│   │                            chaining rule (now filtered_chain_
│   │                            incompatible, never reach Dafny at all);
│   │                            LVR extension then added and matched its
│   │                            own hand-derived prediction exactly (all
│   │                            10 real-verified candidates killed)
│   ├── raw_*/run_manifest_*     Verbatim captures + command/exit manifests
│   ├── concrete_results.json    Structured concrete evidence (T4-0)
│   ├── exhibit_pin_*.json       Version/platform pins + mechanism attribution
│   ├── metadata[.a|.b|.c].yaml  Authored metadata, base + variant shapes.
│   │                            All three of a/b/c now declare real
│   │                            dafny evidence (2026-07-07) for
│   │                            REQ-GIP-1-4-12/REQ-GIP-1-8-1 only -
│   │                            REQ-DOSE-003 permanently excluded, out
│   │                            of dosage.dfy's scope by design.
│   │                            metadata.b.yaml uses new .formal-N
│   │                            shadow rows (e.g.
│   │                            REQ-GIP-1-4-12.formal-1), same pattern
│   │                            as .concrete-N shadows
│   ├── dafny_captures_index.json  Small JSON index (paths, not inlined
│   │                            content) the CLI's --dafny-captures
│   │                            reads to assemble a real dafny_store
│   │                            (2026-07-07)
│   ├── generate_matrix*.py      Generators (validate → bind → check →
│   │                            render); each now calls
│   │                            evidence.render.matrix_variants.build_matrix()
│   │                            (2026-07-06 cutover). generate_matrix_c.py
│   │                            renders THREE artifacts as of 2026-07-07
│   │                            (symbolic/concrete/formal), assembling
│   │                            dafny_store from the real committed Gate
│   │                            C1 capture - no re-running evidence
│   ├── regenerate_all.py        Inner regeneration step: all variant
│   │                            generators + fact-equality gate +
│   │                            run_formal_check() (2026-07-07)
│   ├── generate_artifacts.py    End-to-end pipeline (Turn B4): schema
│   │                            validation -> capture integrity ->
│   │                            CONFLICT Type 1 (frozen base only - a/b/c
│   │                            checked inside build_matrix() now) ->
│   │                            CONFLICT Type 2 (whole-dataset, standalone)
│   │                            -> regenerate_all -> PROVEN sweep (now
│   │                            incl. traceability_matrix.formal.json) ->
│   │                            artifact_index.json
│   ├── artifact_index.json      SHA-256 provenance: inputs -> outputs,
│   │                            per-gate results, frozen evidence hashes.
│   │                            dosage.dfy/raw_dafny_output.txt/
│   │                            run_manifest_dafny.json added to INPUTS,
│   │                            traceability_matrix.formal.* to OUTPUTS
│   │                            (2026-07-07)
│   ├── traceability_matrix.*    Generated artifacts (never hand-typed).
│   │                            traceability_matrix.formal.json/.md
│   │                            (2026-07-07): variant C's third
│   │                            partition, real Dafny-sourced PROVEN
│   │                            evidence - this repository's first ever
│   │                            live rendered PROVEN row
│   ├── README.md                Audit-trail record (citations, caveats,
│   │                            amendments, exhibits, open questions)
│   └── RECONCILIATION.md        Cross-variant same-facts note + findings
├── examples/renal_adjustment/   Worked example 2 (Phase D - Phase 2 built
│   │                            AND confirmed, Phase 3 built 2026-07-11 -
│   │                            see Section 7 below and
│   │                            PHASE1_PLAN.md for current status; this
│   │                            entry is a structural listing, not a
│   │                            narrative - full detail lives in the
│   │                            files themselves)
│   ├── README.md                Audit-trail record (source citations,
│   │                            interpretive-call caveats, dated
│   │                            amendments) - mirrors dosage_calculator's
│   │                            README.md; fixed record, not living status
│   ├── PHASE1_PLAN.md           Living status document for this example -
│   │                            requirements table, closed/open scope
│   │                            decisions, kept current per-session
│   ├── GATE_1C_AUDIT.md         Internal consistency audit + two real
│   │                            findings (one resolved by redesign;
│   │                            Finding 1 closed for Cockcroft-Gault
│   │                            2026-07-09, then the CKD-EPI/eGFR half
│   │                            upgraded 2026-07-10 from an asserted
│   │                            claim to an empirically tested one — see
│   │                            its 2026-07-10 addendum and the pow-probe
│   │                            files below)
│   ├── gate_c1_sketch.md        Signature sketches for all 5 functions,
│   │                            each individually verified before
│   │                            composing into the committed spec
│   ├── gate_c4_stp_plan.md      STP predictions, hand-derived before
│   │                            building - both confirmed for real
│   ├── renal_adjustment.dfy     The committed spec: RoundHalfUp, GStage,
│   │                            SelectFormula, ComposedCeiling,
│   │                            AssessRenalFunction,
│   │                            CockcroftGaultCrClMlPerMin,
│   │                            AssessRenalFunctionFromInputs - verifies
│   │                            clean (7 verified, 0 errors)
│   ├── renal_adjustment_underconstrained.dfy  Gate C4 honesty exhibit:
│   │                            the pre-fix spec, preserved verbatim
│   ├── renal_adjustment_stp_suite(_against_underconstrained).dfy  Gate
│   │                            C4: 44 lemmas pass against the fix
│   │                            (52 verified, 0 errors, including the 7
│   │                            spec functions the suite includes); the
│   │                            same 4 REJECT lemmas genuinely fail
│   │                            against the preserved original
│   ├── nl_confirmation_renal_adjustment_dfy.md  Gate C6: generated
│   │                            summary + two amendments; sign-off
│   │                            CONFIRMED 2026-07-11 - Steven checked
│   │                            every claim against the raw KDIGO/MHRA
│   │                            sources directly, not a rubber stamp
│   │                            (one unverifiable supporting citation
│   │                            flagged, not silently absorbed - see
│   │                            its Decision section)
│   ├── run_verify_renal.py, run_verify_dafny_stp_suite(_against_underconstrained)_renal.py
│   │                            Capture runners, mirroring
│   │                            dosage_calculator's exact discipline
│   ├── run_mutation_suite_renal.py  Gate C5: 450 mutants across all 7
│   │                            functions - 51 survivors, all explained/
│   │                            categorized; 4 real engine gaps fixed,
│   │                            2 named and deliberately left unfixed
│   ├── mutation_report_renal.json/.md, run_manifest_mutation_renal.json
│   │                            Gate C5: real, committed outcome of
│   │                            every mutant
│   ├── dafny_pow_expressiveness_probe.dfy  Gate 1c Finding 1, tested not
│   │                            asserted (2026-07-10): a direct attempt
│   │                            to write CKD-EPI's fractional-exponent
│   │                            shape — refuses (`unresolved identifier:
│   │                            Pow`); Dafny has no real-exponentiation
│   │                            primitive at all
│   ├── dafny_pow_axiom_trap_probe.dfy  Companion probe: the obvious
│   │                            `{:axiom}` workaround verifies cleanly
│   │                            even for an absurd, wrong claim about
│   │                            Pow — an axiom wearing PROVEN's clothing,
│   │                            the exact failure mode Gate C2 refuses
│   ├── run_verify_pow_probes.py  Capture runner for both probes above
│   ├── raw_dafny_output*/run_manifest*  Verbatim captures + manifests
│   ├── dafny_captures_index.json  Phase 3 (built 2026-07-11): 7 entries,
│   │                            all seven functions, all sharing the
│   │                            one real capture (raw_dafny_output_renal.txt)
│   ├── metadata.a.yaml          Phase 3: 9 requirement rows - 4 with real
│   │                            dafny evidence (REQ-RENAL-1/1a/2/5,
│   │                            AssessRenalFunction dual-cited to both
│   │                            REQ-RENAL-1 and REQ-RENAL-2), 5 honest
│   │                            GAP rows (REQ-RENAL-3/4/6/7 intended
│   │                            PROVEN; REQ-RENAL-8 intended DECLARED -
│   │                            a permanent trust-boundary decision, not
│   │                            a future proof target)
│   └── traceability_matrix.a.json/.md  Phase 3: real, committed output of
│                                `evidence.cli build --variant a`, no
│                                --manifest/--concrete (no crosshair/
│                                concrete_test evidence exists for this
│                                Dafny-only example) - see
│                                tests/test_renal_adjustment_matrix.py
├── examples/drug_interaction_checker/  Worked example 3 (Phase E, all
│   │                            six Gates C1-C6 built or confirmed
│   │                            2026-07-10, Phase 3 built 2026-07-11 —
│   │                            see Section 8 below and
│   │                            PHASE1_PLAN.md for current status;
│   │                            structural listing only)
│   ├── PHASE1_PLAN.md           Living status document — Gate 1a/1c
│   │                            requirements table + resolved findings,
│   │                            Gate 1b sketch, Gate C1-C6 status
│   ├── GATE_1C_AUDIT.md         Internal consistency audit: three real
│   │                            findings (dropped risk-direction axis,
│   │                            CheckInteraction non-total over its own
│   │                            Agent type, two genuinely ambiguous
│   │                            source cells), all resolved by explicit
│   │                            decision — 2026-07-10 addendum re-derives
│   │                            every worked-example hand-trace against
│   │                            the redesigned sketch
│   ├── drug_interaction_checker.dfy  The committed spec: DOAC/Agent/
│   │                            RiskDirection/Outcome/InteractionResult/
│   │                            TreatmentIndication (added 2026-07-12,
│   │                            REQ-DDI-5, AFStrokePrevention |
│   │                            RecurrentVTEPrevention; extended
│   │                            2026-07-13 with a third constructor,
│   │                            OrthopaedicVTEProphylaxis, for REQ-DDI-6's
│   │                            own indication scoping - apixaban's own
│   │                            rows are unaffected, still guard on only
│   │                            the first two) datatypes, CheckInteraction
│   │                            (63 match arms, 15 v1 agents, 68 pinning
│   │                            ensures clauses — 60 original + 4 added
│   │                            2026-07-12 for the apixaban+inducer
│   │                            indication-dependent cells + 4 more added
│   │                            2026-07-13 pinning NotCovered for the
│   │                            orthopaedic indication on those same four
│   │                            cells, a second Qodo review finding fixed
│   │                            after PR #40 merged (see
│   │                            KNOWN_LIMITATIONS.md's "Gate C6 review
│   │                            (second, post-merge), 2026-07-13"); no
│   │                            requires clause as of 2026-07-12 — REQ-DDI-5
│   │                            made it provably unnecessary and removed it) —
│   │                            plus DoseReductionTargetMg (added
│   │                            2026-07-12, REQ-DDI-6: requires-gated
│   │                            bare-int, 5 pinned mg figures, apixaban
│   │                            excluded by construction; extended
│   │                            2026-07-13 with a treatmentIndication
│   │                            parameter and an indication guard on its
│   │                            Dabigatran+Verapamil cell, the four
│   │                            Edoxaban cells staying deliberately
│   │                            indication-free) — both verify
│   │                            clean (2 verified, 0 errors). No set/seq
│   │                            Dafny types needed (Gate 1b finding).
│   │                            The ensures clauses aren't decoration:
│   │                            Gate C4 found the original 3-clause
│   │                            version didn't pin almost anything (see
│   │                            _underconstrained.dfy below)
│   ├── drug_interaction_checker_underconstrained.dfy  Gate C4 honesty
│   │                            exhibit: the original 3-ensures-clause
│   │                            spec, preserved verbatim
│   ├── drug_interaction_checker_stp_suite(_against_underconstrained).dfy
│   │                            Gate C4: 11 ACCEPT/REJECT lemmas (7
│   │                            ACCEPT + 4 REJECT) pass against the fix
│   │                            - Dafny reports 22 verified, 0 errors
│   │                            (~2 verification tasks per lemma,
│   │                            confirmed empirically, not 1:1 - a real
│   │                            doc-accuracy bug this repo's own docs
│   │                            previously misread as "22 lemmas,"
│   │                            corrected 2026-07-10);
│   │                            3 ACCEPT lemmas genuinely fail against
│   │                            the preserved original (0 verified, 3
│   │                            errors) — a real captured failure, not
│   │                            smoothed over. Counts above are the
│   │                            original 2026-07-10 build; the real suite
│   │                            has grown since (6 new lemmas for
│   │                            REQ-DDI-5/6, 2026-07-12, 20 verified; 2
│   │                            more for the Dabigatran+Verapamil
│   │                            indication guard, Fix 2A/2B, 2026-07-13,
│   │                            23 verified; 2 more for CheckInteraction's
│   │                            own orthopaedic-indication NotCovered fix,
│   │                            2026-07-13, latest real count 25 verified,
│   │                            0 errors)
│   ├── run_verify_ddi.py, run_verify_dafny_stp_suite(_against_underconstrained)_ddi.py
│   │                            Capture runners, mirroring
│   │                            renal_adjustment's exact discipline
│   ├── raw_dafny_output_ddi*/run_manifest_dafny_ddi*  Verbatim captures
│   │                            + manifests
│   ├── run_mutation_suite_ddi.py  Gate C5: restructured 2026-07-12 to a
│   │                            multi-function loop (FUNCTIONS tuple,
│   │                            mirroring run_mutation_suite_renal.py's
│   │                            precedent) covering both CheckInteraction
│   │                            and DoseReductionTargetMg. Also names a
│   │                            real, deliberately-not-fixed engine
│   │                            boundary: generate_aor_mutants/
│   │                            generate_lvr_mutants' body-scanning mode
│   │                            refuses on DoseReductionTargetMg's body
│   │                            (a `//` comment on the wildcard match
│   │                            arm) — clause-level LVR alone already
│   │                            gave equivalent coverage, used instead of
│   │                            new shared-module engineering. A second,
│   │                            independent engine gap found 2026-07-13
│   │                            while adding DoseReductionTargetMg's
│   │                            treatmentIndication parameter:
│   │                            evidence/dafny_mutate.py's clause-site
│   │                            locator silently truncates a
│   │                            requires/ensures clause at its first
│   │                            physical line - a real coverage
│   │                            regression (1178 mutants dropped to
│   │                            1171 with entire disjuncts missing),
│   │                            not caught by Dafny or by pinned-count-
│   │                            only pytest assertions, diagnosed by
│   │                            reading original_clause text directly.
│   │                            Fixed by reformatting the two new
│   │                            clauses to single lines (matching
│   │                            renal_adjustment.dfy's own established
│   │                            precedent for this exact gap), not by
│   │                            extending the tool. A third, distinct
│   │                            extension 2026-07-13 (later, unrelated
│   │                            to the two above): a new _stp_verify
│   │                            helper re-verifies the committed
│   │                            drug_interaction_checker_stp_suite.dfy
│   │                            (reused verbatim, no new lemma authored)
│   │                            against every mutant that survives the
│   │                            bare-spec check, by redirecting the
│   │                            suite's own include at the mutant file.
│   │                            Hand-probed empirically before building
│   │                            (not assumed): catches the 6
│   │                            DoseReductionTargetMg requires-clause
│   │                            indication-guard survivors (same scope-
│   │                            leak class as the CheckInteraction fix
│   │                            above), does NOT catch the other 44 (both
│   │                            functions are plain, non-{:opaque}
│   │                            function - same-module STP lemmas verify
│   │                            via direct body unfolding, making mutated
│   │                            ensures-clause text provably irrelevant -
│   │                            a genuine Dafny semantics limit, not a
│   │                            shortfall). See KNOWN_LIMITATIONS.md's
│   │                            "Gate C5 extended: STP-suite escalation,
│   │                            2026-07-13" section for the full account.
│   ├── mutation_report_ddi.json/.md, run_manifest_mutation_ddi.json
│   │                            Gate C5: real captured outcome, latest
│   │                            re-run 2026-07-13 (STP-suite escalation
│   │                            above) — 1342 mutants: 744 killed, 522
│   │                            filtered_static, 44 survived, 26
│   │                            unclassifiable, 6 killed_via_stp_suite (a
│   │                            new, distinct outcome, kept separate from
│   │                            ordinary killed so the report stays
│   │                            honest about which check caught each
│   │                            one). CheckInteraction's 7 survivors (4
│   │                            REQ-DDI-5 LOR-vacuity + 3 pre-existing
│   │                            SSRIOrSNRI) are unaffected by this latest
│   │                            extension. DoseReductionTargetMg now
│   │                            contributes 37 survivors (ensures-clause
│   │                            guard-antecedent only - the 6
│   │                            requires-clause indication-guard mutants
│   │                            that used to survive are now
│   │                            killed_via_stp_suite) and all 26
│   │                            unclassifiable results (24 ROR
│   │                            datatype-ordering type errors + 2 LOR
│   │                            parser-ambiguity refusals). All 10 LVR
│   │                            mutants on the 5 pinned mg figures
│   │                            killed, none survived throughout every
│   │                            rerun. Prior run (1250 mutants, before
│   │                            this fix), preserved for context: 668
│   │                            killed, 482 filtered_static, 74 survived,
│   │                            26 unclassifiable.
│   └── nl_confirmation_drug_interaction_checker_dfy.md  Gate C6: the
│                                actual sign-off deliverable. Confirmed
│                                by Steven 2026-07-10 - closed, not
│                                rubber-stamped: the review itself
│                                caught and fixed a real doc-accuracy bug
│                                in this document's own text (an item
│                                mislabeling an indication-dependent
│                                precondition exclusion as apixaban's
│                                "source gap" - the .dfy spec and STP
│                                suite already had it right). Also
│                                documents a real tooling
│                                extension found along the way:
│                                CheckInteraction's one requires clause
│                                is the first genuinely multi-line clause
│                                this repo has pointed the NL summary
│                                generator at; extended
│                                dafny_nl_summary.py to support it rather
│                                than reformat the spec (renal_adjustment's
│                                equivalent gap was fixed the other way,
│                                since that spec had no other gate's
│                                captures riding on its exact formatting
│                                yet). Gained two dated addenda 2026-07-12
│                                for REQ-DDI-5/REQ-DDI-6 (built, not yet
│                                confirmed) and an "Addendum 3" 2026-07-13
│                                documenting a pre-sign-off review that
│                                found and resolved four real defects
│                                (two doc-content, one real spec-scope
│                                gap fixed on Steven's decision, one
│                                independent mutation-testing tooling
│                                gap) - the document is now ready for
│                                Steven's actual REQ-DDI-5/6 sign-off,
│                                which still hasn't happened
│   ├── dafny_captures_index.json  Phase 3 (built 2026-07-11; extended
│   │                            2026-07-12): 2 entries - CheckInteraction
│   │                            (reused by 5 requirement rows, REQ-DDI-
│   │                            1/2/3/4/5) and DoseReductionTargetMg
│   │                            (REQ-DDI-6) - the first time this repo's
│   │                            matrix binder has bound two different
│   │                            Dafny methods from the same spec file
│   │                            across two requirements in one metadata
│   │                            file; both keys point at the same
│   │                            physical capture files (one Dafny
│   │                            invocation verifies both functions)
│   ├── metadata.a.yaml          Phase 3: 6 requirement rows - REQ-DDI-
│   │                            1/2/3/4/5 all sharing the SAME one
│   │                            CheckInteraction evidence entry,
│   │                            REQ-DDI-6 binding DoseReductionTargetMg
│   │                            separately. No GAP rows remain as of
│   │                            2026-07-12 (REQ-DDI-5/6 built for real)
│   ├── traceability_matrix.a.json/.md  Phase 3: real, committed output
│   │                            of `evidence.cli build --variant a`, no
│   │                            --manifest/--concrete (no crosshair/
│   │                            concrete_test evidence exists for this
│   │                            Dafny-only example) - regenerated
│   │                            2026-07-12, all 6 rows PROVEN, see
│   │                            tests/test_drug_interaction_checker_matrix.py
│   └── README.md                Fixed audit-trail record (added
│                                2026-07-11, closing a named-but-open
│                                item from the Phase 3 scoping plan) -
│                                mirrors dosage_calculator's and
│                                renal_adjustment's structure, built from
│                                this example's own already-committed
│                                record, every quoted number cross-
│                                checked against its real capture file
├── sources/
│   ├── README.md                Standing rule for adding source documents
│   ├── gip-v1.0-hazard-analysis.md  GIP v1.0 archived verbatim
│   ├── req-gip-1-4-12-alarm-scope-decision.md  Focused citation extract,
│   │                            dosage_calculator's REQ-GIP-1-4-12
│   ├── KDIGO-2024-CKD-Guideline.pdf  Primary clinical source (Steven
│   │                            committed directly; no PDF tool was
│   │                            installed here, so a stdlib-only re+zlib
│   │                            extractor was written to read it)
│   ├── kdigo-2024-gfr-staging.md  Focused citation extract + a
│   │                            self-correction (2026-07-09 amendment:
│   │                            an earlier claim that round-half-up was
│   │                            "KDIGO's own convention" was wrong -
│   │                            KDIGO specifies no tie-break rule)
│   ├── mhra-renal-formula-selection-2019.md  Focused citation extract,
│   │                            the BMI-threshold formula-selection rule
│   ├── ckd-epi-2021-and-cockcroft-gault-verification.md  Independent
│   │                            verification of externally-supplied
│   │                            equation citations - confirms the real
│   │                            ones, corrects a fabricated NICE NG203
│   │                            citation
│   ├── sps-doac-interactions-2024.md  drug_interaction_checker's
│   │                            primary source (NHS SPS DOAC-interaction
│   │                            guidance) - raw-text extraction, not an
│   │                            AI-summarized pass, after the summary was
│   │                            found to flatten real per-DOAC/indication
│   │                            structure the raw fetch caught
│   ├── emc-smpc-apixaban-posology-2024.md  Added 2026-07-12: verifies
│   │                            an external REQ-DDI-5/6 research
│   │                            document's SmPC claims against both
│   │                            apixaban strengths (products 2878/4756);
│   │                            confirms the NVAF "2-of-3" dose-
│   │                            reduction rule is NVAF-only, and that
│   │                            interaction dosing is qualitative-only
│   │                            even on the legal SmPC. Not cited by any
│   │                            requirement yet
│   ├── mhra-dsu-doac-renal-dosing-2023.md  Added 2026-07-12: MHRA DSU
│   │                            vol 16 iss 10 renal table, confirms the
│   │                            same indication-branching pattern
│   │                            REQ-DDI-5 identified for interactions
│   │                            generalizes to renal dosing. Not cited
│   │                            by any requirement yet
│   └── fda-eliquis-label-interactions-2016.md  Added 2026-07-12:
│                                deliberate non-UK contrast source (every
│                                other apixaban/DOAC source here is
│                                UK-jurisdiction) - confirms the US label
│                                states a numeric 50% interaction dose
│                                reduction that no UK source states
└── tests/
    ├── conftest.py              Import-path plumbing
    ├── test_dosage_concrete.py  T4-0 CASES (single source of concrete truth)
    ├── test_overflow_probe.py   Deterministic IEEE overflow as executable fact
    ├── test_structural_proven_check.py  R3 structural rule over real
    │                            artifacts (formerly R2; corruption cases
    │                            unchanged by the Gate C2 migration)
    ├── test_fact_equality.py    B2 gate: facts/intent/bounds identical across
    │                            views; base = symbolic-subset legacy view
    ├── test_conflict_check.py  Gate 2 CONFLICT Types 1+2: three ratified
    │                            test cases over real data (all three
    │                            metadata shapes) + in-memory fixtures,
    │                            plus a fold-in proof driving build_matrix()
    ├── test_single_evidence_type.py  Gate 5: symbolic-only AND
    │                            concrete-only in-memory fixtures each
    │                            appear in exactly one variant-C artifact
    ├── test_cli.py              Gate 2 CLI: subprocess-driven, all FIVE
    │                            variants (a/b/c-symbolic/c-concrete/
    │                            c-formal, 2026-07-07) match committed
    │                            artifacts via --dafny-captures; Tier-1
    │                            error paths; stdout/file modes
    ├── test_dafny_adapter.py    Gate C1: real committed clean + broken
    │                            captures parse correctly; false-zero
    │                            substring-trap regression; belt-and-
    │                            suspenders check that assert_no_realized_proven
    │                            still blocks this adapter's PROVEN output
    ├── test_proven_exclusivity.py  Gate C2, ruling R3: positive (real
    │                            dafny PROVEN accepted) + explicit
    │                            negatives (crosshair/concrete_test/
    │                            missing-method/incomplete-status all
    │                            still refused, checked not assumed);
    │                            row-level shape; regression over all
    │                            four committed matrix artifacts
    ├── test_dafny_spec_lint.py  Gate C3 vectors 1-2: real vacuous-
    │                            precondition fixture -> unsat; real
    │                            dosage.dfy precondition -> sat (true
    │                            negative); quantifier/unknown-type
    │                            refusal; nat implicit >=0; weak-
    │                            postcondition heuristic flagged/not-
    │                            flagged cases
    ├── test_dafny_timeout_masking.py  Gate C3 vector 3: real resource-
    │                            limited capture refused (exit code);
    │                            synthetic out-of-resource/out-of-memory/
    │                            timed-out markers refused even with a
    │                            forced exit_code=0 (defense in depth);
    │                            ambiguous multi-summary-line capture
    │                            refused; real clean capture unregressed
    ├── test_dafny_stp_suite.py  Gate C4: real committed STP captures -
    │                            underconstrained spec still verifies
    │                            alone; STP suite passes against the
    │                            fix; same suite fails against the
    │                            preserved weak spec; regression on the
    │                            50.0-vs-500.0 wrong-value mistake caught
    │                            mid-build; direct source-text checks for
    │                            the pinning clause present/absent
    ├── test_dafny_nl_summary.py  Gate C6: real dosage.dfy parameters/
    │                            preconditions/postconditions rendered
    │                            correctly; each postcondition cites the
    │                            right requirement or explicitly "no
    │                            requirement cited" (load-bearing -
    │                            wrong citation is the exact defect class
    │                            this gate exists to catch); operator
    │                            gloss; multi-line-clause refusal
    │                            regression (the self-caught count-vs-
    │                            content bug); no-clauses case; output
    │                            determinism
    ├── test_dafny_mutate.py     Gate C5: pure generation/filter logic,
    │                            no Dafny invocations - real-spec ROR/
    │                            LOR/AOR/COI counts and filtering;
    │                            SOR/HOR non-applicability confirmed by
    │                            grepping dosage.dfy for set/heap syntax
    │                            (checked, not assumed); a byte-level
    │                            check that a mutation changes exactly
    │                            the targeted operator; the requires-vs-
    │                            ensures static-filter polarity flip
    │                            (tested on a synthetic spec, the least
    │                            obvious part of the design); tokenizer
    │                            function-call/unknown-syntax handling.
    │                            2026-07-07 extension (19 tests, up from
    │                            11): chain-direction filtering on the
    │                            real chained clause; direct unit tests of
    │                            _chain_incompatible/_ar_group_incompatible
    │                            against hand-derived cases; function-body
    │                            AOR generation and its division-free
    │                            restriction; ASSIGN/SEMI tokenizer
    │                            support; _locate_function_body_arithmetic_sites
    │                            finds exactly the one `*`. LVR extension
    │                            (25 tests, up from 19): literal-site
    │                            location with correct comparison-operand/
    │                            side tracking on the real spec; refusal
    │                            test for a hypothetical non-adjacent
    │                            literal; function-body literal-site
    │                            location; direct unit test of
    │                            _lvr_trivial against hand-derived cases;
    │                            a check that the generation-time half of
    │                            the prediction (14 raw, 4 filtered)
    │                            matches; byte-level check on the
    │                            targeted-literal splice
    ├── test_mutation_report.py  Gate C5: validates the COMMITTED real
    │                            capture (56 mutants; 41 killed, 6
    │                            filtered_static, 4
    │                            filtered_chain_incompatible, 1
    │                            filtered_ar_group_incompatible, 4
    │                            filtered_magnitude_implied, ZERO
    │                            survived, ZERO unclassifiable, as of the
    │                            LVR extension - 8 tests, up from 5)
    │                            rather than re-running Dafny 56 times per
    │                            test pass; the reverse-flow clause's
    │                            filtered (formerly-survivor) mutations,
    │                            the chain-incompatible (formerly-
    │                            unclassifiable) mutations, and the LVR
    │                            real-verification half of the prediction
    │                            (all 10 killed) are each pinned so a
    │                            regeneration can't silently reintroduce
    │                            a survivor or drift from the prediction
    ├── test_dafny_wiring.py     Gate 2/C2-C4 wiring, built for variant C
    │                            then extended to A/B (2026-07-07): real
    │                            formal artifact + real A/B artifacts all
    │                            carry the expected PROVEN rows and pass
    │                            assert_no_realized_proven for real;
    │                            dafny_record()'s two independent gates
    │                            (Z3, false-zero) each exercised;
    │                            dafny_binding_conflicts across all three
    │                            declaration shapes (A/C evidence list,
    │                            B's .dfy shadow rows); the full
    │                            fact-equality gate passes with intent
    │                            True everywhere; the subset-vs-strict-
    │                            equality fix is exercised directly; CLI
    │                            --dafny-captures round-trips for a/b and
    │                            the CLI's refusal without it is real, not
    │                            hypothetical; end-to-end
    │                            build_matrix("c-formal", ...) matches
    │                            the committed artifact
    ├── test_citation_gate.py    Citation gate (2026-07-09): regression
    │                            fixtures are the actual claims and
    │                            source text this session verified by
    │                            hand, not synthetic examples - a real
    │                            NICE NG203 misquote (repeated across two
    │                            separately-supplied documents) and a
    │                            real KDIGO misquote (wrong recommendation
    │                            number AND wrong content); a digit-
    │                            adjacency boundary-check regression
    │                            found by auditing the module against its
    │                            own motivating case ("1.1.2" was a false
    │                            substring match inside "1.1.2.1" before
    │                            the fix)
    └── test_docs_current_with_devlog.py  Mechanical staleness check
                                 (2026-07-10): HANDOFF.md/
                                 KNOWN_LIMITATIONS.md/SYSTEM_BLUEPRINT.md's
                                 own "Last updated" dates must not be
                                 older than DEVLOG.md's newest entry -
                                 built after catching a real, live
                                 instance of exactly this drift (two of
                                 the three still said 2026-07-09 while
                                 DEVLOG.md was already 2026-07-10)
```

## 3. Data flow (end to end)

```
                      AUTHORED                          CAPTURED (real runs)
        ┌─────────────────────────────┐     ┌────────────────────────────────────┐
        │ sources/*.md  (ground truth)│     │ run_verify(.broken)*.py            │
        │        │ cite               │     │   crosshair check <target>         │
        │        ▼                    │     │   --report_all                     │
        │ metadata[.a|.b|.c].yaml     │     │   --per_condition_timeout 30       │
        │  device / requirements /    │     │   -> raw output + manifest with    │
        │  (declared bounds = intent) │     │      effective_bounds (Turn 2.0);  │
        │                             │     │   exhibit runners keep the pinned  │
        │                             │     │   no-flags invocation (frozen)     │
        │  threat_model / toolchain   │     │ run_verify_concrete.py             │
        └──────────────┬──────────────┘     │   pytest tests/test_dosage_...     │
                       │                    │   -> raw_pytest_output_concrete    │
        jsonschema     │                    │   -> concrete_results.json         │
        (draft 2020-12)│                    └──────────────────┬─────────────────┘
                       ▼                                       │
              ┌────────────────────────────────────────────────▼───────┐
              │ generate_matrix*.py                                    │
              │  1 validate metadata against its schema (fail hard)    │
              │  2 build evidence records:                             │
              │      crosshair capture -> BOUNDED_CHECKED              │
              │      concrete case     -> EXAMPLE_CHECKED              │
              │      (binders refuse failed captures)                  │
              │  3 derive_intent(): requirement-scoped, computed ONCE; │
              │      views carry it read-only            [ruling R1]   │
              │  4 assert_no_realized_proven(): generation fails if    │
              │      any realized strength == PROVEN, UNLESS method   │
              │      == "dafny" AND verifier_completion_status ==     │
              │      "completed"                          [ruling R3] │
              │  5 render JSON + Markdown with per-strength caveats    │
              └────────────────────┬───────────────────────────────────┘
                                   ▼
        traceability_matrix.json/.md          (base, one record per row)
        traceability_matrix.a.json/.md        (variant A, evidence[] per req)
        traceability_matrix.b.json/.md        (variant B, shadow rows + parent)
        traceability_matrix.symbolic|concrete (variant C, method-partitioned)
```

**A second, real entry point exists (2026-07, Phase 3 for `renal_adjustment`/
`drug_interaction_checker`): `python -m evidence.cli build --variant a
--metadata ... --dafny-captures ...`, no per-example generator script and
no crosshair/concrete evidence at all.** Both new examples are Dafny-only
(no `.py` implementation, no crosshair run, no concrete test suite) - the
CLI's `--manifest`/`--concrete` flags are genuinely optional now (were
hard-required until this same change), and `derive_bounds_block()`/`_header()`
render `null`/"N/A (no crosshair evidence in this metadata)" for such a
metadata file rather than require a fabricated crosshair manifest just to
satisfy the pipeline. `dosage_calculator`'s own generator-script path
(`generate_matrix*.py`, diagrammed above) is completely unaffected -
confirmed by regenerating its real artifacts before and after this
extension and diffing byte-for-byte (timestamps aside).

## 4. Invariants

1. Strength originates in evidence records only; `intended_method` never
   influences a realized strength.
2. `intent_ok` is requirement-scoped, derived once at bind time, projected
   read-only into every view (R1). Variant B shadow rows project their
   parent's value.
3. `PROVEN` never appears as a realized strength in any generated record or
   rendered cell; enforced structurally at generation time and by pytest
   (R2). It may appear when quoting authored metadata in mismatch notes.
4. Gap = absence. No placeholder strings for missing evidence or fields.
5. Every committed capture carries verbatim output, exact command, exit
   code, and UTC timestamp. Unexpected outcomes are committed as-is (see the
   overflow probe: expected miss, actual confirmation — kept).
6. Committed matrices are generated, never edited by hand. Regeneration is
   deterministic given the same captures (timestamps aside).
7. Exhibit claims are version-contingent and scoped to their pins
   (crosshair-tool 0.0.107 / Python 3.11.15 / Linux x86_64).
8. All T4 variants must carry the same evidence facts; enforced by the
   fact-equality gate (`evidence/reconcile.py`) at generation time via
   `regenerate_all.py` and in the suite via `tests/test_fact_equality.py`.
   Shape divergence is design; fact divergence is a defect.
9. Review is two-tier (REVIEW_PROTOCOL.md): Tier 1 machine gates
   (fact-equality, structural PROVEN) stop defects — never resolved by
   editing generated artifacts; Tier 2 human review is per-reason over the
   structured findings. Declared bounds are intent; effective bounds in
   each manifest are what a run demonstrated (Turn 2.0 B1).

## 5. Evidence inventory (current)

| Capture | Target | Outcome | Strength encoded |
|---|---|---|---|
| Sample A (`run_manifest.json`) | `dosage.py` | exit 0, no counterexample | BOUNDED_CHECKED |
| Sample B (`run_manifest_broken.json`) | `dosage_broken.py` | exit 1, two counterexamples (over-max and negative-rate) | n/a (fixture proves capture works on failure) |
| Sample C (`run_manifest_naive_widening.json`) | `dosage_naive_widening.py` | exit 0 — real violation NOT found | honesty exhibit (class-2 incompleteness) |
| Overflow probe (`run_manifest_overflow_probe.json`) | `overflow_probe.py` | exit 1 — violation CONFIRMED | honesty exhibit (paired measurement) |
| Concrete (`concrete_results.json`) | `dosage.py`, 4 cases | pytest 4 passed, observed==expected | EXAMPLE_CHECKED |

Requirements bound (from GIP v1.0 unless DECLARED): REQ-GIP-1-4-12 (dose
limit), REQ-GIP-1-8-1 (reverse delivery, fault-modelled), REQ-DOSE-003
(finite in-range result, DECLARED). Intent status: 1-4-12 and 1-8-1 intend
PROVEN → realized weaker (intent_ok false, honest); DOSE-003 intent met.

**Phase 3 evidence, `renal_adjustment` and `drug_interaction_checker`
(2026-07, variant A only - see Section 8/9's own status blocks for the
full account):**

| Example | Requirements bound | Evidence | Realized GAP rows |
|---|---|---|---|
| `renal_adjustment` | REQ-RENAL-1/1a/2/5 (4 rows, 8 dafny evidence entries - `AssessRenalFunction` dual-cited to both REQ-RENAL-1 and REQ-RENAL-2, mirroring the `.dfy` file's own inline citation) | `dafny_captures_index.json`, 7 entries, all sharing one real capture (`raw_dafny_output_renal.txt`, `7 verified, 0 errors`) | REQ-RENAL-3/4/6/7 (intended PROVEN - named future formalization candidates); REQ-RENAL-8 (intended DECLARED - a permanent trust-boundary decision, not a proof target) |
| `drug_interaction_checker` | REQ-DDI-1/2/3/4/5 (5 rows, all sharing the SAME one dafny evidence entry - the first many-requirements-to-one-proof binding this repo's matrix binder has exercised) plus REQ-DDI-6 (its own DoseReductionTargetMg entry - the first two-different-methods-in-one-file binding) | `dafny_captures_index.json`, 2 entries (`raw_dafny_output_ddi.txt`, `2 verified, 0 errors`, both keys sharing the one capture) | None - all 6 rows PROVEN as of 2026-07-12 |

Both matrices pass `assert_no_realized_proven` (R3) and were built via
`evidence.cli` directly with `--manifest`/`--concrete` omitted entirely -
see `tests/test_renal_adjustment_matrix.py`/`test_drug_interaction_checker_matrix.py`.

## 6. Phase boundary

Phase A (complete): schema + model + hand-reviewed renderer, real captures,
worked example, T4 three-variant fork, closeout rulings R1–R3.
Phase B (COMPLETE — gate ledger fully closed): Gate 1 (end-to-end pipeline + provenance index)
complete with remediation applied. Gates 3 (bounds enforcement — decided
stay-CLI by real behavioral test), 4 (binding authorship — option 3
decided, mechanism specified), 5 (single-evidence-type fixture for
variant C — fully resolved, both symbolic-only and concrete-only now
constructible), and 6 (FRN — resolved) closed or decided. **Gate 2 is
now complete.** Its CONFLICT rule — both Type 1
(identity mismatch) and Type 2 (outcome mismatch) — is built
(`evidence/conflict.py`); Gate 4's cross-check mechanism is implemented
for all three metadata shapes, including variant C, whose declared-
binding asymmetry is closed. `build_matrix()` is the sole
implementation across all four variants (the original per-variant
functions and the equivalence test that checked build_matrix() against
them are deleted, per Steven's direction to build the CLI first); Type 1
is folded into it, running on every call. Type 2 stays a standalone
`generate_artifacts.py` stage by design (a whole-manifest-set check with
no per-variant home, like fact-equality). The CLI (`evidence/cli.py`,
`python -m evidence.cli build`) wraps `build_matrix()` for any metadata/
manifest/concrete-store path rather than the hardcoded worked-example
paths the generator scripts use. See `KNOWN_LIMITATIONS.md` for the live
gate ledger.

Phase C (COMPLETE — all six Gates C1–C6 built and signed off for
`dosage_calculator`, see Gate C6 below): restructured 2026-07-06 from a two-mechanism sketch
into a gate-sequenced plan (Gates C1–C6, build order specified) in
`payloadguard-evidence-roadmap-phaseB-to-C.md`. Gate C1's Dafny
toolchain blocker is resolved: Z3 4.16.0 is present and Dafny 4.11.0 was
obtained via `dotnet tool install --global dafny` (NuGet, reachable
through the environment's proxy; GitHub release downloads are genuinely
blocked by egress policy, confirmed via the proxy's own status endpoint,
not routed around). Verified against the real binary: the false-zero
note in `evidence/model.py` matches exactly ("Dafny program verifier
finished with N verified, 0 errors"); a failing run exits 4, not 1; the
vacuous-precondition risk Gate C3 names is real and reproducible; its
planned Z3-based mitigation is confirmed feasible. **Gate C1 itself is
now built (2026-07-07):** a real Dafny spec of the dosage kernel
(`dosage.dfy`, clean; `dosage_broken.dfy`, fails for real), a capture
runner pair, and `evidence/dafny_adapter.py::parse_dafny_capture` — the
false-zero guard, implemented and regression-tested
(`tests/test_dafny_adapter.py`, 6 tests). REQ-DOSE-003 is named as an
explicit scope exclusion from the Dafny spec (Dafny `real` has no IEEE
overflow concept). **Gate C2 (PROVEN's exclusivity migration) is also
now built (2026-07-07):** ruling R3 supersedes R2 —
`assert_no_realized_proven` permits PROVEN as a realized strength only
when a record's `method == "dafny"` and its `verifier_completion_status
== "completed"`; every other method, including a record with no method
at all, remains permanently excluded, checked explicitly in 8 new tests
(`tests/test_proven_exclusivity.py`) rather than assumed from the fact
that no binder produces one yet. Neither gate is wired into
`build_matrix()` or any generator — no binder yet assembles a
Dafny-sourced record into a live matrix row, so R3's positive branch is
proven correct in isolation, not yet exercised end-to-end. **Gate C3
(Dafny output-parsing hardening) is also now built for 3 of its 4 named
vectors (2026-07-07):** vector 1 (vacuous preconditions) —
`evidence/dafny_spec_lint.py::check_precondition_satisfiability` asks Z3
directly whether a method's `requires` clauses are jointly satisfiable,
proven against a real committed fixture
(`vacuous_precondition_probe.dfy`) that Dafny itself verifies clean
despite an unsatisfiable precondition. Vector 2 (weak postconditions) —
`scan_weak_postconditions`, an explicitly best-effort heuristic flagging
one-way `==>` in `ensures` clauses. Vector 3 (timeout/resource-limit
masking) — a real finding on the installed binary
(`dafny verify --resource-limit=1` on the real dosage.dfy spec reports
`0 verified, 0 errors, 1 out of resource`, `exit_code=4`, already caught
by Gate C1's exit-code check) led to hardening
`evidence/dafny_adapter.py`'s summary-line parser to also refuse
independently on out-of-resource/out-of-memory/timed-out markers and on
ambiguous multi-summary-line captures. Vector 4 (specification
stripping) remains BLOCKED, named — no new source material surfaced.
None of Gate C3's mechanisms are wired into the capture or generation
pipeline either — standalone, tested modules, same scope discipline as
Gates C1/C2.

**Gate C4 (Spec-Testing Proofs) is also now built (2026-07-07), and
found a real spec gap on its first application:** IronSpec's
methodology — prove a specific input/output pair is accepted or
rejected by the SPECIFICATION itself, independent of any implementation
— revealed that `dosage.dfy`'s original postcondition (bounds +
reverse-flow-zero only) never pinned `dose` to the actual clamped value:
a Dafny lemma trying to prove a wrong candidate value impossible
**failed to verify**, meaning a broken implementation that always
returned `0.0` would have satisfied the exact same spec Gate C1 verified
clean. Fixed for real: `dosage.dfy` gained a `function ExpectedDose(...)`
and a pinning `ensures dose == ExpectedDose(...)` clause, re-verified
clean (`2 verified, 0 errors` — the count changed from Gate C1's
original `1 verified`, and the real committed capture was re-run
honestly to match, not patched). The original weak spec is preserved
byte-for-byte as `dosage_underconstrained.dfy` (same rationale as
`dosage_naive_widening.py`); two STP suites (`dosage_stp_suite.dfy`,
`dosage_stp_suite_against_underconstrained.dfy`, each `include`-ing the
relevant spec rather than duplicating it) mechanically prove both
directions — six lemmas pass against the fix, the same two REJECT
lemmas genuinely fail against the preserved original. A self-caught
mistake during this build (an early wrong-value choice, `500.0`, was
already excluded by the weak spec's own bounds for an unrelated reason,
giving a false pass) was corrected to `50.0` before committing, with a
regression test guarding against reintroducing it. 6 new tests
(`tests/test_dafny_stp_suite.py`); full suite now 78 passed. Neither STP
suite is wired into `build_matrix()` or any generator — matches Gates
C1–C3's scope discipline; this gate authored one STP suite for the one
spec that exists, per its stated scope, not a generic STP-generation
tool.

**Gate C6 (NL-dialogue confirmation) is also now built and signed off
(2026-07-07).** Process-control gate aimed directly at recurrence of Gate
1's original finding — a spec/requirement-text mismatch caught only at
review time, not authoring time. `evidence/dafny_nl_summary.py::summarize_method`
mechanically extracts each requires/ensures clause verbatim plus any
`REQ-ID` cited in a trailing comment, alongside a best-effort operator-
substitution gloss labeled explicitly as a reading aid, not
comprehension — reusing Gate C3's parsing surface rather than
reimplementing Dafny parsing. Only single-line clauses are supported;
the function cross-checks its own extraction against `dafny_spec_lint`'s
canonical multi-line-capable extractor and refuses on any content
mismatch. A self-caught bug during this build: the first draft of that
check compared clause *counts*, not content, and missed a real case — a
synthetic multi-line clause produced the same count under both
extractors while the line-based scan had silently truncated it, dropping
the continuation. Fixed by comparing normalized clause text instead of
counts, before the test suite was even written. 7 new tests
(`tests/test_dafny_nl_summary.py`); full suite now 105 passed. The
gate's actual deliverable is not the code but the recorded decision it
feeds: `examples/dosage_calculator/nl_confirmation_dosage_dfy.md` records
Steven's sign-off on the generated summary for `CalculateHourlyDose`
("it's good for the spec as is") plus a next-phase item he explicitly
scoped out as separate follow-up work. Not wired into any generator —
matches the roadmap's own framing of this gate as a process habit, not
an automated check.

**Gate 2/C2-C4 wiring is also now built (2026-07-07) — the first real
Dafny-sourced PROVEN evidence ever to reach a live matrix row.**
Requested directly ("we need z3 integration and invocation in order to
reach PROVEN status, in concurrence with gate 5 extension"), with three
design decisions confirmed before building: scope is variant C only for
now (A/B explicitly deferred — "post hoc verify A and B after C is
proven"); the Z3 precondition-satisfiability gate lives inside the
binder itself (`dafny_record()`); metadata declares the dafny evidence
explicitly, cross-checked by a new CONFLICT Type 1 sub-check
(`dafny_binding_conflicts`). `traceability_matrix.formal.json` (variant
C's third partition, extending Gate 5's dual-matrix pattern to a triple)
binds real `dosage.dfy` evidence to REQ-GIP-1-4-12 and REQ-GIP-1-8-1 —
both flip `intent_ok` from False to True for the first time since Phase
A, gated by two independent, real checks before any record is even
constructed: Z3 precondition satisfiability (Gate C3) and
`parse_dafny_capture`'s false-zero guard (Gate C1). `assert_no_realized_proven`'s
ruling R3 (Gate C2) is exercised end to end for the first time, not just
in isolation — the structural PROVEN sweep in `generate_artifacts.py`
now explicitly checks the formal artifact too.

**Extended to variants A and B the same day** ("go ahead and extend
variant A and B now"): `metadata.a.yaml`/`metadata.b.yaml` now declare
the same real dafny evidence (A's `evidence` list; B's new `.formal-N`
shadow rows, distinguished from concrete shadows by a `.dfy`
implementation file, no new declared field needed); `_bind_declared`/
`_bind_shadow` gained the matching binder logic, refusing outright
(unlike C's symbolic/concrete sub-views) if dafny evidence is declared
with no `dafny_store` at all — A/B have no "legitimately excludes dafny"
concept. `dafny_binding_conflicts` was generalized (a new
`_declared_dafny_bindings` generator, mirroring how concrete evidence
already unifies A/C's list and B's shadow rows) to cover all three
declaration shapes, and `_declared_concrete_bindings` was fixed to skip
`.dfy`-suffixed shadow rows rather than mis-parsing them as concrete
test ids. `generate_matrix_c.py` now passes `dafny_store` to ALL THREE
of its `build_matrix()` calls, not just `"c-formal"` — necessary so
`c-symbolic`/`c-concrete`'s own `intent_ok` computation matches A/B/
formal (their rendered rows are unaffected either way).
`evidence/reconcile.py::VARIANT_ARTIFACTS` now includes
`traceability_matrix.formal.json` as a full fifth member, and the intent
comparison became subset-based (not strict dict equality) since
`formal.json` permanently lacks an opinion about REQ-DOSE-003 — the
temporary `run_formal_check`/`KNOWN_FORMAL_INTENT_DIVERGENCE` carve-out
is retired. `evidence/cli.py` gained `--dafny-captures` (a small JSON
index of *paths*, not inlined file content) — this turned out to be
necessary, not optional: once metadata.a.yaml/b.yaml declared dafny
evidence, the CLI genuinely could not build those variants without it.
Every variant artifact now reports `intent_ok: true` for both
REQ-GIP-1-4-12 and REQ-GIP-1-8-1; `run_gate()`'s facts count is 9, not
7. Full suite now 98 passed; full pipeline re-run end to end. Full
findings: `KNOWN_LIMITATIONS.md`.

**Gate C5 (mutation testing) is now built for v1 scope (2026-07-07),
following the same-day scoping session, found 2 real survivors, and both
were fixed the same day on Steven's decision.**
`evidence/dafny_mutate.py` generates ROR/LOR/AOR/COI mutants against
`dosage.dfy`'s requires/ensures clauses; `examples/dosage_calculator/run_mutation_suite.py`
real-verifies every one against the installed Dafny 4.11.0 binary,
mirroring `run_verify_dafny.py`'s capture discipline and reusing
`dafny_adapter`'s summary-line parsing rigor per mutant. The design's
least obvious point: a fixed relational-implication table filters out
mutants that are provably uninteresting before spending a real Dafny
invocation on them (pass 1), but the trivial DIRECTION flips by clause
role — weakening is trivial for `ensures` (whatever already satisfies
the original satisfies a logically weaker consequence too), while
*strengthening* is trivial for `requires` (the original proof still
applies under a narrower hypothesis) — verified against a synthetic spec
independent of `dosage.dfy`, not just the one real spec, since getting
this backwards would silently filter out the informative mutants
instead of the uninteresting ones. Real run: 39 mutants, 29 killed, 4
filtered as statically trivial, **2 survived** — `infusionRateMlPerHr >=
0.0 || dose == 0.0`'s `>=` weakened to `!=` or `>` both still verify,
because real multiplication by exactly `0.0` makes `dose == 0.0` already
hold at that boundary independent of the first disjunct's operator; a
real, understood looseness in REQ-GIP-1-8-1's postcondition, reported to
Steven for a decision rather than silently changed in a spec he already
signed off on in Gate C6. **Decision: "go ahead and tighten REQ-GIP-1-8-1
to `>`."** `dosage.dfy` changed, re-verified clean (`2 verified, 0 errors`,
unchanged), mutation suite re-run in full: **zero survivors remain** —
the two former survivor mutations are now recognized as statically
trivial by pass 1 *before* Dafny is even invoked (a proof of `x > 0`
universally implies both `x >= 0` and `x != 0`), itself a clean
mechanical confirmation the boundary is now tight.
`nl_confirmation_dosage_dfy.md` gained an amendment recording the
decision and the regenerated, re-confirmed summary. **4 unclassifiable,
unaffected by the fix** — mutating one side of
the chained `0.0 <= dose <= maxSafeDoseMgPerHr` to a descending operator
produces a genuine Dafny *parse* error (chained comparisons must stay
direction-consistent), a real gap in the mutation engine, not the spec,
confirmed by direct re-run and correctly refused rather than
misclassified. AOR/SOR/HOR explicitly out of v1 scope: SOR/HOR aren't
implemented at all (no set or heap syntax anywhere in `dosage.dfy`,
confirmed by test, not assumed); AOR is implemented and exercised but
returns `[]` against this spec (its one arithmetic operator lives in
`ExpectedDose`'s function body, outside clause-mutation scope) — deferred
per direct guidance ("be careful with Dafny... we can consider floating
points later, it's a known but solvable issue"; later refined to bound
any future real-valued mutant to the accuracy the dosage calculation
actually requires, not Dafny's unbounded exact-`real` precision). 16 new
tests (`tests/test_dafny_mutate.py`, pure generation logic;
`tests/test_mutation_report.py`, validates the committed real capture).
Mutant `.dfy` files are not committed individually (mechanically
derived); the real per-mutant outcome is `mutation_report.json`/`.md` +
`run_manifest_mutation.json`. Full suite was 121 passed at that point.

**Gate C5 was then extended the same day, from external research
findings (`gate_c5_mutation_testing_research_findings.md`), on direct
instruction ("build both").** One correction and two builds. Correction:
the "MutDafny/IronSpec-style" label was wrong — IronSpec's own mutation
technique is a directional, implication-lemma-based approach, distinct
from what this module actually does (brute verify/observe, matching
MutDafny) — fixed in the module docstring. **Build 1, chain-direction-
aware ROR:** confirmed against the Dafny Reference Manual (Sec
5.2.1–5.2.2) that chained comparisons must stay direction-consistent;
new helpers `_chain_group_ids`/`_chain_incompatible` restrict each chain
link's mutation candidates to direction-compatible operators, wired into
`generate_ror_mutants` only (no analogous rule for `&&`/`||`/arithmetic).
The 4 former `unclassifiable` mutants (real Dafny parse errors) are now
filtered *before* generation reaches verification — a new
`filtered_chain_incompatible` outcome, distinct from pass 1's
`filtered_static`. MutDafny itself does not do this — a genuine
improvement over the published state of the art. **Build 2,
function-body AOR:** `generate_aor_mutants` gained an optional
`function_name` parameter; new helpers `_find_function_body_span` (brace-
matched, mirroring `dafny_spec_lint`'s header-finder but returning the
body) and `_locate_function_body_arithmetic_sites` locate arithmetic
operators in `ExpectedDose`'s body (part of the formal spec, never
`CalculateHourlyDose`'s own trusted implementation, which is never
mutated). `_ar_group_incompatible` applies MutDafny's own restriction
directly: `+`/`-`/`*` freely interchange, `/` only with `%` (absent from
this spec) — a mutation can never introduce `/` where the original had
none, eliminating the division-by-zero false-kill risk by construction,
not post-hoc attribution. `_TOKEN_SPAN_RE` gained `ASSIGN`/`SEMI` token
kinds, needed for body statements (`var rawDose := ... ;`) but never
present in clauses. **Real re-run with both extensions active: 42
mutants — 31 killed, 6 filtered_static, 4 filtered_chain_incompatible, 1
filtered_ar_group_incompatible — zero survived, zero unclassifiable.**
The 2 new real-verified function-body mutants (`* -> +`, `* -> -`) are
both genuinely killed, confirming `*` is load-bearing. 10 more tests (19
total in `tests/test_dafny_mutate.py`, 7 in `tests/test_mutation_report.py`);
full suite was 131 passed at that point.

**Gate C5's LVR extension (Literal Value Replacement) was then scoped
and built the same day** ("scope out Gate C5's LVR extension", then
"go"). Tests whether a comparison's LITERAL CONSTANT is load-bearing,
not just its operator or the arithmetic combining it. Every numeric
literal in `dosage.dfy`'s requires/ensures clauses and `ExpectedDose`'s
function body was enumerated by running the real tokenizer: **all 7 are
exactly `0.0`** — no other constant exists anywhere in the spec. Value
strategy: exactly `original ± 0.01` per site — the clinical-precision
floor from the earlier research, finally applied (it was always scoped
to literal perturbation specifically, a class Gate C5 hadn't built).
`_lvr_trivial` generalizes ROR's requires/ensures polarity principle
from operator-implication to magnitude-implication for LT/LE/GT/GE-
adjacent literals; EQ/NE-adjacent and all function-body literals have no
such filter, sent straight to real verification. **Real run matched the
scoping session's hand-derived prediction exactly, site by site: 14
mutants, 4 filtered as `filtered_magnitude_implied`, 10 real-verified,
all 10 genuinely killed — zero survivors.** The one named, unresolved
tension from scoping (whether the clinical floor is the right test for
REQ-GIP-1-8-1's exact-zero safety requirement) didn't need resolving to
get a clean result here, but remains open as a judgment call. **Final
combined real run across all five operator classes: 56 mutants — 41
killed, 6 filtered_static, 4 filtered_chain_incompatible, 1
filtered_ar_group_incompatible, 4 filtered_magnitude_implied — zero
survived, zero unclassifiable.** 7 more tests (25 total in
`tests/test_dafny_mutate.py`, 8 in `tests/test_mutation_report.py`); full
suite now **138 passed**. Full findings: `KNOWN_LIMITATIONS.md`.

## 7. Phase D — second worked example (`examples/renal_adjustment/`)

Deliberately concise, per this file's 2026-07-09 addendum (Section
header, above): this is a status pointer, not a narrative. Full detail
lives in `examples/renal_adjustment/PHASE1_PLAN.md` (kept current
per-session), `GATE_1C_AUDIT.md`, `gate_c4_stp_plan.md`, `DEVLOG.md`
(full dated history), and `HANDOFF.md` (cold-start summary).

**Objective:** prove the Gate C1–C6 pipeline generalizes beyond
`dosage.dfy`'s arithmetic-clamping shape to lookup-table and
conditional-branching logic, using a UK-jurisdiction clinical example
(renal-function dose adjustment, sourced from MHRA/KDIGO/NICE).

**Status as of 2026-07-11 (last updated 2026-07-09, extended since — see
Gate C6 and Phase 3 entries below):**

- Gate 1 (clinical sourcing, spec skeleton, consistency audit): closed,
  under two named, deliberately provisional fallback assumptions — not
  permanent decisions.
- Gate C1 (spec + capture): built. `renal_adjustment.dfy` — seven
  functions (`RoundHalfUp`, `GStage`, `SelectFormula`, `ComposedCeiling`,
  `AssessRenalFunction`, `CockcroftGaultCrClMlPerMin`,
  `AssessRenalFunctionFromInputs`) — verifies clean (`7 verified, 0
  errors`).
- **Gate C6 (NL confirmation): built and confirmed, 2026-07-11.**
  Sign-off document reviewed by Steven against the raw KDIGO/MHRA
  sources directly — every checkable claim independently re-verified,
  not rubber-stamped. One unverifiable supporting citation flagged, not
  silently absorbed. See
  `nl_confirmation_renal_adjustment_dfy.md`'s Decision section.
- Gate C4 (STPs): built. Found and fixed two real under-constrained
  postconditions (`ComposedCeiling`, `AssessRenalFunction`) — confirmed
  failing against the preserved pre-fix spec, confirmed passing after a
  proper pinning-clause fix, both for real, not asserted. Extended
  2026-07-09 with real ACCEPT/REJECT lemma coverage for the two new
  functions below (`52 verified, 0 errors`, up from 44).
- **Gate C3 (spec lint): built 2026-07-09.** All seven functions pass
  vector 1 (satisfiable preconditions); five have expected vector 2
  warnings (one-way `==>` clauses used for exhaustive branch dispatch,
  all independently STP-covered by Gate C4). Found and fixed a real gap:
  the checker used to model every declared parameter regardless of use,
  refusing on `AssessRenalFunction`'s unused `Formula`-typed parameter —
  narrowed to only model referenced parameters.
- **Gate C5 (mutation testing): built 2026-07-09.** 450 mutants across
  all seven functions (no top-level `method` here, unlike `dosage.dfy` —
  each function is its own independent proof target): 250 killed, 137
  filtered pre-verification, 51 survived, 10 unclassifiable, 2 blocked.
  All 51 survivors explained and categorized into three named classes
  (structural blind spot of ROR/LVR against one-way `==>` antecedents;
  requires-clause weakenings not load-bearing for the specific ensures
  clauses proven; one coincidental numeric survivor on `RoundHalfUp`) —
  see `examples/renal_adjustment/README.md`'s Gate C5 amendment and
  `tests/test_renal_mutation_report.py`. Four real gaps in the shared
  `evidence/dafny_mutate.py` engine found and fixed (missing DOT/QUESTION
  tokenizer characters; LVR's int/real literal-type mismatch), two named
  and deliberately left unfixed (a `||`-chain ambiguity; two
  arithmetic-embedded LVR literals — real new engineering, and Gate C4's
  STPs already cover what they'd add).
- **All six Gate C1–C6 pipeline steps are now built and confirmed —
  this example's Phase 2 is done**, matching `drug_interaction_checker`'s
  status. What remains: the named, deliberately unbuilt requirements
  (`REQ-RENAL-3`, `REQ-RENAL-4`, `REQ-RENAL-6`, `REQ-RENAL-7`) and
  `REQ-RENAL-8`'s classification-flag provenance question (a Phase 3
  concern, not a Phase 2 blocker).
- **Phase 3 (evidence packaging) built, 2026-07-11.**
  `metadata.a.yaml`/`dafny_captures_index.json`/`traceability_matrix.a.json`/`.md`
  committed — 4 rows with real evidence, 5 honest GAP rows
  (`REQ-RENAL-3/4/6/7` intended `PROVEN`; `REQ-RENAL-8` intended
  `DECLARED`, a permanent trust-boundary decision, not a future proof
  target). See Section 5's Phase 3 evidence table above.

**Gate 1c Finding 1 closed for Cockcroft-Gault, 2026-07-09.** Source
re-verification first (direct re-fetch of the MHRA and NICE NG203 pages,
confirming both still resolve to the same content originally verified
2026-07-08 — no drift found) surfaced one real correction: the "MHRA's
1.23/1.04 constants" framing used in earlier notes overstated MHRA as
the source — MHRA's page states no formula or constant at all, only
that Cockcroft-Gault is the required method. `CockcroftGaultCrClMlPerMin`
therefore uses the unrounded exact conversion (88.4/72, sourced to the
1976 Cockcroft-Gault paper plus the standard clinical-chemistry µmol/L↔
mg/dL factor) rather than baking in a rounding decision the source never
made. **CKD-EPI eGFR remains caller-supplied — not a scope preference,
a forced consequence of Dafny/Z3 being unable to express real-valued
fractional exponents on a variable base.** `AssessRenalFunctionFromInputs`
orchestrates both branches end to end.

**That last sentence was only an asserted claim until 2026-07-10.** A
direct challenge before Gate C6 sign-off — can this repo actually
*claim* Dafny/Z3 can't express it, with real evidence in hand, not just
plausible domain reasoning — found the prior "confirmed" was circular
between this file and `sources/ckd-epi-2021-and-cockcroft-gault-verification.md`,
neither containing an actual test. Tested for the first time with two
committed probes (`dafny_pow_expressiveness_probe.dfy`,
`dafny_pow_axiom_trap_probe.dfy`, run via `run_verify_pow_probes.py`,
component map above): a direct attempt at CKD-EPI's `min(Scr/κ, 1)^α`
shape refuses outright (`Error: unresolved identifier: Pow` — Dafny has
no real-exponentiation primitive at all, for any exponent), and the
obvious `{:axiom}` workaround verifies cleanly (`2 verified, 0 errors`)
even for a lemma asserting `Pow` always returns `0.0` — an unproven
assumption wearing PROVEN's clothing. Both halves of Finding 1's closing
claim now rest on real, empirical evidence rather than reasoning alone.
See `GATE_1C_AUDIT.md`'s 2026-07-10 addendum for the full account.

**One decision remains explicitly left open**, per `PHASE1_PLAN.md`: who
sets `SelectFormula`'s caller-supplied classification flags, by what
process (reclassified as a Phase 3 concern, not a Phase 2 blocker).

**A citation-verification module, `evidence/citation_gate.py`, was also
added this phase** (component map, above) — built after two real
fabricated citations were caught by hand in externally-supplied
"research findings" documents, one of which repeated the same
fabrication after already being corrected once.

## 8. Phase E — third worked example (`examples/drug_interaction_checker/`)

Deliberately concise, matching Section 7's own precedent: a status
pointer, not a narrative. Full detail lives in
`examples/drug_interaction_checker/PHASE1_PLAN.md` (kept current
per-session), `GATE_1C_AUDIT.md`, `sources/sps-doac-interactions-2024.md`,
`DEVLOG.md`, and `HANDOFF.md`.

**Objective:** prove the Gate C1–C6 pipeline generalizes to
**set/list-membership logic** — checking whether a specific pairing
belongs to a known, bounded set and, if so, what outcome it maps to —
distinct from `dosage.dfy`'s arithmetic clamping and
`renal_adjustment.dfy`'s lookup-table/conditional-branching shape.
UK-jurisdiction (NHS Specialist Pharmacy Service DOAC-interaction
guidance), consistent with `renal_adjustment`'s sourcing convention.

**Status as of 2026-07-11 (last updated 2026-07-10, extended since — see
Gate C6 and Phase 3 entries below):**

- Gate 1a (clinical source audit): done. Single primary source (NHS SPS,
  chosen over BNF/MHRA DSU after direct comparison — bounded, versioned,
  publicly fetchable, states its own scope boundary explicitly).
- Gate 1c (internal consistency audit): performed, found three real
  findings (a dropped risk-direction axis, a `CheckInteraction` function
  non-total over its own declared `Agent` type, two genuinely ambiguous
  source cells) — all three resolved by explicit decision, none
  deferred. Every original worked-example hand-trace re-derived against
  the redesigned sketch to confirm the fix introduced no new
  inconsistency.
- **Gate C1 (spec + capture): built.** `drug_interaction_checker.dfy` —
  `DOAC`/`Agent`/`RiskDirection`/`Outcome`/`InteractionResult` datatypes,
  `CheckInteraction` (63 match arms across 15 v1 agents, a
  `requires` clause excluding the two agents' still-blocked apixaban
  cells) — verifies clean (`1 verified, 0 errors`). `evidence/dafny_adapter.py::parse_dafny_capture`
  parses the real capture unmodified — `Strength.PROVEN`,
  `verifier_completion_status == "completed"` — the third confirmation
  this parser generalizes across worked examples without change.
- **Gate C4 (STPs): also built, and found a real spec gap far larger
  than Gate C1's own first-draft finding.** Gate C1's original three
  `ensures` clauses turned out to be only a stopgap: a genuine
  IronSpec-style ACCEPT lemma restating just those three clauses as
  premises **failed to prove the correct value for any cell they didn't
  directly mention** — confirmed with a real committed failing capture
  (`drug_interaction_checker_stp_suite_against_underconstrained.dfy`,
  preserved against `drug_interaction_checker_underconstrained.dfy`: `0
  verified, 3 errors`), not just predicted. Unlike `renal_adjustment`'s
  own Gate C4 finding (postconditions *bounded* a result without
  *pinning* it), most cells here had no constraint at all, bound or pin
  — the match body's correctness was never actually a signature-level
  claim, only an implementation artifact. Fixed by restating all 63
  match arms as explicit pinning `ensures` clauses (verbose, but an
  honest reflection of a flat lookup table's actual shape, unlike
  `GStage`'s clean six-clause range partition) — re-verified clean (`1
  verified, 0 errors`, resource cost 358,399, still well under a
  second). The real STP suite (`drug_interaction_checker_stp_suite.dfy`)
  then covers the established worked examples as 7 ACCEPT lemmas plus 4
  REJECT lemmas (3 for the `Contraindicated` cells, the highest-stakes
  rows in the table, plus one more) — 11 lemmas total. Dafny's real
  capture reads `22 verified, 0 errors` (~2 verification tasks per
  lemma, not a 1:1 lemma count — confirmed empirically, corrected
  2026-07-10 after this and several other docs previously misread it as
  "22 lemmas"). Full account: `KNOWN_LIMITATIONS.md`'s "Phase E Gate C4"
  section.
- A real design finding from Gate 1b, worth restating here since it
  revises this repo's own earlier estimate: this example's v1 design
  needs **no** `set`/`seq` Dafny types at all (`DOAC`/`Agent` are closed
  enumerated `datatype`s, `CheckInteraction` a total pattern match,
  mirroring `renal_adjustment.dfy`'s own datatype precedent). `set`/`seq`/
  quantifier support would only become necessary for a later, distinct
  extension (checking a new drug against an open, caller-supplied
  medication list, not a single hardcoded pairwise lookup) — **still
  true**, but the "no new Gate C3 engineering needed" half of the
  original estimate turned out wrong once Gate C3 was actually built
  (below): comparing datatype VALUES in a precondition (not just
  declaring a datatype-typed parameter) needed real, if narrower-than-
  feared, new engineering.
- **Gate C3 (spec lint): built, and required extending the shared
  translator for real, not just applying it.** `CheckInteraction`'s
  precondition compares `doac`/`agent` directly against named datatype
  constructors — `evidence/dafny_spec_lint.py`'s vector-1 translator
  genuinely refused before this gate was built
  (`unsupported Dafny parameter type 'DOAC'`), a materially different
  gap from `renal_adjustment`'s own Gate C3 finding (a datatype
  parameter simply unreferenced by its precondition). Fixed by modeling
  every *simple* Dafny datatype (zero-argument constructors only —
  `DOAC`/`Agent`/`Outcome`/`RiskDirection` all qualify;
  `InteractionResult`, with fields, correctly does not) as a Z3
  `EnumSort`. A second, independent, more general bug was caught while
  building the test suite: Z3 registers `EnumSort` names globally per
  process, not per call, so two callers modeling a same-named type
  collide — fixed with a per-call disambiguating tag, a fix that
  protects every future caller of `build_symbol_table`, not just this
  example. Verified against the real spec: `sat` (real Z3 model:
  `agent = Naproxen, doac = Dabigatran`); vector 2 flags all 60 pinning
  `ensures` clauses, expected and independently backed by Gate C4's real
  proofs. Full account: `KNOWN_LIMITATIONS.md`'s "Phase E Gate C3"
  section.
- **Gate C2 (PROVEN exclusivity): confirmed, not newly built — the
  mechanism (`evidence/render/matrix_variants.py::dafny_record()`/
  `assert_no_realized_proven`, ruling R3) already existed, but had never
  been exercised against anything but `dosage_calculator`'s real
  captures since 2026-07-07.** `renal_adjustment` never reached this
  point (no `metadata.yaml` ever built for it). Run for real against
  this example's actual capture: produces a genuine PROVEN record,
  exercising Gate C3's Z3 check and Gate C1's false-zero guard for real
  against a spec neither was written for; `assert_no_realized_proven`
  accepts it cleanly. Two negative-case checks (tampered `method`,
  tampered `verifier_completion_status`) confirm R3 still independently
  refuses, not just trusting `dafny_record()`'s own diligence — tested
  against this example's real record shape, not only a synthetic one.
  No new gap, no shared-code change; the value is confirming
  generalization, not discovering a defect. Full account:
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C2" section.
- **Gate C5 (mutation testing): built.** 962 mutants (ROR/LOR/COI
  against `CheckInteraction`'s one `requires` clause and 60 `ensures`
  clauses; AOR and LVR both confirmed contributing zero — no arithmetic
  operator or numeric literal anywhere in this spec, checked not
  assumed). **Found and fixed a real crash, not a Dafny finding, mid-run:**
  a ROR mutant introducing `<=`/`>=` between two `DOAC` datatype operands
  crashed `evidence/dafny_spec_lint.py`'s Z3 translator with a raw Python
  `TypeError` — Z3's Python bindings don't overload ordering operators
  for `DatatypeRef`. Fixed in `_apply_cmp` (a `z3.is_arith` guard,
  refusing cleanly via `SystemExit` instead of crashing) — a shared-module
  fix, not specific to this example, shipped as its own PR. Final real
  run: **564 killed, 389 filtered_static, 7 survived, 2 unclassifiable.**
  The 2 unclassifiable are genuine Dafny type errors on `<=`/`>=` between
  `DOAC` values — a materially different failure mode from
  `renal_adjustment`'s own unclassifiable case (a parser ambiguity). The
  7 survivors fall into the same two structural categories
  `renal_adjustment`'s own Gate C5 already established (requires-clause
  weakenings not load-bearing for any proven `ensures` clause; a
  guard-style `==>` clause whose consequent is independently guaranteed
  by sibling clauses regardless of the mutated antecedent) — no new
  category of finding. An earlier draft prediction that `<`/`>` between
  datatype values would be "always killed" was wrong (the real run
  proved 3 such mutants survive) and was corrected in place, left
  visible rather than silently rewritten. Full account:
  `KNOWN_LIMITATIONS.md`'s "Phase E Gate C5" section.
- **Gate C6 (NL-dialogue confirmation): built.** `evidence/dafny_nl_summary.py::summarize_method`
  refused outright on first attempt — `CheckInteraction`'s one `requires`
  clause is the first genuinely multi-line clause this repo has pointed
  the summary generator at (every clause in `dosage.dfy`/
  `renal_adjustment.dfy` happened to be one line). Unlike
  `renal_adjustment`'s equivalent gap (fixed by reformatting two
  `ensures` clauses to single-line, since that spec had no other gate's
  captures riding on its exact formatting at the time), this spec
  already had committed Gate C1/C4/C5 captures bound to its current
  formatting, so the tool was genuinely extended instead — a
  deliberately different call, made for a concrete reason, not
  inconsistency. `_extract_annotated_clauses` now accumulates a clause
  across multiple physical lines, ending accumulation at a blank line, a
  standalone comment line, or the next clause keyword, so a
  free-floating block comment between two clauses (this spec has
  several) is never misattributed as either one's citation. The original
  single-line regex is preserved unchanged for `dafny_mutate.py`'s
  different, byte-precise use of it. Verified end-to-end: all 60
  `ensures` clauses and the one multi-line `requires` clause reconstruct
  correctly. Presented for sign-off in
  `nl_confirmation_drug_interaction_checker_dfy.md` — **confirmed by
  Steven, against the raw source directly, not a rubber stamp**: the
  review caught and fixed a real doc-accuracy bug in the sign-off
  document's own text (item 1 mislabeled the precondition's exclusion as
  apixaban's "source gap"; it's actually indication-dependent per the
  source, confirmed verbatim — the precondition itself was always
  correct). 3 new/changed tests, 190 total
  (up from 188). Full account: `KNOWN_LIMITATIONS.md`'s "Phase E Gate
  C6 sign-off" section. **Gate C6 is closed for this example.**
- Two items explicitly named, not built: `REQ-DDI-5` (an
  indication-dependent third axis for two agents' apixaban cells) and
  `REQ-DDI-6` (proving the specific numeric dose-reduction targets,
  staged as v2 per direct instruction — "both but in order of
  difficulty").
- **Phase 3 (evidence packaging) built, 2026-07-11**, once all six
  Gates C1–C6 above were built and confirmed.
  `metadata.a.yaml`/`dafny_captures_index.json`/`traceability_matrix.a.json`/`.md`
  committed — REQ-DDI-1/2/3/4 (4 rows) all sharing the SAME one dafny
  evidence entry, the first many-requirements-to-one-proof binding this
  repo's matrix binder has exercised; REQ-DDI-5/6 render as honest GAP
  rows (intended `PROVEN`, staged v2 — the two items named directly
  above). See Section 5's Phase 3 evidence table above.
