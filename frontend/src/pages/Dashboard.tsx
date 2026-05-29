import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { kpiTotals, monthlyRevenue, ordersByCategory } from '../data/mockEcommerce'
import KPICard from '../components/KPICard'
import './Dashboard.css'

function Dashboard() {
  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const formatNumber = (value: number): string =>
    new Intl.NumberFormat('en-US').format(value)

  const formatYAxisDollar = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

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

      <div className="dashboard-charts">
        <div className="chart-section">
          <h2>Revenue Trend</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyRevenue} margin={{ top: 8, right: 24, left: 16, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis tickFormatter={formatYAxisDollar} stroke="#94a3b8" tick={{ fill: '#94a3b8' }} width={80} />
                <Tooltip
                  formatter={(value) => [typeof value === 'number' ? formatYAxisDollar(value) : value, 'Revenue']}
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={{ fill: '#6366f1', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-section">
          <h2>Orders by Category</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ordersByCategory} margin={{ top: 8, right: 24, left: 16, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="category" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <Tooltip
                  formatter={(value) => [typeof value === 'number' ? formatNumber(value) : value, 'Orders']}
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Legend wrapperStyle={{ color: '#94a3b8' }} />
                <Bar dataKey="orders" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </main>
  )
}

export default Dashboard
