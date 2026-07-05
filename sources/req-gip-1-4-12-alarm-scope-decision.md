# Decision: REQ-GIP-1-4-12 alarm scope split

## Problem found (Gate 1 review, 2026-07-05)

REQ-GIP-1-4-12's requirement text says the pump "shall trigger a Dose
limit exceeded alarm." The concrete evidence backing it
(`over_max_clamps_exactly_to_max`) only verified that the returned dose
value is clamped to the maximum — no alarm, flag, or exception was ever
checked. Evidence and requirement text did not match. Unlike
REQ-GIP-1-8-1, which got an explicit scope-clarifying amendment (Option A,
2026-07-04) when the same kind of question came up, REQ-GIP-1-4-12 had no
equivalent clarification.

## Research

**GIP v1.0 source text** (Arney et al. 2009), Safety Requirement 1.4.12:
"If a bolus request causes the bolus dose to exceed the maximum
permissible limit (for a given time period), the pump shall issue a Dose
limit exceeded alarm." This is explicit — "issue" means the pump itself
generates a signal, not merely that an internal value is clamped.

**IEC 60601-1-8** (the collateral standard for alarm systems in medical
electrical equipment — infusion pumps are a named example device class
under it) formally separates two concepts:

- **ALARM CONDITION** — the detection of a hazardous state.
- **ALARM SIGNAL** — the audible/visual output generated once a condition
  is detected, with its own requirements (priority classification,
  tone/pattern, usability per IEC 62366-1).

An "alarm system" per the standard is defined as the parts of equipment
that detect alarm conditions and, as appropriate, generate alarm signals
— detection and signal generation are already treated as separable
architectural layers by the standard itself, not an invented split.

**The GIP source table's own formal model** supports the same read: hazard
entries are tagged with abstract response functions like `Alarm(); Log()`
rather than a mandate that every hazard-adjacent component emit the
physical signal. The paper's formal model treats alarm-triggering as an
abstracted action, consistent with a layered architecture.

## Decision

REQ-GIP-1-4-12 is split into two explicit scopes in `metadata.yaml`:

- `kernel_scope` — the dosage-calculation kernel detects the ALARM
  CONDITION (bolus would exceed the limit) and reports it via a clamped
  return value. **This is what the current evidence verifies.**
- `system_scope` — the full pump system is responsible for generating the
  ALARM SIGNAL (audible/visual) once the kernel reports the condition.
  **Deferred to integration testing against a real device/UI layer.**
  Not evidenced at this phase, and not claimed to be.

## Follow-up work

- Rename the concrete test from `over_max_clamps_exactly_to_max` to
  something that names what it actually verifies (kernel-level condition
  detection), e.g. `kernel_detects_bolus_limit_exceeded`.
- When integration testing begins, REQ-GIP-1-4-12's `system_scope` becomes
  a new binding target — do not silently fold it into the kernel's
  evidence once a real alarm signal exists; it is a distinct requirement
  with its own evidence chain.
