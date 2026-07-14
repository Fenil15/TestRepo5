import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Customers from './pages/Customers'
import Dashboard from './pages/Dashboard'
import FraudDetection from './pages/FraudDetection'
import RecentOrders from './pages/RecentOrders'
import Settings from './pages/Settings'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="customers" element={<Customers />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="fraud-detection" element={<FraudDetection />} />
        <Route path="recent-orders" element={<RecentOrders />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
