import {
  AlertTriangle,
  Bot,
  CalendarDays,
  CheckCircle2,
  FileText,
  Handshake,
  Megaphone,
  PlusCircle,
  Receipt,
  TrendingDown,
  TrendingUp,
  Wallet2,
} from "lucide-react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { MetricCard } from "../components/MetricCard"
import { SectionHeader } from "../components/SectionHeader"

const metrics = [
  { label: "Saldo Atual", value: "R$ 145.230,00", note: "+2,4% vs mes ant.", icon: Wallet2, tone: "good" },
  { label: "Caixa Projetado", value: "R$ 132.500,00", note: "-1,2% despesas", icon: TrendingDown, tone: "warn" },
  { label: "Inadimplencia", value: "4,8%", note: "Dentro da meta (< 5%)", icon: CheckCircle2, tone: "good" },
  { label: "Recebiveis Pend.", value: "R$ 18.450,00", note: "12 faturas ativas", icon: Receipt, tone: "neutral" },
  { label: "Chamados Abertos", value: "24", note: "5 criticos", icon: AlertTriangle, tone: "danger" },
  { label: "% Atend. Pago", value: "92%", note: "Meta: 95%", icon: TrendingUp, tone: "neutral" },
]

const priorities = [
  {
    title: "Barulho recorrente no Bloco B",
    description: "Identificado padrao de relatos recorrentes nos ultimos 3 dias.",
    badge: "Alto Risco",
    tone: "high" as const,
    action: "Acao Imediata",
  },
  {
    title: "Apto 304 com potencial acordo",
    description: "Morador acessou portal de acordos 2x hoje. Contato proativo sugerido.",
    badge: "Medio",
    tone: "medium" as const,
    action: "Iniciar Contato",
  },
  {
    title: "Renovacao do contrato de limpeza",
    description: "Renovacao necessaria em 45 dias. Orcamentos pre-aprovados disponiveis.",
    badge: "Baixo",
    tone: "neutral" as const,
    action: "Revisar Orcamentos",
  },
]

const quickActions = [
  { label: "Novo Chamado", icon: PlusCircle },
  { label: "Lancar Despesa", icon: Receipt },
  { label: "Gerar Acordo", icon: Handshake },
  { label: "Novo Comunicado", icon: Megaphone },
  { label: "Reservar Espaco", icon: CalendarDays },
  { label: "Relatorio Mensal", icon: FileText },
]

export function Dashboard() {
  return (
    <div className="view-stack">
      <SectionHeader
        title="Dashboard"
        description="Visao geral da operacao, caixa e riscos do Condominio Edificio Horizon."
      />

      <div className="dashboard-grid">
        {metrics.map((metric) => {
          const Icon = metric.icon
          return (
            <MetricCard key={metric.label} label={metric.label} value={metric.value} note={metric.note}>
              <Icon size={18} />
            </MetricCard>
          )
        })}
      </div>

      <div className="grid-2">
        <Card
          title="Fila de Prioridades da IA"
          subtitle="Itens que exigem acao operacional ou contato proativo"
          className="ai-panel"
        >
          <div className="priority-list">
            {priorities.map((item) => (
              <div className="list-row" key={item.title}>
                <div>
                  <div className="status-row">
                    <Bot size={16} />
                    <strong>{item.title}</strong>
                    <Badge tone={item.tone}>{item.badge}</Badge>
                  </div>
                  <p>{item.description}</p>
                </div>
                <button className={item.tone === "high" ? "btn btn-primary" : "btn btn-outline"} type="button">
                  {item.action}
                </button>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Status Critico" subtitle="Risco operacional em acompanhamento" className="critical-panel">
          <div className="stack-list">
            <div className="status-row">
              <AlertTriangle size={18} />
              <strong>Elevador social Bloco A</strong>
            </div>
            <div className="field-grid">
              <div className="field">
                <span>Responsavel</span>
                Manutencao Atlas
              </div>
              <div className="field">
                <span>Risco</span>
                Freio secundario
              </div>
            </div>
            <p className="muted">Acao sugerida: aprovar orcamento de emergencia #4421 pendente na diretoria.</p>
            <div className="stack-list">
              <span className="label">Chamados Relacionados</span>
              <div className="status-row">
                <span>#CH-1029 - Ruido anormal</span>
                <span className="small muted">Hoje, 08:30</span>
              </div>
              <div className="status-row">
                <span>#CH-1025 - Parada brusca</span>
                <span className="small muted">Ontem, 19:45</span>
              </div>
            </div>
            <button className="btn btn-danger" type="button">
              Aprovar Emergencia
            </button>
          </div>
        </Card>
      </div>

      <Card title="Acoes Rapidas" subtitle="Atalhos frequentes da administracao">
        <div className="quick-actions">
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <button className="quick-action" type="button" key={action.label}>
                <Icon size={22} />
                <span>{action.label}</span>
              </button>
            )
          })}
        </div>
      </Card>
    </div>
  )
}
