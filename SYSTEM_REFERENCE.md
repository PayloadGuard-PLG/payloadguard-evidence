# SYSTEM_REFERENCE — payloadguard-evidence

Last updated: 2026-07-18

This document describes what this system does and what state it is in
today. It contains no build history, no narrative of how any decision
was reached, and no discussion of alternatives considered. For the
dated, decision-by-decision record, see `DEVLOG.md`. For open items and
known gaps, see `KNOWN_LIMITATIONS.md`. This document is regenerated in
substance whenever the system's current-state facts change; it is not
an append-only log.

## 1. What this system is

PayloadGuard Evidence is a domain-agnostic evidence engine for
safety-critical software. It converts authored requirements and real
verification-tool output into traceability artifacts suitable for a
regulatory submission — currently demonstrated against IEC 62304 /
ISO 14971 (medical device software) and NHTSA FMVSS No. 127
(automotive braking).

The engine (`evidence/`) knows nothing about medicine or automotive; it
knows about requirements, evidence, and strength. Each worked example
(`examples/`) supplies the domain-specific requirements, sources, and
Dafny specifications. The same engine code runs, unmodified, across all
four worked examples.

For every requirement, the system answers three questions and refuses
to let a claim's confidence exceed what a tool run actually
established:

1. What must the software do or not do? (cited to a primary source in
   `sources/`)
2. How is that established? (bound to one or more real, committed
   verification-tool runs)
3. How strong is that evidence? (one of six fixed strength labels,
   below)

The governing constraint: strength is derived only from committed tool
output. A requirement's intended strength never upgrades its realized
strength. `PROVEN` can appear in a rendered artifact only when a real
Dafny/Z3 run is parsed as clean, complete, and non-vacuous.

## 2. Evidence strength vocabulary

Defined in `evidence/model.py`. Six values, each with a fixed caveat
string that is attached to every record carrying that strength:

| Strength | Meaning | Caveat text |
|---|---|---|
| `PROVEN` | Dafny proof / discharged Z3 verification condition | Formally proven against the stated specification. |
| `BOUNDED_CHECKED` | CrossHair symbolic-execution pass within recorded bounds | No counterexample found within the recorded bounds; this is a bounded search, not a proof. |
| `TESTED` | Concrete test cases executed | Exercised on the recorded test cases only. |
| `EXAMPLE_CHECKED` | Specific recorded input/output pairs executed | Holds for the specific recorded inputs only; no claim of generality beyond them. |
| `DECLARED` | Human assertion, no tool evidence | Asserted by the author; not established by any tool. |
| `GAP` | Nothing established | Not established. Human input required. |

`PROVEN` is exclusive to Dafny-sourced records. A record cannot carry
`PROVEN` unless its `method` field equals `"dafny"` and its
`verifier_completion_status` field equals `"completed"` — enforced
structurally by `assert_no_realized_proven`
(`evidence/render/matrix_variants.py`), independent of what any binder
claims about its own diligence. This is checked at every matrix-build
call, not assumed from upstream correctness.

## 3. Architecture

### 3.1 Engine (`evidence/`)

- `model.py` — the `Strength` enum, `VerificationResult`, and
  `RequirementBinding` dataclasses. Caveats are first-class and
  attached to every record.
- `schema/metadata.schema.{a,b,c}.json` — JSON Schema enforcing
  well-formed requirement IDs (`^REQ-[A-Za-z0-9-]+$`), an explicit
  `intended_method` per requirement, and explicit CrossHair bounds
  (timeout, iterations, seed) when crosshair evidence is declared.
- `render/matrix_variants.py` — the single traceability-matrix
  builder, `build_matrix(variant_key, ...)`. Supports three shapes
  (Section 3.2). Runs conflict checks, intent derivation, and the
  structural `PROVEN` check (`assert_no_realized_proven`) on every
  call, regardless of caller.
- `dafny_adapter.py` — parses real Dafny verifier output into a
  `VerificationResult`. Never trusts a bare exit code or a substring
  match on the output; requires an exact match of the verifier's own
  summary line and refuses on any resource/timeout/memory marker.
