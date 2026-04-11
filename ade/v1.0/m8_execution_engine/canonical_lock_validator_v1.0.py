from __future__ import annotations

from typing import Any


CANONICAL_ENTRY4 = {
    "2143", "2413", "1324", "2431", "3124",
    "4213", "4231", "1342", "3142", "3412",
}

CANONICAL_TABLE_A_LOCK = {
    "2143|13254|1324|1324",
    "2143|31254|3124|3124",
    "2413|13524|1324|1324",
    "2413|31524|3124|3124",
    "2413|35124|3124|3124",
    "1324|21435|2143|2143",
    "1324|24135|2413|2413",
    "1324|24315|2431|2431",
    "1324|24351|2431|2431",
    "2431|13542|1342|1342",
    "2431|35142|3142|3142",
    "2431|31542|3142|3142",
    "2431|35412|3412|3412",
    "3124|42135|4213|4213",
    "3124|42315|4231|4231",
    "3124|42351|4231|4231",
    "4213|53124|3124|3124",
    "4213|51324|1324|1324",
    "4213|15324|1324|1324",
    "4231|53412|3412|3412",
    "4231|53142|3142|3142",
    "4231|51342|1342|1342",
    "4231|15342|1342|1342",
    "1342|21453|2143|2143",
    "1342|24153|2413|2413",
    "1342|24531|2431|2431",
    "1342|24513|2413|2413",
    "3142|42531|4231|4231",
    "3142|42513|4213|4213",
    "3142|42153|4213|4213",
    "3412|45231|4231|4231",
    "3412|45213|4213|4213",
}

ALLOWED_STATUS = {"CONT", "BREAK", "ENTRY", "RANGE"}
ALLOWED_REGIME = {
    "UP_CONT",
    "UP_BREAK_TO_RANGE",
    "DOWN_CONT",
    "DOWN_BREAK_TO_RANGE",
    "RANGE_PREP_UP",
    "RANGE_PREP_DOWN",
    "RANGE_INTERNAL",
}
ALLOWED_STATES = {"S_UP", "S_DOWN", "S_RANGE"}
ALLOWED_EVENT_TYPES = {"process", "fix", "structure"}

REQUIRED_KEYS = {
    "entry4",
    "exit5",
    "reduced4",
    "new_entry4",
    "status",
    "regime_meaning",
    "from_state",
    "event_type",
    "event_code",
    "to_state",
    "step_level",
}


def _row_lock_key(row: dict[str, Any]) -> str:
    return f"{row['entry4']}|{row['exit5']}|{row['reduced4']}|{row['new_entry4']}"


