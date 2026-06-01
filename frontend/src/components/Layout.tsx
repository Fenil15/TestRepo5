import { NavLink, Outlet } from 'react-router-dom'
import './Layout.css'

function Layout() {
  return (
    <>
      <nav className="nav">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/recent-orders">Recent Orders</NavLink>
        <NavLink to="/fraud-detection">Fraud Detection</NavLink>
        <NavLink to="/customers">Manage Customers</NavLink>
      </nav>
      <div className="layout-content">
        <Outlet />
      </div>
    </>
  )
}

export default Layout