- `dafny_spec_lint.py` — Gate C3 (Section 4.3).
- `dafny_mutate.py` — Gate C5 (Section 4.5).
- `dafny_nl_summary.py` — Gate C6 (Section 4.6).
- `citation_gate.py` / `citation_registry.py` / `hazard_id_lint.py` —
  self-consistency lints (Section 5).
- `polish_lint.py` — scans a current-state document (this one) for
  decision-journal narrative language, so its own prose stays pure
  current-state rather than drifting into build narrative (Section 9).
- `conflict.py` — CONFLICT Type 1/2 checks (Section 5.2).
- `reconcile.py` — fact-equality check across variant artifacts
  (Section 5.1).
- `cli.py` — `python -m evidence.cli` (Section 6).
- `test_catalog.py` — generates `TEST_CATALOG.md`.

### 3.2 Variant shapes (A / B / C)

Three ways of rendering the same underlying evidence into a
traceability matrix:

- **Variant A** — one row per requirement; evidence rendered as a
  list.
- **Variant B** — flattened pseudo-requirements with shadow rows, one
  evidence item per row.
- **Variant C** — partitioned by method into three separate
  artifacts: `c-symbolic` (CrossHair), `c-concrete` (concrete tests),
  `c-formal` (Dafny).

All three are produced by the same `build_matrix()` entry point; the
binding strategy (how a record is matched to a requirement) and the
row shape (how a matched record is rendered) are independent axes,
each with its own named function, dispatched through a declarative
table.

### 3.3 Requirements and metadata

A requirement is declared in a `metadata.{a,b,c}.yaml` file per worked
example, validated against the corresponding JSON Schema. Each
requirement carries an `id`, requirement text, an `intended_method`,
and zero or more evidence bindings. A binding may point at a CrossHair
manifest, a concrete-test case ID, or a Dafny spec/method pair (via a
`dafny_captures_index.json` file mapping
`"{spec_target}::{dafny_method}"` keys to the spec source, raw
verifier output, and run manifest).

## 4. The Dafny verification pipeline (Gates C1–C6)

Six checks a Dafny-backed requirement passes through before its
evidence can render as `PROVEN` in a matrix artifact. Not all six are
wired into the matrix-generation pipeline directly (noted per gate);
several are standalone, tested capabilities applied by whoever authors
a spec.

### 4.1 Gate C1 — capture

`dafny_adapter.py::parse_dafny_capture` accepts a raw Dafny verifier
capture and a run manifest, and refuses unless, in order: the exit
code is zero; exactly one summary line matching
`Dafny program verifier finished with N verified, 0 errors` is
present; the parsed error count is zero; and the summary line's tail
contains none of `"out of resource"`, `"out of memory"`,
`"timed out"` (case-insensitive). Only if all four hold does it
construct a `VerificationResult` with `strength=PROVEN`,
`verifier_completion_status="completed"`.

### 4.2 Gate C2 — PROVEN exclusivity

`assert_no_realized_proven` (`evidence/render/matrix_variants.py`)
permits `PROVEN` as a realized strength on a matrix row only when a
record's `method == "dafny"` and
`verifier_completion_status == "completed"`. Every other method —
CrossHair, concrete test, or a row with no method at all — is
unconditionally refused. This check runs independently of Gate C1; it
does not trust that a record reached it through the adapter.

### 4.3 Gate C3 — spec lint

`dafny_spec_lint.py`, four vectors:

- **Vector 1 (vacuous preconditions) — built, load-bearing.**
  `check_precondition_satisfiability` extracts a method's `requires`
  clauses and asks Z3 for satisfiability, independent of what Dafny
  itself reports. A hand-written expression translator covers
  booleans, comparisons (including chains), arithmetic, `real`/
  `int`/`nat`/`bool` identifiers and literals, and zero-argument-
  constructor Dafny datatypes (represented as Z3 `EnumSort`s).
  Anything outside that subset (quantifiers, `old(...)`, parameterized
  datatypes, unsupported types) is refused outright (`SystemExit`),
  never mistranslated. An `unsat` verdict means the method's clean
  Dafny pass proves nothing.
