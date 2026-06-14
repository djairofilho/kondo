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
}

export const finances = {
  summary: {
    expected_revenue: 20640,
    received_revenue: 17640,
    expenses: 19800,
    cash_gap: -2160,
    insights: [
      "A inadimplencia atual pode pressionar o caixa ate o dia 15. Recomendamos antecipar a cobranca amigavel das unidades pendentes.",
      "Conta de agua subiu 18% em relacao a media dos ultimos 3 meses.",
    ],
  } satisfies FinanceSummary,
  transactions: [
    {
      id: "REV-001",
      description: "Condominio junho/2026",
      type: "receita",
      amount: 6200,
      status: "pago",
      issued_at: "2026-06-01",
      unit: null,
    },
    {
      id: "REV-002",
      description: "Taxa extra reforma",
      type: "receita",
      amount: 1020,
      status: "pendente",
      issued_at: "2026-06-05",
      unit: "Apto 401",
    },
    {
      id: "DES-001",
      description: "Servico de agua",
      type: "despesa",
      amount: 5400,
      status: "pago",
      issued_at: "2026-06-06",
      unit: null,
    },
    {
      id: "DES-002",
      description: "Limpeza de portaria",
      type: "despesa",
      amount: 4200,
      status: "pendente",
      issued_at: "2026-06-07",
      unit: null,
    },
    {
      id: "DES-003",
      description: "Seguranca noturna",
      type: "despesa",
      amount: 5000,
      status: "pago",
      issued_at: "2026-06-03",
      unit: null,
    },
  ] satisfies FinanceTransaction[],
}

