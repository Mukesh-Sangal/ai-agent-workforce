import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.api.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Agent Workforce", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(router)