export type AnnouncementStatus = "rascunho" | "publicado"

export type Announcement = {
  id: number
  title: string
  body: string
  audience: string
  status: AnnouncementStatus
  created_at: string
}

export const announcements: Announcement[] = [
  {
    id: 1,
    title: "Reuniao de prestacao de contas",
    body:
      "As contas de maio foram conciliadas e o fechamento segue em revisao. A votacao da nova taxa de manutencao sera enviada na proxima semana.",
    audience: "Conselho e moradores",
    status: "publicado",
    created_at: "2026-06-11T10:00:00-03:00",
  },
  {
    id: 2,
    title: "Paralisacao temporaria do elevador",
    body:
      "A manutencao preventiva do elevador ocorrera entre 8h e 14h, com acesso parcial pela escada social.",
    audience: "Todos os moradores",
    status: "publicado",
    created_at: "2026-06-08T08:10:00-03:00",
  },
]

