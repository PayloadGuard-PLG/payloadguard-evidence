# DEVLOG — payloadguard-evidence

Append-only session log. Every session adds one dated entry (UTC), newest
first, citing commit SHAs. Timestamps below are taken from the git history
and run manifests, not reconstructed from memory.

---

## 2026-07-21 (Tier 3, authoring migration) — Contract ratification: hash-bound attestation artifacts for all four examples

The last Tier-3 plan item, scoped with Steven (mode chosen via `AskUserQuestion`): **ratification for all four examples** (not clean-room re-derivation, available later as an optional upgrade; not document-only), **with the pending Component D reviews folded in**. The honesty constraint drives the whole design: no code can change who authored a spec. All four specs were LLM-drafted and human-reviewed; Component F freezes their contracts going forward, but the frozen baselines inherit that provenance. Ratification is the truthful upgrade available: the human examines every frozen declaration against the sources and formally adopts the contract — earning the label **human-ratified**, never "human-authored," a distinction the code, artifacts, and docs all state plainly.

**`evidence/contract_attestation.py` (new).** Mirrors Component D exactly (template + structure gate, never the sign-off — drafter != checker). `contract_hash` — sha256 over the canonical frozen manifest — is what makes ratification durable rather than a one-time signature: the artifact records the hash of the exact contract it ratifies, and if the contract later changes at all, `check_attestation` reports `hash_current=False` (stale) — a signed adoption can never silently outlive the contract it adopted. `build_attestation` renders a PENDING artifact: sign-off block (reviewer/date/drafter!=checker attestation/adoption statement), then one block per frozen declaration (datatype definitions verbatim; per function its signature/requires/ensures/spec-body) each with an **Adopted?** field — the per-clause *meaning* judgment (modeling fidelity) that no mechanical gate can decide. The Component D blind constant review is **folded in**: `attestation_complete` requires that review's own `review_complete`, so a contract can't read ratified while its constants' source review is pending. Structure gate passes on PENDING (same posture as D); completion is reported, never asserted.

**Committed artifacts:** `contract_attestation_{dosage,renal,aeb,ddi}.md`, all PENDING, drift-pinned, hash-bound to their current frozen contracts. `tests/test_contract_attestation.py` (8): per-example drift+structure; completion blocked on the folded-in D review then flipping with it; the stale-hash tamper case (sign, then weaken an `ensures` — the rebuilt manifest's hash no longer matches, `structure_ok=False`); a dropped declaration block caught via its unique marker; hash stability/content-sensitivity.

**Forward workflow documented** (`OPERATIONS_MANUAL.md` §6.2a): for any NEW example the human author writes and freezes the contract (committed `frozen_contract.yaml`) *before* any automated drafter touches the file; the drafter is confined to proof scaffolding and `check_contract` proves the boundary held. A spec built that way is human-authored **by construction** — the migration exists precisely because the four existing examples were not.

**What remains human, out-of-band, at Steven's pace:** completing the four blind constant reviews (D) and the four adoptions — one sitting per example. Nothing blocks in CI until then; when signed, the ratified provenance becomes real and the hash binding keeps it real. This closes the Tier-3 build surface: the full "PROVEN != meaningful" plan (Tiers 1–3) is now mechanically complete. Full suite: 370 passed.

*Qodo review on the PR, two findings fixed — both the global-substring bypass class PR #71 already taught this repo, repeated in the new checker.* (1) *Hash check spoofable* — `hash_current` was `contract_hash(manifest) in markdown`, unanchored: pasting the current hash anywhere in the file would mask a stale recorded field. Now the dedicated `Contract hash (sha256)` line is parsed with a strict anchored regex (exactly one match required; absent/ambiguous → structural failure) and compared by equality; regression test spoofs a stale recorded hash with the current hash pasted elsewhere and confirms it still reads stale. (2) *Declaration blocks not verified* — only the heading markers were checked, so a declaration's frozen content could be gutted while its heading (and some other section's `Adopted` token) survived. `check_attestation` now splits the artifact into per-declaration sections and requires each to display the exact frozen content the human is adopting (definition or signature, every `requires`/`ensures` clause, the spec body) plus its own `Adopted?` field, reported as `missing_content`; regression tests gut a signature, a single `ensures` line, and one section's Adopted field, each caught. Committed artifacts unchanged (the generator was never wrong — the checker was). Full suite: 372 passed.

---

## 2026-07-20 (Tier 3 cont.) — Component F extended to all four examples (datatype freezing)

The frozen-contract gate now covers every worked example. The pilot (previous entry) modeled `function`/`predicate`/`method`/`lemma` and **failed closed** on any type-level declaration; renal, aeb, and ddi all define `datatype`s, so extending the gate meant teaching it to freeze datatypes — the lift that was deferred at pilot time.

**Datatype freezing (`evidence/frozen_contract.py`).** A `datatype`/`codatatype` is now a modeled, frozen declaration: its whole canonical *definition* (the `= C1 | C2(field: T) | ...` constructors, which ARE the spec's meaning) is captured and diffed. A datatype has no `{...}`/`;` terminator, so its definition is bounded by the start of the next top-level declaration (`_NEXT_DECL_RE`). Enums (single- and multi-line, leading-`|` form) and **parameterized** constructors (renal's `RenalAssessment(stage: GStageCategory)`, ddi's `InteractionResult(outcome: Outcome, direction: RiskDirection)`) are all handled. The fail-closed set narrows to the kinds still unmodeled and absent from this repo's specs — `newtype`/`type`/`const`/`class`/`trait`/`iterator` — which still refuse rather than pass silently.

**Committed frozen manifests** for `renal_adjustment` (10 declarations: 3 datatypes + 7 functions), `aeb_kernel` (7: 1 datatype + 6 functions), and `drug_interaction_checker` (8: 6 datatypes + 2 functions); dosage's manifest is unchanged (byte-identical — it has no datatype). Each real spec self-checks `CONTRACT_INTACT`, drift-pinned against its generator.

**Verified against real datatype tampering (ddi):** dropping an `Outcome` constructor → `CONTRACT_VIOLATED` (`definition_mismatches`); changing `InteractionResult`'s `direction` field type `RiskDirection`→`Outcome` → VIOLATED; adding a whole new datatype → VIOLATED (`added_spec_declarations`); reformatting a datatype (whitespace + comment) → INTACT (AST-grade). `tests/test_frozen_contract.py` grew to 19 (datatype freezing incl. parameterized, the three tamper cases, reformat-invariance, and a per-example drift+self-check parametrized over all four). The earlier Qodo-driven fail-closed test was retargeted to a still-unmodeled kind (`newtype`/`class`). Full suite: 361 passed.

**Still deferred:** the frozen-spec *authoring migration* (human freezes the contract first, LLM confined to proof annotations) — Component F now guards that boundary for all four specs, but the specs were not re-derived under that discipline.

---

## 2026-07-20 (Tier 3) — Component F: the frozen-contract integrity gate (dosage pilot)

Tier 3 (structural separation) begins. Tiers 1–2 made the pipeline honest about what a proof *establishes* and whether the numbers *transcribe* the source; but a `PROVEN` label is only trustworthy if the contract that was proven wasn't itself gamed to be provable. Two classic evasions: weaken the `ensures` until a wrong implementation passes (this repo already owns `dosage_underconstrained.dfy`), or add `assume`/`{:axiom}`/`{:extern}` to force verification. Component F closes this by structurally separating the human-owned safety contract from machine/LLM-authored proof scaffolding and mechanically proving the separation held — the drafter!=checker principle (`citation_gate`) finally applied to the load-bearing artifact, the spec itself. It is an *integrity* guarantee, not a correctness one.

**`evidence/frozen_contract.py` (new).** The frozen contract is the canonical, AST-normalized *contract surface* of a spec: per declaration, its signature + `requires` + `ensures`, plus `function`/`predicate` bodies (which, for a predicate spec, ARE the spec). `build_frozen_contract` extracts it once from the human-authored `.dfy` (generated, committed, drift-checked, like Component D's template); `check_contract` re-extracts a candidate's surface, proves it matches the frozen manifest exactly, and scans the whole candidate for forbidden soundness-escape constructs — `method` bodies are NOT frozen (they're the implementation, where `assert`/`invariant`/`decreases` legitimately live). "AST-grade" = comparison on a normalized token stream (comments stripped, whitespace/formatting irrelevant), so a real clause/body change is caught while a reformat is not. Reuses `dafny_spec_lint`'s `extract_requires/ensures_clauses` and `literal_citation.strip_comments`.

**The verified outcome, all four cases captured (dosage):** case 1 — real `dosage.dfy` → **CONTRACT_INTACT** (Dafny verifies). case 2 — `dosage_underconstrained.dfy` (weakened `ensures`) → **CONTRACT_VIOLATED**, naming the dropped pinning `ensures` and the vanished `ExpectedDose`, while Dafny reports `1 verified, 0 errors`. case 3 — new `dosage_assume_escape.dfy`: contract surface pristine, wrong implementation, `assume false` forces it through — Dafny reports `2 verified, 0 errors` (and `dafny verify --allow-warnings` gives a clean exit-0, so its soundness *warning* is not a robust guard) → **CONTRACT_VIOLATED** on the forbidden `assume`, which the contract-surface diff alone can't see. case 4 — new `dosage_scaffolded.dfy` (identical contract, correct impl, an inert `assert`) → **CONTRACT_INTACT**, the control proving the gate doesn't cry wolf on honest scaffolding. Both new exhibits carry committed Dafny captures + run-manifests.

This is the first concrete mitigation of the long-BLOCKED Vector-4 "specification stripping" concern (`dafny_spec_lint`): no longer without any defense, though not a fully-scoped close (the original source material is still missing). `tests/test_frozen_contract.py` (8): drift, the four outcome cases (each paired with what Dafny itself said), and units for canonicalization (reformat invisible, token change caught), `{:axiom}` detection, and added-lemma-allowed-but-added-function-not. **Scoped to dosage**; extension to renal/aeb/ddi and the frozen-spec authoring migration are deferred. Full suite: 350 passed.

**Qodo review, three findings fixed (all real, all in-scope robustness).** (1) *Lemma breaks manifest build* — `build_frozen_contract` iterated lemmas into `_declaration_record`, which called `dafny_spec_lint`'s method/function-only clause extractor and `SystemExit`ed on a lemma-bearing spec (latent; dosage has none). Rewrote clause extraction to be self-contained and kind-agnostic (`_split_header`), removing the dependency on `_find_method_header` and its keyword restriction; lemmas are now skipped from freezing (they are scaffolding), and predicate-bearing specs no longer crash either. (2) *Datatype changes not frozen* — the docstring claimed added datatypes were caught, but type-level declarations weren't enumerated, so a datatype change would slip through as a false `CONTRACT_INTACT`. Rather than build full datatype-diffing (deferred extension), the gate now **fails closed**: `build_frozen_contract` refuses a spec containing an unmodeled declaration (`datatype`/`newtype`/`type`/`const`/`class`/`trait`/`iterator`), and `check_contract` flags any such declaration in a candidate as a violation (`unmodeled_declarations`) — honest about what it doesn't yet model instead of passing it. (3) *Forbidden "newly present" inaccurate* — the comments framed forbidden constructs as a baseline diff the manifest couldn't actually do; corrected to the true policy (**always forbidden**), and `build_frozen_contract` now refuses a source that already contains one, guaranteeing the baseline is clean so any candidate hit is genuinely an introduced escape. 3 new regression tests. dosage's committed manifest and all four cases unchanged (byte-identical). Full suite: 353 passed.

---

## 2026-07-20 (Tier 2 cont.) — Component C + D extended to all four examples; Qodo review on the renal Component D PR

Two pieces this session, on `claude/repo-docs-review-9l23t8` after PR #71 (renal Component D) merged.

**PR #71 Qodo review, two findings fixed (commit `9684c73`).** (1) *Structure-check bypass* — `source_anchored_review.check_structure` verified each source quote with a global `quote in markdown` substring test. Because two constants can share a verbatim quote (renal's `89` and `60` both cite one KDIGO row), deleting one constant's whole review block could be masked by the other block's identical quote, leaving `structure_ok=True` — the same substring false-positive class fixed in #70. Added a per-literal block check keyed on the unique marker `build_review` already emits (`The spec's constant here is \`{lit}\`.`), reported as `missing_blocks` and folded into `structure_ok`; two literals never share a marker, so a dropped block is always caught whatever its quote. New regression test deletes `60`'s block and confirms it's caught while the shared quote survives. (2) *Unsafe test path join* — the test helper joined `SOURCES / e["source"]` without the `_resolve_within` containment guard `check_example` uses; routed it through `_resolve_within`. Qodo re-review: both **Resolved**, Bugs (0); PayloadGuard SAFE.

**Component C + D rollout to `aeb_kernel` and `dosage_calculator` (and Component D to `drug_interaction_checker`).** Steven committed the converted FMVSS-127 source (`sources/nhtsa-fmvss-127-2024.md`, commit `4c7c01e`), unblocking aeb. `examples/aeb_kernel/literal_citations.yaml`: all seven safety numbers — the S5.1.1/S5.1.2 lead-vehicle envelope (`10.0`/`145.0`), the S5.2.1/S5.2.2 pedestrian upper bound (`73.0`), the S4 onset thresholds (`0.15`/`0.05`/`11.0`), and the S5.3 false-activation threshold (`0.25`) — trace to verbatim quotes from the codified 49 CFR 571.127 text (not the preamble), each CONFIRMED via the citation gate; the non-negativity boundary `0.0` is structural. aeb is the first non-medical example to be literal-cited. `examples/dosage_calculator/literal_citations.yaml`: `dosage.dfy` is fully parameterized (concentration, rate and the safe ceiling are all inputs), so it transcribes no source threshold at all — its single code literal is the structural reverse-flow/non-negativity zero. Component D templates generated for aeb, dosage, and ddi (`source_anchored_review_{aeb,dosage,ddi}.md`), all committed PENDING; dosage's is honestly near-empty (no source constant to blind-check). `tests/test_literal_citation.py` now parametrizes over all four examples plus aeb/dosage pin tests; `tests/test_source_anchored_review.py` parametrizes drift+structure over all four committed review artifacts. Full suite green.

*Qodo review on PR #72, one finding fixed.* The aeb `0.25` quote ("...0.25 g or greater") spanned a hard line-wrap in the converted source, so the normalized citation gate CONFIRMED it but a human Ctrl-F for the displayed "verbatim" quote would fail. An audit for the same class found renal's `88.4` quote ("conversion factor (88.4)") had the identical defect (merged in #70, uncaught). Both re-quoted to contiguous verbatim substrings ("exceeds what manual braking would produce by 0.25 g"; "(88.4) is standard clinical chemistry") - source documents left untouched (the source is ground truth; you don't reshape it to fit a citation). Added `test_committed_source_quotes_are_contiguous_verbatim_substrings`: every source quote must be an exact substring of its source, not merely a normalized match - the stronger, human-facing property the whitespace-normalizing gate can't enforce. Affected Component D templates regenerated. 342 tests pass.

---

## 2026-07-20 (Tier 2 cont.) — `source_anchored_review`: the source-anchored, blind, logged Gate C6 (Component D), renal template

Second half of Tier-2 source fidelity. Component C (`literal_citation`) closes *transcription* - the spec's numbers match the source. Component D reforms the *review*: the original Gate C6 (`dafny_nl_summary`) asks a human to confirm the spec matches a plain-English summary the same system generated from that spec - drafter and checker are the same kind of system, so the checker inherits the drafter's blind spots (the exact rubber-stamp the plan named). This makes the review source-anchored, blind, and logged instead.

**`evidence/source_anchored_review.py` (new).** Builds a review template where each numeric constant is shown next to the verbatim SOURCE quote it must transcribe (reused from Component C's `literal_citations.yaml`, already CONFIRMED present in the source), the reviewer writes the value/boundary they expect FROM THE SOURCE *before* the spec's constant is revealed (kept in a collapsed block - the "blind" step, so agreement means source and spec independently point to the same number), and reviewer + date + an explicit drafter != checker attestation are recorded. `check_structure` mechanically verifies the artifact's structure (every source quote present and CONFIRMED, every required field marker present) and reports `review_complete` (no `_PENDING_` left) separately.

**Deliberately does NOT perform the review.** The sign-off is a human act; having the drafting system fill it would recreate the rubber stamp this component exists to remove. So a freshly generated template is PENDING - structurally valid but not yet reviewed - and per the chosen approach the structure gate PASSES on a PENDING template (`structure_ok=True, review_complete=False`); requiring a completed human review is a separate, out-of-band signal, not a CI blocker. `examples/renal_adjustment/source_anchored_review_renal.md` committed in that PENDING state.

`tests/test_source_anchored_review.py` (4): the generated template is structurally valid but PENDING; the committed renal artifact matches the generator (no drift) with every quote CONFIRMED; replacing every `_PENDING_` flips `review_complete`; and a tampered template (a dropped quote, or a quote absent from the source) is caught. Extension to DDI/aeb/dosage is the remaining Component D rollout. 329 tests pass.

---

## 2026-07-20 (Tier 2 start) — `literal_citation`: mechanical literal-to-source citation, validated on renal + drug_interaction_checker (Component C)

Tier 2 of the "PROVEN != meaningful" work is source *fidelity*: Tier 1 (`proof_content`) says whether a proof carries independent content, but not whether the spec's NUMBERS faithfully transcribe the source. A single mistyped digit (145 -> 154) is a silent, unprovable defect - Dafny happily proves a spec built on the wrong number. This is Component C, the transcription half, built and validated on `renal_adjustment` first (per Steven's "renal first, then extend" scope choice) and then extended to `drug_interaction_checker`; `aeb_kernel`/`dosage_calculator` (PDF sources, pending text conversion) and Component D (source-anchored blind Gate C6) are the remaining Tier-2 work.

**`evidence/literal_citation.py` (new).** Every numeric literal in a spec's CODE (comments stripped, so a year/PMID/line-ref in prose never counts) must be accounted for by a citation-manifest entry classified as exactly one of: `source` (a verbatim quote checked present in the named source document via `evidence/citation_gate.py`'s existing normalized-substring match, whose digit-boundary guard already stops 145 matching inside 1450), `structural` (a mathematical/boundary constant - 0.0 non-negativity, an int zero - that transcribes no requirement), or `design_decision` (a value the author chose that the source does NOT state). Completeness is enforced both ways: no code literal may lack an entry (the exact hole this closes), and no manifest entry may name a literal absent from the code (a stale citation). It checks transcription, not modeling fidelity - that the clause decomposition captures the requirement's meaning stays with Component D.

**`examples/renal_adjustment/literal_citations.yaml` (new).** All 19 of the renal spec's code literals accounted for and mechanically verified against the real committed sources: the 9 KDIGO GFR-stage boundaries (90/89/60/59/45/44/30/29/15) against `kdigo-2024-gfr-staging.md`'s p. S126 category table; the 3 MHRA formula-selection thresholds (age 75, BMI 18.0/40.0) against `mhra-renal-formula-selection-2019.md`; the 4 Cockcroft-Gault constants (140/72.0/88.4/0.85) against `ckd-epi-2021-and-cockcroft-gault-verification.md`'s formula transcription - **16 source-cited, all CONFIRMED by the citation gate**. The round-half-up `0.5` tie-break is classified `design_decision` (the spec itself already notes it is "NOT a KDIGO rule" - KDIGO states no tie-break method); `0.0`/`0` are `structural`. Nothing silently un-accounted-for.

`examples/drug_interaction_checker/literal_citations.yaml` (new): the DDI spec's only numeric constants are REQ-DDI-6's two dose figures - dabigatran 110 mg and edoxaban 30 mg (`DoseReductionTargetMg`) - both CONFIRMED against `sps-doac-interactions-2024.md`'s verbatim "Reduce the dose of dabigatran to 110mg twice daily" / "Reduce the edoxaban dose to 30mg daily"; the unreachable wildcard arm's `0` is structural. (`CheckInteraction` is entirely enum logic - no numeric literals to cite.)

`tests/test_literal_citation.py`: harness unit tests (literal extraction ignoring comments/identifiers, both-way completeness, source verification, malformed/stale detection), the real gate parametrized over renal + DDI, DDI dose-target classification, and a demonstration that mutating a spec constant (90 -> 91) makes the gate flag `91` as uncited - the transcription error Dafny itself cannot catch. 323 tests pass.

---

## 2026-07-20 — `gate_c5_runner` precondition-refusal robustness, and a PayloadGuard false-positive log

Two follow-ups to the `evidence/gate_c5_runner.py` extraction (PR #67, being merged by the maintainer).

**A confirmed Qodo finding, fixed.** Qodo's deeper review pass flagged that `mutants_with_outcomes` called `check_precondition_satisfiability` for `requires` mutants without catching `SystemExit`. Verified against live code before trusting the claim: `dafny_spec_lint.build_symbol_table` raises `SystemExit` (clean refusal, not a crash) on parameter types it doesn't model — e.g. a ROR mutant introducing a comparison between two datatype operands, which Dafny accepts via its own structural rank ordering but the Z3 translator only models for arithmetic sorts. The DDI runner has caught exactly this since PR #26 (records `z3_translation_refused`, continues to real verification); the extracted renal pipeline never carried the catch because renal's params are all real/int/nat and never trip it — which is also why the extraction validated byte-identical. Left unhandled, the first untranslatable `requires` mutant would abort the whole run the moment the "sanctioned" runner is reused on a datatype-heavy spec like DDI, which is its entire purpose. Fixed by wrapping the call in `try/except SystemExit`, recording `precondition_check_outcome="z3_translation_refused"` + detail, and falling through to real *isolated* verification (the shared runner isolates before verifying — stronger than DDI's whole-file path, preserved here). Renal output is unchanged: `mutation_report_renal.json` still byte-identical, `test_renal_mutation_report.py` still green. New `tests/test_gate_c5_runner.py` case monkeypatches the checker to raise `SystemExit` and asserts the run still produces records, the refusal metadata lands on the affected requires mutants, and they still reach verification. 293 tests pass (up from 292).

**A PayloadGuard false-positive log (`PAYLOADGUARD_MERGE_FINDINGS.md`, new).** PR #67's PayloadGuard scan returned `DESTRUCTIVE`/`CRITICAL` ("DO NOT MERGE"), driven entirely by its Structural Drift (Layer 4) reporting `run_mutation_suite_renal.py` at a 55.56% node-deletion ratio — the five helpers (`_PARSE_ERROR_RE`, `_classify`, `_filtered_outcome`, `_real_verify`, `_version`) that the same PR *moved* into `evidence/gate_c5_runner.py` (`+242/-0`), all confirmed present there by hand. Layer 4 parses each file independently, so it cannot distinguish a cross-file move/extraction from a deletion; the other four signals (file-deletion count 0, line-deletion ratio 25.8%, temporal CURRENT, semantic TRANSPARENT) all read the change correctly as benign. Logged as field evidence to harden the PayloadGuard product — with the concrete fix (cross-file move reconciliation before scoring a node deleted; a composite-severity guard when one layer fires alone against otherwise-benign signals). No repo code was contorted to appease the scanner; the maintainer merges over the false positive.

---

## 2026-07-20 (even later) — `proof_content`: telling the truth about what each PROVEN row proves (Components A + B + E)

The `PROVEN` label certifies that Dafny discharged a spec, but conflates a proof of an *independent property* with a proof of a spec that merely *restates its own implementation* (`ensures result <==> body`, obligation `P <==> P`). This lands the classification and the honest labelling; the fidelity half (does the spec match the source) stays named-but-unbuilt as Tier 2.

**Component A — the spec/implementation-gap classifier (`evidence/spec_impl_gap.py`, new; Gate C3 vector 3).** Per `ensures` clause: substitute the function self-call (or method `returns` name) with a result sentinel, strip `guard ==> ...` implications (the aeb `match`-per-target shape), read the consequent's loosest top-level operator with a paren-depth-aware scan (so it survives the commas/casts/`.member` calls the full Z3 tokenizer refuses) — a `==`/`<==>` pinning the result is **definitional**, a bound or boolean combination is **property**. Where the consequent is fully translatable, a Z3 pin-uniqueness check *confirms* the structural verdict; an untranslatable RHS (a companion call like `ExpectedDose(...)`, a parameterized-datatype constructor like `InteractionResult(...)`, an `as real` cast) is refused, not guessed. Reuses `dafny_spec_lint`'s tokenizer/parser/`build_symbol_table`/`translate_clause`.

A real design tension, found against the live specs and resolved before building: the plan's *function-level* "ensures ⟺ body" test classifies dosage's `CalculateHourlyDose` **definitional** (its `dose == ExpectedDose(...)` pin dominates the conjunction), contradicting the expectation that a dosage row read property. The validation target itself disambiguates — classification must be **per-clause**, so the `dose == ExpectedDose` pin reads definitional while the `0.0 <= dose <= max` safety bound reads property in the same function.

Validated against all four committed specs, matching the by-hand analysis: **aeb_kernel** 6 functions / 8 rows all definitional (every clause Z3-confirmed); **dosage** `CalculateHourlyDose` property (pin definitional, two bounds property, Z3-confirmed); **renal** mixed (RoundHalfUp/ComposedCeiling/CockcroftGault property, GStage/SelectFormula definitional); **DDI** CheckInteraction / DoseReductionTargetMg definitional. Across 107 clauses the Z3 cross-check confirmed all 21 it could translate with **zero disagreements**. New `tests/test_spec_impl_gap.py` (9).

**Component B — the qualifier on PROVEN.** `evidence/model.py` gains a `PROOF_CONTENT_CAVEAT` map (definitional/property, each stating plainly what it does and does not certify); `dafny_record` (`render/matrix_variants.py`) derives `proof_content` from Component A per the row's `dafny_method` and carries it (+ its caveat) on every PROVEN record, rendered in the `.md` caveats. Annotation only — a classification failure degrades to `None`, never blocks a valid PROVEN binding; `assert_no_realized_proven` (R3) is untouched, PROVEN-exclusivity unchanged. No schema change: the schema validates input metadata, and `proof_content` is a derived/rendered field. New `tests/test_proof_content.py` (3).

**Component E — reclassify the four examples + correct the overclaims.** Each example's authoritative `traceability_matrix.a.json/.md` regenerated via `evidence.cli` (no hand-editing); the qualifier rides in each PROVEN dafny record's evidence entry and its `.md` caveats. Of the 20 `PROVEN` rows, **14 are definitional** (aeb 8, DDI 6) and **6 property** (dosage 2, renal 4). (The dosage variant-B/C cross-validation views — shadow/symbolic/concrete/formal — use a flattened row projection that carries no per-record annotations, so they render unchanged; the qualifier lives on the authoritative variant-A rows, a boundary left as-is rather than widening the projection here.) Corrected: root `README.md` (the "20 PROVEN" table now shows the definitional/property split and the qualifier), `SYSTEM_REFERENCE.md` (evidence-vocabulary section), `KNOWN_LIMITATIONS.md` (new named limitation: 14/20 PROVEN are definitional, disclosed not fixed), and the `aeb_kernel`/`drug_interaction_checker` READMEs (each states its rows are definitional and why). The fidelity limitation (numbers-match-source) is named as the still-open Tier-2 work everywhere it's relevant. 310 tests pass.

---

## 2026-07-20 — dosage and drug_interaction_checker Gate C5 moved onto the sanctioned isolated runner

Direct instruction: "point the DDI and dosage runners at gate_c5_runner." Not the purely mechanical swap the handoff had projected — investigating the two runners against the live specs first surfaced two real gaps the shared runner didn't model, and one semantic subtlety, all resolved before any Dafny re-run.

**Two gaps the shared runner didn't cover, so `gate_c5_runner` was generalized into a superset (Steven's call, over share-only-the-core / dosage-only):** (1) the DDI runner carries an STP-suite survivor escalation (every bare-spec survivor re-verified against the committed `drug_interaction_checker_stp_suite.dfy`, producing `killed_via_stp_suite`/`unclassifiable_via_stp_suite`) with no equivalent in the runner — naively pointing DDI at it would have silently dropped real kill coverage; (2) dosage mutates `method CalculateHourlyDose`'s clauses plus a *distinct* companion `function ExpectedDose`'s body, where the runner used a single name for both roles. `mutants_with_outcomes` gained two optional params: `body_function` (the method+companion split, mutually exclusive with `body_arithmetic`) and `survivor_escalation` (a `callable(mutated_source) -> (outcome, detail, exit_code)` hook, invoked only on an isolated-verification survivor). Renal's call is unchanged and its report stays byte-identical (parity test green); three new unit tests cover the two params. `isolate_function` already handled `method`s (confirmed by reading it), so dosage's method clause-target isolates fine.

**The semantic subtlety, checked not assumed:** isolation must target the clause entity, and for dosage that is the method `CalculateHourlyDose` — which pulls `ExpectedDose` in as a callee, keeping the pinning `ensures dose == ExpectedDose(...)` inside the unit so a mutated body is still caught. Isolating `ExpectedDose` alone would drop the pinning caller and spuriously flip its body-mutation kills to survivors. And structurally, neither dosage's `CalculateHourlyDose` nor either DDI function has an in-file caller of the mutation target (DDI's two functions only self-reference; confirmed by reading the spec), so the caller-confound never existed for either example — meaning isolation should leave every outcome unchanged and only add the guarantee. Both DDI isolated units were baseline-verified clean (1 verified, 0 errors each) before the full re-run, to catch a broken-baseline "everything kills" failure in 30 seconds rather than 40 minutes.

**Both re-derived against real Dafny 4.11.0, outcomes exactly as predicted — unchanged:** dosage 56 mutants, 41 killed / 15 filtered / 0 survived / 0 unclassifiable (identical); DDI 1342 mutants, 744 killed / 522 filtered_static / 44 survived / 26 unclassifiable / 6 killed_via_stp_suite (identical). Confirmed by identity-plus-outcome multiset diffs against the prior reports: every mutant's outcome is unchanged in both. The reports' only changes are the added `isolation_status: "isolated"` field, the six DDI STP records' "bare spec"→"isolated spec" detail reword, and — for DDI — each verified record's `N verified` summary count dropping by one (the isolated unit is one function, not the whole two-function file; a faithful record of the smaller unit, not an outcome change). Both examples' runners lost their inline `_classify`/`_real_verify`/`_filtered_outcome`/`_version` helpers (DDI keeps its `_stp_verify`, now adapted to the escalation-hook contract and reusing the shared `_classify`). Isolation is now test-pinned for both (`test_every_verified_mutant_was_isolated`). All three worked Dafny examples now run Gate C5 through the one sanctioned, always-isolating entry point; the renal/dosage/DDI reports and the shared runner provably can't drift. 298 tests pass.

---

## 2026-07-19 (later) — `evidence/gate_c5_runner.py`: the sanctioned Gate C5 entry point, extracted from the renal runner with byte-parity

The isolation work landed earlier this day wired `isolate_function` into `run_mutation_suite_renal.py` inline. This extracts that pipeline into a shared, sanctioned module so the caller-confound cannot recur by omission and so extending Gate C5 to the other examples is a call, not a copied loop.

`evidence/gate_c5_runner.py` composes generate (all five operator classes) → static filter → vacuous-precondition filter → isolate → real Dafny verify → classify. `mutants_with_outcomes(source, function_name, body_arithmetic)` returns the per-mutant records; `run_gate_c5(filepath, function_name, ...)` returns a summary dict with `in_file_callers` (a reverse-lookup over `dafny_isolate._referenced_funcs`), `isolation_used: true`, and the enumerated survivors. Isolation is unconditional — there is no whole-file mode to forget, which is the whole point; the module docstring names that as the hard constraint and points Gate C5 at itself as the required entry point.

`run_mutation_suite_renal.py` was refactored to call `mutants_with_outcomes` (its `_classify`/`_real_verify`/`_filtered_outcome`/`_version` helpers removed and now sourced from the shared module). The regenerated `mutation_report_renal.json` is **byte-identical to the committed one** (exact ordered record equality, 504 records), so the two paths provably cannot drift; the timestamp-only churn in the `.md`/manifest was discarded since the evidence is unchanged.

Independent validation via `run_gate_c5` against the three functions the task named, run live against the real Dafny 4.11.0: **ComposedCeiling** (no in-file callers) generated 46 / killed 37 / **survived 0**; **RoundHalfUp** (caller: AssessRenalFunction) 41 / 26 / **survived 4**; **CockcroftGaultCrClMlPerMin** (caller: AssessRenalFunctionFromInputs) 121 / 94 / **survived 2**. The survivor counts (0/4/2) confirm the corrected findings exactly. The task spec's reference numbers (12/28/95 generated, RoundHalfUp 7 survivors) were an earlier session's *pre-LVR-fix* isolation figures and are correctly superseded — the current generator produces more mutants (the arithmetic-embedded LVR literals), which is coverage gained, not a wiring bug; flagged rather than tuned away.

New `tests/test_gate_c5_runner.py` (6): caller reverse-lookup against the real spec, refusal on an unknown function, and — with the Dafny verify step monkeypatched — that every verified mutant is isolated (the isolated unit never contains the caller), that filtered mutants skip verification, and the summary tally shape. Scope held to `renal_adjustment`; dosage/drug_interaction_checker rollout is named follow-on, deliberately untouched. 292 tests pass (up from 286).

---

## 2026-07-19 — Gate C5 accuracy: automated caller-isolation, LVR generator fixes, renal spec tightening — an external session's package, re-derived here before trust

Steven supplied a package of Gate C5 work produced by a different Claude session that could read this repo and run Dafny (a fine-grained-traceability handoff plus `gate_c5_isolation_correction.json`, `gate_c5_cockcroftgault_manual_lvr.json`, `gate_c5_mutation_results_raw.json`, a `renal_adjustment_TIGHTENED.dfy`, and patches to `dafny_mutate.py`/`test_dafny_mutate.py`). Every claim was verified against this repo's own installed Dafny 4.11.0 before anything was trusted or integrated — the numbers were re-derived here, not imported.

**The caller-confound, verified real.** Whole-file `dafny verify` conflates a mutated function's own postcondition failing with a downstream caller failing to discharge the mutated precondition. Reproduced directly against the committed generator: `RoundHalfUp`'s `requires x >= 0.0` widened to `<= 0.0`/`!= 0.0`/`< 0.0` scored KILLED whole-file, but the error was inside `AssessRenalFunction` (a caller); in isolation those three SURVIVE. Whole-file attribution over-reports kills for any function with in-file callers — the same over-report-assurance failure mode this repo keeps hunting.

**Automated isolation, not a manual practice.** `evidence/dafny_isolate.py` (new): `isolate_function` extracts a function with its transitive callees and every datatype but never its callers, so any error under mutation is the function's own. Applied uniformly in `run_mutation_suite_renal.py`, so the confound cannot silently recur on a future function with callers (the handoff had documented a manual "isolate before trusting" practice; this builds it into the runner instead). Every isolated unit confirmed to verify clean at baseline against real Dafny.

**Two LVR generator fixes.** (4a) the literal-site locator refused arithmetic-embedded literals, so `RoundHalfUp`'s `0.5` and `CockcroftGault`'s `140`/`88.4`/`72.0`/`0.85` got no LVR coverage (recorded as `blocked_lvr_clause_literal`); now a distinct never-statically-filtered category. (4b, the serious one, which the first review pass here missed) a literal comparison-adjacent on one side but arithmetic-adjacent on the other (`0.5` in `expr - 0.5 <= x`) was read as a bare comparison operand and `_lvr_trivial` then filtered a real mutation as trivial — a silent false pass in the shipped tool, confirmed a real kill against Dafny. Both fixed; the manual CockcroftGault LVR spot-check (3 literals KILLED, 6 verified/2 errors) reproduced exactly, ensures-only, once my own first attempt's global-replace error (which also hit the body) was corrected.

**Two spec tightenings** making previously-non-load-bearing preconditions load-bearing: `ensures RoundHalfUp(x) >= 0` and `ensures ComposedCeiling(...) > 0.0`. With isolation applied, the precondition mutants of both (formerly confounded-KILLED for RoundHalfUp, honestly SURVIVED for the caller-less ComposedCeiling — a discrepancy the handoff's own summary had papered over, caught by comparing its summary against its raw data) now kill at each function's own contract. Whole-file still 7 verified / 0 errors; STP suite still 52 verified / 0 errors.

**Renal Gate C5 re-derived:** 450 → 504 mutants, 250 → 294 killed, 51 → 53 survivors, `blocked_lvr_clause_literal` gone. Survivors now fall into four explained categories (added: RoundHalfUp's two ensures-LVR rounding-tolerance widenings, newly generated by the fixed locator). `tests/test_renal_mutation_report.py` rewritten to the re-derived reality and now also asserts every verified mutant carries `isolation_status`. New `tests/test_dafny_isolate.py` (7 tests). Not yet applied to dosage/drug_interaction_checker — their functions with callers still need the same isolated re-check, named as the next step, not silently assumed clean.

285 tests pass (up from 272; +7 isolation, +net changes from the mutate-generator and renal-report test rewrites).

---

## 2026-07-18 (even later) — README evidence-strength totals and pip-install docs, plus a real drift-guard fix from Qodo

Direct instruction, following the merged `pyproject.toml` PR (#63): "update readme to include our count of proof, bounded checked etc and the new install, materials stale doc update," with an explicit constraint attached mid-turn: "don't use ambiguous test results on main readme. it needs polish and honesty, but no development hurdles."

Computed real, row-level evidence-strength totals directly from the four committed `examples/*/traceability_matrix.a.json` files (a row's realized strength is its strongest real evidence entry; GAP only when no real evidence entry exists at all) and cross-checked the row counts against each example's `metadata.a.yaml`: 28 requirements total (3 + 9 + 6 + 10), 20 `PROVEN`, 1 `BOUNDED_CHECKED` (`dosage_calculator`'s overflow-safety check — a permanent Dafny/Z3 `real`-type limit, not an unbuilt item), 7 explicit `GAP`. Added a compact table to `README.md` right after the Evidence strengths section, and the `pip install .` / `plg-evidence` console-script path to Quick start — the exact command shown was run for real from the repo root and diffed byte-identical (timestamp aside) against the committed matrix before being committed to the README. `OPERATIONS_MANUAL.md`'s command reference got the same install note for consistency.

**Qodo's review on PR #64 caught a real gap, not a false positive**: the README's new totals table hard-codes numbers derived from files that can change independently, with no mechanical check tying them together — the same failure mode PRs #54/#56 already fixed for this repo's other hard-coded doc counts. Fixed with `tests/test_readme_evidence_totals.py`: recomputes the same row-level totals from the committed matrices on every test run and asserts README's table matches, failing CI on drift rather than letting the numbers go stale silently. Positive-controlled before committing — deliberately edited README's stated PROVEN count to a wrong value, confirmed the test failed with a clear message, then restored the file and reran clean.

Adding the new test file changed the real test-suite counts again, the same self-referential effect this repo has now hit three times this week (`test_polish_lint.py`, `test_packaging.py`, now this one): 261→264 functions, 35→36 categories, 272→275 collected cases. `TEST_CATALOG.md` regenerated for real; `SYSTEM_REFERENCE.md`'s Section 9 (Testing) and Section 12 (Repository layout) counts corrected before commit. `evidence/polish_lint.py` run clean against the updated draft.

275 tests pass (up from 272; 3 new: `tests/test_readme_evidence_totals.py`).

---

## 2026-07-18 (later) — `pyproject.toml` makes the repository pip-installable, verified end to end before committing

Continuing directly from the entry below: Steven supplied `pyproject.toml.pdf` and `test_packaging.pdf` (plus re-uploads of `polish_lint.pdf`/`test_polish_lint.pdf`, confirmed byte-identical to what was already committed) with the instruction "to run e[nd] to end via pip install... verify before building."

**Verified against the live repo before writing anything**: `requirements.txt` pins (`jsonschema==4.26.0`, `PyYAML==6.0.1`, `z3-solver==4.16.0.0`, `pytest==9.1.1`) match the PDF's proposed `pyproject.toml` dependencies exactly, with `pytest` correctly excluded from the runtime `dependencies` list (declared under `[project.optional-dependencies]` instead); `evidence/cli.py` has a real `def main(argv=None):` entry point; `evidence/schema/` has four real `*.json` files; `LICENSE` exists; neither `pyproject.toml` nor `tests/test_packaging.py` already existed.

`pyproject.toml` and `tests/test_packaging.py` committed as supplied. `.gitignore` gained the packaging build-artifacts block (`build/`, `dist/`, `*.egg-info/`) from Steven's pasted version.

**"Verify before building" and "end to end via pip install" both taken literally, not treated as satisfied by the static self-consistency tests alone**: built an isolated venv, ran `pip install .` against the real local source tree, then — from `/tmp`, not the repository — confirmed the installed `plg-evidence` console script runs, `evidence.schema`'s JSON files are present as real installed package data (not just declared), and `plg-evidence build --variant a` against `dosage_calculator`'s real committed metadata/captures produces output byte-identical to the committed `traceability_matrix.a.json` except for the generation timestamp. Scratch venv and output deleted after the check; nothing about the verification method is captured in the committed test suite, matching `test_packaging.py`'s own stated precedent that a real build+install pass is a manual/release-time check, not something CI re-proves every run.

Adding `tests/test_packaging.py` changed the real test-suite counts again, the same self-referential effect caught when `test_polish_lint.py` was added: 257→261 functions, 34→35 categories, 268→272 collected cases. Caught by re-running `evidence/test_catalog.py` and `pytest --collect-only` for real; `SYSTEM_REFERENCE.md` corrected before commit, not left stale. `SYSTEM_REFERENCE.md` also updated for the packaging capability itself: Section 6 (CLI) now describes the `pip install .` path, replacing the now-false claim that no `pyproject.toml`/`setup.py`/`setup.cfg` exists; Section 11 (Known permanent limitations) now describes the still-real gap correctly (installable CLI, still no library API for external metadata) instead of the now-false "no packaging exists" bullet; Section 12's repository-layout test count corrected alongside Section 9's.

Ran `evidence/polish_lint.py` against the updated `SYSTEM_REFERENCE.md` draft — clean.

272 tests pass (up from 268; 4 new: `tests/test_packaging.py`).

---

## 2026-07-18 — `SYSTEM_REFERENCE.md` and `evidence/polish_lint.py` adopted, from an independently-produced document verified before being trusted

Steven had a different Claude Code session review this repo independently and produce `SYSTEM_REFERENCE.pdf` (37 pages) — a current-state-only technical reference, explicitly not an append-only log, contrasting with `DEVLOG.md`/`HANDOFF.md`'s dated narrative style and `SYSTEM_BLUEPRINT.md`'s now 2270+-line chain of "new entry, prior preserved below" amendments. Also supplied: `evidence/polish_lint.py` and `tests/test_polish_lint.py`, a narrow phrase-list scanner built to keep exactly this kind of document from drifting toward narrative prose the way `HANDOFF.md`/`SYSTEM_BLUEPRINT.md` already have (confirmed directly: both contain "turned out," "mistake," and dated entries scattered through body text, not just headers).

Plan mode used for this: read the full PDF (both halves, all 37 pages) before any adoption decision, per this repo's standing discipline of never accepting a secondary source's claims without direct verification — applied here even to another Claude session's own output about this very repo. Two of the document's most specific, independently-checkable claims were spot-checked first, before trusting anything else in it:

- `.github/workflows/payloadguard.yml`'s exit-code-vs-verdict-string gating — confirmed exactly by reading the workflow file directly; its own inline comment already documents the mechanism precisely (gates on `EXIT_CODE`, never the `VERDICT` label, because the composite action's wrapper mislabels any exit-0 result `"SAFE"` even for a true REVIEW/CAUTION).
- `crosshair-tool` 0.0.107's hardcoded solver seed — confirmed exactly by reading the installed package: `statespace.py:744`'s `make_default_solver()` calls `solver.set("random-seed", 42)`/`solver.set("smt.random-seed", 42)`, called from `StateSpace.__init__` (line 768) with no override path.

A fuller verification pass then checked every worked example's exact mutation-testing and traceability-matrix numbers against the real committed JSON reports, not against memory: `dosage_calculator` (56 mutants/41 killed/15 filtered/0 survived/0 unclassifiable; 3 PROVEN rows), `renal_adjustment` (450/250/137/51/10 unclassifiable/2 blocked; 4 PROVEN/5 GAP rows), `drug_interaction_checker` (1342/744/522 filtered_static/44 survived/26 unclassifiable/6 killed_via_stp_suite; 6 PROVEN/0 GAP rows), `aeb_kernel` (63/38/17/4/4; 8 PROVEN/2 GAP rows) — all matched the document's claims exactly. Also confirmed: no `pyproject.toml`/`setup.py`/`setup.cfg` exists (the document's "no packaging" claim); `TEST_CATALOG.md`'s own generated header stated 254 functions/33 categories before this session's additions; `KNOWN_LIMITATIONS.md` already documents Gate C3 Vector 4 and Gate C6's "next-phase adaptation" work as blocked, in the same terms the document used; the `evidence/` module list matched `ls evidence/*.py`'s real output exactly. Nothing required correction.

Adopted `SYSTEM_REFERENCE.md` at the repo root, converting the PDF's real content directly (all 37 pages had been read this session) rather than re-deriving it. Adopted `evidence/polish_lint.py` and `tests/test_polish_lint.py` verbatim as supplied. Ran the lint against the `SYSTEM_REFERENCE.md` draft before committing — clean on the first pass. Adding `test_polish_lint.py` itself changed the real test-suite counts the new document cited in its own Section 9 (254→257 functions, 33→34 categories, 265→268 collected cases) — caught by re-running `evidence/test_catalog.py` and `pytest --collect-only` for real rather than leaving the document's own numbers stale the moment it was committed, and the document was corrected before commit.

Documentation ripple: `README.md` (new `SYSTEM_REFERENCE.md` row in Further reading, `SYSTEM_BLUEPRINT.md`'s row annotated as build-history rather than current-state), `HANDOFF.md` (new status entry). No change to any existing example's spec, metadata, or captures.

268 tests pass (up from 265; 3 new: `tests/test_polish_lint.py`).

---

## 2026-07-16 (even later) — `HAZARD_REGISTER.md` built for `aeb_kernel`: fourth hazard register in this repo, first ISO 26262-informed one

Direct instruction, immediately following the ISO 26262 sourcing entry below: "build the hazard register now please."

10 hazard entries landed at `examples/aeb_kernel/HAZARD_REGISTER.md`, one per `REQ-AEB-*` — following `renal_adjustment`'s convention (no published numbered hazard table to transcribe from, unlike `dosage_calculator`'s GIP source), but a further step removed: `aeb_kernel` also has no internal audit document like `GATE_1C_AUDIT.md` to draw hand-traced findings from, so every entry's `Source`/`Hazardous situation`/`Risk control measure` fields are built directly from `metadata.a.yaml`'s sourced requirement text, `aeb_kernel.dfy`'s real Dafny captures, and § 571.127's own text.

**Severity, Exposure, Controllability, and the resulting ASIL are left explicit `GAP` throughout — for a reason stated precisely rather than copying the three ISO 14971 registers' framing verbatim.** Those three registers' severity/probability gaps were blocked by one thing: no named clinical SME had scored them yet (later resolved for `dosage_calculator` when Steven took that role). This register is blocked by two independent things: no named automotive-safety reviewer has classified these hazards, *and* the HARA methodology itself (§ 6.4.2 "Situation analysis and hazard identification" — the clause that actually defines how to derive Exposure and Controllability from an operational situation) isn't sourced in this repo at all. What's sourced from the entry immediately below — Table 4 (the S×E×C→ASIL lookup) and § 6.4.4 (safety-goal-statement rules) — is the *mechanical* half of risk evaluation, not the *judgment* half; assigning S/E/C without either the methodology text or a qualified reviewer would be exactly the kind of self-declared, unearned confidence this repo's discipline exists to refuse, so it wasn't attempted.

Section 3 ("Explicitly out of scope") names what § 571.127 itself covers that this kernel's ten hazards don't address at all: sensor fusion/perception (every function takes an already-measured value as a trusted input, the same trust-boundary pattern as `renal_adjustment`'s `HAZ-RENAL-8`), S6/S7/S8/S9's test-conduct methodology (confirmed, per `aeb_kernel.dfy`'s own header finding, to be NHTSA's compliance-verification procedure rather than a vehicle requirement), S10's brake-actuator mechanics, and S5.4.2.1/S5.4.2.2's named deactivation exceptions (a further extension of `HAZ-AEB-10`'s territory, not modeled even as a `GAP` row since `REQ-AEB-10` itself isn't formalized).

One hazard worth flagging: `HAZ-AEB-10` (malfunction/degradation going undetected or unnotified) is named as the highest-priority candidate for future formalization among this register's two unbuilt requirements, using the same reasoning `renal_adjustment`'s register applied to `HAZ-RENAL-4` — a silent, undetected loss of protection is a materially worse failure mode than any single mis-timed activation, since it removes the driver's own awareness that manual vigilance is now required.

Documentation ripple: `PHASE1_PLAN.md` (new status block), `README.md` (new amendment section), `SYSTEM_BLUEPRINT.md` (Section 9 addendum, component-map tree entry). No code/spec change — hazard-identification content only, all traced to already-committed evidence.

265 tests pass, unchanged (no code touched).

---

## 2026-07-16 (later) — ISO 26262-3 sourcing: a partial preview archived, a pasted secondary-source ASIL table caught wrong, and the real Table 4/6.4.4 found for free

Continuing directly from the fourth-worked-example entry below: `aeb_kernel`'s risk-management artifacts need ISO 26262 the way the medical-device examples needed ISO 14971, and that document wasn't in the repo yet.

**A real primary-source file landed, and turned out to be partial.** Steven pushed `sources/ISO-26262-3-2018.pdf` directly to `main` via GitHub's web upload. Read directly before any use: it's the iTeh "STANDARD PREVIEW" excerpt (12 pages, RC4-encrypted, print/copy allowed, no edit), covering Clauses 1–5 (Scope through a partial Item definition) of a real document whose own table of contents runs to page 28. Critically absent: Clause 6 (Hazard analysis and risk assessment) and Clause 7 (Functional safety concept) — the two clauses that would play ISO 14971's role for this example. Documented in `sources/README.md`; Steven's call via `AskUserQuestion` at that point was to get the real Clause 6/7 text before building anything, not build on the partial file or a synthesized substitute.

**A pasted "exhaustive" secondary-source summary of Clause 6/7 turned out to be wrong in exactly the way that discipline exists to catch.** Checked directly, not accepted on its own confidence: its "4-step HARA/FSC workflow" didn't match the real subclause structure already read from `ISO-26262-3-2018.pdf`'s own TOC (dropped 6.4.1, 6.4.5, 6.4.6, 7.4.1, and — most substantively — 7.4.3 "Safety validation criteria," a whole real requirement never mentioned). The pasted ASIL determination matrix couldn't be corroborated either: cross-checked against three independent public sources (piembsystech.com, nichecalcs.com, a general web search), found real disagreement between all of them on multiple cells. A follow-up "resolution" message then asserted an "absolute logic gate — C1 always defaults to QM regardless of severity" rule and specific values for the disputed cells, plus a specific clause-7.4.3 title — both directly falsified: the claimed 7.4.3 title contradicted the real TOC already in hand, and the claimed matrix values contradicted the pasted table's OWN first version from the same conversation (S3/C1/E4: original paste said ASIL A, "resolution" said QM). Four sources, four different answers for one cell (S3/C1/E4: A, B, C, QM) — reported plainly as an unresolved conflict, not picked between.

**The real Table 4 and Clause 6.4.4 text were then found for free, verified, and archived.** Steven pointed at a specific URL: `https://sources.debian.org/data/main/p/pymupdf/1.26.7%2Bds1-1/tests/resources/test_2979.pdf` — a 2-page PDF bundled as a regression-test fixture in the open-source PyMuPDF library's test suite (an incidental table-extraction bug report against page 10 of the real standard, publicly attached to [pymupdf/PyMuPDF#2979](https://github.com/pymupdf/PyMuPDF/issues/2979)). Read directly via `pdftotext` and the `Read` tool's visual render, cross-checked against each other and against `ISO-26262-3-2018.pdf`'s own TOC (which independently places "6.4.4 Determination of safety goals" starting on page 10 — an exact match, strong evidence of authenticity from a second, independently-obtained fragment of the same document). Searched further for the same free-fixture pattern covering the remaining missing clauses (6.4.1/6.4.2/6.4.5/6.4.6, all of Clause 7) — checked other PyMuPDF test PDFs (all unrelated, numbered by unrelated GitHub issues), the originating GitHub issue itself (confirmed page 10 only, no other pages attached), and other PDF-library test suites (camelot/pdfplumber/tabula) — found nothing further; only paraphrased secondary citations exist for those clauses (real clause numbers, e.g. 6.4.2.1–6.4.2.4, cited by iso26262guide.com and similar sites, but not verbatim text), not treated as sourced.

**Result: Table 4 (ASIL determination) and Clause 6.4.4 (Determination of safety goals) are now real, verbatim, and archived** — `sources/iso-26262-3-2018-table4-and-6.4.4.md`. This resolved the matrix dispute definitively: piembsystech.com's table matched the real one exactly on all 12 cells; the originally-pasted table had three real errors (S2/C1/E4, S3/C1/E3, S3/C1/E4, all understating the ASIL); nichecalcs.com's table was wrong throughout; the "resolution" message's "C1 always QM" claim is false (the real table shows C1 producing ASIL A at S2/E4 and S3/E3, ASIL B at S3/E4). One genuine substantive finding no secondary source captured: S3/C3/E1 carries a footnote (6.4.3.11) allowing QM to be argued if several independently-unlikely operating situations combine to push real exposure below E1 — real content, not a simplification error.

Steven's explicit scope call throughout: `aeb_kernel` is a proof-of-concept testing whether the Gate C1–C6 architecture generalizes to a new domain, not a real regulatory submission ("lives aren't on the line... this is a big ass test environment") — sourcing rigor was held to (every claim checked directly, nothing built on an unverified paraphrase) without insisting on purchasing the full standard once a legitimate, free, independently-verifiable source for the two operationally load-bearing clauses was found.

**What this unblocks and what's still open**: Table 4 + 6.4.4 are enough to build a first-pass `HAZARD_REGISTER.md`-style artifact for `aeb_kernel` (classify each `REQ-AEB-*` hazard's S/E/C, look up its real ASIL, state its safety goal). The HARA methodology clauses (6.4.1, 6.4.2, 6.4.3.1–.10, 6.4.6) and all of Clause 7 (FSR derivation) remain unsourced — named explicitly in `examples/aeb_kernel/PHASE1_PLAN.md`, not silently assumed covered. No code/spec change this entry — sourcing and documentation only.

265 tests pass, unchanged (no code touched).

---

## 2026-07-16 — Fourth worked example built: `examples/aeb_kernel/`, a Generic AEB kernel — first example outside the medical-device domain

Direct instruction, continuing from an earlier-session discussion about
this repo's Gate C1-C6 architecture being "pretty novel" in how the
tools are chained together: "let's look at the task and reframe it so
our system can handle it... we're not reinventing the wheel, just
looking for another domain and device we can apply our architecture
to." An uploaded research document initially framed the target around a
named commercial vehicle ("Tesla or otherwise"); reframed via
`AskUserQuestion` to a generic, non-manufacturer-specific AEB kernel
before any spec content was written — naming a specific commercial
product would have been a real sourcing/reputational risk this repo's
evidence discipline can't actually support (no OEM's real AEB
implementation detail is public), and the stated goal was proving the
architecture generalizes, not evaluating one company's system.

Asked to name real candidate source documents "line by line" so Steven
could obtain them before any build started — landed on NHTSA/DOT's 2024
Final Rule, "Automatic Emergency Braking Systems for Light Vehicles" (49
CFR Parts 571/595/596, Docket No. NHTSA-2023-0021, RIN 2127-AM37).
Steven found, verified via a screenshot of the document's own title
page, and manually committed the real 317-page PDF to
`sources/nhtsa-fmvss-127-2024.pdf` (commit `fc460c5`, "Nhtsa").

**Locating the real regulatory text.** The document is ~300 pages of
rulemaking preamble followed by the actual codified standard
(§ 571.127). Confirmed via `pdftotext -layout` + `grep -n` that
"§ 571.127 Standard No. 127..." begins at text-line 14282 of 15975;
converted to a PDF page number by counting form-feed page breaks with
`awk` (page 277), then read pages 275-294 directly via the `Read` tool —
the full codified text, S1 (Scope) through the start of S8 (pedestrian
test setup), read before a single line of `aeb_kernel.dfy` was written.
This is the same primary-source-first discipline this repo has held to
for GIP/IEC 60601-2-24/KDIGO/MHRA/NHS SPS, applied for the first time
outside the medical-device domain.

**Real structural finding, resolving an open design question rather
than requiring new engineering to solve it.** § 571.127's actual
performance requirements (S5 — Forward Collision Warning and Automatic
Emergency Braking, both vs. lead vehicles and pedestrians) are entirely
speed-envelope and deceleration-threshold based:

- S5.1.1/S5.1.2 (FCW/AEB, lead vehicle): "...traveling at any forward
  speed that is greater than 10 km/h (6.2 mph) and less than 145 km/h
  (90.1 mph)."
- S5.2.1/S5.2.2 (FCW/AEB, pedestrian): same structure, 10-73 km/h.
- S4 definitions: subject vehicle braking onset = 0.15g deceleration,
  lead vehicle braking onset = 0.05g deceleration, brake pedal
  application onset = 11 N force.
- S5.3 (false activation): peak additional deceleration must not exceed
  manual-braking-equivalent by 0.25g or greater.

No wall-clock timing appears anywhere in these actual requirements. The
document's millisecond/second-level timing figures (500 ms accelerator-
pedal release, 1.0±0.1s brake-application onset) are all confined to
S7/S8 — NHTSA's own test-CONDUCT procedure for verifying compliance on
a physical track, not a claim the vehicle's AEB system itself must
always satisfy. This meant the open design question carried into this
build from the earlier AEB scoping discussion (model the "10ms"-class
timing as an `elapsedMs: nat` Dafny parameter, or split it into an
unprovable `system_scope` claim) resolved itself: neither was needed.
Unlike `dosage_calculator`'s IEEE-754 gap (`HAZ-DOSE-003`) or
`renal_adjustment`'s CKD-EPI `Pow`-exponent gap, this domain's core
requirements hit no Dafny/Z3 structural expressiveness limit at all —
every S4/S5 clause is provable as ordinary real-number interval
arithmetic.

**Built, all in one session:**

- **`aeb_kernel.dfy`** — 6 functions (`FCWRequiredActive`,
  `AEBRequiredActive`, `IsSubjectVehicleBrakingOnset`,
  `IsLeadVehicleBrakingOnset`, `IsBrakePedalApplicationOnset`,
  `IsFalseActivationCompliant`) covering 8 requirement clauses
  (`FCWRequiredActive`/`AEBRequiredActive` each carry a lead-vehicle and
  a pedestrian requirement — numerically identical envelopes but
  confirmed, by reading both source clause pairs directly, to be
  distinct legal obligations, kept as separate functions so the
  traceability matrix credits both). `6 verified, 0 errors` (Gate C1,
  `run_verify_aeb.py`).
- **Gate C6**, run immediately after the spec first verified clean —
  per this repo's own established recommendation for a brand-new spec
  (first articulated in `renal_adjustment`'s Section 7 discussion),
  actually followed on a first build for the first time here rather
  than applied retroactively. All six functions' NL summaries
  (`evidence.dafny_nl_summary.summarize_method`) checked against
  § 571.127's text directly — `nl_confirmation_aeb_kernel_dfy.md`,
  confirmed 2026-07-16. One real thing worth naming: S5.3's compliance
  condition (`< 0.25`) is the logical negation of the source's stated
  *violation* condition ("exceeds... by 0.25g or greater") — the one
  function in this spec whose boundary direction was easy to get
  backwards by reading too quickly, caught during this review.
- **Gate C4** — `aeb_kernel_stp_suite.dfy`, 31 Spec-Testing Proof
  lemmas. Every strict-vs-inclusive boundary in the spec (the S5.1/S5.2
  envelopes and S5.3's limit are strict `<`; the S4 onset definitions
  are inclusive `>=`) tested with an ACCEPT at the exact boundary value,
  an ACCEPT one step inside, and REJECT lemmas confirming the wrong
  boolean is provably impossible. `31 verified, 0 errors`.
- **Gate C3** — all 6 functions `sat` (vector 1, no vacuous
  preconditions). **0 weak-postcondition warnings across all 6**
  (vector 2) — the tightest spec-lint result of any example built so
  far: every ensures clause is a full bi-implication (`<==>`), not a
  bare one-way `==>`, confirmed empirically (`scan_weak_postconditions`
  treats any clause containing `<==>` as strong regardless of an outer
  one-way `==>` guard, which is exactly `FCWRequiredActive`/
  `AEBRequiredActive`'s shape). `tests/test_aeb_kernel_spec_lint.py`.
- **Gate C5** — `run_mutation_suite_aeb.py`, reusing
  `evidence/dafny_mutate.py`'s ROR/LOR/AOR/LVR/COI generators unmodified
  (`function_name=None` throughout — all six functions are pure
  comparison/match logic with no `+`/`-`/`*`/`/` in any body, confirmed
  by reading the spec directly, so only clause-level mutation applies).
  63 mutants: 38 killed, 12 filtered_static, 5
  filtered_magnitude_implied, **4 survived** — all
  `IsFalseActivationCompliant`'s `requires peakAdditionalDecelG >= 0.0`
  precondition weakened (ROR to `<=`/`!=`/`<`, LVR to `-0.01`), real but
  not load-bearing for the function's single ensures clause (the
  biconditional holds regardless of sign) — same category
  `renal_adjustment`'s ledger already names ("requires-clause
  weakenings not load-bearing for the specific ensures clause currently
  proven"). **4 unclassifiable** — all COI (negate ensures clause) on
  `FCWRequiredActive`/`AEBRequiredActive`'s `target == X ==>` guard
  clauses, Dafny rejecting the mutated form with "invalid
  UnaryExpression" (negating a one-way implication whose antecedent is
  itself an equality comparison) — a real, newly-named
  `evidence/dafny_mutate.py` engine gap, same class as
  `renal_adjustment`'s documented `||`-chain ambiguity limitation, named
  rather than worked around (real new engineering, not a bounded fix).
  `tests/test_aeb_kernel_mutation_report.py`.
- **Phase 3** (evidence packaging) — `metadata.a.yaml`,
  `dafny_captures_index.json`, `traceability_matrix.a.json`/`.md`, built
  via `python -m evidence.cli build --variant a` with `--manifest`/
  `--concrete` omitted entirely (no crosshair/concrete_test evidence, as
  with `renal_adjustment`/`drug_interaction_checker`). 8 `PROVEN` rows —
  REQ-AEB-1/3 sharing `FCWRequiredActive`'s one proof, REQ-AEB-2/4
  sharing `AEBRequiredActive`'s — the many-requirements-to-one-proof
  binding `drug_interaction_checker` established, exercised for the
  second time. 2 honest `GAP` rows: REQ-AEB-9 (S3, vehicle-class
  eligibility — GVWR <= 4,536 kg) and REQ-AEB-10 (S5.4, malfunction
  detection and mode controls). Both are the first rows in this repo to
  set `metadata.schema.a.json`'s `system_scope` field, which the matrix
  binder renders as one structured GAP evidence record (`strength: GAP`,
  `scope: system_scope`, a real note) rather than the empty evidence
  array `renal_adjustment`'s no-Dafny-target GAP rows produce (neither
  `kernel_scope` nor `system_scope` set there) — a real, useful
  rendering difference worth naming, not a bug (confirmed by reading the
  produced JSON directly, a test assumption corrected once during
  writing rather than silently weakened). `tests/test_aeb_kernel_matrix.py`,
  7 tests.

**No shared-code change of any kind was needed anywhere in this
build** — `evidence.cli`, `evidence/dafny_spec_lint.py`,
`evidence/dafny_nl_summary.py`, and `evidence/dafny_mutate.py` all ran
against `aeb_kernel.dfy` completely unmodified. That is itself the
result this whole build was designed to test: the Gate C1-C6 evidence
architecture is domain-agnostic, not dosage-calculator- or even
medical-device-specific — the same six gates, the same shared modules,
the same Phase 3 packaging pipeline, applied unmodified to an
automotive-safety regulation nobody involved in building this
architecture had read when it was designed.

**Documentation**: `examples/aeb_kernel/README.md` (new — audit-trail
record: source documents, requirement-to-source mapping, four
interpretive-call caveats, fixture/capture formats, open questions),
`examples/aeb_kernel/PHASE1_PLAN.md` (new — living status document),
`SYSTEM_BLUEPRINT.md` (new Section 9, a new component-map tree entry, a
new Phase 3 evidence-inventory table row, new top header),
`KNOWN_LIMITATIONS.md` (new top entry naming both Gate C5 findings),
`HANDOFF.md` (new top entry). **No ISO 26262 (automotive functional
safety) risk-management artifacts exist for this example** — named as a
real, open gap in `PHASE1_PLAN.md`'s "Still open" section, not silently
assumed out of scope; unlike the three medical-device examples' ISO
14971 `RISK_MANAGEMENT_PLAN.md`/`HAZARD_REGISTER.md` pairs, this
automotive-domain equivalent hasn't been sourced or built.

265 tests pass (up from 253; 12 new:
`tests/test_aeb_kernel_spec_lint.py` (2),
`tests/test_aeb_kernel_mutation_report.py` (3),
`tests/test_aeb_kernel_matrix.py` (7)).

---

## 2026-07-15 (yet later still) — Finding 6 fully closed: IEC 60601-2-24:1998 clause 51.102 read directly, GIP's citation confirmed near-verbatim

Continuing directly from Finding 6 below: that entry closed a wording
drift in this repo's own GIP transcription but left one thing
explicitly open — "the IEC 601-2-24 standard's own text is still
unread by anyone in this chain." This entry closes that.

Steven obtained and supplied the actual IEC 60601-2-24:1998 (First
edition, 1998-02) — confirmed, again by publication-date logic (GIP,
Feb 2009, predates Edition 2's October 2012 publication by three
years), to be the correct edition GIP's authors would have cited. Read
directly and in full: 58 pages, cover through Annex ZB, not excerpted,
not assumed complete from a table of contents.

**Clause 51.102, "Reverse delivery" (p.36) — one of the few clauses in
this standard with no Annex AA rationale marker:**
"During NORMAL USE and/or SINGLE FAULT CONDITION of the EQUIPMENT,
continuous reverse delivery, which may cause a SAFETY HAZARD, shall not
be possible." Compared directly against GIP v1.0's own transcription
(already fixed in this repo per the entry below): the match is
near-verbatim — identical clause order, "and/or," "single fault
condition of the equipment" — GIP omits only the middle clause "which
may cause a SAFETY HAZARD." Not a coincidental resemblance; a citation
this close to word-for-word that this repo can now confirm directly.

This repo's evidentiary basis for `HAZ-GIP-1.14`'s regulatory citation
is no longer GIP v1.0 as a trusted secondary source one hop short of
the standard — it is the standard's own clause text, read and archived
directly (`sources/iec-60601-2-24-1998.pdf`), with GIP's paraphrase
independently confirmed faithful to it. First direct read of any IEC
60601-2-24 edition's actual text, for any requirement, in this repo's
history.

Updated: `HAZARD_REGISTER.md` (`HAZ-GIP-1.14`'s "Hazardous situation"
field), `metadata.yaml`/`.a`/`.b`/`.c.yaml` (REQ-GIP-1-8-1's citation,
clause 51.102 added), `RISK_MANAGEMENT_FINDINGS.md` (Finding 6's
status ledger row and full write-up), `sources/README.md`. Matrices
regenerated via `generate_artifacts.py`/`generate_matrix.py`, all Tier
1 gates passed clean. 253 tests pass, unchanged.

---

## 2026-07-15 (yet later) — Finding 6 resolved: `HAZ-GIP-1.14`'s "verbatim" GIP citation had never been checked against the primary text; a real wording drift found and fixed

Steven pressed on the S3 severity discussion for `HAZ-GIP-1.14`
(reverse delivery) — this repo's `HAZARD_REGISTER.md` cited GIP Safety
Requirement 1.8.1 as a direct quote, attributed to IEC 601-2-24, but
that quote had never actually been checked against GIP v1.0's own PDF.
This repo only ever had a reformatted markdown copy
(`sources/gip-v1.0-hazard-analysis.md`) whose own header claimed
"wording... unchanged" without that claim ever being tested.

Steven independently researched the underlying IEC citation and found
a secondary (ResearchGate-hosted) rendering of GIP's own text that
read differently from this repo's version — clause order reversed,
"or" vs. "and/or," "of the equipment" present in one but not the
other. Direct comparison flagged this as a real discrepancy, not
accepted as either source being automatically right. Steven then
obtained the actual GIP v1.0 PDF directly from the University of
Pennsylvania (not a mirror) and supplied it — read directly, all 17
pages.

**Result: the secondary source was right; this repo's own
transcription was the one that had drifted.** Fixed to the verbatim
primary text ("During normal use and/or single fault condition of the
equipment, continuous reverse delivery shall not be possible") in all
six places it appeared: `sources/gip-v1.0-hazard-analysis.md`,
`metadata.yaml`/`.a`/`.b`/`.c.yaml`, and `HAZARD_REGISTER.md`. The
§2.4.1 hazard-table row for HID 1.14 was also checked directly and
matches exactly — no drift there, closing that row's long-standing
"not yet independently re-verified" caveat too.

**A genuine byproduct, now closed either way**: the primary PDF's
hazard tables span all eight categories and none carry a severity
column — GIP v1.0 never rates severity for any hazard, confirmed
directly rather than inferred. This closes the "GIP's own hazard-table
severity rating" question live in the `HAZ-GIP-1.14` severity
discussion — not by finding a rating, but by confirming none exists.

**What this does not resolve**: the IEC 601-2-24/60601-2-24 standard's
own text is still unread by anyone in this chain — this repo's
evidentiary basis remains GIP v1.0 as a trusted secondary source, one
hop short of the standard itself, named explicitly rather than
silently narrowed by this fix.

No traceability matrix hand-edited: `generate_artifacts.py` (variants
a/b/symbolic/concrete/formal) and `generate_matrix.py` (the frozen
base) both re-run against the corrected metadata files — all Tier 1
gates (schema validation, both CONFLICT gate types, fact-equality,
structural PROVEN sweep) passed clean. `sources/gip-v1.0-full-2009.pdf`
archived as the new primary source. 253 tests pass, unchanged. Full
record: `RISK_MANAGEMENT_FINDINGS.md` Finding 6.

---

## 2026-07-15 (later) — Real severity scoring recorded for all 5 `dosage_calculator` hazards; device overall residual risk now `Unacceptable`

Direct instruction: "start on the severity values for the 5 hazards."
Finding 3/R3 (earlier the same day) had rebuilt the severity **model**
consequence-only but left every hazard's severity **value** an explicit
`GAP` pending Steven's clinical scoring — this session did that
scoring, not the model work again.

As the named Clinical SME (`RISK_MANAGEMENT_PLAN.md` Section 2), Steven
scored all five hazards in `HAZARD_REGISTER.md` via `AskUserQuestion`,
one at a time (four in a first batch, the fifth — `HAZ-DOSE-003`,
non-GIP-sourced — separately), against §4.1's real consequence-only
bands (S1–S4) and each hazard's own documented `Potential harm` text.
This repo's assistant did not propose, default, or infer any of the
five values — each was a real clinical determination, recorded with
attribution, matching the discipline every Gate C6 sign-off in this
repo has held to (substantive work prepared, but the actual
confirmation a recorded human decision).

**Result: `S3 — Serious`, all five** (`HAZ-GIP-1.14`, `HAZ-GIP-1.2`,
`HAZ-GIP-1.3`, `HAZ-GIP-1.2b`, `HAZ-DOSE-003`). Notable: `HAZ-GIP-1.14`
scored `S3` despite carrying this register's strongest probability-side
evidence (Dafny-**proven** zero delivered dose on any negative-rate
fault) — a concrete demonstration, not just an abstract claim, that
severity and proof strength are genuinely independent axes, exactly
the conflation Finding 3 found and fixed in the model itself.

Mechanically applying `RISK_MANAGEMENT_PLAN.md` §4.3's
already-specified acceptance matrix to these real values (a lookup, not
a new judgment call) — `HAZ-GIP-1.14`/`HAZ-GIP-1.2`/`HAZ-GIP-1.3`/
`HAZ-DOSE-003` combine `S3` with §4.2's standing `P5` worst-case default
to **`Unacceptable`**; `HAZ-GIP-1.2b` stays an evaluation `GAP`, since
its `Probability` — not its now-known `Severity` — is blocked by
`RISK_MANAGEMENT_FINDINGS.md` Finding 5's separate, still-open question
(whether TR 24971 §5.5.3's severity-alone evaluation applies to a
hazard with zero probability-side evidence of any kind). Per Section
5's already-specified combination method (unchanged since 2026-07-14):
if any hazard evaluates `Unacceptable`, overall residual risk is
`Unacceptable` until resolved. **This device's overall residual risk is
now `Unacceptable`** — a real, computed result, not the `GAP`
placeholder Finding 3's model-only fix left standing hours earlier.

This is not a claim the device got less safe — it is the honest output
of a real severity input meeting this plan's already-specified,
conservative worst-case-probability policy for a pre-market POC with no
field data. `RISK_MANAGEMENT_PLAN.md`'s "Path to sign-off" section's
two remaining paths (real field/usage probability data, which doesn't
exist yet; or a recorded ALARP determination from Steven as the named
Clinical SME) are now the live next decision, not a hypothetical one.

Updated: `HAZARD_REGISTER.md` (all 5 hazard rows' Severity/Risk
evaluation fields, top status block, change log), `RISK_MANAGEMENT_PLAN.md`
(§4.1's severity table, §4.3's applied matrix, Section 5's applied
method, "Path to sign-off" section throughout, Section 8 change log),
`RISK_MANAGEMENT_FINDINGS.md` (status ledger, Finding 3's full record
and "what's still open" note, the "what actually needs Steven" summary),
`README.md`'s Risk management section, `KNOWN_LIMITATIONS.md`,
`SYSTEM_BLUEPRINT.md`, `HANDOFF.md`. No code, spec, or test change —
253 tests pass, unchanged.

---

## 2026-07-15 — Three real Qodo findings on PR #55 (the R5 harness) fixed: unvalidated Dafny capture, a latent float-serialization bug, a docstring self-contradiction

An externally-supplied Qodo review of PR #55 flagged three issues. Each
independently re-verified against the real committed code before acting,
not accepted on the review's word alone — all three held up.

1. **`run_verify_dosage_differential.py` didn't actually apply "Gate C1
   discipline" despite claiming to.** It only checked `proc.returncode
   != 0`, never the verifier summary line — exactly the false-zero-guard
   gap `evidence/dafny_adapter.py::parse_dafny_capture` exists to close
   for every other Dafny capture in this repo (reused at Gate C2,
   `matrix_variants.py::dafny_record`). This differential capture sits
   outside that matrix pipeline entirely, so it was the one Dafny
   capture in the repo with no validation path at all. Fixed by calling
   `parse_dafny_capture(raw_output, manifest)` directly rather than
   re-deriving a weaker check — re-ran against the real installed Dafny
   4.11.0 toolchain, confirmed it accepts the genuine clean capture
   (`1 verified, 0 errors`) and still produces all-9-matched.
2. **`_dafny_real_literal()` converted any scientific-notation float
   through bare `int(value)`.** Lossless today only because the two
   real vectors that hit this path (`1e10`, `1e308`) are both already
   integer-valued; confirmed empirically that `int(1e-5) == 0` — a
   hypothetical fractional-scientific-notation vector would have
   silently corrupted to `0.0` with no error. Hardened to raise
   `ValueError` when `not value.is_integer()` instead of guessing;
   two new regression tests in `tests/test_dosage_differential.py`
   (the rejection case, and that the two real committed values still
   serialize losslessly).
3. **`dosage_differential_vectors.py`'s own module docstring
   contradicted itself** — opened by claiming "every vector here stays
   within the domain... `raw_dose` finite," then two sentences later
   described a vector "genuinely designed to overflow Python's
   `float`." Reworded to scope the finiteness claim to the Dafny side
   (trivially true — Dafny `real` has no overflow concept) and name the
   one Python-side exception explicitly, rather than asserting a
   blanket claim the file's own next sentence broke.

Regenerated the driver (no diff — no vector currently exercises the
hardened path) and re-ran the real capture; only the manifest's
timestamp changed, confirming the fix is behavior-preserving for
already-committed evidence. `TEST_CATALOG.md` regenerated for the 2 new
tests. 253 tests pass (up from 251).

---

## 2026-07-15 — R5 resolved: differential-testing harness built between `dosage.py`/`dosage.dfy`; postcondition drift found and fixed

Direct instruction: "let's look into R5 directly." Verified the
equivalence claim by direct comparison first, not assumed — for every
input where `raw_dose` is finite (Dafny's `real` has no other kind),
both implementations' branch logic is identical.

**Real finding surfaced during that verification, not previously
flagged:** the two files' *documented* postconditions had already
drifted. `dosage.dfy`'s `ensures` was tightened to strict
`infusionRateMlPerHr > 0.0` on 2026-07-07 (Gate C5 mutation-testing
finding); never back-ported to `dosage.py`'s docstring, still `>= 0`.
Behavior unaffected either way, but the stated contract strength had
silently diverged in this repo's own committed artifacts — three
months, found only by direct comparison.

Confirmed `dafny run` executes concrete inputs in this environment
before recommending a path (Dafny 4.11.0; output prints as clean
decimals matching Python's float format), changing Option 2's cost
assessment from "moderate effort, not attempted" to "concretely
buildable now." Steven chose **Option 2 (differential-testing
harness)** over Options 1/3, and confirmed fixing the postcondition
drift in the same pass (`AskUserQuestion` for both).

- `dosage_differential_vectors.py` (9 shared vectors, single source of
  truth) → `generate_dosage_differential_driver.py` →
  `dosage_differential_driver.dfy` (generated, calls the real
  `CalculateHourlyDose` via Dafny's own `include`) →
  `run_verify_dosage_differential.py` (real `dafny run` capture,
  Gate C1 discipline) → `differential_test_results.json`. **All 9
  vectors matched.** `tests/test_dosage_differential.py`: 5 new tests,
  no live Dafny invocation in CI (this repo's CI has none installed,
  by design).
- `dosage.py`'s postcondition tightened to `> 0`, matching
  `dosage.dfy`. Re-verified for real — `post:`/`pre:` are CrossHair-
  enforced contracts, not comments — clean, no new violations.
  `generate_artifacts.py`'s full pipeline re-run to propagate the new
  capture through every traceability matrix.
- **Scope, stated explicitly:** one vector deliberately mirrors
  `tests/test_dosage_concrete.py`'s own overflow case; both
  implementations agree, but via genuinely different reasoning
  (documented in the vector's own data, checked by a dedicated test) —
  not a REQ-DOSE-003 equivalence claim, which stays structurally
  impossible in Dafny's `real` type.
- `RISK_MANAGEMENT_PLAN.md` §4.1's `HAZ-GIP-1.14`/`1.2`/`1.3`
  evidence-artifact cells updated to cite the new confirmation.
  `RISK_MANAGEMENT_FINDINGS.md` marks R5 resolved. Root `README.md`'s
  "Risk management" section also corrected in the same pass — found
  it still described `dosage_calculator`'s severity values as
  "drafted," stale since Finding 3/R3 replaced them with `GAP` in an
  earlier PR and this paragraph was never updated.

251 tests pass (5 new).

---

## 2026-07-15 — `TEST_CATALOG.md` built: generated, categorized index of every test

Direct instruction: "I need a document that outlines each test
completed and updated as more are added. ensure that are categorized
correctly and a brief description and code." Deliberately generated,
not hand-authored, matching this session's own standing discipline
(`evidence/hazard_id_lint.py`, `evidence/citation_registry.py`): a
large catalog restated by hand would drift the same way a duplicated
citation or hazard ID already has, twice, this session — this entry
originally hard-coded a row count itself and had already gone stale by
the time of the second review round below, real proof of the point.

- `evidence/test_catalog.py`: parses every git-tracked `test_*.py`
  file under `tests/` (including any nested layout, not just direct
  children — see the PR #54 review fix below) via Python's `ast`
  module (no import, no test execution), extracts each `test_*`
  function's name, first-sentence description (from its docstring, or
  derived from its name if none), and file:line location. Categorizes
  by source file — matches how this repo already organizes its suite,
  no new taxonomy invented.
- `TEST_CATALOG.md`: the generated output, committed — its own header
  is the authoritative current count, not restated here.
- `tests/test_test_catalog.py`: regenerates the catalog in memory and
  diffs it against the committed file — CI fails if `TEST_CATALOG.md`
  drifts from the real suite, the same "generated artifact must match
  its generator" discipline `evidence/cli.py`'s own tests already
  apply to the traceability matrices. "Updated as more are added"
  means re-running the generator, not transcribing a new row by hand.
- **Two real findings from an external review (Qodo) on PR #54, both
  confirmed and fixed, not self-caught:** (1) `build_catalog()`'s git
  pathspec (`"tests/test_*.py"`) only matches `tests/`'s direct
  children in real `git ls-files` semantics, confirmed empirically —
  a nested test file would have been silently omitted with no error;
  fixed to a leading-wildcard pattern filtered to `tests/`, matching
  `hazard_id_lint.py`'s own `"*.md"` precedent. (2) this DEVLOG entry
  and `HANDOFF.md` hard-coded a row count that had already drifted by
  the time of the fix — removed the hard-coded number from
  `evidence/test_catalog.py`'s own docstring for the same reason, and
  stopped restating the count here at all; `TEST_CATALOG.md`'s
  generated header is the one place this number should live.

`README.md`'s "Further reading" table updated to link the new file.

---

## 2026-07-15 — Finding 3/R3 resolved: severity model rebuilt consequence-only, Option 3 (hybrid)

Direct instruction: "work through R3's severity model." R3
(`RISK_MANAGEMENT_FINDINGS.md`) had been open since the risk-management
audit earlier this session: `dosage_calculator`'s severity bands
defined severity by *evidence strength* ("S1: Dafny-proven, no harm
pathway is open") rather than by consequence magnitude, contradicting
ISO 14971:2019 §3.27 and stated directly by ISO/TR 24971 §5.5.4
("severity levels... should not include any element of probability").

Option 2 (keep the current model, justify under §7.1 NOTE 2) was
eliminated on textual grounds before asking Steven to choose — TR
§5.5.4 leaves no room for it. Presented Option 1 (pure consequence-only)
versus Option 3 (hybrid: consequence-only severity plus an explicit
per-hazard "which evidence artifact drives probability" column) via
`AskUserQuestion`. **Steven chose Option 3.**

Built across both artifacts:

- `RISK_MANAGEMENT_PLAN.md` §4.1: severity bands rebuilt as pure
  consequence definitions (no reference to what's proven or bounded),
  calibrated against IEC 62304 Class B's own S3 boundary and ISO/TR
  24971 Table 4's five-level descriptor set. New evidence-artifact
  column added per hazard.
- **Real, cascading consequence, stated rather than hidden:** every
  hazard's severity is now an explicit `GAP`, not a regression — the
  old S1/S2 values were never a valid consequence measurement, so
  §4.3's acceptance matrix, Section 5's overall-residual-risk method,
  and the entire "Path to sign-off" section's argument all changed from
  reporting `Unacceptable`/`Acceptable` outputs to reporting `GAP`. This
  device's overall residual risk is now `GAP`, not `Unacceptable` — not
  because it got safer, but because the prior evaluation was never
  actually computed from what ISO 14971 means by severity.
- `HAZARD_REGISTER.md`: all 5 hazards' `Severity`/`Risk evaluation`
  fields updated to `GAP`; `Probability` reverted to §4.2's standing
  worst-case-default policy for every hazard except `HAZ-GIP-1.2b`,
  whose probability stays `GAP` by deliberate design per Finding 5,
  unaffected by R3 either way.
- `RISK_MANAGEMENT_FINDINGS.md`: Finding 3 marked resolved (model), with
  the concrete next item now named explicitly — real severity values
  for all 5 hazards, Steven's clinical call, not an abstract model
  question anymore. Cross-references from Finding 5 and the R5
  (equivalence-gap) item updated to reflect the resolution.
- Two pre-existing staleness bugs fixed in the same pass, found while
  rewriting affected sections, not separately reported: Section 5 and
  the "Path to sign-off" section both still said "four hazards," stale
  since `HAZ-GIP-1.2b` split out earlier the same day (Finding 4).
- `README.md`'s Status section corrected to say `GAP`, not
  `Unacceptable`.

236 tests pass, unchanged — documentation-only, no spec/example content
change.

---

## 2026-07-15 — Root README.md brought current with the system's actual state

Direct instruction: "update the main readme to reflect the current
system." The root `README.md` had drifted in two concrete ways, both
now fixed:

- **Stale test count** (214 → 236) - both the `tests/` bullet and the
  implicit count behind "regression suite" were from before this
  session's REQ-DDI-5/6 build-out and the two new self-consistency
  lints.
- **No mention at all of the risk-management artifacts** built this
  session - `RISK_MANAGEMENT_PLAN.md`/`HAZARD_REGISTER.md` now exist
  for all three examples (ISO 14971:2019/ISO TR 24971:2020-sourced),
  consuming this system's own evidence strengths as risk-control input,
  but the README never named them. Added a new "Risk management (ISO
  14971)" section between the Gate C1-C6 section and "Repository
  layout," stating plainly that all three are `DRAFT`, not signed off,
  and that `dosage_calculator`'s device-level residual risk currently
  evaluates `Unacceptable` pending a named Clinical SME's determination
  - an honest status, not softened for a top-level doc. Also added the
  two new lints (`evidence/hazard_id_lint.py`,
  `evidence/citation_registry.py`) to the `evidence/` bullet in
  Repository layout, alongside the existing `citation_gate.py` mention.

No spec/test change; 236 tests pass (confirmed unchanged, this was a
documentation-only edit).

---

## 2026-07-15 — Two repo self-consistency lints built: `evidence/hazard_id_lint.py`, `evidence/citation_registry.py`

Direct follow-up to PR #50 (the risk-management-artifact remediation
that merged this session): that PR needed two rounds of fixes because
the same failure mode hit twice in one afternoon. First, the original
"ISO 14971's own Annex D" citation error was independently retyped
into six files with no cross-check, so PR #50 had to fix all six by
hand. Second, while fixing the hazard register's `HAZ-GIP-1.2`/`1.3`
split, a hand-edit collapsed both rows into one, silently dropping
`HAZ-GIP-1.3`'s own identity while `HAZ-GIP-1.2b` and five other
documents kept referencing it — caught only by an external reviewer
(Qodo), not self-caught. Both are the same root problem: a fact
restated independently across many files, with nothing mechanical
checking they still agree.

Built the two smallest checks that would have caught each bug on the
day it was introduced, not a session later:

- `evidence/hazard_id_lint.py` — scans every `.md` file for hazard-ID-
  shaped tokens (`HAZ-GIP-1.2b`, `HAZ-RENAL-8`, etc.) and flags any
  that don't resolve to a real `### HAZ-...` heading in some
  `HAZARD_REGISTER.md`. Run against the real repo today: zero findings
  (the `HAZ-GIP-1.3` bug is already fixed) — the value is catching the
  *next* one, mechanically, same-commit.
- `evidence/citation_registry.py` — a small registry of citations this
  repo has already disproven (today: exactly the ISO 14971 Annex D
  claim), plus a scan that flags any occurrence asserted as fact rather
  than clearly marked as a quotation or a correction. Deliberately
  narrow — new entries get added to `BANNED_CITATIONS` only after a
  citation error has actually been found and fixed everywhere it
  appeared, mirroring how this repo's `citation_gate.py` only checks
  claims already in hand rather than fetching/inventing anything.

Both ship with regression tests that run against the real, committed
repo (`test_real_repo_has_no_undefined_hazard_references`,
`test_real_repo_has_no_unmarked_annex_d_claims`) — these are the tests
that would have failed on PR #50's first commit, before the external
review caught it. Neither module resolves or replaces any open
judgment call (R3's severity model, Finding 5's evaluation procedure,
the matrix-naming question) — they only prevent the mechanical class of
error that's orthogonal to those judgment calls but has now bitten this
repo twice. 229 tests pass (13 new), no spec/example content changed.

---

## 2026-07-14 — "Path to sign-off" section added to `examples/dosage_calculator/RISK_MANAGEMENT_PLAN.md`: two of three `Unacceptable` hazards have no more buildable evidence at all

Direct instruction: "let's look at the evidence required in order to
ensure a safe sign off." Answered analytically first, in chat, before
writing anything — checked `dosage.dfy`'s actual committed source
directly rather than assuming an answer, since this repo's whole
session has held to verifying claims against real artifacts before
trusting them.

**What `dosage.dfy`'s own header comment already says, confirmed by
reading it directly:** REQ-DOSE-003 (finiteness under floating-point
overflow) is explicitly, permanently out of Dafny's reach — "Dafny's
`real` type is exact, arbitrary-precision mathematical real arithmetic
with no overflow, no infinity, no NaN... A Dafny 'proof' of finiteness
would therefore be true of a model that cannot even represent the
phenomenon REQ-DOSE-003 is about." Confirmed empirically in this repo
(2026-07-06, cited in the same comment): `y := x / 0.0` on Dafny `real`
is a verification *error*, not IEEE `inf` — there's no way to even pose
the question a Dafny proof would need to answer. `CrossHair`'s
`BOUNDED_CHECKED` result isn't a weaker stand-in for a Dafny proof
here; it's the strongest evidence this postcondition can structurally
ever have in this toolchain, the same class of permanent boundary as
`renal_adjustment`'s CKD-EPI `Pow` gap.

**Separately:** `HAZ-GIP-1.2`/`HAZ-GIP-1.3`'s residual is the
`system_scope` alarm-*signal* gap, which `RISK_MANAGEMENT_PLAN.md`
Section 1 already scopes as belonging to "integration testing against
a real device/UI layer" — outside a kernel-unit-verification POC by
design, not by oversight. No amount of further Dafny/CrossHair/
concrete-test work inside `examples/dosage_calculator/` closes this;
it requires an actual integrated pump system this POC was never scoped
to build.

Direct follow-up: "yes, write it up as a new section." **Landed** as a
new, deliberately unnumbered section in
`examples/dosage_calculator/RISK_MANAGEMENT_PLAN.md`, between Sections
5 and 6 (it doesn't map to any single ISO 14971:2019 clause, so wasn't
forced into the 4.4(a–g) numbering). States, per hazard, exactly what's
buildable versus permanently out of reach, then names the two real
paths that remain: real field/usage probability data (doesn't exist
for a pre-market POC and can't be honestly simulated), or a genuine
ALARP determination from Steven as the named Clinical SME — an ISO
14971 Annex D move [**correction, 2026-07-15**: the 2019 edition has
no Annex D; the real basis is clause 4.2 NOTE 1 and ISO/TR 24971
Annex C.4/Figure C.1 — see `RISK_MANAGEMENT_FINDINGS.md`, entry left
as originally written per this log's append-only discipline] (risk
control exhausted within stated scope,
residual accepted as tolerable with recorded reasoning), explicitly a
policy judgment only he can make, not a technical question this repo's
assistant can answer or pre-draft on his behalf. The section is
explicit that it does not pick a path or write a justification in his
voice — the `Unacceptable` finding from the prior session's work
stands until one of the two paths actually happens.

Documentation ripple: `examples/dosage_calculator/README.md` (new
"Amendment 2026-07-14 (yet later)" section), `HANDOFF.md`,
`KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`. No spec, gate, or
test-suite change; 216 tests pass.

---

## 2026-07-14 — Clinical SME assigned; draft severity/probability proposal built for `dosage_calculator`, first application of Section 4's risk-evaluation content

Direct instruction: "assign a clinical SME and start the
severity/probability tables." This landed squarely on the one boundary
this entire session's risk-management work has been built around never
crossing: a clinical SME must be a real, qualified person, and
severity/probability bands require real clinical judgment, not
plausible-sounding invention. Assigning a fictitious name or inventing
harm/probability data would have quietly undermined every `GAP` label
already committed across three `RISK_MANAGEMENT_PLAN.md` files and
three `HAZARD_REGISTER.md` files this session built.

**Declined to fabricate, asked instead.** Used `AskUserQuestion` —
the same category of moment as every Gate C6 sign-off this session has
handled: genuinely the user's decision, not something an assistant can
make on his behalf. Two questions: who fills the Clinical/SME role
(assign yourself, name someone else, or leave it open), and should
draft severity/probability content be built now (all three devices,
one device first, or wait). Answers: **Steven fills the role himself**;
draft **one device first** — `dosage_calculator`, matching this
session's established "easiest first, evaluate the output" pattern
from the hazard-register work.

**Steven recorded as the named Clinical/Subject Matter Expert**
for `dosage_calculator` (`RISK_MANAGEMENT_PLAN.md` Section 2, "assigned
2026-07-14") — a real, explicit assignment, not inferred. Risk Manager
and Technical/Verification Lead remain unassigned, narrower than
before, not glossed over.

**Built a draft severity/probability/acceptance-matrix proposal**,
reasoned entirely from `HAZARD_REGISTER.md`'s own already-committed
evidence, not invented:
- **Severity bands (S1–S4)**, redefined from illustrative placeholder
  examples to real definitions tied to this kernel's actual proven vs.
  bounded-checked guarantees — S1 Negligible (fully Dafny-proven, no
  harm pathway), S2 Minor (delivered dose stays proven-safe, but a
  real residual awareness/masking gap exists), S3 Serious (not
  currently applicable to any of the 4 hazards as mitigated today —
  retained to classify a hypothetical proof-validity failure), S4
  Critical (also not currently applicable — REQ-GIP-1-8-1 specifically
  proves the reverse-delivery instance of this outcome doesn't occur).
- **Probability bands (P1–P5)**, a standard 5-level qualitative scale
  (Improbable through Frequent) common to ISO 14971 implementations,
  with every hazard defaulting to P5 (Frequent) per this plan's own
  already-established §4.4 policy — no field data exists to justify
  anything lower, and none was invented to pretend otherwise.
- **Acceptance matrix**, extended from the template's original binary
  framing to a 3-region convention (Acceptable / ALARP / Unacceptable)
  per ISO 14971's own Annex D discussion [**correction, 2026-07-15**:
  the 2019 edition has no Annex D; real basis is clause 4.2 NOTE 1 and
  ISO/TR 24971 Annex C.4/Figure C.1 — see `RISK_MANAGEMENT_FINDINGS.md`,
  entry left as originally written per this log's append-only
  discipline] — itself flagged as a
  proposed extension for Steven to confirm or simplify back.
- **Overall residual-risk method** (clause 4.4e, Section 5): a simple,
  conservative combination rule (all hazards must individually
  evaluate Acceptable for the device overall to; any Unacceptable
  hazard makes the whole device Unacceptable) — applied for real, not
  left abstract.

**Applied to all 4 hazards in `HAZARD_REGISTER.md`.** A real, honest
finding, not a formality: given what this kernel's evidence actually
proves today, **none of the 4 hazards reaches S3 or S4** —
`HAZ-GIP-1.14` (reverse delivery) lands at S1, since REQ-GIP-1-8-1 is
fully Dafny-proven to yield exactly zero dose on any negative-rate
fault; the other three (`HAZ-GIP-1.2`, `HAZ-GIP-1.3`, `HAZ-DOSE-003`)
land at S2, since their delivered dose is always proven or bounded-
checked safe — the residual is a missing alarm-signal/masking gap, not
an unsafe dose. But under the mandated worst-case probability default
(P5 for all, per existing policy), **3 of 4 hazards currently evaluate
`Unacceptable`** under the draft matrix, making this device's proposed
**overall residual risk `Unacceptable` today** — not a comfortable
conclusion to default to, but an honest one: it correctly surfaces
that either the `system_scope` alarm-signal proof needs building, real
field probability data needs gathering, or Steven's own review needs
to revise the draft bands, before this device's risk profile could be
considered acceptable as currently evidenced.

**Every value added — severity, probability, matrix cell, and overall
evaluation — is marked `DRAFT` throughout both `RISK_MANAGEMENT_PLAN.md`
and `HAZARD_REGISTER.md`.** This is a substantive starting proposal for
Steven's review, explicitly not a self-declared SME determination —
matching this repo's Gate C6 discipline exactly: prepare the real work,
never record the confirmation on the human's behalf.

Documentation ripple: `examples/dosage_calculator/README.md` (new
"Amendment 2026-07-14 (later still)" section), `HANDOFF.md`,
`KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`. No spec, gate, or
test-suite change; 216 tests pass. Next step: awaiting Steven's actual
review/confirmation of this draft before extending the same approach
to `renal_adjustment` and `drug_interaction_checker`.

---

## 2026-07-14 — `HAZARD_REGISTER.md` landed for `drug_interaction_checker`, third and final hazard-register artifact — all three worked examples now covered

Direct instruction: "open a pr plz when you create files, I can review
them so no need to wait" — after PR #47 (the renal register) was
opened, this was read as authorization to keep building without
pausing for evaluation between steps, so this session proceeded
straight to the third and last remaining example.

Investigated this device's own source material before writing
anything, same discipline as the renal register. Like
`renal_adjustment`, `drug_interaction_checker` has no published,
numbered hazard-analysis document — `sources/sps-doac-interactions-2024.md`
is an interactions table, not a hazard analysis. What's different this
time: this spec's own Gate C6 sign-off document
(`nl_confirmation_drug_interaction_checker_dfy.md`) already contains a
real, closed hazard incident in full narrative detail from earlier
this session — Addendum 4, 2026-07-13 — making this register's
construction a matter of drawing on already-committed evidence rather
than deriving hazards fresh the way the renal register's Gate 1c
findings required more synthesis.

**Landed** as `examples/drug_interaction_checker/HAZARD_REGISTER.md`.
Six hazard entries, one per `REQ-DDI-*` — notably, all six are
currently `PROVEN`, unlike `renal_adjustment`'s mix of proven and
prose-only requirements. `HAZ-DDI-4` (the fail-safe: any pairing
outside the sourced set, including a genuine within-source gap like
apixaban+dronedarone, returns `NotCovered`, never a fabricated
`NoInteractionExpected`) is flagged explicitly as the one hazard in
this register that is fully closed by proof already, not left as
residual — a real point of contrast with `renal_adjustment`'s
still-open `HAZ-RENAL-4` equivalent, worth naming rather than treating
all six entries as uniformly closed.

`HAZ-DDI-5` documents Addendum 4's real incident in full: a second
Qodo review, run against an already-merged PR (#40), found that all
four apixaban+inducer match arms (Rifampicin, Carbamazepine, Phenytoin,
Phenobarbital) computed `Caution` unconditionally — the code never
inspected `treatmentIndication` at all, despite the paired `ensures`
clause explicitly guarding on it. This was harmless while
`TreatmentIndication` had only two constructors (the guard was always
true for every constructible value — mutation testing had already
flagged this exact pattern as a "redundant guard" survivor category).
Adding a third constructor, `OrthopaedicVTEProphylaxis`, for an
unrelated fix on the sibling `DoseReductionTargetMg` function, silently
reopened the gap. Independently re-verified against the real merged
source before being trusted (this document's own standing discipline),
then fixed to return the honest `NotCovered` — matching this repo's
`(Apixaban, Dronedarone)` silent-cell convention — with two new STP
lemmas added. `HAZ-DDI-6` documents a second, related instance: the
Dabigatran+Verapamil dose-reduction cell needed the same
indication-scoping treatment, since the source's 110mg figure applies
only to two of dabigatran's three UK-licensed indications, confirmed
via `sources/emc-smpc-dabigatran-indications-2025.md`.

The Gate C5 mutation-testing residual (1342 mutants, 44 survivors, all
three categories — function-transparency, vacuous-antecedent,
redundant-consequent — already explained in `KNOWN_LIMITATIONS.md`) and
Gate C6's closed status (**Confirmed, 2026-07-13, by Steven**, after a
full independent review and a two-round cross-check of an externally-
produced technical review report) are cited directly rather than
restated. A "Section 3: explicitly out of scope" names genuine
exclusions this device doesn't address at all: multi-drug (more than
pairwise) interactions, non-DOAC anticoagulants, jurisdiction (this
session's own earlier FDA-label research confirmed at least one
interaction is managed differently in the US), quantitative
patient-specific risk scoring, and renal function — cross-referencing
`renal_adjustment` for that last one as the device that actually
addresses it, while noting the two are not currently wired together.

Severity, probability, and risk-acceptability evaluation left as
explicit `GAP`s throughout, same discipline as both prior registers —
hazard identification is real; estimation/evaluation still need a
clinical SME that doesn't exist yet. `RISK_MANAGEMENT_PLAN.md` Section
8 updated to point at the new register.

Documentation ripple: `examples/drug_interaction_checker/README.md`
(new "Amendment 2026-07-14 (later)" section), `HANDOFF.md`,
`KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`. No spec, gate, or
test-suite change; 216 tests pass. **All three worked examples now
have both a risk-management plan and a hazard register** — the natural
next piece, if wanted, is the actual severity/probability/
acceptability evaluation all three still leave as `GAP`, which
requires a real clinical SME this repo doesn't have, not something to
fabricate.

---

## 2026-07-14 — `HAZARD_REGISTER.md` landed for `renal_adjustment`, second real hazard-register artifact — a genuinely different construction

Direct instruction: "extend to renal adjustments," following on from
`dosage_calculator`'s hazard register and the "continue with the
easiest first" instruction that produced it.

Investigated this device's available source material before writing
anything. Unlike `dosage_calculator`, `renal_adjustment` has no
published, numbered hazard-analysis document (no GIP-v1.0 equivalent)
to transcribe from — its sources (`sources/kdigo-2024-gfr-staging.md`,
`sources/mhra-renal-formula-selection-2019.md`) are clinical guidelines
naming individual facts, not a structured hazard table. Found two real
sources to build from instead: `metadata.a.yaml`'s nine sourced
`REQ-RENAL-*` requirement IDs (REQ-RENAL-1 through 8, plus
sub-requirement REQ-RENAL-1a — each already names a specific clinical
failure mode in its own text), and `GATE_1C_AUDIT.md` — this repo's own
2026-07-08 hand-trace audit, which found and named two concrete gaps
in substance, even without ISO 14971 vocabulary: "New finding 1" (no
function computes the actual CrCl/eGFR numeric value — both formulas'
outputs were being treated as already-computed caller-supplied inputs)
and "New finding 2" (a Cockcroft-Gault CrCl value could be run through
`GStage`, KDIGO's eGFR-specific staging function, producing a
category-error label — concretely demonstrated on the NHS SPS patient,
whose CrCl of 37 would misreport as "G3a" if miscategorized this way,
versus the genuinely-G3a eGFR value of 53).

**Landed** as `examples/renal_adjustment/HAZARD_REGISTER.md`. Eight
hazard entries, one per `REQ-RENAL-*` (including 1a), each honestly
split between real Dafny-proven risk control (REQ-RENAL-1/1a/2/5) and
plainly-stated `GAP` (REQ-RENAL-3/4/6/7, prose-only; REQ-RENAL-8, a
permanent trust boundary with an open operational question). Two
entries incorporate Gate 1c's own findings directly: `HAZ-RENAL-1`
folds in Finding 2, now resolved — `AssessRenalFunction`'s tagged-union
return type makes the CrCl/eGFR type confusion a type-level
impossibility, not a caller convention, proven by two explicit lemmas
(`EgfrPathNeverProducesCrClAssessment`, `CrClPathNeverProducesEGFRAssessment`,
11 verified, 0 errors). `HAZ-RENAL-2` folds in Finding 1's still-open
half: CKD-EPI eGFR's value computation remains caller-supplied, backed
by the two real `Pow` probes (`dafny_pow_expressiveness_probe.dfy`:
`Error: unresolved identifier: Pow`; `dafny_pow_axiom_trap_probe.dfy`:
an unproven `{:axiom}` verifies an absurd claim just as cleanly as a
correct one) confirming this is a genuine Dafny/Z3 expressiveness
limit, not a choice — Cockcroft-Gault's own value computation, by
contrast, is closed and proven (`CockcroftGaultCrClMlPerMin`, 7
verified, 0 errors). Along the way, corrected a real prior
mis-attribution while citing REQ-RENAL-2's evidence: an earlier
addendum had attributed the "1.23/1.04" Cockcroft-Gault constants to
MHRA; MHRA only names Cockcroft-Gault as the required method — the
constants are standard unit-conversion arithmetic (corrected
2026-07-10, now cited correctly here rather than repeating the error).

`HAZ-RENAL-4` (fail-safe on missing/invalid data) is flagged explicitly
as the highest-priority candidate among the four prose-only
requirements for eventual formalization — defaulting to an
*unadjusted* full dose on bad data is a fail-open pattern, materially
different in kind from the numeric-accuracy concerns in the other
entries — named as a judgment call, not resolved, since prioritization
itself is a risk-acceptability decision this register doesn't make.
`HAZ-RENAL-5` documents a hazard this pipeline already caught and
closed itself, not left open: Gate C4's STP suite (2026-07-09) found
the original `ComposedCeiling`/`AssessRenalFunction` spec
under-constrained — bounded above by both inputs without being pinned
to either — a REJECT lemma against the underconstrained spec failed to
verify (`raw_dafny_output_stp_suite_against_underconstrained_renal.txt`,
`0 verified, 4 errors`), fixed by adding pinning clauses, re-verified
clean.

A "Section 3: explicitly out of scope" distinguishes genuine
exclusions (per-drug dosing tables downstream of the composed ceiling,
input measurement quality, non-renal contraindications, pregnancy/
paediatric formulas) from the four `GAP` rows, which are in scope but
not yet built — a sharper distinction than `dosage_calculator`'s
register needed to draw, since that device's out-of-scope section was
mostly "not this kernel's job at all" rather than "named but unbuilt."

Severity, probability, and risk-acceptability evaluation left as
explicit `GAP`s throughout, same discipline as both prior artifacts —
hazard identification is real; estimation/evaluation still need a
clinical SME that doesn't exist yet. `RISK_MANAGEMENT_PLAN.md` Section
8 updated to point at the new register.

Documentation ripple: `examples/renal_adjustment/README.md` (new
"Amendment 2026-07-14 (later)" section), `HANDOFF.md`,
`KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`. No spec, gate, or
test-suite change; 216 tests pass. No PR opened yet — not requested for
this change specifically. `drug_interaction_checker` is now the one
remaining worked example without a hazard register.

---

## 2026-07-14 — `HAZARD_REGISTER.md` landed for `dosage_calculator`, first real hazard-register artifact in this repo

Direct instruction, after PR #45 (all three risk-management plans)
merged: "continue with the easiest first please so we can evaluate the
output." Interpreted as: of the three worked examples, build the next
missing piece (a real hazard register, which every plan's Section 8
named as not yet existing) for whichever example makes that most
tractable without fabricating clinical judgment, so the result can be
reviewed before deciding whether/how to extend it to the other two.

Investigated all three examples' primary sources before picking one.
Found `sources/gip-v1.0-hazard-analysis.md` — a real, published formal
hazard analysis (Arney/Jetley/Jones/Lee/Ray/Sokolsky/Zhang, FDA Office
of Science and Engineering Laboratories + UPenn, February 2009),
containing a structured, numbered hazard table (~85 rows across eight
categories: Operational, Environmental, Electrical, Hardware, Software,
Mechanical, Biological/Chemical, Use). `dosage_calculator`'s own
`metadata.a.yaml` already cites three of these hazard IDs directly in
its STRIDE threat model (`THR-GIP-1-2`: GIP Hazard 1.2; `THR-GIP-1-3`:
GIP Hazard 1.3; `THR-GIP-1-14`: GIP Hazard 1.14, mapped to REQ-GIP-1-4-12
and REQ-GIP-1-8-1 respectively). Neither `renal_adjustment` nor
`drug_interaction_checker` has an equivalent formal hazard-analysis
source — their sources (KDIGO, MHRA, NHS SPS, eMC SmPCs) are clinical
guidelines and interaction tables, not structured hazard identification.
This made `dosage_calculator` the clear easiest choice: hazard
identification (ISO 14971:2019 clause 5.4) could be built almost
entirely from real, already-cited source data, not fresh judgment
calls.

**Landed** as `examples/dosage_calculator/HAZARD_REGISTER.md`. Four
hazard entries: `HAZ-GIP-1.2` and `HAZ-GIP-1.3` (both real GIP hazards
mitigated at this kernel's scope by REQ-GIP-1-4-12 — stated explicitly
that the kernel doesn't distinguish their two different causes, since
both collapse to the same detected over-limit condition, rather than
implying two independently-covered hazards); `HAZ-GIP-1.14` (mitigated
by REQ-GIP-1-8-1's reverse-delivery fault handling, cross-referencing
`dosage.py`'s own docstring, which already names "GIP v1.0 Safety
Requirement 1.8.1 / Hazard 1.14" and explains why the negative-rate
check deliberately runs before the finiteness check); `HAZ-DOSE-003`
(the one row with **no** GIP source — `metadata.a.yaml`'s own
`REQ-DOSE-003` text already says so directly — included for real
risk-control completeness but flagged plainly as weaker evidence,
`BOUNDED_CHECKED` not `PROVEN`, not presented at parity with the other
three). A "Section 3: explicitly out of scope" names representative
hazards from GIP's full table this kernel does not address (programmed-
flow-rate validation, physical sensing, hardware/electrical/
environmental/biological categories) so the register cannot be misread
as exhaustive over the whole pump — only over what this narrow
dose-calculation kernel actually touches.

Severity, probability, and risk-acceptability evaluation (ISO
14971:2019 clauses 5.5's quantitative half, 6, and 8) are left as
explicit `GAP`s throughout, same discipline as `RISK_MANAGEMENT_PLAN.md`
— this register completes hazard *identification*, not risk
*estimation* or *evaluation*, both of which require a named clinical
SME and manufacturer acceptability policy that still don't exist.
`RISK_MANAGEMENT_PLAN.md` Section 8 updated to point at the new
register and be precise about what it does and doesn't complete.

**Branch note:** PR #45 (the three risk-management plans) had already
merged before this work started. Per this repo's merged-branch
protocol, the session branch was restarted from the latest `main`
(`git fetch origin main && git checkout -B claude/repo-docs-review-9l23t8
origin/main`) before building this, with the in-progress hazard-register
work stashed and popped across the reset to avoid losing it.

Documentation ripple: `examples/dosage_calculator/README.md` (new
"Amendment 2026-07-14 (later)" section), `HANDOFF.md`,
`KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`. No spec, gate, or
test-suite change; 216 tests pass. No PR opened yet for this change —
the user asked to evaluate this first result before deciding how to
extend the approach to the other two examples, whose sources don't
offer an equivalent formal hazard analysis to build from.

---

## 2026-07-14 — `RISK_MANAGEMENT_PLAN.md` landed for `dosage_calculator`, third and final risk-management-plan artifact — all three worked examples now covered

Direct instruction: "build the same plan for dosage_calculator."
Mirrors both prior plans' structure and ISO 14971:2019 clause
citations (already verified verbatim against the real standard when
the first plan was built; not re-verified per device).

Device-specific content read directly from this repo's own real,
committed evidence: `metadata.a.yaml` (intended use; `B`/`DECLARED`
safety classification, same rationale pattern as the other two
devices), `traceability_matrix.a.md` and `dafny_captures_index.json`
(3 requirement rows: REQ-GIP-1-4-12, REQ-GIP-1-8-1, REQ-DOSE-003),
`mutation_report.md` and `README.md`'s Gate C5 amendments (56 mutants
— 41 killed, 15 filtered across four filter categories, **0
survivors, 0 unclassifiable** — the cleanest residual of the three
worked examples, reached only after two later real engineering
extensions closed 2 mid-run survivors), and
`nl_confirmation_dosage_dfy.md`'s "Decision" section (Gate C6
**Confirmed, 2026-07-07, by Steven** — "it's good for the spec as
is" — confirmed to be the first Gate C6 sign-off recorded anywhere in
this repository, predating both other examples' sign-offs).

Two real, device-specific distinctions surfaced honestly rather than
smoothed over to match the other two plans' shape:

1. **Mixed evidence strength within one requirement set.**
   `dosage_calculator` is the only example with three independent
   evidence types (CrossHair bounded symbolic search, concrete example
   tests, Dafny formal proof) rather than Dafny alone. REQ-DOSE-003
   specifically has no Dafny proof at all — only CrossHair
   `BOUNDED_CHECKED` and one concrete `EXAMPLE_CHECKED` test — and
   Section 6's table states this plainly rather than implying the same
   proof strength as the other two rows.
2. **A real kernel/system scope split already exists in the
   requirement text itself.** REQ-GIP-1-4-12 carries both a
   `kernel_scope` (alarm *detection*, verified at this phase) and a
   `system_scope` (alarm *signal generation*, explicitly deferred to
   integration testing, IEC 60601-1-8/62366-1 territory) — from the
   2026-07-05 Gate 1 review. This became Section 1's real
   life-cycle-phase scoping, not an invented boundary. Also named: the
   device's existing STRIDE threat model (`THR-GIP-1-2/1-3/1-14`) is a
   related but distinct artifact from the clinical hazard register
   this plan still doesn't contain — flagged so the two are never
   conflated later.

Sections requiring clinical judgment (roles; severity/probability
bands; acceptance matrix; overall-residual-risk method) left as
explicit `GAP`s, not fabricated — same discipline as the other two
plans, same underlying reason: `metadata.a.yaml`'s
`classification_rationale` already names the `B` classification as
`DECLARED`, not sourced.

Documentation ripple: `examples/dosage_calculator/README.md` (new
"Amendment 2026-07-14" section), `HANDOFF.md`, `KNOWN_LIMITATIONS.md`,
`SYSTEM_BLUEPRINT.md`. No spec, gate, or test-suite change; 216 tests
pass throughout. **All three worked examples now have a real, landed
risk-management-plan artifact** — the natural next piece, if wanted,
is the actual hazard register all three plans point at and none yet
contain.

---

## 2026-07-14 — `RISK_MANAGEMENT_PLAN.md` landed for `renal_adjustment`, second real ISO 14971 risk-management-plan artifact, same day as the first

Direct instruction: "build the same plan for renal_adjustment." Mirrors
`examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md` (landed
earlier the same day) structurally and in its ISO 14971:2019 clause
citations — those describe the standard itself, already verified
verbatim against the real text, so not re-verified per device.

Device-specific content pulled from this repo's own real, committed
evidence, read directly rather than assumed: `metadata.a.yaml` (intended
use, `B`/`DECLARED` safety classification), `traceability_matrix.a.md`
(5 `PROVEN` rows: REQ-RENAL-1/1a/2/5, plus the multi-function
REQ-RENAL-1/2 bindings; 5 `GAP` rows: REQ-RENAL-3/4/6/7 named-but-
unformalized, REQ-RENAL-8's permanent trust boundary with an open
operational question), `dafny_captures_index.json` (all seven
functions share one raw-output/manifest pair), `mutation_report_renal.md`
and `KNOWN_LIMITATIONS.md` (450 mutants: 250 killed, 137 filtered
pre-verification, 2 blocked, 10 unclassifiable, **51 survive** — all
three survivor categories already explained: 33 vacuous-antecedent-
style guard narrowing, 17 requires-weakenings the proven `ensures`
clauses don't depend on, 1 coincidental numeric survivor independently
resolved by Gate C4's STP suite), and
`nl_confirmation_renal_adjustment_dfy.md`'s "Decision" section (Gate C6
**Confirmed, 2026-07-11, by Steven**, against the raw KDIGO/MHRA
sources directly — all six checkpoints verified, one external citation
flagged as unverifiable and confirmed not load-bearing).

Sections requiring clinical judgment (roles; severity/probability
bands; acceptance matrix; the overall-residual-risk method) left as
explicit `GAP`s, not fabricated — same discipline as the
`drug_interaction_checker` plan, and for the same underlying reason:
`metadata.a.yaml`'s `classification_rationale` already names the `B`
classification as `DECLARED`, not sourced, pending exactly this kind
of file.

**A real, pre-existing staleness bug found and fixed along the way,
unrelated to the new document.** While reading
`examples/renal_adjustment/README.md` for Section 6's Gate C6
reference, its own "Open questions" item 4 still read "Gate C6's
sign-off is still pending" — but Gate C6 was confirmed and closed the
same day that sentence was written (2026-07-11, same session per
`nl_confirmation_renal_adjustment_dfy.md`'s Decision timestamp). The
2026-07-11 documentation audit (this file, same date) had fixed the
equivalent stale "nearly complete" claim in the top-level `README.md`
but evidently never touched this per-example copy — five weeks stale
by today's date, caught only because this session happened to read the
file closely for an unrelated reason. Fixed in place, marked resolved,
not deleted, per this repo's frozen-record discipline.

Documentation ripple: `examples/renal_adjustment/README.md` (new
"Amendment 2026-07-14" section, plus the Open-questions fix above),
`HANDOFF.md`, `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`. No spec,
gate, or test-suite change; 216 tests pass throughout.

---

## 2026-07-14 — `RISK_MANAGEMENT_PLAN.md` landed for `drug_interaction_checker`, first real ISO 14971 risk-management-plan artifact in this repo

Two documents were supplied: the official ISO 14971:2019 standard PDF,
and a provisional, not-yet-reviewed "Risk Management Plan" markdown
template, explicitly flagged as provisional by the person who supplied
it. Per this repo's own standing discipline (externally-supplied claims
get verified against a primary source before being trusted — already
applied twice this session to two drafts of an external "Gate C
Technical Review Report"), the standard was read directly rather than
taking the template's clause citations on faith.

`pdftoppm` (poppler-utils) was not installed in this session's
container; installed via `apt-get install -y poppler-utils` rather than
falling back to a cruder, already-present "best-effort" zlib/regex PDF
text extractor from earlier in the session. Clauses 1 through 7.1 of
the real standard were then read verbatim (title/foreword/scope/
definitions/clause 4 in full/clause 5 in full/clause 6/start of
clause 7), including the exact wording of clause 4.4(a–g) and 4.5,
which the template cites directly.

**Cross-check result:** the template's clause citations for sections
1 through 7 (4.4a scope, 4.4b roles, 4.4c review requirements, 4.4d
risk acceptability — including the specific "criteria for accepting
risk when probability cannot be estimated" sub-requirement, verified
verbatim — 4.4e residual-risk method, 4.4f verification activities,
4.4g production/post-production) all matched the standard's real
wording exactly. Clause 1's stated exclusions (decisions in the
context of a specific clinical procedure; business risk management)
also verified verbatim. **One real, minor citation slip found:** the
template's opening line attributed "this plan is part of the risk
management file" to clause 4.5. That sentence is verbatim in clause
4.4, immediately before the a–g list. Clause 4.5 is a separate
requirement — what the risk management *file* itself must provide
traceability for (risk analysis, risk evaluation, risk-control
implementation/verification, residual-risk results) — which is what
the template's own second sentence (what this document does NOT
contain) actually reflects. Fixed by re-attributing the first sentence
to 4.4 and the second explicitly to 4.5.

**Landed** as `examples/drug_interaction_checker/RISK_MANAGEMENT_PLAN.md`,
with the citation fix applied and device-specific content filled in
from this repo's own already-committed, real evidence — not invented.
Section 1 (scope) uses `metadata.a.yaml`'s real `intended_use` text
verbatim. Section 3 (review requirements) states, as real established
practice rather than aspiration, the out-of-cycle review trigger this
repo already runs in practice (every Gate C6 Addendum 1–5 was exactly
this kind of trigger). Section 6 (verification activities) is
populated with all six REQ-DDI-* rows, each citing its real Gate C1–C6
evidence file (`raw_dafny_output_ddi.txt`, `run_manifest_dafny_ddi.json`,
the STP suite, `mutation_report_ddi.md`) and the current Gate C5
mutation-testing residual (44 survivors, already explained in
`KNOWN_LIMITATIONS.md`, not silently carried forward as an unstated
gap), plus Gate C6's closed status.

**Sections 2 and 4 (roles; severity/probability bands; acceptance
matrix) deliberately left as explicit `GAP`s, not fabricated.** No
clinical SME is assigned to this device yet, and inventing severity or
probability numbers for a decision-support classifier would be exactly
the kind of unearned claim this repo's evidence pipeline exists to
prevent. `metadata.a.yaml`'s own `classification_rationale` already
names this precisely: safety classification `B` is `DECLARED`, not
sourced, and explicitly "requires a manufacturer-specific ISO 14971
risk file before this can be upgraded from DECLARED to sourced" — this
document is the start of that file, not its completion. Section 5
(method for evaluating overall residual risk) is also an explicit GAP:
no hazard register exists yet to evaluate.

Documentation ripple: `examples/drug_interaction_checker/README.md`
(new "Amendment 2026-07-14" section), `HANDOFF.md` (new top entry).
No spec, gate, or test-suite change — this is a new document type, not
a code change; the existing 216-test baseline is unaffected.

---

## 2026-07-13 — Gate C6 confirmed and closed for `drug_interaction_checker.dfy`, against the raw sources directly

A full, independent, line-by-line review was performed at Steven's
request — not a re-read of prior summaries. Every one of
`sources/sps-doac-interactions-2024.md`'s 17 sections was cross-checked
directly against its corresponding `ensures` clause(s) and match arm(s)
in the current spec (all 68 `CheckInteraction` postconditions, all 5
`DoseReductionTargetMg` postconditions) — no discrepancy found. The two
most recently changed cells were checked specifically against both
primary sources and confirmed correct. Live re-verification, not from
memory: `2 verified, 0 errors` (main spec), `25 verified, 0 errors` / 21
real lemmas (STP suite), every lemma spot-checked against its
corresponding `ensures` clause.

**Two drafts of an externally-produced "Gate C Technical Review Report"
were then independently cross-checked against the real artifacts before
either was trusted.** The first draft had four real errors, all
confirmed by direct inspection: a "25 lemmas" miscount (the same class
of task-count/lemma-count conflation this document's own history
already caught once, 2026-07-10); a reversed causality claim about the
`requires` clause removal and the third `TreatmentIndication`
constructor (real chronology: removed 2026-07-12 with two constructors;
the third, added a day later, *caused* the scope-leak bug rather than
enabling anything); a wrong attribution of the multi-line-clause fix
to `evidence/dafny_mutate.py` gaining accumulation logic (the real fix
was reformatting the clauses to single lines; the tool was never
extended — confirmed via direct `grep`); and a conflation of the 26
`unclassifiable` mutants (real static type errors and parser
ambiguities) with "Dafny function transparency limits" (a real, but
unrelated, concept).

A second, corrected draft fixed all four precisely — each re-verified
directly again. One further precision point was raised and preserved,
not merged away: the corrected draft's claim that the 44 `survived`
mutants uniformly "represent a genuine limitation of Dafny function
transparency" is accurate for why the Gate C5 STP-suite escalation
can't help any of them, but not a complete account of why they survive
the bare-spec check at all — this document's own established
categorization keeps three distinct mechanisms deliberately separate
(`CheckInteraction`'s 4 LOR survivors: vacuous-antecedent; its 3
SSRIOrSNRI ROR survivors: redundant-consequent; `DoseReductionTargetMg`'s
37: requires-domain-restriction plus body-obliviousness, the one
function transparency actually names). Recorded in
`nl_confirmation_drug_interaction_checker_dfy.md`'s final "Decision"
section, keeping the distinction explicit rather than collapsing it.

**Decision — Confirmed, 2026-07-13, by Steven.** Every finding raised
against this spec across Addenda 1–5 and this final review is resolved.
**All six Gate C1–C6 pipeline steps are now built AND confirmed for
`drug_interaction_checker` — Gate C6 is closed.** 216 tests pass
(unaffected, doc-only change).

---

## 2026-07-13 — Pre-sign-off numbering-currency review of the C6 doc caught a stale claim Addendum 4 left behind; fixed

A pre-sign-off review of `nl_confirmation_drug_interaction_checker_dfy.md`,
checking specifically whether the document's own numbering claims were
still current (not the spec itself — Addendum 4 already covered that),
found one real defect: the "Summary presented, regenerated 2026-07-13
(current spec, both functions)" section's header and paragraph still
asserted its postcondition numbering "matches exactly" and "no
renumbering was needed" — true when written, false after Addendum 4
added four new `CheckInteraction` postconditions and shifted three of
the four apixaban+inducer `Caution` clauses (Carbamazepine 48→49,
Phenytoin 52→54, Phenobarbital 56→59). Addendum 1's own numbering claim
had already been corrected in place when Addendum 4 was written, but
that correction was never propagated to this earlier section, whose
stale claim sits directly above the actual 68-postcondition block —
the more dangerous copy of the same error, since it's positioned at the
point of use rather than deferred to a cross-reference.

Independently re-verified live before acting, not accepted on the
finding's word alone: re-ran `evidence.dafny_nl_summary.summarize_method`
against the real, current spec directly, confirming 27/28, 49/50, 54/55,
59/60 exactly. **Fixed**: the section header marked `— SUPERSEDED,
historical record only` (matching this document's own established
2026-07-10 convention); a new paragraph explaining the stale claim
inserted immediately below, the original paragraph left in place,
unedited, per this document's own "leave the history alone, re-anchor
it" discipline, with an explicit "do not rely on this" flag appended
directly to the stale text. Recorded as Addendum 5. No `.dfy` spec
content affected — a documentation-currency fix only. 216 tests pass
(unaffected, doc-only change).

## 2026-07-13 — Gate C5 extended to re-verify the STP suite against every mutation-testing survivor; caught a real latent scope-leak class before it could ever become a regression

Continuation of the same day's work (see the entry immediately below,
PR #41, merged): during Gate C6 sign-off review, asked to look into
whether `drug_interaction_checker`'s 50 mutation-testing survivors
could be reduced under current constraints. Diagnosed all 50 by
category before touching anything: `CheckInteraction`'s 7 (3
SSRIOrSNRI "consequent independently proven" + 4 LOR-vacuity on the
REQ-DDI-5 indication disjunction) and `DoseReductionTargetMg`'s 43 (6
`requires`-clause indication-guard ROR + 37 `ensures`-clause
guard-antecedent) — matching this repo's already-established survivor
taxonomy, none new.

**Hand-probed before building, per this repo's own standing
discipline.** Applied one of the 6 `requires`-clause survivor mutations
to a scratch copy and checked whether the already-committed STP suite
(`drug_interaction_checker_stp_suite.dfy`, Gate C4's real ACCEPT/REJECT
lemmas) would catch it if re-verified against the mutant instead of
just the bare spec: **it did** — the STP suite's own ACCEPT lemma for
`DoseReductionTargetMg(Dabigatran, Verapamil, AFStrokePrevention)`
failed to verify (`function precondition could not be proved`), since
the mutation simultaneously widens the requires clause to admit the
orthopaedic indication (the exact class of scope-leak the previous
entry's fix closed on `CheckInteraction`) while excluding the lemma's
own witness call. Also hand-probed one `ensures`-clause ROR mutant and
one LOR mutant on each function to check whether this same escalation
would help there too: **it did not** — both functions are plain
(non-`{:opaque}`) Dafny `function`s, so a same-module STP lemma calling
one with concrete literal arguments gets verified by Dafny unfolding
the body directly, making the mutated `ensures`-clause text provably
irrelevant to that proof. A genuine Dafny-semantics fact, not a
shortfall of the escalation to fix — closing it would require marking
these functions `{:opaque}` with explicit `reveal` calls everywhere
they're used, a much larger, invasive redesign disproportionate to a
testing-methodology limitation.

**Built**: `run_mutation_suite_ddi.py` now re-verifies the committed
STP suite (reused verbatim, no new lemma authored) against every mutant
that survives the bare-spec check, via a new `_stp_verify` helper that
redirects the suite's own `include` at the mutant file. A mutant the
STP suite catches is reclassified from `survived` to a new,
distinct `killed_via_stp_suite` outcome — kept separate from ordinary
`killed` so the report stays honest about which gate actually caught
each one, not merged silently.

**Real run**: 1342 mutants (unchanged) — 744 killed, 522
filtered_static, **44 survived** (down from 50), 26 unclassifiable, **6
killed_via_stp_suite** — exactly the 6 hand-predicted requires-clause
indication-guard mutants, confirmed directly against the report, not
assumed from the count alone. `CheckInteraction`'s 7 and
`DoseReductionTargetMg`'s remaining 37 ensures-clause survivors are
unaffected, matching the hand-probe's prediction.
`tests/test_drug_interaction_checker_mutation_report.py` updated: new
test for the `killed_via_stp_suite` category, existing survivor-count
assertions updated (43 → 37 for `DoseReductionTargetMg`, 50 → 44
overall), a new "Run 5" section added to the module docstring. Full
suite: 215 passed (up from 214).

## 2026-07-13 — Second Qodo review (on merged PR #40) found a real scope-leak in CheckInteraction's own apixaban rows; fixed, all six gates re-run

Continuation of the same day's earlier work (see the entry immediately
below): PR #40 (the `TreatmentIndication` third-constructor fix,
`OrthopaedicVTEProphylaxis`) merged externally. A second Qodo code
review, run against the merged code, found a real bug in a sibling
function to the one PR #40 was written for.

**The bug.** `CheckInteraction`'s four apixaban+inducer match arms
(Rifampicin, Carbamazepine, Phenytoin, Phenobarbital) computed `Caution`
unconditionally — the match body never inspected `treatmentIndication`
at all, even though the corresponding `ensures` clause explicitly
guarded on `treatmentIndication == AFStrokePrevention ||
treatmentIndication == RecurrentVTEPrevention`. This was harmless while
`TreatmentIndication` had only those two constructors (the guard was
always true for every constructible value — already a known mutation-
testing "redundant guard" survivor category). Adding
`OrthopaedicVTEProphylaxis` (for `DoseReductionTargetMg`'s own indication
guard, the actual point of PR #40) silently reopened the gap: calling
`CheckInteraction` with the new indication now returned a fabricated
`Caution` instead of the honest `NotCovered` this repo's own established
silent-cell convention (`(Apixaban, Dronedarone)`) calls for — exactly
the failure mode Addendum 3's Finding 3 had already named as the general
risk of widening a match statement's input domain without re-checking
every existing arm against it, caught here on a different function than
the one that finding was about.

**Independently re-verified before acting**, per this repo's own
standing discipline: read the actual merged `.dfy` source directly
(not the review's word) and confirmed the mismatch — an unambiguous bug,
not a design judgment call, so fixed directly rather than raised as a
question (per this session's own established practice: "if you feel
confident in how to resolve an event... push the fix").

**Fix**: each of the four match arms now branches on
`treatmentIndication`, matching `(Apixaban, Dronedarone)`'s
`NotCovered` pattern exactly. Four new `ensures` clauses added, pinning
`NotCovered` for `OrthopaedicVTEProphylaxis` on each inducer.

**All six gates re-run for real, on a branch restarted from
`origin/main` post-merge** (new work on already-merged code, not a
reopening of PR #40's own change): C1 `2 verified, 0 errors`; C4/STP two
new lemmas, `25 verified, 0 errors` (up from 23); C3
`scan_weak_postconditions` count for `CheckInteraction` now 68 (up from
64); C5 real re-run of `run_mutation_suite_ddi.py` — **1342 mutants: 744
killed, 522 filtered_static, 50 survived, 26 unclassifiable**.
`CheckInteraction`'s own survivors dropped sharply, 31 → 7 (the four
REQ-DDI-5 indication-disjunction survivors collapsed from a broad
"redundant guard" pattern to a narrower LOR-vacuity case now that the
guard is actually load-bearing; the pre-existing 3 SSRIOrSNRI survivors
are unchanged). `DoseReductionTargetMg`'s own 43 survivors are
unaffected — this fix didn't touch that function.
`tests/test_drug_interaction_checker_mutation_report.py` and
`tests/test_drug_interaction_checker_spec_lint.py` updated accordingly;
full suite (214 tests) passing throughout.

Documentation ripple: `metadata.a.yaml`'s REQ-DDI-5 text rewritten to
describe the fix; `traceability_matrix.a.json`/`.md` regenerated (still
6/6 `PROVEN`, no GAP rows);
`nl_confirmation_drug_interaction_checker_dfy.md` gained a fresh
regenerated NL summary (68 postconditions) and "Addendum 4" documenting
the finding, the independent re-verification, and the fix — Addendum 1's
stale postcondition-numbering references (48/52/56) corrected in place
to their new positions (49/54/59) with the renumbering explained, not
silently changed. Gate C6 remains open — not because any finding is
still unresolved (Addendum 3's four findings, including the
`RecurrentVTEPrevention` scope question, were all resolved before it
closed), but because Steven's actual sign-off review of the current
spec shape still hasn't happened; this addendum adds a new finding on
top of an otherwise-ready document, it doesn't reopen Addendum 3.

## 2026-07-13 — REQ-DDI-6's real spec-scope finding fixed: TreatmentIndication's third constructor, plus an independent mutation-testing tooling gap found and fixed

Continuation of the same day's earlier Gate C6 review work (see the
entry immediately below): its third finding — `DoseReductionTargetMg
(Dabigatran, Verapamil) == 110` proven unconditionally despite the
source scoping that figure to specific indications — was left
deliberately open pending primary-source verification and a design
decision only Steven could make.

**Primary source fetched and archived first**, per this repo's own
"verify first" discipline: `sources/emc-smpc-dabigatran-indications-2025.md`
(eMC SmPC for Pradaxa, both 110mg and 150mg products, revision date 16
January 2025). Confirmed two things directly against the real source
text, independent of the earlier review's own claims — (1)
`RecurrentVTEPrevention` correctly covers the verapamil row's
"DVT/PE-prevention-and-treatment" phrase (both it and the rifampicin
row's phrasing are partial descriptions of the *same* single
eMC-licensed indication category, not two different ones — no new
constructor needed for that specific naming worry); (2) dabigatran
genuinely has a third, current, UK-licensed indication (primary VTE
prevention after elective hip/knee replacement surgery, a structurally
different once-daily regimen) that `TreatmentIndication` doesn't
represent at all, and that the verapamil interaction row is
confirmed silent on — the real SmPC's own §4.2 states the
verapamil dose-reduction instruction only under the two twice-daily
indications (NVAF, DVT/PE), never under the orthopaedic regimen.

**Presented to Steven via `AskUserQuestion`, not resolved by an
assistant**: add the third constructor now (recommended, since the
finding was confirmed real), and leave the merged REQ-DDI-6 matrix row
as its prior PROVEN state until the fix landed rather than caveat it in
the interim. Both explicit choices, not defaults.

**Implemented (Fix 2A + Fix 2B, per the earlier review's own proposed
remediation, adjusted after hand-derivation and empirical verification
— not applied blindly):**

- `TreatmentIndication` gained a third constructor,
  `OrthopaedicVTEProphylaxis`. Apixaban's own REQ-DDI-5 rows in
  `CheckInteraction` are unaffected — they still guard on only the
  first two constructors, correctly making no claim about the new
  value, since apixaban's own orthopaedic-indication exclusion was
  already a deliberate, different, unrevisited decision from an earlier
  session.
- `DoseReductionTargetMg` gained a `treatmentIndication` parameter; its
  Dabigatran+Verapamil requires/ensures clauses gained the indication
  guard `(treatmentIndication == AFStrokePrevention ||
  treatmentIndication == RecurrentVTEPrevention)`, matching
  `CheckInteraction`'s own apixaban-row pattern exactly. The four
  Edoxaban clauses stay deliberately indication-free, matching the
  source's own uneven shape.
- **Fix 2B, adjusted after hand-derivation, not applied as originally
  proposed**: a new STP lemma,
  `DoseTargetDomainAgreesWithCheckInteraction`
  (`drug_interaction_checker_stp_suite.dfy`), proves
  `DoseReductionTargetMg`'s precondition domain exactly equals
  "`CheckInteraction` says `DoseReductionAdvised`" minus the SSRI
  exclusion minus a *new* orthopaedic-indication exclusion. The
  original proposed lemma text (predating the third constructor) omitted
  that third conjunct and would NOT have verified once the constructor
  existed — `CheckInteraction`'s own (Dabigatran, Verapamil) ensures
  clause claims `DoseReductionAdvised` unconditionally, for every
  `TreatmentIndication` value including the new one (the outcome KIND
  doesn't depend on indication; only the exact mg figure does) — caught
  by hand-deriving the claim and independently verifying it in a
  standalone probe before editing the real suite, not by trusting the
  review's text to transfer unchanged. Real run: `23 verified, 0
  errors` (up from 20).

**A second, independent finding, not part of the original review,
caught before trusting the first re-run of this fix**: writing the new
requires/ensures clauses across multiple physical lines (for
readability) silently truncated `evidence/dafny_mutate.py`'s
clause-site locator at the first physical line. The first real mutation
re-run reported only 1171 mutants (down from 1178) with the Edoxaban
disjuncts and the ensures clause's own consequent entirely missing from
requires-clause coverage — a real regression in test coverage, not
caught by Dafny (both clauses still verified clean) or by pytest (only
outcome *counts* were pinned, not the exact mutant set, and the count
drop alone didn't obviously signal truncation). Diagnosed directly:
every truncated mutant's `original_clause` read exactly `'(doac ==
Dabigatran && agent == Verapamil'`, cut off before the indication guard
and the `==> ... == 110` consequent. Fixed by reformatting both clauses
to single lines, matching this repo's own established precedent
(`renal_adjustment.dfy`'s equivalent Gate C6 gap, fixed the same way
rather than extending the tool) — no committed capture yet depended on
the multi-line formatting.

**Final real re-run, all six gates**: C1 `2 verified, 0 errors`; C4/STP
`23 verified, 0 errors`; C3 precondition still satisfiable, weak-
postcondition counts unchanged; C5 **1250 mutants — 668 killed, 482
filtered_static, 74 survived, 26 unclassifiable** — the jump in every
count reflects real, previously-missing coverage of the full 5-disjunct
requires clause and the full indication-guarded ensures clause, not a
new class of finding. `CheckInteraction`'s own 31 survivors unchanged
throughout. `DoseReductionTargetMg` contributes 43 survivors (6
requires-clause indication-guard + 37 ensures-clause guard-antecedent,
both the same already-established "never load-bearing" category) and
all 26 unclassifiable results (24 ROR datatype-ordering type errors + 2
LOR parser-ambiguity refusals, both the same already-established
categories now correctly counted at full scale, not a new category).
`tests/test_drug_interaction_checker_mutation_report.py` rewritten to
match, with new tests distinguishing the indication-guard-specific
requires survivors from the (all-killed) doac/agent requires
comparisons via clause-text diffing, not substring presence (a naive
substring check would have misclassified every requires-clause mutant,
since the full multi-disjunct clause text contains both indication
names regardless of which token was actually mutated).

**Phase 3 regenerated via the real CLI, not hand-edited**:
`metadata.a.yaml`'s REQ-DDI-5/REQ-DDI-6 text updated to describe the
third constructor and the new indication guard;
`traceability_matrix.a.json`/`.md` regenerated — still 6/6 `PROVEN`
rows, no GAP rows. Documentation updated throughout:
`nl_confirmation_drug_interaction_checker_dfy.md` (a second regenerated
NL-summary block for `DoseReductionTargetMg`, Addendum 2's item 6, a
fourth finding and closing resolution added to Addendum 3 — the
document now states explicitly it's ready for Steven's actual sign-off,
which still hasn't happened), `HANDOFF.md`, `KNOWN_LIMITATIONS.md`,
`SYSTEM_BLUEPRINT.md`, `PHASE1_PLAN.md`. 214 tests pass.

---

## 2026-07-13 — Gate C6 review of the REQ-DDI-5/REQ-DDI-6 sign-off document: two defects fixed, one real spec-scope finding left open

An externally-supplied review of
`nl_confirmation_drug_interaction_checker_dfy.md`'s two 2026-07-12
addenda (written deliberately before Steven's sign-off, to catch this
before it could be rubber-stamped) found three defects. Every finding
was independently re-verified against the real committed artifacts
before acting on it — not accepted on the review's word alone, matching
this repo's standing discipline for external claims.

**Finding 1 (stale NL summary), FIXED.** The addenda's own "Summary
presented" block was still the pre-REQ-DDI-5/6, 2026-07-10 generation:
`CheckInteraction`'s old 3-arg signature, its now-removed `requires`
clause, 60 (not 64) postconditions, and no `DoseReductionTargetMg`
summary at all — confirmed directly by reading the file. A reviewer
following Addendum 1's own instruction to check "Postcondition
27/48/52/56" against that block would land on four unrelated,
pre-REQ-DDI-5 clauses. Fixed by regenerating both functions' summaries
for real via `evidence.dafny_nl_summary.summarize_method` against the
current committed spec and inserting them as a new, dated "Summary
presented, regenerated 2026-07-13" block; the stale block was marked
superseded and left in place as a frozen historical record, matching
`GATE_1C_AUDIT.md`'s own convention of appending dated corrections
rather than rewriting history. Confirmed the postcondition numbering
Addendum 1 already cited (27/48/52/56) matches the real regenerated
summary exactly — no renumbering was needed, only presenting the block
that had been missing.

**Finding 3 (missing wildcard-arm review item), FIXED.** Grep of the
entire sign-off document for `assert false`/`wildcard`/`Qodo` returned
zero matches — Addendum 2 never mentioned the `case _ => (assert false;
0)` fix from the Qodo review on PR #39, despite it being
`DoseReductionTargetMg`'s most recently changed line and the one with
the largest measured effect on Gate C5's own results (7 survivors
converted to kills, confirmed in the prior 2026-07-12 entry below).
Fixed by adding it as Addendum 2's item 5.

**Finding 2 (REQ-DDI-5/REQ-DDI-6 scope inconsistency), NOT fixed —
open, deliberately not resolved by an assistant.** Verified directly
against `sources/sps-doac-interactions-2024.md` lines 57-65: the
dabigatran+verapamil 110mg dose-reduction figure is stated to apply
"for AF-stroke-prevention and DVT/PE-prevention-and-treatment
indications specifically" — the source treats this row as
indication-scoped, structurally the same as the apixaban+rifampicin/
carbamazepine/phenytoin/phenobarbital rows REQ-DDI-5 was built to
handle. But the archived source file's own editorial layer dismisses
that scoping in the same sentence ("this doesn't need an indication
axis to model correctly... the dose reduction just applies whenever
dabigatran is used for either") — a design judgment baked into
`sources/`'s verbatim-extraction layer at archive time, not itself a
further primary-source quote. `DoseReductionTargetMg` (REQ-DDI-6, built
and merged 2026-07-12) faithfully inherited that dismissal: it takes no
`treatmentIndication` parameter and proves the 110mg figure
unconditionally, wider in scope than the sentence it cites.

Not currently a soundness bug: `TreatmentIndication` has exactly two
constructors and both are within the source's stated scope for this
row, so the proof holds for every currently-representable input. The
defect is that the claim's proven scope is wider than the source's
stated scope, and nothing in `DoseReductionTargetMg`'s signature,
clauses, or comments records that an indication axis was ever
considered and dropped for this cell — a future third
`TreatmentIndication` constructor would degrade `CheckInteraction`
visibly (its guard clauses are explicit, catchable by Gate C4) but
`DoseReductionTargetMg` silently (no clause references indications at
all). Whether `RecurrentVTEPrevention` (named for the rifampicin row's
"prevention of recurrent deep vein thrombosis (DVT) and pulmonary
embolism (PE)") actually contains the verapamil row's differently
worded "DVT/PE-prevention-and-treatment" scope is a real clinical-
licensing question, not a documentation nicety — dabigatran is UK/EU-
licensed for at least three distinct indications (NVAF stroke
prevention; DVT/PE treatment-and-recurrence-prevention; primary VTE
prophylaxis after elective hip/knee replacement, a once-daily regimen
structurally different from the twice-daily rule the 110mg figure
presupposes), and answering this requires a primary source (dabigatran's
own SmPC/EMA product information), not secondary literature.

Presented to Steven via `AskUserQuestion` before acting: chose to verify
the primary source first (matching this repo's own "verify first, then
we'll consider the solutions" discipline, established earlier this
session for the original REQ-DDI-5/6 scoping question) rather than
guess at a fix; also chose to fix Findings 1 and 3 immediately since
they're mechanical, non-judgment-call defects independent of Finding
2's outcome.

Documentation updated to reflect Gate C6 is genuinely open, not
closed, for REQ-DDI-5/REQ-DDI-6: `HANDOFF.md` (new top entry, corrected
the prior "Gate C6 is closed" bullet), `KNOWN_LIMITATIONS.md` (new
ledger row + detailed section), `PHASE1_PLAN.md` (a dated correction
appended after the "Full Gate C1–C6 re-run" claim, not rewritten).
`nl_confirmation_drug_interaction_checker_dfy.md` gained the regenerated
summary block, Addendum 2's new item 5, and a new "Addendum 3"
documenting this whole review pass. Branch restarted from `origin/main`
(`14805d4`, the merged PR #39) before this work, per the established
merged-PR-restart convention. 214 tests pass (no regression; sign-off
document and doc-only changes this pass, no spec or code changes).

Next concrete step: fetch and archive dabigatran's real SmPC/EMA
licensing text under `sources/`, per the established convention, to
determine whether `RecurrentVTEPrevention` covers the verapamil row's
stated scope or whether `TreatmentIndication` needs a third constructor
— then present the resulting decision to Steven (per the review's own
explicit instruction: "do not let an assistant resolve these").

---

## 2026-07-12 — REQ-DDI-5 and REQ-DDI-6 built for real: both v2 items closed, no GAP rows remain in drug_interaction_checker

Follow-on from the same-day source-verification entry below: instruction
"scope out extending drug_interaction_checker with REQ-DDI-5/6" produced
a full plan (`/root/.claude/plans/stateless-weaving-firefly.md`),
approved after two `AskUserQuestion` resolutions — `TreatmentIndication`
gets exactly 2 constructors (only the indications the interaction source
itself names, not a third VTE-prophylaxis case that exists only in a
different, posology source with no stated interaction outcome), and
both requirements are built in one pass, sequenced by risk.

**REQ-DDI-5 (indication axis).** Added
`datatype TreatmentIndication = AFStrokePrevention |
RecurrentVTEPrevention` to `drug_interaction_checker.dfy`, as
`CheckInteraction`'s fourth parameter. Both named indications give
apixaban the identical sourced "use with caution" outcome for the
rifampicin/carbamazepine/phenytoin/phenobarbital rows — so once the type
is closed to exactly those two values, every constructible input is
provable, and `CheckInteraction`'s previous `requires` clause (excluding
the four apixaban+inducer cells outright) is removed entirely, not
narrowed. Four previously-unreachable match arms become real, reachable
arms; 4 new `ensures` clauses added (60→64 total). All 60 pre-existing
`ensures` clauses' recursive calls updated to the new 4-arg signature.
Re-verified clean.

**REQ-DDI-6 (numeric dose-reduction targets).** New companion function
`DoseReductionTargetMg(doac, agent): int`, requires-gated bare-`int`
(deliberately matching `renal_adjustment.dfy`'s `SelectFormula`/
`AssessRenalFunction` precedent rather than introducing this repo's
first `Option<int>` pattern — resolved in `PHASE1_PLAN.md`'s own "Still
open" section), pinning the five real sourced figures:
Dabigatran+Verapamil→110mg, Edoxaban+{Dronedarone,
ErythromycinSystemic, Ketoconazole, Ciclosporin}→30mg each. Apixaban
never appears in this function's precondition — a direct, confirmed
consequence of `CheckInteraction` never producing `DoseReductionAdvised`
for apixaban anywhere in its match arms, not a hand-written exclusion.
Dabigatran+SSRIOrSNRI deliberately excluded permanently (the source
gives no mg figure for that cell). A `case _ => 0 // unreachable`
wildcard arm was added before ever running Dafny, since a `match` on
`(doac, agent)` must be exhaustive over the full type regardless of the
`requires` clause — caught by direct grep-counting during implementation
(4 unreachable match arms existed at that point, not the 3 the plan text
predicted; corrected before editing, not trusted from the plan's prose).
Both functions verify together in one invocation: `2 verified, 0
errors`.

**A real engineering boundary found and deliberately not fixed:**
`evidence/dafny_mutate.py`'s `generate_aor_mutants`/`generate_lvr_mutants`
body-scanning mode refused outright on `DoseReductionTargetMg`'s body —
a `//` comment on the wildcard arm ("refusing to locate mutation sites
rather than risk a misaligned offset or a comment slash mistaken for
division"). Clause-level LVR alone (omitting `function_name`) gave 10
real mutants covering all 5 pinned figures exactly, all killed —
equivalent coverage without new shared-module engineering; named
explicitly in `run_mutation_suite_ddi.py`'s own docstring rather than
silently worked around, matching `renal_adjustment`'s own precedent for
naming (not always fixing) engine limitations.

**All six gates re-run for real, for both requirements, in the
established order:**
- **C1**: re-verified, re-captured (`raw_dafny_output_ddi.txt`,
  `run_manifest_dafny_ddi.json` — one real invocation covers both
  functions now).
- **C6**: two new addenda drafted in
  `nl_confirmation_drug_interaction_checker_dfy.md`, each explicitly
  marked "not yet confirmed — pending review" — drafted, not
  self-signed-off in the same pass that generated them.
- **C4**: `drug_interaction_checker_stp_suite.dfy` gained 6 new lemmas
  (2 ACCEPT + 1 REJECT per requirement); all 11 pre-existing
  `CheckInteraction` calls updated with a placeholder 4th argument
  (`AFStrokePrevention`). `20 verified, 0 errors` (up from 14).
- **C3**: spec lint re-run — `TreatmentIndication` got Z3 `EnumSort`
  treatment automatically, no code change needed (confirmed empirically,
  not assumed from the shared translator's generality);
  weak-postcondition count bumped 60→64; `DoseReductionTargetMg`'s
  precondition confirmed satisfiable.
- **C5**: mutation testing restructured from a single-`FUNCTION`
  constant to a `FUNCTIONS` tuple-driven loop in
  `run_mutation_suite_ddi.py`, mirroring `run_mutation_suite_renal.py`'s
  established precedent (including fixing
  `check_precondition_satisfiability`'s call to use the loop variable,
  not a hardcoded constant). First real run: **1178 mutants — 634
  killed, 472 filtered_static, 68 survived, 4 unclassifiable.**
  `CheckInteraction`'s own 31 survivors are byte-for-byte the same set
  REQ-DDI-5's own build already established (confirmed directly, not
  assumed unaffected): 28 are a new category (the `treatmentIndication`
  disjunction — a redundant guard, since both named indications give the
  identical outcome and the match arm doesn't inspect the value at all
  for these four cells), 3 are the pre-existing SSRIOrSNRI antecedent
  category, unchanged. `DoseReductionTargetMg` contributed 37 new
  survivors (7 requires-clause + 30 ensures-clause guard-antecedent
  mutations — the same "weakening not load-bearing" shape
  `CheckInteraction`'s own now-removed requires clause used to fall
  into, confirmed via a byte-identical-consequent check, not assumed)
  and all 4 unclassifiable results (a real, expected REAPPEARANCE of the
  datatype-vs-datatype ROR type-error category REQ-DDI-5 had made
  disappear entirely, since `DoseReductionTargetMg`'s own new `requires`
  clause reintroduces a `doac`/`agent` datatype comparison — a structural
  consequence of adding a new requires clause with a datatype comparison,
  not a regression in either function). All 10 LVR mutants on the five
  pinned mg figures killed, none survived — proof the figures are exact,
  not just roughly right.

  **Refined the same day, via a Qodo code-review finding on PR #39**:
  `DoseReductionTargetMg`'s wildcard match arm's bare `0` literal
  (returned for any out-of-domain `(doac, agent)` pair, genuinely
  unreachable given the `requires` clause but still a real fallback
  value) was flagged as a reliability risk — if this spec were ever
  compiled and called from unverified code with the precondition
  violated, `0mg` is not a meaningful dose and would fail silently
  rather than loudly. Fixed with `case _ => (assert false; 0)`,
  verified empirically against the real Dafny 4.11.0 toolchain to still
  compile and verify cleanly (Dafny proves the branch unreachable given
  the requires clause, a vacuous-truth argument, not just accepted on
  faith). **A real, positive side effect on Gate C5's own results**: the
  7 requires-clause ROR survivors are now ALL KILLED — a mutated
  requires clause can admit a `(doac, agent)` pair that falls into the
  wildcard arm, and Dafny can no longer prove `assert false` there, so
  the previously-silent "requires-clause weakening not load-bearing"
  survivor category is now a genuine, caught verification failure.
  **Re-run for real: 1178 mutants — 641 killed, 472 filtered_static, 61
  survived, 4 unclassifiable** (`filtered_static`/`unclassifiable`
  unchanged, confirming this was a real strengthening of the proof, not
  a shift in unrelated mutant classes). `DoseReductionTargetMg` now
  contributes exactly 30 survivors (ensures-only), not 37.
  `tests/test_drug_interaction_checker_mutation_report.py` updated to
  match, including a new test pinning that every requires-clause ROR
  mutant is now killed or unclassifiable, never a survivor.

**Phase 3 regenerated, not hand-edited.** `metadata.a.yaml`: REQ-DDI-5
gained a real `implementation`/`evidence` block reusing the
`CheckInteraction` capture (a fifth requirement sharing one proof);
REQ-DDI-6 gained its own block binding `DoseReductionTargetMg` — the
first time this repo's matrix binder has bound two different Dafny
methods from the same spec file across two requirements in one metadata
file. `dafny_captures_index.json` gained a second key
(`drug_interaction_checker.dfy::DoseReductionTargetMg`) pointing at the
same physical capture files as the `CheckInteraction` key — both
functions verify together in one Dafny invocation, mirroring
`renal_adjustment`'s own established multi-key-same-capture precedent.
`traceability_matrix.a.json`/`.md` regenerated via the real
`evidence.cli build` — all 6 rows now `intent_ok: true` with real
`PROVEN` evidence, no GAP rows remain in this example; `assert_no_realized_proven`
(R3) independently re-checked against the committed artifact.

**Test suite updated in place, not just re-run:**
`tests/test_drug_interaction_checker_spec_lint.py` (renamed/rewrote the
removed-requires-clause test, bumped the weak-postcondition count to 64,
added 2 new tests for `DoseReductionTargetMg`);
`tests/test_drug_interaction_checker_mutation_report.py` (rewritten
twice across the two requirements — final: total/outcome-count test,
per-category survivor tests for both new categories, the unclassifiable
type-error test, an LVR-all-killed test, and a closing
all-survivors-accounted-for test); `tests/test_dafny_nl_summary.py` (the
now-obsolete "multiline requires clause" test rewritten to assert "(none
declared)," since REQ-DDI-5 removed the clause it was testing — the
underlying multi-line-reconstruction capability stays separately
protected by its own synthetic fixture test, confirmed unaffected);
`tests/test_drug_interaction_checker_matrix.py` (the old "deferred
requirements render as honest gaps" test replaced with real PROVEN-row
assertions for both requirements plus a no-GAP-rows-remain check).

Documentation ripple: `PHASE1_PLAN.md` (REQ-DDI-5/6 rows moved from
"named, deferred"/"staged v2" to "built 2026-07-12," full gate-by-gate
account, "Still open" item 1 resolved and struck through),
`GATE_1C_AUDIT.md` (a dated update note added near the REQ-by-REQ trace
table, the historical 2026-07-10 rows themselves left untouched as a
frozen record), `KNOWN_LIMITATIONS.md` (new "Phase E REQ-DDI-5/REQ-DDI-6"
table row and section), `SYSTEM_BLUEPRINT.md` (component-map entries for
`DoseReductionTargetMg`, the second `dafny_captures_index.json` key, the
restructured mutation suite, and the summary table row), `HANDOFF.md`
(new top entry, `drug_interaction_checker` status block updated).

213 tests pass (up from 205 — no code regression; the increase is new
`DoseReductionTargetMg`/REQ-DDI-5/6-specific coverage).

---

## 2026-07-12 — Verified an external REQ-DDI-5/6 scoping document against primary sources; archived four new sources, no requirement built

Direct instruction: review of an externally-supplied research document
("Scoping REQ-DDI-5/6: Can Apixaban Indication-Dependent Dosing and
Numeric Dose-Reduction Rules Be Built From Public, Citable Sources?"),
then "verify first, then we'll consider the solutions" — deliberately
deferring any build decision until every load-bearing claim was checked
against a primary source, following this repo's standing rule
(`HANDOFF.md`) that external research documents have carried fabricated
or misattributed citations here more than once.

**In-repo verification (`sources/sps-doac-interactions-2024.md`,
already committed):** ran the document's own claimed quotes through
`evidence/citation_gate.py` directly. All five real claims returned
`CONFIRMED` — edoxaban's "30mg daily" numeric target (4 occurrences),
dabigatran's "110mg twice daily" target, apixaban's qualitative-only
interaction language, the complete absence of any apixaban+mg
co-occurrence anywhere in the source, and the REQ-DDI-5 indication
branching (rifampicin/carbamazepine "use apixaban with caution" scoped
to two named indications only). **A deliberate false control** —
"decrease the dose of apixaban by 50%," a claim the research document
says does NOT exist in UK sources — correctly returned `NOT_FOUND`,
independently confirming the gate isn't rubber-stamping and that the
central negative claim (no UK numeric apixaban interaction rule) holds.
One self-correction along the way: an initial doubt about whether the
dabigatran "110mg" figure was actually in-source was wrong — it hadn't
been read yet; the mechanical grep caught the gap in review, not a
defect in the research document.

**External verification (fetched directly, verbatim extraction
requested, then citation-gated where practical):**
- eMC SmPC, both apixaban strengths (product 2878, 5 mg, revised 04 Jan
  2024; product 4756, 2.5 mg) — confirmed the NVAF "2-of-3" dose-
  reduction rule verbatim on both pages, confirmed it is NVAF-only (the
  VTEt heading carries no such criteria), confirmed the 2.5 mg SmPC's
  own hip/knee VTE-prophylaxis indication and regimen, and independently
  corroborated (from the legal SmPC itself, not just SPS's derived page)
  that apixaban interaction dosing is qualitative-only — "not
  recommended," no percentage or mg figure anywhere.
- MHRA Drug Safety Update, volume 16, issue 10 (May 2023) — confirmed
  the renal-severity dosing table's apixaban row, and confirmed the
  table itself branches by indication at the same renal-severity band
  (SPAF gets a numeric dose reduction at CrCl 15-29; VTEp/VTEt get
  qualitative "caution" only) — the same indication-conditional pattern
  REQ-DDI-5's scoping identified for drug interactions, here shown to
  generalize to renal dosing too, a third independent primary source
  making the same structural point.
- US FDA ELIQUIS label §7.1 (via DailyMed, cross-referenced against
  FDA's own hosted PDF) — confirmed verbatim the "decrease by 50%"
  interaction rule the UK sources lack, establishing the jurisdictional
  divergence is real, not an artifact of incomplete UK source coverage.

**Archived as new sources, per `sources/README.md`'s own convention**
(citation with dates/URLs, fetch provenance, verbatim extraction,
explicit confirms/corrects/extends notes): `emc-smpc-apixaban-posology-
2024.md`, `mhra-dsu-doac-renal-dosing-2023.md`, and
`fda-eliquis-label-interactions-2016.md` (the last explicitly flagged as
a non-UK contrast source, not a substitute for UK guidance — every other
apixaban source in this folder is UK-jurisdiction, matching this
example's established sourcing convention). `sources/README.md`'s
Contents list updated with matching entries.

**`examples/drug_interaction_checker/PHASE1_PLAN.md`'s REQ-DDI-5/6 rows
updated with pointers to the newly-verified sources** — not built, not
scoped as a new requirement yet, just linked so the verified ground is
visible exactly where a future session would look. REQ-DDI-6's row now
states explicitly that apixaban's absence of a numeric interaction
target was checked against three independent UK primary sources, not
assumed from one.

No code changed, no new requirement built, no matrix regenerated —
per direct instruction, this session stopped at verification and
archival. The solutions/scoping conversation (extend
`drug_interaction_checker` vs. a new dosing-calculator example; how to
represent apixaban's genuine gap) is deliberately deferred to a
follow-up session.

## 2026-07-11 — Scoped REQ-RENAL-8 (classification-flag provenance): decision to leave an explicit GAP, framing refined from "permanent" to "parked pending data"

Direct instruction: "scope out REQ-RENAL-8's classification-flag
provenance." Entered plan mode, ran a documentation-history Explore
agent, and read the spec/schema/binder directly. The scoping surfaced a
real structural finding worth recording: **REQ-RENAL-8 can never render
as anything but a GAP as the system currently stands.** The schema's
evidence-method enum is exactly `['crosshair', 'concrete_test',
'dafny']` — there is no `declared` method — and while `DECLARED` exists
in the `Strength` enum with a caveat, no binder ever produces a
*realized* `DECLARED` record. So `DECLARED` is only ever an intent,
never a realized strength; a legitimate evidence level per the repo's
own taxonomy (README's ladder lists it) with no path to actually
realize it. Closing REQ-RENAL-8 therefore splits into two genuinely
separate things: (a) the real-world process decision — who populates
`SelectFormula`'s flags (clinician form / EHR lookup / static versioned
list) — which is Steven's, not code's; and (b) machinery to represent a
DECLARED decision as bound evidence rather than a bare GAP (a new
shared-code path, the untrodden ground the Phase 3 plan already
flagged).

Put the fork to Steven (permanent honest GAP / add a real DECLARED
evidence path / prose-only decision). **His call: "I'll try and get the
data, it doesn't need to be immediate if we can explicitly leave the gap
until I talk to people."** So: no machinery built, no process answer
forced — the row stays an explicit GAP while he gathers the real data by
talking to the relevant people.

The one honest refinement that decision implied, and that this session
made (no code change): the docs had framed REQ-RENAL-8 as *permanent —
"nobody ever intends to resolve"* the provenance question, conflating
two things that are actually separate. The **trust boundary** (flags
caller-supplied, never computed or proven inside the spec) is permanent
and will never be a Dafny proof target — that stays. But the
**provenance answer** is *not* permanently unresolvable; Steven is
actively gathering it, and it will land as a DECLARED process fact, not
a proof. Refined that framing across `metadata.a.yaml` (REQ-RENAL-8
`text`, then the matrix regenerated via `evidence.cli`, not hand-edited
— only `requirement_text` and `generated_utc` changed, the derived
"intended DECLARED, realized GAP" note untouched), `KNOWN_LIMITATIONS.md`
(three spots), `examples/renal_adjustment/README.md`, `PHASE1_PLAN.md`
(fallback section + requirements row), `HANDOFF.md`, and
`tests/test_renal_adjustment_matrix.py` (docstrings; one test renamed
from `..._is_a_permanent_declared_gap...` to
`..._is_a_declared_gap_parked_for_process_data...`, assertions
unchanged — still GAP, still DECLARED intent). The `intended_method:
DECLARED` label and the distinction from REQ-RENAL-3/4/6/7's PROVEN-intent
gaps both stay correct. Dated snapshot `dashboards/status-findings.html`
deliberately left as-is per its own "regenerate, don't trust" discipline.
205 tests pass, no regressions.

## 2026-07-11 — Two named-not-fixed items closed: dosage_calculator's stale provenance hash, drug_interaction_checker's missing README

Direct instruction, following straight on from the documentation-audit
session (previous entry below), which had surfaced these exact two
items as open but explicitly out of scope at the time: "create the
missing readme and fix the 6. bug" (referring to items 5 and 6 of a
"what's next" list given to Steven — the missing README and the stale
provenance-index hash, in that order).

**Fix 1 — `dosage_calculator/artifact_index.json`'s stale SHA-256
hashes for `dosage.dfy` and `run_manifest_dafny.json`.** Root cause
investigated before touching anything, not assumed: `git log` on both
files showed the last real edit was commit `0dc2715` (2026-07-07,
"Fix Gate C5 finding: tighten REQ-GIP-1-8-1 to `>`"), which legitimately
tightened `dosage.dfy`'s postcondition and re-verified it for real
against the Dafny binary — but never re-ran `generate_artifacts.py`'s
stage 7 (provenance index) afterward, despite an otherwise-thorough
"full documentation set updated to match" sweep in that same commit.
The underlying spec/capture content was never in question, only the
index's own bookkeeping. Fixed by running the sanctioned regeneration
entrypoint (`examples/dosage_calculator/generate_artifacts.py`) rather
than hand-editing the index — all 7 stages passed. This also picked up
the metadata schema files' real content changes from the same-day
Phase 3 work (id pattern widened, `crosshair_bounds` made optional,
2026-07-11), which had gone stale in the index the identical way. The
five traceability-matrix variants regenerate with a refreshed
`generated_utc` as an unavoidable side effect (their content is part of
what the index hashes), so committed alongside the index rather than
reverted, which would just reintroduce the same staleness immediately.
`KNOWN_LIMITATIONS.md`'s Phase 3 entry (which had named this bug
"deliberately NOT touched") amended with a "Fixed, 2026-07-11" addendum
rather than rewritten, preserving the original as history.

**Fix 2 — `examples/drug_interaction_checker/README.md` didn't exist.**
Unlike `dosage_calculator/README.md` and `renal_adjustment/README.md`,
this example had no audit-trail record — flagged as a "confirm" item in
the original Phase 3 scoping plan and never resolved either way. Built
mirroring the other two examples' exact structure (source documents →
requirement-to-source mapping → interpretive-call caveats → dated
amendments in chronological order → fixture/capture formats → open
questions), sourced entirely from this example's own already-committed
record — `PHASE1_PLAN.md`, `GATE_1C_AUDIT.md`,
`nl_confirmation_drug_interaction_checker_dfy.md`,
`sources/sps-doac-interactions-2024.md`, `mutation_report_ddi.json`,
and `KNOWN_LIMITATIONS.md`'s "Phase E Gate C1"–"Phase E Gate C6
sign-off" sections — not invented. Every quoted number
(`1 verified, 0 errors`; the STP suite's `22 verified, 0 errors`
against 11 real lemmas; resource costs 113,039 pre-fix / 358,399
post-fix; the mutation run's 962/564/389/7/2 breakdown) cross-checked
directly against the real committed capture files
(`raw_dafny_output_ddi*.txt`, `run_manifest_mutation_ddi.json`) before
being written, not copied from a secondary source without verification.

Two research agents (`Explore`, both foreground) gathered the code/spec
and documentation-history facts for `REQ-RENAL-8` scoping immediately
before this redirect — that plan-mode session was interrupted mid-
research by this more concrete pair of instructions and is not
reflected here; `REQ-RENAL-8`'s classification-flag provenance remains
open, unstarted.

`python -m pytest tests/ -q`: 205 passed throughout both fixes, no
regressions.

## 2026-07-11 — Documentation audit: fixed real disparities across all main docs, none merely re-dated

Direct instruction: "ensure all of the main docs are up to date and no
disparity whatsoever. running system should be clean. please check and
fix where necessary" — a dedicated audit pass, not tied to any new
feature, following directly on the Phase 3 work merged in PR #32
(previous entry below). Cross-checked every main doc (`README.md`,
`HANDOFF.md`, `OPERATIONS_MANUAL.md`, `SYSTEM_BLUEPRINT.md`,
`KNOWN_LIMITATIONS.md`, `REVIEW_PROTOCOL.md`, plus
`examples/dosage_calculator/RECONCILIATION.md`) against the actual repo
state — test counts recomputed via `pytest --collect-only`, gate
statuses cross-checked against `KNOWN_LIMITATIONS.md`'s own gate ledger,
schema `required` fields read directly from the JSON, GAP-row claims
checked against the real committed matrix JSON — rather than trusting
any doc's own prose.

Real findings, all fixed (commit `41be18b`, PR #33, merged
`d7123c2`):

- **Arithmetic bug in three places** (`HANDOFF.md`, `KNOWN_LIMITATIONS.md`
  twice): "9 new tests" next to a correct "205 total, up from 190" —
  9 (`renal_adjustment`) + 6 (`drug_interaction_checker`) is 15, not 9;
  the adjacent correct total is what exposed the undercount.
- **`README.md`**: test count said 190 (stale); `renal_adjustment`'s
  "Status at a glance" bullet still said "nearly complete" pending a
  Gate C6 sign-off that was actually confirmed and closed 2026-07-11
  (same day, earlier session).
- **`REVIEW_PROTOCOL.md`**: "GAP rows ... currently none" — stale;
  Phase 3 introduced the first 7 real GAP rows across the two new
  matrices. Its reconciliation-asymmetries pointer also still cited
  binding authorship as open, but that was resolved 2026-07-05 (Gate 4,
  option 3, cross-checked) — five weeks stale, unrelated to this
  session's own Phase 3 work, just never caught before.
- **`examples/dosage_calculator/RECONCILIATION.md`**: the same binding-
  authorship finding, independently still saying "OPEN, deferred to
  Phase B" in its own source location — fixed with a pointer to Gate 4's
  actual resolution and mechanism.
- **`OPERATIONS_MANUAL.md`**: component map was missing
  `drug_interaction_checker` entirely, marked `renal_adjustment` "in
  progress", and cited a 154-test count (several sessions stale — this
  doc had evidently not been touched by any of the recent example-adding
  sessions' documentation ripples). Command reference had no example of
  the now-common Dafny-only invocation (omitting `--manifest`/
  `--concrete`, both optional since the same-day Phase 3 work).
- **`SYSTEM_BLUEPRINT.md`**: top "Last updated" header still led with
  the prior Gate C6 sign-off entry, not the later same-day Phase 3 work
  (both dated 2026-07-11, so the mechanical staleness test couldn't
  catch it — same date, wrong content); "Phase C (in progress)"
  contradicted its own section content showing all six Gate C1–C6 steps
  built and signed off; the Phase D/E status-block headers were dated to
  their last narrative update despite being extended since;
  `drug_interaction_checker`'s Phase 3 bullet was ordered before its own
  Gate C6 bullet despite structurally depending on it being done first.

Two background audit agents (`general-purpose`, for `OPERATIONS_MANUAL.md`
and `SYSTEM_BLUEPRINT.md`) were launched to parallelize the largest two
files' review; both hit a session rate limit (`429`, "session limit ·
resets 6pm UTC") and failed before producing output. Completed that
portion of the audit directly instead, via targeted `grep` sweeps for
known stale-content patterns (old test-count numbers, "in progress"/
"nearly complete"/"currently none" phrasing, `--manifest`/`--concrete`
"required" claims) rather than a full agent-mediated read — narrower
than originally planned, but every finding reported above was still
independently verified against the real repo state, not guessed.

`python -m pytest tests/ -q` — 205 passed throughout, no regressions (a
docs-only change, but `tests/test_docs_current_with_devlog.py`'s
mechanical staleness check is itself part of the suite and passed on
every run). PR #33 merged same day; both CI checks (pytest, PayloadGuard
scan) green before merge, per direct instruction ("merge it once CI's
green").

## 2026-07-11 — Phase 3 built for renal_adjustment and drug_interaction_checker: three real gaps found and fixed in shared code

Direct instruction: "go ahead and scope out Phase 3," followed by "go
ahead and build it" after plan approval, then "proceed but ensure
regression is possible and verify anything with me as you go" after an
overreach mid-implementation was caught by the auto-mode classifier (I'd
started editing shared code before the user had actually said "build
it," not just approved the scoping plan - a real distinction this
session's own established discipline holds to, that I initially missed
myself).

Entered plan mode, ran three parallel Explore agents (dosage_calculator's
real Phase 3 template, read directly rather than assumed generic;
renal_adjustment's and drug_interaction_checker's real REQ-ID inventories
and capture files), and wrote a concrete replacement for the old,
necessarily-speculative Phase 3 sketch in the standing infrastructure
plan (`/root/.claude/plans/stateless-weaving-firefly.md` - the
speculative section preserved below a clear "superseded" marker, not
deleted).

**Built `drug_interaction_checker`'s packaging first** (the simpler
shape: one `dafny_captures_index.json` entry reused by four requirement
rows) - the fastest path to hitting the plan's own named risk: neither
new example has any crosshair or concrete_test evidence at all (no
companion Python/CrossHair implementation exists for either), and
`dosage_calculator`'s existing pipeline had never been pointed at a
metadata file like that.

**Three real, generally-applicable gaps found running the real CLI, not
assumed from reading the code:**

1. `evidence/cli.py`'s `--manifest`/`--concrete` were hard `required=True`,
   and reading further down the call chain, `derive_bounds_block()`
   (`evidence/render/matrix_variants.py`) unconditionally required
   `manifest["effective_bounds"]`, `_header()`/`build_matrix()` both
   unconditionally indexed `metadata["toolchain"]["crosshair_bounds"]`,
   and `symbolic_binding_conflicts()` (`evidence/conflict.py`)
   unconditionally indexed `manifest["target"]` - five separate hard
   dependencies on a crosshair run existing. Fixed by treating
   `manifest=None` (an omitted `--manifest`) as a legitimate "no
   crosshair evidence declared" state throughout, mirroring
   `dafny_store`'s own already-established `None` convention exactly
   rather than inventing a new one - and, critically, never fabricating
   fake bounds data to paper over the gap, since that would have falsely
   implied a crosshair search happened. `--concrete` defaults to a real,
   honest `{"cases": []}` instead (an empty test list is a genuine
   state, not a fabrication).
2. The metadata schema's `toolchain.crosshair_bounds` was unconditionally
   `required` in all three schema files - relaxed to optional,
   backward-compatible (dosage_calculator's own metadata still declares
   it, so nothing changes for it).
3. The schema's `id` pattern (`^REQ-[A-Z0-9-]+$`) rejected
   `REQ-RENAL-1a` outright - the exact same lowercase-suffix gap already
   fixed once this session in `dafny_nl_summary.py`'s `_REQ_ID_RE`
   (2026-07-08), found completely independently in a second, unrelated
   module that happened to make the identical wrong assumption. Fixed
   the same way.

**A fourth, independent bug caught while reading the code closely for
the fix above, not required by either new example but real**:
`symbolic_binding_conflicts()` never had the `.dfy`-extension skip
`_declared_concrete_bindings()` already carried - a real gap for any
future *mixed* crosshair+dafny example, which would have false-flagged
a dafny requirement's implementation against the crosshair manifest's
Python target file. Fixed, mirroring the sibling function exactly.

**Every change reverified against zero regression, not assumed safe.**
`dosage_calculator`'s real, committed artifacts regenerated
(`generate_artifacts.py`) and diffed content-for-content (timestamp
excluded) before and after each shared-code change - byte-for-byte
identical every time, across all five variants. A pre-existing, wholly
unrelated finding surfaced during this regression testing and
deliberately not touched: `artifact_index.json`'s committed hash for
`dosage.dfy`/`run_manifest_dafny.json` doesn't match their current
on-disk content, reproducible even with every change here fully
reverted - a genuine, pre-existing provenance-index staleness bug,
named here rather than silently fixed in passing or ignored.

**A real design question surfaced mid-build, checked rather than
guessed at**: `intended_method: DECLARED` can structurally never achieve
`intent_ok: true` in this architecture (no evidence-binding path ever
produces a realized `DECLARED` strength - confirmed by reading
`derive_intent()` directly), so it always renders identical to
`intended_method: PROVEN` for a zero-evidence row, differing only in the
note text. Surfaced this to the user (the `AskUserQuestion` call itself
failed technically, not rejected) and proceeded on the reasoned
recommendation: `PROVEN` for genuine future-formalization candidates
(REQ-DDI-5/6, REQ-RENAL-3/4/6/7 - all named as real Dafny candidates in
their own `PHASE1_PLAN.md`), `DECLARED` reserved for REQ-RENAL-8
specifically, a permanent trust-boundary/process decision nobody ever
intends to Dafny-prove - two genuinely different categories of gap, not
the same treatment applied uniformly.

**`renal_adjustment`'s real packaging**: `metadata.a.yaml` (9
requirement rows), `dafny_captures_index.json` (7 entries, all seven
functions sharing the one real capture). REQ-RENAL-1/1a/2/5 bind real
dafny evidence; `AssessRenalFunction` dual-cited to both REQ-RENAL-1 and
REQ-RENAL-2, mirroring its own real `.dfy`-file inline citation exactly;
the unnumbered CrCl-computation functions attached under REQ-RENAL-2
rather than given an invented ID, per the plan's own recommendation.
REQ-RENAL-3/4/6/7 and REQ-RENAL-8 render as the two distinct GAP
categories above.

**`drug_interaction_checker`'s real packaging**: `metadata.a.yaml` (6
requirement rows), `dafny_captures_index.json` (1 entry). REQ-DDI-1/2/3/4
all share the exact same capture entry - confirmed working end to end
by actually running the real pipeline against it, not assumed from the
schema permitting it. REQ-DDI-5/6 render as honest GAP rows.

Both matrices pass `assert_no_realized_proven` (R3), re-checked directly
in each example's own test file. `evidence/render/matrix_variants.py::_md_head()`
also improved in the same pass: a `None` bounds block now renders as an
explicit "N/A (no crosshair evidence in this metadata)" rather than a
bare "None" a reader could misread as a data gap.

9 new tests: `tests/test_drug_interaction_checker_matrix.py` (6),
`tests/test_renal_adjustment_matrix.py` (9). Full documentation ripple:
`SYSTEM_BLUEPRINT.md` (Section 3's data-flow diagram, Section 5's
evidence inventory, both component-map listings - all previously
`dosage_calculator`-only), `KNOWN_LIMITATIONS.md` (new "Phase 3 —
evidence packaging" section), `HANDOFF.md`.

**Both examples that reached Phase 2 now also have Phase 3 built** -
`dosage_calculator` (complete, three evidence types), `renal_adjustment`
and `drug_interaction_checker` (Dafny-only, variant A) all now have a
real, committed traceability matrix.

205 tests pass (up from 190).

## 2026-07-11 — Gate C6 sign-off confirmed for renal_adjustment: six checkpoints verified against raw KDIGO/MHRA sources, one citation flagged as unverifiable

Direct instruction: "go ahead and build gate C6 for renal_adjustment."
Checked the current state before doing anything: Gate C6's mechanical
build already existed (all seven functions summarized, two tooling gaps
found and fixed 2026-07-08, two amendments 2026-07-09), just with its
Decision section still reading "Pending" since then. Rather than
silently redo already-correct work or silently do nothing, asked
directly what was wanted - confirmed: give the actual sign-off.

**Re-verified for drift before treating the existing artifact as still
accurate.** `summarize_method()` re-run fresh for all seven functions,
diff-checked against `nl_confirmation_renal_adjustment_dfy.md` -
byte-identical, confirming the multi-line-clause extension built the
same day for `drug_interaction_checker`'s own Gate C6 didn't silently
change output for `renal_adjustment`'s single-line clauses. `dafny
verify renal_adjustment.dfy` and `dafny verify
renal_adjustment_stp_suite.dfy` both re-run live: `7 verified, 0
errors` and `52 verified, 0 errors`, matching committed captures
exactly. (Confirmed 44 real lemmas in the STP suite via `--progress
Symbol`, correctly already reported as "44 lemmas" separately from "52
verified" in the existing docs - no repeat of the same conflation bug
fixed for `drug_interaction_checker`'s STP suite the day before.)

**The actual review checked six claims against real sources, not the
confidence they were presented with.** All independently re-verified
against `sources/kdigo-2024-gfr-staging.md` and
`sources/mhra-renal-formula-selection-2019.md` directly:
`RoundHalfUp`'s tie-break framing (KDIGO states only "nearest whole
number," no tie-break rule - confirmed at source line 51/137);
`GStage`'s six boundaries (G1 >=90 through G5 <15 - confirmed exact at
source line 31); `SelectFormula`'s BMI thresholds (strict inequality,
<18/>40 - confirmed verbatim at source line 31/33, all five conditions
present); the `ComposedCeiling`/`AssessRenalFunction` Gate C4 pinning
fixes (confirmed via the live STP re-run plus a direct logical
walkthrough); the eGFR/CrCl split's forced asymmetry (both
Pow-expressiveness probes re-run live, still match the established
2026-07-10 finding exactly); and the document's own open question about
"for Cockcroft-Gault only" scoping (confirmed the phrase does exactly
what it claims - closes the branch where the maths is expressible,
leaves the other explicitly open).

**One citation flagged, not silently absorbed.** A supporting claim
that "Sheffield and BSW" clinical-calculator sources corroborate the
88.4 conversion factor could not be verified - no such source exists
anywhere in this repository's `sources/` directory. Not recorded as
confirmed. The underlying claim it was attached to didn't depend on it
and was already independently established via a direct MHRA re-fetch in
an earlier session (2026-07-09). Same discipline that caught a real
mislabeling in this session's own `drug_interaction_checker` Gate C6
sign-off the day before - an external claim gets checked against a real
primary source before being trusted, regardless of how confidently or
thoroughly it's presented.

Gate C6's Decision section recorded, closing the gate. Full
documentation ripple: `SYSTEM_BLUEPRINT.md`, `KNOWN_LIMITATIONS.md` (new
"Phase D Gate C6 sign-off" section), `HANDOFF.md`.

**`renal_adjustment` now has all six Gate C1-C6 pipeline steps both
built and confirmed** - matching `drug_interaction_checker`'s status.
Both of this repo's Dafny-based worked examples are now fully signed
off; only the named, deliberately unbuilt requirements
(`REQ-RENAL-3`/`4`/`6`/`7`/`8`) remain on this example.

No `.dfy` file or code changed - docs-only. 190 tests unchanged.

## 2026-07-10 — Gate C6 sign-off confirmed for drug_interaction_checker: the review itself caught a real doc-accuracy bug

Same day, later still. Steven's actual Gate C6 review of
`nl_confirmation_drug_interaction_checker_dfy.md` - not a rubber stamp,
per this repo's standing rule that a sign-off document is not closed
until an actual decision is recorded and confirmed against real
evidence, not just presented.

**A real bug found, in a place worth being precise about.** Steven
flagged that item 1 of the sign-off document's "worth Steven's
attention" section, and the fix needed, appeared to conflate two
distinct exclusion reasons the source itself distinguishes. Investigated
before accepting the premise, per this repo's own standing discipline
about not trusting an external claim (or, here, one framed as coming
from a separate review) without checking it against the real committed
artifacts first - the same discipline that's caught fabricated
citations in outside documents before.

The investigation found the bug was real, but narrower than first
framed: `drug_interaction_checker.dfy`'s own precondition comment
already correctly says the `(Apixaban, {Rifampicin, Carbamazepine,
Phenytoin, Phenobarbital})` exclusion is about "clinical indication
(REQ-DDI-5, not built in v1)" - not a source gap. The STP suite's own
"real source gap" comment is also already correctly scoped, reserved
for a different cell entirely (`ApixabanDronedarone`, where the source
never mentions apixaban at all). Neither the `.dfy` spec nor the STP
suite needed any change. The actual bug was narrower: item 1 of the
sign-off document I generated during Gate C6's build had mislabeled the
precondition's exclusion as apixaban's "real source gap," conflating it
with the genuinely-silent Dronedarone case - both happen to justify v1
exclusion, but for materially different reasons, and the source itself
draws the distinction explicitly.

Confirmed verbatim against `sources/sps-doac-interactions-2024.md`:
lines 80-84 (rifampicin) and 135-136 (carbamazepine/phenytoin/
phenobarbital) both state apixaban gets "use apixaban with caution" for
two named indications specifically (AF stroke prevention; recurrent
DVT/PE prevention) - an explicit indication-dependent branch, which the
source's own text (line 84, line 134) flags as sharing "the same
indication-dependent structure" across both rows. This is categorically
different from line 53's "Apixaban is never mentioned in this section
at all - a real gap in the source" for dronedarone. Fixed in place in
the sign-off document, left visible as a correction rather than
silently rewritten.

**Every other item in the sign-off was independently re-verified
against the real source, not accepted on the strength of having been
written carefully the first time:**
- `CautionLowRelevance` (verapamil+rivaroxaban, verapamil+apixaban,
  fluconazole+rivaroxaban) - confirmed verbatim against source lines
  57-58 ("unlikely to be clinically relevant") and 104-111 ("not
  considered to be clinically relevant").
- `Contraindicated` (dabigatran+itraconazole/ketoconazole) - confirmed
  against source lines 113-121 ("contraindicated with dabigatran").
- Whole-table validation (no per-clause `REQ-ID` citations) - confirmed
  correct against the source's own explicit scope statement (line 26:
  "not comprehensive for all potential interactions"), which is exactly
  what makes per-clause citation false precision for this spec.

**A programmatic cross-reference, not just a careful re-read.** Wrote a
short script to check `CheckInteraction`'s 60 `ensures` clauses against
the STP suite's 11 lemmas directly: every one of the 7 ACCEPT lemmas'
claimed outcome matches exactly one real `ensures` clause; every one of
the 4 REJECT lemmas' claimed (wrong) outcome is confirmed genuinely
absent from the real `ensures` clause for that cell. All three artifacts
(spec, NL summary, STP suite) mutually consistent; no drift found.

**Gate C6's Decision section recorded, closing the gate for this
example** - all four numbered sign-off items confirmed, the item-1
correction noted explicitly rather than silently fixed. Full
documentation ripple: `SYSTEM_BLUEPRINT.md`, `KNOWN_LIMITATIONS.md`
(new "Phase E Gate C6 sign-off" section), `HANDOFF.md`, `PHASE1_PLAN.md`.

**All six Gate C1-C6 pipeline steps are now both built and confirmed**
for `drug_interaction_checker` - the only remaining work on this
example is the explicitly out-of-scope v2 items, `REQ-DDI-5`/`REQ-DDI-6`.

No `.dfy` file or code changed - docs-only, 190 tests unchanged.

## 2026-07-10 — Gate C6 for drug_interaction_checker: genuinely extended the shared NL-summary generator, a different call than renal_adjustment's own equivalent gap

Same day, later still. Direct instruction: "buiod out c6 please." First
attempt at `evidence.dafny_nl_summary.summarize_method("CheckInteraction")`
refused outright: `CheckInteraction`'s one `requires` clause spans three
physical lines -

```dafny
requires !(doac == Apixaban &&
           (agent == Rifampicin || agent == Carbamazepine ||
            agent == Phenytoin || agent == Phenobarbital))
```

- the first genuinely multi-line clause this repo has pointed the
summary generator at. Every clause in `dosage.dfy` was one line;
`renal_adjustment.dfy` hit an equivalent gap for two `ensures` clauses
in `AssessRenalFunctionFromInputs`, and that time the fix was to
reformat them to single-line rather than extend the tool - recorded
explicitly at the time as "a formatting choice that was mine, not a
genuine spec need," not a tool bug.

Considered doing the same thing here (briefly edited the `requires`
clause down to one line, verified the diff was clean, then reverted it)
before deciding against it: unlike `renal_adjustment.dfy` at the point
its equivalent gap was found, this spec already had a committed Gate C1
capture, an 11-lemma Gate C4 STP suite, and a 962-mutant Gate C5 mutation
report all captured against the file exactly as currently formatted.
Reformatting the `requires` clause - even though Dafny doesn't care
about line breaks and the semantics are byte-identical either way -
would have meant re-running and re-committing all three of those
artifacts to keep them honestly bound to the source they claim to
verify, for a change with zero semantic content. So the call went the
other way this time: extend the tool, not reformat the spec, for a
concrete, checkable reason (downstream artifact cost), not
inconsistency with the earlier decision.

**Fixed** in `evidence/dafny_nl_summary.py`: `_extract_annotated_clauses`
now accumulates a clause across multiple physical lines. A continuation
line is any non-blank line that isn't a standalone `//`-comment line and
doesn't itself open a new `requires`/`ensures`/`modifies`/`reads`/
`decreases` clause; a standalone comment line (or blank line) always
ends the clause currently being accumulated. This matters concretely
here: a 17-line block comment sits between `CheckInteraction`'s
`requires` clause and its first `ensures` clause (explaining the Gate C4
finding that led to the 60 pinning clauses below it) - without the
"standalone comment ends accumulation" rule, that whole block would have
been swept into the `requires` clause's own text and searched for a
`// REQ-ID` citation that was never meant for it.

The original single-line-only regex (`_CLAUSE_LINE_RE`) was kept, not
deleted - `evidence/dafny_mutate.py::_locate_clause_sites` imports it by
name for a different, byte-precise need (absolute offsets of a mutation
site within one physical line), which this extension didn't need to
touch. This is also why Gate C5's own mutation report could already
mutate the `doac == Apixaban` comparison inside this same multi-line
`requires` clause successfully, even before this fix existed - it sits
on the clause's first physical line, and the two modules had different,
independently correct notions of "clause" for their different purposes.

The safety net itself is unchanged in spirit: `summarize_method` still
cross-checks its extraction against `dafny_spec_lint`'s canonical
extractor and refuses (`SystemExit`) on any mismatch. A comment sitting
on its own line *inside* a multi-line boolean expression (as opposed to
between two clauses) still correctly refuses - the "standalone comment
ends accumulation" rule orphans the continuation lines after it,
producing a truncated clause that no longer matches canonical
extraction, genuinely ambiguous rather than something to guess at.
Confirmed with a new regression test.

Verified end-to-end against the real, committed spec: all 60 `ensures`
clauses and the one multi-line `requires` clause reconstruct
byte-for-byte correctly - cross-checked programmatically against
`summarize_method`'s own output before being embedded in the sign-off
document, not just visually inspected.

**A real, notable fact this summary surfaces, not a defect:** none of
`CheckInteraction`'s 60 `ensures` clauses carry an inline `// REQ-DDI-*`
citation - every postcondition in the generated summary reads `*(no
requirement cited)*`. Unlike `dosage.dfy`'s and `renal_adjustment.dfy`'s
per-clause citation style, this spec is validated against
`sources/sps-doac-interactions-2024.md` as a whole lookup table (Gate
1a/1c), not REQ-ID by REQ-ID - accurate, not a gap, but flagged
explicitly in the sign-off document for Steven to confirm is the right
traceability model for this shape of spec.

3 new/changed tests in `tests/test_dafny_nl_summary.py`: one obsolete
blanket single-line-only refusal test rewritten in place
(`test_multiline_clause_is_summarized_correctly_not_refused`, preserving
the original regression-protection intent - a dropped or truncated
continuation still fails this test, it just no longer does so via a
blanket refusal), one new test for the still-genuinely-refusing
mid-clause-comment case
(`test_standalone_comment_inside_a_multiline_clause_still_refuses`), and
one new end-to-end test against the real committed spec
(`test_real_ddi_spec_multiline_requires_clause_summarizes_correctly`).

Gate C6's actual deliverable - the recorded human decision, not the
mechanical summary - is
`examples/drug_interaction_checker/nl_confirmation_drug_interaction_checker_dfy.md`.
Its Decision section is **pending Steven's review, not yet confirmed**,
same discipline as `renal_adjustment`'s own still-open Gate C6 sign-off.
Full documentation ripple: `SYSTEM_BLUEPRINT.md`, `KNOWN_LIMITATIONS.md`
("Phase E Gate C6" section), `HANDOFF.md`, `PHASE1_PLAN.md`.

**All six Gate C1-C6 pipeline steps have now been built or confirmed for
this example** - the third worked example this repo has carried all the
way through. What remains: Steven's actual Gate C6 sign-off decision,
and the two explicitly out-of-scope v2 items (`REQ-DDI-5`/`REQ-DDI-6`).

190 tests pass (up from 188).

## 2026-07-10 — Gate C5 for drug_interaction_checker: found and fixed a real crash bug in Gate C3's own code, then 7 real survivors

Same day, later still. Direct instruction: "c5 please." Mirrored
`run_mutation_suite_renal.py`'s exact capture/classification discipline
in a new `run_mutation_suite_ddi.py` against `CheckInteraction`'s one
`requires` clause and 60 `ensures` clauses, via
`evidence/dafny_mutate.py`'s ROR/LOR/AOR/LVR/COI generators. AOR and LVR
both confirmed contributing zero mutants - checked directly (the
generators return `[]`), not assumed: there is no arithmetic operator
and no numeric literal anywhere in `CheckInteraction`, a pure datatype
pattern match.

**The first run crashed, not a Dafny finding but a real bug in this
repo's own tooling.** A ROR mutant introduced `<=` between two `DOAC`
datatype operands (from the `requires` clause's `doac == Apixaban`
comparison), and `evidence/dafny_spec_lint.py`'s Z3 precondition
translator raised a raw Python `TypeError`
(`'<=' not supported between instances of 'DatatypeRef' and
'DatatypeRef'`) - Z3's Python bindings simply don't overload ordering
operators for `DatatypeRef`, unlike `==`/`!=` which work universally via
generic equality. A real, generally-applicable gap in a shared module:
any future spec with a datatype comparison, mutated by ROR into an
ordering operator, would hit the same crash. Fixed in `_apply_cmp`
(changed from a `@staticmethod` to an instance method) with a
`z3.is_arith(a) and z3.is_arith(b)` guard before applying
`LE`/`GE`/`LT`/`GT`, raising a clean `SystemExit` instead - matching
every other unsupported-construct refusal already in that module.
`run_mutation_suite_ddi.py` was updated to catch this `SystemExit`
around its `requires`-clause pre-filter call and still fall through to
real Dafny verification for that mutant. One new regression test,
`test_ordering_operator_on_enum_datatype_refuses_cleanly_not_a_crash`,
added to `tests/test_dafny_spec_lint.py`. Shipped this fix as its own
PR (#26), independent of the full mutation report, since it stood on
its own and there was no reason to block it behind a still-running
21-minute background job.

**Final real run (re-run clean after the fix): 962 mutants - 564
killed, 389 filtered_static, 7 survived, 2 unclassifiable.** The 2
unclassifiable are both the `<=`/`>=` case above - Dafny genuinely
refuses these with a real type error ("arguments to `<=` must be of a
numeric type... instead got `DOAC` and `DOAC`"), a materially different
failure mode from `renal_adjustment`'s own unclassifiable case (a parser
ambiguity, not a type error).

**A wrong prediction, corrected in place rather than silently rewritten.**
`<` and `>` between two datatype values, unlike `<=`/`>=`, DO type-check
in Dafny (a structural "rank" ordering used for termination metrics). An
earlier draft of this gate's own runner-script comments predicted every
such mutant would be "always killed," assuming the relation was
unconditionally false for a flat, non-recursive enum. Wrong: two direct
Dafny probes showed neither `Apixaban < Dabigatran` nor
`!(d < Apixaban)` is provable as a bare claim - for a flat enum with no
recursive constructor argument, Z3 has no axiom pinning the relation
down at all, genuinely unconstrained rather than false. The real run
then showed exactly 3 such mutants survive. Corrected in place in
`run_mutation_suite_ddi.py`'s header comment, left visible with an
explicit note that the guess was wrong before the real run proved it,
rather than rewritten as if the right answer had been known from the
start.

**All 7 survivors explained, both falling into structural categories
`renal_adjustment`'s own Gate C5 already established - no new class of
finding:**

- 4 survivors mutate the one `requires` clause's `doac == Apixaban`
  comparison (`==`->`!=`, `==`->`<`, `==`->`>`, one LOR `&&`->`||`).
  None of the 60 `ensures` clauses makes any claim about the region this
  clause excludes, so no proof's provability depends on its exact shape
  - "requires-clause weakenings not load-bearing for the specific
  ensures clauses currently proven," `renal_adjustment`'s own category.
- 3 survivors mutate one ensures clause's `doac == Dabigatran`
  antecedent (`==`->`!=`, `==`->`<`, `==`->`>`). `Caution`/`BleedingRisk`
  is already separately, unconditionally guaranteed for
  Apixaban/Edoxaban/Rivaroxaban+SSRIOrSNRI by three sibling ensures
  clauses, confirmed directly against the real spec text - so the
  consequent holds regardless of what the mutated antecedent matches.
  "A structural blind spot against guard-style `==>` clauses whose
  consequent happens to be broadly true," `renal_adjustment`'s own
  largest survivor category (39 of 51).

4 new tests, `tests/test_drug_interaction_checker_mutation_report.py`,
pinning the exact 962-mutant outcome-count distribution and directly
asserting both survivor categories against the real spec text, not just
the report's own labels - mirroring `tests/test_renal_mutation_report.py`'s
discipline. Full documentation ripple: `SYSTEM_BLUEPRINT.md`,
`KNOWN_LIMITATIONS.md` ("Phase E Gate C5" section, plus a follow-up note
on the existing "Phase E Gate C3" row), `HANDOFF.md`, `PHASE1_PLAN.md`.

188 tests pass (up from 184 - 1 from the standalone crash-fix PR, 4 for
this gate's mutation report).

## 2026-07-10 — Gate C2 for drug_interaction_checker: confirmed generalization, no new gap

Same day, later still. Direct instruction: "c2 please." Unlike Gates
C3 and C4, this one didn't find a bug or require a fix - its value is
confirming an already-built mechanism actually works on a third,
independently-authored spec, not discovering it doesn't.

`evidence/render/matrix_variants.py::dafny_record()` (the only place in
the codebase that can produce a dafny-method PROVEN record) and
`assert_no_realized_proven` (ruling R3) were built 2026-07-07 and
tested thoroughly - but only ever against `dosage_calculator`'s real
captures. `renal_adjustment` never exercised this path at all: its
captures were never wired into a `metadata.yaml`, so `dafny_record()`
was never called against them.

Ran it for real against `drug_interaction_checker`'s actual committed
capture, not a synthetic fixture: `dafny_record(capture,
"drug_interaction_checker.dfy::CheckInteraction")` produced a genuine
`{"method": "dafny", "strength": "PROVEN", "verifier_completion_status":
"completed"}` record - exercising Gate C3's Z3 precondition check (now
able to model the datatype comparison, thanks to the same-day
extension) and Gate C1's false-zero guard for real, both against a spec
neither was originally written for. `assert_no_realized_proven`
accepted the record cleanly.

Then two negative-case checks, not just the positive one -
`dafny_record()`'s own docstring makes an explicit claim ("R3 does not
trust this function's own diligence"), worth actually testing rather
than assuming it holds because it holds for `dosage_calculator`'s
fixtures. A hand-tampered copy of the same real record with `method =
"crosshair"` and another with `verifier_completion_status =
"incomplete"` were both independently refused by
`assert_no_realized_proven`, with the same assertion messages
`test_proven_exclusivity.py`'s generic fixtures already established -
now confirmed against this example's own real record shape.

4 new tests, `tests/test_drug_interaction_checker_dafny_wiring.py` -
deliberately narrower than `test_dafny_wiring.py` (which tests the full
`metadata.yaml`/`build_matrix()`/CLI/fact-equality pipeline for
`dosage_calculator`): this example has no traceability matrix yet
(Phase 2, not Phase 3), so there's no fuller pipeline to test against,
only the binder itself. A real, honest scope boundary, not an
oversight. Full documentation ripple: `SYSTEM_BLUEPRINT.md`,
`KNOWN_LIMITATIONS.md` ("Phase E Gate C2" section), `HANDOFF.md`,
`PHASE1_PLAN.md`.

183 tests pass (up from 179 - 4 new for this gate's binder confirmation).

## 2026-07-10 — Gate C3 for drug_interaction_checker: required extending shared tooling, not just running it

Same day, later still. Direct instruction: "go ahead and build gate
C3." Applied `evidence/dafny_spec_lint.py`'s vector 1
(`check_precondition_satisfiability`) to `CheckInteraction` and it
genuinely refused: `requires !(doac == Apixaban && ...)` compares
`doac`/`agent` directly against named datatype constructors, and the
translator's `_TYPE_MAP` only ever modeled `real`/`int`/`nat`/`bool` -
confirmed empirically before touching anything (`SystemExit:
unsupported Dafny parameter type 'DOAC'`). This is the exact risk named
at the very start of scoping this domain, now actually hit: a
materially different, harder gap than `renal_adjustment`'s own Gate C3
finding (a datatype-typed parameter simply unreferenced by its
precondition - narrowing to "only model referenced parameters" was
enough there; here the referenced parameters genuinely need a Z3
representation that never existed).

**Fixed by extending the shared module for real**, not routing around
it. `DOAC`, `Agent`, `Outcome`, and `RiskDirection` are all simple Dafny
datatypes (every constructor zero-argument) - representable natively as
a Z3 `EnumSort`. New `_parse_enum_datatypes` finds every such
declaration in a source file (handling the multi-line form `Agent`'s
own declaration actually uses), and `build_symbol_table` now builds one
`EnumSort` per referenced enum type, adding each constructor name as a
resolvable symbol the same way `true`/`false` already resolve - no
parser changes needed. `InteractionResult` (one parameterized
constructor) is correctly excluded, still refused exactly as before -
`EnumSort` has no way to represent fields.

**A second, independent, more general bug caught while building the
regression suite, not by inspection.** Two of the new test fixtures
both happened to declare `datatype Formula = A | B` and running them in
the same pytest session raised `z3.z3types.Z3Exception: enumeration
sort name is already declared` - Z3 registers `EnumSort` names globally
per process context, not per call. A real footgun for any future caller
of `build_symbol_table`, not specific to this spec. Fixed with a
monotonic per-call counter appended to the registered sort's internal
Z3 name.

**Verified against the real, committed spec.** `CheckInteraction`'s
precondition: `sat` (`agent = Naproxen, doac = Dabigatran` is a real Z3
model), confirming Gate C1's `1 verified, 0 errors` isn't vacuous.
Vector 2 flags all 60 pinning `ensures` clauses, exactly as many as
exist - the same "exhaustive, mutually-exclusive dispatch" pattern
already established for `renal_adjustment`'s `GStage`/`SelectFormula`,
independently backed here by Gate C4's real STP proofs rather than just
asserted benign.

5 new tests in `tests/test_dafny_spec_lint.py` for the extension itself
(a real-spec true-positive, an unsat case confirming EnumSort
comparisons can still correctly fail, a multi-line declaration parse, a
parameterized-constructor exclusion); one pre-existing test rewritten
in place rather than deleted -
`test_referenced_unsupported_type_parameter_still_refuses`'s original
fixture became a *supported* case by this extension, so its datatype
was changed to a parameterized one, preserving the original regression
intent. `tests/test_drug_interaction_checker_spec_lint.py` (new) is the
real-spec application, mirroring `test_renal_adjustment_spec_lint.py`'s
structure exactly. Full documentation ripple: `SYSTEM_BLUEPRINT.md`
(the `evidence/dafny_spec_lint.py` component-map entry, Section 8),
`KNOWN_LIMITATIONS.md` ("Phase E Gate C3" section, plus a note on the
original Phase C Gate C3 entry pointing at the extension),
`HANDOFF.md`, `PHASE1_PLAN.md`.

179 tests pass (up from 171 before this session's Gate C1/C3/C4 work -
5 new for the dafny_spec_lint.py extension, 3 new for the real-spec
application; the one rewritten test doesn't change the count).

## 2026-07-10 — Gate C4 for drug_interaction_checker: the Gate C1 fix was itself only a stopgap

Same day, later still. Direct instruction: "go ahead and build gate
C4." Applied IronSpec methodology to `CheckInteraction`, the same way
Gate C4 was applied to `renal_adjustment.dfy`'s `ComposedCeiling` and
`AssessRenalFunction` — but this time the finding was bigger and came
from a hand-derived prediction that turned out to be exactly right.

**Prediction, before writing anything real:** Gate C1's `ensures`
clauses only covered 3 of `CheckInteraction`'s 63 match arms (the
`NotCovered`/`Contraindicated`/`Digoxin` pins added to fix the earlier
"0 verified, 0 errors" false-clean result). A genuine IronSpec ACCEPT
lemma — restating only those 3 declared clauses as premises on a fresh
hypothetical result, proving the correct value is forced — should fail
for any cell those 3 clauses don't directly mention.

**Confirmed for real, not just predicted.** A probe lemma for
`(Dabigatran, Ketoconazole)` (should be `Contraindicated`) genuinely
failed to verify. Preserved as a proper honesty exhibit before touching
anything further: `drug_interaction_checker_underconstrained.dfy` (the
original Gate C1 spec, byte-for-byte, same rationale as
`dosage_underconstrained.dfy`) and
`drug_interaction_checker_stp_suite_against_underconstrained.dfy` (3
ACCEPT lemmas, one per Gate 1c finding for narrative continuity) — real
committed failing capture, `0 verified, 3 errors`.

**Materially different from, and larger than, `renal_adjustment`'s own
Gate C4 finding.** There, two functions' postconditions *bounded* a
result without *pinning* it — ACCEPT proofs succeeded against the loose
bounds, only REJECT proofs (excluding a wrong candidate) failed. Here,
most of the 60 unmentioned cells had **no constraint at all** — not
even ACCEPT worked, because nothing forced the *correct* value either.
The match body's correctness was never actually a signature-level
claim; the "1 verified, 0 errors" Gate C1 capture was true, but it was
never evidence that the *specification* — as opposed to the
*implementation* — guaranteed the lookup table's content.

**Fixed for real.** `drug_interaction_checker.dfy` gained 60 explicit
pinning `ensures` clauses, one per match arm, replacing the original 3
(now strictly subsumed). Verbose on purpose — an honest reflection of
this function's actual shape, a flat 63-cell lookup table with no clean
range partition to exploit the way `GStage`'s six boundary clauses did.
Re-verified clean: `1 verified, 0 errors`, resource cost 358,399 (up
from 113,039 before the fix — the heaviest single verification task
recorded across all three worked examples so far — still 0.42s real
time, nowhere near the 30s default timeout).

**The real STP suite**, `drug_interaction_checker_stp_suite.dfy`: 7
ACCEPT lemmas covering 6 worked examples already established in
`GATE_1C_AUDIT.md`'s hand-traces (`(Dabigatran, SSRIOrSNRI)` gets both
branches of the `hasOtherBleedingRiskFactors` conditional as separate
lemmas), plus 4 REJECT lemmas — 3, one per `Contraindicated` cell, the
highest-stakes rows in the table, proving a plausible-but-wrong weaker
`Caution` candidate is genuinely excluded — plus one more re-testing
Gate 1c Finding 3's specific ambiguity directly. 11 lemmas total; Dafny's
capture reads `22 verified, 0 errors` (~2 verification tasks per lemma,
not a 1:1 lemma count - a doc-accuracy correction made 2026-07-10 after
this entry and several other docs originally misread the raw capture
figure as "22 lemmas"). Scoped
deliberately short of restating all 60 pinning clauses individually —
each already is its own ACCEPT proof; the suite adds narrative
continuity and safety-focused REJECT coverage on top, not underneath.

Both Gate C1's and Gate C4's captures re-run and re-committed fresh
after the spec changed, not left pointing at stale content.
`evidence/dafny_adapter.py` re-confirmed parsing the (re-captured) Gate
C1 output unmodified. Full documentation ripple in the same session:
`PHASE1_PLAN.md`, `SYSTEM_BLUEPRINT.md` (Section 8 + component map),
`KNOWN_LIMITATIONS.md` ("Phase E Gate C4" section), `HANDOFF.md`
(worked-examples section + a new standing-discipline entry: adding
*some* `ensures` clauses isn't the same as adding *enough*).

171 tests pass throughout (no Python code changed — new Dafny specs and
docs only).

## 2026-07-10 — Docs-staleness fix, pytest CI, and a third worked example through Gate C1

Same day as the Gate C6 walkthrough entry below, later in the session.
Four pieces of work, in order.

**Documentation staleness, closed mechanically, not just by hand.**
`SYSTEM_BLUEPRINT.md` and `KNOWN_LIMITATIONS.md` had drifted behind
`DEVLOG.md`'s own newest entry (still said "2026-07-09" the same day
this file already had a 2026-07-10 entry) — a real, live instance of
exactly the drift Steven had flagged by hand more than once this
session. Fixed with a real content review (not a bare date bump):
`SYSTEM_BLUEPRINT.md`'s component map gained `.github/workflows/`,
`dashboards/`, and the pow-probe files; its Gate 1c Finding 1 narrative
now cites the empirical pow probes instead of stating the claim as
given. New test, `tests/test_docs_current_with_devlog.py`, makes this
specific drift mechanically impossible to reintroduce silently.

**PayloadGuard's exit-code contract corrected, then a pytest CI job
added.** Confirmed by reading `analyze.py` directly rather than
trusting the wrapper's shell logic: exit 0 covers SAFE/REVIEW/CAUTION
alike, only exit 1 (analysis error) and exit 2 (DESTRUCTIVE) block
merge. `.github/workflows/tests.yml` now runs `pytest tests/ -q` on
every PR, closing a real gap — `main` previously had no automated check
that the suite itself still passed. Caught and fixed a stale claim
while touching this area: `HANDOFF.md`'s working-conventions section
still said "no CI is configured on this repo."

**A third worked example, `examples/drug_interaction_checker/`,
scoped and sourced.** Steven's domain choice: set/list-membership
logic. He found the primary source himself (NHS SPS's DOAC-interaction
guidance) after a first attempt at scoping candidate sources came up
short — verified independently via a raw `curl` fetch, not just the
AI-summarized pass, which turned out to matter: the summary had
flattened real structure (per-DOAC downgrades on verapamil/fluconazole,
two indication-dependent apixaban branches, a real gap in the source
itself on apixaban+dronedarone). Full extraction:
`sources/sps-doac-interactions-2024.md`.

**Gate 1c found three real findings; all three resolved by explicit
decision, none deferred.** (1) The `Outcome` taxonomy dropped the
source's own risk-direction axis (every one of its 17 sections is
headed "bleeding risk" or "thrombosis risk" or a no-interaction/
theoretical variant) — resolved by adding a `RiskDirection` field. (2)
`CheckInteraction` wasn't total over its own declared `Agent` type —
two agents' apixaban cells needed an indication axis not yet built, but
their other cells didn't — resolved with a type-level precondition
exclusion, recovering six real cells rather than deferring all eight.
(3) Two cells were genuinely ambiguous in the source itself (hedged
"unlikely to be clinically relevant" without digoxin's clean negative)
— resolved by adding a fourth `Outcome` case, `CautionLowRelevance`.
Every original worked-example hand-trace was re-derived against the
redesigned sketch to confirm the fix introduced no new inconsistency.

**Gate C1 built — and caught a real false-clean result before it was
committed.** `drug_interaction_checker.dfy`: 63 match arms across 15
v1 agents. An early draft with no `ensures` clauses reported "0
verified, 0 errors" from `dafny verify` — not a pass. Dafny generates
verification tasks from postconditions; a function with none has
nothing for Z3 to prove, and match-exhaustiveness is a resolve-time
syntax rule, not an SMT proof. Confirmed with `--progress Symbol` (still
0 verified) and `dafny resolve` (parses and type-checks fine) before
concluding the absence of tasks was real, not a harness glitch. Fixed
by adding three real `ensures` clauses — a `NotCovered`-implies-the-
one-real-gap pin, a `Contraindicated`-implies-`Dabigatran` pin, a
`Digoxin`-always-safe pin — before committing anything. Re-verified: `1
verified, 0 errors`, resource cost 113,039 (heaviest single
verification task across all three worked examples so far, still
under a second real time). `evidence/dafny_adapter.py` parses the real
capture unmodified — the third confirmation this parser generalizes
across independently-authored specs with zero code changes.

Also mined a genuinely worthless-looking external "hardening
recommendations" document for real signal rather than dismissing it
outright: most of its nine items either described already-fixed
problems or repeated design mistakes this repo had already caught and
named (a lookup-table proposal for drug classification that
`REQ-RENAL-8` already rejected, for the reason `REQ-RENAL-8` already
gave). But two things checked out empirically and are worth acting on
later: `dafny verify --json-output` gives real structured per-clause
diagnostics on a failing verification (better than the summary-line
regex `dafny_adapter.py` currently parses), and Dafny's own docs
distinguish `--resource-limit` as "a deterministic alternative to a
time limit" from the wall-clock default every real capture in this
repo currently uses — measured the actual margin (7,443–113,039
resource units observed so far, nowhere near a practical boundary) and
confirmed Dafny's default random seed is fixed at 0, not
entropy-randomized, so the theoretical risk is real but currently low
for every spec in this repo. Neither built yet — held off per direct
instruction to stay on the worked-example thread first.

171 tests pass throughout (no Python code changed this session — new
Dafny specs, new docs, one new test file for the staleness check).

## 2026-07-10 — Gate C6 walkthrough surfaced an unearned claim; tested and closed it for real

Walking through `renal_adjustment.dfy`'s Gate C6 sign-off with Steven
(the actual "does the summary match intent" review this gate exists
for), he pushed back before confirming: "can we make the claim with the
evidence we have and supplied documentation... it's a judgment call but
not entirely my own." That question, applied to Gate 1c Finding 1's
closing claim ("CKD-EPI eGFR stays caller-supplied because Dafny/Z3
can't express it"), found the claim had never actually been tested —
`GATE_1C_AUDIT.md`'s 2026-07-09 addendum said it was "re-confirmed,"
pointing at `sources/ckd-epi-2021-and-cockcroft-gault-verification.md`'s
"Dafny/Z3 architectural strategy" finding, which itself explicitly says
that question is out of scope for that document and defers back. A
circular "confirmed" with no real Dafny run behind it, on either end.

**Tested it for real.** Two probes, committed with genuine captures
(`examples/renal_adjustment/run_verify_pow_probes.py`,
`dafny_pow_expressiveness_probe.dfy`,
`dafny_pow_axiom_trap_probe.dfy`): (1) writing CKD-EPI's `min(Scr/κ,
1)^α` shape directly hits `Error: unresolved identifier: Pow` — Dafny
has no real-exponentiation primitive at all, for any exponent; (2) the
obvious workaround, declaring `Pow` an unproven `{:axiom}`, verifies
trivially (`2 verified, 0 errors`) even for a lemma claiming `Pow`
always returns exactly `0.0` — an absurd, wrong statement that an axiom
this permissive can't distinguish from a correct one. Confirms the
axiom path would be a DECLARED assumption wearing PROVEN's clothing,
exactly what Gate C2 (`assert_no_realized_proven`) exists to refuse
structurally, caught here even earlier at the spec-authoring level.

Both halves of Gate 1c Finding 1's closing claim now rest on real
evidence: Cockcroft-Gault was already PROVEN-strength (Dafny + STP +
independently-sourced citations); CKD-EPI eGFR's exclusion is now
empirically demonstrated, not asserted. Updated everywhere the old
circular claim appeared: `renal_adjustment.dfy`'s header comment,
`GATE_1C_AUDIT.md` (new 2026-07-10 addendum), the CKD-EPI sources doc,
`KNOWN_LIMITATIONS.md`, `examples/renal_adjustment/README.md`, and
`HANDOFF.md` — the last of these now states the pattern explicitly for
future sessions: before signing off Gate C6 on any spec, check whether
every claim in the spec's own comments was actually tested, not just
reasoning that sounded right the first time it was written.

`python -m pytest tests/ -q` — 170 passed, unaffected (no Python code
changed; `renal_adjustment.dfy` re-verifies clean, `7 verified, 0
errors`, comment-only change). **Gate C6 sign-off itself remains open**
— this strengthened one of the claims under review, it did not close
the gate; that's still Steven's decision on the full document.

## 2026-07-09 — Built Gate C3 and Gate C5 for renal_adjustment.dfy: the last two unbuilt gates, four real engine gaps found and fixed, two named and left unfixed

"Build until sign-off, i will review." Applied the shared
`evidence/dafny_spec_lint.py` (Gate C3) and `evidence/dafny_mutate.py`
(Gate C5) engines to `renal_adjustment.dfy` for the first time — both
had only ever been run against `dosage.dfy`'s different shape (one
`method` plus one companion `function`, all real-typed literals, no
member-access calls or datatype discriminators in any clause). Per this
repo's standing discipline, treated "should work unmodified" as a claim
to check empirically, not assume — it didn't, four times.

**Gate C3:** all seven functions `sat` on vector 1 (no vacuous
preconditions); five have expected vector 2 warnings (16 one-way `==>`
clauses used for exhaustive branch dispatch — unlike `dosage.dfy`, which
avoids `==>` entirely). Real gap found and fixed:
`check_precondition_satisfiability` built a Z3 symbol for every declared
parameter regardless of use, so `AssessRenalFunction(formula: Formula,
renalFunctionValue: real)` refused outright on its unused `Formula`-typed
parameter even though the one `requires` clause never mentions it — 
narrowed to only model referenced parameters (two new regression tests
confirm a referenced unsupported-type parameter still refuses,
unchanged). New file: `tests/test_renal_adjustment_spec_lint.py`.

**Gate C5:** ran ROR/LOR/AOR/LVR/COI independently against all seven
functions (no single top-level `method` to target the way `dosage.dfy`
has one) — 450 mutants, real-verified against the installed Dafny
4.11.0 binary. Two real tokenizer gaps found and fixed on the first two
attempts (`.Floor`'s DOT, `.EGFRAssessment?`'s QUESTION — both new
inert-token extensions, same class as the existing COMMA/SEMI
tolerance). A third run surfaced LVR formatting every mutated literal as
a decimal, breaking Dafny's static typing on this spec's many int-typed
boundary literals (`roundedEgfr >= 90`, `ageYears < 140`) — 16
"unsupported syntax"/"unclassifiable" results collapsed to 0 once fixed
(a literal's own lexical form now determines int vs. real formatting).

Two further real gaps found and **named, not fixed** — real new
engineering, not bounded extensions, and Gate C4's STP suite already
independently proves what either would additionally cover:
`RoundHalfUp` and `CockcroftGaultCrClMlPerMin` each have an ensures
literal embedded in arithmetic rather than directly adjacent to a
comparison operator (LVR's documented Tier-1 scope boundary — 2 mutants,
recorded `blocked_lvr_clause_literal`); `SelectFormula`'s flat,
unparenthesized six-term `||` chain makes any LOR `||`→`&&` mutation a
genuine Dafny parser rejection (10 mutants, recorded `unclassifiable`).

**Final run: 250 killed, 137 filtered pre-verification, 51 survived, 10
unclassifiable, 2 blocked.** All 51 survivors explained into three named
categories, not left as an undifferentiated pile — full derivation in
`examples/renal_adjustment/README.md`'s Gate C5 amendment, locked in by
`tests/test_renal_mutation_report.py`:

1. **33 survivors** — ROR/LVR narrowing a one-way `==>` clause's
   antecedent. Mathematically guaranteed to survive regardless of
   whether the spec is tight (a narrower antecedent's true-set is always
   a subset of the original's) — a structural blind spot of this
   technique against guard-style dispatch clauses, not a proof gap.
   Gate C4's STP suite is the tool that actually pins these boundaries.
2. **17 survivors** — `requires`-clause weakenings Dafny can still
   satisfy because the specific `ensures` clauses currently proven don't
   depend on them (`ComposedCeiling`'s `<=`/pinning postconditions hold
   for any real ceiling pair, not just positive ones). Not a defect —
   the preconditions still correctly document real domain facts (dose
   ceilings and BMI are physically positive); they just aren't
   proof-necessary for what's currently established.
3. **1 survivor** — `RoundHalfUp`'s self-referential postcondition
   survives an AOR `-`→`*` substitution for a coincidental numeric
   reason; its exact output is independently pinned by Gate C4 regardless.

New files: `examples/renal_adjustment/run_mutation_suite_renal.py`,
`mutation_report_renal.json`/`.md`, `run_manifest_mutation_renal.json`,
`tests/test_renal_mutation_report.py`. `python -m pytest tests/ -q` —
170 passed (up from 154). `renal_adjustment.dfy` and its STP suite
re-verified unaffected (`7 verified, 0 errors`; `52 verified, 0
errors`) — only `evidence/` and test/script files changed, no `.dfy`
touched. Documentation brought current in the same change: `README.md`
(new Gate C3/C5 amendments), `HANDOFF.md`, `SYSTEM_BLUEPRINT.md`,
`KNOWN_LIMITATIONS.md`.

**Gate C6's sign-off is now the only thing left before this example's
Phase 2 is done** — every other gate is built.

## 2026-07-09 — Independently checked a "Gate C5 verified sources" document; its flag wasn't the bug, but checking it found a real one

Steven supplied a document claiming to independently verify four
citations in `renal_adjustment.dfy` (Cockcroft-Gault 1976, MHRA DSU,
Miller et al. 2022, KDIGO staging), flagging one item: a "Table 2 vs
Table 11" numbering discrepancy for the KDIGO GFR-category table at
p. S126, to resolve before sign-off. Per this repo's standing rule,
checked directly rather than trusted.

**Three of its four claims re-confirmed directly, adding real value:**
Cockcroft-Gault's 1976 abstract (PMID 1244564, via PubMed metadata)
confirms the 249-patient/236-patient/r=0.83 derivation numbers this repo
hadn't previously extracted; Miller et al. 2022's exact "eGFR of 59.7...
reported as 60" worked example (via direct fetch of the published
article) is real and now quoted in `sources/kdigo-2024-gfr-staging.md`;
its note that the MHRA page states no formula or constants at all
independently corroborates the same finding this repo made 2026-07-09
earlier the same day.

**The flagged item itself wasn't a real bug — this repo never cited a
table number for the p. S126 table, only its page.** But checking it
against the committed PDF directly (`sources/KDIGO-2024-CKD-Guideline.pdf`,
extracted with `pypdf` rather than re-reading prior extraction notes)
surfaced a different, real citation error the flag hadn't caught:
`PHASE1_PLAN.md`'s REQ-RENAL-1a row cited "p. S164, Table 11" — S164 is
wrong (it's REQ-RENAL-7's Practice Point 4.2.4 page, apparently carried
over by mistake); Table 11 is actually at S153 (where the quoted text
appears) and S184 (its full first appearance). Fixed. Also confirmed:
the p. S126 GFR-category data reappears explicitly labeled "Table 2" at
S137, a stronger citation available if ever needed.

**Pattern worth naming:** an external document's specific flag can be
wrong and the exercise of checking it can still be worth doing —
neither "trust the flag" nor "the flag was wrong, so nothing to find
here" would have caught the real S164 bug. `python -m pytest tests/ -q`
— 154 passed, unaffected (citation-only change). Full detail:
`sources/kdigo-2024-gfr-staging.md`,
`sources/ckd-epi-2021-and-cockcroft-gault-verification.md`,
`PHASE1_PLAN.md`.

## 2026-07-09 — Closed Gate 1c Finding 1 for Cockcroft-Gault; re-verified MHRA/NICE sources; caught two real gaps along the way

Closed two of the three open items from the last handoff review: (1)
re-confirm the MHRA and NICE NG203 source URLs still resolve to the same
content, and (2) decide and implement Finding 1's CrCl/eGFR computation
scope. Steven's framing for (2) settled the CKD-EPI half without a
judgment call: "if we have to tie to specific software then if we
physically cannot at the moment, then the choice is made for us" — build
whatever Dafny/Z3 can actually prove (Cockcroft-Gault), leave whatever it
can't (CKD-EPI eGFR, real fractional exponents on a variable base) as
caller-supplied, rather than treat both as equally open.

**Source re-verification (item 4), done first, on purpose:** re-fetched
`https://www.gov.uk/drug-safety-update/...` (MHRA) and
`https://www.nice.org.uk/guidance/ng203/chapter/Recommendations` (NICE)
directly. Both confirmed unchanged from the 2026-07-08 verification —
same five formula-selection conditions, same `BMI <18 kg/m2 or >40
kg/m2` boundary text, same NICE 1.1.2/1.1.4/1.1.24 wording. One real
correction surfaced anyway: earlier notes in this repo
(`GATE_1C_AUDIT.md`'s NHS SPS hand-trace, `sources/README.md`) called the
CrCl-formula multiplier 1.23/1.04 "MHRA's constants." Re-checked directly
against MHRA's actual page text — it states no formula or numeric
constant at all, only that Cockcroft-Gault is the required method,
pointing to external calculators. 1.23/1.04 is ordinary unit-conversion
arithmetic (88.4 µmol/L per mg/dL applied to the independently-sourced
1976 Cockcroft-Gault formula), not an MHRA-specific number. Corrected in
`sources/README.md`, `sources/mhra-renal-formula-selection-2019.md`,
`sources/ckd-epi-2021-and-cockcroft-gault-verification.md`, and
`GATE_1C_AUDIT.md`.

**Implementation (item 1):** added `CockcroftGaultCrClMlPerMin` (small
linear arithmetic, self-referential pinning `ensures` matching the exact
formula — no under-constrained postcondition risk from the start) and
`AssessRenalFunctionFromInputs` (end-to-end orchestration: selects the
formula, computes CrCl on the Cockcroft-Gault branch, still takes
`callerSuppliedEgfr` on the eGFR branch) to `renal_adjustment.dfy`.
Checked in a scratch file against the real, installed Dafny 4.11.0
toolchain first, including a sanity check against `GATE_1C_AUDIT.md`'s
NHS SPS worked example (80yo male, 60kg, creatinine 120 µmol/L → the
exact fraction 36.8(3), `RoundHalfUp`'d to the published 37 mL/min) —
matched before either function was committed. `renal_adjustment.dfy`
re-verifies clean: `7 verified, 0 errors` (up from 5).

**Not skipped: Gate C4 extended for the two new functions too,** even
though their postconditions are already exact equalities and therefore
about as tight as a postcondition can be — added real ACCEPT/REJECT
lemmas to `renal_adjustment_stp_suite.dfy` using the same NHS SPS
scenario, rather than assuming exemption because "the equality already
proves it." `52 verified, 0 errors` (up from 44).

**A second real tooling gap found, not worked around:**
`evidence/dafny_nl_summary.py` refused to summarize
`AssessRenalFunctionFromInputs` on the first attempt — its `ensures`
clauses were the first multi-line ones ever written in this repo's Dafny
specs (every other function uses single-line `ensures`, however long),
and the tool correctly refuses to guess a citation association rather
than risk a dropped or misattributed one, exactly the same discipline
behind its two Gate C6 fixes on 2026-07-08. This was my own formatting
choice breaking an established convention, not a genuine spec need — so
the fix was reformatting to single-line, not extending the tool. Named
as a real, permanent tooling constraint in `KNOWN_LIMITATIONS.md`
(single-line clauses only) rather than silently worked around and
forgotten.

Gate C6's sign-off document (`nl_confirmation_renal_adjustment_dfy.md`)
amended with both new functions' generated summaries — still PENDING
Steven's confirmation, now covering five amendments' worth of change
under one outstanding sign-off. `python -m pytest tests/ -q` — 154
passed, unaffected (no Python code changed). Documentation brought
current in the same session as the change, per this repo's own recent
lesson about `DEVLOG.md` drift: `GATE_1C_AUDIT.md`, `PHASE1_PLAN.md`,
`KNOWN_LIMITATIONS.md`, `HANDOFF.md`, `README.md`, `SYSTEM_BLUEPRINT.md`,
and the three `sources/` documents above all updated together with the
code.

**Remaining open item:** `REQ-RENAL-8` classification-flag provenance
(Phase 3 concern, not a Phase 2 blocker) — the sole item left in
`PHASE1_PLAN.md`'s "Closed under named fallback assumptions" section.

## 2026-07-09 — Brought SYSTEM_BLUEPRINT.md and KNOWN_LIMITATIONS.md current (PR #5, `2fc2d88`)

Asked to continue and make sure the main docs (`SYSTEM_BLUEPRINT.md`
especially) represented current state, not just `HANDOFF.md`/`README.md`.
Real gap found: `SYSTEM_BLUEPRINT.md`'s component map had no entry at
all for `examples/renal_adjustment/` - a whole second worked example,
built earlier this session, structurally invisible in the one document
whose stated job is "structure and data flow." Its `sources/` listing
had 2 of the 6 real files; its `tests/` listing was missing
`test_citation_gate.py`; its own top "Last updated" stamp still read
2026-07-07 even though the file's own body already referenced a
2026-07-09 citation-gate addition further down - internally
inconsistent, not just outdated.

Fixed all of it: a real (deliberately concise) component-map entry for
`examples/renal_adjustment/`, the missing `sources/` files, the missing
test file, and a new Section 7 ("Phase D") stating current status -
Gate C1/C4/C6 built, Gate C3/C5 not yet started, the two scope
decisions still explicitly open, the citation gate. Named the actual
root cause in the header itself: prior updates kept appending full
session narrative to the header rather than updating the structure
sections, which is exactly why the drift happened and why it would keep
happening - `DEVLOG.md`/`HANDOFF.md` now own the narrative, this file
owns current structure only, going forward.

`KNOWN_LIMITATIONS.md`'s top stamp had the same problem (stale date,
current content) - fixed the stamp, clarified the append-only framing
so a dated historical entry isn't mistaken for staleness again.
`README.md`/`OPERATIONS_MANUAL.md` still said "152 tests" (real count:
154, from the citation-gate audit's own regression tests) - fixed.

**Then caught a second instance of the exact same failure mode while
writing this entry**: neither this doc-currency PR nor the preceding
`HANDOFF.md`/`CLAUDE.md` PR (below) had a `DEVLOG.md` entry at all until
now - the top entry stayed frozen at the "Audit" session two PRs back,
even though two more real, merged changes had happened since. Flagged
by Steven directly ("devlog in main is still 2 hours old"), not
self-caught. 154 tests unaffected (documentation only, both entries).

## 2026-07-09 — Added HANDOFF.md and CLAUDE.md for cold-start session continuity (PR #4, `aa28992`)

Asked for a handoff document referenced implicitly at session start, so
a fresh session with no memory of this conversation can pick the repo
up cold without Steven re-explaining status each time.

Added `HANDOFF.md`: current state of both worked examples (dosage
calculator complete; renal adjustment at Gate C1/C4/C6 done, C3/C5 not
started - the actual next step), the two decisions left explicitly open
(CrCl/eGFR computation scope, classification-flag provenance) with
recommendations on record rather than silently resolved, and the
working discipline this repo holds itself to (verify empirically before
trusting a claim including this repo's own prior claims, hand-derive
predictions before building, never hand-edit a generated artifact, use
the citation gate before trusting an external source claim).

Added `CLAUDE.md` - the file Claude Code loads automatically at session
start - pointing every future session to `HANDOFF.md` first. This is
what makes the reference implicit: not a process Steven has to invoke,
just how a session in this repo starts by default. Also states the
expectation that `HANDOFF.md` gets updated at the end of any session
that changed something non-trivial - an expectation this same session
failed to fully meet on its own next two PRs (see the entry above and
`HANDOFF.md`'s own updated text), caught only when asked directly
rather than self-caught. 154 tests unaffected (documentation only).

---

## 2026-07-09 — Audit of this session's work: one real code bug found and fixed, plus stale documentation

Asked directly to audit everything built this session and fix any
errors found. Re-verified rather than re-read: re-ran the full test
suite, re-ran `dafny verify` on all four renal-adjustment `.dfy` files
and all four `dosage_calculator` `.dfy` files from scratch (all matched
their documented outcomes exactly - `5 verified`/`44 verified`/`0
verified, 4 errors` etc., no drift), re-ran the mutation suite (56
mutants, same breakdown, confirming the shared-engine regex changes
didn't regress `dosage_calculator`), and re-generated the Gate C6 NL
summaries to diff against the committed sign-off document (exact
match, no drift).

**Found one real code bug**, in the citation gate built earlier this
session — found by deliberately testing it against its own motivating
scenario rather than assuming it worked: `evidence/citation_gate.py`'s
normalization strips all punctuation for whitespace-robustness, which
means a claim citing "Recommendation 1.1.2" would falsely CONFIRM
against source text reading "Recommendation 1.1.2.1" (a different
recommendation with different content) - "112" is a genuine substring
of "1121" after normalization. This is the exact class of error the
module exists to catch, and it was sitting inside the module itself,
undetected until audited directly rather than trusted because it
passed its own test suite. Fixed with `_find_bounded_match`: a
digit-adjacency boundary check applied only to numeric matches (not
letters, since this repo's own PDF extraction has been observed to
glue adjacent words together with no boundary at all - enforcing
letter boundaries would trade a real bug for a worse one). Two new
regression tests confirm the fix and confirm it didn't overcorrect
(an exact numeric match still confirms).

**Found stale documentation**, not code bugs: `README.md` and
`OPERATIONS_MANUAL.md` both still said "142 tests" after the citation
gate had already brought the real count to 152/154 - these are
current-state documents, not dated history entries, so unlike
`KNOWN_LIMITATIONS.md`/`DEVLOG.md`'s "as of" framing, a stale number in
them is actually wrong, not historically accurate. Also found
`OPERATIONS_MANUAL.md`'s component map and README's "what's in this
repository" list never mentioned `citation_gate.py` at all - it was
built after both documents were written and neither was updated
afterward. Fixed both, and added `OPERATIONS_MANUAL.md` §4.7
documenting the citation gate at the same level of detail as the other
gates.

154 tests passing (152 + 2 new regression tests from the audit itself).
No other errors found in the Dafny specs, captures, or cross-document
citation numbering (REQ-RENAL-7/8's renumbering was checked for
consistency across all four files that reference it - clean).

---

## 2026-07-09 — Built the citation gate: mechanical citation verification, from a "thinking out loud" idea

Steven floated a larger idea (automating contract drafting from natural-
language specs via "vericoding," to reduce the need for a specialist to
hand-author every Dafny contract). Talked through what this session's
own history actually shows about that: the process was reverse-
engineered into what's mechanical (drafting Dafny syntax, generating NL
summaries, generating mutants - already automated in this repo) versus
what only worked because a person was holding independent context
(citation verification, spotting silently-resolved ambiguities, judging
whether a postcondition means what it looks like it means). Identified
the citation-verification piece as the one immediately buildable, since
it's exactly what's already been done by hand, repeatedly, this session.

Built `evidence/citation_gate.py`: `verify_citation()`/
`verify_citations()`, mechanical normalized-substring matching between a
claimed quote and source text - deliberately not an LLM judgment call,
so a system that drafts a citation and a system that checks it can't
share the same failure mode. Verdict vocabulary is CONFIRMED/NOT_FOUND,
asymmetric by design (mirroring `evidence/model.py`'s Strength
vocabulary): NOT_FOUND is explicitly never presented as proof of
fabrication, since this repo's own PDF extraction has already been
observed to drop text at some boundaries - a NOT_FOUND verdict says
"couldn't confirm automatically, check the raw source," not "this is
fake."

Regression tests (`tests/test_citation_gate.py`) are built from the two
real fabrication events this session actually caught by hand, not
synthetic examples: a NICE NG203 misquote (claimed Recommendation 1.1.2
"mandates the 2009 equation" and 1.1.4 bars ethnicity-based eGFR
adjustment; neither is real, and the same misquote was repeated
verbatim across two separately-supplied "research findings" documents)
and a KDIGO misquote (claimed "Recommendation 1.1.2" states "the
explicit shift to the 2021 race-free equation"; the real recommendation
is numbered 1.1.2.1 and is actually about the eGFRcr-vs-eGFRcr-cys
choice). Caught two real fixture typos while building the tests
themselves (a claim that dropped the word "to," a claim that used
"estimated glomerular filtration rate" when the real source text
abbreviates it "GFRcreatinine") - both caused genuine NOT_FOUND
verdicts against real source text, exactly the gate doing its job, not
a bug; fixed the test fixtures to match the real source text rather
than loosen the matching logic.

10 new tests, all passing; 152 total (up from 142). Not wired into any
generation pipeline - a standalone, domain-free tool, same scope
discipline as the Gate C3/C5/C6 modules.

---

## 2026-07-09 — Rewrote README.md for a non-expert audience; added OPERATIONS_MANUAL.md

`README.md` had accumulated a full gate-by-gate build history (every
Gate C1-C6 finding, every mutation-testing operator count, every
extension) directly in the repository's front door — accurate, but
unreadable by someone evaluating whether to use the system rather than
already deep in its build log. Rewrote it as a plain-English overview:
what problem this solves, the core vocabulary (requirement / evidence /
strength / traceability matrix) explained without jargon, what's in the
repository, a quick start, and a status summary — no emojis, no gate
history, technical depth pushed out to linked documents instead of
inlined.

Added `OPERATIONS_MANUAL.md` as the "definitive manual... at a high
technical level" - the destination for that technical depth. Covers:
architecture and data flow, the Strength vocabulary and its enforced
invariants, the full evidence pipeline (author/capture/generate), all
six Dafny verification gates (C1-C6) explained by mechanism and purpose
rather than by chronological finding, a complete command reference, a
worked "how to add a new example" section distilled from the
renal-adjustment build (including the honest note that extending the
system to a second example found and fixed two real gaps in shared
tooling - not glossed over as if everything generalized cleanly on the
first try), testing discipline, the review protocol summary, and a
troubleshooting section.

Both documents cross-reference the existing detailed records
(`SYSTEM_BLUEPRINT.md`, `DEVLOG.md`, `KNOWN_LIMITATIONS.md`,
`REVIEW_PROTOCOL.md`) rather than duplicating them - the new manual
synthesizes current-state understanding; the existing docs remain the
dated, append-only record of how it got there. 142 tests unaffected
(documentation only).

---

## 2026-07-09 — Built Gate C4 for real: both predictions confirmed, both real gaps fixed properly

Instructed explicitly: solve any real problems found, don't skip or
apply a flimsy workaround. Built `renal_adjustment_stp_suite.dfy`
(44 lemmas: ACCEPT, REJECT, uniqueness, and totality checks across all
five functions, using the 16-row test-vector table from
`PHASE1_PLAN.md`) and ran it against the spec exactly as it stood,
before touching anything.

Both `gate_c4_stp_plan.md` predictions confirmed empirically, not just
by inspection: the four REJECT lemmas assuming a wrong candidate value
for `ComposedCeiling` (0.0 instead of the correct minimum) and
`AssessRenalFunction` (wrong G-stage / wrong CrCl value) genuinely
**failed to verify** - `0 verified, 4 errors`, a real Dafny run, not a
hypothetical. `RoundHalfUp`, `GStage`, and `SelectFormula`'s
ACCEPT/uniqueness/totality lemmas all passed on the same first run - the
predicted "these three are already tight" also confirmed for real.

Preserved the pre-fix state as an honesty exhibit before fixing anything,
mirroring `dosage_underconstrained.dfy`'s exact pattern: copied the
current file to `renal_adjustment_underconstrained.dfy`, and split the
four failing REJECT lemmas into their own file,
`renal_adjustment_stp_suite_against_underconstrained.dfy`, confirmed to
fail against the preserved original for real (`0 verified, 4 errors`,
captured verbatim, not smoothed over).

Fixed `renal_adjustment.dfy` itself with proper pinning `ensures`
clauses, not a workaround: `ComposedCeiling` gained
`ensures ComposedCeiling(...) == existingCeiling || ComposedCeiling(...) == renalCeiling`,
which combined with the existing two `<=` bounds forces the result to
equal `min(existingCeiling, renalCeiling)` exactly (if it equals
existingCeiling, the renalCeiling bound forces existingCeiling to BE the
minimum, and symmetrically). `AssessRenalFunction` gained two clauses
referencing its own composition directly
(`== EGFRAssessment(GStage(RoundHalfUp(renalFunctionValue)))` and the
CrCl-path equivalent) - the same self-referential pattern `ExpectedDose`
uses in `dosage.dfy`, not an ad hoc constraint chosen to make Dafny
happy without genuinely narrowing the postcondition.

Re-verified `renal_adjustment.dfy`: still `5 verified, 0 errors` -
neither function's body needed to change, only its stated contract.
Discovered on the first re-run of the STP suite that the REJECT lemmas
still failed even after the fix - not because the fix was wrong, but
because the lemmas' own `requires` clauses were manually restating the
OLD two/two-clause postconditions and hadn't picked up the new pinning
clauses automatically. Fixed the lemmas to restate all of each
function's CURRENT ensures clauses (a real, separate small mistake,
caught before reporting success) - re-ran, and the full suite passed:
`44 verified, 0 errors`.

Wrote `run_verify_dafny_stp_suite_renal.py` and
`run_verify_dafny_stp_suite_against_underconstrained_renal.py`,
mirroring `dosage.dfy`'s exact capture-runner pattern; ran both for
real, plus re-ran `run_verify_renal.py` since the main file changed.
All three captures match predictions exactly: main spec exit 0 (5
verified), STP suite exit 0 (44 verified), against-underconstrained
exit 4 (0 verified, 4 errors, preserved as the honest negative result).

Amended `nl_confirmation_renal_adjustment_dfy.md` with the two changed
functions' re-generated, re-cited postconditions, since this touched
functions already presented for Gate C6 sign-off - reported as an
amendment, not a silent edit, per `dosage.dfy`'s own amendment
precedent. 142 tests still passing; the new Dafny files aren't
Python-tested (matching `dosage_stp_suite.dfy`'s own precedent - real
Dafny captures are the evidence, not a pytest wrapper around them).

---

## 2026-07-09 — Scoped Gate C4 (STPs) for renal_adjustment.dfy; two real gaps predicted before building

Asked to plan the next phase after Gate C6. Wrote
`examples/renal_adjustment/gate_c4_stp_plan.md` — a scoping document,
not a build, per this repo's standing "scope first" discipline.

Read all five functions' `ensures` clauses specifically asking whether
each pins its exact output or only bounds/shapes it, before writing any
STP lemma (same hand-derivation discipline the LVR extension used).
Two real, predictable gaps stood out, both the same defect class as
`dosage.dfy`'s own original Gate C4 finding:

- `ComposedCeiling`'s two `<=` bounds don't force the result to equal
  `min(existingCeiling, renalCeiling)` — a wrong candidate value (e.g.
  always returning `0.0`) isn't excluded by the spec as written.
- `AssessRenalFunction` pins which constructor the result uses
  (`EGFRAssessment` vs. `CrClAssessment`, Gate 1c Finding 2's actual
  target) but not the value inside it — a wrong G-stage or wrong
  rounded CrCl value isn't excluded either.

Both are predictions, not yet confirmed by a real Dafny run - recorded
as hypotheses before building, per the LVR extension's own precedent,
so if either turns out wrong that gets reported honestly rather than
silently reconciled. The other three functions (`RoundHalfUp`, `GStage`,
`SelectFormula`) look genuinely tight by inspection - also a prediction,
not yet confirmed. The plan lays out the full per-function STP lemma
table (using the 16-row test-vector table already in `PHASE1_PLAN.md`
for ACCEPT lemmas) and the predicted pinning-clause fixes for the two
gaps, mirroring `ExpectedDose`'s role in `dosage.dfy`'s own fix.

No code changed - `renal_adjustment.dfy` is untouched, this is scoping
only. 142 tests still passing.

---

## 2026-07-09 — Caught and corrected a self-contradictory sourcing overclaim in RoundHalfUp's tie-break rule

Reviewing the Gate C6 sign-off, asked three direct questions: where
REQ-RENAL-3/4/6 live (answer: prose only, not yet Dafny signatures - no
correction needed, already accurately stated); what `RoundHalfUp`'s NL
summary cites as its source for the tie-break rule specifically, not
just the base rounding requirement; and to see Gate 1c Finding 2's text
verbatim (answer: quoted directly from `GATE_1C_AUDIT.md`, no issue
found).

The second question surfaced a real problem. `gate_c1_sketch.md` and
`renal_adjustment.dfy`'s header comment both described round-half-up as
"exactly KDIGO's own convention" in the same paragraph that also said
"KDIGO's cited text says 'rounded to the nearest whole number' with no
even/odd tie-breaking rule stated" — a direct self-contradiction that
had gone unnoticed since these were written. The base rounding
requirement (round to nearest whole number before staging) is genuinely
KDIGO-sourced; the specific tie-break direction (round-half-up vs.
round-half-even) was never sourced to anything and had been dressed in
citation-adjacent language ("clinical dose-staging conventions...
consistently read as round-half-up in practice") that named no actual
authority.

Searched for a real citation rather than just softening the claim.
Found one, and it corrects the assumption rather than rescuing it:
Miller WG, Kaufman HW, Levey AS, et al. "National Kidney Foundation
Laboratory Engagement Working Group Recommendations for Implementing
the CKD-EPI 2021 Race-Free Equations..." *Clinical Chemistry*.
2022;68(4):511-520. PMID 34918062, DOI 10.1093/clinchem/hvab278 -
confirmed via PubMed citation lookup, then fetched directly. States
plainly: "the reported result should be rounded to the closest whole
number based on the rounding logic of a laboratory information system"
- explicitly deferring the tie-break rule to each lab's own software,
confirming there is no single clinical standard for this specific
question at all.

Corrected in place across `sources/kdigo-2024-gfr-staging.md` (dated
amendment, not a silent rewrite), `gate_c1_sketch.md`,
`renal_adjustment.dfy`'s header comment, `PHASE1_PLAN.md`'s
requirements table, `sources/README.md`'s Contents entry,
`KNOWN_LIMITATIONS.md`, and this roadmap doc. No code changed -
`RoundHalfUp`'s body is unchanged (round-half-up remains a reasonable,
defensible design choice) and still verifies: `5 verified, 0 errors`,
re-captured. Only the sourcing claim was wrong, and only because it was
challenged directly rather than re-reviewed by the same process that
wrote it.

---

## 2026-07-08 — Renal-adjustment Gate C6 built; found and fixed two real bugs in shared tooling

Next step in the build order after Gate C1: Gate C6 (NL-dialogue
confirmation), moved earlier per its own recommendation. Attempted to
run `evidence/dafny_nl_summary.py::summarize_method` against
`renal_adjustment.dfy`'s five functions — the infrastructure plan had
predicted this "generalizes for free" since it's parameterized by
`method_name`. Checked empirically rather than trusted, and the
prediction was wrong in one respect.

**Real bug 1:** `_find_method_header` (`evidence/dafny_spec_lint.py`,
shared with `dafny_mutate.py` and `dafny_nl_summary.py`) only matched
Dafny's `method` keyword via `\bmethod\s+`, never `function`.
`renal_adjustment.dfy` is the first spec in this repo consisting
entirely of `function`s — every earlier spec (`dosage.dfy`) paired a
function with a method, and the method was always what got passed to
this extractor, so the function-only case was untested until now. Fixed
by widening the regex to `\b(?:method|function)\s+` in both
`_find_method_header` and the duplicate lookup in
`dafny_mutate.py::_method_header_span`. Two regression tests added
(`test_dafny_nl_summary.py::test_summarizes_a_function_not_just_a_method`,
`test_dafny_spec_lint.py::test_requires_clause_extraction_matches_a_function_not_just_a_method`).

**Real bug 2, found in the same pass:** `_REQ_ID_RE`'s character class
(`[A-Z0-9-]`) excluded lowercase letters, so `REQ-RENAL-1a` (this spec's
own citation for `RoundHalfUp`'s rounding postcondition) was silently
truncated to `REQ-RENAL-1` in generated summaries — a real citation-
accuracy defect misattributing the postcondition to a related but wrong
requirement ID, not a dropped citation that would have been obvious.
`dosage.dfy`'s REQ-IDs (`REQ-GIP-1-4-12`, `REQ-GIP-1-8-1`) never had a
lowercase suffix, so this never fired before. Fixed
(`[A-Za-z0-9-]`), regression-tested.

Also added missing `// REQ-RENAL-*` trailing citations to every
`ensures` clause in `renal_adjustment.dfy` itself (they were absent
entirely, which would have made every postcondition read "no
requirement cited" — understating real traceability, not reflecting an
actual gap) and reformatted `SelectFormula`'s two `ensures` clauses onto
single physical lines each (Gate C6's summarizer only supports
single-line clauses, matching `dosage.dfy`'s own convention — a correct
refusal on the first attempt, not a bug, fixed by reformatting rather
than working around the tool). Re-verified after both changes: `dafny
verify` still `5 verified, 0 errors`; re-captured the real Gate C1
output since the file changed.

Generated and committed the actual sign-off document,
`nl_confirmation_renal_adjustment_dfy.md`, presenting all five
functions' summaries with correct citations. Left the "Decision" section
explicitly pending Steven's confirmation rather than self-signing —
Gate C6's whole purpose is a human check against intent, the same
standard `dosage.dfy`'s own sign-off was held to.

142 tests passing (up from 138 - four new regression tests, two real
bugs fixed).

---

## 2026-07-08 — Renal-adjustment Gate 1 closed under named fallbacks; Phase 2 started

Asked what to suggest for an "easy fallback" so Phase 2 could start
without waiting on Gate 1c's two remaining items. Recommended treating
both as provisional defaults rather than resolved decisions: CrCl/eGFR
computation defaults to caller-supplied for both formulas in Phase 2 v1
(not a design change — `AssessRenalFunction` already takes
`renalFunctionValue: real` as a parameter); classification-flag
provenance (`REQ-RENAL-8`) is reclassified as a Phase 3 integration
concern rather than a Phase 2 blocker, since `SelectFormula`'s flags
were always caller-supplied parameters and the proof doesn't need to
know who populates them. Steven approved ("Ok continue while I keep
digging").

Updated `PHASE1_PLAN.md` and `GATE_1C_AUDIT.md` to record both as named,
dated, reversible defaults — not silently resolved. Gate 1 is now
closed under these two documented assumptions.

**Phase 2 started for real:** wrote `examples/renal_adjustment/renal_adjustment.dfy`,
composing all five functions verified individually during Gate 1c's
audit (`RoundHalfUp`, `GStage`, `SelectFormula`, `ComposedCeiling`,
`AssessRenalFunction`) into one committed file — same bodies as the
scratch checks, verbatim. Verified directly: `dafny verify` reports
`5 verified, 0 errors`. Wrote `run_verify_renal.py`, mirroring
`run_verify_dafny.py`'s capture discipline exactly (verbatim
stdout+stderr, exact command argv, exit code, ISO-8601 timestamp); ran
it for real, producing `raw_dafny_output_renal.txt` and
`run_manifest_dafny_renal.json`. Confirmed
`evidence/dafny_adapter.py::parse_dafny_capture` works unmodified
against this new capture — not assumed from the infrastructure plan's
prediction, actually run: `strength=PROVEN`,
`verifier_completion_status='completed'`. This is the first real,
empirical confirmation that the existing Gate C1/C2 machinery
generalizes to a second spec, the whole point of this POC.

138 tests still passing (no existing code touched); this is the first
commit that adds real, verified Dafny code for the renal-adjustment
POC rather than planning/sketch documents.

---

## 2026-07-08 — Verified Steven's CKD-EPI 2021 research brief; caught one fabricated citation

Steven asked for a precise, portable research prompt to close Gate 1c's
Finding 1 (no function computes the actual CrCl/eGFR numeric value) and
supplied it to an external research tool himself. He returned with a
"research findings" document — explicitly flagged by him as unverified
external knowledge — proposing the exact 2021 CKD-EPI creatinine-only
and creatinine-cystatin C equations, a UK-vs-US practice comparison, a
Cockcroft-Gault 1976 historical derivation, and a Dafny/Z3 lookup-table
architecture strategy.

Verified every checkable claim independently before accepting any of it:

- Both CKD-EPI 2021 equations checked against the National Kidney
  Foundation's own published equations directly (not just the supplied
  document) — matched exactly, all constants confirmed.
- The original 1976 Cockcroft-Gault formula confirmed via PubMed (PMID
  1244564, the correct paper) plus an independent secondary source; the
  88.4/72 unit-conversion arithmetic behind MHRA's rounded 1.23/1.04
  constants checks out.
- **Caught a fabricated citation:** the document claimed NICE NG203
  "Recommendation 1.1.2 mandates the 2009 equation" and "1.1.4 states
  do not use ethnicity to adjust eGFR." Fetched NICE NG203's actual
  recommendations list directly — neither claim is real. The real 1.1.4
  is about not eating meat before a blood test; the real
  ethnicity-related recommendation (1.1.24) is about screening risk
  factors, not equation selection; 1.1.2 doesn't specify an equation
  version at all. An independent, directly on-point 2024 UK study (Roy
  et al., *Nephron*, PMID 39342928, PMC11878410) confirmed the real
  picture: UK lab practice is heterogeneous and in transition (one major
  NHS hospital's own standard result was still MDRD), not settled on any
  single equation — a plausible-sounding but incorrect synthesis, caught
  by fetching the primary source rather than trusting the summary.
- Evaluated the proposed Dafny/Z3 lookup-table architecture on its own
  technical merits: the core diagnosis (Dafny/Z3 can't natively handle
  CKD-EPI's fractional-exponent real power terms — an expressiveness
  gap, not a performance/timeout issue) is correct and reinforces the
  existing recommendation to keep CKD-EPI caller-supplied. But the LUT
  proposal doesn't eliminate the trust boundary, it relocates it — the
  LUT itself would need independent verification against the formula,
  an unaddressed gap in the supplied strategy.

Committed `sources/ckd-epi-2021-and-cockcroft-gault-verification.md`
(full verification record) and folded the confirmed data plus the
corrected UK-practice picture into `PHASE1_PLAN.md`'s Finding 1 entry,
`GATE_1C_AUDIT.md` (addendum), `KNOWN_LIMITATIONS.md`, and this roadmap
doc's status section. Finding 1's actual scope decision (build
Cockcroft-Gault in Phase 2, keep CKD-EPI caller-supplied) remains
Steven's call — not decided here, now backed by verified data instead of
an open question mark. 138 tests still passing; no code touched.

---

## 2026-07-08 — Renal-adjustment Gate 1c Finding 2 resolved by redesign; Finding 1 deferred

Steven's direction: defer Gate 1c's Finding 1 (CrCl/eGFR value
computation scope) and instead design Gate 1b's skeleton to resolve
Finding 2 (the two-downstream-paths gap — `GStage` misapplied to a
Cockcroft-Gault CrCl value), then verify.

Added a dispatcher function, `AssessRenalFunction(formula: Formula,
renalFunctionValue: real): RenalAssessment`, where `RenalAssessment` is
a tagged union (`EGFRAssessment(stage: GStageCategory) |
CrClAssessment(roundedCrClMlPerMin: int)`). This makes the bug Finding 2
described — a KDIGO G-stage label ending up on a raw CrCl number, or
vice versa — a type-level impossibility rather than a convention a
future caller has to remember: `GStage` can only be reached inside the
`EGFRFormula` branch. Verified against the real, installed Dafny 4.11.0
toolchain: 11 verified, 0 errors, including two explicit lemmas
(`EgfrPathNeverProducesCrClAssessment`,
`CrClPathNeverProducesEGFRAssessment`) proving the impossibility
directly rather than relying on the `ensures` clauses' shape alone. The
NHS SPS worked example was re-derived through the new dispatcher and
matches Gate 1c's original hand-trace exactly (eGFR 53 → `G3a`; CrCl
36.9 → rounds to 37).

Folded into `gate_c1_sketch.md` (new section 5), `PHASE1_PLAN.md` (Gate
1b's staging postconditions, "Still open" list — item 3 struck through
and marked resolved), `GATE_1C_AUDIT.md` (dated addendum, not a silent
rewrite of the original findings), `KNOWN_LIMITATIONS.md`, and this
roadmap doc's status section.

**Gate 1 is still not formally closed** — Finding 1 (CrCl/eGFR
computation scope) remains open by explicit choice, and
classification-flag provenance (`REQ-RENAL-8`) is still unscoped. Both
block Phase 2. 138 tests still passing; no code touched (all Dafny
checks were scratch files, not committed artifacts).

---

## 2026-07-08 — Renal-adjustment Gate 1c performed: two real gaps found, Gate 1 not yet closed

Wrote `examples/renal_adjustment/GATE_1C_AUDIT.md`, the hand-trace audit
using the 16-row test-vector table as raw material, per Gate 1c's stated
purpose (catch conceptual gaps at the cheapest possible point, before
any Dafny code exists).

Confirmed total coverage for all four sketched functions, then went
further than a prose argument: wrote the composition
`GStage(RoundHalfUp(x))` as eleven Dafny lemmas (the ten boundary-tie/
just-under pairs plus the NHS SPS eGFR value) and verified them against
the real, installed Dafny 4.11.0 toolchain — 24 verified, 0 errors.
Hand-traced the NHS SPS worked example end to end, including the raw
Cockcroft-Gault arithmetic by hand: `(140-80) x 60 x 1.23 / 120 = 36.9`,
rounds to 37 — matches the published 37 mL/min exactly, cross-checked
with Python before trusting the mental arithmetic.

The audit found two real gaps, not zero — an audit that always finds
nothing is not doing its job:

1. **No function computes the actual CrCl/eGFR numeric value.** The
   skeleton's four functions stage/select/compose an already-computed
   value; nothing calculates it from raw inputs. This fell out silently
   from decomposing the skeleton into separate functions and was never
   an explicit scope decision until this audit surfaced it.
2. **`GStage` is eGFR-specific and must not be applied to a
   Cockcroft-Gault CrCl value** — found concretely while hand-tracing
   NHS SPS: `SelectFormula` correctly picks Cockcroft-Gault (age 80),
   but running its output (37) through `GStage` would report "G3a,"
   an eGFR-scale label on a CrCl-scale number, when the real eGFR (53)
   is what should be staged. The eventual top-level method needs two
   distinct downstream paths, not one unconditional `GStage` call.

Both are named in the audit document and folded into `PHASE1_PLAN.md`'s
"Still open" list, `KNOWN_LIMITATIONS.md`, and the roadmap doc's status
section, with a recommendation (not a decision) on gap 1: build
Cockcroft-Gault's own compute function in Phase 2 (small, fully
specified, low proof risk), treat CKD-EPI eGFR as caller-supplied like
the classification flags (too large a proof undertaking to justify for
this POC's actual purpose). **Gate 1 is not yet formally closed** — per
its own exit criteria, finding and naming real gaps is Gate 1c working
correctly, not a failure to complete it. 138 tests still passing; no
code touched (all Dafny checks were scratch files).

---

## 2026-07-08 — Renal Function Dose Adjustment POC: Gate 1a/1b closed, four proof functions verified against real Dafny

Steven uploaded a "research findings" document proposing to resolve
Phase 1's remaining open items: a BMI-boundary citation (NHS Tayside
ADTC + two ClinicalTrials.gov PK studies), paediatric/cystatin-C
decisions, a 16-row seed test-vector table, a decision that
`SelectFormula`'s drug-classification flags are caller-supplied
(proposed as `REQ-RENAL-7`), and a new `ComposedCeiling` function
resolving `REQ-RENAL-5`'s bound-composition question against
`dosage.dfy`'s actual (checked) signature.

Verified every checkable factual claim independently rather than
accepting the document on its word, per this repo's standing discipline:

- `dosage.dfy`'s quoted signature matched the real file exactly.
- MHRA's BMI threshold ("BMI <18 kg/m2 or >40 kg/m2," strict inequality)
  confirmed by direct WebFetch of the primary MHRA page itself — a
  stronger, simpler citation than the document proposed (NHS Tayside was
  offered as the source; Tayside turned out to be a secondary
  restatement of the same MHRA text, itself confirmed by pulling and
  reading the actual Tayside PDF page image after WebFetch's
  text-summarization pass initially missed the content inside a
  bulleted table graphic — a real tool-reliability gap worth
  remembering). The two ClinicalTrials.gov NCT citations (NCT02942810,
  NCT02039817) checked via the Clinical Trials MCP: both real, both use
  a similar BMI range, but as general PK-study eligibility screening,
  not as validation of MHRA's specific rule — downgraded from "confirms"
  to "corroborates" in the committed record.
- Inker et al.'s 2021 NEJM cystatin-C equation citation (PMID 34554658)
  checked via PubMed: exact title, journal, volume/issue/pages, and DOI
  match.
- `ComposedCeiling`, and (going further than the document itself did)
  `RoundHalfUp`, `GStage`, and `SelectFormula` were each written to a
  scratch `.dfy` file and run through the real, installed Dafny 4.11.0
  toolchain (`dafny verify`) rather than accepted as hand-reasoned
  contract shapes. All four verify cleanly, 1 verified / 0 errors each.

One real conflict caught, not silently merged: the document's proposed
`REQ-RENAL-7` (classification-flag provenance) collided with the
`REQ-RENAL-7` already committed in this repo (BSA de-normalization, from
KDIGO Practice Point 4.2.4, committed before the document arrived).
Renumbered the new one to `REQ-RENAL-8` and recorded the collision and
the fix explicitly in `PHASE1_PLAN.md` rather than overwriting silently.

Folded all of this into `examples/renal_adjustment/PHASE1_PLAN.md`
(closed requirements table through `REQ-RENAL-8`, settled the
paediatric/cystatin-C/rounding decisions, added the 16-row Gate 1c
test-vector table, the verified `ComposedCeiling` interaction contract)
and `examples/renal_adjustment/gate_c1_sketch.md` (all four functions
now marked verified with their checked candidate bodies), plus a new
source file `sources/mhra-renal-formula-selection-2019.md`. Updated
`sources/README.md`, `KNOWN_LIMITATIONS.md`, and this roadmap doc's
status section to match.

**Gate 1c's hand-trace write-up remains the one open item to formally
close Gate 1** — the test-vector table it needs now exists, but the
audit document itself hasn't been written. One new open item,
`REQ-RENAL-8`'s classification-flag provenance (who sets the flags, by
what process), needs its own scoping pass before Phase 2 can start.
138 tests still passing; no code touched (Dafny checks were scratch
files, not committed artifacts).

## 2026-07-08 — Renal Function Dose Adjustment POC: Phase 1 Gate 1a/1b, corrected against primary sources (dab4b29 and this commit)

Steven proposed a second, independent proof-of-concept (renal-function
dose adjustment) as a final POC for submission consideration, uploading
a detailed Phase 1 scoping document. Division of labor: Steven sources
external documents, Claude plans/builds infrastructure.

Verified three concrete unknowns against the actual primary sources
rather than trusting the scoping document's summary:

- MHRA Drug Safety Update (vol. 13, issue 3, Oct 2019): reachable, mostly
  corroborated; one correction — "extremes of muscle mass" is an exact
  BMI <18/>40 threshold, not a fuzzy judgment call.
- NICE NG203: reachable, fully corroborated.
- KDIGO 2024 CKD Guideline: initially blocked (HTTP 403 from this
  environment on both listed URLs). Steven committed the PDF directly to
  the repo (`908dca5`). No PDF-rendering tool was installed here, so a
  stdlib-only (`re`+`zlib`) content-stream text extractor was written to
  recover the text without installing anything. Found: the GFR category
  table confirmed exactly as scoped; a genuinely new nuance — KDIGO's
  Table 11 rounds eGFR to the nearest whole number *before* staging,
  shifting the effective continuous G1/G2 boundary to 89.5, not the
  naive 90.0 (and similarly at every other boundary); partial resolution
  of `REQ-RENAL-3`'s citation gap (obesity/oedema corroborated by KDIGO,
  not MHRA as originally attributed; "unstable renal function" half
  never corroborated by any source, merged into `REQ-RENAL-6` instead);
  and a new candidate requirement, `REQ-RENAL-7`, from Practice Point
  4.2.4 (BSA de-normalization for narrow-therapeutic-index drugs).

Committed `sources/KDIGO-2024-CKD-Guideline.pdf`,
`sources/kdigo-2024-gfr-staging.md` (focused citation-extraction,
following the `req-gip-1-4-12` template rather than a full reformatting,
since only specific sections of a ~200-page guideline are relevant), and
updated `sources/README.md`'s Contents list (`dab4b29`).

This session: wrote `examples/renal_adjustment/PHASE1_PLAN.md`, the
formal Gate 1a/1b document — full corrected requirements table
(`REQ-RENAL-1` through `REQ-RENAL-7`), the Gate 1b spec skeleton
(preconditions, formula-selection proof target, staging/monotonicity/
fail-safe postconditions, `dosage.dfy` interaction contract), and a
decision on the rounding-then-staging design question (accept real-valued
input, prove the rounding step explicitly — not accept pre-rounded
integer input, since the former is more faithful and is exactly what
Gate C4's STPs exist to pin down). Gate 1c (internal consistency audit)
not yet run — blocked on checking Gate 1b against `dosage.dfy`'s actual
precondition structure and on Steven's answers to the still-open
questions (paediatric scope, combined creatinine-cystatin C eGFR, seed
test cases beyond the NHS SPS worked example). Updated
`KNOWN_LIMITATIONS.md` with the per-drug-factors/paediatric/cystatin-C/
REQ-RENAL-3 exclusions. No Dafny code exists yet; Phase 2 remains blocked
on Phase 1 (Gate 1c) closing, per the infrastructure plan already scoped
in `/root/.claude/plans/stateless-weaving-firefly.md`. 138 tests still
passing — no code changed, only source/doc/planning files added.

## 2026-07-07 — Gate C6 next-phase adaptation work: scoped as far as possible, then blocked and asked

Requested directly: "scope out Gate C6's next phase adaptation work."

Checked first whether the trigger condition Steven set at Gate C6
sign-off ("once there is a defensible artifact to build it on top of")
is now met: yes — `dosage.dfy` now carries a full evidence chain (Gate
C1 proof, Gate C4 STP fix, Gate C5's exhaustive mutation testing across
all five operator classes with zero survivors, Gate C6's NL sign-off).

Then tried to scope the actual work the way Gate C5's LVR extension was
scoped (real audit, real prediction, real build order) and could not:
the only description anywhere in the repo is the single sentence
recorded at Gate C6 sign-off, repeated verbatim (never elaborated) in
`nl_confirmation_dosage_dfy.md`, `DEVLOG.md`, `README.md`,
`SYSTEM_BLUEPRINT.md`, and `KNOWN_LIMITATIONS.md`. Grepped the whole
repo, including `PayloadGuard-Evidence-Blueprint-1.md`'s already-cited
FDA premarket-guidance URLs, for anything more specific - found nothing.

Rather than invent a concrete plan from one sentence, wrote the honest
scope this session could reach into
`payloadguard-evidence-roadmap-phaseB-to-C.md`'s new "Gate C6 next-phase
adaptation work" section: the trigger condition is confirmed met, and
three specific unknowns are named as blocking real scoping (what
"adapting the spec" means; what "different downstream software" refers
to; which regulatory pathway - 510(k)/De Novo/PMA/other - this targets).
This mirrors Gate C3 vector 4's own precedent in this exact repo
(specification stripping stayed BLOCKED, named, rather than guessed from
its name alone, since its source material was never available).

`KNOWN_LIMITATIONS.md` gained a pointer row. Asked Steven the three
questions directly, same turn.

## 2026-07-07 — Gate C5 LVR extension built: matched its own prediction exactly

Requested directly: "go" - following through on the scoping session
from the previous entry.

- **`evidence/dafny_mutate.py`**: `generate_lvr_mutants` (+ the
  function-body companion `_generate_function_body_lvr_mutants`).
  `_locate_clause_numeric_literal_sites` finds every `NUM`-kind token in
  a clause and pairs it with its adjacent comparison operator and which
  side it's on (refuses, Tier 1, if a literal is ever found NOT adjacent
  to a comparison - doesn't arise in this repo's real clauses, tested).
  `_locate_function_body_numeric_literal_sites` reuses a new shared
  `_function_body_tokens` helper (factored out of the existing AOR
  function-body locator, so the `//`-comment safety check lives in
  exactly one place for both AOR and LVR).
- **`_lvr_trivial`** generalizes ROR's requires/ensures polarity
  principle from operator-implication (a fixed lookup table) to
  magnitude-implication (a numeric comparison between original and
  mutant literal values): normalizes every comparison to whether
  increasing the literal narrows or widens the constraint, then applies
  the same requires-widens-informative / ensures-narrows-informative
  rule ROR already established. EQ/NE literals have no such
  relationship at all (changing an equality's target is neither a
  superset nor subset of the original in either direction) - always
  sent to verification. Function-body literals have no requires/ensures
  role to apply the principle to at all - sent straight to verification
  unfiltered too, mirroring the AOR function-body precedent.
- **Real run matched the scoping session's hand-derived prediction
  exactly, before verification even confirmed it:** generation alone
  produced 14 raw mutants, 4 filtered (`filtered_magnitude_implied`) -
  matching the predicted count and, checked individually, the predicted
  direction at every one of the 4 sites.
- **Real re-verification: all 10 real-verified candidates genuinely
  killed, zero survivors** - confirmed examples: widening
  `concentrationMgPerMl > 0.0` to `> -0.01` is killed via
  `ExpectedDose`'s own unchanged `requires > 0.0` at the pinning
  clause's call site (a precondition-call violation, not a
  postcondition failure - still a correct, real kill, worth naming
  since it's a different failure shape than most of this repo's other
  kills); both function-body literal mutants (the `< 0.0` threshold and
  the bare `then 0.0` return value) are killed because any mismatch
  between `ExpectedDose`'s mutated definition and the method body's
  unchanged, actual computation breaks the pinning clause for some input
  in the perturbed range.
- **The one named, unresolved tension from scoping** (whether the
  clinical-precision floor is the right test for REQ-GIP-1-8-1's
  exact-zero safety requirement specifically) didn't need resolving to
  get a clean result here - the function-body zero-literal mutant was
  killed at the ±0.01 granularity regardless - but the underlying
  judgment call is still open, not silently closed by this result.
- **Combined final state across all five Gate C5 operator classes: 56
  mutants - 41 killed, 6 filtered_static, 4
  filtered_chain_incompatible, 1 filtered_ar_group_incompatible, 4
  filtered_magnitude_implied - zero survived, zero unclassifiable.**
- **Tests:** `tests/test_dafny_mutate.py` grew from 19 to 25 (literal-
  site location with correct operand/side tracking on the real spec, a
  refusal test for a hypothetical non-adjacent literal, function-body
  literal-site location, a direct unit test of `_lvr_trivial` against
  hand-derived cases independent of the real spec, a check that the
  generation-time half of the prediction matches, a byte-level check on
  the targeted-literal splice). `tests/test_mutation_report.py` grew
  from 7 to 8 (locks in the real-verification half of the prediction -
  all 10 real-verified LVR candidates killed - against the committed
  capture). Full suite: **138 passed** (131 prior + 7 new). No leftover
  temp files (verified).
- Full documentation set updated to match (`KNOWN_LIMITATIONS.md`,
  `SYSTEM_BLUEPRINT.md`, the roadmap doc, this entry, README.md, the
  example's own README). `generate_artifacts.py` re-run as a sanity
  check: no observable change beyond timestamps, as expected.

## 2026-07-07 — Gate C5 LVR extension scoped (not built)

Requested directly: "scope out Gate C5's LVR extension." Full sub-plan
written into `payloadguard-evidence-roadmap-phaseB-to-C.md`, mirroring
the discipline used for Gate C5's own original scoping session and its
chain-direction/function-body-AOR extension.

- **Literal-site audit, checked empirically, not assumed:** ran the real
  tokenizer against `dosage.dfy` to enumerate every numeric literal in
  scope (5 in `CalculateHourlyDose`'s requires/ensures clauses, 2 in
  `ExpectedDose`'s function body). All 7 are exactly `0.0` — no other
  numeric constant exists anywhere in this spec.
- **Value-selection strategy:** exactly `original ± 0.01` per site (the
  clinical-precision floor sourced in the prior research session) —
  this is the first place that guidance has an actual application,
  since it was named as bounding literal/constant perturbation
  specifically, a mutation class Gate C5 hadn't built until now.
- **Static filter, reusing ROR's polarity principle:** generalized from
  operator-implication (a fixed lookup table) to magnitude-implication
  (numeric comparison between original and mutant literal values) for
  LE/LT/GE/GT-adjacent sites. Two real design points named rather than
  glossed over: EQ-literal mutation has no such filter at all (changing
  an equality target is neither a superset nor subset of the original in
  either direction); function-body literals (2 of the 7 sites) have no
  requires/ensures role to apply the principle to, so v1 would send them
  straight to real verification unfiltered, mirroring the AOR
  function-body precedent.
- **Predicted outcome recorded as a hypothesis, not a promise:** 14 raw
  mutants, 4 filtered as statically trivial, 10 sent to real
  verification, all 10 hand-predicted killed (worked through by hand for
  each site, e.g. why widening a requires clause's `> 0.0` to `> -0.01`
  should fail via `ExpectedDose`'s own unchanged precondition at the
  pinning clause's call site) — explicit that disagreement with this
  prediction at build time would itself be the finding worth reporting.
- **One named, unresolved tension:** whether the clinical-precision
  floor (sourced from dosage-*threshold* rounding practice) is the right
  test for REQ-GIP-1-8-1's *exact-zero* safety requirement specifically
  — a regulator could reasonably view any nonzero delivery on reverse
  flow as a real hazard, not clinically negligible noise. Left as an
  open judgment call for whoever builds this, not decided here.
- Reuses all existing extraction machinery
  (`_locate_clause_sites`/`_tokenize_with_spans`/`_find_function_body_span`/
  `check_precondition_satisfiability`) — the build order only needs a new
  filter rule and a new `LVR` operator label, no new extraction code.

Not built. `KNOWN_LIMITATIONS.md` gained a SCOPED table row pointing to
the full sub-plan.

## 2026-07-07 — Gate C5 extended: chain-direction-aware ROR + function-body AOR

Requested directly: "build both" - the two follow-ups named at the end
of the previous entry's research findings.

- **Chain-direction-aware ROR.** New helpers in `evidence/dafny_mutate.py`:
  `_chain_group_ids` partitions a clause's tokens into groups that never
  cross a boolean-connective or parenthesis boundary (a conservative,
  tested approximation of Dafny's actual chain-scoping rule);
  `_chain_incompatible` checks whether a candidate operator would mix an
  ascending relation with a descending one against its chain siblings
  (`==`/`!=` always compatible). Wired into `_generate_token_mutants` via
  a new `chain_aware` parameter, used only by `generate_ror_mutants`
  (`&&`/`||`/arithmetic have no analogous rule). Result: the 4 mutants
  that used to reach real Dafny invocation and come back
  `unclassifiable` are now filtered before generation ever reaches
  verification - a new `filtered_chain_incompatible` outcome, kept
  distinct from pass 1's `filtered_static` since the reason (syntactic
  invalidity vs. semantic redundancy) is genuinely different.
- **Function-body AOR, MutDafny-restricted.** `generate_aor_mutants`
  gained an optional `function_name` parameter. New helpers:
  `_find_function_body_span` (brace-matched, mirroring
  `dafny_spec_lint._find_method_header`'s depth-tracking but returning
  the body content, not the header); `_locate_function_body_arithmetic_sites`
  (refuses outright - rather than risk a misaligned offset - if the body
  contains a `//` comment; none does today, checked).
  `_TOKEN_SPAN_RE` gained `ASSIGN` (`:=`) and `SEMI` (`;`) token kinds,
  needed for body statements but never present in requires/ensures
  clauses. `_ar_group_incompatible` applies MutDafny's own restriction
  directly: `+`/`-`/`*` freely interchange, `/` only with `%` (absent
  from this spec) - a mutation can never introduce `/` where the
  original had none, closing the division-by-zero false-kill risk by
  construction. `generate_mutants` gained the same parameter; the real
  caller (`run_mutation_suite.py`) now passes `"ExpectedDose"`.
- **Real re-run, both extensions active: 42 mutants - 31 killed, 6
  filtered_static, 4 filtered_chain_incompatible, 1
  filtered_ar_group_incompatible, zero survived, zero unclassifiable.**
  The 2 new function-body mutants (`* -> +`, `* -> -`) are both
  genuinely killed - confirming `*` is load-bearing, since the method
  body's own unmutated computation then diverges from the mutated
  `ExpectedDose`'s pinning clause. No leftover temp files (verified).
- **Tests:** `tests/test_dafny_mutate.py` grew from 11 to 19 - new
  chain-direction filtering test on the real spec, direct unit tests of
  `_chain_incompatible`/`_ar_group_incompatible` against hand-derived
  cases independent of the real spec, function-body AOR generation and
  its division-free restriction, a tokenizer test for `:=`/`;`, and a
  direct test that `_locate_function_body_arithmetic_sites` finds
  exactly the one `*`. `tests/test_mutation_report.py` grew from 5 to 7
  - replaced the "4 unclassifiable, all chain-direction" regression with
  "zero survivors AND zero unclassifiable," added a direct check on the
  function-body AOR outcomes. Full suite: **131 passed** (121 prior +
  10 new).
- Full documentation set updated to match (`KNOWN_LIMITATIONS.md`,
  `SYSTEM_BLUEPRINT.md`, the roadmap doc, this entry, README.md, the
  example's own README, and the research-findings doc itself - both
  follow-ups marked BUILT rather than not-yet-built).
  `generate_artifacts.py` re-run as a sanity check: no observable change
  beyond timestamps, as expected (Gate C5 still isn't wired into the
  matrix pipeline).

## 2026-07-07 — Gate C5 research findings recorded; one mischaracterization corrected

Steven sent the external research prompt drafted earlier this session
(`gate-c5-research-prompt.md`) out and brought back a thorough,
well-sourced response covering the three open Gate C5 questions.
Recorded in full at
`examples/dosage_calculator/gate_c5_mutation_testing_research_findings.md`.

- **Correction made:** Gate C5 was labeled "MutDafny/IronSpec-style" in
  `evidence/dafny_mutate.py`'s module docstring and the roadmap doc. The
  research found this wrong - IronSpec's actual mutation-testing
  technique (Goldweber et al., OSDI'24) is a directional,
  implication-lemma-based approach (`S'(p) ⟹ S(p)`), not the brute
  verify/observe approach this module actually implements, which
  matches MutDafny (Amaral, Mendes & Campos, 2025) instead. Corrected
  the docstring and the roadmap doc's separate, also-unconfirmed
  "IronSpec's three-pass framework" attribution for the filter pipeline.
  Gate C4's own IronSpec attribution (Spec-Testing Proofs) is a
  different, correct part of IronSpec's toolkit and is unaffected.
- **Problem A (the `>=` survivor, already fixed last entry) got a name
  and real precedent:** *masking*, the MC/DC term (DO-178B/C,
  Chilenski 1994) for a sibling condition making a boundary's operator
  choice unobservable - an FAA/DO-178C-accepted pattern in the adjacent
  aerospace safety-critical field. Recorded for the historical record;
  Steven's tightening decision already resolved the underlying finding
  before this research came back.
- **Problem B (chain-direction stillborn mutants) confirmed as expected,
  not a gap:** Dafny's chaining rule is now citable directly from the
  Reference Manual (§5.2.1-5.2.2) rather than only empirically observed;
  `run_mutation_suite.py`'s comment updated to cite it.
  `dafny_mutate.py`'s `unclassifiable` bucketing strategy was
  independently confirmed to match MutDafny's own published `Invalid`-
  mutant handling - not behind the state of the art. A genuine,
  not-yet-built improvement was identified (restrict each chain link's
  mutation candidates to direction-compatible operators, eliminating
  the 4 unclassifiable mutants by construction - MutDafny itself doesn't
  do this).
- **Problem C (deferred AOR/floating-point precision) got a concrete
  plan, not just deferred:** MutDafny's own `/`↔`%`-only AOR restriction
  directly resolves the division-by-zero attribution risk named when
  AOR was originally deferred; a sourced ≥0.01 mL/hr clinical-precision
  floor (pharmacy/nursing device-rounding practice, not a formal
  regulatory standard - the research is explicit about that distinction)
  gives a concrete cutoff for real-valued mutant magnitude, whenever
  that work is picked up.
- No code changes beyond the docstring/comment corrections named above;
  no rebuild triggered by this research since the one thing it bore on
  directly (the Problem A survivor) was already fixed in the prior
  entry. Full suite unaffected: **121 passed**, unchanged.

## 2026-07-07 — Gate C5 survivors fixed: REQ-GIP-1-8-1 tightened to `>`

Requested directly, following an out-of-band status message that
falsely claimed the repo was in an early, mostly-empty state (no Phase
B, DEVLOG last dated 2026-07-04) - verified directly against git (local
`main` matched `origin/main` exactly at the real HEAD) and file content
(README/DEVLOG both showed the real, current state) before responding;
flagged the discrepancy rather than acting on it. The user's actual
prior request - interrupted mid-response before this - was "go ahead and
tighten REQ-GIP-1-8-1 to >"; confirmed and executed once the false
status claim was cleared up.

- **`dosage.dfy`:** `ensures infusionRateMlPerHr >= 0.0 || dose == 0.0`
  → `ensures infusionRateMlPerHr > 0.0 || dose == 0.0`. Header comment
  gained an inline note (alongside the existing Gate C4 fix note)
  explaining the Gate C5 finding and fix. Re-verified clean: `2
  verified, 0 errors`, unchanged from before the tightening.
- **STP suites re-verified for real, not assumed unaffected:**
  `dosage_stp_suite.dfy` (includes the changed `dosage.dfy`) still
  verifies clean, `10 verified, 0 errors`, unchanged.
  `dosage_stp_suite_against_underconstrained.dfy` (includes the
  untouched, preserved `dosage_underconstrained.dfy`) still correctly
  fails, `0 verified, 2 errors`, unchanged - both re-captured via their
  existing runner scripts; only the manifests' timestamps changed.
- **Mutation suite re-run in full** (`run_mutation_suite.py`, real
  Dafny invocations, ~45s): **zero survivors remain.** The two former
  survivor mutations (`> -> >=`, `> -> !=`, previously `>= -> !=`,
  `>= -> >`) are now correctly recognized by the pass-1 static filter as
  trivially uninteresting *before* Dafny is even invoked - a proof of
  `x > 0` universally implies both `x >= 0` and `x != 0` - which is
  itself a clean, mechanical confirmation that the boundary is now
  tight, not just an assertion. New counts: killed=29 (unchanged),
  filtered_static=6 (up from 4), unclassifiable=4 (unchanged, unrelated
  chain-direction parse-error gap), survived=0 (down from 2).
  `mutation_report.json`/`.md` and `run_manifest_mutation.json`
  regenerated to reflect the real re-run.
- **Gate C6 sign-off amended, not overwritten:** the original
  2026-07-07 sign-off record
  (`examples/dosage_calculator/nl_confirmation_dosage_dfy.md`) stays
  intact as history; a new "Amendment" section records the Gate C5
  finding, Steven's tightening decision, the regenerated plain-English
  summary (only postcondition 3's gloss changed, `is at least` → `is
  greater than`), and treats it as re-confirmed on the same basis as the
  original sign-off.
- **Tests updated to match the new real reality, not just made to
  pass:** `tests/test_dafny_nl_summary.py` (the reverse-flow-clause
  citation test now matches on `> 0.0`), `tests/test_dafny_mutate.py`
  (filtered-mutant count 4→6, LOR's expected mutated clause text,
  renamed/expanded the equality-clause-filter test to also cover the
  now-tightened reverse-flow clause's own filtered mutations),
  `tests/test_mutation_report.py` (replaced the "2 named survivors"
  regression test with a "zero survivors, and the two former survivor
  mutations are now filtered_static" regression test - so a future
  regeneration can't let a survivor quietly reappear without a test
  failing). Full suite: **121 passed**, same count as before (no tests
  added or removed, only updated).
- Full documentation set updated to match (`KNOWN_LIMITATIONS.md`,
  `SYSTEM_BLUEPRINT.md`, the roadmap doc, this entry, README.md, the
  example's own README). `generate_artifacts.py` re-run as a sanity
  check: no observable change beyond timestamps, as expected (Gate C5
  still isn't wired into the matrix pipeline).

## 2026-07-07 — Gate C5: built for v1 scope, 2 real survivors found

Requested directly, same day as the scoping session: "build it and be
careful with Dafny. just. we can consider floating points later..it's a
known but solvable issue." Read as: build the core (ROR/LOR/COI on
requires/ensures clauses) now, defer the AOR/division-by-zero risk named
in the scoping doc. A later message added guidance for that follow-up:
"we can consider bounding floating points within the terms of accuracy.
if we're dealing with an integer 1*10^10, then we don't have to be any
more accurate that accuracy requires" — recorded, not acted on in this
build.

- **`evidence/dafny_mutate.py`** — `generate_ror/lor/aor/coi_mutants()` +
  `generate_mutants()`. Reuses `dafny_nl_summary._CLAUSE_LINE_RE` (Gate
  C6's single-line clause convention) and `dafny_spec_lint._find_method_header`.
  A local span-preserving tokenizer extends `dafny_spec_lint`'s token
  grammar with one addition (a COMMA token, needed for the pinning
  clause's `ExpectedDose(a, b, c)` function-call syntax) - safe here
  specifically because mutation only relocates operator TEXT, it never
  needs to understand what an expression means the way Z3 translation
  does, so tolerating syntax the Z3 translator correctly refuses can't
  mistranslate anything.
- **Pass-1 static filter, the design point most likely to be silently
  wrong in one direction:** a mutant is skipped when a fixed relational-
  implication table proves it's guaranteed uninteresting - but the
  trivial DIRECTION flips by clause role. Weakening is trivial for
  `ensures` (whatever satisfies the original satisfies a logically
  weaker consequence too); *strengthening* is trivial for `requires`
  (the original proof still applies under a narrower hypothesis) - the
  informative direction for `requires` is weakening it. Verified against
  a synthetic spec independent of `dosage.dfy`'s specific content
  (`test_ror_polarity_flips_between_requires_and_ensures`), since this
  is the one place getting the direction backwards would silently filter
  out exactly the mutants worth testing.
- **Passes 2-3 reused directly, as scoped:** pass 2 (vacuity filtering
  for `requires` mutants) calls `dafny_spec_lint.check_precondition_satisfiability`
  against the mutated source with no new Z3 code. Pass 3
  (`examples/dosage_calculator/run_mutation_suite.py`) mirrors
  `run_verify_dafny.py`'s capture discipline and reuses `dafny_adapter`'s
  `_SUMMARY_RE`/`_INCOMPLETE_MARKERS` per mutant.
- **Real run: 39 mutants against `dosage.dfy::CalculateHourlyDose`** - 29
  killed, 4 filtered as statically trivial, **2 survived**, **4
  unclassifiable**. Mutant `.dfy` files are not committed individually
  (mechanically derived, unlike the STP suites' hand-authored artifacts);
  the real per-mutant outcome is `mutation_report.json`/`.md` +
  `run_manifest_mutation.json`.
- **The 2 survivors - a real finding, reported not silently fixed.**
  `infusionRateMlPerHr >= 0.0 || dose == 0.0` with the first disjunct's
  `>=` mutated to `!=` or `>` both still verify (`2 verified, 0 errors`,
  confirmed by direct re-run). Root cause worked out and checked: at
  `infusionRateMlPerHr == 0.0` exactly, real multiplication makes
  `rawDose == 0.0` exactly, so `dose == 0.0` already holds at that
  boundary independent of the first disjunct's operator - a real
  looseness in REQ-GIP-1-8-1's postcondition. **`dosage.dfy` is the spec
  Steven signed off on in Gate C6 the same day** - this finding is
  reported for his decision (tighten vs. accept-and-document), not
  unilaterally changed.
- **The 4 unclassifiable results - a real mutation-engine gap, not a
  spec finding.** All 4 come from mutating one side of the chained
  `0.0 <= dose <= maxSafeDoseMgPerHr` clause to a descending operator
  (e.g. `0.0 >= dose <= maxSafeDoseMgPerHr`); confirmed by direct re-run
  that Dafny's own PARSER rejects this (`this operator chain cannot
  continue with an ascending/descending operator`, exit code 2) - a real
  Dafny language rule the engine doesn't yet model. Correctly refused
  (Tier 1) rather than misclassified: `_classify` only accepts exit
  codes 0/4, relays Dafny's own error line (temp filename scrubbed for
  report determinism) as detail. Named as a real, scoped follow-up, not
  fixed in this pass.
- **AOR/SOR/HOR out of v1 scope, checked not assumed.** SOR/HOR aren't
  implemented at all - `test_sor_and_hor_not_applicable_confirmed_by_absence_of_syntax`
  greps `dosage.dfy` for set/heap syntax and asserts none present. AOR
  is implemented and exercised (asserted `== []` against the real spec,
  not just left untested) - its one site lives in `ExpectedDose`'s
  function body, out of clause-mutation scope, deferred with the
  division-by-zero risk per the guidance above.
- **Tests:** `tests/test_dafny_mutate.py` (11, pure generation/filter
  logic, no Dafny invocations) + `tests/test_mutation_report.py` (5,
  validates the committed real capture rather than re-running 39 Dafny
  invocations per test pass - the two survivors and four unclassifiable
  entries are pinned by exact description so a regeneration can't
  silently lose or gain one). Full suite: **121 passed** (105 prior +
  16 new).

## 2026-07-07 — Gate C5: mutation testing, scoped (not built)

Requested directly: "scope out C5 please."

Per this repo's build discipline (Gate 2's CONFLICT rule, Gate C4's STPs)
a piece this size gets a written sub-plan and explicit go-ahead before
code — the roadmap's own original note already called Gate C5 "the
largest single piece" and recommended treating it as its own multi-step
sub-plan. Full sub-plan written into
`payloadguard-evidence-roadmap-phaseB-to-C.md`'s Gate C5 section,
replacing the prior one-paragraph sketch. Key content:

- **Operator applicability audited against the real spec**, not assumed
  generically: ROR (~8 comparison sites) and AOR (the single `*`) apply
  directly; LOR applies to exactly one explicit `||`
  (`infusionRateMlPerHr >= 0.0 || dose == 0.0`); COI applies to all 3
  `ensures` clauses via a negate-and-reverify check (a coarser "does this
  clause constrain anything at all" question, distinct from the other
  four's "is this specific boundary load-bearing"). SOR and HOR are
  explicitly NOT APPLICABLE — `dosage.dfy` has no sets and no heap state
  anywhere — named as a checked exclusion (same treatment as REQ-DOSE-003's
  exclusion from this same spec), not silently skipped.
- **A named risk:** AOR's `/` mutant may fail verification for an
  unrelated reason (Dafny's own division-by-zero check, confirmed real
  during Gate C1) rather than because the postcondition caught the
  weakening — the harness must attribute *why* a mutant failed, not just
  pattern-match "verification failed" as a correct kill, or it risks
  reporting a false-confidence finding.
- **Architecture reuses existing infrastructure** rather than building
  fresh: `dafny_spec_lint.py`'s tokenizer/parser as the mutation target
  grammar (needs a small, named, span-preserving extension - the existing
  tokenizer discards character positions since it only ever needed to
  build Z3 expressions, not reconstruct source text);
  `check_precondition_satisfiability` reused directly for IronSpec's pass
  2 (vacuity filtering); re-verification (pass 3) mirrors
  `run_verify_dafny.py`'s capture pattern and `dafny_adapter.py`'s
  false-zero-guarded parser.
- **Six-step build order specified**, ending in a committed report
  enumerating every mutant, its operator class, target clause, and
  outcome — same "real capture, not smoothed over" discipline as the STP
  suites.

Not built. `KNOWN_LIMITATIONS.md` gained a SCOPED table row pointing to
the full sub-plan.

## 2026-07-07 — Gate C6: NL-dialogue confirmation, built and signed off

Requested directly: "gate C6 first please" (choosing it over Gate C5,
which was not requested).

- **Built.** `evidence/dafny_nl_summary.py::summarize_method(source,
  method_name)` — deliberately not a natural-language generator. Extracts
  each requires/ensures clause verbatim (ground truth) plus any `REQ-ID`
  cited in a trailing `//` comment, exactly as authored, alongside a
  best-effort English gloss via a small fixed operator-substitution table
  (`&&`/`||`/`==>`/`<==>`/comparisons → words) — explicitly a template,
  not comprehension; the raw clause is always shown first. Reuses
  `evidence/dafny_spec_lint.py`'s Gate C3 parsing surface
  (`_find_method_header`, `_parse_params`, `extract_requires_clauses`,
  `extract_ensures_clauses`) rather than reimplementing Dafny parsing.
  Citation extraction needed a separate, comment-preserving line-based
  scan (`_extract_annotated_clauses`), since the existing extractors
  strip comments before this module sees the text.
- **Scope boundary, checked not assumed.** Only single-line clauses are
  supported. `summarize_method()` cross-checks its own line-based
  extraction against `dafny_spec_lint`'s canonical, multi-line-capable
  extractor and refuses (`SystemExit`, Tier 1) on any mismatch.
- **Self-caught bug.** The first draft of that refusal check compared
  clause *counts*, not content. Manual testing against a synthetic
  multi-line `requires x > 0\n  && x < 100` clause found it didn't raise —
  both extractors returned the same count (1) even though the line-based
  scan had silently truncated to just `x > 0`, dropping the continuation,
  while the canonical extractor correctly joined the whole clause. Same
  count, silently wrong content. Fixed by comparing whitespace-normalized
  clause text instead of counts; caught and corrected before the test
  suite was even written, matching this repo's "verify empirically,
  don't assume" discipline (e.g. Gate C4's self-caught 500.0-vs-50.0
  wrong-value mistake).
- **Tests.** 7 new tests in `tests/test_dafny_nl_summary.py`: real
  `dosage.dfy` parameters/preconditions listed correctly; each
  postcondition cites the right requirement, or explicitly "no
  requirement cited" for the pinning clause (the load-bearing property —
  a wrong citation is the exact defect class this gate exists to catch);
  operator gloss; the multi-line refusal regression; a no-clauses method
  still summarizes; output is byte-identical across repeated calls. Full
  suite: **105 passed** (98 prior + 7 new).
- **The sign-off itself — the gate's actual deliverable.** The generated
  summary for `dosage.dfy::CalculateHourlyDose` was presented; the
  `AskUserQuestion` tool failed with a stream error (this session turned
  out to be non-interactive), so the question was asked as plain text
  instead. Steven replied via a separate screenshot: "it's good for the
  spec as is," confirming the summary matches intent, and flagged a
  next-phase item (adapting the spec and explaining, for a regulatory
  submission, how results get analyzed by downstream software) as
  separate follow-up work, explicitly scoped out until "a defensible
  artifact" exists. Recorded in
  `examples/dosage_calculator/nl_confirmation_dosage_dfy.md`, mirroring
  `sources/req-gip-1-4-12-alarm-scope-decision.md`'s pattern.
- **Explicitly not done.** Not wired into `build_matrix()` or any
  generator — matches the roadmap's own framing of Gate C6 as a process
  habit, not an automated check. The next-phase adaptation/regulatory-
  analysis work Steven flagged is not started.

Commits: `b6a5810` (generator + tests, pushed before sign-off arrived,
since the code itself was fully verified and didn't need to wait on the
human decision it feeds).

## 2026-07-07 — Gate 2/C2-C4 wiring extended to variants A and B

Requested directly, same day as the variant-C-only wiring: "go ahead and
extend variant A and B now."

- **Declarations.** `metadata.a.yaml` gained `- method: dafny,
  spec_target: "dosage.dfy", dafny_method: "CalculateHourlyDose"` in
  REQ-GIP-1-4-12/REQ-GIP-1-8-1's `evidence` lists - the same declaration
  style Gate 4/5 already established. `evidence/schema/metadata.schema.a.json`
  gained the matching `dafny` enum value + `spec_target`/`dafny_method`
  conditional (identical fix to schema.c.json's). `metadata.b.yaml`
  gained two new shadow pseudo-requirements, `REQ-GIP-1-4-12.formal-1`
  and `REQ-GIP-1-8-1.formal-1`, `implementation: "dosage.dfy::CalculateHourlyDose"`
  - the same shadow pattern concrete evidence uses, distinguished as a
  dafny shadow by the `.dfy` file extension, no new declared field.
  `evidence/schema/metadata.schema.b.json`'s shadow-id pattern extended
  from `\.concrete-[0-9]+` to `\.(concrete|formal)-[0-9]+` to allow it.
- **Binders.** `_bind_declared` (A) and `_bind_shadow` (B) both gained
  an optional `dafny_store` parameter - but unlike variant C's
  symbolic/concrete sub-views, a requirement declaring dafny evidence
  with no `dafny_store` provided at all is refused outright
  (`SystemExit`), not silently skipped: A/B have no "legitimately
  excludes dafny" concept, since their single artifact renders every
  declared evidence type together. `_bind_shadow` distinguishes a dafny
  shadow from a concrete one by checking whether the implementation
  file ends in `.dfy`. `_shape_flattened_shadow` gained the same
  `verifier_completion_status` field `_shape_method_partitioned` already
  carried, load-bearing for ruling R3's row-level check.
- **CONFLICT Type 1 generalized, and a real bug fixed along the way.**
  `_declared_concrete_bindings` previously treated every shadow row's
  implementation suffix as a concrete test_id unconditionally - a dafny
  shadow's `dafny_method` would have been mis-parsed as a bogus test_id
  and crashed with a false "declared test_id not found" error. Fixed to
  skip `.dfy`-suffixed shadow rows. A new `_declared_dafny_bindings`
  generator unifies dafny's two declaration shapes (A/C's evidence list,
  B's `.dfy` shadow rows) the same way concrete evidence's own generator
  already does; `dafny_binding_conflicts` was rewritten to use it.
- **Intent parity required extending dafny_store beyond "c-formal".**
  `generate_matrix_c.py` now passes `dafny_store` to ALL THREE of its
  `build_matrix()` calls, not just `"c-formal"` - `derive_intent()` runs
  inside each call using that call's own bound records, so
  `c-symbolic`/`c-concrete` would otherwise keep computing
  `intent_ok = False` for the two now-proven requirements while A/B/
  formal say `True`, genuinely breaking the fact-equality gate. Their
  RENDERED rows are unaffected either way - only internal intent
  computation changes. Only `"c-formal"`'s header advertises the dafny
  tool version.
- **The fact-equality gate required two real changes.**
  `evidence/reconcile.py::VARIANT_ARTIFACTS` now includes
  `traceability_matrix.formal.json` as a full fifth member.
  `facts_c` is now the union of symbolic, concrete, AND formal. The
  intent comparison changed from strict dict equality to **subset
  comparison**: `formal.json` will *permanently* lack an opinion about
  REQ-DOSE-003 (`dosage.dfy`'s own header comment explicitly excludes
  it - a durable scope boundary, not a temporary gap), so requiring
  identical dicts was never going to hold once C was folded in for
  real. New rule: every requirement a view has an opinion about must
  match the reference exactly; a view may have no opinion about a
  requirement it doesn't cover; a completely unknown requirement id is
  still a hard failure (in practice caught even earlier, by the facts
  check). The temporary `run_formal_check`/`KNOWN_FORMAL_INTENT_DIVERGENCE`
  carve-out built for the C-only phase is retired - deleted from
  `evidence/reconcile.py`, its call removed from `regenerate_all.py`.
- **The CLI needed `--dafny-captures`, and this was not optional.** Once
  metadata.a.yaml/b.yaml declared dafny evidence,
  `python -m evidence.cli build --variant a ...` genuinely broke - a
  real regression this extension would otherwise have introduced.
  `evidence/cli.py` gained `--dafny-captures <index.json>`: a small JSON
  file mapping `"{spec_target}::{dafny_method}"` keys to *paths*
  (relative to the index file's own directory), not inlined file
  content - keeps the index small and hand-readable.
  `examples/dosage_calculator/dafny_captures_index.json` is the real,
  committed index. `"c-formal"` was also added to the CLI's variant
  choices (deferred in the C-only build, needed now).
- **The result:** every variant artifact - A, B, C-symbolic, C-concrete,
  C-formal - now reports `intent_ok: true` for both REQ-GIP-1-4-12 and
  REQ-GIP-1-8-1. `run_gate()`'s facts count is **9**, not 7.
- **Tests:** `tests/test_dafny_wiring.py` rewritten substantially (real
  A/B PROVEN records checked directly; the full fact-equality gate
  checked to pass with intent True everywhere; the subset-vs-strict-
  equality fix exercised directly with both a legitimate-absence case
  and a real-mismatch case; CLI `--dafny-captures` round-trips for a/b
  and the CLI's refusal without it confirmed real, not hypothetical).
  `tests/test_cli.py` and `tests/test_fact_equality.py` updated for the
  new committed reality (5 CLI variants now, including "c-formal"; facts
  9 not 7; intent True not False). Full suite: **98 passed**. Full
  `generate_artifacts.py` pipeline re-run end to end: PASS.
- **Docs:** `examples/dosage_calculator/README.md` gained a 2026-07-07
  amendment (the prior claim that Dafny "is not wired in this phase" was
  specific to the frozen base matrix, which is still accurate and
  unchanged - clarified rather than deleted); `RECONCILIATION.md` gained
  a pointer note that its historical facts/intent figures (7 facts,
  REQ-GIP-1-4-12/1-8-1 false) describe the Phase A/B state, preserved
  unedited as the record of what ruling R1 verified at the time.

## 2026-07-07 — Gate 2/C2-C4 wiring: first real Dafny-sourced PROVEN row ever rendered

Requested directly: "we need z3 integration and invocation in order to
reach PROVEN status, in concurrence with gate 5 extension." The single
highest-stakes change to this repository's structural guarantees since
ruling R1 - the first time PROVEN would ever appear in a live rendered
row, something R1->R2->R2c->R3 has guarded since Phase A. Three design
decisions were confirmed with Steven before building, not guessed at:

- **Scope: variant C only, for now.** "hmm. can we post hoc verify A and
  B after C variant is proven?" - variants A and B are deliberately,
  explicitly deferred. This creates a real, temporary cross-variant
  intent divergence, named and tracked below, not silently permitted.
- **The Z3 gate lives inside the binder itself** (`dafny_record()`),
  mirroring how `symbolic_record`/`concrete_record` already refuse on
  failed captures internally - not a separate pipeline stage.
- **Metadata declares the dafny evidence explicitly**
  (`evidence: [{method: dafny, spec_target: ..., dafny_method: ...}]`),
  consistent with Gate 4/5's existing declaration pattern, cross-checked
  by a new Gate 2 CONFLICT Type 1 sub-check rather than bound
  unconditionally.

**What was built:**

- **`evidence/schema/metadata.schema.c.json`** - `method: dafny` added
  to the evidence enum, requiring `spec_target`/`dafny_method` together
  via a new `allOf` conditional (alongside the existing `concrete_test`/
  `test_id` one).
- **`examples/dosage_calculator/metadata.c.yaml`** - `evidence:
  [{method: dafny, spec_target: "dosage.dfy", dafny_method:
  "CalculateHourlyDose"}]` added to REQ-GIP-1-4-12 and REQ-GIP-1-8-1 -
  exactly the two requirements `intended_method: "PROVEN"` has named
  since Phase A/B, and exactly the two `dosage.dfy`'s own header comment
  scopes itself to.
- **`evidence/conflict.py::dafny_binding_conflicts`** - the new Type 1
  identity check: does the declared `spec_target` match the file the
  captured Dafny manifest actually verified? Deliberately a no-op when
  `dafny_store is None` (not merely falsy) - the symbolic/concrete
  variant-C sub-views, which never intend to bind dafny evidence, must
  not be penalized for metadata that also declares it for the third
  view. `run_conflict_gate` gained an optional `dafny_store` parameter.
- **`evidence/render/matrix_variants.py::dafny_record()`** - the wiring
  itself. Gates PROVEN on two independent, real checks before ever
  constructing a record: (1) Z3 precondition satisfiability
  (`evidence.dafny_spec_lint.check_precondition_satisfiability`, Gate
  C3) - refuses if unsat; (2) `parse_dafny_capture` (Gate C1) - refuses
  on any non-clean signal, already covering false-zero and the Gate C3
  vector 3 hardening. `assert_no_realized_proven`'s ruling R3 still
  independently re-checks `method`/`verifier_completion_status` at the
  matrix boundary regardless - this function satisfying both today
  doesn't change that.
- **`_bind_self_describing`** gained an optional `dafny_store` parameter:
  `None` means "this call doesn't bind dafny evidence at all" (declared
  entries silently ignored), vs. an explicit dict (even empty) meaning
  "this call does bind dafny evidence, and an unresolved declared entry
  is a real refusal." This `is not None` vs. truthiness distinction is
  what keeps `c-symbolic`/`c-concrete` behaviorally unchanged (aside from
  one new, always-null `verifier_completion_status` field added to every
  variant-C row, load-bearing for R3's row-level check) while enabling
  the new `"c-formal"` variant.
- **`generate_matrix_c.py`** now renders THREE artifacts
  (`traceability_matrix.formal.json/.md` alongside symbolic/concrete),
  assembling `dafny_store` from the real, already-committed Gate C1
  capture (`dosage.dfy`, `raw_dafny_output.txt`, `run_manifest_dafny.json`)
  - no re-running evidence inside the generation pipeline. Only the
  formal call's `tool_versions` gains a `"dafny"` key; symbolic/concrete
  stays exactly as before (confirmed by diff).
- **`evidence/reconcile.py::run_formal_check`** - a new, separate,
  narrowly-scoped check for the formal view. The existing fact-equality
  gate (`run_gate`, `VARIANT_ARTIFACTS`) is deliberately **unchanged** -
  the formal artifact isn't in that tuple, so the strict
  A==B==symbolic==concrete check keeps passing exactly as before
  (`intent {'REQ-GIP-1-4-12': False, 'REQ-GIP-1-8-1': False,
  'REQ-DOSE-003': True}`, byte-identical to before this wiring).
  `run_formal_check` instead verifies the formal view's intent_ok
  matches that reference EXCEPT a named, tracked set,
  `KNOWN_FORMAL_INTENT_DIVERGENCE = {"REQ-GIP-1-4-12", "REQ-GIP-1-8-1"}`,
  which must specifically be `True` - any other requirement diverging,
  or either named one diverging in the wrong direction, is still a hard
  failure. Wired into `regenerate_all.py` right after the main gate.
- **`generate_artifacts.py`** - the structural PROVEN sweep (stage 6)
  now explicitly sweeps `traceability_matrix.formal.json` too, proving
  ruling R3 accepts this real row inside the actual pipeline, not just
  when `generate_matrix_c.py` runs standalone. `dosage.dfy`,
  `raw_dafny_output.txt`, `run_manifest_dafny.json` added to `INPUTS`;
  the new formal artifacts added to `OUTPUTS`.

**The result:** `traceability_matrix.formal.json` - 3 rows: two real
PROVEN rows (REQ-GIP-1-4-12, REQ-GIP-1-8-1; `method: "dafny"`;
`verifier_completion_status: "completed"`; `intent_ok: true`) and the
pre-existing `system_scope` GAP row for REQ-GIP-1-4-12 (unchanged in
kind). `intent_ok` flips from `False` to `True` for both requirements in
this view - the first time since Phase A that `intended_method:
"PROVEN"` has actually been realized, not just declared.

**Tests:** `tests/test_dafny_wiring.py`, 15 tests - the real formal
artifact has exactly the two expected PROVEN rows, each satisfying R3;
passes `assert_no_realized_proven` for real; symbolic/concrete/A/B
confirmed completely unaffected (regression); `dafny_record` refuses an
unsatisfiable precondition and a broken capture (both gates
independently exercised) and accepts the real committed capture;
`dafny_binding_conflicts` catches a spec_target mismatch and a missing
capture, correctly no-ops when `dafny_store is None`; the real metadata
+ dafny store combination has zero conflicts; `run_formal_check` passes
on the real committed artifacts and correctly rejects both an unnamed
divergence and a wrong-direction divergence of a named one; an
end-to-end `build_matrix("c-formal", ...)` call matches the committed
artifact byte-for-byte. Full suite: **93 passed** (78 prior + 15 new).
Full `generate_artifacts.py` pipeline re-run end to end: PASS, including
the new formal-view check.

**Explicitly not done, and not this build's job:** variants A and B
don't bind dafny evidence at all - deliberately deferred, per the
ratified scope decision, confirmed unaffected by test rather than
assumed. The CLI (`evidence/cli.py`) was not extended with a
`"c-formal"` variant choice or a way to supply a `dafny_store` from the
command line - a separate design question that wasn't part of this ask.
No generic "wire any future Dafny spec into the matrix" tooling was
built - this wired the one path for the one spec that exists.

## 2026-07-07 — Phase C Gate C4 built: Spec-Testing Proofs found and fixed a real gap in dosage.dfy

Requested directly: "start gate C4." Applied IronSpec's methodology -
prove a specific input/output pair is accepted or rejected by the
SPECIFICATION itself, independent of any implementation - to the one
Dafny spec that exists in this repo (`dosage.dfy`, Gate C1). It found a
real gap on the first attempt, not a synthetic demonstration.

- **The finding, confirmed mechanically:** `CalculateHourlyDose`'s
  original two ensures clauses (`0.0 <= dose <= maxSafeDoseMgPerHr` and
  `infusionRateMlPerHr >= 0.0 || dose == 0.0`) bound `dose` and force it
  to 0 on reverse flow, but never relate it to the actual product of
  rate and concentration otherwise. A Dafny lemma stating "for these
  fixed inputs, if dose satisfies both ensures clauses, dose must equal
  the one correct clamped value" **failed to verify** - Dafny could not
  prove it, because the postcondition genuinely doesn't force it. A
  method that always returned `0.0` for any non-negative-rate input
  would have satisfied the exact spec Gate C1 verified clean. The same
  bug class Gate 1 found by hand for REQ-GIP-1-4-12 (spec/evidence not
  matching the requirement text), recurring independently in this
  session's own new Dafny spec - caught mechanically this time.
- **Fixed for real:** `examples/dosage_calculator/dosage.dfy` gained
  `function ExpectedDose(concentrationMgPerMl, infusionRateMlPerHr,
  maxSafeDoseMgPerHr): real` (the same three-way clamping logic as the
  method body) and a new `ensures dose == ExpectedDose(...)` clause
  pinning the output exactly. The two original ensures clauses stay,
  unchanged, for direct per-requirement traceability. Re-verified clean:
  `2 verified, 0 errors` (the function plus the method - up from `1
  verified`). **The real committed capture was re-run honestly, not
  patched:** `raw_dafny_output.txt` / `run_manifest_dafny.json` now
  reflect the fixed spec; `tests/test_dafny_adapter.py`'s exact
  `raw_status` assertion was updated to match, with a comment.
- **Preserved exhibit:** `examples/dosage_calculator/dosage_underconstrained.dfy`
  keeps the original weak spec byte-for-byte (same rationale as
  `dosage_naive_widening.py`) - it still verifies cleanly on its own (`1
  verified, 0 errors`); the bug is a spec weakness, not a verification
  failure.
- **Two STP suites, mechanically proving both directions, each
  `include`-ing the relevant spec rather than duplicating it:**
  - `dosage_stp_suite.dfy` (`include "dosage.dfy"`): six lemmas across
    the three logical branches of `CalculateHourlyDose` - normal
    in-range, ceiling-clamped, reverse-flow. ACCEPT + REJECT pairs for
    the first two; ACCEPT-only for reverse-flow (never a gap -
    `infusionRateMlPerHr >= 0.0 || dose == 0.0` already pins dose to 0
    there, even in the weak spec). All six verify: `10 verified, 0
    errors`, exit 0.
  - `dosage_stp_suite_against_underconstrained.dfy` (`include
    "dosage_underconstrained.dfy"`): the same two REJECT lemmas, run
    against the weak spec instead. Both **genuinely fail**: `0
    verified, 2 errors`, exit 4 - a real negative capture, not smoothed
    over, same discipline as `dosage_broken.dfy`.
- **A mistake caught during this build, before committing:** an early
  draft of the ceiling-clamped REJECT lemma used the raw unclamped
  product (`500.0`) as the "wrong" value. That lemma verified even
  against the weak spec - not because the weak spec pins the correct
  value, but because `500.0` already violates the weak spec's own
  `0.0 <= dose <= maxSafeDoseMgPerHr` bound directly, so excluding it
  proved nothing about the real gap. Caught by checking the lemma's
  actual behavior against the weak spec directly rather than assuming
  the chosen value was a good test; corrected to `50.0` (in-bounds,
  still wrong) in both suites, re-verified, and a regression test added
  (`test_reject_lemmas_target_in_bounds_wrong_values_not_out_of_bounds_ones`)
  guarding against silently reintroducing the weaker value.
- **New capture runners:** `run_verify_dafny_underconstrained.py`,
  `run_verify_dafny_stp_suite.py`,
  `run_verify_dafny_stp_suite_against_underconstrained.py` - all
  mirroring `run_verify_dafny.py`'s discipline, producing genuine
  committed captures, no fabricated output.
- **Tests:** `tests/test_dafny_stp_suite.py`, 6 tests, checking the real
  committed captures directly (not via `evidence.dafny_adapter.py`,
  since an STP suite's capture is a proof about the spec's tightness,
  not itself a requirement's verification evidence). Full suite: **78
  passed** (72 prior + 6 new). Full `generate_artifacts.py` pipeline
  re-run: zero observable change beyond `generated_utc` timestamps.
- **Explicitly not done, and not this gate's job:** neither STP suite is
  wired into `build_matrix()` or any generator, and no automated
  mechanism runs STPs against future Dafny specs as a matter of course -
  this gate authored one STP suite for the one spec that exists, per
  its stated scope, not a generic STP-generation tool.

## 2026-07-07 — Phase C Gate C3 built (vectors 1-3): Z3 precondition check, weak-postcondition heuristic, timeout/resource-limit masking hardened

Requested directly: "start gate c3." Four vectors were named in the
roadmap; three were scopeable and are built here, the fourth stays
blocked exactly as before.

- **Vector 1 (vacuous preconditions) - BUILT.** New module
  `evidence/dafny_spec_lint.py::check_precondition_satisfiability`:
  extracts a method's `requires` clauses (`_find_method_header` tracks
  paren depth to find the body's opening brace; `_extract_clauses`
  splits on clause keywords) and hands their conjunction to Z3 for a
  real satisfiability check. A small hand-written recursive-descent
  translator (`_tokenize` + `_Parser`) covers the boolean/comparison/
  arithmetic subset this repo's specs actually use - `&&`, `||`, `!`,
  `==>`, `<==>`, chained comparisons, `+-*/`, real/int/nat/bool
  identifiers and literals (`nat` gets its implicit `>= 0` Dafny
  semantics). Quantifiers, `old(...)`, unknown parameter types, and any
  unparseable syntax raise `SystemExit` outright - refused, never
  mistranslated.
- **Proven against a real committed fixture, not a synthetic string
  only:** new `examples/dosage_calculator/vacuous_precondition_probe.dfy`
  - a tiny, dedicated Dafny file with `requires x > 0 && x < 0` and
  `ensures r == 999999`. Verified for real against Dafny 4.11.0: **`1
  verified, 0 errors`, exit 0** - a genuine clean pass on a method whose
  precondition can never hold. The Z3 checker correctly reports `unsat`
  on the same method - catching mechanically what the verifier's own
  clean-pass report missed. A true-negative companion confirms the real
  dosage.dfy kernel's actual precondition is `sat`.
- **Vector 2 (weak postconditions) - BUILT, heuristic, best-effort, as
  the roadmap scoped it.** `scan_weak_postconditions` flags `ensures`
  clauses using `==>` without a matching `<==>`. Tested against a
  synthetic weak clause (flagged, clause text quoted verbatim), the real
  dosage.dfy spec (zero warnings - its clauses use `<=`/`==`/`||`, never
  `==>`, a true negative), and a `<==>` clause (not flagged, another
  true negative). Explicitly not a proof: it cannot decide whether a
  bi-implication was actually needed for a given spec.
- **Vector 3 (timeout/resource-limit masking) - BUILT, with a real
  empirical finding.** `dafny verify --resource-limit=1` on the real,
  committed `dosage.dfy` spec produces
  `Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource`
  - an errors count of 0 on a run that did not complete. Committed for
  real via new `run_verify_dafny_resource_limited.py`, producing genuine
  `raw_dafny_output_resource_limited.txt` /
  `run_manifest_dafny_resource_limited.json`.
- **Checked whether this is actually exploitable via exit_code alone -
  it is not, on this Dafny version.** The real captured `exit_code` is
  **4** (nonzero), so Gate C1's existing exit-code check already refuses
  this capture before the summary line is parsed. An earlier suspicion
  in this same session that the exit code was 0 here turned out to be a
  shell-scripting artifact - a piped command (`... | tail -20; echo
  "EXIT:$?"`) whose `$?` captured `tail`'s exit status, not `dafny`'s.
  Caught and corrected by re-running the same command without the pipe
  before reporting it as a finding - the "verify empirically, don't
  assume" discipline applied to my own probing, not just the tool under
  test.
- **Hardened `evidence/dafny_adapter.py` anyway, as real defense in
  depth:** the summary-line regex now captures the tail after the error
  count and refuses if it contains `"out of resource"`, `"out of
  memory"`, or `"timed out"` (case-insensitive), independent of the
  exit-code check. Of these, only `"out of resource"` was independently
  reproduced end-to-end; the other two are the confirmed sibling
  vocabulary from the same Boogie/Dafny summary-formatting code path
  (verified by extracting UTF-16 string literals directly from the
  installed `Boogie.ExecutionEngine.dll` / `DafnyDriver.dll`) but not
  independently forced to reproduce this session - named as such. Also
  hardened: the parser now refuses if a capture contains more than one
  summary-line match (checked empirically that a normal multi-file
  `dafny verify` still emits exactly one aggregate summary line, so this
  closes a theoretical ambiguity without changing real-capture behavior).
- **Vector 4 (specification stripping) - still BLOCKED, named.** No new
  source material surfaced this session either.
- **Tests:** `tests/test_dafny_spec_lint.py` (11, vectors 1-2) and
  `tests/test_dafny_timeout_masking.py` (6, vector 3) - 17 new tests.
  Full suite: **72 passed** (55 prior + 17 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change beyond
  `generated_utc` timestamps.
- **Explicitly not done, and not this gate's job:** neither the Z3 check
  nor the weak-postcondition heuristic is invoked automatically anywhere
  in the capture or generation pipeline - standalone, tested
  capabilities, matching Gate C1's own scope. Wiring them into the
  capture workflow is a natural follow-up but wasn't asked for.

## 2026-07-07 — Phase C Gate C2 built: ruling R3, PROVEN's exclusivity migration

Requested directly: "start gate C2." The design was already fully
specified in `payloadguard-evidence-roadmap-phaseB-to-C.md`'s Gate C2
section from the prior planning session - this session implemented that
ratified design rather than inventing a new one.

- **`evidence/render/matrix_variants.py::assert_no_realized_proven`** -
  previously hard-failed if ANY record anywhere claimed PROVEN, full
  stop (ruling R2). Now implements ruling **R3**: PROVEN may appear as a
  realized strength only when a record's `method == "dafny"` **and**
  its `verifier_completion_status == "completed"` - both conditions
  required, not just a matching method label. Every other method -
  `crosshair`, `concrete_test`, or a record with no method at all (e.g.
  a scope-GAP row) - remains permanently, unconditionally excluded,
  exactly as under R2. Refactored into a shared `_assert_proven_gate`
  helper checked against both each row's `evidence` list (variant A's
  shape) and the row itself (variant B/C's flat shape).
- **Why both conditions, not just the method label:**
  `evidence/dafny_adapter.py::parse_dafny_capture` (Gate C1) is already
  structurally incapable of returning PROVEN unless its own exit-code,
  summary-line, and false-zero checks all passed - so in the adapter's
  own output the two conditions are always true together. R3 checks
  both anyway, at the matrix boundary, as defense in depth against a
  future binder assembling a Dafny-shaped record by hand instead of
  through the adapter, rather than trusting the method label alone.
- **`tests/test_proven_exclusivity.py`** - 8 new tests. The roadmap
  named two required cases; this build has both plus more:
  1. Positive - a real Dafny PROVEN record, produced via
     `parse_dafny_capture` against the real committed clean capture (the
     same one Gate C1 verified), is accepted.
  2. Negative, crosshair - a `method="crosshair"` record with
     `strength="PROVEN"` and a completed status is refused, checked
     explicitly with a real fixture, not inferred from the absence of a
     binder that would produce one.
  3. Negative, concrete_test - same property, the other permanently-
     excluded method.
  4. Negative, missing method - a record with no `method` key at all is
     refused, not silently accepted because there's nothing to compare
     against `"dafny"`.
  5-6. Negative, dafny method without a completed status (`None` and an
     explicit `"incomplete"` value) - the method label alone is not
     trusted; defense-in-depth, not redundant paranoia.
  7. Row-level shape - variant B/C's rows carry `strength`/`method`
     directly, not nested in an `evidence` list; confirmed the same
     rule applies there too.
  8. Regression - all four committed matrix artifacts (none of which
     contain a dafny record today) still pass unchanged.
- **Existing structural tests needed no changes:**
  `tests/test_structural_proven_check.py`'s corruption cases (a
  `crosshair`-method record forced to `PROVEN`) still raise under R3
  with the identical error-message substring - confirming R3 is a
  strict, narrow relaxation for one specific checked case, not a
  broadening of the rule in general.
- Full suite re-run: **55 passed** (47 prior + 8 new). Full
  `generate_artifacts.py` pipeline re-run: zero observable change to any
  committed matrix artifact beyond `generated_utc` timestamps - R3 has
  no effect on the live pipeline today, since no binder yet produces a
  dafny-method record.
- **Explicitly not done, and not this gate's job:** no binder
  (`_bind_declared`, `_bind_shadow`, `_bind_self_describing`) was
  changed to actually assemble a Dafny-sourced record into a live matrix
  row. R3 makes that *possible* without violating the structural gate;
  it does not make it *happen*. Per the roadmap's suggested build order,
  that wiring belongs alongside Gate C4 (STPs, "alongside the first real
  spec"); trusting a live PROVEN claim in earnest still waits on Gate C3.

## 2026-07-07 — Phase C Gate C1 built: real Dafny spec, capture runner, false-zero-guard adapter

Requested directly: "I need the C1 local build implementation" - not
just the toolchain research from the day before, the actual gate build.

- **`examples/dosage_calculator/dosage.dfy`** - a real Dafny method,
  `CalculateHourlyDose`, translated from `dosage.py`'s contracts
  (mirrors the clamping shape: `requires concentrationMgPerMl > 0.0`,
  `requires maxSafeDoseMgPerHr > 0.0`, `ensures 0.0 <= dose <=
  maxSafeDoseMgPerHr`, `ensures infusionRateMlPerHr >= 0.0 || dose ==
  0.0`). Verified for real against Dafny 4.11.0: `Dafny program
  verifier finished with 1 verified, 0 errors`, exit 0.
- **REQ-DOSE-003 explicitly scoped out of the Dafny spec** - checked,
  not assumed: `y := x / 0.0` on Dafny's `real` type is itself a
  flagged verification error, not a silent `inf`. Dafny reals are
  exact/arbitrary-precision with no IEEE overflow/infinity/NaN concept
  at all, so "finite result under overflow" cannot be faithfully stated
  as a Dafny postcondition. Named here as a deliberate exclusion rather
  than silently dropped or wrongly claimed proven. `weight_kg` also
  intentionally omitted (unused precondition-only guard in the Python
  original).
- **`dosage_broken.dfy`** - the Sample-B-equivalent broken variant
  (clamp removed). Fails for real: `0 verified, 2 errors`, exit code 4
  (not 1 - confirms the exit-code finding from the prior day's
  toolchain research, now exercised on the actual dosage spec).
- **`run_verify_dafny.py` / `run_verify_dafny_broken.py`** - capture
  runners mirroring `run_verify.py` exactly: subprocess `dafny verify`,
  commit verbatim stdout+stderr and a run manifest (tool, tool_version,
  command, exit_code, started_utc, target). Both run for real, producing
  genuine committed captures - `raw_dafny_output.txt`,
  `run_manifest_dafny.json`, `raw_dafny_output_broken.txt`,
  `run_manifest_dafny_broken.json`. No fabricated output anywhere.
- **`evidence/dafny_adapter.py::parse_dafny_capture`** - the false-zero
  guard, sharpened beyond the originally-planned substring floor.
  Parses the verifier's own summary line via regex (`Dafny program
  verifier finished with (\d+) verified, (\d+) errors?`) and checks the
  parsed error count - never a blind `"0 errors" in raw_output`
  substring match, which a printed error message could coincidentally
  contain. Refuses, in order: nonzero exit code (cheapest, checked
  first); no summary line found (a crash, timeout, or a `dafny audit`-
  style "did not attempt verification" message must not be silently
  treated as success just because exit_code happens to be 0); nonzero
  parsed error count. `evidence/model.py` gained
  `verifier_completion_status: Optional[str] = None` on
  `VerificationResult` (purely additive).
- **`tests/test_dafny_adapter.py`** - six tests, all passing. One found
  and fixed an incorrect test expectation during writing: the real
  broken capture's `exit_code=4` triggers the exit-code refusal before
  the summary line is ever parsed, so
  `test_refuses_real_committed_broken_capture` was corrected to expect
  `"does not report a clean pass"` (not a summary-line error match).
  The load-bearing regression,
  `test_false_zero_guard_is_not_fooled_by_a_substring_trap`, constructs
  raw output containing the literal substring `"0 errors"` in an
  unrelated sentence plus a real summary line reporting `3 verified, 2
  errors`, and confirms the parser correctly refuses where a blind
  substring check would have wrongly passed. A sixth test,
  `test_producing_a_proven_result_does_not_reopen_the_matrix_gate`,
  builds a fake matrix row from this adapter's real `Strength.PROVEN`
  output and confirms `assert_no_realized_proven`
  (`evidence/render/matrix_variants.py`) still hard-blocks it.
- **Explicitly not done, and not this module's job:** `dafny_adapter.py`
  is not called from `build_matrix()`, any `generate_matrix_*.py`
  script, or the CLI. Wiring a Dafny-sourced PROVEN result into the
  matrix pipeline is Gate C2's job by name (the PROVEN-exclusivity
  migration), still unbuilt.
- Full suite re-run after the build (47 passed) and the full
  `generate_artifacts.py` pipeline re-run, confirming zero observable
  change to existing committed matrix artifacts beyond `generated_utc`
  timestamps.

## 2026-07-06 — SessionStart hook: make the Dafny/Python toolchain reproducible

The toolchain research below only held for this session's container.
Requested directly: set it up so a future session doesn't have to redo
it from scratch.

- Added `.claude/hooks/session-start.sh` (registered in
  `.claude/settings.json`, synchronous mode): installs the Python deps
  (`crosshair-tool`, `jsonschema`, `pyyaml`, `pytest` - per README's
  "Running it") and the .NET/Dafny toolchain (`dotnet-sdk-8.0` via apt,
  then `dotnet tool install --global dafny --version 4.11.0` via NuGet).
- **Dafny is pinned explicitly to 4.11.0**, not "latest" - the exact
  version this session verified the false-zero note, exit-code
  behavior, and the vacuous-precondition risk against. An unpinned
  install could silently pick up a different Dafny version with
  different output conventions in a future session, undermining
  everything just verified. Matches the `crosshair-tool 0.0.107`
  pinning discipline already established for CrossHair.
- Idempotent: checks `command -v dotnet` / the installed Dafny version
  before doing any apt or dotnet work, so a warm container (already
  provisioned) skips straight through.
- **Validated, not assumed:** ran the hook directly
  (`CLAUDE_CODE_REMOTE=true ./.claude/hooks/session-start.sh`) - exit 0,
  ~1.4s on the already-provisioned path (this session), correctly
  skipped reinstalling. Confirmed `dafny --version` resolves to
  `4.11.0` via the hook's `$CLAUDE_ENV_FILE` PATH export, then ran the
  full test suite (41 passed) and one targeted test file individually,
  both immediately after sourcing that same env file - the same PATH a
  fresh session would inherit.
- No linter is configured in this repository (no `.flake8` / `ruff.toml`
  / CI workflow found) - that validation step from the skill's workflow
  doesn't apply here; noted rather than skipped silently.
- Not yet re-validated from a genuinely cold container (this session
  already had dotnet/Dafny installed from the prior research) - the
  from-scratch apt+dotnet-tool install path was exercised manually
  earlier this session and confirmed to work; the hook runs the
  identical commands.

## 2026-07-06 — Phase C Gate C1: Dafny toolchain blocker resolved (modern Dafny obtained)

Requested directly: research whether a modern Dafny is obtainable rather
than settling for the ancient apt package or asking for an
under-informed decision.

- **GitHub confirmed genuinely blocked, not assumed.** The proxy's own
  status endpoint (`curl $HTTPS_PROXY/__agentproxy/status`) and its
  README are explicit: 403/407 is an organization egress-policy denial -
  "do not retry or route around it." No workaround attempted.
- **Two already-permitted channels turned out to be enough.**
  `api.nuget.org` -> 200. `dot.net` / `dotnet.microsoft.com` -> normal
  redirects. apt has `dotnet-sdk-8.0` directly (Ubuntu's own package,
  not a Microsoft add-on repo) - installed cleanly as 8.0.128 after
  `apt-get update` refreshed a stale index (it had been pointing at a
  version no longer on the mirror).
- **`dotnet tool install --global dafny`** pulled from NuGet - zero
  GitHub involvement anywhere in the chain. Result: **Dafny 4.11.0**
  (full version `4.11.0+fcb2042d6d043a2634f0854338c08feeaaaf4ae2`), a
  real current release, not the `2.3.0+dfsg-0.1` Mono-based package apt
  offers directly.
- **Verified against the running binary, three real checks, not
  documentation:**
  1. Clean pass on a valid clamping method: `Dafny program verifier
     finished with 1 verified, 0 errors`, exit 0 - exact match to the
     false-zero note already in `evidence/model.py`.
  2. Broken method: per-line error blocks + `0 verified, 2 errors`,
     **exit code 4** - new finding, Dafny's exit codes aren't a simple
     0/1 pair the way CrossHair's are.
  3. An unsatisfiable precondition (`x > 0 && x < 0`) against an
     obviously-false postcondition verified clean - confirms Gate C3's
     vacuous-precondition vulnerability is real and reproducible on this
     binary, not speculative.
- **Checked whether `dafny audit` (new in 4.x) makes the Z3-based
  mitigation unnecessary - it doesn't.** Ran it against the vacuous
  case: `0 findings`. Its actual scope (per its own help text) is
  un-annotated assumes/axioms/non-determinism/unverified externs, not
  general precondition satisfiability. Confirmed the originally-planned
  mitigation is still necessary and technically feasible:
  `z3.Solver()` correctly returns `unsat` for the contradictory
  precondition and `sat` for a real one.
- **Net effect: no alteration to the Gate C1-C3 plan.** If anything it's
  on firmer ground than when written. One concrete addition carried
  into Gate C1: capture the exit code as-is, don't assume a specific
  nonzero value on failure.
- **Not done:** no capture runner, no real Dafny spec for `dosage.py`,
  nothing committed to the repository - this was toolchain research
  only, per what was asked. The probe `.dfy` files live only in the
  scratch directory.
- Documentation updated: `KNOWN_LIMITATIONS.md` (Gate C1 row + full
  detail section), roadmap doc (environment-check section + closing
  summary), `SYSTEM_BLUEPRINT.md`, `README.md`.

## 2026-07-06 — Phase C planning: gate-sequenced plan, real environment check

Requested directly ("Move on to Phase C planning") right after Phase
B's gate ledger closed. Planning only - no Phase C code written.

- **Environment check done first**, same discipline as every prior
  toolchain decision in this repo: `z3 --version` -> 4.16.0, and
  `python3 -c "import z3"` succeeds - usable directly. `dafny` is not on
  PATH. `apt-cache show dafny` finds a package, but it's
  `2.3.0+dfsg-0.1` - Ubuntu universe, roughly 2015-era, depending on
  Mono (`mono-mcs`, `mono-runtime`), not the modern .NET-based Dafny
  (4.x) the false-zero note in `evidence/model.py` is written against.
  `dotnet` isn't installed; a direct GitHub release fetch 403'd through
  the environment's proxy. Recorded as a real, named blocker
  (`KNOWN_LIMITATIONS.md`) rather than assumed away or silently deferred
  - mirrors the `crosshair-tool 0.0.107` pinning precedent from Gate 3.
- **Restructured** `payloadguard-evidence-roadmap-phaseB-to-C.md`'s
  Phase C section from a flat two-mechanism sketch into six sequenced
  gates (C1-C6), each with scope, dependencies, and a suggested build
  order:
  - C1: Dafny adapter capture + minimal false-zero guard (foundation).
  - C2: PROVEN's exclusivity migration - sequenced immediately after C1,
    before any real spec exists, since this is the highest-consequence
    change in Phase C (a bug here would let PROVEN leak onto un-proven
    evidence). Recommended it get ratified-ruling-level review, like
    R1/R2 did.
  - C3: output-parsing hardening - three of four vulnerability vectors
    scoped (vacuous preconditions via Z3 satisfiability check, weak
    postconditions as a best-effort pattern check, timeout/resource
    masking via `verifier_completion_status`); the fourth
    (specification stripping) named BLOCKED - the source material
    describing it was cut off before this session had it in full, so
    it's recorded as needing a follow-up read, not guessed at.
  - C4: Spec-Testing Proofs, alongside whichever spec C1 produces first.
  - C5: mutation testing (MutDafny-style, six operators) - flagged as
    the largest single piece, recommended as its own sub-plan once C1-C2
    are stable rather than attempted in one pass.
  - C6: NL-dialogue confirmation - a process control with no technical
    dependency on the others, recommended adopted immediately rather
    than deferred.
- **Also recorded in `KNOWN_LIMITATIONS.md`** as two new blocked/named
  rows (Dafny toolchain decision; C3's fourth vector) so the live gate
  ledger surfaces them, not just the roadmap doc.
- `SYSTEM_BLUEPRINT.md` and `README.md` updated: Phase B marked
  COMPLETE (gate ledger fully closed); Phase C marked "planning," with
  the environment findings summarized.
- No code changes this session - planning only, as requested.

## 2026-07-06 — Gate 5 fully resolved: concrete-only fixture now constructible

Closed the last open item from the original six-gate ledger. Requested
directly ("concrete fix gate 5") right after Gate 2 completed.

- **Root cause:** `_bind_self_describing` (variant C's binding strategy,
  `evidence/render/matrix_variants.py`) bound a symbolic record to
  *every* requirement unconditionally, regardless of what it declared -
  a leftover from before metadata.c.yaml carried `evidence` declarations
  at all. This made a concrete-only requirement structurally impossible:
  it would always show up in the symbolic artifact too.
- **Fix:** `_bind_self_describing` now checks each requirement's
  declared `evidence` list before binding symbolic evidence - a
  requirement declaring only `concrete_test` entries (no `crosshair`
  entry) gets no symbolic record. When `evidence` is absent entirely,
  the original unconditional behavior is preserved for backward
  compatibility - the existing symbolic-only fixture relies on exactly
  this fallback path and needed no changes. Concrete binding is
  untouched either way - stays fully self-describing via
  `concrete_results.json`'s own `requirement_id`, per Gate 4's decision.
- **No effect on committed data:** every real requirement in
  `metadata.c.yaml` declares `crosshair` (added when Gate 4's asymmetry
  was closed), so this changes nothing observable - confirmed by
  regenerating and diffing (differs only by `generated_utc`).
- **Proven, not assumed:** `tests/test_single_evidence_type.py` gained a
  concrete-only fixture (a requirement declaring
  `evidence: [{method: concrete_test, test_id: ...}]`, no `crosshair`
  entry) alongside the existing symbolic-only one - confirmed to appear
  in exactly the concrete artifact and not at all in the symbolic one,
  the property that was previously impossible. 4 tests total (2
  fixtures × schema validation + binding behavior). Full suite: 41
  passed (39 prior + 2 new). Full pipeline re-run independently.
- Documentation updated: `KNOWN_LIMITATIONS.md` (new dedicated Gate 5
  section, ledger table updated to FULLY RESOLVED), `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc (new Gate 5 section, Gate 4's stale
  "constructibility note still holds" corrected, closing summary fixed).
- **Gate 5 is now fully resolved.** Combined with Gate 2's completion,
  every gate in the original ledger is closed, decided, or resolved -
  nothing structural remains open in Phase B's gate work; only Phase C
  (Dafny/Z3 adapters) is ahead.

## 2026-07-06 — Gate 2 build, Phase 7: Step 4 (delete the fallback) — Gate 2 COMPLETE

Requested explicitly, now that the CLI had landed and the cutover had
run stable through multiple independent verification passes.

- **Deleted:** `build_matrix_variant_a`, `build_matrix_variant_b`,
  `build_matrix_variant_c` from `evidence/render/matrix_variants.py`.
  Their shared markdown renderers (`_markdown_variant_a/b/c`) and other
  helpers stayed - `build_matrix()` already used those, not the deleted
  top-level functions.
- **Deleted:** `tests/test_binder_equivalence.py`. Its entire purpose
  was proving the old functions' output equals `build_matrix()`'s
  output - moot once the old functions don't exist.
- **Migrated, not deleted:** `tests/test_single_evidence_type.py` (Gate
  5's fixture test) was the one other place in the suite calling
  `build_matrix_variant_c` directly - updated to call
  `build_matrix("c-symbolic"/"c-concrete", ...)` instead. Confirmed
  still passing (2/2) before moving on.
- **Comments updated, not left stale:** the module-level banner in
  `matrix_variants.py` and the header comments in `generate_matrix_a/b/c.py`
  that described the now-gone fallback were rewritten to stop
  referencing it, rather than left describing something that no longer
  exists.
- **Verified after deletion, not just before it:** full suite (39
  passed - 44 minus the 5 deleted equivalence tests), full pipeline
  re-run (every regenerated artifact still differs only by
  `generated_utc`), and the CLI independently re-checked against a
  committed artifact post-deletion.
- **Corrected an overclaim while updating the roadmap doc:** a first
  draft of the "what's done" summary said Gate 5's concrete-only-fixture
  limitation was now closed by Gate 2's completion. Checked before
  committing: `build_matrix()`'s `_bind_self_describing` strategy for
  variant C is a literal extraction of the original C builder's
  logic - it still binds a symbolic record to every requirement
  unconditionally, unchanged by the refactor. Gate 5 stays resolved for
  the constructible half only; fixed before it went in the doc.
- Documentation updated: `KNOWN_LIMITATIONS.md` (Gate 2 marked
  COMPLETE), `SYSTEM_BLUEPRINT.md`, `README.md`, roadmap doc (Gate 2's
  heading, Gate 4's status, the closing summary).
- **Gate 2 is now structurally complete** - CONFLICT rule (both types),
  the vocabulary-agnostic binder, and the CLI are all built, verified,
  and documented. The only open item in Gate 2's scope was ever its own
  definition, and that's ratified. Git history holds the deleted
  fallback and test if ever needed again.

## 2026-07-06 — Gate 2 build, Phase 6: CLI (built ahead of Step 4, at Steven's direction)

Steven asked to hold off deleting the Step 2 fallback functions and get
the CLI done first - so the fallback stays available while new
capability is still landing, rather than being removed before anything
else changes.

- **Built:** `evidence/cli.py` - `python -m evidence.cli build --variant
  {a|b|c-symbolic|c-concrete} --metadata PATH --manifest PATH --concrete
  PATH [--schema PATH] [--out-json PATH] [--out-md PATH]`. Wraps
  `build_matrix()` with every input as an argument instead of the
  hardcoded `examples/dosage_calculator` paths the generator scripts use
  - the genuinely vocabulary-agnostic surface Gate 2 was named for: this
  can build a matrix for a different device's evidence set matching one
  of the four schema shapes, not just the worked example.
  `tool_versions` is now keyed by the manifest's own declared `tool`
  field rather than a hardcoded `"crosshair"` string, so a future
  Dafny/Z3 manifest won't need this CLI changed.
- **Two real bugs caught and fixed while building it, not left in:**
  1. An uncaught `jsonschema.ValidationError` printed via `str(e)` dumps
     the *entire schema* on every validation failure - useless noise for
     a CLI user. Fixed to use `ValidationError.message`, the short
     human-readable line.
  2. Omitting both `--out-json` and `--out-md` printed the JSON *and*
     the markdown concatenated to stdout, producing invalid combined
     output (caught by `test_cli_prints_to_stdout_when_no_output_path_given`
     failing with a `JSONDecodeError`). Fixed: markdown only ever goes
     where `--out-md` explicitly says to, never to stdout.
- **Proven, not assumed:** `tests/test_cli.py` (10 tests) drives the CLI
  via subprocess (the way a real user would invoke it) for all four
  variants and asserts byte-identical output (timestamp aside) to the
  corresponding committed artifact, plus both Tier-1 error paths (schema
  validation, CONFLICT Type 1 - confirmed to fire through the CLI path
  too) and both output modes (file, stdout). Full pipeline independently
  re-run to confirm the CLI's addition changed nothing about the
  existing generator scripts. Suite: 44 passed (34 prior + 10 new).
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md` (including a new CLI usage example in "Running it"),
  roadmap doc. Only Step 4 (delete the Step 2 fallback once stable)
  remains for Gate 2's binder work.

## 2026-07-06 — Gate 2 build, Phase 5: vocabulary-agnostic binder, Step 3 (fold in Type 1; confirm Type 2 stays standalone)

Continuing the phased binder build. Re-examined the plan before
implementing rather than mechanically following the earlier wording
("fold Types 1/2 into the binder") - Type 2 doesn't actually fit inside
a per-variant builder call, and forcing it in would have been worse
design, not better.

- **Analysis:** Type 1 (identity mismatch) is inherently per-variant -
  it checks one metadata file's declared bindings against the evidence
  store - so it belongs inside `build_matrix()`. Type 2 (outcome
  mismatch) compares raw manifests across the WHOLE dataset regardless
  of which variant is being built; folding it into `build_matrix()`
  would mean re-running the identical whole-dataset check redundantly on
  every one of the four variant calls, for no benefit. It stays a
  standalone `generate_artifacts.py` stage, the same way the
  fact-equality gate does (both are properties of the artifact/input
  set, not of a single generation call).
- **Folded in:** `build_matrix()` now calls `run_conflict_gate(metadata,
  concrete_store, manifest)` as its first step, before assembling any
  record - Tier 1. This closes a real gap: Type 1 previously only ran
  inside the `generate_artifacts.py` pipeline stage, so running e.g.
  `generate_matrix_a.py` alone would have bypassed it entirely (the
  individual generators are documented to bypass fact-equality the same
  way - Type 1 had identical exposure until now).
- **Base matrix's check narrowed, not removed:** `metadata.yaml` never
  calls `build_matrix()` (frozen `manual_matrix.py` path, ruling R2c), so
  it keeps its own explicit check. Renamed `stage_conflict_check` to
  `stage_base_conflict_check`, scoped to just the base file (3 symbolic
  bindings - base declares no concrete evidence at all). Stage 5's
  comment updated to note a/b/c-symbolic/c-concrete are now
  self-checking via `build_matrix()`.
- **Proven, not assumed:** added
  `test_build_matrix_folds_in_type1_check` to
  `tests/test_conflict_check.py` - drives `build_matrix()` directly with
  a conflicting in-memory fixture and confirms it raises before
  assembling a single record, proving the fold-in itself rather than
  just the underlying check function. Full pipeline re-run end to end;
  every regenerated artifact still differs only by `generated_utc`.
  Suite: 34 passed (33 prior + 1 new).
- **Documented tradeoff:** `build_matrix_variant_a/b/c` (the Step 2
  fallback) do NOT have Type 1 folded in. If the fallback is ever used
  in an emergency, Type 1's per-call check is temporarily lost along
  with it - an accepted tradeoff of restoring known-good behavior
  quickly, recorded rather than silently true.
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc. Gate 2's binder work is now Steps 1-3 done;
  Step 4 (delete the fallback once stable) and the CLI remain.

## 2026-07-06 — Gate 2 build, Phase 4: vocabulary-agnostic binder, Step 2 (cutover)

Steven approved proceeding with an explicit request to keep a fallback
available ("ensure we can fallback if necessary"). Cutover done with
that constraint built in, not bolted on afterward.

- **Cut over:** `generate_matrix_a.py` / `_b.py` / `_c.py` now import
  and call `build_matrix("a"/"b"/"c-symbolic"/"c-concrete", ...)` from
  `evidence/render/matrix_variants.py` instead of the original
  `build_matrix_variant_a/b/c` functions directly.
- **Fallback, by design:** the three original functions are deliberately
  left in place, fully intact and unused. If a problem with
  `build_matrix()` ever surfaces, each generator's import + call can be
  reverted to the corresponding original function in one line, or this
  commit can be `git revert`ed outright. Deleting them is scoped as its
  own later cleanup step (Step 4), gated on the cutover proving stable —
  not bundled into the cutover itself.
- **Verified, not assumed:** ran the full `generate_artifacts.py`
  pipeline post-cutover (all 7 stages clean) and diffed every
  regenerated artifact against the pre-cutover committed versions -
  differs only by `generated_utc`, exactly as the Step 1 equivalence
  proof predicted. Full suite: 33 passed, unchanged from Step 1 (this
  step changed which function each generator calls, not any logic).
- Updated the module-level comment in `matrix_variants.py` to mark
  `build_matrix()` as authoritative and the three original functions as
  an explicit, intentional fallback rather than dead code.
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc - Gate 2's binder work now tracked as Steps
  1-2 done, Step 3 (fold CONFLICT Types 1/2 into the binder) and Step 4
  (delete the fallback functions once stable) still open, plus the CLI.

## 2026-07-06 — Gate 2 build, Phase 3: vocabulary-agnostic binder, Step 1

Steven confirmed the phased plan and set the working principle for the
rest of Phase B->C: correctness over speed, one step at a time, always
with the end of Phase C in view. This step is scoped narrowly on
purpose - it is a genuine architectural refactor (unlike Types 1/2,
which extended an existing pattern), so it gets its own proof before
anything currently authoritative is touched.

- **Built:** `build_matrix(variant_key, metadata, manifest,
  concrete_store, tool_versions=None)` in
  `evidence/render/matrix_variants.py` - one entry point replacing
  `build_matrix_variant_a/b/c`. Literal extraction, not new logic: each
  variant's record-assembly ("binder": `_bind_declared`, `_bind_shadow`,
  `_bind_self_describing`) and row-rendering ("shape":
  `_shape_evidence_array`, `_shape_flattened_shadow`,
  `_shape_method_partitioned`) lifted verbatim into named functions,
  dispatched through a declarative table (`_VARIANT_SPECS`) instead of
  three separate top-level functions. Binding strategy and row shape
  split as the two real axes of variation, so a future fifth shape can
  reuse an existing piece instead of requiring a whole new function.
- **Correctness proof:** `tests/test_binder_equivalence.py` (5 tests)
  runs the old function and `build_matrix()` against identical real
  committed inputs for all four variant keys and asserts equality two
  ways - dict equality and `json.dumps()` string equality (the second
  catches key-order drift dict equality alone would miss). All pass.
- **Nothing cut over.** `generate_matrix_a.py` / `_b.py` / `_c.py` and
  `regenerate_all.py` still call the original functions, untouched.
  Pipeline re-run end to end; every regenerated artifact differs only by
  `generated_utc` - zero observable change from this step. Suite: 33
  passed (28 prior + 5 new).
- Documentation updated to record Step 1 as done and Step 2 (the actual
  cutover - retiring the three old functions and generator scripts,
  folding Types 1/2 into the binder) as the next, deliberately separate,
  higher-risk step: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc.

## 2026-07-06 — Gate 2 build, Phase 2: Type 2, variant C asymmetry closed

Continuation of the phased Gate 2 build, addressing the two remaining
well-scoped gaps flagged at the end of Phase 1 (Type 2, variant C's
binding asymmetry). The third — the vocabulary-agnostic binder + CLI
unification — is deliberately left for its own phase: it's a real
architectural refactor (consolidating four separate generator scripts),
not an extension of the existing Type 1 pattern, and carries meaningfully
more regression risk.

- **Variant C asymmetry closed (Gate 4).** `metadata.schema.c.json`
  gained an optional `evidence` property (identical shape to variant
  A's); `metadata.c.yaml` now declares it on all three requirements,
  matching the real bindings already in `concrete_results.json`
  (`kernel_detects_bolus_limit_exceeded` -> REQ-GIP-1-4-12, etc.). This
  is cross-checking-only: `build_matrix_variant_c` never reads
  `evidence` — C's binding stays evidence-store-carried, unchanged.
  Confirmed by regenerating: C's artifacts diff only by `generated_utc`.
  Bindings checked by the Type 1 gate rose from 20 to 24 (C now
  contributes 7 instead of 0).
- **Type 2 (outcome mismatch) built.** `evidence/conflict.py` gained
  `outcome_conflicts()` / `run_outcome_gate()`: manifests are grouped by
  identity (tool, target, enforced `per_condition_timeout_s` —
  deliberately excluding the raw argv's environment-specific absolute
  path and `started_utc`); a group with more than one distinct
  `exit_code` is a conflict. Wired into `generate_artifacts.py` as stage
  4, run against all four committed manifests: 4 manifests, 4 distinct
  identities, 0 conflicts — real, honest, and currently vacuous, since no
  two committed manifests share a target. Tested with two synthetic
  cases (positive mismatch; same-outcome-different-target confirming no
  over-firing).
- `tests/test_conflict_check.py`: 11 tests total (up from 7) — added
  variant C's clean-pass case and three Type 2 cases.
- Full pipeline re-run end to end (7 stages now); regenerated artifacts
  confirmed byte-identical except timestamps. Suite: 28 passed (24 prior
  + 4 new).
- Documentation updated: `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md`,
  `README.md`, roadmap doc.
- **Still open, its own phase:** the vocabulary-agnostic binder (one
  implementation driving all four schema variants, replacing
  `generate_matrix_a/b/c.py`) and the CLI. Both CONFLICT types run today
  as standalone pipeline stages alongside the existing separate
  generators.

## 2026-07-06 — Gate 2 build, Phase 1: CONFLICT rule Type 1 (identity mismatch)

First build increment against the roadmap, taken in a small, self-
contained phase per Steven's direction (small phases, stop for input or
new issues). Scoped to what was already fully specified and ratified —
no new decisions required.

- **`evidence/conflict.py`:** implements Type 1 for real, over real data.
  `concrete_binding_conflicts()` cross-checks metadata's top-down
  concrete bindings (variant A's `evidence` list; variant B's shadow
  `parent_requirement` + implementation-suffix form) against
  `concrete_results.json`'s self-declared `requirement_id`.
  `symbolic_binding_conflicts()` cross-checks each requirement's declared
  `implementation` file against the crosshair manifest's actual
  `target`. `run_conflict_gate()` combines both, Tier 1 (raises on any
  mismatch, matching fact-equality/structural-PROVEN's behavior).
- **Wired into `generate_artifacts.py`** as stage 3 (after capture
  integrity, before regeneration) — checked against all four metadata
  files: 20 bindings checked, 0 conflicts. Pipeline re-run end to end;
  regenerated artifacts differ only by `generated_utc` timestamp
  (deterministic regeneration confirmed).
- **`tests/test_conflict_check.py`** (7 tests): both ratified positive
  cases (variant A's `evidence` shape and variant B's shadow shape) as
  in-memory mutated fixtures reproducing the failure; the ratified
  negative case (REQ-GIP-1-4-12's kernel_scope/system_scope split) run
  against the real committed data, confirmed clean; a symbolic-file
  mismatch case; and a distinct-failure-mode check (a declared test_id
  that doesn't exist in the evidence store at all is a hard error, not a
  silently-passing conflict check, since there's no second claim to
  compare against).
- Variant C is untouched — it declares no top-down concrete binding, so
  Type 1 has nothing to compare there yet (Gate 4's known asymmetry,
  unchanged by this phase).
- Suite: 24 passed (17 prior + 7 new).
- Documentation updated to reflect BUILT status:
  `KNOWN_LIMITATIONS.md`, `SYSTEM_BLUEPRINT.md` (component map + Phase
  boundary), `README.md`, roadmap doc.
- **Not done this phase, staying open per the small-phases plan:** Type
  2 (outcome mismatch — needs a cross-manifest comparison mechanism that
  doesn't exist yet), the vocabulary-agnostic binder itself, and the CLI.

## 2026-07-06 — Gate 2 CONFLICT rule defined and ratified

Working session with Steven to define CONFLICT against the two candidate
test cases already on file, refine the definition, and lock it in.

- **Definition drafted:** CONFLICT requires two claims about the *same*
  `(requirement, scope)` and the same underlying verification act — never
  triggered by two legitimately different evidence types bound to one
  requirement, and never triggered by an `intent_ok` mismatch (that's a
  binding compared to its own stated intent, not two competing claims;
  already has its own mechanism, R1). Two sub-types identified:
  - Type 1 (identity mismatch): top-down and bottom-up claims about one
    binding disagree on target file/method — Gate 4's exact trigger.
  - Type 2 (outcome mismatch), added during review: two claims agree on
    target identity but disagree on what that identical run produced.
    Not hypothetical — motivated directly by this repo's own documented
    CrossHair model-fidelity non-determinism (Sample C / overflow-probe
    exhibits, Gate 3's caveat) that a same-invocation result can vary.
- **Tested against three cases:** positive Type 1 (dual-authorship
  file/method mismatch), negative (REQ-GIP-1-4-12 kernel_scope/
  system_scope split — a GAP, not a conflict, since there's no second
  claim to disagree with), positive Type 2 (a future duplicate manifest
  for an identical target reporting a different exit code).
- **Ratified by Steven** ("yep agree. lock in") — status moves from
  BLOCKED to DEFINED. Not yet built: Type 1 reuses Gate 4's intersection
  check directly; Type 2 needs a new cross-manifest comparison mechanism
  that doesn't exist yet. Building either into Gate 2's generalized
  binder is still open.
- `KNOWN_LIMITATIONS.md` rewritten fresh to reflect the current state of
  all six gates in one pass, rather than accumulating further patches.
  `payloadguard-evidence-roadmap-phaseB-to-C.md`, `SYSTEM_BLUEPRINT.md`,
  and `README.md` updated to match.
- Suite: 17 passed (unchanged — documentation only, no capture or
  generator touched).

## 2026-07-06 — Gate 3 closed by real test; Gate 6 (FRN) resolved; Gate 4 decision recorded; roadmap v2

Verification-first session, per the standing discipline: claims were
checked against actual repo/tool state before being written down,
including claims in the prompts supplied this session.

- **Pre-check on Defects 1/2 (mechanical-fixes prompt):** the prompt
  assumed these were possibly unpushed local commits. Checked for real:
  `5564fdf`/`1d9a260` exist on `main` locally and on `origin/main`
  (fetched and compared — identical, no divergence); DEVLOG already
  documented both under the 2026-07-05 "Gate 1 remediation" entry below.
  Rendered output verified directly (not just commit messages): all four
  variants show the scoped Notes fix and the REQ-GIP-1-4-12 kernel/system
  scope split correctly; suite 17 passed. No remediation needed — the
  prompt's premise didn't hold, and the mismatch was reported before
  proceeding rather than silently skipped or silently actioned.
- **Same-pattern discrepancy found in the roadmap-v2 prompt:** its "read
  first" section claimed FRN was "now closed." It was not — every
  in-repo reference (`KNOWN_LIMITATIONS.md`, `sources/README.md`,
  top-level `README.md`, `examples/dosage_calculator/README.md`) still
  read UNRESOLVED/BLOCKED. Flagged to Steven before proceeding; the
  roadmap v2 document (supplied afterward) carried the actual resolution
  to apply.
- **Gate 6 (FRN) — resolved and written up.** `FRN` = FDA Product Code
  for "Infusion Pump" (21 CFR 880.5725); within GIP's taxonomy, general-
  purpose volumetric infusion pumps (peristaltic, cassette-based),
  distinct from `All`. Source: NotebookLM extraction of the full source
  PDF, cross-checked against independent FDA-registry research. Caveat
  carried forward, not dropped: not yet independently re-verified against
  the raw Sec 2.4.1 text. Updated `sources/README.md` (open question →
  resolved question), `examples/dosage_calculator/README.md`,
  top-level `README.md`, `KNOWN_LIMITATIONS.md`.
- **Gate 3 — decided stay-CLI, by actually running the supplied
  verification script, not by trusting its writeup.** The roadmap's
  corrected seed-override technique (patch `make_default_solver`,
  hyphenated Z3 params) still had three bugs that only running it
  surfaced: (1) the roadmap's own claimed constructor,
  `AnalysisOptions(max_iterations=..., per_condition_timeout=...)`,
  raises `TypeError` on the installed 0.0.107 — `analyze_function` takes
  `AnalysisOptionSet`, not `AnalysisOptions`; (2) `crosshair.core` alone
  raises `CrossHairInternal("Opcode patches haven't been loaded yet.")`
  on `.analyze()` — must import from `crosshair.core_and_libs`; (3)
  `analyze_function` only returns parsed `Checkable`s, it doesn't run the
  solver — `.analyze()` must be called on each to get a real result. The
  uncorrected script "completed" in under a second and would have looked
  like a clean pass without ever invoking CrossHair's solver. After all
  three fixes, ran it for real, twice per target, seed 1 vs seed 2:
  `dosage.py::calculate_hourly_dose` gave byte-identical "Not confirmed"
  results both times; `dosage_broken.py::calculate_hourly_dose` (a
  stronger discriminator — it has real counterexamples) gave the exact
  same two counterexamples both times, matching the values already on
  file in `raw_crosshair_output_broken.txt`. No observed effect from the
  patch on either target tested. Decision: stay-CLI; `seed` documented as
  a tool-version limitation (tool-fixed at 42, hard-coded in
  `make_default_solver()`, not `StateSpace.__init__`, with hyphenated
  param names); `max_iterations` confirmed enforceable via
  `AnalysisOptionSet` independent of the seed question. Verification
  script committed at
  `examples/dosage_calculator/gate3_seed_patch_test.py`; nothing
  re-captured, Gate 1's committed evidence is untouched. Also closed as a
  non-issue: installed/pinned crosshair-tool is 0.0.107 in this
  environment (`pip show` confirmed), consistent with the toolchain pin;
  GitHub's latest *tag* trailing at 0.0.106 doesn't indicate a real
  discrepancy here.
- **Gate 4 — decision recorded (not built).** Option 3 (both binding-
  authorship models, cross-checked, Tier-1 failure on disagreement) is
  now the decision on record, with the dual-authorship top-down/bottom-up
  code-location-match mechanism specified. Building it is Gate 2's binder
  work.
- **Gate 2 — still blocked**, now with two candidate test cases on file
  for whatever CONFLICT definition eventually lands: a positive case
  (top-down/bottom-up binding disagreement under Gate 4's mechanism) and
  a negative case (REQ-GIP-1-4-12's kernel/system scope split, which is a
  documented absence, not a conflict).
- `payloadguard-evidence-roadmap-phaseB-to-C.md` replaced in place with
  the roadmap-v2 content (supersedes the 2026-07-05 morning version per
  its own text) plus the real Gate 3 result folded in.
- Suite: 17 passed (unchanged — no capture or generator touched this
  session).

## 2026-07-05 — Gate 1 remediation (two items from Steven's review)

Gate 1 review verdict received: fact-equality doing its job; two issues to
fix before Gate 2. Both fixed in generators/metadata — no generated file
hand-edited.

- **Item 2 (Tier 1 renderer defect):** variant C's method-filtered views
  were leaking the cross-evidence-type intent summary into their Notes,
  and the aggregate Notes section emitted once per table row (duplicate
  REQ-GIP-1-8-1 line in concrete.md). Fixed: `_view_notes()` scopes note
  text to the rendering view's evidence contribution (the intent_ok VALUE
  stays requirement-scoped per R1, never re-derived); `_md_notes()`
  de-duplicates by (requirement, note).
- **Item 1 (REQ-GIP-1-4-12 alarm scope):** evidence didn't match the
  requirement text — clamped output was verified, alarm emission never
  was. Steven's design decision (sources/req-gip-1-4-12-alarm-scope-
  decision.md, IEC 60601-1-8 ALARM CONDITION vs ALARM SIGNAL) implemented:
  metadata.yaml gains kernel_scope/system_scope on 1-4-12 (all four
  schemas extended with the optional fields; positive+negative
  revalidated for every variant); concrete test renamed
  over_max_clamps_exactly_to_max → kernel_detects_bolus_limit_exceeded
  and re-captured for real (4 passed); variant metadata re-derived;
  evidence rows for 1-4-12 reference the kernel_scope text; system_scope
  renders as an explicit named GAP in every view. GAPs are excluded from
  normalize_facts by rule (absence is not a fact) — fact-equality gate
  still PASS at 7 facts. Suite: 17 passed.
- Gates 2/3/4/6 untouched per the remediation prompt's "still open" list;
  the CONFLICT-vs-scope-GAP test question recorded in KNOWN_LIMITATIONS.

## 2026-07-05 — Deferred-gate work while Gate 1 output under review

Performed the deferrable gate processes without touching Gate 1's ground
truth (no re-capture, no artifact regeneration).

- **Gate 2 / CONFLICT rule — BLOCKED, named.** Retrieved
  PayloadGuard-Evidence-Blueprint-1 from Drive in full (committed to the
  repo with provenance header; Drive doc remains authoritative). The term
  CONFLICT appears nowhere in it (0 occurrences) nor in
  SYSTEM_BLUEPRINT.md (single to-do mention, no definition). Per roadmap:
  stopped, named, asking Steven. Closest neighbouring concept: Blueprint
  Phase 2 acceptance (b), intent mismatch "raises a GAP/flag".
- **Gate 3 — investigated, decision pending.** Verified against the
  installed package: per_condition_timeout CLI-enforceable (done in B1);
  max_iterations exposed by the Python API only
  (AnalysisOptions.max_iterations, default sys.maxsize); seed hard-coded
  to 42 in crosshair/statespace.py:750-751 — declared seed:1 is
  unenforceable at any interface on 0.0.107. Two wiring options recorded
  in KNOWN_LIMITATIONS; either requires re-capture, so the decision waits
  until Gate 1 review completes.
- **Gate 4 — options prepared** (metadata-authored / store-carried /
  both-with-cross-check, recommendation noted) for slotting into the Gate
  2 binder design. Design input recorded: the current C builder binds
  symbolic evidence to every requirement without verifying implementation
  against the capture target; the Gate 2 binder must bind by verified
  code-location match.
- **Gate 5 — resolved for the constructible half.**
  tests/test_single_evidence_type.py: in-memory symbolic-only fixture
  through the real variant C builder — appears in exactly one artifact;
  schema-c-validated; committed data untouched. Concrete-only fixture
  impossible pre-Gate-2 (see Gate 4 input). Suite: 17 passed.
- **Gate 6 — remains blocked** on a one-line FRN definition from Steven.

## 2026-07-05 (Turn B4) — Phase B Gate 1: end-to-end artifact generation

Phase B v3 prompt + roadmap received; roadmap committed verbatim as
`payloadguard-evidence-roadmap-phaseB-to-C.md`. Note for the record: the
prompt's B4/B5 spec bodies arrived as placeholders; B4 scope taken from
roadmap Gate 1 (minimal pipeline, four real variant artifacts as ground
truth, Steven review before Gate 2).

- `generate_artifacts.py`: five-stage end-to-end pipeline — (1) all four
  metadata files schema-validated, (2) capture integrity verified without
  re-running evidence (Sample A exit 0 + effective_bounds present, Sample
  B exit 1, concrete store clean), (3) regeneration + fact-equality gate
  via the B2 path (PASS, 7 facts), (4) structural PROVEN sweep over four
  variants plus frozen base, (5) `artifact_index.json` — SHA-256
  provenance binding 12 inputs to 8 outputs plus 10 frozen evidence files,
  with per-gate results. Any stage failure is a Tier 1 stop.
- `KNOWN_LIMITATIONS.md` created as the standing gate ledger: Gate 3
  (CrossHair API bounds) deferred — not hit in B4; Gate 4 (binding
  authorship) deferred to Gate 2's binder design; Gate 5 (single-evidence
  fixture) deferred as a Gate 2 test prerequisite; Gate 6 (FRN) blocked on
  a one-line definition from Steven; Phase C `verifier_completion_status`
  schema consideration noted for the Gate 2 binder.
- Suite: 15 passed. Gate 2 (vocabulary-agnostic binder + CONFLICT rule)
  not started — gated on Steven's review of the four real artifacts.

## 2026-07-05 09:46 UTC — Turn 2.0: bounds reconciliation, fact-equality gate, review protocol (678a3a5, 6347645, B3: this commit)

Three ratified rulings from the Q1–Q3 design review, executed in strict
order B1 → B2 → B3. Kernels untouched; exhibits frozen.

- **B1 (678a3a5, bounds):** `run_verify.py`/`run_verify_broken.py` now pass
  `--per_condition_timeout 30` (the one declared bound the 0.0.107 CLI can
  enforce) and record `effective_bounds` in the manifest — the single
  source of truth for what a run demonstrated. Samples A and B re-captured
  for real; raw outputs byte-identical to the previous captures. Generation
  gained a model-level `{declared, effective, enforcement_note}` bounds
  block, derived once (`derive_bounds_block`) and verified uniform across
  all four views. Exhibit captures/pins/runners byte-unchanged (frozen
  measurements). Ratified: metadata's declared triple kept — declared
  bounds are the bounds analogue of `intended_method`.
- **B2 (6347645, gate):** same-facts check mechanized.
  `evidence/reconcile.py` normalizes any matrix shape to fact tuples;
  `run_gate` asserts A/B/C fact equality, base-matrix = symbolic subset
  (frozen legacy view, ratified), intent uniformity, bounds-block
  uniformity. Enforced at generation time by `regenerate_all.py` (the
  sanctioned entrypoint; ratified that individual generators stay
  unchanged — a cross-artifact property cannot live inside one generator)
  and in the suite by `tests/test_fact_equality.py` (corruption cases
  mutate tmp copies only). Gate on real artifacts: PASS, 7 facts. Suite:
  15 passed.
- **B3 (this commit, protocol):** `REVIEW_PROTOCOL.md` codifies two-tier
  review: Tier 1 machine gates (fact-equality + structural PROVEN) stop
  defects and are never resolved by editing generated artifacts; Tier 2
  human review is per-reason over six structured finding classes.
  "Review only on validator disagreement" documented as void by
  construction. README pointer, BLUEPRINT invariants 8–9 and timestamp
  updated.

## 2026-07-04 18:52 UTC — Documentation pass: README, SYSTEM_BLUEPRINT, DEVLOG

- Root `README.md` populated (was an empty scaffold placeholder): purpose,
  non-goals, claims-discipline table including EXAMPLE_CHECKED, end-to-end
  flow, worked-example walkthrough, honesty exhibits, run instructions,
  known limitations.
- `SYSTEM_BLUEPRINT.md` created: component map, data-flow diagram,
  invariants (R1/R2 encoded), evidence inventory, Phase A/B boundary.
- `DEVLOG.md` created with the full dated history of the repository to date.
- No code, schema, kernel, or evidence changes in this session.

## 2026-07-04 16:40–16:42 UTC — Phase A closeout rulings (f5977d0, 96eaeee, d23689a)

Implemented the three rulings ratified after the Phase A audit. Kernels
untouched; one commit per ruling.

- **R1 (f5977d0):** `intent_ok` made requirement-scoped and derived exactly
  once at bind time (`derive_intent` in `matrix_variants.py`); all variant
  views carry it read-only, variant C assembles the full two-method model
  before filtering, variant B shadows project the parent value. Verified
  uniform across A / B parents / both C views (1-4-12 false, 1-8-1 false,
  DOSE-003 true). Same-facts check re-run: 7 facts, set-equal.
  RECONCILIATION asymmetry (1) closed; asymmetry (2) annotated deferred to
  Phase B.
- **R2 (96eaeee):** PROVEN rule made structural, not textual. Inline
  `intended PROVEN, realized …` notes restored (quoting authored metadata is
  fidelity). `assert_no_realized_proven()` fails generation if any realized
  strength equals PROVEN; committed as pytest over the four real artifacts
  plus in-memory corruption cases. Grep audit retired. Base Option A
  matrices untouched. Suite: 11 passed.
- **R3 (d23689a):** class-(2) incompleteness reframed: the IEEE-faithful
  channel exists but is unreliably sampled and sharply complexity-dependent
  (confirmed on the one-operation probe, silent on the four-parameter kernel
  under identical invocation; recorded bounds do not disclose the regime).
  Both exhibit pins' `mechanism_attribution` updated to match the README —
  verified identical modulo self-reference. Old "invisible" phrasing gone.

## 2026-07-04 16:15–16:26 UTC — Phase A completion T1–T4-C (0894da2…274115d)

- **T1 (0894da2):** BOUNDED_CHECKED incompleteness split into search-budget
  vs model-fidelity classes; CrossHair changelog cited (v0.0.72 real-valued
  float modelling, v0.0.58 nan/±inf as arguments only).
- **T2 (82a18a0):** naive-widening exhibit pinned
  (`exhibit_pin_naive_widening.json`): crosshair-tool 0.0.107, Python
  3.11.15, platform, exact invocation, mechanism attribution,
  version-contingency note.
- **T3 (d66162f):** domain-free `overflow_probe.py`. Expected a miss;
  CrossHair **confirmed** the violation (`double_it(8.98846567431158e+307)`
  → inf, exit 1). Recorded as-is, not re-rolled — paired with Sample C it
  measures the FP channel's width. Deterministic pytest companion added.
- **T4-0 (88bf755):** concrete evidence foundation — four requirement-mapped
  cases in `tests/test_dosage_concrete.py` (single CASES source), captured
  verbatim (pytest 4 passed) plus structured `concrete_results.json`.
  `Strength.EXAMPLE_CHECKED` added to the model.
- **T4-A/B/C (c2768da, 5745e0b, 274115d):** three parallel schema variants
  generated from identical evidence — A: evidence array per requirement
  (3 rows / 7 records); B: shadow pseudo-requirements with machine-enforced
  `parent_requirement` (7 rows); C: dual matrices partitioned by method
  (3 symbolic / 4 concrete rows), one filter-parametrised renderer.
  `RECONCILIATION.md`: programmatic same-facts confirmation (7 fact tuples)
  plus four recorded asymmetries. All schemas validated positive + negative.

## 2026-07-04 15:34 UTC — Option A amendment (b090d54)

Post-ship review found REQ-GIP-1-8-1's verification vacuous: the
`infusion_rate_ml_per_hr >= 0` precondition made the negative-dose clamp
dead code, so the postcondition's lower bound held by algebra. Applied
Option A: precondition widened to any finite rate (negative models the GIP
SR 1.8.1 single-fault reverse flow), directional postcondition added
(negative rate ⇒ return exactly 0.0), and the negative check reordered
before the finiteness check — a naive widening would have returned the
MAXIMUM dose on a −inf overflow. The naive variant and its real CrossHair
capture (exit 0 — the violation was NOT found) were committed deliberately
as the honesty exhibit. Sample B re-capture now shows a second, negative
counterexample, proving the widened domain is genuinely explored. Matrices
regenerated; 2× intent_ok false / 1× true preserved.

## 2026-07-04 14:47 UTC — Phase A initial build (9ca085a)

Repository scaffolded (empty skeleton, then populated per the Phase A
prompt) and pushed to `PayloadGuard-PLG/payloadguard-evidence`:

- `evidence/model.py` (Strength enum, CAVEAT map, dataclasses; Dafny
  false-zero parser note carried for Phase B), `evidence/schema/
  metadata.schema.json` (draft 2020-12, unknown-key rejection,
  crosshair_bounds required), `evidence/render/manual_matrix.py`
  (hand-reviewed binder/renderer).
- `examples/dosage_calculator/`: dose-clamping kernel with PEP316 contracts;
  Sample A (clean, exit 0) and Sample B (broken, exit 1 with concrete
  counterexample) captured by real CrossHair 0.0.107 runs;
  `metadata.yaml` sourced from GIP v1.0 with three requirements;
  matrices generated (not hand-typed) showing intended-PROVEN vs realized-
  BOUNDED_CHECKED mismatches honestly.
- `sources/`: GIP v1.0 hazard analysis archived verbatim + standing rule for
  future source documents. FRN pump-type tag left explicitly unresolved
  after a failed resolution attempt (web search; UPenn pages unreachable).
- Known bounds divergence (declared vs effective CrossHair bounds) flagged,
  not smoothed over. Nothing in the repo asserts PROVEN as realized.
