// Dafny spec for renal-function dose adjustment — Gate C1 (Phase 2),
// PayloadGuard-Evidence's second, independent proof-of-concept.
//
// SCOPE, NAMED EXPLICITLY (per PHASE1_PLAN.md's "Closed under named
// fallback assumptions" section): this spec covers REQ-RENAL-1,
// REQ-RENAL-1a, REQ-RENAL-2, and REQ-RENAL-5 — GFR staging with KDIGO's
// rounding convention, formula selection between eGFR and Cockcroft-Gault
// CrCl, the type-level guarantee that a CrCl value can never be run
// through eGFR staging, and bound composition against dosage.dfy's
// existing ceiling. REQ-RENAL-3, REQ-RENAL-4, REQ-RENAL-6, and
// REQ-RENAL-7 are not yet formalized as Dafny signatures (see
// GATE_1C_AUDIT.md's REQ-by-REQ trace) — they exist only as prose in
// Gate 1a/1b so far.
//
// Gate 1c Finding 1 (GATE_1C_AUDIT.md) — closed 2026-07-09 for
// Cockcroft-Gault only, per Steven's scope decision: CKD-EPI eGFR stays
// caller-supplied because Dafny/Z3 cannot express its real-valued
// fractional exponents on a variable base — a toolchain expressiveness
// gap CONFIRMED EMPIRICALLY (2026-07-10, prompted by direct challenge
// on whether the closing claim was actually earned), not just asserted
// from general Z3-theory knowledge: `dafny_pow_expressiveness_probe.dfy`
// shows Dafny has no real-exponentiation primitive at all
// ("unresolved identifier: Pow"); `dafny_pow_axiom_trap_probe.dfy` shows
// the obvious workaround (declaring Pow as an unproven axiom) verifies
// trivially even for an absurd, wrong claim about it — a DECLARED
// assumption wearing PROVEN's clothing, exactly what Gate C2 exists to
// refuse. So the eGFR side of the decision follows from what the
// toolchain can actually prove, not a judgment call. Cockcroft-Gault
// CrCl, by contrast, is small linear arithmetic and is now computed and
// proven below (`CockcroftGaultCrClMlPerMin`, `AssessRenalFunctionFromInputs`).
//
// Every function body below was first checked in a scratch file against
// this same installed Dafny 4.11.0 toolchain during Gate 1c's audit and
// its addendum (2026-07-08), and again for the Cockcroft-Gault
// computation (2026-07-09), before being committed here verbatim — no
// body changed between the scratch check and this file.

datatype GStageCategory = G1 | G2 | G3a | G3b | G4 | G5
datatype Formula = EGFRFormula | CockcroftGaultFormula
datatype RenalAssessment =
  | EGFRAssessment(stage: GStageCategory)
  | CrClAssessment(roundedCrClMlPerMin: int)

// REQ-RENAL-1a: KDIGO reports eGFR rounded to the nearest whole number
// before staging (sources/kdigo-2024-gfr-staging.md, Table 11) — this
// shifts the effective continuous G-stage boundaries to 89.5/59.5/44.5/
// 29.5/14.5, not the naive 90.0/60.0/45.0/30.0/15.0. The base rounding
// requirement is KDIGO-sourced; the round-half-up TIE-BREAK specifically
// (89.5 -> 90, not 89) is a named, uncited design decision, NOT a KDIGO
// rule - KDIGO states no tie-breaking method, and the NKF Laboratory
// Engagement Working Group's implementation guidance (Miller et al.,
// Clin Chem 2022;68(4):511-520, PMID 34918062) explicitly defers this to
// "the rounding logic of a laboratory information system." See
// sources/kdigo-2024-gfr-staging.md's 2026-07-09 amendment.
function RoundHalfUp(x: real): int
  requires x >= 0.0
  ensures (RoundHalfUp(x) as real) - 0.5 <= x < (RoundHalfUp(x) as real) + 0.5 // REQ-RENAL-1a
  ensures RoundHalfUp(x) >= 0 // REQ-RENAL-1a-EXT, Gate C5 (isolated re-verification,
  // 2026-07-19): makes `requires x >= 0.0` load-bearing. Without this, three
  // qualitative weakenings of the precondition (<= 0.0, != 0.0, < 0.0) survive
  // mutation in isolation - RoundHalfUp's own body satisfies its rounding
  // ensures for negative x too, so nothing here depended on x >= 0.0 until this
  // positivity guarantee was stated. The whole-file run had wrongly scored those
  // three KILLED; the kill was AssessRenalFunction (a caller) failing to
  // discharge the mutated precondition, not RoundHalfUp itself. Does NOT close
  // the LVR-scale survivor (x >= -0.01): RoundHalfUp(x) for x in [-0.01, 0) is
  // still 0, so >= 0 holds; the positivity break only occurs once x < -0.5.
  // That survivor is a sound consequence, correctly left open, not a spec gap.
{
  (x + 0.5).Floor
}

