import math


def calculate_hourly_dose(
    weight_kg: float,
    concentration_mg_per_ml: float,
    infusion_rate_ml_per_hr: float,
    max_safe_dose_mg_per_hr: float,
) -> float:
    """
    Deliberately broken variant of dosage.py (Sample B fixture): both clamps
    are removed and raw_dose is returned directly, so the postconditions are
    violated whenever raw_dose exceeds max_safe_dose_mg_per_hr or is
    negative. Exists only to prove the fixture capture works on a failing
    run. Contract mirrors dosage.py (2026-07-04 Option A amendment).

    pre: math.isfinite(weight_kg) and 0 < weight_kg <= 200
    pre: math.isfinite(concentration_mg_per_ml) and concentration_mg_per_ml > 0
    pre: math.isfinite(infusion_rate_ml_per_hr)
    pre: math.isfinite(max_safe_dose_mg_per_hr) and max_safe_dose_mg_per_hr > 0
    post: 0.0 <= __return__ <= max_safe_dose_mg_per_hr
    post: infusion_rate_ml_per_hr >= 0 or __return__ == 0.0
    """
    raw_dose = infusion_rate_ml_per_hr * concentration_mg_per_ml
    return raw_dose
