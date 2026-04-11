# M8 Execution Engine v1.0

Canonical engineering specification of the regime-aware ADE execution layer.

---

## Contents

- `M8_Execution_Engine_v1.0.md` — canonical specification
- `tableA_m8_execution.json` — machine-readable execution engine
- `validator_v1.0.py` — structural and semantic validator
- `canonical_lock_validator_v1.0.py` — exact canonical lock validator
- `CANONICAL_TABLE_A_10_32_10.pdf` — source of truth

---

## Canonical Status

Draft-Canonical v1.0

---

## Core Invariant

New Entry-4 ≡ Reduced-4

---

## Notes

- This module extends ADE Table A with regime logic and execution semantics
- Table A itself is not modified
- All transitions are protected by canonical lock validation
