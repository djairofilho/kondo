import { BookOpenText, BotMessageSquare, Search } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { askDocumentQuestion, listDocuments } from "../services/mockApi"
import type { DocumentItem } from "../data/documents"

export function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [question, setQuestion] = useState("Pode fazer obra com ruído?")
  const [answer, setAnswer] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [source, setSource] = useState<string>("")

  useEffect(() => {
    let active = true
    listDocuments().then((payload) => {
      if (!active) return
      setDocuments(payload)
      setLoading(false)
    })
    return () => {
      active = false
    }
  }, [])

  async function ask() {
    if (!question.trim()) return
    const result = await askDocumentQuestion({ question })
    setSource(result.source)
    setAnswer(result.answer)
  }

  return (
    <div className="view-stack">
      <SectionHeader title="Documentos" description="Regras, regimento e comunicações oficiais." />

      <div className="grid-2">
        <Card title="Documentos do condomínio" subtitle="Acesso rápido por documento">
          <div className="documents-list">
            {loading ? (
              <p className="muted">Carregando...</p>
            ) : (
              documents.map((doc) => (
                <article key={doc.id} className="doc-item">
                  <h4>{doc.title}</h4>
                  <p>{doc.summary}</p>
                  <div className="muted">
                    {doc.document_type} • status {doc.status} • atualizado {doc.updated_at}
                  </div>
                </article>
              ))
            )}
          </div>
        </Card>

        <Card title="Perguntas rápidas por IA" subtitle="Consulta contextual com evidência">
          <label htmlFor="question">
            <span className="label-inline">
              <Search size={14} />
              Pergunta
            </span>
          </label>
          <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button type="button" className="btn btn-primary" onClick={ask}>
            <BotMessageSquare size={16} />
            Consultar IA
          </button>

          {answer ? (
            <div className="qa">
              <h4>
                <BookOpenText size={16} />
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

