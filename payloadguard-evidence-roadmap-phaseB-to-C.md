# PayloadGuard Evidence Layer — Roadmap: Phase B → Phase C

Updated 2026-07-07: Phase B's gate ledger is fully closed (Gates 1–6 all
resolved, decided, or complete — see below), and Phase C is restructured
from a two-mechanism sketch into a gate-sequenced plan (Gates C1–C6)
mirroring how Phase B was actually run. Gate C1's Dafny toolchain
blocker — resolved 2026-07-06: modern Dafny 4.11.0 obtained via NuGet
(`dotnet tool install --global dafny`), no GitHub involvement, verified
against the real binary. **Gate C1 itself is built:** a real Dafny spec
for the dosage kernel, a capture runner pair, and
`evidence/dafny_adapter.py`'s false-zero-guard parser, with a committed
regression test proving the guard resists a substring trap. **Gate C2
is also now built (2026-07-07):** ruling R3 supersedes R2 —
`assert_no_realized_proven` permits PROVEN only for `method == "dafny"`
records with `verifier_completion_status == "completed"`; every other
method stays permanently excluded, checked explicitly (not by omission)
in 8 new tests. **Gate C3 is now built for 3 of its 4 named vectors:**
`evidence/dafny_spec_lint.py` adds a real Z3-based vacuous-precondition
check (vector 1, proven against a real committed Dafny fixture that
verifies clean despite an unsatisfiable precondition) and a best-effort
weak-postcondition heuristic (vector 2); `evidence/dafny_adapter.py`'s
summary-line parser is hardened (vector 3) after a real finding on the
installed binary — a resource-starved run can report `"0 errors"`
alongside an `"N out of resource"` marker. Vector 4 (specification
stripping) stays BLOCKED, named. **Gate C4 (Spec-Testing Proofs) is also
now built (2026-07-07), and found a real gap on its first use:**
`dosage.dfy`'s original postcondition only bounded `dose`, never pinned
it to the actual clamped value — confirmed by a Dafny lemma that failed
to prove a wrong candidate value impossible. Fixed for real (an
`ExpectedDose` function + a pinning ensures clause, re-verified clean,
real capture re-run to match); the original preserved as
`dosage_underconstrained.dfy`; two STP suites mechanically prove both
directions. **Gate 2/C2-C4 wiring is also now built (2026-07-07): the
first real Dafny-sourced PROVEN evidence to reach a live matrix row.**
`traceability_matrix.formal.json` (variant C's third partition, Gate 5's
dual-matrix pattern extended) binds real `dosage.dfy` evidence to
REQ-GIP-1-4-12/REQ-GIP-1-8-1, gated inside the binder by Z3 precondition
satisfiability and the false-zero guard. Built for variant C first, then
**extended to variants A and B the same day** ("go ahead and extend
variant A and B now"): `metadata.a.yaml`'s evidence list and
`metadata.b.yaml`'s new `.formal-N` shadow rows declare the same real
evidence; the CLI gained `--dafny-captures` (required once A/B declared
it); the fact-equality gate's intent comparison became subset-based to
accommodate `formal.json` permanently lacking an opinion about
REQ-DOSE-003. Both requirements' `intent_ok` is now `True` in EVERY
variant artifact — the temporary A/B divergence tracked when C landed
first is closed, and its carve-out mechanism retired — see below.
**Gate C6 (NL-dialogue confirmation) is also now built and signed off
(2026-07-07):** `evidence/dafny_nl_summary.py` mechanically summarizes a
Dafny method's requires/ensures clauses in plain English (verbatim clause
plus a best-effort gloss, citations pulled from trailing `// REQ-ID`
comments), cross-checked by content against `dafny_spec_lint`'s canonical
extractor and refusing on any multi-line clause it can't safely associate
a citation with — a real bug in that refusal check (comparing counts
instead of content) was self-caught before the test suite was written.
The gate's actual deliverable — a recorded human decision, not the code —
is `examples/dosage_calculator/nl_confirmation_dosage_dfy.md`: Steven
confirmed the generated summary for `CalculateHourlyDose` ("it's good for
the spec as is") and flagged a next-phase item (spec adaptation plus an
explanation of downstream analysis by different software, for a
regulatory submission) as separate follow-up work, out of scope for this
gate.

**Gate C5 (mutation testing) is now built for v1 scope (2026-07-07)**,
same day as its own scoping session, on direct instruction ("build it and
be careful with Dafny... we can consider floating points later, it's a
known but solvable issue"): `evidence/dafny_mutate.py` generates
ROR/LOR/AOR/COI mutants against `dosage.dfy`'s requires/ensures clauses;
`examples/dosage_calculator/run_mutation_suite.py` real-verifies every
one. Initial real run: 39 mutants, 29 killed, 4 filtered as statically
trivial, **2 survived** (a real, understood looseness in REQ-GIP-1-8-1's
postcondition at the `infusionRateMlPerHr == 0.0` boundary — reported to
Steven for a decision, not silently changed in a spec he already signed
off on in Gate C6), **4 unclassifiable** (a real gap in the mutation
engine, not the spec: mutating one side of a chained comparison to a
descending operator produces a Dafny parse error, not a semantic test).
**Decision, same day: "go ahead and tighten REQ-GIP-1-8-1 to `>`."**
`dosage.dfy` changed, re-verified clean (`2 verified, 0 errors`,
unchanged), mutation suite re-run in full: **zero survivors remain** —
the two former survivor mutations are now correctly recognized as
statically trivial before Dafny is even invoked, itself a clean
confirmation the boundary is now tight. AOR/SOR/HOR stay out of v1
scope, checked not assumed. Full detail below.

## Where we are

- Phase A closed (R1–R3).
- Gate 1 (artifact generation) — clean pass. Fact-equality holds (7
  facts, consistent across A/B/C-split renders). Two defects found and
  fixed: the Notes-column cross-evidence-type leak/duplication, and
  REQ-GIP-1-4-12's evidence not matching its "shall trigger an alarm"
  text.
- Gate 5 (single-evidence-type fixture) — fully resolved 2026-07-06: the
  concrete-only case that was blocked (variant C bound symbolic evidence
  unconditionally) is now constructible, see below.
- Gate 6 (FRN) — resolved, see below.
- Gate 2 (CONFLICT rule + vocabulary-agnostic binder + CLI) — COMPLETE,
  see below.
- Phase C Gate C1 (Dafny adapter) — BUILT 2026-07-07: real spec, capture
  runner, false-zero-guard parser, regression-tested. See below.
- Phase C Gate C2 (PROVEN exclusivity migration) — BUILT 2026-07-07:
  ruling R3 supersedes R2, 8 new tests.
- Phase C Gate C3 (Dafny output-parsing hardening) — BUILT 2026-07-07 for
  vectors 1–3 (Z3 vacuous-precondition check, weak-postcondition
  heuristic, hardened summary-line parser after a real "out of resource"
  finding); vector 4 (specification stripping) stays BLOCKED, named.
- Phase C Gate C4 (Spec-Testing Proofs) — BUILT 2026-07-07: found and
  fixed a real gap in dosage.dfy's postcondition (bounds-only, never
  pinned the dose value); two STP suites prove both directions for real.
