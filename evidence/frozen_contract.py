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
spec: every `datatype`/`codatatype` definition (the constructors are the
spec's meaning), and for every function/method its signature + `requires` +
`ensures`, plus `function`/`predicate` bodies (which, for a predicate spec,
ARE the spec). `method` bodies are the implementation, not the contract, so
they are NOT frozen - they are exactly where legitimate proof scaffolding
(`assert`, `invariant`, `decreases`) lives - but the whole candidate is
scanned for the soundness-escape constructs a drafter must never introduce.

**Fail-closed scope.** The gate models `datatype` / `codatatype` / `function`
/ `predicate` / `method` / `lemma`. It does NOT yet model the remaining
type-level declarations (`newtype`, `type`, `const`, `class`, `trait`,
`iterator`) - none appear in this repo's four worked specs. Rather than
silently ignore a construct it can't diff (which would let such a change slip
through as a false CONTRACT_INTACT), the gate FAILS CLOSED: it refuses to
build a frozen manifest for a spec containing an unmodeled declaration, and
flags any unmodeled declaration in a candidate as a violation. Extending the
model to freeze those kinds is how you lift the refusal, not by weakening it.

`build_frozen_contract` extracts the contract surface once from the
human-authored spec (generated, then committed and drift-tested, like
Component D's review template). `check_contract` re-extracts a candidate's
surface and proves it matches the frozen manifest exactly, and that no
forbidden construct appeared. Deliberately mechanical: it interprets nothing,
it only canonicalizes and diffs. "AST-grade" here means the comparison is on a
normalized token stream (comments stripped, whitespace and formatting
irrelevant), so a real change to a clause or body is caught while a
reformatting is not.
"""

import pathlib
import re

import yaml

from evidence.literal_citation import strip_comments

# Soundness-escape constructs a drafter must never introduce to force
# verification. `assume` takes a proposition as given (so `assume false`
# discharges anything); `{:axiom}` marks a declaration an unproven axiom;
# `{:extern}` links a body to unverified external code. These are ALWAYS
# forbidden - an honestly-authored spec contains none, and `build_frozen_contract`
# refuses to freeze a source that already contains one, so any occurrence in a
# candidate is unambiguously an introduced escape, not a pre-existing one.
_FORBIDDEN = ("assume", "{:axiom}", "{:extern}")

# Dafny allows attribute blocks between a declaration keyword and its name
# (`function {:opaque} F(...)`, `lemma {:axiom} L(...)` - the latter form is
# live in this repo's own dafny_pow_axiom_trap_probe.dfy). The enumeration
# regexes must see through them, or an attribute-bearing declaration would be
# invisible to the gate entirely - addable without ever appearing in
# added_spec_declarations/unmodeled_declarations (a real bypass, caught by
# review on the datatype extension).
_ATTRS = r"(?:\s+\{:[^}]*\})*"

# Declaration keywords this gate models. A `datatype`/`codatatype` definition
# and a `function`/`predicate` body are spec and are frozen; a `method` body is
# the implementation (not frozen); a `lemma` is itself proof scaffolding,
# freely addable, so it is not frozen either.
_DECL_RE = re.compile(
    r"\b(datatype|codatatype|function|predicate|method|lemma)\b"
    + _ATTRS
    + r"\s+([A-Za-z_][A-Za-z0-9_']*)"
)
_DATATYPE_KINDS = ("datatype", "codatatype")
_BODY_FROZEN_KINDS = ("function", "predicate")
# Frozen: the contract surface. `lemma` is scaffolding, not frozen.
_FROZEN_KINDS = ("datatype", "codatatype", "function", "predicate", "method")

# Any top-level declaration keyword - used to find where a datatype definition
# (which has no `{...}`/`;` terminator) ends: at the start of the next
# declaration, or end of file.
_NEXT_DECL_RE = re.compile(
    r"\b(datatype|codatatype|newtype|type|const|class|trait|iterator|"
    r"function|predicate|method|lemma)\b"
)

# Type-level / other top-level declaration keywords this gate still does NOT
# model (datatypes ARE modeled now). Their presence triggers the fail-closed
# refusal described in the module docstring, rather than a silent, false
# "intact". `\btype\b` does not match inside `newtype` (no word boundary), so
# both are listed to catch each on its own.
_UNMODELED_DECL_RE = re.compile(
    r"\b(newtype|type|const|class|trait|iterator)\b"
    + _ATTRS
    + r"\s+([A-Za-z_][A-Za-z0-9_']*)"
)

_CLAUSE_KEYWORDS = ("requires", "ensures", "decreases", "reads", "modifies")
_CLAUSE_SPLIT_RE = re.compile(r"\b(%s)\b" % "|".join(_CLAUSE_KEYWORDS))

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


def _split_header(header):
    """Split a declaration header (comment-stripped, up to but excluding the
    body) into its canonical signature and its requires/ensures clause lists.
    Kind-agnostic - works for function/predicate/method/lemma alike, unlike
    dafny_spec_lint's method/function-only header helper - so a lemma- or
    predicate-bearing spec is handled, not crashed on."""
    parts = _CLAUSE_SPLIT_RE.split(header)
    signature = _canonical(parts[0])
    requires, ensures = [], []
    for i in range(1, len(parts), 2):
        keyword, text = parts[i], parts[i + 1].strip()
        if not text:
            continue
        if keyword == "requires":
            requires.append(_canonical(text))
        elif keyword == "ensures":
            ensures.append(_canonical(text))
    return signature, requires, ensures


def _iter_declarations(source):
    """Yield {kind, name, signature, requires, ensures, body} for each modeled
    top-level declaration, in source order, over the COMMENT-STRIPPED source
    (so a keyword inside a comment is never mistaken for a declaration).
    `body` is the canonical body block, or None for a bodiless declaration."""
    code = strip_comments(source)
    for m in _DECL_RE.finditer(code):
        kind, name = m.group(1), m.group(2)
        if kind in _DATATYPE_KINDS:
            # A datatype has no `{...}`/`;` terminator - its definition (the
            # `= C1 | C2(field: T) | ...` constructors, which ARE part of the
            # spec's meaning) runs to the start of the next declaration.
            nxt = _NEXT_DECL_RE.search(code, m.end())
            end = nxt.start() if nxt else len(code)
            yield {"kind": kind, "name": name, "definition": _canonical(code[m.start():end])}
            continue
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
        signature, requires, ensures = _split_header(code[m.start():header_end])
        yield {
            "kind": kind,
            "name": name,
            "signature": signature,
            "requires": requires,
            "ensures": ensures,
            "body": _canonical(body) if body is not None else None,
        }


def _unmodeled_declarations(source):
    """Type-level / other top-level declarations this pilot does not model,
    as [(keyword, name)] over the comment-stripped source. Non-empty means the
    gate must fail closed rather than report a (false) clean result."""
    code = strip_comments(source)
    return [(m.group(1), m.group(2)) for m in _UNMODELED_DECL_RE.finditer(code)]


def _forbidden_in(source):
    """Every forbidden soundness-escape construct present in `source`
    (comments stripped), as [(construct, declaration_name_or_'<file>')]."""
    code = strip_comments(source)
    decls = list(_iter_declarations(source))
    found = []
    for construct in _FORBIDDEN:
        pattern = r"\b%s\b" % construct if construct.isalpha() else re.escape(construct)
        for m in re.finditer(pattern, code):
            where = "<file>"
            for d in decls:
                di = code.find(d["name"])
                if di != -1 and di <= m.start():
                    where = d["name"]
            found.append((construct, where))
    return found


def _declaration_record(decl):
    """Frozen record for one declaration. A datatype freezes its whole
    canonical `definition` (the constructors are the spec). A function/method
    freezes its signature + requires + ensures; a function/predicate also
    freezes its body (spec). A method's body is NOT frozen (implementation)."""
    if decl["kind"] in _DATATYPE_KINDS:
        return {"kind": decl["kind"], "name": decl["name"], "definition": decl["definition"]}
    record = {
        "kind": decl["kind"],
        "name": decl["name"],
        "signature": decl["signature"],
        "requires": decl["requires"],
        "ensures": decl["ensures"],
    }
    if decl["kind"] in _BODY_FROZEN_KINDS:
        record["body"] = decl["body"]
    return record


def build_frozen_contract(spec_name, source):
    """Extract and return the frozen-contract manifest (a dict) for `source`
    (a .dfy file's text), named `spec_name`. One record per FROZEN declaration
    (function/predicate/method; a lemma is scaffolding, not frozen), in source
    order. Generated, not hand-authored - committed and drift-checked against
    the current spec, like Component D's review template.

    Fails closed rather than produce a manifest that would give a false sense
    of coverage: refuses a source containing an unmodeled type-level
    declaration (see `_UNMODELED_DECL_RE`) or a forbidden soundness-escape
    construct (you cannot freeze a spec that already contains one - the whole
    point is that the frozen baseline is clean)."""
    unmodeled = _unmodeled_declarations(source)
    if unmodeled:
        raise SystemExit(
            "frozen_contract: refusing to freeze a spec with unmodeled "
            f"declaration(s) {unmodeled} - this pilot models only "
            "function/predicate/method/lemma; extend the model to freeze these "
            "kinds rather than silently omit them"
        )
    forbidden = _forbidden_in(source)
    if forbidden:
        raise SystemExit(
            "frozen_contract: refusing to freeze a spec that already contains "
            f"forbidden soundness-escape construct(s) {forbidden} - the frozen "
            "baseline must be clean"
        )
    declarations = [
        _declaration_record(d)
        for d in _iter_declarations(source)
        if d["kind"] in _FROZEN_KINDS
    ]
    return {
        "spec": spec_name,
        "forbidden_constructs": list(_FORBIDDEN),
        "declarations": declarations,
    }


def check_contract(candidate_source, manifest):
    """Prove `candidate_source` (a .dfy file's text) preserves the frozen
    `manifest` exactly and introduced no forbidden construct. Returns a report:
      - missing_declarations:  frozen declarations absent from the candidate
      - added_spec_declarations: non-lemma modeled declarations the candidate
                                 adds that the frozen contract didn't have (a
                                 new lemma is allowed proof scaffolding)
      - unmodeled_declarations:  type-level declarations the gate does not
                                 model (newtype/type/const/class/trait/
                                 iterator - datatypes ARE modeled and diffed);
                                 their presence fails the check closed rather
                                 than passing a construct that cannot be diffed
      - signature_mismatches / requires_mismatches / ensures_mismatches /
        body_mismatches / definition_mismatches:  per-declaration (name) where
                          the canonical contract surface differs from the
                          frozen manifest (definition_mismatches is a datatype
                          whose constructors changed)
      - forbidden_constructs:  (construct, where) present in the candidate. The
                               baseline is guaranteed clean (build refuses
                               otherwise), so any hit is an introduced escape.
      - contract_intact:  True iff all of the above are empty
      - verdict:  "CONTRACT_INTACT" or "CONTRACT_VIOLATED"
      - violations:  human-readable lines naming exactly what changed
    """
    frozen = {d["name"]: d for d in manifest["declarations"]}
    candidate_decls = list(_iter_declarations(candidate_source))
    candidate_by_name = {d["name"]: d for d in candidate_decls}
    # Only build records for the declarations the frozen contract names - those
    # are the ones we diff. An added lemma/function isn't in `frozen` and only
    # needs its kind (below).
    candidate = {
        name: _declaration_record(candidate_by_name[name])
        for name in frozen
        if name in candidate_by_name
    }

    missing_declarations = []
    signature_mismatches = []
    requires_mismatches = []
    ensures_mismatches = []
    body_mismatches = []
    definition_mismatches = []
    violations = []

    for name, frec in frozen.items():
        crec = candidate.get(name)
        if crec is None:
            missing_declarations.append(name)
            violations.append(f"declaration {name!r} is missing from the candidate")
            continue
        # A datatype freezes its whole definition; a function/method freezes its
        # signature + clauses (+ body for a function/predicate). Compare by which
        # fields the frozen record actually carries, so a kind change (e.g. a
        # datatype turned into a function of the same name) shows as a mismatch.
        if "definition" in frec and crec.get("definition") != frec["definition"]:
            definition_mismatches.append(name)
            violations.append(f"{name}: {frec['kind']} definition changed")
        if "signature" in frec:
            if crec.get("signature") != frec["signature"]:
                signature_mismatches.append(name)
                violations.append(f"{name}: signature changed")
            if crec.get("requires") != frec["requires"]:
                requires_mismatches.append(name)
                violations.append(
                    f"{name}: requires changed (frozen {frec['requires']} -> "
                    f"candidate {crec.get('requires')})"
                )
            if crec.get("ensures") != frec["ensures"]:
                ensures_mismatches.append(name)
                violations.append(
                    f"{name}: ensures changed (frozen {frec['ensures']} -> "
                    f"candidate {crec.get('ensures')})"
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

    unmodeled_declarations = _unmodeled_declarations(candidate_source)
    for keyword, name in unmodeled_declarations:
        violations.append(
            f"candidate contains unmodeled {keyword} declaration {name!r} - the "
            "gate cannot diff it, so it fails closed rather than pass it"
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
        or unmodeled_declarations
        or signature_mismatches
        or requires_mismatches
        or ensures_mismatches
        or body_mismatches
        or definition_mismatches
        or forbidden_constructs
    )
    return {
        "missing_declarations": missing_declarations,
        "added_spec_declarations": added_spec_declarations,
        "unmodeled_declarations": unmodeled_declarations,
        "signature_mismatches": signature_mismatches,
        "requires_mismatches": requires_mismatches,
        "ensures_mismatches": ensures_mismatches,
        "body_mismatches": body_mismatches,
        "definition_mismatches": definition_mismatches,
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
