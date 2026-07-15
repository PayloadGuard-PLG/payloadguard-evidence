# PayloadGuard Evidence

PayloadGuard Evidence generates IEC 62304 / FDA §524B traceability
artifacts for medical device software. For each requirement it binds a
claim to captured verification-tool output and labels the result with an
honestly-scoped evidence strength, so a traceability matrix never states
more than the underlying evidence supports.

The system is built around a single constraint: a strength label is
derived only from what a verification tool actually reported in a real,
recorded run. It is never inferred from a requirement's intent, and the
strongest label — `PROVEN` — is admitted only when a completed Dafny/Z3
proof produced it.

## What it produces

Every requirement is expected to answer three questions, and the
generated traceability matrix records all three:

1. **What must the software do (or never do)?** Traced to a primary
   source document — a hazard analysis, a safety standard, or a clinical
   guideline.
2. **How is that established?** Traced to a specific run of a specific
   verification tool, with the tool's verbatim output committed
   alongside the claim.
3. **How strong is the evidence?** Labelled with one of the strengths
   below, so the confidence level is always explicit rather than
   inferred.

## Evidence strengths

| Label | Meaning |
|---|---|
| `PROVEN` | A machine-checked proof (Dafny/Z3) that the requirement holds for every input in scope. |
| `BOUNDED_CHECKED` | A bounded symbolic search (CrossHair) found no counterexample within a recorded budget. Not a proof; inputs outside the budget are not covered. |
| `TESTED` / `EXAMPLE_CHECKED` | Executed on specific concrete inputs with the expected result. No claim beyond those inputs. |
| `DECLARED` | Asserted by a human; not established by any tool. |
| `GAP` | Not yet established. Rendered explicitly, never omitted. |

Each label is legitimate evidence at its own level; the design goal is
that the level is always explicit. The traceability matrix is
machine-generated from these inputs — it is never hand-edited, and
generation fails rather than emit a `PROVEN` label that is not backed by
a real, completed proof.

## The verification pipeline (Gates C1–C6)

Requirements backed by a formal (Dafny) specification pass through six
gates. Each captures or checks a distinct property, and every real tool
run is committed verbatim with a manifest recording the command, exit
code, tool version, and timestamp.

- **C1 — Capture.** The proof is run and its raw output committed. The
  adapter (`evidence/dafny_adapter.py`) distinguishes a real proof
  (`N verified, 0 errors`, N > 0) from a vacuous `0 verified, 0 errors`
  before any `PROVEN` label is assigned.
- **C2 — Exclusivity.** `PROVEN` is attached only by
  `evidence/render/matrix_variants.py::dafny_record()`, re-derived from
  the raw capture. `assert_no_realized_proven` (ruling R3) rejects any
  record whose method is not `dafny` or whose
  `verifier_completion_status` is not `completed`.
- **C3 — Spec lint.** `evidence/dafny_spec_lint.py` checks precondition
  satisfiability via Z3, flags one-directional postconditions, and
  refuses captures masked by resource or timeout limits.
- **C4 — Spec-testing proofs (STPs).** Specification-only ACCEPT/REJECT
  lemmas confirm the spec pins the intended value and excludes plausible
  weaker ones, independent of the implementation.
- **C5 — Mutation testing.** `evidence/dafny_mutate.py` perturbs the
  spec's operators and re-runs the verifier, confirming a wrong spec
  fails to verify. Surviving mutants are enumerated and explained.
- **C6 — Confirmation.** `evidence/dafny_nl_summary.py` renders each
  contract clause in plain English for a recorded human review prior to
  sign-off.

