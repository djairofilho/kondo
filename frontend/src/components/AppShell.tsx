import type { ReactNode } from "react"
import { menuItems } from "../navigation/menu"
import { Sidebar } from "./Sidebar"
import { Topbar } from "./Topbar"

export type View =
  | "dashboard"
  | "kanban"
  | "tickets"
  | "finance"
  | "agreements"
  | "documents"
  | "announcements"
  | "portal"

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

      <nav className="mobile-nav" aria-label="Navegacao principal mobile">
        {menuItems.map((item) => {
          const active = view === item.key
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onNavigate(item.key)}
              className={active ? "mobile-nav-item active" : "mobile-nav-item"}
              aria-current={active ? "page" : undefined}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}
