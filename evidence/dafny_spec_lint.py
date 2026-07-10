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

    Extended 2026-07-10 (drug_interaction_checker.dfy's Gate C3): a
    parameter typed as a simple Dafny `datatype` - every constructor
    zero-argument, e.g. `datatype DOAC = Apixaban | Dabigatran | ...` -
    is now modeled as a Z3 EnumSort when a `requires` clause actually
    compares it (`doac == Apixaban`). This is the exact gap
    renal_adjustment's own Gate C3 build never had to close: every
    datatype-typed parameter in dosage.dfy/renal_adjustment.dfy that a
    requires clause referenced was already real/int/nat/bool underneath,
    and the one genuinely datatype-typed parameter (AssessRenalFunction's
    `formula: Formula`) was never referenced by its one requires clause,
    so the "only model referenced parameters" narrowing sidestepped it
    entirely. drug_interaction_checker.dfy's precondition, `requires
    !(doac == Apixaban && agent in {...})` (written as an explicit
    disjunction, not this set-literal form, but comparing datatype values
    either way), references two datatype-typed parameters directly -
    confirmed to refuse before this extension existed
    (SystemExit: "unsupported Dafny parameter type 'DOAC'"). A
    *parameterized* constructor (e.g. `InteractionResult(outcome: ...,
    direction: ...)`) is still refused, unchanged - EnumSort only
    represents a finite set of nullary values, not a real datatype with
    fields, and this module still refuses rather than guessing a
    representation for those.

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

import itertools
import re

import z3

# Z3 registers EnumSort names globally per context, not per call - two
# separate build_symbol_table() calls that both happen to model a Dafny
# datatype named e.g. "Formula" (a real collision across two different
# test fixtures, caught empirically: "enumeration sort name is already
# declared") would otherwise clash. A monotonic per-call tag keeps every
# call's sorts distinct regardless of how many times a type name recurs
# across this process's lifetime.
_ENUM_SORT_CALL_COUNTER = itertools.count()

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
    """Return the source text from `method <name>(` or `function <name>(`
    up to (not including) the body's opening brace - the region
    requires/ensures/etc. clauses live in. Matches either keyword since a
    Dafny `function`'s header (requires/ensures/params) has the same shape
    as a `method`'s for the purposes of every caller of this helper -
    Gate C6's renal-adjustment functions surfaced this gap empirically
    (2026-07-08): every earlier caller of this module only ever ran
    against dosage.dfy's one `method`, so the `function`-only case was
    untested until then. Refuses if neither keyword's declaration or its
    body brace can be found, rather than guessing at a truncated header."""
    m = re.search(rf"\b(?:method|function)\s+{re.escape(method_name)}\s*\(", source)
    if not m:
        raise SystemExit(
            f"no method or function named {method_name!r} found in Dafny source"
        )
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


_DATATYPE_DECL_RE = re.compile(
    r"\bdatatype\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
    r"(?P<body>.*?)"
    r"(?=\bdatatype\b|\bfunction\b|\bmethod\b|\Z)",
    re.DOTALL,
)
_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _parse_enum_datatypes(source):
    """Find every `datatype Name = C1 | C2 | ...` declaration in source
    whose constructors are ALL zero-argument (a finite enumeration, e.g.
    `datatype DOAC = Apixaban | Dabigatran | Edoxaban | Rivaroxaban`) -
    representable as a Z3 EnumSort. A datatype with any parameterized
    constructor (e.g. `InteractionResult(outcome: Outcome, direction:
    RiskDirection)`) is simply not included here, not silently
    misrepresented - callers still refuse on it via the normal
    unsupported-type path. Declarations may span multiple lines (Dafny
    doesn't require them on one line); line comments are stripped first
    so a commented-out constructor never leaks in as real content.
    Returns {datatype_name: [constructor_names]}."""
    source_nc = re.sub(r"//[^\n]*", "", source)
    enums = {}
    for m in _DATATYPE_DECL_RE.finditer(source_nc):
        name = m.group("name")
        parts = [p.strip() for p in m.group("body").split("|")]
        parts = [p for p in parts if p]
        if parts and all(_IDENTIFIER_RE.fullmatch(p) for p in parts):
            enums[name] = parts
    return enums


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

    def _apply_cmp(self, kind, a, b):
        """EQ/NE work for any Z3 sort (Bool, Int, Real, or an EnumSort
        built by build_symbol_table for a simple Dafny datatype) - Z3's
        generic equality is universal. LE/GE/LT/GT are only meaningful
        for arithmetic (int/real) operands: Z3's Python bindings simply
        don't overload <=/</>/>= for DatatypeRef at all (confirmed
        empirically - a naive `a <= b` between two EnumSort constants
        raises a raw Python TypeError, not a clean refusal, found while
        mutation-testing drug_interaction_checker.dfy's precondition:
        Gate C5's ROR generator has no reason to know this translator
        can't handle an ordering operator it happily generates as a
        candidate mutant). Dafny's OWN semantics may define some
        ordering for other types (e.g. a structural "rank" order on
        datatypes, used for termination metrics) - this translator does
        not attempt to replicate that, and refuses cleanly rather than
        crash or silently mistranslate."""
        if kind in ("LE", "GE", "LT", "GT") and not (z3.is_arith(a) and z3.is_arith(b)):
            raise SystemExit(
                f"unsupported comparison in {self.clause_desc}: {kind!r} "
                "(</<=/>/>=) is only modeled for real/int/nat operands - "
                "refusing rather than crash or guess an ordering for a "
                "non-arithmetic (e.g. datatype) sort"
            )
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


def build_symbol_table(params, enums=None):
    """{name: dafny_type} -> ({name: z3 var}, [implicit constraints]).
    `nat` gets an implicit >= 0 constraint (Dafny's own semantics).

    `enums` is an optional {datatype_name: [constructor_names]} map (see
    _parse_enum_datatypes) for simple, zero-argument-constructor Dafny
    datatypes - represented as a Z3 EnumSort, one per distinct enum type
    referenced, memoized within this call so two parameters of the same
    enum type share one sort. Each constructor name becomes a resolvable
    symbol too (e.g. `Apixaban`), the same way `true`/`false` already
    resolve as literals in _Parser._atom - no parser changes needed for
    this to work, since it's just more entries in the same symbol table.

    Any type that is neither real/int/nat/bool nor a known simple enum -
    including a parameterized datatype constructor, which EnumSort can't
    represent at all - is refused rather than guessed at, unchanged."""
    enums = enums or {}
    symbols = {}
    implicit = []
    enum_sorts = {}
    call_tag = next(_ENUM_SORT_CALL_COUNTER)
    for name, ty in params.items():
        if ty in _TYPE_MAP:
            var = _TYPE_MAP[ty](name)
            symbols[name] = var
            if ty == "nat":
                implicit.append(var >= 0)
        elif ty in enums:
            if ty not in enum_sorts:
                sort, values = z3.EnumSort(f"{ty}#{call_tag}", enums[ty])
                const_map = dict(zip(enums[ty], values))
                for cname, cval in const_map.items():
                    if cname in symbols:
                        raise SystemExit(
                            f"name collision: {cname!r} is both a parameter "
                            "and a datatype constructor - refusing rather "
                            "than guessing which one a clause means"
                        )
                    symbols[cname] = cval
                enum_sorts[ty] = sort
            symbols[name] = z3.Const(name, enum_sorts[ty])
        else:
            raise SystemExit(
                f"unsupported Dafny parameter type {ty!r} for {name!r} - "
                "only real/int/nat/bool and simple (zero-argument-"
                "constructor) datatypes are modeled; refusing rather than "
                "guessing a Z3 representation"
            )
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
    "sat" / "unsat" / "unknown".

    Only builds Z3 symbols for parameters actually referenced by a
    `requires` clause - a parameter of an unsupported type (e.g. a
    parameterized Dafny datatype like `InteractionResult`) that no
    precondition mentions doesn't need a Z3 representation to answer "is
    this conjunction satisfiable," and refusing on it anyway would be
    refusing to check a clause that never touches it. A referenced
    identifier of an unsupported type still refuses, unchanged - this
    only narrows what counts as "referenced." Found empirically:
    renal_adjustment.dfy's AssessRenalFunction takes a `Formula`-typed
    parameter its one requires clause never mentions. A *simple* Dafny
    datatype (every constructor zero-argument, e.g. `DOAC`) that a
    requires clause DOES reference is modeled as a Z3 EnumSort - see
    _parse_enum_datatypes/build_symbol_table; found empirically the same
    way, drug_interaction_checker.dfy's precondition compares `doac`/
    `agent` directly."""
    params = _parse_params(_find_method_header(source, method_name))
    clauses = extract_requires_clauses(source, method_name)
    if not clauses:
        return "sat", "no requires clauses on this method - trivially satisfiable"

    combined = " ".join(clauses)
    referenced = {
        name for name in params
        if re.search(rf"\b{re.escape(name)}\b", combined)
    }
    relevant_params = {name: ty for name, ty in params.items() if name in referenced}
    enums = _parse_enum_datatypes(source)
    symbols, implicit = build_symbol_table(relevant_params, enums)

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