- **Vector 2 (weak postconditions) — built, heuristic.**
  `scan_weak_postconditions` flags `ensures` clauses using a one-way
  `==>` without a matching `<==>`. Advisory only; does not determine
  whether a bi-implication was actually needed.
- **Vector 3 (timeout/resource-limit masking) — built.** Independent
  of Gate C1's exit-code check: the summary-line parser itself
  refuses on resource/memory/timeout markers in the summary line's
  tail, and refuses if more than one summary line is present in a
  capture.
- **Vector 4 (specification stripping) — blocked.** Not scoped; the
  source material describing this vector is incomplete in the
  repository's own planning documents.

Vectors 1 and 2 are standalone, tested capabilities; neither runs
automatically inside the capture or matrix-generation pipeline.

### 4.4 Gate C4 — Spec-Testing Proofs (STPs)

IronSpec methodology: prove that specific, manually chosen
input/output pairs are accepted or rejected by the specification
alone, independent of any implementation. An ACCEPT lemma proves a
correct value is forced by the declared postconditions; a REJECT
lemma proves a plausible-but-wrong candidate value is excluded. Each
worked example's spec has its own STP suite, hand-authored alongside
it; STP suites are not wired into `build_matrix()` or any generator —
they are a proof about the spec's own tightness, not verification
evidence for a requirement.

### 4.5 Gate C5 — mutation testing

`dafny_mutate.py` generates mutants across five operator classes —
ROR (relational), LOR (logical), AOR (arithmetic, function-body
scope), LVR (literal value replacement), COI (clause negation) — and
re-verifies each against the real Dafny binary. SOR (set-typed
operations) and HOR (heap/object state) are checked, not assumed, as
not applicable per spec, confirmed by grepping for the relevant
syntax.

Filtering happens in three passes, all before or independent of a
Dafny invocation:

- **Static triviality** — a mutant is skipped if a fixed relational
  implication table shows it's guaranteed uninteresting. Direction is
  role-dependent: weakening is trivial for an `ensures` clause;
  strengthening is trivial for a `requires` clause.
- **Chain-direction compatibility** — a comparison-chain mutant is
  skipped if it would produce an operator direction Dafny's own
  grammar forbids mixing within one chain (Dafny Reference Manual
  §5.2.1–5.2.2). Filtered before generation, not caught post-hoc as
  an unclassifiable Dafny parse error.
- **Arithmetic-group compatibility** — an AOR mutant is restricted to
  never introduce `/` where the original had none (MutDafny's own
  restriction), eliminating division-by-zero false kills by
  construction.

A mutant that survives real Dafny re-verification and is not
explained by a named, documented category (see each worked example's
own mutation report) is treated as a real spec-tightness finding.

An escalation path exists for `drug_interaction_checker` specifically:
any survivor is additionally re-verified against that spec's own STP
suite; a survivor the STP suite independently catches is reclassified
`killed_via_stp_suite`, distinct from an ordinary `killed` mutant.

### 4.6 Gate C6 — NL-dialogue confirmation

`dafny_nl_summary.py::summarize_method` mechanically extracts each
`requires`/`ensures` clause verbatim, plus any `REQ-ID` cited in a
trailing comment, alongside a best-effort operator-substitution
English gloss labeled explicitly as a reading aid, not comprehension.
Only single-line clauses are supported by the citation-preserving
extractor; it cross-checks its own extraction against
`dafny_spec_lint`'s canonical, multi-line-capable extractor and
refuses (`SystemExit`) on any content mismatch.

The gate's actual deliverable is not the generated summary but the
recorded human sign-off it produces — a markdown file per spec
(`nl_confirmation_<spec>_dfy.md`) recording a named person's
confirmation that the summary matches intent. This gate is not wired
into any generator; it is a process habit applied at spec-authoring
time.

