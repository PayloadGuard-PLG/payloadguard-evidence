# Phase C, Gate C4: real capture of the PRESERVED ORIGINAL (under-
# constrained) dosage_underconstrained.dfy spec, verified standalone.
# Mirrors run_verify_dafny.py's discipline. Expected to verify cleanly on
# its own (the bug is a spec weakness, not a verification failure) - the
# gap only shows up when an STP suite tries to exclude a wrong candidate
# value; see run_verify_dafny_stp_suite_against_underconstrained.py.
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage_underconstrained.dfy"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    cmd = ["dafny", "verify", str(TARGET)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_dafny_output_underconstrained.txt").write_text(
        (proc.stdout or "") + (proc.stderr or "")
    )
    manifest = {
        "tool": "dafny",
        "tool_version": _version(),
        "command": cmd,
        "exit_code": proc.returncode,
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
    }
    (HERE / "run_manifest_dafny_underconstrained.json").write_text(json.dumps(manifest, indent=2))
    print(f"captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
