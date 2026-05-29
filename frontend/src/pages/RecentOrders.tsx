import { recentOrders } from '../data/mockEcommerce'
import './RecentOrders.css'

function RecentOrders() {
  const formatCurrency = (value: number): string =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)

  const formatDate = (value: string): string =>
    new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(`${value}T00:00:00`))

  return (
    <main className="recent-orders-page">
      <h1>Recent Orders</h1>

      <section className="recent-orders-section">
        <div className="recent-orders-table-wrap">
          <table className="recent-orders-table">
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
                  <td className="recent-orders-id">{order.id}</td>
                  <td>{order.customer}</td>
                  <td>{formatDate(order.date)}</td>
                  <td>
                    <span className={`recent-orders-status recent-orders-status-${order.status.toLowerCase()}`}>
                      {order.status}
                    </span>
                  </td>
                  <td>{order.items}</td>
                  <td>{formatCurrency(order.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  )
}

export default RecentOrders
