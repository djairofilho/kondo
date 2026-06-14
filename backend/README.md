# Kondo API

Backend FastAPI do Kondo.

## Setup

```bash
cd backend
cp .env.example .env
uv sync
```

## Rodar

```bash
uv run uvicorn app.main:app --reload
```

## Criar dados demo

```bash
uv run python -m app.seed
```

API local:

```txt
http://localhost:8000
```

Documentacao interativa:

```txt
http://localhost:8000/docs
```

## Variaveis de ambiente

```env
APP_NAME=Kondo API
DATABASE_URL=sqlite:///./kondo.db
CORS_ORIGINS=http://localhost:5173
OPENAI_API_KEY=
```
