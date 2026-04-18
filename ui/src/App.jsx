import React, { useState, useEffect } from 'react'
import Login from './components/Login'
import Chat from './components/Chat'

const KEY = 'support_auth'

export default function App() {
  const [auth, setAuth] = useState(null)

  useEffect(() => {
    try {
      const stored = localStorage.getItem(KEY)
      if (stored) setAuth(JSON.parse(stored))
    } catch {
      localStorage.removeItem(KEY)
    }
  }, [])

  const handleLogin = (data) => {
    localStorage.setItem(KEY, JSON.stringify(data))
    setAuth(data)
  }

  const handleLogout = () => {
    localStorage.removeItem(KEY)
    setAuth(null)
  }

  return auth
    ? <Chat auth={auth} onLogout={handleLogout} />
    : <Login onLogin={handleLogin} />
}
