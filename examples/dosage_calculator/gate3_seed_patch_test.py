"""
Gate 3 candidate fix: CrossHair seed override — verification script.

CORRECTED from the original external-research proposal after checking it
against the real source (github.com/pschanely/CrossHair,
crosshair/statespace.py). Two errors found and fixed:

1. WRONG TARGET. The seed is not hard-coded inline inside
   StateSpace.__init__. It's hard-coded in a separate function,
   make_default_solver(), which __init__ calls to build self.solver.
   This script patches make_default_solver directly.

2. WRONG PARAMETER NAMES. The real code sets HYPHENATED Z3 params:
       solver.set("random-seed", 42)
       solver.set("smt.random-seed", 42)
   The original proposal used underscored names ("random_seed",
   "smt.random_seed"). If Z3 doesn't normalize the two forms, that patch
   would silently set a no-op parameter while the real hard-coded seed
   stayed in effect - a false "it works" or a false "it doesn't work"
   depending on how the check was done. This script uses the real
   hyphenated names.

Also flagged, not fixed here: CrossHair's latest tagged release is
v0.0.106, not v0.0.107 as pinned in this project's toolchain metadata.
Confirm what's actually installed (`pip show crosshair-tool`) before
trusting any version-specific claim, including this one.

THIRD CORRECTION, found by actually running this script against 0.0.107:
`analyze_function`'s second parameter is typed `AnalysisOptionSet`, not
`AnalysisOptions` — `AnalysisOptions(max_iterations=..., per_condition_timeout=...)`
raises `TypeError: missing 9 required positional arguments` on this
installed version, since `AnalysisOptions` has no defaults and
`analyze_function` never accepted it directly. `AnalysisOptionSet` is the
partially-specified, defaultable variant meant for this call site. Fixed
below to import and construct `AnalysisOptionSet`.

WHAT THIS SCRIPT DOES NOT DO: assume the patch works. Z3 has no reliable
get() for these params, so introspection can't confirm the override took
effect. The only real confirmation is behavioral: run the same target
with two different seed values and check whether CrossHair's actual
exploration output (paths taken, counterexamples found, or their order)
differs. If it's identical regardless of seed, the patch did not take
effect - full stop, do not rationalize a partial success.

USAGE:
    CROSSHAIR_SOLVER_SEED=1 python gate3_seed_patch_test.py > run_seed_1.txt
    CROSSHAIR_SOLVER_SEED=2 python gate3_seed_patch_test.py > run_seed_2.txt
    diff run_seed_1.txt run_seed_2.txt

If the diff is empty: the patch had no effect. Fall back to Gate 3's
stay-CLI recommendation and document seed as a tool-version limitation.

If the diff shows different exploration order/counterexamples: the patch
works. Proceed to build the API harness and re-capture.
"""

import os
import sys

try:
    import crosshair.statespace as statespace
except ImportError:
    print("ERROR: crosshair-tool is not installed in this environment.")
    print("Run: pip install crosshair-tool --break-system-packages")
    sys.exit(1)

# --- Sanity check: confirm what's actually installed ---
try:
    import importlib.metadata as _im

    installed_version = _im.version("crosshair-tool")
except Exception:
    installed_version = "UNKNOWN - could not determine via importlib.metadata"

print(f"[sanity check] Installed crosshair-tool version: {installed_version}")
print(
    "[sanity check] This project's toolchain metadata pins 0.0.107. "
    "GitHub's latest tagged release at time of writing is 0.0.106. "
    "If these don't match what's installed, treat every version-specific "
    "claim in this script and the roadmap as unverified for your actual "
    "environment until reconciled."
)
print()

# --- Confirm the target function actually exists before patching it ---
if not hasattr(statespace, "make_default_solver"):
    print(
        "ERROR: crosshair.statespace.make_default_solver not found. "
        "The installed version's internals may differ from what was "
        "checked against the GitHub source. Do not proceed with this "
        "patch on an unverified internal API - re-check the installed "
        "version's actual source before continuing."
    )
    sys.exit(1)

