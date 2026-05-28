from app.services import DEFAULT_CLIENT_STATUS, HIGH_PRIORITY, NORMAL_PRIORITY, PROCESSED_CLIENT_STATUS


def test_create_client_persists_data(client) -> None:
    response = client.post(
        "/clientes",
        json={
            "cliente_nome": "Joao Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualizacao cadastral",
            "valor_patrimonio": 250000,
        },
    )

    assert response.status_code == 201

    payload = response.json()
    assert payload["client"]["cliente_nome"] == "Joao Silva"
    assert payload["client"]["cliente_email"] == "joao.silva@example.com"
    assert payload["client"]["status"] == DEFAULT_CLIENT_STATUS
    assert payload["pipefy_request"]["variables"]["input"]["fields_attributes"][1]["field_value"] == (
        "joao.silva@example.com"
    )


def test_webhook_sets_high_priority_for_high_net_worth_client(client) -> None:
    client.post(
        "/clientes",
        json={
            "cliente_nome": "Joao Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualizacao cadastral",
            "valor_patrimonio": 250000,
        },
    )

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_123",
            "card_id": "card_456",
            "cliente_email": "joao.silva@example.com",
            "timestamp": "2026-05-18T12:00:00Z",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["client"]["status"] == PROCESSED_CLIENT_STATUS
    assert payload["client"]["prioridade"] == HIGH_PRIORITY
    assert payload["pipefy_requests"][0]["variables"]["input"]["field_id"] == "status"
    assert payload["pipefy_requests"][1]["variables"]["input"]["new_value"] == HIGH_PRIORITY


def test_webhook_sets_normal_priority_for_lower_net_worth_client(client) -> None:
    client.post(
        "/clientes",
        json={
            "cliente_nome": "Maria Souza",
            "cliente_email": "maria.souza@example.com",
            "tipo_solicitacao": "Novo investimento",
            "valor_patrimonio": 150000,
        },
    )

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_124",
            "card_id": "card_789",
            "cliente_email": "maria.souza@example.com",
            "timestamp": "2026-05-18T12:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["client"]["prioridade"] == NORMAL_PRIORITY


def test_webhook_rejects_duplicate_event_id(client) -> None:
    client.post(
        "/clientes",
        json={
            "cliente_nome": "Joao Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualizacao cadastral",
            "valor_patrimonio": 250000,
        },
    )

    payload = {
        "event_id": "evt_123",
        "card_id": "card_456",
        "cliente_email": "joao.silva@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }

    first_response = client.post("/webhooks/pipefy/card-updated", json=payload)
    second_response = client.post("/webhooks/pipefy/card-updated", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "event_id already processed"}


def test_create_client_rejects_duplicate_email(client) -> None:
    payload = {
        "cliente_nome": "Joao Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualizacao cadastral",
        "valor_patrimonio": 250000,
    }

    first_response = client.post("/clientes", json=payload)
    second_response = client.post("/clientes", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "client with this email already exists"}


def test_webhook_returns_not_found_when_client_does_not_exist(client) -> None:
    response = client.post(
        "/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_999",
            "card_id": "card_999",
            "cliente_email": "missing@example.com",
            "timestamp": "2026-05-18T12:00:00Z",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "client not found"}