- Gate 2/C2-C4 wiring — BUILT 2026-07-07: `traceability_matrix.formal.json`
  (variant C's third partition) carries this repository's first-ever
  real, rendered PROVEN rows, gated by Z3 + the false-zero guard inside
  the binder. Variants A/B deliberately deferred - a named, tracked
  divergence, not silently permitted. See below.
- Phase C Gate C6 (NL-dialogue confirmation) — BUILT and SIGNED OFF
  2026-07-07: `evidence/dafny_nl_summary.py` generates the plain-English
  summary; `examples/dosage_calculator/nl_confirmation_dosage_dfy.md`
  records Steven's sign-off on it for `dosage.dfy::CalculateHourlyDose`.
  See below.
- Phase C Gate C5 (mutation testing) — BUILT for v1 scope 2026-07-07:
  `evidence/dafny_mutate.py` + `run_mutation_suite.py`. 39 mutants
  against `dosage.dfy::CalculateHourlyDose` found 2 real REQ-GIP-1-8-1
  survivors, reported then FIXED same day (tightened `>=` to `>` on
  Steven's decision) — zero survivors remain after re-run (29 killed, 6
  filtered static, 4 unclassifiable — a real, unrelated mutation-engine
  gap: chain-direction parse errors). AOR/SOR/HOR out of v1 scope,
  checked not assumed. See below.

## Guiding principle (unchanged)

Open questions get resolved at the gate where they're first encountered,
with the resolution documented inline — not batched and left for later.
If a gate can't be resolved when reached, name it explicitly as blocked
and why.

---

## Gate 2 — CONFLICT rule + binder + CLI: COMPLETE

Was not defined anywhere in the Blueprint or SYSTEM_BLUEPRINT.md beyond a
to-do mention — correctly left unresolved rather than inferred, until
tested against concrete cases and ratified.

**Definition, two sub-types sharing one precondition** (full text and
worked test cases in `KNOWN_LIMITATIONS.md`): CONFLICT only applies
between two claims about the *same* `(requirement, scope)` **and** the
same underlying verification act — never between two legitimately
different evidence types bound to one requirement.
- **Type 1 (identity mismatch):** a top-down ALM-authored contract claims
  "REQ-X is verified at file F, method M" and the bottom-up
  source-embedded assertion says a different file/method/hash. This is
  Gate 4's exact cross-check trigger.
- **Type 2 (outcome mismatch):** two claims agree on target identity but
  disagree on what that identical run produced — added after the
  original single-test-case draft, because CrossHair's own documented
  model-fidelity non-determinism (see Gate 3, and the Sample C /
  overflow-probe exhibits) means the same invocation really can produce
  different results, and the original definition had no way to catch
  that if it ever happened twice for the same target.

REQ-GIP-1-4-12's kernel_scope vs. system_scope split (one evidenced, one
an explicit GAP) remains the negative case — not a conflict, a documented
absence, because there's no second claim to disagree with.

**Status:** definition ratified by Steven; **both types built
2026-07-06** (`evidence/conflict.py`, wired into `generate_artifacts.py`
as stages 3–4, `tests/test_conflict_check.py` — 11 tests, all three
ratified cases covered across all three metadata shapes, 0 conflicts on
the real committed dataset). Variant C's declared-binding asymmetry
(Gate 4) is closed: `metadata.c.yaml` now carries the same top-down
`evidence` declarations as variant A, for cross-checking only — C's
actual binding stays evidence-store-carried, confirmed unchanged by a
byte-identical regeneration diff (timestamp aside).

**Vocabulary-agnostic binder — COMPLETE (Steps 1 through 4, plus the CLI).**
`evidence/render/matrix_variants.py` gained `build_matrix()`: a literal
extraction of all three existing variants' binding/rendering logic into
named, reusable functions, dispatched through one declarative table
instead of three top-level functions. Proven byte-identical (dict AND
JSON-string equality) to the original `build_matrix_variant_a/b/c` over
real committed data (`tests/test_binder_equivalence.py`, 5 tests). Step
2: `generate_matrix_a.py` / `_b.py` / `_c.py` now call `build_matrix()`
instead of the original functions — Steven approved with an explicit
request to keep a fallback available, so `build_matrix_variant_a/b/c`
are deliberately kept in place, unused, rather than deleted in the same
step (one-line revert per generator, or a plain `git revert`, if a
problem ever surfaces). Step 3: CONFLICT Type 1 is now folded into
`build_matrix()` itself — checked on every call, not just inside the
full pipeline, closing a real gap (previously running `generate_matrix_a.py`
alone would have bypassed it entirely). Type 2 was deliberately NOT
folded in: it compares raw manifests across the whole dataset, not any
single variant's binding, so it has no per-variant home and correctly
stays a standalone stage, the same way fact-equality does. The frozen
base matrix (never calling `build_matrix()`) keeps its own narrower
explicit check. Verified at every step, not assumed: the full pipeline
was re-run end to end after each change and every regenerated artifact
diffed against the pre-cutover committed versions — differs only by
timestamp throughout.

**CLI — built ahead of Step 4, at Steven's explicit direction** ("get
the CLI done first" before deleting the Step 2 fallback). `evidence/cli.py`
(`python -m evidence.cli build`) wraps `build_matrix()` with metadata/
manifest/concrete/schema paths as arguments instead of hardcoding
`examples/dosage_calculator` — the genuinely vocabulary-agnostic
surface Gate 2 was named for. tool_versions is now keyed by the
manifest's own declared tool name rather than a hardcoded `"crosshair"`
string. Two real bugs were caught and fixed while building it: an
uncaught `jsonschema.ValidationError` dumped the entire schema on a
validation failure (fixed to use `.message`), and omitting both output
paths printed JSON and markdown concatenated to stdout as invalid
combined output (fixed so markdown only ever goes where `--out-md`
explicitly says to). `tests/test_cli.py` (10 tests) drives the CLI via
subprocess for all four variants and proves byte-identical output to
the committed artifacts, plus both error paths. Suite: 44 passed.

**Step 4 — done.** Requested last, deliberately after the CLI landed:
`build_matrix_variant_a/b/c` deleted from `matrix_variants.py` (their
shared markdown renderers stayed — `build_matrix()` already used those);
`tests/test_binder_equivalence.py` deleted too, since its entire purpose
(proving old-function output equals `build_matrix()` output) is moot
once the old functions don't exist. `tests/test_single_evidence_type.py`
(Gate 5's fixture test) was the one other place calling
`build_matrix_variant_c` directly — migrated to `build_matrix()`.
Verified after deletion, not just before it: full suite (39 passed — 44
minus the 5 deleted equivalence tests), full pipeline re-run (every
regenerated artifact still differs only by timestamp), and the CLI
re-checked independently against a committed artifact. Git history
holds the deleted functions and test if a fallback is ever needed again
— that was the entire point of the Step 2→3→CLI→4 ordering rather than
deleting immediately after the cutover.

**Gate 2 is now structurally complete.** Nothing remains in its binder
work; the only item anywhere in Gate 2's scope was the CONFLICT rule's
own definition, already ratified.

## Gate 3 — Bounds enforcement via CrossHair API: DECIDED, stay-CLI (empirically tested, 2026-07-05)

**Result:** seed override tested for real, not just read. The verification
script itself had three bugs that only surfaced by actually running it —
worth recording, since it's the same lesson this whole gate has been
teaching, now caught in my own "corrected" output:

1. The documented constructor `AnalysisOptions(max_iterations=...,
   per_condition_timeout=...)` throws `TypeError` on the installed
   0.0.107 — `analyze_function` actually wants `AnalysisOptionSet`.
2. Importing from bare `crosshair.core` raises
   `CrossHairInternal("Opcode patches haven't been loaded yet.")` —
   needs `crosshair.core_and_libs`.
3. The critical one: `analyze_function` only parses conditions into
   `Checkable` objects — it never runs the solver unless `.analyze()` is
   called on each one. The uncorrected script "passed" in under a second
   without ever actually invoking CrossHair. A script that runs without
   error is not the same as a script that tested anything.

**After fixing all three:** ran twice per seed, on two targets — the
clean kernel (no counterexample either way) and the broken variant
(which has real counterexamples). **Both seeds produced byte-identical
results, including identical counterexamples on the broken variant.**
The patch applies without error. It has no observed effect.

**Decision:** stay on CLI capture. `seed` is a confirmed hard
tool-version limitation — not "probably unfixable," empirically tested
and found to have no effect on solver behavior at 0.0.107.
`max_iterations` remains confirmed enforceable via the API, independent
of the seed question — that part of Gate 3 is solved and can be wired in
whenever it's useful.

**Status: closed.**

## Gate 4 — Binding authorship: DECIDED (option 3), mechanism BUILT via Gate 2

**Decision:** option 3 — both models, cross-checked, Tier-1 failure on
disagreement. Matches the cross-validation philosophy already built into
the four-variant design.

**Mechanism, built as Gate 2's CONFLICT Type 1** (`evidence/conflict.py`,
folded into `build_matrix()`): dual-authorship cross-checking via
verified code-location match —
- **Top-down contract:** the system/QA-authored master traceability
  config states "REQ-X is verified by the proof/test at file F, method
  M."
- **Bottom-up contract:** the source-embedded assertion (a decorator,
  structured comment, or in Dafny's case an `ensures`/`invariant` clause)
  states "this method verifies REQ-X."
- **Intersection check:** at generation time, extract both, and flag
  non-compliant if the physical file/method/hash doesn't match between
  them. This is exactly what Fable's bonus finding from Gate 5 flagged as
  missing — variant C's builder didn't verify evidence against the
  capture's actual target; the concrete-side check now runs (via
  `evidence/conflict.py`). C's concrete evidence *binding* stays
  evidence-store-carried by design (unchanged); the SYMBOLIC binding is
  no longer unconditional — see Gate 5.

