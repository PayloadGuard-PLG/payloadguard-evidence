"""Gate C3, vector 3 (Component A of the "PROVEN != meaningful" work):
the spec/implementation-gap classifier.

A Dafny `PROVEN` label certifies that the verifier discharged a spec, but
not how much *independent content* that spec carries beyond the function's
own definition. Two honest-but-very-different situations both earn PROVEN:

  - **Definitional.** The postcondition just restates the body. For a pure
    predicate `function F(x): bool ensures F(x) <==> E { E }`, the proof
    obligation is `E <==> E`, discharged by reflexivity. What is certified
    is totality, type-safety, match-exhaustiveness, and the literal
    boundary structure of `E` - real, but not an *independent* property.
  - **Property.** The postcondition is strictly weaker than the body: a
    bound or invariant many values could satisfy, so a wrong body could
    violate it (e.g. `ensures 0.0 <= dose <= maxSafeDoseMgPerHr` over a
    real computation). Here the proof carries content beyond the
    definition.

This module classifies each `ensures` clause into one of those two kinds,
per clause (a single function can carry both - dosage's `CalculateHourlyDose`
pins `dose == ExpectedDose(...)` *and* bounds `0.0 <= dose <= max`), and
rolls the per-clause verdicts up to a per-declaration verdict.

**How.** The load-bearing question for one clause is: does it constrain
the result to a *single* value (a definition) or leave it *freedom* (a
property)? That is answered structurally, then confirmed semantically:

  1. Substitute the function's self-call `F(args)` (or a method's `returns`
     name) with a result sentinel, so a clause referring to the result
     becomes a plain constraint on one symbol.
  2. Strip any leading `guard ==> ...` implications (a guarded clause pins
     the result only within its guard - aeb_kernel's `match`-per-target
     shape). The classification is about the *consequent*.
  3. Read the consequent's loosest top-level operator (paren-depth aware,
     so it survives commas/casts/`.member` calls that the full Z3
     tokenizer would refuse): a `==` or `<==>` with the result isolated on
     one side *pins* it -> DEFINITIONAL; a bound (`<,<=,>,>=,!=`) or a
     boolean combination (`||`,`&&`) over the result leaves freedom ->
     PROPERTY.
  4. Where the consequent is fully translatable by `evidence.dafny_spec_lint`
     (many are not - a companion-function RHS like `ExpectedDose(...)` or a
     parameterized-datatype RHS like `InteractionResult(...)` is not), a Z3
     pin-uniqueness check *confirms* the structural verdict: a definitional
     consequent must pin the result uniquely; a property one must not. A
     disagreement is reported, never silently resolved.

Nothing here changes a label yet - that is Component B. This module only
*derives* the classification, so the by-hand analysis can be confirmed
mechanically before anything downstream depends on it.
"""

import re

import z3

from evidence.dafny_spec_lint import (
    _find_method_header,
    _parse_enum_datatypes,
    _parse_params,
    build_symbol_table,
    extract_ensures_clauses,
    extract_requires_clauses,
    translate_clause,
)

_RESULT = "__result__"

# Loosest-to-tightest precedence of the operators that decide whether a
# clause pins the result or bounds it. Arithmetic (+ - * /) is tighter than
# every entry here, so it never wins the "loosest top-level operator" race
# that classification turns on.
_OPS = [
    ("EQIMP", "<==>"),
    ("IMP", "==>"),
    ("OR", "||"),
    ("AND", "&&"),
    ("LE", "<="),
    ("GE", ">="),
    ("EQ", "=="),
    ("NE", "!="),
    ("LT", "<"),
    ("GT", ">"),
]
_PIN_OPS = {"EQIMP", "EQ"}
_BOUND_OPS = {"LE", "GE", "NE", "LT", "GT"}
_BOOL_OPS = {"OR", "AND"}


