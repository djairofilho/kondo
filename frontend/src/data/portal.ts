import { tickets, type Ticket } from "./tickets"

export type ResidentProfile = {
  id: number
  role: "residente" | "sindico" | "mecanico" | "admin"
  name: string
  unit: string
  block: string
  building: string
}

export type PortalTimelineEvent = {
  id: string
  created_at: string
  status: string
  actor: string
  note: string
}

export type PortalUnit = {
  id: number
  number: string
  block: string
  condominium_id: number
}

export type PortalTicket = Pick<
  Ticket,
  "id" | "status" | "title" | "unit" | "created_at" | "owner" | "priority" | "category"
>

export const residentProfile: ResidentProfile = {
  id: 4,
  role: "residente",
  name: "João Morador",
  unit: "304",
  block: "Bloco A",
  building: "Condomínio Jardim Aurora",
}

export const residentTimeline: PortalTimelineEvent[] = [
  {
    id: "evt-1",
    created_at: "2026-06-14T09:10:00-03:00",
    status: "Recebido",
    actor: "Portal",
    note: "Chamado registrado e classificado para análise de urgência.",
  },
  {
    id: "evt-2",
    created_at: "2026-06-14T10:40:00-03:00",
    status: "Classificado pela IA",
    actor: "IA Kondo",
    note: "Risco elétrico com prioridade alta no local garagem B2.",
  },
  {
    id: "evt-3",
    created_at: "2026-06-14T11:10:00-03:00",
    status: "Fornecedor acionado",
    actor: "Gestor",
    note: "Equipe de emergência confirmou vistoria para esse fim de tarde.",
  },
  {
    id: "evt-4",
    created_at: "2026-06-14T13:20:00-03:00",
    status: "Área isolada",
    actor: "Equipe técnica",
    note: "Área da garagem isolada e sinalizada para evitar risco de choque.",
  },
]

export const portalTickets: PortalTicket[] = tickets.slice(0, 2).map((ticket) => ({
  id: ticket.id,
  status: ticket.status,
  title: ticket.title,
  unit: ticket.unit,
  created_at: ticket.created_at,
  owner: ticket.owner,
  priority: ticket.priority,
  category: ticket.category,
}))

export const residentUnit: PortalUnit = {
  id: 304,
  number: "304",
  block: "Bloco A",
  condominium_id: 1,
}

