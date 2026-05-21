import { kpiTotals } from '../data/mockEcommerce'
import KPICard from '../components/KPICard'
import './Dashboard.css'

function Dashboard() {
  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const formatNumber = (value: number): string =>
    new Intl.NumberFormat('en-US').format(value)

  return (
    <main className="dashboard-page">
      <h1>Dashboard</h1>
      <div className="dashboard-kpi-grid">
        <KPICard title="Revenue" value={formatCurrency(kpiTotals.revenue)} />
        <KPICard title="Orders" value={formatNumber(kpiTotals.orders)} />
        <KPICard title="Customers" value={formatNumber(kpiTotals.customers)} />
        <KPICard
          title="Avg Order Value"
          value={new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(kpiTotals.averageOrderValue)}
        />
      </div>
    </main>
  )
}

export default Dashboard
