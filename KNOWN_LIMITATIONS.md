# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-06 (Gate 2 vocabulary-agnostic binder, Step 1:
build_matrix() added, proven byte-identical to all three existing
per-variant functions; nothing cut over yet).

| Gate | Status | Summary |
|---|---|---|
| Gate 2 — CONFLICT rule | **Types 1 and 2 BUILT; vocabulary-agnostic binder Step 1 done (proven, not cut over); CLI still open** | `evidence/conflict.py` implements both CONFLICT sub-types for real, over real committed data (11 tests). `evidence/render/matrix_variants.py` gained `build_matrix()`, a declarative binder+shape dispatch proven byte-identical to `build_matrix_variant_a/b/c` (`tests/test_binder_equivalence.py`, 5 tests) — additive only, generators still call the original functions. Details below. |
| Gate 3 — bounds enforcement via CrossHair API | **DECIDED 2026-07-06: stay-CLI** | Real behavioral test executed (not just a technique writeup) — findings below. |
| Gate 4 — binding authorship | **DECIDED: option 3 (both, cross-checked); Type 1 now implements this for all three metadata shapes, incl. variant C** | Decision and mechanism below. |
| Gate 5 — single-evidence-type fixture for variant C | **RESOLVED (symbolic-only); concrete-only impossible pre-Gate-2, named** | `tests/test_single_evidence_type.py`: in-memory fixture requirement with symbolic evidence only, driven through the real variant C builder — appears in exactly one artifact (symbolic 1 row, concrete 0 rows), intent projected per R1. Committed data untouched. A concrete-only fixture cannot exist yet: the current C builder binds a symbolic record to every requirement unconditionally (see Gate 4 note 3). |
| Gate 6 — FRN pump-type tag | **RESOLVED** | `FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725); within the GIP taxonomy, general-purpose volumetric infusion pumps (peristaltic mechanism, cassette-based administration set), distinct from `All`. Full trail in `sources/README.md`. Well-supported (NotebookLM extraction of the full source PDF, cross-checked against independent FDA-registry research landing on the same code) but not yet independently re-verified against the raw Sec 2.4.1 text — noted, not hidden. |
| Phase C interface: `verifier_completion_status` on VerificationResult | **NOTED for Gate 2** | The Gate 2 binder/schema must reserve room for this field (Blueprint false-zero trap) and keep strength-assignment adapter-scoped so PROVEN remains structurally impossible for CrossHair/pytest-backed requirements even after the Dafny adapter exists. Phase C now has four concrete mechanisms (STPs, mutation testing, sharpened false-zero parsing, NL-dialogue confirmation) — see `payloadguard-evidence-roadmap-phaseB-to-C.md`. |

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

### Vocabulary-agnostic binder — Step 1 done (2026-07-06): built, proven equivalent, not cut over

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

**Status: additive only, nothing cut over.** `generate_matrix_a.py` /
`_b.py` / `_c.py` and `regenerate_all.py` are untouched and still call
the original `build_matrix_variant_a/b/c` functions; `build_matrix()` is
not called from anywhere in the generation path yet. The full pipeline
was re-run end to end after this change and every regenerated artifact
differs only by `generated_utc` — proving this step introduced zero
observable change. This is deliberately the stopping point before the
higher-risk step (retiring the three old functions and the separate
generator scripts, and folding Types 1/2 into the binder as internal
steps instead of standalone pipeline stages) — see "What's left for Gate
2" below.

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

Design input from Gate 5 work (still applies): the current C builder
binds a symbolic record to every requirement by construction and does not
verify the requirement's `implementation` against the capture manifest's
`target` — the Gate 2 binder must bind symbolic evidence by verified
code-location match per this mechanism. **Status: decision and mechanism
recorded; building it is Gate 2's binder work, not yet started.**

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

## What's left for Gate 2

- CONFLICT rule Type 1: **built** (`evidence/conflict.py`, wired into
  `generate_artifacts.py` stage 3, tested across all three metadata
  shapes including variant C).
- CONFLICT rule Type 2: **built** (`evidence/conflict.py`, wired into
  `generate_artifacts.py` stage 4, tested against real + synthetic
  data).
- Binding authorship (Gate 4): decided (option 3) and now implemented
  for all three metadata shapes — variant C's asymmetry is closed.
- Vocabulary-agnostic binder: **Step 1 done** — `build_matrix()` built
  and proven byte-identical to the three existing per-variant functions
  (`tests/test_binder_equivalence.py`). **Step 2 (not started):** cut
  `generate_matrix_a.py` / `_b.py` / `_c.py` over to call `build_matrix()`
  instead of the original functions, then retire the originals; fold
  Types 1/2 into the binder as internal steps instead of standalone
  pipeline stages once the cutover is proven stable.
- CLI: not started — planned as a thin wrapper once the binder itself is
  stable post-cutover.

## Session-scope note (2026-07-05, Turn B4)

The Phase B v3 prompt's Turn B4/B5 spec bodies arrived as placeholder
text; the companion roadmap was supplied separately and is committed as
`payloadguard-evidence-roadmap-phaseB-to-C.md` — its Gate 1 section defines
Turn B4's scope (minimal pipeline, four real variant artifacts as ground
truth, reviewed by Steven before Gate 2 starts). "Four real files" is read
as the four variant JSON artifacts (a / b / symbolic / concrete, each with
its Markdown sibling); the base matrix remains the frozen legacy symbolic
subset per ruling R2c, as the roadmap's own verified-state section records.
