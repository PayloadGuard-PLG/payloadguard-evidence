# DEVLOG — payloadguard-evidence

Append-only session log. Every session adds one dated entry (UTC), newest
first, citing commit SHAs. Timestamps below are taken from the git history
and run manifests, not reconstructed from memory.

---

## 2026-07-07 — Phase C Gate C4 built: Spec-Testing Proofs found and fixed a real gap in dosage.dfy

Requested directly: "start gate C4." Applied IronSpec's methodology -
prove a specific input/output pair is accepted or rejected by the
SPECIFICATION itself, independent of any implementation - to the one
Dafny spec that exists in this repo (`dosage.dfy`, Gate C1). It found a
real gap on the first attempt, not a synthetic demonstration.

- **The finding, confirmed mechanically:** `CalculateHourlyDose`'s
  original two ensures clauses (`0.0 <= dose <= maxSafeDoseMgPerHr` and
  `infusionRateMlPerHr >= 0.0 || dose == 0.0`) bound `dose` and force it
  to 0 on reverse flow, but never relate it to the actual product of
  rate and concentration otherwise. A Dafny lemma stating "for these
  fixed inputs, if dose satisfies both ensures clauses, dose must equal
  the one correct clamped value" **failed to verify** - Dafny could not
  prove it, because the postcondition genuinely doesn't force it. A
  method that always returned `0.0` for any non-negative-rate input
  would have satisfied the exact spec Gate C1 verified clean. The same
  bug class Gate 1 found by hand for REQ-GIP-1-4-12 (spec/evidence not
  matching the requirement text), recurring independently in this
  session's own new Dafny spec - caught mechanically this time.
- **Fixed for real:** `examples/dosage_calculator/dosage.dfy` gained
  `function ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr,
  maxSafeDoseMgPerHr): real` (the same three-way clamping logic as the
  method body) and a new `ensures dose == ExpectedDose(...)` clause
  pinning the output exactly. The two original ensures clauses stay,
  unchanged, for direct per-requirement traceability. Re-verified clean:
  `2 verified, 0 errors` (the function plus the method - up from `1
  verified`). **The real committed capture was re-run honestly, not
  patched:** `raw_dafny_output.txt` / `run_manifest_dafny.json` now
  reflect the fixed spec; `tests/test_dafny_adapter.py`'s exact
  `raw_status` assertion was updated to match, with a comment.
- **Preserved exhibit:** `examples/dosage_calculator/dosage_underconstrained.dfy`
  keeps the original weak spec byte-for-byte (same rationale as
  `dosage_naive_widening.py`) - it still verifies cleanly on its own (`1
  verified, 0 errors`); the bug is a spec weakness, not a verification
  failure.
- **Two STP suites, mechanically proving both directions, each
  `include`-ing the relevant spec rather than duplicating it:**
  - `dosage_stp_suite.dfy` (`include "dosage.dfy"`): six lemmas across
    the three logical branches of `CalculateHourlyDose` - normal
    in-range, ceiling-clamped, reverse-flow. ACCEPT + REJECT pairs for
    the first two; ACCEPT-only for reverse-flow (never a gap -
    `infusionRateMlPerHr >= 0.0 || dose == 0.0` already pins dose to 0
    there, even in the weak spec). All six verify: `10 verified, 0
    errors`, exit 0.
  - `dosage_stp_suite_against_underconstrained.dfy` (`include
    "dosage_underconstrained.dfy"`): the same two REJECT lemmas, run
    against the weak spec instead. Both **genuinely fail**: `0
    verified, 2 errors`, exit 4 - a real negative capture, not smoothed
    over, same discipline as `dosage_broken.dfy`.
- **A mistake caught during this build, before committing:** an early
  draft of the ceiling-clamped REJECT lemma used the raw unclamped
  product (`500.0`) as the "wrong" value. That lemma verified even
  against the weak spec - not because the weak spec pins the correct
  value, but because `500.0` already violates the weak spec's own
  `0.0 <= dose <= maxSafeDoseMgPerHr` bound directly, so excluding it
  proved nothing about the real gap. Caught by checking the lemma's
  actual behavior against the weak spec directly rather than assuming
  the chosen value was a good test; corrected to `50.0` (in-bounds,
  still wrong) in both suites, re-verified, and a regression test added
  (`test_reject_lemmas_target_in_bounds_wrong_values_not_out_of_bounds_ones`)
  guarding against silently reintroducing the weaker value.
