# Gate C4 honesty exhibit: capture runner for
# drug_interaction_checker_stp_suite_against_underconstrained.dfy,
# mirroring renal_adjustment's exact discipline for the same purpose.
# Expected to FAIL (nonzero exit, real errors) -- that failure is the
# evidence, captured verbatim, not smoothed over.
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "drug_interaction_checker_stp_suite_against_underconstrained.dfy"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    cmd = ["dafny", "verify", str(TARGET)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_dafny_output_ddi_stp_suite_against_underconstrained.txt").write_text(
        (proc.stdout or "") + (proc.stderr or "")
    )
    manifest = {
        "tool": "dafny",
        "tool_version": _version(),
        "command": cmd,
        "exit_code": proc.returncode,
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "expected_outcome": "FAILS -- honesty exhibit, real error capture, not smoothed over",
    }
    (HERE / "run_manifest_dafny_ddi_stp_suite_against_underconstrained.json").write_text(
        json.dumps(manifest, indent=2)
    )
    print(f"captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
