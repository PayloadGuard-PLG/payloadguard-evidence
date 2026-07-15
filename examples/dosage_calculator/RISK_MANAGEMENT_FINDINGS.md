# Risk Management Findings — dosage_calculator (provisional)

**Status:** PROVISIONAL — working ledger, not a closed document.
**Covers:** `RISK_MANAGEMENT_PLAN.md` and `HAZARD_REGISTER.md`, this
example only.
**Purpose:** single point of reference for every finding raised against
these two artifacts to date, whether resolved or open, so a reader
doesn't need the original chat session or the standalone audit report
to know current state.
**Last updated:** 2026-07-15.

---

## Status ledger

| # | Finding | Verdict | Status | Where |
|---|---|---|---|---|
| 1 | Clause 4.4 header citation stale | Refuted on audit | Closed, no action | — |
| 2 | "ISO 14971's own Annex D" cited — doesn't exist in 2019 edition | Confirmed | **Remediated, 2026-07-15 (verified applied, not just claimed)** | `RISK_MANAGEMENT_PLAN.md` §4.3, Path-to-sign-off; `HANDOFF.md`; `DEVLOG.md` (×2, corrected in place with a bracketed note per this log's append-only discipline); `README.md`. **Correction to this row's own location list:** `KNOWN_LIMITATIONS.md` was checked directly and does not contain the "Annex D" citation error — its one "ALARP" mention is a correct use of the policy concept (clause 4.2 NOTE 1), not a false citation. This ledger's earlier claim that it needed the fix was itself inaccurate. |
| 3 | Severity bands conflate risk control with risk estimation | Confirmed | **Open — R3 options below, Steven's decision** | `RISK_MANAGEMENT_PLAN.md` §4.1 |
| 4 | `HAZ-GIP-1.2`/`1.3` name a proven-closed pathway while describing an open one | Confirmed | **Remediated (structurally), 2026-07-15 (verified applied, not just claimed)** — `HAZ-GIP-1.2b` split out; `HAZ-GIP-1.2`/`1.3`'s own Severity/Probability marked stale/pending re-derivation rather than silently carried over; `HAZ-GIP-1.2b`'s Probability left `GAP`, not defaulted to P5, per Finding 5 below | `HAZARD_REGISTER.md` |
| — | No checked equivalence claim between `dosage.py`/`dosage.dfy` | Partially confirmed | **Open — R5 options below** | `dosage.dfy` header comment (unverified), `traceability_matrix.a.md` |
| 5 | Inestimable-probability hazards should be evaluated on severity alone (TR §5.5.3), not the full matrix | New, from direct TR 24971 read | **Open — options below, Steven's decision** | `HAZ-GIP-1.2b` is the live case |
| — | TR 24971's real three-region matrix uses different region names than "ALARP" | New, from direct TR 24971 read | **Open — naming reconciliation, Steven's call** | `RISK_MANAGEMENT_PLAN.md` §4.3 |

---

## Resolved items — brief record

### Finding 2 — Annex D citation

ISO 14971:2019 has no Annex D (third edition contains only A, B, C).
Table B.1 records the 2007 edition's Annex D as moved to ISO/TR 24971.
Both citation sites corrected; `sources/ISO-24971-2020.pdf` has since
been obtained and read (2026-07-15), see Finding 5 and the naming item
below for what that reading actually surfaced.

### Finding 4 — hazard split

`HAZ-GIP-1.2`/`HAZ-GIP-1.3` previously named "overinfusion," a pathway
Dafny-proves closed, while their own residual/severity fields already
described a different, open situation (no proof a clinician is ever
told a clamp fired). Split, not renamed: the GIP-sourced traceability
anchor (HID 1.2/1.3) stays on the original rows, narrowed to the
pathway it actually covers; the real residual moved to a new row,
`HAZ-GIP-1.2b`. `HAZ-DOSE-003`'s related masking mechanism was
cross-referenced but deliberately not folded in — left as Steven's
register-organization call.

