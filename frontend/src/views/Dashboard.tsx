import { AlertTriangle, ArrowUpRight, CheckCircle2, Clock3, FileWarning, Wallet2, XCircle } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { MetricCard } from "../components/MetricCard"
import { SectionHeader } from "../components/SectionHeader"
import { getDashboard, listTickets } from "../services/mockApi"
import { type Ticket } from "../data/tickets"

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

function toPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`
}

function mapRiskTone(value?: "baixo" | "medio" | "alto") {
  if (!value) return "medium" as const
  if (value === "alto") return "critical" as const
  if (value === "medio") return "high" as const
  return "resolved" as const
}

export function Dashboard() {
  const [summary, setSummary] = useState<Awaited<ReturnType<typeof getDashboard>> | null>(null)
  const [tickets, setTickets] = useState<Ticket[]>([])

  useEffect(() => {
    let active = true

    Promise.all([getDashboard(), listTickets()]).then(([dashboardPayload, ticketsPayload]) => {
      if (!active) return
      setSummary(dashboardPayload)
      setTickets(ticketsPayload)
    })

    return () => {
      active = false
    }
  }, [])

  const criticalTickets = useMemo(() => {
    return tickets.filter((ticket) => ticket.risk === "alto" || ticket.priority === "alta").slice(0, 4)
  }, [tickets])

  return (
    <div className="view-stack">
      <SectionHeader
        title="Dashboard operacional"
        description="Visão executiva do condomínio para decisões em minutos."
      />

      <div className="dashboard-grid">
        <MetricCard label="Saldo atual" value={summary ? money.format(summary.cash_balance) : "..."}><Wallet2 size={16} /></MetricCard>
        <MetricCard label="Caixa projetado" value={summary ? money.format(summary.projected_cash) : "..."} />
        <MetricCard label="Inadimplência" value={summary ? toPercent(summary.delinquency_rate) : "..."} note={summary ? `${summary.units} unidades ativas` : undefined} />
        <MetricCard label="Recebíveis pendentes" value={summary ? money.format(summary.expected_revenue - summary.received_revenue) : "..."} note="Projeção de entradas em atraso" />
        <MetricCard label="Chamados abertos" value={summary ? `${summary.open_tickets}` : "..."} note={`${summary?.critical_tickets ?? 0} críticos`} />
        <MetricCard label="Atendimento pago" value={summary ? `${Math.round(summary.paid_percentage * 100)}%` : "..."} note="Pagamentos conciliados no mês atual" />
      </div>

      <div className="grid-2">
        <Card title="Fila de prioridades da IA" subtitle="Top prioridades para resolver hoje">
          <div className="priority-list">
            {!summary ? (
              <p className="muted">Carregando prioridades...</p>
            ) : (
              summary.ai_priorities.map((item) => (
                <div key={item.id} className="k-list-row">
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.description}</p>
                  </div>
                  <Badge tone={item.urgency === "alto" ? "critical" : item.urgency === "medio" ? "high" : "medium"}>
                    {item.urgency}
                  </Badge>
                </div>
              ))
            )}
          </div>
        </Card>

        <Card title="Status crítico" subtitle="Painel de risco operacional">
          <div className="critical-stack">
            <div className="critical-title">
              <FileWarning size={16} />
              <span>{summary?.critical_status_block.title ?? "Sem bloqueio crítico"}</span>
            </div>
            <p>{summary?.critical_status_block.description}</p>
            <div className="status-row">
              <Badge tone={mapRiskTone(summary?.critical_status_block.risk)}>{summary?.critical_status_block.risk ?? "baixo"}</Badge>
              <span className="muted">Responsável: {summary?.critical_status_block.owner}</span>
            </div>
            <p className="muted">Próxima ação: {summary?.critical_status_block.next_action}</p>
            <div className="ticket-compact">
              <strong>Chamados em foco</strong>
              {criticalTickets.length > 0 ? (
                criticalTickets.map((item) => (
                  <div className="status-row" key={item.id}>
                    <Badge tone={item.priority === "alta" ? "critical" : item.priority === "média" ? "high" : "medium"}>
                      {item.priority}
                    </Badge>
                    <span>{item.title}</span>
                  </div>
                ))
              ) : (
                <p className="muted">Sem chamado com risco elevado no momento.</p>
              )}
            </div>
          </div>
        </Card>
      </div>

      <Card title="Ações rápidas" subtitle="Atalhos para o ciclo operacional">
        <div className="action-row">
          <button type="button" className="btn btn-outline">
            <Clock3 size={16} />
            Abrir fila de chamados
          </button>
          <button type="button" className="btn btn-outline">
            <ArrowUpRight size={16} />
            Ir para Kanban
          </button>
          <button type="button" className="btn btn-outline">
            <CheckCircle2 size={16} />
            Revisar financeiro
          </button>
          <button type="button" className="btn btn-outline">
            <AlertTriangle size={16} />
            Priorizar acordo
          </button>
          <button type="button" className="btn btn-outline">
            <XCircle size={16} />
            Resolver bloqueios
          </button>
        </div>
      </Card>
    </div>
  )
}

