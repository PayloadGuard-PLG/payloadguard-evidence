# SYSTEM_BLUEPRINT — payloadguard-evidence

Last updated: 2026-07-07 (Phase C Gate C3 built for 3 of 4 named vectors:
evidence/dafny_spec_lint.py adds a real Z3-based vacuous-precondition
check (vector 1, proven against a real committed Dafny fixture that
verifies clean despite an unsatisfiable precondition) and a best-effort
weak-postcondition heuristic (vector 2); evidence/dafny_adapter.py's
summary-line parser is hardened against a real "N out of resource"
false-zero-adjacent finding on the installed binary (vector 3). Vector 4
(specification stripping) stays BLOCKED, named. Gates C1/C2 (built
earlier the same week) are unchanged. Nothing from Phase C is wired into
build_matrix() or any generator yet — see
payloadguard-evidence-roadmap-phaseB-to-C.md and KNOWN_LIMITATIONS.md).
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
│   ├── cli.py                   Gate 2 CLI (`python -m evidence.cli
│   │                            build`): vocabulary-agnostic wrapper
│   │                            around build_matrix() - takes metadata/
│   │                            manifest/concrete/schema as arguments,
│   │                            not hardcoded to examples/dosage_calculator
│   ├── schema/
│   │   ├── metadata.schema.json     Base metadata contract (draft 2020-12)
│   │   ├── metadata.schema.a.json   T4-A: evidence[] per requirement
│   │   ├── metadata.schema.b.json   T4-B: shadow ids + parent_requirement
│   │   └── metadata.schema.c.json   T4-C: base shape, dual-matrix notes
│   └── render/
│       ├── manual_matrix.py     Base binder/renderer (Phase A, hand-reviewed)
│       └── matrix_variants.py   build_matrix() - Gate 2's vocabulary-
│                                agnostic dispatch, the SOLE
│                                implementation across all four variants
│                                (all three generators + the CLI call
│                                it); folds in CONFLICT Type 1 as its
│                                first step, before assembling any
│                                record; derive_intent (R1);
│                                assert_no_realized_proven (R3, Phase C
│                                Gate C2 - supersedes R2: PROVEN permitted
│                                only for method=="dafny" records with
│                                verifier_completion_status=="completed";
│                                every other method stays permanently
│                                excluded). The original per-variant
│                                functions and the test that checked
│                                build_matrix() against them are deleted
│                                (Step 4) - git history holds them if ever
│                                needed again
│   ├── dafny_adapter.py         Gate C1 (+ C3 vector 3 hardening):
│                                 parse_dafny_capture() - the false-zero
│                                 guard, regex on the verifier's own
│                                 summary line, never a substring match or
│                                 bare exit_code. Also refuses on an
│                                 "out of resource"/"out of memory"/"timed
│                                 out" marker in the summary tail (real
│                                 finding, Gate C3) and on more than one
│                                 summary line in a capture. NOT called
│                                 from build_matrix() or any generator - no
│                                 binder yet assembles a dafny-method
│                                 record into a live matrix row, though R3
│                                 (Gate C2) now permits one to exist there
│   └── dafny_spec_lint.py       Gate C3 vectors 1-2: lints Dafny SOURCE
│                                 TEXT (not captured output, that's
│                                 dafny_adapter.py's job). vector 1 -
│                                 check_precondition_satisfiability():
│                                 extracts requires clauses, asks Z3 for
│                                 real satisfiability via a small scoped
│                                 expression translator (refuses on
│                                 quantifiers/unsupported syntax rather
│                                 than mistranslating). vector 2 -
│                                 scan_weak_postconditions(): heuristic,
│                                 best-effort flag of one-way ==> ensures
│                                 clauses without a matching <==>. Neither
│                                 is wired into the capture/generation
│                                 pipeline - standalone, tested modules
├── examples/dosage_calculator/  Worked example + all committed evidence
│   ├── dosage.py                Kernel under verification (contracts in
│   │                            docstring; negative rate = fault model)
│   ├── dosage_broken.py         Clamp removed — failure-path fixture source
│   ├── dosage_naive_widening.py Preserved review artifact (wrong branch
│   │                            order; documents why ordering is load-bearing)
│   ├── dosage.dfy               Gate C1: real Dafny spec of the dosage
│   │                            kernel's clamping shape; verifies clean
│   │                            (1 verified, 0 errors). REQ-DOSE-003
│   │                            excluded by name (Dafny real has no IEEE
│   │                            overflow concept - confirmed empirically)
│   ├── dosage_broken.dfy        Gate C1: Sample-B-equivalent broken variant
│   │                            (clamp removed); fails for real (0 verified,
│   │                            2 errors, exit code 4)
│   ├── vacuous_precondition_probe.dfy  Gate C3 vector 1 fixture: a real,
│   │                            committed Dafny file with an
│   │                            unsatisfiable precondition
│   │                            (x > 0 && x < 0) - Dafny itself verifies
│   │                            it clean (1 verified, 0 errors),
│   │                            confirming the false-positive is real;
│   │                            dafny_spec_lint.py's Z3 check correctly
│   │                            reports unsat on the same method
│   ├── overflow_probe.py        Domain-free model-fidelity probe
│   ├── run_verify*.py           Capture runners (one per target + concrete)
│   ├── run_verify_dafny(_broken).py  Gate C1: capture runners mirroring
│   │                            run_verify.py exactly, targeting
│   │                            dosage.dfy / dosage_broken.dfy
│   ├── run_verify_dafny_resource_limited.py  Gate C3 vector 3: real
│   │                            capture of dosage.dfy under
│   │                            --resource-limit=1, producing the real
│   │                            "0 verified, 0 errors, 1 out of resource"
│   │                            finding (exit_code=4, already caught by
│   │                            the exit-code check; hardened anyway)
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
    ├── test_structural_proven_check.py  R3 structural rule over real
    │                            artifacts (formerly R2; corruption cases
    │                            unchanged by the Gate C2 migration)
    ├── test_fact_equality.py    B2 gate: facts/intent/bounds identical across
    │                            views; base = symbolic-subset legacy view
    ├── test_conflict_check.py  Gate 2 CONFLICT Types 1+2: three ratified
    │                            test cases over real data (all three
    │                            metadata shapes) + in-memory fixtures,
    │                            plus a fold-in proof driving build_matrix()
    ├── test_single_evidence_type.py  Gate 5: symbolic-only AND
    │                            concrete-only in-memory fixtures each
    │                            appear in exactly one variant-C artifact
    ├── test_cli.py              Gate 2 CLI: subprocess-driven, all four
    │                            variants match committed artifacts;
    │                            Tier-1 error paths; stdout/file modes
    ├── test_dafny_adapter.py    Gate C1: real committed clean + broken
    │                            captures parse correctly; false-zero
    │                            substring-trap regression; belt-and-
    │                            suspenders check that assert_no_realized_proven
    │                            still blocks this adapter's PROVEN output
    ├── test_proven_exclusivity.py  Gate C2, ruling R3: positive (real
    │                            dafny PROVEN accepted) + explicit
    │                            negatives (crosshair/concrete_test/
    │                            missing-method/incomplete-status all
    │                            still refused, checked not assumed);
    │                            row-level shape; regression over all
    │                            four committed matrix artifacts
    ├── test_dafny_spec_lint.py  Gate C3 vectors 1-2: real vacuous-
    │                            precondition fixture -> unsat; real
    │                            dosage.dfy precondition -> sat (true
    │                            negative); quantifier/unknown-type
    │                            refusal; nat implicit >=0; weak-
    │                            postcondition heuristic flagged/not-
    │                            flagged cases
    └── test_dafny_timeout_masking.py  Gate C3 vector 3: real resource-
                                 limited capture refused (exit code);
                                 synthetic out-of-resource/out-of-memory/
                                 timed-out markers refused even with a
                                 forced exit_code=0 (defense in depth);
                                 ambiguous multi-summary-line capture
                                 refused; real clean capture unregressed
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
              │      any realized strength == PROVEN, UNLESS method   │
              │      == "dafny" AND verifier_completion_status ==     │
              │      "completed"                          [ruling R3] │
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
Phase B (COMPLETE — gate ledger fully closed): Gate 1 (end-to-end pipeline + provenance index)
complete with remediation applied. Gates 3 (bounds enforcement — decided
stay-CLI by real behavioral test), 4 (binding authorship — option 3
decided, mechanism specified), 5 (single-evidence-type fixture for
variant C — fully resolved, both symbolic-only and concrete-only now
constructible), and 6 (FRN — resolved) closed or decided. **Gate 2 is
now complete.** Its CONFLICT rule — both Type 1
(identity mismatch) and Type 2 (outcome mismatch) — is built
(`evidence/conflict.py`); Gate 4's cross-check mechanism is implemented
for all three metadata shapes, including variant C, whose declared-
binding asymmetry is closed. `build_matrix()` is the sole
implementation across all four variants (the original per-variant
functions and the equivalence test that checked build_matrix() against
them are deleted, per Steven's direction to build the CLI first); Type 1
is folded into it, running on every call. Type 2 stays a standalone
`generate_artifacts.py` stage by design (a whole-manifest-set check with
no per-variant home, like fact-equality). The CLI (`evidence/cli.py`,
`python -m evidence.cli build`) wraps `build_matrix()` for any metadata/
manifest/concrete-store path rather than the hardcoded worked-example
paths the generator scripts use. See `KNOWN_LIMITATIONS.md` for the live
gate ledger.

Phase C (in progress): restructured 2026-07-06 from a two-mechanism sketch
into a gate-sequenced plan (Gates C1–C6, build order specified) in
`payloadguard-evidence-roadmap-phaseB-to-C.md`. Gate C1's Dafny
toolchain blocker is resolved: Z3 4.16.0 is present and Dafny 4.11.0 was
obtained via `dotnet tool install --global dafny` (NuGet, reachable
through the environment's proxy; GitHub release downloads are genuinely
blocked by egress policy, confirmed via the proxy's own status endpoint,
not routed around). Verified against the real binary: the false-zero
note in `evidence/model.py` matches exactly ("Dafny program verifier
finished with N verified, 0 errors"); a failing run exits 4, not 1; the
vacuous-precondition risk Gate C3 names is real and reproducible; its
planned Z3-based mitigation is confirmed feasible. **Gate C1 itself is
now built (2026-07-07):** a real Dafny spec of the dosage kernel
(`dosage.dfy`, clean; `dosage_broken.dfy`, fails for real), a capture
runner pair, and `evidence/dafny_adapter.py::parse_dafny_capture` — the
false-zero guard, implemented and regression-tested
(`tests/test_dafny_adapter.py`, 6 tests). REQ-DOSE-003 is named as an
explicit scope exclusion from the Dafny spec (Dafny `real` has no IEEE
overflow concept). **Gate C2 (PROVEN's exclusivity migration) is also
now built (2026-07-07):** ruling R3 supersedes R2 —
`assert_no_realized_proven` permits PROVEN as a realized strength only
when a record's `method == "dafny"` and its `verifier_completion_status
== "completed"`; every other method, including a record with no method
at all, remains permanently excluded, checked explicitly in 8 new tests
(`tests/test_proven_exclusivity.py`) rather than assumed from the fact
that no binder produces one yet. Neither gate is wired into
`build_matrix()` or any generator — no binder yet assembles a
Dafny-sourced record into a live matrix row, so R3's positive branch is
proven correct in isolation, not yet exercised end-to-end. **Gate C3
(Dafny output-parsing hardening) is also now built for 3 of its 4 named
vectors (2026-07-07):** vector 1 (vacuous preconditions) —
`evidence/dafny_spec_lint.py::check_precondition_satisfiability` asks Z3
directly whether a method's `requires` clauses are jointly satisfiable,
proven against a real committed fixture
(`vacuous_precondition_probe.dfy`) that Dafny itself verifies clean
despite an unsatisfiable precondition. Vector 2 (weak postconditions) —
`scan_weak_postconditions`, an explicitly best-effort heuristic flagging
one-way `==>` in `ensures` clauses. Vector 3 (timeout/resource-limit
masking) — a real finding on the installed binary
(`dafny verify --resource-limit=1` on the real dosage.dfy spec reports
`0 verified, 0 errors, 1 out of resource`, `exit_code=4`, already caught
by Gate C1's exit-code check) led to hardening
`evidence/dafny_adapter.py`'s summary-line parser to also refuse
independently on out-of-resource/out-of-memory/timed-out markers and on
ambiguous multi-summary-line captures. Vector 4 (specification
stripping) remains BLOCKED, named — no new source material surfaced.
None of Gate C3's mechanisms are wired into the capture or generation
pipeline either — standalone, tested modules, same scope discipline as
Gates C1/C2. That wiring belongs alongside Gate C4 (STPs, "alongside the
first real spec") per the roadmap's suggested build order. Full
findings: `KNOWN_LIMITATIONS.md`.
