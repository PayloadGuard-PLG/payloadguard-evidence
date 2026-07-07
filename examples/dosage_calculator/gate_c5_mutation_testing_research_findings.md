# Research findings: Gate C5 mutation testing (2026-07-07)

External research response to `gate-c5-research-prompt.md` (sent to
Steven for exploration outside this repo, results brought back and
recorded here). Full text of the response is preserved in git history
of the conversation this document was extracted from; this file records
what was established, what corrections it produced, and what remains an
open, scoped follow-up.

## Correction made as a direct result of this research

**Gate C5 is MutDafny-style, not "MutDafny/IronSpec-style."** This
repo's own code and docs previously described the mutation-testing
harness as "MutDafny/IronSpec-style" in several places. The research
found this conflation is wrong: IronSpec's actual mutation-testing
technique (Goldweber et al., OSDI'24) generates mutants that are
strictly *stronger* than the original spec and checks a formal
weakness-implication lemma (`S is at least as weak as S′ iff
∀p. S′(p) ⟹ S(p)`) to see whether the original spec could have been
tightened without breaking the implementation — a directional,
implication-lemma-based approach. Gate C5's harness instead perturbs
operators in ways that aren't uniformly stronger or weaker (e.g. `!=` is
neither a superset nor subset of `>=`) and checks brute Dafny
verification pass/fail, which is what MutDafny (Amaral, Mendes & Campos,
2025) does, not IronSpec. Gate C4's own "IronSpec methodology" label is
correct and unaffected — Spec-Testing Proofs (proving specific
input/output pairs accepted/rejected by the spec alone) are a real,
separate part of IronSpec's toolkit, distinct from its mutation-testing
feature. Only Gate C5's own MutDafny/IronSpec label was wrong; corrected
in `evidence/dafny_mutate.py`'s module docstring and this repo's docs.

The roadmap's original scoping text also attributed the three-pass
filter pipeline (discard statically-weaker mutants, discard
vacuity-inducing mutants, re-verify survivors) to "IronSpec's three-pass
framework." This research did not confirm that attribution and its
account of IronSpec's actual mutation technique doesn't match a
three-pass filter pipeline at all — so that credit is unconfirmed and
should not be repeated as fact. The three-pass structure stands on its
own merits regardless of provenance.

## Problem A — the `>=` → `!=`/`>` survivor: name and precedent found

No term exists in the mutation-testing literature for this exact
pattern ("a boundary survives mutation because a sibling disjunct
coincidentally covers it") — MutDafny's own paper names this class of
problem as unsolved future work (55% of their 284 manually-triaged
surviving mutants were equivalent mutants classified by hand). But two
established, precise, applicable frames were found:

- **Equivalent mutant, relative to the trusted implementation** (Budd &
  Angluin, 1982; still the cited origin point in current surveys,
  Kushigian et al. 2024) — not equivalent to the spec in the abstract,
  but for every input the real implementation can produce.
- **Masking, in the MC/DC sense** (DO-178B/C, Chilenski 1994, DO-248C):
  "a condition is masked if changing its value while keeping the other
  inputs fixed does not change the decision." This is a named,
  FAA/DO-178C-*accepted* pattern in exactly the adjacent safety-critical
  aerospace field. `infusionRateMlPerHr >= 0.0 || dose == 0.0` at
  `infusionRateMlPerHr == 0.0` is a textbook masking instance: the
  second disjunct is already true there, masking the first disjunct's
  operator choice.

Steven's decision (recorded in `nl_confirmation_dosage_dfy.md`'s
amendment) was to tighten `>=` to `>` rather than document the masking
as accepted looseness — resolving the finding directly rather than
choosing between the two options this research laid out (document as
masking, vs. restructure as a single `==>` implication to make every
operator load-bearing). The masking/equivalent-mutant terminology is
recorded here for the historical record and for anyone auditing why the
original `>=` survived mutation testing before the fix.

