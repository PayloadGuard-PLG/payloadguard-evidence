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

v1 scope cut, named explicitly (matches direct guidance: "be careful
with Dafny... we can consider floating points later, it's a known but
solvable issue"): mutation sites are limited to single-line
requires/ensures clauses on the target METHOD's own header - the same
single-line convention Gate C6 already established. The one arithmetic
operator in this spec (`infusionRateMlPerHr * concentrationMgPerMl`)
lives inside `ExpectedDose`'s FUNCTION BODY, not a requires/ensures
clause, so it is out of this module's mutation-site scope; AOR's
generator exists and is exercised (returns an empty list against this
spec, confirmed by test, not just left unimplemented) but produces no
real mutants here. This is also exactly where the named risk lives: a
`/` mutant on `real` division can fail Dafny's own division-by-zero
check rather than because a postcondition caught the weakening, which
would need explicit failure-reason attribution to avoid a false "kill"
- deferred alongside function-body mutation, not solved here. Related
guidance for that follow-up: bound any future real-valued mutant/
comparison to the accuracy the dosage calculation actually requires
(e.g. do not demand more precision than an input on the order of 1e10
needs), rather than treating Dafny's exact arbitrary-precision `real` as
requiring unbounded exactness - a decision for that future work, named
here so it isn't lost.
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


def _generate_token_mutants(source, method_name, operator_label, text_map, implies_table):
    mutants = []
    for keyword in ("requires", "ensures"):
        for code_start, _code_end, code_text in _locate_clause_sites(source, method_name, keyword):
            for kind, _value, tstart, tend in _tokenize_with_spans(code_text):
                if kind not in text_map:
                    continue
                abs_start = code_start + tstart
                abs_end = code_start + tend
                for mutant_kind, mutant_text in text_map.items():
                    if mutant_kind == kind:
                        continue
                    mutated_clause = code_text[:tstart] + mutant_text + code_text[tend:]
                    mutated_source = source[:abs_start] + mutant_text + source[abs_end:]
                    if keyword == "ensures":
                        trivial = mutant_kind in implies_table.get(kind, set())
                    else:
                        trivial = kind in implies_table.get(mutant_kind, set())
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
                            filtered_reason=(
                                f"statically weaker ({keyword})" if trivial else None
                            ),
                        )
                    )
    return mutants


def generate_ror_mutants(source, method_name):
    return _generate_token_mutants(source, method_name, "ROR", _CMP_TEXT, _CMP_IMPLIES)


def generate_lor_mutants(source, method_name):
    return _generate_token_mutants(source, method_name, "LOR", _LOGIC_TEXT, _LOGIC_IMPLIES)


def generate_aor_mutants(source, method_name):
    """Present for symmetry with ROR/LOR and to keep the engine correct
    if a future spec's requires/ensures clauses ever contain arithmetic -
    but see the module docstring: this repo's real spec's only
    arithmetic operator lives in a function body, out of clause-mutation
    scope, so this returns [] against dosage.dfy today. Confirmed by
    test, not just left unexercised."""
    return _generate_token_mutants(source, method_name, "AOR", _AR_TEXT, _AR_IMPLIES)


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


def generate_mutants(source, method_name):
    """Every mutant this module can generate for method_name, across all
    four implemented operator classes. SOR/HOR contribute nothing (not
    implemented - see module docstring); AOR contributes nothing against
    this repo's real spec today (see generate_aor_mutants)."""
    return (
        generate_ror_mutants(source, method_name)
        + generate_lor_mutants(source, method_name)
        + generate_aor_mutants(source, method_name)
        + generate_coi_mutants(source, method_name)
    )
