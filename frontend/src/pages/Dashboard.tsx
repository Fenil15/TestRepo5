import { useState } from 'react'
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
import { kpiTotals, monthlyRevenue, ordersByCategory, recentOrders } from '../data/mockEcommerce'
import KPICard from '../components/KPICard'
import './Dashboard.css'

type DashboardTab = 'overview' | 'recent-orders'

function Dashboard() {
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview')

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const formatNumber = (value: number): string =>
    new Intl.NumberFormat('en-US').format(value)

  const formatYAxisDollar = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const formatDate = (value: string): string =>
    new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${value}T00:00:00`))

  return (
    <main className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard Left</h1>
        <div className="dashboard-tabs" role="tablist" aria-label="Dashboard sections">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'overview'}
            className={activeTab === 'overview' ? 'dashboard-tab dashboard-tab-active' : 'dashboard-tab'}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'recent-orders'}
            className={activeTab === 'recent-orders' ? 'dashboard-tab dashboard-tab-active' : 'dashboard-tab'}
            onClick={() => setActiveTab('recent-orders')}
          >
            Recent Orders
          </button>
        </div>
      </div>

      <div className="dashboard-kpi-grid">
        <KPICard title="Revenue" value={formatCurrency(kpiTotals.revenue)} />
        <KPICard title="Orders" value={formatNumber(kpiTotals.orders)} />
        <KPICard title="Customers" value={formatNumber(kpiTotals.customers)} />
        <KPICard
          title="Avg Order Value"
          value={new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(kpiTotals.averageOrderValue)}
        />
      </div>

      {activeTab === 'overview' ? (
        <div className="dashboard-charts" role="tabpanel">
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
      ) : (
        <section className="orders-section" role="tabpanel">
          <div className="orders-table-wrap">
            <table className="orders-table">
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Items</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {recentOrders.map((order) => (
                  <tr key={order.id}>
                    <td className="orders-id">{order.id}</td>
                    <td>{order.customer}</td>
                    <td>{formatDate(order.date)}</td>
                    <td>
                      <span className={`orders-status orders-status-${order.status.toLowerCase()}`}>{order.status}</span>
                    </td>
                    <td>{order.items}</td>
                    <td>{formatCurrency(order.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  )
}

export default Dashboard
