# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-06 (Gate 5 fully resolved: variant C's binder no
longer binds symbolic evidence unconditionally, so a concrete-only
fixture is now constructible — the last remaining limitation from the
original six-gate ledger is closed).

| Gate | Status | Summary |
|---|---|---|
| Gate 2 — CONFLICT rule + binder | **COMPLETE** | `evidence/conflict.py` implements both CONFLICT sub-types (12 tests). `build_matrix()` (`evidence/render/matrix_variants.py`) is the sole implementation across all four variants, running Type 1 internally on every call; Type 2 stays standalone (whole-manifest-set check, not per-variant). `evidence/cli.py` wraps it for any metadata/manifest/concrete-store path. The Step 2 fallback functions (`build_matrix_variant_a/b/c`) and `tests/test_binder_equivalence.py` (which existed solely to check against them) are deleted — git history holds them if ever needed again. Details below. |
| Gate 3 — bounds enforcement via CrossHair API | **DECIDED 2026-07-06: stay-CLI** | Real behavioral test executed (not just a technique writeup) — findings below. |
| Gate 4 — binding authorship | **DECIDED: option 3 (both, cross-checked); Type 1 now implements this for all three metadata shapes, incl. variant C** | Decision and mechanism below. |
| Gate 5 — single-evidence-type fixture for variant C | **FULLY RESOLVED (2026-07-06)** | `tests/test_single_evidence_type.py`: both symbolic-only AND concrete-only in-memory fixtures now appear in exactly one variant-C artifact each. The concrete-only case was impossible until today: `_bind_self_describing` bound a symbolic record to every requirement unconditionally, regardless of what it declared. Details below. |
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
