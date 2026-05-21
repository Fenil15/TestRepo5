import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Customers from './pages/Customers'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="customers" element={<Customers />} />
        <Route path="dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  )
}

export default App
