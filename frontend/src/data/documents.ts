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
  evidence_tags: string[]
}

export const documents: DocumentItem[] = [
  {
    id: 1,
    title: "Regimento interno",
    document_type: "Regimento",
    summary:
      "Regras de convivencia, uso de areas comuns e comunicacao para obras em unidades privadas.",
    status: "publicado",
    created_at: "2026-06-12T09:00:00-03:00",
    updated_at: "2026-06-12T09:00:00-03:00",
    source: "Assembleia",
    evidence_tags: ["documento_oficial", "assinado"],
  },
  {
    id: 2,
    title: "Convenio de condominio",
    document_type: "Convencao",
    summary: "Regras formais de responsabilidade por danos e uso de areas comuns.",
    status: "publicado",
    created_at: "2026-05-28T14:20:00-03:00",
    updated_at: "2026-06-02T11:20:00-03:00",
    source: "Assessoria juridica",
    evidence_tags: ["documento_oficial", "revisado"],
  },
  {
    id: 3,
    title: "Ata de assembleia",
    document_type: "Ata",
    summary: "Deliberacoes aprovadas e definicoes de prazo para cobranca preventiva.",
    status: "publicado",
    created_at: "2026-05-15T18:30:00-03:00",
    updated_at: "2026-05-15T18:30:00-03:00",
    source: "Secretaria",
    evidence_tags: ["transcricao"],
  },
  {
    id: 4,
    title: "Contrato de limpeza",
    document_type: "Contrato",
    summary: "Termo de prestacao do servico mensal de limpeza e responsabilidades.",
    status: "publicado",
    created_at: "2026-04-02T10:10:00-03:00",
    updated_at: "2026-04-10T10:10:00-03:00",
    source: "Administracao",
    evidence_tags: ["anexo", "financeiro"],
  },
]

export const documentFaqMock = [
  {
    question: "Pode fazer obra com ruido?",
    answer:
      "Pode, de segunda a sexta entre 9h e 13h, com comunicacao previa no grupo do condominio. Aos domingos e feriados nao e permitido.",
  },
  {
    question: "Qual a regra da churrasqueira?",
    answer:
      "A churrasqueira precisa de reserva no sistema e pagamento da taxa de limpeza para fechar a solicitacao.",
  },
]

