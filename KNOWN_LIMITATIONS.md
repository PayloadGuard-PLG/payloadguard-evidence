# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-05 (deferred-gate work while Gate 1 output is under
Steven's review).

| Gate | Status | Summary |
|---|---|---|
| Gate 2 — CONFLICT rule definition | **BLOCKED on Steven** | Searched both authorized sources in full. The term does not appear in PayloadGuard-Evidence-Blueprint-1 (Drive doc id 154iVHHPkCbrNN6XQ_B07jS0LJG7VYKxtSPT8TEwmMwY; 0 case-insensitive occurrences; committed copy in-repo) nor in SYSTEM_BLUEPRINT.md (single occurrence is a to-do mention, line 162 — not a definition). Per the roadmap: stop, name it, ask. Closest neighbouring concept found: Blueprint Phase 2 acceptance (b) — intent-vs-reality mismatch "raises a GAP/flag". Semantics will not be inferred from the name. Test case recorded per the Gate 1 remediation prompt: when a definition lands, evaluate it against REQ-GIP-1-4-12's alarm-scope split — is a requirement with evidence at one scope and an explicit GAP at another a CONFLICT or a different category? Open, not decided. |
| Gate 3 — bounds enforcement via CrossHair API | **INVESTIGATED — decision pending (re-capture would move Gate 1's ground truth mid-review)** | Findings below. |
| Gate 4 — binding authorship | **OPTIONS PREPARED — decision slots into Gate 2** | Options below. |
| Gate 5 — single-evidence-type fixture for variant C | **RESOLVED (symbolic-only); concrete-only impossible pre-Gate-2, named** | `tests/test_single_evidence_type.py`: in-memory fixture requirement with symbolic evidence only, driven through the real variant C builder — appears in exactly one artifact (symbolic 1 row, concrete 0 rows), intent projected per R1. Committed data untouched. A concrete-only fixture cannot exist yet: the current C builder binds a symbolic record to every requirement unconditionally (see Gate 4 note 3). |
| Gate 6 — FRN pump-type tag | **BLOCKED on Steven** | Needs a one-line definition; all in-repo/web resolution attempts previously failed; no inference will be made. |
| Phase C interface: `verifier_completion_status` on VerificationResult | **NOTED for Gate 2** | The Gate 2 binder/schema must reserve room for this field (Blueprint false-zero trap) and keep strength-assignment adapter-scoped so PROVEN remains structurally impossible for CrossHair/pytest-backed requirements even after the Dafny adapter exists. |

## Gate 3 findings (crosshair-tool 0.0.107, investigated 2026-07-05)

Verified against the installed package, not documentation:

- `per_condition_timeout` — CLI-enforceable (`--per_condition_timeout`);
  already enforced since Turn 2.0 B1.
- `max_iterations` — **not** exposed by the CLI (which offers only
  `--max_uninteresting_iterations`), but **is** exposed by the Python API:
  `crosshair.options.AnalysisOptions.max_iterations` (default
  `sys.maxsize`), settable via
  `analyze_function(fn, AnalysisOptionSet(max_iterations=...))`.
- `seed` — **not settable at any interface.** The solver seed is
  hard-coded: `crosshair/statespace.py:750-751` sets
  `solver.set("random-seed", 42)` and `solver.set("smt.random-seed", 42)`.
  The metadata's declared `seed: 1` is unenforceable at this tool version;
  the tool pins its own seed of 42. This is a hard tool-version
  limitation.

Options for the decision (post-Gate-1-review, since either re-capture
changes the artifacts currently under review):

1. **API harness (fuller enforcement):** replace the CLI subprocess in the
   evidence-path runners with a Python-API harness enforcing
   `per_condition_timeout=30, max_iterations=100000`; record both in
   `effective_bounds`; document seed as tool-fixed-42. Cost: the captured
   raw output becomes the harness's rendering of API messages rather than
   verbatim CLI stdout — a change to the capture format that Phase A's
   discipline treated as load-bearing.
2. **Stay CLI (current state):** keep verbatim CLI capture; document
   `max_iterations` as enforceable-only-via-API (an interface limitation,
   not a tool limitation) and seed as tool-fixed. Weaker enforcement,
   stronger capture fidelity.

Either way, the declared `seed: 1` can never be demonstrated on 0.0.107
and the enforcement_note should be updated to say "seed is hard-coded to
42 by the tool" once the decision lands.

## Gate 4 options (binding authorship — slots into the Gate 2 binder design)

1. **Metadata-authored everywhere (A/B model):** the binder consumes only
   bindings declared in metadata; C's evidence-store `requirement_id`
   channel is dropped. Pro: single review surface, authorship errors live
   in one place. Con: evidence stores stop being self-describing;
   concrete evidence must be double-entered (in CASES and in metadata).
2. **Evidence-store-carried everywhere (C model):** bindings live with the
   evidence (each record names its requirement). Pro: no duplication;
   evidence is portable. Con: binding errors move into test/capture files
   that regulatory reviewers are less likely to read; metadata no longer
   shows the full evidence picture.
3. **Both, with precedence + cross-check (recommended for evaluation):**
   metadata declarations are authoritative where present; store-carried
   ids are validated against them, and a disagreement is a hard generation
   failure (Tier 1). Pro: keeps A/B's review surface and C's portability
   while turning the asymmetry into a consistency check. Con: most
   machinery; needs the (blocked) CONFLICT rule semantics if "disagreement"
   is to be rendered rather than fatal.

Design input from Gate 5 work: the current C builder binds a symbolic
record to every requirement by construction and does not verify the
requirement's `implementation` against the capture manifest's `target` —
the Gate 2 binder must bind symbolic evidence by verified code-location
match, whichever authorship model is chosen.

## Session-scope note (2026-07-05, Turn B4)

The Phase B v3 prompt's Turn B4/B5 spec bodies arrived as placeholder
text; the companion roadmap was supplied separately and is committed as
`payloadguard-evidence-roadmap-phaseB-to-C.md` — its Gate 1 section defines
Turn B4's scope (minimal pipeline, four real variant artifacts as ground
truth, reviewed by Steven before Gate 2 starts). "Four real files" is read
as the four variant JSON artifacts (a / b / symbolic / concrete, each with
its Markdown sibling); the base matrix remains the frozen legacy symbolic
subset per ruling R2c, as the roadmap's own verified-state section records.
