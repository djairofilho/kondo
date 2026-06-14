export type DocumentStatus = "publicado" | "rascunho" | "arquivado"

export type DocumentItem = {
  id: number
  title: string
  document_type: string
  summary: string
  status: DocumentStatus
  created_at: string
  updated_at: string
  source: string
  source_path?: string
  evidence_tags: string[]
}

export const documents: DocumentItem[] = [
  {
    id: 1,
    title: "Regimento Interno",
    document_type: "Regimento",
    summary:
      "Regras de convivência, uso de áreas comuns e comunicação obrigatória para reformas em unidades privadas.",
    status: "publicado",
    created_at: "2026-06-12T09:00:00-03:00",
    updated_at: "2026-06-12T09:00:00-03:00",
    source: "Assembleia",
    source_path: "assembleia/2026-06-regimento.pdf",
    evidence_tags: ["documento_oficial", "assinado"],
  },
  {
    id: 2,
    title: "Convenção Condominial",
    document_type: "Convenção",
    summary: "Responsabilidades por danos e regras de uso de áreas de lazer e administrativas.",
    status: "publicado",
    created_at: "2026-05-28T14:20:00-03:00",
    updated_at: "2026-06-02T11:20:00-03:00",
    source: "Assessoria Jurídica",
    source_path: "juridico/convenção-condominio.pdf",
    evidence_tags: ["documento_oficial", "revisado"],
  },
  {
    id: 3,
    title: "Ata de Assembleia",
    document_type: "Ata",
    summary: "Deliberações aprovadas e prazos de cobrança preventiva definidos pelo conselho.",
    status: "publicado",
    created_at: "2026-05-15T18:30:00-03:00",
    updated_at: "2026-05-15T18:30:00-03:00",
    source: "Secretaria",
    source_path: "atas/assembleia-05-2026.pdf",
    evidence_tags: ["transcrição", "documento_oficial"],
  },
  {
    id: 4,
    title: "Contrato de Limpeza",
    document_type: "Contrato",
    summary: "Termo de prestação do serviço mensal de limpeza e atribuições da administração.",
    status: "publicado",
    created_at: "2026-04-02T10:10:00-03:00",
    updated_at: "2026-04-10T10:10:00-03:00",
    source: "Administração",
    source_path: "contratos/limpeza-2026-12.pdf",
    evidence_tags: ["anexo", "financeiro"],
  },
]

export const documentFaqMock = [
  {
    question: "Pode fazer obra com barulho?",
    answer:
      "Sim, de segunda a sexta entre 9h e 13h e com comunicação prévia no grupo do condomínio. Não é permitido aos domingos e feriados.",
  },
  {
    question: "Qual é a regra da churrasqueira?",
    answer:
      "A churrasqueira precisa de reserva no sistema e pagamento da taxa de limpeza antes do uso. Sem taxa, o pedido não é finalizado.",
  },
  {
    question: "Pode mudar de portaria o dia da reserva?",
    answer: "Alterações em reserva devem ser solicitadas com 12 horas de antecedência no canal do proprietário.",
  },
]

