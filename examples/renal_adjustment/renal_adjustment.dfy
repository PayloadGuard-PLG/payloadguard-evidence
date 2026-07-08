// Dafny spec for renal-function dose adjustment — Gate C1 (Phase 2),
// PayloadGuard-Evidence's second, independent proof-of-concept.
//
// SCOPE, NAMED EXPLICITLY (per PHASE1_PLAN.md's "Closed under named
// fallback assumptions" section): this spec covers REQ-RENAL-1,
// REQ-RENAL-1a, REQ-RENAL-2, and REQ-RENAL-5 — GFR staging with KDIGO's
// rounding convention, formula selection between eGFR and Cockcroft-Gault
// CrCl, the type-level guarantee that a CrCl value can never be run
// through eGFR staging, and bound composition against dosage.dfy's
// existing ceiling. It does NOT compute Cockcroft-Gault CrCl or CKD-EPI
// eGFR from raw patient data (age/weight/sex/creatinine/cystatin C) —
// both formulas' numeric outputs are caller-supplied inputs to
// AssessRenalFunction, a provisional default (not a permanent decision)
// per Steven's explicit direction, backed by verified equation data in
// sources/ckd-epi-2021-and-cockcroft-gault-verification.md. REQ-RENAL-3,
// REQ-RENAL-4, REQ-RENAL-6, and REQ-RENAL-7 are not yet formalized as
// Dafny signatures (see GATE_1C_AUDIT.md's REQ-by-REQ trace) — they
// exist only as prose in Gate 1a/1b so far.
//
// Every function body below was first checked in a scratch file against
// this same installed Dafny 4.11.0 toolchain during Gate 1c's audit and
// its addendum (2026-07-08) before being committed here verbatim — no
// body changed between the scratch check and this file.

datatype GStageCategory = G1 | G2 | G3a | G3b | G4 | G5
datatype Formula = EGFRFormula | CockcroftGaultFormula
datatype RenalAssessment =
  | EGFRAssessment(stage: GStageCategory)
  | CrClAssessment(roundedCrClMlPerMin: int)

// REQ-RENAL-1a: KDIGO reports eGFR rounded to the nearest whole number
// before staging (sources/kdigo-2024-gfr-staging.md, Table 11) — this
// shifts the effective continuous G-stage boundaries to 89.5/59.5/44.5/
// 29.5/14.5 (round-half-up), not the naive 90.0/60.0/45.0/30.0/15.0.
function RoundHalfUp(x: real): int
  requires x >= 0.0
  ensures (RoundHalfUp(x) as real) - 0.5 <= x < (RoundHalfUp(x) as real) + 0.5 // REQ-RENAL-1a
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
function ComposedCeiling(existingCeiling: real, renalCeiling: real): real
  requires existingCeiling > 0.0
  requires renalCeiling > 0.0
  ensures ComposedCeiling(existingCeiling, renalCeiling) <= existingCeiling // REQ-RENAL-5
  ensures ComposedCeiling(existingCeiling, renalCeiling) <= renalCeiling // REQ-RENAL-5
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
function AssessRenalFunction(formula: Formula, renalFunctionValue: real): RenalAssessment
  requires renalFunctionValue >= 0.0
  ensures formula == EGFRFormula ==> AssessRenalFunction(formula, renalFunctionValue).EGFRAssessment? // REQ-RENAL-1, REQ-RENAL-2
  ensures formula == CockcroftGaultFormula ==> AssessRenalFunction(formula, renalFunctionValue).CrClAssessment? // REQ-RENAL-1, REQ-RENAL-2
{
  if formula == EGFRFormula then
    EGFRAssessment(GStage(RoundHalfUp(renalFunctionValue)))
  else
    CrClAssessment(RoundHalfUp(renalFunctionValue))
}
