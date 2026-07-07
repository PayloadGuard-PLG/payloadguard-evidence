# Phase C, Gate C4: real capture of dosage_stp_suite_against_underconstrained.dfy
# - the same REJECT lemmas run against the PRESERVED ORIGINAL weak spec.
# Expected to FAIL for real (a genuinely negative capture, same
# discipline as dosage_broken.dfy) - this is the mechanized proof that
# Gate C4's methodology actually caught a real gap, not a synthetic one.
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage_stp_suite_against_underconstrained.dfy"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    cmd = ["dafny", "verify", str(TARGET)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_dafny_output_stp_suite_against_underconstrained.txt").write_text(
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
    (HERE / "run_manifest_dafny_stp_suite_against_underconstrained.json").write_text(json.dumps(manifest, indent=2))
    print(f"captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
