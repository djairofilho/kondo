import { Bot, Building2, CalendarDays, ChevronRight, Edit, Plus, Send, Ticket, UserRound } from "lucide-react"
import { useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"

const residentTickets = [
  ["Em analise", "Vazamento teto banheiro suite", "12/10/2023"],
  ["Aberto", "Reserva Churrasqueira (15/11)", "10/10/2023"],
  ["Resolvido", "Tag de acesso garagem nao funciona", "05/09/2023"],
]

const events = [
  ["Amanha, 14:00", "Manutencao Elevador Bloco B", "O elevador social ficara inoperante para manutencao preventiva ate as 16h."],
  ["20/10/2023", "Assembleia Geral", "Aprovacao de contas anuais e previsao orcamentaria 2024. Local: Salao de Festas."],
  ["25/10/2023", "Dedetizacao", "Areas comuns e subsolo. Evite circulacao de pets nestes locais durante o dia."],
]

export function ResidentPortal() {
  const [question, setQuestion] = useState("Qual o horario de funcionamento da piscina aos finais de semana?")
  const [answer, setAnswer] = useState(true)

  return (
    <div className="view-stack">
      <SectionHeader title="Portal do Morador" description="Autosservico, chamados e avisos para o residente." />

      <div className="grid-2">
        <div className="view-stack">
          <Card>
            <div className="status-row">
              <UserRound size={22} />
              <div>
                <h2>Mariana Costa e Silva</h2>
                <p className="muted">Morador Titular</p>
              </div>
            </div>
            <div className="field-grid">
              <div className="field">
                <span>Unidade</span>
                <div className="status-row">
                  <Building2 size={16} />
                  <strong>142</strong>
                </div>
              </div>
              <div className="field">
                <span>Bloco</span>
                <strong>B - Torre Sul</strong>
              </div>
            </div>
            <button className="btn btn-primary" type="button">
              <Edit size={16} />
              Atualizar dados
            </button>
          </Card>

          <Card title="Meus Chamados" subtitle="Acompanhe os status recentes">
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Titulo</th>
                    <th>Data</th>
                    <th className="text-right">Acao</th>
                  </tr>
                </thead>
                <tbody>
                  {residentTickets.map(([status, title, date]) => (
                    <tr key={title}>
                      <td>
                        <Badge tone={status === "Resolvido" ? "paid" : status === "Aberto" ? "neutral" : "medium"}>
                          {status}
                        </Badge>
                      </td>
                      <td>{title}</td>
                      <td>{date}</td>
                      <td className="text-right">
                        <button className="icon-button" type="button" aria-label={`Abrir ${title}`}>
                          <ChevronRight size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button className="btn btn-outline" type="button">
              <Plus size={16} />
              Abrir Novo Chamado
            </button>
          </Card>

          <Card title="Comunicados e Eventos" subtitle="Proximas ocorrencias">
            <ul className="timeline">
              {events.map(([date, title, description]) => (
                <li key={title}>
                  <strong>{title}</strong>
                  <span className="small muted">{date}</span>
                  <p className="muted">{description}</p>
                </li>
              ))}
            </ul>
          </Card>
        </div>

        <Card className="sticky-panel" title="Assistente Kondo" subtitle="Tire suas duvidas rapidamente">
          <div className="stack-list">
            <div className="ai-panel">
              <div className="status-row">
                <Bot size={20} />
                <strong>Conversa</strong>
              </div>
              <div className="field">
                <span>Voce</span>
                {question}
              </div>
              {answer ? (
                <div className="field">
                  <span>Assistente</span>
                  Ola! A piscina funciona das 08h00 as 20h00 aos sabados e domingos. As segundas-feiras ela e fechada
                  para manutencao.
                </div>
              ) : null}
            </div>
            <label>
              Pergunta
              <div className="status-row">
                <input value={question} onChange={(event) => setQuestion(event.target.value)} />
                <button className="icon-button" type="button" onClick={() => setAnswer(true)} aria-label="Enviar pergunta">
                  <Send size={18} />
                </button>
              </div>
            </label>
            <div className="panel quick-panel">
              <h3>Atalho rapido</h3>
              <button className="quick-action" type="button">
                <Ticket size={22} />
                Solicitar segunda via de boleto
              </button>
              <button className="quick-action" type="button">
                <CalendarDays size={22} />
                Reservar area comum
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