- **New capture runners:** `run_verify_dafny_underconstrained.py`,
  `run_verify_dafny_stp_suite.py`,
  `run_verify_dafny_stp_suite_against_underconstrained.py` - all
  mirroring `run_verify_dafny.py`'s discipline, producing genuine
  committed captures, no fabricated output.
- **Tests:** `tests/test_dafny_stp_suite.py`, 6 tests, checking the real
  committed captures directly (not via `evidence.dafny_adapter.py`,
  since an STP suite's capture is a proof about the spec's tightness,
  not itself a requirement's verification evidence). Full suite: **78
  passed** (72 prior + 6 new). Full `generate_artifacts.py` pipeline
  re-run: zero observable change beyond `generated_utc` timestamps.
- **Explicitly not done, and not this gate's job:** neither STP suite is
  wired into `build_matrix()` or any generator, and no automated
  mechanism runs STPs against future Dafny specs as a matter of course -
  this gate authored one STP suite for the one spec that exists, per
  its stated scope, not a generic STP-generation tool.

## 2026-07-07 — Phase C Gate C3 built (vectors 1-3): Z3 precondition check, weak-postcondition heuristic, timeout/resource-limit masking hardened

Requested directly: "start gate c3." Four vectors were named in the
roadmap; three were scopeable and are built here, the fourth stays
blocked exactly as before.

- **Vector 1 (vacuous preconditions) - BUILT.** New module
  `evidence/dafny_spec_lint.py::check_precondition_satisfiability`:
  extracts a method's `requires` clauses (`_find_method_header` tracks
  paren depth to find the body's opening brace; `_extract_clauses`
  splits on clause keywords) and hands their conjunction to Z3 for a
  real satisfiability check. A small hand-written recursive-descent
  translator (`_tokenize` + `_Parser`) covers the boolean/comparison/
  arithmetic subset this repo's specs actually use - `&&`, `||`, `!`,
  `==>`, `<==>`, chained comparisons, `+-*/`, real/int/nat/bool
  identifiers and literals (`nat` gets its implicit `>= 0` Dafny
  semantics). Quantifiers, `old(...)`, unknown parameter types, and any
  unparseable syntax raise `SystemExit` outright - refused, never
  mistranslated.
- **Proven against a real committed fixture, not a synthetic string
  only:** new `examples/dosage_calculator/vacuous_precondition_probe.dfy`
  - a tiny, dedicated Dafny file with `requires x > 0 && x < 0` and
  `ensures r == 999999`. Verified for real against Dafny 4.11.0: **`1
  verified, 0 errors`, exit 0** - a genuine clean pass on a method whose
  precondition can never hold. The Z3 checker correctly reports `unsat`
  on the same method - catching mechanically what the verifier's own
  clean-pass report missed. A true-negative companion confirms the real
  dosage.dfy kernel's actual precondition is `sat`.
- **Vector 2 (weak postconditions) - BUILT, heuristic, best-effort, as
  the roadmap scoped it.** `scan_weak_postconditions` flags `ensures`
  clauses using `==>` without a matching `<==>`. Tested against a
  synthetic weak clause (flagged, clause text quoted verbatim), the real
  dosage.dfy spec (zero warnings - its clauses use `<=`/`==`/`||`, never
  `==>`, a true negative), and a `<==>` clause (not flagged, another
  true negative). Explicitly not a proof: it cannot decide whether a
  bi-implication was actually needed for a given spec.
- **Vector 3 (timeout/resource-limit masking) - BUILT, with a real
  empirical finding.** `dafny verify --resource-limit=1` on the real,
  committed `dosage.dfy` spec produces
  `Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource`
  - an errors count of 0 on a run that did not complete. Committed for
  real via new `run_verify_dafny_resource_limited.py`, producing genuine
  `raw_dafny_output_resource_limited.txt` /
  `run_manifest_dafny_resource_limited.json`.
