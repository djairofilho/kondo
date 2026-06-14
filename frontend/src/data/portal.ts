import { tickets, type Ticket } from "./tickets"

export type ResidentProfile = {
  id: number
  role: "residente" | "sindico" | "mecanico" | "admin"
  name: string
  unit: string
  block: string
}

export type PortalTimelineEvent = {
  id: string
  created_at: string
  status: string
  actor: string
  note: string
}

export type PortalTicket = Pick<Ticket, "id" | "status" | "title" | "unit" | "created_at" | "owner" | "priority" | "category">

export const residentProfile: ResidentProfile = {
  id: 4,
  role: "residente",
  name: "Joao Morador",
  unit: "304",
  block: "Bloco A",
}

export const residentTimeline: PortalTimelineEvent[] = [
  {
    id: "evt-1",
    created_at: "Hoje, 09:10",
    status: "Recebido",
    actor: "Portal",
    note: "Chamado foi registrado e classificado como urgente.",
  },
  {
    id: "evt-2",
    created_at: "Hoje, 10:40",
    status: "Classificado pela IA",
    actor: "IA Kondo",
    note: "Risco eletronico com prioridade alta no local B2.",
  },
  {
    id: "evt-3",
    created_at: "Hoje, 11:10",
    status: "Fornecedor acionado",
    actor: "Gestor",
    note: "Equipe de emergencia confirmou acao para inspeccao.",
  },
  {
    id: "evt-4",
    created_at: "Hoje, 13:20",
    status: "Area isolada",
    actor: "Equipe tecnica",
    note: "Area da garagem esta isolada com aviso no portao.",
  },
]

export const portalTickets: PortalTicket[] = tickets
  .slice(0, 2)
  .map((ticket) => ({
    id: ticket.id,
    status: ticket.status,
    title: ticket.title,
    unit: ticket.unit,
    created_at: ticket.created_at,
    owner: ticket.owner,
    priority: ticket.priority,
    category: ticket.category,
  }))

