# PayloadGuard Evidence Layer — Roadmap: Phase B → Phase C

Committed 2026-07-05 as supplied by Steven (companion to the Phase B v3
build prompt). Source of truth for gate order and Phase C interface
constraints.

## Where we are (verified, bf57888)

- Phase A closed (R1–R3).
- Turn 2.0 / B1–B3 shipped: bounds reconciled at the capture layer,
  fact-equality gate mechanized, two-tier review protocol codified.
- 15 tests passing. Four-variant fact-equality holding (7 facts; A/B/C
  equal; base = frozen legacy symbolic subset).

## Guiding principle for everything below

Open questions get resolved at the gate where they're first encountered,
with the resolution documented inline — not batched and left for a "later
phase" that never gets scoped. If a gate can't be resolved when reached,
it gets named explicitly as blocked, and why — never silently skipped or
carried forward to compound later.

## Phase B — remaining scope, in build order

### Gate 1 — End-to-end artifact generation (build this FIRST)

- Why first: there's currently no way to look at real throughput. Get the
  CLI and renderers producing actual traceability_matrix.json/.md for the
  toy dosage calculator, across all four variants, before finishing the
  rest of the binder work. This becomes ground truth — everything after
  this point gets debugged against real output, not assumptions.
- Minimal CLI, using what B1–B3 already provide (CrossHair adapter,
  fact-equality gate, two-tier review) — doesn't need the
  vocabulary-agnostic binder or CONFLICT rule to produce a first real
  output.
- Deliverable: four real files, reviewed by Steven, before Gate 2 starts.

### Gate 2 — Vocabulary-agnostic binder + CONFLICT rule

- Generalize the binder so one implementation drives all four schema
  variants (base/A/B/C) instead of separate generator scripts.
- CONFLICT rule: locate its exact definition in
  PayloadGuard-Evidence-Blueprint-1 (Drive) or SYSTEM_BLUEPRINT.md before
  implementing. If not precisely specified in either — this is a blocked
  gate: stop, name it, ask Steven. Do not infer semantics from the name
  alone.
- Test against Gate 1's real output as ground truth, not a hand-typed
  exemplar.

### Gate 3 — Bounds enforcement via CrossHair API

- Known gap: crosshair-tool 0.0.107 can't CLI-enforce
  max_iterations/seed. Investigate whether the CrossHair Python API
  (rather than the CLI) exposes these.
- If yes: wire it through, re-capture, confirm the fact-equality gate
  still holds with the tightened bounds.
- If no: document as a hard tool-version limitation in
  KNOWN_LIMITATIONS.md — an explicit, named constraint, not a silent
  omission.

### Gate 4 — Binding authorship asymmetry (RECONCILIATION.md asymmetry 2)

- Metadata-authored in A/B vs. evidence-store-carried in C. Decide which
  model Gate 2's generalized binder actually follows for variant C, or
  explicitly support both with a documented reason they differ.
- Previously deferred without a target phase — bringing it into Phase B
  explicitly, since Gate 2 will otherwise have to guess.

### Gate 5 — Single-evidence-type fixture for variant C

- Open per current state. Needs a concrete fixture before variant C's
  binder path can be tested independently of A/B.

### Gate 6 — FRN (unresolved)

- Named as open without further detail available. Needs a one-line
  definition from Steven of what FRN refers to before this can be scoped
  as an actionable gate at all.

## Phase C — interface contract to design NOW, build LATER

Even though building the Dafny/Z3 adapter is out of scope for Phase B, the
binder and schema from Gate 2 need to be shaped so Phase C doesn't force a
rework. Two things matter today:

1. **The false-zero trap.** A Dafny run reporting "0 errors" can mean
   genuinely proven, or a silent timeout. The eventual parser must assert
   the literal substring "0 errors" and independently confirm the verifier
   actually completed — not timed out — before ever emitting PROVEN. This
   is a schema constraint now: the VerificationResult record needs room
   for a verifier-completion-status field, or Phase C will have nowhere to
   put that information without breaking Phase B's frozen schema.
2. **PROVEN's exclusivity.** R2 (assert_no_realized_proven) currently
   guarantees PROVEN never appears as a realized strength anywhere in
   Phase B. Phase C's job is narrowly to earn the right to lift that
   guarantee for Dafny-backed requirements only — CrossHair/pytest-backed
   requirements must never be able to claim PROVEN even after the Dafny
   adapter exists. Gate 2's binder needs to keep strength-assignment
   adapter-scoped so this stays true structurally, not by convention.

## What "done" looks like for this roadmap

Every gate above resolved, blocked-and-named, or explicitly deferred with
a stated reason — never silently dropped. When Phase C starts, the Dafny
adapter plugs into a binder and schema that already anticipated it.