- **Checked whether this is actually exploitable via exit_code alone -
  it is not, on this Dafny version.** The real captured `exit_code` is
  **4** (nonzero), so Gate C1's existing exit-code check already refuses
  this capture before the summary line is parsed. An earlier suspicion
  in this same session that the exit code was 0 here turned out to be a
  shell-scripting artifact - a piped command (`... | tail -20; echo
  "EXIT:$?"`) whose `$?` captured `tail`'s exit status, not `dafny`'s.
  Caught and corrected by re-running the same command without the pipe
  before reporting it as a finding - the "verify empirically, don't
  assume" discipline applied to my own probing, not just the tool under
  test.
- **Hardened `evidence/dafny_adapter.py` anyway, as real defense in
  depth:** the summary-line regex now captures the tail after the error
  count and refuses if it contains `"out of resource"`, `"out of
  memory"`, or `"timed out"` (case-insensitive), independent of the
  exit-code check. Of these, only `"out of resource"` was independently
  reproduced end-to-end; the other two are the confirmed sibling
  vocabulary from the same Boogie/Dafny summary-formatting code path
  (verified by extracting UTF-16 string literals directly from the
  installed `Boogie.ExecutionEngine.dll` / `DafnyDriver.dll`) but not
  independently forced to reproduce this session - named as such. Also
  hardened: the parser now refuses if a capture contains more than one
  summary-line match (checked empirically that a normal multi-file
  `dafny verify` still emits exactly one aggregate summary line, so this
  closes a theoretical ambiguity without changing real-capture behavior).
- **Vector 4 (specification stripping) - still BLOCKED, named.** No new
  source material surfaced this session either.
- **Tests:** `tests/test_dafny_spec_lint.py` (11, vectors 1-2) and
  `tests/test_dafny_timeout_masking.py` (6, vector 3) - 17 new tests.
  Full suite: **72 passed** (55 prior + 17 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change beyond
  `generated_utc` timestamps.
- **Explicitly not done, and not this gate's job:** neither the Z3 check
  nor the weak-postcondition heuristic is invoked automatically anywhere
  in the capture or generation pipeline - standalone, tested
  capabilities, matching Gate C1's own scope. Wiring them into the
  capture workflow is a natural follow-up but wasn't asked for.

## 2026-07-07 — Phase C Gate C2 built: ruling R3, PROVEN's exclusivity migration

Requested directly: "start gate C2." The design was already fully
specified in `payloadguard-evidence-roadmap-phaseB-to-C.md`'s Gate C2
section from the prior planning session - this session implemented that
ratified design rather than inventing a new one.

- **`evidence/render/matrix_variants.py::assert_no_realized_proven`** -
  previously hard-failed if ANY record anywhere claimed PROVEN, full
  stop (ruling R2). Now implements ruling **R3**: PROVEN may appear as a
  realized strength only when a record's `method == "dafny"` **and**
  its `verifier_completion_status == "completed"` - both conditions
  required, not just a matching method label. Every other method -
  `crosshair`, `concrete_test`, or a record with no method at all (e.g.
  a scope-GAP row) - remains permanently, unconditionally excluded,
  exactly as under R2. Refactored into a shared `_assert_proven_gate`
  helper checked against both each row's `evidence` list (variant A's
  shape) and the row itself (variant B/C's flat shape).
- **Why both conditions, not just the method label:**
  `evidence/dafny_adapter.py::parse_dafny_capture` (Gate C1) is already
  structurally incapable of returning PROVEN unless its own exit-code,
  summary-line, and false-zero checks all passed - so in the adapter's
  own output the two conditions are always true together. R3 checks
  both anyway, at the matrix boundary, as defense in depth against a
  future binder assembling a Dafny-shaped record by hand instead of
  through the adapter, rather than trusting the method label alone.
- **`tests/test_proven_exclusivity.py`** - 8 new tests. The roadmap
  named two required cases; this build has both plus more:
  1. Positive - a real Dafny PROVEN record, produced via
     `parse_dafny_capture` against the real committed clean capture (the
     same one Gate C1 verified), is accepted.
  2. Negative, crosshair - a `method="crosshair"` record with
     `strength="PROVEN"` and a completed status is refused, checked
     explicitly with a real fixture, not inferred from the absence of a
     binder that would produce one.
  3. Negative, concrete_test - same property, the other permanently-
     excluded method.
  4. Negative, missing method - a record with no `method` key at all is
     refused, not silently accepted because there's nothing to compare
     against `"dafny"`.
  5-6. Negative, dafny method without a completed status (`None` and an
     explicit `"incomplete"` value) - the method label alone is not
     trusted; defense-in-depth, not redundant paranoia.
  7. Row-level shape - variant B/C's rows carry `strength`/`method`
     directly, not nested in an `evidence` list; confirmed the same
     rule applies there too.
  8. Regression - all four committed matrix artifacts (none of which
     contain a dafny record today) still pass unchanged.
- **Existing structural tests needed no changes:**
  `tests/test_structural_proven_check.py`'s corruption cases (a
  `crosshair`-method record forced to `PROVEN`) still raise under R3
  with the identical error-message substring - confirming R3 is a
  strict, narrow relaxation for one specific checked case, not a
  broadening of the rule in general.
