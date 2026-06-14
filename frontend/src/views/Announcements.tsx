import { Megaphone, PenLine, Send } from "lucide-react"
import { useEffect, useState } from "react"
import { Card } from "../components/Card"
import { SectionHeader } from "../components/SectionHeader"
import { generateAnnouncement, listAnnouncements, postAnnouncement, publishAnnouncement } from "../services/mockApi"
import type { Announcement } from "../data/announcements"

export function Announcements() {
  const [draft, setDraft] = useState("Informamos que a garagem B2 ficará parcialmente isolada para reparo emergencial.")
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
    setGenerated({
      title: result.title,
      body: result.body,
      status: result.status,
    })
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

  async function publish(itemId: number) {
    const updated = await publishAnnouncement(itemId)
    setAnnouncements((previous) => previous.map((entry) => (entry.id === itemId ? updated : entry)))
  }

  return (
    <div className="view-stack">
      <SectionHeader title="Comunicados" description="Rascunho, geração por IA e publicação no painel interno." />

      <Card title="Rascunho operacional" subtitle="Construa e gere com IA">
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
              {saving ? "Publicando..." : "Publicar comunicado"}
            </button>
          </div>
        ) : null}
      </Card>

      <Card title="Comunicados publicados" subtitle="Histórico recente">
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
              {item.status !== "publicado" ? (
                <button className="btn btn-outline" type="button" onClick={() => publish(item.id)}>
                  Publicar agora
                </button>
              ) : null}
            </article>
          ))
        )}
      </Card>
    </div>
  )
}

