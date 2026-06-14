import { Clock3, MessageCircleMore, Ticket, UserRound } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { askResidentRule, getResidentPortalHome, listPortalTimeline, listResidentTickets } from "../services/mockApi"
import type { PortalTimelineEvent, PortalTicket, ResidentProfile } from "../data/portal"

export function ResidentPortal() {
  const [profile, setProfile] = useState<ResidentProfile | null>(null)
  const [tickets, setTickets] = useState<PortalTicket[]>([])
  const [timeline, setTimeline] = useState<PortalTimelineEvent[]>([])
  const [question, setQuestion] = useState("Pode fazer obra no sábado?")
  const [answer, setAnswer] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [concluded, setConcluded] = useState(false)

  useEffect(() => {
    let active = true
    getResidentPortalHome().then((payload) => {
      if (!active) return
      setProfile(payload.profile)
      setTickets(payload.active_tickets)
      setLoading(false)
    })
    listPortalTimeline().then((payload) => {
      if (!active) return
      setTimeline(payload)
    })
    return () => {
      active = false
    }
  }, [])

  const unitId = useMemo(() => profile?.unit ?? "", [profile])

  useEffect(() => {
    if (!unitId) return
    let active = true
    listResidentTickets(unitId).then((payload) => {
      if (!active) return
      setTickets(payload)
    })
    return () => {
      active = false
    }
  }, [unitId])

  return (
    <div className="view-stack">
      <SectionHeader title="Portal do morador" description="Acompanhe chamados e regras do condomínio." />

      <div className="grid-2">
        <Card title="Meu perfil e unidade">
          {loading ? (
            <p className="muted">Carregando...</p>
          ) : (
            <>
              <div className="status-row">
                <UserRound size={16} />
                <strong>{profile ? profile.name : "Morador"}</strong>
              </div>
              <p>Unidade: {profile ? `${profile.unit} - ${profile.block}` : "-"}</p>
              <p>Papel: {profile ? profile.role : "-"}</p>
              {concluded ? (
                <p className="muted">Sem pendências no momento.</p>
              ) : (
                <button className="btn btn-primary" type="button">
                  <Ticket size={16} />
                  Abrir novo chamado
                </button>
              )}
            </>
          )}
        </Card>

        <Card title="Assistente de regras" subtitle="Pergunte para o time de atendimento">
          <label htmlFor="residentQuestion">Dúvida</label>
          <input id="residentQuestion" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button
            className="btn btn-outline"
            type="button"
            onClick={async () => {
              const result = await askResidentRule({ question })
              setAnswer(result.answer)
              setConcluded(true)
            }}
          >
            <MessageCircleMore size={16} />
            Perguntar IA
          </button>
          <p className="muted">{answer ?? "Digite uma pergunta para tirar sua dúvida."}</p>
        </Card>
      </div>

      <div className="grid-2">
        <Card title="Meus chamados ativos" subtitle="Acompanhe os status no portal">
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

        <Card title="Linha do tempo" subtitle="Status da ocorrência principal">
          <ul className="timeline">
            {timeline.map((item) => (
              <li key={item.id}>
                <div className="status-row">
                  <Clock3 size={14} />
                  <strong>{item.status}</strong>
                  <span className="muted">({item.created_at})</span>
                </div>
                <p>{item.note}</p>
                <p className="small muted">Origem: {item.actor}</p>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  )
}

