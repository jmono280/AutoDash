from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, chat, hours, imports, sales, technicians, wip

app = FastAPI(title="Automania Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(imports.router, prefix="/imports", tags=["imports"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(hours.router, prefix="/hours", tags=["hours"])
app.include_router(technicians.router, prefix="/technicians", tags=["technicians"])
app.include_router(wip.router, prefix="/wip", tags=["wip"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "app": "automania"}
