# Generic Infusion Pump Hazard Analysis and Safety Requirements — Version 1.0

**Authors:** David Arney¹, Raoul Jetley², Paul Jones², Insup Lee¹, Arnab Ray³, Oleg Sokolsky¹, Yi Zhang²
¹ University of Pennsylvania · ² Office of Science and Engineering Laboratories, FDA · ³ Fraunhofer Center for Experimental Software Engineering
**Date:** February 6, 2009

> This file is a faithful markdown reformatting of the original PDF (tables
> rebuilt for readability; hazard/requirement numbering, wording, and
> content unchanged) for use as the audit-trail source-of-truth behind
> `examples/dosage_calculator/metadata.yaml`. Per this repo's `sources/README.md`
> rule: read closely before touching metadata.yaml; propose changes, don't
> silently overwrite.
>
> **Correction, 2026-07-15**: that "wording... unchanged" claim was false
> for one line — Safety Requirement 1.8.1 below had silently reworded
> GIP's own sentence structure (clause order, "or" for "and/or", a
> dropped "of the equipment"). Found and fixed after Steven obtained and
> supplied the actual PDF directly from the University of Pennsylvania
> (`sources/gip-v1.0-full-2009.pdf`, archived here); every other line in
> this file has NOT been re-verified against that PDF word-for-word —
> only 1.8.1 and the full §2.4.1 Operational Hazards table (HID 1.1–1.28)
> were checked directly. Full account: `RISK_MANAGEMENT_FINDINGS.md`.

## Abstract

The Generic Infusion Pump (GIP) project develops generic formal models of
infusion pump systems, starting from requirements elicitation and hazard
analysis. This document contains the informal requirements and hazard
analysis used to create a generic pump model, intended to support future
generation of conformance tests for real pump implementations.

---

## 1. Introduction

The goal of the GIP project is to develop models and reference
specifications of generic infusion pumps to verify correct software
functioning for infusion pumps submitted for FDA approval. The reference
specification lets manufacturers concentrate on specialized functionality
and simplifies verification. It can be extended toward more specialized
pumps, such as volumetric and patient-controlled analgesic (PCA) pumps.

## 2. Hazard Analysis

### 2.1 Hazard categories

1. Operational Hazards
2. Environmental Hazards
3. Electrical Hazards
4. Hardware Hazards
5. Software Hazards
6. Mechanical Hazards (Physical Hazards)
7. Biological and Chemical Hazards
8. Use Hazards

### 2.2 Alarms and Alerts

**Pump actions in response to a hazardous event:**
- **Alarm(p):** audio + video signal; `p` is the specific alarm type (e.g. occlusion).
- **Alert(p):** visual warning only; infusion should not be stopped.
- **Log():** entry made in the pump log.
- **Stop():** pump stops infusion.

**Defined alarms:** Occlusion; Air-in-line; Dead battery/No power; Empty
reservoir; No reservoir; Dose limit/Bolus limit exceeded; Key pressed
alarm; POST failure (CPU, ROM/RAM CRC, battery, stuck key, watchdog, RTC,
tone test failures); Watchdog alarm; Overheating; Channel disconnected;
Sensor failure; Defective battery; A-to-D conversion failed; System
failure.

**Defined alerts:** Low battery; Dose out of range/check dose settings;
Low reservoir; Panel unlocked/door open; Infusion set not loaded properly;
Dose error reduction check failed; Key press required (idle >5 min).

### 2.3 Pump Checks

Safety mechanisms: POST checks, watchdog interrupt tests, periodic system
checks, sensor checks, dose error reduction tests.

**2.3.1 POST (Power On Self Test) checks:** CPU test; ROM/RAM CRC test;
battery test; stuck key test; watchdog test; real-time clock test; tone
test.

**2.3.2 Periodic system checks:** RAM test (periodic, low-level driver);
ROM CRC test (periodic, low-level driver); CPU test (every 60 min,
processor code register); communications test (CRC per packet during
RF/wireless, dropped packets retransmitted ≥ n times); system failure
alarm issued if any system check fails.

