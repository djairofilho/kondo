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
  residentUnit,
  ticketStatusLabels,
  ticketStatusOptions,
  tickets,
  type Agreement,
  type Announcement,
  type Delinquency,
  type DocumentItem,
  type FinanceSummary,
  type FinanceTransaction,
  type PortalTimelineEvent,
  type ResidentProfile,
  type Ticket,
  type TicketStatus,
  type TicketPriority,
} from "../data/mock"

import { makeAgreementSuggestion } from "../data/agreements"
import type { PortalTicket } from "../data/portal"

type ApiError = {
  status: number
  message: string
}

const apiError = (message: string): never => {
  const error = new Error(message) as Error & ApiError
  error.status = 404
  throw error
}

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value))
}

const mockState = {
  tickets: clone(tickets) as Ticket[],
  delinquencies: clone(delinquencies) as Delinquency[],
  agreements: clone(agreements) as Agreement[],
  announcements: clone(announcements) as Announcement[],
  financeSummary: clone(finances.summary) as FinanceSummary,
  financeTransactions: clone(finances.transactions) as FinanceTransaction[],
}

type KanbanColumn = {
  id: string
  label: string
  count: number
  tickets: Ticket[]
}

type AiQuestionPayload = { question: string; document_id?: number }

type AgreementSimulationPayload = {
  unit_id: number
  amount_due: number
  entry_amount: number
  installments: number
}

type AnnouncementTone = "formal" | "informal" | "urgente"

function money(value: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", minimumFractionDigits: 2 }).format(value)
}

export async function getDashboard() {
  await wait(80)
  return clone({
    ...dashboardSummary,
    condo_id: condo.id,
    condo_name: condo.name,
  })
}

export async function listTickets() {
  await wait(120)
  return clone(mockState.tickets)
}

export async function getTicketById(ticketId: number) {
  await wait(90)
  const payload = mockState.tickets.find((item) => item.id === ticketId)
  return payload ? clone(payload) : null
}

export async function listTicketsByStatus(status: TicketStatus) {
  await wait(90)
  return clone(mockState.tickets.filter((ticket) => ticket.status === status))
}

export async function classifyTicket(ticketId: number) {
  await wait(110)
  const ticket = mockState.tickets.find((item) => item.id === ticketId)
  if (!ticket) return null
  ticket.confidence = Math.min(99, ticket.confidence + 1)
  return clone(ticket.ai_analysis)
}

export async function listKanbanColumns() {
  await wait(90)
  return ticketStatusOptions
    .slice()
    .sort((a, b) => a.order - b.order)
    .map((status) => {
      const grouped = mockState.tickets.filter((ticket) => ticket.status === status.value)
      return {
        id: status.value,
        label: status.label,
        count: grouped.length,
        tickets: clone(grouped),
      } as KanbanColumn
    })
}

export async function moveKanbanTicket(ticketId: number, nextStatus: TicketStatus) {
  await wait(90)
  const item = mockState.tickets.find((ticket) => ticket.id === ticketId)
  if (!item) return apiError(`Ticket ${ticketId} nao encontrado.`)

  item.status = nextStatus
  item.next_action = "Item avancado para a proxima etapa do fluxo."
  return clone(item)
}

export async function listFinanceSummary() {
  await wait(80)
  return clone(mockState.financeSummary)
}

export async function listFinanceTransactions() {
  await wait(80)
  return clone(mockState.financeTransactions)
}

export async function getFinanceInsightsAI() {
  await wait(120)
  return clone({ insights: mockState.financeSummary.insights })
}

export async function listFinance() {
  await wait(80)
  return {
    summary: clone(mockState.financeSummary),
    transactions: clone(mockState.financeTransactions),
    insights: clone(mockState.financeSummary.insights),
  }
}

export async function getFinanceProjectionImpact(payload: { cash_gap_delta: number; agreement_impact: number }) {
  await wait(60)
  const projectedCashGap = mockState.financeSummary.cash_gap + payload.cash_gap_delta - payload.agreement_impact
  return {
    current_cash_gap: mockState.financeSummary.cash_gap,
    projected_cash_gap: projectedCashGap,
    scenario: `Impacto projetado: ${money(payload.cash_gap_delta)} de arrecadacao e ${money(payload.agreement_impact)} de acordos.`,
  }
}

export async function listDelinquencies() {
  await wait(70)
  return clone(mockState.delinquencies)
}

export async function listAgreements() {
  await wait(80)
  return clone(mockState.agreements)
}

