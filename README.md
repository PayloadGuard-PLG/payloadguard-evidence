# PayloadGuard Evidence

PayloadGuard Evidence is a domain-agnostic compliance-evidence engine. It
generates traceability artifacts (IEC 62304 / FDA §524B style) for software
requirements: for each requirement it binds a claim to captured
verification-tool output and labels the result with an honestly-scoped
evidence strength, so a traceability matrix never states more than the
underlying evidence supports.

The system is built around a single constraint: a strength label is derived
only from what a verification tool actually reported in a real, recorded run.
It is never inferred from a requirement's intent, and the strongest label —
`PROVEN` — is admitted only when a completed Dafny/Z3 proof produced it. The
matrix is machine-generated from these inputs; it is never hand-edited, and
generation fails rather than emit a `PROVEN` label not backed by a real,
completed proof.

## What it produces

Every requirement answers three questions, and the generated traceability
matrix records all three:

1. **What must the software do (or never do)?** Traced to a primary source
   document — a hazard analysis, a safety standard, or a clinical guideline,
   archived verbatim in `sources/`.
2. **How is that established?** Traced to a specific run of a specific
   verification tool, with the tool's verbatim output committed alongside the
   claim.
3. **How strong is the evidence?** Labelled with one of the strengths below,
   so the confidence level is always explicit rather than inferred.

## Evidence strengths

| Label | Meaning |
|---|---|
| `PROVEN` | A machine-checked proof (Dafny/Z3) that the requirement holds for every input in scope. |
| `BOUNDED_CHECKED` | A bounded symbolic search (CrossHair) found no counterexample within a recorded budget. Not a proof; inputs outside the budget are not covered. |
| `TESTED` / `EXAMPLE_CHECKED` | Executed on specific concrete inputs with the expected result. No claim beyond those inputs. |
| `DECLARED` | Asserted by a human; not established by any tool. |
| `GAP` | Not yet established. Rendered explicitly, never omitted. |

Each label is legitimate evidence at its own level; the design goal is that
the level is always explicit. Across the four worked examples the committed
matrices record 28 formalized requirements, each carrying a real evidence
status:

| Strength | Requirements |
|---|---|
| `PROVEN` | 20 |
| `BOUNDED_CHECKED` | 1 |
| `GAP` (explicit, named) | 7 |

Every `GAP` is reasoned in [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md),
never dropped silently.

### The proof-content qualifier

`PROVEN` alone conflates two different things, so every `PROVEN` row also
carries a mechanically-derived qualifier (`evidence/spec_impl_gap.py`,
Gate C3 vector 3) stating what the proof actually establishes:

- **`definitional`** — the postcondition restates the implementation, so the
  proof certifies totality, type-safety, match-exhaustiveness, and boundary
  structure, but not an *independent* property.
- **`property`** — the postcondition is strictly weaker than the body, so the
  proof carries content beyond the definition (a wrong implementation could
  violate it).

Both are real and machine-checked; they differ in how much independent
content the proof carries. Of the 20 `PROVEN` requirements, 14 are
definitional and 6 are property-bearing:

| Example | definitional | property |
|---|---|---|
| `aeb_kernel` | 8 | 0 |
| `drug_interaction_checker` | 6 | 0 |
| `dosage_calculator` | 0 | 2 |
| `renal_adjustment` | 0 | 4 |

`aeb_kernel` and `drug_interaction_checker` are predicate/lookup specs
(`ensures` equivalent to the body); `dosage_calculator` and `renal_adjustment`
do real arithmetic, so their safety bounds are genuine content. The single
`BOUNDED_CHECKED` requirement is `dosage_calculator`'s overflow-safety check —
a permanent Dafny/Z3 limit (no IEEE-754 overflow semantics for `real`), not an
unbuilt item.

## The verification pipeline (Gates C1–C6)

Requirements backed by a formal (Dafny) specification pass through six gates.
Each captures or checks a distinct property, and every real tool run is
committed verbatim with a manifest recording the command, exit code, tool
version, and timestamp.

- **C1 — Capture.** The proof is run and its raw output committed. The adapter
  (`evidence/dafny_adapter.py`) distinguishes a real proof (`N verified, 0
  errors`, N > 0) from a vacuous `0 verified, 0 errors` before any `PROVEN`
  label is assigned.
- **C2 — Exclusivity.** `PROVEN` is attached only by
  `evidence/render/matrix_variants.py::dafny_record()`, re-derived from the raw
  capture. `assert_no_realized_proven` (ruling R3) rejects any record whose
  method is not `dafny` or whose `verifier_completion_status` is not
  `completed`.
- **C3 — Spec lint.** `evidence/dafny_spec_lint.py` checks precondition
  satisfiability via Z3, flags one-directional postconditions, refuses captures
  masked by resource or timeout limits, and classifies each `ensures` clause as
  definitional or property-bearing (the qualifier above).
