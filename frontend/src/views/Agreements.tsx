import { Calculator, Download, Filter, Play, ShieldCheck, TrendingUp, Wallet } from "lucide-react"
import { useMemo, useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { MetricCard } from "../components/MetricCard"
import { SectionHeader } from "../components/SectionHeader"

const rows = [
  ["Apto 102 - Bloco A", 45, 1850, "Medio", "Sem Acordo"],
  ["Apto 304 - Bloco B", 120, 5400, "Alto", "Pendente Assinatura"],
  ["Apto 501 - Bloco A", 15, 650, "Baixo", "Ativo"],
  ["Casa 12", 80, 3200, "Medio", "Encerrado/Quebrado"],
] as const

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

export function Agreements() {
  const [selected, setSelected] = useState<string>(rows[0][0])
  const [entry, setEntry] = useState(500)
  const [installments, setInstallments] = useState(3)
  const current = rows.find((row) => row[0] === selected) ?? rows[0]
  const monthly = useMemo(() => Math.max(0, (current[2] - entry) / installments), [current, entry, installments])

  return (
    <div className="view-stack">
      <SectionHeader title="Inadimplencia e Acordos" description="Controle de atrasos e simulacao de renegociacao." />

      <div className="metrics-grid">
        <MetricCard label="Total em Atraso" value="R$ 11.100,00" note="14 unidades">
          <TrendingUp size={18} />
        </MetricCard>
        <MetricCard label="Unidades Inadimplentes" value="14" note="4 em risco alto" />
        <MetricCard label="Acordos Ativos" value="8" note="3 pendentes de assinatura">
          <ShieldCheck size={18} />
        </MetricCard>
        <MetricCard label="Recuperado Mes" value="R$ 7.450,00" note="+18% vs mes anterior">
          <Wallet size={18} />
        </MetricCard>
      </div>

      <div className="grid-2">
        <Card
          title="Lista de Unidades Inadimplentes"
          subtitle="Mostrando 4 de 14 unidades"
          className="panel"
        >
          <div className="action-row">
            <button className="btn btn-outline" type="button">
              <Filter size={14} />
              Filtrar
            </button>
            <button className="btn btn-outline" type="button">
              <Download size={14} />
              Exportar
            </button>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Unidade</th>
                  <th>Dias em Atraso</th>
                  <th>Valor Devido</th>
                  <th>Risco</th>
                  <th>Status de Acordo</th>
                  <th className="text-right">Acao</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row[0]} onClick={() => setSelected(row[0])}>
                    <td>{row[0]}</td>
                    <td>{row[1]} dias</td>
                    <td className="money">{money.format(row[2])}</td>
                    <td>
                      <Badge tone={row[3] === "Alto" ? "critical" : row[3] === "Medio" ? "high" : "paid"}>
                        {row[3]}
                      </Badge>
                    </td>
                    <td>
                      <Badge tone={row[4] === "Ativo" ? "paid" : row[4].startsWith("Pendente") ? "medium" : "neutral"}>
                        {row[4]}
                      </Badge>
                    </td>
                    <td className="text-right">
                      <button className="btn btn-outline" type="button">
                        {row[4] === "Sem Acordo" ? "Simular" : "Detalhes"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="sticky-panel" title="Painel de Simulacao" subtitle="Ajuste entrada e parcelas">
          <div className="form-grid">
            <label>
              Selecionar Unidade
              <select value={selected} onChange={(event) => setSelected(event.target.value)}>
                {rows.map((row) => (
                  <option key={row[0]}>{row[0]}</option>
                ))}
              </select>
            </label>
            <label>
              Valor da Entrada (R$)
              <input type="number" value={entry} min={0} onChange={(event) => setEntry(Number(event.target.value))} />
            </label>
            <label>
              Numero de Parcelas
              <div className="range-row">
                <input
                  type="range"
                  min={1}
                  max={12}
                  value={installments}
                  onChange={(event) => setInstallments(Number(event.target.value))}
                />
                <strong>{installments}x</strong>
              </div>
            </label>
            <button className="btn btn-primary" type="button">
              <Play size={16} />
              Simular Acordo
            </button>
            <div className="ai-panel">
              <div className="status-row">
                <Calculator size={18} />
                <strong>Resultado da Simulacao</strong>
              </div>
              <div className="field-grid">
                <div className="field">
                  <span>Parcela Mensal</span>
                  <strong>{money.format(monthly)}</strong>
                </div>
                <div className="field">
                  <span>Total Final</span>
                  <strong>{money.format(current[2])}</strong>
                </div>
              </div>
              <p className="muted">Projecao de caixa positiva a partir do proximo ciclo.</p>
            </div>
            <div className="action-row">
              <button className="btn btn-outline" type="button">
                Salvar Rascunho
              </button>
              <button className="btn btn-primary" type="button">
                Gerar Termo
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
