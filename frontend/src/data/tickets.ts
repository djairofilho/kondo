export type TicketStatus = "received" | "in_review" | "vendor_contacted" | "waiting_approval" | "in_progress" | "resolved"

export const ticketStatusLabels: Record<TicketStatus, string> = {
  received: "Recebido",
  in_review: "Em analise",
  vendor_contacted: "Fornecedor acionado",
  waiting_approval: "Aguardando aprovacao",
  in_progress: "Em execucao",
  resolved: "Resolvido",
}

export const ticketStatusOptions: Array<{ value: TicketStatus; label: string }> = Object.entries(ticketStatusLabels).map(
  ([value, label]) => ({ value: value as TicketStatus, label }),
)

export type TicketPriority = "baixa" | "media" | "alta"

export type TicketRisk = "baixo" | "medio" | "alto" | "risco operacional moderado" | "risco eletronico" | "risco de dano estrutural"

export const ticketRiskTone: Record<string, "resolved" | "critical" | "high" | "medium"> = {
  baixo: "resolved",
  medio: "high",
  alto: "critical",
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
  risk: "baixo" | "medio" | "alto" | string
  status: TicketStatus
  owner: string
  next_action: string
  assignee: string | null
  confidence: number
  source: string
  created_at: string
  ai_analysis: {
    category: string
    priority: TicketPriority
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
    description: "Foi reportada perda de agua proxima ao quadro da entrada da garagem B2 com risco para a rede eletrica.",
    location: "Garagem B2",
    category: "Hidraulica",
    priority: "alta",
    risk: "alto",
    status: "vendor_contacted",
    owner: "Zelador e fornecedor hidraulico",
    next_action: "Isolar area e acionar fornecedor imediatamente.",
    assignee: "Carlos Silva (Zelador)",
    confidence: 98,
    source: "Morador 304",
    created_at: "2026-06-14T09:14:00-03:00",
    ai_analysis: {
      category: "hidraulica",
      priority: "alta",
      risk: "risco eletronico",
      suggested_owner: "Zelador e fornecedor hidraulico",
      next_action: "Isolar area e acionar fornecedor imediatamente.",
    },
  },
  {
    id: 1041,
    condominium_id: 1,
    unit_id: 402,
    unit: "402",
    title: "Barulho excessivo apos 22h",
    description: "Relato recorrente de ruido acima do permitido na noite.",
    location: "Apt 402 - Bloco A",
    category: "Convivencia",
    priority: "media",
    risk: "medio",
    status: "in_review",
    owner: "Equipe de portaria",
    next_action: "Validar reincidencia e orientar moradores.",
    assignee: "Equipe de portaria",
    confidence: 84,
    source: "Morador 402",
    created_at: "2026-06-14T08:15:00-03:00",
    ai_analysis: {
      category: "convivencia",
      priority: "media",
      risk: "risco operacional moderado",
      suggested_owner: "Condomino de plantao",
      next_action: "Validar reincidencia e orientar moradores.",
    },
  },
  {
    id: 1040,
    condominium_id: 1,
    unit_id: 501,
    unit: "C-05",
    title: "Lampada queimada no hall",
    description: "Iluminacao intermitente no hall do 5o andar.",
    location: "Hall - 5o andar Bloco C",
    category: "Eletrica",
    priority: "baixa",
    risk: "baixo",
    status: "received",
    owner: "Encarregado",
    next_action: "Programar troca e revisar soquete.",
    assignee: "Equipe de manutencao",
    confidence: 82,
    source: "Portaria",
    created_at: "2026-06-13T14:22:00-03:00",
    ai_analysis: {
      category: "eletrica",
      priority: "baixa",
      risk: "baixo",
      suggested_owner: "Equipe de manutencao",
      next_action: "Programar troca e revisar soquete.",
    },
  },
  {
    id: 1039,
    condominium_id: 1,
    unit_id: 1105,
    unit: "1105",
    title: "Reserva de churrasqueira solicitada",
    description: "Pedido de reserva para domingo 15/06, com autorizacao parcial.",
    location: "Apto 1105 - Bloco B",
    category: "Reservas",
    priority: "baixa",
    risk: "baixo",
    status: "resolved",
    owner: "Administracao",
    next_action: "Confirmar pagamento da taxa de limpeza.",
    assignee: "Atendimento",
    confidence: 76,
    source: "Residente",
    created_at: "2026-06-12T19:10:00-03:00",
    ai_analysis: {
      category: "servico",
      priority: "baixa",
      risk: "baixo",
      suggested_owner: "Atendimento",
      next_action: "Confirmar pagamento da taxa de limpeza.",
    },
  },
]