**Status:** decision, mechanism, and build all done. `evidence/conflict.py`'s
`concrete_binding_conflicts` / `symbolic_binding_conflicts` implement the
intersection check for real, run inside `build_matrix()` on every call.

## Gate 5 — single-evidence-type fixture for variant C: FULLY RESOLVED (2026-07-06)

Originally resolved for the constructible half only: a symbolic-only
fixture (no `evidence` list declared) correctly appeared in exactly one
of variant C's two artifacts. Concrete-only was named as impossible —
`_bind_self_describing` bound a symbolic record to every requirement
unconditionally, regardless of what it declared, so nothing could ever
be concrete-only.

**Fix:** `_bind_self_describing` now checks each requirement's declared
`evidence` list before binding symbolic evidence — a requirement
declaring only `concrete_test` entries gets no symbolic record. When
`evidence` is absent entirely, the original unconditional behavior is
preserved (the existing symbolic-only fixture relies on exactly this
fallback, and still passes unchanged). Concrete binding is untouched —
still fully self-describing via `concrete_results.json`'s own
`requirement_id`, per Gate 4's decision for C.

No effect on committed data: every real requirement in `metadata.c.yaml`
declares `crosshair`, so nothing changed observably — confirmed by
regenerating and diffing (timestamp aside). `tests/test_single_evidence_type.py`
now proves both directions: symbolic-only and (new) concrete-only each
appear in exactly one artifact. Suite: 41 passed.

## Gate 6 — FRN: RESOLVED

`FRN` = FDA Product Code for "Infusion Pump" (21 CFR 880.5725). Within the
GIP taxonomy specifically, denotes general-purpose volumetric infusion
pumps (peristaltic mechanism, cassette-based administration set), distinct
from `All`. Resolved via NotebookLM's extraction of the full source PDF,
cross-checked against independent FDA-registry research landing on the
same code. Well-supported, not yet independently re-verified against the
raw Sec 2.4.1 text. Full trail in `sources/README.md`.

---

## Phase C — gate-sequenced plan (2026-07-06)

Restructured from a two-mechanism sketch into gates, mirroring how Phase
B was actually run: each gate has a scope, a dependency, and (where one
exists) a decision that has to land before building starts. Nothing
below is built yet — this is the plan, produced before any Phase C code,
per the same discipline Phase B used (design review before implementation,
verify against the real environment before assuming a tool works a
certain way).

### Environment check (done 2026-07-06; RESOLVED same day — modern Dafny obtained)

- **Z3 4.16.0 is present** — both the `z3` CLI and the `z3` Python
  bindings import cleanly (`import z3` succeeds). Usable directly for
  satisfiability-style checks (Gate C3) — confirmed working (see below).
