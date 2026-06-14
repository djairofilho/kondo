import { Megaphone, PenLine, Send } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { generateAnnouncement, listAnnouncements, postAnnouncement } from "../services/mockApi"
import type { Announcement } from "../data/announcements"

export function Announcements() {
  const [draft, setDraft] = useState("Informamos que a garagem B2 estara parcialmente isolada para reparo emergencial")
  const [tone, setTone] = useState<"formal" | "informal" | "urgente">("formal")
  const [loading, setLoading] = useState(true)
  const [generated, setGenerated] = useState<{ title: string; body: string; status: string } | null>(null)
  const [announcements, setAnnouncements] = useState<Announcement[]>([])
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let active = true
    listAnnouncements().then((payload) => {
      if (!active) return
      setAnnouncements(payload)
      setLoading(false)
    })
    return () => {
      active = false
    }
  }, [])

  async function runGenerator() {
    const result = await generateAnnouncement({ draft, tone })
    setGenerated(result)
  }

  async function save() {
    if (!generated) return
    setSaving(true)
    const posted = await postAnnouncement({
      title: generated.title,
      body: generated.body,
      audience: "Todos os moradores",
      date: new Date().toISOString(),
      status: "publicado",
    })
    setAnnouncements((prev) => [posted, ...prev])
    setSaving(false)
  }

  return (
    <div className="view-stack">
      <SectionHeader title="Comunicados" description="Escreva, gere com IA e publique com transparência." />

      <Card title="Rascunho operacional" subtitle="Prompt do comunicado">
        <label htmlFor="tone">Tom:</label>
        <select id="tone" value={tone} onChange={(event) => setTone(event.target.value as "formal" | "informal" | "urgente")}>
          <option value="formal">Formal</option>
          <option value="informal">Informal</option>
          <option value="urgente">Urgente</option>
        </select>
        <label htmlFor="draft">Texto base</label>
        <textarea id="draft" value={draft} onChange={(event) => setDraft(event.target.value)} />
        <div className="action-row">
          <button type="button" className="btn btn-primary" onClick={runGenerator}>
            <Megaphone size={16} />
            Gerar com IA
          </button>
        </div>

        {generated ? (
          <div className="preview">
            <h4>
              <PenLine size={16} /> Preview
            </h4>
            <p>
              <strong>{generated.title}</strong>
            </p>
            <p>{generated.body}</p>
            <button className="btn btn-outline" type="button" onClick={save} disabled={saving}>
              <Send size={16} />
              {saving ? "Salvando..." : "Publicar comunicado"}
            </button>
          </div>
        ) : null}
      </Card>

      <Card title="Comunicados publicados" subtitle="Historico recente">
        {loading ? (
          <p className="muted">Carregando...</p>
        ) : (
          announcements.map((item) => (
            <article key={item.id} className="announcement-item">
              <h4>{item.title}</h4>
              <p>{item.body}</p>
              <div className="muted">
                {item.audience} • {item.status} • {item.created_at}
              </div>
            </article>
          ))
        )}
      </Card>
    </div>
  )
}