- Full suite re-run: **55 passed** (47 prior + 8 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change to any
  committed matrix artifact beyond `generated_utc` timestamps - R3 has
  no effect on the live pipeline today, since no binder yet produces a
  dafny-method record.
- **Explicitly not done, and not this gate's job:** no binder
  (`_bind_declared`, `_bind_shadow`, `_bind_self_describing`) was
  changed to actually assemble a Dafny-sourced record into a live matrix
  row. R3 makes that *possible* without violating the structural gate;
  it does not make it *happen*. Per the roadmap's suggested build order,
  that wiring belongs alongside Gate C4 (STPs, "alongside the first real
  spec"); trusting a live PROVEN claim in earnest still waits on Gate C3.

## 2026-07-07 — Phase C Gate C1 built: real Dafny spec, capture runner, false-zero-guard adapter

Requested directly: "I need the C1 local build implementation" - not
just the toolchain research from the day before, the actual gate build.

- **`examples/dosage_calculator/dosage.dfy`** - a real Dafny method,
  `CalculateHourlyDose`, translated from `dosage.py`'s contracts
  (mirrors the clamping shape: `requires concentrationMgPerMl > 0.0`,
  `requires maxSafeDoseMgPerHr > 0.0`, `ensures 0.0 <= dose <=
  maxSafeDoseMgPerHr`, `ensures infusionRateMlPerHr >= 0.0 || dose ==
  0.0`). Verified for real against Dafny 4.11.0: `Dafny program
  verifier finished with 1 verified, 0 errors`, exit 0.
- **REQ-DOSE-003 explicitly scoped out of the Dafny spec** - checked,
  not assumed: `y := x / 0.0` on Dafny's `real` type is itself a
  flagged verification error, not a silent `inf`. Dafny reals are
  exact/arbitrary-precision with no IEEE overflow/infinity/NaN concept
  at all, so "finite result under overflow" cannot be faithfully stated
  as a Dafny postcondition. Named here as a deliberate exclusion rather
  than silently dropped or wrongly claimed proven. `weight_kg` also
  intentionally omitted (unused precondition-only guard in the Python
  original).
- **`dosage_broken.dfy`** - the Sample-B-equivalent broken variant
  (clamp removed). Fails for real: `0 verified, 2 errors`, exit code 4
  (not 1 - confirms the exit-code finding from the prior day's
  toolchain research, now exercised on the actual dosage spec).
- **`run_verify_dafny.py` / `run_verify_dafny_broken.py`** - capture
  runners mirroring `run_verify.py` exactly: subprocess `dafny verify`,
  commit verbatim stdout+stderr and a run manifest (tool, tool_version,
  command, exit_code, started_utc, target). Both run for real, producing
  genuine committed captures - `raw_dafny_output.txt`,
  `run_manifest_dafny.json`, `raw_dafny_output_broken.txt`,
  `run_manifest_dafny_broken.json`. No fabricated output anywhere.
- **`evidence/dafny_adapter.py::parse_dafny_capture`** - the false-zero
  guard, sharpened beyond the originally-planned substring floor.
  Parses the verifier's own summary line via regex (`Dafny program
  verifier finished with (\d+) verified, (\d+) errors?`) and checks the
  parsed error count - never a blind `"0 errors" in raw_output`
  substring match, which a printed error message could coincidentally
  contain. Refuses, in order: nonzero exit code (cheapest, checked
  first); no summary line found (a crash, timeout, or a `dafny audit`-
  style "did not attempt verification" message must not be silently
  treated as success just because exit_code happens to be 0); nonzero
  parsed error count. `evidence/model.py` gained
  `verifier_completion_status: Optional[str] = None` on
  `VerificationResult` (purely additive).
- **`tests/test_dafny_adapter.py`** - six tests, all passing. One found
  and fixed an incorrect test expectation during writing: the real
  broken capture's `exit_code=4` triggers the exit-code refusal before
  the summary line is ever parsed, so
  `test_refuses_real_committed_broken_capture` was corrected to expect
  `"does not report a clean pass"` (not a summary-line error match).
  The load-bearing regression,
  `test_false_zero_guard_is_not_fooled_by_a_substring_trap`, constructs
  raw output containing the literal substring `"0 errors"` in an
  unrelated sentence plus a real summary line reporting `3 verified, 2
  errors`, and confirms the parser correctly refuses where a blind
  substring check would have wrongly passed. A sixth test,
  `test_producing_a_proven_result_does_not_reopen_the_matrix_gate`,
  builds a fake matrix row from this adapter's real `Strength.PROVEN`
  output and confirms `assert_no_realized_proven`
  (`evidence/render/matrix_variants.py`) still hard-blocks it.
- **Explicitly not done, and not this module's job:** `dafny_adapter.py`
  is not called from `build_matrix()`, any `generate_matrix_*.py`
  script, or the CLI. Wiring a Dafny-sourced PROVEN result into the
  matrix pipeline is Gate C2's job by name (the PROVEN-exclusivity
  migration), still unbuilt.
- Full suite re-run after the build (47 passed) and the full
  `generate_artifacts.py` pipeline re-run, confirming zero observable
  change to existing committed matrix artifacts beyond `generated_utc`
  timestamps.

## 2026-07-06 — SessionStart hook: make the Dafny/Python toolchain reproducible

The toolchain research below only held for this session's container.
Requested directly: set it up so a future session doesn't have to redo
it from scratch.

- Added `.claude/hooks/session-start.sh` (registered in
  `.claude/settings.json`, synchronous mode): installs the Python deps
  (`crosshair-tool`, `jsonschema`, `pyyaml`, `pytest` - per README's
  "Running it") and the .NET/Dafny toolchain (`dotnet-sdk-8.0` via apt,
  then `dotnet tool install --global dafny --version 4.11.0` via NuGet).
- **Dafny is pinned explicitly to 4.11.0**, not "latest" - the exact
  version this session verified the false-zero note, exit-code
  behavior, and the vacuous-precondition risk against. An unpinned
  install could silently pick up a different Dafny version with
  different output conventions in a future session, undermining
  everything just verified. Matches the `crosshair-tool 0.0.107`
  pinning discipline already established for CrossHair.
- Idempotent: checks `command -v dotnet` / the installed Dafny version
  before doing any apt or dotnet work, so a warm container (already
  provisioned) skips straight through.
- **Validated, not assumed:** ran the hook directly
  (`CLAUDE_CODE_REMOTE=true ./.claude/hooks/session-start.sh`) - exit 0,
  ~1.4s on the already-provisioned path (this session), correctly
  skipped reinstalling. Confirmed `dafny --version` resolves to
  `4.11.0` via the hook's `$CLAUDE_ENV_FILE` PATH export, then ran the
  full test suite (41 passed) and one targeted test file individually,
  both immediately after sourcing that same env file - the same PATH a
  fresh session would inherit.
- No linter is configured in this repository (no `.flake8` / `ruff.toml`
  / CI workflow found) - that validation step from the skill's workflow
  doesn't apply here; noted rather than skipped silently.
- Not yet re-validated from a genuinely cold container (this session
  already had dotnet/Dafny installed from the prior research) - the
  from-scratch apt+dotnet-tool install path was exercised manually
  earlier this session and confirmed to work; the hook runs the
  identical commands.

## 2026-07-06 — Phase C Gate C1: Dafny toolchain blocker resolved (modern Dafny obtained)

Requested directly: research whether a modern Dafny is obtainable rather
than settling for the ancient apt package or asking for an
under-informed decision.

- **GitHub confirmed genuinely blocked, not assumed.** The proxy's own
  status endpoint (`curl $HTTPS_PROXY/__agentproxy/status`) and its
  README are explicit: 403/407 is an organization egress-policy denial -
  "do not retry or route around it." No workaround attempted.
- **Two already-permitted channels turned out to be enough.**
  `api.nuget.org` -> 200. `dot.net` / `dotnet.microsoft.com` -> normal
  redirects. apt has `dotnet-sdk-8.0` directly (Ubuntu's own package,
  not a Microsoft add-on repo) - installed cleanly as 8.0.128 after
  `apt-get update` refreshed a stale index (it had been pointing at a
  version no longer on the mirror).
- **`dotnet tool install --global dafny`** pulled from NuGet - zero
  GitHub involvement anywhere in the chain. Result: **Dafny 4.11.0**
  (full version `4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2`), a
  real current release, not the `2.3.0+dfsg-0.1` Mono-based package apt
  offers directly.
- **Verified against the running binary, three real checks, not
  documentation:**
  1. Clean pass on a valid clamping method: `Dafny program verifier
     finished with 1 verified, 0 errors`, exit 0 - exact match to the
     false-zero note already in `evidence/model.py`.
  2. Broken method: per-line error blocks + `0 verified, 2 errors`,
     **exit code 4** - new finding, Dafny's exit codes aren't a simple
     0/1 pair the way CrossHair's are.
  3. An unsatisfiable precondition (`x > 0 && x < 0`) against an
     obviously-false postcondition verified clean - confirms Gate C3's
     vacuous-precondition vulnerability is real and reproducible on this
     binary, not speculative.
- **Checked whether `dafny audit` (new in 4.x) makes the Z3-based
  mitigation unnecessary - it doesn't.** Ran it against the vacuous
  case: `0 findings`. Its actual scope (per its own help text) is
  un-annotated assumes/axioms/non-determinism/unverified externs, not
  general precondition satisfiability. Confirmed the originally-planned
  mitigation is still necessary and technically feasible:
  `z3.Solver()` correctly returns `unsat` for the contradictory
  precondition and `sat` for a real one.
- **Net effect: no alteration to the Gate C1-C3 plan.** If anything it's
  on firmer ground than when written. One concrete addition carried
  into Gate C1: capture the exit code as-is, don't assume a specific
  nonzero value on failure.
- **Not done:** no capture runner, no real Dafny spec for `dosage.py`,
  nothing committed to the repository - this was toolchain research
  only, per what was asked. The probe `.dfy` files live only in the
  scratch directory.
- Documentation updated: `KNOWN_LIMITATIONS.md` (Gate C1 row + full
  detail section), roadmap doc (environment-check section + closing
  summary), `SYSTEM_BLUEPRINT.md`, `README.md`.

## 2026-07-06 — Phase C planning: gate-sequenced plan, real environment check

Requested directly ("Move on to Phase C planning") right after Phase
B's gate ledger closed. Planning only - no Phase C code written.

- **Environment check done first**, same discipline as every prior
  toolchain decision in this repo: `z3 --version` -> 4.16.0, and
  `python3 -c "import z3"` succeeds - usable directly. `dafny` is not on
  PATH. `apt-cache show dafny` finds a package, but it's
  `2.3.0+dfsg-0.1` - Ubuntu universe, roughly 2015-era, depending on
  Mono (`mono-mcs`, `mono-runtime`), not the modern .NET-based Dafny
  (4.x) the false-zero note in `evidence/model.py` is written against.
  `dotnet` isn't installed; a direct GitHub release fetch 403'd through
  the environment's proxy. Recorded as a real, named blocker
  (`KNOWN_LIMITATIONS.md`) rather than assumed away or silently deferred
  - mirrors the `crosshair-tool 0.0.107` pinning precedent from Gate 3.
- **Restructured** `payloadguard-evidence-roadmap-phaseB-to-C.md`'s
  Phase C section from a flat two-mechanism sketch into six sequenced
  gates (C1-C6), each with scope, dependencies, and a suggested build
  order:
  - C1: Dafny adapter capture + minimal false-zero guard (foundation).
  - C2: PROVEN's exclusivity migration - sequenced immediately after C1,
    before any real spec exists, since this is the highest-consequence
    change in Phase C (a bug here would let PROVEN leak onto un-proven
    evidence). Recommended it get ratified-ruling-level review, like
    R1/R2 did.
  - C3: output-parsing hardening - three of four vulnerability vectors
    scoped (vacuous preconditions via Z3 satisfiability check, weak
    postconditions as a best-effort pattern check, timeout/resource
    masking via `verifier_completion_status`); the fourth
    (specification stripping) named BLOCKED - the source material
    describing it was cut off before this session had it in full, so
    it's recorded as needing a follow-up read, not guessed at.
  - C4: Spec-Testing Proofs, alongside whichever spec C1 produces first.
  - C5: mutation testing (MutDafny-style, six operators) - flagged as
    the largest single piece, recommended as its own sub-plan once C1-C2
    are stable rather than attempted in one pass.
  - C6: NL-dialogue confirmation - a process control with no technical
    dependency on the others, recommended adopted immediately rather
    than deferred.
- **Also recorded in `KNOWN_LIMITATIONS.md`** as two new blocked/named
  rows (Dafny toolchain decision; C3's fourth vector) so the live gate
  ledger surfaces them, not just the roadmap doc.
- `SYSTEM_BLUEPRINT.md` and `README.md` updated: Phase B marked
  COMPLETE (gate ledger fully closed); Phase C marked "planning," with
  the environment findings summarized.
- No code changes this session - planning only, as requested.

## 2026-07-06 — Gate 5 fully resolved: concrete-only fixture now constructible

Closed the last open item from the original six-gate ledger. Requested
directly ("concrete fix gate 5") right after Gate 2 completed.

- **Root cause:** `_bind_self_describing` (variant C's binding strategy,
  `evidence/render/matrix_variants.py`) bound a symbolic record to
  *every* requirement unconditionally, regardless of what it declared -
  a leftover from before metadata.c.yaml carried `evidence` declarations
  at all. This made a concrete-only requirement structurally impossible:
  it would always show up in the symbolic artifact too.
- **Fix:** `_bind_self_describing` now checks each requirement's
  declared `evidence` list before binding symbolic evidence - a
  requirement declaring only `concrete_test` entries (no `crosshair`
  entry) gets no symbolic record. When `evidence` is absent entirely,
  the original unconditional behavior is preserved for backward
  compatibility - the existing symbolic-only fixture relies on exactly
  this fallback path and needed no changes. Concrete binding is
  untouched either way - stays fully self-describing via
  `concrete_results.json`'s own `requirement_id`, per Gate 4's decision.
- **No effect on committed data:** every real requirement in
  `metadata.c.yaml` declares `crosshair` (added when Gate 4's asymmetry
  was closed), so this changes nothing observable - confirmed by
  regenerating and diffing (differs only by `generated_utc`).
- **Proven, not assumed:** `tests/test_single_evidence_type.py` gained a
  concrete-only fixture (a requirement declaring
  `evidence: [{method: concrete_test, test_id: ...}]`, no `crosshair`
  entry) alongside the existing symbolic-only one - confirmed to appear
  in exactly the concrete artifact and not at all in the symbolic one,
  the property that was previously impossible. 4 tests total (2
  fixtures × schema validation + binding behavior). Full suite: 41
  passed (39 prior + 2 new). Full pipeline re-run independently.
- Documentation updated: `KNOWN_LIMITATIONS.md` (new dedicated Gate 5
  section, ledger table updated to FULLY RESOLVED), `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc (new Gate 5 section, Gate 4's stale
  "constructibility note still holds" corrected, closing summary fixed).
- **Gate 5 is now fully resolved.** Combined with Gate 2's completion,
  every gate in the original ledger is closed, decided, or resolved -
  nothing structural remains open in Phase B's gate work; only Phase C
  (Dafny/Z3 adapters) is ahead.

## 2026-07-06 — Gate 2 build, Phase 7: Step 4 (delete the fallback) — Gate 2 COMPLETE

Requested explicitly, now that the CLI had landed and the cutover had
run stable through multiple independent verification passes.

- **Deleted:** `build_matrix_variant_a`, `build_matrix_variant_b`,
  `build_matrix_variant_c` from `evidence/render/matrix_variants.py`.
  Their shared markdown renderers (`_markdown_variant_a/b/c`) and other
  helpers stayed - `build_matrix()` already used those, not the deleted
  top-level functions.
- **Deleted:** `tests/test_binder_equivalence.py`. Its entire purpose
  was proving the old functions' output equals `build_matrix()`'s
  output - moot once the old functions don't exist.
- **Migrated, not deleted:** `tests/test_single_evidence_type.py` (Gate
  5's fixture test) was the one other place in the suite calling
  `build_matrix_variant_c` directly - updated to call
  `build_matrix("c-symbolic"/"c-concrete", ...)` instead. Confirmed
  still passing (2/2) before moving on.
- **Comments updated, not left stale:** the module-level banner in
  `matrix_variants.py` and the header comments in `generate_matrix_a/b/c.py`
  that described the now-gone fallback were rewritten to stop
  referencing it, rather than left describing something that no longer
  exists.
- **Verified after deletion, not just before it:** full suite (39
  passed - 44 minus the 5 deleted equivalence tests), full pipeline
  re-run (every regenerated artifact still differs only by
  `generated_utc`), and the CLI independently re-checked against a
  committed artifact post-deletion.
- **Corrected an overclaim while updating the roadmap doc:** a first
  draft of the "what's done" summary said Gate 5's concrete-only-fixture
  limitation was now closed by Gate 2's completion. Checked before
  committing: `build_matrix()`'s `_bind_self_describing` strategy for
  variant C is a literal extraction of the original C builder's
  logic - it still binds a symbolic record to every requirement
  unconditionally, unchanged by the refactor. Gate 5 stays resolved for
  the constructible half only; fixed before it went in the doc.
- Documentation updated: `KNOWN_LIMITATIONS.md` (Gate 2 marked
  COMPLETE), `SYSTEM_BLUEPRINT.md`, `README.md`, roadmap doc (Gate 2's
  heading, Gate 4's status, the closing summary).
- **Gate 2 is now structurally complete** - CONFLICT rule (both types),
  the vocabulary-agnostic binder, and the CLI are all built, verified,
  and documented. The only open item in Gate 2's scope was ever its own
  definition, and that's ratified. Git history holds the deleted
  fallback and test if ever needed again.

## 2026-07-06 — Gate 2 build, Phase 6: CLI (built ahead of Step 4, at Steven's direction)

Steven asked to hold off deleting the Step 2 fallback functions and get
the CLI done first - so the fallback stays available while new
capability is still landing, rather than being removed before anything
else changes.

- **Built:** `evidence/cli.py` - `python -m evidence.cli build --variant
  {a|b|c-symbolic|c-concrete} --metadata PATH --manifest PATH --concrete
  PATH [--schema PATH] [--out-json PATH] [--out-md PATH]`. Wraps
  `build_matrix()` with every input as an argument instead of the
  hardcoded `examples/dosage_calculator` paths the generator scripts use
  - the genuinely vocabulary-agnostic surface Gate 2 was named for: this
  can build a matrix for a different device's evidence set matching one
  of the four schema shapes, not just the worked example.
  `tool_versions` is now keyed by the manifest's own declared `tool`
  field rather than a hardcoded `"crosshair"` string, so a future
  Dafny/Z3 manifest won't need this CLI changed.
- **Two real bugs caught and fixed while building it, not left in:**
  1. An uncaught `jsonschema.ValidationError` printed via `str(e)` dumps
     the *entire schema* on every validation failure - useless noise for
     a CLI user. Fixed to use `ValidationError.message`, the short
     human-readable line.
  2. Omitting both `--out-json` and `--out-md` printed the JSON *and*
     the markdown concatenated to stdout, producing invalid combined
     output (caught by `test_cli_prints_to_stdout_when_no_output_path_given`
     failing with a `JSONDecodeError`). Fixed: markdown only ever goes
     where `--out-md` explicitly says to, never to stdout.
- **Proven, not assumed:** `tests/test_cli.py` (10 tests) drives the CLI
  via subprocess (the way a real user would invoke it) for all four
  variants and asserts byte-identical output (timestamp aside) to the
  corresponding committed artifact, plus both Tier-1 error paths (schema
  validation, CONFLICT Type 1 - confirmed to fire through the CLI path
  too) and both output modes (file, stdout). Full pipeline independently
  re-run to confirm the CLI's addition changed nothing about the
  existing generator scripts. Suite: 44 passed (34 prior + 10 new).
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md` (including a new CLI usage example in "Running it"),
  roadmap doc. Only Step 4 (delete the Step 2 fallback once stable)
  remains for Gate 2's binder work.

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