### 4.7 Citation gate

`citation_gate.py` performs mechanical, digit-boundary-protected
verification that a quoted claim actually appears in its cited
source. `citation_registry.py` forbids reintroducing a previously
disproven claim without an explicit correction marker.

## 5. Self-consistency mechanisms

### 5.1 Fact equality

`evidence/reconcile.py::run_gate` enforces that variants A, B, and
C's symbolic+concrete+formal sub-views share the same fact set
(method, strength, result_status, test_id) for every requirement they
have an opinion about. Where a view has no opinion about a
requirement (e.g. the formal view has no concept of a permanently
CrossHair-only requirement), it is exempt for that requirement, not a
mismatch. Any requirement id absent from the reference set entirely
is a hard failure.

### 5.2 Conflict gate

`evidence/conflict.py`, two sub-types, both Tier-1 hard failures:

- **Type 1 (binding-identity conflict)** — a top-down,
  metadata-authored binding and a bottom-up, evidence-store-carried
  assertion disagree on the physical target (file, method) a
  requirement's evidence points to.
- **Type 2 (evidence-outcome conflict)** — two manifests agree on
  target identity (same tool, target, invocation, bounds) but
  disagree on outcome (different exit codes for what claims to be the
  same verification act).

Type 1 is folded into every `build_matrix()` call. Type 2 is a
standalone, whole-dataset check (not per-variant), since it compares
across the full manifest set regardless of which variant is being
built.

### 5.3 Hazard ID and citation lints

`hazard_id_lint.py` requires every `HAZ-...` reference to resolve to
a real heading in some `HAZARD_REGISTER.md`. `citation_registry.py`
forbids reintroducing a disproven statement without a correction
marker.

### 5.4 Documentation-staleness check

`tests/test_docs_current_with_devlog.py` asserts that `HANDOFF.md`,
`KNOWN_LIMITATIONS.md`, and `SYSTEM_BLUEPRINT.md` each carry a
`Last updated` date no older than `DEVLOG.md`'s newest dated entry.

### 5.5 Polish lint

`evidence/polish_lint.py::scan_for_narrative_language` scans this
document for a fixed set of phrases that mark decision-journal prose
(a past-tense conclusion, a dated body reference outside this file's
own header, a reference to whose decision something was) and reports
every match. `tests/test_polish_lint.py` fails CI if this document
contains any such phrase, keeping it pure current-state rather than
letting it drift toward narrative the way other nominally
current-state documents in this repository have.

## 6. Command-line interface

`evidence/cli.py`, single subcommand:

```
python -m evidence.cli build \
  --variant {a|b|c-symbolic|c-concrete|c-formal} \
  --metadata PATH \
  [--manifest PATH] \
  [--concrete PATH] \
  [--schema PATH] \
  [--dafny-captures PATH] \
  [--out-json PATH] \
  [--out-md PATH]
```

- `--metadata` and `--variant` are the only required arguments.
- `--manifest` (CrossHair run manifest) and `--concrete` (concrete
  test results) are optional; omitting either means "no evidence of
  this type is declared anywhere in this metadata," not an error.
- `--schema` defaults to `evidence/schema/metadata.schema.<a|b|c>.json`
  for the given variant.
- `--dafny-captures` is required whenever the target metadata
  declares any `method: dafny` evidence; points at a small JSON index
  file mapping spec/method keys to the paths of the three real Dafny
  capture files.
- Schema validation runs first. A Tier-1 failure (schema validation,
  CONFLICT Type 1, the structural PROVEN check) exits non-zero with a
  short message on stderr — never a raw traceback.
- JSON prints to stdout when `--out-json` is omitted (composes with
  other tools). Markdown is written only when `--out-md` is given
  explicitly, never printed to stdout.

Must be run from the repository root; the package has no installer or
packaging configuration (no `pyproject.toml`/`setup.py`/`setup.cfg`
exists in this repository).

## 7. Worked examples — current status

