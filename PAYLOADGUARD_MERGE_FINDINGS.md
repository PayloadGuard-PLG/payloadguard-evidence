# PayloadGuard merge findings

A running log of PayloadGuard scan verdicts on this repo's own pull
requests where the verdict did **not** match the reality of the change —
kept as field evidence to harden the PayloadGuard product for production
use. Each entry records what PayloadGuard said, what the change actually
was, why the two diverged, and the concrete product change that would
close the gap.

This is a plain append-only log (newest first). It is **not** a defect
tracker for this repo's own code — the changes described here were
correct; the entries are about PayloadGuard's own detection behaviour.

---

## 2026-07-20 (Tier 3) — Soft misfire: `CAUTION_MISMATCH` (`cross_stack_micro_claim`) as the SOLE signal on a purely additive feature PR (PR #73)

**Verdict issued:** `REVIEW` [LOW] — "✓ Proceed with normal review
process." Scan 2026-07-20 19:45:36, branch commit `e3acc24` → target
`ee7c7e5`. Non-blocking (exit-0 verdict; `payloadguard.yml` gates on exit
code, not the verdict string).

**What the change actually was:** Component F — the frozen-contract
integrity gate (dosage pilot). Purely **additive**: 9 files added, 5
modified, **743 added / 4 deleted** (0.5% deletion ratio), no file
deletions. Layer 4 Structural Drift `LOW`, 0.0% max deletion — nothing
removed or gutted. Temporal `CURRENT`.

**Which layer fired:** Semantic Transparency (Layer 5b) **alone** —
`CAUTION_MISMATCH`, MCI `0.200`, signal `cross_stack_micro_claim`. Every
other layer benign. This is the notable part: in the PR #67/#68 entries
below, `cross_stack_micro_claim` (MCI 0.200) appeared only as a soft
co-signal *underneath* a hard Layer-4 `DESTRUCTIVE` verdict. Here it is the
**only** signal, on a change with **zero deletions** — isolating the
signal's behaviour from any structural-drift event for the first time in
this log.

**Root cause.** Layer 5b compares the PR description's language against the
diff's profile to catch the deceptive-payload pattern (low-impact
*wording* concealing high-impact *removal* — the April 2026 incident
shape). This PR's description is dense with precise, *cross-stack* micro-
claims: verbatim Dafny verifier strings (`2 verified, 0 errors`), exit
codes, `--allow-warnings` behaviour (the Dafny toolchain) sitting next to
`check_contract`'s `CONTRACT_INTACT`/`VIOLATED` verdicts (the Python
module). The heuristic reads that specificity-spanning-two-stacks as a
partial intent/diff divergence. But the profile is the **opposite** of the
deception pattern: the diff is net-additive with a near-zero deletion
ratio, and every micro-claim is backed by a committed Dafny capture or a
test — accurate, not minimizing. "Specific + cross-stack" is a hallmark of
honest, evidence-grounded engineering writing (pervasive in this repo), not
of concealment.

**Recommended product hardening:**
- **Gate `cross_stack_micro_claim` on the deletion profile.** The
  deceptive-payload pattern Layer 5b targets is low-impact-description-over-
  high-impact-*removal*. When the diff is net-additive with a near-zero
  deletion ratio **and** Layer 4 is `LOW`, this signal has no deception
  substrate to sit on — down-weight or suppress it rather than surfacing a
  `CAUTION_MISMATCH`. An all-additive PR cannot be hiding a destructive
  payload it does not contain.
- **Distinguish "specific + cross-stack" from "vague + minimizing."** The
  real deception signal is *under*-description of scope; dense, verifiable,
  capture-backed claims that happen to reference two stacks are the inverse
  and should not raise the same flag.

**Disposition in this repo:** the overall verdict (`REVIEW`, "proceed") is
reasonable and non-blocking; only the Layer-5b sub-signal misfired. The
description was verified accurate against the diff — every micro-claim
traces to a committed capture or test. **Nothing was changed to appease the
scanner:** trimming the verified claims to lower the MCI would itself be the
transparency-gaming this check exists to prevent, so the honest description
stands. Logged as field evidence — the first isolated data point on the
`cross_stack_micro_claim` signal, distinct from the structural-drift family
below.

