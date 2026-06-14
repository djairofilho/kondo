import { ArrowRight, MoveRight, PlaySquare } from "lucide-react"
import { useEffect, useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { getKanbanMetadata, listKanbanColumns, moveKanbanTicket } from "../services/mockApi"
import { type Ticket, type TicketStatus } from "../data/tickets"

const statusFlow: TicketStatus[] = ["received", "in_review", "vendor_contacted", "waiting_approval", "in_progress", "resolved"]

export function Kanban() {
  const [loading, setLoading] = useState(true)
  const [columns, setColumns] = useState<Array<{ id: string; label: string; count: number; tickets: Ticket[] }>>([])
  const [metadata, setMetadata] = useState<Record<string, string>>({})

  async function loadBoard() {
    const [board, meta] = await Promise.all([listKanbanColumns(), getKanbanMetadata()])
    setColumns(board)
    setMetadata(meta.status_map)
    setLoading(false)
  }

  useEffect(() => {
    let active = true
    void (async () => {
      const [board, meta] = await Promise.all([listKanbanColumns(), getKanbanMetadata()])
      if (!active) return
      setColumns(board)
      setMetadata(meta.status_map)
      setLoading(false)
    })()
    return () => {
      active = false
    }
  }, [])

  async function handleMove(ticketId: number, currentStatus: TicketStatus) {
    const index = statusFlow.indexOf(currentStatus)
    const nextStatus = statusFlow[Math.min(index + 1, statusFlow.length - 1)]
    await moveKanbanTicket(ticketId, nextStatus)
    await loadBoard()
  }

  return (
    <div className="view-stack">
      <SectionHeader title="Kanban operacional" description="Fluxo de manutenção com microestado por chamado." />

      <div className="kanban-toolbar">
        <span className="muted">{loading ? "Sincronizando..." : `Colunas ativas: ${columns.length}`}</span>
        <button className="btn btn-primary" type="button" onClick={loadBoard} disabled={loading}>
          <PlaySquare size={16} />
          Atualizar
        </button>
      </div>

      <div className="kanban-grid">
        {loading ? (
          <Card title="Carregando quadro" subtitle="Buscando status dos chamados">
            <p className="muted">Aguarde...</p>
          </Card>
        ) : (
          columns.map((column) => (
            <Card key={column.id} title={column.label} className="kanban-column" subtitle={`${column.tickets.length} itens`}>
              <div className="kanban-list">
                {column.tickets.length === 0 ? (
                  <p className="muted">Sem itens no momento.</p>
                ) : (
                  column.tickets.map((ticket) => (
                    <article key={ticket.id} className="k-kanban-card">
                      <div className="card-head">
                        <strong>
                          {ticket.unit} • #{ticket.id}
                        </strong>
                        <Badge
                          tone={
                            ticket.priority === "alta" ? "critical" : ticket.priority === "média" ? "high" : "medium"
                          }
                        >
                          {ticket.priority}
                        </Badge>
                      </div>
                      <p>{ticket.title}</p>
                      <p className="muted small">{ticket.location}</p>
                      <p className="muted small">{ticket.ai_analysis.next_action}</p>
                      <div className="kanban-item-meta">
                        <span>{metadata[ticket.status] ?? ticket.status}</span>
                        <span className="muted">ID {ticket.id}</span>
                      </div>
                      <button
                        className="btn btn-outline"
                        type="button"
                        onClick={() => handleMove(ticket.id, ticket.status)}
                        disabled={ticket.status === "resolved"}
                      >
                        <MoveRight size={14} />
                        Próximo passo
                      </button>
                    </article>
                  ))
                )}
              </div>
            </Card>
          ))
        )}
      </div>

      <Card title="Legenda" subtitle="Ordem operacional do fluxo">
        <div className="status-flow">
          {statusFlow.map((item) => (
            <span className="status-flow-item" key={item}>
              <ArrowRight size={12} />
              {metadata[item] ?? item}
            </span>
          ))}
        </div>
      </Card>
    </div>
  )
}
