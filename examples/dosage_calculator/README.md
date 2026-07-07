# Dosage Calculator Example — Audit-Trail Record

Proof-of-concept kernel for the PayloadGuard evidence layer: a pure
dose-clamping function, verified by CrossHair within recorded bounds, bound
to safety requirements extracted from a published hazard analysis, and
rendered into an IEC 62304-style traceability matrix by
`evidence/render/manual_matrix.py`.

## Source document

All sourced requirements and threats in `metadata.yaml` derive from:

> Arney, D., Jetley, R., Jones, P., Lee, I., Ray, A., Sokolsky, O.,
> Zhang, Y. (2009). *Generic Infusion Pump Hazard Analysis and Safety
> Requirements Version 1.0.* University of Pennsylvania / U.S. FDA Office
> of Science and Engineering Laboratories / Fraunhofer Center for
> Experimental Software Engineering. February 6, 2009.

The full text is archived verbatim in `sources/gip-v1.0-hazard-analysis.md`
per the standing rule in `sources/README.md`.

## Requirement-to-source mapping

| Metadata ID | GIP v1.0 source | Notes |
|---|---|---|
| `REQ-GIP-1-4-12` | Safety Requirement 1.4.12 (bolus dose limit alarm); mitigates Hazards 1.2, 1.3 | Dual-scope split (2026-07-05): kernel_scope = ALARM CONDITION detection (evidenced); system_scope = ALARM SIGNAL emission (explicit GAP, deferred to integration) — see `sources/req-gip-1-4-12-alarm-scope-decision.md` |
| `REQ-GIP-1-8-1` | Safety Requirement 1.8.1 (no continuous reverse delivery, citing IEC 601-2-24); mitigates Hazard 1.14 | Fault-input modelling — see caveat 1 and the amendment note below |
| `REQ-DOSE-003` | **DECLARED, no GIP source** | See caveat 2 below |

## Interpretive-call caveats

1. `REQ-GIP-1-8-1` (reverse delivery) is modelled as a fault input at
   this kernel: a negative `infusion_rate_ml_per_hr` represents the
   hardware single-fault reverse-flow condition, and the directional
   postcondition (`infusion_rate_ml_per_hr >= 0 or __return__ == 0.0`)
   requires that any such fault yields exactly zero delivered dose. This
   is still an interpretive extension of the source requirement — GIP
   v1.0 SR 1.8.1 addresses the physical pump, and mapping the fault to a
   negative rate parameter is a modelling decision — but the clamp
   branch is now genuinely exercised, unlike the pre-amendment contract
   (see the amendment note below).
2. `REQ-DOSE-003` has no GIP source at all — GIP v1.0 does not address
   floating-point overflow. It is DECLARED engineering judgement.
3. Hazards HID 1.1, 1.4, 1.5, 1.10 and Safety Requirements 1.2.2/1.2.3
   (flow-rate-deviation-over-15-minutes) were deliberately excluded from
   this metadata — they describe a stateful, time-windowed sensor model,
   not a pure function, and don't fit this kernel. Note them in the
   README as a candidate second kernel, not as an oversight.

## Amendment 2026-07-04 — Option A: reverse delivery modelled as a fault input

Recorded per the audit-trail discipline in `sources/README.md` (changes
are proposed and recorded, never silent).

**Finding (independent review of the original Phase A):** the original
contract required `infusion_rate_ml_per_hr >= 0`. Under that
precondition, `raw_dose = infusion_rate_ml_per_hr *
concentration_mg_per_ml` is non-negative by algebra, so the
`if raw_dose < 0.0: return 0.0` branch was dead code and the
postcondition's lower bound held tautologically. The `REQ-GIP-1-8-1`
binding therefore verified nothing about the reverse-delivery fault
scenario: it was vacuously true.

**Change applied:**
- Precondition widened to `math.isfinite(infusion_rate_ml_per_hr)` — any
  finite rate, negative rates modelling the fault.
- Directional postcondition added:
  `infusion_rate_ml_per_hr >= 0 or __return__ == 0.0`.
- Branch order fixed: the negative check now runs **before** the
  finiteness check. This matters: under the original order, a negative
  rate whose product overflows to `-inf` is caught by
  `not math.isfinite(raw_dose)` and returns the **maximum** safe dose —
  the worst possible response to a reverse-flow fault.
- `metadata.yaml` `REQ-GIP-1-8-1` text updated to state the fault
  modelling; `intended_method: PROVEN` retained (the intent/realized
  mismatch remains real and is still reported in the matrix).

