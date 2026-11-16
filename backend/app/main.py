import logging

from fastapi import FastAPI

from app.api.routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AI Agent Workforce", version="0.1.0")
app.include_router(router)