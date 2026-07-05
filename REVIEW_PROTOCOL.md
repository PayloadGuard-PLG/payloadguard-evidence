# REVIEW_PROTOCOL — payloadguard-evidence

Established 2026-07-05 (Turn 2.0 B3, ruling Q3). Governs how generated
traceability artifacts are reviewed before any use in a real submission.

## The two tiers

**Tier 1 — machine gates (defect path).** Two structural checks run at
generation time and in the test suite:

1. Fact-equality gate (`evidence/reconcile.py::run_gate`,
   `tests/test_fact_equality.py`): all variant views must carry identical
   normalized facts, identical requirement-scoped `intent_ok`, and an
   identical bounds block; the frozen base matrix must equal the symbolic
   subset.
2. Structural PROVEN check
   (`evidence/render/matrix_variants.py::assert_no_realized_proven`,
   `tests/test_structural_proven_check.py`): no realized strength may be
   `PROVEN` in any record or rendered cell.

A Tier 1 failure is a **defect, never a judgment call**: generation or CI
stops, the failure is escalated to the maintainer, and it is resolved by
fixing the code, metadata, or evidence that caused it — **never by editing
a generated artifact**. Generated artifacts are outputs; hand-editing one
to make a gate pass is falsification.

**Tier 2 — human review (regulatory path).** With Tier 1 green, human
review is **per-reason**: the reviewer walks the structured findings below,
not the artifacts wholesale.

Note on scope: a policy of "review only when the validators disagree" is
void by construction — Tier 1 makes fact disagreement impossible in shipped
artifacts, so such a policy would mean nothing is ever reviewed. That
contradicts this repository's founding constraint: every generated claim is
reviewed by a human before it enters a real submission.

## Tier 2 reviewable reason classes

Each class points at its structured source; reasons are fields, not prose
to be rediscovered.

| Reason class | Where to look |
|---|---|
| Intent mismatches | rows with `intent_ok: false` and their notes (e.g. `intended PROVEN, realized BOUNDED_CHECKED, EXAMPLE_CHECKED`) |
| GAP rows | rows whose strength is `GAP` (no evidence bound; currently none) |
| DECLARED-strength records | metadata fields marked DECLARED (e.g. safety classification rationale, REQ-DOSE-003 provenance) |
| Bounds block | each matrix's `bounds` field: declared (intent) vs effective (demonstrated) plus the enforcement note (`max_iterations`/`seed` not CLI-enforceable at crosshair-tool 0.0.107) |
| Honesty exhibits | `exhibit_pin_naive_widening.json` / `exhibit_pin_overflow_probe.json` — the paired measurement scoping what BOUNDED_CHECKED can miss; claims are version-contingent |
| Open reconciliation asymmetries | `examples/dosage_calculator/RECONCILIATION.md` — currently: binding authorship (deferred to Phase B) |

## Not reviewable as findings

Shape and presentation divergence between variant artifacts (row counts,
grouping, note placement, evidence-list vs shadow-row vs dual-matrix form)
is documented design, not a finding — see RECONCILIATION.md. Raising it as
a review finding is a category error; raising a **fact** divergence is
moot, because Tier 1 already stopped the line.

## Escalation path (Tier 1 failures)

1. Generation or suite fails with the gate's assertion message.
2. Do not commit, do not edit generated artifacts, do not re-roll captures
   hoping for a different result.
3. Identify the layer at fault: capture (manifest/raw output), metadata,
   binder/renderer code, or a genuinely divergent evidence fact.
4. Fix at that layer; regenerate via the sanctioned entrypoint
   (`examples/dosage_calculator/regenerate_all.py`); confirm the suite is
   green; record the episode in DEVLOG.md with the failing assertion
   verbatim.
