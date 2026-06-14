import { Bot, History, Mail, Megaphone, Save, Send, Smartphone } from "lucide-react"
import { useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"

const history = [
  ["Assembleia Geral Ordinaria", "Todos os Moradores", "12/10/2023 14:30", "Enviado"],
  ["Limpeza da Caixa D'agua", "Bloco A e B", "10/10/2023 09:00", "Enviado"],
  ["Novas Regras Academia", "Todos os Moradores", "05/10/2023 16:45", "Rascunho"],
]

export function Announcements() {
  const [title, setTitle] = useState("Manutencao preventiva no elevador")
  const [draft, setDraft] = useState("Informar moradores do Bloco B sobre parada do elevador social amanha das 14h as 16h.")
  const [tone, setTone] = useState("Formal")
  const [generated, setGenerated] = useState(false)

  return (
    <div className="view-stack">
      <SectionHeader title="Comunicados" description="Gerencie e envie comunicados para os moradores." />

      <div className="grid-2">
        <div className="view-stack">
          <Card title="Novo Comunicado" subtitle="Crie um rascunho ou gere texto com IA">
            <div className="form-grid">
              <label>
                Titulo do Comunicado
                <input value={title} onChange={(event) => setTitle(event.target.value)} />
              </label>
              <label>
                Texto Base / Topicos
                <textarea value={draft} maxLength={500} onChange={(event) => setDraft(event.target.value)} />
              </label>
              <label>
                Tom de Voz (IA)
                <div className="action-row">
                  {["Formal", "Informativo", "Urgente"].map((item) => (
                    <button
                      key={item}
                      className={tone === item ? "btn btn-primary" : "btn btn-outline"}
                      type="button"
                      onClick={() => setTone(item)}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </label>
              <button className="btn btn-primary" type="button" onClick={() => setGenerated(true)}>
                <Bot size={16} />
                Gerar com IA
              </button>
            </div>
          </Card>

          <Card
            title="Historico Recente"
            subtitle="Comunicados publicados e rascunhos"
          >
            <div className="status-row">
              <History size={16} />
              <span className="muted">Ultimos envios</span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Titulo</th>
                    <th>Audiencia</th>
                    <th>Data</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map(([itemTitle, audience, date, status]) => (
                    <tr key={itemTitle}>
                      <td>{itemTitle}</td>
                      <td>{audience}</td>
                      <td>{date}</td>
                      <td>
                        <Badge tone={status === "Enviado" ? "paid" : "neutral"}>{status}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        <Card className="sticky-panel" title="Preview" subtitle="Visualizacao celular">
          <div className="action-row">
            <button className="btn btn-primary" type="button">
              <Smartphone size={14} />
              Celular
            </button>
            <button className="btn btn-outline" type="button">
              <Mail size={14} />
              Email
            </button>
          </div>
          <div className="preview-phone">
            <div className="phone-top">
              <div className="status-row">
                <Megaphone size={18} />
                <strong>Kondo Admin</strong>
                <span className="small">Agora</span>
              </div>
            </div>
            <div className="phone-body">
              {generated ? (
                <>
                  <h3>{title}</h3>
                  <p>
                    Prezados moradores, informamos que {draft.toLowerCase()} Agradecemos a compreensao e reforcamos que
                    a equipe permanecera disponivel durante o periodo.
                  </p>
                  <Badge tone="medium">{tone}</Badge>
                </>
              ) : (
                <p className="muted">O conteudo gerado aparecera aqui.</p>
              )}
            </div>
          </div>
          <label>
            Audiencia
            <select>
              <option>Todos os Moradores</option>
              <option>Bloco A e B</option>
              <option>Conselho</option>
            </select>
          </label>
          <div className="action-row">
            <button className="btn btn-outline" type="button">
              <Save size={16} />
              Salvar
            </button>
            <button className="btn btn-primary" type="button">
              <Send size={16} />
              Publicar
            </button>
          </div>
        </Card>
      </div>
    </div>
  )
}
