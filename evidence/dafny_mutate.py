"""Phase C, Gate C5: mutation testing (MutDafny-style) for the real Dafny
spec in this repository.

Correction (2026-07-07, per external research recorded in
examples/dosage_calculator/gate_c5_mutation_testing_research_findings.md):
this was originally mislabeled "MutDafny/IronSpec-style." IronSpec's own
mutation-testing technique (Goldweber et al., OSDI'24) is directional -
it generates mutants strictly STRONGER than the original spec and checks
a formal weakness-implication lemma (S is at least as weak as S' iff
forall p. S'(p) implies S(p)) to see whether the spec could have been
tightened without breaking the implementation. This module instead
perturbs operators in ways that aren't uniformly stronger or weaker
(e.g. `!=` is neither a superset nor subset of `>=`) and checks brute
Dafny verification pass/fail - MutDafny's (Amaral, Mendes & Campos,
2025) approach, not IronSpec's. Gate C4's STP suites (Spec-Testing
Proofs) are correctly IronSpec-attributed - a real, separate part of
IronSpec's toolkit - only this module's own label was wrong.

Gates C1/C4 prove `dosage.dfy`'s postconditions HOLD. Neither proves they
are TIGHT - that each boundary is actually load-bearing rather than
incidental. This module answers that question mechanically: perturb a
requires/ensures clause in one small, specific way (a "mutant") and ask
the real installed Dafny binary whether the unchanged method body still
satisfies the mutated spec. If it does ("survives"), that boundary was
never actually proven - a real finding, reported exactly like Gate C4's
spec gap, never smoothed over.

Scope, audited against the real spec rather than assumed generically
(full audit in payloadguard-evidence-roadmap-phaseB-to-C.md's Gate C5
section): this module implements ROR (relational operator replacement),
LOR (logical operator replacement), AOR (arithmetic operator
replacement), and COI (constant/negation insertion). SOR and HOR are not
implemented at all - `dosage.dfy` contains no set-typed values and no
heap/object state (no `old()`, `reads`, `modifies`), confirmed by
tests/test_dafny_mutate.py rather than merely asserted in prose.

v1 scope cut (mutation sites limited to single-line requires/ensures
clauses, the same single-line convention Gate C6 established) is
extended by two follow-ups built 2026-07-07 from the research findings
above:

1. **Chain-direction-aware ROR.** Naive per-token mutation of a chained
   comparison like `0.0 <= dose <= maxSafeDoseMgPerHr` can produce a
   syntactically invalid mutant (`0.0 >= dose <= maxSafeDoseMgPerHr`) -
   a genuine Dafny PARSER rejection (confirmed against the Dafny
   Reference Manual Sec 5.2.1-5.2.2: chained relational operators must
   stay the same direction; `==`/`!=` mix freely into either).
   `_generate_token_mutants`'s `chain_aware` path (used by
   `generate_ror_mutants` only - `&&`/`||`/arithmetic operators have no
   analogous chaining rule) restricts each chain link's candidate
   operators to direction-compatible ones, filtering the
   direction-incompatible candidates before a real Dafny invocation
   rather than generating-then-refusing them. MutDafny itself does not
   do this (its own pipeline buckets these as `Invalid` post-hoc, per
   the research); this is a genuine improvement over the published
   state of the art, not just parity with it.

2. **Function-body AOR, restricted per MutDafny's own group rule.** The
   one arithmetic operator in this spec
   (`infusionRateMlPerHr * concentrationMgPerMl`) lives inside
   `ExpectedDose`'s FUNCTION BODY (part of the formal spec - `ExpectedDose`
   is referenced by the pinning `ensures` clause - never
   `CalculateHourlyDose`'s own imperative `{...}` body, which mutation
   testing must never touch). `generate_aor_mutants`'s optional
   `function_name` parameter now also scans that body.
   `_ar_group_incompatible` applies MutDafny's own restriction (Amaral,
   Mendes & Campos 2025): `+`/`-`/`*` freely interchange; `/` only
   interchanges with `%` (not present in this spec). A mutation is never
   allowed to introduce `/` from `+`/`-`/`*`, which is exactly what would
   trigger Dafny's division-by-zero safety check on a mutation that
   wasn't already division-shaped - the false-kill risk named when AOR
   was originally deferred is resolved by construction, not by post-hoc
   failure-reason attribution.

3. **LVR (Literal Value Replacement), built 2026-07-07 from a scoped
   sub-plan** (full derivation in
   payloadguard-evidence-roadmap-phaseB-to-C.md's "Gate C5 LVR
   extension" section): tests whether a comparison's LITERAL CONSTANT is
   load-bearing, not just its operator. Every numeric literal in this
   spec's requires/ensures clauses and `ExpectedDose`'s function body is
   exactly `0.0` (audited empirically, not assumed) - mutated to
   `original +/- 0.01`, the clinical-precision-floor guidance from the
   research findings above finally applied (it was always scoped to
   literal perturbation specifically). `_lvr_trivial` generalizes ROR's
   requires/ensures polarity principle from operator-implication to
   magnitude-implication for LT/LE/GT/GE-adjacent literals; EQ/NE
   literals have no such filter (changing an equality's target is
   neither a superset nor subset of the original in either direction);
   function-body literals have no requires/ensures role to filter by at
   all, so those go straight to real verification unfiltered, mirroring
   AOR's function-body precedent.
"""

