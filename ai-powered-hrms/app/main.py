from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI-Powered HRMS", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/", tags=["root"])  # simple health/landing
    async def root() -> dict:
        return {"status": "ok", "service": "ai-hrms"}

    return app


app = create_app()


