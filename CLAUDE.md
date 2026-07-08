# payloadguard-evidence

Compliance-evidence generator for medical device software — see
`README.md` for the plain-English overview.

**Read `HANDOFF.md` first, before doing anything else in this repo.**
It states current status, what's actually done vs. in progress, the
concrete next step, and the working discipline this repo holds itself
to. It's kept current at the end of each work session — if it looks
stale against `DEVLOG.md`'s latest entry, trust `DEVLOG.md` and update
`HANDOFF.md` to match.

For depth beyond the handoff summary: `OPERATIONS_MANUAL.md` (technical
reference — architecture, every verification gate, full command
reference), `SYSTEM_BLUEPRINT.md` (component map and data flow),
`KNOWN_LIMITATIONS.md` (live gate ledger), `DEVLOG.md` (full dated
history), `REVIEW_PROTOCOL.md` (how generated artifacts get reviewed).

Before ending a work session that changed anything non-trivial, update
`HANDOFF.md` to reflect the new current state — that's what makes the
next session's cold start work.
