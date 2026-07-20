"""Component D: tests for evidence/source_anchored_review.py - the
source-anchored, blind, logged Gate C6 review.

The module builds the review TEMPLATE and mechanically checks its structure;
it never performs the human sign-off (drafter != checker). So these tests
pin: the generated template is structurally well-formed with every source
quote CONFIRMED, a freshly generated template is PENDING (structure_ok but
not review_complete), the committed renal template matches the generator
(no drift), and a tampered template is caught."""

import pathlib

from evidence.source_anchored_review import (
    PENDING,
    build_review,
    check_example,
    check_structure,
    load_manifest,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
RENAL_DIR = REPO_ROOT / "examples" / "renal_adjustment"
SOURCES = REPO_ROOT / "sources"
RENAL_MANIFEST = RENAL_DIR / "literal_citations.yaml"
RENAL_REVIEW = RENAL_DIR / "source_anchored_review_renal.md"


def _manifest():
    return load_manifest(RENAL_MANIFEST)


def _source_texts(manifest):
    from evidence.source_anchored_review import _source_constants
    return {
        e["source"]: (SOURCES / e["source"]).read_text(encoding="utf-8")
        for _lit, e in _source_constants(manifest)
    }


def test_generated_template_is_structurally_valid_but_pending():
    md = build_review("renal_adjustment.dfy", _manifest())
    report = check_structure(md, _manifest(), _source_texts(_manifest()))
    assert report["structure_ok"] is True
    assert report["missing_fields"] == []
    assert report["missing_quotes"] == []
    assert report["unconfirmed"] == []
    # a freshly generated template is not yet a completed human review
    assert report["review_complete"] is False


def test_committed_renal_review_matches_the_generator_and_passes_structure():
    """No drift between the committed PENDING artifact and the generator, and
    every source quote in it is CONFIRMED present in its actual source."""
    assert RENAL_REVIEW.read_text(encoding="utf-8") == build_review(
        "renal_adjustment.dfy", _manifest()
    )
    report = check_example(RENAL_REVIEW, RENAL_MANIFEST, SOURCES)
    assert report["structure_ok"] is True
    assert report["review_complete"] is False  # PENDING until a human signs off


def test_a_completed_review_reads_as_complete():
    """Replacing every _PENDING_ (what a real reviewer does) flips
    review_complete, without changing structural validity."""
    md = build_review("renal_adjustment.dfy", _manifest())
    completed = md.replace(PENDING, "Dr. A. Reviewer / 2026-07-21 / yes")
    report = check_structure(completed, _manifest(), _source_texts(_manifest()))
    assert report["structure_ok"] is True
    assert report["review_complete"] is True


def test_tampered_template_is_caught():
    manifest = _manifest()
    md = build_review("renal_adjustment.dfy", manifest)
    # (a) a source quote silently removed from the artifact
    dropped = md.replace("> G1 | ≥90 | Normal or high", "> (quote removed)")
    r1 = check_structure(dropped, manifest, _source_texts(manifest))
    assert r1["structure_ok"] is False
    assert "90" in r1["missing_quotes"]
    # (b) a source quote that isn't actually in the source text
    bad_manifest = {k: dict(v) for k, v in manifest.items()}
    bad_manifest["90"]["quote"] = "G1 | this is not in KDIGO at all"
    md2 = build_review("renal_adjustment.dfy", bad_manifest)
    r2 = check_structure(md2, bad_manifest, _source_texts(manifest))
    assert r2["structure_ok"] is False
    assert "90" in r2["unconfirmed"]
