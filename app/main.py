from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy import text

from app.core.errors import ERROR_RESPONSES
from app.core.exception_handlers import register_exception_handlers
from app.db.session import SessionLocal
from app.modules.anilist.activities.router import (
    activities_router,
    my_activities_router,
)
from app.modules.anilist.anime_details.router import animes_router
from app.modules.anilist.anime_lists.router import router as user_anime_lists_router
from app.modules.anilist.gateway import create_gateway
from app.modules.anilist.profile.router import router as profile_router
from app.modules.anilist.replies.router import router as replies_router
from app.modules.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Owns the AniList gateway: one ``httpx`` client for the whole process."""
    app.state.anilist_gateway = create_gateway()
    try:
        yield
    finally:
        await app.state.anilist_gateway.aclose()


app = FastAPI(title="Neko Track Backend", version="1.0.0", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(auth_router, responses=ERROR_RESPONSES)
app.include_router(profile_router, responses=ERROR_RESPONSES)
app.include_router(activities_router, responses=ERROR_RESPONSES)
app.include_router(my_activities_router, responses=ERROR_RESPONSES)
app.include_router(user_anime_lists_router, responses=ERROR_RESPONSES)
app.include_router(animes_router, responses=ERROR_RESPONSES)
app.include_router(replies_router, responses=ERROR_RESPONSES)


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    db: Literal["ok", "error"]


class RouteInfo(BaseModel):
    path: str
    name: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        db = SessionLocal()
        db.execute(text("Select 1"))
        return HealthResponse(status="ok", db="ok")
    except Exception:
        return HealthResponse(status="degraded", db="error")
    finally:
        try:
            db.close()
        except Exception:
            pass


@app.get("/routes", response_model=list[RouteInfo])
def listar_todas_as_rotas() -> list[RouteInfo]:
    return [
        RouteInfo(path=r.path, name=r.name) for r in app.routes if isinstance(r, APIRoute)
    ]
