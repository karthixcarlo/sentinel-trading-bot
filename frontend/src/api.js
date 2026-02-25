// Central API configuration.
// Set VITE_API_URL in your Vercel environment variables to your backend URL (e.g. https://your-app.onrender.com).
// Falls back to local dev server when not set.
export const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

// Derives wss:// or ws:// from BASE_URL for WebSocket connections.
export const WS_BASE = BASE_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');
