import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, ArrowUpRight, ArrowDownRight, AlertCircle, RefreshCw, Zap } from 'lucide-react';
import { BASE_URL } from './api';

const DEMO = {
    cash: 100000, positions: [], portfolio_value: 100000,
    total_holdings_value: 0, total_returns: 0, returns_pct: 0
};

function MetricCard({ label, value, delta, deltaPositive, color }) {
    return (
        <div className={`bg-dark-card rounded-2xl border border-dark-border p-6 shadow-sm relative overflow-hidden group hover:shadow-md hover:-translate-y-1 transition-all duration-300`}>
            <div className={`absolute top-0 right-0 w-28 h-28 rounded-bl-[100px] -mr-6 -mt-6 transition-transform group-hover:scale-110 ${color || 'bg-[#111111]'}`}></div>
            <p className="text-sm font-medium text-dark-muted mb-2 relative z-10">{label}</p>
            <p className="text-2xl font-bold font-mono text-dark-text tracking-tight relative z-10">{value}</p>
            {delta !== undefined && (
                <p className={`text-sm font-bold mt-2 relative z-10 ${deltaPositive ? 'text-[#00D09C]' : 'text-[#EB5B3C]'}`}>
                    {deltaPositive ? '▲' : '▼'} {delta}
                </p>
            )}
        </div>
    );
}

