import React, { useEffect, useState, useMemo } from 'react';
import { Briefcase, AlertCircle, ArrowUpRight, ShieldCheck, Grid3X3, Plus, X, TrendingUp } from 'lucide-react';
import TradingChart from './components/TradingChart';
import { BASE_URL } from './api';

const DEFAULT_PINNED = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS'];

function loadPinnedTickers() {
    try {
        const stored = localStorage.getItem('sentinel_pinned_tickers');
        return stored ? JSON.parse(stored) : DEFAULT_PINNED;
    } catch { return DEFAULT_PINNED; }
}

function savePinnedTickers(tickers) {
    localStorage.setItem('sentinel_pinned_tickers', JSON.stringify(tickers));
}

export default function Dashboard() {
    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);
    const [pinnedTickers, setPinnedTickers] = useState(loadPinnedTickers);
    const [showAddTicker, setShowAddTicker] = useState(false);
    const [newTicker, setNewTicker] = useState('');

    useEffect(() => {
        const userId = "demo_user";
        fetch(`${BASE_URL}/api/portfolio/${userId}`)
            .then(res => res.json())
            .then(data => {
                const cash = data?.cash ?? 100000;
                const positions = Array.isArray(data?.positions) ? data.positions : [];
                const orders = Array.isArray(data?.orders) ? data.orders : [];
                setPortfolio({ cash, positions, orders });
                setLoading(false);
            })
            .catch(() => {
                setPortfolio({ cash: 100000, positions: [], orders: [] });
                setLoading(false);
            });
    }, []);

    const portfolioValue = useMemo(() => {
        if (!portfolio) return 0;
        const cash = portfolio.cash ?? 100000;
        const positions = portfolio.positions ?? [];
        return positions.reduce((acc, pos) => acc + (pos.quantity * pos.current_price), cash);
    }, [portfolio]);

    const addTicker = () => {
        const t = newTicker.toUpperCase().trim();
        if (!t) return;
        const ticker = t.endsWith('.NS') || t.endsWith('.BO') ? t : `${t}.NS`;
        if (pinnedTickers.length < 4 && !pinnedTickers.includes(ticker)) {
            const updated = [...pinnedTickers, ticker];
            setPinnedTickers(updated);
            savePinnedTickers(updated);
        }
        setNewTicker('');
        setShowAddTicker(false);
    };

    const removeTicker = (ticker) => {
        const updated = pinnedTickers.filter(t => t !== ticker);
        setPinnedTickers(updated);
        savePinnedTickers(updated);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-dark-bg p-6 lg:p-10 font-sans">
                <div className="animate-pulse space-y-8 max-w-7xl mx-auto">
                    <div className="space-y-3">
                        <div className="h-8 bg-dark-card rounded w-1/4"></div>
                        <div className="h-4 bg-dark-card rounded w-1/3"></div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-32 bg-dark-card border border-dark-border rounded-2xl"></div>
                        ))}
                    </div>
                    <div className="h-[400px] bg-dark-card border border-dark-border rounded-2xl"></div>
                </div>
            </div>
        );
    }

    if (!portfolio && !loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-dark-bg text-accent-red">
                <AlertCircle className="mb-4 h-12 w-12" />
                <h2 className="text-xl font-bold text-dark-text">Connection Interrupted</h2>
                <p className="text-dark-muted mt-2">Failed to load live portfolio data from Neural Core.</p>
            </div>
        );
    }

    const { cash, positions } = portfolio;

    return (
        <div className="min-h-screen bg-dark-bg font-sans text-dark-text p-6 lg:p-10">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Dashboard</h1>
                        <p className="text-dark-muted mt-1 text-sm md:text-base flex items-center">
                            Welcome back. <ShieldCheck size={16} className="ml-2 mr-1 text-accent-green" /> Neural Core Online
                        </p>
                    </div>
                    <div className="bg-dark-card px-4 py-2 rounded-lg border border-dark-border inline-flex items-center text-sm font-bold text-dark-muted">
                        <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse mr-2"></div>
                        Live Market Sync
                    </div>
                </header>

                {/* Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="bg-dark-card rounded-2xl border border-dark-border p-6 hover:border-accent-green/20 transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-accent-green/5 rounded-bl-[100px] -mr-8 -mt-8 group-hover:scale-110 transition-transform"></div>
                        <div className="text-sm font-medium text-dark-muted mb-2 relative z-10">Total Portfolio Value</div>
                        <div className="text-3xl font-bold font-mono tracking-tight relative z-10">₹{portfolioValue.toLocaleString()}</div>
                        <div className="text-accent-green text-sm flex items-center mt-3 font-bold bg-accent-green/10 w-max px-2 py-1 rounded-md relative z-10">
                            <ArrowUpRight size={16} className="mr-1" /> +2.1% All Time
                        </div>
                    </div>

                    <div className="bg-dark-card rounded-2xl border border-dark-border p-6 hover:border-dark-border transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-dark-hover rounded-bl-[100px] -mr-8 -mt-8 group-hover:scale-110 transition-transform"></div>
                        <div className="text-sm font-medium text-dark-muted mb-2 relative z-10">Available Trading Cash</div>
                        <div className="text-3xl font-bold font-mono tracking-tight relative z-10">₹{cash.toLocaleString()}</div>
                    </div>

                    <div className="bg-dark-card rounded-2xl border border-dark-border p-6 hover:border-dark-border transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-dark-hover rounded-bl-[100px] -mr-8 -mt-8 group-hover:scale-110 transition-transform"></div>
                        <div className="text-sm font-medium text-dark-muted mb-2 relative z-10">Active Positions</div>
                        <div className="text-3xl font-bold font-mono tracking-tight relative z-10">{positions.length} Assets</div>
                    </div>
                </div>

                {/* Multi-Ticker Grid */}
                <div className="bg-dark-card rounded-2xl border border-dark-border overflow-hidden">
                    <div className="p-5 border-b border-dark-border flex items-center justify-between">
                        <h2 className="text-sm font-bold text-dark-muted uppercase tracking-wider flex items-center">
                            <Grid3X3 size={16} className="mr-2" /> Sector Monitor
                        </h2>
                        {pinnedTickers.length < 4 && (
                            showAddTicker ? (
                                <form onSubmit={(e) => { e.preventDefault(); addTicker(); }} className="flex items-center gap-2">
                                    <input
                                        value={newTicker}
                                        onChange={e => setNewTicker(e.target.value)}
                                        placeholder="e.g. SBIN"
                                        autoFocus
                                        className="bg-dark-bg border border-dark-border rounded-lg px-3 py-1.5 text-xs text-dark-text w-28
                                            placeholder:text-dark-muted/50 focus:outline-none focus:border-accent-green/50"
                                    />
                                    <button type="submit" className="text-accent-green text-xs font-bold hover:underline">Add</button>
                                    <button type="button" onClick={() => setShowAddTicker(false)} className="text-dark-muted hover:text-dark-text">
                                        <X size={14} />
                                    </button>
                                </form>
                            ) : (
                                <button
                                    onClick={() => setShowAddTicker(true)}
                                    className="text-dark-muted hover:text-accent-green text-xs font-bold flex items-center transition-colors"
                                >
                                    <Plus size={14} className="mr-1" /> Add Ticker
                                </button>
                            )
                        )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-dark-border">
                        {pinnedTickers.map(ticker => (
                            <div key={ticker} className="bg-dark-card relative group">
                                <button
                                    onClick={() => removeTicker(ticker)}
                                    className="absolute top-3 right-3 z-10 p-1 rounded-md bg-dark-bg/80 text-dark-muted
                                        hover:text-accent-red hover:bg-accent-red/10 opacity-0 group-hover:opacity-100 transition-all"
                                    title="Unpin"
                                >
                                    <X size={12} />
                                </button>
                                <div className="px-4 pt-3 flex items-center text-xs">
                                    <TrendingUp size={12} className="mr-1.5 text-accent-green" />
                                    <span className="font-bold font-mono text-dark-text">{ticker}</span>
                                </div>
                                <div className="h-[220px]">
                                    <TradingChart symbol={ticker} userId="demo_user" compact />
                                </div>
                            </div>
                        ))}
                        {pinnedTickers.length === 0 && (
                            <div className="col-span-2 bg-dark-card py-16 text-center">
                                <Grid3X3 size={32} className="mx-auto mb-3 text-dark-muted/30" />
                                <p className="text-dark-muted text-sm font-bold">No tickers pinned</p>
                                <p className="text-dark-muted/60 text-xs mt-1">Click "Add Ticker" to monitor up to 4 stocks</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Holdings Table */}
                <div className="bg-dark-card rounded-2xl border border-dark-border overflow-hidden">
                    <div className="p-6 border-b border-dark-border flex items-center justify-between">
                        <h2 className="text-lg font-bold flex items-center">
                            <Briefcase size={20} className="mr-2 text-dark-muted" /> Current Holdings
                        </h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-dark-bg text-dark-muted text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-bold">Asset</th>
                                    <th className="px-6 py-4 font-bold text-right">Quantity</th>
                                    <th className="px-6 py-4 font-bold text-right">Avg Price</th>
                                    <th className="px-6 py-4 font-bold text-right">Total Value</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-dark-border">
                                {positions.map((pos, idx) => {
                                    const total = pos.quantity * pos.current_price;
                                    return (
                                        <tr key={idx} className="hover:bg-dark-hover transition-colors group cursor-default">
                                            <td className="px-6 py-5 font-bold flex items-center">
                                                <div className="w-8 h-8 rounded-full bg-dark-hover flex items-center justify-center mr-3 text-xs group-hover:bg-accent-green/10 group-hover:text-accent-green transition-colors">
                                                    {pos.symbol.charAt(0)}
                                                </div>
                                                {pos.symbol}
                                            </td>
                                            <td className="px-6 py-5 font-mono text-right text-dark-muted">{pos.quantity}</td>
                                            <td className="px-6 py-5 font-mono text-right text-dark-muted">₹{pos.current_price.toLocaleString()}</td>
                                            <td className="px-6 py-5 font-mono text-right font-bold">₹{total.toLocaleString()}</td>
                                        </tr>
                                    );
                                })}
                                {positions.length === 0 && (
                                    <tr>
                                        <td colSpan="4" className="px-6 py-12 text-center text-dark-muted">
                                            <div className="flex flex-col items-center justify-center">
                                                <div className="w-16 h-16 bg-dark-hover rounded-full flex items-center justify-center mb-3">
                                                    <Briefcase className="text-dark-muted/50" size={24} />
                                                </div>
                                                <p className="font-bold">No Active Positions</p>
                                                <p className="text-sm mt-1">Superagent is currently scouting for optimal entry points.</p>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
}
