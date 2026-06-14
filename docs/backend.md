# Backend

## Stack

- FastAPI para API HTTP.
- SQLAlchemy para ORM.
- Pydantic para validacao e contratos.
- `uv` para ambiente e dependencias Python.
- SQLite no desenvolvimento.
- PostgreSQL em producao.

## Setup com uv

Criar o projeto dentro de `backend/`:

```bash
cd backend
uv init
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings
```

Dependencias futuras recomendadas:

```bash
uv add alembic python-dotenv
uv add openai
uv add psycopg[binary]
```

Rodar a API:

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

## Variaveis de ambiente

```env
DATABASE_URL=sqlite:///./kondo.db
CORS_ORIGINS=http://localhost:5173
OPENAI_API_KEY=
JWT_SECRET_KEY=dev-only-change-me
```

O arquivo versionado `backend/.env.example` deve ser usado como base. O arquivo
real `backend/.env` e local e nao deve ser commitado.

Para producao com Postgres:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/kondo
```

## Estrutura sugerida

```txt
backend/
  app/
    main.py
    core/
      config.py
      database.py
      deps.py
      security.py
    models/
      attachments.py
      audit.py
      base.py
      content.py
      finance.py
      identity.py
      operations.py
      property.py
      vendors.py
    schemas/
    routers/
    services/
    seed.py
  storage/
    uploads/
  tests/
  alembic/
  pyproject.toml
```

## Banco e seed

A camada de banco fica em `app/core/database.py` e usa SQLAlchemy com
`DATABASE_URL`. O SQLite e o padrao local para desenvolvimento rapido, mas os
modelos devem continuar portaveis para Postgres.

Criar tabelas e popular dados demo:

```bash
cd backend
uv run python -m app.seed
```

Rodar migrations:

```bash
cd backend
uv run alembic upgrade head
```

O seed cria o Condominio Jardim Aurora com usuarios demo. A senha dos usuarios
demo e:

```txt
kondo123
```

## Auth e permissoes

O MVP usa JWT local e hash de senha com PBKDF2.

Papeis:

- `platform_admin`: admin interno da plataforma.
- `manager`: sindico, sindico profissional ou gestor operacional.
- `board_member`: conselho e governanca.
- `resident`: morador, proprietario, inquilino ou ocupante.

Nao existe login de condominio. Pessoas logam como `User` e recebem acesso por
`Membership`.

## Chamados e Kanban

Chamados ja sao persistidos via SQLAlchemy. Ao criar um chamado, a API tambem
cria um `WorkItem` para o Kanban operacional.

Status padrao do Kanban:

- `received`
- `in_review`
- `vendor_contacted`
- `waiting_approval`
- `in_progress`
- `resolved`

## Regras de implementacao

- Usar `Decimal` ou `Numeric` para valores financeiros, nunca `float`.
- Usar `Date` e `DateTime` para vencimentos e timestamps.
- Evitar recursos especificos de Postgres no MVP.
- Manter respostas de IA atras de `services/ai_service.py`.
- Permitir que o MVP rode sem chave de IA, usando respostas simuladas.
- Documentar toda funcionalidade criada no mesmo PR.
- Atualizar `docs/api.md` sempre que endpoints forem criados, alterados ou
  removidos.

## Storage local

Anexos usam storage local apenas para desenvolvimento rapido:

```txt
backend/storage/uploads/
```

Arquivos reais nao sao commitados. O backend expõe download por endpoint
controlado e salva no banco apenas metadados de `Attachment`.

## SQLite agora, Postgres depois

SQLite e suficiente para desenvolvimento e demo. A migracao para Postgres deve
ser simples se os modelos SQLAlchemy forem portaveis e as queries evitarem
funcoes especificas do banco.
