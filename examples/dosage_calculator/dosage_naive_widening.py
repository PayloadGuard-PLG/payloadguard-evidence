import math


def calculate_hourly_dose(
    weight_kg: float,
    concentration_mg_per_ml: float,
    infusion_rate_ml_per_hr: float,
    max_safe_dose_mg_per_hr: float,
) -> float:
    """
    Review artifact (2026-07-04 Option A amendment), preserved deliberately:
    the NAIVE widening of dosage.py's contract. The precondition accepts
    negative infusion rates (modelling the reverse-delivery fault) and the
    directional postcondition demands negative rate -> zero dose, but the
    branch order is the ORIGINAL one: the finiteness check runs first. A
    negative rate whose product overflows to -inf is therefore caught by
    `not math.isfinite(raw_dose)` and returns the MAXIMUM safe dose - the
    worst possible response to a reverse-flow fault. Concrete violation:
    calculate_hourly_dose(70.0, 1e308, -2.0, 10.0) returns 10.0, not 0.0.
    dosage.py fixes this by testing `raw_dose < 0.0` first (true for -inf).
    Do not use this variant; it exists to document why the branch order in
    dosage.py is load-bearing.

    pre: math.isfinite(weight_kg) and 0 < weight_kg <= 200
    pre: math.isfinite(concentration_mg_per_ml) and concentration_mg_per_ml > 0
    pre: math.isfinite(infusion_rate_ml_per_hr)
    pre: math.isfinite(max_safe_dose_mg_per_hr) and max_safe_dose_mg_per_hr > 0
    post: 0.0 <= __return__ <= max_safe_dose_mg_per_hr
    post: infusion_rate_ml_per_hr >= 0 or __return__ == 0.0
    """
    raw_dose = infusion_rate_ml_per_hr * concentration_mg_per_ml
    if not math.isfinite(raw_dose) or raw_dose > max_safe_dose_mg_per_hr:
        return max_safe_dose_mg_per_hr
    if raw_dose < 0.0:
        return 0.0
    return raw_dose