**Not built:** a second-stage formal `S′(p) ⟹ S(p)` implication-lemma
check (IronSpec's actual technique) on any future Problem-A-style
survivor, which the research suggests as a strictly stronger evidence
artifact than observing verification didn't distinguish two clauses.
Not needed for the current fix (tightening resolved it directly) but
worth keeping in mind if a future survivor is judged acceptable-as-is
rather than fixed.

## Problem B — chained-comparison stillborn mutants: confirmed as expected, then closed

- Dafny's chaining rule is now citable from a primary source: Dafny
  Reference Manual §5.2.1–5.2.2 and the official Errors/FAQ page
  ("cannot have chains that include both less-than operations... and
  greater-than operations") — confirms the empirical finding from the
  mutation suite's real run exactly, including that `==`/`!=` mix freely
  into either direction.
- The general term for what the 4 unclassifiable mutants are is
  **stillborn mutant** (syntactically illegal, never reaches semantic
  evaluation) — standard mutation-testing taxonomy.
- **MutDafny itself does not generate only well-formed mutants by
  construction either** — its pipeline has an explicit *Invalid* outcome
  bucket for exactly this case (mutant fails Dafny's resolution) and
  excludes Invalid mutants from its mutation-score denominator. Gate
  C5's `unclassifiable` bucket is independently the same strategy the
  most recent published Dafny mutation tool uses — not a gap relative to
  the state of the art.

**Built (2026-07-07), genuinely ahead of published tooling:** each
chain link's mutation candidates are now restricted to
direction-compatible operators only (for an ascending chain:
`{<, <=, ==, !=}`, never `>`/`>=`) — `evidence/dafny_mutate.py`'s
`_chain_group_ids`/`_chain_incompatible`, wired into
`_generate_token_mutants`'s `chain_aware` path (used by
`generate_ror_mutants` only). Eliminates the 4 stillborn mutants by
construction: they're now `filtered_chain_incompatible` before any
Dafny invocation, not generated-then-refused. Re-run against the real
spec: the `unclassifiable` outcome bucket is now empty entirely.
MutDafny itself does not do this - this is a genuine improvement over
the published state of the art, not parity with it.

## Problem C — bounding real-valued mutation precision: no established term, but a concrete technique and a concrete number

- "Epsilon mutation testing" / "tolerance-aware mutation testing" is not
  established terminology — a genuine literature gap, not a missed
  search.
- **MutDafny's actual AOR restriction is the direct answer to the
  division-by-zero risk named in the original Gate C5 scoping session:**
  it does not allow free replacement into `/`/`%` from `+`/`-`/`*` — only
  `/ ↔ %` are ever mutually substitutable. Applying the same restriction
  here would mean a mutation never *introduces* division where the
  original spec had none, so Dafny's division-by-zero safety check can
  never be triggered by a mutation that wasn't already division-shaped.
  This directly resolves the attribution risk named when AOR was
  originally deferred.
- **Concrete clinical precision cutoff, sourced from pharmacy/nursing
  calculation practice (not a formal regulatory standard — the research
  is explicit about that distinction):** volumetric infusion-pump rates
  are conventionally rounded to 1 decimal place (tenths of mL/hr),
  syringe pumps to 2 decimal places (hundredths); general doctrine is to
  round to the delivery device's actual precision, not the arithmetic's.
  This gives a defensible, sourced cutoff (≥ 0.01 mL/hr) for "no
  clinically meaningful mutant differs from the original by less than
  this," should real-valued/AOR mutation testing be built later.

**Built (2026-07-07):** AOR mutation now extends to `ExpectedDose`'s
function body - `generate_aor_mutants`'s optional `function_name`
parameter, `_locate_function_body_arithmetic_sites`,
`_generate_function_body_aor_mutants`. MutDafny's `/`↔`%` group
restriction is applied directly (`_ar_group_incompatible`): the one `*`
operator's candidates are `+`/`-` (both real-verified, both genuinely
killed - confirming `*` is load-bearing) and `/` (filtered before
verification, never risking a division-by-zero false-kill). **Not
built at the time:** the ≥0.01 mL/hr clinical-precision floor had no
application yet - it bounds literal-value-replacement (LVR) mutants
specifically (a *magnitude* concept), and Gate C5's scope was always
ROR/LOR/AOR/SOR/HOR/COI, never LVR. Named rather than forced onto AOR,
which mutates operators, not literal magnitudes.

**LVR built (2026-07-07), same day, via its own scoped sub-plan**
(`payloadguard-evidence-roadmap-phaseB-to-C.md`'s "Gate C5 LVR
extension" section): the ≥0.01 mL/hr floor found its actual application.
All 7 numeric literals in this spec are exactly `0.0`; each mutated to
`± 0.01`. `_lvr_trivial` generalizes ROR's requires/ensures polarity
principle to literal magnitude. Real run matched a fully hand-derived
prediction exactly: 14 mutants, 4 filtered, 10 real-verified, all 10
genuinely killed - zero survivors. The clinical-floor-vs-exact-zero-
safety-requirement tension named in the LVR scoping session (whether
±0.01 is the right test for REQ-GIP-1-8-1 specifically, vs. a threshold
requirement like the max-dose ceiling) didn't need resolving to get a
clean result here, but is still an open judgment call, not decided by
this outcome.

## Full response and sources

The complete research response, with full citations (Amaral/Mendes/
Campos 2025 on MutDafny; Goldweber et al. 2024 on IronSpec; Budd &
Angluin 1982; Kaminski/Ammann/Offutt 2011/2013; Kushigian et al. 2024;
Dafny Reference Manual; DO-178C/MC/DC masking sources; pharmacy
calculation references), is preserved in the session transcript this
repository's work was produced in. This document summarizes it for
in-repo reference; it is not itself the primary source.
