import { delinquencies, type Delinquency } from "./delinquencies"

export type AgreementStatus = "rascunho" | "ativo" | "encerrado" | "cancelado" | "pendente"

export type Agreement = {
  id: number
  condominium_id: number
  unit_id: number
  unit: string
  delinquency_id: number | null
  amount_due: number
  days_late: number
  risk: "baixo" | "medio" | "alto"
  status: AgreementStatus
  entry_amount: number
  installments: number
  monthly_installment: number
  recommendation: string
  created_at: string
  updated_at: string
}

const baseByUnit: Record<
  number,
  Pick<Agreement, "entry_amount" | "installments" | "monthly_installment" | "recommendation">
> = {
  304: {
    entry_amount: 400,
    installments: 4,
    monthly_installment: 287,
    recommendation: "Entrada mínima de R$ 400 com 4x e fluxo positivo projetado no próximo mês.",
  },
  1202: {
    entry_amount: 320,
    installments: 3,
    monthly_installment: 320,
    recommendation: "Entrada mínima de R$ 320 com 3x para normalizar a carteira.",
  },
  708: {
    entry_amount: 200,
    installments: 6,
    monthly_installment: 470,
    recommendation: "Entrada inicial sugerida e negociação em andamento com histórico de contato recente.",
  },
}

export const agreements: Agreement[] = delinquencies.map((delinquency, index) => ({
  id: 100 + delinquency.id,
  condominium_id: delinquency.condominium_id,
  unit_id: delinquency.unit_id,
  unit: delinquency.unit,
  delinquency_id: delinquency.id,
  amount_due: delinquency.amount_due,
  days_late: delinquency.days_late,
  risk: delinquency.risk,
  status: delinquency.status === "em_negociacao" ? "ativo" : "pendente",
  entry_amount: baseByUnit[delinquency.unit_id]?.entry_amount ?? 300,
  installments: baseByUnit[delinquency.unit_id]?.installments ?? 2,
  monthly_installment: baseByUnit[delinquency.unit_id]?.monthly_installment ?? Math.round(delinquency.amount_due / 2),
  recommendation:
    baseByUnit[delinquency.unit_id]?.recommendation ??
    "Entrada sugerida com base no saldo atual e risco da unidade.",
  created_at: "2026-05-15T10:00:00-03:00",
  updated_at: `2026-06-${10 + index}T08:00:00-03:00`,
}))

export function makeAgreementSuggestion(delinquency: Delinquency) {
  return (
    baseByUnit[delinquency.unit_id] ?? {
      entry_amount: 300,
      installments: 3,
      monthly_installment: Math.round(delinquency.amount_due / 3),
      recommendation: "Entrada sugerida baseada no saldo atual e risco da unidade.",
    }
  )
}