**Preserved evidence — `dosage_naive_widening.py` fixture pair:** the
naive widening (new contract, original branch order) is committed
deliberately, with its own real CrossHair capture
(`raw_crosshair_output_naive_widening.txt`,
`run_manifest_naive_widening.json`). Two facts it documents:

1. The concrete violation exists and is deterministic:
   `calculate_hourly_dose(70.0, 1e308, -2.0, 10.0)` returns `10.0`
   where the directional postcondition requires `0.0` (verified by
   execution in this session; reproduce with two lines of Python).
2. **CrossHair did not find it — and not for bounds reasons.** The
   capture shows exit code 0 and `Not confirmed` for both
   postconditions. A `BOUNDED_CHECKED` result is incomplete in two
   distinct ways. (1) *Search-budget incompleteness*: only part of the
   representable input space is explored within the recorded bounds.
   (2) *Model-fidelity incompleteness*: the symbolic model reaches some
   machine-level behaviours only through channels that are unreliably
   sampled and sharply complexity-dependent, so some real, reachable
   violations may go undetected regardless of bounds. The `-inf`
   exhibit demonstrates class (2): CrossHair predominantly models
   Python floats as mathematical reals, attempting IEEE-faithful
   floating-point execution only infrequently (changelog v0.0.72) — in
   real arithmetic 1e308 × −2.0 = −2e308 exactly, so the overflow
   state is reached only when the IEEE-faithful channel is sampled.
   That channel exists but is unreliably sampled and sharply
   complexity-dependent: under identical invocation and bounds it
   confirmed a violation on the one-operation probe yet stayed silent
   on the four-parameter kernel — the paired measurement is pinned in
   `exhibit_pin_overflow_probe.json` and
   `exhibit_pin_naive_widening.json` — and nothing in the recorded
   bounds discloses which regime a run sat in. Raising timeouts or
   iterations does not reliably close class (2). CrossHair injects
   nan/+inf/−inf as float *arguments* (changelog v0.0.58); a *computed
   intermediate* overflow from finite inputs is reachable only through
   the IEEE-faithful channel. Changelog:
   https://crosshair.readthedocs.io/en/stable/changelog.html
   A "no counterexample found" result on the fixed `dosage.py` is
   therefore evidence of absence within the recorded bounds *and*
   within the model's sampled fidelity, nothing stronger.

**Post-amendment evidence that the widened domain is really explored:**
the Sample B (broken variant) capture now contains a second, negative
counterexample — `calculate_hourly_dose(0.5, 0.25, -0.125, 0.125)`
returning `-0.03125` — showing CrossHair genuinely drives negative rates
through the contract after the widening.

## Amendment 2026-07-05 — REQ-GIP-1-4-12 alarm scope split (Gate 1 review)

Recorded per the audit-trail discipline in `sources/README.md`.

