export const condo = {
  id: 1,
  name: "Condomínio Jardim Aurora",
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
    id: string
    title: string
    description: string
    urgency: "baixo" | "medio" | "alto"
  }>
  critical_status_block: {
    id: string
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
      id: "priority-1",
      title: "Risco de déficit no próximo mês",
      description: "A projeção indica déficit de R$ 2.160 se três acordos não forem fechados nesta semana.",
      urgency: "alto",
    },
    {
      id: "priority-2",
      title: "Vazamento de garagem com risco de impacto",
      description:
        "Chamado com risco elétrico e prioridade alta. O fornecedor já foi acionado e precisa retorno em até 90 minutos.",
      urgency: "alto",
    },
    {
      id: "priority-3",
      title: "Gasto acima da média no trimestre",
      description:
        "Conta de segurança e manutenção saiu 18% acima da média e deve ser revisada no comitê financeiro.",
      urgency: "medio",
    },
  ],
  critical_status_block: {
    id: "critical-1",
    title: "Vazamento próximo ao quadro de garagem",
    description:
      "Perda de água reportada em área com acesso ao circuito do quadro elétrico. É necessário isolamento imediato para evitar risco de choque.",
    risk: "alto",
    owner: "Zelador e fornecedor hidráulico",
    next_action: "Isolar área e concluir inspeção em até 2 horas.",
  },
}

