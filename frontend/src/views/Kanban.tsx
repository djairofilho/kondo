import { MapPin, Plus, Search } from "lucide-react"
import { useState } from "react"

import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"

type CardItem = {
  id: number
  unit: string
  title: string
  location: string
  microstate: string
  next: string
  priority: "urgent" | "normal" | "low"
}

const initialColumns: Array<{ id: string; title: string; action: string; cards: CardItem[] }> = [
  {
    id: "received",
    title: "Recebido",
    action: "Analisar",
    cards: [
      {
        id: 1042,
        unit: "Apto 402",
        title: "Vazamento no teto do banheiro suite",
        location: "Torre A",
        microstate: "Aguardando triagem",
        next: "Validar com zelador",
        priority: "urgent",
      },
      {
        id: 1044,
        unit: "Apto 105",
        title: "Duvida sobre reserva de churrasqueira",
        location: "Torre B",
        microstate: "Novo relato",
        next: "Checar livro de ocorrencias",
        priority: "normal",
      },
    ],
  },
  {
    id: "analysis",
    title: "Em analise",
    action: "Aprovar",
    cards: [
      {
        id: 1039,
        unit: "Area Comum",
        title: "Reserva em conflito no clube",
        location: "Clube",
        microstate: "Checando conflitos",
        next: "Emitir boleto taxa",
        priority: "normal",
      },
    ],
  },
  {
    id: "vendor",
    title: "Fornecedor acionado",
    action: "P/ aprovacao",
    cards: [
      {
        id: 1035,
        unit: "Area Comum",
        title: "Bomba de drenagem com falha",
        location: "Subsolo 1",
        microstate: "Visita tecnica agendada",
        next: "Receber orcamento",
        priority: "urgent",
      },
    ],
  },
  { id: "approval", title: "Aguardando aprovacao", action: "Liberar", cards: [] },
  {
    id: "execution",
    title: "Em execucao",
    action: "Concluir",
    cards: [
      {
        id: 1028,
        unit: "Area Comum",
        title: "Pintura de corredores",
        location: "Torre A e B",
        microstate: "Em andamento (Torre A)",
        next: "Vistoria final",
        priority: "low",
      },
    ],
  },
  {
    id: "resolved",
    title: "Resolvido",
    action: "Arquivar",
    cards: [
      {
        id: 1025,
        unit: "Apto 801",
        title: "Tag de acesso substituida",
        location: "Portaria",
        microstate: "Finalizado em 12/05",
        next: "Sem pendencias",
        priority: "low",
      },
    ],
  },
]

export function Kanban() {
  const [columns, setColumns] = useState(initialColumns)

  function advance(columnId: string, card: CardItem) {
    const index = columns.findIndex((column) => column.id === columnId)
    if (index < 0 || index === columns.length - 1) return
    setColumns((current) =>
      current.map((column, currentIndex) => {
        if (currentIndex === index) return { ...column, cards: column.cards.filter((item) => item.id !== card.id) }
        if (currentIndex === index + 1) return { ...column, cards: [{ ...card, microstate: column.title }, ...column.cards] }
        return column
      }),
    )
  }

  return (
    <div className="view-stack">
      <SectionHeader
        title="Gestao de Chamados"
        description="Kanban operacional para acompanhar cada microestado de manutencao."
        action={
          <button className="btn btn-primary" type="button">
            <Plus size={16} />
            Novo chamado
          </button>
        }
      />

      <div className="kanban-toolbar">
        <div className="status-row">
          <span className="priority-dot urgent" />
          <span className="small muted">Urgente</span>
          <span className="priority-dot normal" />
          <span className="small muted">Normal</span>
          <span className="priority-dot low" />
          <span className="small muted">Baixa</span>
        </div>
        <label className="global-search">
          <Search size={16} />
          <span className="sr-only">Buscar chamado</span>
          <input placeholder="Buscar chamado..." />
        </label>
      </div>

      <div className="kanban-grid">
        {columns.map((column) => (
          <Card key={column.id} className="kanban-column" title={column.title} subtitle={`${column.cards.length} itens`}>
            <div className="kanban-list">
              {column.cards.length === 0 ? <p className="muted">Sem itens nesta etapa.</p> : null}
              {column.cards.map((card) => (
                <article className="kanban-card" key={card.id}>
                  <div className="card-head">
                    <span className="status-pill">{card.unit}</span>
                    <span className="small muted">#{card.id}</span>
                    <span className={`priority-dot ${card.priority}`} title={card.priority} />
                  </div>
                  <strong>{card.title}</strong>
                  <div className="status-row small muted">
                    <MapPin size={14} />
                    {card.location}
                  </div>
                  <p className="small muted">Status: {card.microstate}</p>
                  <p className="small">
                    <span className="muted">Proxima acao:</span> {card.next}
                  </p>
                  <button className="btn btn-outline" type="button" onClick={() => advance(column.id, card)}>
                    {column.action} →
                  </button>
                </article>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
