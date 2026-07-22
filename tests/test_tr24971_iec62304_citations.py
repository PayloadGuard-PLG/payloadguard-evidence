"""Live coverage for evidence/verify_tr24971_iec62304_citations.py.

The script is a re-checkable citation manifest: every prose claim this
repo makes about ISO/TR 24971:2020 and IEC 62304:2006+AMD1:2015 is
asserted to be a verbatim substring of the actual committed source
(the TR docx read directly, the two PDFs via PyMuPDF). A script that
can't run is worthless as a verification artifact, so this test runs it
for real and fails if any claim stops matching its source - which is
exactly what would happen if a quote were edited to say something the
standard does not, or a source file were replaced.

Also a regression guard on the source *filename*: the ISO 14971 preview
was committed as `ISO-14691-2019-E.pdf` (a transposed-digit typo) and
renamed to `ISO-14971-2019-E.pdf`; if it ever reverts, the script's
hardcoded path breaks and this test catches it.
"""

import importlib
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# PyMuPDF is a declared dependency (requirements.txt); skip rather than
# error only if a stripped environment somehow lacks it.
pytest.importorskip("fitz")

verify_mod = importlib.import_module(
    "evidence.verify_tr24971_iec62304_citations"
)


def test_iso14971_preview_filename_is_correct():
    """The renamed source must exist and the misnamed one must not."""
    assert verify_mod.ISO14971_PREVIEW_PDF.name == "ISO-14971-2019-E.pdf"
    assert verify_mod.ISO14971_PREVIEW_PDF.exists(), (
        "ISO 14971 preview missing under the corrected name"
    )
    assert not (REPO_ROOT / "sources" / "ISO-14691-2019-E.pdf").exists(), (
        "the transposed-digit typo filename has come back"
    )


def test_all_citations_confirmed():
    """Every claim must still be a verbatim substring of its source."""
    from evidence.citation_gate import verify_citations

    verdicts = verify_citations(verify_mod.build_claims())
    not_found = [v.label for v in verdicts if v.verdict != "CONFIRMED"]
    assert verdicts, "expected a non-empty claim set"
    assert not not_found, f"citations no longer confirmed: {not_found}"


def test_script_main_exits_zero():
    """The script itself runs green end to end."""
    assert verify_mod.main() == 0
