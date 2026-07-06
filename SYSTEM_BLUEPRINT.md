# SYSTEM_BLUEPRINT — payloadguard-evidence

Last updated: 2026-07-06 (Gate 2 vocabulary-agnostic binder, Step 3:
CONFLICT Type 1 folded into build_matrix() itself; Type 2 confirmed to
have no per-variant home and stays a standalone pipeline stage — see
KNOWN_LIMITATIONS.md).
Derived from the codebase; when in doubt, the code wins. Update this file in
the same commit as any structural change (new module, new generation path,
new evidence source, schema change).

## 1. Purpose

Turn verification captures plus authored metadata into IEC 62304 / FDA §524B
traceability artifacts whose every row is bound to a committed, replayable
evidence record of known strength. The system never infers strength and
never lets declared intent leak into realized results.

## 2. Component map

```
payloadguard-evidence/
├── README.md                    Repository overview (this system, end to end)
├── SYSTEM_BLUEPRINT.md          This file — structure and data flow
├── DEVLOG.md                    Dated session log, append-only
├── evidence/                    Reusable core (domain-free by design)
│   ├── model.py                 Strength enum + CAVEAT map + dataclasses
│   │                            (VerificationResult, RequirementBinding);
│   │                            carries the Phase-B Dafny false-zero note
│   ├── reconcile.py             Normalized fact extraction + cross-artifact
│   │                            fact-equality gate (Turn 2.0 B2)
│   ├── conflict.py              Gate 2 CONFLICT rule, both ratified
│   │                            sub-types: Type 1 (identity mismatch,
│   │                            top-down metadata vs. bottom-up
│   │                            evidence-store) and Type 2 (outcome
│   │                            mismatch across manifests); Tier 1
│   ├── schema/
│   │   ├── metadata.schema.json     Base metadata contract (draft 2020-12)
│   │   ├── metadata.schema.a.json   T4-A: evidence[] per requirement
│   │   ├── metadata.schema.b.json   T4-B: shadow ids + parent_requirement
│   │   └── metadata.schema.c.json   T4-C: base shape, dual-matrix notes
│   └── render/
│       ├── manual_matrix.py     Base binder/renderer (Phase A, hand-reviewed)
│       └── matrix_variants.py   build_matrix() - Gate 2's vocabulary-
│                                agnostic dispatch, AUTHORITATIVE as of
│                                2026-07-06 (all three generators call it);
│                                folds in CONFLICT Type 1 (Step 3) as its
│                                first step, before assembling any record;
│                                derive_intent (R1);
│                                assert_no_realized_proven (R2);
│                                build_matrix_variant_a/b/c kept in place,
│                                unused, as an explicit fallback (NOT
│                                Type-1-checked) - deleted only in a later
│                                cleanup step
├── examples/dosage_calculator/  Worked example + all committed evidence
│   ├── dosage.py                Kernel under verification (contracts in
│   │                            docstring; negative rate = fault model)
│   ├── dosage_broken.py         Clamp removed — failure-path fixture source
│   ├── dosage_naive_widening.py Preserved review artifact (wrong branch
│   │                            order; documents why ordering is load-bearing)
│   ├── overflow_probe.py        Domain-free model-fidelity probe
│   ├── run_verify*.py           Capture runners (one per target + concrete)
│   ├── gate3_seed_patch_test.py Gate 3 investigation script (not part of
│   │                            the evidence-capture path): behaviorally
│   │                            tests a make_default_solver seed-override
│   │                            patch; result documented in
│   │                            KNOWN_LIMITATIONS.md, no capture changed
│   ├── raw_*/run_manifest_*     Verbatim captures + command/exit manifests
│   ├── concrete_results.json    Structured concrete evidence (T4-0)
│   ├── exhibit_pin_*.json       Version/platform pins + mechanism attribution
│   ├── metadata[.a|.b|.c].yaml  Authored metadata, base + variant shapes
│   ├── generate_matrix*.py      Generators (validate → bind → check →
│   │                            render); each now calls
│   │                            evidence.render.matrix_variants.build_matrix()
│   │                            (2026-07-06 cutover)
│   ├── regenerate_all.py        Inner regeneration step: all variant
│   │                            generators + fact-equality gate
│   ├── generate_artifacts.py    End-to-end pipeline (Turn B4): schema
│   │                            validation -> capture integrity ->
│   │                            CONFLICT Type 1 (frozen base only - a/b/c
│   │                            checked inside build_matrix() now) ->
│   │                            CONFLICT Type 2 (whole-dataset, standalone)
│   │                            -> regenerate_all -> PROVEN sweep ->
│   │                            artifact_index.json
│   ├── artifact_index.json      SHA-256 provenance: inputs -> outputs,
│   │                            per-gate results, frozen evidence hashes
│   ├── traceability_matrix.*    Generated artifacts (never hand-typed)
│   ├── README.md                Audit-trail record (citations, caveats,
│   │                            amendments, exhibits, open questions)
│   └── RECONCILIATION.md        Cross-variant same-facts note + findings
├── sources/
│   ├── README.md                Standing rule for adding source documents
│   └── gip-v1.0-hazard-analysis.md  GIP v1.0 archived verbatim
└── tests/
    ├── conftest.py              Import-path plumbing
    ├── test_dosage_concrete.py  T4-0 CASES (single source of concrete truth)
    ├── test_overflow_probe.py   Deterministic IEEE overflow as executable fact
    ├── test_structural_proven_check.py  R2 structural rule over real artifacts
    ├── test_fact_equality.py    B2 gate: facts/intent/bounds identical across
    │                            views; base = symbolic-subset legacy view
    ├── test_conflict_check.py  Gate 2 CONFLICT Types 1+2: three ratified
    │                            test cases over real data (all three
    │                            metadata shapes) + in-memory fixtures,
    │                            plus a fold-in proof driving build_matrix()
    └── test_binder_equivalence.py  Gate 2 binder Step 1: build_matrix()
                                 proven byte-identical (dict + JSON string)
                                 to build_matrix_variant_a/b/c
```

