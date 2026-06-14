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
    models/
    schemas/
    routers/
    services/
  pyproject.toml
```

## Regras de implementacao

- Usar `Decimal` ou `Numeric` para valores financeiros, nunca `float`.
- Usar `Date` e `DateTime` para vencimentos e timestamps.
- Evitar recursos especificos de Postgres no MVP.
- Manter respostas de IA atras de `services/ai_service.py`.
- Permitir que o MVP rode sem chave de IA, usando respostas simuladas.

## SQLite agora, Postgres depois

SQLite e suficiente para desenvolvimento e demo. A migracao para Postgres deve
ser simples se os modelos SQLAlchemy forem portaveis e as queries evitarem
funcoes especificas do banco.
