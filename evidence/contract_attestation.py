"""Tier 3, the authoring migration: contract ratification (the human half of
Component F, mechanized as far as a machine honestly can). Template v2:
defeater-based (eliminative) ratification.

Component F (`evidence/frozen_contract.py`) freezes each spec's contract
surface and mechanically proves no automated contributor altered it. But the
frozen baselines themselves were extracted from LLM-drafted, human-reviewed
specs - the gate guards the boundary going forward without changing where the
contracts came from. This module is the migration's mechanism: a per-example
CONTRACT RATIFICATION artifact through which the human reviewer examines
every frozen declaration against the sources and formally ADOPTS the contract
as their own specification of the requirement.

What that act can and cannot claim, stated plainly: ratification earns the
label **human-ratified**, not "human-authored" - no artifact can rewrite who
drafted the spec, and this repo does not pretend otherwise. A spec authored
under the forward workflow (human freezes the contract BEFORE any automated
drafter touches the file - see OPERATIONS_MANUAL section 6.2a) earns strong
provenance natively; ratification is the honest upgrade available to the four
already-built examples.

**Why v2 is eliminative, not assent-based.** v1 asked one passive question
per declaration (`Adopted? yes/no`). The empirical reading-technique
literature (Basili et al.: scenario/defect-focused reading beat both ad hoc
and checklist reading; checklist reading was no better than ad hoc) says a
passive checkbox is close to no structure at all - what helps is ACTIVE
guidance, the reviewer *producing* something. The assurance-case literature
gives the thing to produce: candidate DEFEATERS (Goodenough, Weinstock &
Klein, *Eliminative Argumentation*, SEI/CMU 2015; Bloomfield & Rushby,
*Assurance 2.0*, arXiv:2405.15800 - confidence is earned by raising doubts
and eliminating them, and an unresolved doubt blocks case closure, which is
structurally what `_PENDING_` gating already does here). The three defeater
classes are distributed to the layer that already owns each:

  - **Undermining** (are the grounds wrong - mistyped constant, bad source?)
    is Component D's blind constant review, already folded in - not repeated
    per declaration.
  - **Rebutting** (does this clause assert the wrong thing?) is the new
    per-declaration `Wrong-if` production field.
  - **Undercutting** (could every clause hold and the requirement still be
    violated?) is the new per-declaration `Gap-if` production field.

The artifact auto-assembles the context the judgment needs (mapped
requirement text from the traceability matrix, source-cited literals with
their verbatim quotes, and a warning banner where the recorded Dafny proof is
definitional - i.e. where mechanical evidence is weakest and reviewer doubt
matters most), so the machine does all lookup and the human performs only the
judgment no machine can. The eliminative ORDER (produce defeaters, eliminate
or sustain them, only then adopt) is discipline stated in prose; the gate
checks structure only - mechanical gates never judge the quality of a human
verdict.

The mechanism otherwise mirrors Component D
(`evidence/source_anchored_review.py`): this module builds the template and
mechanically checks its STRUCTURE; it never performs the ratification - the
sign-off is a human act, and a freshly generated artifact is PENDING
(structurally valid, not yet ratified). The structure gate passes on PENDING;
whether a *completed* ratification exists is a separate signal
(`attestation_complete`), reported but never asserted.

What makes ratification durable rather than a one-time signature is the
HASH BINDING: the artifact records the sha256 of the exact canonical frozen
contract it ratifies. If the contract later changes in any way, the recorded
hash no longer matches the current manifest and the structure gate reports the
attestation stale (`hash_current=False`) - a signed adoption can never
silently outlive the contract it adopted. Requirement text is bound
differently but to the same effect: each mapped row's verbatim
`requirement_text` is expected content in its declaration's section, so a
requirement-text change flags the artifact structurally stale even though the
contract hash (which binds only the contract surface) still matches - a
ratification adopts a clause<->requirement correspondence, and if the
requirement changes, the adoption must be redone.

Ratification also FOLDS IN the Component D blind constant review: an
example's attestation is only `attestation_complete` when its
`source_anchored_review_*.md` is itself review-complete. The two halves of
the human act - "the constants transcribe the sources" (blind, per-constant)
and "the clauses mean what the requirement means" (per-declaration
production + adoption below) - are mechanically linked, so a contract cannot
read as ratified while its constants' source review is still pending.
"""

import hashlib
import json
import pathlib
import re

