import type { ReactNode } from "react"

type SectionHeaderProps = {
  title: string
  description?: string
  action?: ReactNode
}

export function SectionHeader({ title, description, action }: SectionHeaderProps) {
  return (
    <header className="section-header">
      <div>
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {action ? <div>{action}</div> : null}
    </header>
  )
}
