"""Component C of the "PROVEN != meaningful" work (Gate C3, source-fidelity
vector): mechanical literal-to-source citation.

A PROVEN Dafny proof certifies a spec is internally sound, and
`evidence.spec_impl_gap` (Component A) says whether it carries independent
content beyond its own definition - but neither checks that the spec's
NUMBERS faithfully transcribe the source requirement. A single mistyped digit
(145 -> 154) is a silent, unprovable defect: Dafny happily proves a spec built
on the wrong number, and every downstream gate inherits it.

This module closes the *transcription* half of that gap mechanically. Every
numeric literal in a spec's code (comments stripped) must be accounted for by
a citation-manifest entry, classified as exactly one of:

  - `source`  - carries a verbatim `quote` from a named source document,
    checked present in that document's text via
    `evidence.citation_gate.verify_citation` (whose digit-boundary guard
    already stops 145 from matching inside 1450).
  - `structural` - a mathematical/boundary constant (0.0 non-negativity, a
    real/int zero) that transcribes no source requirement. Declared, not
    cited.
  - `design_decision` - a value the spec author chose that the source does
    NOT state (renal's round-half-up 0.5 tie-break, which KDIGO leaves to the
    lab information system). Declared and named, never dressed up as
    source-derived.

Completeness is enforced both ways: no code literal may lack a manifest entry
(an un-accounted-for constant is the exact hole this closes), and no manifest
entry may name a literal absent from the code (a stale citation drifting from
the spec). What this does NOT check is *modeling* fidelity - that decomposing
the requirement into these particular clauses captures its meaning - which
remains the job of the source-anchored human review (Component D).

Deliberately mechanical, like the citation gate it drives: it interprets
nothing, it only checks that an authored quote is present in source text the
caller supplies.
"""

import pathlib
import re

from evidence.citation_gate import CitationClaim, verify_citation

# A numeric literal not glued to an identifier, a dotted member, or another
# number: the negative lookbehind keeps the `1`/`3` in `G1`/`G3a` and the
# minor version in `4.11` (were it in code) from leaking in, and the decimal
# alternative is tried first so `0.0` matches whole, not as `0` then `0`. A
# unary +/- immediately before the digits is folded in afterwards (see
# spec_literals), not here, so binary subtraction isn't mistaken for a sign.
_LITERAL_RE = re.compile(r"(?<![A-Za-z0-9_.])(?:[0-9]+\.[0-9]+|[0-9]+)")

# A char that ENDS an operand: a preceding `-`/`+` after one of these is
# binary arithmetic, not a literal's sign.
_OPERAND_END = ")]"

_KINDS = ("source", "structural", "design_decision")


def strip_comments(source):
    """Dafny source with line (`//`) and block (`/* */`) comments removed -
    so a number that appears only in prose (a date, a citation, a PMID) is
    never mistaken for a spec constant that needs a source.

    Single pass, not two regex substitutions: once inside a `//` line comment
    a `/*` is inert, and once inside a `/* */` block a `//` is inert, so
    stripping one kind before the other can corrupt the other's delimiters
    (e.g. a `//` inside a block comment eating that block's closing `*/`)."""
    out = []
    i, n = 0, len(source)
    while i < n:
        two = source[i:i + 2]
        if two == "//":
            nl = source.find("\n", i)
            i = n if nl == -1 else nl  # keep the newline itself
        elif two == "/*":
            end = source.find("*/", i + 2)
            i = n if end == -1 else end + 2
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


def _with_unary_sign(code, start, literal):
    """Fold a unary +/- immediately before `literal` (at index `start` in
    `code`) into it - but only when the sign is not binary arithmetic, i.e.
    the char before the sign is not an operand-ender (a value, `)`, or `]`).
    So `>= -0.5` yields `-0.5`, while `x - 0.5` and `x-0.5` keep `0.5`."""
    if start == 0 or code[start - 1] not in "+-":
        return literal
    before = code[start - 2] if start >= 2 else ""
    if before and (before.isalnum() or before in "_." or before in _OPERAND_END):
        return literal  # binary arithmetic, not a sign
    return code[start - 1] + literal


def spec_literals(source):
    """Distinct numeric literals in `source`'s CODE (comments stripped), in
    first-appearance order. The literal string is kept verbatim (`0.0` and
    `0` are distinct, `18.0` is not `18`, `-0.5` is not `0.5`) - a citation is
    about the number exactly as written in the spec, sign included."""
    code = strip_comments(source)
    seen = []
    for m in _LITERAL_RE.finditer(code):
        lit = _with_unary_sign(code, m.start(), m.group())
        if lit not in seen:
            seen.append(lit)
    return seen