### 7.1 Infusion-pump dose calculator (`examples/dosage_calculator/`)

All six Gate C1–C6 steps built and confirmed. Three evidence types
per requirement (CrossHair `BOUNDED_CHECKED`, concrete
`EXAMPLE_CHECKED`, Dafny `PROVEN`) — the only worked example with all
three. Gate C5: 56 mutants, 41 killed, 15 filtered across four named
categories, zero survivors, zero unclassifiable. `REQ-DOSE-003`
(finite result under numeric overflow) has no Dafny proof and cannot
reach `PROVEN` — Dafny's `real` type has no IEEE-754
overflow/NaN semantics, a permanent toolchain limit, not an unbuilt
item.

### 7.2 Renal-function dose adjustment (`examples/renal_adjustment/`)

All six Gate C1–C6 steps built and confirmed. Seven Dafny functions
verify together (`7 verified, 0 errors`), including a proven
Cockcroft-Gault creatinine-clearance computation from raw patient
inputs. CKD-EPI eGFR remains caller-supplied — a permanent, confirmed
Dafny/Z3 expressiveness limit (no real-valued fractional-exponentiation
primitive on a variable base). Gate C5: 450 mutants, 250 killed,
137 filtered pre-verification, 51 survived (three named,
explained categories), 10 unclassifiable, 2 blocked (a literal embedded
in arithmetic rather than adjacent to a comparison operator, outside
the LVR locator's scope). `REQ-RENAL-3`, `REQ-RENAL-4`, `REQ-RENAL-6`,
`REQ-RENAL-7` render as honest `GAP` rows with
`intended_method: PROVEN` — real, named future formalization
candidates, not silently dropped. `REQ-RENAL-8` (drug-classification-flag
provenance) renders as `GAP` with `intended_method: DECLARED` — a
permanent trust boundary; the flags are caller-supplied by design, and
resolving their provenance will produce a declared process fact, never
a proof.

### 7.3 Drug-drug interaction checker (`examples/drug_interaction_checker/`)

All six Gate C1–C6 steps built and confirmed. Six requirement rows,
all `PROVEN`, no `GAP` rows remain. `CheckInteraction` covers 68
match arms across 4 DOACs and a clinical-indication axis
(`TreatmentIndication`); `DoseReductionTargetMg` proves five specific
numeric dose-reduction figures. Gate C5: 1,342 mutants, 744 killed,
522 filtered_static, 44 survived (all explained across three named
mechanisms — vacuous-antecedent, redundant-consequent, and
requires-domain-restriction-plus-body-obliviousness), 26
unclassifiable (datatype-ordering type errors), 6 additionally killed
via the STP-suite escalation described in Section 4.5.

### 7.4 Generic AEB kernel (`examples/aeb_kernel/`)

All six Gate C1–C6 steps built and confirmed. First worked example
outside the medical-device domain, sourced directly from NHTSA FMVSS
No. 127 (§571.127). Every shared tool (`evidence.cli`, spec lint, NL
confirmation, mutation testing) runs unmodified against this domain.
Six Dafny functions verify together (`6 verified, 0 errors`), 31 STP
lemmas, zero weak-postcondition warnings across all six functions —
the tightest Gate C3 result of any worked example. Gate C5: 63
mutants, 38 killed, 17 filtered, 4 explained survivors (a
non-load-bearing precondition-sign weakening), 4 unclassifiable (a
named COI-generator gap on `target == X ==>` guard clauses, the same
class as `renal_adjustment`'s documented `||`-chain limitation).
Traceability matrix: 8 `PROVEN` rows, 2 honest `GAP` rows.
`REQ-AEB-9` (vehicle-class eligibility) and `REQ-AEB-10` (malfunction
detection/mode controls) are deliberately unbuilt.

A `HAZARD_REGISTER.md` exists for this example (10 entries, one per
`REQ-AEB-*`) but its Severity/Exposure/Controllability/ASIL fields are
`GAP` on two independent, simultaneous blockers: no named
automotive-safety reviewer exists, and the ISO 26262-3 §6.4.2 HARA
methodology clause that defines how to derive Exposure/Controllability
from an operational situation is unsourced (only Table 4's lookup
mechanism and §6.4.4's safety-goal rules are sourced). No ISO 26262
risk-management-plan artifact exists yet for this example.

## 8. Risk management (ISO 14971)

Applies to the three medical-device worked examples
(`dosage_calculator`, `renal_adjustment`, `drug_interaction_checker`).
All three risk-management artifacts are status `DRAFT`, not signed
off.

`dosage_calculator` is the most developed. Hazard identification
(clause 5.4) is complete: `HAZ-GIP-1.2`, `HAZ-GIP-1.3`,
`HAZ-GIP-1.14` (sourced from GIP v1.0's published hazard analysis,
cross-checked against IEC 60601-2-24:1998 clause 51.102 directly),
and `HAZ-DOSE-003` (no GIP source, weaker `BOUNDED_CHECKED` evidence,
stated plainly). Severity model is consequence-only (ISO 14971
§3.27 / TR 24971 §5.5.4). Steven, the named Clinical SME, has scored
all five hazards `S3 — Serious`. Overall residual risk is
`Unacceptable` — a real, computed result on four of five hazards
(`HAZ-GIP-1.14`/1.2/1.3/`HAZ-DOSE-003`, each `P5 × S3`); the fifth,
`HAZ-GIP-1.2b`, stays an evaluation `GAP`, blocked on a still-open
probability-side question. Resolving the `Unacceptable` result
requires either real field/usage data (does not exist, pre-market) or
a recorded ALARP determination from Steven — both open.

`renal_adjustment` and `drug_interaction_checker` have complete
hazard identification (8 and 6 entries respectively) but severity,
probability, and evaluation fields remain explicit `GAP`s — no
clinical SME has scored either device's hazards yet.

## 9. Testing

257 test functions across 34 categories (`TEST_CATALOG.md`, generated
by AST-parsing the real test suite — CI fails if this file drifts
from what the generator produces against the committed suite). Pytest
collects 268 individual test cases from those 257 functions (the gap
is parametrized functions expanding into multiple cases).

The committed test suite reads committed verification captures; it
does not invoke a live Dafny, Z3, or CrossHair binary. Verifying this
document's own numbers requires cloning the repository and running
`pytest tests/ --collect-only -q` after installing `pytest`,
`z3-solver`, `jsonschema`, and `pyyaml` — none of which are bundled
with the repository itself, and none of which require a Dafny/CrossHair
binary to be present.

## 10. Continuous integration

Two GitHub Actions workflows:

- `.github/workflows/tests.yml` — runs `python -m pytest tests/ -q`
  on every pull request into `main`. Installs from a pinned
  `requirements.txt`. Does not install or invoke a live Dafny/Z3/
  CrossHair binary toolchain.
- `.github/workflows/payloadguard.yml` — runs a third-party GitHub
  Action (`PayloadGuard-PLG/payload-consequence-analyser`, pinned to
  a commit SHA, not a mutable tag) on every pull request into `main`.
  Exit code 0 covers SAFE, REVIEW, and CAUTION verdicts alike (none
  block merge); exit 1 is an analysis error (blocks merge); exit 2 is
  DESTRUCTIVE (blocks merge). The workflow gates on the numeric exit
  code directly, never on the action's own `verdict` output string,
  which mislabels any exit-0 result `"SAFE"` even when the real
  finding was REVIEW or CAUTION. `runtime-mode` (eBPF process-killing)
  and `auto-remediate` (tag-to-SHA auto-PR) are both left at their
  safe defaults (disabled).

## 11. Known permanent limitations

Stated as current facts. For the full ledger including resolved
items, see `KNOWN_LIMITATIONS.md`.

- Dafny's `real` type has no IEEE-754 overflow/NaN/infinity concept.
  Any requirement needing "finite result under numeric overflow" as a
  postcondition cannot be formalized in Dafny; `dosage_calculator`'s
  `REQ-DOSE-003` is the confirmed instance.
- Dafny/Z3 cannot express fractional exponents on a variable base.
  CKD-EPI eGFR's real-world formula (`Scr^-1.200`, `Scr^-0.302`, etc.)
  cannot be proven; `renal_adjustment` leaves this caller-supplied.
  Declaring it an unproven axiom was tested directly and confirmed
  worthless — an axiom-backed lemma verifies trivially even for an
  absurd, wrong claim about the axiom.
- `crosshair-tool` 0.0.107 hard-codes its solver seed to 42
  (`make_default_solver()`, not `StateSpace.__init__()`), making a
  metadata file's declared `seed: 1`/`seed: 2` unenforceable on this
  tool version. Disclosed as "declared-only, not enforced" everywhere
  it appears. `max_iterations` is independently enforceable via
  `AnalysisOptionSet`, unaffected by this limit.
- Gate C3 Vector 4 (specification stripping) is blocked — insufficient
  source material to scope, not a technical refusal.
- Gate C6's "next-phase adaptation" work (adapting a signed-off spec
  for downstream regulatory-submission analysis) is blocked — the
  target downstream software, the regulatory pathway (510(k)/De
  Novo/PMA/other), and what "adapting the spec" concretely means are
  all unspecified.
- `evidence/dafny_mutate.py`'s COI (clause negation) generator cannot
  produce a mutant negating a one-way implication whose antecedent is
  itself an equality comparison (`target == X ==>` guard clauses) —
  Dafny rejects the mutated form outright ("invalid UnaryExpression").
  Confirmed present in both `renal_adjustment` (as a `||`-chain
  ambiguity) and `aeb_kernel` (as this specific COI case).
- No packaging exists. The system runs only as `python -m evidence.cli`
  from a cloned repository's root; there is no installable package and
  no documented interface for a team outside this repository to point
  the engine at their own, externally-hosted metadata and evidence.

## 12. Repository layout

```
evidence/               the engine — vocabulary-agnostic, no domain knowledge
examples/               one directory per worked example
  dosage_calculator/
  renal_adjustment/
  drug_interaction_checker/
  aeb_kernel/
sources/                 archived primary-source documents, one per citation
tests/                   the test suite (254 functions / 265 collected cases)
dashboards/              dated HTML status snapshots, not auto-regenerated
.github/workflows/       tests.yml, payloadguard.yml
```

Per-example directories each contain: a Dafny spec (`.dfy`), an STP
suite, a mutation-testing runner and report, a `metadata.{a,b,c}.yaml`,
`RISK_MANAGEMENT_PLAN.md` and `HAZARD_REGISTER.md` (medical-device
examples), a `PHASE1_PLAN.md`, and an `nl_confirmation_<spec>_dfy.md`
sign-off record.

Root-level reference documents: `README.md` (entry point),
`SYSTEM_REFERENCE.md` (this document — current-state facts only),
`OPERATIONS_MANUAL.md` (architecture, gate reference, command
reference, how to add an example), `SYSTEM_BLUEPRINT.md` (component
map and data-flow reference — a build-history document, not a
current-state one), `KNOWN_LIMITATIONS.md` (the open-items ledger),
`REVIEW_PROTOCOL.md` (how generated artifacts are reviewed before
use), `DEVLOG.md` (dated, append-only build log), `TEST_CATALOG.md`
(generated test index), `HANDOFF.md` (current status for picking up
the repository).

## 13. Scope

- Not a PR-gate or merge-blocking CI tool.
  `PayloadGuard-PLG/payload-consequence-analyser` is a separate
  repository and shares no code with this one.
- Not a replacement for human regulatory sign-off. Every generated
  claim is reviewed by a person before use in a submission
  (`REVIEW_PROTOCOL.md`).
- Not a tool that infers evidence strength. Strength labels come only
  from a verification tool's recorded output, never from a
  requirement's intended or hoped-for outcome.
- Not currently packaged for use outside this repository. See Section
  11.
