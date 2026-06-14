import { ClipboardList, CreditCard, FileText, LayoutDashboard, Megaphone, Ticket, UserCircle2, KanbanSquare } from "lucide-react"
import type { View } from "./AppShell"

type Menu = { key: View; label: string; icon: React.ReactNode }

type SidebarProps = {
  active: View
  onNavigate: (view: View) => void
}

const menu: Menu[] = [
  { key: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} /> },
  { key: "kanban", label: "Kanban", icon: <KanbanSquare size={18} /> },
  { key: "tickets", label: "Chamados", icon: <Ticket size={18} /> },
  { key: "finance", label: "Financeiro", icon: <CreditCard size={18} /> },
  { key: "agreements", label: "Acordos", icon: <ClipboardList size={18} /> },
  { key: "portal", label: "Portal do Morador", icon: <UserCircle2 size={18} /> },
  { key: "documents", label: "Documentos", icon: <FileText size={18} /> },
  { key: "announcements", label: "Comunicados", icon: <Megaphone size={18} /> },
]

export function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">Kondo</div>
      <nav>
        {menu.map((item) => (
          <button
            key={item.key}
            onClick={() => onNavigate(item.key)}
            className={active === item.key ? "item active" : "item"}
            type="button"
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
