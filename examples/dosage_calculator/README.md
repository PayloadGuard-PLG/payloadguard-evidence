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

**Final real run at this point: 42 mutants — 31 killed, 6
filtered_static, 4 filtered_chain_incompatible, 1
filtered_ar_group_incompatible, 0 survived, 0 unclassifiable.** See the
next amendment for the LVR extension that added 14 more.

## Amendment 2026-07-07 — Gate C5 LVR extension: matched its own prediction exactly

Recorded per the audit-trail discipline in `sources/README.md`.

Requested directly ("scope out Gate C5's LVR extension", then "go"):
tests whether a comparison's LITERAL CONSTANT is load-bearing, not just
its operator or the arithmetic combining it. Every numeric literal in
this spec's requires/ensures clauses and `ExpectedDose`'s function body
was audited empirically — **all 7 are exactly `0.0`**, no other numeric
constant exists anywhere in the spec.

Each is mutated to `original ± 0.01` — the clinical-precision floor from
the earlier research, finally applied (it was always scoped to literal
perturbation specifically). A new filter generalizes ROR's
requires/ensures polarity principle from operator-implication to
magnitude-implication: 4 of the 14 raw mutants are filtered as
`filtered_magnitude_implied` (the narrowing/weakening direction, per
clause role); EQ-adjacent literals and function-body literals have no
such filter and always go to real verification.

**The real run matched the scoping session's hand-derived prediction
exactly, site by site: 10 real-verified candidates, all 10 genuinely
killed, zero survivors.** For example, widening
`concentrationMgPerMl > 0.0` to `> -0.01` is killed via `ExpectedDose`'s
own unchanged precondition at the pinning clause's call site; both
function-body literal mutants (the `< 0.0` threshold and the bare
`then 0.0` return value) are killed because any mismatch between
`ExpectedDose`'s mutated definition and the method body's unchanged,
actual computation breaks the pinning clause for some input in the
perturbed range.

The scoping session flagged one unresolved tension: whether the
clinical-precision floor is the right test for REQ-GIP-1-8-1's
*exact-zero* safety requirement specifically, since a regulator could
reasonably view any nonzero delivery as a real hazard rather than
negligible noise. This result didn't need to resolve that tension to
come out clean (the zero-literal mutant was killed at the ±0.01
granularity regardless), but the underlying judgment call remains open.

**Final combined real run across all five operator classes: 56 mutants
— 41 killed, 6 filtered_static, 4 filtered_chain_incompatible, 1
filtered_ar_group_incompatible, 4 filtered_magnitude_implied, 0
survived, 0 unclassifiable.** `mutation_report.json`/`.md` and
`run_manifest_mutation.json` reflect this final state.

## Amendment 2026-07-14 — `RISK_MANAGEMENT_PLAN.md` landed: third and final ISO 14971 risk-management-plan artifact in this repo

Mirrors `examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`
and `examples/renal_adjustment/RISK_MANAGEMENT_PLAN.md` (both landed
earlier the same day) — same template, same ISO 14971:2019 clause
citations, already cross-checked against the real standard's verbatim
text when the first plan was built.

Landed as `examples/dosage_calculator/RISK_MANAGEMENT_PLAN.md`.
Device-specific content is genuinely different from the other two
plans in one real way: this is the only example with three independent
evidence types per requirement (CrossHair `BOUNDED_CHECKED`, concrete
`EXAMPLE_CHECKED`, Dafny `PROVEN`), stated with their real, differing
strengths rather than flattened — REQ-DOSE-003 in particular has no
Dafny proof at all, only CrossHair + one concrete test, and the plan
says so plainly rather than implying parity with the other two rows.
The plan also surfaces REQ-GIP-1-4-12's existing `kernel_scope`/
`system_scope` split (Gate 1 review, 2026-07-05) as Section 1's
life-cycle-phase scoping — a real precedent already in this device's
own requirement text, not invented for the plan — and names the
existing STRIDE threat model (`THR-GIP-1-2/1-3/1-14`) as a related but
distinct artifact, not a substitute for the clinical hazard register
this plan still doesn't contain. Gate C5's mutation-testing residual
is genuinely cleaner here than the other two examples: 56 mutants, 0
survivors, 0 unclassifiable (see the amendment immediately above).
Gate C6 — `nl_confirmation_dosage_dfy.md`'s "Decision" section,
**Confirmed, 2026-07-07, by Steven** — was in fact the very first Gate
C6 sign-off recorded anywhere in this repository, preceding both other
examples' own sign-offs by several days.