### 2.4 Hazard Analysis Tables

#### 2.4.1 Operational Hazards

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 1.1 | Overinfusion | All | Programmed flow rate too high | Alarm();Log() | Drug library | 1.1, 1.4.4, 1.4.11 |
| 1.2 | Overinfusion | All | Dose limit exceeded due to too many bolus requests | Alarm();Log() | Flow sensor | 1.4, 3.4.6 |
| 1.3 | Overinfusion | All | (Programmed) Bolus volume/concentration too high | Alarm();Log() | Drug library | 1.4, 3.4.6 |
| 1.4 | Over/Underinfusion | All | Incorrect drug concentration specified | Alarm();Log() | Barcode scanner | 1.1, 6.1.3, 6.1.4 |
| 1.5 | Underinfusion | All | Programmed flow rate too low | Alarm();Log() | Drug library | 1.1, 6.1.3, 6.1.4 |
| 1.6 | Underinfusion | FRN | Air in line | Alarm();Log() | Flow sensor | 1.9 |
| 1.7 | Underinfusion | FRN | Occlusion (supply side and patient side) | Alarm();Log() | Flow sensor | 1.10 |
| 1.8 | Underinfusion | FRN | Reservoir empty | Alarm();Log() | Flow sensor; Drug library | 1.5 |
| 1.9 | Underinfusion | FRN | Reservoir low | Alert();Log() | Flow sensor; Drug library | 1.5 |
| 1.10 | Underinfusion | All | Flow rate does not match programmed rate | Alarm();Log() | Flow sensor | 1.2, 6.1.3, 6.1.4 |
| 1.11 | Deflation issue | FRN | Inability to release gas or air | Alert();Log() | — | — |
| 1.12 | Filling problem | All | Inability to auto fill | Alert();Log() | — | — |
| 1.13 | Improper flow | FRN | Free flow of drug | Alarm();Log() | Flow sensor | 1.2.2 |
| 1.14 | Improper flow | FRN | Bleed back; reflux within device | Alarm();Log() | Flow sensor | 1.8 |
| 1.15 | Improper flow | FRN | Fluctuation of tidal volume | Alarm();Log() | — | — |
| 1.16 | Improper flow | All | Inaccurate flow rate; infusion intermittent | Alarm();Log() | Flow sensor | 1.2 |
| 1.17 | Inflation issue | FRN | Inability to expand/enlarge with gas or air | Alert();Log() | — | — |
| 1.18 | Low pressure | All | Decrease in / no pressure | Alarm();Log() | — | 1.10.3, 1.10.4, 1.10.5 |
| 1.19 | High pressure | All | Increase in pressure | Alarm();Log() | — | 1.10.3, 1.10.4, 1.10.5 |
| 1.20 | Low pump speed | All | Decreased pump speed; pumping stopped | Alarm();Log() | Flow sensor | 1.1.5, 1.1.8, 1.2.3 |
| 1.21 | High pump speed | All | Increased pump speed | Alarm();Log() | Flow sensor | 1.2.3 |
| 1.22 | Failure to alarm | All | Defective alarm unit; delayed alarm detection | Log() | — | — |
| 1.23 | False alarm | All | — | Log() | — | — |
| 1.24 | Failure to prime | FRN | Air in line | Alert();Log() | Flow sensor | 1.9 |
| 1.25 | Incorrect therapy | FRN | Prescription/dosage falls out of default range | Alert();Log() | Drug library; Barcode scanner | 5.1 |
| 1.26 | False alarm | FRN | Inappropriate prompts | Log() | — | — |
| 1.27 | Air bubble in bloodstream | All | Air in line | Alarm();Log() | Flow sensor | 1.9 |
| 1.28 | Incorrect therapy | FRN | Rate/dose cannot be read from order | — | — | — |
| 1.28* | Underinfusion | FRN | Pump programmed but 'start' not pressed | Alert();Log() | — | — |

