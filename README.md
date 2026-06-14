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
- Banco local: SQLite.
- Banco futuro: PostgreSQL.
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

### Pre-requisitos

- Python 3.11 ou superior.
- `uv` instalado.

Se precisar instalar o `uv`, consulte a documentacao oficial:

```txt
https://docs.astral.sh/uv/
```

### Backend

```bash
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

- `.env.example`: variaveis da API.

Arquivos `.env` reais nao devem ser commitados.

### Criar dados demo

```bash
uv run python -m app.seed
```

Condominio criado: **Condominio Jardim Aurora**.

Usuarios demo (senha universal: `kondo123`):

| Perfil       | E-mail                  | Papel              | Acesso                                              |
|--------------|-------------------------|--------------------|-----------------------------------------------------|
| Sindico      | `sindico@kondo.com`     | `manager`          | Completo: financeiro, chamados, comunicados, IA     |
| Conselho     | `conselho@kondo.com`    | `board_member`     | Financeiro, documentos, comunicados, governanca     |
| Morador      | `morador@kondo.com`     | `resident`         | Portal da unidade 304-A, chamados, boletos          |
| Admin        | `admin@kondo.local`     | `platform_admin`   | Administracao da plataforma (nao aparece no front)  |

Para entrar no frontend, acesse `http://localhost:5173/login` e use um dos e-mails acima com a senha `kondo123`, ou clique nos atalhos de perfil demo na propria tela de login.

### Migrations

```bash
uv run alembic upgrade head
```

Gerar nova migration depois de alterar modelos:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

### Rodar com o frontend

```bash
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

Em outro terminal, use o repositorio de frontend:

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
