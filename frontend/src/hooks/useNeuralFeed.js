import { useEffect, useState, useRef, useCallback } from 'react';
import { WS_BASE, getAuthToken } from '../api';

/**
 * Shared hook for the /ws/neural-feed WebSocket.
 * Deduplicates the connection logic previously copy-pasted across
 * AutonomousControl, GodMode, and ReasoningEngine.
 *
 * @param {object} opts
 * @param {number} [opts.maxMessages=50]  - ring-buffer size
 * @param {boolean} [opts.filterHeartbeats=true] - drop Heartbeat frames
 * @param {number} [opts.reconnectMs=3000] - reconnect delay
 * @returns {{ messages: Array, connected: boolean, clear: () => void }}
 */
export default function useNeuralFeed({
    maxMessages = 50,
    filterHeartbeats = true,
    reconnectMs = 3000,
} = {}) {
    const [messages, setMessages] = useState([]);
    const [connected, setConnected] = useState(false);
    const wsRef = useRef(null);

    const clear = useCallback(() => setMessages([]), []);

    useEffect(() => {
        let reconnectTimer = null;
        let unmounted = false;

        const connect = () => {
            const token = getAuthToken();
            const url = token
                ? `${WS_BASE}/ws/neural-feed?token=${token}`
                : `${WS_BASE}/ws/neural-feed`;
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => setConnected(true);

            ws.onmessage = (evt) => {
                try {
                    const msg = JSON.parse(evt.data);
                    if (filterHeartbeats && msg.agent === 'Heartbeat') return;
                    setMessages((prev) =>
                        [...prev, { ...msg, id: Date.now() + Math.random() }].slice(-maxMessages)
                    );
                } catch { /* malformed frame */ }
            };

            ws.onerror = () => {};

            ws.onclose = () => {
                setConnected(false);
                if (!unmounted) {
                    reconnectTimer = setTimeout(connect, reconnectMs);
                }
            };
        };

        connect();

        return () => {
            unmounted = true;
            clearTimeout(reconnectTimer);
            wsRef.current?.close();
        };
    }, [maxMessages, filterHeartbeats, reconnectMs]);

    return { messages, connected, clear };
}