*Two entries share the number 1.28 in the source document.*

#### 2.4.2 Environmental Hazards

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 2.1 | Failure to operate/malfunction | All | Temperature/humidity/air pressure too high or low | — | — | 7.1 |
| 2.2 | Contamination | FRN | Spillage/exposure to toxins | — | — | — |
| 2.3 | Incorrect therapy | FRN | Patient under/overweight or medically disallowed for pump | Alert();Log() | Barcode scanner | 5.1.1 |
| 2.4 | Failure to attend alarm | All | Background noise | — | — | 3.2.3 |
| 2.5 | Failure to attend alarm | FRN | Patient muffles alarm (ambulatory pump) | — | — | 3.2.3 |
| 2.6 | Failure to attend alarm | FRN | Inaudible or no voice prompts | — | — | 3.2.3 |
| 2.7 | Tampering | FRN | Unauthorized settings change | — | — | 2.1 |
| 2.8 | Tampering | FRN | Panel lock broken/opened during infusion | Alert();Stop() | — | 2.1, 3.3 |
| 2.9 | Tampering | FRN | Panel/door opened or infusion started with door open | Alert();Log() | — | 2.1, 3.3 |
| 2.10 | Interference | All | Electrical interference (cell phones, ESD, etc.) | — | — | 6.1 |
| 2.11 | Interference | All | Inadequate shielding | — | — | 6.1 |
| 2.12 | Overheating | FRN | Fire | — | — | 7.1.2 |
| 2.13 | Contamination | FRN | Battery leak | — | — | — |
| 2.14 | Tampering | FRN | Children/animals pull tubing, press buttons | — | — | — |

#### 2.4.3 Electrical Hazards

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 3.1 | Overheating | FRN | Loose interconnections; channel error | Alarm();Log() | — | 7.1.2 |
| 3.2 | Overheating | FRN | Charge too high; insufficient cooling; magnet quench | Alarm();Log() | — | 7.1.2, 7.3 |
| 3.3 | Charge error | All | Battery could not be charged | Alarm();Log() | — | 4.1.8 |
| 3.4 | Supply voltage error | FRN | Voltage too high/low; battery exceeds limits | — | — | 7.3 |
| 3.5 | Battery failure | FRN | Voltage too low; battery depleted | Alarm();Log() | — | 4.1 |
| 3.6 | A-to-D conversion failure | All | Conversion failed | — | — | — |
| 3.7 | Electric shock | FRN | Leakage current too high | — | — | 4.2.1 |
| 3.8 | Electric shock | FRN | Power failure; power surge | — | — | 4.1.9 |
| 3.9 | Electric shock | All | Inadequate/loss of resistance | — | — | — |
| 3.10 | Circuit failure | FRN | Electrical shorting; high/low impedance | — | — | 4.1.9 |
| 3.11 | EMC issue | FRN | EMI/ESD/RFI | — | — | — |

#### 2.4.4 Hardware Hazards

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 4.1 | System failure | All | Malfunctioning component | Alarm();Log() | — | 3.3, 3.5 |
| 4.2 | System failure | FRN | RTC not synchronized; clock frequency check failed | — | — | 3.3, 3.4 |
| 4.3 | System failure | All | CPU test failed; component failure | — | — | 3.3, 3.4 |
| 4.4 | System failure | All | Synchronization error between pump components | — | Drug library | 3.3.4 |
| 4.5 | Channel error | FRN | Sync problem between channels (multi-channel pump) | — | — | 3.5 |
| 4.6 | Network error | FRN | Pump incompatible with networked device | — | — | 3.3.4 |
| 4.7 | Memory failure | FRN | RAM test failed; write failure; data integrity error | — | — | 3.3, 3.4 |
| 4.8 | Memory failure | FRN | ROM/flash CRC test failed | — | — | 3.3, 3.4 |
| 4.9 | Watchdog failure | All | Timer test failed; not interrupted in 90s | — | — | 3.4.4.5 |
| 4.10 | False alarm | All | False watchdog interrupt | — | — | — |
| 4.11 | Incorrect test results | All | False negative/positive; inaccurate measurement | — | — | — |
| 4.12 | Incorrect dose entered | FRN | Key debounce not detected | — | Drug library | 2.3 |
| 4.13 | Failure to alarm | All | Sensor failure | — | — | — |