A worked instance of one requirement carried through all six gates, with
the verbatim captured output at each step, is committed under
`examples/drug_interaction_checker/`; the gates are described in full in
[`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) §4.

## Risk management (ISO 14971)

Each of the three examples also carries a **risk management plan** and
**hazard register**, built against ISO 14971:2019, that consume this
system's own evidence as risk-control input — a `PROVEN` Dafny result,
a `BOUNDED_CHECKED` CrossHair result, or an explicit `GAP` each feeds
directly into a hazard's evidence citations, so the risk analysis can't
silently claim stronger grounding than the traceability matrix itself
supports.

- `examples/<name>/RISK_MANAGEMENT_PLAN.md` — scope, risk-acceptance
  criteria, and a severity/probability/acceptance matrix, per clause
  4.4.
- `examples/<name>/HAZARD_REGISTER.md` — per-hazard entries citing the
  device's primary hazard-analysis or clinical source, this repo's own
  proof/test evidence as the risk-control measure, and an explicit
  `Known, named residual`.

**All three are `DRAFT`, not signed off, and at meaningfully different
stages — stated plainly rather than implied uniform.**
`dosage_calculator`'s is by far the most developed: hazard
identification is complete, its severity **model** was rebuilt
consequence-only (2026-07-15, replacing an earlier model that measured
evidence strength instead of real-world consequence — see
`RISK_MANAGEMENT_FINDINGS.md` Finding 3), its equivalence with the
Python implementation is now differentially tested rather than merely
asserted (Finding 5/R5, also resolved 2026-07-15), its citations were
extended to ISO/TR 24971:2020 during an earlier audit, and a findings
ledger (`RISK_MANAGEMENT_FINDINGS.md`) tracks corrections already
applied and what's still open. **Every hazard's severity value is an
explicit `GAP` across all three examples** — `dosage_calculator`'s
model and evidence citations are more developed, not its scored values,
which remain Steven's clinical call same as the other two.
`renal_adjustment`'s and `drug_interaction_checker`'s hazard registers
complete identification only, and their plans cite ISO 14971:2019
alone; extending them to `dosage_calculator`'s TR-24971-informed model
is future work, not started. Assigning a severity score, accepting a
residual risk, or closing a hazard as `Acceptable` is, for all three, a
human decision this repo's assistant has declined to make on a
reviewer's behalf, even where no further evidence is buildable.

Two repo-wide self-consistency lints (`evidence/hazard_id_lint.py`,
`evidence/citation_registry.py`) guard against exactly the kind of
cross-file drift this discipline is exposed to: a hazard ID referenced
in one document but renamed or dropped in the register it comes from,
or a standards citation re-typed incorrectly in one file without the
others being checked. Both scan the real, git-tracked repository as
part of the regular test suite.

## Repository layout

- **`evidence/`** — the domain-agnostic engine: schema validation,
  evidence binding, traceability-matrix generation, Dafny toolchain
  integration (capture, spec lint, mutation testing, NL confirmation),
  mechanical citation verification against a primary source
  (`citation_gate.py`), and repo self-consistency lints against this
  repo's own committed content (`hazard_id_lint.py`,
  `citation_registry.py`).
- **`examples/dosage_calculator/`** — IV infusion-pump dose-clamping
  logic; requirements from a published infusion-pump hazard analysis.
  Carried through proof and mutation testing; the most developed risk
  management plan and hazard register of the three examples.
- **`examples/renal_adjustment/`** — renal-function dose adjustment;
  requirements from UK clinical guidelines (MHRA, KDIGO, NICE).
  Exercises lookup-table and conditional-branching logic.
- **`examples/drug_interaction_checker/`** — DOAC drug-interaction
  checking; requirements from NHS Specialist Pharmacy Service guidance.
  Exercises set/membership logic.
- **`sources/`** — primary source documents, archived verbatim so every
  sourced requirement can be checked against the original.
- **`tests/`** — regression suite (251 tests; see
  [`TEST_CATALOG.md`](TEST_CATALOG.md) for the current, generated count
  and a categorized per-test index — not restated here to avoid the
  same staleness this file has already needed fixing for once).

## Quick start

```bash
pip install crosshair-tool jsonschema pyyaml pytest
# Dafny 4.11.0 and Z3 are required for the formal-proof examples;
# see OPERATIONS_MANUAL.md for install notes.

# Run the test suite
python -m pytest tests/ -v

# Regenerate the infusion-pump example's traceability matrices
cd examples/dosage_calculator
python generate_artifacts.py
```

For re-running the verification tools, adding a requirement, or
extending the system to a new example, see
[`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md).

## Status

- **Infusion-pump dose calculator** — complete: source citation, formal
  specification, proof, mutation testing, and recorded human
  confirmation.
- **Drug-drug interaction checker** — complete: all six verification
  gates built and confirmed.
- **Renal-function dose adjustment** — complete: all six gates built and
  confirmed, including a proven Cockcroft-Gault CrCl computation from raw
  patient inputs. CKD-EPI eGFR is caller-supplied — a Dafny/Z3
  expressiveness limit, confirmed empirically. Several requirements
  (`REQ-RENAL-3/4/6/7`, and `REQ-RENAL-8`'s classification-flag
  provenance) are deliberately unbuilt and tracked as open items; none
  blocks the pipeline.
- **Risk management artifacts (all three examples)** — `DRAFT`, not
  signed off. `dosage_calculator`'s is the most developed: hazard
  identification is real and complete, and its severity model was
  rebuilt 2026-07-15 to be consequence-only (ISO 14971 §3.27 / TR
  24971 §5.5.4), replacing an earlier model that measured evidence
  strength instead. The device's overall residual risk currently
  evaluates `GAP` — not `Acceptable`, not `Unacceptable` — pending a
  named Clinical SME's real, consequence-based severity score for each
  hazard, an explicit, honestly-rendered open finding, not a gap in the
  pipeline. See
  [`RISK_MANAGEMENT_FINDINGS.md`](examples/dosage_calculator/RISK_MANAGEMENT_FINDINGS.md)
  for the live list of what's still undecided.

Full build history: [`DEVLOG.md`](DEVLOG.md). Open items and known gaps:
[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md).

## Scope

- **Not a PR-gate or merge-blocking CI tool.** A separate repository,
  `PayloadGuard-PLG/payload-consequence-analyser`, is that product; it
  shares no code with this one.
- **Not a replacement for human regulatory sign-off.** Every generated
  claim is reviewed by a person before use in a submission — see
  [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md).
- **Not a tool that infers evidence strength.** Strength labels come
  only from a verification tool's recorded output, never from a
  requirement's intended or hoped-for outcome.

## Further reading

| Document | Contents |
|---|---|
| [`HANDOFF.md`](HANDOFF.md) | Current status and next steps for picking up the repository. |
| [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) | Technical reference: architecture, each gate, command reference, adding an example. |
| [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md) | Component map and data-flow reference. |
| [`dashboards/`](dashboards/) | Dated HTML status snapshots (not auto-regenerated; see its README). |
| [`DEVLOG.md`](DEVLOG.md) | Dated, append-only build log. |
| [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | Ledger of open items and known gaps. |
| [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) | How generated artifacts are reviewed before use. |
| [`sources/README.md`](sources/README.md) | Discipline for adding and citing a primary source. |
| [`TEST_CATALOG.md`](TEST_CATALOG.md) | Generated, categorized index of every test in the suite — description and file:line pointer per test. Regenerate with `python -m evidence.test_catalog --out TEST_CATALOG.md`. |
