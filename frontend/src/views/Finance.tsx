import { Download, Lightbulb, Plus, SlidersHorizontal, TrendingUp } from "lucide-react"
import { useMemo, useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { MetricCard } from "../components/MetricCard"
import { SectionHeader } from "../components/SectionHeader"

const revenues = [
  ["REC-1042", "Cota Condominial - Apto 402", "05/09/2023", "R$ 850,00", "Recebido"],
  ["REC-1043", "Cota Condominial - Apto 501", "05/09/2023", "R$ 850,00", "Recebido"],
  ["REC-1044", "Reserva Salao de Festas", "08/09/2023", "R$ 150,00", "Pendente"],
]

const expenses = [
  ["DES-2088", "Conta de Agua (Sabesp)", "10/09/2023", "R$ 4.200,00", "Agendado"],
  ["DES-2089", "Manutencao Elevadores", "15/09/2023", "R$ 1.850,00", "A Pagar"],
]

export function Finance() {
  const [lateRate, setLateRate] = useState(15)
  const [extra, setExtra] = useState(0)
  const projectedGap = useMemo(() => 34100 - lateRate * 220 + extra, [lateRate, extra])

  return (
    <div className="view-stack">
      <SectionHeader
        title="Visao Financeira"
        description="Competencia: Setembro 2023"
        action={
          <div className="action-row">
            <button className="btn btn-outline" type="button">
              <Download size={16} />
              Exportar
            </button>
            <button className="btn btn-primary" type="button">
              <Plus size={16} />
              Novo Lancamento
            </button>
          </div>
        }
      />

      <div className="metrics-grid">
        <MetricCard label="Receita Esperada" value="R$ 145.000,00" note="+2,4% vs mes ant.">
          <TrendingUp size={18} />
        </MetricCard>
        <MetricCard label="Receita Recebida" value="R$ 132.500,00" note="91,4% liquidado" />
        <MetricCard label="Despesas (Pagas/Previstas)" value="R$ 98.400,00" note="2 pagamentos pendentes" />
        <MetricCard label="Gap (Saldo Projetado)" value="R$ 34.100,00" note="Projecao atual" />
      </div>

      <div className="split-even">
        <Card title="Receitas" subtitle="Lancamentos de entrada">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Descricao</th>
                  <th>Data</th>
                  <th>Valor</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {revenues.map(([id, description, date, amount, status]) => (
                  <tr key={id}>
                    <td>{id}</td>
                    <td>{description}</td>
                    <td>{date}</td>
                    <td className="money">{amount}</td>
                    <td>
                      <Badge tone={status === "Recebido" ? "paid" : "pending"}>{status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Despesas" subtitle="Pagamentos e previsoes">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Descricao</th>
                  <th>Data Venc.</th>
                  <th>Valor</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map(([id, description, date, amount, status]) => (
                  <tr key={id}>
                    <td>{id}</td>
                    <td>{description}</td>
                    <td>{date}</td>
                    <td className="money">{amount}</td>
                    <td>
                      <Badge tone="neutral">{status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      <div className="grid-2">
        <Card title="Simulador de Fluxo" subtitle="Ajuste cenarios de inadimplencia e entrada extra">
          <div className="form-grid">
            <label>
              Inadimplencia projetada
              <div className="range-row">
                <input value={lateRate} min={0} max={35} type="range" onChange={(event) => setLateRate(Number(event.target.value))} />
                <strong>{lateRate}%</strong>
              </div>
            </label>
            <label>
              Entrada extra prevista
              <input value={extra} type="number" onChange={(event) => setExtra(Number(event.target.value))} />
            </label>
            <div className="field">
              <span>Novo Gap Projetado</span>
              <strong className="metric-value">
                {new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(projectedGap)}
              </strong>
            </div>
          </div>
        </Card>

        <Card title="Insights IA" subtitle="Leituras operacionais do mes" className="ai-panel">
          <div className="stack-list">
            <div className="status-row">
              <SlidersHorizontal size={18} />
              <strong>Alerta de Inadimplencia</strong>
            </div>
            <p className="muted">
              O bloco B apresentou aumento de 4% nos atrasos este mes. Sugerimos campanha de renegociacao direcionada.
            </p>
            <div className="status-row">
              <Lightbulb size={18} />
              <strong>Otimizacao de Despesas</strong>
            </div>
            <p className="muted">
              Os gastos com energia da area comum estao 12% acima da media historica. Considere revisar o timer de
              iluminacao.
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