import yaml

from evidence.frozen_contract import load_manifest
from evidence.literal_citation import spec_literals
from evidence.source_anchored_review import PENDING

_HEADER_FIELDS = ("Reviewer:", "Date:", "Attestation", "Adoption:", "Status:")
# Every per-declaration production/verdict field the checker requires in each
# declaration's own section (not globally - a field surviving in one section
# must not mask its deletion from another). Matched on the FULL bold marker
# string, not the bare word: the Adopted line's own prose mentions "Wrong-if
# and Gap-if" unbolded, so a bare-word match would let a gutted Wrong-if field
# pass on that prose (caught while building the tamper test, not by
# inspection). (marker, report_label) pairs.
_PER_DECL_FIELDS = (
    ("**Wrong-if (rebutting)?**", "Wrong-if"),
    ("**Gap-if (undercutting)?**", "Gap-if"),
    ("**Adopted?**", "Adopted"),
)

# The artifact's dedicated recorded-hash field, matched strictly (anchored to
# its own line, exactly 64 hex chars). The checker compares THIS recorded
# value against the current manifest's hash - never an unanchored "is the
# current hash somewhere in the file" search, which could be satisfied by
# pasting the current hash anywhere while the recorded field stays stale (the
# same global-substring bypass class PR #71 fixed in Component D's checker).
_HASH_LINE_RE = re.compile(r"^- Contract hash \(sha256\): `([0-9a-f]{64})`$", re.MULTILINE)

_ATTESTATION = (
    "I am a human reviewer, and not the system that drafted this spec "
    "(drafter != checker)."
)
_ADOPTION = (
    "Having examined every frozen declaration below against the primary "
    "sources, I adopt this contract as my own specification of the "
    "requirement (human-ratified)."
)

_DEFINITIONAL_BANNER = (
    "> ⚠ **Definitional proof** — the recorded Dafny evidence for this "
    "declaration proves a postcondition that restates the definition "
    "(tautology by reflexivity). The proof certifies totality/type-safety/"
    "exhaustiveness only; independent meaning rests entirely on this "
    "ratification. Weight your Wrong-if / Gap-if accordingly."
)


def contract_hash(manifest):
    """Stable sha256 over the canonical frozen-contract manifest. Any change
    to the contract surface - a clause, a datatype constructor, a signature,
    even adding a declaration - changes this hash, which is what binds a
    signed attestation to the exact contract it ratified."""
    canonical = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _decl_marker(decl):
    """The per-declaration heading `build_attestation` emits - unique per
    declaration (names are unique in a spec), so a dropped block is always
    caught, mirroring source_anchored_review's per-literal marker fix."""
    return f"### {decl['kind']} `{decl['name']}`"


# ------------------------------------------------- auto-assembly (pure data)

def _row_locations(row):
    """Every code_location a matrix row carries: the row's own plus each
    evidence entry's. The evidence level MATTERS: dosage's row-level
    code_location names the Python implementation (dosage.py::
    calculate_hourly_dose) and three renal functions appear only at evidence
    level - matching on the row level alone would falsely mark those
    declarations unmapped (verified against the real committed matrices, a
    correction to the v2 design spec's row-only rule)."""
    locations = []
    if row.get("code_location"):
        locations.append(row["code_location"])
    for e in row.get("evidence") or []:
        if e.get("code_location"):
            locations.append(e["code_location"])
    return locations


def _matched_rows(decl, matrix, spec_name):
    """Matrix rows linked to `decl`: any row- or evidence-level code_location
    equal to '{spec_name}::{decl name}' exactly. The spec-file constraint
    stops an implementation-file location (dosage.py::...) from ever
    matching. Sorted by requirement_id for deterministic rendering."""
    target = f"{spec_name}::{decl['name']}"
    rows = [r for r in matrix["rows"] if target in _row_locations(r)]
    return sorted(rows, key=lambda r: r["requirement_id"])


def _is_definitional(decl, matrix, spec_name):
    """True iff any evidence entry TARGETING THIS DECLARATION (its own
    code_location, not merely its row's) records proof_content
    'definitional'. Rows mix proof_content across declarations (renal's
    REQ-RENAL-2 carries definitional SelectFormula alongside property
    CockcroftGaultCrClMlPerMin in one row - verified against the committed
    matrix), so keying the banner on the row would falsely flag
    property-proof declarations; a precision correction to the v2 design
    spec's any-evidence-in-row rule."""
    target = f"{spec_name}::{decl['name']}"
    for row in matrix["rows"]:
        for e in row.get("evidence") or []:
            if e.get("code_location") == target and e.get("proof_content") == "definitional":
                return True
    return False


