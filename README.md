# payloadguard-evidence

Compliance-evidence generator for medical device software. It consumes
formal-verification output (CrossHair today; Dafny and Z3 planned for Phase B)
and a structured metadata file, and emits IEC 62304 / FDA §524B-oriented
traceability artifacts in which every claim is bound to a specific,
committed verification capture of known strength.

**Status:** Phase A complete and closed out (rulings R1–R3 applied,
2026-07-04). Phase B (adapters, vocabulary-agnostic binder, CLI) not started.

Companion documents: [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md) (structure
and data flow), [`DEVLOG.md`](DEVLOG.md) (dated session log),
[`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) (two-tier review: machine gates
stop defects, humans review per-reason),
[`examples/dosage_calculator/README.md`](examples/dosage_calculator/README.md)
(audit-trail record for the worked example),
[`examples/dosage_calculator/RECONCILIATION.md`](examples/dosage_calculator/RECONCILIATION.md)
(schema-variant reconciliation).

## What this is not

- Not a PR-gate or merge-blocking tool. (The separate
  `PayloadGuard-PLG/payload-consequence-analyser` repository is that product;
  this repository shares no code with it.)
- Not a replacement for human regulatory sign-off. Every generated claim is
  reviewed by a human before it enters a real submission.
- Not a tool that infers or estimates evidence strength. Strength labels come
  only from what a verifier actually reported in a committed capture.

## Claims discipline

Strength vocabulary (`evidence/model.py`, single source of truth):

| Strength | Meaning | Caveat carried on every rendered record |
|---|---|---|
| `PROVEN` | Machine-checked deductive proof (Dafny/Z3 — not wired in Phase A) | Formally proven against the stated specification. |
| `BOUNDED_CHECKED` | CrossHair pass within recorded bounds | No counterexample found within the recorded bounds; this is a bounded search, not a proof. |
| `TESTED` | Concrete test cases executed | Exercised on the recorded test cases only. |
| `EXAMPLE_CHECKED` | Specific recorded input/output pairs executed | Holds for the specific recorded inputs only; no claim of generality beyond them. |
| `DECLARED` | Human assertion, no tool evidence | Asserted by the author; not established by any tool. |
| `GAP` | Nothing established | Not established. Human input required. |

Standing rules, machine-enforced where possible:

- Strength comes only from verification results, never from a requirement's
  `intended_method`. Intended-vs-realized mismatches are rendered explicitly
  (`intent_ok: false`, note `intended PROVEN, realized BOUNDED_CHECKED`).
- `PROVEN` never appears as a realized strength in any generated record or
  cell. This is a structural assertion in the generation path
  (`assert_no_realized_proven`) and a pytest, not a text grep. Quoting
  authored metadata inside mismatch notes is permitted (ruling R2).
- `intent_ok` is requirement-scoped and derived exactly once at bind time —
  true iff any evidence record for the requirement realizes the intended
  strength; all rendered views carry it read-only (ruling R1).
- Gaps are signalled by field absence, never by placeholder strings.
- Every capture is a real run: verbatim tool output, exact command, and exit
  code are committed together. Unexpected results are recorded and reported,
  never re-rolled.

## End-to-end flow

```
authored inputs                 captures (real runs)             generation
---------------                 --------------------             ----------
metadata.yaml                   run_verify*.py -> raw CrossHair  generate_matrix*.py
  (device, requirements,          output + run manifest            validate metadata
   threat model, toolchain      run_verify_concrete.py ->          against schema,
   bounds; validated against      pytest capture +                 bind evidence to
   evidence/schema/*.json)        concrete_results.json            requirements,
sources/*.md                    exhibit_pin_*.json                 derive intent once,
  (primary source documents       (tool/platform pinning +         render matrices
   grounding every sourced        mechanism attribution)           (JSON + Markdown)
   requirement)
```

1. **Author metadata.** `examples/*/metadata.yaml` declares the device, its
   requirements (each with source citation or an explicit DECLARED marker),
   threat model, and the intended verification envelope. Every sourced claim
   traces to a document archived verbatim in `sources/`.
2. **Capture evidence.** Runner scripts invoke the verifier as a subprocess
   and commit stdout+stderr verbatim alongside a JSON manifest (tool version,
   exact command, exit code, ISO-8601 UTC timestamp). Concrete test evidence
   is captured the same way from a pytest run plus a structured
   `concrete_results.json` whose observed values come from real execution.
3. **Generate.** Generator scripts validate the metadata against its JSON
   Schema (draft 2020-12), bind captures to requirements, derive
   requirement-scoped intent, run the structural PROVEN check, and write the
   traceability matrix as JSON and Markdown. Committed matrices are always
   generated by this path, never hand-typed.

## The worked example: infusion-dose kernel

`examples/dosage_calculator/` is a complete proof-of-concept:

- `dosage.py` — pure dose-clamping kernel with CrossHair PEP316 contracts.
  Negative infusion rates model the reverse-delivery single-fault condition
  of GIP v1.0 Safety Requirement 1.8.1 (negative rate ⇒ exactly zero dose).
- `metadata.yaml` — three requirements sourced from Arney et al. (2009),
  *Generic Infusion Pump Hazard Analysis and Safety Requirements v1.0*
  (archived verbatim in `sources/gip-v1.0-hazard-analysis.md`).
- Captured fixture pairs (all real runs): Sample A (clean pass), Sample B
  (broken variant, two counterexamples), Sample C (naive-widening exhibit),
  and the domain-free overflow probe.
- Generated traceability matrices in four shapes (base + three T4 schema
  variants, kept deliberately parallel for side-by-side audit — see
  `RECONCILIATION.md`).

### Honesty exhibits

Two committed exhibit pairs document what a `BOUNDED_CHECKED` result does and
does not establish. A bounded result is incomplete in two distinct ways:
**(1) search-budget incompleteness** — only part of the input space is
explored within the recorded bounds — and **(2) model-fidelity
incompleteness** — CrossHair predominantly models floats as mathematical
reals, sampling IEEE-faithful execution only infrequently (changelog
v0.0.72), so some real violations are reached only through an unreliably
sampled, sharply complexity-dependent channel:

- `dosage_naive_widening.py` + capture: a wrong-branch-order variant with a
  deterministic violation (`f(70.0, 1e308, -2.0, 10.0)` returns the maximum
  dose where the contract requires 0.0) that CrossHair did **not** find
  (exit 0).
- `overflow_probe.py` + capture: a one-operation function whose IEEE overflow
  CrossHair **did** find (exit 1).

Same invocation, same bounds — the paired measurement is pinned in
`exhibit_pin_naive_widening.json` and `exhibit_pin_overflow_probe.json`, and
nothing in the recorded bounds discloses which regime a run sat in. This is
the in-repo demonstration of why `BOUNDED_CHECKED` must never be presented
as proof.

## Running it

```bash
pip install crosshair-tool jsonschema pyyaml pytest

# test suite (concrete evidence, probe, structural PROVEN check)
python -m pytest tests/ -v

# re-capture verification evidence (writes verbatim output + manifests)
cd examples/dosage_calculator
python run_verify.py                 # Sample A: dosage.py
python run_verify_broken.py          # Sample B: broken variant
python run_verify_naive_widening.py  # Sample C exhibit
python run_verify_overflow_probe.py  # overflow probe
python run_verify_concrete.py        # pytest capture + concrete_results.json

# regenerate traceability matrices (schema-validated, structurally checked)
python generate_artifacts.py         # END-TO-END PIPELINE (Turn B4): schema
                                     # validation -> capture integrity ->
                                     # regeneration + fact-equality gate ->
                                     # structural PROVEN sweep -> provenance
                                     # index (artifact_index.json)
python regenerate_all.py             # inner regeneration step: variant
                                     # generators + the fact-equality gate
python generate_matrix.py            # base matrix (frozen legacy view)
```

Individual variant generators (`generate_matrix_a.py` / `_b.py` / `_c.py`)
exist but bypass the generation-time fact-equality gate; committed
divergence is still caught by `tests/test_fact_equality.py`.

Toolchain pinned by the exhibits: crosshair-tool 0.0.107, Python 3.11,
Linux x86_64. Exhibit claims are version-contingent and scoped to their pins.

## Known limitations and open items

- Declared CrossHair bounds in `metadata.yaml` are the intended envelope;
  each manifest's `effective_bounds` records what the run demonstrated
  (Turn 2.0). The Sample A/B captures enforce `--per_condition_timeout 30`;
  `max_iterations` and `seed` remain declared-only — the 0.0.107 CLI cannot
  enforce them (gap open at the tool level, Phase B may close it via the
  API). Every variant matrix carries the declared/effective block.
- Binding authorship differs across T4 variants (metadata-authored in A/B,
  evidence-store-carried in C) — open, deferred to Phase B
  (`RECONCILIATION.md`, asymmetry 2).
- The `FRN` pump-type tag in the GIP v1.0 source is undefined in the
  extracted text and remains an explicitly unresolved open question.
- Dafny/Z3 adapters, the CONFLICT rule, and the vocabulary-agnostic binder
  are Phase B; nothing in this repository currently claims `PROVEN` as a
  realized strength.