---

## 2026-07-20 (later) — False positive: `DESTRUCTIVE`/`CRITICAL` on a dedup-after-consolidation (PR #68)

**Verdict issued:** `DESTRUCTIVE` [CRITICAL] — "❌ DO NOT MERGE." Scan
2026-07-20 13:48:50, branch commit `99659b7` → target `6c13671`.

**What the change actually was:** the second half of the same
consolidation the PR #67 entry below describes. PR #67 created the shared
`evidence/gate_c5_runner.py` and pointed `renal_adjustment` at it; PR #68
points the last two runners (`run_mutation_suite.py`,
`run_mutation_suite_ddi.py`) at it too, and **deletes the now-redundant
duplicate helpers** (`_PARSE_ERROR_RE`, `_classify`, `_filtered_outcome`,
`_real_verify`, `_version`) from both — five per file — since the runners
now import them from `gate_c5_runner`. The functionality is fully
retained: all five helpers live in `evidence/gate_c5_runner.py` (verified
present) and both runners `import` them from there. Nothing was removed
from the codebase; duplicate copies were collapsed onto the one canonical
copy. 298 tests pass; every mutation outcome is multiset-identical to
before.

**Which layer fired:** Structural Drift (Layer 4) again, CRITICAL — 5
nodes deleted at 50.0% in `run_mutation_suite.py`, 5 at 41.67% in
`run_mutation_suite_ddi.py`. Every other layer benign: File Changes
`Deleted: 0`, line deletion ratio 43.0% (under the >50% flag), Temporal
CURRENT. Semantic Transparency read `CAUTION_MISMATCH` (MCI 0.200, signal
`cross_stack_micro_claim`) — a low, soft "review advised" well under the
deceptive threshold, tripped by the PR body's specific numeric claims
(mutant/kill counts), not a substantive mismatch.

