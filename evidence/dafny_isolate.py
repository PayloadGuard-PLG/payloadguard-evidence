"""Phase C, Gate C5: single-function isolation for mutation testing.

The caller-confound (gate_c5 isolation finding, 2026-07-19): Dafny
verifies a whole file at once, and the mutation runner's kill/survive
signal is "does the whole file still verify." That conflates two
different failures:

  (a) the MUTATED function's own postcondition failing against its own
      body - the only thing that says the function's own contract is
      tight, and

  (b) a DOWNSTREAM CALLER failing to discharge the mutated function's
      (now-changed) requires/ensures at a call site - a real failure,
      but attributed to the wrong function's tightness.

Reproduced empirically against renal_adjustment.dfy: RoundHalfUp's
`requires x >= 0.0` widened to `<= 0.0` was scored KILLED whole-file,
but the error was inside AssessRenalFunction (a caller), not RoundHalfUp
itself - in isolation that mutant SURVIVES. Whole-file attribution
therefore over-reports kills for any function that has in-file callers.

This module removes the confound at its source: `isolate_function`
extracts a function together with ONLY its transitive callees and every
datatype, and NEVER its callers. Verifying a mutant of F against that
isolated unit means any resulting error is F's own - a caller cannot be
the source because no caller is present. A function with no callers
isolates to essentially itself, so isolation is uniformly safe to apply
to every function, not only ones known to have callers (removing the
"did I remember to check for callers" judgment call the manual practice
otherwise depends on).

Comments are stripped before structural parsing (and from the emitted
unit): the real specs carry heavy `//` commentary that can contain
braces and the words `function`/`method`, which naive structural
scanning would trip on. The isolated unit is a scratch verification
artifact, never committed, so dropping comments costs nothing and Dafny
verifies it identically.
"""

import re

_COMMENT_RE = re.compile(r"//[^\n]*")
_DECL_RE = re.compile(r"\b(?P<kind>function|method)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(")
_DATATYPE_RE = re.compile(
    r"\bdatatype\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(?P<body>.*?)"
    r"(?=\bdatatype\b|\bfunction\b|\bmethod\b|\Z)",
    re.DOTALL,
)
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _strip_comments(source):
    return _COMMENT_RE.sub("", source)


def _decl_end(source, header_match):
    """Absolute end offset (exclusive) of the function/method declaration
    whose header regex match is `header_match`: scans past the header's
    parenthesised/bracketed groups to the body's opening `{` at paren
    depth 0, then depth-matches to its closing `}`. Mirrors
    dafny_mutate._find_function_body_span's brace logic exactly."""
    depth = 0
    i = header_match.end() - 1  # at the '(' of the parameter list
    open_brace = None
    while i < len(source):
        c = source[i]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "{" and depth == 0:
            open_brace = i
            break
        i += 1
    if open_brace is None:
        raise SystemExit(
            f"dafny_isolate: could not find the body opening brace for "
            f"{header_match.group('name')!r}; refusing to guess declaration bounds"
        )
    depth = 0
    j = open_brace
    while j < len(source):
        if source[j] == "{":
            depth += 1
        elif source[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise SystemExit(
        f"dafny_isolate: could not find the matching closing brace for "
        f"{header_match.group('name')!r}; refusing to guess declaration bounds"
    )


def _parse_decls(clean_source):
    """Return (datatypes, funcs) where datatypes is [(name, text)] in
    source order and funcs is {name: text} - both from comment-stripped
    source."""
    datatypes = []
    for m in _DATATYPE_RE.finditer(clean_source):
        datatypes.append((m.group("name"), m.group(0).strip()))
    funcs = {}
    for m in _DECL_RE.finditer(clean_source):
        name = m.group("name")
        end = _decl_end(clean_source, m)
        funcs[name] = clean_source[m.start():end]
    return datatypes, funcs


def _referenced_funcs(decl_text, own_name, all_func_names):
    """Every declared function/method name referenced in decl_text, minus
    the declaration's own name (a function references itself in its own
    ensures clauses; that self-reference is not a call to a *different*
    declaration and must not seed the closure)."""
    tokens = set(_IDENT_RE.findall(decl_text))
    return {n for n in tokens if n in all_func_names and n != own_name}


def isolate_function(source, function_name):
    """Return a standalone, comment-free Dafny source containing
    `function_name`, every function/method it transitively calls, and
    every datatype in the file - but none of its callers. Any Dafny error
    when verifying a mutant of `function_name` against this unit is
    therefore attributable to `function_name`'s own contract, never to a
    downstream caller (see module docstring).

    Datatypes are always included wholesale: an unused datatype is
    harmless to Dafny, and tracking exact type/constructor usage would be
    a parsing burden with no soundness benefit here."""
    clean = _strip_comments(source)
    datatypes, funcs = _parse_decls(clean)
    if function_name not in funcs:
        raise SystemExit(
            f"dafny_isolate: no function or method named {function_name!r} "
            f"found in source (declared: {sorted(funcs)})"
        )
    all_names = set(funcs)
    # Down-closure: function_name plus everything it transitively calls.
    keep = set()
    frontier = [function_name]
    while frontier:
        name = frontier.pop()
        if name in keep:
            continue
        keep.add(name)
        for ref in _referenced_funcs(funcs[name], name, all_names):
            if ref not in keep:
                frontier.append(ref)
    # Emit datatypes (all, source order) then kept functions in source order.
    kept_in_order = [text for name, text in funcs.items() if name in keep]
    parts = [text for _name, text in datatypes] + kept_in_order
    return "\n\n".join(parts) + "\n"
