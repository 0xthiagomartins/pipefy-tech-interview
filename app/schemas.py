from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, field_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str


class ClientCreate(BaseModel):
    cliente_nome: str
    cliente_email: str
    tipo_solicitacao: str
    valor_patrimonio: float

    @field_validator("cliente_nome", "cliente_email", "tipo_solicitacao")
    @classmethod
    def validate_required_string(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("field is required")
        return cleaned_value

    @field_validator("cliente_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.match(value):
            raise ValueError("invalid email")
        return value

    @field_validator("valor_patrimonio")
    @classmethod
    def validate_valor_patrimonio(cls, value: float) -> float:
        if value < 0:
            raise ValueError("valor_patrimonio must be greater than or equal to zero")
        return value


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_nome: str
    cliente_email: str
    tipo_solicitacao: str
    valor_patrimonio: float
    status: str
    prioridade: str | None


class PipefyRequestPayload(BaseModel):
    query: str
    variables: dict[str, object]


class ClientCreateResponse(BaseModel):
    client: ClientResponse
    pipefy_request: PipefyRequestPayload


class WebhookCardUpdated(BaseModel):
    event_id: str
    card_id: str
    cliente_email: str
    timestamp: datetime

    @field_validator("event_id", "card_id", "cliente_email")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("field is required")
        return cleaned_value

    @field_validator("cliente_email")
    @classmethod
    def validate_webhook_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.match(value):
            raise ValueError("invalid email")
        return value


class WebhookProcessResponse(BaseModel):
    client: ClientResponse
    pipefy_requests: list[PipefyRequestPayload]