#### 2.4.5 Software Hazards

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 5.1 | Data error | FRN | Backup failure; retrieval error; log write failure | — | — | 1.7.1 |
| 5.2 | Data error | FRN | Drug library retrieval failure; transmit failure | — | — | — |
| 5.3 | Incorrect version | FRN | Update not installed; wrong version | — | Barcode scanner | 5.1.8 |
| 5.4 | Failure to alarm | All | Inter-channel communication problem | Log() | — | — |
| 5.5 | Pump could not be silenced | FRN | Alarm priority set incorrectly | Log() | — | — |
| 5.6 | Incorrect dose administered | FRN | Incorrect/old drug library version | — | — | 5.1.8 |
| 5.7 | Channel error | FRN | Failure to recognize new channels | — | — | — |
| 5.8 | Communication error | All | RF communication test failed | — | — | 3.3.4 |
| 5.9 | Pump failed to start up | FRN | POST test(s) failed | — | — | 3.4.5 |
| 5.10 | Pump failed to shut down | All | Auto-stop failure after critical failure | — | — | — |
| 5.11 | Pump reverts to default dose | All | Dose set incorrectly; inappropriate reset | — | Drug library | 5.1.3 |
| 5.12 | Incorrect test results | All | False negative/positive; inaccurate measurement | — | — | — |

#### 2.4.6 Mechanical Hazards (Physical Hazards)

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 6.1 | Unable to set dose/start/stop/reset/silence | FRN | Broken part (e.g. keypad) | Alert() | — | 3.3 |
| 6.2 | Incorrect dose value entered | FRN | Key stuck/depressed | Alarm() | — | 2.3 |
| 6.3 | No alarm signal | FRN | Speaker/audio unit failure | Log() | — | 3.3 |
| 6.4 | Physical damage to pump | All | Falling; shear; stress | — | — | — |
| 6.5 | Injury to medic/patient | FRN | Sharp edges | — | — | — |
| 6.6 | Pump stops infusion | All | Motor failure; unable to stroke | — | Flow sensor | 3.5 |
| 6.7 | Physical damage to pump | All | Chemical damage from cleaning fluid | — | — | — |
| 6.8 | Physical damage to pump | All | Fluid ingress | — | — | — |

#### 2.4.7 Biological and Chemical Hazards

| HID | Hazard | Type | Cause |
|---|---|---|---|
| 7.1 | Biological/chemical hazard | FRN | Device contaminated during use, by blood/fluid |
| 7.2 | Biological/chemical hazard | FRN | Inadequate cleaning; residue; failure to flush/disinfect |

#### 2.4.8 Use Hazards

| HID | Hazard | Type | Cause | Action | Mitigated by | Safety Req |
|---|---|---|---|---|---|---|
| 8.1 | Overfill | All | Incorrect fill volume specified | Alert();Log() | Barcode scanner | — |
| 8.2 | Short fill | All | Incorrect fill volume specified | Alert();Log() | Barcode scanner | — |
| 8.3 | Knowledge-based failure | All | Incomplete instructions; inaccurate labeling | — | Barcode scanner | — |
| 8.4 | Knowledge-based failure | FRN | Medic fails to recognize hazardous situation | — | — | — |
| 8.5 | Knowledge-based failure | FRN | Pump doesn't display adequate dosage info | — | — | — |
| 8.6 | Rule-based failure | FRN | Incorrect prescription/drug library loaded | — | Barcode scanner | 2.2, 5.1.8 |
| 8.7 | Overinfusion | FRN | User/patient inadvertently changes settings | — | Drug library | 2.2, 5.1 |
| 8.8 | Underinfusion | FRN | User/patient inadvertently changes settings | — | Drug library | 2.2, 5.1 |
| 8.9 | Patient incapacitated | FRN | Unable to self-administer/service alarm | — | — | — |
| 8.10 | Attentional failure | All | Incorrect prescription entered | — | — | 2.2, 5.1 |
| 8.11 | Memory failure | FRN | Too few doses given; multiple doses given | — | Flow sensor | — |
| 8.12 | Incorrect dose settings | FRN | Key pressed too long | Alarm() | — | 2.3.1 |
| 8.13 | Inadequate training | All | User not trained/familiar | — | — | — |
| 8.14 | Incorrect dose mode | FRN | Wrong units used (e.g. ml/hr vs mcg/hr) | — | Barcode scanner | — |

