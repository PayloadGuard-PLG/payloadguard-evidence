# Phase C, Gate C3, vector 3: a real, deliberately resource-starved capture
# of the SAME dosage.dfy spec Gate C1 verified cleanly. `--resource-limit=1`
# forces Dafny to abandon verification before it completes, producing a
# summary line that reports "0 errors" alongside an "N out of resource"
# suffix - a real, reproducible instance of the exact false-zero class
# named in KNOWN_LIMITATIONS.md Gate C3 vector 3 ("not just '0 errors'
# appearing somewhere in output"). Confirmed empirically: Dafny 4.11.0
# still exits nonzero (4) in this case, so Gate C1's exit-code check alone
# already refuses it; this capture exists so the summary-line hardening in
# evidence/dafny_adapter.py has a real committed fixture to regress against,
# not just a synthetic in-memory string.
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage.dfy"


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    cmd = ["dafny", "verify", "--resource-limit=1", str(TARGET)]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_dafny_output_resource_limited.txt").write_text(
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
    (HERE / "run_manifest_dafny_resource_limited.json").write_text(json.dumps(manifest, indent=2))
    print(f"captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
