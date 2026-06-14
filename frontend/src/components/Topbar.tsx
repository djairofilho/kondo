import { Bell, CircleHelp, Search, User } from "lucide-react"

type TopbarProps = {
  condoName: string
  title: string
}

export function Topbar({ condoName, title }: TopbarProps) {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <p className="eyebrow">Kondo Operacional</p>
        <h2>{title}</h2>
        <p>{condoName}</p>
      </div>
      <div className="topbar-right">
        <label className="search">
          <Search size={16} />
          <span>Buscar chamado, documento ou unidade</span>
          <input aria-label="Busca rápida" placeholder="Buscar..." />
        </label>
        <button type="button" aria-label="Notificações" title="Notificações">
          <Bell size={18} />
        </button>
        <button type="button" aria-label="Central de ajuda" title="Central de ajuda">
          <CircleHelp size={18} />
        </button>
        <button type="button" className="user-avatar" aria-label="Perfil" title="Perfil">
          <User size={16} />
          <span>João</span>
        </button>
      </div>
    </header>
  )
}