def _return_type(header, name):
    """The declared result type of `function name(...): T` or the out-param
    (name, type) of `method name(...) returns (out: T)`. Refuses rather
    than guessing if neither shape is present."""
    kind = re.match(r"\s*(method|function)\b", header)
    if not kind:
        raise SystemExit(f"{name!r}: header is neither a function nor a method")
    if kind.group(1) == "method":
        m = re.search(r"\breturns\s*\(\s*([A-Za-z_]\w*)\s*:\s*([^,)]+?)\s*\)", header)
        if not m:
            raise SystemExit(
                f"{name!r}: method has no single `returns (out: T)` this "
                "classifier can bind a result to; refusing to guess"
            )
        return "method", m.group(1), m.group(2).strip()
    # function: the type after the top-level param-list close-paren.
    depth = 0
    i = header.index("(")
    while i < len(header):
        c = header[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    m = re.match(r"\s*:\s*([A-Za-z_][\w.<>]*)", header[i + 1:])
    if not m:
        raise SystemExit(f"{name!r}: function has no `): T` return type; refusing to guess")
    return "function", None, m.group(1).strip()


def _replace_call(text, fn_name, replacement):
    """Replace every `fn_name(...)` (balanced parens) in `text` with
    `replacement` - used to turn a function's self-reference in its own
    postcondition into a plain result symbol."""
    out = []
    i = 0
    pat = re.compile(rf"\b{re.escape(fn_name)}\s*\(")
    while i < len(text):
        m = pat.match(text, i)
        if not m:
            out.append(text[i])
            i += 1
            continue
        depth = 0
        j = m.end() - 1
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(replacement)
        i = j + 1
    return "".join(out)


def _strip_line_comment(clause):
    """Return (clause_without_comment, req_id_or_None). REQ ids are carried
    on a trailing `// REQ-...` the way every spec in this repo cites them."""
    req = None
    m = re.search(r"//\s*(REQ-[A-Za-z0-9-]+)", clause)
    if m:
        req = m.group(1)
    return re.sub(r"//[^\n]*", "", clause).strip(), req


def _strip_outer_parens(text):
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        matched = True
        for idx, c in enumerate(text):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0 and idx != len(text) - 1:
                    matched = False
                    break
        if matched:
            text = text[1:-1].strip()
        else:
            break
    return text


def _find_top_op(text):
    """The loosest-precedence top-level (paren-depth 0) operator in `text`,
    as (kind, lhs, rhs) split at its FIRST occurrence, or None if the text
    has no such operator (a bare atom). Depth tracks `(` and `[` so commas,
    casts and `.member` accesses inside a call never register."""
    text = _strip_outer_parens(text)
    for kind, sym in _OPS:  # loosest first
        depth = 0
        i = 0
        n = len(text)
        while i < n:
            c = text[i]
            if c in "([":
                depth += 1
                i += 1
                continue
            if c in ")]":
                depth -= 1
                i += 1
                continue
            if depth == 0 and text.startswith(sym, i):
                # Guard against matching a prefix of a longer operator that
                # sorts later (e.g. `<` inside `<==>`/`<=`): only accept if
                # the longer forms don't also start here.
                if sym == "<" and (text.startswith("<==>", i) or text.startswith("<=", i)):
                    i += 1
                    continue
                if sym == ">" and text.startswith(">=", i):
                    i += 1
                    continue
                if sym == "==" and text.startswith("==>", i):
                    i += 1
                    continue
                return kind, text[:i].strip(), text[i + len(sym):].strip()
            i += 1
    return None


def _result_isolated(side, result_token):
    return _strip_outer_parens(side).strip() == result_token


def classify_clause(source, name, raw_clause, result_kind, result_token, result_type):
    """Classify one ensures clause. Returns a dict:
      classification: "definitional" | "property" | "not_result_constraining"
      reason, guards (stripped implication antecedents), req (or None),
      and z3_check: "confirmed" | "disagrees:<detail>" | "not_attempted:<why>".
    """
    clause, req = _strip_line_comment(raw_clause)
    if result_kind == "function":
        clause = _replace_call(clause, name, result_token)

    guards = []
    consequent = clause
    while True:
        top = _find_top_op(consequent)
        if top and top[0] == "IMP":
            guards.append(top[1])
            consequent = top[2]
        else:
            break

    record = {"req": req, "clause": raw_clause.strip(), "guards": guards}

    if not re.search(rf"\b{re.escape(result_token)}\b", consequent):
        record.update(
            classification="not_result_constraining",
            reason="the consequent does not mention the result at all",
            z3_check="not_attempted:no result reference",
        )
        return record

    top = _find_top_op(consequent)
    if top and top[0] in _PIN_OPS and (
        _result_isolated(top[1], result_token) or _result_isolated(top[2], result_token)
    ):
        classification = "definitional"
        reason = (
            f"consequent pins the result: `{top[0] == 'EQ' and '==' or '<==>'}` "
            "with the result isolated on one side (restates the definition)"
        )
    elif top and top[0] in _BOUND_OPS:
        classification = "property"
        reason = f"consequent bounds the result (`{top[0]}`), not an equality - strictly weaker than the body"
    elif top and top[0] in _BOOL_OPS:
        classification = "property"
        reason = f"consequent constrains the result under a boolean combination (`{top[0]}`), not a single-value pin"
    else:
        classification = "property"
        reason = "consequent constrains the result without pinning it to a single expression"

    record.update(classification=classification, reason=reason)
    record["z3_check"] = _z3_confirm(
        source, name, consequent, guards, classification, result_token, result_type
    )
    return record


def _z3_confirm(source, name, consequent, guards, classification, result_token, result_type):
    """Best-effort semantic cross-check of the structural verdict: a
    definitional consequent must pin the result uniquely (no two distinct
    result values satisfy it under the guards and preconditions); a property
    one must not. Returns "confirmed", "disagrees:...", or
    "not_attempted:..." when any part is outside the Z3-translatable subset
    (a companion-function or parameterized-datatype RHS, a cast, etc.)."""
    if result_type not in ("real", "int", "nat", "bool"):
        return f"not_attempted:result type {result_type!r} not modeled"
    try:
        header = _find_method_header(source, name)
        params = _parse_params(header)
        enums = _parse_enum_datatypes(source)
        # Two independent result symbols of the declared type.
        base = {n: t for n, t in params.items()}
        base[result_token] = result_type
        r2_token = "__result2__"
        base2 = dict(base)
        base2[result_token] = result_type  # placeholder; r2 built separately
        symbols, implicit = build_symbol_table(
            {**{n: t for n, t in params.items()}, result_token: result_type}, enums
        )
        symbols2, _ = build_symbol_table({r2_token: result_type}, enums)
        r1 = symbols[result_token]
        r2 = symbols2[r2_token]

        pre = [
            translate_clause(c, symbols, f"requires of {name!r}")
            for c in extract_requires_clauses(source, name)
        ]
        guard_z3 = [translate_clause(g, symbols, f"guard of {name!r}") for g in guards]

        c1 = translate_clause(consequent, symbols, f"ensures of {name!r}")
        sym_r2 = dict(symbols)
        sym_r2[result_token] = r2
        c2 = translate_clause(consequent, sym_r2, f"ensures of {name!r} (2nd result)")

        solver = z3.Solver()
        solver.add(*implicit, *pre, *guard_z3, c1, c2, r1 != r2)
        outcome = solver.check()
    except SystemExit as e:
        return f"not_attempted:{e}"
    except z3.Z3Exception as e:  # pragma: no cover - defensive
        return f"not_attempted:z3 error {e}"

    pins_uniquely = outcome == z3.unsat
    if classification == "definitional":
        return "confirmed" if pins_uniquely else "disagrees:structure says pin but Z3 finds two result values"
    if pins_uniquely:
        return "disagrees:structure says property but Z3 finds the clause pins the result uniquely"
    return "confirmed"


def _declaration_names(source):
    """Every `function`/`method` name declared in `source`, in source
    order, comments stripped so a commented-out signature never counts."""
    src = re.sub(r"//[^\n]*", "", source)
    return [m.group(2) for m in re.finditer(r"\b(function|method)\s+([A-Za-z_]\w*)\s*\(", src)]


def classify_declaration(source, name):
    """Per-clause classification plus a rolled-up verdict for one function
    or method: `definitional` if every result-constraining ensures clause
    restates the definition, `property` if any clause carries independent
    content, `no_postcondition` if there are no ensures clauses."""
    header = _find_method_header(source, name)
    result_kind, out_name, result_type = _return_type(header, name)
    result_token = out_name if result_kind == "method" else _RESULT

    clauses = extract_ensures_clauses(source, name)
    per_clause = [
        classify_clause(source, name, c, result_kind, result_token, result_type)
        for c in clauses
    ]
    constraining = [c for c in per_clause if c["classification"] != "not_result_constraining"]
    if not constraining:
        overall = "no_postcondition" if not per_clause else "no_result_postcondition"
    elif any(c["classification"] == "property" for c in constraining):
        overall = "property"
    else:
        overall = "definitional"
    return {
        "name": name,
        "kind": result_kind,
        "result_type": result_type,
        "overall": overall,
        "clauses": per_clause,
    }


def classify_source(source):
    """Classify every function/method in `source`."""
    return [classify_declaration(source, n) for n in _declaration_names(source)]