_original_make_default_solver = statespace.make_default_solver


def _patched_make_default_solver():
    solver = _original_make_default_solver()
    custom_seed = int(os.getenv("CROSSHAIR_SOLVER_SEED", "42"))
    # Real hyphenated parameter names, confirmed against source - not the
    # underscored names from the original (incorrect) proposal.
    solver.set("random-seed", custom_seed)
    solver.set("smt.random-seed", custom_seed)
    return solver


statespace.make_default_solver = _patched_make_default_solver

seed_used = os.getenv("CROSSHAIR_SOLVER_SEED", "42")
print(f"[patch] make_default_solver patched. Requested seed: {seed_used}")
print(
    "[patch] No reliable introspection exists to confirm Z3 accepted "
    "this value - the real test is behavioral, below."
)
print()

# --- Behavioral test: run calculate_hourly_dose twice (once per script
#     invocation, per the diff-based usage above) and let the actual
#     CrossHair output be the evidence, not this script's assumptions.
#
#     Starting target: calculate_hourly_dose (simplest case). Move to
#     other functions once this one is confirmed working end to end.
#
#     Determinism expectation: for a GIVEN seed, this must produce the
#     SAME result every time it's run - same pass/fail, same
#     counterexample if one is found. That's what "deterministic" means
#     here. The seed override is only doing its job if DIFFERENT seeds
#     can produce DIFFERENT results (one finds a violation, another
#     doesn't, or they find different counterexamples) - not if the
#     same seed produces different results on repeat runs. If you see
#     the latter, something else is non-deterministic in the pipeline
#     and that's a separate bug, not a seed-patch success. ---

try:
    # crosshair.core alone is not enough: analyze_calltree requires the
    # opcode-level tracing patches, which are only installed as a side
    # effect of importing crosshair.core_and_libs (confirmed by running
    # this script against crosshair.core directly first: it raised
    # CrossHairInternal("Opcode patches haven't been loaded yet.")).
    from crosshair.core_and_libs import analyze_function
    from crosshair.options import AnalysisOptionSet
except ImportError as e:
    print(f"ERROR: could not import CrossHair core/options: {e}")
    sys.exit(1)

try:
    from dosage import calculate_hourly_dose
except ImportError as e:
    print(f"ERROR: could not import calculate_hourly_dose from dosage.py: {e}")
    print(
        "Run this script from the directory containing dosage.py, or "
        "adjust the import path before proceeding."
    )
    sys.exit(1)

options = AnalysisOptionSet(max_iterations=100000, per_condition_timeout=30)

print(f"[test] Target: calculate_hourly_dose")
print(f"[test] Bounds: max_iterations=100000, per_condition_timeout=30")
print(f"[test] Seed requested: {seed_used}")
print("[test] Running analyze_function - this may take up to 30s...")
print()

checkables = list(analyze_function(calculate_hourly_dose, options))
print(
    f"[test] analyze_function returned {len(checkables)} Checkable(s) "
    "(one per postcondition parsed from source - this step does NOT run "
    "the solver yet). Calling .analyze() on each to actually execute the "
    "symbolic search."
)
print()

results = []
for c in checkables:
    results.extend(c.analyze())

if not results:
    print(f"RESULT (seed={seed_used}): PASS - no counterexample found")
else:
    print(f"RESULT (seed={seed_used}): FAIL - {len(results)} issue(s) found")
    for i, r in enumerate(results, start=1):
        print(f"  [{i}] {r.state} {r.message} (line {r.line})")
        if r.test_fn:
            print(f"      test_fn: {r.test_fn}")

print()
print(
    "[next step] Run this script again with a different "
    "CROSSHAIR_SOLVER_SEED value, then diff the two full outputs. "
    "Identical RESULT lines (and identical counterexamples, if any) "
    "across both seeds means the patch had no effect - fall back to "
    "stay-CLI. A difference in PASS/FAIL or in which counterexample was "
    "found means the patch works - proceed to build the API harness."
)