def validate_tableA_m8_execution_with_lock(payload: dict[str, Any]) -> list[str]:
    """
    Validates:
    1. structural integrity
    2. FSM / regime invariants
    3. exact canonical Table A lock
    """
    errors: list[str] = []

    if "tableA_m8_execution" not in payload:
        return ["Missing top-level key: tableA_m8_execution"]

    rows = payload["tableA_m8_execution"]

    if not isinstance(rows, list):
        return ["tableA_m8_execution must be a list"]

    if len(rows) != 32:
        errors.append(f"Expected exactly 32 rows, got {len(rows)}")

    seen_entry_exit_pairs: set[tuple[str, str]] = set()
    seen_lock_keys: set[str] = set()

    for i, row in enumerate(rows):
        prefix = f"row[{i}]"

        if not isinstance(row, dict):
            errors.append(f"{prefix}: row must be an object")
            continue

        missing = REQUIRED_KEYS - set(row.keys())
        if missing:
            errors.append(f"{prefix}: missing keys {sorted(missing)}")
            continue

        entry4 = row["entry4"]
        exit5 = row["exit5"]
        reduced4 = row["reduced4"]
        new_entry4 = row["new_entry4"]
        status = row["status"]
        regime_meaning = row["regime_meaning"]
        from_state = row["from_state"]
        event_type = row["event_type"]
        event_code = row["event_code"]
        to_state = row["to_state"]
        step_level = row["step_level"]

        if entry4 not in CANONICAL_ENTRY4:
            errors.append(f"{prefix}: invalid entry4 {entry4}")

        if reduced4 not in CANONICAL_ENTRY4:
            errors.append(f"{prefix}: invalid reduced4 {reduced4}")

        if new_entry4 not in CANONICAL_ENTRY4:
            errors.append(f"{prefix}: invalid new_entry4 {new_entry4}")

        if not isinstance(exit5, str) or len(exit5) != 5:
            errors.append(f"{prefix}: exit5 must be a 5-char string")

        if new_entry4 != reduced4:
            errors.append(f"{prefix}: new_entry4 must equal reduced4")

        if status not in ALLOWED_STATUS:
            errors.append(f"{prefix}: invalid status {status}")

        if regime_meaning not in ALLOWED_REGIME:
            errors.append(f"{prefix}: invalid regime_meaning {regime_meaning}")

        if from_state not in ALLOWED_STATES:
            errors.append(f"{prefix}: invalid from_state {from_state}")

        if to_state not in ALLOWED_STATES:
            errors.append(f"{prefix}: invalid to_state {to_state}")

        if event_type not in ALLOWED_EVENT_TYPES:
            errors.append(f"{prefix}: invalid event_type {event_type}")

        if not isinstance(event_code, str) or not event_code.strip():
            errors.append(f"{prefix}: event_code must be a non-empty string")

        if step_level not in {0, 1, 2}:
            errors.append(f"{prefix}: step_level must be 0, 1, or 2")

        pair = (entry4, exit5)
        if pair in seen_entry_exit_pairs:
            errors.append(f"{prefix}: duplicate (entry4, exit5) pair {pair}")
        else:
            seen_entry_exit_pairs.add(pair)

        lock_key = _row_lock_key(row)
        if lock_key in seen_lock_keys:
            errors.append(f"{prefix}: duplicate canonical lock row {lock_key}")
        else:
            seen_lock_keys.add(lock_key)

        if lock_key not in CANONICAL_TABLE_A_LOCK:
            errors.append(f"{prefix}: row not present in canonical Table A lock: {lock_key}")

        # Forbidden direct regime flips
        if from_state == "S_UP" and to_state == "S_DOWN":
            errors.append(f"{prefix}: forbidden direct transition S_UP -> S_DOWN")
        if from_state == "S_DOWN" and to_state == "S_UP":
            errors.append(f"{prefix}: forbidden direct transition S_DOWN -> S_UP")

        # Status semantics
        if status == "BREAK" and to_state != "S_RANGE":
            errors.append(f"{prefix}: BREAK must go to S_RANGE")

        if status == "CONT":
            if from_state != to_state:
                errors.append(f"{prefix}: CONT must preserve state")
            if from_state == "S_RANGE":
                errors.append(f"{prefix}: CONT cannot start from S_RANGE")

        if status == "ENTRY":
            if from_state != "S_RANGE":
                errors.append(f"{prefix}: ENTRY must start from S_RANGE")
            if to_state not in {"S_UP", "S_DOWN"}:
                errors.append(f"{prefix}: ENTRY must end in S_UP or S_DOWN")

        if status == "RANGE":
            if from_state != "S_RANGE" or to_state != "S_RANGE":
                errors.append(f"{prefix}: RANGE must remain inside S_RANGE")

        # Event/step consistency
        if event_type == "process" and step_level != 0:
            errors.append(f"{prefix}: process must have step_level 0")

        if event_type == "fix" and step_level not in {1, 2}:
            errors.append(f"{prefix}: fix must have step_level 1 or 2")

        if event_type == "structure" and step_level not in {1, 2}:
            errors.append(f"{prefix}: structure must have step_level 1 or 2")

        # Regime meaning semantics
        if regime_meaning == "UP_CONT" and to_state != "S_UP":
            errors.append(f"{prefix}: UP_CONT must end in S_UP")

        if regime_meaning == "DOWN_CONT" and to_state != "S_DOWN":
            errors.append(f"{prefix}: DOWN_CONT must end in S_DOWN")

        if regime_meaning == "UP_BREAK_TO_RANGE":
            if from_state != "S_UP" or to_state != "S_RANGE":
                errors.append(f"{prefix}: UP_BREAK_TO_RANGE must be S_UP -> S_RANGE")

        if regime_meaning == "DOWN_BREAK_TO_RANGE":
            if from_state != "S_DOWN" or to_state != "S_RANGE":
                errors.append(f"{prefix}: DOWN_BREAK_TO_RANGE must be S_DOWN -> S_RANGE")

        if regime_meaning in {"RANGE_PREP_UP", "RANGE_PREP_DOWN", "RANGE_INTERNAL"}:
            if from_state != "S_RANGE" or to_state != "S_RANGE":
                errors.append(f"{prefix}: range-prep/internal must stay in S_RANGE")

    # Global exact-lock checks
    missing_rows = sorted(CANONICAL_TABLE_A_LOCK - seen_lock_keys)
    extra_rows = sorted(seen_lock_keys - CANONICAL_TABLE_A_LOCK)

    if missing_rows:
        errors.append("Missing canonical rows:")
        errors.extend([f"  - {row}" for row in missing_rows])

    if extra_rows:
        errors.append("Unexpected extra rows:")
        errors.extend([f"  - {row}" for row in extra_rows])

    return errors
