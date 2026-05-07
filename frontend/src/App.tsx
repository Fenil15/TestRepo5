import { useEffect, useState } from 'react'
import './App.css'

type Status = 'loading' | 'ok' | 'error'

function App() {
  const [message, setMessage] = useState<string>('')
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    fetch('/api/hello')
      .then((r) => {
        if (!r.ok) throw new Error('non-ok')
        return r.json()
      })
      .then((data: { message: string }) => {
        setMessage(data.message)
        setStatus('ok')
      })
      .catch(() => setStatus('error'))
  }, [])

  return (
    <main>
      {status === 'loading' && <h1>Loading…</h1>}
      {status === 'ok' && <h1>{message}</h1>}
      {status === 'error' && <h1>Could not reach API</h1>}
    </main>
  )
}

export default App