def _surface_text(decl):
    """The declaration's whole frozen surface as one string, for literal
    extraction."""
    if "definition" in decl:
        return decl["definition"]
    pieces = [decl["signature"]] + list(decl.get("requires", [])) + list(decl.get("ensures", []))
    if decl.get("body"):
        pieces.append(decl["body"])
    return " ".join(pieces)


def _decl_source_literals(decl, citations):
    """Source-cited literals occurring in this declaration's frozen surface:
    [(literal, source, quote)], sorted by literal key (string sort -
    deterministic). Only kind 'source' entries render - structural/
    design_decision literals are Component C/D territory. Reuses the public
    `spec_literals` extractor (comment-stripping is a no-op on canonical
    surface text)."""
    present = set(spec_literals(_surface_text(decl)))
    out = []
    for key in sorted(citations):
        entry = citations[key]
        if key in present and entry.get("kind") == "source":
            out.append((key, entry["source"], entry["quote"]))
    return out


# ------------------------------------------------------------- the template

def build_attestation(spec_name, manifest, review_name, matrix, citations):
    """Render a PENDING v2 (defeater-based) ratification artifact for
    `spec_name` from its frozen-contract `manifest`, folding in the Component
    D review named `review_name`. `matrix` is the parsed
    traceability_matrix.a.json dict (variant A); `citations` the parsed
    literal_citations.yaml `literals` dict. Both passed as DATA, not paths -
    this function stays I/O-free like check_attestation."""
    lines = [
        f"# Contract ratification — `{spec_name}`",
        "",
        "Generated by `evidence/contract_attestation.py`. This is the human "
        "half of Component F (Tier 3, authoring migration): the reviewer "
        "works ELIMINATIVELY through every frozen declaration — producing "
        "candidate defeaters and eliminating them — and formally adopts the "
        "contract. Completing this earns the label **human-ratified** — not "
        "\"human-authored\"; see the module docstring for exactly what this "
        "act can and cannot claim.",
        "",
        f"- Frozen contract: `frozen_contract.yaml`",
        f"- Contract hash (sha256): `{contract_hash(manifest)}`",
        f"- Blind constant review (folded in): `{review_name}` — this "
        "ratification is not complete until that review is itself complete "
        "(no `_PENDING_` left in it).",
        "- Template: v2 (defeater-based ratification; see module docstring)",
        "",
        "## Sign-off",
        "",
        f"- Reviewer: {PENDING}",
        f"- Date: {PENDING}",
        f"- Attestation (drafter != checker): {PENDING} — \"{_ATTESTATION}\"",
        f"- Adoption: {PENDING} — \"{_ADOPTION}\"",
        f"- Status: {PENDING} (a freshly generated artifact is PENDING — "
        "structurally valid, not yet ratified)",
        "",
        "## How to complete this ratification",
        "",
        f"First complete `{review_name}` (the blind, source-anchored constant "
        "review — this is where doubts about the *constants and sources "
        "themselves* are raised and eliminated; do not repeat them below). "
        "Then, for each declaration below: read the mapped requirement and "
        "the frozen contract surface side by side, and work eliminatively — "
        "confidence is earned by raising doubts and eliminating them, not by "
        "assent. Record in **Wrong-if** the most credible concrete condition "
        "under which a clause here would assert the wrong thing (boundary "
        "direction, inequality strictness, unit, operand order), and how you "
        "eliminated it — or, if you could not eliminate it, stop: the "
        "contract needs changing, not ratifying. Record in **Gap-if** the "
        "most credible way every clause here could hold while the requirement "
        "is still violated (missing case, bound too weak, vacuous guard), and "
        "how you eliminated it. Declarations flagged **definitional proof** "
        "deserve your strongest doubt: the proof certifies nothing beyond the "
        "definition itself, so independent meaning rests entirely on this "
        "ratification. Only then record **Adopted?**. Fill the sign-off above "
        "and replace every `_PENDING_`. If the spec's contract ever changes, "
        "the hash above goes stale and this ratification must be redone "
        "against the new contract — the structure gate enforces that "
        "mechanically.",
        "",
        "## Frozen declarations",
        "",
    ]
    for decl in manifest["declarations"]:
        lines += [_decl_marker(decl), ""]
        # requirement block (auto-assembled; deterministic - never inline
        # generated_utc/tool versions, only requirement_id + verbatim text)
        rows = _matched_rows(decl, matrix, spec_name)
        if rows:
            lines.append("**Requirement (auto-assembled from `traceability_matrix.a.json`):**")
            for row in rows:
                lines.append(f"> **{row['requirement_id']}** — {row['requirement_text']}")
            lines.append("")
        else:
            lines += [
                "**Requirement (auto-assembled):** none mapped in "
                "`traceability_matrix.a.json` (type declaration or "
                "helper/internal — confirm this is expected as part of "
                "Gap-if).",
                "",
            ]
        if _is_definitional(decl, matrix, spec_name):
            lines += [_DEFINITIONAL_BANNER, ""]
        # frozen surface - byte-identical rendering to v1
        if "definition" in decl:
            lines += ["```", decl["definition"], "```", ""]
        else:
            lines += ["```", decl["signature"], "```", ""]
            for kw in ("requires", "ensures"):
                for clause in decl.get(kw, []):
                    lines.append(f"- {kw} `{clause}`")
            if "body" in decl:
                lines.append(f"- body (spec) `{decl['body']}`")
            lines.append("")
        lits = _decl_source_literals(decl, citations)
        if lits:
            lines.append("**Sourced literals in this declaration (auto-assembled from `literal_citations.yaml`):**")
            for lit, source, quote in lits:
                lines.append(f"> `{lit}` — {source}: \"{quote}\"")
            lines.append("")
        lines += [
            f"**Wrong-if (rebutting)?** {PENDING} (state the concrete "
            "condition under which a clause above would assert the wrong "
            "thing relative to the requirement, and how it was eliminated — "
            "or sustained, which blocks adoption)",
            "",
            f"**Gap-if (undercutting)?** {PENDING} (state how every clause "
            "above could hold while the requirement is still violated, and "
            "how it was eliminated — or sustained, which blocks adoption)",
            "",
            f"**Adopted?** {PENDING} (yes / no + notes — recorded only after "
            "Wrong-if and Gap-if are eliminated; does this declaration mean "
            "what the requirement means?)",
            "",
        ]
    return "\n".join(lines)


