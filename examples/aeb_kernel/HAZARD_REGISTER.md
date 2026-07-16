# Hazard Register — Generic AEB Kernel (POC)

**Document ID:** HZ-AEB-001
**Part of the risk management file** per ISO 26262-3:2018 Clause 6
(Hazard analysis and risk assessment) — the automotive-domain analogue
of `dosage_calculator`/`renal_adjustment`/`drug_interaction_checker`'s
ISO 14971 hazard registers, and this repo's fourth hazard register
overall, its first outside the medical-device domain. Genuinely
different construction from all three prior ones: this device has no
published, numbered hazard table like GIP v1.0 to transcribe from, and
(unlike `renal_adjustment`/`drug_interaction_checker`) it also has no
internal audit document like `GATE_1C_AUDIT.md` to draw hand-traced
findings from. Every hazard entry below is derived directly from the
ten named `REQ-AEB-*` requirement IDs (`metadata.a.yaml`,
`aeb_kernel.dfy`) and the real regulatory text they trace to
(§ 571.127 S4/S5, `sources/nhtsa-fmvss-127-2024.pdf`).

**Status:** DRAFT | Version: 0.1 | Last reviewed: 2026-07-16

**What this register does, and does not, complete.** Hazard
identification (the ISO 26262 analogue of ISO 14971 clause 5.4) is real
here — grounded in sourced requirement text and real Dafny captures,
not invented. **Risk classification (Severity/Exposure/Controllability
and the resulting ASIL) is left an explicit `GAP` throughout, for a
reason worth stating precisely rather than just copying the medical
examples' framing**: unlike those examples (blocked only by the absence
of a named clinical SME), this register is blocked by two independent
gaps — no named automotive-safety reviewer has classified these hazards
yet, *and* the HARA methodology itself (§ 6.4.2 "Situation analysis and
hazard identification," the clause that defines how to derive E and C
for a given operational situation) is not sourced in this repo (see
`sources/README.md`'s `ISO-26262-3-2018.pdf` entry). What *is* sourced
— Table 4 (the S×E×C→ASIL lookup) and § 6.4.4 (how to state a safety
goal once an ASIL is known) — is the mechanical half of risk evaluation,
not the judgment half. Assigning S/E/C without the methodology text or
a qualified reviewer would be exactly the kind of self-declared,
unearned confidence this repo's discipline exists to refuse.

---

## 1. Scope of this register

**10 hazard entries** (`HAZ-AEB-1` through `HAZ-AEB-10`), one per
`REQ-AEB-*` requirement ID — this device's own numbering already
partitions its hazard-relevant surface (mirroring
`renal_adjustment`'s convention), so this register follows it directly
rather than inventing a separate scheme. Each entry states whether the
requirement is currently backed by a real Dafny proof or remains an
honest `GAP`, per `traceability_matrix.a.md`'s own `PROVEN`/`GAP`
split. Section 3 names what's genuinely outside this kernel's scope
entirely.

---

## 2. Hazard entries

### HAZ-AEB-1 — Forward collision warning fails to activate within the required speed envelope (lead vehicle)

| Field | Value |
|---|---|
| Source | REQ-AEB-1, `metadata.a.yaml`. § 571.127 S5.1.1: "The system must operate under the conditions specified in S6 when traveling at any forward speed that is greater than 10 km/h (6.2 mph) and less than 145 km/h (90.1 mph)" |
| Hazardous situation | The vehicle is closing on a lead vehicle within the mandated 10–145 km/h speed envelope, but the forward collision warning fails to activate (or activates outside the envelope, giving the driver a false sense that the system is watching a speed range it isn't) — the driver isn't alerted to an impending collision they might otherwise have avoided |
| Risk control measure | `FCWRequiredActive(LeadVehicleTarget, speedKmh)`'s ensures clause pins the exact envelope (`aeb_kernel.dfy:61-63`), proven — `6 verified, 0 errors` (`raw_dafny_output_aeb.txt`). Boundary correctness independently confirmed by Gate C4: `aeb_kernel_stp_suite.dfy`'s `STP_Accept_FCW_Lead_LowerBoundExcluded`/`STP_Accept_FCW_Lead_JustAboveLowerBound`/`STP_Accept_FCW_Lead_UpperBoundExcluded`/`STP_Accept_FCW_Lead_JustBelowUpperBound` lemmas, `31 verified, 0 errors` |
| Known, named residual | This proves the *envelope logic* is correct given a true `speedKmh` reading — it does not prove the vehicle's speed sensor itself is accurate, nor that the warning signal (auditory/visual thresholds, S5.1.1(a)/(b)) actually reaches the driver; those are S5.1.1's own sub-requirements, not modeled in this kernel (see Section 3) |
| Potential harm (qualitative, not scored) | A missed or mistimed forward collision warning removes the driver's opportunity to brake manually before AEB's own, later intervention threshold — a real-world antecedent to a rear-end collision |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-2 — Automatic emergency braking fails to engage within the required speed envelope (lead vehicle)

| Field | Value |
|---|---|
| Source | REQ-AEB-2, `metadata.a.yaml`. § 571.127 S5.1.2: same 10–145 km/h envelope as S5.1.1, but for the automatic service-brake-application obligation, confirmed a distinct legal requirement by reading both clauses directly |
| Hazardous situation | The vehicle is closing on a lead vehicle within the mandated speed envelope and a collision is imminent, but the system fails to automatically apply the service brakes (or applies them outside the envelope) |
| Risk control measure | `AEBRequiredActive(LeadVehicleTarget, speedKmh)`'s ensures clause (`aeb_kernel.dfy:81-83`), proven — same capture as HAZ-AEB-1. Boundary correctness: `STP_Accept_AEB_Lead_*` lemma family, `31 verified, 0 errors` |
| Known, named residual | Same class of residual as HAZ-AEB-1 — proves the envelope logic, not sensor accuracy, brake-actuator mechanics, or the deceleration achieved once engaged (that's HAZ-AEB-8's territory) |
| Potential harm (qualitative, not scored) | A missed AEB engagement inside the mandated envelope is this kernel's single most direct path to an unmitigated collision — the last automated intervention layer the standard requires |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-3 — Forward collision warning fails to activate within the required speed envelope (pedestrian)

| Field | Value |
|---|---|
| Source | REQ-AEB-3, `metadata.a.yaml`. § 571.127 S5.2.1: "...when the vehicle is traveling at any forward speed that is greater than 10 km/h (6.2 mph) and less than 73 km/h (45.3 mph)" |
| Hazardous situation | Same failure mode as HAZ-AEB-1, against a pedestrian rather than a lead vehicle — a narrower, lower-speed envelope reflecting the standard's own distinct pedestrian test parameters |
| Risk control measure | `FCWRequiredActive(PedestrianTarget, speedKmh)`'s ensures clause (`aeb_kernel.dfy:64-65`), proven. Boundary correctness: `STP_Accept_FCW_Pedestrian_*` lemma family |
| Known, named residual | Same class as HAZ-AEB-1, plus: this kernel does not model pedestrian detection itself (overlap, obstruction, direction — S8's own test parameters) — only the speed-envelope requirement once a pedestrian collision is deemed imminent |
| Potential harm (qualitative, not scored) | A pedestrian struck without any warning to the driver — categorically higher vulnerability than a vehicle-vehicle collision, reflected in the standard's own lower upper speed bound (73 vs. 145 km/h) |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-4 — Automatic emergency braking fails to engage within the required speed envelope (pedestrian)

| Field | Value |
|---|---|
| Source | REQ-AEB-4, `metadata.a.yaml`. § 571.127 S5.2.2: same 10–73 km/h envelope as S5.2.1, for the AEB action itself |
| Hazardous situation | Same failure mode as HAZ-AEB-2, against a pedestrian |
| Risk control measure | `AEBRequiredActive(PedestrianTarget, speedKmh)`'s ensures clause (`aeb_kernel.dfy:84-85`), proven. Boundary correctness: `STP_Accept_AEB_Pedestrian_*` lemma family |
| Known, named residual | Same class as HAZ-AEB-2 and HAZ-AEB-3 combined |
| Potential harm (qualitative, not scored) | This kernel's most severe single failure mode by the standard's own framing — an unmitigated vehicle-pedestrian collision |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-5 — Subject vehicle's own braking onset misclassified

| Field | Value |
|---|---|
| Source | REQ-AEB-5, `metadata.a.yaml`. § 571.127 S4: "Subject vehicle braking onset is the point at which the subject vehicle achieves a deceleration of 0.15 g due to the automatic control of the service brakes" |
| Hazardous situation | The system misjudges whether AEB has actually begun braking (relative to the standard's own 0.15g threshold) — relevant both to S5.4's malfunction-detection telltale logic (which needs to know whether performance is meeting S5.1–S5.3) and to any downstream safety-validation check that depends on correctly detecting "AEB fired" |
| Risk control measure | `IsSubjectVehicleBrakingOnset(decelG)`'s ensures clause (`aeb_kernel.dfy:96`), proven — the >= 0.15 threshold is inclusive, boundary-tested at the exact value by Gate C4 (`STP_Accept_SubjectBrakingOnset_AtThreshold`, `STP_Reject_SubjectBrakingOnset_AtThreshold_WrongValueExcluded`) |
| Known, named residual | Proves the threshold *comparison* is correct given a true deceleration reading — not that the vehicle's own accelerometer/deceleration measurement is accurate |
| Potential harm (qualitative, not scored) | An incorrectly-detected braking onset could feed a false "AEB is working" signal into S5.4's malfunction-detection logic, masking a real degradation |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-6 — Lead vehicle's braking onset misclassified

| Field | Value |
|---|---|
| Source | REQ-AEB-6, `metadata.a.yaml`. § 571.127 S4: "Lead vehicle braking onset is the point at which the lead vehicle achieves a deceleration of 0.05 g due to brake application" |
| Hazardous situation | The system misjudges when the lead vehicle itself began braking — this threshold underpins S7's own decelerating-lead-vehicle test parameters (S7.5.1/S7.5.2's timing relative to "lead vehicle braking onset"), which in turn structure the time-to-collision calculation (S7.2's `TTC0 = 5.0`) that determines when FCW/AEB should trigger |
| Risk control measure | `IsLeadVehicleBrakingOnset(decelG)`'s ensures clause (`aeb_kernel.dfy:105`), proven — same >= 0.05 inclusive-threshold discipline as HAZ-AEB-5, boundary-tested by Gate C4 |
| Known, named residual | Same class as HAZ-AEB-5 — comparison logic proven, not the underlying relative-motion sensing this kernel doesn't model |
| Potential harm (qualitative, not scored) | Misjudging when a lead vehicle starts decelerating could delay the subject vehicle's own FCW/AEB response relative to the actual closing-speed profile |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-7 — Driver's own brake pedal application onset misclassified

| Field | Value |
|---|---|
| Source | REQ-AEB-7, `metadata.a.yaml`. § 571.127 S4: "Brake pedal application onset is when 11 N of force has been applied to the brake pedal" |
| Hazardous situation | The system misjudges whether and when the driver manually applied the brake pedal — relevant to any driver-in-the-loop logic that would suppress or adjust automated intervention based on manual braking already being underway |
| Risk control measure | `IsBrakePedalApplicationOnset(forceN)`'s ensures clause (`aeb_kernel.dfy:113`), proven — same inclusive-threshold discipline, boundary-tested by Gate C4 (`STP_Accept_BrakePedalOnset_AtThreshold`, `STP_Reject_BrakePedalOnset_AtThreshold_WrongValueExcluded`) |
| Known, named residual | Same class as HAZ-AEB-5/6 — this kernel proves the 11N comparison, not the physical force-sensing mechanism |
| Potential harm (qualitative, not scored) | A misjudged manual-braking state could cause the system to either withhold AEB when the driver's own braking is genuinely insufficient, or double-count braking effort in a way that skews S5.3's false-activation check |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-8 — Unnecessary (false) automatic braking activation

| Field | Value |
|---|---|
| Source | REQ-AEB-8, `metadata.a.yaml`. § 571.127 S5.3: "The vehicle must not automatically apply braking that results in peak additional deceleration that exceeds what manual braking would produce by 0.25 g or greater" |
| Hazardous situation | The AEB system engages when no real collision threat exists (e.g., triggered by a steel trench plate or other false-positive stimulus, per S9's own false-activation test setup) and applies enough additional deceleration to itself create a hazard — a rear-end collision from a following vehicle, or driver loss of confidence in the system leading to future manual overrides at genuinely dangerous moments |
| Risk control measure | `IsFalseActivationCompliant(peakAdditionalDecelG)`'s ensures clause (`aeb_kernel.dfy:125`), proven — the compliance condition (`< 0.25`) is the direct logical negation of the standard's own stated violation condition, boundary-tested at the exact 0.25g value by Gate C4 (`STP_Accept_FalseActivation_AtThreshold_NotCompliant`, `STP_Reject_FalseActivation_AtThreshold_WrongValueExcluded`) — the one function in this spec whose boundary direction is inverted relative to HAZ-AEB-5/6/7 (compliant is *below* the threshold, not at-or-above it), specifically flagged as an easy-to-invert case in `nl_confirmation_aeb_kernel_dfy.md` |
| Known, named residual | Proves the threshold comparison given a real `peakAdditionalDecelG` measurement — not that the underlying false-activation stimulus (steel trench plates, road debris, etc.) is correctly rejected by whatever sensor/perception system produces that measurement, which this kernel doesn't model |
| Potential harm (qualitative, not scored) | Unlike HAZ-AEB-1–4 (a missed intervention), this is a hazard the system itself *causes* by acting — the standard's own framing (a distinct requirement, not just "AEB should work correctly") reflects that false activation is a materially different risk category |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-9 — Vehicle outside the standard's mass class treated as covered

| Field | Value |
|---|---|
| Source | REQ-AEB-9, `metadata.a.yaml`. § 571.127 S3: "This standard applies to passenger cars and to multipurpose passenger vehicles, trucks, and buses with a gross vehicle weight rating (GVWR) of 4,536 kilograms (10,000 pounds) or less" |
| Hazardous situation | A vehicle above the GVWR threshold (where braking dynamics, stopping distances, and driver sightlines differ materially) is fitted with this kernel's logic and treated as though the S5.1–S5.3 requirements were validated for its class, when the standard itself never claims applicability there |
| Risk control measure | **None — not yet formalized as a Dafny signature.** `traceability_matrix.a.md`'s own row: `intended_method: DECLARED`, `realized: GAP`, `system_scope` — a fleet/homologation-level eligibility gate, not a per-detection-event claim this kernel's own logic evaluates (see `metadata.a.yaml`'s `system_scope` field for REQ-AEB-9) |
| Known, named residual | Genuinely out of this kernel's proof scope by construction, not an oversight — see `aeb_kernel.dfy`'s header comment and `PHASE1_PLAN.md`'s scope discussion |
| Potential harm (qualitative, not scored) | Applying this kernel's speed-envelope logic to a heavier vehicle class it was never validated against could produce false assurance that S5.1–S5.3's requirements are actually being met for that vehicle |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

### HAZ-AEB-10 — Malfunction or performance degradation goes undetected or unnotified

| Field | Value |
|---|---|
| Source | REQ-AEB-10, `metadata.a.yaml`. § 571.127 S5.4: "The system must continuously detect system malfunctions, including performance degradation caused solely by sensor obstructions... the system must provide the vehicle operator with a telltale notification" |
| Hazardous situation | A real malfunction or sensor-obstruction-caused degradation occurs, but the system fails to detect it or fails to notify the driver — the driver continues to rely on FCW/AEB coverage that no longer actually exists, a silent failure rather than an announced one |
| Risk control measure | **None — not yet formalized as a Dafny signature.** `traceability_matrix.a.md`'s own row: `intended_method: DECLARED`, `realized: GAP`, `system_scope` — a stateful, continuous-monitoring/mode-control requirement (system state across time and ignition cycles), a genuinely different kind of claim than HAZ-AEB-1–8's pure per-event functions, not a smaller version of the same kind (see `metadata.a.yaml`'s `system_scope` field for REQ-AEB-10) |
| Known, named residual | Flagged here as the highest-priority candidate for future formalization among this register's two `GAP` rows, using the same reasoning `renal_adjustment`'s register applied to its own fail-open hazard (HAZ-RENAL-4): a silent, undetected loss of protection is a materially worse failure mode than any single mis-timed activation, since it removes the driver's own awareness that manual vigilance is now required |
| Potential harm (qualitative, not scored) | A driver who believes AEB/FCW coverage is active, when it silently is not, may drive with reduced manual attention precisely when it's most needed |
| Severity | `GAP` |
| Exposure | `GAP` |
| Controllability | `GAP` |
| ASIL (Table 4, once S/E/C known) | `GAP` |

---

## 3. Explicitly out of scope (named, not omitted)

What § 571.127 itself covers that this kernel's ten hazards do not
address at all — not deferred, not a `GAP` row, just never this
kernel's job:

- **Sensor fusion and perception** — how the vehicle actually detects
  an imminent collision, classifies a pedestrian, or measures its own
  speed/deceleration is entirely outside this kernel's scope. Every
  function here takes an already-measured value (`speedKmh`, `decelG`,
  `forceN`) as a trusted input, the same trust-boundary pattern
  `renal_adjustment`'s `HAZ-RENAL-8` and `drug_interaction_checker`'s
  caller-supplied classification flags already establish for this
  repo.
- **S6 test conditions and S7/S8/S9 test procedures** — environmental
  conditions, road surface specifications, and the exact test-conduct
  sequencing (including the standard's own millisecond-level timing
  figures, e.g. the 500 ms accelerator-release window) are NHTSA's
  compliance-verification methodology, not requirements the vehicle's
  AEB system itself must satisfy — see `aeb_kernel.dfy`'s header
  comment's structural finding.
- **S10 (brake application specification)** and **the actual brake
  actuator/hydraulic control logic** — this kernel proves *when*
  braking is required, not the mechanical/control-systems means by
  which a real vehicle achieves the commanded deceleration.
- **Adaptive cruise control interaction, low-range four-wheel-drive
  deactivation, and law-enforcement deactivation** (S5.4.2.1/S5.4.2.2's
  named exceptions to the "no user control may disable AEB" rule) —
  real, sourced requirements, but a further extension of HAZ-AEB-10's
  territory, not modeled here even as a `GAP` row since REQ-AEB-10
  itself isn't yet formalized.

---

## 4. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-07-16 | Initial draft: 10 hazard entries (one per `REQ-AEB-*`), explicitly-out-of-scope section, S/E/C/ASIL left `GAP` throughout with the two-part reason (no named automotive-safety reviewer, and the HARA methodology clause 6.4.2 itself not yet sourced) stated explicitly | Fourth hazard register in this repo, its first outside the medical-device domain. Built directly following `sources/iso-26262-3-2018-table4-and-6.4.4.md`'s archival — Table 4 and § 6.4.4 make risk *evaluation* mechanically possible once S/E/C are known, but identification (this document) doesn't depend on that and was buildable immediately |

---

*Hazard identification (Section 2's `Source`, `Hazardous situation`,
and `Risk control measure` fields) is drawn directly from this repo's
own committed evidence (`metadata.a.yaml`, `aeb_kernel.dfy`,
`traceability_matrix.a.md`, `nl_confirmation_aeb_kernel_dfy.md`,
`raw_dafny_output_aeb.txt`, `sources/nhtsa-fmvss-127-2024.pdf`) — not
fabricated. Severity, Exposure, Controllability, and the resulting ASIL
are explicit `GAP`s: this register identifies hazards; it does not yet
classify or evaluate their risk, per ISO 26262-3:2018 Clause 6.4.2
(not yet sourced in this repo) and Clause 6.4.3 (sourced only as its
output table, Table 4, not its classification methodology).*
