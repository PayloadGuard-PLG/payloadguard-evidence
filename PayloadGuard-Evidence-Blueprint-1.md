<!--
Committed 2026-07-05 (Phase B deferred-gate work). Faithful markdown
conversion of the Google Drive document "PayloadGuard-Evidence-Blueprint-1"
(doc id 154iVHHPkCbrNN6XQ_B07jS0LJG7VYKxtSPT8TEwmMwY, modified
2026-07-03T17:06Z), retrieved via Drive API; escape characters from the
Drive export normalized mechanically. The Drive document remains
authoritative; consult it on any discrepancy.
-->

# PayloadGuard → Compliance Evidence Layer

**A phased, defensible build blueprint for Claude Code**

Version 0.1 · Draft for execution · Target: medical-device software (IEC 62304 + FDA §524B), extensible to DO-178C/DO-333

---

## 0. How to use this document (for the coding agent)

This is a build spec, not prose. Execute it **phase by phase**. Do not begin a phase until the previous phase's **Acceptance Criteria** are met and checked in. Each phase is designed to be independently deliverable and to *prove the next phase is doable before committing to it*. If a phase's acceptance criteria cannot be met, **stop and report** — do not paper over the gap.

The single most important rule in this document is the **Claims Discipline** in §3. Read it before writing any code. A compliance-evidence tool that overstates the strength of its evidence is worse than useless — it is a liability. Everything here is engineered so that every generated statement is true, sourced, and traceable to a specific verification result of a known strength.

---

## 1. Objective

Extend PayloadGuard so that, after it runs its existing verification methods (Dafny, Z3, CrossHair) as a pre-merge CI gate, it **emits a structured compliance-evidence bundle** that maps each verified property to a named requirement, records the *strength* of the assurance honestly, and generates auditor-shaped artifacts aligned to:

- **IEC 62304** (medical device software lifecycle) — traceability, verification summary, safety classification.
- **FDA §524B** cyber-device documentation (as revised Feb 2026 to align with QMSR/ISO 13485) — threat model, security architecture view, machine-readable SBOM.

The deliverable is not a better verifier. It is the **proof-to-evidence bridge**: turning verification output into documentation a regulator/notified-body reviewer can accept, with a human expert sign-off step preserved.

**Non-goal:** replacing the human assurance-case author or claiming regulatory approval. The tool *accelerates* expert review; it does not substitute for it.

---

## 2. Context (why this exists)

None of the target frameworks lack verification *capability*. They lack **soundness evidence and traceable, process-linked documentation** — the artifact that says "this property was established by a known method of known strength, and here is how it maps to the requirement and to the quality system."

Regulatory drivers (current as of this writing):

- **FDA §524B** — statutory since 29 Mar 2023; SBOM refusal authority since 1 Oct 2023. Guidance reissued **3 Feb 2026** ("Quality Management System Considerations…") to align with the **QMSR**, effective **2 Feb 2026**, which incorporates ISO 13485:2016 by reference. Technical expectations unchanged from the June 2025 version; the shift is structural — cybersecurity documentation must now **trace to controlled QMS processes**, not stand alone.
  - https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-management-system-considerations-and-content-premarket
  - https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity
  - https://www.fda.gov/medical-devices/quality-management-system-regulation-qmsr
- **IEC 62304** — FDA-recognized consensus standard; EU-accepted as EN 62304 under MDR. Risk-based rigor (Class A/B/C), lifecycle Clauses 5–9, traceability from risk → code → test.
  - https://www.iso.org/obp/ui/#iso:std:iec:62304:ed-1:v1:en
  - Companion: ISO 14971 (risk) https://www.iso.org/standard/72704.html · ISO 13485 (QMS) https://www.iso.org/standard/59752.html
- **DO-178C / DO-333** (aviation, later phase) — objective-oriented; DO-333 permits formal analysis to replace certain tests, but **requires a soundness argument** for any formal method and **tool qualification** under DO-330. This is the same proof-to-evidence gap in a higher-assurance domain.
  - https://ntrs.nasa.gov/citations/20140004055
  - https://shemesh.larc.nasa.gov/fm/FMinCert/NASA-CR-2017-219371.pdf

---

## 3. Non-negotiable principles (defensibility constraints)

These are hard constraints on every line of generated output. Violating any one makes the artifact indefensible.

### 3.1 Claims Discipline — the keystone

