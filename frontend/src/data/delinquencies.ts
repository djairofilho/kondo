export type DelinquencyStatus = "vencido" | "pendente" | "em_negociacao" | "quitado"

export type Delinquency = {
  id: number
  unit_id: number
  unit: string
  amount_due: number
  days_late: number
  risk: "baixo" | "medio" | "alto"
  status: DelinquencyStatus
}

export const delinquencies: Delinquency[] = [
  { id: 1, unit_id: 304, unit: "304", amount_due: 1548, days_late: 63, risk: "medio", status: "vencido" },
  { id: 2, unit_id: 1202, unit: "1202", amount_due: 980, days_late: 41, risk: "medio", status: "vencido" },
  { id: 3, unit_id: 708, unit: "708", amount_due: 2460, days_late: 74, risk: "alto", status: "vencido" },
]