import re
from collections import namedtuple

from evidence.dafny_nl_summary import _CLAUSE_LINE_RE
from evidence.dafny_spec_lint import _find_method_header

Mutant = namedtuple(
    "Mutant",
    [
        "operator",  # "ROR" / "LOR" / "AOR" / "COI"
        "keyword",  # "requires" / "ensures"
        "original_clause",
        "mutated_clause",
        "description",
        "mutated_source",  # the FULL .dfy source text, one clause changed
        "filtered_reason",  # None, or why pass 1 discards it before verification
    ],
)

_WS_RE = re.compile(r"\s*")

# Superset of dafny_spec_lint._TOKEN_RE's grammar: adds a COMMA token so
# clauses containing a function call (e.g. the pinning clause's
# `ExpectedDose(a, b, c)`) can be lexically scanned. This is safe here in
# a way it would NOT be safe in dafny_spec_lint's Z3 translator: mutation
# only ever locates and replaces an operator token's TEXT, it never needs
# to understand what the expression MEANS the way Z3 translation does -
# so tolerating syntax the Z3 translator correctly refuses (function
# calls) does not risk mistranslating anything. An unrecognized character
# still raises rather than being silently skipped.
_TOKEN_SPAN_RE = re.compile(
    r"""
      (?P<EQIMP><==>)
    | (?P<IMP>==>)
    | (?P<ASSIGN>:=)
    | (?P<AND>&&)
    | (?P<OR>\|\|)
    | (?P<LE><=)
    | (?P<GE>>=)
    | (?P<EQ>==)
    | (?P<NE>!=)
    | (?P<LT><)
    | (?P<GT>>)
    | (?P<PLUS>\+)
    | (?P<MINUS>-)
    | (?P<STAR>\*)
    | (?P<SLASH>/)
    | (?P<LPAREN>\()
    | (?P<RPAREN>\))
    | (?P<NOT>!)
    | (?P<COMMA>,)
    | (?P<SEMI>;)
    | (?P<NUM>\d+\.\d+|\d+)
    | (?P<ID>[A-Za-z_][A-Za-z0-9_']*)
    """,
    re.VERBOSE,
)

_CMP_TEXT = {"LE": "<=", "GE": ">=", "EQ": "==", "NE": "!=", "LT": "<", "GT": ">"}
_LOGIC_TEXT = {"AND": "&&", "OR": "||"}
_AR_TEXT = {"PLUS": "+", "MINUS": "-", "STAR": "*", "SLASH": "/"}

# a op_a b UNIVERSALLY implies a op_b b, independent of a/b's actual
# values - the fixed, context-free lattice pass 1's static filter uses.
_CMP_IMPLIES = {
    "EQ": {"LE", "GE"},
    "LT": {"LE", "NE"},
    "GT": {"GE", "NE"},
    "LE": set(),
    "GE": set(),
    "NE": set(),
}
# A && B implies A || B, universally; OR implies nothing further.
_LOGIC_IMPLIES = {"AND": {"OR"}, "OR": set()}
# Arithmetic operators aren't boolean-valued, so no universal implication
# relationship exists between them - nothing is ever statically trivial.
_AR_IMPLIES = {}

