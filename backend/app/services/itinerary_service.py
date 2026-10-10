from __future__ import annotations

from datetime import datetime, timedelta

from app.utils.time_utils import calculate_usable_window_minutes, parse_datetime

MOCK_ACTIVITY_CATALOG = [
    {"title": "Coffee & reset", "category": "food", "duration_minutes": 45, "priority": 4},
    {"title": "Quick city walk", "category": "explore", "duration_minutes": 60, "priority": 3},
    {"title": "Museum stop", "category": "culture", "duration_minutes": 90, "priority": 5},
    {"title": "Light shopping", "category": "shopping", "duration_minutes": 75, "priority": 4},
    {"title": "Stretch + shower", "category": "wellness", "duration_minutes": 45, "priority": 2},
]


def build_itinerary(layover: dict, usable_minutes: int | None = None):
    start_dt = parse_datetime(layover["arrival_time"])
    layover_minutes = int((parse_datetime(layover["departure_time"]) - start_dt).total_seconds() / 60)
    usable = usable_minutes if usable_minutes is not None else calculate_usable_window_minutes(layover_minutes, 60, 60)

    chosen = []
    total = 0
    for activity in sorted(MOCK_ACTIVITY_CATALOG, key=lambda item: (-item["priority"], item["duration_minutes"])):
        if total + activity["duration_minutes"] <= usable:
            chosen.append(activity)
            total += activity["duration_minutes"]

    start = start_dt + timedelta(minutes=60)
    activities = []
    current = start
    for item in chosen:
        end = current + timedelta(minutes=item["duration_minutes"])
        activities.append({
            "title": item["title"],
            "category": item["category"],
            "start_time": current.isoformat(),
            "end_time": end.isoformat(),
            "duration_minutes": item["duration_minutes"],
        })
        current = end

    return {
        "id": f"itinerary-{layover['id']}",
        "layover_id": layover["id"],
        "start_time": start.isoformat(),
        "end_time": current.isoformat(),
        "usable_minutes": usable,
        "activities": activities,
    }
