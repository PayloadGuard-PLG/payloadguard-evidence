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
- **`blueprint.html`** — condensed system map: data flow, the six-gate
  pipeline (C1–C6), the `evidence/` module map, and both examples
  side by side.

## What these are NOT

**Snapshots, not generated artifacts.** Nothing in this repo's pipeline
regenerates these from live data — unlike a traceability matrix (always
built from real captures via `evidence/cli.py`), these are hand-authored
HTML that summarize state as of a specific date, stated on each page's
masthead. `DEVLOG.md` and `KNOWN_LIMITATIONS.md` remain the actual
sources of truth; if a claim on these pages conflicts with either of
those, trust the markdown and treat the dashboard as stale.

**Dated 2026-07-09.** Built after Gate C3/C5 landed for
`renal_adjustment.dfy`, with Gate C6's sign-off still the one open item.
If picking this repo up later and these look out of date against
`HANDOFF.md`'s own "Last updated" line, they are — regenerate rather
than trust them.