_ASCENDING = {"LT", "LE"}
_DESCENDING = {"GT", "GE"}
_NEUTRAL = {"EQ", "NE"}
# Tokens that end a Dafny relational chain's scope: a chain never
# crosses a boolean connective or a parenthesis boundary. Conservative
# by construction (a paren boundary always safely breaks chain-grouping,
# even if some hypothetical nested chain is missed - that only costs a
# few extra unclassifiable candidates later, never an incorrect one).
_CHAIN_BOUNDARY_KINDS = {"AND", "OR", "IMP", "EQIMP", "NOT", "LPAREN", "RPAREN"}

# MutDafny's own AOR restriction (Amaral, Mendes & Campos 2025): +/-/*
# freely interchange; / only interchanges with % (not present in this
# spec's real-valued arithmetic, so / has no compatible replacement
# here at all - never generated as a candidate that reaches Dafny).
_AR_GROUPS = ({"PLUS", "MINUS", "STAR"}, {"SLASH"})

# LVR's clinical-precision-floor guidance
# (gate_c5_mutation_testing_research_findings.md): the smallest
# clinically-distinguishable perturbation for a syringe-pump mL/hr
# value, sourced from pharmacy/nursing device-rounding practice - not a
# formal regulatory standard, but a defensible, cited cutoff.
_LVR_DELTA = 0.01


def _chain_group_ids(tokens):
    """Parallel array: a group id per token in `tokens`, where a group is
    a maximal run not crossing a _CHAIN_BOUNDARY_KINDS token. Multiple
    CMP-kind tokens in one group are directly chained (e.g. the two `<=`
    in `0.0 <= dose <= max`); tokens at a boundary get id None."""
    ids = []
    gid = 0
    for kind, _value, _s, _e in tokens:
        if kind in _CHAIN_BOUNDARY_KINDS:
            ids.append(None)
            gid += 1
        else:
            ids.append(gid)
    return ids


def _chain_incompatible(mutant_kind, sibling_kinds):
    """True if replacing a chain link with mutant_kind would produce a
    direction-inconsistent chain against `sibling_kinds` (the OTHER
    CMP-kind tokens in the same chain group) - a genuine Dafny PARSER
    rejection, confirmed against the Dafny Reference Manual Sec
    5.2.1-5.2.2, not a semantic test."""
    ascending = any(k in _ASCENDING for k in sibling_kinds)
    descending = any(k in _DESCENDING for k in sibling_kinds)
    if not ascending and not descending:
        return False  # no directional siblings (none, or all EQ/NE) - unconstrained
    if mutant_kind in _NEUTRAL:
        return False  # EQ/NE always chain-compatible
    if ascending and mutant_kind in _DESCENDING:
        return True
    if descending and mutant_kind in _ASCENDING:
        return True
    return False


def _ar_group_incompatible(kind, mutant_kind):
    """MutDafny's own restriction: never introduce a mutation that
    crosses the +/-/* <-> /,% group boundary - see _AR_GROUPS above."""
    for group in _AR_GROUPS:
        if kind in group:
            return mutant_kind not in group
    return True  # unknown kind - refuse rather than guess


