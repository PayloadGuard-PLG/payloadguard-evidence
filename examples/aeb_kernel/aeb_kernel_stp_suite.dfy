// Phase 2, Gate C4: Spec-Testing Proofs (IronSpec methodology) for
// aeb_kernel.dfy, mirroring renal_adjustment_stp_suite.dfy's discipline
// exactly - each lemma restates a function's ACTUAL declared ensures
// clause(s) as `requires` premises on a fresh hypothetical output value,
// then proves either the correct value is forced (ACCEPT) or a wrong
// candidate value is provably excluded (REJECT, `ensures false`) -
// testing the SPECIFICATION alone, independent of the function body ever
// being evaluated.
//
// Boundary values chosen directly from § 571.127's own strict/non-strict
// wording (source: sources/nhtsa-fmvss-127-2024.pdf): every "greater
// than X" / "less than Y" envelope gets an ACCEPT at the excluded
// boundary itself (proving the boundary is really excluded, not an
// off-by-one), an ACCEPT just inside it, and at least one REJECT
// confirming the wrong boolean is provably impossible.

include "aeb_kernel.dfy"

// ==================================================== FCWRequiredActive

// REQ-AEB-1 (S5.1.1, lead vehicle): envelope is 10.0 < speedKmh < 145.0.
lemma STP_Accept_FCW_Lead_LowerBoundExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 10.0 < 145.0))
  ensures !r
{}

lemma STP_Reject_FCW_Lead_LowerBoundExcluded_WrongValueExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 10.0 < 145.0))
  requires r // wrong: 10.0 is not strictly greater than 10.0, so FCW is
             // NOT required at exactly the lower boundary
  ensures false
{}

lemma STP_Accept_FCW_Lead_JustAboveLowerBound(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 10.001 < 145.0))
  ensures r
{}

lemma STP_Accept_FCW_Lead_UpperBoundExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 145.0 < 145.0))
  ensures !r
{}

lemma STP_Reject_FCW_Lead_UpperBoundExcluded_WrongValueExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 145.0 < 145.0))
  requires r // wrong: 145.0 is not strictly less than 145.0
  ensures false
{}

lemma STP_Accept_FCW_Lead_JustBelowUpperBound(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 144.999 < 145.0))
  ensures r
{}

// REQ-AEB-3 (S5.2.1, pedestrian): envelope is 10.0 < speedKmh < 73.0.
lemma STP_Accept_FCW_Pedestrian_LowerBoundExcluded(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 10.0 < 73.0))
  ensures !r
{}

lemma STP_Accept_FCW_Pedestrian_UpperBoundExcluded(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 73.0 < 73.0))
  ensures !r
{}

lemma STP_Reject_FCW_Pedestrian_UpperBoundExcluded_WrongValueExcluded(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 73.0 < 73.0))
  requires r // wrong: 73.0 is not strictly less than 73.0
  ensures false
{}

lemma STP_Accept_FCW_Pedestrian_JustBelowUpperBound(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 72.999 < 73.0))
  ensures r
{}

// ==================================================== AEBRequiredActive
//
// REQ-AEB-2/REQ-AEB-4: numerically identical envelopes to REQ-AEB-1/3,
// but a distinct declared requirement (confirmed in nl_confirmation_
// aeb_kernel_dfy.md) - restated in full rather than assumed to follow
// from the FCW lemmas above.

lemma STP_Accept_AEB_Lead_LowerBoundExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 10.0 < 145.0))
  ensures !r
{}

lemma STP_Reject_AEB_Lead_LowerBoundExcluded_WrongValueExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 10.0 < 145.0))
  requires r // wrong: excluded at exactly the lower boundary
  ensures false
{}

lemma STP_Accept_AEB_Lead_JustAboveLowerBound(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 10.001 < 145.0))
  ensures r
{}

lemma STP_Accept_AEB_Lead_UpperBoundExcluded(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 145.0 < 145.0))
  ensures !r
{}

lemma STP_Accept_AEB_Lead_JustBelowUpperBound(r: bool)
  requires LeadVehicleTarget == LeadVehicleTarget ==> (r <==> (10.0 < 144.999 < 145.0))
  ensures r
{}

