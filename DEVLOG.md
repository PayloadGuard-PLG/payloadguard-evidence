# DEVLOG — payloadguard-evidence

Append-only session log. Every session adds one dated entry (UTC), newest
first, citing commit SHAs. Timestamps below are taken from the git history
and run manifests, not reconstructed from memory.

---

## 2026-07-06 — Gate 3 closed by real test; Gate 6 (FRN) resolved; Gate 4 decision recorded; roadmap v2

Verification-first session, per the standing discipline: claims were
checked against actual repo/tool state before being written down,
including claims in the prompts supplied this session.

- **Pre-check on Defects 1/2 (mechanical-fixes prompt):** the prompt
  assumed these were possibly unpushed local commits. Checked for real:
  `5564fdf`/`1d9a260` exist on `main` locally and on `origin/main`
  (fetched and compared — identical, no divergence); DEVLOG already
  documented both under the 2026-07-05 "Gate 1 remediation" entry below.
  Rendered output verified directly (not just commit messages): all four
  variants show the scoped Notes fix and the REQ-GIP-1-4-12 kernel/system
  scope split correctly; suite 17 passed. No remediation needed — the
  prompt's premise didn't hold, and the mismatch was reported before
  proceeding rather than silently skipped or silently actioned.
- **Same-pattern discrepancy found in the roadmap-v2 prompt:** its "read
  first" section claimed FRN was "now closed." It was not — every
  in-repo reference (`KNOWN_LIMITATIONS.md`, `sources/README.md`,
  top-level `README.md`, `examples/dosage_calculator/README.md`) still
  read UNRESOLVED/BLOCKED. Flagged to Steven before proceeding; the
  roadmap v2 document (supplied afterward) carried the actual resolution
  to apply.
- **Gate 6 (FRN) — resolved and written up.** `FRN` = FDA Product Code
  for "Infusion Pump" (21 CFR 880.5725); within GIP's taxonomy, general-
  purpose volumetric infusion pumps (peristaltic, cassette-based),
  distinct from `All`. Source: NotebookLM extraction of the full source
  PDF, cross-checked against independent FDA-registry research. Caveat
  carried forward, not dropped: not yet independently re-verified against
  the raw Sec 2.4.1 text. Updated `sources/README.md` (open question →
  resolved question), `examples/dosage_calculator/README.md`,
  top-level `README.md`, `KNOWN_LIMITATIONS.md`.
- **Gate 3 — decided stay-CLI, by actually running the supplied
  verification script, not by trusting its writeup.** The roadmap's
  corrected seed-override technique (patch `make_default_solver`,
  hyphenated Z3 params) still had three bugs that only running it
  surfaced: (1) the roadmap's own claimed constructor,
  `AnalysisOptions(max_iterations=..., per_condition_timeout=...)`,
  raises `TypeError` on the installed 0.0.107 — `analyze_function` takes
  `AnalysisOptionSet`, not `AnalysisOptions`; (2) `crosshair.core` alone
  raises `CrossHairInternal("Opcode patches haven't been loaded yet.")`
  on `.analyze()` — must import from `crosshair.core_and_libs`; (3)
  `analyze_function` only returns parsed `Checkable`s, it doesn't run the
  solver — `.analyze()` must be called on each to get a real result. The
  uncorrected script "completed" in under a second and would have looked
  like a clean pass without ever invoking CrossHair's solver. After all
  three fixes, ran it for real, twice per target, seed 1 vs seed 2:
  `dosage.py::calculate_hourly_dose` gave byte-identical "Not confirmed"
  results both times; `dosage_broken.py::calculate_hourly_dose` (a
  stronger discriminator — it has real counterexamples) gave the exact
  same two counterexamples both times, matching the values already on
  file in `raw_crosshair_output_broken.txt`. No observed effect from the
  patch on either target tested. Decision: stay-CLI; `seed` documented as
  a tool-version limitation (tool-fixed at 42, hard-coded in
  `make_default_solver()`, not `StateSpace.__init__`, with hyphenated
  param names); `max_iterations` confirmed enforceable via
  `AnalysisOptionSet` independent of the seed question. Verification
  script committed at
  `examples/dosage_calculator/gate3_seed_patch_test.py`; nothing
  re-captured, Gate 1's committed evidence is untouched. Also closed as a
  non-issue: installed/pinned crosshair-tool is 0.0.107 in this
  environment (`pip show` confirmed), consistent with the toolchain pin;
  GitHub's latest *tag* trailing at 0.0.106 doesn't indicate a real
  discrepancy here.
- **Gate 4 — decision recorded (not built).** Option 3 (both binding-
  authorship models, cross-checked, Tier-1 failure on disagreement) is
  now the decision on record, with the dual-authorship top-down/bottom-up
  code-location-match mechanism specified. Building it is Gate 2's binder
  work.
