import { Calculator, CheckCircle2, CircleAlert, FileChartColumn } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { listAgreements, listDelinquencies, simulateAgreement } from "../services/mockApi"
import type { Agreement } from "../data/agreements"
import type { Delinquency } from "../data/delinquencies"

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" })

export function Agreements() {
  const [agreements, setAgreements] = useState<Agreement[]>([])
  const [delinquencies, setDelinquencies] = useState<Delinquency[]>([])
  const [selectedUnit, setSelectedUnit] = useState<string>("")
  const [entryAmount, setEntryAmount] = useState<number>(400)
  const [installments, setInstallments] = useState<number>(4)
  const [simulation, setSimulation] = useState<Awaited<ReturnType<typeof simulateAgreement>> | null>(null)

  useEffect(() => {
    let active = true
    Promise.all([listAgreements(), listDelinquencies()]).then(([agPayload, dPayload]) => {
      if (!active) return
      setAgreements(agPayload)
      setDelinquencies(dPayload)
      setSelectedUnit(dPayload[0]?.unit ?? "")
    })
    return () => {
      active = false
    }
  }, [])

  const current = useMemo(
    () => delinquencies.find((item) => item.unit === selectedUnit) ?? null,
    [delinquencies, selectedUnit],
  )
  const agreement = useMemo(
    () => agreements.find((item) => item.unit === selectedUnit) ?? null,
    [agreements, selectedUnit],
  )

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
        description="Selecione unidades inadimplentes e simule cenários de entrada e parcelas."
      />

      <div className="grid-2">
        <Card title="Unidades inadimplentes" subtitle="Painel de recuperação">
          {delinquencies.length === 0 ? (
            <p className="muted">Sem unidades inadimplentes no momento.</p>
          ) : (
            delinquencies.map((row) => (
              <button
                key={row.id}
                type="button"
                className={`row-button ${selectedUnit === row.unit ? "active" : ""}`}
                onClick={() => {
                  setSelectedUnit(row.unit)
                  setSimulation(null)
                }}
              >
                <span>
                  <strong>Unidade {row.unit}</strong>
                  <span className="small muted"> {row.days_late} dias em atraso</span>
                </span>
                <span>{money.format(row.amount_due)}</span>
                <span>{row.risk}</span>
                <span>{row.status}</span>
              </button>
            ))
          )}
        </Card>

        <Card title="Simulador de acordo" subtitle="Ajuste entrada e parcelas para impacto no fluxo">
          <p>
            <strong>Unidade selecionada:</strong> {selectedUnit || "não selecionada"}
          </p>
          <p>{current ? `Saldo devedor: ${money.format(current.amount_due)}` : "Sem acordo vinculado ainda."}</p>
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
            Simular impacto
          </button>

          <div className="simulation-result">
            <div className="status-row">
              <FileChartColumn size={16} />
              <span>Situação atual: {agreement?.recommendation ?? "Sem acordo definido."}</span>
            </div>
          </div>

          {simulation ? (
            <>
              <div className="status-row">
                <CheckCircle2 size={16} />
                <span>Entrada: {money.format(simulation.entry_amount || 0)}</span>
              </div>
              <div className="status-row">
                <CircleAlert size={16} />
                <span>Parcela: {money.format(simulation.monthly_installment)} / mês</span>
              </div>
              <p>Impacto no caixa: {money.format(simulation.projected_cash_impact)}</p>
              <p className="muted">{simulation.recommendation}</p>
            </>
          ) : (
            <p className="muted">Ainda sem simulação. Clique em simular.</p>
          )}
        </Card>
      </div>
    </div>
  )
}

