# Separacao de Repositorios

## Decisao

A partir desta etapa, o Kondo fica dividido em dois repositorios locais:

```txt
kondo-front/  # frontend React / TanStack / Vite
kondo/        # backend FastAPI, banco, testes e documentacao
```

O repositorio `kondo` nao deve voltar a ter uma aplicacao em `frontend/`. O
diretorio `frontend/` que existia aqui foi removido da arvore de trabalho e a
evolucao visual deve acontecer em `../kondo-front`.

## Por que separar

- O frontend veio de um projeto proprio e tem toolchain independente.
- O backend precisa continuar focado em API, dominio, banco e contratos.
- A separacao reduz ruido de dependencias Node dentro do repositorio Python.
- Cada parte pode evoluir com comandos, lockfiles e revisoes especificas.

## Responsabilidades

### `kondo-front`

- Rotas, telas e layout.
- Componentes de interface.
- Dados mockados de demo enquanto a integracao nao estiver completa.
- Chamadas para a API quando os contratos estiverem conectados.
- Documentacao de setup do frontend.

### `kondo`

- API FastAPI.
- Modelos SQLAlchemy e migrations Alembic.
- Servicos de dominio.
- Testes de backend.
- Documentacao de API, arquitetura, produto, demo e roadmap.

## Contrato entre front e back

- Endpoints e payloads ficam documentados em `kondo/docs/api.md`.
- Mudancas de contrato devem atualizar o backend e sinalizar o impacto no
  frontend.
- O backend deve manter CORS liberado para `http://localhost:5173` em
  desenvolvimento.

## Comandos locais

Backend:

```bash
cd kondo/backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

Frontend:

```bash
cd kondo-front
bun install
bun run dev
```
