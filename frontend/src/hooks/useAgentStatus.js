import { useEffect, useState, useCallback } from 'react';
import { BASE_URL } from '../api';

/**
 * Shared hook that polls the agent status endpoints.
 * Used by AutonomousControl and GodMode (and any future page that
 * needs to display whether the autonomous agent is running).
 *
 * @param {object} opts
 * @param {number} [opts.pollInterval=30000] - ms between lightweight polls
 * @param {boolean} [opts.fetchTrades=false]  - also poll /api/agent/trades
 * @returns {{ status, trades, loading, refetch }}
 */
export default function useAgentStatus({
    pollInterval = 30000,
    fetchTrades = false,
} = {}) {
    const [status, setStatus] = useState({
        status: 'idle', running: null, start_time: null,
        portfolio: {}, performance: {}, recent_thoughts: [],
    });
    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(true);

    // Full status fetch (heavier — includes portfolio + thoughts)
    const fetchFullStatus = useCallback(() => {
        fetch(`${BASE_URL}/api/agent/status`)
            .then((r) => r.json())
            .then((d) => { setStatus(d); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);

    // Lightweight poll — just running flag + start_time
    const fetchLightStatus = useCallback(() => {
        fetch(`${BASE_URL}/api/autonomous/status`)
            .then((r) => r.json())
            .then((d) =>
                setStatus((prev) => ({
                    ...prev,
                    running: d.running,
                    status: d.status,
                    start_time: d.start_time,
                    workflow_id: d.workflow_id,
                }))
            )
            .catch(() => {});
    }, []);

    const fetchTradeHistory = useCallback(() => {
        if (!fetchTrades) return;
        fetch(`${BASE_URL}/api/agent/trades`)
            .then((r) => r.json())
            .then((d) => setTrades(d.trades || []))
            .catch(() => {});
    }, [fetchTrades]);

    // Convenience: trigger a full re-fetch from outside
    const refetch = useCallback(() => {
        fetchFullStatus();
        fetchTradeHistory();
    }, [fetchFullStatus, fetchTradeHistory]);

    useEffect(() => {
        // Full fetch on mount
        fetchFullStatus();
        fetchTradeHistory();

        // Lightweight heartbeat keeps UI in sync
        const interval = setInterval(() => {
            fetchLightStatus();
            fetchTradeHistory();
        }, pollInterval);

        return () => clearInterval(interval);
    }, [pollInterval, fetchFullStatus, fetchLightStatus, fetchTradeHistory]);

    return { status, trades, loading, refetch };
}
