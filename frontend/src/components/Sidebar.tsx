import type { MenuItem } from "../navigation/menu"
import type { View } from "./AppShell"

import { menuItems } from "../navigation/menu"

export type SidebarProps = {
  active: View
  onNavigate: (view: View) => void
  compact?: boolean
}

export function Sidebar({ active, onNavigate, compact = false }: SidebarProps) {
  return (
    <aside className={`sidebar ${compact ? "sidebar-compact" : ""}`}>
      {!compact ? <div className="brand">Kondo</div> : null}
      <nav className="sidebar-nav" aria-label="Navegação principal">
        {menuItems.map((item: MenuItem) => (
          <button
            key={item.key}
            onClick={() => onNavigate(item.key)}
            className={active === item.key ? "item active" : "item"}
            type="button"
            aria-current={active === item.key ? "page" : undefined}
            title={item.label}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