**Note on "FRN":** the source document uses this pump-type tag throughout
Section 2.4 without defining it in the extracted text. Not decoded here —
left as an open question (see `sources/README.md`).

---

## 3. Safety Requirements

### 1. Infusion Control

**1.1 Flow rate**
1.1.1 Flow rate (primary and secondary) shall be programmable.
1.1.2 Minimum: pump shall deliver primary (basal) infusion across 0.1–999 ml/hr.
1.1.3 Small-volume pumps (as low as 0.1 ml/hr): max flow rate limited to 99.9 ml/hr.
1.1.4 Large-volume pumps (up to 999 ml/hr): min flow rate at least 1 ml/hr.
1.1.5 Flow discontinuity at low flows (≤1 ml/hr) should be minimal.
1.1.6 Basal delivery rate programmable for durations up to 24 hours.
1.1.7 Active basal continues unchanged while programming basal rates.
1.1.8 Pump should maintain a minimum KVO (keep vein open) rate at all times.

**1.2 Flow rate accuracy**
1.2.1 Flow rate accurate within 5% of setting for ≥72 hours continuous use.
1.2.2 If flow rate exceeds programmed rate by >10% for >15 min, or free flow occurs, pump shall alarm for overinfusion.
1.2.3 If flow rate is <90% of programmed rate for 15 min, pump shall alarm for underinfusion.

**1.3 Volume to be infused (VTBI)**
1.3.1 Small-volume pumps: VTBI range 0.1–999 ml.
1.3.2 Large-volume pumps: VTBI range 1–9,999 ml.
1.3.3 Small-volume: settable in 0.1 ml increments below 1 ml.
1.3.4 Large-volume: settable in 1 ml increments below 100 ml.
1.3.5 Small-volume: settable in 10 ml increments above 100 ml.
1.3.6 Large-volume: settable in 100 ml increments above 1000 ml.

**1.4 Bolus dose**
1.4.1 Normal bolus given on patient request; square bolus programmable over time.
1.4.2 Flow rates for normal/square bolus separately programmable.
1.4.3 Combined flow rate (basal + max of bolus rates) limited by pump maximum.
1.4.4 A bolus dose shall not change the programmed basal flow rate.
1.4.5 Normal bolus takes precedence over square bolus; square bolus suspends during normal bolus.
1.4.6 At completion of normal bolus, square bolus resumes.
1.4.7 Square bolus delivery distributed evenly over its duration.
1.4.8 Only one square bolus may be programmed at a time.
1.4.9 Max programmable duration for square bolus limited to x hrs.
1.4.10 Max programmable period for square bolus limited to x hrs.
1.4.11 No normal bolus during an alarm/error state.
1.4.12 A bolus request exceeding the maximum permissible limit shall trigger a Dose limit exceeded alarm.

**1.5 Drug reservoir**
1.5.1 Reservoir volume/time remaining calculated before infusion starts.
1.5.2 Calculated reservoir time accurate to 3 minutes.
1.5.3 Reservoir time recalculated when basal rate changes.
1.5.4 Reservoir time recalculated at the start of every bolus dose.
1.5.5 Low Reservoir alert if calculated volume < x ml during infusion.
1.5.6 Empty Reservoir alarm if calculated volume = 0 ml during infusion.

