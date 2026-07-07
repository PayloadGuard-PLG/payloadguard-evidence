# payloadguard-evidence

Compliance-evidence generator for medical device software. It consumes
formal-verification output (CrossHair today; Dafny and Z3 planned for Phase B)
and a structured metadata file, and emits IEC 62304 / FDA §524B-oriented
traceability artifacts in which every claim is bound to a specific,
committed verification capture of known strength.

**Status (2026-07-06):** Phase A complete and closed out (rulings R1–R3).
Turn 2.0 shipped (declared/effective bounds reconciliation, mechanized
fact-equality gate, two-tier review protocol). Phase B Gate 1 complete
(end-to-end pipeline + provenance index) with Gate 1 review remediation
applied (REQ-GIP-1-4-12 alarm-scope split, renderer notes fixes). Gates 3
(bounds enforcement, decided: stay-CLI), 4 (binding authorship, decision
+ mechanism recorded, implemented for all three metadata shapes), 5
(single-evidence-type fixture for variant C, fully resolved — both
symbolic-only and concrete-only now constructible), and 6 (FRN,
resolved) closed. **Gate 2 is now complete.** Its CONFLICT rule
(both Type 1 and Type 2) is built; `build_matrix()` is the sole
implementation across all four variants — all three generator scripts
and the CLI (`python -m evidence.cli build`, `evidence/cli.py`) call
it — with Type 1 folded in, running on every call, and Type 2 staying a
standalone stage by design (a whole-dataset check with no per-variant
home). The original per-variant functions and the equivalence test that
checked `build_matrix()` against them are deleted, per explicit
direction to build the CLI first — git history holds them if ever
needed again. **Phase B's gate ledger is now fully closed.**