## Amendment 2026-07-14 (later) — `HAZARD_REGISTER.md` landed: first real hazard-register artifact in this repo

Direct instruction, after all three examples' risk-management plans
landed: "continue with the easiest first please so we can evaluate the
output." `dosage_calculator` was chosen as the easiest of the three
because its primary source, `sources/gip-v1.0-hazard-analysis.md`, is
itself a formal, published hazard analysis (the GIP v1.0 project,
2009) — unlike `renal_adjustment`'s and `drug_interaction_checker`'s
clinical-guideline sources, which name clinical facts but not a
structured hazard table. This device's own `metadata.a.yaml` STRIDE
threat model already cited three GIP hazard IDs directly
(`THR-GIP-1-2`, `THR-GIP-1-3`, `THR-GIP-1-14`), so hazard
*identification* (ISO 14971:2019 clause 5.4) could be built from real,
already-cited source data rather than fresh judgment calls.

Landed as `examples/dosage_calculator/HAZARD_REGISTER.md`: four hazard
entries — `HAZ-GIP-1.2`, `HAZ-GIP-1.3`, `HAZ-GIP-1.14` (each with the
verbatim GIP `HID` row, cause, and GIP's own stated mitigation, cross-
referenced against this kernel's actual risk control measure and real
evidence), plus `HAZ-DOSE-003` (the one row with no GIP source at all
— `metadata.a.yaml`'s own text already says so — stated plainly, not
presented at the same evidentiary strength as the other three). A
"explicitly out of scope" section names representative hazards from
GIP's ~85-row table this kernel does *not* address (physical sensing,
hardware, environmental, biological/chemical, most of Operational) so
the register can't be misread as covering the full pump. Severity,
probability, and risk-acceptability evaluation are left as explicit
`GAP`s throughout, same discipline as `RISK_MANAGEMENT_PLAN.md` —
hazard identification is real here; risk *estimation* and
*evaluation* (clauses 5.5, 6, 8) still require a clinical SME that
doesn't exist yet.

`RISK_MANAGEMENT_PLAN.md` Section 8 updated to reflect that the
register now exists and what it does and doesn't complete.

Sections requiring clinical judgment (roles, severity/probability
bands, acceptance matrix, overall-residual-risk method) left as
explicit `GAP`s, not fabricated, matching `metadata.a.yaml`'s own
`classification_rationale` (`B`, `DECLARED`, pending exactly this kind
of file).

## Amendment 2026-07-14 (later still) — clinical SME assigned; draft severity/probability proposal built and applied