// REQ-RENAL-1: KDIGO's six GFR categories (sources/kdigo-2024-gfr-staging.md,
// p. S126). Takes an already-rounded integer — composes with
// RoundHalfUp's output rather than re-deriving the boundary shift itself,
// so the STP suite can prove GStage(RoundHalfUp(x)) pins every boundary
// correctly without GStage needing to know about rounding.
function GStage(roundedEgfr: int): GStageCategory
  requires roundedEgfr >= 0
  ensures roundedEgfr >= 90 ==> GStage(roundedEgfr) == G1 // REQ-RENAL-1
  ensures 60 <= roundedEgfr <= 89 ==> GStage(roundedEgfr) == G2 // REQ-RENAL-1
  ensures 45 <= roundedEgfr <= 59 ==> GStage(roundedEgfr) == G3a // REQ-RENAL-1
  ensures 30 <= roundedEgfr <= 44 ==> GStage(roundedEgfr) == G3b // REQ-RENAL-1
  ensures 15 <= roundedEgfr <= 29 ==> GStage(roundedEgfr) == G4 // REQ-RENAL-1
  ensures roundedEgfr < 15 ==> GStage(roundedEgfr) == G5 // REQ-RENAL-1
{
  if roundedEgfr >= 90 then G1
  else if roundedEgfr >= 60 then G2
  else if roundedEgfr >= 45 then G3a
  else if roundedEgfr >= 30 then G3b
  else if roundedEgfr >= 15 then G4
  else G5
}

// REQ-RENAL-2: MHRA Drug Safety Update vol. 13, issue 3 (Oct 2019),
// verified directly (sources/mhra-renal-formula-selection-2019.md).
// Cockcroft-Gault CrCl is required instead of eGFR whenever any of the
// five named conditions holds; BMI thresholds are strict inequality
// (<18.0 / >40.0 — exactly 18.0 or 40.0 is not itself "extreme"),
// confirmed against MHRA's verbatim wording, not assumed.
function SelectFormula(
  isDirectActingOralAnticoagulant: bool,
  isOnNephrotoxicDrug: bool,
  ageYears: int,
  bmi: real,
  isNarrowTherapeuticIndexDrug: bool
): Formula
  requires ageYears >= 0
  requires bmi > 0.0
  ensures (isDirectActingOralAnticoagulant || isOnNephrotoxicDrug || ageYears >= 75 || bmi < 18.0 || bmi > 40.0 || isNarrowTherapeuticIndexDrug) ==> SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug) == CockcroftGaultFormula // REQ-RENAL-2
  ensures !(isDirectActingOralAnticoagulant || isOnNephrotoxicDrug || ageYears >= 75 || bmi < 18.0 || bmi > 40.0 || isNarrowTherapeuticIndexDrug) ==> SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug) == EGFRFormula // REQ-RENAL-2
{
  if isDirectActingOralAnticoagulant || isOnNephrotoxicDrug || ageYears >= 75
     || bmi < 18.0 || bmi > 40.0 || isNarrowTherapeuticIndexDrug
  then CockcroftGaultFormula
  else EGFRFormula
}

// REQ-RENAL-5: dosage.dfy's CalculateHourlyDose takes a single
// maxSafeDoseMgPerHr: real parameter — no pair of bounds inside it to
// intersect, checked directly against the literal file at
// examples/dosage_calculator/dosage.dfy, not described from memory.
// "The more conservative bound wins" is therefore a composition step
// upstream of it, named here as its own proven function.
//
// Gate C4 finding and fix (2026-07-09): the original two `<=` ensures
// clauses below verified cleanly but never pinned the result to
// min(existingCeiling, renalCeiling) — a function that always returned
// 0.0 would have satisfied them just as well as the real "smaller of
// the two" implementation (confirmed mechanically, not by inspection:
// an STP trying to prove a wrong candidate value impossible FAILED to
// verify against the original spec — see
// renal_adjustment_stp_suite_against_underconstrained.dfy). The third
// ensures clause below is the fix: combined with the two `<=` bounds,
// forcing the result to equal one of the two inputs exactly pins it to
// their minimum (if it equals existingCeiling, the second bound forces
// existingCeiling <= renalCeiling, so existingCeiling IS the minimum,
// and symmetrically for the other disjunct). The original is preserved
// verbatim as renal_adjustment_underconstrained.dfy; the STP suites
// proving both directions are renal_adjustment_stp_suite.dfy (passes
// against this fixed spec) and
// renal_adjustment_stp_suite_against_underconstrained.dfy (fails
// against the preserved original).
function ComposedCeiling(existingCeiling: real, renalCeiling: real): real
  requires existingCeiling > 0.0
  requires renalCeiling > 0.0
  ensures ComposedCeiling(existingCeiling, renalCeiling) <= existingCeiling // REQ-RENAL-5
  ensures ComposedCeiling(existingCeiling, renalCeiling) <= renalCeiling // REQ-RENAL-5
  ensures ComposedCeiling(existingCeiling, renalCeiling) == existingCeiling || ComposedCeiling(existingCeiling, renalCeiling) == renalCeiling // REQ-RENAL-5, Gate C4 pinning fix
  ensures ComposedCeiling(existingCeiling, renalCeiling) > 0.0 // REQ-RENAL-5-EXT, Gate C5 (2026-07-19):
  // makes the two `requires > 0.0` clauses load-bearing. Without this, every
  // mutation of those preconditions survived (the min-of-two body verifies its
  // other ensures regardless of input positivity). ComposedCeiling has no
  // in-file callers, so this was an honest isolated survivor, not a confounded
  // one - positivity is preserved through composition, so stating it is real
  // added content, not a decorative guard.
{
  if renalCeiling < existingCeiling then renalCeiling else existingCeiling
}

