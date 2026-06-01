import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import KPICard from '../components/KPICard'
import './FraudDetection.css'

type RiskLevel = 'Low' | 'Medium' | 'High'

type ProductLine = {
  name: string
  category: string
  quantity: number
  unitPrice: number
}

type RiskOrder = {
  id: string
  customer: string
  customerEmail: string
  date: string
  status: string
  products: ProductLine[]
  shippingCountry: string
  billingCountry: string
  paymentMethod: string
  total: number
  riskScore: number
  riskLevel: RiskLevel
  riskReasons: string[]
}

type RiskSummary = {
  totalOrders: number
  highRisk: number
  mediumRisk: number
  lowRisk: number
  averageRiskScore: number
}

type RiskReport = {
  summary: RiskSummary
  orders: RiskOrder[]
}

type FraudDetectionState =
  | { status: 'loading' }
  | { status: 'ok'; report: RiskReport }
  | { status: 'error' }

const riskColors: Record<RiskLevel, string> = {
  Low: '#10b981',
  Medium: '#f59e0b',
  High: '#ef4444',
}

function FraudDetection() {
  const [state, setState] = useState<FraudDetectionState>({ status: 'loading' })

  useEffect(() => {
    let cancelled = false

    fetch('/api/order-risk')
      .then((r) => {
        if (!r.ok) throw new Error('Failed to fetch order risk report')
        return r.json() as Promise<RiskReport>
      })
      .then((report) => {
        if (!cancelled) setState({ status: 'ok', report })
      })
      .catch(() => {
        if (!cancelled) setState({ status: 'error' })
      })

    return () => {
      cancelled = true
    }
  }, [])

  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const formatDate = (value: string): string =>
    new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${value}T00:00:00`))

  const formatNumber = (value: number): string =>
    new Intl.NumberFormat('en-US').format(value)

  function renderContent() {
    if (state.status === 'loading') {
      return <p className="fraud-detection-status">Loading fraud signals…</p>
    }

    if (state.status === 'error') {
      return (
        <p className="fraud-detection-status fraud-detection-status--error">
          Failed to load fraud detection data. Please refresh.
        </p>
      )
    }

    const { summary, orders } = state.report
    const riskDistribution = [
      { level: 'Low', orders: summary.lowRisk, fill: riskColors.Low },
      { level: 'Medium', orders: summary.mediumRisk, fill: riskColors.Medium },
      { level: 'High', orders: summary.highRisk, fill: riskColors.High },
    ]

    return (
      <>
        <div className="fraud-detection-kpi-grid">
          <KPICard title="Total Orders" value={formatNumber(summary.totalOrders)} />
          <KPICard title="High Risk" value={formatNumber(summary.highRisk)} />
          <KPICard title="Medium Risk" value={formatNumber(summary.mediumRisk)} />
          <KPICard title="Avg Risk Score" value={summary.averageRiskScore.toFixed(1)} />
        </div>

        <section className="fraud-detection-section">
          <h2>Risk Distribution</h2>
          <div className="fraud-detection-chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={riskDistribution} margin={{ top: 8, right: 24, left: 16, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="level" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} allowDecimals={false} />
                <Tooltip
                  formatter={(value) => [typeof value === 'number' ? formatNumber(value) : value, 'Orders']}
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Bar dataKey="orders" radius={[4, 4, 0, 0]}>
                  {riskDistribution.map((entry) => (
                    <Cell key={entry.level} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="fraud-detection-section">
          <h2>Scored Orders</h2>
          <div className="fraud-detection-table-wrap">
            <table className="fraud-detection-table">
              <thead>
                <tr>
                  <th>Order</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Products</th>
                  <th>Total</th>
                  <th>Risk</th>
                  <th>Reasons</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td className="fraud-detection-order-id">{order.id}</td>
                    <td>
                      <span className="fraud-detection-customer">{order.customer}</span>
                      <span className="fraud-detection-customer-email">{order.customerEmail}</span>
                    </td>
                    <td>{formatDate(order.date)}</td>
                    <td>
                      {order.products.map((product) => (
                        <span className="fraud-detection-product" key={`${order.id}-${product.name}`}>
                          {product.quantity}× {product.name}
                        </span>
                      ))}
                    </td>
                    <td>{formatCurrency(order.total)}</td>
                    <td>
                      <span className={`fraud-detection-risk fraud-detection-risk--${order.riskLevel.toLowerCase()}`}>
                        {order.riskLevel} · {order.riskScore}
                      </span>
                    </td>
                    <td>
                      <div className="fraud-detection-reasons">
                        {order.riskReasons.length === 0 ? (
                          <span className="fraud-detection-reason fraud-detection-reason--empty">No signals</span>
                        ) : (
                          order.riskReasons.map((reason) => (
                            <span className="fraud-detection-reason" key={`${order.id}-${reason}`}>
                              {reason}
                            </span>
                          ))
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </>
    )
  }

  return (
    <main className="fraud-detection-page">
      <h1>Fraud Detection</h1>
      {renderContent()}
    </main>
  )
}

export default FraudDetection
