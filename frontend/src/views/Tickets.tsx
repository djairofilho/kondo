import { BotMessageSquare, ChevronRight, Filter } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { classifyTicket, listTickets } from "../services/mockApi"
import { ticketStatusLabels, type Ticket, type TicketPriority, type TicketStatus, ticketStatusOptions } from "../data/tickets"

const priorityTone: Record<TicketPriority, "critical" | "high" | "medium"> = {
  baixa: "medium",
  media: "high",
  alta: "critical",
}

function riskTone(value: string): "critical" | "high" | "medium" {
  if (value === "alto") return "critical"
  if (value === "medio") return "high"
  return "medium"
}

export function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<"all" | TicketStatus>("all")
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [classified, setClassified] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    void (async () => {
      const payload = await listTickets()
      if (!active) return
      setTickets(payload)
      if (payload[0]) setSelectedId(payload[0].id)
      setLoading(false)
    })()
    return () => {
      active = false
    }
  }, [])

  const selected = useMemo(() => {
    if (selectedId === null) return null
    return tickets.find((ticket) => ticket.id === selectedId) ?? null
  }, [selectedId, tickets])

  const dataset = useMemo(() => {
    if (statusFilter === "all") return tickets
    return tickets.filter((item) => item.status === statusFilter)
  }, [statusFilter, tickets])

  return (
    <div className="view-stack">
      <SectionHeader
        title="Chamados"
        description="Fila operacional e detalhe rápido para o chamado selecionado."
      />
      <div className="toolbar-inline">
        <div className="toolbar-group">
          <Filter size={16} />
          <label className="label-inline" htmlFor="status-filter">
            Filtro de status:
          </label>
          <select
            id="status-filter"
            className="btn btn-outline"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value as "all" | TicketStatus)}
          >
            <option value="all">Todos</option>
            {ticketStatusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="toolbar-group">
          <span className="muted">{loading ? "Carregando..." : `${dataset.length} itens`}</span>
        </div>
      </div>

      <div className="tickets-layout">
        <Card title="Chamados" subtitle="Lista densa com microestado">
          <div className="tickets-head">
            <span>Unidade</span>
            <span>Título</span>
            <span>Prioridade</span>
            <span>Status</span>
          </div>
          <div className="tickets-body">
            {dataset.map((ticket) => (
              <button
                key={ticket.id}
                type="button"
                className={`row-button ${selectedId === ticket.id ? "active" : ""}`}
                onClick={() => {
                  setSelectedId(ticket.id)
                }}
              >
                <span>{ticket.unit}</span>
                <span>
                  <strong>{ticket.title}</strong>
                  <div className="muted small">{ticket.location}</div>
                </span>
                <span>
                  <Badge tone={priorityTone[ticket.priority]}>{ticket.priority}</Badge>
                </span>
                <span className="status-value">
                  {ticketStatusLabels[ticket.status] || ticket.status}
                  <ChevronRight size={16} />
                </span>
              </button>
            ))}
          </div>
        </Card>

        <Card title="Detalhe do chamado" subtitle={selected ? `ID ${selected.id}` : "Selecione um chamado"}>
          {!selected ? (
            <p className="muted">Selecione um chamado para visualizar o detalhe.</p>
          ) : (
            <>
              <h3>{selected.title}</h3>
              <p>{selected.description}</p>
              <div className="ticket-meta-grid">
                <p>
                  <strong>Unidade:</strong> {selected.unit}
                </p>
                <p>
                  <strong>Local:</strong> {selected.location}
                </p>
                <p>
                  <strong>Categoria:</strong> {selected.category}
                </p>
                <p>
                  <strong>Prioridade:</strong> {selected.priority}
                </p>
                <p>
                  <strong>Status:</strong> {ticketStatusLabels[selected.status]}
                </p>
                <p>
                  <strong>Origem:</strong> {selected.source}
                </p>
              </div>
              <p>
                <strong>Próxima ação:</strong> {selected.next_action}
              </p>
              <p>
                <strong>Responsável atual:</strong> {selected.owner}
              </p>
              <div className="ticket-meta">
                <Badge tone={priorityTone[selected.priority]}>{`Prioridade ${selected.priority}`}</Badge>
                <Badge tone={riskTone(selected.risk)}>{selected.risk}</Badge>
              </div>
              <div className="ia-card">
                <h4>
                  <BotMessageSquare size={16} /> Classificação IA
                </h4>
                <p>
                  Categoria: {selected.ai_analysis.category} • Ação sugerida: {selected.ai_analysis.next_action}
                </p>
                <button
                  className="btn btn-outline"
                  type="button"
                  onClick={async () => {
                    const result = await classifyTicket(selected.id)
                    setClassified(JSON.stringify(result, null, 2))
                  }}
                >
                  Reexecutar classificação IA
                </button>
                {classified ? <pre className="json">{classified}</pre> : null}
              </div>
              <p className="small muted">Confiança IA: {selected.confidence}%</p>
            </>
          )}
        </Card>
      </div>
    </div>
  )
}

