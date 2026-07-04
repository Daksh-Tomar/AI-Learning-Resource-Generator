from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LearnLens AI API", version="1.0.0")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import chat
from .database import engine
from . import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "LearnLens AI API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