Direct instruction: "assign a clinical SME and start the
severity/probability tables." This was **not** treated as an
instruction to fabricate a name or invent clinical data — both would
have directly contradicted every `GAP` this repo's risk-management
plans and hazard registers had deliberately left unfilled. Instead:
Steven is now recorded, by his own explicit choice, as this device's
named Clinical/Subject Matter Expert (`RISK_MANAGEMENT_PLAN.md`
Section 2) — the same class of boundary this repo has held to for
every Gate C6 sign-off (a recorded human decision, never self-declared
on the human's behalf).

With that role filled, a **draft severity/probability/acceptance-
matrix proposal** was built, reasoned entirely from evidence already
committed in `HAZARD_REGISTER.md` and `metadata.a.yaml` — not invented
clinical judgment. Real severity bands (S1 Negligible through S4
Critical) were defined against this kernel's actual proven/bounded-
checked guarantees rather than generic examples; a standard five-level
qualitative probability scale (P1 Improbable through P5 Frequent) was
adopted, with every hazard defaulting to P5 per this plan's own
already-established worst-case policy, since no field data exists to
justify anything lower. A three-region acceptance matrix (Acceptable /
ALARP / Unacceptable) was proposed and applied. **Citation correction,
2026-07-15**: this was originally attributed to "ISO 14971's own Annex
D," but the 2019 edition has no Annex D — see
`RISK_MANAGEMENT_PLAN.md` §4.3's citation correction and
`RISK_MANAGEMENT_FINDINGS.md` for the real basis (clause 4.2 NOTE 1;
ISO/TR 24971 Annex C.4/Figure C.1) and the still-open question of
whether this matrix's region *names* match TR 24971's own wording.

**A real, honest finding, not a formality:** given what this kernel's
evidence actually proves today, none of the four hazards reaches S3 or
S4 — `HAZ-GIP-1.14` (reverse delivery) lands at S1, fully proven zero-
harm; the other three land at S2, a residual awareness/masking gap,
not an unsafe delivered dose. But under the mandated conservative
probability default, three of four currently evaluate `Unacceptable`,
making this device's proposed overall residual risk `Unacceptable`
today — correctly surfacing that either the `system_scope` alarm-
signal proof needs building, real field data needs gathering, or
Steven's own review needs to revise the draft bands themselves, before
this device's risk profile could be considered acceptable as currently
evidenced.

**Every value added is marked `DRAFT`, throughout both documents.**
This work is a substantive starting proposal for Steven's review, not
a completed SME sign-off — the same distinction this repo has held to
since its very first Gate C6 confirmation.

## Amendment 2026-07-14 (yet later) — "Path to sign-off" section added: two of three Unacceptable hazards have no more buildable evidence at all

Direct instruction: "let's look at the evidence required in order to
ensure a safe sign off," followed by "yes, write it up as a new
section." Added a new, deliberately unnumbered section to
`RISK_MANAGEMENT_PLAN.md` (between Sections 5 and 6, since it doesn't
map to any single ISO 14971:2019 clause) answering one question
directly: what would actually resolve the three `Unacceptable` hazards
Section 5 already found.

**A real, previously-implicit finding, now stated plainly:** for two of
the three (`HAZ-DOSE-003`'s finiteness postcondition; the
`system_scope` alarm-signal gap behind `HAZ-GIP-1.2`/`1.3`), there is
no further evidence this repo can build at all — not a queue item, a
permanent boundary. `dosage.dfy`'s own header comment already
documents that Dafny's `real` type has no IEEE-754 overflow/NaN
semantics, so a "proof" of REQ-DOSE-003's finiteness would be true of
a model that can't represent the phenomenon in question — the same
class of limit as `renal_adjustment`'s CKD-EPI `Pow` gap.
`system_scope` requires an actual integrated pump system (hardware,
firmware, UI), explicitly outside a kernel-verification POC's scope
per this plan's own Section 1.

**The two real remaining paths, neither of them more spec work:** real
field/usage probability data (doesn't exist for a pre-market POC), or
a genuine ALARP determination from Steven as the named Clinical SME —
a policy judgment about accepting residual risk given exhausted
in-scope controls, not a technical question this repo's assistant can
answer or draft on his behalf. The new section is explicit that it
does not pick between these paths or pre-write a justification —
`Unacceptable` stands until one of them actually happens.

## Amendment 2026-07-15 — Finding 3/R3 resolved: severity model rebuilt consequence-only, Option 3; the `Unacceptable` finding above is superseded, not still current

**Superseded, not merely extended: this file's own two "Amendment
2026-07-14" entries above (severity bands, and the `Unacceptable`
overall-residual-risk conclusion that followed from them) describe a
severity model this repo has since found invalid and replaced.**
Preserved verbatim above per this file's own audit-trail discipline —
they're what was actually built and believed true that day — but a
reader relying on this file for current status should treat the S1/S2
values and the `Unacceptable` conclusion above as historical record,
not present fact. Current status: see `RISK_MANAGEMENT_FINDINGS.md`
and the root `README.md`'s "Risk management (ISO 14971)" section.

Direct instruction: "work through R3's severity model." R3
(`RISK_MANAGEMENT_FINDINGS.md` Finding 3) had been open since the
earlier risk-management audit this session: the severity bands built
in the "Amendment 2026-07-14 (later still)" entry above defined
severity by *evidence strength* ("S1: Dafny-proven, no harm pathway is
open") rather than consequence magnitude, contradicting ISO
14971:2019 §3.27 and directly contradicted by ISO/TR 24971 §5.5.4
("severity levels... should not include any element of probability").

Option 2 (keep the current model, justify under §7.1 NOTE 2) was
eliminated on textual grounds before asking Steven to choose — TR
§5.5.4 leaves no room for it. Presented Option 1 (pure
consequence-only) versus Option 3 (hybrid: consequence-only severity
plus an explicit per-hazard evidence-artifact column) via
`AskUserQuestion`. **Steven chose Option 3.**

**Real, cascading consequence, stated rather than hidden:** every
hazard's severity in `HAZARD_REGISTER.md` is now an explicit `GAP`,
not a regression — the old S1/S2 values above were never a valid
consequence measurement. `RISK_MANAGEMENT_PLAN.md` §4.3's acceptance
matrix, Section 5's overall-residual-risk method, and the "Path to
sign-off" section's entire argument all changed from reporting
`Unacceptable`/`Acceptable` outputs to reporting `GAP`. **This
device's overall residual risk is now `GAP`, not `Unacceptable`** —
not because it got safer, but because the prior evaluation (this
file's own "Amendment 2026-07-14 (yet later)" entry above) was never
actually computed from what ISO 14971 means by severity.

Two pre-existing staleness bugs also fixed in this pass, both
predating R3, caught while resolving it: `RISK_MANAGEMENT_PLAN.md`'s
"Path to sign-off" Step 0 and `HAZARD_REGISTER.md` Section 3 both
still said "four hazards"/"four rows," stale since `HAZ-GIP-1.2b`
split out of `HAZ-GIP-1.2`/`HAZ-GIP-1.3` (Finding 4) — this register
has held five hazard rows since that split, not four.

The concrete next step is real severity values (S1–S4) for each of the
5 hazards — Steven's clinical call, not an abstract model question
anymore. Every value marked `GAP` throughout, same discipline as every
other value this repo has never invented on Steven's behalf.

## Amendment 2026-07-15 (later) — R5 resolved: differential-testing harness built between `dosage.py` and `dosage.dfy`; a real postcondition drift found and fixed

Direct instruction: "let's look into R5 directly." `dosage.dfy`'s
header comment has always claimed to be a "Dafny translation of
dosage.py's clamping kernel" — verified this directly rather than
trusting it, before proposing any option. For every input where
`raw_dose` is finite (Dafny's `real` type has no other kind), both
implementations' branch logic is identical: `raw_dose < 0` → 0,
`raw_dose > max` → max, else → `raw_dose`.

**A real finding surfaced by that verification, not previously
flagged anywhere:** the two files' *documented* postconditions had
already drifted. `dosage.dfy`'s `ensures` clause was tightened to
strict `infusionRateMlPerHr > 0.0` back on 2026-07-07 (a Gate C5
mutation-testing finding — `>=` wasn't independently load-bearing at
`rate == 0.0` exactly). That fix was never carried back to
`dosage.py`'s own docstring `post:` line, which still said `>= 0` —
three months of silent drift between two contracts describing the same
function, in this repo's own committed artifacts. Behavior was
unaffected either way (dose is 0.0 at rate 0.0 regardless), but the
*stated* contract strength had quietly diverged, exactly the failure
mode R5 exists to guard against.

Confirmed empirically before recommending a path, not assumed: `dafny
run` actually executes concrete inputs in this environment (Dafny
4.11.0), and its output prints as clean decimals matching Python's
float format — this changed Option 2's original cost assessment from
"moderate effort, not yet attempted" to "concretely buildable now."
Steven chose **Option 2 (differential-testing harness)**, and
confirmed fixing the postcondition drift in the same pass.

**Built:**

- `dosage_differential_vectors.py` — 9 shared test vectors, the single
  source of truth both sides are checked against.
- `dosage_differential_driver.dfy`, generated by
  `generate_dosage_differential_driver.py` from those vectors — calls
  the real `CalculateHourlyDose` through Dafny's own `include`
  mechanism, not a reimplementation of its logic.
- `run_verify_dosage_differential.py` — runs the driver via real
  `dafny run`, captures raw output verbatim
  (`raw_dafny_differential_output.txt`,
  `run_manifest_dafny_differential.json`, same Gate C1 discipline as
  every other Dafny capture here), runs `dosage.py`'s real
  `calculate_hourly_dose` on the identical vectors, and writes
  `differential_test_results.json`. **All 9 vectors matched.**
- `tests/test_dosage_differential.py` — confirms the committed driver
  matches its generator, the capture shows full agreement, and
  Python's live behavior still reproduces the captured values, all
  without invoking Dafny during the test suite itself (this repo's CI
  has no Dafny/Z3 binary installed, by design).
- `dosage.py`'s postcondition tightened to `> 0`, matching
  `dosage.dfy`. Re-verified for real — CrossHair-enforced contracts
  aren't comments — clean, no new violations
  (`raw_crosshair_output.txt`, `run_manifest.json`); the full
  `generate_artifacts.py` pipeline re-run to propagate the new capture
  through every traceability matrix.

**Scope, stated explicitly, not implied:** one vector deliberately
mirrors `tests/test_dosage_concrete.py`'s own overflow case
(`overflow_negative_rate_clamps_to_zero`); both implementations agree
there too, but via genuinely different reasoning (Python: float
overflow to `-inf`, still caught by `< 0`; Dafny: the exact,
un-overflowed large value, also `< 0`). That agreement is real but
coincidental to this vector's chosen magnitudes — not a general
REQ-DOSE-003 equivalence claim, which stays structurally impossible in
Dafny's `real` type, exactly as `dosage.dfy`'s own header comment has
always said. Checked mechanically, not just stated in prose: a
dedicated test asserts the vector's own documentation says so.

251 tests pass (5 new). Full record:
`RISK_MANAGEMENT_FINDINGS.md`.

## Amendment 2026-07-15 (yet later) — Real severity scoring recorded for all 5 hazards; overall residual risk now `Unacceptable`, superseding the `GAP` conclusion above

**Superseded, not merely extended:** the "Amendment 2026-07-15" entry
above (Finding 3/R3, model-only) concluded "this device's overall
residual risk is now `GAP`, not `Unacceptable`." That was accurate at
the time — the severity **model** had been fixed, but every hazard's
severity **value** was still an explicit `GAP` pending Steven's
clinical scoring. This amendment is that scoring. Preserved above per
this file's own audit-trail discipline; a reader relying on this file
for current status should treat the `GAP` conclusion above as
historical record of an intermediate state, not present fact.

Direct instruction: "start on the severity values for the 5 hazards."
As the named Clinical SME (`RISK_MANAGEMENT_PLAN.md` Section 2), Steven
scored each of the five hazards in `HAZARD_REGISTER.md` via
`AskUserQuestion`, one at a time, against §4.1's real consequence-only
bands and each hazard's own documented `Potential harm` text — never
proposed, defaulted, or inferred by this repo's assistant.

**Result: `S3 — Serious`, all five** (`HAZ-GIP-1.14`, `HAZ-GIP-1.2`,
`HAZ-GIP-1.3`, `HAZ-GIP-1.2b`, `HAZ-DOSE-003`). Worth noting explicitly:
`HAZ-GIP-1.14` scored `S3` despite carrying this register's strongest
probability-side evidence — a full Dafny proof of exactly zero
delivered dose on any negative-rate fault. That's a concrete
demonstration, not just an abstract claim, that severity and proof
strength are genuinely independent axes — exactly the conflation
Finding 3 found and fixed in the model itself.

Mechanically applying `RISK_MANAGEMENT_PLAN.md` §4.3's
already-specified acceptance matrix to these real values (a lookup, not
a new judgment call): `HAZ-GIP-1.14`/`HAZ-GIP-1.2`/`HAZ-GIP-1.3`/
`HAZ-DOSE-003` combine `S3` with §4.2's standing `P5` worst-case default
to **`Unacceptable`**; `HAZ-GIP-1.2b` stays an evaluation `GAP`, since
its `Probability` — not its now-known `Severity` — is separately
blocked by `RISK_MANAGEMENT_FINDINGS.md` Finding 5's still-open
question. Per Section 5's combination method: **this device's overall
residual risk is now `Unacceptable`** — a real, computed result, not
the `GAP` placeholder the entry above left standing.

This is not a claim the device got less safe — it is the honest output
of a real severity input meeting this plan's already-specified,
conservative worst-case-probability policy for a pre-market POC with no
field data. The concrete next step: `RISK_MANAGEMENT_PLAN.md`'s "Path
to sign-off" section names two remaining live paths — real field/usage
probability data (doesn't exist yet), or a recorded ALARP determination
from Steven as the named Clinical SME — neither chosen yet.

253 tests pass, unchanged (no code, spec, or test change — this
amendment is documentation content only). Full record:
`RISK_MANAGEMENT_FINDINGS.md` Finding 3.

## Amendment 2026-07-15 (yet later) — Finding 6 resolved: `HAZ-GIP-1.14`'s "verbatim" GIP citation had never been checked against the primary text; a real wording drift found and fixed

Steven pressed on the S3 severity determination for `HAZ-GIP-1.14`
(reverse delivery) directly — this repo had cited GIP Safety
Requirement 1.8.1 as a direct quote, attributed to IEC 601-2-24, in
`HAZARD_REGISTER.md` and every `metadata.*.yaml` variant, but that
quote had never actually been checked against GIP v1.0's own PDF. This
repo only ever held a reformatted markdown copy
(`sources/gip-v1.0-hazard-analysis.md`), whose own header claimed
"wording... unchanged" — a claim nobody had tested.

Steven independently researched the underlying IEC citation and found
a secondary (ResearchGate-hosted) rendering of GIP's text that read
differently from this repo's version: clause order reversed, "or" vs.
"and/or," "of the equipment" present in one but not the other. Rather
than treat either source as automatically correct, the discrepancy was
flagged directly. Steven then obtained the actual GIP v1.0 PDF directly
from the University of Pennsylvania — not a third-party mirror — and
supplied it. Read directly, all 17 pages.

**Result: the secondary source was right; this repo's own
transcription was the one that had drifted.** Fixed to the verbatim
primary text ("During normal use and/or single fault condition of the
equipment, continuous reverse delivery shall not be possible") in all
six places it appeared: `sources/gip-v1.0-hazard-analysis.md`,
`metadata.yaml`/`.a`/`.b`/`.c.yaml`, `HAZARD_REGISTER.md`. The
§2.4.1 hazard-table row for HID 1.14 was checked directly too, and
matches this repo's existing citation exactly — closing that row's
long-standing "not yet independently re-verified" caveat.

**A real byproduct, now closed either way, not the original
question**: the primary PDF's hazard tables span all eight categories
and none of them carry a severity column — GIP v1.0 never rates
severity for any hazard it lists, confirmed directly rather than
inferred from `metadata.a.yaml`'s `classification_rationale` alone.
This closes the "GIP's own hazard-table severity rating" question that
was still open in the `HAZ-GIP-1.14` severity discussion.

**What this does not resolve**: the IEC 601-2-24/60601-2-24 standard's
own clause text remains unread by anyone in this chain — this repo's
evidentiary basis for this citation stays GIP v1.0 as a trusted
secondary source, one hop short of the standard itself, named
explicitly rather than silently narrowed by this fix.

No traceability matrix was hand-edited: `generate_artifacts.py`
(variants a/b/symbolic/concrete/formal) and `generate_matrix.py` (the
frozen base) were both re-run against the corrected metadata files —
every Tier 1 gate (schema validation, both CONFLICT gate types,
fact-equality, structural PROVEN sweep) passed clean.
`sources/gip-v1.0-full-2009.pdf` is now archived as this repo's
primary source for GIP v1.0. 253 tests pass, unchanged. Full record:
`RISK_MANAGEMENT_FINDINGS.md` Finding 6.

## Amendment 2026-07-15 (yet later still) — Finding 6 fully closed: IEC 60601-2-24:1998 clause 51.102 read directly, GIP's citation confirmed near-verbatim

The amendment immediately above closed a wording drift in this repo's
own GIP transcription, but explicitly left one thing open: "the IEC
601-2-24/60601-2-24 standard's own clause text remains unread by
anyone in this chain." This amendment closes that.

Steven obtained and supplied the actual IEC 60601-2-24:1998 (First
edition, 1998-02) — confirmed, again by publication-date logic (GIP,
Feb 2009, predates Edition 2's October 2012 publication by three
years), to be the correct edition GIP's authors would have cited. Read
directly and in full: 58 pages, cover through Annex ZB.

**Clause 51.102, "Reverse delivery" (p.36) — one of the few clauses in
this standard with no Annex AA rationale marker:** "During NORMAL USE
and/or SINGLE FAULT CONDITION of the EQUIPMENT, continuous reverse
delivery, which may cause a SAFETY HAZARD, shall not be possible."
Compared directly against GIP v1.0's own transcription: the match is
near-verbatim — identical clause order, "and/or," "single fault
condition of the equipment" — GIP omits only the middle clause "which
may cause a SAFETY HAZARD."

This repo's evidentiary basis for `HAZ-GIP-1.14`'s regulatory citation
is no longer GIP v1.0 as a trusted secondary source one hop short of
the standard — it is the standard's own clause text, read and archived
directly (`sources/iec-60601-2-24-1998.pdf`), with GIP's paraphrase
independently confirmed faithful to it. This is this repo's first
direct read of any IEC 60601-2-24 edition's actual text, for any
requirement.

Updated: `HAZARD_REGISTER.md`, `metadata.yaml`/`.a`/`.b`/`.c.yaml`
(clause 51.102 added to the citation), `RISK_MANAGEMENT_FINDINGS.md`
(Finding 6 fully closed), `sources/README.md`. Matrices regenerated via
`generate_artifacts.py`/`generate_matrix.py`, all Tier 1 gates passed
clean. 253 tests pass, unchanged.

## Amendment 2026-07-20 — Gate C5 moved onto the sanctioned isolated runner

`run_mutation_suite.py` no longer carries its own
generate/classify/verify loop; it now calls
`evidence/gate_c5_runner.py::mutants_with_outcomes`, the single
sanctioned Gate C5 entry point, passing `CalculateHourlyDose` as the
clause target and `ExpectedDose` as `body_function` (the method+companion
shape). Every mutant that reaches Dafny is now verified in **isolation** —
`CalculateHourlyDose` plus its `ExpectedDose` callee (so the pinning
`ensures dose == ExpectedDose(...)` stays in the unit and a mutated body
is still caught), never a caller.

`CalculateHourlyDose` has no in-file callers, so isolation coincides with
whole-file verification here: the regenerated `mutation_report.json`
carries the **same 56 mutants and identical outcome counts** (41 killed,
15 filtered across the four filter buckets, 0 survived, 0 unclassifiable)
as before — confirmed by diffing the report record-for-record: the only
additions are the `function` and `isolation_status: "isolated"` fields on
each record, with zero outcome or detail drift. The value is the
guarantee, now recorded and test-pinned
(`tests/test_mutation_report.py::test_every_verified_mutant_was_isolated`),
that a future function-with-callers can't silently reintroduce the
caller-confound. `mutation_report.md` and `run_manifest_mutation.json`
regenerated to match.

## Amendment 2026-07-20 (Tier 3) — Component F: frozen-contract integrity gate piloted here

Tier 3 of the "PROVEN ≠ meaningful" work (structural separation) is
piloted on this example. A `PROVEN` label is only trustworthy if the
contract that was proven wasn't itself gamed to be provable —
`evidence/frozen_contract.py` freezes this spec's human-authored
**contract surface** (per declaration: signature + `requires` +
`ensures`, plus `ExpectedDose`'s body, which *is* spec) as a committed,
drift-checked manifest, `frozen_contract.yaml`, and proves any candidate
`.dfy` preserves it exactly and adds no soundness escape
(`assume`/`{:axiom}`/`{:extern}`). `CalculateHourlyDose`'s method body is
**not** frozen — it's the implementation, where honest proof scaffolding
(`assert`/`invariant`/`decreases`) lives. This is an *integrity*
guarantee (the contract wasn't altered by an automated contributor —
drafter≠checker applied to the spec itself), **not** a correctness one;
correctness stays with Gates C1–C6.

Two new honesty exhibits (same discipline as `dosage_underconstrained.dfy`
and `dosage_naive_widening.py`) show the checker catching what Dafny
accepts:

- **`dosage_assume_escape.dfy`** — the frozen contract surface is
  *identical* to `dosage.dfy` (same `ExpectedDose`, same signature/
  requires/ensures), but the implementation is wrong and `assume false;`
  forces Dafny to accept it: `raw_dafny_output_assume_escape.txt` reports
  `2 verified, 0 errors` (and `dafny verify --allow-warnings` gives a
  clean exit-0, so Dafny's own soundness *warning* on the assume is not a
  robust guard). `check_contract` returns **CONTRACT_VIOLATED** on the
  forbidden `assume` — the escape the contract-surface diff alone cannot
  see.
- **`dosage_scaffolded.dfy`** — identical contract, correct
  implementation, plus an inert whitelisted `assert`. Dafny verifies and
  the checker returns **CONTRACT_INTACT** — the control proving the gate
  doesn't cry wolf on honest scaffolding.

Paired with the existing `dosage_underconstrained.dfy` (weakened
`ensures`, `1 verified, 0 errors`, checker **CONTRACT_VIOLATED** on the
dropped pinning clause) and the real spec (checker **CONTRACT_INTACT**),
this is the full four-case verified outcome, pinned in
`tests/test_frozen_contract.py`. It is the first concrete mitigation of
the long-BLOCKED Vector-4 "specification stripping" concern in
`KNOWN_LIMITATIONS.md`. Extension to the other three examples, and the
frozen-spec authoring migration, are deferred.
