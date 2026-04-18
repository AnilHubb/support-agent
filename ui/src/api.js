const BASE = "http://localhost:8000";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Error ${res.status}`);
  return data;
}

export const api = {
  login: (username, password) =>
    req("/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  sendMessage: (message, session_id) =>
    req("/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id }),
    }),
  getSession: (session_id) => req(`/session/${session_id}`),
  listSessions: (auth_session_id) =>
    req(`/sessions?auth_session_id=${encodeURIComponent(auth_session_id)}`),
  newSession: (auth_session_id) =>
    req("/session/new", {
      method: "POST",
      body: JSON.stringify({ auth_session_id }),
    }),
};
