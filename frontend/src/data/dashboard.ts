export const condo = {
  id: 1,
  name: "Condominio Jardim Aurora",
  units: 40,
}

export type DashboardSummary = {
  condo_id: number
  condo_name: string
  units: number
  cash_balance: number
  projected_cash: number
  delinquency_rate: number
  open_tickets: number
  critical_tickets: number
  received_revenue: number
  expected_revenue: number
  expenses: number
  paid_percentage: number
  ai_priorities: Array<{
    title: string
    description: string
    urgency: "baixo" | "medio" | "alto"
  }>
  critical_status_block: {
    title: string
    description: string
    risk: "baixo" | "medio" | "alto"
    owner: string
    next_action: string
  }
}

export const dashboardSummary: DashboardSummary = {
  condo_id: condo.id,
  condo_name: condo.name,
  units: condo.units,
  cash_balance: 18400,
  projected_cash: 14200,
  delinquency_rate: 0.1195,
  open_tickets: 12,
  critical_tickets: 2,
  received_revenue: 17640,
  expected_revenue: 20640,
  expenses: 19800,
  paid_percentage: 0.856,
  ai_priorities: [
    {
      title: "Risco de deficit no proximo mes",
      description: "Projecao indica deficit de R$ 2.160 se tres acordos nao forem fechados nesta semana.",
      urgency: "alto",
    },
    {
      title: "Vazamento de garagem com risco de impacto",
      description:
        "Ticket com risco eletronico e prioridade alta. Fornecedor ja foi acionado e precisa retorno em ate 90 minutos.",
      urgency: "alto",
    },
    {
      title: "Gasto acima da media no trimestre",
      description:
        "Conta de seguranca e manutencao saiu 18% acima da media e deve ser revisado no comite financeiro.",
      urgency: "medio",
    },
  ],
  critical_status_block: {
    title: "Vazamento proximo ao quadro de garagem",
    description:
      "Perda de agua reportada em area com acesso a circuito do quadro. Requeria isolamento para evitar risco de choque.",
    risk: "alto",
    owner: "Zelador e fornecedor hidraulico",
    next_action: "Isolar area e concluir inspeccao em campo em 2 horas.",
  },
}

