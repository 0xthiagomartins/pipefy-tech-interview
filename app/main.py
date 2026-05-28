from fastapi import FastAPI

from app.db import Base, engine

# Import models before create_all so SQLAlchemy registers the tables.
from app import models  # noqa: F401
from app.schemas import HealthResponse

app = FastAPI(title="Pipefy Tech Interview", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")

