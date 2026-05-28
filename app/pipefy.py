from app.schemas import PipefyRequestPayload

CREATE_CARD_MUTATION = """
mutation CreateCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
    }
  }
}
""".strip()

UPDATE_CARD_FIELD_MUTATION = """
mutation UpdateCardField($input: UpdateCardFieldInput!) {
  updateCardField(input: $input) {
    success
    card {
      id
    }
  }
}
""".strip()


def build_create_card_request(
    *,
    pipe_id: str,
    cliente_nome: str,
    cliente_email: str,
    tipo_solicitacao: str,
    valor_patrimonio: float,
) -> PipefyRequestPayload:
    return PipefyRequestPayload(
        query=CREATE_CARD_MUTATION,
        variables={
            "input": {
                "pipe_id": pipe_id,
                "title": cliente_nome,
                "fields_attributes": [
                    {"field_id": "cliente_nome", "field_value": cliente_nome},
                    {"field_id": "cliente_email", "field_value": cliente_email},
                    {"field_id": "tipo_solicitacao", "field_value": tipo_solicitacao},
                    {"field_id": "valor_patrimonio", "field_value": str(valor_patrimonio)},
                ],
            }
        },
    )


def build_update_card_field_requests(
    *,
    card_id: str,
    status: str,
    prioridade: str,
) -> list[PipefyRequestPayload]:
    return [
        PipefyRequestPayload(
            query=UPDATE_CARD_FIELD_MUTATION,
            variables={
                "input": {
                    "card_id": card_id,
                    "field_id": "status",
                    "new_value": status,
                }
            },
        ),
        PipefyRequestPayload(
            query=UPDATE_CARD_FIELD_MUTATION,
            variables={
                "input": {
                    "card_id": card_id,
                    "field_id": "prioridade",
                    "new_value": prioridade,
                }
            },
        ),
    ]