// Gate 1c Finding 2 (GATE_1C_AUDIT.md), resolved by redesign: GStage's
// KDIGO-derived boundaries are eGFR-specific and must never be applied
// to a Cockcroft-Gault CrCl value (CrCl isn't BSA-normalized and isn't
// clinically staged via G1-G5). AssessRenalFunction is the ONLY entry
// point that may call GStage, and its tagged-union return type makes
// the category error a type-level impossibility rather than a calling
// convention a future caller has to remember correctly.
//
// Deliberately still takes renalFunctionValue: real as an already-
// computed input (Gate 1c Finding 1, closed under a named fallback
// assumption — see this file's header and PHASE1_PLAN.md): this
// function dispatches, rounds, and stages; it does not compute
// Cockcroft-Gault CrCl or CKD-EPI eGFR from raw patient data.
//
// Gate C4 finding and fix (2026-07-09): the original two ensures
// clauses below pinned only which RenalAssessment CONSTRUCTOR the
// result uses (Gate 1c Finding 2's actual target, and they still do
// that correctly), never the VALUE inside it — a function that always
// returned EGFRAssessment(G1) on the eGFR path would have satisfied
// them just as well as the real staging logic (confirmed mechanically:
// an STP trying to prove a wrong stage/CrCl value impossible FAILED to
// verify against the original spec — see
// renal_adjustment_stp_suite_against_underconstrained.dfy). The two
// pinning clauses below are the fix, mirroring ExpectedDose's role in
// dosage.dfy exactly: each ensures the result equals the function's own
// composition, not just its shape. The original is preserved verbatim
// as renal_adjustment_underconstrained.dfy.
function AssessRenalFunction(formula: Formula, renalFunctionValue: real): RenalAssessment
  requires renalFunctionValue >= 0.0
  ensures formula == EGFRFormula ==> AssessRenalFunction(formula, renalFunctionValue).EGFRAssessment? // REQ-RENAL-1, REQ-RENAL-2
  ensures formula == CockcroftGaultFormula ==> AssessRenalFunction(formula, renalFunctionValue).CrClAssessment? // REQ-RENAL-1, REQ-RENAL-2
  ensures formula == EGFRFormula ==> AssessRenalFunction(formula, renalFunctionValue) == EGFRAssessment(GStage(RoundHalfUp(renalFunctionValue))) // REQ-RENAL-1, REQ-RENAL-2, Gate C4 pinning fix
  ensures formula == CockcroftGaultFormula ==> AssessRenalFunction(formula, renalFunctionValue) == CrClAssessment(RoundHalfUp(renalFunctionValue)) // REQ-RENAL-1, REQ-RENAL-2, Gate C4 pinning fix
{
  if formula == EGFRFormula then
    EGFRAssessment(GStage(RoundHalfUp(renalFunctionValue)))
  else
    CrClAssessment(RoundHalfUp(renalFunctionValue))
}

