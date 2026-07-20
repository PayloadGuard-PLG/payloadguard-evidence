"""Component F of the "PROVEN != meaningful" work (Tier 3, structural
separation): the frozen-contract integrity gate.

Tiers 1-2 made the pipeline honest about what a proof *establishes*
(definitional vs property) and whether the spec's numbers *transcribe* the
source. But a PROVEN label is only trustworthy if the contract that was
proven was not itself gamed to be provable. Two classic evasions let an
automated drafter make a false spec pass Dafny:

  1. **Weaken the `ensures`** until a wrong implementation satisfies it. This
     repo already owns a real specimen: `dosage_underconstrained.dfy` verifies
     cleanly yet proves almost nothing (its pinning `ensures` was dropped).
  2. **Add `assume`** (or `{:axiom}` / `{:extern}`) inside a body. `assume
     false;` makes any postcondition verify - Dafny accepts it by design; it
     is the documented soundness escape hatch, invisible to plain `verify`.

This module closes that hole by STRUCTURALLY separating the human-owned
safety contract from machine/LLM-authored proof scaffolding, and mechanically
proving the separation held. It is an *integrity/provenance* guarantee, not a
correctness one: it proves the contract is UNCHANGED by the automated
contributor, not that the contract is right (that stays Tiers 1-2 + the
human Gate C6 review). This is the drafter != checker principle
(`evidence/citation_gate.py`) applied at last to the load-bearing artifact -
the specification itself.

The frozen contract is the canonical, AST-normalized *contract surface* of a
spec: for every declaration, its signature + `requires` + `ensures`, plus
`function`/`predicate` bodies (which, for a predicate spec, ARE the spec).
`method` bodies are the implementation, not the contract, so they are NOT
frozen - they are exactly where legitimate proof scaffolding (`assert`,
`invariant`, `decreases`) lives - but the whole candidate is scanned for the
soundness-escape constructs a drafter must never introduce.

`build_frozen_contract` extracts that surface once from the human-authored
spec (generated, then committed and drift-tested, like Component D's review
template). `check_contract` re-extracts a candidate's surface and proves it
matches the frozen manifest exactly, and that no forbidden construct appeared.
Deliberately mechanical: it interprets nothing, it only canonicalizes and
diffs. "AST-grade" here means the comparison is on a normalized token stream
(comments stripped, whitespace and formatting irrelevant), so a real change to
a clause or body is caught while a reformatting is not.
"""

import pathlib
import re

import yaml

from evidence.dafny_spec_lint import (
    extract_ensures_clauses,
    extract_requires_clauses,
)
from evidence.literal_citation import strip_comments

# Soundness-escape constructs a drafter must never introduce to force
# verification. `assume` takes a proposition as given (so `assume false`
# discharges anything); `{:axiom}` marks a declaration an unproven axiom;
# `{:extern}` links a body to unverified external code. None appear in this
# repo's honestly-authored specs; any appearance in a candidate that the
# frozen baseline didn't have is a violation.
_FORBIDDEN = ("assume", "{:axiom}", "{:extern}")

# Declaration keywords we enumerate. A `function`/`predicate` body is spec and
# is frozen; a `method`/`lemma` body is not (a lemma is itself proof
# scaffolding, freely addable).
_DECL_RE = re.compile(r"\b(function|predicate|method|lemma)\b\s+([A-Za-z_][A-Za-z0-9_']*)")
_BODY_FROZEN_KINDS = ("function", "predicate")

_CLAUSE_KEYWORDS = ("requires", "ensures", "decreases", "reads", "modifies")
_CLAUSE_BOUNDARY_RE = re.compile(r"\b(?:%s)\b" % "|".join(_CLAUSE_KEYWORDS))

# Longest-match tokenizer for canonicalization: multi-char operators first,
# then identifiers, numbers, and any remaining single non-space char. Joining
# the tokens with single spaces yields a form invariant to whitespace and
# formatting but sensitive to any real token change.
_CANON_TOKEN_RE = re.compile(
    r"<==>|==>|<==|::|:=|\.\.|&&|\|\||<=|>=|==|!="
    r"|[A-Za-z_][A-Za-z0-9_']*"
    r"|\d+\.\d+|\d+"
    r"|\S"
)


