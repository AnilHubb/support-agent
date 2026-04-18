import React, { useState } from 'react'
import { api } from '../api'

const DEMO = [
  { username: 'alice',   password: 'alice123' },
  { username: 'bob',     password: 'bob123' },
  { username: 'charlie', password: 'charlie123' },
]

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.')
      return
    }
    setLoading(true)
    setError('')
    try {
      onLogin(await api.login(username.trim(), password))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">🛒</div>
          <h1>Customer Support</h1>
          <p>Sign in to get help with your orders</p>
        </div>

        <form onSubmit={submit} noValidate>
          {error && (
            <div className="error-banner">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {error}
            </div>
          )}

          <div className="field">
            <label htmlFor="u">Username</label>
            <input
              id="u" type="text" autoComplete="username"
              placeholder="Enter your username"
              value={username} onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="field">
            <label htmlFor="p">Password</label>
            <input
              id="p" type="password" autoComplete="current-password"
              placeholder="Enter your password"
              value={password} onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? <span className="spin" /> : 'Sign In'}
          </button>
        </form>

        <div className="demo-section">
          <p className="demo-title">Demo accounts — click to fill</p>
          <div className="demo-chips">
            {DEMO.map((d) => (
              <button
                key={d.username}
                type="button"
                className="demo-chip"
                onClick={() => { setUsername(d.username); setPassword(d.password); setError('') }}
              >
                {d.username}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
