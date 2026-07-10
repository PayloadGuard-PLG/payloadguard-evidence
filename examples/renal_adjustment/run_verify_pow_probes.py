# Gate 1c Finding 1 (eGFR side) closure evidence: two real probes testing
# whether Dafny/Z3 can express CKD-EPI's fractional-exponent term at all,
# rather than continuing to assert it from general Z3-theory knowledge.
# Mirrors run_verify_renal.py's exact capture discipline (verbatim
# stdout+stderr, exit code, ISO-8601 UTC timestamp).
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
PROBES = [
    ("dafny_pow_expressiveness_probe.dfy", "raw_dafny_output_pow_expressiveness_probe.txt",
     "run_manifest_pow_expressiveness_probe.json"),
    ("dafny_pow_axiom_trap_probe.dfy", "raw_dafny_output_pow_axiom_trap_probe.txt",
     "run_manifest_pow_axiom_trap_probe.json"),
]


def _version():
    r = subprocess.run(["dafny", "--version"], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())


def main():
    version = _version()
    for target_name, output_name, manifest_name in PROBES:
        target = HERE / target_name
        cmd = ["dafny", "verify", str(target)]
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        (HERE / output_name).write_text((proc.stdout or "") + (proc.stderr or ""))
        manifest = {
            "tool": "dafny",
            "tool_version": version,
            "command": cmd,
            "exit_code": proc.returncode,
            "started_utc": started,
            "target": target_name,
        }
        (HERE / manifest_name).write_text(json.dumps(manifest, indent=2))
        print(f"{target_name}: captured; exit_code={proc.returncode}")


if __name__ == "__main__":
    sys.exit(main())
