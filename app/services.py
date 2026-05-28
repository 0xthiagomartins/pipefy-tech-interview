from sqlalchemy.orm import Session

from app.models import Client, WebhookEvent
from app.pipefy import build_create_card_request, build_update_card_field_requests
from app.schemas import (
    ClientCreate,
    ClientCreateResponse,
    WebhookCardUpdated,
    WebhookProcessResponse,
)

DEFAULT_CLIENT_STATUS = "Aguardando Analise"
PROCESSED_CLIENT_STATUS = "Processado"
HIGH_PRIORITY = "prioridade_alta"
NORMAL_PRIORITY = "prioridade_normal"
DEFAULT_PIPE_ID = "demo-pipe-id"


class DuplicateClientError(Exception):
    pass


class DuplicateWebhookEventError(Exception):
    pass


class ClientNotFoundError(Exception):
    pass


def create_client(db: Session, payload: ClientCreate) -> ClientCreateResponse:
    existing_client = db.query(Client).filter(Client.cliente_email == payload.cliente_email).first()
    if existing_client is not None:
        raise DuplicateClientError

    client = Client(
        cliente_nome=payload.cliente_nome,
        cliente_email=payload.cliente_email,
        tipo_solicitacao=payload.tipo_solicitacao,
        valor_patrimonio=payload.valor_patrimonio,
        status=DEFAULT_CLIENT_STATUS,
        prioridade=None,
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    pipefy_request = build_create_card_request(
        pipe_id=DEFAULT_PIPE_ID,
        cliente_nome=client.cliente_nome,
        cliente_email=client.cliente_email,
        tipo_solicitacao=client.tipo_solicitacao,
        valor_patrimonio=client.valor_patrimonio,
    )
    return ClientCreateResponse(client=client, pipefy_request=pipefy_request)


def process_card_updated_webhook(db: Session, payload: WebhookCardUpdated) -> WebhookProcessResponse:
    existing_event = db.query(WebhookEvent).filter(WebhookEvent.event_id == payload.event_id).first()
    if existing_event is not None:
        raise DuplicateWebhookEventError

    client = db.query(Client).filter(Client.cliente_email == payload.cliente_email).first()
    if client is None:
        raise ClientNotFoundError

    prioridade = HIGH_PRIORITY if client.valor_patrimonio >= 200000 else NORMAL_PRIORITY
    client.status = PROCESSED_CLIENT_STATUS
    client.prioridade = prioridade

    webhook_event = WebhookEvent(
        event_id=payload.event_id,
        card_id=payload.card_id,
        cliente_email=payload.cliente_email,
        timestamp=payload.timestamp.isoformat(),
    )
    db.add(webhook_event)
    db.commit()
    db.refresh(client)

    pipefy_requests = build_update_card_field_requests(
        card_id=payload.card_id,
        status=client.status,
        prioridade=prioridade,
    )
    return WebhookProcessResponse(client=client, pipefy_requests=pipefy_requests)