def _entry_problems(literal, entry):
    """Static shape check on one manifest entry; returns a list of problems."""
    problems = []
    kind = entry.get("kind")
    if kind not in _KINDS:
        problems.append(f"{literal!r}: kind must be one of {_KINDS}, got {kind!r}")
        return problems
    if kind == "source":
        if not entry.get("source"):
            problems.append(f"{literal!r}: kind 'source' needs a 'source' filename")
        if not entry.get("quote"):
            problems.append(f"{literal!r}: kind 'source' needs a verbatim 'quote'")
    else:
        if not entry.get("note"):
            problems.append(f"{literal!r}: kind {kind!r} needs a 'note' saying why")
    return problems


def verify_literal_citations(spec_source, manifest, source_texts):
    """Check every code literal in `spec_source` against `manifest`.

    `manifest`: {literal_string: {"kind": ..., "source": ..., "quote": ...,
    "note": ...}}. `source_texts`: {source_filename: full_text} for every
    source a `source`-kind entry names.

    Returns a report dict:
      - literals:   the code literals found, in order
      - results:    per-literal {literal, kind, verdict, detail}, where
                    verdict is "confirmed" (source quote found in the source
                    text), "declared" (a structural/design_decision entry -
                    accepted as stated, no source to check), "not_found"
                    (source quote absent), "uncited" (no manifest entry), or
                    "malformed" (bad entry shape)
      - uncited:    literals with no manifest entry
      - not_found:  source literals whose quote isn't in the source text
      - stale:      manifest literals absent from the code
      - malformed:  entry-shape problems
      - ok:         True iff uncited, not_found, stale, malformed are all empty
    """
    literals = spec_literals(spec_source)
    lit_set = set(literals)

    results = []
    uncited = []
    not_found = []
    malformed = []

    for lit in literals:
        entry = manifest.get(lit)
        if entry is None:
            uncited.append(lit)
            results.append({"literal": lit, "kind": None, "verdict": "uncited",
                            "detail": "no citation-manifest entry for this constant"})
            continue
        shape = _entry_problems(lit, entry)
        if shape:
            malformed.extend(shape)
            results.append({"literal": lit, "kind": entry.get("kind"),
                            "verdict": "malformed", "detail": "; ".join(shape)})
            continue
        if entry["kind"] != "source":
            results.append({"literal": lit, "kind": entry["kind"], "verdict": "declared",
                            "detail": entry["note"]})
            continue
        src_name = entry["source"]
        if src_name not in source_texts:
            not_found.append(lit)
            results.append({"literal": lit, "kind": "source", "verdict": "not_found",
                            "detail": f"source text {src_name!r} was not provided"})
            continue
        verdict = verify_citation(
            CitationClaim(label=f"{lit} @ {src_name}", claimed_quote=entry["quote"],
                          source_text=source_texts[src_name])
        )
        if verdict.verdict == "CONFIRMED":
            results.append({"literal": lit, "kind": "source", "verdict": "confirmed",
                            "detail": f"quote found in {src_name}"})
        else:
            not_found.append(lit)
            results.append({"literal": lit, "kind": "source", "verdict": "not_found",
                            "detail": f"quote NOT found in {src_name}: {entry['quote']!r}"})

    stale = [lit for lit in manifest if lit not in lit_set]

    return {
        "literals": literals,
        "results": results,
        "uncited": uncited,
        "not_found": not_found,
        "stale": stale,
        "malformed": malformed,
        "ok": not (uncited or not_found or stale or malformed),
    }


def _resolve_within(base, name):
    """Resolve `name` against `base`, refusing to escape `base` - an absolute
    path, a `..` segment, or a symlink pointing outside is rejected rather
    than read. The manifest is trusted today, but this wrapper may be reused
    where it isn't (a gate run on an unmerged branch), and a citation source
    is always a plain filename inside the sources tree."""
    if pathlib.PurePath(name).is_absolute() or ".." in pathlib.PurePath(name).parts:
        raise SystemExit(f"literal_citation: refusing source path outside the tree: {name!r}")
    base = pathlib.Path(base).resolve()
    candidate = (base / name).resolve()
    if base != candidate and base not in candidate.parents:
        raise SystemExit(f"literal_citation: source path escapes {base}: {name!r}")
    return candidate


def check_example(dfy_path, manifest, sources_dir):
    """Convenience wrapper: read the .dfy at `dfy_path`, read every source
    file a `source`-kind manifest entry names from `sources_dir`, and run
    `verify_literal_citations`. Pure verification lives in that function; this
    only does the file I/O. Source filenames are confined to `sources_dir`
    (see `_resolve_within`)."""
    spec_source = pathlib.Path(dfy_path).read_text(encoding="utf-8")
    source_texts = {}
    for entry in manifest.values():
        if entry.get("kind") == "source" and entry.get("source"):
            name = entry["source"]
            if name not in source_texts:
                source_texts[name] = _resolve_within(sources_dir, name).read_text(encoding="utf-8")
    return verify_literal_citations(spec_source, manifest, source_texts)
