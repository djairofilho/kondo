export type TicketStatus = "received" | "in_review" | "vendor_contacted" | "waiting_approval" | "in_progress" | "resolved"

export const ticketStatusLabels: Record<TicketStatus, string> = {
  received: "Recebido",
  in_review: "Em análise",
  vendor_contacted: "Fornecedor acionado",
  waiting_approval: "Aguardando aprovação",
  in_progress: "Em execução",
  resolved: "Resolvido",
}

export const ticketStatusOptions: Array<{ value: TicketStatus; label: string; order: number }> = Object.entries(ticketStatusLabels).map(
  ([value, label], index) => ({ value: value as TicketStatus, label, order: index }),
)

export type TicketPriority = "baixa" | "média" | "alta"

export type TicketRisk = "baixo" | "médio" | "alto" | "risco operacional moderado" | "risco elétrico" | "risco de dano estrutural"

export const ticketRiskTone: Record<string, "high" | "critical" | "medium"> = {
  baixo: "medium",
  médio: "high",
  alto: "critical",
  "risco operacional moderado": "high",
  "risco elétrico": "critical",
  "risco de dano estrutural": "critical",
}

export type Ticket = {
  id: number
  condominium_id: number
  unit_id: number
  unit: string
  title: string
  description: string
  location: string
  category: string
  priority: TicketPriority
  risk: string
  status: TicketStatus
  owner: string
  next_action: string
  assignee: string | null
  confidence: number
  source: string
  created_at: string
  ai_analysis: {
    category: string
    priority: Exclude<TicketPriority, "média"> | "média"
    risk: TicketRisk
    suggested_owner: string
    next_action: string
  }
}

export const tickets: Ticket[] = [
  {
    id: 1042,
    condominium_id: 1,
    unit_id: 304,
    unit: "304",
    title: "Vazamento forte na garagem B2",
    description:
      "Foi reportada perda de água próxima ao quadro da entrada da garagem B2 com risco para a rede elétrica.",
    location: "Garagem B2",
    category: "Hidráulica",
    priority: "alta",
    risk: "alto",
    status: "vendor_contacted",
    owner: "Zelador e fornecedor hidráulico",
    next_action: "Isolar a área e acionar fornecedor imediatamente.",
    assignee: "Carlos Silva (Zelador)",
    confidence: 98,
    source: "Morador 304",
    created_at: "2026-06-14T09:14:00-03:00",
    ai_analysis: {
      category: "Hidráulica",
      priority: "alta",
      risk: "risco elétrico",
      suggested_owner: "Zelador e fornecedor hidráulico",
      next_action: "Isolar a área e acionar fornecedor imediatamente.",
    },
  },
  {
    id: 1041,
    condominium_id: 1,
    unit_id: 402,
    unit: "402",
    title: "Barulho excessivo após 22h",
    description: "Relato recorrente de ruído acima do permitido à noite.",
    location: "Apto 402 - Bloco A",
    category: "Convivência",
    priority: "média",
    risk: "médio",
    status: "in_review",
    owner: "Equipe de portaria",
    next_action: "Validar reincidência e orientar moradores.",
    assignee: "Equipe de portaria",
    confidence: 84,
    source: "Morador 402",
    created_at: "2026-06-14T08:15:00-03:00",
    ai_analysis: {
      category: "Convivência",
      priority: "média",
      risk: "risco operacional moderado",
      suggested_owner: "Condomínio - Plantão",
      next_action: "Validar reincidência e orientar moradores.",
    },
  },
  {
    id: 1040,
    condominium_id: 1,
    unit_id: 501,
    unit: "C-05",
    title: "Lâmpada queimada no hall",
    description: "Iluminação intermitente no hall do 5º andar.",
    location: "Hall - 5º andar Bloco C",
    category: "Elétrica",
    priority: "baixa",
    risk: "baixo",
    status: "received",
    owner: "Encarregado",
    next_action: "Programar troca e revisar soquete.",
    assignee: "Equipe de manutenção",
    confidence: 82,
    source: "Portaria",
    created_at: "2026-06-13T14:22:00-03:00",
    ai_analysis: {
      category: "Elétrica",
      priority: "baixa",
      risk: "baixo",
      suggested_owner: "Equipe de manutenção",
      next_action: "Programar troca e revisar soquete.",
    },
  },
  {
    id: 1039,
    condominium_id: 1,
    unit_id: 1105,
    unit: "1105",
    title: "Reserva de churrasqueira solicitada",
    description: "Pedido de reserva para domingo 15/06, com autorização parcial.",
    location: "Apto 1105 - Bloco B",
    category: "Reservas",
    priority: "baixa",
    risk: "baixo",
    status: "resolved",
    owner: "Administração",
    next_action: "Confirmar pagamento da taxa de limpeza.",
    assignee: "Atendimento",
    confidence: 76,
    source: "Residente",
    created_at: "2026-06-12T19:10:00-03:00",
    ai_analysis: {
      category: "Serviço",
      priority: "baixa",
      risk: "baixo",
      suggested_owner: "Atendimento",
      next_action: "Confirmar pagamento da taxa de limpeza.",
    },
  },
]