Every statement in a generated artifact MUST be tagged with the verification method that produced it and the **strength** of that method. The tool must never launder a weak result into a strong claim.

| Method | What it actually establishes | Permitted claim language | Forbidden claim language |
|---|---|---|---|
| **Dafny** (deductive verifier) | Machine-checked proof that code meets its specification, given the spec and any supplied loop invariants/termination measures | "formally proven to satisfy", "verified by deductive proof" | — |
| **Z3** (SMT solver, standalone VC) | Discharge of a verification condition within a decidable/decided fragment | "proven for the stated verification condition" | claims beyond the discharged VC |
| **CrossHair** (concolic testing) | **Bounded counterexample search.** A PASS means *no counterexample was found within the configured exploration bounds* — it is **not** a proof, and bugs may remain | "no counterexample found within bounds ⟨B⟩", "bounded-checked" | "proven", "verified correct", "guaranteed" |
| **Unit / property tests** | Behaviour on executed inputs | "tested against ⟨N⟩ cases" | "exhaustively verified" |
| **Manual/declared** | Human assertion, not tool-established | "declared by author; not tool-verified" | any tool-verification phrasing |

CrossHair's own documentation is explicit that it sits between property testing and formal methods and cannot generally prove properties hold; treat that as binding. Where a "proven" strength is required for a safety-critical kernel, provide a **Dafny model** of that kernel and document its correspondence to the implementation (see §9, Option B).

### 3.2 Traceability is mandatory

Every generated artifact statement links back to: a **requirement ID** → a **code location** (file, symbol) → a **verification result** (method, strength, run ID/timestamp). No orphan claims.

### 3.3 Reproducibility / determinism

Given the same inputs (code, contracts, metadata, tool versions, CrossHair bounds/seed), the evidence layer must produce byte-stable artifacts. Record tool versions and CrossHair exploration budget in every bundle.

### 3.4 No fabrication, ever

If a required field has no supporting evidence, the tool emits an explicit **GAP** marker ("not established — human input required") rather than inventing content. Gaps are surfaced in a summary, never hidden.

### 3.5 Isolation from core verifiers

The evidence layer only *consumes* verifier output. It must not modify how Dafny/Z3/CrossHair run. This keeps the change low-risk and keeps the verification trustworthy independent of the reporting.

### 3.6 QMS-traceable, not standalone

Per the Feb 2026 FDA guidance, generated cybersecurity artifacts must carry fields that map them to a controlled QMS process (ISO 13485 clause references, configuration-management linkage for the SBOM). The schema (§7) carries these hooks even if a given project leaves them blank.

---

## 4. Evidence-strength taxonomy (single source of truth)

Define one enum used everywhere in code and output:

```
PROVEN            # Dafny proof, or Z3-discharged VC (within stated scope)
BOUNDED_CHECKED   # CrossHair PASS within recorded bounds; NOT a proof
TESTED            # concrete test cases executed
DECLARED          # human assertion, no tool evidence
GAP               # nothing established; human input required
```

Every requirement-to-result mapping carries exactly one of these. Human-readable artifacts render the taxonomy with its caveat text inline (e.g. every BOUNDED_CHECKED line prints the bound and the "no counterexample within bounds" qualifier).

---

## 5. Target architecture

**Current PayloadGuard flow**
```
code + contracts ─▶ Dafny / Z3 / CrossHair ─▶ pass/fail logs ─▶ CI gate
```

**New flow**
```
code + contracts ─▶ Dafny / Z3 / CrossHair ─▶ raw results ─┐
                                                            ├─▶ [Evidence-Emit Layer] ─▶ evidence bundle
metadata.yaml (requirements, class, threats, QMS refs) ─────┘
```

**Evidence-Emit Layer = one new module, ~300–500 LOC**, with three internal stages:
1\. **Ingest/normalize** — parse each verifier's output into a common internal result record: `{requirement_ref?, code_location, method, raw_status, bounds/seed, run_id, timestamp}`. (A per-verifier adapter; add a translation shim if a verifier's native output is not clean.)
2\. **Bind** — join normalized results to the metadata contract by requirement ID + code location; assign the evidence-strength enum; detect gaps.
3\. **Render** — emit machine-readable (JSON) first, then human-readable (Markdown/PDF) artifacts. JSON is the source of truth; documents are projections of it.