- **C4 — Spec-testing proofs (STPs).** Specification-only ACCEPT/REJECT lemmas
  confirm the spec pins the intended value and excludes plausible weaker ones,
  independent of the implementation.
- **C5 — Mutation testing.** `evidence/dafny_mutate.py` perturbs the spec's
  operators and re-runs the verifier, confirming a wrong spec fails to verify.
  Each mutant is verified against the mutated function in isolation
  (`evidence/dafny_isolate.py` — the function with its own callees, never its
  callers), so a kill is attributed to that function's own contract rather than
  a downstream caller. The shared entry point `evidence/gate_c5_runner.py`
  always isolates; surviving mutants are enumerated and explained.
- **C6 — Confirmation.** `evidence/dafny_nl_summary.py` renders each contract
  clause in plain English for a recorded human review prior to sign-off.

The gates are described in full in
[`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) §4.

## Keeping `PROVEN` honest

`PROVEN` means Dafny discharged the spec — no more. On its own that conflates
whether the proof carries independent content, whether the spec's numbers
faithfully transcribe the source, and whether the contract itself was shaped to
be provable. A sequence of mechanisms separates and labels each:

- **Proof content** — the `definitional` / `property` qualifier above
  (`evidence/spec_impl_gap.py`), a structural pin-vs-bound analysis with a Z3
  pin-uniqueness cross-check.
- **Source fidelity** — every numeric constant in a spec carries a verbatim
  source quote, checked present in the archived primary document by a
  mechanical citation gate (`evidence/literal_citation.py` over
  `evidence/citation_gate.py`; each example commits a `literal_citations.yaml`).
  The Gate C6 review is source-anchored and **blind**
  (`evidence/source_anchored_review.py`): the reviewer records the value
  expected *from the source* before the spec's constant is revealed.
- **Frozen contract** — `evidence/frozen_contract.py` freezes each spec's
  contract surface (signatures, `requires`/`ensures`, function bodies, datatype
  definitions) as a committed, drift-checked manifest, and mechanically proves a
  candidate spec preserves it exactly and introduces no soundness-escape
  construct (e.g. `assume false`).
- **Ratification** — `evidence/contract_attestation.py` produces a per-example,
  hash-bound ratification artifact through which a human reviewer works
  eliminatively (producing and eliminating candidate defeaters against each
  declaration's mapped requirement and source quotes) and formally adopts the
  contract. The sha256 binding makes a signed adoption go stale the moment the
  contract changes.

The ratification artifacts are committed `PENDING`, one per example. Until a
reviewer completes each adoption, the provenance of the four specs is
*LLM-drafted, human-reviewed, gate-enforced — ratification pending*. On
signing, each earns *human-ratified*.

## Domain-agnostic engine

The engine (`evidence/`) is not medical-device-specific. Three worked examples
are medical, and one — `examples/aeb_kernel/` — applies the same Gate C1–C6
pipeline to a different regulatory domain entirely (NHTSA FMVSS No. 127,
automotive automatic emergency braking), sourced from public regulation, with
no shared-code changes. The same code that verifies infusion-pump dosing logic
against a clinical hazard analysis runs unmodified against a federal
vehicle-safety regulation.

The traceability-matrix engine is open to read here; the verification method
itself is proprietary (see [`LICENSE`](LICENSE)).

## Risk management (ISO 14971)

Each medical-device example carries an ISO 14971:2019 risk management plan and
hazard register (both `DRAFT`) that consume the engine's own evidence as
risk-control input: a `PROVEN`, `BOUNDED_CHECKED`, or `GAP` status feeds
directly into a hazard's evidence citations, so the risk analysis cannot claim
stronger grounding than the traceability matrix supports.

- `examples/<name>/RISK_MANAGEMENT_PLAN.md` — scope, risk-acceptance criteria,
  and a severity/probability/acceptance matrix (clause 4.4).
- `examples/<name>/HAZARD_REGISTER.md` — per-hazard entries citing the device's
  primary hazard-analysis or clinical source, this repo's own proof/test
  evidence as the risk-control measure, and an explicit `Known, named residual`.

Severity assessments and risk-acceptability determinations (including ALARP
determinations) are produced as decision-ready **prepared packages** —
evidence assembled, reasoning structured, open questions surfaced — for a
qualified clinical/regulatory subject-matter expert to ratify. The SME role is
**unfilled**; SME ratification is an explicit, recorded prerequisite, never
self-signed by the preparer. This mirrors the drafter≠checker boundary the
engine enforces throughout.

`dosage_calculator` is the most developed: hazard identification is complete,
its severity model is consequence-only (ISO 14971 §3.27 / ISO TR 24971
§5.5.4), and each hazard carries a prepared severity assessment. Its current
overall residual risk evaluates `Unacceptable` — the mechanical result of
prepared severity values under a conservative worst-case-probability policy for
a pre-market POC with no field data. Two hazards sit on a severity-alone
evaluation track (per ISO TR 24971 §5.5.3) with per-hazard determinations
prepared and SME sign-off pending. `renal_adjustment` and
`drug_interaction_checker` complete hazard identification only, with severity
left as explicit `GAP`.

Two repo-wide self-consistency lints (`evidence/hazard_id_lint.py`,
`evidence/citation_registry.py`) guard against cross-file drift — a hazard ID
referenced in one document but renamed or dropped in its register, or a
standards citation re-typed incorrectly in one file. Both scan the real,
git-tracked repository as part of the test suite.

## Repository layout

- **`evidence/`** — the domain-agnostic engine: schema validation, evidence
  binding, traceability-matrix generation, Dafny toolchain integration
  (capture, spec lint, mutation testing, NL confirmation), mechanical citation
  verification against a primary source (`citation_gate.py`), the `PROVEN`
  honesty mechanisms (`spec_impl_gap.py`, `literal_citation.py`,
  `frozen_contract.py`, `contract_attestation.py`, `source_anchored_review.py`),
  and repo self-consistency lints (`hazard_id_lint.py`, `citation_registry.py`).
- **`examples/dosage_calculator/`** — IV infusion-pump dose-clamping logic;
  requirements from a published infusion-pump hazard analysis. The most
  developed risk management plan and hazard register of the examples.
- **`examples/renal_adjustment/`** — renal-function dose adjustment;
  requirements from UK clinical guidelines (MHRA, KDIGO, NICE). Lookup-table and
  conditional-branching logic.
- **`examples/drug_interaction_checker/`** — DOAC drug-interaction checking;
  requirements from NHS Specialist Pharmacy Service guidance. Set/membership
  logic.
- **`examples/aeb_kernel/`** — a generic Autonomous Emergency Braking kernel;
  requirements from NHTSA FMVSS No. 127 (49 CFR 571.127). The non-medical
  example demonstrating the pipeline is domain-agnostic. Speed-envelope and
  deceleration-threshold logic.
- **`sources/`** — primary source documents, archived verbatim so every sourced
  requirement can be checked against the original.
- **`tests/`** — regression suite. Run `python -m pytest tests/ -q` for the
  current count, or see [`TEST_CATALOG.md`](TEST_CATALOG.md) for a categorized
  per-test index.

## Quick start

```bash
# Engine + test dependencies
pip install -r requirements.txt
# The formal-proof examples additionally require Dafny 4.11.0, Z3, and
# crosshair-tool; see OPERATIONS_MANUAL.md for install notes.

# Run the test suite
python -m pytest tests/ -q

# Regenerate the infusion-pump example's traceability matrices
cd examples/dosage_calculator
python generate_artifacts.py
```

The matrix builder is also installable standalone via `pyproject.toml`, which
exposes `evidence.cli` as a `plg-evidence` console script:

```bash
pip install .
plg-evidence build --variant a \
  --metadata examples/dosage_calculator/metadata.a.yaml \
  --manifest examples/dosage_calculator/run_manifest.json \
  --concrete examples/dosage_calculator/concrete_results.json \
  --dafny-captures examples/dosage_calculator/dafny_captures_index.json \
  --out-json matrix.json --out-md matrix.md
```

This builds a matrix from already-captured evidence without a full clone. It
does not install the verification toolchain; regenerating an example's
underlying Dafny/CrossHair evidence still needs the clone-based setup above.
For re-running the verification tools, adding a requirement, or extending the
system to a new example, see [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md).

## Scope

- **Not a PR-gate or merge-blocking CI tool.** A separate repository,
  `PayloadGuard-PLG/payload-consequence-analyser`, is that product; it shares no
  code with this one.
- **Not a replacement for human regulatory sign-off.** Every generated claim is
  reviewed by a person before use in a submission — see
  [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md).
- **Not a tool that infers evidence strength.** Strength labels come only from a
  verification tool's recorded output, never from a requirement's intended or
  hoped-for outcome.

## Further reading

| Document | Contents |
|---|---|
| [`SYSTEM_REFERENCE.md`](SYSTEM_REFERENCE.md) | Pure current-state technical reference — no build history, regenerated in substance (not appended to) whenever the system's facts change. |
| [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) | Technical reference: architecture, each gate, command reference, adding an example. |
| [`HANDOFF.md`](HANDOFF.md) | Current status and next steps for picking up the repository. |
| [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md) | Component map and data-flow reference (build-history document). |
| [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | Ledger of open items and known gaps. |
| [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) | How generated artifacts are reviewed before use. |
| [`DEVLOG.md`](DEVLOG.md) | Dated, append-only build log — the full development history. |
| [`sources/README.md`](sources/README.md) | Discipline for adding and citing a primary source. |
| [`TEST_CATALOG.md`](TEST_CATALOG.md) | Generated, categorized index of every test. Regenerate with `python -m evidence.test_catalog --out TEST_CATALOG.md`. |
| [`dashboards/`](dashboards/) | Dated HTML status snapshots (not auto-regenerated; see its README). |
| [`LICENSE`](LICENSE) | Proprietary — all rights reserved. Not open source. |
