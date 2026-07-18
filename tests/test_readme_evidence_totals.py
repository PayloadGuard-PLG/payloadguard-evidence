"""Guards README.md's evidence-strength totals table against drift.

README.md states hard-coded counts (currently 28 requirements / 20
PROVEN / 1 BOUNDED_CHECKED / 7 GAP) rather than a formula, matching
this repo's existing convention of committing concrete numbers where
they're meaningful (RISK_MANAGEMENT_FINDINGS.md's hazard counts,
DEVLOG.md's per-entry test-pass counts) rather than hiding them behind
indirection. What's mechanically enforced here isn't the number's
existence but its accuracy: every count is recomputed from the real,
committed examples/*/traceability_matrix.a.json files on each run, so a
spec/requirement change that shifts a row's evidence status fails CI
instead of leaving the README's claim silently stale - the same failure
mode PRs #54/#56 fixed for this repo's other hard-coded doc counts.
"""

import json
import pathlib
import re
from collections import Counter

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

EXAMPLES = [
    "dosage_calculator",
    "renal_adjustment",
    "drug_interaction_checker",
    "aeb_kernel",
]

# A row's realized strength is its strongest real evidence entry - GAP
# only when no real evidence entry is present at all (a wholly-GAP row,
# or a row whose only entries are GAP notes for a deferred sub-scope
# alongside no real evidence).
STRENGTH_PRIORITY = ["PROVEN", "BOUNDED_CHECKED", "TESTED", "EXAMPLE_CHECKED", "DECLARED", "GAP"]


def _row_strength(row: dict) -> str:
    present = {ev["strength"] for ev in row.get("evidence", [])}
    for strength in STRENGTH_PRIORITY:
        if strength in present:
            return strength
    return "GAP"


def _real_totals() -> Counter:
    totals: Counter = Counter()
    for name in EXAMPLES:
        matrix_path = REPO_ROOT / "examples" / name / "traceability_matrix.a.json"
        data = json.loads(matrix_path.read_text())
        for row in data["rows"]:
            totals[_row_strength(row)] += 1
    return totals


def test_readme_total_requirement_count_matches_committed_matrices():
    real_total = sum(_real_totals().values())
    readme_text = README_PATH.read_text()

    match = re.search(r"every one of (\d+) formalized\s*\nrequirements", readme_text)
    assert match, (
        "README.md's evidence-totals intro sentence ('every one of N "
        "formalized requirements...') was not found or has been reworded - "
        "update this test's pattern to match, don't just skip the check."
    )
    assert int(match.group(1)) == real_total, (
        f"README.md claims {match.group(1)} total formalized requirements, "
        f"but the committed examples/*/traceability_matrix.a.json files "
        f"show {real_total}. Regenerate the README's totals table."
    )


def test_readme_evidence_strength_table_matches_committed_matrices():
    real_totals = _real_totals()
    readme_text = README_PATH.read_text()

    expected_rows = {
        "PROVEN": r"\| `PROVEN` \| (\d+) \|",
        "BOUNDED_CHECKED": r"\| `BOUNDED_CHECKED` \| (\d+) \|",
        "GAP": r"\| `GAP` \(explicit, named\) \| (\d+) \|",
    }

    for strength, pattern in expected_rows.items():
        match = re.search(pattern, readme_text)
        assert match, (
            f"README.md's evidence-totals table has no matching row for "
            f"{strength!r} (pattern {pattern!r} not found)."
        )
        assert int(match.group(1)) == real_totals.get(strength, 0), (
            f"README.md claims {match.group(1)} {strength} requirements, "
            f"but the committed matrices show {real_totals.get(strength, 0)}. "
            f"Regenerate the README's totals table."
        )


def test_no_realized_strength_is_silently_missing_from_the_readme_table():
    """Every strength this repo's four matrices actually produce must
    appear as its own row - not folded into another number unnoticed."""
    real_totals = _real_totals()
    readme_text = README_PATH.read_text()

    covered = {"PROVEN", "BOUNDED_CHECKED", "GAP"}
    unexpected = set(real_totals) - covered
    assert not unexpected, (
        f"The committed matrices now produce {sorted(unexpected)}, a "
        f"strength not represented in README.md's evidence-totals table - "
        f"add a row for it rather than letting the table go out of sync."
    )
