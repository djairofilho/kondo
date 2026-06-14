# Kondo Backend

Backend e documentacao tecnica/produto do Kondo.

O frontend web agora vive no repositorio irmao `../kondo-front`. Este
repositorio deve ser usado apenas para API, banco, servicos de dominio,
migrations, testes de backend e documentacao de contratos.

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

## Produto

Kondo e uma plataforma AI-native para a vida em condominio. Ela facilita a
rotina do sindico, aumenta a transparencia para o condominio e da ao
inquilino/morador um canal simples para resolver problemas, acompanhar status e
entender regras.

O objetivo e reduzir administracao manual, aumentar confianca entre as partes e
criar uma base de dados operacional que no futuro possa habilitar produtos
financeiros para condominios.

## Stack do backend

- Backend: FastAPI, SQLAlchemy, Pydantic e `uv`.
- Banco dev: SQLite (sem Docker) ou PostgreSQL (Docker).
- IA: servico abstrato no MVP, com possibilidade de plugar OpenAI API.

## Estrutura

```txt
app/          # FastAPI app, routers, schemas, models e services
alembic/      # migrations
tests/        # testes do backend
storage/      # storage local de desenvolvimento
docs/         # documentacao de produto, tecnica, demo e pitch
pyproject.toml
```

## Como executar localmente

Existem duas formas de rodar o backend: **Docker** (PostgreSQL, zero configuracao) ou **local com SQLite** (mais rapido para iterar).

---

### Opcao 1 — Docker (recomendado)

Pre-requisito: Docker e Docker Compose instalados.

```bash
cd kondo
docker compose up --build
```

Isso sobe dois servicos:

| Servico | URL |
|---------|-----|
| API (FastAPI) | `http://localhost:8000` |
| PostgreSQL | `localhost:5432` |

Na inicializacao, o container executa automaticamente:

1. `alembic upgrade head` — aplica migrations
2. `python -m app.seed` — popula o banco com dados demo
3. `uvicorn` — sobe a API

Nenhum comando adicional e necessario.

Para parar e remover os volumes (limpa o banco):

```bash
docker compose down -v
```

---

### Opcao 2 — Local com SQLite

Pre-requisitos:

- Python 3.11 ou superior.
- `uv` instalado.

Se precisar instalar o `uv`, consulte a documentacao oficial:

```txt
https://docs.astral.sh/uv/
```

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

O `.env.example` ja vem configurado com SQLite por padrao:

```env
DATABASE_URL=sqlite:///./kondo.db
```

Para usar PostgreSQL local (sem Docker), ajuste o `.env`:

```env
DATABASE_URL=postgresql://kondo:kondo@localhost:5432/kondo
```

Em ambos os modos, a API fica disponivel em:

| Endpoint | URL |
|----------|-----|
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| Health | `http://localhost:8000/health` |

Arquivos `.env` reais nao devem ser commitados. Use `.env.example` como base.

---

### Dados demo

O banco e populado automaticamente ao subir com Docker. Para rodar manualmente no modo local:

```bash
uv run python -m app.seed
```

Condominio criado: **Condominio Jardim Aurora**.

Usuarios demo (senha universal: `kondo123`):

| Perfil   | E-mail               | Papel            | Acesso                                          |
|----------|----------------------|------------------|-------------------------------------------------|
| Sindico  | `sindico@kondo.com`  | `manager`        | Completo: financeiro, chamados, comunicados, IA |
| Conselho | `conselho@kondo.com` | `board_member`   | Financeiro, documentos, comunicados, governanca |
| Morador  | `morador@kondo.com`  | `resident`       | Portal da unidade 804, chamados, boletos        |
| Admin    | `admin@kondo.local`  | `platform_admin` | Administracao da plataforma                     |

Para entrar no frontend, acesse `http://localhost:5173/login` e use um dos e-mails acima com a senha `kondo123`.

---

### Migrations

```bash
uv run alembic upgrade head
```

Gerar nova migration depois de alterar modelos:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

---

### Rodar com o frontend (modo local)

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

Em outro terminal, no repositorio de frontend:

```bash
cd ../kondo-front
bun install
bun run dev
```

## Documentacao

- [Produto](docs/product.md)
- [Casos de Uso](docs/use-cases.md)
- [Arquitetura](docs/architecture.md)
- [Separacao de Repositorios](docs/repository-split.md)
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