**1.6 Pump suspend**
1.6.1 Current pump stroke completes before suspend, if selected normally.
1.6.2 On fault-triggered suspend, pump stops immediately without completing the stroke.

**1.7 Data retention**
1.7.1 If powered off, dose settings and patient data retained ≥4 hours.

**1.8 Reverse delivery**
1.8.1 During normal use and/or single fault condition of the equipment, continuous reverse delivery shall not be possible (from IEC 601-2-24).

**1.9 Air-in-line alarm**
1.9.1 Alarm triggered if air bubbles >200 µL detected.
1.9.2 Enteral pumps: alarm if bubbles >50 µL detected for x minutes.

**1.10 Occlusion alarm**
1.10.1 Upstream occlusion alarm on fluid-container-side occlusion.
1.10.2 Downstream occlusion alarm on patient-side occlusion.
1.10.3 Downstream occlusion pressure limit < 20 psi (1034 mmHg).
1.10.4 Upstream occlusion pressure limit > y psi (z mmHg).
1.10.5 On occlusion, pump stops flow and alarms within a max delay of x seconds.
1.10.6 On occlusion, pump should release built-up tubing pressure (may reverse momentarily).
1.10.7 After occlusion clears, released bolus volume should be at most 0.5 ml.

### 2. User Interface

**2.1 Resistance to tampering and accidents**
2.1.1 ≥2 steps required to change flow rate/VTBI settings.
2.1.2 Changing weight/duration mid-infusion disallowed or requires confirmation.
2.1.3 Administration set designed to prevent unacceptable flow error.
2.1.4 No legal inputs require simultaneous multi-key presses.
2.1.5 Alarm if numeric keypad cover is broken/unlocked during infusion.

**2.2 User input**
2.2.1 Periodic alerts every 15 min while required input is pending.
2.2.2 Alert if paused for more than x minutes.
2.2.3 Clearing/resetting settings requires confirmation.
2.2.4 Alert after 5 min idle while programming a dose.
2.2.5 Alarm + clear parameters after 10 min idle while programming.
2.2.6 On power-on, prompt for new-patient status and clinical location.
2.2.7 Multi-channel: display drug/dose per channel (2.2.7.1); alert (overridable) if the same drug is programmed on more than one channel (2.2.7.2).

**2.3 Keypad**
2.3.1 Key depressed alarm if a non-repeating key held down for 1 minute.
2.3.2 A key press shorter than 1 second is not recognized as a distinct input.

### 3. Error Handling

**3.1 Alarm signaling**
3.1.1 Alarm indicated via both audio and visual signals.
3.1.2 Alarms clearly indicate the specific problem.
3.1.3 Active bolus cancelled on encountering an error condition.

**3.2 Alarm silencing**
3.2.1 Audible alarms can be temporarily disabled; auto-reactivate within ≤2 minutes.
3.2.2 Audible alarms cannot be permanently disabled.
3.2.3 Audible alarm range: 20–100 dB.
3.2.4 Audio alert on invalid/illegal input.

**3.3 Safety checks**
3.3.1 Periodic RAM test via low-level drivers.
3.3.2 Periodic ROM CRC test via low-level drivers.
3.3.3 CPU test every 60 minutes.
3.3.4 System failure alarm if any safety check fails.

**3.4 POST (Power On Self Test)**
3.4.1 POST performed on power-on.
3.4.2 POST covers all devices/subassemblies without degrading normal operation.
3.4.3 POST duration ≤ 1 min 10 s.
3.4.4 POST includes: CPU test; ROM/RAM CRC test; battery test; stuck key test; watchdog test; RTC test; tone test.
3.4.5 Any POST step failure aborts remaining steps and generates the appropriate alarm.
3.4.6 No bolus dose possible during POST.

**3.5 Watchdog**
3.5.1 Each delivery task has an associated watchdog timer/counter.
3.5.2 Watchdog interrupts the pump after 90 s of no response/normal operation.
3.5.3 Watchdog checks each task responded within the last 90 s.
3.5.4 Watchdog alarm if a task doesn't respond for >3 minutes.
3.5.5 Watchdog test failure alarm generated via low-level driver call on failure.

