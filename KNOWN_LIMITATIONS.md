# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-06 (Gate 3 closed by real behavioral test; Gate 6
resolved; Gate 4 decision recorded; Gate 2 candidate test cases added).

| Gate | Status | Summary |
|---|---|---|
| Gate 2 — CONFLICT rule definition | **BLOCKED on Steven** | Searched both authorized sources in full. The term does not appear in PayloadGuard-Evidence-Blueprint-1 (Drive doc id 154iVHHPkCbrNN6XQ_B07jS0LJG7VYKxtSPT8TEwmMwY; 0 case-insensitive occurrences; committed copy in-repo) nor in SYSTEM_BLUEPRINT.md (single occurrence is a to-do mention, line 162 — not a definition). Per the roadmap: stop, name it, ask. Closest neighbouring concept found: Blueprint Phase 2 acceptance (b) — intent-vs-reality mismatch "raises a GAP/flag". Semantics will not be inferred from the name. Two candidate test cases now on file (2026-07-05 roadmap v2): positive — a top-down ALM contract claiming "REQ-X verified at file F, method M" disagreeing with a bottom-up source-embedded assertion of a different file/method/hash; negative — REQ-GIP-1-4-12's kernel_scope/system_scope split (one evidenced, one an explicit GAP), which is a documented absence, not a conflict. Still open, not decided. |
| Gate 3 — bounds enforcement via CrossHair API | **DECIDED 2026-07-06: stay-CLI** | Real behavioral test executed (not just a technique writeup) — findings below. |
| Gate 4 — binding authorship | **DECIDED: option 3 (both, cross-checked); mechanism specified; build deferred to Gate 2** | Decision and mechanism below. |
| Gate 5 — single-evidence-type fixture for variant C | **RESOLVED (symbolic-only); concrete-only impossible pre-Gate-2, named** | `tests/test_single_evidence_type.py`: in-memory fixture requirement with symbolic evidence only, driven through the real variant C builder — appears in exactly one artifact (symbolic 1 row, concrete 0 rows), intent projected per R1. Committed data untouched. A concrete-only fixture cannot exist yet: the current C builder binds a symbolic record to every requirement unconditionally (see Gate 4 note 3). |
| Gate 6 — FRN pump-type tag | **RESOLVED** | `FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725); within the GIP taxonomy, general-purpose volumetric infusion pumps (peristaltic mechanism, cassette-based administration set), distinct from `All`. Full trail in `sources/README.md`. Well-supported (NotebookLM extraction of the full source PDF, cross-checked against independent FDA-registry research landing on the same code) but not yet independently re-verified against the raw Sec 2.4.1 text — noted, not hidden. |
| Phase C interface: `verifier_completion_status` on VerificationResult | **NOTED for Gate 2** | The Gate 2 binder/schema must reserve room for this field (Blueprint false-zero trap) and keep strength-assignment adapter-scoped so PROVEN remains structurally impossible for CrossHair/pytest-backed requirements even after the Dafny adapter exists. Phase C now has four concrete mechanisms (STPs, mutation testing, sharpened false-zero parsing, NL-dialogue confirmation) — see `payloadguard-evidence-roadmap-phaseB-to-C.md`. |

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
actually uses. Documented as-is, not oversold.

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
   turning the asymmetry into a consistency check. Needs Gate 2's
   CONFLICT rule semantics if "disagreement" is ever to be rendered
   rather than fatal.

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
  them.

This mechanism also gives Gate 2's CONFLICT rule its clearest concrete
positive trigger (see Gate 2 above): a top-down/bottom-up disagreement
under this exact check.

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

## Session-scope note (2026-07-05, Turn B4)

The Phase B v3 prompt's Turn B4/B5 spec bodies arrived as placeholder
text; the companion roadmap was supplied separately and is committed as
`payloadguard-evidence-roadmap-phaseB-to-C.md` — its Gate 1 section defines
Turn B4's scope (minimal pipeline, four real variant artifacts as ground
truth, reviewed by Steven before Gate 2 starts). "Four real files" is read
as the four variant JSON artifacts (a / b / symbolic / concrete, each with
its Markdown sibling); the base matrix remains the frozen legacy symbolic
subset per ruling R2c, as the roadmap's own verified-state section records.
