"""R2 structural rule as pytest: PROVEN must never appear as a realized
strength in any evidence record or rendered strength cell of a generated
matrix. Replaces the Phase A grep audit. The corruption case builds a
deliberately bad record IN MEMORY only — no corrupted fixture is committed.
"""

import copy
import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.render.matrix_variants import assert_no_realized_proven  # noqa: E402

ARTIFACTS = [
    "examples/dosage_calculator/traceability_matrix.a.json",
    "examples/dosage_calculator/traceability_matrix.b.json",
    "examples/dosage_calculator/traceability_matrix.symbolic.json",
    "examples/dosage_calculator/traceability_matrix.concrete.json",
]


@pytest.mark.parametrize("artifact", ARTIFACTS)
def test_committed_variant_artifacts_pass_structural_check(artifact):
    matrix = json.loads((REPO_ROOT / artifact).read_text())
    assert_no_realized_proven(matrix)  # must not raise on real data


def test_corrupted_in_memory_record_fails_structural_check():
    matrix = json.loads((REPO_ROOT / ARTIFACTS[0]).read_text())
    corrupted = copy.deepcopy(matrix)
    corrupted["rows"][0]["evidence"][0]["strength"] = "PROVEN"
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(corrupted)


def test_corrupted_in_memory_row_cell_fails_structural_check():
    matrix = json.loads((REPO_ROOT / "examples/dosage_calculator/traceability_matrix.b.json").read_text())
    corrupted = copy.deepcopy(matrix)
    corrupted["rows"][0]["strength"] = "PROVEN"
    with pytest.raises(AssertionError, match="realized strength PROVEN"):
        assert_no_realized_proven(corrupted)
