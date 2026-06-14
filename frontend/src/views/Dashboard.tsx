import { AlertTriangle, ArrowUpRight, CheckCircle2, Clock3, FileWarning, Wallet2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { getDashboard, listTickets } from "../services/mockApi"
import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { MetricCard } from "../components/MetricCard"
import { SectionHeader } from "../components/SectionHeader"
import type { Ticket } from "../data/tickets"

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

function toPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`
}

function toBadgeRisk(value?: "baixo" | "medio" | "alto") {
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
    getDashboard().then((payload) => {
      if (active) setSummary(payload)
    })
    listTickets().then((data) => {
      if (active) setTickets(data)
    })
    return () => {
      active = false
    }
  }, [])

  const criticalItems = useMemo(() => {
    if (!tickets.length) return []
    return tickets
      .filter((ticket) => ticket.risk === "alto" || ticket.priority === "alta")
      .slice(0, 4)
      .map((ticket) => ({
        id: ticket.id,
        title: ticket.title,
        description: ticket.next_action,
        urgency: ticket.risk === "alto" ? "critical" : "high",
      }))
  }, [tickets])

  return (
    <div className="view-stack">
      <SectionHeader
        title="Dashboard operacional"
        description="Visão executiva para decisões de curto e médio prazo."
      />
      <div className="dashboard-grid">
        <MetricCard label="Saldo atual" value={summary ? money.format(summary.cash_balance) : "..."}>
          <Wallet2 size={16} />
        </MetricCard>
        <MetricCard label="Caixa projetado" value={summary ? money.format(summary.projected_cash) : "..."} />
        <MetricCard
          label="Inadimplência"
          value={summary ? toPercent(summary.delinquency_rate) : "..."}
          note={summary ? `${summary.units} unidades ativas` : undefined}
        />
        <MetricCard
          label="Atraso no fluxo"
          value={summary ? money.format(summary.expected_revenue - summary.received_revenue) : "..."}
          note="Projecao de receitas pendentes"
        />
        <MetricCard
          label="Chamados abertos"
          value={summary ? `${summary.open_tickets}` : "..."}
          note={`${summary?.critical_tickets ?? 0} criticos`}
        />
        <MetricCard
          label="Taxa de atendimento pago"
          value={summary ? `${Math.round(summary.paid_percentage * 100)}%` : "..."}
          note="Pagamentos conciliados no mes atual"
        />
      </div>

      <div className="grid-2">
        <Card title="Fila de prioridades da IA" subtitle="Top prioridades para resolver hoje">
          <ul className="list-stack">
            {!summary ? (
              <li className="muted">Carregando prioridades</li>
            ) : (
              summary.ai_priorities.map((item) => (
                <li key={item.title} className="k-list-row">
                  <div className="list-content">
                    <strong>{item.title}</strong>
                    <p>{item.description}</p>
                  </div>
                  <Badge
                    tone={
                      item.urgency === "alto"
                        ? "critical"
                        : item.urgency === "medio"
                          ? "high"
                          : "medium"
                    }
                  >
                    {item.urgency}
                  </Badge>
                </li>
              ))
            )}
          </ul>
        </Card>

        <Card title="Status critico" subtitle="Bloco de risco operacional">
          <div className="critical-stack">
            <div className="critical-title">
              <FileWarning size={16} />
              <span>{summary?.critical_status_block.title ?? "Sem bloco critico"}</span>
            </div>
            <p>{summary?.critical_status_block.description}</p>
            <div className="status-row">
                <Badge tone={toBadgeRisk(summary?.critical_status_block.risk)}>
                {summary?.critical_status_block?.risk ?? "baixo"}
              </Badge>
              <span className="muted">Responsável: {summary?.critical_status_block.owner}</span>
            </div>
            <p className="muted">Próxima ação: {summary?.critical_status_block.next_action}</p>
            {criticalItems.length > 0 ? (
              <div className="ticket-compact">
                <h4>Chamados em foco</h4>
                {criticalItems.map((item) => (
                  <div key={item.id} className="status-row">
                    <Badge tone={item.urgency === "critical" ? "critical" : "high"}>{item.urgency}</Badge>
                    <span>{item.title}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </Card>
      </div>

      <Card title="Ações rápidas da operação" className="quick-actions">
        <div className="action-row">
          <button type="button" className="btn btn-outline">
            <Clock3 size={16} />
            Abrir Kanban
          </button>
          <button type="button" className="btn btn-outline">
            <CheckCircle2 size={16} />
            Ver financeiro
          </button>
          <button type="button" className="btn btn-outline">
            <ArrowUpRight size={16} />
            Ajustar acordos
          </button>
          <button type="button" className="btn btn-outline">
            <AlertTriangle size={16} />
            Novo comunicado
          </button>
        </div>
      </Card>
    </div>
  )
}
