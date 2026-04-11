from __future__ import annotations

from typing import Any


CANONICAL_ENTRY4 = {
    "2143", "2413", "1324", "2431", "3124",
    "4213", "4231", "1342", "3142", "3412",
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


def validate_tableA_m8_execution(payload: dict[str, Any]) -> list[str]:
    """
    Structural + semantic validator for M8 execution engine JSON.
    Returns a list of errors. Empty list means validation passed.
    """
    errors: list[str] = []

    if "tableA_m8_execution" not in payload:
        return ["Missing top-level key: tableA_m8_execution"]

    rows = payload["tableA_m8_execution"]

    if not isinstance(rows, list):
        return ["tableA_m8_execution must be a list"]

    seen_pairs: set[tuple[str, str]] = set()

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
        if pair in seen_pairs:
            errors.append(f"{prefix}: duplicate (entry4, exit5) pair {pair}")
        else:
            seen_pairs.add(pair)

        # Forbidden direct regime flips
        if from_state == "S_UP" and to_state == "S_DOWN":
            errors.append(f"{prefix}: forbidden direct transition S_UP -> S_DOWN")

        if from_state == "S_DOWN" and to_state == "S_UP":
            errors.append(f"{prefix}: forbidden direct transition S_DOWN -> S_UP")

        # Status semantics
        if status == "BREAK":
            if to_state != "S_RANGE":
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

        # Event / step consistency
        if event_type == "process" and step_level != 0:
            errors.append(f"{prefix}: process must have step_level 0")

        if event_type == "fix" and step_level not in {1, 2}:
            errors.append(f"{prefix}: fix must have step_level 1 or 2")

        if event_type == "structure" and step_level not in {1, 2}:
            errors.append(f"{prefix}: structure must have step_level 1 or 2")

        # Regime meaning semantics
        if regime_meaning == "UP_CONT":
            if to_state != "S_UP":
                errors.append(f"{prefix}: UP_CONT must end in S_UP")

        if regime_meaning == "DOWN_CONT":
            if to_state != "S_DOWN":
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

    return errors
