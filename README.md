# Pipefy Tech Interview

Implementacao simples de uma API backend para gerenciamento de clientes com integracao simulada ao Pipefy.

## Stack

- FastAPI
- SQLAlchemy
- SQLite local e perecivel
- Pytest

## Objetivo

Esta aplicacao expoe endpoints para:

- criar clientes
- persistir dados localmente
- processar webhook de atualizacao de card
- aplicar regra de prioridade por patrimonio
- montar payloads GraphQL compativeis com Pipefy

## Status

Projeto em desenvolvimento para teste tecnico.

## Proximos passos

- instalar dependencias
- executar a API localmente
- implementar os endpoints do teste
- adicionar testes automatizados obrigatorios
- documentar exemplos de uso

## Estrutura inicial

```text
app/
  __init__.py
  db.py
  main.py
  models.py
  schemas.py
tests/
  test_health.py
pyproject.toml
```
