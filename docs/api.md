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

## Acordos

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

Resposta:

```json
{
  "monthly_installment": "287.00",
  "cash_impact": "Mantem o caixa positivo no proximo mes.",
  "recommendation": "Recomenda-se entrada minima de R$ 400 e ate 4 parcelas."
}
```

## Comunicados

### `POST /announcements/generate-ai`

Gera comunicado a partir de rascunho.

```json
{
  "draft": "avisar manutencao caixa dagua terca 9h ate 13h pode faltar agua",
  "tone": "formal"
}
```

## Documentos

### `POST /documents/{id}/summarize`

Resume um documento cadastrado.

### `POST /documents/{id}/ask`

Responde pergunta com base no documento.

```json
{
  "question": "Pode fazer obra no sabado?"
}
```