**Finding:** the requirement text ("shall trigger a Dose limit exceeded
alarm") was backed only by a concrete test verifying clamped output —
evidence and text did not match. **Decision** (full reasoning in
`sources/req-gip-1-4-12-alarm-scope-decision.md`): split per
IEC 60601-1-8's ALARM CONDITION / ALARM SIGNAL separation into
`kernel_scope` (condition detection via clamped output — what the
evidence actually verifies) and `system_scope` (signal emission —
deferred to integration testing, rendered as an explicit named GAP in
every matrix view, never a silent omission). **Changes:** the concrete
test was renamed `over_max_clamps_exactly_to_max` →
`kernel_detects_bolus_limit_exceeded` and re-captured; evidence rows for
this requirement reference the kernel_scope text; the GAP is excluded
from fact-equality by rule (a GAP is the rendering of absent evidence,
not a fact) — the gate still holds at 7 facts. When integration testing
exists, system_scope becomes a new binding target with its own evidence
chain, not folded into the kernel's.

## `FRN` pump-type tag: RESOLVED (2026-07-05)

The GIP v1.0 hazard tables tag many hazards with pump type `FRN` (e.g.
Hazard 1.14, referenced by `THR-GIP-1-14`) without defining the
abbreviation in the extracted text. Resolution was attempted earlier in
this project (web search for the GIP project pages and companion
documents; direct retrieval of `rtg.cis.upenn.edu/gip-UPenn/` and the
UPenn `cis_reports/893` tech-report page failed — host unreachable / HTTP
403 from this environment); no companion document defining `FRN` was
found at that time.

**Resolution:** `FRN` = FDA Product Code for "Infusion Pump"
(21 CFR 880.5725). Within the GIP taxonomy specifically, denotes
general-purpose volumetric infusion pumps (peristaltic mechanism,
cassette-based administration set), distinct from the `All` tag used
elsewhere in the source's hazard tables. Resolved via NotebookLM's
extraction of the full source PDF, cross-checked against independent
FDA-registry research landing on the same product code.

**Confidence caveat, carried forward rather than dropped:** well-supported,
but not yet independently re-verified against the raw Sec 2.4.1 text of
the source document itself. `THR-GIP-1-14` and any other `FRN`-tagged
hazard should be read with that caveat until re-verified. See
`sources/README.md` and `KNOWN_LIMITATIONS.md` (Gate 6) for the same
record.

## Fixture formats

Three fixture pairs are committed, all captured by actually running
CrossHair (`crosshair-tool 0.0.107`, Python 3.11) — none is hand-written.

### Sample A — clean (`dosage.py`)

Produced by `python3 run_verify.py`.

- `raw_crosshair_output.txt` — verbatim stdout+stderr of
  `crosshair check dosage.py --report_all`. Content for this capture:
  two `info: Not confirmed.` lines, one per postcondition (range and
  directional). With `--report_all`, CrossHair reports `Not confirmed`
  when its bounded search ends without finding a counterexample and
  without exhausting all paths — precisely the evidence class
  `BOUNDED_CHECKED` encodes. It is not a proof (see the amendment note
  above for a committed demonstration of why).
- `run_manifest.json` — JSON object with keys `tool`, `tool_version`,
  `command` (argv list), `exit_code` (0 = no counterexample found),
  `started_utc` (ISO-8601 UTC), `target`.

### Sample B — broken (`dosage_broken.py`)

Produced by `python3 run_verify_broken.py` (a duplicate of
`run_verify.py` retargeted at the clamp-free variant, kept separate so
`run_verify.py` stays identical to the reviewed original).

- `raw_crosshair_output_broken.txt` — verbatim capture containing two
  postcondition-violation lines with concrete counterexamples:
  `calculate_hourly_dose(1.0, 1.0, 0.5, 0.25)` returning `0.5`
  (range postcondition: 0.5 exceeds the 0.25 maximum) and
  `calculate_hourly_dose(0.5, 0.25, -0.125, 0.125)` returning
  `-0.03125` (directional postcondition: negative rate must yield 0.0).
- `run_manifest_broken.json` — same manifest shape, `exit_code` 1.

### Sample C — naive widening (`dosage_naive_widening.py`), review artifact

Produced by `python3 run_verify_naive_widening.py`. See the amendment
note above for why this pair exists: it preserves the wrong-branch-order
variant whose real violation CrossHair's bounded search did not find
(`exit_code` 0, both postconditions `Not confirmed`). Machine-readable
pinning (tool/Python/platform versions, exact invocation, mechanism
attribution) lives in `exhibit_pin_naive_widening.json`. The miss is
version-contingent — a future CrossHair release that samples
floating-point theory more aggressively may confirm the violation; this
exhibit's claim is scoped to the pinned version.

### Domain-free probe — `overflow_probe.py` (outcome: CONFIRMED)

`overflow_probe.py` isolates the model-fidelity question from all dosage
logic: `double_it(x)` with `pre: math.isfinite(x)` and
`post: math.isfinite(__return__)` has a deterministic IEEE violation
(`double_it(1e308)` → `inf`; executable fact in
`tests/test_overflow_probe.py`). Run with the same invocation and
defaults as the amendment runs (`python3 run_verify_overflow_probe.py`),
CrossHair **confirmed** it: exit 1,
`false when calling double_it(8.98846567431158e+307) (which returns
float("inf"))`. The expected outcome was a miss; the confirmation was
recorded as-is and not re-run — it measures the width of CrossHair's
infrequent IEEE-faithful channel. Read together with Sample C (same
invocation, violation NOT found on the 4-parameter kernel), the two
exhibits bound that channel: it exists and fires on a minimal
single-operation target, but is not dependable on more complex targets
at default settings. Pin: `exhibit_pin_overflow_probe.json`.

### Bounds: declared vs effective (resolved 2026-07-04, Turn 2.0 B1)

`metadata.yaml` declares `toolchain.crosshair_bounds`
(`per_condition_timeout_s: 30`, `max_iterations: 100000`, `seed: 1`) as
the *intended* verification envelope — the bounds analogue of
`intended_method`. What a run actually *demonstrated* is recorded in its
manifest's `effective_bounds` field, the single source of truth. Since
Turn 2.0, the Sample A/B capture command passes
`--per_condition_timeout 30` (the one declared bound the 0.0.107 CLI can
enforce); `max_iterations` and `seed` remain declared-only — the CLI has
no flags for them, an enforcement gap open at the tool level (Phase B
may close it via the CrossHair API). Every variant matrix carries a
model-level `bounds` block `{declared, effective, enforcement_note}`,
derived once and projected read-only into all views. The exhibit
captures (Sample C, overflow probe) remain pinned to their original
no-flags invocation and were not re-run — they are frozen measurements.
Bounds govern class (1) search-budget incompleteness only (see the
amendment note above): they determine how much of the representable
input space is explored. The Sample C miss is class (2) model-fidelity
incompleteness and is not closed by raising bounds.

## Matrix generation

`traceability_matrix.json` / `traceability_matrix.md` are generated —
not hand-typed — by `python3 generate_matrix.py`, which reads the Sample A
manifest and raw output, constructs a `VerificationResult`, and runs
`evidence.render.manual_matrix.build_traceability_matrix` against
`metadata.yaml`. Strength in every row comes only from the verification
result (`BOUNDED_CHECKED`); the two requirements whose `intended_method`
is `PROVEN` are correctly reported with `intent_ok: false` in THIS
FROZEN BASE VIEW specifically (ruling R2c) — it never calls
`build_matrix()` and stays the unchanged Phase A symbolic-subset legacy
view even after Dafny was wired into variants A/B/C (below). Variants
A/B/C now report `intent_ok: true` for both — see the 2026-07-07
amendment.

## Amendment 2026-07-07 — Dafny evidence wired into variants A, B, and C

Recorded per the audit-trail discipline in `sources/README.md`.

Phase C, Gates C1-C4 built a real Dafny spec (`dosage.dfy`), a capture
runner, a false-zero-guard parser, a PROVEN-exclusivity structural rule
(ruling R3), Z3-based precondition-satisfiability hardening, and
Spec-Testing Proofs — all standalone, none wired into any traceability
matrix. This amendment is the wiring: `evidence/render/matrix_variants.py::dafny_record()`
gates PROVEN on both Z3 satisfiability and the false-zero guard before
constructing any record, and is now reachable from every schema variant.

- **Variant C** gained a third partition, `traceability_matrix.formal.json`
  (extending Gate 5's dual-matrix pattern to a triple), built first and
  confirmed correct before extending A/B.
- **Variants A and B** now declare the same real dafny evidence
  explicitly (`metadata.a.yaml`'s `evidence: [{method: dafny, ...}]`;
  `metadata.b.yaml`'s new `.formal-N` shadow rows, e.g.
  `REQ-GIP-1-4-12.formal-1`), cross-checked by a new Gate 2 CONFLICT
  Type 1 sub-check (`dafny_binding_conflicts`).
- **REQ-GIP-1-4-12 and REQ-GIP-1-8-1's `intent_ok` flips from `false` to
  `true`** in every variant artifact (A, B, C-symbolic, C-concrete,
  C-formal) — the first time since Phase A that `intended_method:
  "PROVEN"` has been realized, not just declared. The frozen base matrix
  (above) is unaffected by design.
- **The fact-equality gate** (`evidence/reconcile.py::run_gate`) now
  holds at **9 facts**, not 7 — the two new dafny facts. Its intent
  comparison became subset-based rather than strict dict equality:
  `traceability_matrix.formal.json` permanently, deliberately has no
  opinion about REQ-DOSE-003 (out of `dosage.dfy`'s scope, named in its
  own header comment), so it can never carry the FULL requirement set
  the way A/B/base/symbolic/concrete always do — a real structural
  asymmetry between C's three-way split and A/B's single-artifact shape,
  not a bug to paper over.
- **The CLI** (`evidence/cli.py`) gained a `--dafny-captures` option -
  once metadata.a.yaml/metadata.b.yaml declared dafny evidence,
  `build_matrix()` genuinely requires a `dafny_store` to build those
  variants at all, so the CLI needed a way to supply one.
- Built in two phases on explicit direction: variant C first ("hmm. can
  we post hoc verify A and B after C variant is proven?"), then A and B
  the same day ("go ahead and extend variant A and B now").

## Amendment 2026-07-07 — Gate C6: NL-dialogue confirmation sign-off

Recorded per the audit-trail discipline in `sources/README.md`.

`nl_confirmation_dosage_dfy.md`, in this same directory, records Gate
C6's actual deliverable: a plain-English summary of
`CalculateHourlyDose`'s contract, generated by
`evidence/dafny_nl_summary.py`, and Steven's explicit sign-off that it
matches intent ("it's good for the spec as is"). Not wired into any
traceability matrix — a process-control artifact, not evidence bound to
a requirement.

## Amendment 2026-07-07 — Gate C5: mutation testing, 2 real survivors found

Recorded per the audit-trail discipline in `sources/README.md`.

`run_mutation_suite.py` real-verified mutants (generated by
`evidence/dafny_mutate.py`) against `CalculateHourlyDose` using the
installed Dafny binary. An initial run of 39 found 2 real survivors
(below), which were fixed the same day. `mutation_report.json`/`.md` and
`run_manifest_mutation.json`, in this same directory, now reflect the
FINAL state after this amendment's fix and the further extension
recorded below (42 mutants: 31 killed, 6 filtered_static, 4
filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 0
survived, 0 unclassifiable) — see the next amendment for what changed
the count from 39 to 42 and closed out the 4 that were unclassifiable
here.

**The 2 survivors were a real, understood finding about REQ-GIP-1-8-1's
postcondition, not a bug in this build.** `infusionRateMlPerHr >= 0.0 ||
dose == 0.0` with the first disjunct's `>=` weakened to `!=` or `>` both
verified: at `infusionRateMlPerHr == 0.0` exactly, real multiplication
makes `rawDose == 0.0` exactly, so `dose == 0.0` already holds at that
boundary regardless of the first disjunct's operator. The `>=` choice
wasn't independently load-bearing at that single point. This spec is
the one Steven signed off on in Gate C6 the same day — **reported for
his decision, not silently changed.** See the
"Amendment 2026-07-07 — Gate C5: mutation testing" entry in
`nl_confirmation_dosage_dfy.md` for the fix: Steven decided to tighten
REQ-GIP-1-8-1 to `>`; `dosage.dfy` changed, re-verified clean, and the
mutation suite re-run in full confirmed zero survivors remain at that
point (killed=29, filtered_static=6, unclassifiable=4, survived=0 — see
the next amendment for how the remaining 4 unclassifiable also closed
out).

At this point, the 4 unclassifiable results were a real, understood gap
in the mutation engine, not the spec: mutating one side of the chained
`0.0 <= dose <= maxSafeDoseMgPerHr` clause to a descending operator
(`>=` or `>`) produces a genuine Dafny parse error (chained comparisons
must stay direction-consistent) — confirmed by direct re-run, correctly
refused rather than misclassified as killed or survived. AOR/SOR/HOR
were explicitly out of this build's scope — SOR/HOR because this spec
has no set or heap syntax at all (confirmed by test); AOR because its
one site lives inside `ExpectedDose`'s function body, not a
requires/ensures clause, deferred per direct guidance to handle
real-number precision/accuracy bounding as a separate follow-up.

## Amendment 2026-07-07 — Gate C5 extended: chain-direction-aware ROR + function-body AOR

Recorded per the audit-trail discipline in `sources/README.md`.

External research into the previous amendment's two open items (full
findings: `gate_c5_mutation_testing_research_findings.md`) came back the
same day and was built the same day, on direct instruction ("build
both"):

- **Chain-direction-aware ROR** closes out the 4 unclassifiable results
  above. `evidence/dafny_mutate.py` now restricts each chained-
  comparison link's mutation candidates to direction-compatible
  operators (confirmed against the Dafny Reference Manual's own chaining
  rule), so those 4 mutants are filtered *before* generation ever
  reaches Dafny, not sent and refused post-hoc. They no longer count as
  "unclassifiable" at all — a new `filtered_chain_incompatible` outcome.
- **Function-body AOR** extends mutation testing to `ExpectedDose`'s one
  arithmetic operator (`infusionRateMlPerHr * concentrationMgPerMl`) -
  part of the formal spec, never `CalculateHourlyDose`'s own trusted
  implementation, which is never mutated. Restricted to MutDafny's own
  group rule (`+`/`-`/`*` freely interchange; `/` only with `%`, absent
  from this spec), so a mutation can never introduce `/` where the
  original had none - the division-by-zero false-kill risk named when
  this was originally deferred is closed by construction. The two real
  candidates (`* -> +`, `* -> -`) are both genuinely killed, confirming
  `*` is load-bearing.

**Final real run: 42 mutants — 31 killed, 6 filtered_static, 4
filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 0
survived, 0 unclassifiable.** `mutation_report.json`/`.md` and
`run_manifest_mutation.json` reflect this final state.
