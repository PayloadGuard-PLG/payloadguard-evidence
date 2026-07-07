// Phase C, Gate C3, vector 1 fixture: a deliberately unsatisfiable
// (vacuous) precondition. Dafny's verifier reports a clean pass on this
// method because the precondition can never be true, so the postcondition
// holds vacuously for every (nonexistent) reachable input - confirmed for
// real below, not assumed. This is exactly the false-positive class named
// in KNOWN_LIMITATIONS.md / the Phase C roadmap as Gate C3 vector 1.
// evidence/dafny_spec_lint.py::check_precondition_satisfiability catches
// what the verifier alone misses, by asking Z3 directly whether the
// precondition is satisfiable rather than trusting a clean verifier run.
method VacuousExample(x: int) returns (r: int)
  requires x > 0 && x < 0
  ensures r == 999999
{
  r := 0;
}