## 3. Data flow (end to end)

```
                      AUTHORED                          CAPTURED (real runs)
        ┌─────────────────────────────┐     ┌────────────────────────────────────┐
        │ sources/*.md  (ground truth)│     │ run_verify(.broken)*.py            │
        │        │ cite               │     │   crosshair check <target>         │
        │        ▼                    │     │   --report_all                     │
        │ metadata[.a|.b|.c].yaml     │     │   --per_condition_timeout 30       │
        │  device / requirements /    │     │   -> raw output + manifest with    │
        │  (declared bounds = intent) │     │      effective_bounds (Turn 2.0);  │
        │                             │     │   exhibit runners keep the pinned  │
        │                             │     │   no-flags invocation (frozen)     │
        │  threat_model / toolchain   │     │ run_verify_concrete.py             │
        └──────────────┬──────────────┘     │   pytest tests/test_dosage_...     │
                       │                    │   -> raw_pytest_output_concrete    │
        jsonschema     │                    │   -> concrete_results.json         │
        (draft 2020-12)│                    └──────────────────┬─────────────────┘
                       ▼                                       │
              ┌────────────────────────────────────────────────▼───────┐
              │ generate_matrix*.py                                    │
              │  1 validate metadata against its schema (fail hard)    │
              │  2 build evidence records:                             │
              │      crosshair capture -> BOUNDED_CHECKED              │
              │      concrete case     -> EXAMPLE_CHECKED              │
              │      (binders refuse failed captures)                  │
              │  3 derive_intent(): requirement-scoped, computed ONCE; │
              │      views carry it read-only            [ruling R1]   │
              │  4 assert_no_realized_proven(): generation fails if    │
              │      any realized strength == PROVEN     [ruling R2]   │
              │  5 render JSON + Markdown with per-strength caveats    │
              └────────────────────┬───────────────────────────────────┘
                                   ▼
        traceability_matrix.json/.md          (base, one record per row)
        traceability_matrix.a.json/.md        (variant A, evidence[] per req)
        traceability_matrix.b.json/.md        (variant B, shadow rows + parent)
        traceability_matrix.symbolic|concrete (variant C, method-partitioned)
```

## 4. Invariants

1. Strength originates in evidence records only; `intended_method` never
   influences a realized strength.
2. `intent_ok` is requirement-scoped, derived once at bind time, projected
   read-only into every view (R1). Variant B shadow rows project their
   parent's value.
