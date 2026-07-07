"""Phase C, Gate C3: hardening against three of the four named Dafny
output-parsing/proof vulnerabilities (the fourth, specification stripping,
stays BLOCKED - see KNOWN_LIMITATIONS.md - its source material was never
available to scope it). This module lints the Dafny SOURCE TEXT itself;
evidence/dafny_adapter.py parses CAPTURED VERIFIER OUTPUT - the two vectors
that need output parsing (false-zero, timeout/resource masking) live there,
the two that need spec inspection (vacuous preconditions, weak
postconditions) live here.

Vector 1 - vacuous proofs from contradictory preconditions
    A `requires` clause that can never be true (e.g. `x > 0 && x < 0`) makes
    every postcondition hold vacuously - Dafny reports a clean pass with no
    hint anything is wrong (confirmed empirically on the real 4.11.0 binary,
    see examples/dosage_calculator/vacuous_precondition_probe.dfy). This
    module extracts a method's `requires` clauses and hands their
    conjunction to Z3 for a real satisfiability check, rather than trusting
    Dafny's own report. A tiny, explicitly scoped expression translator
    handles the boolean/arithmetic/comparison subset actually used in this
    repo's specs (&&, ||, !, ==>, <==>, chained comparisons, +-*/, real/int/
    bool literals and identifiers) - anything else (quantifiers, function
    calls, old-expressions, sequences/sets/maps, ...) is refused outright,
    Tier 1, rather than silently mistranslated or skipped.

Vector 2 - weak postconditions (heuristic, best-effort, NOT a full proof,
    named as such in the roadmap): a one-way implication (`==>`) in an
    `ensures` clause can let a broken implementation vacuously satisfy the
    spec whenever the antecedent is false, where a bi-implication (`<==>`)
    would have pinned down both directions. scan_weak_postconditions flags
    such clauses for human review; it does not and cannot decide whether a
    bi-implication was actually "needed" for a given spec - that is a
    design judgment call the roadmap explicitly scopes out of automation.

Vector 3 (timeout/resource-limit masking) lives in evidence/dafny_adapter.py,
not here - see that module for the real, empirically-confirmed
"N out of resource" finding and how the false-zero guard was hardened
against it.
"""

import re

import z3

_CLAUSE_KEYWORDS = ("requires", "ensures", "modifies", "reads", "decreases")

_DISALLOWED_IDENTIFIERS = {
    "forall", "exists", "old", "fresh", "allocated", "in", "then", "if",
    "else", "this", "new",
}

