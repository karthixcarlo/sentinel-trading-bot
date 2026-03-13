import React, { useEffect, useRef } from 'react';
import { Activity, Terminal, ShieldAlert, Cpu, Database, CheckCircle2, Zap, BarChart2 } from 'lucide-react';
import useNeuralFeed from './hooks/useNeuralFeed';
import useAgentStatus from './hooks/useAgentStatus';

const AGENT_COLORS = {
    Supervisor: '#8B5CF6', Scout: '#3B82F6', Analyst: '#00D09C',
    Risk: '#F59E0B', Trader: '#EC4899', Monitor: '#14B8A6',
    Learning: '#F97316', System: '#6B7280', Heartbeat: '#9CA3AF', default: '#6B7280'
};

function AgentBadge({ name }) {
    const color = AGENT_COLORS[name] || AGENT_COLORS.default;
    return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold mr-2 flex-shrink-0"
            style={{ background: color + '20', color }}>
            {name}
        </span>
    );
}

export default function GodMode() {
    const { messages: logs, connected: isConnected } = useNeuralFeed({ maxMessages: 50, filterHeartbeats: false });
    const { status: agentStatus } = useAgentStatus({ pollInterval: 5000 });
    const bottomRef = useRef(null);

    // Auto-scroll to bottom of logs
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const getAgentColor = (agent) => {
        switch (agent.toUpperCase()) {
            case 'SCOUT': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
            case 'ANALYST': return 'text-green-500 bg-green-500/10 border-green-500/20';
            case 'RISK': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
            case 'TRADER': return 'text-pink-500 bg-pink-500/10 border-pink-500/20';
            case 'MONITOR': return 'text-teal-500 bg-teal-500/10 border-teal-500/20';
            case 'LEARNING': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
            case 'SYSTEM': return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
            case 'HEARTBEAT': return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
            default: return 'text-dark-muted bg-dark-card border-dark-border';
        }
    };

    const getAgentIcon = (agent) => {
        switch (agent.toUpperCase()) {
            case 'SCOUT': return <Activity size={16} className="mr-2" />;
            case 'ANALYST': return <Cpu size={16} className="mr-2" />;
            case 'RISK': return <ShieldAlert size={16} className="mr-2" />;
            case 'TRADER': return <CheckCircle2 size={16} className="mr-2" />;
            case 'MONITOR': return <BarChart2 size={16} className="mr-2" />;
            case 'LEARNING': return <Zap size={16} className="mr-2" />;
            case 'SYSTEM': return <Database size={16} className="mr-2" />;
            default: return <Terminal size={16} className="mr-2" />;
        }
    };

    return (
        <div className="min-h-screen bg-dark-bg font-sans text-dark-text p-6">

            {/* Header */}
            <header className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-dark-text flex items-center">
                        <Terminal className="mr-3 text-dark-muted" size={28} /> God Mode Feed
                    </h1>
                    <p className="text-dark-muted mt-1">Live autonomous agent operations and system state.</p>
                </div>

                <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-dark-muted">Status:</span>
                    {isConnected ? (
                        <span className="flex items-center text-sm font-bold text-[#00D09C] bg-[#00D09C]/10 px-3 py-1 rounded-full border border-[#00D09C]/20">
                            <span className="w-2 h-2 rounded-full bg-[#00D09C] mr-2 animate-pulse"></span>
                            Live Feed Active
                        </span>
                    ) : (
                        <span className="flex items-center text-sm font-bold text-[#EB5B3C] bg-[#EB5B3C]/10 px-3 py-1 rounded-full border border-[#EB5B3C]/20">
                            <span className="w-2 h-2 rounded-full bg-[#EB5B3C] mr-2"></span>
                            Disconnected
                        </span>
                    )}
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Terminal Window (Left 2 columns) */}
                <div className="lg:col-span-2 bg-black rounded-xl border border-dark-border overflow-hidden flex flex-col h-[70vh]">
                    {/* Mac-style window header */}
                    <div className="bg-dark-card px-4 py-3 flex items-center border-b border-dark-border">
                        <div className="flex gap-2 mr-4">
                            <div className="w-3 h-3 rounded-full bg-[#FF5F56]"></div>
                            <div className="w-3 h-3 rounded-full bg-[#FFBD2E]"></div>
                            <div className="w-3 h-3 rounded-full bg-[#27C93F]"></div>
                        </div>
                        <span className="text-xs font-mono text-dark-muted">sentinel-hive-daemon</span>
                    </div>

                    {/* Log Stream */}
                    <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-3">
                        {logs.map((log) => {
                            const date = new Date(log.timestamp);
                            const timeString = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`;

                            return (
                                <div key={log.id} className="flex items-start animate-fade-in">
                                    <span className="text-dark-muted mr-3 shrink-0">[{timeString}]</span>
                                    <div className="flex-1">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold border mr-2 ${getAgentColor(log.agent)}`}>
                                            {getAgentIcon(log.agent)} {log.agent.toUpperCase()}
                                        </span>
                                        <span className="text-white/70 leading-relaxed">{log.thought}</span>
                                    </div>
                                </div>
                            );
                        })}
                        <div ref={bottomRef} />
                    </div>
                </div>

                {/* System Controls (Right column) */}
                <div className="flex flex-col gap-6">

                    <div className="bg-dark-card rounded-xl border border-dark-border p-6">
                        <h2 className="text-lg font-bold mb-4 flex items-center border-b border-dark-border pb-3">
                            <ShieldAlert size={20} className="mr-2 text-[#EB5B3C]" /> Global Safety
                        </h2>
                        <p className="text-sm text-dark-muted mb-4">
                            Instantly halt all autonomous trading operations. Current portfolio will remain untouched.
                        </p>
                        <button className="w-full bg-[#EB5B3C] hover:bg-[#D44A2D] text-white font-bold py-3 px-4 rounded-lg transition-colors flex justify-center items-center">
                            EMERGENCY STOP
                        </button>
                    </div>

                    <div className="bg-dark-card rounded-xl border border-dark-border p-6 flex-1">
                        <h2 className="text-lg font-bold mb-4 flex items-center border-b border-dark-border pb-3">
                            <Activity size={20} className="mr-2 text-[#00D09C]" /> Cluster Health
                        </h2>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-bold text-dark-muted">LangGraph Engine</span>
                                <span className="text-xs font-mono bg-[#00D09C]/10 text-[#00D09C] px-2 py-1 rounded">ONLINE</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-bold text-dark-muted">FastAPI Bridge</span>
                                <span className="text-xs font-mono bg-[#00D09C]/10 text-[#00D09C] px-2 py-1 rounded">ONLINE</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-bold text-dark-muted">Agent Status</span>
                                <span className={`text-xs font-mono px-2 py-1 rounded ${agentStatus.status === 'running' ? 'bg-[#00D09C]/10 text-[#00D09C]' : 'bg-dark-card text-dark-muted'}`}>
                                    {agentStatus.status?.toUpperCase() || 'IDLE'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Portfolio Summary */}
                    <div className="bg-dark-card rounded-xl border border-dark-border p-6">
                        <h2 className="text-lg font-bold mb-4 flex items-center border-b border-dark-border pb-3">
                            <Zap size={20} className="mr-2 text-[#00D09C]" /> AI Portfolio
                        </h2>
                        {agentStatus.portfolio?.total_value ? (
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-dark-muted">Total Value</span>
                                    <span className="font-bold font-mono">₹{agentStatus.portfolio.total_value?.toLocaleString('en-IN')}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-dark-muted">Cash</span>
                                    <span className="font-mono">₹{agentStatus.portfolio.cash?.toLocaleString('en-IN')}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-dark-muted">Positions</span>
                                    <span className="font-bold">{Object.keys(agentStatus.portfolio.positions || {}).length}</span>
                                </div>
                                {agentStatus.performance?.win_rate !== undefined && (
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-dark-muted">Win Rate</span>
                                        <span className={`font-bold ${agentStatus.performance.win_rate > 50 ? 'text-[#00D09C]' : 'text-[#EB5B3C]'}`}>
                                            {agentStatus.performance.win_rate.toFixed(0)}%
                                        </span>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <p className="text-sm text-dark-muted opacity-60">No portfolio data</p>
                        )}
                    </div>

                </div>

            </div>
        </div>
    );
}

// Add a simple fade-in animation to Tailwind via global CSS or inline config
// (Assumes you have a fade-in keyframe defined, or just use normal rendering)
