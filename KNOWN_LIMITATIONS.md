# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-07 (Phase C Gate C4 BUILT: Spec-Testing Proofs
(IronSpec methodology) for the dosage.dfy Dafny spec found a genuine gap
— the original postcondition only bounded `dose`, never pinned it to the
actual clamped value, so a wrong implementation could have satisfied it
— confirmed mechanically via a Dafny lemma that failed to exclude a
wrong candidate value. Fixed dosage.dfy directly (added an ExpectedDose
function + a pinning ensures clause), preserved the original as an
honesty exhibit (dosage_underconstrained.dfy), and built two STP suites
proving both directions for real. Gate C3 (vectors 1-3, vector 4
blocked) and Gates C1/C2 were built earlier the same week and are
otherwise unchanged, still not wired into any live traceability matrix).

| Gate | Status | Summary |
|---|---|---|
| Gate 2 — CONFLICT rule + binder | **COMPLETE** | `evidence/conflict.py` implements both CONFLICT sub-types (12 tests). `build_matrix()` (`evidence/render/matrix_variants.py`) is the sole implementation across all four variants, running Type 1 internally on every call; Type 2 stays standalone (whole-manifest-set check, not per-variant). `evidence/cli.py` wraps it for any metadata/manifest/concrete-store path. The Step 2 fallback functions (`build_matrix_variant_a/b/c`) and `tests/test_binder_equivalence.py` (which existed solely to check against them) are deleted — git history holds them if ever needed again. Details below. |
| Gate 3 — bounds enforcement via CrossHair API | **DECIDED 2026-07-06: stay-CLI** | Real behavioral test executed (not just a technique writeup) — findings below. |
| Gate 4 — binding authorship | **DECIDED: option 3 (both, cross-checked); Type 1 now implements this for all three metadata shapes, incl. variant C** | Decision and mechanism below. |
| Gate 5 — single-evidence-type fixture for variant C | **FULLY RESOLVED (2026-07-06)** | `tests/test_single_evidence_type.py`: both symbolic-only AND concrete-only in-memory fixtures now appear in exactly one variant-C artifact each. The concrete-only case was impossible until today: `_bind_self_describing` bound a symbolic record to every requirement unconditionally, regardless of what it declared. Details below. |
| Gate 6 — FRN pump-type tag | **RESOLVED** | `FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725); within the GIP taxonomy, general-purpose volumetric infusion pumps (peristaltic mechanism, cassette-based administration set), distinct from `All`. Full trail in `sources/README.md`. Well-supported (NotebookLM extraction of the full source PDF, cross-checked against independent FDA-registry research landing on the same code) but not yet independently re-verified against the raw Sec 2.4.1 text — noted, not hidden. |
| Phase C Gate C1 — Dafny adapter | **BUILT 2026-07-07; spec strengthened 2026-07-07 by Gate C4** | Real Dafny 4.11.0 spec for the dosage kernel (`examples/dosage_calculator/dosage.dfy`, verifies clean: `2 verified, 0 errors` — an `ExpectedDose` function plus the method, since Gate C4's fix) plus a deliberately broken variant (`dosage_broken.dfy`, fails for real: `0 verified, 2 errors`, exit 4); a capture runner pair (`run_verify_dafny.py` / `run_verify_dafny_broken.py`) mirroring `run_verify.py`'s discipline, with real committed captures; and `evidence/dafny_adapter.py::parse_dafny_capture`, implementing the false-zero guard via regex on the verifier's own summary line (never a substring match, never bare exit code), refusing on nonzero exit, missing summary line, or nonzero error count. Six tests in `tests/test_dafny_adapter.py`, including a substring-trap regression and a check that `assert_no_realized_proven` still blocks this adapter's PROVEN output from ever reaching a matrix row. REQ-DOSE-003 is explicitly scoped out of the Dafny spec (Dafny `real` has no IEEE overflow concept — confirmed empirically). |
| Phase C Gate C2 — PROVEN exclusivity migration | **BUILT 2026-07-07** | Ruling **R3** (supersedes R2): `assert_no_realized_proven` (`evidence/render/matrix_variants.py`) now permits PROVEN as a realized strength only when a record's `method == "dafny"` AND `verifier_completion_status == "completed"`; every other method — including a record with no method at all — is still hard-blocked, exactly as under R2. 8 new tests in `tests/test_proven_exclusivity.py`: a positive case (a real Dafny PROVEN record, produced the same way Gate C1's adapter produces it, is accepted), explicit negatives for crosshair and concrete_test records forced to claim PROVEN (checked explicitly, not by omission), a missing-method case, two defense-in-depth cases (a `method == "dafny"` record without a completed status is still refused), the row-level-cell shape (variant B/C), and a regression check that all four committed matrix artifacts — none of which contain a dafny record today — still pass unchanged. Still not wired into `build_matrix()` or any generator; a Dafny-sourced record cannot yet reach a live matrix row at all, so R3's positive branch is proven correct in isolation, not yet exercised end-to-end. |
| Phase C Gate C3 — Dafny output-parsing hardening | **BUILT for vectors 1–3 (2026-07-07); vector 4 BLOCKED, named** | **Vector 1 (vacuous preconditions):** `evidence/dafny_spec_lint.py::check_precondition_satisfiability` extracts a method's `requires` clauses and asks Z3 for real satisfiability, via a small hand-written expression translator (booleans, comparisons incl. chaining, arithmetic, real/int/nat/bool — anything else, e.g. quantifiers, refused outright). Proven against a real committed fixture, `examples/dosage_calculator/vacuous_precondition_probe.dfy`: Dafny itself reports a clean pass (`1 verified, 0 errors`) on a method whose precondition (`x > 0 && x < 0`) can never hold; the checker correctly reports `unsat`. **Vector 2 (weak postconditions, best-effort heuristic, not a proof):** `scan_weak_postconditions` flags `ensures` clauses using a one-way `==>` without a matching `<==>`, tested against a synthetic weak clause (flagged) and both the real dosage.dfy spec and a `<==>` clause (correctly not flagged). **Vector 3 (timeout/resource-limit masking):** real finding on the installed 4.11.0 binary — `dafny verify --resource-limit=1` on the real dosage.dfy spec produces `Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource` — an "errors" count of 0 alongside an incomplete run. Confirmed the real capture's exit_code is 4 (nonzero), so Gate C1's exit-code check already refuses it (an earlier suspicion of an exit-0 false-zero here was a shell-piping artifact in this session's own probing, corrected before being reported as a finding); the summary-line parser in `evidence/dafny_adapter.py` was still hardened to refuse independently on `"out of resource"`/`"out of memory"`/`"timed out"` markers and on more than one summary line in a capture, as defense in depth. **Vector 4 (specification stripping): still BLOCKED, named** — the source material describing this fourth vector was cut off before detail was captured; needs a follow-up read of the original document before it can be scoped at all, not inferred from the name. |
| Phase C interface: `verifier_completion_status` on VerificationResult | **RESOLVED via Gate C1 + C2** | The field exists on `VerificationResult` (`evidence/model.py`), is set by Gate C1's adapter, and is now load-bearing in Gate C2's R3 check — PROVEN requires it to equal `"completed"`, not just a matching method label. Strength-assignment stays adapter-scoped, so PROVEN remains structurally impossible for CrossHair/pytest-backed requirements. |
| Phase C Gate C4 — Spec-Testing Proofs (STPs) | **BUILT 2026-07-07; found and fixed a real spec gap** | IronSpec methodology: prove specific input/output pairs are accepted or rejected by the SPECIFICATION alone, independent of any implementation. Applied to dosage.dfy, an STP lemma revealed the original postcondition (bounds + reverse-flow-zero only) never pinned `dose` to the actual clamped value — a wrong candidate value could not be proven excluded, meaning a broken implementation could have satisfied the spec undetected. **Fixed for real:** `dosage.dfy` gained an `ExpectedDose` function and a pinning `ensures dose == ExpectedDose(...)` clause; re-verified clean (`2 verified, 0 errors`); the real committed capture was re-run honestly (`raw_dafny_output.txt` / `run_manifest_dafny.json` now reflect the fixed spec). The original weak spec is preserved verbatim as `dosage_underconstrained.dfy` (an honesty exhibit, same rationale as `dosage_naive_widening.py`). Two STP suites prove both directions for real: `dosage_stp_suite.dfy` (6 lemmas across the 3 logical branches — normal in-range, ceiling-clamped, reverse-flow — `include`s the fixed spec, all verify: `10 verified, 0 errors`) and `dosage_stp_suite_against_underconstrained.dfy` (the 2 REJECT lemmas for the branches that actually had a gap, `include`s the preserved weak spec, both genuinely fail: `0 verified, 2 errors`, exit 4 — a real negative capture, not smoothed over). 6 new tests in `tests/test_dafny_stp_suite.py`, including a regression on a self-caught mistake (an early REJECT-lemma draft used an out-of-bounds wrong value that the weak spec already excluded trivially, giving a false pass that didn't test the real gap — caught and corrected before committing). Neither STP suite is wired into `build_matrix()` or any generator; matches Gates C1–C3's scope discipline. |

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
