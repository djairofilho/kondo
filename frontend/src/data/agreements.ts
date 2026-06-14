import { delinquencies, type Delinquency } from "./delinquencies"

export type AgreementStatus = "rascunho" | "ativo" | "encerrado" | "cancelado" | "pendente"

export type Agreement = {
  id: number
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
}

const baseByUnit: Record<number, Pick<Agreement, "entry_amount" | "installments" | "monthly_installment" | "recommendation">> = {
  304: { entry_amount: 400, installments: 4, monthly_installment: 287, recommendation: "Entrada minima de R$ 400 com 4x e fluxo positivo projetado no proximo mes." },
  1202: { entry_amount: 320, installments: 3, monthly_installment: 320, recommendation: "Entrada minima de R$ 320 com 3x para normalizar a carteira." },
  708: { entry_amount: 0, installments: 6, monthly_installment: 470, recommendation: "Aguardar retorno do morador para validar entrada parcial." },
}

export const agreements: Agreement[] = delinquencies.map((delinquency) => ({
  id: delinquency.id + 100,
  unit_id: delinquency.unit_id,
  unit: delinquency.unit,
  delinquency_id: delinquency.id,
  amount_due: delinquency.amount_due,
  days_late: delinquency.days_late,
  risk: delinquency.risk,
  status: delinquency.status === "vencido" ? "pendente" : "ativo",
  entry_amount: baseByUnit[delinquency.unit_id]?.entry_amount ?? 200,
  installments: baseByUnit[delinquency.unit_id]?.installments ?? 2,
  monthly_installment: baseByUnit[delinquency.unit_id]?.monthly_installment ?? Math.round(delinquency.amount_due / 2),
  recommendation: baseByUnit[delinquency.unit_id]?.recommendation ?? "Acordo em ajuste conforme aceite do condominio.",
}))

export function makeAgreementSuggestion(delinquency: Delinquency) {
  return baseByUnit[delinquency.unit_id] ?? {
    entry_amount: 300,
    installments: 3,
    monthly_installment: Math.round(delinquency.amount_due / 3),
    recommendation: "Entrada sugerida baseada no saldo atual e risco da unidade.",
  }
}