CLI surface (additive, non-breaking):
```
payloadguard verify ... --emit-evidence --metadata ./evidence/metadata.yaml --out ./compliance-evidence/
```
Absent `--emit-evidence`, behaviour is exactly as today.

---

## 6. Repository layout (proposed)

```
payloadguard/
  evidence/                     # NEW module
    __init__.py
    ingest/                     # per-verifier adapters
      dafny_adapter.py
      z3_adapter.py
      crosshair_adapter.py
    model.py                    # internal result record + Strength enum
    binder.py                   # join results ↔ metadata, assign strength, find gaps
    render/
      json_bundle.py            # source-of-truth JSON
      iec62304.py               # IEC 62304 artifacts
      fda_524b.py               # §524B artifacts (threat model view, security arch view)
      sbom.py                   # CycloneDX (primary) + SPDX (secondary)
      markdown.py               # human-readable projections
    schema/
      metadata.schema.json      # JSON Schema for metadata.yaml (validated on load)
      bundle.schema.json        # JSON Schema for the emitted bundle
  examples/
    dosage_calculator/          # the toy POC (§9)
      dosage.py
      dosage_contracts.py
      dosage_model.dfy          # Option B: proven Dafny kernel
      metadata.yaml
      README.md
  tests/
    evidence/                   # unit tests for each stage + golden-file tests
```

---

## 7. The metadata contract (input schema)

The device team supplies one `metadata.yaml`. It is validated against `metadata.schema.json` on load; invalid metadata is a hard error (never a silent default). Illustrative shape:

```yaml
device:
  name: "Infusion Pump Dosage Calculator (POC)"
  intended_use: "Compute safe hourly infusion dose from patient and drug parameters."
  safety_classification: "B"          # IEC 62304 A|B|C
  classification_rationale: >
    Failure could contribute to a non-serious injury (over/under-dose) given
    clinician oversight; not reasonably capable of causing death or serious
    injury after risk controls. Ref ISO 14971 risk file RMF-DOSE.
  iso14971_risk_file: "RMF-DOSE-001"

qms:                                   # ISO 13485 / QMSR linkage (may be blank -> GAP)
  design_control_ref: "DHF-DOSE-2026-014"
  config_management_ref: "CM-DOSE-SBOM"
  iso13485_clauses: ["7.3.6", "7.3.7"]

requirements:
  - id: "REQ-DOSE-001"
    text: "Computed hourly dose shall not exceed max_safe_dose_mg_per_hr."
    implementation: "dosage.py::calculate_hourly_dose"
    intended_method: "PROVEN"          # target strength; binder checks reality vs. intent
  - id: "REQ-DOSE-002"
    text: "Computed hourly dose shall be non-negative."
    implementation: "dosage.py::calculate_hourly_dose"
    intended_method: "PROVEN"
  - id: "REQ-DOSE-003"
    text: "Calculation shall not overflow for inputs within stated ranges."
    implementation: "dosage.py::calculate_hourly_dose"
    intended_method: "BOUNDED_CHECKED"

threat_model:                          # feeds §524B security artifacts
  - id: "THR-DOSE-001"
    threat: "Numeric overflow yields an unsafe dose."
    asset: "Dose output value"
    mitigation_ref: "REQ-DOSE-003"
    method: "STRIDE:Tampering"
  - id: "THR-DOSE-002"
    threat: "Out-of-range input produces undefined behaviour."
    asset: "Input contract"
    mitigation_ref: "REQ-DOSE-001"

sbom:
  primary_format: "CycloneDX"          # CycloneDX primary, SPDX secondary
  generator: "syft"                    # or trivy/etc.; tool records name+version
  components_source: "build"           # generated from build, not hand-curated

toolchain:                             # recorded verbatim into every bundle
  crosshair_bounds:
    per_condition_timeout_s: 30
    max_iterations: 100000
    seed: 1
```

---

## 8. Output artifacts (Phase-3 target set)

All artifacts are projections of the source-of-truth JSON bundle. Each carries: generation timestamp, tool + verifier versions, CrossHair budget, and a per-artifact **gap summary**.

