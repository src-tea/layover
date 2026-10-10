from __future__ import annotations

from datetime import datetime


def parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def calculate_usable_window_minutes(total_minutes: int, exit_buffer_minutes: int = 60, return_buffer_minutes: int = 60) -> int:
    if total_minutes <= 0:
        return 0
    usable = total_minutes - exit_buffer_minutes - return_buffer_minutes
    return max(0, usable)


def overlap_minutes(start_a, end_a, start_b, end_b) -> int:
    start = max(start_a, start_b)
    end = min(end_a, end_b)
    if end <= start:
        return 0
    return int((end - start).total_seconds() / 60)