**What's still open here:** `HAZ-GIP-1.2b`'s severity is `GAP`, not
scored — same clinical-judgment dependency as everything else in §4.1.
Its probability is also left `GAP`, deliberately **not** defaulted to
P5 — Finding 5 below questions whether P5-plus-matrix is even the
right procedure for this specific row, and presuming P5 during the
restructuring would have prejudged that open question rather than
just restructured the register. `HAZ-GIP-1.2`/`1.3`'s own prior
`DRAFT: S2`/`P5` values are likewise not carried over to the narrowed
rows — marked stale/pending re-derivation instead, since that DRAFT
reasoning was based on the residual that moved to `HAZ-GIP-1.2b`.

---

## Open — Finding 3: severity/control conflation

**The plan's §4.1 defines severity by evidence strength** (S1: "Dafny-
proven... no harm pathway is open"; S4: "unproven failure mode") rather
than by consequence magnitude. ISO 14971:2019 §3.27 defines severity as
the measure of a hazard's possible consequences — independent of
control status. **ISO/TR 24971 §5.5.4 confirms this directly**:
severity levels should be descriptive and should not include any
element of probability. That's textual confirmation from the
referenced guidance document itself, not just an inference from the
standard.

**Consequence:** a Dafny proof of unreachability is a probability
claim wearing a severity label. Re-scoring `HAZ-GIP-1.14` (reverse
delivery) by consequence alone plausibly lands S3–S4 (IEC 601-2-24's
"shall not be possible" mandate, GIP's own physical-sensor mitigation);
paired with the proof-driven P1 this yields, the plan's own matrix
would call that ALARP, not the Acceptable it currently shows.

### R3 options (unchanged from the original audit, still undecided)

**Option 1 — Adopt the standard's model.** Severity by consequence
alone; proofs/bounds move probability, not severity. Buildable
mechanically; the actual consequence values need Steven's clinical
input — most severity cells become explicit `GAP`s, which is arguably
correct rather than a regression.

**Option 2 — Keep the current model, justify per hazard under §7.1
NOTE 2.** That clause permits a control to reduce severity, but only
when it shrinks the harm's *magnitude if it occurs* — not when it
eliminates whether it occurs. A proof does the latter. Assessed as not
defensible for the proof-reliant hazards (`HAZ-GIP-1.14` especially);
weaker still now that TR §5.5.4 states the exclusion directly.

**Option 3 — Hybrid.** Consequence-only severity, plus an explicit
"which evidence artifact drives this probability" column. Preserves
the current model's real strength (traceability from a risk cell to a
`raw_dafny_output.txt`) without asking severity to silently encode it.
Assessed as the strongest fit for what this repo actually produces.

**Not decided.** Whichever option is chosen, TR 24971's Table 4 (five
consequence-only severity descriptors: Catastrophic/Fatal, Critical,
Serious/Major, Minor, Negligible) is now a real, source-backed
calibration reference for the clinical work this requires.

---

## Open — Finding 5: inestimable-probability hazards and the matrix

**Full write-up:** see the standalone finding document (same content,
reproduced in summary here for a single-file reference).

TR §5.5.3 covers exactly `HAZ-GIP-1.2b`'s situation — a hazard with no
evidence of any kind — and its actual recommendation is to evaluate
such risks **on severity alone**, not to assume worst-case probability
and run the full S×P matrix, which is what §4.4's current policy does.
These are procedurally different and can disagree on outcomes; which
is more conservative depends on where a severity-only threshold would
be set, a threshold that doesn't currently exist in this plan.