export default function Portfolio() {
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPortfolio = () => {
        setLoading(true);
        fetch(`${BASE_URL}/api/portfolio/demo_user/detail`)
            .then(r => {
                if (!r.ok) throw new Error('Backend not reachable');
                return r.json();
            })
            .then(d => { setData(d); setLoading(false); })
            .catch(e => { setError(e.message); setData(DEMO); setLoading(false); });
    };

    useEffect(() => { fetchPortfolio(); }, []);

    const d = data || DEMO;
    const isProfit = d.total_returns >= 0;

    return (
        <div className="min-h-screen bg-dark-bg p-6 lg:p-10 font-sans text-dark-text">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <header className="flex flex-col md:flex-row items-start md:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center">
                            <Briefcase size={30} className="mr-3 text-[#00D09C]" /> Portfolio
                        </h1>
                        <p className="text-dark-muted mt-1 text-sm">Your holdings, P&L, and cash balance</p>
                    </div>
                    <div className="flex gap-3">
                        <button onClick={fetchPortfolio}
                            className="flex items-center px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-sm font-bold text-dark-muted shadow-sm hover:bg-[#111111] transition-colors">
                            <RefreshCw size={15} className={`mr-2 ${loading ? 'animate-spin' : ''}`} /> Refresh
                        </button>
                        <button onClick={() => navigate('/trade')}
                            className="flex items-center px-5 py-2 bg-[#111111] text-white rounded-lg text-sm font-bold shadow-sm hover:bg-black transition-colors">
                            <Zap size={15} className="mr-2 text-[#00D09C]" /> New Trade
                        </button>
                    </div>
                </header>

                {error && (
                    <div className="bg-[#EB5B3C]/10 border border-[#EB5B3C]/20 text-[#EB5B3C] px-4 py-3 rounded-xl text-sm flex items-center">
                        <AlertCircle size={16} className="mr-2 flex-shrink-0" /> Using demo data — FastAPI backend not reachable: {error}
                    </div>
                )}

                {/* Summary Metrics */}
                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 animate-pulse">
                        {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-dark-card rounded-2xl border border-dark-border" />)}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        <MetricCard label="Portfolio Value" value={`₹${d.portfolio_value.toLocaleString('en-IN')}`}
                            delta={`${d.returns_pct >= 0 ? '+' : ''}${d.returns_pct}%`} deltaPositive={isProfit} color="bg-[#00D09C]/5" />
                        <MetricCard label="Available Cash" value={`₹${d.cash.toLocaleString('en-IN')}`} color="bg-dark-hover" />
                        <MetricCard label="Holdings Value" value={`₹${d.total_holdings_value.toLocaleString('en-IN')}`} color="bg-dark-hover" />
                        <MetricCard label="Total Returns"
                            value={`₹${Math.abs(d.total_returns).toLocaleString('en-IN')}`}
                            delta={`${d.returns_pct >= 0 ? '+' : ''}${d.returns_pct}%`}
                            deltaPositive={isProfit}
                            color={isProfit ? 'bg-[#00D09C]/5' : 'bg-[#EB5B3C]/5'} />
                    </div>
                )}

                {/* Holdings Table */}
                <div className="bg-dark-card rounded-2xl border border-dark-border overflow-hidden shadow-sm">
                    <div className="p-6 border-b border-dark-border">
                        <h2 className="text-lg font-bold text-dark-text">Holdings</h2>
                    </div>
                    {loading ? (
                        <div className="p-6 animate-pulse space-y-3">
                            {[1, 2, 3].map(i => <div key={i} className="h-14 bg-dark-hover rounded-lg" />)}
                        </div>
                    ) : d.positions.length === 0 ? (
                        <div className="py-24 text-center text-dark-muted">
                            <Briefcase size={40} className="mx-auto mb-4 opacity-30" />
                            <p className="font-bold text-lg">No positions yet</p>
                            <p className="text-sm mt-1 mb-6">Place your first trade to get started.</p>
                            <button onClick={() => navigate('/trade')}
                                className="px-6 py-3 bg-[#111111] text-white rounded-lg font-bold hover:bg-black transition-colors">
                                Go to Trade Executor
                            </button>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead className="bg-dark-card text-dark-muted text-xs uppercase tracking-wider">
                                    <tr>
                                        <th className="px-6 py-4 font-bold">Stock</th>
                                        <th className="px-6 py-4 font-bold text-right">Qty</th>
                                        <th className="px-6 py-4 font-bold text-right">Avg Price</th>
                                        <th className="px-6 py-4 font-bold text-right">CMP</th>
                                        <th className="px-6 py-4 font-bold text-right">Value</th>
                                        <th className="px-6 py-4 font-bold text-right">P&L</th>
                                        <th className="px-6 py-4 font-bold text-center">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-dark-border">
                                    {d.positions.map(pos => {
                                        const pnlPositive = pos.pnl >= 0;
                                        return (
                                            <tr key={pos.symbol} className="hover:bg-dark-card transition-colors group">
                                                <td className="px-6 py-5">
                                                    <div className="flex items-center">
                                                        <div className="w-8 h-8 rounded-full bg-dark-hover flex items-center justify-center mr-3 text-xs font-bold group-hover:bg-[#00D09C]/10 group-hover:text-[#00D09C] transition-colors">
                                                            {pos.symbol.charAt(0)}
                                                        </div>
                                                        <span className="font-bold">{pos.symbol}</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-5 text-right font-mono text-dark-muted">{pos.quantity}</td>
                                                <td className="px-6 py-5 text-right font-mono text-dark-muted">₹{pos.average_price.toLocaleString('en-IN')}</td>
                                                <td className="px-6 py-5 text-right font-mono font-bold">₹{pos.current_price.toLocaleString('en-IN')}</td>
                                                <td className="px-6 py-5 text-right font-mono font-bold">₹{pos.position_value.toLocaleString('en-IN')}</td>
                                                <td className="px-6 py-5 text-right">
                                                    <div className={`inline-flex flex-col items-end ${pnlPositive ? 'text-[#00D09C]' : 'text-[#EB5B3C]'}`}>
                                                        <span className="font-bold font-mono">₹{Math.abs(pos.pnl).toLocaleString('en-IN')}</span>
                                                        <span className="text-xs font-bold">{pnlPositive ? '+' : '-'}{Math.abs(pos.pnl_pct).toFixed(2)}%</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-5 text-center">
                                                    <button
                                                        onClick={() => navigate(`/trade?symbol=${pos.symbol}&action=SELL`)}
                                                        className="px-4 py-1.5 bg-[#EB5B3C]/10 text-[#EB5B3C] rounded-lg text-xs font-bold hover:bg-[#EB5B3C] hover:text-white transition-colors">
                                                        Sell
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}
