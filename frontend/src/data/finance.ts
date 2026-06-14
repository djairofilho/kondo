export type TransactionStatus = "pago" | "pendente" | "vencido"
export type TransactionType = "receita" | "despesa"

export type FinanceSummary = {
  expected_revenue: number
  received_revenue: number
  expenses: number
  cash_gap: number
  insights: string[]
}

export type FinanceTransaction = {
  id: string
  description: string
  type: TransactionType
  status: TransactionStatus
  amount: number
  issued_at: string
  unit: string | null
  category: string
}

export const finances = {
  summary: {
    expected_revenue: 20640,
    received_revenue: 17640,
    expenses: 19800,
    cash_gap: -2160,
    insights: [
      "A inadimplência atual pode pressionar o caixa até o dia 15. Recomendamos antecipar a cobrança amigável das unidades pendentes.",
      "Conta de água subiu 18% em relação aos últimos 3 meses. Validação com prestador já foi aberta.",
    ],
  } satisfies FinanceSummary,
  transactions: [
    {
      id: "REV-001",
      description: "Condomínio junho/2026",
      type: "receita",
      status: "pago",
      amount: 6200,
      issued_at: "2026-06-01",
      unit: null,
      category: "Condomínio",
    },
    {
      id: "REV-002",
      description: "Taxa extra reforma",
      type: "receita",
      status: "pendente",
      amount: 1020,
      issued_at: "2026-06-05",
      unit: "Apto 401",
      category: "Receita Extra",
    },
    {
      id: "DES-001",
      description: "Serviço de água",
      type: "despesa",
      status: "pago",
      amount: 5400,
      issued_at: "2026-06-06",
      unit: null,
      category: "Infraestrutura",
    },
    {
      id: "DES-002",
      description: "Limpeza de portaria",
      type: "despesa",
      status: "pendente",
      amount: 4200,
      issued_at: "2026-06-07",
      unit: null,
      category: "Serviços",
    },
    {
      id: "DES-003",
      description: "Segurança noturna",
      type: "despesa",
      status: "pago",
      amount: 5000,
      issued_at: "2026-06-03",
      unit: null,
      category: "Segurança",
    },
  ] satisfies FinanceTransaction[],
}

