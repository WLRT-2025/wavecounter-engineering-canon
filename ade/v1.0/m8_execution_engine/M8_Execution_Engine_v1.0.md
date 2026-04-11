# WaveCounter / WLRT

# M8 Regime + ADE Execution Engine
## Canonical Specification v1.0

**Status:** Draft-Canonical  
**Version:** v1.0

---

## 0. Purpose

This document fixes the canonical engineering layer that unifies:

- ADE Core (`Canonical Table A: 10–32–10`)
- Regime FSM (`S_UP / S_DOWN / S_RANGE`)
- M8 Regime Overlay
- Execution Event Layer
- Canonical Validator
- Canonical Lock Validator

The purpose of this document is to define a fully closed and machine-verifiable execution specification suitable for:

- algorithmic implementation
- deterministic testing
- formal validation
- repository fixation
- later PDF publication

---

## 1. Canonical Architecture

The system consists of five layers.

### Layer 1. ADE Core

Canonical configuration layer:

- Entry-4: 10 configurations
- Exit-5: 32 transitions
- Reduced-4: 10 configurations

This layer is fixed by `Canonical Table A`.

---

### Layer 2. Regime FSM

The regime layer contains exactly three mutually exclusive states:

- `S_UP` — clean uptrend
- `S_DOWN` — clean downtrend
- `S_RANGE` — sideways / range

This layer answers the question:

**Which regime is active now?**

---

### Layer 3. Regime Mapping

Each canonical Table A row receives one regime interpretation:

- `UP_CONT`
- `UP_BREAK_TO_RANGE`
- `DOWN_CONT`
- `DOWN_BREAK_TO_RANGE`
- `RANGE_PREP_UP`
- `RANGE_PREP_DOWN`
- `RANGE_INTERNAL`

This layer answers the question:

**What does this configuration transition mean at regime level?**

---

### Layer 4. Execution Event Layer

Each canonical row is extended by runtime fields:

- `from_state`
- `event_type`
- `event_code`
- `to_state`
- `step_level`

This layer answers the question:

**How is this transition executed in runtime?**

---

### Layer 5. Canonical Validation Layer

The validation layer checks:

- structural correctness
- FSM consistency
- regime consistency
- canonical exact-match lock

This layer answers the question:

**Does the current object exactly match the frozen canonical engine?**

---

## 2. Canonical Source of Table A

The source of truth for the ADE transition system is:

`CANONICAL TABLE A 10_32_10.pdf`

The canonical properties of that source are:

- exactly 32 rows
- synchronized plain text / JSON / LaTeX forms
- corrected transition rows
- canonical invariant:

`New Entry-4 ≡ Reduced-4`

---

## 3. Regime FSM

### 3.1. Canonical States

- `S_UP`
- `S_DOWN`
- `S_RANGE`

These states are mutually exclusive.

---

### 3.2. Base Law of Regime Switching

1. Any trend violation always transfers the system into `S_RANGE`.
2. Any valid trend entry always terminates `S_RANGE` and transfers the system into the corresponding trend regime.
3. Direct transitions are forbidden:

- `S_UP -> S_DOWN`
- `S_DOWN -> S_UP`

Any trend-to-trend transition must pass through `S_RANGE`.

---

### 3.3. Process Events

Process events occur inside active movement development, before final fixation.

- `break_up(3)`
- `break_down(3)`

These are **step 0** events.

---

### 3.4. Fix Events

Fix events occur upon completed configuration fixation.

- `fix_3124`
- `fix_4213`
- `fix_1342`
- `fix_2431`

These are **step 1** or **step 2** events depending on context.

---

### 3.5. Canonical FSM Invariants

#### Invariant 1. Three regimes only
The FSM contains exactly three regimes:

- `S_UP`
- `S_DOWN`
- `S_RANGE`

#### Invariant 2. No direct reversal
Direct `S_UP -> S_DOWN` and `S_DOWN -> S_UP` transitions are forbidden.

#### Invariant 3. Trend violation enters range first
Any violation of an active trend transfers the system into `S_RANGE`.

#### Invariant 4. Step 0 is valid
Regime change may occur inside active movement, before fixation.

#### Invariant 5. Step 1 is valid
Regime change may occur on completed fixation.

#### Invariant 6. Step 2 is not a separate regime
Second-step structures do not create a new state. They remain inside `S_RANGE`.

#### Invariant 7. No “unconfirmed trend” state exists
There are only three states:
- uptrend
- downtrend
- range

#### Invariant 8. Break of point 3 is regime-level formation
At FSM level:

- `break_up(3)` means formation of `1324`
- `break_down(3)` means formation of `4231`

The configuration is treated as already formed at the moment of break and may continue to develop afterward. Fixation does not create the regime event; it only structurally закрепляет it.

