"""Shared test-vector data for R5's differential-testing harness
(`RISK_MANAGEMENT_FINDINGS.md`): the single source of truth both
`generate_dosage_differential_driver.py` (Dafny side) and
`run_verify_dosage_differential.py` (Python side) read, so the two
implementations are checked against the identical inputs rather than
two independently-typed lists that could themselves drift.

Scope, stated explicitly rather than implied: every vector here keeps
its Dafny-side `raw_dose` within the domain `dosage.dfy`'s own header
comment already scopes itself to — finite in the IEEE-754 sense, since
Dafny's `real` type has no overflow concept at all to be out of range
of. On the Python side, one vector is the deliberate exception:
`overflow_negative_mirrors_test_dosage_concrete` below genuinely
overflows Python's `float` (reusing `tests/test_dosage_concrete.py`'s
own `overflow_negative_rate_clamps_to_zero` case) and still produces the
same output in both — but only because the chosen `max_safe_dose_mg_per_hr`
is far smaller than any overflowed value, so both implementations reach
their respective clamp branch. That agreement is real but coincidental
to this specific vector's chosen magnitudes, not a general proof that
REQ-DOSE-003's overflow-detection behavior is equivalent across the two
artifacts — it structurally cannot be, since Dafny cannot represent
"this value overflowed" as a concept. Documented here so a reader of
the generated results doesn't mistake vector-level agreement for a
claim this harness does not and cannot make.

Values are deliberately chosen to be exactly representable in both IEEE
double precision and Dafny's arbitrary-precision rational `real` (whole
numbers and halves/quarters), so a printed-decimal comparison between
the two tools' output is a real equivalence check, not an artifact of
independent rounding in two different numeric representations. Testing
genuinely non-terminating-in-binary decimals (e.g. 0.1, 0.3) against
Dafny's exact rational arithmetic is a real, separate question this
harness does not attempt to answer.
"""

VECTORS = [
    {
        "id": "ordinary_in_range",
        "concentration_mg_per_ml": 2.0,
        "infusion_rate_ml_per_hr": 3.0,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": "Plain in-range case: raw_dose (6.0) stays below the ceiling, else branch",
    },
    {
        "id": "ordinary_negative_rate",
        "concentration_mg_per_ml": 2.0,
        "infusion_rate_ml_per_hr": -5.0,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": "Reverse-delivery fault (REQ-GIP-1-8-1): negative raw_dose clamps to zero",
    },
    {
        "id": "boundary_rate_zero",
        "concentration_mg_per_ml": 2.0,
        "infusion_rate_ml_per_hr": 0.0,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": (
            "The exact postcondition boundary tightened 2026-07-15 (Dafny "
            "side, 2026-07-07): raw_dose == 0.0 is not negative, so this "
            "exercises the else branch, not the reverse-delivery clamp - "
            "both postconditions' strict-> vs >= distinction is moot here "
            "since dose == 0.0 either way, confirmed by this vector directly"
        ),
    },
    {
        "id": "boundary_raw_equals_max",
        "concentration_mg_per_ml": 2.0,
        "infusion_rate_ml_per_hr": 5.0,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": "raw_dose (10.0) exactly equals the ceiling: > is false, else branch returns it unclamped",
    },
    {
        "id": "clamp_above_max",
        "concentration_mg_per_ml": 2.0,
        "infusion_rate_ml_per_hr": 6.0,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": "raw_dose (12.0) exceeds the ceiling (REQ-GIP-1-4-12): clamps to max_safe_dose_mg_per_hr",
    },
    {
        "id": "fractional_exact_below",
        "concentration_mg_per_ml": 4.0,
        "infusion_rate_ml_per_hr": 1.5,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": "Non-integer but exactly binary-representable inputs (1.5 = 3/2): raw_dose 6.0, else branch",
    },
    {
        "id": "fractional_exact_at_boundary",
        "concentration_mg_per_ml": 4.0,
        "infusion_rate_ml_per_hr": 2.5,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": "Fractional inputs (2.5 = 5/2) landing exactly on the ceiling: raw_dose 10.0, else branch",
    },
    {
        "id": "large_but_finite",
        "concentration_mg_per_ml": 1e10,
        "infusion_rate_ml_per_hr": 1e10,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": (
            "raw_dose = 1e20 - large, but well within IEEE double range "
            "(no overflow in Python either), so this is a genuine finite-"
            "domain clamp-above-max case, not an overflow one, confirming "
            "the two implementations agree at magnitude, not just near zero"
        ),
    },
    {
        "id": "overflow_negative_mirrors_test_dosage_concrete",
        "concentration_mg_per_ml": 1e308,
        "infusion_rate_ml_per_hr": -2.0,
        "max_safe_dose_mg_per_hr": 10.0,
        "note": (
            "Reuses tests/test_dosage_concrete.py's own "
            "overflow_negative_rate_clamps_to_zero case. In Python, "
            "raw_dose overflows to -inf (still < 0.0, so it clamps to "
            "zero via the SAME branch as an ordinary negative rate). In "
            "Dafny, raw_dose is the exact value -2e308 (no overflow "
            "concept exists), also < 0.0. Both reach dose == 0.0, but via "
            "genuinely different reasoning - see this file's own module "
            "docstring for why this is not a REQ-DOSE-003 equivalence claim"
        ),
    },
]