- **Gate 2 — still blocked**, now with two candidate test cases on file
  for whatever CONFLICT definition eventually lands: a positive case
  (top-down/bottom-up binding disagreement under Gate 4's mechanism) and
  a negative case (REQ-GIP-1-4-12's kernel/system scope split, which is a
  documented absence, not a conflict).
- `payloadguard-evidence-roadmap-phaseB-to-C.md` replaced in place with
  the roadmap-v2 content (supersedes the 2026-07-05 morning version per
  its own text) plus the real Gate 3 result folded in.
- Suite: 17 passed (unchanged — no capture or generator touched this
  session).

## 2026-07-05 — Gate 1 remediation (two items from Steven's review)

Gate 1 review verdict received: fact-equality doing its job; two issues to
fix before Gate 2. Both fixed in generators/metadata — no generated file
hand-edited.

- **Item 2 (Tier 1 renderer defect):** variant C's method-filtered views
  were leaking the cross-evidence-type intent summary into their Notes,
  and the aggregate Notes section emitted once per table row (duplicate
  REQ-GIP-1-8-1 line in concrete.md). Fixed: `_view_notes()` scopes note
  text to the rendering view's evidence contribution (the intent_ok VALUE
  stays requirement-scoped per R1, never re-derived); `_md_notes()`
  de-duplicates by (requirement, note).
- **Item 1 (REQ-GIP-1-4-12 alarm scope):** evidence didn't match the
  requirement text — clamped output was verified, alarm emission never
  was. Steven's design decision (sources/req-gip-1-4-12-alarm-scope-
  decision.md, IEC 60601-1-8 ALARM CONDITION vs ALARM SIGNAL) implemented:
  metadata.yaml gains kernel_scope/system_scope on 1-4-12 (all four
  schemas extended with the optional fields; positive+negative
  revalidated for every variant); concrete test renamed
  over_max_clamps_exactly_to_max → kernel_detects_bolus_limit_exceeded
  and re-captured for real (4 passed); variant metadata re-derived;
  evidence rows for 1-4-12 reference the kernel_scope text; system_scope
  renders as an explicit named GAP in every view. GAPs are excluded from
  normalize_facts by rule (absence is not a fact) — fact-equality gate
  still PASS at 7 facts. Suite: 17 passed.
- Gates 2/3/4/6 untouched per the remediation prompt's "still open" list;
  the CONFLICT-vs-scope-GAP test question recorded in KNOWN_LIMITATIONS.

## 2026-07-05 — Deferred-gate work while Gate 1 output under review

Performed the deferrable gate processes without touching Gate 1's ground
truth (no re-capture, no artifact regeneration).

- **Gate 2 / CONFLICT rule — BLOCKED, named.** Retrieved
  PayloadGuard-Evidence-Blueprint-1 from Drive in full (committed to the
  repo with provenance header; Drive doc remains authoritative). The term
  CONFLICT appears nowhere in it (0 occurrences) nor in
  SYSTEM_BLUEPRINT.md (single to-do mention, no definition). Per roadmap:
  stopped, named, asking Steven. Closest neighbouring concept: Blueprint
  Phase 2 acceptance (b), intent mismatch "raises a GAP/flag".
- **Gate 3 — investigated, decision pending.** Verified against the
  installed package: per_condition_timeout CLI-enforceable (done in B1);
  max_iterations exposed by the Python API only
  (AnalysisOptions.max_iterations, default sys.maxsize); seed hard-coded
  to 42 in crosshair/statespace.py:750-751 — declared seed:1 is
  unenforceable at any interface on 0.0.107. Two wiring options recorded
  in KNOWN_LIMITATIONS; either requires re-capture, so the decision waits
  until Gate 1 review completes.
- **Gate 4 — options prepared** (metadata-authored / store-carried /
  both-with-cross-check, recommendation noted) for slotting into the Gate
  2 binder design. Design input recorded: the current C builder binds
  symbolic evidence to every requirement without verifying implementation
  against the capture target; the Gate 2 binder must bind by verified
  code-location match.
- **Gate 5 — resolved for the constructible half.**
  tests/test_single_evidence_type.py: in-memory symbolic-only fixture
  through the real variant C builder — appears in exactly one artifact;
  schema-c-validated; committed data untouched. Concrete-only fixture
  impossible pre-Gate-2 (see Gate 4 input). Suite: 17 passed.
- **Gate 6 — remains blocked** on a one-line FRN definition from Steven.

## 2026-07-05 (Turn B4) — Phase B Gate 1: end-to-end artifact generation

Phase B v3 prompt + roadmap received; roadmap committed verbatim as
`payloadguard-evidence-roadmap-phaseB-to-C.md`. Note for the record: the
prompt's B4/B5 spec bodies arrived as placeholders; B4 scope taken from
roadmap Gate 1 (minimal pipeline, four real variant artifacts as ground
truth, Steven review before Gate 2).

