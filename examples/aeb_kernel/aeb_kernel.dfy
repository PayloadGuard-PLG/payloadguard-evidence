// Dafny spec for a Generic Autonomous Emergency Braking (AEB) kernel —
// Gate C1 (Phase 2), PayloadGuard-Evidence's fourth worked example and
// its first outside the medical-device domain: automotive functional
// safety. Deliberately scoped to a generic light-vehicle AEB system, NOT
// any named commercial vehicle or manufacturer (Steven's explicit
// scoping decision, 2026-07-16) — the point of this example is to show
// the Gate C1-C6 architecture generalizes to a new regulatory domain,
// not to evaluate any specific product.
//
// PRIMARY SOURCE, read directly before any line below was written:
// sources/nhtsa-fmvss-127-2024.pdf — NHTSA/DOT Final Rule "Automatic
// Emergency Braking Systems for Light Vehicles," 49 CFR Parts 571, 595,
// 596, Docket No. NHTSA-2023-0021, RIN 2127-AM37 (2024). The codified
// regulatory text is § 571.127 ("Standard No. 127; Automatic emergency
// braking systems for light vehicles"), confirmed to begin partway
// through the 317-page PDF after ~300 pages of rulemaking preamble —
// every requirement cited below is transcribed from that section
// directly, not from the preamble discussion or any secondary summary.
//
// STRUCTURAL FINDING, worth naming explicitly: § 571.127's S5
// ("Requirements") — the actual performance obligations a vehicle must
// meet — are entirely SPEED-ENVELOPE and DECELERATION-THRESHOLD based,
// not wall-clock-timing based. The millisecond/second-level timing
// figures in the document (500 ms accelerator-pedal release, 1.0 ± 0.1 s
// brake-application onset) appear only in S7/S8, which specify how
// NHTSA CONDUCTS a compliance test on a track — not what the vehicle's
// AEB system itself must always guarantee. So unlike dosage_calculator's
// IEEE-754 gap or renal_adjustment's Pow-exponent gap, this domain's
// core requirements hit no Dafny/Z3 structural expressiveness limit:
// every S5 clause below is provable as ordinary real-number interval
// arithmetic, no wall-clock or floating-point modeling required.
//
// SCOPE, named explicitly (matching PHASE1_PLAN.md's convention in the
// other three examples): this file covers S4's three named onset
// definitions and S5.1.1, S5.1.2, S5.2.1, S5.2.2, and S5.3 — the
// speed-envelope and deceleration-threshold requirements that are
// directly, numerically checkable from the codified text. S3
// (Application — GVWR <= 4,536 kg), S5.4 (malfunction detection and
// controls), S6 (test conditions), S7/S8/S9 (test procedures), and S10
// (brake application specification) are NOT formalized here: S3 is a
// vehicle-class eligibility gate rather than kernel logic, S5.4 is a
// stateful telltale/mode-control requirement (a different kind of
// claim than a pure function), and S6-S10 are test-procedure detail,
// not requirements the AEB kernel itself must satisfy. This mirrors the
// kernel_scope/system_scope split established in
// examples/dosage_calculator/ (REQ-GIP-1-4-12).
//
// Every function body below was checked against the installed Dafny
// 4.11.0 toolchain before being committed here.

datatype TargetType = LeadVehicleTarget | PedestrianTarget

// REQ-AEB-1 (S5.1.1, Forward collision warning vs. a lead vehicle):
// "The system must operate under the conditions specified in S6 when
// traveling at any forward speed that is greater than 10 km/h (6.2 mph)
// and less than 145 km/h (90.1 mph)."
//
// REQ-AEB-3 (S5.2.1, Forward collision warning vs. a pedestrian):
// "...when the vehicle is traveling at any forward speed that is
// greater than 10 km/h (6.2 mph) and less than 73 km/h (45.3 mph)."
function FCWRequiredActive(target: TargetType, speedKmh: real): bool
  ensures target == LeadVehicleTarget ==>
    (FCWRequiredActive(target, speedKmh) <==> (10.0 < speedKmh < 145.0)) // REQ-AEB-1
  ensures target == PedestrianTarget ==>
    (FCWRequiredActive(target, speedKmh) <==> (10.0 < speedKmh < 73.0)) // REQ-AEB-3
{
  match target
  case LeadVehicleTarget => 10.0 < speedKmh < 145.0
  case PedestrianTarget => 10.0 < speedKmh < 73.0
}

// REQ-AEB-2 (S5.1.2, Automatic emergency braking vs. a lead vehicle):
// same speed envelope as S5.1.1, but for the AEB obligation (automatic
// service-brake application) rather than the warning obligation — a
// distinct legal requirement in the source text even though its numeric
// envelope happens to coincide with REQ-AEB-1's, confirmed by reading
// both clauses directly rather than assumed from the shared numbers.
//
// REQ-AEB-4 (S5.2.2, Automatic emergency braking vs. a pedestrian): same
// envelope as S5.2.1, same FCW/AEB distinction.
function AEBRequiredActive(target: TargetType, speedKmh: real): bool
  ensures target == LeadVehicleTarget ==>
    (AEBRequiredActive(target, speedKmh) <==> (10.0 < speedKmh < 145.0)) // REQ-AEB-2
  ensures target == PedestrianTarget ==>
    (AEBRequiredActive(target, speedKmh) <==> (10.0 < speedKmh < 73.0)) // REQ-AEB-4
{
  match target
  case LeadVehicleTarget => 10.0 < speedKmh < 145.0
  case PedestrianTarget => 10.0 < speedKmh < 73.0
}

// REQ-AEB-5 (S4, "Subject vehicle braking onset"): "the point at which
// the subject vehicle achieves a deceleration of 0.15 g due to the
// automatic control of the service brakes."
function IsSubjectVehicleBrakingOnset(decelG: real): bool
  ensures IsSubjectVehicleBrakingOnset(decelG) <==> decelG >= 0.15 // REQ-AEB-5
{
  decelG >= 0.15
}

// REQ-AEB-6 (S4, "Lead vehicle braking onset"): "the point at which the
// lead vehicle achieves a deceleration of 0.05 g due to brake
// application."
function IsLeadVehicleBrakingOnset(decelG: real): bool
  ensures IsLeadVehicleBrakingOnset(decelG) <==> decelG >= 0.05 // REQ-AEB-6
{
  decelG >= 0.05
}

// REQ-AEB-7 (S4, "Brake pedal application onset"): "when 11 N of force
// has been applied to the brake pedal."
function IsBrakePedalApplicationOnset(forceN: real): bool
  ensures IsBrakePedalApplicationOnset(forceN) <==> forceN >= 11.0 // REQ-AEB-7
{
  forceN >= 11.0
}

// REQ-AEB-8 (S5.3, False activation): "The vehicle must not
// automatically apply braking that results in peak additional
// deceleration that exceeds what manual braking would produce by 0.25 g
// or greater..." — so compliance is peakAdditionalDecelG < 0.25;
// violating the standard is >= 0.25.
function IsFalseActivationCompliant(peakAdditionalDecelG: real): bool
  requires peakAdditionalDecelG >= 0.0
  ensures IsFalseActivationCompliant(peakAdditionalDecelG) <==> peakAdditionalDecelG < 0.25 // REQ-AEB-8
{
  peakAdditionalDecelG < 0.25
}
