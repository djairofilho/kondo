import { ArrowRight, MoveRight, PlaySquare } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { moveKanbanTicket, getKanbanColumns } from "../services/mockApi"
import { type Ticket, ticketStatusOptions, type TicketStatus } from "../data/tickets"

const statusFlow: TicketStatus[] = ["received", "in_review", "vendor_contacted", "waiting_approval", "in_progress", "resolved"]

export function Kanban() {
  const [loading, setLoading] = useState(true)
  const [columns, setColumns] = useState<Array<{ id: string; label: string; tickets: Ticket[] }>>([])

  const load = useCallback(async () => {
    setLoading(true)
    const data = await getKanbanColumns()
    setColumns(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    let active = true
    ;(async () => {
      await load()
      if (!active) {
        setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [load])

  async function handleMove(ticketId: number, currentStatus: TicketStatus) {
    const index = statusFlow.indexOf(currentStatus)
    const nextStatus = statusFlow[Math.min(index + 1, statusFlow.length - 1)] as TicketStatus
    await moveKanbanTicket(ticketId, nextStatus)
    load()
  }

  return (
    <div className="view-stack">
      <SectionHeader
        title="Kanban operacional"
        description="Fluxo em andamento com microestado por chamado."
      />
      <div className="kanban-toolbar">
        <span className="muted">{loading ? "Sincronizando status..." : `Colunas ativas: ${columns.length}`}</span>
        <button className="btn btn-primary" type="button" onClick={load}>
          <PlaySquare size={16} />
          Atualizar
        </button>
      </div>

      <div className="kanban-grid">
        {columns.map((column) => (
          <Card key={column.id} title={column.label} className="kanban-column" subtitle={`${column.tickets.length} itens`}>
            <div className="kanban-list">
              {column.tickets.length === 0 ? (
                <p className="muted">Sem itens no momento.</p>
              ) : (
                column.tickets.map((ticket) => (
                  <article key={ticket.id} className="k-kanban-card">
                    <div className="card-head">
                      <h4>
                        {ticket.unit} • #{ticket.id}
                      </h4>
                      <Badge tone={ticket.priority === "alta" ? "critical" : ticket.priority === "media" ? "high" : "medium"}>
                        {ticket.priority}
                      </Badge>
                    </div>
                    <p>{ticket.title}</p>
                    <p className="muted">{ticket.location}</p>
                    <p className="muted">{ticket.ai_analysis.next_action}</p>
                    <button
                      className="btn btn-outline"
                      type="button"
                      onClick={() => handleMove(ticket.id, ticket.status)}
                      disabled={ticket.status === "resolved"}
                    >
                      <MoveRight size={14} /> Próximo passo
                    </button>
                  </article>
                ))
              )}
            </div>
          </Card>
        ))}
      </div>

      <Card title="Legenda" subtitle="Status do fluxo operacional">
        <div className="status-flow">
          {ticketStatusOptions.map((status) => (
            <span key={status.value} className="status-flow-item">
              <ArrowRight size={12} />
              {status.label}
            </span>
          ))}
        </div>
      </Card>
    </div>
  )
}
