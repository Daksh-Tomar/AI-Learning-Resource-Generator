from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging, RequestContextLogMiddleware
from app.core.config import settings

# Initialize logging
setup_logging(settings.LOG_LEVEL)

def create_app() -> FastAPI:
    app = FastAPI(
        title="LearnLens AI API",
        version="1.0.0",
        description="Phase 0 API Foundation for LearnLens Recommendation System"
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextLogMiddleware)

    # Exceptions
    setup_exception_handlers(app)

    # Routers
    app.include_router(api_router)
    
    @app.get("/")
    def read_root():
        return {"status": "ok", "message": "LearnLens AI API is running (Phase 0 Foundation)"}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
