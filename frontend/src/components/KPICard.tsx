import './KPICard.css'

type KPICardProps = {
  title: string
  value: string
  subtitle?: string
}

function KPICard({ title, value, subtitle }: KPICardProps) {
  return (
    <div className="kpi-card">
      <p className="kpi-card__title">{title}</p>
      <p className="kpi-card__value">{value}</p>
      {subtitle && <p className="kpi-card__subtitle">{subtitle}</p>}
    </div>
  )
}

export default KPICard
