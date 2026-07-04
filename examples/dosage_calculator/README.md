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
| `REQ-GIP-1-8-1` | Safety Requirement 1.8.1 (no continuous reverse delivery, citing IEC 601-2-24); mitigates Hazard 1.14 | Interpretive mapping — see caveat 1 below |
| `REQ-DOSE-003` | **DECLARED, no GIP source** | See caveat 2 below |

## Interpretive-call caveats

Carried verbatim from the metadata extraction; do not smooth these over:

1. `REQ-GIP-1-8-1` (reverse delivery) is mapped to the kernel's
   non-negativity postcondition. This is an interpretive correspondence
   (the source hazard is about physical backward flow; the postcondition
   is a mathematical bound on a returned value), not a direct restatement.
   Flag it as such.
2. `REQ-DOSE-003` has no GIP source at all — GIP v1.0 does not address
   floating-point overflow. It is DECLARED engineering judgement.
3. Hazards HID 1.1, 1.4, 1.5, 1.10 and Safety Requirements 1.2.2/1.2.3
   (flow-rate-deviation-over-15-minutes) were deliberately excluded from
   this metadata — they describe a stateful, time-windowed sensor model,
   not a pure function, and don't fit this kernel. Note them in the
   README as a candidate second kernel, not as an oversight.

## Deliberately excluded hazards — candidate second kernel

HID 1.1 (programmed flow rate too high), 1.4 (incorrect drug
concentration), 1.5 (programmed flow rate too low), 1.10 (flow rate does
not match programmed rate), and Safety Requirements 1.2.2/1.2.3 (flow-rate
deviation sustained over 15 minutes) require a stateful, time-windowed
model of sensed versus programmed flow. They are out of scope for this
pure-function kernel by design, not by oversight. A second kernel modelling
windowed flow-rate deviation is the natural next example if this layer is
extended.

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

Two fixture pairs are committed, both captured by actually running
CrossHair (`crosshair-tool 0.0.107`, Python 3.11) — neither file is
hand-written.

### Sample A — clean (`dosage.py`)

Produced by `python3 run_verify.py`.

- `raw_crosshair_output.txt` — verbatim stdout+stderr of
  `crosshair check dosage.py --report_all`. Content for this capture:
  a single `info: Not confirmed.` line for the postcondition. With
  `--report_all`, CrossHair reports `Not confirmed` when its bounded
  search ends without finding a counterexample and without exhausting
  all paths — precisely the evidence class `BOUNDED_CHECKED` encodes.
  It is not a proof.
- `run_manifest.json` — JSON object with keys `tool`, `tool_version`,
  `command` (argv list), `exit_code` (0 = no counterexample found),
  `started_utc` (ISO-8601 UTC), `target`.

### Sample B — broken (`dosage_broken.py`)

Produced by `python3 run_verify_broken.py` (a duplicate of
`run_verify.py` retargeted at the clamp-free variant, kept separate so
`run_verify.py` stays identical to the reviewed original).

- `raw_crosshair_output_broken.txt` — verbatim capture containing a
  postcondition-violation line with a concrete counterexample:
  `error: false when calling calculate_hourly_dose(1.0, 2.0, 0.5, 0.25)
  (which returns 1.0)` — 1.0 mg/hr exceeds the 0.25 mg/hr maximum, as
  expected once the clamp is removed.
- `run_manifest_broken.json` — same manifest shape, `exit_code` 1.

### Known bounds divergence (flagged, not smoothed over)

`metadata.yaml` declares `toolchain.crosshair_bounds`
(`per_condition_timeout_s: 30`, `max_iterations: 100000`, `seed: 1`), and
the traceability matrix reports those declared bounds. The capture
command specified by this phase (`crosshair check <target> --report_all`)
passes no bounds flags, so the actual runs used CrossHair's defaults. The
declared bounds are therefore the *intended* verification envelope, not
yet the demonstrated one. The Phase-B adapter/binder should either pass
the declared bounds to the CrossHair invocation or record the effective
bounds in the manifest, and reconcile the two.

## Matrix generation

`traceability_matrix.json` / `traceability_matrix.md` are generated —
not hand-typed — by `python3 generate_matrix.py`, which reads the Sample A
manifest and raw output, constructs a `VerificationResult`, and runs
`evidence.render.manual_matrix.build_traceability_matrix` against
`metadata.yaml`. Strength in every row comes only from the verification
result (`BOUNDED_CHECKED`); the two requirements whose `intended_method`
is `PROVEN` are correctly reported with `intent_ok: false`, because Dafny
is not wired in this phase and nothing in this repository claims `PROVEN`.
