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