**Open interpretive question underneath this:** are hazards like
`system_scope`'s gap genuinely *inestimable* (TR's target case —
software failure, novel hazards) or merely *unmeasured* (the
integration work needed to measure it was simply never built, per
`RISK_MANAGEMENT_PLAN.md` Section 1's own scope boundary)? If the
latter, §5.5.3 may not even be the operative clause — the honest
statement might instead be "no risk control measure currently exists,"
a §7-territory statement, not a §5.5 estimation question. Not resolved
here.

### Options

**Option A — Adopt §5.5.3 literally.** Define a severity-only
acceptability rule for hazards judged genuinely inestimable. Most
textually faithful; requires both the threshold and the interpretive
call above before it can be applied to `HAZ-GIP-1.2b`.

**Option B — Keep P5-plus-matrix, justified explicitly as a deliberate
departure.** No new mechanism needed. Cannot honestly claim TR-24971
alignment without stating the departure and arguing (not assuming) it
is at least as conservative.

**Option C — Two-track.** Severity-alone for hazards with zero
evidence (`HAZ-GIP-1.2b`, and `HAZ-DOSE-003`'s masking mechanism if not
folded into it); full matrix retained for hazards with genuinely
estimable probability, including the proof-driven ones — a Dafny proof
is arguably a stronger probability basis than most of TR's own
"estimable" examples. Closest fit to the source; costs a second
acceptability procedure to maintain and document.

**Not decided.** Interacts directly with Finding 3/R3: whichever
severity model is chosen there, this procedural question (matrix
lookup vs. severity-alone) still needs its own answer.

---

## Open — matrix region naming

TR Annex C.4/Figure C.1's actual three-region matrix names its regions
**"unacceptable risk / investigate further risk control / insignificant
or negligible risk."** This plan's matrix uses "Unacceptable / ALARP /
Acceptable" — ALARP is a real TR 24971 concept, but it names a
risk-control-*policy* approach (clause 4.2 NOTE 1 / TR §C.2), not the
matrix's own middle-region label. The three-tier *structure* is
validated by the source; the *labels* conflated two adjacent concepts.

**Not decided:** rename the middle region to track TR's own wording, or
keep "ALARP" as a stated, deliberate departure from the source's
terminology. Either is defensible once stated explicitly; what isn't
defensible is the current unstated conflation.

---

## Open — equivalence gap (`dosage.py` / `dosage.dfy`)

`dosage.dfy`'s header comment asserts it is a "Dafny translation of
dosage.py's clamping kernel," but no test or harness checks the two
implementations agree on any input — the claim is stated, not
evidenced. This is structurally unique to `dosage_calculator`; the
other two worked examples are Dafny-only.

**Matters for:** any probability credit a Dafny proof would extend to
the Python artifact, if the severity model moves toward Option 1/3
above (where probability-from-proof becomes load-bearing rather than
hidden inside a severity label).

### R5 options

1. **Dafny-to-Python extraction/codegen.** Highest assurance, highest
   cost — not supported by the current toolchain without new tooling.
   Disproportionate for a POC.
2. **Differential-testing harness** — generate shared test vectors, run
   both implementations, compare. Moderate effort; both branch
   structures already read and match (negative → zero, non-finite-or-
   over-limit → clamp, else → raw), so this would formalize an already
   plausible equivalence rather than discover a surprise.
3. **Explicit scoping statement** — record that the Dafny spec is the
   artifact of record for the `PROVEN` claims, the Python is
   illustrative/independently `BOUNDED_CHECKED`, and no behavioral
   identity is claimed beyond a manual read-through. Lowest cost,
   buildable today, and arguably the minimum bar regardless of whether
   1 or 2 is ever pursued.

**Not decided.**

---

## Summary — what actually needs Steven, listed once

- Finding 3 / R3: which severity model (Options 1/2/3)
- Finding 5: which evaluation procedure for inestimable-probability
  hazards (Options A/B/C), and the interpretive call underneath it
  (inestimable vs. unmeasured)
- Matrix region naming: reconcile to TR's wording or keep ALARP as a
  stated departure
- `HAZ-GIP-1.2b`'s actual severity value (blocks all of the above from
  producing a real evaluation)
- `HAZ-GIP-1.14`'s actual severity value, if Option 1/3 is chosen for
  Finding 3
- R5: which equivalence-gap option, if any, for `dosage.py`/`dosage.dfy`
- `HAZ-DOSE-003`: fold into `HAZ-GIP-1.2b` or keep separate

None of these are resolved by this document. It exists so they're
findable in one place, not scattered across a chat session and an
external audit file.
