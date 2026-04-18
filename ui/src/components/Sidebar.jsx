import React from 'react'

function timeAgo(isoStr) {
  if (!isoStr) return ''
  const diff = Date.now() - new Date(isoStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1)  return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export default function Sidebar({
  username, sessions, activeSessionId,
  onSelect, onNew, onLogout, loading,
}) {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sb-brand">
        <span className="sb-brand-icon">🛒</span>
        <div>
          <div className="sb-brand-name">ShopSupport</div>
          <div className="sb-brand-sub">AI Assistant</div>
        </div>
      </div>

      {/* New chat */}
      <button className="sb-new-btn" onClick={onNew} disabled={loading}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        New Chat
      </button>

      {/* Sessions */}
      <div className="sb-sessions-label">Recent conversations</div>
      <nav className="sb-sessions">
        {sessions.length === 0 && (
          <div className="sb-empty">No previous chats</div>
        )}
        {sessions.map((s) => (
          <button
            key={s.session_id}
            className={`sb-session ${s.session_id === activeSessionId ? 'active' : ''}`}
            onClick={() => onSelect(s.session_id)}
          >
            <span className="sb-session-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </span>
            <span className="sb-session-body">
              <span className="sb-session-title">{s.title || 'New Chat'}</span>
              <span className="sb-session-time">{timeAgo(s.created_at)}</span>
            </span>
          </button>
        ))}
      </nav>

      {/* User footer */}
      <div className="sb-footer">
        <div className="sb-user">
          <div className="sb-avatar">{username[0].toUpperCase()}</div>
          <span className="sb-username">{username}</span>
        </div>
        <button className="sb-logout" onClick={onLogout} title="Sign out">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </div>
    </aside>
  )
}
