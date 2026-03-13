import React, { useState, useRef } from 'react';
import { Bot, Play, Square, Activity, Clock, BarChart2, Zap, AlertCircle } from 'lucide-react';
import { BASE_URL } from './api';
import useNeuralFeed from './hooks/useNeuralFeed';
import useAgentStatus from './hooks/useAgentStatus';

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
    const { status, trades, loading, refetch } = useAgentStatus({ pollInterval: 30000, fetchTrades: true });
    const { messages: wsMessages } = useNeuralFeed({ maxMessages: 50 });
    const [toggling, setToggling] = useState(false);
    const feedRef = useRef(null);

    // null while loading — avoids rendering "stopped" before the server responds
    const isRunning = status.running === true;

    const toggleAgent = async () => {
        setToggling(true);
        try {
            const endpoint = isRunning
                ? `${BASE_URL}/api/agent/stop`
                : `${BASE_URL}/api/agent/start`;
            const res = await fetch(endpoint, { method: 'POST' });
            // Confirm with the actual server state
            refetch();
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
        <div className="min-h-screen bg-dark-bg p-6 lg:p-10 font-sans text-dark-text">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <header>
                    <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center">
                        <Bot size={30} className="mr-3 text-[#00D09C]" /> Autonomous Control
                    </h1>
                    <p className="text-dark-muted mt-1 text-sm">Start, stop, and monitor the LangGraph multi-agent trading system</p>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Control Panel */}
                    <div className="lg:col-span-1 space-y-6">

                        {/* Agent Status Card */}
                        <div className="bg-dark-card rounded-2xl border border-dark-border shadow-sm p-6">
                            <h2 className="text-sm font-bold text-dark-muted uppercase tracking-wider mb-4">Agent Status</h2>
                            <div className="flex items-center mb-4">
                                <div className={`w-4 h-4 rounded-full mr-3 flex-shrink-0 ${loading ? 'bg-dark-muted/20' : isRunning ? 'bg-[#00D09C] animate-pulse' : 'bg-dark-muted/30'}`}></div>
                                <div>
                                    <p className="font-bold text-lg">
                                        {loading ? 'CHECKING…' : isRunning ? 'RUNNING' : (status.status || 'idle').toUpperCase()}
                                    </p>
                                    <p className="text-xs text-dark-muted">
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
                                className={`w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center transition-all ${(toggling || loading) ? 'bg-dark-hover text-dark-muted cursor-not-allowed' :
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
                        <div className={`rounded-2xl border p-5 shadow-sm ${marketOpen ? 'bg-[#00D09C]/5 border-[#00D09C]/20' : 'bg-dark-card border-dark-border'}`}>
                            <div className="flex items-center justify-between mb-2">
                                <p className="text-sm font-bold text-dark-muted uppercase tracking-wider">NSE Market</p>
                                <span className={`text-xs font-bold px-2 py-1 rounded-md ${marketOpen ? 'bg-[#00D09C]/20 text-[#00D09C]' : 'bg-dark-hover text-dark-muted'}`}>
                                    {marketOpen ? 'OPEN' : 'CLOSED'}
                                </span>
                            </div>
                            <p className="text-xs text-dark-muted">9:15 AM – 3:30 PM IST, Mon–Fri</p>
                        </div>

                        {/* Portfolio Summary Card */}
                        <div className="bg-dark-card rounded-2xl border border-dark-border shadow-sm p-5">
                            <h2 className="text-sm font-bold text-dark-muted uppercase tracking-wider mb-4 flex items-center">
                                <Zap size={15} className="mr-2" /> AI Portfolio
                            </h2>
                            {status.portfolio && status.portfolio.total_value ? (
                                <div className="space-y-3">
                                    <div className="flex justify-between">
                                        <span className="text-sm text-dark-muted">Total Value</span>
                                        <span className="font-bold font-mono">₹{status.portfolio.total_value?.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-dark-muted">Cash</span>
                                        <span className="font-mono">₹{status.portfolio.cash?.toLocaleString('en-IN')}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-dark-muted">Positions</span>
                                        <span className="font-bold">{Object.keys(status.portfolio.positions || {}).length}</span>
                                    </div>
                                    {status.performance?.win_rate !== undefined && (
                                        <div className="flex justify-between">
                                            <span className="text-sm text-dark-muted">Win Rate (7d)</span>
                                            <span className={`font-bold ${status.performance.win_rate > 50 ? 'text-[#00D09C]' : 'text-[#EB5B3C]'}`}>
                                                {status.performance.win_rate.toFixed(0)}%
                                            </span>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <p className="text-dark-muted text-sm text-center py-4 opacity-60">No active portfolio</p>
                            )}
                        </div>

                        {/* Recent Trades */}
                        <div className="bg-dark-card rounded-2xl border border-dark-border shadow-sm p-5">
                            <h2 className="text-sm font-bold text-dark-muted uppercase tracking-wider mb-4 flex items-center">
                                <BarChart2 size={15} className="mr-2" /> Recent AI Trades
                            </h2>
                            {trades.length === 0 ? (
                                <p className="text-dark-muted text-sm text-center py-6 opacity-60">No trades executed yet</p>
                            ) : (
                                <div className="space-y-2">
                                    {trades.slice(0, 5).map((t, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-dark-border last:border-0">
                                            <div>
                                                <span className={`text-xs font-bold mr-2 px-1.5 py-0.5 rounded ${t.side === 'BUY' ? 'text-[#00D09C] bg-[#00D09C]/10' : 'text-[#EB5B3C] bg-[#EB5B3C]/10'}`}>
                                                    {t.side}
                                                </span>
                                                <span className="font-bold">{t.symbol?.replace('.NS', '')}</span>
                                            </div>
                                            <span className="font-mono text-dark-muted text-xs">₹{parseFloat(t.price || 0).toLocaleString('en-IN')} × {t.quantity}</span>
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
                        <div className="bg-dark-card rounded-2xl border border-dark-border shadow-sm overflow-hidden">
                            <div className="px-5 py-4 border-b border-dark-border">
                                <h2 className="text-sm font-bold text-dark-muted uppercase tracking-wider flex items-center">
                                    <Clock size={15} className="mr-2" /> Agent Log History
                                </h2>
                            </div>
                            <div className="divide-y divide-dark-border max-h-96 overflow-y-auto">
                                {loading ? (
                                    <div className="p-6 animate-pulse space-y-3">
                                        {[1, 2, 3].map(i => <div key={i} className="h-10 bg-dark-hover rounded-lg" />)}
                                    </div>
                                ) : status.recent_thoughts?.length === 0 ? (
                                    <div className="py-16 text-center text-dark-muted">
                                        <Bot size={36} className="mx-auto mb-3 opacity-30" />
                                        <p className="font-bold">No agent logs yet</p>
                                        <p className="text-sm mt-1">Start the agent to see its neural reasoning here.</p>
                                    </div>
                                ) : status.recent_thoughts.map((t, i) => (
                                    <div key={i} className="px-5 py-3.5 flex items-start hover:bg-dark-card transition-colors">
                                        <AgentBadge name={t.agent || t.agent_name || 'Agent'} />
                                        <span className="text-sm text-dark-text flex-1">{t.thought || t.message}</span>
                                        <span className="text-xs text-dark-muted/60 font-mono ml-4 flex-shrink-0">
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
