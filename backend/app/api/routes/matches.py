from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.repositories import store
from app.services.airport_service import resolve_airport
from app.services.matching_service import find_candidates
from app.utils.time_utils import parse_datetime

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("")
def find_matches(airport_code: str | None = None, layover_id: str | None = None):
    pairing_locked_ids = store.list_pairing_locked_user_ids()
    layovers = [item for item in store.list_layovers() if item.get("user_id") not in pairing_locked_ids]
    if layover_id:
        selected = [item for item in layovers if item["id"] == layover_id]
        if not selected:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layover not found")
        candidates = [item for item in layovers if item["id"] != layover_id]
        results = find_candidates(selected, candidates)
    else:
        if airport_code:
            airports = store.list_airports()
            airport = resolve_airport(airports, airport_code)
            if airport is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown airport code or name")
            layovers = [
                item for item in layovers
                if (resolve_airport(airports, item.get("airport_code", "")) or {}).get("iata_code") == airport["iata_code"]
            ]
        results = []
        for index, first in enumerate(layovers):
            for second in layovers[index + 1 :]:
                results.extend(find_candidates([first], [second]))

    return {"items": results}
