import { useState } from "react"
import { AppShell, type View } from "./components/AppShell"
import { Agreements } from "./views/Agreements"
import { Announcements } from "./views/Announcements"
import { Dashboard } from "./views/Dashboard"
import { Documents } from "./views/Documents"
import { Finance } from "./views/Finance"
import { Kanban } from "./views/Kanban"
import { ResidentPortal } from "./views/ResidentPortal"
import { Tickets } from "./views/Tickets"

const titles: Record<View, string> = {
  dashboard: "Dashboard",
  tickets: "Chamados",
  kanban: "Kanban operacional",
  finance: "Financeiro",
  agreements: "Inadimplencia e acordos",
  documents: "Documentos",
  announcements: "Comunicados",
  portal: "Portal do morador",
}

export default function App() {
  const [view, setView] = useState<View>("dashboard")

  return (
    <AppShell
      view={view}
      activeTitle={titles[view]}
      condoName="Condominio Edificio Horizon"
      onNavigate={(next) => setView(next)}
    >
      {view === "dashboard" && <Dashboard />}
      {view === "tickets" && <Tickets />}
      {view === "kanban" && <Kanban />}
      {view === "finance" && <Finance />}
      {view === "agreements" && <Agreements />}
      {view === "documents" && <Documents />}
      {view === "announcements" && <Announcements />}
      {view === "portal" && <ResidentPortal />}
    </AppShell>
  )
}