def _lvr_trivial(keyword, op_kind, literal_is_lhs, delta):
    """Generalizes ROR's requires/ensures polarity principle (see
    _CMP_IMPLIES's docstring and the roadmap's LVR sub-plan for the full
    derivation) from operator-implication to magnitude-implication.

    Normalize every comparison to whether increasing the literal
    NARROWS the set of values that satisfy it (a stricter constraint) or
    WIDENS it (a looser one): `expr > literal`/`expr >= literal`
    (literal on the right) narrows as the literal increases; so does
    `literal <= expr`/`literal < expr` (literal on the left, an
    equivalent "expr >= literal"-shaped constraint). The other two
    operator/side combinations widen as the literal increases. From
    there, the same rule ROR already established applies: for a
    REQUIRES clause, narrowing (strengthening the precondition) is
    trivial - the original proof still applies under the narrower
    hypothesis - so the informative direction is widening (admitting
    inputs the original proof never had to handle). For an ENSURES
    clause it's the opposite: widening (weakening the guarantee) is
    trivial - whatever already satisfies the original satisfies a looser
    consequence too - so the informative direction is narrowing (a
    stronger claim not already implied by the original).

    EQ/NE have no such relationship at all: changing an equality's
    target value is neither a superset nor a subset of the original in
    either direction (`dose == 0.0` doesn't imply, or get implied by,
    `dose == 0.01`) - every EQ/NE literal mutation is always sent to
    real verification, never statically filtered."""
    if op_kind in ("EQ", "NE"):
        return False
    ascending = op_kind in (("LT", "LE") if literal_is_lhs else ("GT", "GE"))
    increased = delta > 0
    narrows = ascending == increased
    if keyword == "ensures":
        return not narrows
    return narrows


def _tokenize_with_spans(expr):
    """Like dafny_spec_lint._tokenize, but returns (kind, value, start,
    end) - character spans within `expr`, needed to splice a mutated
    replacement back into the original source text rather than just
    build a Z3 expression from it."""
    tokens = []
    pos = 0
    n = len(expr)
    while True:
        pos = _WS_RE.match(expr, pos).end()
        if pos >= n:
            return tokens
        m = _TOKEN_SPAN_RE.match(expr, pos)
        if not m:
            raise SystemExit(
                f"dafny_mutate: unsupported syntax at {expr[pos:pos + 20]!r} "
                "- refusing to guess a mutation site rather than risk "
                "mutating the wrong thing"
            )
        tokens.append((m.lastgroup, m.group(), m.start(), m.end()))
        pos = m.end()


def _method_header_span(source, method_name):
    """Absolute (start, end, text) of method_name's header in `source`.
    Reuses dafny_spec_lint._find_method_header's exact matching regex so
    these offsets are guaranteed consistent with its already-tested
    extraction, rather than re-deriving the header boundary logic here."""
    header = _find_method_header(source, method_name)
    m = re.search(rf"\bmethod\s+{re.escape(method_name)}\s*\(", source)
    return m.start(), m.start() + len(header), header


