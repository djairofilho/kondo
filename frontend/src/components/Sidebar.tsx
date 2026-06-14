import { Building2 } from "lucide-react"
import type { MenuItem } from "../navigation/menu"
import { menuItems } from "../navigation/menu"
import type { View } from "./AppShell"

export type SidebarProps = {
  active: View
  onNavigate: (view: View) => void
}

export function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand-lockup">
        <span className="brand-mark" aria-hidden="true">
          <Building2 size={20} />
        </span>
        <div>
          <strong>Kondo</strong>
          <span>Administracao</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Navegacao principal">
        {menuItems.map((item: MenuItem) => {
          const activeItem = active === item.key
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onNavigate(item.key)}
              className={activeItem ? "item active" : "item"}
              aria-current={activeItem ? "page" : undefined}
              title={item.label}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
