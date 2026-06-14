import { Bell, Menu, Search, Settings, UserRound } from "lucide-react"

type TopbarProps = {
  condoName: string
  title: string
}

export function Topbar({ condoName, title }: TopbarProps) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <button className="icon-button mobile-menu-trigger" type="button" aria-label="Abrir menu">
          <Menu size={20} />
        </button>
        <div>
          <p>{title}</p>
          <h2>{condoName}</h2>
        </div>
      </div>

      <label className="global-search">
        <Search size={18} />
        <span className="sr-only">Busca rapida</span>
        <input placeholder="Buscar chamado, documento ou unidade" />
      </label>

      <div className="topbar-actions">
        <button type="button" className="icon-button notification-button" aria-label="Notificacoes">
          <Bell size={18} />
          <span aria-hidden="true" />
        </button>
        <button type="button" className="icon-button" aria-label="Configuracoes">
          <Settings size={18} />
        </button>
        <button type="button" className="user-chip" aria-label="Perfil do usuario">
          <UserRound size={16} />
          <span>Joao</span>
        </button>
      </div>
    </header>
  )
}
