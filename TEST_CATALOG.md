# Test Catalog — payloadguard-evidence

**Generated — do not hand-edit.** Every row is read directly from
the real test suite via `evidence/test_catalog.py`'s AST parser, not
transcribed by hand. Regenerate after adding, renaming, or removing
any test:

```
python -m evidence.test_catalog --out TEST_CATALOG.md
```

`tests/test_test_catalog.py` fails CI if this file drifts from what
the generator actually produces against the committed test suite —
the same discipline `evidence/cli.py`'s own tests already apply to
the traceability matrices.

**Total: 296 test functions across 39 categories.**
Counts test *functions*, not pytest's collected test-case count -
a `@pytest.mark.parametrize`-decorated function is one row here
(one description, one code location) even though pytest runs it as
several cases with different data. Run `python -m pytest tests/ -q`
for the actual collected-case count.

---

## Aeb Kernel Matrix (`tests/test_aeb_kernel_matrix.py`)

| Test | Description | Code |
|---|---|---|
| `test_cli_omitting_manifest_and_concrete_entirely_still_works` | Cli omitting manifest and concrete entirely still works. | `tests/test_aeb_kernel_matrix.py:45` |
| `test_cli_writes_markdown_matching_committed` | Cli writes markdown matching committed. | `tests/test_aeb_kernel_matrix.py:60` |
| `test_single_function_requirements_bind_correctly` | Single function requirements bind correctly. | `tests/test_aeb_kernel_matrix.py:85` |
| `test_fcw_required_active_backs_both_req_1_and_req_3` | FCWRequiredActive's ensures clause is a single function covering both the lead-vehicle (S5.1.1) and pedestrian (S5.2.1) envelopes - two distinct requirements, one proof, mirroring drug_interaction_checker's CheckInterac… | `tests/test_aeb_kernel_matrix.py:103` |
| `test_aeb_required_active_backs_both_req_2_and_req_4` | Aeb required active backs both req 2 and req 4. | `tests/test_aeb_kernel_matrix.py:117` |
| `test_declared_scope_requirements_render_as_honest_gaps` | REQ-AEB-9 (vehicle-class eligibility) and REQ-AEB-10 (malfunction detection/mode controls) are named, sourced, and deliberately not Dafny targets for this kernel - intended_method DECLARED, so the gap note reads "intend… | `tests/test_aeb_kernel_matrix.py:127` |
| `test_committed_matrix_passes_the_structural_proven_check` | Committed matrix passes the structural proven check. | `tests/test_aeb_kernel_matrix.py:148` |

## Aeb Kernel Mutation Report (`tests/test_aeb_kernel_mutation_report.py`)

| Test | Description | Code |
|---|---|---|
| `test_report_total_and_outcome_counts` | Report total and outcome counts. | `tests/test_aeb_kernel_mutation_report.py:40` |
| `test_survivors_are_all_false_activation_non_negativity_precondition_weakenings` | Survivors are all false activation non negativity precondition weakenings. | `tests/test_aeb_kernel_mutation_report.py:55` |
| `test_unclassifiable_are_all_coi_on_target_equality_guard_clauses` | Unclassifiable are all coi on target equality guard clauses. | `tests/test_aeb_kernel_mutation_report.py:66` |

## Aeb Kernel Spec Lint (`tests/test_aeb_kernel_spec_lint.py`)

| Test | Description | Code |
|---|---|---|
| `test_every_function_precondition_is_satisfiable` | None of the six functions' requires clauses are vacuous - a Dafny 'clean pass' on aeb_kernel.dfy proves what it appears to prove, not something trivially true because no input could ever satisfy the precondition. | `tests/test_aeb_kernel_spec_lint.py:32` |
| `test_no_function_has_weak_postcondition_warnings` | Every ensures clause in aeb_kernel.dfy is a bi-implication (<==>), not a bare one-way ==> - each function's postcondition pins its result exactly for every input, not just in one direction. | `tests/test_aeb_kernel_spec_lint.py:44` |

## Citation Gate (`tests/test_citation_gate.py`)