// Gate 1c Finding 1, closed for Cockcroft-Gault (2026-07-09). Formula:
// Cockcroft DW, Gault MH. "Prediction of creatinine clearance from serum
// creatinine." Nephron. 1976;16(1):31-41. PMID 1244564, independently
// verified in sources/ckd-epi-2021-and-cockcroft-gault-verification.md:
//   CrCl (men)   = (140 - age) * weight(kg) / (72 * Scr[mg/dL])
//   CrCl (women) = above * 0.85
// Scr is supplied here in µmol/L (the UK's standard reporting unit,
// matching AssessRenalFunction's other caller-supplied inputs), so the
// mg/dL-based formula above is converted using the standard clinical-
// chemistry factor 88.4 µmol/L per 1 mg/dL: 88.4 / 72 = 1.2278.
//
// NOTE (2026-07-09, source re-verification): earlier notes in this repo
// (GATE_1C_AUDIT.md's NHS SPS hand-trace, sources/README.md) described
// the resulting rounded multiplier as "MHRA's 1.23/1.04 constants." A
// direct re-fetch of the MHRA source page confirmed this was imprecise —
// MHRA's page does not itself state the Cockcroft-Gault formula or any
// numeric constant; it names Cockcroft-Gault as the required method and
// points to external calculators (e.g. MDCalc). The 1.23/1.04 figures
// are simply the standard unit-conversion arithmetic above, rounded for
// manual calculation — not an MHRA-specific number. This function uses
// the unrounded exact fraction rather than the rounded 1.23/1.04, so no
// rounding decision is baked into a "proven" artifact that the source
// itself never made.
function CockcroftGaultCrClMlPerMin(ageYears: int, weightKg: real, isFemale: bool, serumCreatinineUmolPerL: real): real
  requires 0 <= ageYears < 140
  requires weightKg > 0.0
  requires serumCreatinineUmolPerL > 0.0
  ensures CockcroftGaultCrClMlPerMin(ageYears, weightKg, isFemale, serumCreatinineUmolPerL) > 0.0
  ensures !isFemale ==> CockcroftGaultCrClMlPerMin(ageYears, weightKg, isFemale, serumCreatinineUmolPerL) == ((140 - ageYears) as real) * weightKg * 88.4 / (72.0 * serumCreatinineUmolPerL)
  ensures isFemale ==> CockcroftGaultCrClMlPerMin(ageYears, weightKg, isFemale, serumCreatinineUmolPerL) == ((140 - ageYears) as real) * weightKg * 88.4 / (72.0 * serumCreatinineUmolPerL) * 0.85
{
  var base := ((140 - ageYears) as real) * weightKg * 88.4 / (72.0 * serumCreatinineUmolPerL);
  if isFemale then base * 0.85 else base
}

// End-to-end orchestration closing the loop Gate 1c Finding 1 opened:
// selects the formula (REQ-RENAL-2), and on the Cockcroft-Gault branch
// computes the CrCl value from raw inputs instead of taking it
// caller-supplied. The eGFR branch still takes `callerSuppliedEgfr` as
// an input — CKD-EPI eGFR is NOT computed here, per this file's header:
// that's a real Dafny/Z3 expressiveness gap (fractional exponents on a
// variable base), not a choice, so the asymmetry between the two
// branches is forced, not arbitrary.
function AssessRenalFunctionFromInputs(
  isDirectActingOralAnticoagulant: bool,
  isOnNephrotoxicDrug: bool,
  ageYears: int,
  bmi: real,
  isNarrowTherapeuticIndexDrug: bool,
  weightKg: real,
  isFemale: bool,
  serumCreatinineUmolPerL: real,
  callerSuppliedEgfr: real
): RenalAssessment
  requires 0 <= ageYears < 140
  requires bmi > 0.0
  requires weightKg > 0.0
  requires serumCreatinineUmolPerL > 0.0
  requires callerSuppliedEgfr >= 0.0
  ensures SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug) == CockcroftGaultFormula ==> AssessRenalFunctionFromInputs(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug, weightKg, isFemale, serumCreatinineUmolPerL, callerSuppliedEgfr) == AssessRenalFunction(CockcroftGaultFormula, CockcroftGaultCrClMlPerMin(ageYears, weightKg, isFemale, serumCreatinineUmolPerL)) // Gate 1c Finding 1 (Cockcroft-Gault)
  ensures SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug) == EGFRFormula ==> AssessRenalFunctionFromInputs(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug, weightKg, isFemale, serumCreatinineUmolPerL, callerSuppliedEgfr) == AssessRenalFunction(EGFRFormula, callerSuppliedEgfr) // eGFR remains caller-supplied — Dafny/Z3 expressiveness gap, not a scope choice
{
  var formula := SelectFormula(isDirectActingOralAnticoagulant, isOnNephrotoxicDrug, ageYears, bmi, isNarrowTherapeuticIndexDrug);
  if formula == CockcroftGaultFormula then
    AssessRenalFunction(formula, CockcroftGaultCrClMlPerMin(ageYears, weightKg, isFemale, serumCreatinineUmolPerL))
  else
    AssessRenalFunction(formula, callerSuppliedEgfr)
}
