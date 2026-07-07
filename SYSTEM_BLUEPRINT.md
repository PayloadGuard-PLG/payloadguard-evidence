# SYSTEM_BLUEPRINT — payloadguard-evidence

Last updated: 2026-07-07 (Gate C6, NL-dialogue confirmation, BUILT and
SIGNED OFF: evidence/dafny_nl_summary.py mechanically summarizes a Dafny
method's requires/ensures clauses in plain English, cross-checked against
dafny_spec_lint's canonical extractor and refusing on any multi-line
clause it can't safely associate a citation with. The gate's actual
deliverable, examples/dosage_calculator/nl_confirmation_dosage_dfy.md,
records Steven's sign-off on the generated summary for
CalculateHourlyDose. 7 new tests; full suite now 105 passed. Earlier the
same week: Gate 2/C2-C4 wiring EXTENDED TO VARIANTS A/B - every schema
variant now binds the same real Dafny evidence for
REQ-GIP-1-4-12/REQ-GIP-1-8-1 - metadata.a.yaml's evidence list,
metadata.b.yaml's new .formal-N shadow rows, and
traceability_matrix.formal.json (variant C's third partition, built
first). intent_ok is True for both requirements in EVERY variant
artifact now (was a named, temporary A/B divergence when C landed
first; that carve-out mechanism, run_formal_check, is retired).
evidence/reconcile.py::run_gate()'s intent comparison is now subset-
based (formal.json permanently lacks an opinion about REQ-DOSE-003,
out of dosage.dfy's scope by design). evidence/cli.py gained
--dafny-captures, now required to build variant A/B at all. Gate C4
and Gates C1-C3 were built earlier the same week - see
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
│   │                            fact-equality gate (Turn 2.0 B2).
│   │                            VARIANT_ARTIFACTS includes
│   │                            traceability_matrix.formal.json as a
│   │                            full 5th member (2026-07-07, once
│   │                            variants A/B were extended to match) -
│   │                            the intent comparison is subset-based,
│   │                            not strict dict equality, since formal.json
│   │                            permanently lacks an opinion about
│   │                            REQ-DOSE-003 (out of dosage.dfy's scope
│   │                            by design). The temporary carve-out
│   │                            mechanism used while C was ahead of A/B
│   │                            (run_formal_check,
│   │                            KNOWN_FORMAL_INTENT_DIVERGENCE) is retired
│   ├── conflict.py              Gate 2 CONFLICT rule, both ratified
│   │                            sub-types: Type 1 (identity mismatch,
│   │                            top-down metadata vs. bottom-up
│   │                            evidence-store, now incl.
│   │                            dafny_binding_conflicts /
│   │                            _declared_dafny_bindings for dafny
│   │                            evidence across all three metadata
│   │                            shapes, 2026-07-07) and Type 2 (outcome
│   │                            mismatch across manifests); Tier 1
│   ├── cli.py                   Gate 2 CLI (`python -m evidence.cli
│   │                            build`): vocabulary-agnostic wrapper
│   │                            around build_matrix() - takes metadata/
│   │                            manifest/concrete/schema as arguments,
│   │                            not hardcoded to examples/dosage_calculator.
│   │                            --dafny-captures (2026-07-07, required
│   │                            once metadata.a.yaml/b.yaml declared
│   │                            dafny evidence) points at a small JSON
│   │                            index of paths (not inlined content) for
│   │                            the real dafny_store the CLI assembles
│   ├── schema/
│   │   ├── metadata.schema.json     Base metadata contract (draft 2020-12)
│   │   ├── metadata.schema.a.json   T4-A: evidence[] per requirement,
│   │   │                            + dafny method (2026-07-07, same fix
│   │   │                            as schema.c.json)
│   │   ├── metadata.schema.b.json   T4-B: shadow ids + parent_requirement;
│   │   │                            shadow-id pattern extended to allow
│   │   │                            .formal-N (2026-07-07) alongside
│   │   │                            .concrete-N, for dafny shadow rows
│   │   │                            distinguished by a .dfy implementation
│   │   └── metadata.schema.c.json   T4-C: base shape, dual-matrix notes,
│   │                            + dafny evidence entries (spec_target,
│   │                            dafny_method required together), 2026-07-07
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
│                                needed again. dafny_record() (2026-07-07,
│                                Gate 2/C2-C4 wiring) is the mechanism
│                                that lets a real Dafny capture ever
│                                satisfy R3 - gates PROVEN on Z3
│                                precondition satisfiability AND the
│                                false-zero guard inside the binder
│                                itself, before assert_no_realized_proven
│                                ever re-checks it. build_matrix(),
│                                _bind_self_describing() (variant C),
│                                _bind_declared() (variant A), and
│                                _bind_shadow() (variant B) all gained an
│                                optional dafny_store parameter (default
│                                None = "don't bind dafny evidence at
│                                all", not "bind zero captures" -
│                                is-not-None, not truthiness). A/B's
│                                binders refuse outright if dafny evidence
│                                is declared with no dafny_store at all
│                                (unlike C's symbolic/concrete sub-views,
│                                they have no "legitimately excludes
│                                dafny" concept - a single artifact
│                                renders every evidence type together).
│                                _bind_shadow() distinguishes a dafny
│                                shadow row from a concrete one by
│                                checking whether the implementation file
│                                ends in .dfy - no new declared field
│   ├── dafny_adapter.py         Gate C1 (+ C3 vector 3 hardening):
│                                 parse_dafny_capture() - the false-zero
│                                 guard, regex on the verifier's own
│                                 summary line, never a substring match or
│                                 bare exit_code. Also refuses on an
│                                 "out of resource"/"out of memory"/"timed
│                                 out" marker in the summary tail (real
│                                 finding, Gate C3) and on more than one
│                                 summary line in a capture. Called from
│                                 build_matrix() as of 2026-07-07 (Gate
│                                 2/C2-C4 wiring), via matrix_variants.py's
│                                 dafny_record() - the "c-formal" variant
│                                 key is what actually assembles a
│                                 dafny-method record into a live matrix
│                                 row today; every other variant_key is
│                                 unaffected
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
│   └── dafny_nl_summary.py      Gate C6: NL-dialogue confirmation.
│                                 summarize_method() mechanically extracts
│                                 each requires/ensures clause verbatim
│                                 plus any REQ-ID cited in a trailing
│                                 comment, alongside a best-effort
│                                 operator-substitution English gloss
│                                 (template, not comprehension - the raw
│                                 clause is always shown first). Reuses
│                                 dafny_spec_lint.py's Gate C3 parsing
│                                 surface. Only single-line clauses
│                                 supported; cross-checks its own
│                                 line-based extraction against
│                                 dafny_spec_lint's canonical multi-line-
│                                 capable extractor by CONTENT (not just
│                                 count - an earlier count-only draft
│                                 missed a real silently-truncated case)
│                                 and refuses (SystemExit) on mismatch.
│                                 Not wired into the capture/generation
│                                 pipeline - a process habit, not an
│                                 automated gate
├── examples/dosage_calculator/  Worked example + all committed evidence
│   ├── dosage.py                Kernel under verification (contracts in
│   │                            docstring; negative rate = fault model)
│   ├── dosage_broken.py         Clamp removed — failure-path fixture source
│   ├── dosage_naive_widening.py Preserved review artifact (wrong branch
│   │                            order; documents why ordering is load-bearing)
│   ├── dosage.dfy               Gate C1: real Dafny spec of the dosage
│   │                            kernel's clamping shape; verifies clean
│   │                            (2 verified, 0 errors - an ExpectedDose
│   │                            function + the method, since Gate C4's
│   │                            fix pinned dose == ExpectedDose(...)).
│   │                            REQ-DOSE-003 excluded by name (Dafny
│   │                            real has no IEEE overflow concept -
│   │                            confirmed empirically)
│   ├── dosage_broken.dfy        Gate C1: Sample-B-equivalent broken variant
│   │                            (clamp removed); fails for real (0 verified,
│   │                            2 errors, exit code 4)
│   ├── dosage_underconstrained.dfy  Gate C4 honesty exhibit: Gate C1's
│   │                            ORIGINAL dosage.dfy postcondition,
│   │                            byte-for-byte, before the ExpectedDose
│   │                            fix - verifies clean on its own (the bug
│   │                            is a spec weakness, not a verification
│   │                            failure); same rationale as
│   │                            dosage_naive_widening.py
│   ├── dosage_stp_suite.dfy     Gate C4: 6 Spec-Testing Proof lemmas
│   │                            (IronSpec methodology) against the FIXED
│   │                            dosage.dfy (include'd) - ACCEPT + REJECT
│   │                            pairs for the normal/ceiling-clamped
│   │                            branches, ACCEPT-only for reverse-flow;
│   │                            all verify (10 verified, 0 errors)
│   ├── dosage_stp_suite_against_underconstrained.dfy  Gate C4: the same
│   │                            2 REJECT lemmas, include'ing the
│   │                            preserved weak spec instead - both
│   │                            genuinely FAIL (0 verified, 2 errors,
│   │                            exit 4), the mechanized "before" proof
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
│   ├── run_verify_dafny_underconstrained.py  Gate C4: real capture of
│   │                            dosage_underconstrained.dfy standalone
│   ├── run_verify_dafny_stp_suite(_against_underconstrained).py  Gate
│   │                            C4: real captures of the two STP
│   │                            suites (fixed spec passes; weak spec
│   │                            genuinely fails)
│   ├── gate3_seed_patch_test.py Gate 3 investigation script (not part of
│   │                            the evidence-capture path): behaviorally
│   │                            tests a make_default_solver seed-override
│   │                            patch; result documented in
│   │                            KNOWN_LIMITATIONS.md, no capture changed
│   ├── nl_confirmation_dosage_dfy.md  Gate C6: the actual deliverable -
│   │                            a recorded human decision, not code. The
│   │                            generated plain-English summary for
│   │                            CalculateHourlyDose, plus Steven's
│   │                            sign-off ("it's good for the spec as
│   │                            is", 2026-07-07) and a next-phase item
│   │                            he explicitly scoped out as separate
│   │                            follow-up work
│   ├── raw_*/run_manifest_*     Verbatim captures + command/exit manifests
│   ├── concrete_results.json    Structured concrete evidence (T4-0)
│   ├── exhibit_pin_*.json       Version/platform pins + mechanism attribution
│   ├── metadata[.a|.b|.c].yaml  Authored metadata, base + variant shapes.
│   │                            All three of a/b/c now declare real
│   │                            dafny evidence (2026-07-07) for
│   │                            REQ-GIP-1-4-12/REQ-GIP-1-8-1 only -
│   │                            REQ-DOSE-003 permanently excluded, out
│   │                            of dosage.dfy's scope by design.
│   │                            metadata.b.yaml uses new .formal-N
│   │                            shadow rows (e.g.
│   │                            REQ-GIP-1-4-12.formal-1), same pattern
│   │                            as .concrete-N shadows
│   ├── dafny_captures_index.json  Small JSON index (paths, not inlined
│   │                            content) the CLI's --dafny-captures
│   │                            reads to assemble a real dafny_store
│   │                            (2026-07-07)
│   ├── generate_matrix*.py      Generators (validate → bind → check →
│   │                            render); each now calls
│   │                            evidence.render.matrix_variants.build_matrix()
│   │                            (2026-07-06 cutover). generate_matrix_c.py
│   │                            renders THREE artifacts as of 2026-07-07
│   │                            (symbolic/concrete/formal), assembling
│   │                            dafny_store from the real committed Gate
│   │                            C1 capture - no re-running evidence
│   ├── regenerate_all.py        Inner regeneration step: all variant
│   │                            generators + fact-equality gate +
│   │                            run_formal_check() (2026-07-07)
│   ├── generate_artifacts.py    End-to-end pipeline (Turn B4): schema
│   │                            validation -> capture integrity ->
│   │                            CONFLICT Type 1 (frozen base only - a/b/c
│   │                            checked inside build_matrix() now) ->
│   │                            CONFLICT Type 2 (whole-dataset, standalone)
│   │                            -> regenerate_all -> PROVEN sweep (now
│   │                            incl. traceability_matrix.formal.json) ->
│   │                            artifact_index.json
│   ├── artifact_index.json      SHA-256 provenance: inputs -> outputs,
│   │                            per-gate results, frozen evidence hashes.
│   │                            dosage.dfy/raw_dafny_output.txt/
│   │                            run_manifest_dafny.json added to INPUTS,
│   │                            traceability_matrix.formal.* to OUTPUTS
│   │                            (2026-07-07)
│   ├── traceability_matrix.*    Generated artifacts (never hand-typed).
│   │                            traceability_matrix.formal.json/.md
│   │                            (2026-07-07): variant C's third
│   │                            partition, real Dafny-sourced PROVEN
│   │                            evidence - this repository's first ever
│   │                            live rendered PROVEN row
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
    ├── test_cli.py              Gate 2 CLI: subprocess-driven, all FIVE
    │                            variants (a/b/c-symbolic/c-concrete/
    │                            c-formal, 2026-07-07) match committed
    │                            artifacts via --dafny-captures; Tier-1
    │                            error paths; stdout/file modes
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
    ├── test_dafny_timeout_masking.py  Gate C3 vector 3: real resource-
    │                            limited capture refused (exit code);
    │                            synthetic out-of-resource/out-of-memory/
    │                            timed-out markers refused even with a
    │                            forced exit_code=0 (defense in depth);
    │                            ambiguous multi-summary-line capture
    │                            refused; real clean capture unregressed
    ├── test_dafny_stp_suite.py  Gate C4: real committed STP captures -
    │                            underconstrained spec still verifies
    │                            alone; STP suite passes against the
    │                            fix; same suite fails against the
    │                            preserved weak spec; regression on the
    │                            50.0-vs-500.0 wrong-value mistake caught
    │                            mid-build; direct source-text checks for
    │                            the pinning clause present/absent
    ├── test_dafny_nl_summary.py  Gate C6: real dosage.dfy parameters/
    │                            preconditions/postconditions rendered
    │                            correctly; each postcondition cites the
    │                            right requirement or explicitly "no
    │                            requirement cited" (load-bearing -
    │                            wrong citation is the exact defect class
    │                            this gate exists to catch); operator
    │                            gloss; multi-line-clause refusal
    │                            regression (the self-caught count-vs-
    │                            content bug); no-clauses case; output
    │                            determinism
    └── test_dafny_wiring.py     Gate 2/C2-C4 wiring, built for variant C
                                 then extended to A/B (2026-07-07): real
                                 formal artifact + real A/B artifacts all
                                 carry the expected PROVEN rows and pass
                                 assert_no_realized_proven for real;
                                 dafny_record()'s two independent gates
                                 (Z3, false-zero) each exercised;
                                 dafny_binding_conflicts across all three
                                 declaration shapes (A/C evidence list,
                                 B's .dfy shadow rows); the full
                                 fact-equality gate passes with intent
                                 True everywhere; the subset-vs-strict-
                                 equality fix is exercised directly; CLI
                                 --dafny-captures round-trips for a/b and
                                 the CLI's refusal without it is real, not
                                 hypothetical; end-to-end
                                 build_matrix("c-formal", ...) matches
                                 the committed artifact
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
Gates C1/C2.

**Gate C4 (Spec-Testing Proofs) is also now built (2026-07-07), and
found a real spec gap on its first application:** IronSpec's
methodology — prove a specific input/output pair is accepted or
rejected by the SPECIFICATION itself, independent of any implementation
— revealed that `dosage.dfy`'s original postcondition (bounds +
reverse-flow-zero only) never pinned `dose` to the actual clamped value:
a Dafny lemma trying to prove a wrong candidate value impossible
**failed to verify**, meaning a broken implementation that always
returned `0.0` would have satisfied the exact same spec Gate C1 verified
clean. Fixed for real: `dosage.dfy` gained a `function ExpectedDose(...)`
and a pinning `ensures dose == ExpectedDose(...)` clause, re-verified
clean (`2 verified, 0 errors` — the count changed from Gate C1's
original `1 verified`, and the real committed capture was re-run
honestly to match, not patched). The original weak spec is preserved
byte-for-byte as `dosage_underconstrained.dfy` (same rationale as
`dosage_naive_widening.py`); two STP suites (`dosage_stp_suite.dfy`,
`dosage_stp_suite_against_underconstrained.dfy`, each `include`-ing the
relevant spec rather than duplicating it) mechanically prove both
directions — six lemmas pass against the fix, the same two REJECT
lemmas genuinely fail against the preserved original. A self-caught
mistake during this build (an early wrong-value choice, `500.0`, was
already excluded by the weak spec's own bounds for an unrelated reason,
giving a false pass) was corrected to `50.0` before committing, with a
regression test guarding against reintroducing it. 6 new tests
(`tests/test_dafny_stp_suite.py`); full suite now 78 passed. Neither STP
suite is wired into `build_matrix()` or any generator — matches Gates
C1–C3's scope discipline; this gate authored one STP suite for the one
spec that exists, per its stated scope, not a generic STP-generation
tool.

**Gate C6 (NL-dialogue confirmation) is also now built and signed off
(2026-07-07).** Process-control gate aimed directly at recurrence of Gate
1's original finding — a spec/requirement-text mismatch caught only at
review time, not authoring time. `evidence/dafny_nl_summary.py::summarize_method`
mechanically extracts each requires/ensures clause verbatim plus any
`REQ-ID` cited in a trailing comment, alongside a best-effort operator-
substitution gloss labeled explicitly as a reading aid, not
comprehension — reusing Gate C3's parsing surface rather than
reimplementing Dafny parsing. Only single-line clauses are supported;
the function cross-checks its own extraction against `dafny_spec_lint`'s
canonical multi-line-capable extractor and refuses on any content
mismatch. A self-caught bug during this build: the first draft of that
check compared clause *counts*, not content, and missed a real case — a
synthetic multi-line clause produced the same count under both
extractors while the line-based scan had silently truncated it, dropping
the continuation. Fixed by comparing normalized clause text instead of
counts, before the test suite was even written. 7 new tests
(`tests/test_dafny_nl_summary.py`); full suite now 105 passed. The
gate's actual deliverable is not the code but the recorded decision it
feeds: `examples/dosage_calculator/nl_confirmation_dosage_dfy.md` records
Steven's sign-off on the generated summary for `CalculateHourlyDose`
("it's good for the spec as is") plus a next-phase item he explicitly
scoped out as separate follow-up work. Not wired into any generator —
matches the roadmap's own framing of this gate as a process habit, not
an automated check.

**Gate 2/C2-C4 wiring is also now built (2026-07-07) — the first real
Dafny-sourced PROVEN evidence ever to reach a live matrix row.**
Requested directly ("we need z3 integration and invocation in order to
reach PROVEN status, in concurrence with gate 5 extension"), with three
design decisions confirmed before building: scope is variant C only for
now (A/B explicitly deferred — "post hoc verify A and B after C is
proven"); the Z3 precondition-satisfiability gate lives inside the
binder itself (`dafny_record()`); metadata declares the dafny evidence
explicitly, cross-checked by a new CONFLICT Type 1 sub-check
(`dafny_binding_conflicts`). `traceability_matrix.formal.json` (variant
C's third partition, extending Gate 5's dual-matrix pattern to a triple)
binds real `dosage.dfy` evidence to REQ-GIP-1-4-12 and REQ-GIP-1-8-1 —
both flip `intent_ok` from False to True for the first time since Phase
A, gated by two independent, real checks before any record is even
constructed: Z3 precondition satisfiability (Gate C3) and
`parse_dafny_capture`'s false-zero guard (Gate C1). `assert_no_realized_proven`'s
ruling R3 (Gate C2) is exercised end to end for the first time, not just
in isolation — the structural PROVEN sweep in `generate_artifacts.py`
now explicitly checks the formal artifact too.

**Extended to variants A and B the same day** ("go ahead and extend
variant A and B now"): `metadata.a.yaml`/`metadata.b.yaml` now declare
the same real dafny evidence (A's `evidence` list; B's new `.formal-N`
shadow rows, distinguished from concrete shadows by a `.dfy`
implementation file, no new declared field needed); `_bind_declared`/
`_bind_shadow` gained the matching binder logic, refusing outright
(unlike C's symbolic/concrete sub-views) if dafny evidence is declared
with no `dafny_store` at all — A/B have no "legitimately excludes dafny"
concept. `dafny_binding_conflicts` was generalized (a new
`_declared_dafny_bindings` generator, mirroring how concrete evidence
already unifies A/C's list and B's shadow rows) to cover all three
declaration shapes, and `_declared_concrete_bindings` was fixed to skip
`.dfy`-suffixed shadow rows rather than mis-parsing them as concrete
test ids. `generate_matrix_c.py` now passes `dafny_store` to ALL THREE
of its `build_matrix()` calls, not just `"c-formal"` — necessary so
`c-symbolic`/`c-concrete`'s own `intent_ok` computation matches A/B/
formal (their rendered rows are unaffected either way).
`evidence/reconcile.py::VARIANT_ARTIFACTS` now includes
`traceability_matrix.formal.json` as a full fifth member, and the intent
comparison became subset-based (not strict dict equality) since
`formal.json` permanently lacks an opinion about REQ-DOSE-003 — the
temporary `run_formal_check`/`KNOWN_FORMAL_INTENT_DIVERGENCE` carve-out
is retired. `evidence/cli.py` gained `--dafny-captures` (a small JSON
index of *paths*, not inlined file content) — this turned out to be
necessary, not optional: once metadata.a.yaml/b.yaml declared dafny
evidence, the CLI genuinely could not build those variants without it.
Every variant artifact now reports `intent_ok: true` for both
REQ-GIP-1-4-12 and REQ-GIP-1-8-1; `run_gate()`'s facts count is 9, not
7. Full suite now 98 passed; full pipeline re-run end to end. Full
findings: `KNOWN_LIMITATIONS.md`.
