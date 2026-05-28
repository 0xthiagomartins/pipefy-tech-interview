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

- inicializar a API com FastAPI
- modelar persistencia com SQLAlchemy
- usar SQLite3 local
- adicionar testes automatizados
- documentar execucao e exemplos de curl
