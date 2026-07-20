# Generic AEB Kernel — Audit-Trail Record

Fourth proof-of-concept for the PayloadGuard evidence layer, and the
first outside the medical-device domain: a generic (not manufacturer-
specific) light-vehicle Automatic Emergency Braking system's speed-
envelope and deceleration-threshold requirements, verified with the same
Gate C1–C6 Dafny/Z3 pipeline built for `dosage_calculator/`,
`renal_adjustment/`, and `drug_interaction_checker/` — built to test
whether that architecture generalizes to a new regulatory domain
(automotive functional safety, NHTSA), not to evaluate any specific
commercial vehicle or manufacturer.

This file is the fixed audit-trail record — source citations,
interpretive-call caveats, and dated amendments. For **current, living
status**, see `PHASE1_PLAN.md` and the repository root's `HANDOFF.md`;
this file doesn't duplicate that and isn't kept in lockstep with it turn
by turn.

## Why this domain, and why "generic"

Direct instruction: find a component testable against public
information and regulations, in a new domain, to prove the Gate C1–C6
architecture isn't dosage-calculator-specific. An uploaded research
document initially framed this around a named commercial vehicle;
reframed on request to a generic AEB kernel before any spec content was
written — naming a specific manufacturer's product would have been a
real sourcing and reputational risk (this repo's evidence is only as
good as its primary sources, and no OEM-specific AEB implementation
detail is public), and the point of the exercise was the architecture,
not any one company's system.

## Source documents

| Document | Role |
|---|---|
| NHTSA/DOT Final Rule, "Automatic Emergency Braking Systems for Light Vehicles," 49 CFR Parts 571, 595, 596, Docket No. NHTSA-2023-0021, RIN 2127-AM37 (2024) | The entire spec — every REQ-AEB-* below traces to § 571.127's codified text (S4 definitions, S5 requirements), read directly (PDF pages ~277-283 of a 317-page document, located by `pdftotext -layout` + line search after confirming the first ~300 pages are rulemaking preamble, not codified text). Archived as `sources/nhtsa-fmvss-127-2024.pdf`, added directly by Steven from the Federal Register (confirmed via a screenshot of the document's own title page before archiving). |

No secondary source was used for any requirement text — the full
codified section (S1 Scope through S10) was read via the `Read` tool
before this file's header comment or `aeb_kernel.dfy` were written, per
this repo's standing sourcing discipline.

## Requirement-to-source mapping

| ID | Requirement | Built? |
|---|---|---|
| `REQ-AEB-1` | FCW required, lead vehicle: 10 < speed < 145 km/h (S5.1.1) | `FCWRequiredActive` — proven |
| `REQ-AEB-2` | AEB required, lead vehicle: 10 < speed < 145 km/h (S5.1.2) | `AEBRequiredActive` — proven |
| `REQ-AEB-3` | FCW required, pedestrian: 10 < speed < 73 km/h (S5.2.1) | `FCWRequiredActive` — proven |
| `REQ-AEB-4` | AEB required, pedestrian: 10 < speed < 73 km/h (S5.2.2) | `AEBRequiredActive` — proven |
| `REQ-AEB-5` | Subject vehicle braking onset: decel >= 0.15g (S4) | `IsSubjectVehicleBrakingOnset` — proven |
| `REQ-AEB-6` | Lead vehicle braking onset: decel >= 0.05g (S4) | `IsLeadVehicleBrakingOnset` — proven |
| `REQ-AEB-7` | Brake pedal application onset: force >= 11 N (S4) | `IsBrakePedalApplicationOnset` — proven |
| `REQ-AEB-8` | False activation: peak additional decel < 0.25g (S5.3) | `IsFalseActivationCompliant` — proven |
| `REQ-AEB-9` | Vehicle-class eligibility, GVWR <= 4,536 kg (S3) | Prose only — not a kernel proof target (system_scope) |
| `REQ-AEB-10` | Malfunction detection and mode controls (S5.4) | Prose only — not a kernel proof target (system_scope, stateful) |

Full requirement text: `metadata.a.yaml`. Full plain-English contract
review: `nl_confirmation_aeb_kernel_dfy.md`.

## Structural finding worth naming explicitly

§ 571.127's actual performance obligations (S5) are entirely **speed-
envelope and deceleration-threshold** based — no wall-clock timing
appears anywhere in S5. The document's millisecond/second-level timing
figures (500 ms accelerator-pedal release, 1.0 ± 0.1 s brake-application
onset) are all in S7/S8 — NHTSA's own **test-conduct** procedure for
verifying compliance on a track, not a claim the vehicle's AEB system
itself must always satisfy. This meant the open design question carried
into this build (model the standard's "10 ms"-class timing as an
`elapsedMs: nat` parameter, or split it into an unprovable
`system_scope` claim, per the AEB planning discussion) resolved itself
once the real text was read: neither was needed. Unlike
`dosage_calculator`'s IEEE-754 gap or `renal_adjustment`'s `Pow`-exponent
gap, this domain's core requirements hit no Dafny/Z3 structural
expressiveness limit at all.