export async function simulateAgreement(payload: AgreementSimulationPayload) {
  await wait(120)
  const remaining = Math.max(0, payload.amount_due - payload.entry_amount)
  const monthly_installment = payload.installments > 0 ? Number((remaining / payload.installments).toFixed(2)) : 0
  const cashImpact = payload.entry_amount + monthly_installment * 0.2

  const delinquency = mockState.delinquencies.find((entry) => entry.unit_id === payload.unit_id)
  const agreement = mockState.agreements.find((entry) => entry.unit_id === payload.unit_id)
  const suggestion = delinquency ? makeAgreementSuggestion(delinquency) : null

  const simulation = {
    unit_id: payload.unit_id,
    entry_amount: payload.entry_amount,
    installments: payload.installments,
    monthly_installment,
    projected_cash_impact: Number(cashImpact.toFixed(2)),
    recommendation:
      agreement?.recommendation ??
      (suggestion
        ? suggestion.recommendation
        : `Sugerimos entrada de ${money(payload.entry_amount)} e ${payload.installments} parcelas de ${money(monthly_installment)}.`),
    agreement_id: agreement?.id ?? null,
    source: suggestion?.recommendation ?? "Cenário de simulação gerado com base no saldo atual.",
    created_at: new Date().toISOString(),
  }

  if (agreement) {
    agreement.entry_amount = payload.entry_amount
    agreement.installments = payload.installments
    agreement.monthly_installment = monthly_installment
    agreement.updated_at = new Date().toISOString()
  }

  return clone(simulation)
}

export async function listDocuments() {
  await wait(90)
  return clone(documents as DocumentItem[])
}

export async function askDocumentQuestion(payload: AiQuestionPayload) {
  await wait(120)
  const lowered = payload.question.trim().toLowerCase()
  const directHit = documentFaqMock.find((entry) => lowered.includes(entry.question.toLowerCase()))
  const answer = directHit
    ? directHit.answer
    : "Pergunta encaminhada para a equipe juridica. Retorno previsto em ate 2 dias uteis."

  return {
    document_id: payload.document_id ?? documents[0]?.id ?? 1,
    question: payload.question,
    answer,
    source: directHit ? "Base normativa do condominio" : "Base de conhecimento + triagem juridica",
    confidence: directHit ? 0.97 : 0.76,
    answered_at: new Date().toISOString(),
  }
}

export async function listAnnouncements() {
  await wait(80)
  return clone(mockState.announcements)
}

export async function generateAnnouncement(payload: { draft: string; tone?: AnnouncementTone }) {
  await wait(90)
  const tone = payload.tone ?? "formal"
  return clone({
    title: "Comunicado do condominio",
    body: `[${tone.toUpperCase()}] ${payload.draft} Este comunicado foi gerado com linguagem adequada para o comunicado oficial.`,
    status: "rascunho",
    tone,
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
  const newItem: Announcement = {
    id: mockState.announcements.length + 1,
    condominium_id: condo.id,
    title: payload.title,
    body: payload.body,
    audience: payload.audience,
    status: payload.status ?? "publicado",
    created_at: payload.date,
    scheduled_at: null,
  }
  mockState.announcements = [newItem, ...mockState.announcements]
  return clone(newItem)
}

export async function publishAnnouncement(announcementId: number) {
  await wait(100)
  const payload = mockState.announcements.find((item) => item.id === announcementId)
  if (!payload) return apiError(`Comunicado ${announcementId} nao encontrado.`)
  payload.status = "publicado"
  return clone(payload)
}

export async function getResidentPortalHome() {
  await wait(80)
  return clone({
    profile: residentProfile as ResidentProfile,
    condo: clone(condo),
    unit: clone(residentUnit),
    active_tickets: clone(portalTickets as PortalTicket[]),
    recent_announcements_count: mockState.announcements.filter((item) => item.status === "publicado").length,
  })
}

export async function listResidentTickets(unit: string) {
  await wait(90)
  const normalizedUnit = unit.trim()
  return clone(portalTickets.filter((ticket) => ticket.unit === normalizedUnit))
}

export async function listPortalTimeline() {
  await wait(90)
  return clone(residentTimeline as PortalTimelineEvent[])
}

export async function askResidentRule(payload: { question: string }) {
  await wait(100)
  const lowered = payload.question.toLowerCase()
  const directHit = documentFaqMock.find((entry) => lowered.includes(entry.question.toLowerCase()))
  const answer = directHit
    ? directHit.answer
    : "Segundo o regimento e as regras do condominio, se houver risco operacional registre chamado. Para dúvidas operacionais, acompanhe a regra e agende com a administracao."

  return {
    answer,
    confidence: directHit ? 0.94 : 0.74,
    answered_at: new Date().toISOString(),
  }
}

export async function getKanbanMetadata() {
  await wait(10)
  return clone({ status_map: ticketStatusLabels })
}

export { ticketStatusOptions, ticketStatusLabels, type TicketStatus, type TicketPriority }
