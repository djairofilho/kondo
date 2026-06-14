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
  kanban: "Kanban operacional",
  tickets: "Chamados inteligentes",
  finance: "Financeiro e pagamentos",
  agreements: "Inadimplência e acordos",
  documents: "Documentos e regras",
  announcements: "Comunicados",
  portal: "Portal do morador",
}

export default function App() {
  const [view, setView] = useState<View>("dashboard")
  const [condoName, setCondoName] = useState("Kondo")

  useEffect(() => {
    let active = true
    getDashboard().then((payload) => {
      if (active) {
        setCondoName(payload.condo_name)
      }
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
      {view === "documents" && <Documents />}
      {view === "announcements" && <Announcements />}
      {view === "portal" && <ResidentPortal />}
    </AppShell>
  )
}

