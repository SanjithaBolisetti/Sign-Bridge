import { useEffect, useState } from 'react'
import { Link, Route, Routes } from 'react-router-dom'
import './App.css'
import SignToText from './pages/SignToText.jsx'

const HEALTH_URL = 'http://127.0.0.1:8000/health'

function Home() {
  const [status, setStatus] = useState({ label: 'Checking backend...', ok: null })

  useEffect(() => {
    let isMounted = true
    const checkHealth = async () => {
      try {
        const res = await fetch(HEALTH_URL)
        if (!res.ok) throw new Error('Bad status')
        const data = await res.json()
        if (isMounted) {
          const healthy = data?.status === 'healthy'
          setStatus({ label: healthy ? 'Backend Connected ✅' : 'Backend Not Connected ❌', ok: healthy })
        }
      } catch (err) {
        if (isMounted) setStatus({ label: 'Backend Not Connected ❌', ok: false })
      }
    }
    checkHealth()
    return () => {
      isMounted = false
    }
  }, [])

  const statusClass = status.ok === null ? 'status neutral' : status.ok ? 'status ok' : 'status fail'

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">SignBridge</p>
        <h1>SignBridge - AI Sign Language System</h1>
        <p className="subhead">Bridge sign and speech with a unified AI recognition and avatar pipeline.</p>

        <div className="actions">
          <Link to="/sign-to-text" className="primary">Sign to Text</Link>
          <Link to="/text-to-sign" className="ghost" aria-disabled="true">Text to Sign</Link>
        </div>

        <div className={statusClass}>{status.label}</div>
      </header>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/sign-to-text" element={<SignToText />} />
      <Route path="/text-to-sign" element={<Home />} />
    </Routes>
  )
}

export default App