def _canonical(text):
    """Canonical token form of a Dafny snippet: comments stripped, then the
    token stream joined by single spaces. Whitespace/comment/formatting
    differences vanish; any real token-level change survives."""
    return " ".join(_CANON_TOKEN_RE.findall(strip_comments(text)))


def _balanced_body(source, open_brace_idx):
    """Return the `{...}` block starting at `open_brace_idx` (inclusive),
    brace-matched. Assumes source[open_brace_idx] == '{'."""
    depth = 0
    i = open_brace_idx
    n = len(source)
    while i < n:
        c = source[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return source[open_brace_idx:i + 1]
        i += 1
    raise SystemExit("unbalanced braces: could not find the closing brace of a body")


def _iter_declarations(source):
    """Yield {kind, name, signature, body} for each top-level declaration, in
    source order, over the COMMENT-STRIPPED source (so a keyword inside a
    comment is never mistaken for a declaration). `signature` is the canonical
    name+params+return portion (clauses excluded); `body` is the canonical
    body block, or None for a bodiless declaration."""
    code = strip_comments(source)
    for m in _DECL_RE.finditer(code):
        kind, name = m.group(1), m.group(2)
        # Find where the header ends: the first top-level `{` (body) or `;`
        # (bodiless), tracking (),[] nesting so a `{` inside a type/set stays
        # inert (none in this repo's specs, but correct regardless).
        depth = 0
        i = m.end()
        body = None
        header_end = None
        while i < len(code):
            c = code[i]
            if c in "([":
                depth += 1
            elif c in ")]":
                depth -= 1
            elif depth == 0 and c == "{":
                header_end = i
                body = _balanced_body(code, i)
                break
            elif depth == 0 and c == ";":
                header_end = i
                break
            i += 1
        if header_end is None:
            raise SystemExit(f"could not find the end of declaration {name!r}'s header")
        header = code[m.start():header_end]
        boundary = _CLAUSE_BOUNDARY_RE.search(header)
        signature = header[:boundary.start()] if boundary else header
        yield {
            "kind": kind,
            "name": name,
            "signature": _canonical(signature),
            "body": _canonical(body) if body is not None else None,
        }


def _declaration_record(source, decl):
    """Full frozen record for one declaration: its canonical signature, its
    canonical requires/ensures clauses, and (for a spec-bearing function/
    predicate) its canonical body. A method's body is NOT frozen."""
    name = decl["name"]
    record = {
        "kind": decl["kind"],
        "name": name,
        "signature": decl["signature"],
        "requires": [_canonical(c) for c in extract_requires_clauses(source, name)],
        "ensures": [_canonical(c) for c in extract_ensures_clauses(source, name)],
    }
    if decl["kind"] in _BODY_FROZEN_KINDS:
        record["body"] = decl["body"]
    return record


def build_frozen_contract(spec_name, source):
    """Extract and return the frozen-contract manifest (a dict) for `source`
    (a .dfy file's text), named `spec_name`. One record per declaration, in
    source order. Generated, not hand-authored - committed and drift-checked
    against the current spec, exactly like Component D's review template."""
    declarations = [
        _declaration_record(source, d)
        for d in _iter_declarations(source)
    ]
    return {
        "spec": spec_name,
        "forbidden_constructs": list(_FORBIDDEN),
        "declarations": declarations,
    }


def _forbidden_in(source):
    """Every forbidden soundness-escape construct present in `source`
    (comments stripped), as [(construct, declaration_name_or_'<file>')]."""
    code = strip_comments(source)
    decls = list(_iter_declarations(source))
    found = []
    for construct in _FORBIDDEN:
        for m in re.finditer(re.escape(construct) if not construct.isalpha()
                             else r"\b%s\b" % construct, code):
            # attribute the hit to the enclosing declaration, best-effort
            where = "<file>"
            for d in decls:
                di = code.find(d["name"])
                if di != -1 and di <= m.start():
                    where = d["name"]
            found.append((construct, where))
    return found


def check_contract(candidate_source, manifest):
    """Prove `candidate_source` (a .dfy file's text) preserves the frozen
    `manifest` exactly and introduced no forbidden construct. Returns a report:
      - missing_declarations:  frozen declarations absent from the candidate
      - added_spec_declarations: non-lemma declarations the candidate adds that
                                 the frozen contract didn't have (a new lemma is
                                 allowed proof scaffolding; a new function/
                                 method/datatype is not)
      - signature_mismatches / requires_mismatches / ensures_mismatches /
        body_mismatches:  per-declaration (name) where the canonical contract
                          surface differs from the frozen manifest
      - forbidden_constructs:  (construct, where) newly present in the candidate
      - contract_intact:  True iff all of the above are empty
      - verdict:  "CONTRACT_INTACT" or "CONTRACT_VIOLATED"
      - violations:  human-readable lines naming exactly what changed
    """
    frozen = {d["name"]: d for d in manifest["declarations"]}
    candidate_decls = list(_iter_declarations(candidate_source))
    candidate_by_name = {d["name"]: d for d in candidate_decls}
    # Only build full records for declarations the frozen contract names: those
    # are the ones we diff. An added lemma/function isn't in `frozen` and only
    # needs its kind (below) - and building a record for a `lemma` would fail,
    # since the clause extractor only recognizes method/function headers.
    candidate = {
        name: _declaration_record(candidate_source, candidate_by_name[name])
        for name in frozen
        if name in candidate_by_name
    }

    missing_declarations = []
    signature_mismatches = []
    requires_mismatches = []
    ensures_mismatches = []
    body_mismatches = []
    violations = []

    for name, frec in frozen.items():
        crec = candidate.get(name)
        if crec is None:
            missing_declarations.append(name)
            violations.append(f"declaration {name!r} is missing from the candidate")
            continue
        if crec["signature"] != frec["signature"]:
            signature_mismatches.append(name)
            violations.append(f"{name}: signature changed")
        if crec["requires"] != frec["requires"]:
            requires_mismatches.append(name)
            violations.append(
                f"{name}: requires changed (frozen {frec['requires']} -> "
                f"candidate {crec['requires']})"
            )
        if crec["ensures"] != frec["ensures"]:
            ensures_mismatches.append(name)
            violations.append(
                f"{name}: ensures changed (frozen {frec['ensures']} -> "
                f"candidate {crec['ensures']})"
            )
        if "body" in frec and crec.get("body") != frec["body"]:
            body_mismatches.append(name)
            violations.append(f"{name}: {frec['kind']} body (spec) changed")

    added_spec_declarations = [
        d["name"] for d in candidate_decls
        if d["name"] not in frozen and d["kind"] != "lemma"
    ]
    for name in added_spec_declarations:
        violations.append(
            f"candidate adds spec-bearing declaration {name!r} not in the "
            "frozen contract (only new lemmas are allowed proof scaffolding)"
        )

    frozen_forbidden = set(manifest.get("forbidden_constructs", _FORBIDDEN))
    forbidden_constructs = [
        (c, where) for (c, where) in _forbidden_in(candidate_source)
        if c in frozen_forbidden
    ]
    for construct, where in forbidden_constructs:
        violations.append(
            f"forbidden construct {construct!r} present in {where} - a "
            "soundness-escape a drafter must never introduce"
        )

    intact = not (
        missing_declarations
        or added_spec_declarations
        or signature_mismatches
        or requires_mismatches
        or ensures_mismatches
        or body_mismatches
        or forbidden_constructs
    )
    return {
        "missing_declarations": missing_declarations,
        "added_spec_declarations": added_spec_declarations,
        "signature_mismatches": signature_mismatches,
        "requires_mismatches": requires_mismatches,
        "ensures_mismatches": ensures_mismatches,
        "body_mismatches": body_mismatches,
        "forbidden_constructs": forbidden_constructs,
        "contract_intact": intact,
        "verdict": "CONTRACT_INTACT" if intact else "CONTRACT_VIOLATED",
        "violations": violations,
    }


def load_manifest(manifest_path):
    return yaml.safe_load(pathlib.Path(manifest_path).read_text(encoding="utf-8"))


def check_example(candidate_dfy, manifest_path):
    """Convenience wrapper: read a candidate .dfy and a committed frozen
    manifest, and check the candidate against it. Pure verification lives in
    `check_contract`; this only does file I/O."""
    candidate_source = pathlib.Path(candidate_dfy).read_text(encoding="utf-8")
    return check_contract(candidate_source, load_manifest(manifest_path))
