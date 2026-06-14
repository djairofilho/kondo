import { Bot, Download, ExternalLink, FileUp, Gavel, MoreVertical, Search, ShieldCheck } from "lucide-react"
import { useState } from "react"

import { Badge } from "../components/Badge"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"

const docs = [
  ["Regimento Interno 2023", "Regras", "Vigente", "15/08/2023", "Regras de convivencia e areas comuns."],
  ["Ata Assembleia Marco", "Ata", "Registrado", "10/03/2023", "Aprovacao de contas e previsao orcamentaria."],
  ["Convencao Condominial", "Legal", "Vigente", "05/01/2015", "Normas juridicas e deveres do condominio."],
  ["Apolice de Seguro", "Seguro", "Renovacao Pendente", "20/01/2024", "Cobertura patrimonial e civil."],
]

export function Documents() {
  const [question, setQuestion] = useState("Pode usar churrasqueira depois das 22h?")
  const [asked, setAsked] = useState(true)

  return (
    <div className="view-stack">
      <SectionHeader
        title="Documentos"
        description="Gestao e consulta inteligente de arquivos do condominio."
        action={
          <button className="btn btn-primary" type="button">
            <FileUp size={16} />
            Enviar Documento
          </button>
        }
      />

      <Card title="Consulta Inteligente (IA)" className="ai-panel">
        <div className="form-grid">
          <label>
            Pergunta
            <div className="status-row">
              <Search size={16} />
              <input value={question} onChange={(event) => setQuestion(event.target.value)} />
              <button className="btn btn-primary" type="button" onClick={() => setAsked(true)}>
                Consultar
              </button>
            </div>
          </label>
          {asked ? (
            <div className="field">
              <div className="status-row">
                <ShieldCheck size={16} />
                <strong>Resposta com evidencia</strong>
                <Badge tone="paid">97% confianca</Badge>
              </div>
              <p>
                A churrasqueira deve encerrar o uso sonoro as 22h. Eventos podem permanecer ate 23h apenas com volume
                baixo e reserva confirmada.
              </p>
              <p className="small muted">Linha de Evidencia: Regimento Interno (2023), capitulo de areas comuns.</p>
              <button className="btn btn-outline" type="button">
                Ver documento original
                <ExternalLink size={14} />
              </button>
            </div>
          ) : null}
        </div>
      </Card>

      <Card title="Repositorio" subtitle="Mostrando 1-4 de 42 documentos">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Titulo / Resumo</th>
                <th>Tipo</th>
                <th>Status</th>
                <th>Atualizado em</th>
                <th className="text-right">Acoes</th>
              </tr>
            </thead>
            <tbody>
              {docs.map(([title, type, status, updated, summary]) => (
                <tr key={title}>
                  <td>
                    <strong>{title}</strong>
                    <p className="small muted">{summary}</p>
                  </td>
                  <td>
                    <Badge tone="neutral">
                      <Gavel size={12} />
                      {type}
                    </Badge>
                  </td>
                  <td>
                    <Badge tone={status.includes("Pendente") ? "pending" : "paid"}>{status}</Badge>
                  </td>
                  <td>{updated}</td>
                  <td className="text-right">
                    <button className="icon-button" type="button" aria-label={`Baixar ${title}`}>
                      <Download size={16} />
                    </button>
                    <button className="icon-button" type="button" aria-label={`Mais opcoes para ${title}`}>
                      <MoreVertical size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Base de Evidencias" subtitle="Fontes citadas pelo assistente">
        <div className="documents-list">
          <div className="doc-item">
            <div className="status-row">
              <Bot size={16} />
              <strong>Regimento Interno (2023)</strong>
              <Badge tone="neutral">documento oficial</Badge>
            </div>
            <p>Trechos citados sempre devem indicar documento, secao e data de atualizacao.</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
