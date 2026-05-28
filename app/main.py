from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db

# Import models before create_all so SQLAlchemy registers the tables.
from app import models  # noqa: F401
from app.schemas import (
    ClientCreate,
    ClientCreateResponse,
    ErrorResponse,
    HealthResponse,
    WebhookCardUpdated,
    WebhookProcessResponse,
)
from app.services import (
    ClientNotFoundError,
    DuplicateClientError,
    DuplicateWebhookEventError,
    create_client,
    process_card_updated_webhook,
)

app = FastAPI(title="Pipefy Tech Interview", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/clientes",
    response_model=ClientCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"model": ErrorResponse}},
)
def create_client_endpoint(payload: ClientCreate, db: Session = Depends(get_db)) -> ClientCreateResponse:
    try:
        return create_client(db, payload)
    except DuplicateClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="client with this email already exists",
        ) from exc


@app.post(
    "/webhooks/pipefy/card-updated",
    response_model=WebhookProcessResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
)
def process_card_updated_webhook_endpoint(
    payload: WebhookCardUpdated,
    db: Session = Depends(get_db),
) -> WebhookProcessResponse:
    try:
        return process_card_updated_webhook(db, payload)
    except DuplicateWebhookEventError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="event_id already processed",
        ) from exc
    except ClientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="client not found",
        ) from exc
