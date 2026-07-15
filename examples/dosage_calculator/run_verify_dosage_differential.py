"""R5 differential-testing harness capture (RISK_MANAGEMENT_FINDINGS.md):
runs the real `dafny run` on the generated dosage_differential_driver.dfy,
captures its raw output verbatim (Gate C1 discipline - the exact command,
exit code, tool version, and timestamp, mirroring run_verify_dafny.py),
then runs dosage.py's real calculate_hourly_dose on the identical shared
vectors and compares. Writes differential_test_results.json: one record
per vector, with both implementations' output and a match flag.

This is a capture step, run manually/in-session against the real
installed Dafny toolchain - like every other raw_*_output.txt in this
repo, the committed differential_test_results.json is read by
tests/test_dosage_differential.py, not re-produced by re-invoking Dafny
during the test suite (this repo's CI has no Dafny/Z3 binary installed,
by design - see .github/workflows/tests.yml's own comment).

Usage:
    python run_verify_dosage_differential.py
"""

import datetime
import json
import pathlib
import subprocess
import sys

from dosage import calculate_hourly_dose
from dosage_differential_vectors import VECTORS

HERE = pathlib.Path(__file__).parent
DRIVER = HERE / "dosage_differential_driver.dfy"


def _dafny_version() -> str:
    result = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (result.stdout.strip() or result.stderr.strip())


def _run_dafny_driver() -> dict:
    """Runs the driver, captures raw output verbatim, returns {vector_id:
    dafny_output_string} parsed from its "id|dose" lines. The parsed
    dose stays a string here deliberately - comparison against Python's
    output happens in main(), not here, so this function's own
    responsibility (run + capture + parse) stays separate from the
    comparison policy."""
    cmd = ["dafny", "run", str(DRIVER)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    raw_output = (proc.stdout or "") + (proc.stderr or "")
    (HERE / "raw_dafny_differential_output.txt").write_text(raw_output)

    manifest = {
        "tool": "dafny",
        "tool_version": _dafny_version(),
        "command": cmd,
        "exit_code": proc.returncode,
        "started_utc": started,
        "target": str(DRIVER.relative_to(HERE)),
    }
    (HERE / "run_manifest_dafny_differential.json").write_text(json.dumps(manifest, indent=2))

    if proc.returncode != 0:
        raise RuntimeError(
            f"dafny run failed (exit {proc.returncode}); see raw_dafny_differential_output.txt"
        )

    dafny_outputs = {}
    for line in proc.stdout.splitlines():
        if "|" not in line:
            continue
        vector_id, _, dose_text = line.partition("|")
        dafny_outputs[vector_id] = dose_text.strip()
    return dafny_outputs


def main() -> None:
    dafny_outputs = _run_dafny_driver()

    results = []
    all_matched = True
    for vector in VECTORS:
        vector_id = vector["id"]
        python_dose = calculate_hourly_dose(
            weight_kg=70.0,  # unused precondition-only guard, see dosage.py
            concentration_mg_per_ml=vector["concentration_mg_per_ml"],
            infusion_rate_ml_per_hr=vector["infusion_rate_ml_per_hr"],
            max_safe_dose_mg_per_hr=vector["max_safe_dose_mg_per_hr"],
        )
        dafny_output_text = dafny_outputs.get(vector_id)
        if dafny_output_text is None:
            raise RuntimeError(f"dafny run produced no output line for vector {vector_id!r}")
        dafny_dose = float(dafny_output_text)
        matched = python_dose == dafny_dose
        all_matched = all_matched and matched
        results.append(
            {
                "id": vector_id,
                "inputs": {
                    k: v
                    for k, v in vector.items()
                    if k not in ("id", "note")
                },
                "note": vector["note"],
                "python_dose": python_dose,
                "dafny_dose_raw_text": dafny_output_text,
                "dafny_dose": dafny_dose,
                "matched": matched,
            }
        )

    output = {
        "all_matched": all_matched,
        "vector_count": len(results),
        "results": results,
    }
    (HERE / "differential_test_results.json").write_text(json.dumps(output, indent=2) + "\n")
    print(f"all_matched={all_matched}; {len(results)} vectors compared")
    if not all_matched:
        sys.exit(1)


if __name__ == "__main__":
    main()
