# Reconciliation Note — T4 Variants A / B / C

All three variants are generated from the identical underlying evidence:
the Sample A CrossHair capture (`run_manifest.json`,
`raw_crosshair_output.txt`) and the four concrete runs of T4-0
(`concrete_results.json`, produced from
`tests/test_dosage_concrete.py::CASES`, pytest 4 passed). No variant has
its own evidence source.

## Evidence records per requirement per variant

Fact tuples: (requirement, method, record, status). Verified identical
across variants by programmatic extraction from the generated JSON
artifacts (set equality over 7 facts) — not by eye.

| Requirement | Evidence fact | A (evidence array) | B (shadow rows) | C (dual matrix) |
|---|---|---|---|---|
| REQ-GIP-1-4-12 | crosshair / no_counterexample | record 1 of row | parent row | symbolic row |
| REQ-GIP-1-4-12 | concrete `over_max_clamps_exactly_to_max` / passed | record 2 of row | shadow `.concrete-1` | concrete row |
| REQ-GIP-1-8-1 | crosshair / no_counterexample | record 1 of row | parent row | symbolic row |
| REQ-GIP-1-8-1 | concrete `ordinary_negative_rate_clamps_to_zero` / passed | record 2 of row | shadow `.concrete-1` | concrete row |
| REQ-GIP-1-8-1 | concrete `overflow_negative_rate_clamps_to_zero` / passed | record 3 of row | shadow `.concrete-2` | concrete row |
| REQ-DOSE-003 | crosshair / no_counterexample | record 1 of row | parent row | symbolic row |
| REQ-DOSE-003 | concrete `normal_in_range_exact_value` / passed | record 2 of row | shadow `.concrete-1` | concrete row |

Row counts: A = 3 rows / 7 evidence records; B = 7 rows (3 parent + 4
shadow); C = 3 symbolic rows + 4 concrete rows.

**SAME-FACTS: confirmed.** The three views carry the same seven evidence
facts in different shapes.

## Findings (asymmetries — reported, not silently fixed)

1. **RESOLVED by ruling R1 (Phase A closeout, 2026-07-04).**
   Originally: derived `intent_ok` diverged in variant C's concrete view
   (REQ-DOSE-003 false there, true elsewhere) because each view
   re-derived intent from only the records it carried. Ruling: intent_ok
   is requirement-scoped and computed exactly once at the model level —
   true iff ANY evidence record for the requirement realizes the
   intended strength (`derive_intent` in
   `evidence/render/matrix_variants.py`); all projections, including
   C's method-filtered views, carry the value read-only, and variant
   B's shadow rows project their parent's value. Verified after
   regeneration: intent_ok is identical per requirement across A, B
   parents, C-symbolic, and C-concrete
   (REQ-GIP-1-4-12 false / REQ-GIP-1-8-1 false / REQ-DOSE-003 true),
   and the same-facts check still holds (7 facts, set-equal).
2. **Binding authorship differs — OPEN, deferred to Phase B.** In A and
   B the requirement↔evidence binding is authored in the metadata file
   (evidence arrays / shadow entries); in C the concrete binding is
   carried by the evidence store itself (`requirement_id` in each
   concrete_results.json case) and the metadata is byte-identical in
   facts to the base file. Same facts, different place of authorship —
   affects who can introduce a binding error and where a reviewer must
   look. Per the Phase A closeout ruling this is explicitly NOT fixed
   here; Phase B (vocabulary-agnostic binder) owns the decision.
3. **B duplicates inputs into prose.** Shadow requirement `text` fields
   restate the case inputs/expected that also exist structurally in
   concrete_results.json (and in B's own row fields). Redundant but
   consistent at generation time; a future edit to CASES would make the
   authored shadow text stale unless metadata.b.yaml is regenerated.
4. **No single-evidence-type requirement exists in this dataset.** The
   C acceptance property "a requirement with only one evidence type
   appears in exactly one artifact" is enforced by construction
   (concrete rows exist only where a case names the requirement) but is
   not exercised by the current data: all three requirements carry both
   types. Verifiable by deleting a case and regenerating; not done this
   session (evidence is fixed).

## Mechanization (Turn 2.0 B2)

The same-facts check is no longer a session-time script. Normalization and
the cross-artifact gate live in `evidence/reconcile.py` (`normalize_facts`,
`run_gate`) and are enforced in two places:

- `regenerate_all.py` — the sanctioned regeneration entrypoint: runs all
  three variant generators, then the gate, so fact divergence fails at
  generation time. Running a single generator alone bypasses this layer.
- `tests/test_fact_equality.py` — the suite backstop: committed artifacts
  that diverge in facts, requirement-scoped intent, or the bounds block
  fail the test suite.

The base Phase A matrix is frozen (ruling R2c) and participates as the
symbolic-subset legacy view: its facts must equal the symbolic projection
of the variants. Shape divergence remains design; fact divergence is a
defect that stops generation — never something to document instead of fix.

## Derived-field conventions common to all variants

- Strength comes only from evidence records (never intended_method).
- GAP records/rows (declared-but-unevidenced scopes, e.g.
  REQ-GIP-1-4-12's system_scope) render in every view but are excluded
  from `normalize_facts`: a GAP is the explicit rendering of ABSENT
  evidence, not a fact — fact equality stays at 7. Single-evidence-type
  views' note text is view-scoped (Gate 1 remediation, Item 2); the
  intent_ok value itself remains requirement-scoped and derived once (R1).
- intent_ok is requirement-scoped, derived once at the model level
  (ruling R1); all views carry it read-only.
- Intent-mismatch notes inline intended_method verbatim (ruling R2:
  quoting authored metadata is required fidelity). The enforced
  structural rule is that PROVEN never appears as a REALIZED strength
  in any record or rendered cell — checked at generation time by
  `assert_no_realized_proven()` and by
  `tests/test_structural_proven_check.py`, replacing the grep audit.
- Caveats come from `evidence.model.CAVEAT`; every EXAMPLE_CHECKED
  record carries "Holds for the specific recorded inputs only; no claim
  of generality beyond them."
