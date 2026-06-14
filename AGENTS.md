# AGENTS.md — Kondo Backend

Guia de referência para agentes de IA trabalhando neste repositório. Leia antes de qualquer alteração.

---

## Visão geral

O **Kondo** é uma plataforma AI-native para gestão condominial. Este repositório contém exclusivamente o backend: API REST, banco de dados, serviços de domínio, migrations e documentação técnica/produto.

O frontend vive no repositório irmão `../kondo-front`. Nunca crie código de interface aqui.

---

## Stack

| Camada | Tecnologia |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Validação | Pydantic v2 |
| Gerenciador de ambiente | `uv` |
| Banco (dev) | SQLite |
| Banco (prod) | PostgreSQL |
| Migrations | Alembic |
| IA | `pydantic-ai-slim[anthropic]` (com fallback simulado) |
| Testes | pytest + httpx |

---

## Estrutura do projeto

```
app/
  main.py          # entrypoint FastAPI — registra routers e middleware
  core/
    config.py      # settings via pydantic-settings
    database.py    # engine SQLAlchemy e init_db()
    deps.py        # dependências FastAPI (get_db, get_current_user)
    security.py    # JWT e hash de senha (PBKDF2)
  models/          # modelos SQLAlchemy — um arquivo por domínio
  schemas/         # schemas Pydantic — contratos de request/response
  routers/         # handlers HTTP — sem lógica de negócio
  services/        # lógica de domínio e IA
  seed.py          # cria Condomínio Jardim Aurora com dados demo
alembic/           # migrations
tests/             # testes de backend (pytest)
storage/           # uploads locais de desenvolvimento (não commitar arquivos)
docs/              # documentação técnica e de produto
pyproject.toml
```

---

## Fluxo obrigatório por camada

```
Router  →  Schema (Pydantic)  →  Service  →  Model (SQLAlchemy)  →  DB
```

- **Routers** (`app/routers/`): recebem request, validam via schema, chamam service, retornam response. Nenhuma query SQL aqui.
- **Schemas** (`app/schemas/`): contratos Pydantic para request/response. Nunca expõem modelos SQLAlchemy diretamente.
- **Services** (`app/services/`): toda lógica de domínio e IA. Recebem `db: Session` e schemas, retornam dados.
- **Models** (`app/models/`): declarações SQLAlchemy. Um arquivo por domínio (`identity.py`, `operations.py`, `finance.py`, etc.).
- **Core** (`app/core/`): configuração, banco e dependências compartilhadas. Não colocar lógica de negócio aqui.

---

## Regras de implementação (não negociáveis)

### Financeiro
- Usar `Decimal` ou `Numeric` para valores monetários. **Nunca `float`.**
- Usar `Date` / `DateTime` para vencimentos e timestamps.

### IA
- Toda chamada de IA passa por `services/ai_service.py` ou `services/ai_chat_service.py`.
- O sistema deve rodar **sem chave de IA** usando respostas simuladas como fallback.
- IA não deve tomar decisões sensíveis sozinha (perdoar dívida, aprovar gasto, iniciar cobrança jurídica).

### Banco
- Evitar recursos exclusivos de PostgreSQL no MVP. Os modelos devem ser portáveis.
- `DATABASE_URL` controla o banco. Trocar SQLite por Postgres não deve exigir alteração de modelo.
- Nenhuma regra de negócio deve depender diretamente do SQLite ou do filesystem local.

### Auth
- JWT local com hash PBKDF2. Lógica em `app/core/security.py`.
- Papéis: `platform_admin`, `manager`, `board_member`, `resident`.
- Acesso por `Membership` — pessoas logam como `User` e recebem papel no contexto do condomínio.

### Kanban
- Ao criar um `Ticket`, a API deve criar automaticamente um `WorkItem` no Kanban.
- Status válidos: `received`, `in_review`, `vendor_contacted`, `waiting_approval`, `in_progress`, `resolved`.

### Storage
- Uploads em `storage/uploads/` apenas para desenvolvimento.
- O banco armazena apenas metadados em `Attachment`. Nunca o binário.
- O download é feito via endpoint controlado.

---

