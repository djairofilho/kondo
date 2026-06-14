import { Clock3, MessageCircleMore, Ticket, UserRound } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { askDocumentQuestion, getResidentPortalHome, listPortalTimeline } from "../services/mockApi"
import type { PortalTicket, PortalTimelineEvent, ResidentProfile } from "../data/portal"

export function ResidentPortal() {
  const [profile, setProfile] = useState<ResidentProfile | null>(null)
  const [tickets, setTickets] = useState<PortalTicket[]>([])
  const [timeline, setTimeline] = useState<PortalTimelineEvent[]>([])
  const [question, setQuestion] = useState("Pode fazer obra no sábado?")
  const [answer, setAnswer] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    getResidentPortalHome().then((payload) => {
      if (!active) return
      setProfile(payload.profile)
      setTickets(payload.active_tickets)
    })
    listPortalTimeline().then((payload) => {
      if (!active) return
      setTimeline(payload)
    })
    return () => {
      active = false
    }
  }, [])

  return (
    <div className="view-stack">
      <SectionHeader title="Portal do morador" description="Acompanhamento de chamados, timeline e regras do condomínio." />

      <div className="grid-2">
        <Card title="Meu perfil e unidade">
          <div className="status-row">
            <UserRound size={16} />
            <strong>{profile ? profile.name : "..."}</strong>
          </div>
          <p>Unidade: {profile ? `${profile.unit} - ${profile.block}` : "..."}</p>
          <p>Papel: {profile ? profile.role : "..."}</p>
          <button className="btn btn-primary" type="button">
            <Ticket size={16} />
            Abrir novo chamado
          </button>
        </Card>

        <Card title="Pergunte ao atendimento por regras">
          <label htmlFor="residentQuestion">Dúvida rápida</label>
          <input id="residentQuestion" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button
            className="btn btn-outline"
            type="button"
            onClick={async () => {
              const result = await askDocumentQuestion({ question })
              setAnswer(result.answer)
            }}
          >
            <MessageCircleMore size={16} />
            Perguntar IA
          </button>
          <p className="muted">{answer ?? "Digite uma pergunta para tirar sua dúvida."}</p>
        </Card>
      </div>

      <div className="grid-2">
        <Card title="Meus chamados ativos">
          {tickets.length === 0 ? (
            <p className="muted">Sem chamados em aberto.</p>
          ) : (
            tickets.map((ticket) => (
              <div key={ticket.id} className="status-row">
                <span>
                  <strong>{ticket.title}</strong>
                  <p className="muted">Unidade {ticket.unit}</p>
                </span>
                <span className="muted">{ticket.status}</span>
              </div>
            ))
          )}
        </Card>

        <Card title="Linha do tempo" subtitle="Status do chamado principal">
          <ul className="timeline">
            {timeline.map((item) => (
              <li key={item.id}>
                <div className="status-row">
                  <Clock3 size={14} />
                  <strong>{item.status}</strong>
                  <span className="muted">({item.created_at})</span>
                </div>
                <p>{item.note}</p>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  )
}
