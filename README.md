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
- RAG de documentos: extracao local de PDF com `pypdf` e busca lexical sem custo de API.

## Estrutura

```txt
app/          # FastAPI app, routers, schemas, models e services
alembic/      # migrations
tests/        # testes do backend
storage/      # storage local de desenvolvimento
docs/         # documentacao de produto, tecnica, demo e pitch
pyproject.toml
```

## Decisoes tecnicas

### Separacao de repositorios

- O backend fica neste repositorio (`kondo`).
- O frontend fica no repositorio irmao `../kondo-front`.
- Contratos e regras de dominio devem ficar no backend; telas, estado de UI e chamadas via TanStack Query ficam no frontend.
- Mudancas que alteram contrato de API devem ser refletidas nos dois repositorios.

### Banco e portabilidade

- O MVP deve rodar em SQLite para desenvolvimento rapido e PostgreSQL via Docker para ambiente mais proximo de producao.
- Modelos SQLAlchemy devem evitar recursos exclusivos de um banco quando nao forem essenciais.
- Valores financeiros usam `Decimal` / `Numeric`, nunca `float`, para evitar erro de arredondamento em acordos, receitas e despesas.

### Storage local

- Uploads ficam em `storage/uploads/` apenas para desenvolvimento.
- O banco guarda metadados em `Attachment`; o binario fica no filesystem.
- Downloads passam por endpoint autenticado para respeitar permissoes de documento, chamado ou pagamento.

### RAG de documentos

- A decisao foi usar RAG lexical local no MVP, por ser o caminho mais barato e confiavel para demo.
- Ao subir PDF em `/documents/upload`, o arquivo e salvo como `Attachment` e o texto e extraido com `pypdf`.
- O texto extraido alimenta `Document.content`, que passa a ser a base pesquisavel.
- Perguntas em `/documents/{id}/ask` dividem o conteudo em chunks, normalizam texto, removem stopwords simples e ranqueiam trechos por termos da pergunta.
- Nao ha embeddings, banco vetorial ou chamada de LLM nesse fluxo; o custo por consulta e zero em API.
- Se nenhum trecho relevante for encontrado, a API informa que nao ha base suficiente no documento em vez de inventar resposta.
- Essa abordagem e adequada para regras de condominio, atas e contratos simples. O caminho futuro e trocar o retrieval lexical por embeddings e usar LLM apenas para sintetizar respostas com citacoes.

### IA e fallback

- Chamadas de IA ficam concentradas em `app/services/ai_service.py` e `app/services/ai_chat_service.py`.
- O sistema deve continuar funcional sem chave de IA, usando respostas simuladas ou logica local.
- A IA nao deve executar decisoes sensiveis sozinha, como aprovar gasto, perdoar divida ou iniciar cobranca juridica.

### Simulacao de acordos de inadimplencia

- A simulacao de acordo recebe `amount_due`, `entry_amount`, `installments` e `fine_amount`.
- A multa entra no total renegociado, mas nao exigiu nova coluna no modelo de `Agreement`; o contrato persistido continua guardando entrada, numero de parcelas e parcela mensal.
- A resposta retorna `total_due`, `financed_amount`, `monthly_installment`, impacto no caixa e recomendacao.
- Parcelamento e limitado a 24 vezes pelo schema.
- Multa alta gera recomendacao de cautela porque pode reduzir adesao do morador.

### Autorizacao por perfil

- `manager` pode escrever dados operacionais e financeiros.
- `board_member` pode consultar informacoes de governanca/financeiro, mas nao registrar despesas nem alterar status sensiveis.
- `resident` tem acesso restrito ao portal e a documentos/comunicados permitidos.
- Acesso real passa por `Membership`, conectando usuario, condominio, unidade e papel.

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