## Interpretive-call caveats

1. **FCW and AEB are numerically identical envelopes but distinct legal
   obligations.** S5.1.1 (FCW, lead vehicle) and S5.1.2 (AEB, lead
   vehicle) both use `10 < speed < 145`; S5.2.1/S5.2.2 (pedestrian) both
   use `10 < speed < 73`. Confirmed by reading both clause pairs
   directly, not assumed from the shared numbers — kept as two separate
   functions (`FCWRequiredActive`, `AEBRequiredActive`) so the
   traceability matrix shows two requirements independently met, not
   one requirement counted twice.
2. **Boundary direction differs across functions, and this matters.**
   The S5.1/S5.2 speed envelopes and S5.3's false-activation limit are
   all strict inequalities (`<`, excluding the boundary itself); the S4
   onset definitions ("achieves a deceleration of X g", "when Y N of
   force has been applied") are inclusive (`>=`, the boundary itself IS
   the onset point). Both directions are STP-tested explicitly at their
   exact boundary value (Gate C4) — getting either backwards would be
   exactly the kind of off-by-one this gate exists to catch.
3. **S5.3's compliance condition is a negated violation clause.** The
   source states the *violation* ("exceeds... by 0.25 g or greater");
   `IsFalseActivationCompliant`'s `< 0.25` is that statement's logical
   negation, not an independently-sourced compliance threshold — worth
   naming since it's the one function in this spec whose boundary
   direction is easy to get backwards by reading too quickly.
4. **S3 (vehicle-class eligibility) and S5.4 (malfunction detection/mode
   controls) are named, sourced, and deliberately not formalized here.**
   S3 is a fleet/homologation-level gate on whether § 571.127 applies to
   a given vehicle at all, not a claim this kernel's per-event logic
   needs to satisfy. S5.4 is a genuinely different *kind* of claim —
   continuous state across ignition cycles, not a pure function of one
   detection event's inputs — and would need a state-machine modeling
   approach this kernel doesn't currently use anywhere else, not a
   smaller version of the same kind of proof. Both render as honest
   `GAP` rows via `metadata.a.yaml`'s `system_scope` field, mirroring
   `dosage_calculator`'s REQ-GIP-1-4-12 kernel_scope/system_scope split.

## Fixture and capture formats

Mirrors `renal_adjustment/`'s discipline: every capture below is the
verbatim output of a real, installed Dafny 4.11.0 / Z3 run — none is
hand-typed.

- **`aeb_kernel.dfy`** — the committed spec, six functions
  (`FCWRequiredActive`, `AEBRequiredActive`,
  `IsSubjectVehicleBrakingOnset`, `IsLeadVehicleBrakingOnset`,
  `IsBrakePedalApplicationOnset`, `IsFalseActivationCompliant`).
  Captured by `run_verify_aeb.py` → `raw_dafny_output_aeb.txt` /
  `run_manifest_dafny_aeb.json` (6 verified, 0 errors).
- **`nl_confirmation_aeb_kernel_dfy.md`** — Gate C6, run immediately
  after the spec first verified clean (before STPs/mutation testing),
  per this repo's own established best practice. All six functions'
  contracts checked against § 571.127's text directly and confirmed.
  **Confirmed, 2026-07-16.**
- **`aeb_kernel_stp_suite.dfy`** — Gate C4: 31 Spec-Testing Proof
  lemmas, boundary-value ACCEPT/REJECT pairs for every strict/inclusive
  threshold in the spec. Runner: `run_verify_dafny_stp_suite_aeb.py` →
  `raw_dafny_output_stp_suite_aeb.txt` /
  `run_manifest_dafny_stp_suite_aeb.json` (31 verified, 0 errors).
