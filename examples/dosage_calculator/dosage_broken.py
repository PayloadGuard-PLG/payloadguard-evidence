import math


def calculate_hourly_dose(
    weight_kg: float,
    concentration_mg_per_ml: float,
    infusion_rate_ml_per_hr: float,
    max_safe_dose_mg_per_hr: float,
) -> float:
    """
    Deliberately broken variant of dosage.py (Sample B fixture): the clamp is
    removed and raw_dose is returned directly, so the postcondition is
    violated whenever raw_dose exceeds max_safe_dose_mg_per_hr. Exists only
    to prove the fixture capture works on a failing run.

    pre: math.isfinite(weight_kg) and 0 < weight_kg <= 200
    pre: math.isfinite(concentration_mg_per_ml) and concentration_mg_per_ml > 0
    pre: math.isfinite(infusion_rate_ml_per_hr) and infusion_rate_ml_per_hr >= 0
    pre: math.isfinite(max_safe_dose_mg_per_hr) and max_safe_dose_mg_per_hr > 0
    post: 0.0 <= __return__ <= max_safe_dose_mg_per_hr
    """
    raw_dose = infusion_rate_ml_per_hr * concentration_mg_per_ml
    return raw_dose
