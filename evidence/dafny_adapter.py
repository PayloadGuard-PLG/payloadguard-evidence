"""Phase C, Gate C1: Dafny capture parser (the "minimal false-zero guard").

Turns a committed Dafny capture (verbatim raw output + run manifest, both
produced by run_verify_dafny.py / run_verify_dafny_broken.py) into a
VerificationResult. This module does NOT bind that result into any
traceability matrix - build_matrix() and every generator script are
untouched. `evidence.render.matrix_variants.assert_no_realized_proven`
still guarantees PROVEN never appears as a realized strength anywhere in
a rendered matrix, and this module cannot change that: producing a
VerificationResult in Python is not the same as it ever reaching a
matrix row. Wiring a Dafny-sourced PROVEN result into the matrix pipeline
is explicitly Gate C2's job (the PROVEN-exclusivity migration, still
unbuilt) - not this one.

False-zero guard (2026-07-06 finding, KNOWN_LIMITATIONS.md Gate C1):
the verifier's own summary line, e.g.
    Dafny program verifier finished with 1 verified, 0 errors
is parsed for its actual error COUNT via regex - never a blind substring
search for "0 errors", which a printed error message could coincidentally
contain, and never a bare exit_code == 0 check, which is exactly the
false-zero bug class this repo has tracked since Phase A
(evidence/model.py's parser note). A capture whose summary line is
missing entirely (a crash, a timeout, or a Dafny subcommand that "did not
attempt verification" - confirmed real behavior of `dafny audit` on some
inputs) is refused, not guessed at.

Phase C, Gate C3 vector 3 hardening (2026-07-07): a real, reproducible
capture (examples/dosage_calculator/raw_dafny_output_resource_limited.txt,
produced by run_verify_dafny_resource_limited.py running the real
dosage.dfy spec under `--resource-limit=1`) shows Dafny 4.11.0 can report
    Dafny program verifier finished with 0 verified, 0 errors, 1 out of resource
- an "errors" count of 0 alongside an incomplete run. Confirmed empirically
that this real capture's exit_code is 4 (nonzero), so the exit-code check
above already refuses it - but the summary-line parser is hardened to
refuse on this signal independently, as defense in depth against ever
relying on exit_code alone (Boogie/Dafny's shared vocabulary for this class
also includes "out of memory" and "timed out" suffixes in the same summary
line, per the installed binary's own strings, though only "out of
resource" was independently reproduced end-to-end this session - all
three are treated identically here). The parser also now refuses if more
than one summary line is found in one capture, rather than silently
trusting the first match - confirmed empirically that a normal
multi-target `dafny verify` invocation still emits exactly one aggregate
summary line, so this only closes a theoretical ambiguity, it does not
change behavior for any real single-target capture in this repo.
"""

import re

from evidence.model import Strength, VerificationResult

_SUMMARY_RE = re.compile(
    r"Dafny program verifier finished with (\d+) verified, (\d+) errors?(.*)"
)
_INCOMPLETE_MARKERS = ("out of resource", "out of memory", "timed out")


def parse_dafny_capture(raw_output: str, manifest: dict) -> VerificationResult:
    """Parse one committed Dafny capture. Raises SystemExit (Tier 1,
    refuses rather than guesses) on any non-clean signal: nonzero exit, no
    summary line, more than one summary line, an incomplete-run marker in
    the summary line's tail, or a nonzero error count in that summary."""
    target = manifest["target"]

    if manifest["exit_code"] != 0:
        raise SystemExit(
            f"dafny capture {target!r} does not report a clean pass "
            f"(exit_code={manifest['exit_code']}); refusing to bind"
        )

    matches = list(_SUMMARY_RE.finditer(raw_output))
    if not matches:
        raise SystemExit(
            f"dafny capture {target!r} has no verifier summary line; "
            "cannot confirm verification actually completed "
            "(verifier_completion_status would be 'incomplete') - refusing to bind"
        )
    if len(matches) > 1:
        raise SystemExit(
            f"dafny capture {target!r} contains {len(matches)} verifier "
            "summary lines; refusing to guess which one is authoritative"
        )

    match = matches[0]
    verified_count, error_count, tail = (
        int(match.group(1)),
        int(match.group(2)),
        match.group(3),
    )

    tail_lower = tail.lower()
    marker = next((m for m in _INCOMPLETE_MARKERS if m in tail_lower), None)
    if marker is not None:
        raise SystemExit(
            f"dafny capture {target!r} reports incomplete verification "
            f"({marker!r} present in the summary line: {tail.strip()!r}); "
            f"refusing to bind a PROVEN result even though the reported "
            f"error count is {error_count} (Gate C3 vector 3: a clean-"
            "looking error count does not mean verification completed)"
        )

    if error_count != 0:
        raise SystemExit(
            f"dafny capture {target!r} reports {error_count} error(s) "
            f"({verified_count} verified); refusing to bind a PROVEN result"
        )

    return VerificationResult(
        method="dafny",
        code_location=target,
        raw_status=f"{verified_count} verified, {error_count} errors",
        strength=Strength.PROVEN,
        run_id=manifest["started_utc"],
        timestamp=manifest["started_utc"],
        verifier_completion_status="completed",
    )