**Root cause — a distinct variant of the same blind spot.** The PR #67
entry below is the *cross-file move in one diff* case (Layer 4 can't
match a moved node to its new home). This is the **delete-redundant-copy-
after-consolidation** case: the canonical copies landed in a *prior*
merge (PR #67, already on `main`), so this diff contains only the
deletions from the duplicate sites with no corresponding additions
anywhere in it. Layer 4, diffing per-file against the target, correctly
sees the nodes leave the two runner files and — having no cross-file *or*
cross-commit awareness of where the canonical definition already lives —
scores it a large-scale deletion. Deduplication (removing a copy once a
shared module owns the canonical one) is a routine, safe refactor that
this blind spot systematically misreads as destruction.

**Recommended product hardening (in addition to the PR #67 entry's
cross-file move reconciliation):**
- **Whole-repo symbol resolution, not whole-PR-diff.** Before scoring a
  named node as *deleted*, check whether a same-named (ideally
  body-matching) definition still exists **anywhere in the post-merge
  tree** — including files the PR doesn't touch. A deletion that leaves
  the symbol still defined elsewhere in the repo, and adds an `import` of
  it in the deleting file, is a dedup, not a loss. This subsumes the
  same-diff move case and also catches the consolidation-across-commits
  case this entry documents.
- **Import-aware deletion scoring.** When a file deletes a local
  definition and, in the same diff, adds an import of that same name, the
  net capability of the file is unchanged — a strong "reclassify from
  DELETE" signal on its own.

**Disposition in this repo:** merged by the maintainer over the false
positive, verified by hand that all five helpers remain in
`gate_c5_runner` and both runners import them. No repo code was contorted
to appease the scanner (keeping dead duplicate helpers solely to placate
Layer 4 would defeat the consolidation this work exists to do). This
entry is the evidence artifact — a second, distinct data point in the
same structural-drift family.

---

## 2026-07-20 — False positive: `DESTRUCTIVE`/`CRITICAL` on an extraction refactor (PR #67)

**Verdict issued:** `DESTRUCTIVE` [CRITICAL] — "❌ DO NOT MERGE — This
would catastrophically alter the codebase." Scan timestamp
2026-07-20 09:25:45, branch commit `f29b822` → target `bfdb876`.

**What the change actually was:** an extraction refactor. Five helpers
inline in `examples/renal_adjustment/run_mutation_suite_renal.py` —
`_PARSE_ERROR_RE`, `_classify`, `_filtered_outcome`, `_real_verify`, and
`_version` — were **moved** into a new shared module,
`evidence/gate_c5_runner.py`. The same PR that removed them from the
renal runner added them to the new module (`+242 / −0` in
`gate_c5_runner.py`); four moved verbatim and `_version` was moved and
exposed as the module's public `dafny_version`. Nothing was deleted from
the codebase — the code changed files, not existence. Net diff across
the PR was `+426 / −148` (`+278`), pytest was green (292 passed), and the
refactored runner regenerates its committed report byte-for-byte.

**Which layer fired, and which correctly did not:**

| Layer | Verdict | Correct? |
|---|---|---|
| File Changes (added 2, deleted 0) | no deletions | ✅ correct |
| Line Changes (deletion ratio 25.8%, threshold >50%) | within normal range | ✅ correct |
| **Structural Drift (Layer 4)** | **CRITICAL — max deletion ratio 55.56%** | ❌ **false positive** |
| Temporal Drift (Layer 5a) | CURRENT (score 0.0) | ✅ correct |
| Semantic Transparency (Layer 5b) | TRANSPARENT (MCI 0.000) | ✅ correct |

Four of the five signals read the change correctly as benign. The
composite `DESTRUCTIVE` verdict was driven **entirely** by Layer 4,
which reported `run_mutation_suite_renal.py` as having 5 named nodes
deleted at a 55.56% node-deletion ratio.

**Root cause — the structural-drift blind spot:** Layer 4 parses each
modified source file **independently** and diffs its named
classes/functions/constants against the target. It has no cross-file
view within a single PR, so it cannot tell a **cross-file move**
(function `X` leaves file A and appears in file B in the same diff) from
a **deletion** (function `X` leaves file A and exists nowhere). An
extraction refactor — one of the most common and lowest-risk
refactorings — is exactly the shape that reads, per-file, as
large-scale deletion. The very signal Layer 4 is built to catch (a file
"modified" but actually gutted) is indistinguishable, at single-file
granularity, from a file whose contents were promoted into a new module.

**Why the other layers got it right and Layer 4 could too:** the
whole-PR file manifest already showed `Added: 2, Deleted: 0`, and a new
file (`gate_c5_runner.py`, `+242/−0`) was added in the same diff
containing the "missing" nodes. The information needed to reclassify the
move as a move — rather than a deletion — was present in the same scan;
Layer 4 simply never consulted it.

**Recommended product hardening (for PayloadGuard, not this repo):**
- **Cross-file move reconciliation in Layer 4.** Before scoring a named
  node as *deleted*, check whether a node with the same name (and,
  better, a matching or near-matching body/signature) *appeared* in any
  file **added or modified in the same PR**. If so, classify it as
  `MOVED`, not `DELETED`, and exclude it from the deletion-ratio that
  feeds severity. This is the single change that would have flipped this
  verdict.
- **Composite-severity guard.** A CRITICAL from a single layer should be
  reconsidered when every other layer — file-deletion count, line
  deletion ratio, temporal, and semantic transparency — reads benign.
  Layer 4 firing alone, against a `Deleted: 0` file manifest and a
  25.8% line-deletion ratio, is a strong "reconcile before blocking"
  signal rather than a "catastrophic" one.
- **Body-hash-based node identity** (stronger form of the first item):
  track nodes by a content hash so a rename-on-move (`_version` →
  `dafny_version`) is still matched as the same relocated node rather
  than a delete + unrelated add.

**Disposition in this repo:** merged by the maintainer over the false
positive, verified by hand that all five nodes are present in
`evidence/gate_c5_runner.py`. No repo code was changed to appease the
scanner (adding shims or splitting the refactor to dodge Layer 4 would
have contorted correct code around a tool blind spot). This entry is the
evidence artifact instead.
