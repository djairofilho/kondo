# Kondo

Kondo e uma plataforma AI-native para a vida em condominio. Ela facilita a
rotina do sindico, aumenta a transparencia para o condominio e da ao
inquilino/morador um canal simples para resolver problemas, acompanhar status e
entender regras.

O objetivo e reduzir administracao manual, aumentar confianca entre as partes e
criar uma base de dados operacional que no futuro possa habilitar produtos
financeiros para condominios.

## Problema

Condominios ainda dependem de planilhas, PDFs, e-mails e processos manuais para
chamados, prestacao de contas, inadimplencia, documentos e comunicados. Para o
sindico, isso gera retrabalho. Para o condominio, gera baixa governanca. Para o
inquilino ou morador, gera demora, duvida e falta de visibilidade.

## Solucao

O Kondo centraliza a operacao do condominio em um painel web e usa IA para:

- classificar chamados e priorizar urgencias;
- explicar prestacao de contas em linguagem simples;
- simular acordos de inadimplencia;
- gerar comunicados;
- resumir documentos e responder perguntas sobre regras do condominio.

Assim, o sindico ganha controle, o condominio ganha transparencia e o
inquilino/morador ganha resolucao mais rapida.

## Stack

- Frontend: React, Vite e Tailwind.
- Backend: FastAPI, SQLAlchemy, Pydantic e `uv`.
- Banco local: SQLite.
- Banco futuro: PostgreSQL.
- IA: servico abstrato no MVP, com possibilidade de plugar OpenAI API.

## Estrutura

```txt
frontend/     # React + Vite + Tailwind
backend/      # FastAPI + SQLAlchemy + Pydantic
docs/         # documentacao de produto, tecnica, demo e pitch
```

## Como executar localmente

### Pre-requisitos

- Node.js 24 ou superior.
- npm.
- Python 3.11 ou superior.
- `uv` instalado.

Se precisar instalar o `uv`, consulte a documentacao oficial:

```txt
https://docs.astral.sh/uv/
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

O frontend roda em:

```txt
http://localhost:5173
```

### Backend

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

O backend roda em:

```txt
http://localhost:8000
```

Documentacao interativa da API:

```txt
http://localhost:8000/docs
```

Health check:

```bash
curl http://localhost:8000/health
```

No desenvolvimento, use SQLite:

```env
DATABASE_URL=sqlite:///./kondo.db
CORS_ORIGINS=http://localhost:5173
```

Arquivos de ambiente versionados:

- `.env.example`: referencia geral do monorepo.
- `backend/.env.example`: variaveis da API.
- `frontend/.env.example`: variaveis do app web.

Arquivos `.env` reais nao devem ser commitados.

### Rodar tudo

Abra dois terminais:

```bash
# terminal 1
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

```bash
# terminal 2
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Documentacao

- [Produto](docs/product.md)
- [Casos de Uso](docs/use-cases.md)
- [Arquitetura](docs/architecture.md)
- [Backend](docs/backend.md)
- [Roadmap do Backend](docs/backend-roadmap.md)
- [Checklist de Revisao](docs/review-checklist.md)
- [API](docs/api.md)
- [Modelo de Dados](docs/data-model.md)
- [IA](docs/ai.md)
- [WhatsApp](docs/whatsapp.md)
- [Frontend](docs/frontend.md)
- [Regras de Desenvolvimento](docs/development-rules.md)
- [Roteiro de Demo](docs/demo-script.md)
- [Pitch](docs/pitch.md)
