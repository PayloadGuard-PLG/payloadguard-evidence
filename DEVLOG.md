# DEVLOG — payloadguard-evidence

Append-only session log. Every session adds one dated entry (UTC), newest
first, citing commit SHAs. Timestamps below are taken from the git history
and run manifests, not reconstructed from memory.

---

## 2026-07-06 — Gate 2 build, Phase 5: vocabulary-agnostic binder, Step 3 (fold in Type 1; confirm Type 2 stays standalone)

Continuing the phased binder build. Re-examined the plan before
implementing rather than mechanically following the earlier wording
("fold Types 1/2 into the binder") - Type 2 doesn't actually fit inside
a per-variant builder call, and forcing it in would have been worse
design, not better.

- **Analysis:** Type 1 (identity mismatch) is inherently per-variant -
  it checks one metadata file's declared bindings against the evidence
  store - so it belongs inside `build_matrix()`. Type 2 (outcome
  mismatch) compares raw manifests across the WHOLE dataset regardless
  of which variant is being built; folding it into `build_matrix()`
  would mean re-running the identical whole-dataset check redundantly on
  every one of the four variant calls, for no benefit. It stays a
  standalone `generate_artifacts.py` stage, the same way the
  fact-equality gate does (both are properties of the artifact/input
  set, not of a single generation call).
- **Folded in:** `build_matrix()` now calls `run_conflict_gate(metadata,
  concrete_store, manifest)` as its first step, before assembling any
  record - Tier 1. This closes a real gap: Type 1 previously only ran
  inside the `generate_artifacts.py` pipeline stage, so running e.g.
  `generate_matrix_a.py` alone would have bypassed it entirely (the
  individual generators are documented to bypass fact-equality the same
  way - Type 1 had identical exposure until now).
- **Base matrix's check narrowed, not removed:** `metadata.yaml` never
  calls `build_matrix()` (frozen `manual_matrix.py` path, ruling R2c), so
  it keeps its own explicit check. Renamed `stage_conflict_check` to
  `stage_base_conflict_check`, scoped to just the base file (3 symbolic
  bindings - base declares no concrete evidence at all). Stage 5's
  comment updated to note a/b/c-symbolic/c-concrete are now
  self-checking via `build_matrix()`.
- **Proven, not assumed:** added
  `test_build_matrix_folds_in_type1_check` to
  `tests/test_conflict_check.py` - drives `build_matrix()` directly with
  a conflicting in-memory fixture and confirms it raises before
  assembling a single record, proving the fold-in itself rather than
  just the underlying check function. Full pipeline re-run end to end;
  every regenerated artifact still differs only by `generated_utc`.
  Suite: 34 passed (33 prior + 1 new).
- **Documented tradeoff:** `build_matrix_variant_a/b/c` (the Step 2
  fallback) do NOT have Type 1 folded in. If the fallback is ever used
  in an emergency, Type 1's per-call check is temporarily lost along
  with it - an accepted tradeoff of restoring known-good behavior
  quickly, recorded rather than silently true.
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc. Gate 2's binder work is now Steps 1-3 done;
  Step 4 (delete the fallback once stable) and the CLI remain.

## 2026-07-06 — Gate 2 build, Phase 4: vocabulary-agnostic binder, Step 2 (cutover)

Steven approved proceeding with an explicit request to keep a fallback
available ("ensure we can fallback if necessary"). Cutover done with
that constraint built in, not bolted on afterward.

- **Cut over:** `generate_matrix_a.py` / `_b.py` / `_c.py` now import
  and call `build_matrix("a"/"b"/"c-symbolic"/"c-concrete", ...)` from
  `evidence/render/matrix_variants.py` instead of the original
  `build_matrix_variant_a/b/c` functions directly.
- **Fallback, by design:** the three original functions are deliberately
  left in place, fully intact and unused. If a problem with
  `build_matrix()` ever surfaces, each generator's import + call can be
  reverted to the corresponding original function in one line, or this
  commit can be `git revert`ed outright. Deleting them is scoped as its
  own later cleanup step (Step 4), gated on the cutover proving stable —
  not bundled into the cutover itself.
- **Verified, not assumed:** ran the full `generate_artifacts.py`
  pipeline post-cutover (all 7 stages clean) and diffed every
  regenerated artifact against the pre-cutover committed versions -
  differs only by `generated_utc`, exactly as the Step 1 equivalence
  proof predicted. Full suite: 33 passed, unchanged from Step 1 (this
  step changed which function each generator calls, not any logic).
