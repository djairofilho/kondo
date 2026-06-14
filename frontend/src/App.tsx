import { useEffect, useState } from "react"
import { AppShell, type View } from "./components/AppShell"
import { Dashboard } from "./views/Dashboard"
import { Kanban } from "./views/Kanban"
import { Tickets } from "./views/Tickets"
import { Finance } from "./views/Finance"
import { Agreements } from "./views/Agreements"
import { ResidentPortal } from "./views/ResidentPortal"
import { Documents } from "./views/Documents"
import { Announcements } from "./views/Announcements"
import { getDashboard } from "./services/mockApi"

const titles: Record<View, string> = {
  dashboard: "Dashboard operacional",
  kanban: "Kanban",
  tickets: "Chamados",
  finance: "Financeiro e pagamentos",
  agreements: "Inadimplência e acordos",
  portal: "Portal do morador",
  documents: "Documentos IA",
  announcements: "Comunicados",
}

export default function App() {
  const [view, setView] = useState<View>("dashboard")
  const [condoName, setCondoName] = useState("Kondo")

  useEffect(() => {
    let active = true
    getDashboard().then((payload) => {
      if (!active) return
      setCondoName(payload.condo_name)
    })
    return () => {
      active = false
    }
  }, [])

  return (
    <AppShell view={view} activeTitle={titles[view]} condoName={condoName} onNavigate={(next) => setView(next)}>
      {view === "dashboard" && <Dashboard />}
      {view === "kanban" && <Kanban />}
      {view === "tickets" && <Tickets />}
      {view === "finance" && <Finance />}
      {view === "agreements" && <Agreements />}
      {view === "portal" && <ResidentPortal />}
      {view === "documents" && <Documents />}
      {view === "announcements" && <Announcements />}
    </AppShell>
  )
}