- `generate_artifacts.py`: five-stage end-to-end pipeline — (1) all four
  metadata files schema-validated, (2) capture integrity verified without
  re-running evidence (Sample A exit 0 + effective_bounds present, Sample
  B exit 1, concrete store clean), (3) regeneration + fact-equality gate
  via the B2 path (PASS, 7 facts), (4) structural PROVEN sweep over four
  variants plus frozen base, (5) `artifact_index.json` — SHA-256
  provenance binding 12 inputs to 8 outputs plus 10 frozen evidence files,
  with per-gate results. Any stage failure is a Tier 1 stop.
- `KNOWN_LIMITATIONS.md` created as the standing gate ledger: Gate 3
  (CrossHair API bounds) deferred — not hit in B4; Gate 4 (binding
  authorship) deferred to Gate 2's binder design; Gate 5 (single-evidence
  fixture) deferred as a Gate 2 test prerequisite; Gate 6 (FRN) blocked on
  a one-line definition from Steven; Phase C `verifier_completion_status`
  schema consideration noted for the Gate 2 binder.
- Suite: 15 passed. Gate 2 (vocabulary-agnostic binder + CONFLICT rule)
  not started — gated on Steven's review of the four real artifacts.

## 2026-07-05 09:46 UTC — Turn 2.0: bounds reconciliation, fact-equality gate, review protocol (678a3a5, 6347645, B3: this commit)

Three ratified rulings from the Q1–Q3 design review, executed in strict
order B1 → B2 → B3. Kernels untouched; exhibits frozen.

- **B1 (678a3a5, bounds):** `run_verify.py`/`run_verify_broken.py` now pass
  `--per_condition_timeout 30` (the one declared bound the 0.0.107 CLI can
  enforce) and record `effective_bounds` in the manifest — the single
  source of truth for what a run demonstrated. Samples A and B re-captured
  for real; raw outputs byte-identical to the previous captures. Generation
  gained a model-level `{declared, effective, enforcement_note}` bounds
  block, derived once (`derive_bounds_block`) and verified uniform across
  all four views. Exhibit captures/pins/runners byte-unchanged (frozen
  measurements). Ratified: metadata's declared triple kept — declared
  bounds are the bounds analogue of `intended_method`.
- **B2 (6347645, gate):** same-facts check mechanized.
  `evidence/reconcile.py` normalizes any matrix shape to fact tuples;
  `run_gate` asserts A/B/C fact equality, base-matrix = symbolic subset
  (frozen legacy view, ratified), intent uniformity, bounds-block
  uniformity. Enforced at generation time by `regenerate_all.py` (the
  sanctioned entrypoint; ratified that individual generators stay
  unchanged — a cross-artifact property cannot live inside one generator)
  and in the suite by `tests/test_fact_equality.py` (corruption cases
  mutate tmp copies only). Gate on real artifacts: PASS, 7 facts. Suite:
  15 passed.
- **B3 (this commit, protocol):** `REVIEW_PROTOCOL.md` codifies two-tier
  review: Tier 1 machine gates (fact-equality + structural PROVEN) stop
  defects and are never resolved by editing generated artifacts; Tier 2
  human review is per-reason over six structured finding classes.
  "Review only on validator disagreement" documented as void by
  construction. README pointer, BLUEPRINT invariants 8–9 and timestamp
  updated.

## 2026-07-04 18:52 UTC — Documentation pass: README, SYSTEM_BLUEPRINT, DEVLOG

- Root `README.md` populated (was an empty scaffold placeholder): purpose,
  non-goals, claims-discipline table including EXAMPLE_CHECKED, end-to-end
  flow, worked-example walkthrough, honesty exhibits, run instructions,
  known limitations.
- `SYSTEM_BLUEPRINT.md` created: component map, data-flow diagram,
  invariants (R1/R2 encoded), evidence inventory, Phase A/B boundary.
- `DEVLOG.md` created with the full dated history of the repository to date.
- No code, schema, kernel, or evidence changes in this session.

## 2026-07-04 16:40–16:42 UTC — Phase A closeout rulings (f5977d0, 96eaeee, d23689a)

Implemented the three rulings ratified after the Phase A audit. Kernels
untouched; one commit per ruling.

- **R1 (f5977d0):** `intent_ok` made requirement-scoped and derived exactly
  once at bind time (`derive_intent` in `matrix_variants.py`); all variant
  views carry it read-only, variant C assembles the full two-method model
  before filtering, variant B shadows project the parent value. Verified
  uniform across A / B parents / both C views (1-4-12 false, 1-8-1 false,
  DOSE-003 true). Same-facts check re-run: 7 facts, set-equal.
  RECONCILIATION asymmetry (1) closed; asymmetry (2) annotated deferred to
  Phase B.
