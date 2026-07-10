# Gate C1: capture runner for the drug-interaction-checker Dafny spec,
# mirroring examples/renal_adjustment/run_verify_renal.py's discipline
# exactly - verbatim stdout+stderr, the exact command argv, exit code,
# and ISO-8601 UTC timestamp.
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "drug_interaction_checker.dfy"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    cmd = ["dafny", "verify", str(TARGET)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_dafny_output_ddi.txt").write_text(
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
    (HERE / "run_manifest_dafny_ddi.json").write_text(json.dumps(manifest, indent=2))
    print(f"captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