3. `PROVEN` never appears as a realized strength in any generated record or
   rendered cell; enforced structurally at generation time and by pytest
   (R2). It may appear when quoting authored metadata in mismatch notes.
4. Gap = absence. No placeholder strings for missing evidence or fields.
5. Every committed capture carries verbatim output, exact command, exit
   code, and UTC timestamp. Unexpected outcomes are committed as-is (see the
   overflow probe: expected miss, actual confirmation — kept).
6. Committed matrices are generated, never edited by hand. Regeneration is
   deterministic given the same captures (timestamps aside).
7. Exhibit claims are version-contingent and scoped to their pins
   (crosshair-tool 0.0.107 / Python 3.11.15 / Linux x86_64).
8. All T4 variants must carry the same evidence facts; enforced by the
   fact-equality gate (`evidence/reconcile.py`) at generation time via
   `regenerate_all.py` and in the suite via `tests/test_fact_equality.py`.
   Shape divergence is design; fact divergence is a defect.
9. Review is two-tier (REVIEW_PROTOCOL.md): Tier 1 machine gates
   (fact-equality, structural PROVEN) stop defects — never resolved by
   editing generated artifacts; Tier 2 human review is per-reason over the
   structured findings. Declared bounds are intent; effective bounds in
   each manifest are what a run demonstrated (Turn 2.0 B1).

## 5. Evidence inventory (current)

| Capture | Target | Outcome | Strength encoded |
|---|---|---|---|
| Sample A (`run_manifest.json`) | `dosage.py` | exit 0, no counterexample | BOUNDED_CHECKED |
| Sample B (`run_manifest_broken.json`) | `dosage_broken.py` | exit 1, two counterexamples (over-max and negative-rate) | n/a (fixture proves capture works on failure) |
| Sample C (`run_manifest_naive_widening.json`) | `dosage_naive_widening.py` | exit 0 — real violation NOT found | honesty exhibit (class-2 incompleteness) |
| Overflow probe (`run_manifest_overflow_probe.json`) | `overflow_probe.py` | exit 1 — violation CONFIRMED | honesty exhibit (paired measurement) |
| Concrete (`concrete_results.json`) | `dosage.py`, 4 cases | pytest 4 passed, observed==expected | EXAMPLE_CHECKED |

Requirements bound (from GIP v1.0 unless DECLARED): REQ-GIP-1-4-12 (dose
limit), REQ-GIP-1-8-1 (reverse delivery, fault-modelled), REQ-DOSE-003
(finite in-range result, DECLARED). Intent status: 1-4-12 and 1-8-1 intend
PROVEN → realized weaker (intent_ok false, honest); DOSE-003 intent met.

## 6. Phase boundary

Phase A (complete): schema + model + hand-reviewed renderer, real captures,
worked example, T4 three-variant fork, closeout rulings R1–R3.
Phase B (in progress): Gate 1 (end-to-end pipeline + provenance index)
complete with remediation applied. Gates 3 (bounds enforcement — decided
stay-CLI by real behavioral test), 4 (binding authorship — option 3
decided, mechanism specified), 5 (single-evidence-type fixture —
resolved for the constructible half), and 6 (FRN — resolved) closed or
decided. Gate 2's CONFLICT rule — both Type 1 (identity mismatch) and
Type 2 (outcome mismatch) — is built (`evidence/conflict.py`); Gate 4's
cross-check mechanism is now implemented for all three metadata shapes,
including variant C, whose declared-binding asymmetry is closed. The
vocabulary-agnostic binder is built and cut over (Steps 1–2), and Type 1
is folded into `build_matrix()` itself as of Step 3 — it runs on every
call, not just inside the full pipeline. Type 2 stays a standalone
`generate_artifacts.py` stage by design (a whole-manifest-set check with
no per-variant home, like fact-equality). Still open: deleting the
Step 2 fallback functions once the cutover has proven stable (Step 4),
and the CLI. See `KNOWN_LIMITATIONS.md` for the live gate ledger and
`payloadguard-evidence-roadmap-phaseB-to-C.md` for Phase C's now-concrete
mechanisms (Dafny/Z3 adapters remain unbuilt; parser must assert the
literal substring "0 errors" plus the three further checks in the
roadmap — false-zero bug note in `evidence/model.py`).