def _find_function_body_span(source, function_name):
    """Absolute (start, end, text) of function_name's BODY - the region
    between its opening brace (after any requires clauses) and the
    matching closing brace. Mirrors dafny_spec_lint._find_method_header's
    depth-tracked brace matching, but returns the body content itself
    rather than the header preceding it, since AOR mutation needs to
    perturb an expression INSIDE the body, not a requires/ensures
    clause."""
    m = re.search(rf"\bfunction\s+{re.escape(function_name)}\s*\(", source)
    if not m:
        raise SystemExit(f"no function named {function_name!r} found in Dafny source")
    depth = 0
    i = m.end() - 1
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
            f"could not find the function body opening brace for {function_name!r}; "
            "refusing to guess where the body starts"
        )
    depth = 0
    j = open_brace
    while j < len(source):
        c = source[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return open_brace + 1, j, source[open_brace + 1 : j]
        j += 1
    raise SystemExit(
        f"could not find the matching closing brace for {function_name!r}'s body; "
        "refusing to guess where it ends"
    )


def _function_body_tokens(source, function_name):
    """(body_start, tokens) for function_name's BODY, tokenized with
    spans. Refuses (rather than silently misaligning offsets) if the
    body contains a `//` comment: stripping it would shift character
    positions, and a `//` also lexically collides with SLASH in the
    tokenizer - this repo's real body (ExpectedDose's) has neither,
    checked, not assumed. Shared by every function-body mutation class
    (AOR, LVR) so the comment-safety check lives in exactly one place."""
    body_start, _body_end, body = _find_function_body_span(source, function_name)
    if "//" in body:
        raise SystemExit(
            f"dafny_mutate: {function_name!r}'s body contains a `//` comment - "
            "refusing to locate mutation sites rather than risk a "
            "misaligned offset or a comment slash mistaken for division"
        )
    return body_start, _tokenize_with_spans(body)


def _locate_function_body_arithmetic_sites(source, function_name):
    """Every arithmetic-operator token (+,-,*,/) within function_name's
    BODY, as (abs_start, abs_end, kind) tuples."""
    body_start, tokens = _function_body_tokens(source, function_name)
    return [
        (body_start + tstart, body_start + tend, kind)
        for kind, _value, tstart, tend in tokens
        if kind in _AR_TEXT
    ]


def _locate_function_body_numeric_literal_sites(source, function_name):
    """Every NUM-kind token within function_name's BODY, as
    (abs_start, abs_end, value) tuples - used by LVR. No comparison-
    operand/side information is tracked here (unlike the clause-level
    LVR locator) because function-body literals have no requires/ensures
    role to apply the magnitude-implication filter to at all - see
    generate_lvr_mutants."""
    body_start, tokens = _function_body_tokens(source, function_name)
    return [
        (body_start + tstart, body_start + tend, value)
        for kind, value, tstart, tend in tokens
        if kind == "NUM"
    ]


def _locate_clause_sites(source, method_name, keyword):
    """Every single-line `keyword` (requires/ensures) clause of
    method_name, as (code_start, code_end, code_text) absolute offsets
    into `source`. Mirrors dafny_nl_summary's single-line-clause
    convention and regex exactly (imported, not re-derived) - clauses
    spanning more than one line are simply not matched here, same as
    that module; this repo's real spec has none."""
    header_start, _header_end, header = _method_header_span(source, method_name)
    sites = []
    offset = 0
    for line in header.splitlines(keepends=True):
        m = _CLAUSE_LINE_RE.match(line)
        if m and m.group(1) == keyword and m.group(2).strip():
            abs_start = header_start + offset + m.start(2)
            abs_end = header_start + offset + m.end(2)
            sites.append((abs_start, abs_end, source[abs_start:abs_end]))
        offset += len(line)
    return sites


def _locate_clause_numeric_literal_sites(code_text):
    """Every NUM-kind token in one clause's text, paired with the
    comparison operator kind it's an operand of and which side it's on
    (needed by _lvr_trivial to determine narrowing vs widening).
    Every literal in this repo's real clauses sits immediately adjacent
    to a comparison operator in the flat token stream - no literal is
    buried inside a nested arithmetic sub-expression. Refuses (Tier 1)
    rather than guess a role if that assumption ever breaks, instead of
    silently treating an arithmetic-embedded literal as a bare
    comparison operand."""
    tokens = _tokenize_with_spans(code_text)
    sites = []
    for i, (kind, value, tstart, tend) in enumerate(tokens):
        if kind != "NUM":
            continue
        if i + 1 < len(tokens) and tokens[i + 1][0] in _CMP_TEXT:
            sites.append((tstart, tend, value, tokens[i + 1][0], True))
        elif i > 0 and tokens[i - 1][0] in _CMP_TEXT:
            sites.append((tstart, tend, value, tokens[i - 1][0], False))
        else:
            raise SystemExit(
                f"dafny_mutate: literal {value!r} in {code_text!r} is not "
                "adjacent to a comparison operator - refusing to guess its "
                "role rather than risk mutating an unrelated literal"
            )
    return sites


def _format_real_literal(value):
    """Dafny real literals always show a decimal point; two decimal
    places matches this module's +/-0.01 perturbation of literals that
    all start as the integer-valued real 0.0 in this repo's real spec."""
    return f"{value:.2f}"


def _generate_token_mutants(
    source, method_name, operator_label, text_map, implies_table, chain_aware=False
):
    mutants = []
    for keyword in ("requires", "ensures"):
        for code_start, _code_end, code_text in _locate_clause_sites(source, method_name, keyword):
            tokens = _tokenize_with_spans(code_text)
            group_ids = _chain_group_ids(tokens) if chain_aware else None
            for idx, (kind, _value, tstart, tend) in enumerate(tokens):
                if kind not in text_map:
                    continue
                abs_start = code_start + tstart
                abs_end = code_start + tend
                sibling_kinds = ()
                if chain_aware:
                    sibling_kinds = [
                        tokens[j][0]
                        for j in range(len(tokens))
                        if j != idx and group_ids[j] == group_ids[idx] and tokens[j][0] in text_map
                    ]
                for mutant_kind, mutant_text in text_map.items():
                    if mutant_kind == kind:
                        continue
                    mutated_clause = code_text[:tstart] + mutant_text + code_text[tend:]
                    mutated_source = source[:abs_start] + mutant_text + source[abs_end:]
                    if keyword == "ensures":
                        trivial = mutant_kind in implies_table.get(kind, set())
                    else:
                        trivial = kind in implies_table.get(mutant_kind, set())
                    filtered_reason = None
                    if trivial:
                        filtered_reason = f"statically weaker ({keyword})"
                    elif chain_aware and _chain_incompatible(mutant_kind, sibling_kinds):
                        filtered_reason = (
                            "chain-direction incompatible with a sibling comparison "
                            "in the same chain - would be a Dafny parse error, not a "
                            "semantic test (Dafny Reference Manual Sec 5.2.1-5.2.2)"
                        )
                    mutants.append(
                        Mutant(
                            operator=operator_label,
                            keyword=keyword,
                            original_clause=code_text,
                            mutated_clause=mutated_clause,
                            description=(
                                f"{operator_label} on {keyword} clause {code_text!r}: "
                                f"{text_map[kind]} -> {mutant_text}"
                            ),
                            mutated_source=mutated_source,
                            filtered_reason=filtered_reason,
                        )
                    )
    return mutants


def generate_ror_mutants(source, method_name):
    return _generate_token_mutants(
        source, method_name, "ROR", _CMP_TEXT, _CMP_IMPLIES, chain_aware=True
    )


def generate_lor_mutants(source, method_name):
    return _generate_token_mutants(source, method_name, "LOR", _LOGIC_TEXT, _LOGIC_IMPLIES)


def generate_aor_mutants(source, method_name, function_name=None):
    """AOR: requires/ensures clauses (present for symmetry with ROR/LOR
    - this repo's real spec's clauses contain no arithmetic, so this
    part contributes [] against dosage.dfy, confirmed by test, not just
    left unexercised) plus, when `function_name` is given, that
    function's BODY - part of the formal spec (referenced by a pinning
    ensures clause), never the target method's own trusted
    implementation body, which is never mutated. Restricted per
    MutDafny's own group rule (_ar_group_incompatible): a mutation can
    never introduce `/` where the original had none, eliminating the
    division-by-zero false-kill risk by construction."""
    mutants = _generate_token_mutants(source, method_name, "AOR", _AR_TEXT, _AR_IMPLIES)
    if function_name is not None:
        mutants += _generate_function_body_aor_mutants(source, function_name)
    return mutants


def _generate_function_body_aor_mutants(source, function_name):
    mutants = []
    for abs_start, abs_end, kind in _locate_function_body_arithmetic_sites(source, function_name):
        for mutant_kind, mutant_text in _AR_TEXT.items():
            if mutant_kind == kind:
                continue
            mutated_source = source[:abs_start] + mutant_text + source[abs_end:]
            incompatible = _ar_group_incompatible(kind, mutant_kind)
            mutants.append(
                Mutant(
                    operator="AOR",
                    keyword="function_body",
                    original_clause=f"{function_name} body operator {_AR_TEXT[kind]!r}",
                    mutated_clause=f"{function_name} body operator {mutant_text!r}",
                    description=(
                        f"AOR on {function_name}'s function body: "
                        f"{_AR_TEXT[kind]} -> {mutant_text}"
                    ),
                    mutated_source=mutated_source,
                    filtered_reason=(
                        "arithmetic-operator group incompatible (MutDafny's own "
                        "restriction: never introduce / from +/-/*, avoiding a "
                        "division-by-zero false-kill by construction)"
                        if incompatible
                        else None
                    ),
                )
            )
    return mutants


def generate_lvr_mutants(source, method_name, function_name=None):
    """LVR: is a comparison's LITERAL CONSTANT load-bearing, not just its
    operator (ROR) or the arithmetic combining it (AOR)? Every numeric
    literal in this repo's real spec is exactly 0.0 (requires/ensures
    clauses plus, when `function_name` is given, that companion
    function's body); each is mutated to `original +/- _LVR_DELTA`, the
    clinical-precision floor from
    gate_c5_mutation_testing_research_findings.md. Clause-level literals
    adjacent to LT/LE/GT/GE are filtered per _lvr_trivial's magnitude-
    implication principle; EQ/NE-adjacent and all function-body literals
    are never filtered (see _lvr_trivial and
    _locate_function_body_numeric_literal_sites' docstrings)."""
    mutants = []
    for keyword in ("requires", "ensures"):
        for code_start, _code_end, code_text in _locate_clause_sites(source, method_name, keyword):
            for tstart, tend, value, op_kind, literal_is_lhs in _locate_clause_numeric_literal_sites(
                code_text
            ):
                original_value = float(value)
                abs_start = code_start + tstart
                abs_end = code_start + tend
                for delta in (-_LVR_DELTA, _LVR_DELTA):
                    mutant_text = _format_real_literal(original_value + delta)
                    mutated_clause = code_text[:tstart] + mutant_text + code_text[tend:]
                    mutated_source = source[:abs_start] + mutant_text + source[abs_end:]
                    trivial = _lvr_trivial(keyword, op_kind, literal_is_lhs, delta)
                    mutants.append(
                        Mutant(
                            operator="LVR",
                            keyword=keyword,
                            original_clause=code_text,
                            mutated_clause=mutated_clause,
                            description=(
                                f"LVR on {keyword} clause {code_text!r}: "
                                f"{value} -> {mutant_text}"
                            ),
                            mutated_source=mutated_source,
                            filtered_reason=(
                                f"magnitude-implied ({keyword})" if trivial else None
                            ),
                        )
                    )
    if function_name is not None:
        mutants += _generate_function_body_lvr_mutants(source, function_name)
    return mutants


def _generate_function_body_lvr_mutants(source, function_name):
    mutants = []
    for abs_start, abs_end, value in _locate_function_body_numeric_literal_sites(
        source, function_name
    ):
        original_value = float(value)
        for delta in (-_LVR_DELTA, _LVR_DELTA):
            mutant_text = _format_real_literal(original_value + delta)
            mutated_source = source[:abs_start] + mutant_text + source[abs_end:]
            mutants.append(
                Mutant(
                    operator="LVR",
                    keyword="function_body",
                    original_clause=f"{function_name} body literal {value!r}",
                    mutated_clause=f"{function_name} body literal {mutant_text!r}",
                    description=(
                        f"LVR on {function_name}'s function body: {value} -> {mutant_text}"
                    ),
                    mutated_source=mutated_source,
                    filtered_reason=None,
                )
            )
    return mutants


def generate_coi_mutants(source, method_name):
    """Negate-and-reverify: a different question than ROR/LOR/AOR ask.
    Those ask "is this specific boundary load-bearing"; COI asks "does
    this clause constrain anything at all." Applies to `ensures` only -
    negating a `requires` clause does not test the same thing (it would
    just ask Z3-style vacuity questions pass 2 already covers)."""
    mutants = []
    for code_start, code_end, code_text in _locate_clause_sites(source, method_name, "ensures"):
        mutated_clause = f"!({code_text})"
        mutated_source = source[:code_start] + mutated_clause + source[code_end:]
        mutants.append(
            Mutant(
                operator="COI",
                keyword="ensures",
                original_clause=code_text,
                mutated_clause=mutated_clause,
                description=f"COI: negate ensures clause {code_text!r}",
                mutated_source=mutated_source,
                filtered_reason=None,
            )
        )
    return mutants


def generate_mutants(source, method_name, function_name=None):
    """Every mutant this module can generate for method_name, across all
    five implemented operator classes. SOR/HOR contribute nothing (not
    implemented - see module docstring). `function_name`, when given,
    extends AOR and LVR to that companion function's body (see
    generate_aor_mutants/generate_lvr_mutants) - dosage.dfy's real
    caller passes "ExpectedDose" here."""
    return (
        generate_ror_mutants(source, method_name)
        + generate_lor_mutants(source, method_name)
        + generate_aor_mutants(source, method_name, function_name=function_name)
        + generate_lvr_mutants(source, method_name, function_name=function_name)
        + generate_coi_mutants(source, method_name)
    )
