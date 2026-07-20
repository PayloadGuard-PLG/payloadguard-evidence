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

### What this has actually produced

Across the four worked examples, every one of 28 formalized
requirements carries a real evidence status — counted directly from
the committed traceability matrices, not estimated:

| Strength | Requirements |
|---|---|
| `PROVEN` | 20 |
| `BOUNDED_CHECKED` | 1 |
| `GAP` (explicit, named) | 7 |

Each `PROVEN` row now also carries a mechanically-derived **proof-content
qualifier** (`evidence/spec_impl_gap.py`, Gate C3 vector 3) distinguishing
what the proof actually establishes — because `PROVEN` alone conflates two
very different things. Of the 20 `PROVEN` requirements, **14 are
definitional** (the postcondition restates the implementation, so the proof
certifies totality/type-safety/exhaustiveness/boundary structure but not an
*independent* property) and **6 are property-bearing** (the postcondition is
strictly weaker than the body, so the proof carries content beyond the
definition):

| Example | definitional | property |
|---|---|---|
| `aeb_kernel` | 8 | 0 |
| `drug_interaction_checker` | 6 | 0 |
| `dosage_calculator` | 0 | 2 |
| `renal_adjustment` | 0 | 4 |

This is not a downgrade of the label — Dafny did discharge every spec — but
an honest statement of *which* `PROVEN` rows prove a non-trivial property and
which restate a definition. `aeb_kernel` and `drug_interaction_checker` are
predicate/lookup specs (`ensures` equivalent to the body); `dosage_calculator`
and `renal_adjustment` do real arithmetic, so their safety bounds are genuine
content. Neither the qualifier nor this table certifies fidelity of the
numbers to the source — that is a separate, named limitation.

The single `BOUNDED_CHECKED` requirement is `dosage_calculator`'s
overflow-safety check — a permanent Dafny/Z3 limit (no IEEE-754
overflow semantics for `real`), not an unbuilt item. Every `GAP` is
named and reasoned in [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md),
never dropped silently.

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
  fails to verify. A mutant can be verified against the mutated function
  in isolation (`evidence/dafny_isolate.py` — the function with its own
  callees, never its callers), so a kill is attributed to that
  function's own contract rather than to a downstream caller that
  happened to fail; without this, whole-file verification silently
  over-reports how load-bearing a spec is. All three worked Dafny
  examples (`renal_adjustment`, `dosage_calculator`,
  `drug_interaction_checker`) now run Gate C5 through this isolation.
  Surviving mutants are enumerated and explained.
- **C6 — Confirmation.** `evidence/dafny_nl_summary.py` renders each
  contract clause in plain English for a recorded human review prior to
  sign-off.

