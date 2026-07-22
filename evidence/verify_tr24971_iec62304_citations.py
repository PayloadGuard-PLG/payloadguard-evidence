"""One-off verification manifest: every quoted/paraphrased claim this
assistant made about ISO/TR 24971:2020 and IEC 62304:2006+AMD1:2015
during the 2026-07-22 session, checked mechanically against the actual
committed sources via evidence/citation_gate.py.

Why this exists: the session's TR 24971 / IEC 62304 findings were
reported in prose (with page/clause numbers), not as a checkable
artifact. That's exactly the gap citation_gate.py exists to close - see
its own module docstring for the two prior fabrication events that
motivated it. This script makes the same claims re-checkable by anyone
(including a different agent, e.g. Claude Code) without re-deriving
them or trusting the original prose.

Source text extraction method (reproducible, no external binaries):
- TR 24971 is read from the committed .docx directly, by unzipping it
  and concatenating every <w:t> run in word/document.xml. Every claim
  below is a verbatim *prose* phrase - none quotes a clause number - so
  the docx's own text layer is sufficient and authoritative. An earlier
  draft of this script rendered the docx to PDF via LibreOffice first,
  on the theory that Word auto-numbering was needed; it isn't (no claim
  cites an auto-number), and the LibreOffice dependency made the script
  unrunnable where LibreOffice can't load the file. Dropped entirely.
- The two PDFs (IEC 62304, ISO 14971 preview) are read via PyMuPDF
  (fitz) page.get_text(), concatenated across all pages.

Run: python3 evidence/verify_tr24971_iec62304_citations.py
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evidence.citation_gate import CitationClaim, verify_citations  # noqa: E402

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required to extract source text: pip install pymupdf --break-system-packages")
    sys.exit(1)


def _extract_pdf_text(pdf_path: pathlib.Path) -> str:
    """Concatenate get_text() across every page via PyMuPDF."""
    doc = fitz.open(str(pdf_path))
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def _extract_docx_text(docx_path: pathlib.Path) -> str:
    """Concatenate every text run in a .docx's word/document.xml.

    No external binary (no LibreOffice): a .docx is a zip, and the body
    text lives in <w:t> elements. This is sufficient for verbatim prose
    phrases - the only kind of claim this manifest checks - and it runs
    anywhere Python does."""
    import zipfile
    import xml.etree.ElementTree as ET

    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    with zipfile.ZipFile(docx_path) as zf:
        root = ET.fromstring(zf.read("word/document.xml").decode("utf-8", "ignore"))
    paragraphs = (
        "".join(t.text or "" for t in para.iter(ns + "t"))
        for para in root.iter(ns + "p")
    )
    return "\n".join(paragraphs)


TR24971_DOCX = REPO_ROOT / "sources" / "CEN-ISO-TR-24971-2020-E.docx"
IEC62304_PDF = REPO_ROOT / "sources" / "IEC 62304.pdf"
# 7-page publisher preview (Contents, Foreword, Introduction, and Clause
# 1/start-of-3 only) - it does NOT cover Clauses 4-10 or Annexes A-C,
# which is why only one claim below cites it.
ISO14971_PREVIEW_PDF = REPO_ROOT / "sources" / "ISO-14971-2019-E.pdf"


def build_claims() -> list:
    tr24971_text = _extract_docx_text(TR24971_DOCX)
    iec62304_text = _extract_pdf_text(IEC62304_PDF)
    iso14971_preview_text = _extract_pdf_text(ISO14971_PREVIEW_PDF)

    return [
        # --- TR 24971 Annex C.2: three named risk-control approaches ---
        CitationClaim(
            label="TR24971-C2-three-approaches",
            claimed_quote=(
                "reducing risk as low as reasonably practicable, "
                "reducing risk as low as reasonably achievable, or "
                "reducing risk as far as possible without adversely "
                "affecting the benefit-risk ratio"
            ),
            source_text=tr24971_text,
        ),
        # --- TR 24971: severity-alone criteria (appears at both §4.4.5
        # and Annex C.3 - checking the shared sentence once is
        # sufficient to confirm it exists; the two-locations claim is
        # verified separately by grep count, not by this gate) ---
        CitationClaim(
            label="TR24971-severity-alone-criteria",
            claimed_quote=(
                "criteria for situations where the probability of "
                "occurrence of harm cannot be estimated, in which case "
                "the criteria for risk acceptability can be based on "
                "the severity of harm alone"
            ),
            source_text=tr24971_text,
        ),
        # --- TR 24971 Annex C.4: economic practicability + guard clause ---
        CitationClaim(
            label="TR24971-C4-economic-practicability",
            claimed_quote=(
                "Economic practicability refers to the ability to "
                "reduce the risk without making the medical device an "
                "unsound economic proposition"
            ),
            source_text=tr24971_text,
        ),
        CitationClaim(
            label="TR24971-C4-guard-clause",
            claimed_quote=(
                "economic practicability should not be used as a "
                "rationale for the acceptance of unnecessary risk"
            ),
            source_text=tr24971_text,
        ),
        # --- TR 24971 Figure C.1: middle region's real label ---
        CitationClaim(
            label="TR24971-figureC1-middle-region-label",
            claimed_quote="investigate further risk control",
            source_text=tr24971_text,
        ),
        # --- TR 24971 §5.5.3 (main body): "software failure" as an
        # inestimable-probability example, and the severity-alone
        # requirement stated as necessary, not optional ---
        CitationClaim(
            label="TR24971-5.5.3-software-failure-example",
            claimed_quote="software failure",
            source_text=tr24971_text,
        ),
        CitationClaim(
            label="TR24971-5.5.3-necessary-to-evaluate-on-severity-alone",
            claimed_quote=(
                "When the probability of occurrence of harm cannot be "
                "estimated, it is necessary to evaluate the risk on "
                "the basis of the severity of harm alone"
            ),
            source_text=tr24971_text,
        ),
        # --- ISO 14971:2019 (7-page preview): scope claim ---
        CitationClaim(
            label="ISO14971-2019-scope-no-acceptable-risk-levels",
            claimed_quote=(
                "requires manufacturers to establish objective "
                "criteria for risk acceptability but does not "
                "specify acceptable risk levels"
            ),
            source_text=iso14971_preview_text,
        ),
        # --- IEC 62304 §4.3: Class B definition, the repeatedly-cited
        # boundary underlying every S3 severity determination in
        # HAZARD_REGISTER.md / RISK_MANAGEMENT_PLAN.md ---
        CitationClaim(
            label="IEC62304-4.3-class-B-definition",
            claimed_quote="Class B: Non-SERIOUS INJURY is possible",
            source_text=iec62304_text,
        ),
        CitationClaim(
            label="IEC62304-4.3-class-B-full-criteria",
            claimed_quote=(
                "the SOFTWARE SYSTEM can contribute to a HAZARDOUS "
                "SITUATION which results in unacceptable RISK after "
                "consideration of RISK CONTROL measures external to "
                "the SOFTWARE SYSTEM and the resulting possible HARM "
                "is non-SERIOUS INJURY"
            ),
            source_text=iec62304_text,
        ),
    ]


def main() -> int:
    claims = build_claims()
    verdicts = verify_citations(claims)

    not_found = [v for v in verdicts if v.verdict == "NOT_FOUND"]

    print(f"{len(verdicts)} claims checked.\n")
    for v in verdicts:
        marker = "✓ CONFIRMED" if v.verdict == "CONFIRMED" else "✗ NOT_FOUND"
        print(f"[{marker}] {v.label}")
        if v.context:
            print(f"    context: ...{v.context}...")
        if v.verdict == "NOT_FOUND":
            print(f"    {v.caveat}")
        print()

    if not_found:
        print(f"{len(not_found)} claim(s) NOT_FOUND - see caveat above; "
              f"this means 'could not confirm automatically', not "
              f"'disproven'. Check the raw source directly.")
        return 1

    print("All claims CONFIRMED as normalized substrings of their cited source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
