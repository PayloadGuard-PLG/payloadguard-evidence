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
"""

import re

from evidence.model import Strength, VerificationResult

_SUMMARY_RE = re.compile(
    r"Dafny program verifier finished with (\d+) verified, (\d+) errors?"
)


def parse_dafny_capture(raw_output: str, manifest: dict) -> VerificationResult:
    """Parse one committed Dafny capture. Raises SystemExit (Tier 1,
    refuses rather than guesses) on any non-clean signal: nonzero exit,
    no summary line, or a nonzero error count in that summary."""
    target = manifest["target"]

    if manifest["exit_code"] != 0:
        raise SystemExit(
            f"dafny capture {target!r} does not report a clean pass "
            f"(exit_code={manifest['exit_code']}); refusing to bind"
        )

    match = _SUMMARY_RE.search(raw_output)
    if match is None:
        raise SystemExit(
            f"dafny capture {target!r} has no verifier summary line; "
            "cannot confirm verification actually completed "
            "(verifier_completion_status would be 'incomplete') - refusing to bind"
        )

    verified_count, error_count = int(match.group(1)), int(match.group(2))
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