A worked instance of one requirement carried through all six gates, with
the verbatim captured output at each step, is committed under
`examples/drug_interaction_checker/`; the gates are described in full in
[`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) §4.

### Timed example: primary source to formal proof

`examples/aeb_kernel/` (built 2026-07-16) is a concrete, timed instance
of the pipeline above run end to end against a domain it wasn't built
for, using only a public source document — no clinical, patient, or
otherwise proprietary data. Source: NHTSA/DOT's public Final Rule
"Automatic Emergency Braking Systems for Light Vehicles" (49 CFR
571.127), a 317-page federal regulation.

Every number below is taken from committed git history and Dafny run
manifests, not reconstructed from memory:

- **Under 9 minutes** from the source document landing in the
  repository to a from-scratch formal specification — 6 Dafny
  functions, covering 8 distinct regulatory requirement clauses —
  verifying clean on its first real capture. This includes locating
  the actual operative clauses inside the document: ~300 of the 317
  pages are rulemaking preamble, not the codified regulatory text.
- **Under 8 minutes more** to run the remaining five independent
  verification gates for real: plain-English contract confirmation
  against the source text, 31 boundary-value proof lemmas, a
  precondition-satisfiability and postcondition-strength lint (zero
  weak-postcondition warnings — the tightest result this pipeline has
  produced across any example so far), a 63-mutant adversarial stress
  test of the proofs themselves, and a machine-generated regulatory
  traceability matrix.
- **Result:** 8 regulatory requirements with machine-checked (`PROVEN`)
  evidence status, and 2 requirements left as explicit, named open
  gaps rather than glossed over — the same discipline this system
  applies to every example, including the three medical-device ones.
- **No change to the underlying pipeline was needed.** The same code
  that verifies infusion-pump dosing logic against a clinical hazard
  analysis ran, unmodified, against a federal vehicle-safety
  regulation it had never been built or tuned for.

We haven't found a comparable automated, six-gate,
document-to-formal-proof pipeline elsewhere, and are treating that as
a real, differentiated capability until shown otherwise — research
still in progress. Accordingly, *how* each gate works stays described
here only at the level already used above; the implementation itself
is proprietary (see [`LICENSE`](LICENSE)). What's shown in this
example is the outcome, timed and reproducible from a public source
document — not the method.

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
applied and what's still open. **`dosage_calculator` now has real,
Steven-scored severity values for all 5 hazards** (`S3 — Serious`,
recorded 2026-07-15 via `AskUserQuestion` — a real clinical
determination, not inferred or defaulted by this repo's assistant),
which mechanically produce this device's current overall residual risk:
**`Unacceptable`** (4 of 5 hazards; the fifth, `HAZ-GIP-1.2b`, stays an
explicit evaluation `GAP`, blocked by a separate open question about
which procedure applies to a hazard with zero probability-side
evidence — see `RISK_MANAGEMENT_FINDINGS.md` Finding 5). This is not a
claim the device is newly unsafe — it is the honest output of a
real severity input meeting this plan's already-specified, conservative
worst-case-probability policy for a pre-market POC with no field data;
resolving it needs either real field data or a recorded ALARP
determination from Steven, both still open. `renal_adjustment`'s and
`drug_interaction_checker`'s hazard registers still leave every
severity value an explicit `GAP` — they complete identification only,
and their plans cite ISO 14971:2019 alone; extending them to
`dosage_calculator`'s TR-24971-informed model and real scoring is
future work, not started. Assigning a severity score, accepting a
residual risk, or closing a hazard as `Acceptable` is, for all three, a
human decision this repo's assistant has declined to make on a
reviewer's behalf, even where no further evidence is buildable.

**A real citation-integrity gap was also found and closed, 2026-07-15**
(`RISK_MANAGEMENT_FINDINGS.md` Finding 6): `dosage_calculator`'s
`HAZ-GIP-1.14` row had quoted its GIP source as "verbatim" without that
claim ever being checked against GIP v1.0's own PDF — a wording drift
this repo's own transcription had introduced, caught only when Steven
independently sourced and supplied the real document. Fixed against the
primary text, then taken one step further: Steven also obtained the
actual IEC 60601-2-24:1998 standard GIP's citation traces to, and its
clause 51.102 confirms GIP's citation is near-verbatim. Both primary
sources are now archived (`sources/gip-v1.0-full-2009.pdf`,
`sources/iec-60601-2-24-1998.pdf`) — this repo's first direct read of
the actual IEC 60601-2-24 standard text for any requirement, not a
secondary source taken on trust.

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
- **`examples/aeb_kernel/`** — a generic (non-manufacturer-specific)
  Autonomous Emergency Braking kernel; requirements from NHTSA FMVSS No.
  127 (49 CFR 571.127). The first example outside the medical-device
  domain, built to test whether the Gate C1–C6 architecture generalizes
  to a different regulatory domain entirely — it does, with no
  shared-code changes required. Exercises speed-envelope and
  deceleration-threshold logic.
- **`sources/`** — primary source documents, archived verbatim so every
  sourced requirement can be checked against the original.
- **`tests/`** — regression suite. Run `python -m pytest tests/ -q` for
  the current collected-case count, or see
  [`TEST_CATALOG.md`](TEST_CATALOG.md) for a categorized per-test index
  (counts test *functions*, a different and smaller number than
  pytest's case count wherever `@pytest.mark.parametrize` is used —
  neither number is restated here, to avoid the same staleness this
  file has already needed fixing for twice).

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

The traceability-matrix builder is also installable standalone, via
`pyproject.toml`:

```bash
pip install .
plg-evidence build --variant a \
  --metadata examples/dosage_calculator/metadata.a.yaml \
  --manifest examples/dosage_calculator/run_manifest.json \
  --concrete examples/dosage_calculator/concrete_results.json \
  --dafny-captures examples/dosage_calculator/dafny_captures_index.json \
  --out-json matrix.json --out-md matrix.md
```

This installs `evidence.cli` as a `plg-evidence` console script,
runnable from any directory — useful for building a matrix from
already-captured evidence without a full clone. It does not install
the verification toolchain: regenerating an example's underlying
Dafny/CrossHair evidence still needs the clone-based setup above.

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
- **Generic AEB kernel** — complete: all six gates built and confirmed,
  sourced directly from NHTSA FMVSS No. 127. The first example outside
  the medical-device domain — proves the pipeline is domain-agnostic,
  not medical-device-specific; every shared tool (`evidence.cli`,
  spec lint, NL confirmation, mutation testing) ran unmodified. Two
  requirements (`REQ-AEB-9` vehicle-class eligibility, `REQ-AEB-10`
  malfunction detection/mode controls) are deliberately unbuilt,
  tracked as open `GAP` rows; no ISO 26262 risk-management artifacts
  exist for this example yet.
- **Risk management artifacts (the three medical-device examples)** — `DRAFT`, not
  signed off. `dosage_calculator`'s is the most developed: hazard
  identification is real and complete, its severity model was rebuilt
  2026-07-15 to be consequence-only (ISO 14971 §3.27 / TR 24971
  §5.5.4), and Steven, the named Clinical SME, has since scored all 5
  hazards (`S3 — Serious`, every one). The device's overall residual
  risk is now **`Unacceptable`** — a real, computed result (four of
  five hazards; the fifth, `HAZ-GIP-1.2b`, stays an evaluation `GAP`,
  blocked by a separate open question about which procedure applies to
  a hazard with zero probability-side evidence), not the `GAP`
  placeholder the model-only fix left standing. This isn't a claim the
  device got less safe — it's the honest output of a real severity
  input meeting an already-conservative worst-case-probability policy
  for a pre-market POC with no field data. Resolving it needs either
  real field/usage data or a recorded ALARP determination from Steven —
  both still open. See
  [`RISK_MANAGEMENT_FINDINGS.md`](examples/dosage_calculator/RISK_MANAGEMENT_FINDINGS.md)
  for the live list of what's still undecided.

Full build history: [`DEVLOG.md`](DEVLOG.md). Open items and known gaps:
[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md).

## In progress and designed

Two improvements are named here rather than implied complete. Both have
landed in substance and are kept here for continuity (this section tracked
each while it was in progress); each still names the piece that remains
designed-but-unbuilt:

- **Isolated mutation testing — landed for all three worked Dafny
  examples (2026-07-20).** Gate C5 verifies each mutant against the
  mutated function in isolation (its own callees, never its callers), so
  a kill reflects that function's own contract rather than a downstream
  caller that happened to fail. The composition is a single sanctioned
  entry point, `evidence/gate_c5_runner.py`, which always isolates —
  there is no whole-file mode to forget. `renal_adjustment`,
  `dosage_calculator`, and `drug_interaction_checker` all now run Gate C5
  through it (the latter two via the runner's `body_function` and
  `survivor_escalation` extension points); each reproduces its committed
  report with every mutation outcome unchanged, since none of their
  mutation targets has an in-file caller for isolation to change — the
  guarantee is now in place and test-pinned, not merely available.

- **Distinguishing a proven property from a definitional restatement —
  landed (classification + labelling), 2026-07-20.** A `PROVEN` label
  means Dafny discharged the spec, but it conflates a proof of an
  *independent property* (e.g. `dosage_calculator`'s output-stays-within-
  safe-bounds — strictly weaker than the computation that produces it, so
  a wrong implementation could violate it) with a *definitional* spec that
  restates its own implementation (`aeb_kernel`'s threshold predicates and
  `drug_interaction_checker`'s per-case lookup, where the `ensures` clause
  is the function body). Both are real and machine-checked; they differ in
  how much *independent* content the proof carries. `evidence/spec_impl_gap.py`
  now classifies each `ensures` clause mechanically (structural
  pin-vs-bound analysis with a Z3 pin-uniqueness cross-check), and every
  `PROVEN` matrix row carries a `proof_content: definitional | property`
  qualifier with distinct caveat text (see the breakdown table above: 14
  definitional, 6 property). Still designed but **not** yet built: the
  Tier-2 fidelity work — mechanical source-citation of every spec constant
  and a source-anchored, blind human review — so a label also attests the
  numbers match the source, not only that the proof is internally sound.

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
| [`SYSTEM_REFERENCE.md`](SYSTEM_REFERENCE.md) | Pure current-state technical reference — no build history, regenerated in substance (not appended to) whenever the system's facts change. |
| [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md) | Technical reference: architecture, each gate, command reference, adding an example. |
| [`SYSTEM_BLUEPRINT.md`](SYSTEM_BLUEPRINT.md) | Component map and data-flow reference (build-history document, not current-state). |
| [`dashboards/`](dashboards/) | Dated HTML status snapshots (not auto-regenerated; see its README). |
| [`DEVLOG.md`](DEVLOG.md) | Dated, append-only build log. |
| [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | Ledger of open items and known gaps. |
| [`REVIEW_PROTOCOL.md`](REVIEW_PROTOCOL.md) | How generated artifacts are reviewed before use. |
| [`sources/README.md`](sources/README.md) | Discipline for adding and citing a primary source. |
| [`TEST_CATALOG.md`](TEST_CATALOG.md) | Generated, categorized index of every test in the suite — description and file:line pointer per test. Regenerate with `python -m evidence.test_catalog --out TEST_CATALOG.md`. |
| [`LICENSE`](LICENSE) | Proprietary — all rights reserved. Not open source. |
