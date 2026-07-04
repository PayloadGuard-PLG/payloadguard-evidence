import math

from overflow_probe import double_it


def test_double_it_overflows_to_inf_on_ieee_hardware():
    """Deterministic IEEE violation of overflow_probe.py's postcondition
    (post: math.isfinite(__return__)): 1e308 * 2.0 overflows to inf. This
    executable fact sits beside the symbolic capture
    (raw_crosshair_output_overflow_probe.txt) so the model-fidelity gap is
    documented by both a concrete run and the symbolic result."""
    assert math.isinf(double_it(1e308))
