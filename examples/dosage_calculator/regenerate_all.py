# Sanctioned regeneration entrypoint (Turn 2.0 B2). Runs the three variant
# generators in sequence, then the cross-artifact fact-equality gate. The
# gate is a property of the artifact SET, so it cannot live inside any
# single generator (a mid-regeneration comparison would race stale sibling
# files); individual generators are unchanged by design (ratified). The
# base Phase A matrix is frozen (ruling R2c) and participates in the gate
# as the symbolic-subset legacy view. Running a generator alone bypasses
# the generation-time gate; the committed artifacts remain protected by
# tests/test_fact_equality.py.
#
# 2026-07-07 (Gate 2/C2-C4 wiring, extended to variants A/B same day):
# traceability_matrix.formal.json is now a full peer inside run_gate()
# itself (evidence/reconcile.py::VARIANT_ARTIFACTS) - the separate,
# narrower run_formal_check() this file used to call while A/B's own
# dafny wiring was still pending has been retired now that it's landed
# and the temporary divergence it tracked is closed.
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.reconcile import run_gate  # noqa: E402

GENERATORS = ("generate_matrix_a.py", "generate_matrix_b.py", "generate_matrix_c.py")


def main():
    for script in GENERATORS:
        subprocess.run([sys.executable, str(HERE / script)], check=True, cwd=HERE)
    result = run_gate(HERE)
    print(
        f"fact-equality gate: PASS ({result['facts']} facts; "
        f"intent {result['intent']})"
    )


if __name__ == "__main__":
    main()