- Updated the module-level comment in `matrix_variants.py` to mark
  `build_matrix()` as authoritative and the three original functions as
  an explicit, intentional fallback rather than dead code.
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc - Gate 2's binder work now tracked as Steps
  1-2 done, Step 3 (fold CONFLICT Types 1/2 into the binder) and Step 4
  (delete the fallback functions once stable) still open, plus the CLI.

## 2026-07-06 — Gate 2 build, Phase 3: vocabulary-agnostic binder, Step 1

Steven confirmed the phased plan and set the working principle for the
rest of Phase B->C: correctness over speed, one step at a time, always
with the end of Phase C in view. This step is scoped narrowly on
purpose - it is a genuine architectural refactor (unlike Types 1/2,
which extended an existing pattern), so it gets its own proof before
anything currently authoritative is touched.

- **Built:** `build_matrix(variant_key, metadata, manifest,
  concrete_store, tool_versions=None)` in
  `evidence/render/matrix_variants.py` - one entry point replacing
  `build_matrix_variant_a/b/c`. Literal extraction, not new logic: each
  variant's record-assembly ("binder": `_bind_declared`, `_bind_shadow`,
  `_bind_self_describing`) and row-rendering ("shape":
  `_shape_evidence_array`, `_shape_flattened_shadow`,
  `_shape_method_partitioned`) lifted verbatim into named functions,
  dispatched through a declarative table (`_VARIANT_SPECS`) instead of
  three separate top-level functions. Binding strategy and row shape
  split as the two real axes of variation, so a future fifth shape can
  reuse an existing piece instead of requiring a whole new function.
- **Correctness proof:** `tests/test_binder_equivalence.py` (5 tests)
  runs the old function and `build_matrix()` against identical real
  committed inputs for all four variant keys and asserts equality two
  ways - dict equality and `json.dumps()` string equality (the second
  catches key-order drift dict equality alone would miss). All pass.
- **Nothing cut over.** `generate_matrix_a.py` / `_b.py` / `_c.py` and
  `regenerate_all.py` still call the original functions, untouched.
  Pipeline re-run end to end; every regenerated artifact differs only by
  `generated_utc` - zero observable change from this step. Suite: 33
  passed (28 prior + 5 new).
- Documentation updated to record Step 1 as done and Step 2 (the actual
  cutover - retiring the three old functions and generator scripts,
  folding Types 1/2 into the binder) as the next, deliberately separate,
  higher-risk step: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc.

## 2026-07-06 — Gate 2 build, Phase 2: Type 2, variant C asymmetry closed

Continuation of the phased Gate 2 build, addressing the two remaining
well-scoped gaps flagged at the end of Phase 1 (Type 2, variant C's
binding asymmetry). The third — the vocabulary-agnostic binder + CLI
unification — is deliberately left for its own phase: it's a real
architectural refactor (consolidating four separate generator scripts),
not an extension of the existing Type 1 pattern, and carries meaningfully
more regression risk.

- **Variant C asymmetry closed (Gate 4).** `metadata.schema.c.json`
  gained an optional `evidence` property (identical shape to variant
  A's); `metadata.c.yaml` now declares it on all three requirements,
  matching the real bindings already in `concrete_results.json`
  (`kernel_detects_bolus_limit_exceeded` -> REQ-GIP-1-4-12, etc.). This
  is cross-checking-only: `build_matrix_variant_c` never reads
  `evidence` — C's binding stays evidence-store-carried, unchanged.
  Confirmed by regenerating: C's artifacts diff only by `generated_utc`.
  Bindings checked by the Type 1 gate rose from 20 to 24 (C now
  contributes 7 instead of 0).
- **Type 2 (outcome mismatch) built.** `evidence/conflict.py` gained
  `outcome_conflicts()` / `run_outcome_gate()`: manifests are grouped by
  identity (tool, target, enforced `per_condition_timeout_s` —
  deliberately excluding the raw argv's environment-specific absolute
  path and `started_utc`); a group with more than one distinct
  `exit_code` is a conflict. Wired into `generate_artifacts.py` as stage
  4, run against all four committed manifests: 4 manifests, 4 distinct
  identities, 0 conflicts — real, honest, and currently vacuous, since no
  two committed manifests share a target. Tested with two synthetic
  cases (positive mismatch; same-outcome-different-target confirming no
  over-firing).
- `tests/test_conflict_check.py`: 11 tests total (up from 7) — added
  variant C's clean-pass case and three Type 2 cases.
- Full pipeline re-run end to end (7 stages now); regenerated artifacts
  confirmed byte-identical except timestamps. Suite: 28 passed (24 prior
  + 4 new).
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc.
- **Still open, its own phase:** the vocabulary-agnostic binder (one
  implementation driving all four schema variants, replacing
  `generate_matrix_a/b/c.py`) and the CLI. Both CONFLICT types run today
  as standalone pipeline stages alongside the existing separate
  generators.

## 2026-07-06 — Gate 2 build, Phase 1: CONFLICT rule Type 1 (identity mismatch)

First build increment against the roadmap, taken in a small, self-
contained phase per Steven's direction (small phases, stop for input or
new issues). Scoped to what was already fully specified and ratified —
no new decisions required.

