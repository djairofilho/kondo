# API

## Padroes

- Base URL local: `http://localhost:8000`.
- Formato: JSON.
- Datas: ISO 8601.
- Valores financeiros: string decimal ou numero com duas casas, validado no
  backend como decimal.

## Saude

### `GET /health`

Retorna status basico da API.

```json
{
  "status": "ok",
  "service": "kondo-api"
}
```

## Auth e usuario atual

### `POST /auth/register`

Cria usuario e retorna tokens.

```json
{
  "name": "Maria Sindica",
  "email": "sindico@kondo.com",
  "password": "kondo123"
}
```

### `POST /auth/login`

Autentica usuario.

```json
{
  "email": "sindico@kondo.com",
  "password": "kondo123"
}
```

### `POST /auth/logout`

Encerra a sessao no cliente. No MVP, o token continua stateless.

### `POST /auth/refresh`

Renova tokens usando `refresh_token`.

### `GET /me`

Retorna o usuario autenticado.

### `GET /me/memberships`

Lista os acessos do usuario a condominios.

### `GET /me/permissions`

Lista papeis e permissoes derivadas de memberships.

## Admin da plataforma

Endpoints exigem token de usuario `platform_admin`.

```txt
GET  /admin/overview
GET  /admin/condominiums
POST /admin/condominiums
GET  /admin/users
GET  /admin/audit-events
```

## Dashboard

### `GET /dashboard`

Retorna indicadores principais do condominio.

```json
{
  "cash_balance": "18400.00",
  "projected_cash": "14200.00",
  "delinquency_rate": 0.1195,
  "open_tickets": 12,
  "critical_tickets": 2,
  "ai_priorities": [
    "Risco de deficit no proximo mes se 3 acordos nao forem fechados.",
    "Chamado de vazamento na garagem deve ser priorizado."
  ]
}
```

## Chamados

### `GET /tickets`

Lista chamados.

### `POST /tickets`

Cria chamado.

```json
{
  "unit_id": 304,
  "title": "Vazamento na garagem",
  "description": "Vazamento forte na garagem B2 perto do quadro eletrico.",
  "location": "Garagem B2"
}
```

### `GET /tickets/{id}`

Busca chamado por id.

### `PATCH /tickets/{id}`

Atualiza campos basicos do chamado.

### `PATCH /tickets/{id}/status`

Atualiza status do chamado e move os work items vinculados.

### `PATCH /tickets/{id}/assign`

Define responsavel nos itens operacionais vinculados ao chamado.

### `GET /tickets/{id}/comments`

Lista comentarios do chamado.

### `POST /tickets/{id}/comments`

Cria comentario no chamado.

### `POST /tickets/{id}/classify-ai`

Classifica um chamado com IA ou simulacao.

```json
{
  "category": "hidraulica",
  "priority": "alta",
  "risk": "risco eletrico",
  "suggested_owner": "zelador e fornecedor hidraulico",
  "next_action": "Isolar a area e acionar fornecedor imediatamente."
}
```

## Kanban operacional

### `GET /kanban`

Lista itens do Kanban operacional.

### `GET /kanban/columns`

Lista colunas padrao.

### `POST /kanban/items`

Cria item operacional.

### `GET /kanban/items/{id}`

Busca item operacional.

### `PATCH /kanban/items/{id}`

Atualiza item operacional.

### `PATCH /kanban/items/{id}/move`

Move item entre colunas.

```json
{
  "status": "in_progress"
}
```

## Condominios, unidades e pessoas

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

## Dashboards, conselho e portal do morador

```txt
GET /manager/dashboard
GET /board/dashboard
GET /board/overview
GET /board/financial-transparency
GET /board/maintenance-status
GET /board/decisions
GET /board/audit-events

GET  /resident-portal/home
GET  /resident-portal/my-unit
GET  /resident-portal/my-tickets
POST /resident-portal/tickets
GET  /resident-portal/announcements
GET  /resident-portal/rules
POST /resident-portal/rules/ask
```

## Fornecedores, auditoria e IA

```txt
GET   /vendors
POST  /vendors
GET   /vendors/{vendor_id}
PATCH /vendors/{vendor_id}

GET  /quotes
POST /quotes
POST /quotes/compare-ai

GET  /audit/events
POST /audit/events

POST /ai/priorities
POST /ai/ticket-classification
POST /ai/financial-insights
POST /ai/agreement-recommendation
POST /ai/announcement-generation
POST /ai/document-summary/{document_id}
POST /ai/document-question/{document_id}
POST /ai/vendor-quote-comparison
```

