import type { ReactNode } from "react"
import { Sidebar } from "./Sidebar"
import { Topbar } from "./Topbar"

export type View =
  | "dashboard"
  | "kanban"
  | "tickets"
  | "finance"
  | "agreements"
  | "portal"
  | "documents"
  | "announcements"

type AppShellProps = {
  view: View
  activeTitle: string
  onNavigate: (view: View) => void
  children: ReactNode
  condoName: string
}

export function AppShell({ view, activeTitle, onNavigate, children, condoName }: AppShellProps) {
  return (
    <div className="app-shell">
      <Sidebar active={view} onNavigate={onNavigate} />
      <div className="content">
        <Topbar condoName={condoName} title={activeTitle} />
        <main className="view-area">{children}</main>
      </div>
    </div>
  )
}