---

## 4. Step Model

The system uses a three-level event model.

### Step 0
Event inside movement development:

- process
- break of point 3
- immediate regime consequence

### Step 1
Event on completed fixation:

- fixation-based confirmation or violation

### Step 2
Preparatory structural stage inside range:

- no separate regime state
- no direct trend activation by itself
- only preparation for the next possible entry

---

## 5. Trend Logic

### 5.1. Clean Uptrend

Clean uptrend is defined by the chain:

- `2143`
- `2413`
- `1324`

Canonical meanings:

- `1324` — direct trend entry, continuation, self-sufficient uptrend form
- `2143`, `2413` — classical continuation forms
- fixed `3124` after uptrend continuation — violation
- `2431` formed against uptrend — violation

---

### 5.2. Clean Downtrend

Clean downtrend is defined by the chain:

- `3412`
- `3142`
- `4231`

Canonical meanings:

- `4231` — direct trend entry, continuation, self-sufficient downtrend form
- `3412`, `3142` — classical continuation forms
- fixed `4213` after downtrend continuation — violation
- `1342` formed against downtrend — violation

---

### 5.3. Range

Range is the regime entered after violation of any active trend when no valid new trend entry has yet appeared.

Canonical range-preparatory forms:

- `3124`
- `4213`
- `2431`
- `1342`

These forms do not create a separate trend by themselves. They either:

- record a previous trend violation, or
- structurally prepare a future trend entry

---

## 6. Execution Row Format

Each execution row has the following canonical structure:

- `entry4`
- `exit5`
- `reduced4`
- `new_entry4`
- `status`
- `regime_meaning`
- `from_state`
- `event_type`
- `event_code`
- `to_state`
- `step_level`

Canonical invariant:

`new_entry4 == reduced4`

---

## 7. Status Semantics

Canonical status values:

- `CONT` — trend continuation
- `BREAK` — trend violation leading to `S_RANGE`
- `ENTRY` — valid entry from range into trend
- `RANGE` — internal or preparatory range logic

---

## 8. Regime Meaning Semantics

Canonical regime meanings:

- `UP_CONT`
- `UP_BREAK_TO_RANGE`
- `DOWN_CONT`
- `DOWN_BREAK_TO_RANGE`
- `RANGE_PREP_UP`
- `RANGE_PREP_DOWN`
- `RANGE_INTERNAL`

Interpretation:

- `UP_CONT` — continues or confirms clean uptrend
- `UP_BREAK_TO_RANGE` — violates uptrend and transfers to range
- `DOWN_CONT` — continues or confirms clean downtrend
- `DOWN_BREAK_TO_RANGE` — violates downtrend and transfers to range
- `RANGE_PREP_UP` — remains in range and structurally prepares possible uptrend entry
- `RANGE_PREP_DOWN` — remains in range and structurally prepares possible downtrend entry
- `RANGE_INTERNAL` — remains inside range without immediate directional preparation

---

## 9. Runtime Semantics

Each row is executed through:

- `from_state`
- `event_type`
- `event_code`
- `to_state`
- `step_level`

### Allowed event types

- `process`
- `fix`
- `structure`

### Allowed states

- `S_UP`
- `S_DOWN`
- `S_RANGE`

### Allowed step levels

- `0`
- `1`
- `2`

---

## 10. Validator Architecture

The validation layer has three levels.

### Level 1. JSON Schema Validation

Checks:

- object structure
- required fields
- enum validity
- field type validity

---

### Level 2. Semantic Validation

Checks:

- no direct `S_UP -> S_DOWN`
- no direct `S_DOWN -> S_UP`
- `BREAK -> S_RANGE`
- `CONT` preserves trend state
- `ENTRY` starts from `S_RANGE`
- range-preparatory meanings remain in `S_RANGE`
- step/event consistency

---

### Level 3. Canonical Lock Validation

Checks:

- exact row count = 32
- no missing canonical rows
- no extra rows
- no duplicate canonical rows
- exact lock-match with canonical Table A

This is the strongest validation level.

---

## 11. Canonical Lock

The canonical lock is defined by the exact frozen set of 32 Table A rows.

Each row is locked by the tuple:

`entry4 | exit5 | reduced4 | new_entry4`

Any deviation from the canonical set is treated as a lock violation.

This means:

- silent edits are forbidden
- added rows are forbidden
- deleted rows are forbidden
- modified canonical rows are forbidden

---

## 12. Repository Structure Recommendation

Recommended repository placement:

```text
/WaveCounter
  /canonical
    M8_Execution_Engine_v1.0.md
    tableA_m8_execution.json
    validator_v1.0.py
    canonical_lock_validator_v1.0.py
    CANONICAL TABLE A 10_32_10.pdf
