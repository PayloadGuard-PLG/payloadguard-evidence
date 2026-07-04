# Capture runner for the concrete evidence foundation (T4-0). Two real
# artifacts from one source of truth (tests/test_dosage_concrete.py CASES):
#   - raw_pytest_output_concrete.txt / run_manifest_concrete.json: verbatim
#     pytest run, command and exit code recorded.
#   - concrete_results.json: per-case structured records (inputs, expected,
#     observed, passed) produced by actually executing the kernel, for the
#     T4 variant binders. Observed values are recorded from execution, never
#     copied from expectations.
import datetime
import json
import pathlib
import platform
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))
sys.path.insert(0, str(HERE))

from test_dosage_concrete import CASES  # noqa: E402
from dosage import calculate_hourly_dose  # noqa: E402


def main():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()

    cases_out = []
    for case in CASES:
        observed = calculate_hourly_dose(**case["inputs"])
        cases_out.append(
            {
                "test_id": case["test_id"],
                "requirement_id": case["requirement_id"],
                "function": case["function"],
                "inputs": case["inputs"],
                "expected": case["expected"],
                "observed": observed,
                "passed": observed == case["expected"],
            }
        )

    cmd = [sys.executable, "-m", "pytest", "tests/test_dosage_concrete.py", "-v"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    (HERE / "raw_pytest_output_concrete.txt").write_text(
        (proc.stdout or "") + (proc.stderr or "")
    )
    manifest = {
        "tool": "pytest",
        "command": cmd,
        "cwd": str(REPO_ROOT),
        "exit_code": proc.returncode,
        "started_utc": started,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "target": "tests/test_dosage_concrete.py",
    }
    (HERE / "run_manifest_concrete.json").write_text(json.dumps(manifest, indent=2))
    (HERE / "concrete_results.json").write_text(
        json.dumps(
            {
                "source": "tests/test_dosage_concrete.py::CASES",
                "started_utc": started,
                "pytest_exit_code": proc.returncode,
                "cases": cases_out,
            },
            indent=2,
        )
    )
    print(f"captured; pytest exit_code={proc.returncode}; cases={len(cases_out)}")


if __name__ == "__main__":
    main()
