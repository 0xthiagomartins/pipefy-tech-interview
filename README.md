# Pipefy Tech Interview

API backend simples para gerenciamento de clientes com integracao simulada ao Pipefy.

## Stack

- FastAPI
- SQLAlchemy
- SQLite local e perecivel
- Pytest

## O que a API faz

- cria clientes
- salva dados em SQLite
- processa webhook de atualizacao de card
- aplica regra de prioridade por patrimonio
- monta payloads GraphQL compativeis com as mutations `createCard` e `updateCardField`

## Estrutura

```text
app/
  db.py
  main.py
  models.py
  pipefy.py
  schemas.py
  services.py
tests/
  conftest.py
  test_clients.py
  test_health.py
pyproject.toml
```

## Requisitos

- Python 3.11+

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

API disponivel em `http://127.0.0.1:8000`.

## Como rodar os testes

```bash
source .venv/bin/activate
pytest -q
```

## Endpoints

### Healthcheck

```bash
curl http://127.0.0.1:8000/health
```

### Criar cliente

```bash
curl -X POST http://127.0.0.1:8000/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_nome": "Joao Silva",
    "cliente_email": "joao.silva@example.com",
    "tipo_solicitacao": "Atualizacao cadastral",
    "valor_patrimonio": 250000
  }'
```

### Processar webhook

```bash
curl -X POST http://127.0.0.1:8000/webhooks/pipefy/card-updated \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_123",
    "card_id": "card_456",
    "cliente_email": "joao.silva@example.com",
    "timestamp": "2026-05-18T12:00:00Z"
  }'
```

## Regras de negocio

- cliente novo entra com status `Aguardando Analise`
- webhook duplicado por `event_id` retorna `409`
- patrimonio maior ou igual a `200000` gera `prioridade_alta`
- patrimonio menor que `200000` gera `prioridade_normal`
- quando o webhook e processado, o status do cliente vira `Processado`

## Pipefy

As mutations GraphQL simuladas estao em `app/pipefy.py`.

- `createCard` e usada na criacao do cliente
- `updateCardField` e usada duas vezes no webhook:
  uma para `status` e outra para `prioridade`

Nao existe integracao real com a API do Pipefy nesta versao. Apenas a estrutura da mutation e do payload foi mantida no codigo.

## Respostas de erro

- `409` ao tentar criar cliente com email duplicado
- `409` ao reenviar um webhook com `event_id` ja processado
- `404` ao processar webhook de um cliente inexistente
- `422` quando o payload enviado e invalido

## Guia rapido para a defesa

- A aplicacao foi mantida simples de proposito: FastAPI, SQLAlchemy e SQLite local
- A regra de negocio ficou concentrada em `app/services.py`
- A camada HTTP ficou em `app/main.py`
- As mutations do Pipefy ficaram isoladas em `app/pipefy.py`
- O webhook usa idempotencia por `event_id`
- A prioridade e derivada exclusivamente de `valor_patrimonio`
