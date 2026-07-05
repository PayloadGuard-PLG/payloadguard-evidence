# Duplicate of run_verify.py targeting the deliberately broken variant
# (Sample B). Kept as a separate script, per the Phase-A instruction to
# "parameterize TARGET or duplicate the script", so run_verify.py stays
# byte-identical to the reviewed original.
import json, subprocess, sys, datetime, pathlib

HERE = pathlib.Path(__file__).parent
TARGET = HERE / "dosage_broken.py"

def _version():
    r = subprocess.run(["crosshair", "--version"], capture_output=True, text=True)
    if r.returncode == 0:
        return r.stdout.strip() or r.stderr.strip()
    # crosshair-tool 0.0.107 has no --version flag; fall back to package
    # metadata rather than recording the CLI usage error as a version.
    import importlib.metadata
    return "crosshair-tool " + importlib.metadata.version("crosshair-tool")

def main():
    # Turn 2.0 (B1): same reconciliation as run_verify.py — enforce the one
    # enforceable declared bound, record effective_bounds in the manifest.
    cmd = ["crosshair", "check", str(TARGET), "--report_all",
           "--per_condition_timeout", "30"]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    (HERE / "raw_crosshair_output_broken.txt").write_text(
        (proc.stdout or "") + (proc.stderr or "")
    )
    manifest = {
        "tool": "crosshair",
        "tool_version": _version(),
        "command": cmd,
        "exit_code": proc.returncode,
        "started_utc": started,
        "target": str(TARGET.relative_to(HERE)),
        "effective_bounds": {
            "per_condition_timeout_s": 30,
            "enforcement_note": (
                "max_iterations and seed are declared-only in metadata; "
                "crosshair-tool 0.0.107 has no CLI flags to enforce them."
            ),
        },
    }
    (HERE / "run_manifest_broken.json").write_text(json.dumps(manifest, indent=2))
    print(f"captured; exit_code={proc.returncode}")

if __name__ == "__main__":
    sys.exit(main())
