from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError
from sqlalchemy import text

from app.db.session import SessionLocal
from app.modules.anilist.activities.router import router as activities_router
from app.modules.anilist.anime_lists.router import router as user_anime_lists_router
from app.modules.anilist.profile.router import router as profile_router
from app.modules.anilist.replies.router import router as replies_router
from app.modules.auth.router import router as auth_router

app = FastAPI(title="Neko Track Backend")

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(activities_router)
app.include_router(user_anime_lists_router)
app.include_router(replies_router)


@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("Select 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        return {"status": "degraded", "db": "error"}
    finally:
        try:
            db.close()
        except Exception:
            pass


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=502,
        content={"detail": "Invalid AniList response"},
    )


@app.get("/routes")
def listar_todas_as_rotas():
    return [
        {"path": r.path, "name": r.name} for r in app.routes if isinstance(r, APIRoute)
    ]
