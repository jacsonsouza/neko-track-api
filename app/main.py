from fastapi import FastAPI

from app.modules.auth.router import router as auth_router

app = FastAPI(title="Neko Track Backend")

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
