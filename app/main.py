from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import text

from app.db.session import SessionLocal
from app.modules.anilist.profile.router import router as profile_router
from app.modules.anilist.router import router as anilist_router
from app.modules.auth.router import router as auth_router

app = FastAPI(title="Neko Track Backend")

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(anilist_router)


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
