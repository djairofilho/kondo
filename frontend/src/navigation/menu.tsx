import { ClipboardList, CreditCard, FileText, KanbanSquare, LayoutDashboard, Megaphone, Ticket, UserCircle2 } from "lucide-react"
import type { ReactNode } from "react"
import type { View } from "../components/AppShell"

export type MenuItem = { key: View; label: string; icon: ReactNode }

export const menuItems: MenuItem[] = [
  { key: "dashboard", label: "Dashboard", icon: <LayoutDashboard size={18} /> },
  { key: "tickets", label: "Chamados", icon: <Ticket size={18} /> },
  { key: "kanban", label: "Kanban", icon: <KanbanSquare size={18} /> },
  { key: "finance", label: "Financeiro", icon: <CreditCard size={18} /> },
  { key: "agreements", label: "Inadimplencia e Acordos", icon: <ClipboardList size={18} /> },
  { key: "documents", label: "Documentos", icon: <FileText size={18} /> },
  { key: "announcements", label: "Comunicados", icon: <Megaphone size={18} /> },
  { key: "portal", label: "Portal do Morador", icon: <UserCircle2 size={18} /> },
]