- **Dafny was not installed**, and apt's only offering was
  `2.3.0+dfsg-0.1` — an Ubuntu-universe package from roughly 2015,
  Mono-based, not modern .NET. **Resolved by researching further rather
  than settling for it:** GitHub release downloads are genuinely blocked
  by egress policy (confirmed via the proxy's own status endpoint — a
  policy denial, not a config problem, so not routed around), but
  `api.nuget.org` is reachable and apt has `dotnet-sdk-8.0` directly
  (Ubuntu's own package). Installed the SDK, then ran
  `dotnet tool install --global dafny`, which pulled from NuGet — no
  GitHub involvement anywhere. Result: **Dafny 4.11.0**, a real current
  release.
- **Verified against the running binary, not documentation:** a clean
  pass on a valid clamping method produced exactly `Dafny program
  verifier finished with 1 verified, 0 errors`, exit 0 — matching
  `evidence/model.py`'s false-zero note precisely. A broken method
  produced per-line error blocks plus `0 verified, 2 errors`, **exit
  code 4** (not 1 — a real finding: Dafny's exit codes aren't a simple
  0/1 pair the way CrossHair's are). An unsatisfiable precondition
  (`x > 0 && x < 0`) against an obviously-false postcondition verified
  clean — confirming Gate C3's vector 1 is a real, reproducible risk on
  this binary, not speculative. `dafny audit` was checked against the
  same case and found nothing (`0 findings`) — it's scoped to
  un-annotated assumes/axioms/non-determinism, not general precondition
  satisfiability, so Gate C3's originally-planned Z3-based mitigation is
  still the right approach — confirmed technically feasible (`z3.Solver()`
  correctly returns `unsat`/`sat` for the contradictory/real cases
  respectively).
- **No alteration to the plan needed.** If anything the plan is on
  firmer ground than when it was written: the false-zero note holds
  exactly, the vacuous-precondition risk is empirically confirmed rather
  than assumed, and its mitigation is confirmed feasible with tools
  already present. One concrete addition to carry into Gate C1: capture
  the exit code as-is rather than assuming a specific nonzero value.
  Full findings: `KNOWN_LIMITATIONS.md`.
- **Not done yet:** this was toolchain research, not Gate C1 itself — no
  capture runner, no real Dafny spec for `dosage.py`, nothing committed
  to the repository. That's the next step.

### Gate C1 — Dafny adapter: capture + minimal false-zero guard — BUILT (2026-07-07)

- **Target decision made:** reused `dosage.py`'s existing contracts,
  translated to Dafny (`examples/dosage_calculator/dosage.dfy`), rather
  than forking a second worked example — keeps one through-line for the
  REQ-GIP-* citations. `weight_kg` is intentionally omitted (an unused
  precondition-only guard in the Python original). **REQ-DOSE-003 is
  explicitly excluded from the Dafny spec** — confirmed empirically that
  Dafny's `real` type is exact/arbitrary-precision with no IEEE
  overflow/infinity/NaN concept (`y := x / 0.0` on a `real` is itself a
  flagged verification error, not a silent `inf`), so "finite result
  under overflow" cannot be faithfully stated as a Dafny postcondition.
  Named as a deliberate scope exclusion, not a silent gap.
- Verifies clean against the real 4.11.0 binary: `Dafny program verifier
  finished with 1 verified, 0 errors`, exit 0.
  `examples/dosage_calculator/dosage_broken.dfy` (clamp removed) fails
  for real: `0 verified, 2 errors`, exit code 4 (confirms the exit-code
  finding from the toolchain research, now exercised on the actual spec).
- A capture runner pair mirroring `run_verify.py`'s discipline
  (`run_verify_dafny.py` / `run_verify_dafny_broken.py`): invoke Dafny as
  a subprocess, commit verbatim stdout+stderr, the exact command argv,
  exit code, and ISO-8601 UTC timestamp — no re-running evidence inside
  the generation pipeline, same as every existing capture. Both run for
  real, producing genuine committed captures (`raw_dafny_output*.txt`,
  `run_manifest_dafny*.json`).
- **Parser sharpened beyond the originally-planned floor:** rather than
  asserting the literal substring `"0 errors"` (the minimum bar named in
  `evidence/model.py`'s false-zero note), `evidence/dafny_adapter.py`
  parses the verifier's own summary line via regex
  (`Dafny program verifier finished with (\d+) verified, (\d+) errors?`)
  and checks the parsed error count — never a blind substring match. A
  committed regression test
  (`test_false_zero_guard_is_not_fooled_by_a_substring_trap`) constructs
  raw output containing the literal substring `"0 errors"` in an
  unrelated sentence plus a real summary line reporting `3 verified, 2
  errors`, and confirms the regex-based parser correctly refuses where a
  substring check would have wrongly passed. Refuses, in order: nonzero
  exit code (cheapest, checked first); no summary line found (a crash,
  timeout, or `dafny audit`-style "did not attempt verification" — must
  not be silently treated as success); nonzero parsed error count.
- `verifier_completion_status` added to `VerificationResult`
  (`evidence/model.py`) — purely additive, `"completed"` on success, only
  meaningful for adapter-produced results so far.
- Six tests in `tests/test_dafny_adapter.py`, including a belt-and-
  suspenders check that constructs a fake matrix row from this adapter's
  real `Strength.PROVEN` output and confirms
  `assert_no_realized_proven` still hard-blocks it — proving this
  adapter cannot itself reopen the PROVEN-exclusivity boundary.
- **Explicitly not done here:** `dafny_adapter.py` is not called from
  `build_matrix()`, any `generate_matrix_*.py` script, or the CLI. That
  wiring is Gate C2's job by name, not an incidental side effect of this
  build.

### Gate C2 — PROVEN's exclusivity migration — BUILT (2026-07-07)

The highest-consequence change in Phase C. Sequenced right after C1 as
planned, though by the time it was built, Gate C1's real spec already
existed — no retrofit was needed in practice because no binder had
wired a Dafny record into `build_matrix()` yet, so the structural
guarantee was never at risk of being violated by existing data.

- **The rule shipped exactly as specified above, ratified rather than
  altered:** `assert_no_realized_proven` (`evidence/render/matrix_variants.py`)
  previously hard-failed if ANY record anywhere claimed PROVEN, full
  stop. Ruling **R3** (in the R1/R2/R2c lineage) now permits PROVEN as a
  realized strength only when a record's `method == "dafny"` **and**
  its `verifier_completion_status == "completed"` — both conditions
  required, not just a matching method label. Every other method —
  `crosshair`, `concrete_test`, or a record with no method at all —
  remains permanently, unconditionally excluded, exactly as under R2.
- **Why both conditions, not just the method check:**
  `evidence/dafny_adapter.py::parse_dafny_capture` is already
  structurally incapable of returning PROVEN unless its own exit-code,
  summary-line, and false-zero checks all passed — so in the adapter's
  own output the two conditions are always true together. R3 checks
  both anyway, at the matrix boundary, as defense in depth against a
  future binder assembling a Dafny-shaped record by hand instead of
  through the adapter.
- **Both required tests built, plus more:** `tests/test_proven_exclusivity.py`
  (8 tests) — the positive case (a real Dafny PROVEN record, produced
  the same way Gate C1's adapter produces it, is accepted) and the
  negative case (CrossHair and concrete_test records forced to claim
  PROVEN are refused, checked explicitly with real fixtures, not
  inferred from the absence of a binder that would produce one), plus
  a missing-method case, two dafny-method-without-completed-status
  cases (defense in depth), the row-level-cell shape (variant B/C), and
  a regression confirming all four committed matrix artifacts still
  pass unchanged. `tests/test_structural_proven_check.py`'s existing
  corruption cases needed no changes — same error-message substring,
  same behavior for every method this rule doesn't touch.
- Full suite re-run: 55 passed (47 prior + 8 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change to any
  committed artifact beyond `generated_utc` timestamps — R3 has no
  effect on the live pipeline today, since no binder yet produces a
  dafny-method record.
- **Explicitly not done here:** no binder (`_bind_declared`,
  `_bind_shadow`, `_bind_self_describing`) was changed to actually
  assemble a Dafny-sourced record into a live matrix row. R3 makes that
  *possible* without violating the structural gate; it does not make it
  *happen*. That wiring belongs alongside Gate C4 (STPs, "alongside the
  first real spec") per the suggested build order below; trusting a
  live PROVEN claim in earnest still waits on Gate C3.

### Gate C3 — Dafny output-parsing hardening — BUILT for vectors 1–3 (2026-07-07); vector 4 BLOCKED

Four distinct failure modes were named, each with its own signature —
"0 errors" in the output is necessary but not sufficient. Three were
scopeable and are now built; the fourth remains blocked exactly as
before, no new source material surfaced.

- **Vacuous proofs from contradictory preconditions — BUILT.**
  `evidence/dafny_spec_lint.py::check_precondition_satisfiability`
  extracts a method's `requires` clauses and hands their conjunction to
  Z3 for a real satisfiability check, via a small, explicitly-scoped
  expression translator (booleans, comparisons incl. chaining,
  arithmetic, real/int/nat/bool) — quantifiers and anything else out of
  scope raise `SystemExit` rather than being mistranslated. **Proven
  against a real committed fixture, not a synthetic string only:**
  `examples/dosage_calculator/vacuous_precondition_probe.dfy` — Dafny
  4.11.0 verifies it clean (`1 verified, 0 errors`, exit 0) despite an
  unsatisfiable precondition (`x > 0 && x < 0`); the Z3 checker
  correctly reports `unsat` on the same method. A true-negative
  companion confirms the real dosage.dfy kernel's actual precondition is
  `sat`.
- **Weak postconditions — BUILT (heuristic, best-effort, as scoped).**
  `scan_weak_postconditions` flags `ensures` clauses using `==>` without
  a matching `<==>`, tested against a synthetic weak clause (flagged),
  the real dosage.dfy spec (zero warnings, true negative — its clauses
  use `<=`/`==`/`||`, never `==>`), and a `<==>` clause (not flagged).
  This is a lint for human review, not a proof — it cannot decide
  whether a bi-implication was actually *needed* for a given spec.
- **Timeout/resource-limit masking — BUILT, with a real finding.** A
  genuine empirical result on the installed Dafny 4.11.0 binary:
  `dafny verify --resource-limit=1` on the real, committed `dosage.dfy`
  spec produces `Dafny program verifier finished with 0 verified, 0
  errors, 1 out of resource` — an errors count of 0 on an incomplete
  run. Committed for real via `run_verify_dafny_resource_limited.py`.
  **Checked, not assumed:** the real captured `exit_code` is 4
  (nonzero), so Gate C1's exit-code check already refuses this capture —
  this vector does not silently bypass exit-code protection on this
  Dafny version. (An earlier session suspicion that exit_code was 0 here
  turned out to be a shell-piping artifact in this session's own
  probing — `$?` captured `tail`'s exit status, not `dafny`'s — caught
  and corrected before being reported as a finding.) Hardened anyway, as
  real defense in depth: `evidence/dafny_adapter.py`'s summary-line
  parser now refuses independently on `"out of resource"`/`"out of
  memory"`/`"timed out"` markers in the summary tail, and on more than
  one summary line in a capture (checked empirically that a normal
  multi-file `dafny verify` still emits exactly one aggregate summary
  line). Only `"out of resource"` was independently reproduced
  end-to-end; the sibling markers are the confirmed vocabulary from the
  same Boogie/Dafny code path (verified via UTF-16 string extraction
  from the installed `Boogie.ExecutionEngine.dll` / `DafnyDriver.dll`)
  but not independently forced to reproduce — named as such.
- **Specification stripping — still BLOCKED, named rather than
  dropped:** the source material describing this fourth vector was cut
  off before this session had it in full (an LLM-self-healing-loop
  scenario was referenced but not detailed). Needs a follow-up read of
  the original document before this vector can be scoped at all — per
  the standing discipline, not inferred from the name. No new
  information surfaced this session either.

**Test count:** 11 new tests in `tests/test_dafny_spec_lint.py` (vectors
1–2), 6 in `tests/test_dafny_timeout_masking.py` (vector 3) — 17 new,
full suite now 72 passed. Full `generate_artifacts.py` pipeline re-run:
zero observable change beyond `generated_utc` timestamps.

**Explicitly not done here:** neither the Z3 check nor the
weak-postcondition heuristic is invoked automatically anywhere in the
capture or generation pipeline — standalone, tested capabilities, same
scope discipline as Gate C1. Wiring them into the capture workflow so
every future Dafny spec gets both checks run as a matter of course is a
natural follow-up but wasn't asked for here.

### Gate C4 — Spec-Testing Proofs (STPs) — BUILT (2026-07-07), found and fixed a real gap

IronSpec's methodology: prove that specific, manually chosen input/output
pairs are correctly accepted or rejected *by the specification itself*,
independent of whether the implementation satisfies it. Direct,
mechanized fix for the exact class of bug Gate 1 found by hand
(REQ-GIP-1-4-12's spec/evidence not matching its text) — an STP would
have caught that the "alarm" spec only encoded clamping before any proof
was attempted. Applied to Gate C1's `dosage.dfy` — the only Dafny spec
that exists in this repo — it found the *same class of bug recurring*,
independently, on its first real application.

**The finding, confirmed mechanically, not by inspection:** the original
`CalculateHourlyDose` postcondition — `0.0 <= dose <= maxSafeDoseMgPerHr`
and `infusionRateMlPerHr >= 0.0 || dose == 0.0` — bounds `dose` and
forces it to `0` on reverse flow, but never relates it to the actual
product of rate and concentration otherwise. A Dafny lemma stating "for
these fixed inputs, if `dose` satisfies both ensures clauses, then `dose`
must equal the one correct clamped value" **failed to verify** — the
postcondition genuinely does not force it. A method that always returned
`0.0` for any non-negative-rate input would have satisfied the exact
same spec Gate C1 verified clean.

**The fix:** `dosage.dfy` gained `function ExpectedDose(concentrationMgPerMl,
infusionRateMlPerHr, maxSafeDoseMgPerHr): real` — the same three-way
clamping logic as the method body — and a new
`ensures dose == ExpectedDose(...)` clause pinning the output exactly.
The two original ensures clauses stay, unchanged, for direct
per-requirement traceability. Re-verified clean: `2 verified, 0 errors`
(the function plus the method — the count changed from Gate C1's
original `1 verified`). **The real committed capture was re-run
honestly, not patched:** `raw_dafny_output.txt` / `run_manifest_dafny.json`
now reflect the fixed spec; `tests/test_dafny_adapter.py`'s exact
`raw_status` assertion was updated to match, with a comment explaining
why.

**The preserved exhibit and the two-sided mechanized proof:**
`dosage_underconstrained.dfy` preserves the original weak spec
byte-for-byte (same rationale as `dosage_naive_widening.py`) — it still
verifies cleanly on its own (`1 verified, 0 errors`); the bug is a spec
weakness, not a verification failure. Two STP suites, each `include`-ing
the relevant spec rather than duplicating it, prove both directions for
real:
- `dosage_stp_suite.dfy` (`include "dosage.dfy"`): six lemmas across the
  three logical branches (normal in-range, ceiling-clamped, reverse-flow)
  — ACCEPT + REJECT pairs for the first two, ACCEPT-only for the third
  (never a gap — `infusionRateMlPerHr >= 0.0 || dose == 0.0` already
  pins `dose` to `0` there, even in the weak spec). All six verify:
  `10 verified, 0 errors`, exit 0.
- `dosage_stp_suite_against_underconstrained.dfy` (`include
  "dosage_underconstrained.dfy"`): the same two REJECT lemmas, run
  against the weak spec instead. Both **genuinely fail**: `0 verified,
  2 errors`, exit 4 — a real negative capture, not smoothed over, same
  discipline as `dosage_broken.dfy`. This is the mechanized proof the
  gap was real: the identical lemma succeeds against the fix and fails
  against the original.

**A mistake caught during this build, before committing:** an early
draft of the ceiling-clamped REJECT lemma used the raw unclamped product
(`500.0`) as the "wrong" value. That lemma verified even against the
**weak** spec — not because the weak spec pins the correct value, but
because `500.0` already violates the weak spec's own `0.0 <= dose <=
maxSafeDoseMgPerHr` bound directly, so excluding it proves nothing about
the real gap. Caught by checking the lemma's actual behavior against the
weak spec rather than assuming the chosen value was a good test;
corrected to `50.0` (in-bounds, still wrong) in both suites, with a
regression test guarding against silently reintroducing the weaker
value.

**Tests:** `tests/test_dafny_stp_suite.py`, 6 tests, checking the real
committed captures directly (not via `evidence.dafny_adapter.py`, since
an STP suite's capture is a proof about the spec's tightness, not a
requirement's verification evidence). Full suite: **78 passed** (72
prior + 6 new). Full `generate_artifacts.py` pipeline re-run: zero
observable change beyond `generated_utc` timestamps.

**Scope, as built (not expanded beyond what was asked):** every Dafny
spec written for Phase C gets a small STP suite alongside it, authored
by whoever writes the spec — this gate authored one STP suite for the
one spec that exists (`dosage.dfy`), not a generic STP-generation tool
or an automated gate that runs on every future spec. Neither STP suite
is wired into `build_matrix()` or any generator.

### Gate 2 / C2-C4 wiring — real Dafny evidence reaches a live matrix row — BUILT (2026-07-07)

Requested directly: "we need z3 integration and invocation in order to
reach PROVEN status, in concurrence with gate 5 extension." This is the
highest-stakes change to this repository's structural guarantees since
ruling R1 itself — the first time PROVEN would ever appear in a live
rendered row — so three design decisions were confirmed before building,
not guessed at:

1. **Scope: variant C only, for now** ("hmm. can we post hoc verify A
   and B after C variant is proven?"). Variants A and B are deliberately
   deferred, creating a real, temporary cross-variant divergence -
   named and tracked below, not silently permitted.
2. **The Z3 gate lives inside the binder itself** (`dafny_record()`),
   mirroring how `symbolic_record`/`concrete_record` already refuse on
   failed captures internally - not a separate pipeline stage.
3. **Metadata declares the dafny evidence explicitly**, consistent with
   Gate 4/5's existing declaration pattern, cross-checked by a new Gate
   2 CONFLICT Type 1 sub-check rather than bound unconditionally.

**What was built:** `metadata.schema.c.json` gained a `dafny` evidence
method (requiring `spec_target`/`dafny_method` together);
`metadata.c.yaml` declares it for REQ-GIP-1-4-12 and REQ-GIP-1-8-1 -
exactly the two requirements `intended_method: "PROVEN"` has named since
Phase A/B, and exactly the two `dosage.dfy` scopes itself to.
`evidence/conflict.py::dafny_binding_conflicts` adds the Type 1 check
(declared `spec_target` vs. the captured manifest's actual target),
correctly a no-op when `dafny_store is None` rather than merely falsy -
a symbolic/concrete build_matrix() call that never intends to bind dafny
evidence must not be penalized for metadata that also declares it for
the third view. `evidence/render/matrix_variants.py::dafny_record()` is
the wiring itself: gates PROVEN on Z3 precondition satisfiability (Gate
C3) AND `parse_dafny_capture`'s false-zero guard (Gate C1) before ever
constructing a record - `assert_no_realized_proven`'s ruling R3 still
independently re-checks both conditions at the matrix boundary
regardless. `_bind_self_describing`, `_shape_method_partitioned`,
`_VARIANT_SPECS`, and `build_matrix()` itself all gained the plumbing
for a new `"c-formal"` variant key and an optional `dafny_store`
parameter. `generate_matrix_c.py` now renders THREE artifacts
(`traceability_matrix.formal.json/.md` alongside symbolic/concrete),
assembling `dafny_store` from the real, already-committed Gate C1
capture - no re-running evidence inside the generation pipeline.

**The result:** `traceability_matrix.formal.json` has two real PROVEN
rows (REQ-GIP-1-4-12, REQ-GIP-1-8-1), both `verifier_completion_status:
"completed"`, both `intent_ok: true` for the first time since Phase A.

**The temporary variant A/B divergence, named and tracked:** since A/B
don't bind dafny evidence, their `intent_ok` for these two requirements
correctly stays `False` - a real divergence from the formal view's
`True`. The existing fact-equality gate
(`evidence/reconcile.py::run_gate`, `VARIANT_ARTIFACTS`) is deliberately
**unchanged** (the formal artifact isn't in that tuple), so the
pre-existing strict A==B==symbolic==concrete check keeps passing exactly
as before. A new, separate, narrowly-scoped check,
`run_formal_check`, verifies the formal view's divergence is EXACTLY the
expected one (`KNOWN_FORMAL_INTENT_DIVERGENCE = {"REQ-GIP-1-4-12",
"REQ-GIP-1-8-1"}`) and no other - any other requirement diverging, or
either named one diverging in the wrong direction, is still a hard
failure. This carve-out is meant to be temporary: removed and tightened
to plain equality once variant A/B's own dafny wiring lands.

**Tests:** `tests/test_dafny_wiring.py`, 15 tests. Full suite: **93
passed** (78 prior + 15 new). Full `generate_artifacts.py` pipeline
re-run end to end, including the new formal-view check: PASS, with the
structural PROVEN sweep now explicitly sweeping the formal artifact too.

**Explicitly not done in the variant-C-only build, done same day as a
follow-up (below):** variants A/B binding dafny evidence; the CLI
supporting a `"c-formal"` variant choice or a `dafny_store` argument.
**Still not done:** no generic tooling wires any future Dafny spec into
the matrix automatically - this built the one wiring path for the one
spec that exists.

#### Extended to variants A and B (2026-07-07)

Requested directly, same day: "go ahead and extend variant A and B
now." `metadata.a.yaml` declares the same dafny evidence in its
`evidence` list; `metadata.b.yaml` gained two new `.formal-N` shadow
pseudo-requirements (`REQ-GIP-1-4-12.formal-1`,
`REQ-GIP-1-8-1.formal-1`), distinguished from concrete shadows by a
`.dfy` implementation file extension rather than a new declared field.
`_bind_declared`/`_bind_shadow` gained the matching binder logic - both
refuse outright if dafny evidence is declared with no `dafny_store` at
all, unlike C's symbolic/concrete sub-views, since A/B have no
"legitimately excludes dafny" concept. `dafny_binding_conflicts` was
generalized via a new `_declared_dafny_bindings` generator (mirroring
how concrete evidence already unifies A/C's list and B's shadow rows)
to cover all three declaration shapes; `_declared_concrete_bindings` was
fixed to skip `.dfy`-suffixed shadow rows rather than mis-parsing them
as concrete test ids (a real bug this extension would otherwise have
introduced). `generate_matrix_c.py` now passes `dafny_store` to ALL
THREE of its `build_matrix()` calls, not just `"c-formal"` - necessary
so `c-symbolic`/`c-concrete`'s own intent computation matches A/B/formal
(their rendered rows are unaffected either way).

**The fact-equality gate itself needed two real changes.**
`VARIANT_ARTIFACTS` now includes `traceability_matrix.formal.json` as a
full fifth member - no longer carved out. The intent comparison changed
from strict dict equality to subset comparison: `formal.json`
*permanently* lacks an opinion about REQ-DOSE-003 (out of `dosage.dfy`'s
scope by design, not a temporary gap), so requiring it to match A's full
requirement set byte-for-byte was never going to hold once C was folded
in for real. The temporary `run_formal_check`/
`KNOWN_FORMAL_INTENT_DIVERGENCE` carve-out is retired, exactly as
promised when it was built.

**The CLI needed `--dafny-captures`, and this was not optional** - once
metadata.a.yaml/b.yaml declared dafny evidence, the CLI genuinely broke
without a way to supply a `dafny_store`. A small JSON index of *paths*
(not inlined file content), `dafny_captures_index.json`, is the real
committed index for the worked example. `"c-formal"` was also added to
the CLI's variant choices.

**The result:** every variant artifact - A, B, C-symbolic, C-concrete,
C-formal - now reports `intent_ok: true` for both requirements.
`run_gate()`'s facts count is 9, not 7. Full suite: **98 passed** (93
prior + updates). Full pipeline re-run end to end.

### Gate C5 — Mutation testing (MutDafny-style) — BUILT for v1 scope (2026-07-07)

**Purpose, stated precisely:** Gates C1/C4 prove `dosage.dfy`'s postconditions
hold. Neither proves those postconditions are *tight* — that each boundary
in them is actually load-bearing rather than incidental. A postcondition
that would still verify if a boundary were loosened isn't proving that
boundary at all; it just hasn't been asked to. Mutation testing asks that
question directly: weaken or perturb the spec in a small, specific way and
re-run the real verifier. If it still passes, that boundary was never
proven in the first place — a real finding, not a tooling gap, and it gets
named and reported exactly like Gate C4's spec gap was, not smoothed over.

**Build result summary (2026-07-07), full detail in `KNOWN_LIMITATIONS.md`:**
built same day as the scoping session below, on direct instruction
("build it and be careful with Dafny... we can consider floating points
later, it's a known but solvable issue" — read as: build ROR/LOR/COI on
clauses now, defer the AOR/division-by-zero risk named below). Initial
real run against `dosage.dfy::CalculateHourlyDose`: 39 mutants — 29
killed, 4 filtered as statically trivial, **2 survived**
(`infusionRateMlPerHr >= 0.0 || dose == 0.0` weakened to `!=` or `>` at
the first disjunct both still verify, because real multiplication by
exactly `0.0` already makes `dose == 0.0` hold at that boundary
regardless of the first disjunct's operator — a real, understood
REQ-GIP-1-8-1 postcondition looseness, **reported to Steven for a
decision, not silently changed** in a spec already signed off in Gate
C6), **4 unclassifiable** (mutating one side of the chained
`0.0 <= dose <= maxSafeDoseMgPerHr` to a descending operator is a
genuine Dafny *parse* error — a real gap in the mutation engine's
understanding of chain-direction compatibility, not a spec finding).
**Decision, same day: "go ahead and tighten REQ-GIP-1-8-1 to `>`."**
`dosage.dfy` changed, re-verified clean (`2 verified, 0 errors`,
unchanged), mutation suite re-run in full to confirm rather than assume
the fix: **zero survivors remain** — the two former survivor mutations
(`> -> >=`, `> -> !=`) are now correctly recognized by the pass-1 static
filter as trivially uninteresting *before* Dafny is even invoked (a
proof of `x > 0` universally implies both `x >= 0` and `x != 0`), a
clean mechanical confirmation the boundary is now tight
(`filtered_static` rose 4→6, `killed` unchanged at 29, `unclassifiable`
unchanged at 4 and unrelated). `nl_confirmation_dosage_dfy.md` gained an
amendment recording the decision and the regenerated, re-confirmed
summary. AOR/SOR/HOR stayed out of v1 scope exactly as scoped below,
checked not assumed (SOR/HOR: no set/heap syntax anywhere in the spec,
confirmed by test; AOR: implemented and exercised, correctly returns
zero mutants since its one site lives in a function body, out of
clause-mutation scope). 16 tests, updated to match the post-fix reality;
full suite 121 passed.

What follows is the original same-day sub-plan this build actually
followed — kept as the architectural record, not superseded by the
summary above.

#### Operator applicability audit against the real spec (not generic — checked against `dosage.dfy` as it exists today)

The literature defines six operator classes. Auditing each against the
one real spec in this repo, clause by clause, rather than assuming all
six apply:

- **ROR (Relational Operator Replacement) — applicable, the primary
  target.** Every comparison in `dosage.dfy` is a candidate: `rawDose <
  0.0` and `rawDose > maxSafeDoseMgPerHr` in `ExpectedDose`'s body;
  `concentrationMgPerMl > 0.0` and `maxSafeDoseMgPerHr > 0.0` (both
  `requires` clauses); the chained `0.0 <= dose <= maxSafeDoseMgPerHr`
  (two comparisons); `infusionRateMlPerHr >= 0.0` (ensures 3); and the
  pinning clause's `dose == ExpectedDose(...)` itself, where mutating `==`
  to `!=` should be killed trivially and is a useful sanity check on the
  harness, not just on the spec. 8 comparison sites, each mutable to up to
  5 other relational operators — on the order of 30-40 raw mutants before
  any filtering.
- **AOR (Arithmetic Operator Replacement) — applicable, narrowly.** Exactly
  one arithmetic operator exists in the whole spec: the `*` in
  `infusionRateMlPerHr * concentrationMgPerMl`. Mutating it to `+`, `-`,
  or `/` gives 3 mutants. **Named risk:** `/` on Dafny `real` is
  division-checked (confirmed empirically during Gate C1 — `possible
  division by zero` is a real verification error on this installed
  binary), so that mutant may fail to verify for a reason that has
  nothing to do with the postcondition being violated. The harness must
  attribute *why* a mutant failed (postcondition violated vs. an
  unrelated static error like division-by-zero) rather than pattern-match
  "verification failed" as "mutant killed for the right reason" — an
  unattributed kill would be exactly the kind of false-confidence finding
  this repo's discipline exists to prevent.
- **SOR (Set Operator Replacement) — NOT APPLICABLE, named explicitly.**
  `dosage.dfy` contains no set-typed values or set operations anywhere.
  Not silently skipped — recorded here as a real, checked scope exclusion
  (same pattern as REQ-DOSE-003's exclusion from this same spec in Gate
  C1), to revisit only if a future Dafny spec in this repo uses sets.
- **HOR (Heap Operator Replacement) — NOT APPLICABLE, named explicitly.**
  No object references, `old()` expressions, or `reads`/`modifies`
  clauses — `dosage.dfy` is pure functional/value code. Same treatment as
  SOR: named exclusion, not silent omission, revisit if a future spec
  needs it.
- **LOR (Logical Operator Replacement) — applicable, narrowly.** Exactly
  one explicit boolean connective exists: the `||` in
  `infusionRateMlPerHr >= 0.0 || dose == 0.0` (ensures 3), mutable to
  `&&`. 1 mutant. **Scope boundary named:** Dafny implicitly ANDs multiple
  `requires`/`ensures` clauses on one method together, but there is no
  explicit `&&` token at that seam to mutate — v1 only mutates explicit
  connectives written within a single clause, and does not attempt to
  "mutate" the implicit inter-clause conjunction (doing so would mean
  deleting a whole clause, which is really a different, coarser kind of
  mutant not attempted here).
- **COI (Constant Operator Insertion) — applicable, but answers a
  different question than the other five.** ROR/AOR/LOR ask "is this
  specific boundary/operator load-bearing." COI asks a coarser question:
  "does this clause constrain anything at all." Concretely: wrap each
  `ensures` clause's body in a top-level negation and re-verify. If the
  *negated* clause still verifies against the real implementation, the
  original clause was vacuous — true regardless of what the method
  actually returns, contributing nothing to the proof. This is close in
  spirit to Gate C3 vector 1's precondition-vacuity check, but applied to
  postconditions instead, and by direct re-verification rather than Z3
  satisfiability (Z3 can't evaluate the concrete implementation's return
  value the way `dafny verify` can). Applied to `dosage.dfy`'s three
  `ensures` clauses: 3 mutants.

Total: roughly 35-45 raw mutants, entirely from ROR/AOR/LOR/COI — SOR/HOR
contribute zero for this spec, named rather than hidden.

#### Architecture: reuse, don't reinvent

- **Parsing/mutation target grammar:** `evidence/dafny_spec_lint.py`'s
  existing tokenizer (`_tokenize`) and recursive-descent parser
  (`_Parser`) already define exactly the boolean/arithmetic/comparison
  grammar this repo's clauses use, built and tested in Gate C3. Reuse
  that grammar as the mutation target set rather than defining a second,
  possibly-inconsistent one. **Gap named:** the existing `_tokenize`
  discards character-span information (it only needs token kind/value to
  build a Z3 expression) — a mutation generator needs to reconstruct
  mutated *Dafny source text*, so it needs span-preserving tokenization.
  This is a small, additive extension (carry `m.start()`/`m.end()`
  alongside each token), not a rewrite — but it's new code, named here so
  it doesn't get assumed-free at build time.
- **Vacuity filtering (pass 2 of IronSpec's three-pass framework):**
  `evidence/dafny_spec_lint.py::check_precondition_satisfiability`
  already does exactly the check pass 2 needs (Z3 satisfiability of a
  clause set) — call it directly against each mutant's `requires` clauses
  before spending a real `dafny verify` invocation on it. A mutant that
  makes the precondition unsatisfiable is uninteresting (any postcondition
  holds vacuously) and should be discarded before verification, not
  reported as a false "survivor."
- **Static weaker-mutant filtering (pass 1):** discard mutants that are
  statically implied by the original clause (e.g. `>` mutated to `>=` on
  a clause already compatible with equality) before running the verifier
  at all — cheap to check syntactically for the small operator set this
  spec uses (ROR's own operator lattice), avoids burning a `dafny verify`
  call on a mutant that was never going to be interesting.
- **Re-verification (pass 3) and capture discipline:** mirror
  `run_verify_dafny.py`'s exact pattern — write each surviving mutant to
  a temp `.dfy` file, invoke the real installed Dafny binary, capture
  real stdout/exit code, parse via the same false-zero-guarded summary-line
  logic `evidence/dafny_adapter.py::parse_dafny_capture` already
  implements (a mutant "kill" must be a real `N verified, M errors` parse
  with M > 0 and the *right* error — see the AOR division-by-zero caveat
  above — never a bare nonzero exit code taken on faith).

#### Success criterion

A boundary in `dosage.dfy` is "mutation-proven" only if every mutant that
touches it is killed by the real verifier for the right reason (the
mutated postcondition genuinely fails, not an unrelated static error). Any
surviving mutant is a named, reported finding — a real gap in what the
proof establishes — exactly as Gate C4's STP finding was handled: fixed if
fixable, or recorded as a scoped, known limitation if not.

#### Build order (own multi-step sub-plan, not a single pass) — steps 1-4 and 6 done, step 5 done in reduced form

1. **Done.** Span-preserving tokenizer extension (small, additive, on top
   of `dafny_spec_lint.py`'s existing grammar — plus one addition beyond
   what was scoped here: a COMMA token, needed for the pinning clause's
   function-call syntax).
2. **Done.** ROR/LOR mutant generator + the static weaker-mutant filter
   (pass 1). AOR's generator is also built (for engine symmetry/future
   specs) but correctly produces zero mutants against this spec's
   clauses — see the v1 scope cut below.
3. **Done.** Vacuity filter (pass 2), wired directly to
   `check_precondition_satisfiability`.
4. **Done.** Re-verification harness (pass 3),
   `examples/dosage_calculator/run_mutation_suite.py`, mirroring
   `run_verify_dafny.py` and reusing `dafny_adapter.py`'s parser.
   Failure-reason attribution turned out to matter even without AOR: a
   non-(0,4) exit code (a genuine Dafny parse error, observed for real on
   4 mutants) is relayed with Dafny's own error line rather than being
   folded into "killed" or "survived" — see the unclassifiable findings
   above.
5. **Done.** COI's negation-and-reverify check, built alongside ROR/LOR
   rather than strictly after (the codebase was small enough that
   sequencing this after didn't add safety).
6. **Done.** `mutation_report.json`/`.md` + `run_manifest_mutation.json`,
   enumerating every one of the 39 mutants with its real outcome.
   Simplified from the originally-scoped killed-for-the-right-reason vs.
   killed-for-the-wrong-reason split: that distinction was scoped
   specifically for AOR's division-by-zero risk, which doesn't arise in
   v1 (no AOR mutants generated against this spec's clauses) — v1 uses a
   flatter killed/survived/filtered_static/filtered_vacuous/unclassifiable
   taxonomy instead, with the *unclassifiable* bucket catching exactly
   the "wrong reason" case (a real, non-postcondition parse error) that
   did occur, so the safety property (never mislabel a wrong-reason
   result as a real kill) held even without building the finer split.

#### v1 scope cut, named explicitly (not silently narrower than scoped)

AOR/SOR/HOR are out of scope for this build, per direct guidance ("be
careful with Dafny... we can consider floating points later, it's a
known but solvable issue"): AOR's one site
(`infusionRateMlPerHr * concentrationMgPerMl`) lives in `ExpectedDose`'s
function body, not a requires/ensures clause, so mutating it needs a
function-body extractor this build didn't scope in — deferred alongside
the division-by-zero attribution risk this same guidance flagged.
Follow-up guidance recorded for whenever that work is picked up: bound
any future real-valued mutant/comparison to the accuracy the dosage
calculation actually requires (e.g. an input on the order of 1e10 needs
no more precision than that), rather than treating Dafny's exact
arbitrary-precision `real` as demanding unbounded exactness. SOR/HOR
were never in scope (no sets or heap state anywhere in this spec, now
confirmed by a real test rather than only audited by inspection).

#### Explicit non-goals — held

Not a generic, Dafny-spec-agnostic mutation tool — like Gates C1-C4, this
builds one mutation suite for the one real spec that exists, per the
roadmap's own stated scope for this gate. Not wired into `build_matrix()`
or any generator — a pre-trust check run before relying on a PROVEN claim,
not part of the artifact-generation pipeline.

### Gate C6 — NL-dialogue confirmation (process control, lightest gate, adopt early) — BUILT and SIGNED OFF (2026-07-07)

Before the proof search runs: generate a plain-English summary of what
the formal spec actually asserts, get explicit human sign-off that the
summary matches intent. This is the process fix that prevents Gate 1's
finding from recurring — catch the intent/spec mismatch at authoring
time, not at review time.

This is a workflow practice more than software — the summary-and-sign-off
step itself could be a small script, but the actual artifact is a
recorded decision (mirroring `sources/req-gip-1-4-12-alarm-scope-decision.md`'s
pattern), not a database entry. **No technical dependency on any other
Gate C item** — recommend adopting it as a habit starting with the very
first real Dafny spec, not deferring it behind C1–C5.

**Built:** `evidence/dafny_nl_summary.py::summarize_method` — extracts
each requires/ensures clause verbatim plus any REQ-ID cited in a trailing
comment, alongside a best-effort operator-substitution English gloss
(explicitly labeled as a template, not comprehension). Reuses
`dafny_spec_lint.py`'s Gate C3 parsing surface. Only single-line clauses
supported; cross-checks its own extraction against `dafny_spec_lint`'s
canonical multi-line-capable extractor by content and refuses
(`SystemExit`) on any mismatch — a self-caught bug during this build
found the first draft of that check compared clause counts, not content,
and missed a real silently-truncated multi-line case; fixed before the 7
new tests (`tests/test_dafny_nl_summary.py`) were written. **Signed off:**
`examples/dosage_calculator/nl_confirmation_dosage_dfy.md` records
Steven's confirmation of the generated summary for
`dosage.dfy::CalculateHourlyDose` ("it's good for the spec as is",
2026-07-07), plus a next-phase item (spec adaptation and an explanation
of downstream analysis by different software, for a regulatory
submission) he explicitly scoped out as separate follow-up work.

### Suggested build order

1. **Environment decision** (which Dafny) — blocks C1 and everything
   downstream of it.
2. **Gate C6** (process habit) — costs nothing to start now, no
   technical blocker. **BUILT and signed off 2026-07-07**, taken up after
   C1–C4 and the Gate 2 wiring rather than first as suggested here — no
   technical dependency was violated by that order, the suggestion above
   was a recommendation, not a requirement.
3. **Gate C1** (capture + minimal false-zero guard) — foundation.
4. **Gate C2** (PROVEN exclusivity migration) — immediately after C1,
   before any real spec exists.
5. **Gate C4** (STPs) — alongside the first real spec.
6. **Gate C3** (parser hardening, 3 of 4 vectors; 4th named-blocked) —
   before trusting any PROVEN claim in earnest.
7. **Gate C5** (mutation testing) — largest, last, its own sub-plan.

**Actual order taken (2026-07-07):** C1 → C2 → C3 → C4, each built on
explicit direction ("start gate C2" / "start gate c3" / "start gate C4"),
matching the order suggested above from C3 onward (C4 was suggested
before C3, but nothing about C4 was ever blocked on C3 landing first, so
the swap cost nothing). C4 turned out to matter more than a checklist
item: it found and fixed a real gap in Gate C1's own spec.

### PROVEN's exclusivity today (R3 landed 2026-07-07; now exercised for real, not just possible)

`assert_no_realized_proven` implements ruling **R3**: PROVEN may appear
as a realized strength only for a record with `method == "dafny"` and
`verifier_completion_status == "completed"`; every other method remains
permanently excluded, exactly as R2 guaranteed before it. As of the Gate
2/C2-C4 wiring (2026-07-07, extended to variants A/B the same day), this
is no longer only a structural possibility: `traceability_matrix.a.json`,
`.b.json`, and `.formal.json` are real, committed artifacts each
containing real PROVEN records (REQ-GIP-1-4-12, REQ-GIP-1-8-1), all
satisfying R3's two conditions for real, confirmed by the structural
PROVEN sweep in `generate_artifacts.py`. The base matrix and variant C's
symbolic/concrete sub-views still contain zero PROVEN records by
design - the base is frozen (ruling R2c) and never touches
`build_matrix()`, and symbolic/concrete's shape deliberately filters to
crosshair/concrete_test only - R3's guarantee remains observationally
identical to R2's there.

---

## What "done" looks like for this roadmap

Every gate resolved, blocked-and-named, or explicitly deferred with a
stated reason. Gate 3 is closed — tested empirically, not assumed. Gate 4
is decided (option 3) and its mechanism is built via Gate 2. Gate 2
itself is complete: the CONFLICT rule (two sub-types, tested against
three cases), the vocabulary-agnostic binder (`build_matrix()`, sole
implementation across all four variants, original per-variant functions
deleted), and the CLI (`evidence/cli.py`) are all built and verified.
Gate 6 (FRN) is resolved and written into four files. Gate 5 is now
fully resolved: variant C's binder no longer binds symbolic evidence
unconditionally, so a concrete-only fixture is constructible — the last
open item from the original six-gate ledger. **Phase B's gate ledger is
fully closed.**

Phase C is now a gate-sequenced plan (Gates C1–C6, suggested build order
above), not a two-mechanism sketch — produced with the same discipline
Phase B used: real environment check before assuming a tool works a
certain way. That check found Dafny not installed and apt's only
offering badly out of date (2.3.0+dfsg from roughly 2015) — researched
further rather than settling for it or asking for an under-informed
decision, and resolved same day: modern Dafny 4.11.0 obtained via NuGet,
verified against the real binary (exact false-zero match, real exit-code
behavior, the vacuous-precondition risk confirmed reproducible, its Z3
mitigation confirmed feasible). One gate (C3's fourth vector,
specification stripping) stays named as blocked on incomplete source
material rather than guessed at. **Gate C1 is built:** a real Dafny spec
for the dosage kernel (REQ-DOSE-003 named as an explicit scope
exclusion), a capture runner pair, and `evidence/dafny_adapter.py`'s
false-zero-guard parser — sharpened beyond the originally-planned
substring floor to a regex on the verifier's own summary line,
regression-tested against a substring trap and against
`assert_no_realized_proven`. **Gate C2 is also now built (2026-07-07):**
ruling R3 supersedes R2 — PROVEN may appear as a realized strength only
for `method == "dafny"` records with `verifier_completion_status ==
"completed"`, every other method permanently excluded, checked
explicitly in 8 new tests rather than assumed. **Gate C3 is also now
built for 3 of its 4 named vectors (2026-07-07):**
`evidence/dafny_spec_lint.py` adds a real Z3-based vacuous-precondition
check (proven against a real committed fixture Dafny itself verifies
clean despite an unsatisfiable precondition) and a best-effort
weak-postcondition heuristic; `evidence/dafny_adapter.py`'s summary-line
parser is hardened after a real "N out of resource" finding on the
installed binary (a resource-starved run can report a 0 errors count
while incomplete — confirmed the real capture's exit code is nonzero,
already caught, hardened anyway as defense in depth). Vector 4
(specification stripping) stays BLOCKED, named. **Gate C4 (Spec-Testing
Proofs) is also now built (2026-07-07), and found a real gap on its
first application, not a synthetic one:** a Dafny lemma trying to prove
a wrong candidate dose value impossible for `dosage.dfy`'s original
postcondition failed to verify — the spec bounded `dose` but never
pinned it, so a broken implementation could have satisfied it
undetected. Fixed for real: an `ExpectedDose` function and a pinning
ensures clause, re-verified clean (`2 verified, 0 errors`, up from
Gate C1's original `1 verified`), the real committed capture re-run
honestly to match. The original is preserved as
`dosage_underconstrained.dfy`; two STP suites
(`dosage_stp_suite.dfy`, `dosage_stp_suite_against_underconstrained.dfy`)
mechanically prove both directions — six lemmas pass against the fix,
the same two REJECT lemmas genuinely fail against the preserved
original. A self-caught mistake (an out-of-bounds wrong-value choice
that gave a false pass for an unrelated reason) was corrected before
committing, with a regression test guarding against it recurring.

**Gate 2/C2-C4 wiring is also now built (2026-07-07) — the first real
Dafny-sourced PROVEN evidence ever to reach a live matrix row — and
extended to variants A and B the same day.** Three design decisions were
confirmed before building the variant-C-only version: scope is variant C
only, for now; the Z3 gate lives inside the binder itself
(`dafny_record()`); metadata declares the dafny evidence explicitly,
cross-checked by a new CONFLICT Type 1 sub-check.
`traceability_matrix.formal.json` (variant C's third partition, Gate 5's
dual-matrix pattern extended to a triple) binds real `dosage.dfy`
evidence to REQ-GIP-1-4-12/REQ-GIP-1-8-1, gated by Z3 precondition
satisfiability and the false-zero guard before any record is even
constructed. Confirmed correct, then extended the same day ("go ahead
and extend variant A and B now"): `metadata.a.yaml`'s evidence list and
`metadata.b.yaml`'s new `.formal-N` shadow rows declare the same
evidence; the CLI gained `--dafny-captures`, which turned out to be
required, not optional, once A/B declared dafny evidence; the fact-
equality gate's intent comparison became subset-based to accommodate
`formal.json` permanently lacking an opinion about REQ-DOSE-003. Both
requirements' `intent_ok` is now `True` in EVERY variant artifact — the
temporary A/B divergence tracked when C landed first is fully closed,
and its carve-out mechanism (`run_formal_check`,
`KNOWN_FORMAL_INTENT_DIVERGENCE`) retired, exactly as promised when it
was built. `assert_no_realized_proven`'s ruling R3 is exercised end to
end across five real artifacts now, not just in isolation. Full suite
now 98 passed, full pipeline re-run end to end.