- **`evidence/conflict.py`:** implements Type 1 for real, over real data.
  `concrete_binding_conflicts()` cross-checks metadata's top-down
  concrete bindings (variant A's `evidence` list; variant B's shadow
  `parent_requirement` + implementation-suffix form) against
  `concrete_results.json`'s self-declared `requirement_id`.
  `symbolic_binding_conflicts()` cross-checks each requirement's declared
  `implementation` file against the crosshair manifest's actual
  `target`. `run_conflict_gate()` combines both, Tier 1 (raises on any
  mismatch, matching fact-equality/structural-PROVEN's behavior).
- **Wired into `generate_artifacts.py`** as stage 3 (after capture
  integrity, before regeneration) — checked against all four metadata
  files: 20 bindings checked, 0 conflicts. Pipeline re-run end to end;
  regenerated artifacts differ only by `generated_utc` timestamp
  (deterministic regeneration confirmed).
- **`tests/test_conflict_check.py`** (7 tests): both ratified positive
  cases (variant A's `evidence` shape and variant B's shadow shape) as
  in-memory mutated fixtures reproducing the failure; the ratified
  negative case (REQ-GIP-1-4-12's kernel_scope/system_scope split) run
  against the real committed data, confirmed clean; a symbolic-file
  mismatch case; and a distinct-failure-mode check (a declared test_id
  that doesn't exist in the evidence store at all is a hard error, not a
  silently-passing conflict check, since there's no second claim to
  compare against).
- Variant C is untouched — it declares no top-down concrete binding, so
  Type 1 has nothing to compare there yet (Gate 4's known asymmetry,
  unchanged by this phase).
- Suite: 24 passed (17 prior + 7 new).
- Documentation updated to reflect BUILT status:
  `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md` (component map + Phase
  boundary), `README.md`, roadmap doc.
- **Not done this phase, staying open per the small-phases plan:** Type
  2 (outcome mismatch — needs a cross-manifest comparison mechanism that
  doesn't exist yet), the vocabulary-agnostic binder itself, and the CLI.

## 2026-07-06 — Gate 2 CONFLICT rule defined and ratified

Working session with Steven to define CONFLICT against the two candidate
test cases already on file, refine the definition, and lock it in.

- **Definition drafted:** CONFLICT requires two claims about the *same*
  `(requirement, scope)` and the same underlying verification act — never
  triggered by two legitimately different evidence types bound to one
  requirement, and never triggered by an `intent_ok` mismatch (that's a
  binding compared to its own stated intent, not two competing claims;
  already has its own mechanism, R1). Two sub-types identified:
  - Type 1 (identity mismatch): top-down and bottom-up claims about one
    binding disagree on target file/method — Gate 4's exact trigger.
  - Type 2 (outcome mismatch), added during review: two claims agree on
    target identity but disagree on what that identical run produced.
    Not hypothetical — motivated directly by this repo's own documented
    CrossHair model-fidelity non-determinism (Sample C / overflow-probe
    exhibits, Gate 3's caveat) that a same-invocation result can vary.
- **Tested against three cases:** positive Type 1 (dual-authorship
  file/method mismatch), negative (REQ-GIP-1-4-12 kernel_scope/
  system_scope split — a GAP, not a conflict, since there's no second
  claim to disagree with), positive Type 2 (a future duplicate manifest
  for an identical target reporting a different exit code).
- **Ratified by Steven** ("yep agree. lock in") — status moves from
  BLOCKED to DEFINED. Not yet built: Type 1 reuses Gate 4's intersection
  check directly; Type 2 needs a new cross-manifest comparison mechanism
  that doesn't exist yet. Building either into Gate 2's generalized
  binder is still open.
- `KNOWN_LIMITATIONS.md` rewritten fresh to reflect the current state of
  all six gates in one pass, rather than accumulating further patches.
  `payloadguard-evidence-roadmap-phaseB-to-C.md`, `SYSTEM_BLUEPRINT.md`,
  and `README.md` updated to match.
- Suite: 17 passed (unchanged — documentation only, no capture or
  generator touched).

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
