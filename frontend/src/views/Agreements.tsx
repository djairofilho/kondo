import { Calculator, CheckCircle2, CircleAlert } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { listAgreements, listDelinquencies, simulateAgreement } from "../services/mockApi"
import type { Agreement } from "../data/agreements"
import type { Delinquency } from "../data/delinquencies"

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

export function Agreements() {
  const [list, setList] = useState<Agreement[]>([])
  const [delinquencies, setDelinquencies] = useState<Delinquency[]>([])
  const [selectedUnit, setSelectedUnit] = useState<string>("")
  const [entryAmount, setEntryAmount] = useState<number>(400)
  const [installments, setInstallments] = useState<number>(4)
  const [simulation, setSimulation] = useState<Awaited<ReturnType<typeof simulateAgreement>> | null>(null)

  useEffect(() => {
    let active = true
    listAgreements().then((payload) => {
      if (active) {
        setList(payload)
        setSelectedUnit(payload[0]?.unit || "")
      }
    })
    listDelinquencies().then((payload) => {
      if (active) setDelinquencies(payload)
    })
    return () => {
      active = false
    }
  }, [])

  const current = delinquencies.find((item) => item.unit === selectedUnit)
  const agreement = list.find((item) => item.unit === selectedUnit)

  async function runSimulation() {
    if (!current) return
    const result = await simulateAgreement({
      unit_id: current.unit_id,
      amount_due: current.amount_due,
      entry_amount: entryAmount,
      installments,
    })
    setSimulation(result)
  }

  return (
    <div className="view-stack">
      <SectionHeader
        title="Inadimplência e acordos"
        description="Lista de unidades em atraso e simulação de acordo por unidade."
      />

      <div className="grid-2">
        <Card title="Unidades inadimplentes" subtitle="Painel de recuperação financeira">
          {delinquencies.map((row) => (
            <button
              key={row.id}
              type="button"
              className={`row-button ${selectedUnit === row.unit ? "active" : ""}`}
              onClick={() => setSelectedUnit(row.unit)}
            >
              <span>
                <strong>Unidade {row.unit}</strong>
                <span className="muted small"> {row.days_late} dias em atraso</span>
              </span>
              <span>{money.format(row.amount_due)}</span>
              <span>{row.risk}</span>
            </button>
          ))}
        </Card>

        <Card title="Simulação de acordo" subtitle="Ajuste entrada e parcelas e veja impacto no caixa">
          <p>
            <strong>Unidade selecionada:</strong> {selectedUnit || "não selecionada"}
          </p>
          <p>Situação atual: {agreement ? `${money.format(agreement.amount_due)} em aberto` : "Sem acordo vinculado ainda"}</p>
          <label htmlFor="entry">Entrada (R$)</label>
          <input
            id="entry"
            type="number"
            value={entryAmount}
            onChange={(event) => setEntryAmount(Number(event.target.value))}
            min={0}
          />
          <label htmlFor="installments">Parcelas</label>
          <input
            id="installments"
            type="number"
            value={installments}
            onChange={(event) => setInstallments(Number(event.target.value))}
            min={1}
            max={24}
          />
          <button type="button" className="btn btn-primary" onClick={runSimulation}>
            <Calculator size={16} />
            Simular impacto no fluxo
          </button>
          {simulation ? (
            <div className="simulation-result">
              <div className="status-row">
                <CheckCircle2 size={16} />
                <span>Entrada: {money.format(simulation.entry_amount || 0)}</span>
              </div>
              <div className="status-row">
                <CircleAlert size={16} />
                <span>Parcela: {money.format(simulation.monthly_installment)}/mês</span>
              </div>
              <p>Impacto no caixa: {money.format(simulation.projected_cash_impact)}</p>
              <p className="muted">{simulation.recommendation}</p>
            </div>
          ) : (
            <p className="muted">Ainda sem simulação. Clique em simular.</p>
          )}
        </Card>
      </div>
    </div>
  )
}