- **`run_mutation_suite_aeb.py`** / **`mutation_report_aeb.json`/`.md`**
  / **`run_manifest_mutation_aeb.json`** — Gate C5: 63 mutants, 38
  killed, 12 filtered_static, 5 filtered_magnitude_implied, 4 survivors
  (all `IsFalseActivationCompliant`'s non-negativity precondition being
  weakened — real, but not load-bearing for the current single ensures
  clause, same category as `renal_adjustment`'s documented survivors),
  4 unclassifiable (COI generator can't negate a `target == X ==>` guard
  clause — "invalid UnaryExpression" — a real, named
  `evidence/dafny_mutate.py` engine gap, same class as
  `renal_adjustment`'s documented `||`-chain limitation, not silently
  worked around). Full detail: `tests/test_aeb_kernel_mutation_report.py`.
- **`metadata.a.yaml`**, **`dafny_captures_index.json`**,
  **`traceability_matrix.a.json`/`.md`** — Phase 3: 8 real `PROVEN` rows
  (two requirement pairs, REQ-AEB-1/3 and REQ-AEB-2/4, each sharing one
  proof — mirroring `drug_interaction_checker`'s established
  many-requirements-to-one-proof pattern), 2 honest `GAP` rows
  (REQ-AEB-9/10). Built via `python -m evidence.cli build --variant a`,
  omitting `--manifest`/`--concrete` entirely (no crosshair/concrete_test
  evidence exists in this metadata, same as `renal_adjustment`/
  `drug_interaction_checker`). Full detail:
  `tests/test_aeb_kernel_matrix.py`.

## Amendment 2026-07-16 (later) — ISO 26262-3 sourced (partially) and `HAZARD_REGISTER.md` built

Sourcing this domain's risk-management standard turned into its own
verification saga, worth recording. `sources/ISO-26262-3-2018.pdf`
(the iTeh preview, Clauses 1–5 only) landed first, missing exactly the
clauses needed (6 and 7). A pasted secondary-source summary of those
clauses was checked directly and found wrong: its "workflow steps"
didn't match the real clause structure already read from the preview's
own table of contents, and its ASIL determination matrix disagreed with
independent public sources on multiple cells. A follow-up "resolution"
message claiming an absolute "C1 always defaults to QM" rule was
directly falsified — both by the real primary text eventually found,
and by the fact that it contradicted the original pasted table's own
first version.

The real Table 4 (ASIL determination) and Clause 6.4.4 (Determination
of safety goals) were then found for free and archived:
`sources/iso-26262-3-2018-table4-and-6.4.4.md`, sourced from a 2-page
PDF (page 10 of the actual standard) bundled as a regression-test
fixture in the open-source PyMuPDF library's test suite, cross-verified
authentic against the preview's own table of contents. Steven's
explicit scope call: this is a proof-of-concept for review, not a real
regulatory submission, so paying for the full standard to source two
clauses wasn't warranted once a real, independently-verifiable free
source existed. Full account: `DEVLOG.md`'s 2026-07-16 (later) entry.

`HAZARD_REGISTER.md` built the same session, using what's now sourced:
10 hazard entries, one per `REQ-AEB-*`. Severity/Exposure/
Controllability/ASIL left explicit `GAP` — Table 4 makes the *lookup*
possible once S/E/C are known, but the HARA methodology clause (6.4.2)
that defines how to derive E and C from an operational situation is
still unsourced, and no automotive-safety reviewer has been named
(the domain-equivalent of the three ISO 14971 registers' clinical-SME
gap).

## Open questions

Not resolved here — named, not guessed at:

1. **REQ-AEB-9/10's Dafny formalization** would need a genuinely
   different modeling approach (a state machine for S5.4's mode
   controls; a vehicle-class eligibility gate that's arguably outside
   what a per-event AEB kernel should even model) — real future work,
   not scoped here.
2. **This is a proof-of-concept, not a production AEB implementation.**
   Real vehicle sensor fusion, perception, and control-loop code is
   vastly more complex than these eight boolean predicates — the point
   of this example is that the Gate C1–C6 evidence architecture
   generalizes to a new domain's real, numeric, citable requirements,
   not that this kernel is a complete AEB system.

## Amendment 2026-07-20 — proof-content qualifier: all 8 rows are definitional

`evidence/spec_impl_gap.py` (Gate C3 vector 3) now classifies each proven
`ensures` clause as **definitional** (restates the body) or **property**
(strictly weaker than the body). Every one of aeb_kernel's 8 `PROVEN` rows
is **definitional**: each function's `ensures` is `F(args) <==> E` with body
`E` (the FCW/AEB speed envelopes are `match`-per-target, the onset predicates
are single comparisons), so the proof obligation is `E <==> E`, discharged by
reflexivity — every clause is Z3-confirmed to pin its result uniquely.

What the 8 `PROVEN` rows therefore certify is real but bounded: **totality,
type-safety, `match`-exhaustiveness, and the literal boundary structure**
(`<` vs `<=`, and the exact numbers 10/145/73/0.15/0.05/11/0.25) — the same
scope Gate C4's STP suite pins. They do **not** certify an independent
property beyond the definition, nor that those numbers faithfully transcribe
§571.127 (a separate, still-open fidelity question — see the root
`README.md`'s "In progress and designed" note). The `traceability_matrix.a.json`
rows now carry `proof_content: "definitional"` with the matching caveat.
