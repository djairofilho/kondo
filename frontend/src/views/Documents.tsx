import { BotMessageSquare, Search, ShieldCheck } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { askDocumentQuestion, listDocuments } from "../services/mockApi"
import type { DocumentItem } from "../data/documents"

export function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [question, setQuestion] = useState("Pode fazer obra com barulho?")
  const [answer, setAnswer] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [source, setSource] = useState<string>("")
  const [selectedDoc, setSelectedDoc] = useState<number | null>(null)

  useEffect(() => {
    let active = true
    listDocuments().then((payload) => {
      if (!active) return
      setDocuments(payload)
      setSelectedDoc(payload[0]?.id ?? null)
      setLoading(false)
    })
    return () => {
      active = false
    }
  }, [])

  async function ask() {
    if (!question.trim()) return
    const result = await askDocumentQuestion({ question, document_id: selectedDoc ?? undefined })
    setSource(result.source)
    setAnswer(result.answer)
  }

  return (
    <div className="view-stack">
      <SectionHeader
        title="Documentos"
        description="Regras, atas e contratos com consulta por IA e rastreabilidade de evidência."
      />

      <div className="grid-2">
        <Card title="Documentos do condomínio" subtitle="Base normativa operacional">
          <div className="documents-list">
            {loading ? (
              <p className="muted">Carregando...</p>
            ) : (
              documents.map((doc) => (
                <button
                  key={doc.id}
                  type="button"
                  className={`doc-item ${selectedDoc === doc.id ? "active" : ""}`}
                  onClick={() => setSelectedDoc(doc.id)}
                >
                  <h4>{doc.title}</h4>
                  <p>{doc.summary}</p>
                  <div className="muted">
                    {doc.document_type} • status {doc.status} • atualizado {doc.updated_at}
                  </div>
                  <div className="muted small">
                    Fonte: {doc.source} • Evidência: {(doc.evidence_tags ?? []).join(", ")}
                  </div>
                </button>
              ))
            )}
          </div>
        </Card>

        <Card title="Perguntas rápidas por IA" subtitle="Consulta contextual com fonte de resposta">
          <label htmlFor="question">
            <span className="label-inline">
              <Search size={14} />
              Pergunta
            </span>
          </label>
          <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button className="btn btn-primary" type="button" onClick={ask}>
            <BotMessageSquare size={16} />
            Consultar IA
          </button>
          {answer ? (
            <div className="qa">
              <h4>
                <ShieldCheck size={16} />
                Resposta da IA
              </h4>
              <p>{answer}</p>
              <p className="muted small">Fonte: {source}</p>
            </div>
          ) : (
            <p className="muted">Sem resposta ainda.</p>
          )}
        </Card>
      </div>
    </div>
  )
}

