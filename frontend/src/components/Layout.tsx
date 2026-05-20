import { NavLink, Outlet } from 'react-router-dom'
import './Layout.css'

function Layout() {
  return (
    <>
      <nav className="nav">
        <NavLink to="/" end>
          Home
        </NavLink>
        <NavLink to="/customers">Manage Customers</NavLink>
      </nav>
      <div className="layout-content">
        <Outlet />
      </div>
    </>
  )
}

export default Layout