Phase C is in progress: restructured from a two-mechanism sketch into a
gate-sequenced plan (Gates C1–C6) in
`payloadguard-evidence-roadmap-phaseB-to-C.md`. Gate C1's Dafny
toolchain blocker is resolved — Z3 4.16.0 was already present; modern
**Dafny 4.11.0** was obtained via `dotnet tool install --global dafny`
(NuGet, not GitHub — GitHub release downloads are genuinely blocked by
this environment's egress policy), then verified against the real
binary (exact false-zero match, real exit-code behavior, the
vacuous-precondition risk confirmed reproducible and its Z3-based
mitigation confirmed feasible). **Gate C1 itself is now built:** a real
Dafny spec for the dosage kernel (`examples/dosage_calculator/dosage.dfy`,
verifies clean; REQ-DOSE-003 named as an explicit scope exclusion —
Dafny's `real` type has no IEEE overflow concept), a capture runner
pair, and `evidence/dafny_adapter.py`'s false-zero-guard parser (regex
on the verifier's own summary line, regression-tested against a
substring trap). **Gate C2 is also now built:** ruling **R3** supersedes
R2 — `assert_no_realized_proven` now permits PROVEN as a realized
strength only for a record with `method == "dafny"` **and**
`verifier_completion_status == "completed"`; every other method
(`crosshair`, `concrete_test`, or no method at all) remains permanently
excluded, checked explicitly in 8 new tests
(`tests/test_proven_exclusivity.py`), not by omission. **Gate C3 is also
now built for 3 of its 4 named vectors:** `evidence/dafny_spec_lint.py`
adds a real Z3-based vacuous-precondition check (proven against a real
committed fixture, `examples/dosage_calculator/vacuous_precondition_probe.dfy`,
that Dafny itself verifies clean — `1 verified, 0 errors` — despite an
unsatisfiable precondition) and a best-effort weak-postcondition
heuristic; `evidence/dafny_adapter.py`'s summary-line parser is hardened
after a real finding on the installed binary — a resource-starved run
(`dafny verify --resource-limit=1`) can report `0 errors` alongside an
`"N out of resource"` marker (the real capture's exit code is confirmed
nonzero, so already caught; hardened independently anyway). Vector 4
(specification stripping) stays BLOCKED, named. **Gate C4 (Spec-Testing
Proofs) is also now built, and found a real gap on its first
application:** a Dafny lemma trying to prove a wrong candidate dose
value impossible for `dosage.dfy`'s original postcondition failed to
verify — the spec bounded `dose` but never pinned it to the actual
clamped value, so a broken implementation could have satisfied it
undetected. Fixed for real: `dosage.dfy` gained a `function
ExpectedDose(...)` and a pinning `ensures dose == ExpectedDose(...)`
clause, re-verified clean (`2 verified, 0 errors`, up from `1 verified`
— the real committed capture was re-run honestly to match). The
original is preserved byte-for-byte as `dosage_underconstrained.dfy`
(same rationale as `dosage_naive_widening.py`); two STP suites
(`dosage_stp_suite.dfy`, `dosage_stp_suite_against_underconstrained.dfy`)
mechanically prove both directions for real — six lemmas pass against
the fix, the same two REJECT lemmas genuinely fail against the preserved
original.

**Gate 2/C2-C4 wiring is also now built, and extended to every schema
variant — the first real Dafny-sourced PROVEN evidence ever to reach a
live, rendered matrix row.** `traceability_matrix.formal.json` (variant
C's third partition, extending Gate 5's dual-matrix pattern to a triple)
binds real `dosage.dfy` evidence to REQ-GIP-1-4-12 and REQ-GIP-1-8-1,
gated inside the binder itself by Z3 precondition satisfiability (Gate
C3) and the false-zero guard (Gate C1) before any record is even
constructed — built and confirmed correct for variant C first, then
**extended to variants A and B the same day**: `metadata.a.yaml`'s
evidence list and `metadata.b.yaml`'s new `.formal-N` shadow rows
declare the same real evidence; the CLI gained `--dafny-captures`
(required, not optional, once A/B declared it); the fact-equality
gate's intent comparison became subset-based, since
`traceability_matrix.formal.json` permanently lacks an opinion about
REQ-DOSE-003 (out of `dosage.dfy`'s scope by design). **`intent_ok` is
now `True` for both requirements in every variant artifact** — the
first time since Phase A that `intended_method: "PROVEN"` has been
realized everywhere it's declared. See `KNOWN_LIMITATIONS.md` for the
live gate ledger.

**Gate C6 (NL-dialogue confirmation) is also now built and signed off.**
`evidence/dafny_nl_summary.py::summarize_method` mechanically summarizes
a Dafny method's requires/ensures clauses in plain English — the raw
clause verbatim plus a best-effort operator-substitution gloss, labeled
explicitly as a reading aid, not comprehension — cross-checked by content
against `dafny_spec_lint`'s canonical extractor and refusing on any
multi-line clause it can't safely associate a citation with. But the
gate's actual deliverable, per its own definition, is not this code — it
is the recorded human decision it feeds:
[`examples/dosage_calculator/nl_confirmation_dosage_dfy.md`](examples/dosage_calculator/nl_confirmation_dosage_dfy.md)
records Steven's sign-off on the generated summary for
`dosage.dfy::CalculateHourlyDose` ("it's good for the spec as is"), plus
a next-phase item he explicitly scoped out as separate follow-up work.

**Gate C5 (mutation testing) is also now built, and extended the same
day from external research — zero survivors, zero unclassifiable
remain.** `evidence/dafny_mutate.py` generates ROR/LOR/AOR/COI mutants
against `dosage.dfy`'s requires/ensures clauses (and, as of the
extension, `ExpectedDose`'s function body);
[`examples/dosage_calculator/run_mutation_suite.py`](examples/dosage_calculator/run_mutation_suite.py)
real-verifies every one against the installed Dafny binary. The v1 build
found 2 real survivors — `infusionRateMlPerHr >= 0.0 || dose == 0.0`
weakened at its first disjunct still verified, because real
multiplication by exactly `0.0` already makes `dose == 0.0` hold at that
boundary — a real, understood looseness in REQ-GIP-1-8-1's
postcondition, **reported to Steven for a decision, not silently
changed** in the spec he'd just signed off on in Gate C6; his decision,
"go ahead and tighten REQ-GIP-1-8-1 to `>`," fixed it. External research
into that finding and a separate mutation-engine gap
([full findings](examples/dosage_calculator/gate_c5_mutation_testing_research_findings.md))
then produced one correction (Gate C5 was mislabeled
"MutDafny/IronSpec-style" — corrected to MutDafny-style) and two
concrete follow-ups, both built the same day on "build both":
**chain-direction-aware ROR** (restricts each chained-comparison link's
candidates to direction-compatible operators, per the Dafny Reference
Manual's own chaining rule — eliminates 4 formerly-unclassifiable
mutants by construction, ahead of what MutDafny itself does) and
**function-body AOR** (extends mutation to `ExpectedDose`'s one
arithmetic operator, restricted to MutDafny's own group rule so a
mutation can never introduce `/` where the original had none —
eliminating the division-by-zero false-kill risk by construction, not
post-hoc attribution). Final real run: **42 mutants — 31 killed, 6
filtered_static, 4 filtered_chain_incompatible, 1
filtered_ar_group_incompatible — zero survived, zero unclassifiable** —
see
[`examples/dosage_calculator/mutation_report.md`](examples/dosage_calculator/mutation_report.md)
for the full per-mutant outcome and `KNOWN_LIMITATIONS.md` for complete
detail.

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

# Gate 2 CLI: vocabulary-agnostic - takes any metadata/manifest/
# concrete-store path, not just this worked example (run from repo root)
python -m evidence.cli build --variant a \
    --metadata examples/dosage_calculator/metadata.a.yaml \
    --manifest examples/dosage_calculator/run_manifest.json \
    --concrete examples/dosage_calculator/concrete_results.json \
    --out-json /tmp/out.json --out-md /tmp/out.md
```

Individual variant generators (`generate_matrix_a.py` / `_b.py` / `_c.py`,
and the CLI above) bypass the generation-time fact-equality gate, which is
a property of the whole four-artifact set and can only run after all four
exist; committed divergence is still caught by `tests/test_fact_equality.py`.
They do NOT bypass the Gate 2 CONFLICT Type 1 check — that runs inside
`build_matrix()` itself now, on every call, however it's invoked.

Toolchain pinned by the exhibits: crosshair-tool 0.0.107, Python 3.11,
Linux x86_64. Exhibit claims are version-contingent and scoped to their pins.

## Known limitations and open items

- Declared CrossHair bounds in `metadata.yaml` are the intended envelope;
  each manifest's `effective_bounds` records what the run demonstrated
  (Turn 2.0). The Sample A/B captures enforce `--per_condition_timeout 30`;
  `max_iterations` and `seed` remain declared-only. **Gate 3 decided
  2026-07-06 (stay-CLI):** a corrected seed-override patch
  (`crosshair.statespace.make_default_solver`) was actually run twice per
  target with different seeds — both the clean and broken dosage kernels
  produced byte-identical results regardless of seed, so the patch is
  documented as having no observed effect and the CLI capture stays as
  the evidence path; `seed` remains a hard tool-version limitation
  (tool-fixed at 42) and `max_iterations` remains enforceable only via the
  API, not the CLI. Verification script and full findings:
  `examples/dosage_calculator/gate3_seed_patch_test.py`,
  `KNOWN_LIMITATIONS.md`. Every variant matrix carries the
  declared/effective block.
- Binding authorship differs across T4 variants (metadata-authored in A/B,
  evidence-store-carried in C). **Gate 4 decision recorded:** both models,
  cross-checked, with a Tier-1 failure on disagreement (dual-authorship
  code-location matching) — building it is Gate 2's binder work, not yet
  started (`RECONCILIATION.md` asymmetry 2, `KNOWN_LIMITATIONS.md`).
- The `FRN` pump-type tag in the GIP v1.0 source is now resolved (FDA
  Product Code for "Infusion Pump," 21 CFR 880.5725) — see
  `sources/README.md` and `KNOWN_LIMITATIONS.md` (Gate 6) for the
  citation trail and the one open caveat (not yet independently
  re-verified against the raw source text).
- Dafny/Z3 adapters are Phase C; nothing in this repository currently
  claims `PROVEN` as a realized strength. **Gate 2 is complete** — both
  CONFLICT sub-types, Type 1 (identity mismatch) and Type 2 (outcome
  mismatch) (`evidence/conflict.py`, 12 tests in
  `tests/test_conflict_check.py`), implement Gate 4's cross-check
  mechanism for all three metadata shapes, including variant C (whose
  declared-binding asymmetry is closed). `build_matrix()` is the sole
  implementation across all four variants — all three generator scripts
  and the CLI (`python -m evidence.cli build`, `evidence/cli.py`) call
  it — running Type 1 internally on every call. Type 2 stays a
  standalone `generate_artifacts.py` stage by design — it compares raw
  manifests across the whole dataset, with no single variant to fold
  into. The original per-variant functions and the equivalence test that
  checked `build_matrix()` against them are deleted (`KNOWN_LIMITATIONS.md`).
