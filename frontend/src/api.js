// Central API configuration.
// Set VITE_API_URL in your Vercel environment variables to your backend URL (e.g. https://your-app.onrender.com).
// Falls back to local dev server when not set.
export const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

// Derives wss:// or ws:// from BASE_URL for WebSocket connections.
export const WS_BASE = BASE_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');

// --- Auth-aware API client ---
// Call setAuthToken(session?.access_token) from AuthContext when session changes.
let _authToken = null;
export function setAuthToken(token) { _authToken = token; }
export function getAuthToken() { return _authToken; }

function authHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (_authToken) headers["Authorization"] = `Bearer ${_authToken}`;
    return headers;
}

export const api = {
    get: (endpoint) => fetch(`${BASE_URL}${endpoint}`, { headers: authHeaders() }),
    post: (endpoint, body) => fetch(`${BASE_URL}${endpoint}`, {
        method: "POST", headers: authHeaders(), body: JSON.stringify(body),
    }),
    put: (endpoint, body) => fetch(`${BASE_URL}${endpoint}`, {
        method: "PUT", headers: authHeaders(), body: JSON.stringify(body),
    }),
    delete: (endpoint) => fetch(`${BASE_URL}${endpoint}`, {
        method: "DELETE", headers: authHeaders(),
    }),
};
