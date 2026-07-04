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
| `REQ-GIP-1-4-12` | Safety Requirement 1.4.12 (bolus dose limit alarm); mitigates Hazards 1.2, 1.3 | Direct restatement |
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
2. **CrossHair did not find it.** The capture shows exit code 0 and
   `Not confirmed` for both postconditions — the bounded search missed
   a real, reachable violation within its default bounds. This is the
   clearest in-repo demonstration of why `BOUNDED_CHECKED` must never
   be presented as proof, and why this repository's claims discipline
   forbids exactly that. A "no counterexample found" result on the
   fixed `dosage.py` is evidence of absence-within-bounds, nothing
   stronger.

**Post-amendment evidence that the widened domain is really explored:**
the Sample B (broken variant) capture now contains a second, negative
counterexample — `calculate_hourly_dose(0.5, 0.25, -0.125, 0.125)`
returning `-0.03125` — showing CrossHair genuinely drives negative rates
through the contract after the widening.

## Open question — `FRN` pump-type tag: UNRESOLVED

The GIP v1.0 hazard tables tag many hazards with pump type `FRN` (e.g.
Hazard 1.14, referenced by `THR-GIP-1-14`) without defining the
abbreviation in the extracted text. Resolution was attempted during this
session (web search for the GIP project pages and companion documents;
direct retrieval of `rtg.cis.upenn.edu/gip-UPenn/` and the UPenn
`cis_reports/893` tech-report page failed — host unreachable / HTTP 403
from this environment). No companion document defining `FRN` was found.
The meaning is therefore **not inferred**: `THR-GIP-1-14` records only
that the tag denotes a source-defined pump subtype distinct from the
"All" category. If a future source added to `sources/` defines it, update
this section and `sources/README.md` per the standing rule.

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
(`exit_code` 0, both postconditions `Not confirmed`).

### Known bounds divergence (flagged, not smoothed over)

`metadata.yaml` declares `toolchain.crosshair_bounds`
(`per_condition_timeout_s: 30`, `max_iterations: 100000`, `seed: 1`), and
the traceability matrix reports those declared bounds. The capture
command specified by Phase A (`crosshair check <target> --report_all`)
passes no bounds flags, so the actual runs used CrossHair's defaults. The
declared bounds are therefore the *intended* verification envelope, not
yet the demonstrated one. Constraint noted for the pending decision:
crosshair-tool 0.0.107's CLI can enforce only `--per_condition_timeout`;
it has no flags for `max_iterations` or `seed`. The Phase-B
adapter/binder should reconcile declared and effective bounds. The
Sample C result above makes this divergence more than cosmetic: bounds
determine what a bounded search can miss.

## Matrix generation

`traceability_matrix.json` / `traceability_matrix.md` are generated —
not hand-typed — by `python3 generate_matrix.py`, which reads the Sample A
manifest and raw output, constructs a `VerificationResult`, and runs
`evidence.render.manual_matrix.build_traceability_matrix` against
`metadata.yaml`. Strength in every row comes only from the verification
result (`BOUNDED_CHECKED`); the two requirements whose `intended_method`
is `PROVEN` are correctly reported with `intent_ok: false`, because Dafny
is not wired in this phase and nothing in this repository claims `PROVEN`.
