from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import agreements, announcements, dashboard, documents, finance, tickets


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API do Kondo para operacao condominial AI-native.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "kondo-api"}


app.include_router(dashboard.router)
app.include_router(tickets.router)
app.include_router(finance.router)
app.include_router(agreements.router)
app.include_router(announcements.router)
app.include_router(documents.router)

