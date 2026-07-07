# Gate C1 (Phase C): capture runner for the Dafny spec, mirroring
# run_verify.py's discipline exactly - verbatim stdout+stderr, the exact
# command argv, exit code, and ISO-8601 UTC timestamp. No bounds block:
# unlike CrossHair's bounded symbolic search, Dafny's SMT proof search has
# no declared/effective envelope in this repo's model - completion is
# judged from the captured output itself (see evidence/dafny_adapter.py).
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage.dfy"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    cmd = ["dafny", "verify", str(TARGET)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_dafny_output.txt").write_text(
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
    (HERE / "run_manifest_dafny.json").write_text(json.dumps(manifest, indent=2))
    print(f"captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