- **R2 (96eaeee):** PROVEN rule made structural, not textual. Inline
  `intended PROVEN, realized …` notes restored (quoting authored metadata is
  fidelity). `assert_no_realized_proven()` fails generation if any realized
  strength equals PROVEN; committed as pytest over the four real artifacts
  plus in-memory corruption cases. Grep audit retired. Base Option A
  matrices untouched. Suite: 11 passed.
- **R3 (d23689a):** class-(2) incompleteness reframed: the IEEE-faithful
  channel exists but is unreliably sampled and sharply complexity-dependent
  (confirmed on the one-operation probe, silent on the four-parameter kernel
  under identical invocation; recorded bounds do not disclose the regime).
  Both exhibit pins' `mechanism_attribution` updated to match the README —
  verified identical modulo self-reference. Old "invisible" phrasing gone.

## 2026-07-04 16:15–16:26 UTC — Phase A completion T1–T4-C (0894da2…274115d)

- **T1 (0894da2):** BOUNDED_CHECKED incompleteness split into search-budget
  vs model-fidelity classes; CrossHair changelog cited (v0.0.72 real-valued
  float modelling, v0.0.58 nan/±inf as arguments only).
- **T2 (82a18a0):** naive-widening exhibit pinned
  (`exhibit_pin_naive_widening.json`): crosshair-tool 0.0.107, Python
  3.11.15, platform, exact invocation, mechanism attribution,
  version-contingency note.
- **T3 (d66162f):** domain-free `overflow_probe.py`. Expected a miss;
  CrossHair **confirmed** the violation (`double_it(8.98846567431158e+307)`
  → inf, exit 1). Recorded as-is, not re-rolled — paired with Sample C it
  measures the FP channel's width. Deterministic pytest companion added.
- **T4-0 (88bf755):** concrete evidence foundation — four requirement-mapped
  cases in `tests/test_dosage_concrete.py` (single CASES source), captured
  verbatim (pytest 4 passed) plus structured `concrete_results.json`.
  `Strength.EXAMPLE_CHECKED` added to the model.
- **T4-A/B/C (c2768da, 5745e0b, 274115d):** three parallel schema variants
  generated from identical evidence — A: evidence array per requirement
  (3 rows / 7 records); B: shadow pseudo-requirements with machine-enforced
  `parent_requirement` (7 rows); C: dual matrices partitioned by method
  (3 symbolic / 4 concrete rows), one filter-parametrised renderer.
  `RECONCILIATION.md`: programmatic same-facts confirmation (7 fact tuples)
  plus four recorded asymmetries. All schemas validated positive + negative.

## 2026-07-04 15:34 UTC — Option A amendment (b090d54)

Post-ship review found REQ-GIP-1-8-1's verification vacuous: the
`infusion_rate_ml_per_hr >= 0` precondition made the negative-dose clamp
dead code, so the postcondition's lower bound held by algebra. Applied
Option A: precondition widened to any finite rate (negative models the GIP
SR 1.8.1 single-fault reverse flow), directional postcondition added
(negative rate ⇒ return exactly 0.0), and the negative check reordered
before the finiteness check — a naive widening would have returned the
MAXIMUM dose on a −inf overflow. The naive variant and its real CrossHair
capture (exit 0 — the violation was NOT found) were committed deliberately
as the honesty exhibit. Sample B re-capture now shows a second, negative
counterexample, proving the widened domain is genuinely explored. Matrices
regenerated; 2× intent_ok false / 1× true preserved.

## 2026-07-04 14:47 UTC — Phase A initial build (9ca085a)

Repository scaffolded (empty skeleton, then populated per the Phase A
prompt) and pushed to `PayloadGuard-PLG/payloadguard-evidence`:

- `evidence/model.py` (Strength enum, CAVEAT map, dataclasses; Dafny
  false-zero parser note carried for Phase B), `evidence/schema/
  metadata.schema.json` (draft 2020-12, unknown-key rejection,
  crosshair_bounds required), `evidence/render/manual_matrix.py`
  (hand-reviewed binder/renderer).
- `examples/dosage_calculator/`: dose-clamping kernel with PEP316 contracts;
  Sample A (clean, exit 0) and Sample B (broken, exit 1 with concrete
  counterexample) captured by real CrossHair 0.0.107 runs;
  `metadata.yaml` sourced from GIP v1.0 with three requirements;
  matrices generated (not hand-typed) showing intended-PROVEN vs realized-
  BOUNDED_CHECKED mismatches honestly.
- `sources/`: GIP v1.0 hazard analysis archived verbatim + standing rule for
  future source documents. FRN pump-type tag left explicitly unresolved
  after a failed resolution attempt (web search; UPenn pages unreachable).
- Known bounds divergence (declared vs effective CrossHair bounds) flagged,
  not smoothed over. Nothing in the repo asserts PROVEN as realized.
