# Kondo API

Backend FastAPI do Kondo.

## Setup

```bash
cd backend
uv sync
```

## Rodar

```bash
uv run uvicorn app.main:app --reload
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
```

