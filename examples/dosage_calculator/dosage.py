import math


def calculate_hourly_dose(
    weight_kg: float,
    concentration_mg_per_ml: float,
    infusion_rate_ml_per_hr: float,
    max_safe_dose_mg_per_hr: float,
) -> float:
    """
    Compute the hourly delivered drug dose (mg/hr), clamped so it can never
    exceed max_safe_dose_mg_per_hr and never fall below zero.

    infusion_rate_ml_per_hr may be negative: a negative rate models the
    single-fault reverse-delivery condition of GIP v1.0 Safety Requirement
    1.8.1 / Hazard 1.14 (hardware driving flow backward). Any negative rate
    must yield exactly zero delivered dose (second postcondition).

    The negative check runs BEFORE the finiteness check deliberately: a
    negative rate whose product overflows to -inf must clamp to zero, not
    be mistaken for a positive overflow and clamped to the maximum. See
    dosage_naive_widening.py for the preserved wrong-order variant.

    weight_kg is a validated clinical input reserved for future weight-based
    ceilings; it is bounded here as a precondition guard.

    Second postcondition tightened to strict `>` (2026-07-15, R5
    differential-testing investigation): dosage.dfy's mirrored `ensures`
    clause was already tightened to `infusionRateMlPerHr > 0.0` on
    2026-07-07 (Gate C5 mutation testing found `>=` not independently
    load-bearing at rate == 0.0 exactly - real multiplication by exactly
    0.0 already forces dose == 0.0 there via the first postcondition).
    That fix was never back-ported to this docstring - found as a live
    example of exactly the cross-file drift R5 warns about. Behavior is
    unchanged (dose is 0.0 at rate == 0.0 either way); only the stated
    contract strength changes, re-verified against CrossHair below.

    pre: math.isfinite(weight_kg) and 0 < weight_kg <= 200
    pre: math.isfinite(concentration_mg_per_ml) and concentration_mg_per_ml > 0
    pre: math.isfinite(infusion_rate_ml_per_hr)
    pre: math.isfinite(max_safe_dose_mg_per_hr) and max_safe_dose_mg_per_hr > 0
    post: 0.0 <= __return__ <= max_safe_dose_mg_per_hr
    post: infusion_rate_ml_per_hr > 0 or __return__ == 0.0
    """
    raw_dose = infusion_rate_ml_per_hr * concentration_mg_per_ml
    if raw_dose < 0.0:
        return 0.0
    if not math.isfinite(raw_dose) or raw_dose > max_safe_dose_mg_per_hr:
        return max_safe_dose_mg_per_hr
    return raw_dose
