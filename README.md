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

## Como rodar

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
uv init
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings
uv run uvicorn app.main:app --reload
```

No desenvolvimento, use SQLite:

```env
DATABASE_URL=sqlite:///./kondo.db
CORS_ORIGINS=http://localhost:5173
```

## Documentacao

- [Produto](docs/product.md)
- [Casos de Uso](docs/use-cases.md)
- [Arquitetura](docs/architecture.md)
- [Backend](docs/backend.md)
- [API](docs/api.md)
- [Modelo de Dados](docs/data-model.md)
- [IA](docs/ai.md)
- [Frontend](docs/frontend.md)
- [Roteiro de Demo](docs/demo-script.md)
- [Pitch](docs/pitch.md)