### 8.1 IEC 62304 set
- **Software Safety Classification record** — class + rationale + ISO 14971 reference (from metadata; GAP if absent).
- **Software Requirements list** — requirement IDs and text.
- **Verification Summary** — per requirement: method used, **evidence strength (§4)**, result, run ID/timestamp, and the strength's caveat text rendered inline.
- **Traceability Matrix** — requirement ID → code location → verification method → strength → result. This is the core deliverable. Machine-readable (JSON/CSV) + human-readable table.
- (Class C later: architectural/detailed-design linkage fields — schema reserves them.)

### 8.2 FDA §524B set (QMSR-aligned)
- **Threat Model view** — from `threat_model`, each threat linked to its mitigating requirement and that requirement's evidence strength. Marked as "maintained" artifact (living document).
- **Security Architecture view** — code review methods applied (which properties checked by which method), presented as the SPDF verification evidence.
- **SBOM** — see §8.3.
- Fields tying artifacts to the QMS (ISO 13485 clause refs, configuration-management ref for the SBOM). GAP if metadata omits them.

### 8.3 SBOM specification
- **Machine-readable, primary = CycloneDX (OWASP), secondary = SPDX (Linux Foundation).** A PDF/spreadsheet does **not** satisfy FDA machine-readability. Generated from the build via an SCA tool (name+version recorded), not hand-curated.
- **NTIA minimum elements per component:** supplier, component name, version, unique identifier (Package URL / `purl`), dependency relationships, SBOM author, timestamp.
- **FDA additions:** support level (actively maintained / maintenance / end-of-life), end-of-support date when known, and known-vulnerability assessment (CVE / CISA KEV) with mitigations.
- **VEX** companion document supported (exploitability of listed CVEs in this configuration).
- Accompanied by a short **human-readable narrative** (how the SBOM is kept current, how CVEs are triaged) — required alongside the machine-readable file.
- References: NTIA minimum elements; CycloneDX; SPDX. (Do not reinvent SBOM generation — wrap an existing SCA generator; the value here is the *linkage* of SBOM ↔ threat model ↔ QMS config management, which FDA now expects.)

---

## 9. The toy POC specification (build target for Phases 1–3)

**Module:** infusion-pump hourly-dose calculator. Small, IEC 62304 Class B/C-plausible, naturally expressible as formal contracts, and a recognized regulatory device type.

**Signature (Python):**
```python
def calculate_hourly_dose(
    weight_kg: float,                 # (0, 200]
    concentration_mg_per_ml: float,   # > 0
    infusion_rate_ml_per_hr: float,   # >= 0
    max_safe_dose_mg_per_hr: float,   # > 0
) -> float:
    """
    Returns the hourly delivered dose (mg/hr), clamped so it never exceeds
    max_safe_dose_mg_per_hr.

    Contracts:
      pre:  0 \< weight_kg \<= 200
      pre:  concentration_mg_per_ml > 0
      pre:  infusion_rate_ml_per_hr >= 0
      pre:  max_safe_dose_mg_per_hr > 0
      post: 0 \<= result \<= max_safe_dose_mg_per_hr
      post: no overflow / non-finite result for inputs within the preconditions
    """
```

**Requirement → property → intended strength:**
- REQ-DOSE-001 (`result \<= max_safe`) → postcondition → **PROVEN** (Dafny kernel, Option B) / BOUNDED_CHECKED (Option A)
- REQ-DOSE-002 (`result >= 0`) → postcondition → **PROVEN** / BOUNDED_CHECKED
- REQ-DOSE-003 (no overflow / finite) → **BOUNDED_CHECKED** (CrossHair within bounds)

**Two build options (do Option A first):**
- **Option A — Phase-1 spike (fastest):** Python implementation + contracts, checked by **CrossHair** via PayloadGuard. Artifacts label the postcondition claims honestly as `BOUNDED_CHECKED` with the recorded bounds. Sufficient to prove the *evidence pipeline* end-to-end.
- **Option B — flagship (recommended for the demo bundle):** additionally model the numeric safety kernel in **Dafny** (`dosage_model.dfy`), obtain a `PROVEN` result for REQ-DOSE-001/002, and document the correspondence between the Dafny model and the Python implementation. This yields a genuinely "proven" claim for the safety-critical postconditions and directly answers the DO-333-style property-preservation concern. Do this once Option A's pipeline works.

This split is deliberate: Option A validates the machinery under an honest weak claim; Option B upgrades the *claim strength* without changing the machinery.

---

## 10. Phased workflow

Each phase: **Tasks → Deliverable → Acceptance Criteria → Blocker-clearance** (why the next phase is now known-doable). Do not proceed on unmet criteria.

