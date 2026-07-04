import math


def calculate_hourly_dose(
    weight_kg: float,
    concentration_mg_per_ml: float,
    infusion_rate_ml_per_hr: float,
    max_safe_dose_mg_per_hr: float,
) -> float:
    """
    Compute the hourly delivered drug dose (mg/hr), clamped so it can never
    exceed max_safe_dose_mg_per_hr.

    weight_kg is a validated clinical input reserved for future weight-based
    ceilings; it is bounded here as a precondition guard.

    pre: math.isfinite(weight_kg) and 0 < weight_kg <= 200
    pre: math.isfinite(concentration_mg_per_ml) and concentration_mg_per_ml > 0
    pre: math.isfinite(infusion_rate_ml_per_hr) and infusion_rate_ml_per_hr >= 0
    pre: math.isfinite(max_safe_dose_mg_per_hr) and max_safe_dose_mg_per_hr > 0
    post: 0.0 <= __return__ <= max_safe_dose_mg_per_hr
    """
    raw_dose = infusion_rate_ml_per_hr * concentration_mg_per_ml
    if not math.isfinite(raw_dose) or raw_dose > max_safe_dose_mg_per_hr:
        return max_safe_dose_mg_per_hr
    if raw_dose < 0.0:
        return 0.0
    return raw_dose
