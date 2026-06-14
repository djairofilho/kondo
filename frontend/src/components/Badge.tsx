import type { ReactNode } from "react"

type Tone = "critical" | "high" | "medium" | "resolved" | "in_progress" | "paid" | "pending" | "neutral"

type BadgeProps = {
  children: ReactNode
  tone?: Tone
}

const toneClass: Record<Tone, string> = {
  critical: "critical",
  high: "high",
  medium: "medium",
  resolved: "resolved",
  in_progress: "in-progress",
  paid: "paid",
  pending: "pending",
  neutral: "neutral",
}

export function Badge({ children, tone = "medium" }: BadgeProps) {
  return <span className={`k-badge ${toneClass[tone]}`}>{children}</span>
}
