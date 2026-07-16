# Generic AEB Kernel — Phase 1 (Specification & Foundation)

Status: **Built end to end in one session, 2026-07-16.** All six Gate
C1–C6 pipeline steps built AND confirmed, plus Phase 3 (evidence
packaging). This is this repo's fourth worked example and its first
outside the medical-device domain — see `README.md` for the full
audit-trail record (source documents, interpretive-call caveats,
structural findings) and `KNOWN_LIMITATIONS.md` for how this changes the
repo's live gate ledger.

## What's built

- **`aeb_kernel.dfy`** — 6 functions, 8 requirement clauses total
  (`FCWRequiredActive`/`AEBRequiredActive` each carry two requirements —
  lead vehicle and pedestrian). `6 verified, 0 errors` against real
  Dafny 4.11.0. Every requirement traces directly to § 571.127's
  codified text, read via the `Read` tool before any spec content was
  written — no paraphrase, no secondary source.
- **Gate C1** (capture): `run_verify_aeb.py` →
  `raw_dafny_output_aeb.txt` / `run_manifest_dafny_aeb.json`.
- **Gate C6** (NL confirmation, run immediately after the spec first
  verified clean, per this repo's own established best practice for a
  brand-new spec): `nl_confirmation_aeb_kernel_dfy.md`, all six
  functions' contracts checked against the source text directly.
  **Confirmed, 2026-07-16.**
- **Gate C4** (STPs): `aeb_kernel_stp_suite.dfy`, 31 lemmas, every
  strict/inclusive boundary in the spec tested at its exact value plus
  one step inside/outside. `31 verified, 0 errors`.
- **Gate C3** (spec lint): all 6 functions `sat` (vector 1, no vacuous
  preconditions), 0 weak-postcondition warnings across all 6 (vector 2 —
  every ensures clause is a full bi-implication, not a bare one-way
  `==>`, confirmed empirically). `tests/test_aeb_kernel_spec_lint.py`.
- **Gate C5** (mutation testing): `run_mutation_suite_aeb.py`, 63
  mutants — 38 killed, 12 filtered_static, 5 filtered_magnitude_implied,
  4 survived (all `IsFalseActivationCompliant`'s non-load-bearing
  non-negativity precondition, explained), 4 unclassifiable (a real,
  named `evidence/dafny_mutate.py` COI-generator gap negating
  `target == X ==>` guard clauses — "invalid UnaryExpression"). Locked
  in by `tests/test_aeb_kernel_mutation_report.py`.
- **Phase 3** (evidence packaging): `metadata.a.yaml`,
  `dafny_captures_index.json`, `traceability_matrix.a.json`/`.md` — 8
  `PROVEN` rows (REQ-AEB-1/3 sharing `FCWRequiredActive`'s proof,
  REQ-AEB-2/4 sharing `AEBRequiredActive`'s — the
  many-requirements-to-one-proof pattern `drug_interaction_checker`
  established), 2 honest `GAP` rows (REQ-AEB-9/10, both carrying a real
  `system_scope` field rather than an empty evidence array).
  `tests/test_aeb_kernel_matrix.py`, 7 tests.

## Requirement inventory

| REQ ID | Source clause | Dafny target | Status |
|---|---|---|---|
| REQ-AEB-1 | S5.1.1 (FCW, lead vehicle) | `FCWRequiredActive` | PROVEN |
| REQ-AEB-2 | S5.1.2 (AEB, lead vehicle) | `AEBRequiredActive` | PROVEN |
| REQ-AEB-3 | S5.2.1 (FCW, pedestrian) | `FCWRequiredActive` | PROVEN |
| REQ-AEB-4 | S5.2.2 (AEB, pedestrian) | `AEBRequiredActive` | PROVEN |
| REQ-AEB-5 | S4 (subject vehicle braking onset) | `IsSubjectVehicleBrakingOnset` | PROVEN |
| REQ-AEB-6 | S4 (lead vehicle braking onset) | `IsLeadVehicleBrakingOnset` | PROVEN |
| REQ-AEB-7 | S4 (brake pedal application onset) | `IsBrakePedalApplicationOnset` | PROVEN |
| REQ-AEB-8 | S5.3 (false activation) | `IsFalseActivationCompliant` | PROVEN |
| REQ-AEB-9 | S3 (vehicle-class eligibility) | none — `system_scope` | DECLARED, GAP |
| REQ-AEB-10 | S5.4 (malfunction detection/mode controls) | none — `system_scope` | DECLARED, GAP |

## Still open

1. **REQ-AEB-9/10's own Dafny formalization** is real future work, not
   scoped for this build — S5.4 in particular needs a state-machine
   modeling approach (continuous state across ignition cycles) this
   kernel doesn't use anywhere else, a genuinely different kind of claim
   than REQ-AEB-1..8, not a smaller version of the same kind.
2. **No ISO 26262 (automotive functional safety) risk-management
   artifacts exist for this example, and the source needed to build
   them is only partially in hand.** `sources/ISO-26262-3-2018.pdf`
   (added 2026-07-16) is the iTeh "STANDARD PREVIEW" excerpt — 12 of a
   real ~28+ page document, covering Clauses 1–5 (Scope through Item
   definition) but **not** Clause 6 (Hazard analysis and risk
   assessment) or Clause 7 (Functional safety concept) — exactly the
   two clauses that would play the role ISO 14971 played for the three
   medical-device examples' hazard registers/risk-management plans.
   Steven's explicit decision (`AskUserQuestion`, 2026-07-16): get the
   full Clause 6/7 text before building any ISO 26262 artifact, rather
   than build on the partial source or leave the gap unremarked. Full
   detail: `sources/README.md`'s `ISO-26262-3-2018.pdf` entry.
3. **This is a proof-of-concept kernel, not a production AEB
   controller.** See `README.md`'s "Open questions" for the full framing.
