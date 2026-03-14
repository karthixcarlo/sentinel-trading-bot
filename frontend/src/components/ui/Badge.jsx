import React from 'react';

const AGENT_COLORS = {
    Supervisor: '#00D09C',
    Analyst: '#3B82F6',
    RiskManager: '#F59E0B',
    Risk: '#F59E0B',
    Executor: '#8B5CF6',
    Trader: '#8B5CF6',
    Router: '#EC4899',
    Scout: '#06B6D4',
    System: '#6B7280',
    Heartbeat: '#374151',
};

export function AgentBadge({ name }) {
    const color = AGENT_COLORS[name] || '#6B7280';
    return (
        <span
            className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold tracking-wide uppercase flex-shrink-0"
            style={{ background: color + '18', color, border: `1px solid ${color}30` }}
        >
            {name}
        </span>
    );
}

