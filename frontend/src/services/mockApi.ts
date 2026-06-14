import {
  agreements,
  announcements,
  condo,
  dashboardSummary,
  delinquencies,
  documentFaqMock,
  documents,
  finances,
  portalTickets,
  residentProfile,
  residentTimeline,
  ticketStatusLabels,
  ticketStatusOptions,
  tickets,
  type Announcement,
  type Delinquency,
  type DocumentItem,
  type FinanceSummary,
  type FinanceTransaction,
  type PortalTimelineEvent,
  type ResidentProfile,
  type Ticket,
  type TicketStatus,
} from "../data/mock"

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value))
}

type KanbanColumn = {
  id: string
  label: string
  count: number
  tickets: Ticket[]
}

export async function getDashboard() {
  await wait(120)
  return clone(dashboardSummary)
}

export async function listTickets() {
  await wait(120)
  return clone(tickets)
}

export async function listTicketsByStatus(status: TicketStatus) {
  await wait(120)
  return clone(tickets.filter((ticket) => ticket.status === status))
}

export async function getTicketById(ticketId: number) {
  await wait(120)
  return clone(tickets.find((ticket) => ticket.id === ticketId))
}

export async function classifyTicket(ticketId: number) {
  await wait(80)
  const payload = tickets.find((item) => item.id === ticketId)
  if (!payload) return null
  return clone(payload.ai_analysis)
}

export async function getKanbanColumns() {
  await wait(120)
  const columns = ticketStatusOptions.map((item) => ({
    id: item.value,
    label: item.label,
    tickets: tickets.filter((ticket) => ticket.status === item.value),
    count: 0,
  }))

  return columns.map((column) => ({
    ...column,
    count: column.tickets.length,
    tickets: clone(column.tickets),
  })) as KanbanColumn[]
}

export async function moveKanbanTicket(ticketId: number, nextStatus: TicketStatus) {
  await wait(90)
  const current = tickets.find((ticket) => ticket.id === ticketId)
  if (!current) return null
  current.status = nextStatus
  return clone(current)
}

export async function listFinanceSummary() {
  await wait(120)
  return clone(finances.summary)
}

export async function listFinanceTransactions() {
  await wait(120)
  return clone(finances.transactions)
}

export async function listFinance() {
  await wait(120)
  return clone({
    summary: finances.summary as FinanceSummary,
    transactions: finances.transactions as FinanceTransaction[],
    insights: finances.summary.insights,
  })
}

export async function getFinanceInsight() {
  await wait(120)
  return clone({ insights: finances.summary.insights })
}

export async function getFinanceProjectionImpact(payload: { cash_gap_delta: number; agreement_impact: number }) {
  await wait(80)
  return {
    current_cash_gap: finances.summary.cash_gap,
    projected_cash_gap: finances.summary.cash_gap + payload.cash_gap_delta - payload.agreement_impact,
    scenario: `Impacto projetado: ${payload.cash_gap_delta} de arrecadacao e ${payload.agreement_impact} de acordos.`,
  }
}

export async function listDelinquencies() {
  await wait(120)
  return clone(delinquencies as Delinquency[])
}

export async function listAgreements() {
  await wait(120)
  return clone(agreements)
}

export async function simulateAgreement(payload: {
  unit_id: number
  amount_due: number
  entry_amount: number
  installments: number
}) {
  await wait(120)
  const remaining = Math.max(0, payload.amount_due - payload.entry_amount)
  const monthly_installment = payload.installments > 0 ? Number((remaining / payload.installments).toFixed(2)) : 0
  const cashImpact = payload.entry_amount + monthly_installment * 0.15

  return clone({
    unit_id: payload.unit_id,
    entry_amount: payload.entry_amount,
    monthly_installment,
    projected_cash_impact: Number(cashImpact.toFixed(2)),
    recommendation: `Sugerimos entrada de R$ ${payload.entry_amount.toLocaleString("pt-BR")} e ${payload.installments} parcelas.`,
    agreement_id: delinquencies.find((item) => item.unit_id === payload.unit_id)?.id,
    created_at: new Date().toISOString(),
  })
}

export async function listDocuments() {
  await wait(120)
  return clone(documents as DocumentItem[])
}

export async function askDocumentQuestion(payload: { question: string; document_id?: number }) {
  await wait(120)
  const lowered = payload.question.toLowerCase()
  const directHit = documentFaqMock.find((entry) => lowered.includes(entry.question.toLowerCase()))
  const answer = directHit
    ? directHit.answer
    : "Pergunta enviada para revisao juridica. Retorno previsto em ate 2 dias uteis pelo conselho."

  return clone({
    answer,
    source: directHit ? documents[0].title : "Base de conhecimento condominial",
    confidence: directHit ? 0.97 : 0.79,
    answered_at: new Date().toISOString(),
    question: payload.question,
    document_id: payload.document_id ?? documents[0]?.id ?? null,
  })
}

export async function listAnnouncements() {
  await wait(120)
  return clone(announcements as Announcement[])
}

export async function generateAnnouncement(payload: { draft: string; tone?: "formal" | "informal" | "urgente" }) {
  await wait(120)
  const tone = payload.tone ?? "formal"
  return clone({
    title: "Comunicado do condominio",
    body: `${payload.draft}. Este comunicado foi formatado no tom ${tone}.`,
    status: "rascunho",
  })
}

export async function postAnnouncement(payload: {
  title: string
  body: string
  audience: string
  date: string
  status?: "rascunho" | "publicado"
}) {
  await wait(120)
  return clone({
    id: announcements.length + 1,
    title: payload.title,
    body: payload.body,
    audience: payload.audience,
    status: payload.status ?? "publicado",
    created_at: payload.date,
  } satisfies Announcement)
}

export async function listPortalTimeline() {
  await wait(120)
  return clone(residentTimeline as PortalTimelineEvent[])
}

export async function listResidentTickets(unit: string) {
  await wait(120)
  const selected = unit.trim()
  return clone(portalTickets.filter((ticket) => ticket.unit === selected))
}

export async function getResidentPortalHome() {
  await wait(120)
  return clone({
    profile: residentProfile as ResidentProfile,
    condo,
    unit: {
      id: Number(residentProfile.unit),
      number: residentProfile.unit,
      block: residentProfile.block,
    },
    active_tickets: portalTickets,
    recent_announcements_count: 2,
  })
}

export function getKanbanMetadata() {
  return clone({ status_map: ticketStatusLabels })
}
