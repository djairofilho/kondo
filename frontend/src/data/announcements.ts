export type AnnouncementStatus = "rascunho" | "publicado" | "agendado"

export type Announcement = {
  id: number
  condominium_id: number
  title: string
  body: string
  audience: string
  status: AnnouncementStatus
  created_at: string
  scheduled_at: string | null
}

export const announcements: Announcement[] = [
  {
    id: 1,
    condominium_id: 1,
    title: "Reunião de prestação de contas",
    body:
      "As contas de maio foram conciliadas e o fechamento segue em revisão. A votação da nova taxa de manutenção será enviada na próxima semana.",
    audience: "Conselho e moradores",
    status: "publicado",
    created_at: "2026-06-11T10:00:00-03:00",
    scheduled_at: null,
  },
  {
    id: 2,
    condominium_id: 1,
    title: "Paralisação temporária do elevador",
    body:
      "A manutenção preventiva do elevador ocorrerá entre 8h e 14h, com acesso parcial apenas pela escada social do bloco A.",
    audience: "Todos os moradores",
    status: "publicado",
    created_at: "2026-06-08T08:10:00-03:00",
    scheduled_at: null,
  },
]

