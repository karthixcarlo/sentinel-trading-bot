import React, { useEffect, useState, useRef } from 'react';
import { Bot, Play, Square, Activity, Clock, BarChart2, Zap, AlertCircle } from 'lucide-react';
import { BASE_URL, WS_BASE } from './api';

const AGENT_COLORS = {
    Supervisor: '#00D09C', Analyst: '#3B82F6', RiskManager: '#F59E0B',
    Executor: '#8B5CF6', Router: '#EC4899', default: '#6B7280'
};

function AgentBadge({ name }) {
    const color = AGENT_COLORS[name] || AGENT_COLORS.default;
    return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold mr-2 flex-shrink-0"
            style={{ background: color + '20', color }}>
            {name}
        </span>
    );
}

export default function AutonomousControl() {
    // null = still loading from server (prevents false "stopped" flash on mount)
    const [status, setStatus] = useState({ status: 'idle', running: null, start_time: null, portfolio: {}, performance: {}, recent_thoughts: [] });
    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [toggling, setToggling] = useState(false);
    const [wsMessages, setWsMessages] = useState([]);
    const wsRef = useRef(null);
    const feedRef = useRef(null);

    // Lightweight poll — syncs running state from server without the full payload
    const fetchAutonomousStatus = () => {
        fetch(`${BASE_URL}/api/autonomous/status`)
            .then(r => r.json())
            .then(d => setStatus(prev => ({ ...prev, running: d.running, status: d.status, start_time: d.start_time, workflow_id: d.workflow_id })))
            .catch(() => {});
    };

    // Full status fetch — used on mount and after toggle
    const fetchStatus = () => {
        fetch(`${BASE_URL}/api/agent/status`)
            .then(r => r.json())
            .then(d => {
                setStatus(d);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    const fetchTrades = () => {
        fetch(`${BASE_URL}/api/agent/trades`)
            .then(r => r.json())
            .then(d => setTrades(d.trades || []))
            .catch(() => {});
    };

    // null while loading — avoids rendering "stopped" before the server responds
    const isRunning = status.running === true;

    useEffect(() => {
        // Full fetch on mount to get portfolio + thoughts
        fetchStatus();
        fetchTrades();

        // Lightweight 30-second heartbeat keeps the toggle accurate
        // even after tab hibernation or page navigation
        const interval = setInterval(() => {
            fetchAutonomousStatus();
            fetchTrades();
        }, 30000);
        return () => clearInterval(interval);
    }, []);

    // WebSocket for live neural feed
    useEffect(() => {
        const connect = () => {
            const ws = new WebSocket(`${WS_BASE}/ws/neural-feed`);
            wsRef.current = ws;
            ws.onopen = () => console.log('Neural Feed WebSocket connected');
            ws.onmessage = (evt) => {
                try {
                    const msg = JSON.parse(evt.data);
                    setWsMessages(prev => [msg, ...prev].slice(0, 50));
                    setTimeout(() => feedRef.current?.scrollTo({ top: 0, behavior: 'smooth' }), 50);
                } catch { }
            };
            ws.onerror = () => { };
            ws.onclose = () => setTimeout(connect, 3000);
        };
        connect();
        return () => wsRef.current?.close();
    }, []);

    const toggleAgent = async () => {
        setToggling(true);
        try {
            const endpoint = isRunning
                ? `${BASE_URL}/api/agent/stop`
                : `${BASE_URL}/api/agent/start`;
            const res = await fetch(endpoint, { method: 'POST' });
            if (res.ok) {
                // Optimistic update so the toggle flips instantly
                setStatus(prev => ({ ...prev, running: !isRunning, status: !isRunning ? 'running' : 'stopped' }));
            }
            // Confirm with the actual server state
            fetchStatus();
        } catch { }
        setToggling(false);
    };

    // Market open check (IST 9:15–15:30)
    const now = new Date();
    const istHour = parseInt(new Intl.DateTimeFormat('en-IN', { hour: '2-digit', hour12: false, timeZone: 'Asia/Kolkata' }).format(now));
    const istMin = now.getMinutes();
    const isWeekday = now.getDay() >= 1 && now.getDay() <= 5;
    const afterOpen = istHour > 9 || (istHour === 9 && istMin >= 15);
    const beforeClose = istHour < 15 || (istHour === 15 && istMin <= 30);
    const marketOpen = isWeekday && afterOpen && beforeClose;

    return (
        <div className="min-h-screen bg-black p-6 lg:p-10 font-sans text-white">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <header>
                    <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center">
                        <Bot size={30} className="mr-3 text-[#00D09C]" /> Autonomous Control
                    </h1>
                    <p className="text-[#9CA3AF] mt-1 text-sm">Start, stop, and monitor the LangGraph multi-agent trading system</p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Control Panel */}
                    <div className="lg:col-span-1 space-y-6">

                        {/* Agent Status Card */}
                        <div className="bg-[#0A0A0A] rounded-2xl border border-[#1E1E1E] shadow-sm p-6">
                            <h2 className="text-sm font-bold text-[#9CA3AF] uppercase tracking-wider mb-4">Agent Status</h2>
                            <div className="flex items-center mb-4">
                                <div className={`w-4 h-4 rounded-full mr-3 flex-shrink-0 ${loading ? 'bg-[#444444]/20' : isRunning ? 'bg-[#00D09C] animate-pulse' : 'bg-[#444444]/30'}`}></div>
                                <div>
                                    <p className="font-bold text-lg">
                                        {loading ? 'CHECKING…' : isRunning ? 'RUNNING' : (status.status || 'idle').toUpperCase()}
                                    </p>
                                    <p className="text-xs text-[#9CA3AF]">
                                        {loading ? 'Syncing with server…' : isRunning ? 'Agent is actively scanning markets' : 'Agent is idle'}
                                    </p>
                                </div>
                            </div>
                            {isRunning && status.start_time && (
                                <p className="text-xs text-[#00D09C] mb-4 flex items-center">
                                    <Clock size={12} className="mr-1" />
                                    Running since {new Date(status.start_time).toLocaleTimeString()}
                                </p>
                            )}
                            <button
                                onClick={toggleAgent}
                                disabled={toggling || loading}
                                className={`w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center transition-all ${(toggling || loading) ? 'bg-[#1E1E1E] text-[#9CA3AF] cursor-not-allowed' :
                                    isRunning
                                        ? 'bg-[#EB5B3C]/10 text-[#EB5B3C] hover:bg-[#EB5B3C] hover:text-white border border-[#EB5B3C]/20'
                                        : 'bg-[#00D09C] text-white hover:bg-[#00C090] shadow-lg shadow-[#00D09C]/20'}`}>
                                {toggling ? (
                                    <Activity size={18} className="mr-2 animate-spin" />
                                ) : isRunning ? (
                                    <Square size={18} className="mr-2" />
                                ) : (
                                    <Play size={18} className="mr-2" />
                                )}
                                {toggling ? 'Processing...' : isRunning ? 'Stop Agent' : 'Start Agent'}
                            </button>
                        </div>

                        {/* Market Status Card */}
                        <div className={`rounded-2xl border p-5 shadow-sm ${marketOpen ? 'bg-[#00D09C]/5 border-[#00D09C]/20' : 'bg-[#0A0A0A] border-[#1E1E1E]'}`}>
                            <div className="flex items-center justify-between mb-2">
                                <p className="text-sm font-bold text-[#9CA3AF] uppercase tracking-wider">NSE Market</p>
                                <span className={`text-xs font-bold px-2 py-1 rounded-md ${marketOpen ? 'bg-[#00D09C]/20 text-[#00D09C]' : 'bg-[#1E1E1E] text-[#9CA3AF]'}`}>
                                    {marketOpen ? 'OPEN' : 'CLOSED'}
                                </span>
                            </div>
                            <p className="text-xs text-[#9CA3AF]">9:15 AM – 3:30 PM IST, Mon–Fri</p>
                        </div>

                        {/* Portfolio Summary Card */}
                        <div className="bg-[#0A0A0A] rounded-2xl border border-[#1E1E1E] shadow-sm p-5">
                            <h2 className="text-sm font-bold text-[#9CA3AF] uppercase tracking-wider mb-4 flex items-center">
                                <Zap size={15} className="mr-2" /> AI Portfolio
                            </h2>
                            {status.portfolio && status.portfolio.total_value ? (
                                <div className="space-y-3">
                                    <div className="flex justify-between">
                                        <span className="text-sm text-[#9CA3AF]">Total Value</span>
                                        <span className="font-bold font-mono">₹{status.portfolio.total_value?.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-[#9CA3AF]">Cash</span>
                                        <span className="font-mono">₹{status.portfolio.cash?.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-[#9CA3AF]">Positions</span>
                                        <span className="font-bold">{Object.keys(status.portfolio.positions || {}).length}</span>
                                    </div>
                                    {status.performance?.win_rate !== undefined && (
                                        <div className="flex justify-between">
                                            <span className="text-sm text-[#9CA3AF]">Win Rate (7d)</span>
                                            <span className={`font-bold ${status.performance.win_rate > 50 ? 'text-[#00D09C]' : 'text-[#EB5B3C]'}`}>
                                                {status.performance.win_rate.toFixed(0)}%
                                            </span>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p className="text-[#9CA3AF] text-sm text-center py-4 opacity-60">No active portfolio</p>
                            )}
                        </div>

                        {/* Recent Trades */}
                        <div className="bg-[#0A0A0A] rounded-2xl border border-[#1E1E1E] shadow-sm p-5">
                            <h2 className="text-sm font-bold text-[#9CA3AF] uppercase tracking-wider mb-4 flex items-center">
                                <BarChart2 size={15} className="mr-2" /> Recent AI Trades
                            </h2>
                            {trades.length === 0 ? (
                                <p className="text-[#9CA3AF] text-sm text-center py-6 opacity-60">No trades executed yet</p>
                            ) : (
                                <div className="space-y-2">
                                    {trades.slice(0, 5).map((t, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-[#1E1E1E] last:border-0">
                                            <div>
                                                <span className={`text-xs font-bold mr-2 px-1.5 py-0.5 rounded ${t.side === 'BUY' ? 'text-[#00D09C] bg-[#00D09C]/10' : 'text-[#EB5B3C] bg-[#EB5B3C]/10'}`}>
                                                    {t.side}
                                                </span>
                                                <span className="font-bold">{t.symbol?.replace('.NS', '')}</span>
                                            </div>
                                            <span className="font-mono text-[#9CA3AF] text-xs">₹{parseFloat(t.price || 0).toLocaleString('en-IN')} × {t.quantity}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Neural Feed */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Live WebSocket Feed */}
                        <div className="bg-black rounded-2xl overflow-hidden shadow-sm border border-white/5">
                            <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between">
                                <h2 className="text-sm font-bold text-white/70 uppercase tracking-wider flex items-center">
                                    <span className="w-2 h-2 rounded-full bg-[#00D09C] animate-pulse mr-2"></span>
                                    Live Neural Feed
                                </h2>
                                <span className="text-xs text-white/30 font-mono">WebSocket /ws/neural-feed</span>
                            </div>
                            <div ref={feedRef} className="h-64 overflow-y-auto p-4 space-y-2 font-mono text-xs">
                                {wsMessages.length === 0 ? (
                                    <p className="text-white/30 text-center py-8">Awaiting neural transmissions...</p>
                                ) : wsMessages.map((msg, i) => (
                                    <div key={i} className="flex items-start text-white/70">
                                        <span className="text-white/30 mr-3 flex-shrink-0">{msg.timestamp?.slice(11, 19) || '??:??:??'}</span>
                                        <AgentBadge name={msg.agent || 'System'} />
                                        <span>{msg.thought || msg.message}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* DB Agent Logs */}
                        <div className="bg-[#0A0A0A] rounded-2xl border border-[#1E1E1E] shadow-sm overflow-hidden">
                            <div className="px-5 py-4 border-b border-[#1E1E1E]">
                                <h2 className="text-sm font-bold text-[#9CA3AF] uppercase tracking-wider flex items-center">
                                    <Clock size={15} className="mr-2" /> Agent Log History
                                </h2>
                            </div>
                            <div className="divide-y divide-[#1E1E1E] max-h-96 overflow-y-auto">
                                {loading ? (
                                    <div className="p-6 animate-pulse space-y-3">
                                        {[1, 2, 3].map(i => <div key={i} className="h-10 bg-[#1E1E1E] rounded-lg" />)}
                                    </div>
                                ) : status.recent_thoughts?.length === 0 ? (
                                    <div className="py-16 text-center text-[#9CA3AF]">
                                        <Bot size={36} className="mx-auto mb-3 opacity-30" />
                                        <p className="font-bold">No agent logs yet</p>
                                        <p className="text-sm mt-1">Start the agent to see its neural reasoning here.</p>
                                    </div>
                                ) : status.recent_thoughts.map((t, i) => (
                                    <div key={i} className="px-5 py-3.5 flex items-start hover:bg-[#0A0A0A] transition-colors">
                                        <AgentBadge name={t.agent || t.agent_name || 'Agent'} />
                                        <span className="text-sm text-white flex-1">{t.thought || t.message}</span>
                                        <span className="text-xs text-[#9CA3AF]/60 font-mono ml-4 flex-shrink-0">
                                            {t.timestamp ? new Date(t.timestamp).toLocaleTimeString('en-IN') : ''}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>
                </div>

            </div>
        </div>
    );
}
