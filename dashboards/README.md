# Dashboards

Self-contained HTML snapshots of project state, built for skimming
without loading the full markdown reference docs (`SYSTEM_BLUEPRINT.md`
is ~1,100 lines; `KNOWN_LIMITATIONS.md` is longer). Open either file
directly in a browser — no server, no build step, no external
resources.

- **`status-findings.html`** — live-style readout: current test/gate
  status for both worked examples, the evidence-strength ladder, and
  every real finding from citation-verification and tool-hardening work
  aggregated into one table.
- **`blueprint.html`** — comprehensive system map: the full `evidence/`
  module map (all 12 files), real per-gate mechanism detail (not just
  labels), and both examples down to function- and mutant-level detail.
- **`phase-c-closure-review.html`** — interactive, gate-by-gate
  comparison built specifically for closing Phase C: each gate is an
  expandable panel showing the *real captured output that gate itself
  produced* (raw Dafny verifier lines, the STP honesty-exhibit's genuine
  pass/fail pair, real mutation-table rows, real citation-gate
  CONFIRMED/NOT_FOUND examples) for both examples side by side. Gate C6
  is the centerpiece, open by default — both full plain-English
  summaries, `dosage.dfy`'s signed-off decision next to
  `renal_adjustment.dfy`'s pending one, with a direct prompt for what
  reviewing the latter actually requires.

## What these are NOT

**Snapshots, not generated artifacts.** Nothing in this repo's pipeline
regenerates these from live data — unlike a traceability matrix (always
built from real captures via `evidence/cli.py`), these are hand-authored
HTML that summarize state as of a specific date, stated on each page's
masthead. Every real number and captured-output excerpt on these pages
was pulled from the actual committed files (`raw_dafny_output*.txt`,
`mutation_report*.md`, `nl_confirmation*.md`) at build time, not
invented — but if this page and those files ever disagree after further
work, the files win. `DEVLOG.md` and `KNOWN_LIMITATIONS.md` remain the
actual sources of truth.

**Dated 2026-07-09/07-10.** Built after Gate C3/C5 landed for
`renal_adjustment.dfy`, with Gate C6's sign-off still the one open item.
If picking this repo up later and these look out of date against
`HANDOFF.md`'s own "Last updated" line, they are — regenerate rather
than trust them.