_TOKEN_RE = re.compile(
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
    | (?P<NUM>\d+\.\d+|\d+)
    | (?P<ID>[A-Za-z_][A-Za-z0-9_']*)
    """,
    re.VERBOSE,
)
_WS_RE = re.compile(r"\s*")

_CMP_KINDS = {"LE", "GE", "EQ", "NE", "LT", "GT"}

_TYPE_MAP = {
    "real": z3.Real,
    "int": z3.Int,
    "nat": z3.Int,
    "bool": z3.Bool,
}


# --------------------------------------------------------------- extraction

def _find_method_header(source, method_name):
    """Return the source text from `method <name>(` up to (not including)
    the method body's opening brace - the region requires/ensures/etc.
    clauses live in. Refuses if the method or its body brace can't be
    found, rather than guessing at a truncated header."""
    m = re.search(rf"\bmethod\s+{re.escape(method_name)}\s*\(", source)
    if not m:
        raise SystemExit(f"no method named {method_name!r} found in Dafny source")
    depth = 0
    i = m.end() - 1
    while i < len(source):
        c = source[i]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c == "{" and depth == 0:
            return source[m.start():i]
        i += 1
    raise SystemExit(
        f"could not find the method body opening brace for {method_name!r}; "
        "refusing to guess where the header ends"
    )


def _parse_params(header):
    """Extract {name: dafny_type} from the method's parameter list (the
    first top-level parenthesized group in the header)."""
    m = re.search(r"\((.*?)\)", header, re.DOTALL)
    params = {}
    if m and m.group(1).strip():
        for part in m.group(1).split(","):
            part = part.strip()
            if not part:
                continue
            name, _, ty = part.partition(":")
            if not ty:
                raise SystemExit(
                    f"parameter {name.strip()!r} has no declared type; "
                    "refusing to guess a Z3 representation"
                )
            params[name.strip()] = ty.strip()
    return params


def _extract_clauses(source, method_name, keyword):
    """Every clause introduced by `keyword` (requires/ensures/...) in
    method_name's header, in source order, with line comments stripped
    first so a commented-out clause never leaks in as real content."""
    header = _find_method_header(source, method_name)
    header_nc = re.sub(r"//[^\n]*", "", header)
    tokens = re.split(rf"\b({'|'.join(_CLAUSE_KEYWORDS)})\b", header_nc)
    clauses = []
    for idx in range(1, len(tokens), 2):
        if tokens[idx] == keyword:
            text = tokens[idx + 1].strip()
            if text:
                clauses.append(text)
    return clauses


def extract_requires_clauses(source, method_name):
    return _extract_clauses(source, method_name, "requires")


def extract_ensures_clauses(source, method_name):
    return _extract_clauses(source, method_name, "ensures")


# ---------------------------------------------------------- Z3 translation

def _tokenize(expr, clause_desc):
    tokens = []
    pos = 0
    n = len(expr)
    while True:
        pos = _WS_RE.match(expr, pos).end()
        if pos >= n:
            return tokens
        m = _TOKEN_RE.match(expr, pos)
        if not m:
            raise SystemExit(
                f"unsupported syntax in {clause_desc}, cannot translate to "
                f"Z3: {expr[pos:pos + 20]!r}"
            )
        kind = m.lastgroup
        value = m.group()
        pos = m.end()
        if kind == "ID" and value in _DISALLOWED_IDENTIFIERS:
            raise SystemExit(
                f"unsupported construct {value!r} in {clause_desc} - "
                "quantifiers/old-expressions/etc. are out of scope for this "
                "checker; refusing rather than guessing"
            )
        tokens.append((kind, value))


class _Parser:
    """Minimal recursive-descent parser for the boolean/arithmetic subset of
    Dafny expressions actually used in this repo's requires/ensures clauses.
    Anything outside that subset raises SystemExit rather than being
    mistranslated or silently dropped."""

    def __init__(self, tokens, symbols, clause_desc):
        self.tokens = tokens
        self.i = 0
        self.symbols = symbols
        self.clause_desc = clause_desc

    def _peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def _advance(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def _expect(self, kind):
        k, v = self._peek()
        if k != kind:
            raise SystemExit(
                f"expected {kind} in {self.clause_desc}, got {v!r} instead"
            )
        return self._advance()

    def parse(self):
        expr = self._iff()
        if self.i != len(self.tokens):
            raise SystemExit(
                f"trailing unparsed tokens in {self.clause_desc}: "
                f"{self.tokens[self.i:]}"
            )
        return expr

    def _iff(self):
        left = self._imp()
        while self._peek()[0] == "EQIMP":
            self._advance()
            left = left == self._imp()
        return left

    def _imp(self):
        left = self._or()
        if self._peek()[0] == "IMP":
            self._advance()
            return z3.Implies(left, self._imp())  # right-associative
        return left

    def _or(self):
        left = self._and()
        while self._peek()[0] == "OR":
            self._advance()
            left = z3.Or(left, self._and())
        return left

    def _and(self):
        left = self._not()
        while self._peek()[0] == "AND":
            self._advance()
            left = z3.And(left, self._not())
        return left

    def _not(self):
        if self._peek()[0] == "NOT":
            self._advance()
            return z3.Not(self._not())
        return self._cmp()

    def _cmp(self):
        operands = [self._add()]
        kinds = []
        while self._peek()[0] in _CMP_KINDS:
            kinds.append(self._advance()[0])
            operands.append(self._add())
        if not kinds:
            return operands[0]
        parts = [
            self._apply_cmp(kind, operands[idx], operands[idx + 1])
            for idx, kind in enumerate(kinds)
        ]
        return parts[0] if len(parts) == 1 else z3.And(*parts)

    @staticmethod
    def _apply_cmp(kind, a, b):
        return {
            "LE": lambda: a <= b,
            "GE": lambda: a >= b,
            "EQ": lambda: a == b,
            "NE": lambda: a != b,
            "LT": lambda: a < b,
            "GT": lambda: a > b,
        }[kind]()

    def _add(self):
        left = self._mul()
        while self._peek()[0] in ("PLUS", "MINUS"):
            kind = self._advance()[0]
            right = self._mul()
            left = left + right if kind == "PLUS" else left - right
        return left

    def _mul(self):
        left = self._unary()
        while self._peek()[0] in ("STAR", "SLASH"):
            kind = self._advance()[0]
            right = self._unary()
            left = left * right if kind == "STAR" else left / right
        return left

    def _unary(self):
        if self._peek()[0] == "MINUS":
            self._advance()
            return -self._unary()
        return self._atom()

    def _atom(self):
        kind, value = self._peek()
        if kind == "LPAREN":
            self._advance()
            expr = self._iff()
            self._expect("RPAREN")
            return expr
        if kind == "NUM":
            self._advance()
            return z3.RealVal(value) if "." in value else z3.IntVal(value)
        if kind == "ID":
            self._advance()
            if value == "true":
                return z3.BoolVal(True)
            if value == "false":
                return z3.BoolVal(False)
            if value not in self.symbols:
                raise SystemExit(
                    f"unknown identifier {value!r} in {self.clause_desc} - "
                    "not a declared parameter; refusing to guess its type"
                )
            return self.symbols[value]
        raise SystemExit(f"unexpected token in {self.clause_desc}: {value!r}")


def build_symbol_table(params):
    """{name: dafny_type} -> ({name: z3 var}, [implicit constraints]).
    `nat` gets an implicit >= 0 constraint (Dafny's own semantics); any
    type outside real/int/nat/bool is refused rather than guessed at."""
    symbols = {}
    implicit = []
    for name, ty in params.items():
        if ty not in _TYPE_MAP:
            raise SystemExit(
                f"unsupported Dafny parameter type {ty!r} for {name!r} - "
                "only real/int/nat/bool are modeled; refusing rather than "
                "guessing a Z3 representation"
            )
        var = _TYPE_MAP[ty](name)
        symbols[name] = var
        if ty == "nat":
            implicit.append(var >= 0)
    return symbols, implicit


def translate_clause(expr_text, symbols, clause_desc):
    tokens = _tokenize(expr_text, clause_desc)
    if not tokens:
        raise SystemExit(f"empty {clause_desc}")
    return _Parser(tokens, symbols, clause_desc).parse()


# -------------------------------------------------------------- vector 1

def check_precondition_satisfiability(source, method_name):
    """Gate C3 vector 1: extract every `requires` clause for method_name and
    ask Z3 whether their conjunction is satisfiable, independent of whatever
    Dafny itself reported. Returns (verdict, detail) with verdict one of
    "sat" / "unsat" / "unknown"."""
    params = _parse_params(_find_method_header(source, method_name))
    symbols, implicit = build_symbol_table(params)
    clauses = extract_requires_clauses(source, method_name)
    if not clauses:
        return "sat", "no requires clauses on this method - trivially satisfiable"

    constraints = list(implicit)
    for idx, clause in enumerate(clauses):
        desc = f"requires clause {idx + 1} of {method_name!r} ({clause!r})"
        constraints.append(translate_clause(clause, symbols, desc))

    solver = z3.Solver()
    solver.add(*constraints)
    outcome = solver.check()
    if outcome == z3.sat:
        return "sat", f"model: {solver.model()}"
    if outcome == z3.unsat:
        return (
            "unsat",
            "precondition is unsatisfiable - every postcondition holds "
            "vacuously; a Dafny 'clean pass' on this method proves nothing",
        )
    return "unknown", "Z3 could not decide satisfiability (result: unknown)"


# -------------------------------------------------------------- vector 2

def scan_weak_postconditions(source, method_name):
    """Gate C3 vector 2 (heuristic, best-effort - see module docstring):
    flag every `ensures` clause that uses a one-way implication (==>)
    without also being a bi-implication (<==>). Returns a list of warning
    strings; empty means nothing was flagged. This is a lint, not a proof -
    it cannot know whether a bi-implication was actually warranted for a
    given spec."""
    warnings = []
    for clause in extract_ensures_clauses(source, method_name):
        if "<==>" in clause:
            continue
        if "==>" in clause:
            warnings.append(
                "one-way implication (==>) in ensures clause - review "
                "whether a bi-implication (<==>) would more tightly "
                f"constrain the specification: {clause}"
            )
    return warnings
