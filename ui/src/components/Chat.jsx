import React, { useState, useEffect, useRef, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import Sidebar from './Sidebar'
import { api } from '../api'

const WELCOME = (name) =>
  `Hi **${name}**! 👋 I'm your customer support assistant.\n\nI can help you with:\n- **Order tracking** and status updates\n- **Delivery estimates** and tracking numbers\n- **Delayed or missing orders**\n- **Cancellations** and order issues\n\nHow can I help you today?`

const SUGGESTIONS = [
  'Show all my orders',
  'Where is my order ORD-001?',
  'When will my order arrive?',
  'I have a delayed order',
]

function BotMessage({ content }) {
  return (
    <div className="msg-markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p:      ({ children }) => <p className="md-p">{children}</p>,
          ul:     ({ children }) => <ul className="md-ul">{children}</ul>,
          ol:     ({ children }) => <ol className="md-ol">{children}</ol>,
          li:     ({ children }) => <li className="md-li">{children}</li>,
          strong: ({ children }) => <strong className="md-strong">{children}</strong>,
          code:   ({ inline, children }) =>
            inline
              ? <code className="md-code-inline">{children}</code>
              : <pre className="md-pre"><code>{children}</code></pre>,
          a:      ({ href, children }) => <a href={href} target="_blank" rel="noreferrer" className="md-link">{children}</a>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

function Message({ msg, username }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`msg-row ${isUser ? 'msg-row--user' : 'msg-row--bot'}`}>
      <div className={`msg-avatar ${isUser ? 'msg-avatar--user' : 'msg-avatar--bot'}`}>
        {isUser ? username[0].toUpperCase() : '🤖'}
      </div>
      <div className={`msg-bubble ${isUser ? 'msg-bubble--user' : 'msg-bubble--bot'}`}>
        {isUser ? <p>{msg.content}</p> : <BotMessage content={msg.content} />}
      </div>
    </div>
  )
}

function Typing() {
  return (
    <div className="msg-row msg-row--bot">
      <div className="msg-avatar msg-avatar--bot">🤖</div>
      <div className="msg-bubble msg-bubble--bot typing-bubble">
        <span /><span /><span />
      </div>
    </div>
  )
}

export default function Chat({ auth, onLogout }) {
  const [sessions, setSessions]           = useState([])
  const [activeId, setActiveId]           = useState(auth.session_id)
  const [messages, setMessages]           = useState([])
  const [input, setInput]                 = useState('')
  const [sending, setSending]             = useState(false)
  const [sidebarOpen, setSidebarOpen]     = useState(true)
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  // Load session list
  const loadSessions = useCallback(async () => {
    try {
      const list = await api.listSessions(auth.session_id)
      setSessions(list)
    } catch { /* silent */ }
  }, [auth.session_id])

  useEffect(() => { loadSessions() }, [loadSessions])

  // Load messages for active session
  useEffect(() => {
    const load = async () => {
      try {
        const s = await api.getSession(activeId)
        if (s.messages.length > 0) {
          setMessages(s.messages)
        } else {
          setMessages([{ role: 'assistant', content: WELCOME(auth.username) }])
        }
      } catch {
        setMessages([{ role: 'assistant', content: WELCOME(auth.username) }])
      }
    }
    load()
  }, [activeId, auth.username])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const send = async (text) => {
    const msg = text.trim()
    if (!msg || sending) return
    setInput('')
    setMessages((p) => [...p, { role: 'user', content: msg }])
    setSending(true)
    try {
      const data = await api.sendMessage(msg, activeId)
      setMessages((p) => [...p, { role: 'assistant', content: data.response }])
      loadSessions() // refresh sidebar titles
    } catch (err) {
      setMessages((p) => [...p, { role: 'assistant', content: `⚠️ ${err.message}` }])
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  const handleNew = async () => {
    try {
      const s = await api.newSession(auth.session_id)
      await loadSessions()
      setActiveId(s.session_id)
    } catch { /* silent */ }
  }

  const handleSelect = (sid) => {
    if (sid !== activeId) {
      setActiveId(sid)
      setSending(false)
    }
  }

  const showSuggestions = messages.length <= 1 && !sending

  return (
    <div className={`layout ${sidebarOpen ? 'layout--open' : 'layout--closed'}`}>
      <Sidebar
        username={auth.username}
        sessions={sessions}
        activeSessionId={activeId}
        onSelect={handleSelect}
        onNew={handleNew}
        onLogout={onLogout}
        loading={sending}
      />

      <div className="chat-pane">
        {/* Topbar */}
        <header className="topbar">
          <button className="topbar-toggle" onClick={() => setSidebarOpen((v) => !v)} aria-label="Toggle sidebar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6"  x2="21" y2="6"/>
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div className="topbar-title">
            <span className="topbar-dot" />
            Customer Support
          </div>
          <div className="topbar-right">
            <span className="topbar-badge">{auth.username}</span>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-area">
          {messages.map((m, i) => (
            <Message key={i} msg={m} username={auth.username} />
          ))}
          {sending && <Typing />}
          <div ref={bottomRef} />
        </div>

        {/* Quick suggestions */}
        {showSuggestions && (
          <div className="suggestions-bar">
            {SUGGESTIONS.map((s) => (
              <button key={s} className="suggestion-pill" onClick={() => setInput(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <form className="input-bar" onSubmit={(e) => { e.preventDefault(); send(input) }}>
          <input
            ref={inputRef}
            className="input-field"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your orders…"
            disabled={sending}
            autoComplete="off"
          />
          <button
            type="submit"
            className="send-btn"
            disabled={sending || !input.trim()}
            aria-label="Send"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  )
}