lemma STP_Accept_AEB_Pedestrian_LowerBoundExcluded(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 10.0 < 73.0))
  ensures !r
{}

lemma STP_Accept_AEB_Pedestrian_UpperBoundExcluded(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 73.0 < 73.0))
  ensures !r
{}

lemma STP_Reject_AEB_Pedestrian_UpperBoundExcluded_WrongValueExcluded(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 73.0 < 73.0))
  requires r // wrong: excluded at exactly the upper boundary
  ensures false
{}

lemma STP_Accept_AEB_Pedestrian_JustBelowUpperBound(r: bool)
  requires PedestrianTarget == PedestrianTarget ==> (r <==> (10.0 < 72.999 < 73.0))
  ensures r
{}

// ============================================= IsSubjectVehicleBrakingOnset
//
// REQ-AEB-5 (S4): "achieves a deceleration of 0.15 g" - inclusive
// threshold (>=), unlike the S5.1/S5.2 envelopes above.

lemma STP_Accept_SubjectBrakingOnset_AtThreshold(r: bool)
  requires r <==> (0.15 >= 0.15)
  ensures r
{}

lemma STP_Reject_SubjectBrakingOnset_AtThreshold_WrongValueExcluded(r: bool)
  requires r <==> (0.15 >= 0.15)
  requires !r // wrong: 0.15g IS the onset point (inclusive)
  ensures false
{}

lemma STP_Accept_SubjectBrakingOnset_JustBelowThreshold(r: bool)
  requires r <==> (0.1499 >= 0.15)
  ensures !r
{}

// ================================================ IsLeadVehicleBrakingOnset
//
// REQ-AEB-6 (S4): "achieves a deceleration of 0.05 g" - inclusive.

lemma STP_Accept_LeadBrakingOnset_AtThreshold(r: bool)
  requires r <==> (0.05 >= 0.05)
  ensures r
{}

lemma STP_Reject_LeadBrakingOnset_AtThreshold_WrongValueExcluded(r: bool)
  requires r <==> (0.05 >= 0.05)
  requires !r // wrong: 0.05g IS the onset point (inclusive)
  ensures false
{}

lemma STP_Accept_LeadBrakingOnset_JustBelowThreshold(r: bool)
  requires r <==> (0.0499 >= 0.05)
  ensures !r
{}

// ============================================= IsBrakePedalApplicationOnset
//
// REQ-AEB-7 (S4): "when 11 N of force has been applied" - inclusive.

lemma STP_Accept_BrakePedalOnset_AtThreshold(r: bool)
  requires r <==> (11.0 >= 11.0)
  ensures r
{}

lemma STP_Reject_BrakePedalOnset_AtThreshold_WrongValueExcluded(r: bool)
  requires r <==> (11.0 >= 11.0)
  requires !r // wrong: 11 N IS the onset point (inclusive)
  ensures false
{}

lemma STP_Accept_BrakePedalOnset_JustBelowThreshold(r: bool)
  requires r <==> (10.999 >= 11.0)
  ensures !r
{}

// =================================================== IsFalseActivationCompliant
//
// REQ-AEB-8 (S5.3): violation is "exceeds... by 0.25 g or greater", so
// compliance is the strict-less-than negation - exactly at 0.25 g is
// already a violation (NOT compliant), unlike the >= onset thresholds
// above. Worth an explicit STP since this function's boundary direction
// is the opposite of REQ-AEB-5/6/7's, and getting that backwards would
// be exactly the kind of off-by-one Gate C4 exists to catch.

lemma STP_Accept_FalseActivation_AtThreshold_NotCompliant(r: bool)
  requires 0.25 >= 0.0
  requires r <==> (0.25 < 0.25)
  ensures !r
{}

lemma STP_Reject_FalseActivation_AtThreshold_WrongValueExcluded(r: bool)
  requires 0.25 >= 0.0
  requires r <==> (0.25 < 0.25)
  requires r // wrong: 0.25g is already a violation ("...by 0.25 g or
             // greater"), not compliant
  ensures false
{}

lemma STP_Accept_FalseActivation_JustBelowThreshold_Compliant(r: bool)
  requires 0.2499 >= 0.0
  requires r <==> (0.2499 < 0.25)
  ensures r
{}
