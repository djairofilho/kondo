import { BotMessageSquare, ChevronRight, Filter, Timer, UserRound } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { classifyTicket, listTickets } from "../services/mockApi"
import {
  ticketRiskTone,
  ticketStatusLabels,
  ticketStatusOptions,
  type Ticket,
  type TicketPriority,
  type TicketStatus,
} from "../data/tickets"

const priorityTone: Record<TicketPriority, "critical" | "high" | "medium"> = {
  baixa: "medium",
  média: "high",
  alta: "critical",
}

function riskTone(value: string): "critical" | "high" | "medium" {
  return ticketRiskTone[value] ?? "medium"
}

export function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<"all" | TicketStatus>("all")
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [classified, setClassified] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    ;(async () => {
      const payload = await listTickets()
      if (!active) return
      setTickets(payload)
      setSelectedId(payload[0]?.id ?? null)
      setLoading(false)
    })()
    return () => {
      active = false
    }
  }, [])

  const selected = useMemo(
    () => (selectedId === null ? null : tickets.find((ticket) => ticket.id === selectedId) ?? null),
    [selectedId, tickets],
  )

  const dataset = useMemo(() => {
    if (statusFilter === "all") return tickets
    return tickets.filter((item) => item.status === statusFilter)
  }, [statusFilter, tickets])

  return (
    <div className="view-stack">
      <SectionHeader
        title="Chamados"
        description="Visão completa da fila de operação e detalhamento do chamado."
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
        <span className="muted">{loading ? "Carregando..." : `${dataset.length} chamado(s)`}</span>
      </div>

      <div className="tickets-layout">
        <Card title="Chamados" subtitle="Lista densa com status e prioridade">
          <div className="tickets-head">
            <span>Unidade</span>
            <span>Título</span>
            <span>Prioridade</span>
            <span>Status</span>
          </div>
          <div className="tickets-body">
            {loading ? (
              <p className="muted">Sincronizando chamados...</p>
            ) : dataset.length === 0 ? (
              <p className="muted">Sem chamados para este filtro.</p>
            ) : (
              dataset.map((ticket) => (
                <button
                  key={ticket.id}
                  type="button"
                  className={`row-button ${selectedId === ticket.id ? "active" : ""}`}
                  onClick={() => {
                    setSelectedId(ticket.id)
                    setClassified(null)
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
              ))
            )}
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
                <p>
                  <strong>Responsável:</strong> {selected.owner}
                </p>
                <p>
                  <strong>Assistente:</strong> {selected.assignee ?? "A definir"}
                </p>
              </div>

              <p>
                <strong>Próxima ação:</strong> {selected.next_action}
              </p>

              <div className="ticket-meta">
                <Badge tone={priorityTone[selected.priority]}>{`Prioridade ${selected.priority}`}</Badge>
                <Badge tone={riskTone(selected.risk)}>{selected.risk}</Badge>
                <div className="status-row small">
                  <UserRound size={14} />
                  <Badge tone="in_progress">{selected.owner}</Badge>
                </div>
                <div className="status-row small">
                  <Timer size={14} />
                  <Badge tone="resolved">{`Confiança IA ${selected.confidence}%`}</Badge>
                </div>
              </div>

              <div className="ia-card">
                <h4>
                  <BotMessageSquare size={16} />
                  Classificação IA
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
            </>
          )}
        </Card>
      </div>
    </div>
  )
}
