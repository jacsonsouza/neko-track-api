from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import SessionLocal
from app.modules.anilist.router import router as anilist_router
from app.modules.auth.router import router as auth_router

app = FastAPI(title="Neko Track Backend")

app.include_router(auth_router)
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
