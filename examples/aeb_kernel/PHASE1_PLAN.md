# Generic AEB Kernel — Phase 1 (Specification & Foundation)

Status: **Built end to end in one session, 2026-07-16.** All six Gate
C1–C6 pipeline steps built AND confirmed, plus Phase 3 (evidence
packaging). This is this repo's fourth worked example and its first
outside the medical-device domain — see `README.md` for the full
audit-trail record (source documents, interpretive-call caveats,
structural findings) and `KNOWN_LIMITATIONS.md` for how this changes the
repo's live gate ledger.

**`HAZARD_REGISTER.md` built, 2026-07-16 (later).** 10 hazard entries
(one per `REQ-AEB-*`), fourth hazard register in this repo and its
first ISO 26262-informed one. Hazard identification is real, drawn from
sourced requirement text and real Dafny captures. Severity/Exposure/
Controllability/ASIL left explicit `GAP` throughout — not blocked only
by the absence of a named automotive-safety reviewer (as with the three
ISO 14971 registers' clinical-SME gap), but doubly blocked: the HARA
methodology clause (§ 6.4.2) that defines how to derive E and C from an
operational situation isn't sourced either, only Table 4's lookup
mechanism and § 6.4.4's safety-goal-statement rules are. See
`HAZARD_REGISTER.md` itself for the full reasoning.

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
   artifacts exist for this example yet, and the source is now
   partially — not fully — in hand.** `sources/ISO-26262-3-2018.pdf`
   (the iTeh "STANDARD PREVIEW" excerpt, Clauses 1-5 only) plus
   `sources/iso-26262-3-2018-table4-and-6.4.4.md` (added 2026-07-16,
   later — verbatim Table 4 "ASIL determination" and Clause 6.4.4
   "Determination of safety goals," obtained via an independent, free,
   legitimate source and cross-verified against the first file's own
   table of contents). Together these cover the actual *computation*
   rules (the S×E×C→ASIL lookup table, the safety-goal assignment
   rules) but **not** the HARA *methodology* (6.4.1 Initiation, 6.4.2
   Situation analysis and hazard identification, 6.4.3.1–.10
   classification procedure, 6.4.6 Verification) or Clause 7
   (Functional safety concept — FSR derivation). Steven's explicit
   scope call, 2026-07-16: this is a proof-of-concept testing
   architecture generalization, not a real regulatory submission, so
   paying for the full standard wasn't warranted once real, verbatim,
   independently-verifiable text for the operationally load-bearing
   clauses was found for free. A first-pass `HAZARD_REGISTER.md`-style
   artifact is buildable from what's now sourced (classify each
   REQ-AEB-* hazard's S/E/C, look up its real ASIL via Table 4, state
   its safety goal per 6.4.4's rules); the methodology/FSR-derivation
   clauses remain a named gap for any future extension. Full detail:
   `sources/README.md`'s `ISO-26262-3-2018.pdf` and
   `iso-26262-3-2018-table4-and-6.4.4.md` entries, `DEVLOG.md`'s
   2026-07-16 entry.
3. **This is a proof-of-concept kernel, not a production AEB
   controller.** See `README.md`'s "Open questions" for the full framing.
