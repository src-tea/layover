from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.airports import router as airports_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.health import router as health_router
from app.api.routes.itineraries import router as itineraries_router
from app.api.routes.layovers import router as layovers_router
from app.api.routes.matches import router as matches_router
from app.api.routes.payments import router as payments_router
from app.api.routes.storage import router as storage_router
from app.api.routes.users import router as users_router
from app.core.config import settings

app = FastAPI(
    title="LAYOVER API",
    description="Layover storage sharing and travel planning API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(airports_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(layovers_router)
app.include_router(matches_router)
app.include_router(storage_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(itineraries_router)


@app.get("/")
def root():
    return {"app": "LAYOVER", "status": "ok"}
