export type DelinquencyStatus = "vencido" | "pendente" | "em_negociacao" | "quitado"

export type Delinquency = {
  id: number
  condominium_id: number
  unit_id: number
  unit: string
  amount_due: number
  days_late: number
  risk: "baixo" | "medio" | "alto"
  status: DelinquencyStatus
  created_at: string
  updated_at: string
}

export const delinquencies: Delinquency[] = [
  {
    id: 1,
    condominium_id: 1,
    unit_id: 304,
    unit: "304",
    amount_due: 1548,
    days_late: 63,
    risk: "medio",
    status: "vencido",
    created_at: "2026-05-02T09:00:00-03:00",
    updated_at: "2026-06-14T09:10:00-03:00",
  },
  {
    id: 2,
    condominium_id: 1,
    unit_id: 1202,
    unit: "1202",
    amount_due: 980,
    days_late: 41,
    risk: "medio",
    status: "vencido",
    created_at: "2026-05-12T13:00:00-03:00",
    updated_at: "2026-06-14T09:10:00-03:00",
  },
  {
    id: 3,
    condominium_id: 1,
    unit_id: 708,
    unit: "708",
    amount_due: 2460,
    days_late: 74,
    risk: "alto",
    status: "em_negociacao",
    created_at: "2026-04-20T10:00:00-03:00",
    updated_at: "2026-06-14T09:10:00-03:00",
  },
]