### Phase 0 — Fixture & baseline (0.5 wk)
**Tasks:** Write the Option-A toy (`dosage.py` + `dosage_contracts.py`). Run it through *current* PayloadGuard. Capture the raw CrossHair/Z3 output verbatim into `examples/dosage_calculator/`.
**Deliverable:** A real, committed verification-output sample + a note describing its exact format.
**Acceptance:** PayloadGuard runs the toy and produces parseable output; the output format is documented.
**Blocker-clearance for Phase 1:** We now hold real verifier output, so schema design is grounded in fact, not assumption.

### Phase 1 — Evidence schema + one artifact, hand-built (2–3 wk)
**Tasks:** Author `metadata.schema.json` and `bundle.schema.json`. Write `metadata.yaml` for the toy. **By hand**, produce ONE artifact (the Traceability Matrix) from the Phase-0 output + metadata, applying §3–§4 exactly (correct strength labels, gap markers).
**Deliverable:** Validated schemas + one exemplar Traceability Matrix (JSON + Markdown).
**Acceptance:** (a) `metadata.yaml` validates against the schema; (b) the matrix links every requirement to a code location, method, strength, and result with zero orphan claims; (c) BOUNDED_CHECKED lines carry the bound + caveat; (d) a knowledgeable reviewer confirms the artifact "looks like something a reviewer could accept." If (d) fails, iterate the schema — **do not build Phase 2.**
**Blocker-clearance for Phase 2:** The target shape is proven acceptable, so codifying it is mechanical.

### Phase 2 — Single-artifact generator (2–3 wk)
**Tasks:** Implement `ingest/crosshair_adapter.py` + `ingest/z3_adapter.py` → `model.py`; implement `binder.py`; implement `render/json_bundle.py` + the Traceability Matrix renderer. Generate the same artifact automatically.
**Deliverable:** `payloadguard ... --emit-evidence` produces the Traceability Matrix that matches the Phase-1 hand-built exemplar (golden-file test).
**Acceptance:** (a) generated matrix is byte-equal to the reviewed exemplar (modulo timestamps/run-ids); (b) strengths are assigned solely from verifier output, never from `intended_method` (intent is only checked *against* reality, and a mismatch raises a GAP/flag); (c) deterministic across runs; (d) unit tests for adapter + binder pass.
**Blocker-clearance for Phase 3:** Verifier output ↔ template wiring is proven; remaining artifacts are more of the same.