### 4. Event and Error Logging

**4.1 Log data**
4.1.1 Electronic log records each external (user) event.
4.1.2 Electronic log records each fault condition and associated alarm/alert.
4.1.3 Each log entry stamped with date/time.
4.1.4 Log data not lost when pump is powered off.

### 5. Power and Battery Operations

**5.1 Battery voltage**
5.1.1 Active battery voltage measured at least every 3 minutes.
5.1.2 Active battery voltage = average of 10 consecutive readings.
5.1.3 Remaining battery life calculated from active voltage.
5.1.4 Low battery alarm if remaining life < 15 minutes.
5.1.5 Low battery alarm silenced when on external power.
5.1.6 Battery depleted alarm if remaining life < 5 minutes.
5.1.7 Battery depleted alarm silenced when on external power.
5.1.8 Defective battery alarm if voltage doesn't exceed 1V within 30 min (15 min idle).

**5.2 Leakage current**
5.2.1 Patient Leakage Current alarm if leakage exceeds x mA.

**5.3 Auto-off / sleep mode**
5.3.1 Sleep mode entered if idle (no infusion, no alarm) for the programmed duration.
5.3.2 Wakes on user event (e.g. key press).
5.3.3 Auto-off duration programmable 0–24 hours in 1-hour increments.
5.3.4 Auto-off duration must exceed the user-input idle time (2.2.4).

### 6. Dose Error Reduction

**6.1 Drug library**
6.1.1 Programmable drug library, configurable by patient type and care area.
6.1.2 Drug library entries include: drug list (6.1.2.1); amount/diluent/concentration (6.1.2.2); dose mode (6.1.2.3); hard/soft limits for infusion (6.1.2.4), bolus (6.1.2.5), loading dose (6.1.2.6); VTBI where applicable (6.1.2.7).
6.1.3 Value outside hard limit: incorrect-dose warning, prompt re-entry.
6.1.4 Value outside soft limit: warning, prompt confirmation before starting.
6.1.5 Patient cannot alter drug library profiles/settings.
6.1.6 Pump should log drug-library entry history with enable dates.
6.1.7 Clear indication displayed when drug library is not in use.

**6.2 Infusion settings**
6.2.1 Changing drug type stops any active infusion.
6.2.2 Changing drug type forces restart; reservoir time/volume recomputed.

**6.3 Pump defaults**
6.3.1 Pump has built-in default dose/flow-rate settings.
6.3.2 User/patient cannot change defaults.
6.3.3 Defaults modifiable only by a pump administrator.
6.3.4 Administrator screens protected by secure login/password.
6.3.5 Defaults may include: default basal rate, max flow rate, bolus units, time format, min/max patient weight, min/max VTBI, default concentrations, min/max pressure ratings.

### 7. System Environment

**7.1 Operating conditions**
7.1.1 Operating temperature 5–45°C (35–40°C for implanted pumps).
7.1.2 Pump Overheated alarm above x°C.
7.1.3 Operable under atmospheric pressure 500–5000 mmHg.
7.1.4 External pump operable at 20–90% relative humidity (non-condensing).

**7.2 RF signals**
7.2.1 RF/wireless pumps built per FDA wireless guidance; resistant to disruption from common EM signals.

**7.3 Vibration**
7.3.1 Implantable pumps withstand random vibration per EN 60068-2-64 Test Fh: 5–500 Hz test range; 0.7 (m/s²)²/Hz acceleration spectral density; flat horizontal spectral density curve across the range.

## 4. Conclusion and Future Work

The hazard enumeration formed the basis for the safety requirements
developed here. Planned future work: build formal models from these
requirements, analyze for correctness (hazard-derived properties) and
structural properties (completeness, consistency); extend the document
with network-connection hazards/requirements and pump-type-specific
additions (e.g. PCA pumps).