## Variáveis de ambiente

```env
DATABASE_URL=sqlite:///./kondo.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
OPENAI_API_KEY=           # opcional — sem chave, usa fallback simulado
JWT_SECRET_KEY=dev-only-change-me
```

Base: `.env.example`. O arquivo `.env` real não deve ser commitado.

---

## Comandos essenciais

```bash
# Instalar dependências
uv sync

# Rodar API em modo desenvolvimento
uv run uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger)

# Popular banco com dados demo (senha: kondo123)
uv run python -m app.seed

# Aplicar migrations
uv run alembic upgrade head

# Gerar nova migration após alterar modelos
uv run alembic revision --autogenerate -m "describe change"

# Rodar testes
uv run pytest
```

---

## Routers existentes

| Arquivo | Domínio |
|---|---|
| `auth.py` | Login, refresh token, registro |
| `admin.py` | Administração de plataforma |
| `condominiums.py` | Condomínios e unidades |
| `tickets.py` | Chamados operacionais |
| `kanban.py` | WorkItems e quadro Kanban |
| `finance.py` | Receitas, despesas, inadimplência |
| `agreements.py` | Acordos de pagamento |
| `announcements.py` | Comunicados para moradores |
| `documents.py` | Regimentos, atas, contratos |
| `attachments.py` | Upload e download de arquivos |
| `vendors.py` | Fornecedores e orçamentos |
| `calendar.py` | Eventos do condomínio |
| `dashboard.py` | Métricas consolidadas |
| `ai.py` | Endpoints de IA |
| `audit.py` | Rastreamento de eventos |
| `experiences.py` | Portal do morador |

---

## Modelos de dados (entidades principais)

`Condominium` → `Unit` → `Membership` (conecta `User` ao condomínio com papel)

Operações: `Ticket` → `WorkItem` (Kanban), `Expense`, `Revenue`, `Delinquency` → `Agreement`

Conteúdo: `Document`, `Announcement`, `Attachment`

Outros: `Vendor`, `Quote`, `AuditEvent`, `CalendarEvent`

Detalhes completos: [`docs/data-model.md`](docs/data-model.md)

---

## Documentação de referência

| Documento | Quando atualizar |
|---|---|
| [`docs/api.md`](docs/api.md) | Endpoints criados, alterados ou removidos |
| [`docs/data-model.md`](docs/data-model.md) | Modelos ou relações alterados |
| [`docs/backend.md`](docs/backend.md) | Arquitetura, auth, banco, storage ou comandos |
| [`docs/architecture.md`](docs/architecture.md) | Decisões estruturais de sistema |
| [`docs/ai.md`](docs/ai.md) | Casos de uso ou comportamento de IA |
| [`docs/development-rules.md`](docs/development-rules.md) | Regras de processo e PR |
| `README.md` | Setup, execução, env ou estrutura |

---

## Checklist antes de abrir PR

- [ ] `docs/api.md` atualizado se endpoints mudaram.
- [ ] `docs/data-model.md` atualizado se modelos mudaram.
- [ ] Migration Alembic criada se modelos SQLAlchemy foram alterados.
- [ ] Testes adicionados ou atualizados para comportamentos novos.
- [ ] `README.md` atualizado se setup ou env mudou.
- [ ] Se a mudança afeta integração front/backend, abrir ou referenciar alteração em `../kondo-front`.

---

## Padrão de commit

```
feat(backend): add ticket classification endpoint
fix(backend): correct decimal rounding in agreement simulation
docs: update api.md with new finance endpoints
chore: update .env.example with AI key placeholder
```

---

## O que NÃO fazer

- **Não criar frontend aqui.** O React fica em `../kondo-front`.
- **Não usar `float` para valores monetários.**
- **Não colocar lógica de negócio em routers.** Vai para `services/`.
- **Não commitar `.env` real**, `kondo.db` nem arquivos de `storage/uploads/`.
- **Não usar recursos exclusivos de SQLite** que impeçam migração para Postgres.
- **Não fazer IA tomar decisões sensíveis** (aprovações financeiras, cobranças jurídicas).
- **Não criar routers sem o service correspondente.**
