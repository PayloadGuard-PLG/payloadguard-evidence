# KNOWN_LIMITATIONS — gate ledger

Standing rule (Phase B working principle): open questions are resolved at
the gate where they are hit, documented inline; anything not resolvable in
a session is named here with a reason — never silently dropped.

Last updated: 2026-07-05 (Turn B4).

| Gate | Status | Reason / next step |
|---|---|---|
| Gate 3 — bounds enforcement via CrossHair API (`max_iterations`/`seed` beyond the CLI) | **DEFERRED — not hit in B4** | B4 never touches capture invocation (captures are committed evidence; the pipeline refuses to re-run them). The gate is hit when capture runners are next revised; investigate the CrossHair Python API then, wire through if exposed, re-run fact-equality. Until then the enforcement_note in every manifest and bounds block remains the honest record. |
| Gate 4 — binding authorship (RECONCILIATION asymmetry 2: metadata-authored A/B vs evidence-store-carried C) | **DEFERRED — B5 decision** | This is the central design decision of the vocabulary-agnostic binder (Turn B5), which is gated on Steven's approval of B4 output. Deciding it inside B4 would preempt the binder design. Both models currently coexist, documented in RECONCILIATION.md. |
| Gate 5 — single-evidence-type fixture for variant C | **DEFERRED — B5 prerequisite** | Needed before variant C's binder path can be tested independently; belongs with the B5 binder tests. Current data has both evidence types on every requirement, so the property is enforced by construction but unexercised (RECONCILIATION finding 4). |
| Gate 6 — FRN pump-type tag | **BLOCKED on Steven** | Insufficient information to act: needs a one-line definition from a source. All prior resolution attempts failed (web search; UPenn pages unreachable — see example README). No inference will be made. |
| Phase C interface: `verifier_completion_status` field on VerificationResult | **NOTED for B5** | Out of scope for this session's build, but the B5 binder design must leave room for it so the Dafny/Z3 adapters (Phase C) do not force a schema break. Recorded here so B5 inherits the consideration. |

Session-scope note (2026-07-05): the Phase B v3 prompt's Turn B4/B5 spec
bodies arrived as placeholder text; the companion roadmap was supplied
separately and is committed as
`payloadguard-evidence-roadmap-phaseB-to-C.md` — its Gate 1 section defines
Turn B4's scope (minimal pipeline, four real variant artifacts as ground
truth, reviewed by Steven before Gate 2 starts). Turn B4 was implemented
against that scope plus the VERIFIED STATE report for bf57888. "Four real
files" is read as the four variant JSON artifacts (a / b / symbolic /
concrete, each with its Markdown sibling); the base matrix remains the
frozen legacy symbolic subset per ruling R2c, as the roadmap's own
verified-state section records.