# --------------------------------------------------------------- the checker

def _decl_sections(markdown, manifest):
    """Split `markdown` into per-declaration sections keyed by name: each
    section runs from a declaration's unique marker to the next present
    marker (or end of document). Declarations whose marker is absent are
    simply not in the result - the caller reports them as missing blocks."""
    found = []
    for decl in manifest["declarations"]:
        idx = markdown.find(_decl_marker(decl))
        if idx != -1:
            found.append((idx, decl["name"]))
    found.sort()
    sections = {}
    for i, (idx, name) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(markdown)
        sections[name] = markdown[idx:end]
    return sections


def _expected_content(decl):
    """The frozen-contract strings a declaration's section must display for
    the human to actually be adopting them: the datatype definition, or the
    signature plus every requires/ensures clause and the spec body."""
    if "definition" in decl:
        return [("definition", decl["definition"])]
    pieces = [("signature", decl["signature"])]
    for kw in ("requires", "ensures"):
        pieces += [(kw, clause) for clause in decl.get(kw, [])]
    if "body" in decl:
        pieces.append(("body", decl["body"]))
    return pieces


def check_attestation(markdown, manifest, review_markdown, matrix=None):
    """Mechanically check a ratification artifact's STRUCTURE (never its
    human verdicts). Returns a report dict:
      - recorded_hash:     the hash parsed from the artifact's dedicated
                           field (None if absent or ambiguous)
      - hash_current:      that RECORDED hash equals the CURRENT frozen
                           manifest's hash - parsed and compared, never an
                           unanchored search, so pasting the current hash
                           elsewhere cannot mask a stale recorded field.
                           False means the contract changed after this
                           artifact was generated/signed (stale ratification)
      - missing_fields:    required sign-off field markers absent
      - missing_blocks:    frozen declarations whose per-declaration block
                           (unique marker) is absent from the artifact
      - missing_content:   "(name): (piece)" entries where a declaration's
                           section is present but no longer displays the
                           frozen content the human is adopting (definition/
                           signature/each clause/spec body), one of its own
                           production/verdict fields (Adopted/Wrong-if/
                           Gap-if), or - when `matrix` is provided - the
                           FULL rendered requirement line of a mapped row
                           ("> **REQ-ID** — text", ID and verbatim text
                           paired, reported "(name): requirement (REQ-ID)")
                           or a definitional declaration's warning banner
                           ("(name): definitional banner"). The requirement
                           check is deliberate: a requirement-text change
                           flags the artifact structurally stale even though
                           the contract hash (which binds only the contract
                           surface) still matches - a ratification adopts a
                           clause<->requirement correspondence, so if the
                           requirement changes, the adoption must be redone.
                           When `matrix` is None the requirement checks are
                           skipped (pure three-argument form for unit tests
                           of other properties).
      - review_complete:   the folded-in Component D review has no _PENDING_
      - structure_ok:      True iff hash_current and nothing missing
                           (PENDING is fine - same posture as Component D)
      - attestation_complete: True iff no _PENDING_ remains in the artifact
                           AND review_complete (the folded-in requirement) -
                           reported, never asserted by the structure gate
    """
    hash_matches = _HASH_LINE_RE.findall(markdown)
    recorded_hash = hash_matches[0] if len(hash_matches) == 1 else None
    hash_current = recorded_hash == contract_hash(manifest)

    missing_fields = [f for f in _HEADER_FIELDS if f not in markdown]
    if recorded_hash is None:
        missing_fields.append("Contract hash")

    missing_blocks = [
        d["name"] for d in manifest["declarations"] if _decl_marker(d) not in markdown
    ]
    sections = _decl_sections(markdown, manifest)
    missing_content = []
    spec_name = manifest.get("spec", "")
    for decl in manifest["declarations"]:
        section = sections.get(decl["name"])
        if section is None:
            continue  # already reported in missing_blocks
        for piece, text in _expected_content(decl):
            if text not in section:
                missing_content.append(f"{decl['name']}: {piece}")
        for marker, label in _PER_DECL_FIELDS:
            if marker not in section:
                missing_content.append(f"{decl['name']}: {label} field")
        if matrix is not None:
            for row in _matched_rows(decl, matrix, spec_name):
                # require the FULL rendered line (ID + verbatim text paired),
                # not the text alone - otherwise the requirement ID marker
                # could be removed or altered while the text survives,
                # degrading the clause<->requirement binding unnoticed
                rendered = f"> **{row['requirement_id']}** — {row['requirement_text']}"
                if rendered not in section:
                    missing_content.append(
                        f"{decl['name']}: requirement {row['requirement_id']}"
                    )
            if _is_definitional(decl, matrix, spec_name) and _DEFINITIONAL_BANNER not in section:
                # the banner is a safety signal (it directs reviewer doubt
                # where mechanical evidence is weakest); its deletion from a
                # signed artifact must not pass the gate
                missing_content.append(f"{decl['name']}: definitional banner")

    review_complete = PENDING not in review_markdown
    return {
        "recorded_hash": recorded_hash,
        "hash_current": hash_current,
        "missing_fields": missing_fields,
        "missing_blocks": missing_blocks,
        "missing_content": missing_content,
        "review_complete": review_complete,
        "structure_ok": hash_current
        and not (missing_fields or missing_blocks or missing_content),
        "attestation_complete": (PENDING not in markdown) and review_complete,
    }


# ------------------------------------------------------------------ file I/O

def load_matrix(matrix_path):
    return json.loads(pathlib.Path(matrix_path).read_text(encoding="utf-8"))


def load_citations(citations_path):
    return yaml.safe_load(pathlib.Path(citations_path).read_text(encoding="utf-8"))["literals"]


def check_example(attestation_path, manifest_path, review_path, matrix_path):
    """Convenience wrapper: read a committed ratification artifact, its
    frozen-contract manifest, its folded-in Component D review, and the
    traceability matrix, and structure-check the artifact. Pure verification
    lives in `check_attestation`; this only does file I/O."""
    markdown = pathlib.Path(attestation_path).read_text(encoding="utf-8")
    manifest = load_manifest(manifest_path)
    review_markdown = pathlib.Path(review_path).read_text(encoding="utf-8")
    return check_attestation(markdown, manifest, review_markdown, matrix=load_matrix(matrix_path))