## Financeiro

### `GET /finance/summary`

Retorna resumo financeiro.

```json
{
  "expected_revenue": "20640.00",
  "received_revenue": "17640.00",
  "expenses": "19800.00",
  "cash_gap": "-2160.00",
  "insights": [
    "A inadimplencia atual pode pressionar o caixa ainda este mes."
  ]
}
```

### `GET /finance/cashflow`

Retorna fluxo de caixa agregado.

### `GET /finance/monthly-report`

Retorna relatorio mensal resumido.

### `POST /finance/insights-ai`

Gera insights financeiros simulados.

### `GET /revenues`

Lista receitas persistidas.

### `POST /revenues`

Cria receita.

### `GET /revenues/{id}`

Busca receita.

### `PATCH /revenues/{id}`

Atualiza receita.

### `GET /expenses`

Lista despesas persistidas.

### `POST /expenses`

Cria despesa.

### `GET /expenses/{id}`

Busca despesa.

### `PATCH /expenses/{id}`

Atualiza despesa.

### `GET /payments`

Lista pagamentos.

### `POST /payments`

Cria pagamento.

### `GET /payments/{id}`

Busca pagamento.

### `PATCH /payments/{id}`

Atualiza pagamento.

### `POST /payments/{id}/mark-paid`

Marca pagamento como pago.

### `POST /payments/{id}/generate-boleto`

Gera metadados simulados de boleto no MVP.

## Inadimplencia

### `GET /delinquencies`

Lista unidades inadimplentes.

```json
[
  {
    "unit_id": 304,
    "amount_due": "1548.00",
    "days_late": 63,
    "risk": "medio"
  }
]
```

### `GET /delinquencies/{id}`

Busca inadimplencia.

### `PATCH /delinquencies/{id}`

Atualiza inadimplencia.

## Acordos

### `GET /agreements`

Lista acordos.

### `POST /agreements`

Cria acordo.

### `GET /agreements/{id}`

Busca acordo.

### `PATCH /agreements/{id}`

Atualiza acordo.

### `POST /agreements/simulate`

Simula acordo e impacto no caixa.

```json
{
  "unit_id": 304,
  "amount_due": "1548.00",
  "entry_amount": "400.00",
  "installments": 4
}
```

### `POST /agreements/{id}/payments`

Cria pagamento vinculado ao acordo.

### `POST /agreements/{id}/cancel`

Cancela acordo.

Resposta:

```json
{
  "monthly_installment": "287.00",
  "cash_impact": "Mantem o caixa positivo no proximo mes.",
  "recommendation": "Recomenda-se entrada minima de R$ 400 e ate 4 parcelas."
}
```

## Comunicados

```txt
GET   /announcements
POST  /announcements
GET   /announcements/{announcement_id}
PATCH /announcements/{announcement_id}
POST  /announcements/{announcement_id}/publish
```

### `POST /announcements/generate-ai`

Gera comunicado a partir de rascunho.

```json
{
  "draft": "avisar manutencao caixa dagua terca 9h ate 13h pode faltar agua",
  "tone": "formal"
}
```

## Documentos

```txt
GET    /documents
POST   /documents
GET    /documents/{document_id}
PATCH  /documents/{document_id}
DELETE /documents/{document_id}
POST   /documents/upload
```

O upload de PDF vinculado a um documento extrai texto automaticamente e atualiza
`content`, permitindo resumo e pergunta sobre o arquivo.

### `POST /documents/{id}/summarize`

Resume um documento cadastrado usando o texto salvo em `content`, inclusive texto
extraido de PDFs enviados.

### `POST /documents/{id}/ask`

Responde pergunta com base nos trechos mais relevantes do documento.

```json
{
  "question": "Pode fazer obra no sabado?"
}
```

## Anexos

### `POST /attachments`

Cria anexo generico usando `multipart/form-data`.

Campos:

- `file`
- `condominium_id`
- `entity_type`
- `entity_id`
- `visibility`

### `GET /attachments/{id}`

Busca metadados do anexo.

### `GET /attachments/{id}/download`

Baixa o arquivo pelo backend, sem expor a pasta local diretamente.

### `DELETE /attachments/{id}`

Remove metadados e arquivo local.

### Atalhos

```txt
POST /tickets/{ticket_id}/attachments
GET  /tickets/{ticket_id}/attachments
POST /payments/{payment_id}/attachments
GET  /payments/{payment_id}/attachments
POST /kanban/items/{item_id}/attachments
GET  /kanban/items/{item_id}/attachments
```
