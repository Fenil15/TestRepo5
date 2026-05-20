import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Customers from './pages/Customers'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="customers" element={<Customers />} />
      </Route>
    </Routes>
  )
}

export default App
