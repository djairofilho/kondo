# Roadmap do Backend

## Visao

O backend do Kondo deve evoluir em cortes pequenos, sempre via branch, PR e
merge. SQLite e storage local sao estrategias de desenvolvimento rapido, nao
decisoes permanentes. A troca para PostgreSQL e storage remoto deve acontecer
por configuracao e implementacoes internas, sem redesenhar endpoints.

## Cortes de implementacao

### 1. Fundacao persistida

Status: implementado.

- SQLAlchemy com `DATABASE_URL`.
- SQLite local como padrao de desenvolvimento.
- Modelos principais do dominio.
- Seed demo do Condominio Jardim Aurora.
- Testes de criacao de tabelas e smoke da API.

### 2. Auth e memberships

Status: implementado.

- JWT local.
- Hash de senha com PBKDF2.
- `User` como pessoa.
- `Membership` como acesso da pessoa a um condominio.
- Papeis:
  - `platform_admin`
  - `manager`
  - `board_member`
  - `resident`

### 3. Operacao, chamados e Kanban

Status: implementado.

- Chamados persistidos.
- Criacao automatica de `WorkItem` ao abrir chamado.
- Kanban operacional.
- Movimento de cards entre colunas.
- Classificacao de IA simulada.

### 4. Financeiro, pagamentos e acordos

Status: implementado parcialmente.

- Persistir receitas, despesas, inadimplencia, pagamentos e acordos.
- Calcular resumo financeiro a partir do banco.
- Criar endpoints CRUD basicos para receitas, despesas e pagamentos.
- Expandir acordos para listagem, criacao, pagamento e cancelamento.
- Manter simulacao de acordo como endpoint de apoio.

Ainda falta:

- `GET /finance/cashflow`
- `GET /finance/monthly-report`
- `POST /finance/insights-ai`
- `GET /revenues/{revenue_id}`
- `GET /expenses/{expense_id}`
- `GET /payments/{payment_id}`
- `GET /delinquencies/{delinquency_id}`
- `PATCH /delinquencies/{delinquency_id}`

### 5. Anexos e storage local

Status: implementado.

- Criar `storage_service.py`.
- Implementar `LocalStorageService`.
- Salvar arquivos em `backend/storage/uploads/`.
- Ignorar arquivos reais no Git.
- Persistir apenas metadados em `Attachment`.
- Preparar troca futura para S3, R2 ou Supabase Storage.

## Endpoints planejados

### Health e Auth

```txt
GET  /health
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET  /me
GET  /me/memberships
GET  /me/permissions
```

### Admin Plataforma

```txt
GET  /admin/overview
GET  /admin/condominiums
POST /admin/condominiums
GET  /admin/users
GET  /admin/audit-events
```

### Condominios, unidades e pessoas

Status: implementado.

```txt
GET   /condominiums
POST  /condominiums
GET   /condominiums/{condominium_id}
PATCH /condominiums/{condominium_id}
GET   /condominiums/{condominium_id}/overview

GET   /condominiums/{condominium_id}/units
POST  /condominiums/{condominium_id}/units
GET   /units/{unit_id}
PATCH /units/{unit_id}
GET   /units/{unit_id}/history

GET    /condominiums/{condominium_id}/memberships
POST   /condominiums/{condominium_id}/memberships
PATCH  /memberships/{membership_id}
DELETE /memberships/{membership_id}

GET   /units/{unit_id}/residents
POST  /units/{unit_id}/residents
PATCH /residents/{resident_id}
```

### Dashboards por perfil

Status: implementado.

```txt
GET /dashboard
GET /manager/dashboard
GET /board/dashboard
GET /resident-portal/home
```

### Chamados e Kanban

```txt
GET   /tickets
POST  /tickets
GET   /tickets/{ticket_id}
PATCH /tickets/{ticket_id}
PATCH /tickets/{ticket_id}/status
PATCH /tickets/{ticket_id}/assign
POST  /tickets/{ticket_id}/comments
GET   /tickets/{ticket_id}/comments
POST  /tickets/{ticket_id}/classify-ai

GET   /kanban
GET   /kanban/columns
POST  /kanban/items
GET   /kanban/items/{item_id}
PATCH /kanban/items/{item_id}
PATCH /kanban/items/{item_id}/move
```

### Financeiro, pagamentos e acordos

```txt
GET  /finance/summary
GET  /finance/cashflow
GET  /finance/monthly-report
POST /finance/insights-ai

GET   /revenues
POST  /revenues
GET   /revenues/{revenue_id}
PATCH /revenues/{revenue_id}

GET   /expenses
POST  /expenses
GET   /expenses/{expense_id}
PATCH /expenses/{expense_id}

GET   /payments
POST  /payments
GET   /payments/{payment_id}
PATCH /payments/{payment_id}
POST  /payments/{payment_id}/mark-paid
POST  /payments/{payment_id}/generate-boleto

GET   /delinquencies
GET   /delinquencies/{delinquency_id}
PATCH /delinquencies/{delinquency_id}

GET   /agreements
POST  /agreements
GET   /agreements/{agreement_id}
PATCH /agreements/{agreement_id}
POST  /agreements/simulate
POST  /agreements/{agreement_id}/payments
POST  /agreements/{agreement_id}/cancel
```

### Documentos, comunicados e anexos

```txt
GET    /documents
POST   /documents
POST   /documents/upload
GET    /documents/{document_id}
PATCH  /documents/{document_id}
DELETE /documents/{document_id}
POST   /documents/{document_id}/summarize
POST   /documents/{document_id}/ask

GET   /announcements
POST  /announcements
GET   /announcements/{announcement_id}
PATCH /announcements/{announcement_id}
POST  /announcements/generate-ai
POST  /announcements/{announcement_id}/publish

POST   /attachments
GET    /attachments/{attachment_id}
GET    /attachments/{attachment_id}/download
DELETE /attachments/{attachment_id}

POST /tickets/{ticket_id}/attachments
GET  /tickets/{ticket_id}/attachments
POST /payments/{payment_id}/attachments
GET  /payments/{payment_id}/attachments
POST /kanban/items/{item_id}/attachments
GET  /kanban/items/{item_id}/attachments
```

### Conselho, morador, fornecedores e IA

Status: conselho e morador implementados parcialmente; fornecedores e IA
dedicada ainda planejados.

```txt
GET /board/overview
GET /board/financial-transparency
GET /board/maintenance-status
GET /board/decisions
GET /board/audit-events

GET  /resident-portal/my-unit
GET  /resident-portal/my-tickets
POST /resident-portal/tickets
GET  /resident-portal/announcements
GET  /resident-portal/rules
POST /resident-portal/rules/ask

GET   /vendors
POST  /vendors
GET   /vendors/{vendor_id}
PATCH /vendors/{vendor_id}

GET  /quotes
POST /quotes
POST /quotes/compare-ai

POST /ai/priorities
POST /ai/ticket-classification
POST /ai/financial-insights
POST /ai/agreement-recommendation
POST /ai/announcement-generation
POST /ai/document-summary
POST /ai/document-question
POST /ai/vendor-quote-comparison

GET /audit/events
```

## Testes

Para o momento atual, `pytest` e suficiente como base de testes automatizados.
Todo PR de backend deve rodar:

```bash
cd backend
uv run python -m compileall app
uv run pytest
```

Os testes devem cobrir:

- smoke dos endpoints principais;
- criacao de tabelas;
- auth basico;
- permissoes por papel quando aplicavel;
- fluxos de dominio criados no PR.

No futuro, adicionar testes de migracao, testes com Postgres real em CI e testes
de storage remoto quando essas camadas existirem.

