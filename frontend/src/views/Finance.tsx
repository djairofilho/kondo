import { ArrowUpRight, CircleDollarSign, MinusCircle, RefreshCw } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { MetricCard } from "../components/MetricCard"
import { SectionHeader } from "../components/SectionHeader"
import {
  getFinanceInsightsAI,
  getFinanceProjectionImpact,
  listFinance,
  listFinanceSummary,
  listFinanceTransactions,
} from "../services/mockApi"

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

type FinanceData = Awaited<ReturnType<typeof listFinance>>

export function Finance() {
  const [finance, setFinance] = useState<FinanceData | null>(null)
  const [loading, setLoading] = useState(true)
  const [delta, setDelta] = useState(500)
  const [agreementImpact, setAgreementImpact] = useState(300)
  const [impact, setImpact] = useState<number | null>(null)
  const [insights, setInsights] = useState<string[]>([])

  useEffect(() => {
    let active = true

    Promise.all([listFinance(), getFinanceInsightsAI()]).then(([payload, insightPayload]) => {
      if (!active) return
      setFinance(payload)
      setInsights(insightPayload.insights)
      setLoading(false)
    })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true
    getFinanceProjectionImpact({ cash_gap_delta: delta, agreement_impact: agreementImpact }).then((result) => {
      if (active) setImpact(result.projected_cash_gap)
    })
    return () => {
      active = false
    }
  }, [delta, agreementImpact])

  async function refresh() {
    setLoading(true)
    const payload = await listFinanceSummary()
    const transactions = await listFinanceTransactions()
    const data = {
      summary: payload,
      transactions,
      insights: (await getFinanceInsightsAI()).insights,
    }
    setFinance(data)
    setInsights(data.insights)
    setLoading(false)
  }

  return (
    <div className="view-stack">
      <SectionHeader
        title="Financeiro e transparência"
        description="Resumo de receitas, despesas e impactos de ação para tomada de decisão."
      />

      <div className="grid metrics-grid">
        <MetricCard label="Receita esperada" value={loading ? "..." : money.format(finance?.summary.expected_revenue ?? 0)}>
          <CircleDollarSign size={16} />
        </MetricCard>
        <MetricCard label="Receita recebida" value={loading ? "..." : money.format(finance?.summary.received_revenue ?? 0)} />
        <MetricCard label="Despesas" value={loading ? "..." : money.format(finance?.summary.expenses ?? 0)} />
        <MetricCard label="Gap projetado" value={loading ? "..." : money.format(finance?.summary.cash_gap ?? 0)} />
      </div>

      <Card title="Simulação de impacto no caixa" subtitle="Ajuste os parâmetros para estimar cenários">
        <div className="simulation-form">
          <div>
            <label htmlFor="delta">Entrada antecipada (R$)</label>
            <input
              id="delta"
              type="range"
              min={-2000}
              max={5000}
              step={50}
              value={delta}
              onChange={(event) => setDelta(Number(event.target.value))}
            />
            <p className="small muted">Impacto selecionado: {money.format(delta)}</p>
          </div>
          <div>
            <label htmlFor="impact">Impacto de acordos (R$)</label>
            <input
              id="impact"
              type="range"
              min={0}
              max={3000}
              step={50}
              value={agreementImpact}
              onChange={(event) => setAgreementImpact(Number(event.target.value))}
            />
            <p className="small muted">Impacto selecionado: {money.format(agreementImpact)}</p>
          </div>
          <button type="button" className="btn btn-primary" onClick={refresh}>
            <RefreshCw size={16} />
            Recalcular
          </button>
          {impact !== null ? <p className="txn-total">Gap projetado: {money.format(impact)}</p> : null}
        </div>
      </Card>

      <div className="grid-2">
        <Card title="Receitas" subtitle="Pagamentos esperados e recebidos">
          {loading || !finance ? (
            <p className="muted">Carregando...</p>
          ) : (
            finance.transactions
              .filter((txn) => txn.type === "receita")
              .map((txn) => (
                <div key={txn.id} className="txn-row">
                  <span>
                    {txn.description}
                    <span className="small muted">#{txn.id}</span>
                  </span>
                  <span>{money.format(txn.amount)}</span>
                  <span>{txn.status}</span>
                  <span className="muted small">{txn.issued_at}</span>
                </div>
              ))
          )}
        </Card>
        <Card title="Despesas" subtitle="Custos fixos e variáveis">
          {loading || !finance ? (
            <p className="muted">Carregando...</p>
          ) : (
            finance.transactions
              .filter((txn) => txn.type === "despesa")
              .map((txn) => (
                <div key={txn.id} className="txn-row">
                  <span>
                    {txn.description}
                    <span className="small muted">#{txn.id}</span>
                  </span>
                  <span>{money.format(txn.amount)}</span>
                  <span>{txn.status}</span>
                  <span className="muted small">{txn.issued_at}</span>
                </div>
              ))
          )}
        </Card>
      </div>

      <Card
        title="Insights financeiros"
        subtitle={insights.length > 0 ? "Recomendações do assistente" : "Sem insights no momento"}
      >
        <div className="insights">
          {loading ? (
            <p className="muted">Carregando...</p>
          ) : (
            <>
              <div className="insight-item">
                <ArrowUpRight size={16} />
                {finance && finance.summary.cash_gap < 0 ? (
                  <span>
                    <strong>Fluxo:</strong> necessário recuperar {money.format(Math.abs(finance.summary.cash_gap))}
                  </span>
                ) : (
                  <span>
                    <strong>Fluxo:</strong> sem desequilíbrio no mês.
                  </span>
                )}
              </div>
              {insights.map((item, idx) => (
                <p key={`${item}-${idx}`} className={idx === 0 ? "muted" : "small muted"}>
                  {item}
                </p>
              ))}
              <p className="muted small">
                <MinusCircle size={14} /> Reavalie o cenário após simulação para comparar cenários.
              </p>
            </>
          )}
        </div>
      </Card>
    </div>
  )
}
