import type { ReactNode } from "react"

type CardProps = {
  title?: string
  subtitle?: string
  children: ReactNode
  className?: string
}

export function Card({ title, subtitle, children, className = "" }: CardProps) {
  return (
    <section className={`k-card ${className}`}>
      {(title || subtitle) && (
        <header className="k-card-head">
          {title && <h3>{title}</h3>}
          {subtitle && <p>{subtitle}</p>}
        </header>
      )}
      <div>{children}</div>
    </section>
  )
}