| Test | Description | Code |
|---|---|---|
| `test_confirms_a_real_nice_citation` | Confirms a real nice citation. | `tests/test_citation_gate.py:48` |
| `test_rejects_the_actual_fabricated_nice_1_1_2_claim` | The real event: a supplied document claimed NICE's Recommendation 1.1.2 "mandates the 2009 equation" - the real 1.1.2 says nothing of the sort (see NICE_NG203_1_1_2_REAL above, fetched directly). | `tests/test_citation_gate.py:60` |
| `test_rejects_the_actual_fabricated_nice_1_1_4_claim` | The real event: a supplied document claimed NICE's 1.1.4 says "Do not use a person's ethnicity to adjust their eGFR." The real 1.1.4 is about not eating meat before a blood test. | `tests/test_citation_gate.py:74` |
| `test_confirms_the_real_kdigo_recommendation` | Confirms the real kdigo recommendation. | `tests/test_citation_gate.py:87` |
| `test_rejects_the_actual_fabricated_kdigo_claim` | The real event: a supplied document claimed KDIGO's "Recommendation 1.1.2" (wrong number - the real one is 1.1.2.1) states "the explicit shift to the 2021 race-free equation." The real recommendation is about the eGFRcr… | `tests/test_citation_gate.py:97` |
| `test_normalization_survives_whitespace_and_case_differences` | The claim need not match the source's exact spacing/casing - PDF extraction in this repo has already been observed to produce unspaced text (sources/kdigo-2024-gfr-staging.md's extraction method note). | `tests/test_citation_gate.py:111` |
| `test_does_not_false_positive_on_an_unrelated_short_phrase` | Sanity check against the opposite failure mode - the gate shouldn't report CONFIRMED just because a short substring happens to appear somewhere unrelated. | `tests/test_citation_gate.py:125` |
| `test_does_not_false_positive_a_short_recommendation_number_inside_a_longer_one` | Real bug, found auditing this module against its own motivating case: normalization strips all punctuation for whitespace- robustness, so "1.1.2" normalizes to "112" - which is a genuine substring of "1.1.2.1" normalize… | `tests/test_citation_gate.py:138` |
| `test_exact_recommendation_number_still_confirms` | The fix above must not overcorrect into never matching numbers - an exact numeric identifier, with a real boundary, still confirms. | `tests/test_citation_gate.py:157` |
| `test_refuses_a_vacuous_empty_claim` | Refuses a vacuous empty claim. | `tests/test_citation_gate.py:169` |
| `test_not_found_verdict_never_claims_fabrication_is_certain` | Load-bearing wording check: a NOT_FOUND caveat must not overclaim - this is the exact honesty discipline this repo already applies to BOUNDED_CHECKED (evidence/model.py's CAVEAT map), extended here to citation checking. | `tests/test_citation_gate.py:175` |
| `test_verify_citations_batch_preserves_order` | Verify citations batch preserves order. | `tests/test_citation_gate.py:195` |

## Citation Registry (`tests/test_citation_registry.py`)

| Test | Description | Code |
|---|---|---|
| `test_real_repo_has_no_unmarked_annex_d_claims` | The regression test. | `tests/test_citation_registry.py:24` |
| `test_detects_a_fresh_unmarked_claim` | Detects a fresh unmarked claim. | `tests/test_citation_registry.py:38` |
| `test_allows_a_directly_quoted_occurrence` | Allows a directly quoted occurrence. | `tests/test_citation_registry.py:51` |
| `test_allows_an_occurrence_with_a_nearby_correction_marker` | Mirrors DEVLOG.md's actual pattern: the original, unquoted wrong text preserved verbatim (append-only discipline), immediately followed by a bracketed correction - never quoted, but clearly marked. | `tests/test_citation_registry.py:66` |
| `test_does_not_match_the_correct_true_statement` | "ISO 14971:2019 has no Annex D" is a TRUE statement (it's the finding itself), not a re-assertion of the wrong claim - the pattern requires "ISO 14971" immediately followed by "Annex D" (mod an optional possessive), whi… | `tests/test_citation_registry.py:85` |
| `test_matches_survive_a_markdown_line_wrap` | Matches survive a markdown line wrap. | `tests/test_citation_registry.py:100` |
| `test_untracked_markdown_is_not_scanned` | The exact case an external review (Qodo, PR #51) flagged: a workspace file that was never `git add`-ed must not affect the result, even though it asserts the banned claim unmarked. | `tests/test_citation_registry.py:117` |

## CLI (`tests/test_cli.py`)

| Test | Description | Code |
|---|---|---|
| `test_cli_build_matches_committed_artifact` | Cli build matches committed artifact. | `tests/test_cli.py:45` |
| `test_cli_writes_markdown_too` | Cli writes markdown too. | `tests/test_cli.py:68` |
| `test_cli_prints_to_stdout_when_no_output_path_given` | Cli prints to stdout when no output path given. | `tests/test_cli.py:93` |
| `test_cli_schema_validation_failure_is_a_clean_exit` | Cli schema validation failure is a clean exit. | `tests/test_cli.py:108` |
| `test_cli_conflict_failure_is_a_clean_exit` | Drives the CLI end to end (subprocess, real files) with a corrupted concrete store, proving Type 1 fires through the CLI path too, not just when build_matrix() is called from Python directly. | `tests/test_cli.py:124` |
| `test_cli_missing_required_arg_exits_nonzero` | Cli missing required arg exits nonzero. | `tests/test_cli.py:147` |
| `test_cli_tool_name_derived_from_manifest_not_hardcoded` | tool_versions is keyed by the manifest's own 'tool' field, not a hardcoded 'crosshair' string - a small genuine vocabulary-agnostic improvement over the existing generator scripts. | `tests/test_cli.py:152` |

## Conflict Check (`tests/test_conflict_check.py`)

| Test | Description | Code |
|---|---|---|
| `test_gate_passes_on_committed_variant_a` | Gate passes on committed variant a. | `tests/test_conflict_check.py:35` |
| `test_gate_passes_on_committed_variant_b` | Gate passes on committed variant b. | `tests/test_conflict_check.py:43` |
| `test_gate_passes_on_committed_variant_c` | Gate 4's asymmetry (variant C declared no top-down binding, so Type 1 had nothing to check there) closed 2026-07-06: metadata.c.yaml now carries the same top-down evidence declarations as variant A, for cross-checking o… | `tests/test_conflict_check.py:51` |
| `test_negative_case_scope_split_is_not_a_conflict` | Gate 2's ratified negative test case: REQ-GIP-1-4-12's kernel_scope (evidenced) vs. | `tests/test_conflict_check.py:68` |
| `test_positive_type1_concrete_identity_mismatch` | Gate 2's ratified positive Type 1 case: a top-down declared binding disagrees with the bottom-up evidence-store's self-declared owner. | `tests/test_conflict_check.py:82` |
| `test_positive_type1_shadow_binding_mismatch` | Same failure shape via variant B's shadow-pseudo-requirement form. | `tests/test_conflict_check.py:111` |
| `test_positive_type1_symbolic_file_mismatch` | A requirement declaring an implementation in a different file than the one the crosshair manifest actually captured. | `tests/test_conflict_check.py:131` |
| `test_build_matrix_folds_in_type1_check` | Step 3 (2026-07-06): the fold-in itself, proven by driving the real entry point rather than the underlying check function directly. | `tests/test_conflict_check.py:152` |
| `test_missing_declared_test_id_is_a_hard_error_not_a_silent_pass` | A declared test_id that doesn't exist in the evidence store at all is a different failure mode than a conflict (there's no second claim to disagree with) - it must not be silently treated as clean. | `tests/test_conflict_check.py:172` |
| `test_type2_gate_passes_on_committed_manifests` | All four committed manifests target distinct files, so none share an identity and there is nothing to disagree about - a real, honest zero, not an untested check. | `tests/test_conflict_check.py:187` |
| `test_positive_type2_outcome_mismatch` | The ratified positive Type 2 case: two manifests agree on tool, target, and enforced timeout (the same verification act) but report different exit codes - a real conflict, not covered by Type 1. | `tests/test_conflict_check.py:206` |
| `test_type2_different_targets_are_not_compared` | Two manifests for genuinely different targets are not a conflict even if their outcomes differ - Type 2 only compares claims about the SAME verification act. | `tests/test_conflict_check.py:232` |

## Dafny Adapter (`tests/test_dafny_adapter.py`)

| Test | Description | Code |
|---|---|---|
| `test_parses_real_committed_clean_capture` | Parses real committed clean capture. | `tests/test_dafny_adapter.py:28` |
| `test_refuses_real_committed_broken_capture` | The real broken capture fails on exit code alone (Dafny exits 4 on a postcondition failure, confirmed in KNOWN_LIMITATIONS.md Gate C1) - refused at the cheapest, most definitive check before the summary line is ever par… | `tests/test_dafny_adapter.py:43` |
| `test_refuses_nonzero_exit_code_before_parsing_output` | Refuses nonzero exit code before parsing output. | `tests/test_dafny_adapter.py:55` |
| `test_refuses_missing_summary_line` | A crash, a timeout, or a subcommand that never attempted verification (confirmed real: `dafny audit` prints exactly "Dafny program verifier did not attempt verification" on some inputs) must be refused, not silently tre… | `tests/test_dafny_adapter.py:61` |
| `test_false_zero_guard_is_not_fooled_by_a_substring_trap` | The core false-zero property: a literal "0 errors" substring appearing anywhere else in the output must not cause a false accept - only the verifier's own summary line's parsed count matters. | `tests/test_dafny_adapter.py:73` |
| `test_producing_a_proven_result_does_not_reopen_the_matrix_gate` | Belt and suspenders: even after constructing a real PROVEN VerificationResult via this adapter, assert_no_realized_proven still hard-blocks PROVEN from ever appearing in a rendered matrix row - Gate C2 (not built) is wh… | `tests/test_dafny_adapter.py:89` |

## Dafny Isolate (`tests/test_dafny_isolate.py`)

| Test | Description | Code |
|---|---|---|
| `test_parse_decls_finds_every_renal_function_and_datatype` | Parse decls finds every renal function and datatype. | `tests/test_dafny_isolate.py:26` |
| `test_leaf_function_isolates_to_itself_plus_datatypes_no_callers` | Leaf function isolates to itself plus datatypes no callers. | `tests/test_dafny_isolate.py:38` |
| `test_non_leaf_includes_transitive_callees_excludes_callers` | AssessRenalFunction calls GStage and RoundHalfUp (callees, kept) and is called by AssessRenalFunctionFromInputs (a caller, dropped). | `tests/test_dafny_isolate.py:48` |
| `test_full_down_closure_for_the_top_orchestrator` | AssessRenalFunctionFromInputs calls SelectFormula, AssessRenalFunction, CockcroftGaultCrClMlPerMin - transitively pulling in GStage and RoundHalfUp too. | `tests/test_dafny_isolate.py:60` |
| `test_self_reference_does_not_seed_the_closure` | A function names itself in its own ensures clauses; that must not be treated as a call that pulls anything extra in. | `tests/test_dafny_isolate.py:72` |
| `test_isolate_refuses_unknown_function` | Isolate refuses unknown function. | `tests/test_dafny_isolate.py:80` |
| `test_isolate_handles_attribute_bearing_declarations` | Dafny allows attribute blocks between the keyword and the name (`function {:axiom} Pow(...)`, `method {:vcs_split_on_every_assert} Foo(...)`). | `tests/test_dafny_isolate.py:85` |
| `test_synthetic_caller_is_excluded_even_when_it_shares_a_datatype` | Synthetic caller is excluded even when it shares a datatype. | `tests/test_dafny_isolate.py:112` |

## Dafny Mutate (`tests/test_dafny_mutate.py`)

| Test | Description | Code |
|---|---|---|
| `test_ror_against_real_spec_produces_expected_raw_and_filtered_counts` | Ror against real spec produces expected raw and filtered counts. | `tests/test_dafny_mutate.py:41` |
| `test_ror_filters_equality_clauses_and_the_tightened_reverse_flow_clause` | The pinning/second-disjunct '==' clauses filter their weakenings to <=/>=; REQ-GIP-1-8-1's tightened '>' clause (post Gate C5 fix) filters its own weakenings to >=/!= - a proof of `x > 0` universally implies both, so th… | `tests/test_dafny_mutate.py:48` |
| `test_ror_filters_chain_direction_incompatible_mutants_on_the_chained_clause` | Built 2026-07-07 from external research: naively mutating one side of the chained `0.0 <= dose <= maxSafeDoseMgPerHr` to a descending operator (>=, >) produces a Dafny PARSE error, not a semantic test (Dafny Reference M… | `tests/test_dafny_mutate.py:72` |
| `test_lor_finds_the_single_or_site_and_does_not_filter_it` | Lor finds the single or site and does not filter it. | `tests/test_dafny_mutate.py:102` |
| `test_aor_returns_empty_against_real_spec_clauses_alone` | No requires/ensures clause of CalculateHourlyDose contains arithmetic - confirmed by an empty result, not just left unexercised, when no companion function_name is given. | `tests/test_dafny_mutate.py:109` |
| `test_aor_against_expecteddose_body_restricts_to_plus_minus_only` | Built 2026-07-07 from external research: MutDafny's own AOR restriction (+/-/* freely interchange; / only with %, not present in this spec) means the one `*` in ExpectedDose's body never gets a `/` candidate sent to rea… | `tests/test_dafny_mutate.py:116` |
| `test_aor_never_touches_the_method_body_only_the_function_body` | Mutation testing perturbs the SPEC (ExpectedDose, referenced by a pinning ensures clause), never CalculateHourlyDose's own trusted `{...}` implementation, which recomputes the same multiplication but must never be mutat… | `tests/test_dafny_mutate.py:137` |
| `test_coi_wraps_every_ensures_clause_and_only_ensures_clauses` | Coi wraps every ensures clause and only ensures clauses. | `tests/test_dafny_mutate.py:151` |
| `test_sor_and_hor_not_applicable_confirmed_by_absence_of_syntax` | SOR/HOR aren't implemented at all - this confirms the reason is real (checked), not assumed: the spec genuinely contains no set syntax and no heap/object-state syntax anywhere. | `tests/test_dafny_mutate.py:160` |
| `test_mutated_source_changes_exactly_the_targeted_operator` | Mutated source changes exactly the targeted operator. | `tests/test_dafny_mutate.py:171` |
| `test_generate_mutants_aggregates_all_five_implemented_classes` | Generate mutants aggregates all five implemented classes. | `tests/test_dafny_mutate.py:192` |
| `test_generate_mutants_with_function_name_includes_body_aor_and_lvr` | Generate mutants with function name includes body aor and lvr. | `tests/test_dafny_mutate.py:203` |
| `test_tokenize_with_spans_handles_function_call_commas` | Tokenize with spans handles function call commas. | `tests/test_dafny_mutate.py:209` |
| `test_tokenize_with_spans_refuses_unknown_syntax` | Tokenize with spans refuses unknown syntax. | `tests/test_dafny_mutate.py:216` |
| `test_tokenize_with_spans_handles_assignment_and_semicolon` | Needed for function-body scanning (`var rawDose := a * b;`) - requires/ensures clauses never contain `:=` or `;`, so this wasn't needed before the AOR function-body extension. | `tests/test_dafny_mutate.py:221` |
| `test_chain_incompatible_matches_dafny_direction_rule` | Direct unit test of the pure helper, independent of the real spec: ascending (</<=) and descending (>/>=) can't mix in one chain; EQ/NE are always compatible with either direction; a chain link with no directional sibli… | `tests/test_dafny_mutate.py:232` |
| `test_ar_group_incompatible_matches_mutdafny_restriction` | Direct unit test of the pure helper: +/-/* freely interchange; / is only compatible with % (not present in _AR_TEXT at all), so every +/-/* <-> / crossing is incompatible in both directions. | `tests/test_dafny_mutate.py:248` |
| `test_locate_function_body_arithmetic_sites_finds_exactly_the_one_star` | Locate function body arithmetic sites finds exactly the one star. | `tests/test_dafny_mutate.py:260` |
| `test_ror_polarity_flips_between_requires_and_ensures` | The load-bearing, non-obvious design property: strengthening a requires clause is trivial (the original proof still applies under a narrower hypothesis) while weakening an ensures clause is trivial (whatever already sat… | `tests/test_dafny_mutate.py:269` |
| `test_locate_clause_numeric_literal_sites_finds_every_zero_with_correct_role` | Every literal in dosage.dfy's real clauses is exactly 0.0, at 5 sites, each immediately adjacent to a comparison operator - verified directly against the real spec, not assumed. | `tests/test_dafny_mutate.py:310` |
| `test_locate_clause_numeric_literal_sites_accepts_arithmetic_embedded_literal` | Pinning fix, 2026-07-19 (Gate C5 finding against renal_adjustment.dfy's RoundHalfUp and CockcroftGaultCrClMlPerMin, both of which have real literals in exactly this shape - `140` in `(140 - ageYears) as real) == ...` an… | `tests/test_dafny_mutate.py:328` |
| `test_locate_clause_numeric_literal_sites_still_refuses_truly_ambiguous_literal` | The narrowed refusal this module still makes after the 2026-07-19 fix above: a literal adjacent to neither a comparison NOR an arithmetic operator - here, a bare function-call argument - has no comparison-relevant role… | `tests/test_dafny_mutate.py:354` |
| `test_locate_clause_numeric_literal_sites_still_refuses_when_no_comparison_present` | A second still-refused shape: an arithmetic-adjacent literal in a clause with NO comparison operator anywhere. | `tests/test_dafny_mutate.py:367` |
| `test_locate_function_body_numeric_literal_sites_finds_both_zeros` | Locate function body numeric literal sites finds both zeros. | `tests/test_dafny_mutate.py:380` |
| `test_lvr_trivial_matches_the_magnitude_implication_principle` | Direct unit test of the pure helper, independent of the real spec. | `tests/test_dafny_mutate.py:389` |
| `test_lvr_against_real_spec_matches_the_hand_derived_prediction` | The scoping session's own hand-worked prediction (roadmap doc's Gate C5 LVR sub-plan): 14 raw mutants (7 sites x 2 candidates), 4 filtered as magnitude-implied, 10 sent to real verification. | `tests/test_dafny_mutate.py:409` |
| `test_int_literal_lvr_mutant_stays_int_typed` | Real bug found applying this module to renal_adjustment.dfy (2026-07-09): formatting an int-typed literal's LVR mutant as a decimal (`90.01`) produces a genuine Dafny static type error ('arguments to >= must have a comm… | `tests/test_dafny_mutate.py:426` |
| `test_lvr_mutated_source_changes_exactly_the_targeted_literal` | Lvr mutated source changes exactly the targeted literal. | `tests/test_dafny_mutate.py:457` |

## Dafny NL Summary (`tests/test_dafny_nl_summary.py`)

| Test | Description | Code |
|---|---|---|
| `test_real_dosage_spec_summary_lists_parameters` | Real dosage spec summary lists parameters. | `tests/test_dafny_nl_summary.py:18` |
| `test_real_dosage_spec_summary_lists_preconditions_verbatim` | Real dosage spec summary lists preconditions verbatim. | `tests/test_dafny_nl_summary.py:26` |
| `test_real_dosage_spec_summary_cites_the_right_requirement_per_postcondition` | The load-bearing property: each postcondition's citation must match what the source itself declares, not be inferred or guessed. | `tests/test_dafny_nl_summary.py:33` |
| `test_gloss_renders_common_operators_as_words` | Gloss renders common operators as words. | `tests/test_dafny_nl_summary.py:51` |
| `test_multiline_clause_is_summarized_correctly_not_refused` | Real gap found 2026-07-10 building Gate C6 for drug_interaction_checker.dfy: its one requires clause is the first genuinely multi-line clause this repo has built against (every clause in dosage.dfy/renal_adjustment.dfy… | `tests/test_dafny_nl_summary.py:64` |
| `test_standalone_comment_inside_a_multiline_clause_still_refuses` | A multi-line clause's continuation lines are only ever joined up to the first blank line, standalone `//`-comment line, or next clause keyword - deliberately, so a free-floating block comment BETWEEN two clauses is neve… | `tests/test_dafny_nl_summary.py:89` |
| `test_real_ddi_spec_has_no_requires_clause_since_req_ddi_5` | End-to-end confirmation against the real, committed spec. | `tests/test_dafny_nl_summary.py:114` |
| `test_method_with_no_requires_or_ensures_still_summarizes` | Method with no requires or ensures still summarizes. | `tests/test_dafny_nl_summary.py:136` |
| `test_summary_is_deterministic` | No timestamps, no randomness - the same source always produces byte-identical output, since this feeds a committed, reviewable artifact. | `tests/test_dafny_nl_summary.py:147` |
| `test_summarizes_a_function_not_just_a_method` | The real gap: _find_method_header only matched `method` until this fix - every real Dafny function in this repo before renal_adjustment.dfy was a companion to a method (ExpectedDose next to CalculateHourlyDose), so summ… | `tests/test_dafny_nl_summary.py:169` |
| `test_lowercase_suffixed_req_id_is_cited_in_full_not_truncated` | The real bug: REQ-RENAL-1a was silently cited as REQ-RENAL-1 (the trailing lowercase 'a' dropped by the old [A-Z0-9-] character class) before this fix - a genuine citation-accuracy defect, not a hypothetical, caught by… | `tests/test_dafny_nl_summary.py:181` |
| `test_all_five_renal_functions_summarize_without_error` | Every function in the real, committed renal_adjustment.dfy summarizes cleanly - the concrete end-to-end confirmation for Gate C6's own sign-off document, not just a synthetic fixture. | `tests/test_dafny_nl_summary.py:193` |

## Dafny Spec Lint (`tests/test_dafny_spec_lint.py`)

| Test | Description | Code |
|---|---|---|
| `test_real_dosage_kernel_precondition_is_satisfiable` | True-negative: the real, committed dosage.dfy spec's requires clauses are a genuine, non-vacuous precondition - the checker must not cry wolf on legitimate specs. | `tests/test_dafny_spec_lint.py:30` |
| `test_real_vacuous_precondition_fixture_is_unsat` | The load-bearing regression: examples/dosage_calculator/ vacuous_precondition_probe.dfy is a REAL, committed Dafny file whose verifier run is a genuine clean pass (confirmed separately - Dafny reports 1 verified, 0 erro… | `tests/test_dafny_spec_lint.py:39` |
| `test_requires_clause_extraction_matches_the_real_dosage_spec` | Requires clause extraction matches the real dosage spec. | `tests/test_dafny_spec_lint.py:51` |
| `test_requires_clause_extraction_matches_a_function_not_just_a_method` | Real gap surfaced by renal_adjustment.dfy (2026-07-08): every Dafny declaration this module's _find_method_header had ever been asked to locate before was a `method` (dosage.dfy's ExpectedDose function was never passed… | `tests/test_dafny_spec_lint.py:59` |
| `test_conjunction_of_satisfiable_clauses_is_satisfiable` | Conjunction of satisfiable clauses is satisfiable. | `tests/test_dafny_spec_lint.py:70` |
| `test_quantifier_in_precondition_is_refused_not_mistranslated` | Tier 1: an out-of-scope construct (forall) must raise, not be silently dropped or mistranslated into something satisfiable-looking. | `tests/test_dafny_spec_lint.py:85` |
| `test_unknown_parameter_type_is_refused` | Unknown parameter type is refused. | `tests/test_dafny_spec_lint.py:100` |
| `test_unreferenced_unsupported_type_parameter_does_not_block_the_check` | A parameter of an unsupported type (e.g. | `tests/test_dafny_spec_lint.py:113` |
| `test_referenced_simple_enum_datatype_parameter_is_now_modeled` | Extended 2026-07-10 (drug_interaction_checker.dfy's Gate C3): a referenced parameter whose type is a SIMPLE Dafny datatype - every constructor zero-argument, e.g. | `tests/test_dafny_spec_lint.py:132` |
| `test_referenced_unsupported_type_parameter_still_refuses` | The narrowing above must not swallow a real refusal - if the unsupported-type parameter IS referenced by a requires clause AND it's not a simple enum (here, a parameterized constructor - EnumSort can't represent a datat… | `tests/test_dafny_spec_lint.py:154` |
| `test_real_drug_interaction_checker_precondition_is_satisfiable` | True-positive regression against the real, committed spec: the exact scenario that originally exposed this gap. | `tests/test_dafny_spec_lint.py:174` |
| `test_enum_comparison_precondition_can_still_be_unsat` | The EnumSort extension must not make every datatype-comparing precondition trivially sat - a genuinely contradictory one (no value of the enum can be both A and B) must still be caught. | `tests/test_dafny_spec_lint.py:185` |
| `test_ordering_operator_on_enum_datatype_refuses_cleanly_not_a_crash` | Real bug found 2026-07-10 mutation-testing drug_interaction_checker.dfy: a ROR mutant introducing <=/</>/>= between two datatype (EnumSort) operands used to crash with a raw Python TypeError ("'<=' not supported between… | `tests/test_dafny_spec_lint.py:203` |
| `test_parse_enum_datatypes_handles_multiline_declaration` | Dafny datatype declarations aren't required to fit on one line - drug_interaction_checker.dfy's own Agent datatype spans several. | `tests/test_dafny_spec_lint.py:225` |
| `test_parse_enum_datatypes_excludes_parameterized_constructors` | A datatype with any parameterized constructor isn't a simple enumeration and isn't representable as a Z3 EnumSort - it must be excluded from the result entirely, not partially or incorrectly modeled. | `tests/test_dafny_spec_lint.py:247` |
| `test_nat_parameter_gets_implicit_nonnegativity_constraint` | requires n < 0 on a nat parameter must be unsat - Dafny's own nat semantics (>= 0) are load-bearing for the satisfiability check, not something the checker can afford to ignore. | `tests/test_dafny_spec_lint.py:262` |
| `test_method_with_no_requires_clause_is_trivially_satisfiable` | Method with no requires clause is trivially satisfiable. | `tests/test_dafny_spec_lint.py:278` |
| `test_real_dosage_kernel_has_no_weak_postcondition_warnings` | True-negative: the real dosage.dfy ensures clauses use <=/==/\|\|, never ==>, so the heuristic must not flag anything on the live spec. | `tests/test_dafny_spec_lint.py:292` |
| `test_one_way_implication_postcondition_is_flagged` | The exact failure pattern the roadmap names: a one-way implication lets a broken implementation (e.g. | `tests/test_dafny_spec_lint.py:300` |
| `test_bi_implication_postcondition_is_not_flagged` | True-negative: a clause already using <==> is exactly what the heuristic is nudging authors toward - it must not also be flagged. | `tests/test_dafny_spec_lint.py:317` |

## Dafny STP Suite (`tests/test_dafny_stp_suite.py`)

| Test | Description | Code |
|---|---|---|
| `test_underconstrained_spec_still_verifies_cleanly_on_its_own` | The preserved original spec's bug is a WEAKNESS, not a verification failure - dosage_underconstrained.dfy must still pass Dafny's own check by itself. | `tests/test_dafny_stp_suite.py:29` |
| `test_stp_suite_passes_against_the_fixed_spec` | All STP lemmas (3 ACCEPT + 2 REJECT + 1 ACCEPT for the reverse-flow case) verify cleanly against the fixed dosage.dfy, included via `include "dosage.dfy"`. | `tests/test_dafny_stp_suite.py:38` |
| `test_stp_suite_fails_against_the_preserved_weak_spec` | The mechanized 'before' proof: the same two REJECT lemmas, run against the preserved original weak spec instead of the fix, FAIL to verify - real, negative capture, not smoothed over. | `tests/test_dafny_stp_suite.py:48` |
| `test_reject_lemmas_target_in_bounds_wrong_values_not_out_of_bounds_ones` | Regression on a mistake caught during this build: an early draft used 500.0 (the raw unclamped product) as the 'wrong' ceiling-clamped value, but 500.0 already violates the weak spec's own 0<=dose<=max bound directly -… | `tests/test_dafny_stp_suite.py:60` |
| `test_fixed_spec_pins_the_dose_value_no_longer_just_bounds_it` | The actual fix, checked directly against the real dosage.dfy source: the pinning ensures clause referencing ExpectedDose must be present, not just the original two bounding clauses. | `tests/test_dafny_stp_suite.py:75` |
| `test_preserved_underconstrained_spec_lacks_the_pinning_clause` | The honesty exhibit must be a byte-for-byte preservation of the gap, not a partially-fixed copy - it must not declare an ExpectedDose function or reference one in an ensures clause (the header comment's prose discussion… | `tests/test_dafny_stp_suite.py:84` |

## Dafny Timeout Masking (`tests/test_dafny_timeout_masking.py`)

| Test | Description | Code |
|---|---|---|
| `test_real_resource_limited_capture_is_refused` | Real, committed capture: the actual dosage.dfy spec run for real under `--resource-limit=1`. | `tests/test_dafny_timeout_masking.py:23` |
| `test_out_of_resource_marker_refused_even_with_a_zero_exit_code` | Defense in depth: if exit_code were ever 0 alongside an 'out of resource' summary tail (not observed in this repo's real captures, but not something the parser should have to trust blindly either), the summary-line hard… | `tests/test_dafny_timeout_masking.py:36` |
| `test_out_of_memory_marker_refused_even_with_a_zero_exit_code` | Out of memory marker refused even with a zero exit code. | `tests/test_dafny_timeout_masking.py:48` |
| `test_timed_out_marker_refused_even_with_a_zero_exit_code` | Timed out marker refused even with a zero exit code. | `tests/test_dafny_timeout_masking.py:55` |
| `test_ambiguous_multiple_summary_lines_are_refused` | A capture with more than one summary-line match must be refused outright rather than silently trusting whichever one regex finds first - Tier 1, don't guess which is authoritative. | `tests/test_dafny_timeout_masking.py:62` |
| `test_real_committed_clean_capture_still_accepted` | Regression: Gate C1's real clean capture (no incomplete-run marker, exactly one summary line) must still parse to PROVEN after the vector 3 hardening - the new checks must not regress the happy path. | `tests/test_dafny_timeout_masking.py:75` |

## Dafny Wiring (`tests/test_dafny_wiring.py`)

| Test | Description | Code |
|---|---|---|
| `test_real_formal_artifact_has_two_proven_rows` | Real formal artifact has two proven rows. | `tests/test_dafny_wiring.py:64` |
| `test_real_formal_artifact_passes_the_structural_proven_check` | assert_no_realized_proven (ruling R3) must accept this real, legitimate dafny-sourced PROVEN row - not just in theory (Gate C2's tests) but against the actual generated artifact. | `tests/test_dafny_wiring.py:74` |
| `test_variant_a_has_dafny_evidence_and_a_proven_record` | Variant a has dafny evidence and a proven record. | `tests/test_dafny_wiring.py:81` |
| `test_variant_b_has_dafny_shadow_rows_and_a_proven_record` | Variant b has dafny shadow rows and a proven record. | `tests/test_dafny_wiring.py:98` |
| `test_full_fact_equality_gate_passes_with_intent_true_everywhere` | The end state this whole extension was for: run_gate() (unchanged core logic, now including traceability_matrix.formal.json as a full peer) passes with intent_ok True for both formally-proven requirements across every v… | `tests/test_dafny_wiring.py:113` |
| `test_reconcile_intent_comparison_is_subset_not_strict_equality` | The load-bearing fix that made folding formal.json into run_gate() possible: a variant missing a requirement entirely (formal.json never has one for REQ-DOSE-003) must not fail the gate on that basis alone - only an act… | `tests/test_dafny_wiring.py:126` |
| `test_reconcile_still_rejects_a_completely_unknown_requirement` | Subset semantics must not become 'anything goes': a requirement id the other artifacts have never heard of at all is still a hard failure - caught here by the facts-equality check (an even earlier, stricter gate than th… | `tests/test_dafny_wiring.py:156` |
| `test_dafny_record_refuses_an_unsatisfiable_precondition` | The Z3 gate lives inside the binder (dafny_record), as decided. | `tests/test_dafny_wiring.py:200` |
| `test_dafny_record_still_enforces_the_false_zero_guard` | The second, independent gate (Gate C1's parser) still applies - a broken capture must be refused even with a perfectly satisfiable precondition. | `tests/test_dafny_wiring.py:223` |
| `test_dafny_record_accepts_the_real_committed_capture` | Dafny record accepts the real committed capture. | `tests/test_dafny_wiring.py:237` |
| `test_dafny_binding_conflict_catches_a_spec_target_mismatch` | Dafny binding conflict catches a spec target mismatch. | `tests/test_dafny_wiring.py:247` |
| `test_dafny_binding_conflict_catches_a_missing_capture` | Dafny binding conflict catches a missing capture. | `tests/test_dafny_wiring.py:271` |
| `test_dafny_binding_conflict_catches_a_shadow_spec_target_mismatch` | Variant B's dafny shadow shape, not just A/C's evidence list - the parent id is what gets reported as the declared owner. | `tests/test_dafny_wiring.py:288` |
| `test_dafny_binding_conflict_is_a_noop_when_dafny_store_is_none` | A caller that never intends to bind dafny evidence at all - the conflict check must not fire just because metadata happens to declare it. | `tests/test_dafny_wiring.py:309` |
| `test_real_metadata_and_dafny_store_have_no_conflicts` | Real metadata and dafny store have no conflicts. | `tests/test_dafny_wiring.py:326` |
| `test_build_matrix_c_formal_end_to_end_matches_committed` | Build matrix c formal end to end matches committed. | `tests/test_dafny_wiring.py:337` |
| `test_cli_build_matches_committed_with_dafny_captures` | The CLI regression this wiring would otherwise have caused: once metadata.a.yaml/metadata.b.yaml declare dafny evidence, the CLI must be given --dafny-captures or build_matrix() refuses outright - this is what keeps tha… | `tests/test_dafny_wiring.py:379` |
| `test_cli_refuses_variant_a_without_dafny_captures` | Confirms the regression is real, not hypothetical: without --dafny-captures, the CLI must refuse (not silently drop the dafny evidence) once metadata.a.yaml declares it. | `tests/test_dafny_wiring.py:402` |

## Docs Current With Devlog (`tests/test_docs_current_with_devlog.py`)

| Test | Description | Code |
|---|---|---|
| `test_current_state_docs_are_not_older_than_devlogs_newest_entry` | Current state docs are not older than devlogs newest entry. | `tests/test_docs_current_with_devlog.py:40` |

## Dosage Concrete (`tests/test_dosage_concrete.py`)

| Test | Description | Code |
|---|---|---|
| `test_dosage_concrete` | Requirement: see case['requirement_id'] (mapping per metadata.yaml). | `tests/test_dosage_concrete.py:78` |

## Dosage Differential (`tests/test_dosage_differential.py`)

| Test | Description | Code |
|---|---|---|
| `test_committed_driver_matches_the_generator` | The generated-artifact-matches-its-generator check, same discipline as evidence/cli.py's and evidence/test_catalog.py's own tests. | `tests/test_dosage_differential.py:41` |
| `test_captured_results_show_every_vector_matched` | The regression test proper: the last real `dafny run` capture agreed with dosage.py on every vector. | `tests/test_dosage_differential.py:54` |
| `test_captured_results_cover_every_current_vector` | Sanity check that the capture wasn't taken against a stale vector list - every vector in dosage_differential_vectors.py right now has a corresponding captured result, and vice versa. | `tests/test_dosage_differential.py:66` |
| `test_python_side_reproduces_the_captured_values_live` | Re-runs dosage.py's real calculate_hourly_dose (no Dafny needed) against every vector and confirms it still produces the dose the last capture recorded - catches a Python-side regression between captures without requiri… | `tests/test_dosage_differential.py:80` |
| `test_real_literal_rejects_fractional_scientific_notation` | Qodo review finding on PR #55: _dafny_real_literal's scientific- notation branch used to convert through int(value) unconditionally, which is lossless for the two committed vectors (1e10, 1e308 - both already integer-va… | `tests/test_dosage_differential.py:101` |
| `test_real_literal_still_handles_committed_large_integer_vectors` | The two real scientific-notation-repr'd values this file's vectors actually use (1e10, 1e308) stay lossless through the hardened path - both are exactly integer-valued floats, so int() on them is exact regardless of mag… | `tests/test_dosage_differential.py:113` |
| `test_overflow_vector_is_explicitly_documented_as_coincidental` | This harness's one real scoping caveat, checked mechanically so it can't silently disappear on a future edit: the overflow-domain vector's own note must state plainly that its agreement is coincidental to the chosen mag… | `tests/test_dosage_differential.py:122` |

## Drug Interaction Checker Dafny Wiring (`tests/test_drug_interaction_checker_dafny_wiring.py`)

| Test | Description | Code |
|---|---|---|
| `test_dafny_record_produces_a_real_proven_record` | dafny_record() against the real, committed capture -- not a synthetic fixture -- exercises both gates it's documented to run: Gate C3 vector 1 (Z3 precondition satisfiability, now able to model CheckInteraction's dataty… | `tests/test_drug_interaction_checker_dafny_wiring.py:45` |
| `test_real_record_passes_r3_cleanly` | The real record, wrapped in a minimal matrix, must pass assert_no_realized_proven without complaint -- confirms R3 doesn't reject dafny_record()'s own honest output for this example. | `tests/test_drug_interaction_checker_dafny_wiring.py:58` |
| `test_r3_still_refuses_wrong_method_for_this_records_shape` | R3 does not trust dafny_record()'s own diligence (per that function's docstring) -- it must independently refuse a hand-tampered copy of this real record claiming a non-dafny method, confirmed against this example's act… | `tests/test_drug_interaction_checker_dafny_wiring.py:67` |
| `test_r3_still_refuses_incomplete_verifier_status_for_this_records_shape` | Same independent-refusal confirmation for the second half of R3's check -- a dafny-method record without verifier_completion_status == 'completed' must still be refused, even though it otherwise matches this example's r… | `tests/test_drug_interaction_checker_dafny_wiring.py:80` |

## Drug Interaction Checker Matrix (`tests/test_drug_interaction_checker_matrix.py`)

| Test | Description | Code |
|---|---|---|
| `test_cli_omitting_manifest_and_concrete_entirely_still_works` | The real point of this test file's existence: --manifest and --concrete are genuinely optional now, not just defaulted to an empty stub file - this example passes neither flag at all. | `tests/test_drug_interaction_checker_matrix.py:63` |
| `test_cli_writes_markdown_matching_committed` | Cli writes markdown matching committed. | `tests/test_drug_interaction_checker_matrix.py:72` |
| `test_four_requirements_share_the_one_real_proof` | REQ-DDI-1/2/3/4 all bind to the SAME CheckInteraction capture - the first time this repo's matrix binder has been exercised with a many-requirements-to-one-proof shape (every dosage_calculator/ renal_adjustment requirem… | `tests/test_drug_interaction_checker_matrix.py:93` |
| `test_req_ddi_5_shares_check_interaction_capture_as_a_fifth_binding` | REQ-DDI-5 (the TreatmentIndication axis, built 2026-07-12) binds the SAME CheckInteraction capture REQ-DDI-1/2/3/4 already bind - a fifth requirement sharing one proof, not a new capture. | `tests/test_drug_interaction_checker_matrix.py:111` |
| `test_req_ddi_6_binds_its_own_separate_dose_reduction_capture` | REQ-DDI-6 (the numeric dose-reduction targets, built 2026-07-12) binds DoseReductionTargetMg - a DIFFERENT Dafny method than CheckInteraction, the first time this repo's matrix binder has bound two different methods fro… | `tests/test_drug_interaction_checker_matrix.py:129` |
| `test_no_gap_rows_remain_in_this_example` | As of REQ-DDI-6 (2026-07-12), every one of this example's six requirements has real, bound evidence - confirmed directly across the whole matrix, not just the two rows the tests above check individually. | `tests/test_drug_interaction_checker_matrix.py:148` |
| `test_no_crosshair_evidence_renders_bounds_as_explicitly_not_applicable` | Real, notable fact about this artifact: the header's bounds block reads a clear N/A, not a bare 'None' that could be misread as a data gap rather than the honest 'no crosshair pipeline exists for this example' it actual… | `tests/test_drug_interaction_checker_matrix.py:159` |
| `test_committed_matrix_passes_the_structural_proven_check` | R3 (assert_no_realized_proven) re-checked directly against the real committed artifact, not just trusted because build_matrix() itself calls it internally at generation time. | `tests/test_drug_interaction_checker_matrix.py:172` |

## Drug Interaction Checker Mutation Report (`tests/test_drug_interaction_checker_mutation_report.py`)

| Test | Description | Code |
|---|---|---|
| `test_report_total_and_outcome_counts` | Report total and outcome counts. | `tests/test_drug_interaction_checker_mutation_report.py:140` |
| `test_every_verified_mutant_was_isolated` | Since 2026-07-20 this example runs through the sanctioned evidence/gate_c5_runner.py, so every mutant reaching real Dafny verification is verified in ISOLATION (the mutated function plus its callees and datatypes, never… | `tests/test_drug_interaction_checker_mutation_report.py:155` |
| `test_dose_reduction_target_mg_unclassifiable_results_are_the_same_named_type_error_case_at_full_scale` | The datatype-ordering type-error category (ROR mutating <=/>= onto a datatype-vs-datatype equality, refused by evidence/dafny_spec_lint.py's Z3 translator rather than crashing or guessing) now appears at its real, full… | `tests/test_drug_interaction_checker_mutation_report.py:176` |
| `test_ddi5_indication_disjunction_survivors_are_now_only_the_deeper_lor_vacuity_case` | Shrunk sharply by Run 4's fix (28 -> 4 of CheckInteraction's survivors): one LOR survivor per REQ-DDI-5 clause (Rifampicin/Carbamazepine/Phenytoin/Phenobarbital + Apixaban), `\|\|` mutated to `&&` on `(treatmentIndication… | `tests/test_drug_interaction_checker_mutation_report.py:216` |
| `test_ensures_survivors_are_a_broadly_true_consequent_not_load_bearing_antecedent` | Pre-existing category (3 of CheckInteraction's 31 survivors, unchanged this session): ROR on the SSRIOrSNRI/Dabigatran/no-risk- factor clause's `doac == Dabigatran` antecedent (mutated to !=, <, >). | `tests/test_drug_interaction_checker_mutation_report.py:287` |
| `test_check_interaction_survivors_dropped_sharply_after_the_scope_leak_fix` | CheckInteraction WAS touched in Run 4 (unlike Runs 2-3, which only touched DoseReductionTargetMg) - fixing the apixaban scope-leak bug (branching the four inducer match arms on treatmentIndication instead of ignoring it… | `tests/test_drug_interaction_checker_mutation_report.py:316` |
| `test_dose_reduction_target_mg_survivors_are_guard_antecedent_pattern_at_full_scale` | 37 survivors, all on DoseReductionTargetMg's ensures clauses (down from 43 - the 6 requires-clause indication-guard survivors are no longer counted as survivors as of Run 5, since the STP-suite escalation now catches th… | `tests/test_drug_interaction_checker_mutation_report.py:334` |
| `test_dose_reduction_target_mg_requires_clause_indication_guard_is_now_caught_by_the_stp_suite` | Run 5's real, measured effect: the 6 requires-clause ROR mutants on the indication guard's own comparisons (`treatmentIndication == AFStrokePrevention`, `treatmentIndication == RecurrentVTEPrevention`, 3 ROR variants ea… | `tests/test_drug_interaction_checker_mutation_report.py:375` |
| `test_stp_escalation_never_silently_folds_an_inconclusive_check_into_survived` | A Qodo code-review finding on this PR's own diff (not part of the original hand-probing): an earlier draft of the escalation only handled `stp_outcome == "killed"`, silently leaving a mutant `survived` if the STP-suite… | `tests/test_drug_interaction_checker_mutation_report.py:404` |
| `test_dose_reduction_target_mg_doac_agent_requires_comparisons_are_all_killed` | Unlike the indication sub-condition (redundant, tested above), the requires clause's own doac==Dabigatran/agent==Verapamil and doac==Edoxaban comparisons ARE load-bearing: mutating any of them genuinely changes which (d… | `tests/test_drug_interaction_checker_mutation_report.py:438` |
| `test_dose_reduction_target_mg_lvr_mutants_all_killed` | The 10 clause-level LVR mutants (110->109/111, 30->29/31 x4) are ALL killed, none survived - confirmed directly, not assumed from the absence of "LVR" in the survivor list above. | `tests/test_drug_interaction_checker_mutation_report.py:468` |
| `test_all_survivors_are_accounted_for_by_the_three_named_categories` | No fourth, unexplained survivor category exists - the 4 REQ-DDI-5 LOR-vacuity survivors, the 3 pre-existing SSRIOrSNRI survivors, and the 37 DoseReductionTargetMg ensures-clause guard-antecedent survivors add up to the… | `tests/test_drug_interaction_checker_mutation_report.py:483` |

## Drug Interaction Checker Spec Lint (`tests/test_drug_interaction_checker_spec_lint.py`)

| Test | Description | Code |
|---|---|---|
| `test_check_interaction_precondition_is_satisfiable` | CheckInteraction has no requires clause at all as of REQ-DDI-5 (2026-07-12) -- the precondition that used to exclude the two agents' apixaban cells (Gate 1c Finding 2) was removed once TreatmentIndication closed those c… | `tests/test_drug_interaction_checker_spec_lint.py:36` |
| `test_check_interaction_datatype_comparisons_still_modeled_via_ensures` | Historical regression, still relevant after REQ-DDI-5: the original gap this file's module docstring describes was CheckInteraction's requires clause directly comparing doac/agent (simple-enum datatypes) against named c… | `tests/test_drug_interaction_checker_spec_lint.py:50` |
| `test_check_interaction_weak_postcondition_count_matches_the_real_spec` | Every one of CheckInteraction's 68 pinning ensures clauses uses a one-way ==> -- expected, not a regression, same pattern already established for renal_adjustment's GStage/SelectFormula/ AssessRenalFunction: each clause… | `tests/test_drug_interaction_checker_spec_lint.py:68` |
| `test_dose_reduction_target_mg_precondition_is_satisfiable` | DoseReductionTargetMg's requires clause -- exactly the five real (doac, agent) pairs sources/sps-doac-interactions-2024.md states a numeric target for -- is not vacuous: a real Z3 model exists (unlike an accidentally-un… | `tests/test_drug_interaction_checker_spec_lint.py:104` |
| `test_dose_reduction_target_mg_weak_postcondition_count` | All 5 pinning ensures clauses use a one-way ==>, same pattern as CheckInteraction's own clauses -- expected, not a regression. | `tests/test_drug_interaction_checker_spec_lint.py:115` |

## Fact Equality (`tests/test_fact_equality.py`)

| Test | Description | Code |
|---|---|---|
| `test_gate_passes_on_committed_artifacts` | 9 facts, not 7 (2026-07-07, Gate 2/C2-C4 wiring extended to variants A/B): +1 real dafny fact each for REQ-GIP-1-4-12 and REQ-GIP-1-8-1. | `tests/test_fact_equality.py:21` |
| `test_gate_fails_on_fact_divergence` | Gate fails on fact divergence. | `tests/test_fact_equality.py:41` |
| `test_gate_fails_on_intent_divergence` | Gate fails on intent divergence. | `tests/test_fact_equality.py:50` |
| `test_gate_fails_on_base_subset_divergence` | Gate fails on base subset divergence. | `tests/test_fact_equality.py:61` |

## Gate C5 Runner (`tests/test_gate_c5_runner.py`)

| Test | Description | Code |
|---|---|---|
| `test_in_file_callers_reverse_lookup_matches_the_real_spec` | In file callers reverse lookup matches the real spec. | `tests/test_gate_c5_runner.py:58` |
| `test_in_file_callers_refuses_unknown_function` | In file callers refuses unknown function. | `tests/test_gate_c5_runner.py:69` |
| `test_every_verified_mutant_is_isolated` | The hard constraint: anything that reaches real verification is verified in isolation - there is no whole-file path. | `tests/test_gate_c5_runner.py:74` |
| `test_filtered_mutants_never_reach_verification` | Statically filtered and vacuous-precondition mutants are tallied without a verify call and carry no isolation_status. | `tests/test_gate_c5_runner.py:97` |
| `test_precondition_refusal_is_recorded_and_does_not_abort_the_run` | A SystemExit from the Z3 precondition checker is an expected refusal (clause shapes it can't model, e.g. | `tests/test_gate_c5_runner.py:111` |
| `test_run_gate_c5_summary_shape_and_tally` | Run gate c5 summary shape and tally. | `tests/test_gate_c5_runner.py:148` |
| `test_body_function_mutates_a_distinct_companion_body` | The dosage method+companion shape: clauses come from the clause target (TopLevel), body AOR/LVR from a distinct companion (Companion). | `tests/test_gate_c5_runner.py:169` |
| `test_body_arithmetic_and_body_function_are_mutually_exclusive` | Body arithmetic and body function are mutually exclusive. | `tests/test_gate_c5_runner.py:194` |
| `test_survivor_escalation_retags_killed_and_inconclusive` | The DDI STP-escalation shape: a mutant that survives isolated verification is re-checked against a stronger oracle. | `tests/test_gate_c5_runner.py:201` |
| `test_run_gate_c5_reports_no_callers_for_a_leaf` | Run gate c5 reports no callers for a leaf. | `tests/test_gate_c5_runner.py:245` |

## Hazard ID Lint (`tests/test_hazard_id_lint.py`)

| Test | Description | Code |
|---|---|---|
| `test_real_repo_has_no_undefined_hazard_references` | The regression test. | `tests/test_hazard_id_lint.py:28` |
| `test_real_repo_defines_the_expected_hazard_ids_per_example` | Sanity check that the scanner actually finds real headings, not an accidentally-empty set that would make the regression test above vacuously pass. | `tests/test_hazard_id_lint.py:40` |
| `test_detects_an_undefined_reference` | Detects an undefined reference. | `tests/test_hazard_id_lint.py:54` |
| `test_does_not_flag_a_defined_id_referenced_elsewhere` | Does not flag a defined id referenced elsewhere. | `tests/test_hazard_id_lint.py:70` |
| `test_split_hazard_style_ids_are_parsed_correctly` | The exact shape of the bug this module exists to catch: a base ID (HAZ-X-2) and a lettered split-row ID (HAZ-X-2b) must be treated as distinct IDs, not merged or confused. | `tests/test_hazard_id_lint.py:82` |
| `test_intentionally_retired_ids_are_not_flagged` | Intentionally retired ids are not flagged. | `tests/test_hazard_id_lint.py:100` |
| `test_dotted_and_undotted_ids_both_parse` | Dotted and undotted ids both parse. | `tests/test_hazard_id_lint.py:114` |
| `test_untracked_markdown_is_not_scanned` | The exact case an external review (Qodo, PR #51) flagged: a workspace file that was never `git add`-ed - a local scratch note, or something a tool generated (this repo's own working tree already had pytest's cache READM… | `tests/test_hazard_id_lint.py:125` |
| `test_test_catalog_md_is_excluded_even_when_tracked` | Real false positive, found 2026-07-15 the first time TEST_CATALOG.md was generated: it quotes test docstrings verbatim, including tests/test_hazard_id_lint.py's own fixture examples ("HAZ-X-2", etc.) - fictional IDs use… | `tests/test_hazard_id_lint.py:142` |

## Mutation Report (`tests/test_mutation_report.py`)

| Test | Description | Code |
|---|---|---|
| `test_report_total_and_outcome_counts` | Report total and outcome counts. | `tests/test_mutation_report.py:21` |
| `test_no_survivors_and_no_unclassifiable_results_remain` | 2026-07-07: mutation testing originally found 2 real survivors (REQ-GIP-1-8-1's `>=` boundary, fixed by tightening to `>`) and 4 unclassifiable results (chain-direction parse errors, fixed by teaching the generator Dafn… | `tests/test_mutation_report.py:36` |
| `test_reverse_flow_clause_weakenings_are_filtered_not_survivors` | The two mutations that used to be real survivors before the REQ-GIP-1-8-1 tightening are now correctly recognized as statically trivial (a proof of `x > 0` universally implies both `x >= 0` and `x != 0`) before Dafny is… | `tests/test_mutation_report.py:52` |
| `test_chained_clause_direction_incompatible_mutants_are_filtered_pre_verification` | Built 2026-07-07 from external research: mutating one side of the chained `0.0 <= dose <= maxSafeDoseMgPerHr` to a descending operator (>=, >) is a genuine Dafny PARSE error (chained comparisons must stay direction-cons… | `tests/test_mutation_report.py:73` |
| `test_function_body_aor_mutants_present_and_division_free_candidate_filtered` | Built 2026-07-07 from external research: ExpectedDose's function body (part of the formal spec, referenced by the pinning ensures clause) now gets AOR mutation on its one `*` operator, restricted per MutDafny's own grou… | `tests/test_mutation_report.py:90` |
| `test_lvr_mutants_present_and_all_real_verified_candidates_killed` | Built 2026-07-07 from a scoped sub-plan (LVR extension): every numeric literal in the spec is exactly 0.0, mutated to +/-0.01. | `tests/test_mutation_report.py:108` |
| `test_no_mutant_touches_the_calculatehourlydose_method_implementation_body` | Mutation testing perturbs the SPEC, never CalculateHourlyDose's trusted implementation - every recorded mutant comes from a requires/ensures clause, an explicit COI negation of one, or ExpectedDose's function body (also… | `tests/test_mutation_report.py:126` |
| `test_every_verified_mutant_was_isolated` | Since 2026-07-20 this example runs through the sanctioned evidence/gate_c5_runner.py, so every mutant that reaches real Dafny verification is verified against CalculateHourlyDose in ISOLATION (the method plus its Expect… | `tests/test_mutation_report.py:137` |
| `test_run_manifest_records_real_dafny_version_and_matching_counts` | Run manifest records real dafny version and matching counts. | `tests/test_mutation_report.py:153` |

## Overflow Probe (`tests/test_overflow_probe.py`)

| Test | Description | Code |
|---|---|---|
| `test_double_it_overflows_to_inf_on_ieee_hardware` | Deterministic IEEE violation of overflow_probe.py's postcondition (post: math.isfinite(__return__)): 1e308 * 2.0 overflows to inf. | `tests/test_overflow_probe.py:6` |

## Packaging (`tests/test_packaging.py`)

| Test | Description | Code |
|---|---|---|
| `test_pyproject_is_valid_toml_with_expected_shape` | Pyproject is valid toml with expected shape. | `tests/test_packaging.py:60` |
| `test_runtime_dependencies_match_requirements_txt_pins` | Every runtime dep in pyproject.toml must match requirements.txt's pin exactly - not "compatible", not "close enough". | `tests/test_packaging.py:66` |
| `test_console_script_points_at_a_real_callable_main` | Console script points at a real callable main. | `tests/test_packaging.py:100` |
| `test_schema_json_files_are_declared_as_package_data` | Schema json files are declared as package data. | `tests/test_packaging.py:118` |

## Polish Lint (`tests/test_polish_lint.py`)

| Test | Description | Code |
|---|---|---|
| `test_system_reference_has_no_narrative_language` | System reference has no narrative language. | `tests/test_polish_lint.py:22` |
| `test_scanner_actually_detects_narrative_language` | Positive-control test: prove the scanner isn't vacuously passing by feeding it text it must flag. | `tests/test_polish_lint.py:33` |
| `test_last_updated_header_line_is_exempt_from_the_date_check` | The one legitimate date in the document -- its own header -- must not itself trip the dated-reference check. | `tests/test_polish_lint.py:47` |

## Proven Exclusivity (`tests/test_proven_exclusivity.py`)

| Test | Description | Code |
|---|---|---|
| `test_positive_real_dafny_proven_record_is_accepted` | A real, fully-checked Dafny PROVEN record — produced the same way Gate C1's adapter produces it, not hand-waved — passes R3. | `tests/test_proven_exclusivity.py:33` |
| `test_negative_crosshair_record_can_never_carry_proven` | Checked explicitly, not by omission: a crosshair-method record claiming PROVEN is refused even though it carries a completed status, and even though the fixture is otherwise well-formed. | `tests/test_proven_exclusivity.py:48` |
| `test_negative_concrete_test_record_can_never_carry_proven` | Same property, other permanently-excluded method. | `tests/test_proven_exclusivity.py:61` |
| `test_negative_missing_method_can_never_carry_proven` | A record with no method at all (e.g. | `tests/test_proven_exclusivity.py:72` |
| `test_negative_dafny_method_without_completed_status_is_still_refused` | Defense in depth: even a record naming method="dafny" is refused if it doesn't also carry a completed verifier_completion_status - R3 does not trust the method label alone. | `tests/test_proven_exclusivity.py:80` |
| `test_negative_dafny_method_with_incomplete_status_is_still_refused` | Negative dafny method with incomplete status is still refused. | `tests/test_proven_exclusivity.py:90` |
| `test_row_level_strength_cell_honors_the_same_rule` | Variant B/C rows carry strength/method directly on the row, not inside an evidence list - the same R3 gate must cover that shape too. | `tests/test_proven_exclusivity.py:96` |
| `test_committed_matrix_artifacts_still_pass_unchanged` | R3 must not regress the existing, fully-CrossHair/concrete-sourced committed artifacts - none of them contain a dafny record today, so they must pass exactly as they did under R2. | `tests/test_proven_exclusivity.py:113` |

## Readme Evidence Totals (`tests/test_readme_evidence_totals.py`)

| Test | Description | Code |
|---|---|---|
| `test_readme_total_requirement_count_matches_committed_matrices` | Readme total requirement count matches committed matrices. | `tests/test_readme_evidence_totals.py:56` |
| `test_readme_evidence_strength_table_matches_committed_matrices` | Readme evidence strength table matches committed matrices. | `tests/test_readme_evidence_totals.py:73` |
| `test_no_realized_strength_is_silently_missing_from_the_readme_table` | Every strength this repo's four matrices actually produce must appear as its own row - not folded into another number unnoticed. | `tests/test_readme_evidence_totals.py:96` |

## Renal Adjustment Matrix (`tests/test_renal_adjustment_matrix.py`)

| Test | Description | Code |
|---|---|---|
| `test_cli_omitting_manifest_and_concrete_entirely_still_works` | Cli omitting manifest and concrete entirely still works. | `tests/test_renal_adjustment_matrix.py:48` |
| `test_cli_writes_markdown_matching_committed` | Cli writes markdown matching committed. | `tests/test_renal_adjustment_matrix.py:63` |
| `test_single_function_requirements_bind_correctly` | Single function requirements bind correctly. | `tests/test_renal_adjustment_matrix.py:88` |
| `test_dual_cited_assess_renal_function_backs_both_req_1_and_req_2` | AssessRenalFunction is tagged REQ-RENAL-1, REQ-RENAL-2 inline in the real .dfy file - its evidence must appear in BOTH rows, not just one, mirroring that dual citation exactly. | `tests/test_renal_adjustment_matrix.py:104` |
| `test_req_renal_1_covers_gstage_and_assess_renal_function` | Req renal 1 covers gstage and assess renal function. | `tests/test_renal_adjustment_matrix.py:119` |
| `test_req_renal_2_covers_formula_selection_and_crcl_computation` | The unnumbered CrCl-computation functions (CockcroftGaultCrClMlPerMin, AssessRenalFunctionFromInputs - neither carries its own REQ-ID citation in the .dfy file) are attached here rather than given a new requirement ID,… | `tests/test_renal_adjustment_matrix.py:129` |
| `test_prose_only_requirements_render_as_honest_gaps_intending_proven` | REQ-RENAL-3/4/6/7 are real future Dafny-formalization candidates, not yet built - intended_method PROVEN, so the gap note reads "intended PROVEN, realized GAP", correctly signaling unmet ambition rather than something n… | `tests/test_renal_adjustment_matrix.py:145` |
| `test_req_renal_8_is_a_declared_gap_parked_for_process_data_not_a_proof_target` | REQ-RENAL-8 (classification-flag provenance): its trust boundary is permanent and will never be a Dafny proof target - genuinely different from REQ-RENAL-3/4/6/7's "not yet formalized" gaps, since nobody ever intends to… | `tests/test_renal_adjustment_matrix.py:158` |
| `test_committed_matrix_passes_the_structural_proven_check` | Committed matrix passes the structural proven check. | `tests/test_renal_adjustment_matrix.py:175` |

## Renal Adjustment Spec Lint (`tests/test_renal_adjustment_spec_lint.py`)

| Test | Description | Code |
|---|---|---|
| `test_every_function_precondition_is_satisfiable` | None of the seven functions' requires clauses are vacuous - a Dafny 'clean pass' on renal_adjustment.dfy proves what it appears to prove, not something trivially true because no input could ever satisfy the precondition. | `tests/test_renal_adjustment_spec_lint.py:42` |
| `test_assess_renal_function_no_longer_refused_for_its_unused_formula_param` | Named regression for the real gap this file's module docstring describes: AssessRenalFunction's Formula-typed parameter is never referenced by its requires clause, so the check must not refuse on it. | `tests/test_renal_adjustment_spec_lint.py:52` |
| `test_weak_postcondition_warning_counts_match_the_real_spec` | Unlike dosage.dfy (which avoids one-way ==> entirely), five of the seven renal functions genuinely use ==> in their ensures clauses - this is expected here, not a regression: GStage/SelectFormula/AssessRenalFunction dis… | `tests/test_renal_adjustment_spec_lint.py:62` |
| `test_composed_ceiling_and_round_half_up_have_no_weak_postconditions` | The two functions whose ensures clauses use <=/== rather than ==> (ComposedCeiling's bounds, RoundHalfUp's interval) should stay clean - a true-negative check mirroring dosage.dfy's own pattern. | `tests/test_renal_adjustment_spec_lint.py:86` |

## Renal Mutation Report (`tests/test_renal_mutation_report.py`)

| Test | Description | Code |
|---|---|---|
| `test_report_total_and_outcome_counts` | Report total and outcome counts. | `tests/test_renal_mutation_report.py:36` |
| `test_verified_mutants_are_recorded_as_isolated` | Every mutant that reached real Dafny verification (i.e. | `tests/test_renal_mutation_report.py:56` |
| `test_survivors_are_all_antecedent_narrowing_on_a_one_way_implication` | Category 1 (33 of 53 survivors): ROR/LVR mutations that NARROW the antecedent of a one-way `==>` ensures clause (e.g. | `tests/test_renal_mutation_report.py:68` |
| `test_survivors_are_all_requires_clause_weakenings_not_load_bearing` | Category 2 (17 of 53 survivors): ROR/LVR mutations to a `requires` clause that Dafny's real verifier can still satisfy under the weakened precondition, because the specific `ensures` clauses proven for that function don… | `tests/test_renal_mutation_report.py:90` |
| `test_round_half_up_aor_survivor_is_the_one_named_exception` | Category 3 (1 of 53 survivors): RoundHalfUp's self-referential ensures clause (`(RoundHalfUp(x) as real) - 0.5 <= x < ...`) survives a `-` -> `*` mutation for a coincidental numeric reason (the mutated lower bound is lo… | `tests/test_renal_mutation_report.py:118` |
| `test_round_half_up_ensures_lvr_widening_survivors_are_the_named_pair` | Category 4 (2 of 53 survivors): now that the LVR generator covers RoundHalfUp's arithmetic-embedded ensures literal (fix 4a), widening the rounding tolerance `0.5 -> 0.51` in `(RoundHalfUp(x) as real) - 0.5 <= x < (Roun… | `tests/test_renal_mutation_report.py:133` |
| `test_all_53_survivors_accounted_for_by_the_four_named_categories` | No survivor should exist outside the four categories above - a future spec change producing a genuinely new, unexplained survivor must fail this test, not blend into an unexamined total. | `tests/test_renal_mutation_report.py:152` |
| `test_unclassifiable_results_are_all_the_named_lor_ambiguity_gap` | Real, named engine limitation (2026-07-09), not fixed: SelectFormula's ensures clause antecedent is a flat, unparenthesized run of six `\|\|` terms; mutating any one `\|\|` to `&&` produces Dafny's own genuine 'Ambiguous us… | `tests/test_renal_mutation_report.py:171` |
| `test_no_mutant_touches_a_function_body_other_than_the_two_named` | AOR/LVR body mutation is scoped to exactly RoundHalfUp and CockcroftGaultCrClMlPerMin - the only two functions with arithmetic operators or numeric literals in their own bodies (see run_mutation_suite_renal.py's module… | `tests/test_renal_mutation_report.py:186` |
| `test_run_manifest_records_real_dafny_version_and_matching_counts` | Run manifest records real dafny version and matching counts. | `tests/test_renal_mutation_report.py:198` |

## Single Evidence Type (`tests/test_single_evidence_type.py`)

| Test | Description | Code |
|---|---|---|
| `test_symbolic_only_fixture_validates_against_schema_c` | Symbolic only fixture validates against schema c. | `tests/test_single_evidence_type.py:84` |
| `test_concrete_only_fixture_validates_against_schema_c` | Concrete only fixture validates against schema c. | `tests/test_single_evidence_type.py:91` |
| `test_symbolic_only_requirement_appears_in_exactly_one_artifact` | Symbolic only requirement appears in exactly one artifact. | `tests/test_single_evidence_type.py:98` |
| `test_concrete_only_requirement_appears_in_exactly_one_artifact` | The Gate 5 fix itself: a requirement declaring only concrete_test evidence gets no symbolic record, so it must NOT appear in the symbolic artifact at all - previously impossible (every requirement got an unconditional s… | `tests/test_single_evidence_type.py:119` |

## Spec Impl Gap (`tests/test_spec_impl_gap.py`)

| Test | Description | Code |
|---|---|---|
| `test_definitional_predicate_is_definitional_and_z3_confirms` | Definitional predicate is definitional and z3 confirms. | `tests/test_spec_impl_gap.py:62` |
| `test_mixed_method_has_both_a_definitional_pin_and_a_property_bound` | Mixed method has both a definitional pin and a property bound. | `tests/test_spec_impl_gap.py:70` |
| `test_guarded_match_function_is_definitional_with_guards_recorded` | Guarded match function is definitional with guards recorded. | `tests/test_spec_impl_gap.py:83` |
| `test_unknown_declaration_is_refused` | Unknown declaration is refused. | `tests/test_spec_impl_gap.py:92` |
| `test_aeb_kernel_every_function_is_definitional` | Every aeb_kernel function restates its own body (ensures F <==> E, body E) - the motivating definitional case. | `tests/test_spec_impl_gap.py:103` |
| `test_dosage_calculate_hourly_dose_is_property_with_a_definitional_pin` | dosage's CalculateHourlyDose pins dose == ExpectedDose(...) (definitional) but also bounds 0.0 <= dose <= max and infusionRate > 0 \|\| dose == 0 (property) - so the row carries real content. | `tests/test_spec_impl_gap.py:117` |
| `test_renal_carries_both_property_and_definitional_functions` | renal_adjustment mixes real-arithmetic property functions (RoundHalfUp's rounding bound and >= 0 floor, ComposedCeiling's > 0.0) with definitional category-lookup functions (GStage) - the classifier separates them. | `tests/test_spec_impl_gap.py:136` |
| `test_ddi_check_interaction_is_definitional` | drug_interaction_checker's CheckInteraction is a per-case lookup: every ensures pins the result to an InteractionResult(...) constructor under a guard. | `tests/test_spec_impl_gap.py:148` |
| `test_structure_and_z3_never_disagree_on_the_committed_specs` | The load-bearing correctness invariant: wherever the Z3 pin-uniqueness cross-check can run, it agrees with the structural verdict. | `tests/test_spec_impl_gap.py:159` |

## Structural Proven Check (`tests/test_structural_proven_check.py`)

| Test | Description | Code |
|---|---|---|
| `test_committed_variant_artifacts_pass_structural_check` | Committed variant artifacts pass structural check. | `tests/test_structural_proven_check.py:28` |
| `test_corrupted_in_memory_record_fails_structural_check` | Corrupted in memory record fails structural check. | `tests/test_structural_proven_check.py:33` |
| `test_corrupted_in_memory_row_cell_fails_structural_check` | Corrupted in memory row cell fails structural check. | `tests/test_structural_proven_check.py:41` |

## Test Catalog (`tests/test_test_catalog.py`)

| Test | Description | Code |
|---|---|---|
| `test_committed_catalog_matches_the_generator` | Committed catalog matches the generator. | `tests/test_test_catalog.py:24` |
| `test_nested_test_files_are_included` | Real bug, found by an external review (Qodo) on PR #54: a literal "tests/" prefix in the tracked_files() pathspec ("tests/test_*.py") only matches tests/'s direct children in real `git ls-files` semantics, confirmed emp… | `tests/test_test_catalog.py:34` |
| `test_every_real_test_file_produces_a_nonempty_category` | Sanity check that the parser actually finds tests, not an accidentally-empty result that would make the regression test above vacuously pass. | `tests/test_test_catalog.py:58` |
| `test_category_heading_title_cases_and_expands_acronyms` | Category heading title cases and expands acronyms. | `tests/test_test_catalog.py:67` |
| `test_parses_a_docstring_first_sentence_as_the_description` | Parses a docstring first sentence as the description. | `tests/test_test_catalog.py:75` |
| `test_derives_a_description_from_the_name_when_no_docstring` | Derives a description from the name when no docstring. | `tests/test_test_catalog.py:98` |
| `test_non_test_functions_are_excluded` | Non test functions are excluded. | `tests/test_test_catalog.py:110` |
| `test_a_file_with_no_test_functions_produces_no_category` | A file with no test functions produces no category. | `tests/test_test_catalog.py:130` |
| `test_rendered_markdown_escapes_pipe_characters_in_descriptions` | Rendered markdown escapes pipe characters in descriptions. | `tests/test_test_catalog.py:136` |

## Tracked Files (`tests/test_tracked_files.py`)

| Test | Description | Code |
|---|---|---|
| `test_returns_only_staged_files_matching_pattern` | Returns only staged files matching pattern. | `tests/test_tracked_files.py:29` |
| `test_untracked_file_is_not_returned` | The exact case Qodo's review asked for: an untracked .md file present on disk (e.g. | `tests/test_tracked_files.py:40` |
| `test_matches_nested_paths` | Matches nested paths. | `tests/test_tracked_files.py:55` |
| `test_no_matches_returns_empty_list` | No matches returns empty list. | `tests/test_tracked_files.py:67` |
| `test_raises_clear_error_when_not_a_git_repository` | Deliberately refuses to fall back to a filesystem walk on git failure - that fallback would silently reintroduce the exact untracked-file problem this module exists to avoid. | `tests/test_tracked_files.py:75` |
