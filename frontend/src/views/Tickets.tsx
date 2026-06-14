import { Bot, Plus, RefreshCw, X } from "lucide-react"
import { useMemo, useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"

const tickets = [
  {
    id: 1042,
    unit: "Apt 402",
    title: "Vazamento no teto do banheiro suite",
    priority: "Alta",
    status: "Em analise",
    risk: "Dano Estrutural",
    created: "Hoje, 08:30",
    location: "Apt 402 - Bloco A",
    category: "Manutencao Hidraulica",
    owner: "Carlos, zelador",
    description:
      "O teto do banheiro da suite esta com vazamento constante e manchas aumentando. Ha risco de infiltracao para o apartamento abaixo.",
  },
  {
    id: 1041,
    unit: "Area Comum",
    title: "Lampada queimada na garagem G2",
    priority: "Baixa",
    status: "Fornecedor acionado",
    risk: "Nenhum",
    created: "Ontem, 18:15",
    location: "Garagem G2",
    category: "Eletrica",
    owner: "Equipe de manutencao",
    description: "Ponto de iluminacao intermitente proximo ao portao de acesso da garagem.",
  },
  {
    id: 1040,
    unit: "Apt 101",
    title: "Barulho apos as 22h no andar de cima",
    priority: "Media",
    status: "Recebido",
    risk: "Convivencia",
    created: "Ontem, 23:45",
    location: "Torre A",
    category: "Convivencia",
    owner: "Portaria",
    description: "Relato recorrente de ruido alto depois do horario permitido pelo regimento.",
  },
]

const filters = ["Todos", "Recebido", "Em analise", "Fornecedor acionado", "Aguardando aprovacao", "Em execucao"]

function priorityTone(priority: string) {
  if (priority === "Alta") return "critical" as const
  if (priority === "Media") return "medium" as const
  return "neutral" as const
}

export function Tickets() {
  const [filter, setFilter] = useState("Todos")
  const [selectedId, setSelectedId] = useState(1042)
  const selected = tickets.find((ticket) => ticket.id === selectedId) ?? tickets[0]
  const rows = useMemo(() => {
    if (filter === "Todos") return tickets
    return tickets.filter((ticket) => ticket.status === filter)
  }, [filter])

  return (
    <div className="view-stack">
      <SectionHeader
        title="Gestao de Chamados"
        description="Tabela operacional com triagem, risco e painel de detalhe do chamado."
        action={
          <button className="btn btn-primary" type="button">
            <Plus size={16} />
            Novo Chamado
          </button>
        }
      />

      <div className="toolbar-inline">
        {filters.map((item) => (
          <button
            key={item}
            className={filter === item ? "btn btn-primary" : "btn btn-outline"}
            type="button"
            onClick={() => setFilter(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="tickets-layout">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Unidade</th>
                <th>Titulo</th>
                <th>Prioridade</th>
                <th>Status</th>
                <th>Risco</th>
                <th>Criado em</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((ticket) => (
                <tr key={ticket.id} onClick={() => setSelectedId(ticket.id)}>
                  <td>#{ticket.id}</td>
                  <td>{ticket.unit}</td>
                  <td>{ticket.title}</td>
                  <td>
                    <Badge tone={priorityTone(ticket.priority)}>{ticket.priority}</Badge>
                  </td>
                  <td>{ticket.status}</td>
                  <td>
                    <Badge tone={ticket.risk === "Dano Estrutural" ? "critical" : "neutral"}>{ticket.risk}</Badge>
                  </td>
                  <td>{ticket.created}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <Card className="ticket-detail" title={`#${selected.id}`} subtitle={selected.title}>
          <div className="stack-list">
            <div className="card-head">
              <Badge tone={priorityTone(selected.priority)}>Prioridade {selected.priority}</Badge>
              <button className="icon-button" type="button" aria-label="Fechar detalhe">
                <X size={16} />
              </button>
            </div>
            <div className="field-grid">
              <div className="field">
                <span>Unidade / Local</span>
                {selected.location}
              </div>
              <div className="field">
                <span>Categoria</span>
                {selected.category}
              </div>
              <div className="field">
                <span>Status</span>
                {selected.status}
              </div>
              <div className="field">
                <span>Responsavel</span>
                {selected.owner}
              </div>
            </div>
            <div>
              <span className="label">Descricao do Morador</span>
              <p className="field">{selected.description}</p>
            </div>
            <div className="ia-card">
              <div className="status-row">
                <Bot size={18} />
                <strong>Classificacao Sugerida</strong>
              </div>
              <div className="field-grid">
                <div className="field">
                  <span>Tipo</span>
                  Vazamento / Infiltracao
                </div>
                <div className="field">
                  <span>Risco</span>
                  Dano Estrutural Iminente
                </div>
              </div>
              <p>
                Acionar manutencao hidro-sanitaria imediatamente e notificar o morador do apartamento acima para fechar
                o registro temporariamente.
              </p>
              <div className="status-row">
                <span className="small muted">Confianca da Analise:</span>
                <strong>92%</strong>
                <button className="btn btn-outline" type="button">
                  <RefreshCw size={14} />
                  Reclassificar
                </button>
              </div>
            </div>
            <div className="action-row">
              <button className="btn btn-outline" type="button">
                Encaminhar
              </button>
              <button className="btn btn-primary" type="button">
                Aprovar acao
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