### Phase 3 — Full bundle + Option B upgrade (3–4 wk)
**Tasks:** Implement remaining renderers: IEC 62304 (classification, requirements, verification summary), §524B (threat model view, security architecture view), and SBOM (wrap an SCA generator → CycloneDX primary + SPDX secondary + narrative + VEX hook). Add the **Dafny kernel** (`dosage_model.dfy`), a `dafny_adapter.py`, and the model-to-implementation correspondence note to upgrade REQ-DOSE-001/002 to `PROVEN`.
**Deliverable:** A complete `./compliance-evidence/` bundle for the toy: JSON source-of-truth + all human-readable artifacts + SBOM + gap summary.
**Acceptance:** (a) all artifacts are internally consistent (no artifact contradicts another — e.g. every threat's mitigation requirement exists and its strength matches the verification summary); (b) the gap summary lists exactly the fields the metadata left blank; (c) SBOM validates against CycloneDX schema and carries all NTIA minimum elements; (d) a reader unfamiliar with the tool can follow the bundle from requirement → proof/CrossHair result → artifact.
**Blocker-clearance for Phase 4:** The bundle is complete and coherent; integration is packaging.

### Phase 4 — CI integration (2–3 wk)
**Tasks:** Wire `--emit-evidence` into PayloadGuard's existing GitHub CI gate so a passing gate also emits the bundle as a build artifact. No change to core verification.
**Deliverable:** On push, CI runs verification (unchanged) and attaches the evidence bundle.
**Acceptance:** (a) fully automated, no manual step; (b) gate pass/fail semantics unchanged when the flag is off; (c) bundle reproducible in CI; (d) integration surfaces no regression in the core verifiers.

**Indicative total: 9–13 weeks**, testable artifact at every phase boundary.

---

## 11. Definition of Done (overall)

- `payloadguard verify --emit-evidence --metadata … --out …` produces, for the toy device, a complete evidence bundle whose every claim is (i) traceable to a verifier result, (ii) labelled with the correct evidence strength per §4, (iii) free of fabricated content, with gaps explicitly marked.
- The safety-critical postconditions carry a `PROVEN` claim backed by the Dafny kernel (Option B), with a documented correspondence to the Python implementation.
- The SBOM is machine-readable (CycloneDX + SPDX), NTIA-complete, with narrative + VEX hook.
- All artifacts trace to QMS hooks where metadata supplies them, and flag gaps where it does not.
- The whole run is deterministic and records tool/verifier versions and CrossHair budget.

---

## 12. Validation gate (outside the code, before selling)

Independent of the build: put the Phase-3 bundle in front of a regulatory reviewer / Designated Entity Representative / notified-body contact and ask one question — **"Would this reduce your review effort?"**
- **Yes →** the wedge is real; proceed to a second device type.
- "Needs human sign-off" → expected; confirms the **accelerator-not-replacement** positioning already baked into §1.
This is a market-validation step, not a technical blocker. Building the tool does not depend on it; *pricing* the tool does.

---

## 13. Honest caveats & known limitations (state these plainly in the product)

- **CrossHair PASS ≠ proof.** It is bounded counterexample search; results are sensitive to the configured budget and to type precision. Never rendered as "verified/guaranteed." Deep loops / complex branching / external calls can exhaust it and yield inconclusive results, which must be reported as such, not as success.
- **Dafny proofs are only as good as their specifications.** A proven postcondition proves the code meets *the written spec*; it does not prove the spec captures the clinical intent. The classification rationale and requirement text remain human responsibilities.
- **Model-to-implementation gap (Option B).** A proven Dafny kernel and a Python implementation correspond only as well as the documented argument between them; this correspondence is `DECLARED` unless separately established.
- **The tool generates evidence, not approval.** No output asserts regulatory clearance. Assurance cases require expert human sign-off; the tool accelerates their assembly.
- **Guidance vs. law.** FDA guidance is non-binding recommendation; §524B itself is statute. The tool's artifacts target the guidance's documentation expectations and must be described that way.
- **SBOM generation is delegated.** Component discovery uses an existing SCA tool with its own coverage limits (e.g. deeply embedded/binary components). The tool's contribution is linkage and NTIA/FDA completeness checks, not novel discovery.

---

## 14. References

**FDA / §524B / QMSR**
- Current cybersecurity guidance (Feb 2026, QMSR-aligned): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/cybersecurity-medical-devices-quality-management-system-considerations-and-content-premarket
- June 2025 Federal Register notice: https://www.federalregister.gov/documents/2025/06/27/2025-11669/cybersecurity-in-medical-devices-quality-system-considerations-and-content-of-premarket-submissions
- FDA cybersecurity hub: https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity
- Postmarket cybersecurity guidance: https://www.fda.gov/media/95862/download
- QMSR final rule / FAQ: https://www.fda.gov/medical-devices/quality-management-system-regulation-qmsr

**IEC 62304 / companions**
- IEC 62304 (ISO OBP): https://www.iso.org/obp/ui/#iso:std:iec:62304:ed-1:v1:en
- ISO 14971 (risk management): https://www.iso.org/standard/72704.html
- ISO 13485 (QMS): https://www.iso.org/standard/59752.html

**DO-178C / DO-333 (later phase)**
- NASA DO-333 case studies: https://ntrs.nasa.gov/citations/20140004055
- NASA formal-methods tool qualification: https://shemesh.larc.nasa.gov/fm/FMinCert/NASA-CR-2017-219371.pdf
- AdaCore DO-178C/DO-333 primer: https://learn.adacore.com/booklets/adacore-technologies-for-airborne-software/chapters/standards.html

**Verification tooling**
- CrossHair (nature & limits): https://crosshair.readthedocs.io/en/latest/related_work.html · https://crosshair.readthedocs.io/en/latest/how_does_it_work.html
- Dafny: https://dafny.org
- Z3: https://github.com/Z3Prover/z3

**SBOM**
- NTIA Minimum Elements: https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom
- CycloneDX (OWASP): https://cyclonedx.org
- SPDX (Linux Foundation): https://spdx.dev

---

*End of blueprint v0.1. Build Phase 0 first. Honour §3 everywhere.*
