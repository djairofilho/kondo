import type { ReactNode } from "react"
import { Card } from "./Card"

type MetricCardProps = {
  label: string
  value: string
  note?: ReactNode
  children?: ReactNode
}

export function MetricCard({ label, value, note, children }: MetricCardProps) {
  return (
    <Card title={label} className="metric-card">
      {children ? <div className="metric-icon">{children}</div> : null}
      <p className="metric-value">{value}</p>
      {note && <p className="metric-note">{note}</p>}
    </Card>
  )
}
