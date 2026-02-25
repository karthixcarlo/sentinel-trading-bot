import React, { useEffect, useState, useMemo } from 'react';
import { Briefcase, Activity, AlertCircle, ArrowUpRight, ShieldCheck } from 'lucide-react';
import TradingChart from './components/TradingChart';

export default function Dashboard() {
    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const userId = "demo_user";
        fetch(`/api/portfolio/${userId}`)
            .then(res => res.json())
            .then(data => {
                // Ensure valid structure (API may return error object or missing fields)
                const cash = data?.cash ?? 100000;
                const positions = Array.isArray(data?.positions) ? data.positions : [];
                const orders = Array.isArray(data?.orders) ? data.orders : [];
                setPortfolio({ cash, positions, orders });
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching portfolio", err);
                setPortfolio({ cash: 100000, positions: [], orders: [] });
                setLoading(false);
            });
    }, []);

    // VERCEL BEST PRACTICE: rerender-memo - Memoize derived expensive calculations
    const portfolioValue = useMemo(() => {
        if (!portfolio) return 0;
        const cash = portfolio.cash ?? 100000;
        const positions = portfolio.positions ?? [];
        return positions.reduce((acc, pos) => acc + (pos.quantity * pos.current_price), cash);
    }, [portfolio]);

    // PREMIUM FRONTEND: Skeleton loaders to prevent layout shift
    if (loading) {
        return (
            <div className="min-h-screen bg-[#F8F9FA] p-6 lg:p-10 font-sans">
                <div className="animate-pulse space-y-8 max-w-7xl mx-auto">
                    <div className="space-y-3">
                        <div className="h-8 bg-black/5 rounded w-1/4"></div>
                        <div className="h-4 bg-black/5 rounded w-1/3"></div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-32 bg-white border border-black/5 rounded-2xl shadow-sm"></div>
                        ))}
                    </div>
                    <div className="h-[400px] bg-white border border-black/5 rounded-2xl shadow-sm"></div>
                </div>
            </div>
        );
    }

    if (!portfolio && !loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-[#F8F9FA] text-[#EB5B3C]">
                <AlertCircle className="mb-4 h-12 w-12" />
                <h2 className="text-xl font-bold text-[#111111]">Connection Interrupted</h2>
                <p className="text-[#444444] mt-2">Failed to load live portfolio data from Neural Core.</p>
            </div>
        );
    }

    const { cash, positions } = portfolio;

    return (
        <div className="min-h-screen bg-[#F8F9FA] font-sans text-[#111111] p-6 lg:p-10">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#111111]">Dashboard</h1>
                        <p className="text-[#444444] mt-1 text-sm md:text-base flex items-center">
                            Welcome back. <ShieldCheck size={16} className="ml-2 mr-1 text-[#00D09C]" /> Neural Core Online
                        </p>
                    </div>
                    <div className="bg-white px-4 py-2 rounded-lg border border-black/5 shadow-sm inline-flex items-center text-sm font-bold text-[#444444]">
                        <div className="w-2 h-2 rounded-full bg-[#00D09C] animate-pulse mr-2"></div>
                        Live Market Sync
                    </div>
                </header>

                {/* Premium Metrics Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="bg-white rounded-2xl border border-black/5 p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-[#00D09C]/5 rounded-bl-[100px] -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div className="text-sm font-medium text-[#444444] mb-2 relative z-10">Total Portfolio Value</div>
                        <div className="text-3xl font-bold font-mono tracking-tight text-[#111111] relative z-10">₹{portfolioValue.toLocaleString()}</div>
                        <div className="text-[#00D09C] text-sm flex items-center mt-3 font-bold bg-[#00D09C]/10 w-max px-2 py-1 rounded-md relative z-10">
                            <ArrowUpRight size={16} className="mr-1" /> +2.1% All Time
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl border border-black/5 p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-black/5 rounded-bl-[100px] -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div className="text-sm font-medium text-[#444444] mb-2 relative z-10">Available Trading Cash</div>
                        <div className="text-3xl font-bold font-mono tracking-tight text-[#111111] relative z-10">₹{cash.toLocaleString()}</div>
                    </div>

                    <div className="bg-white rounded-2xl border border-black/5 p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-[#444444]/5 rounded-bl-[100px] -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>
                        <div className="text-sm font-medium text-[#444444] mb-2 relative z-10">Active Superagent Positions</div>
                        <div className="text-3xl font-bold font-mono tracking-tight text-[#111111] relative z-10">{positions.length} Assets</div>
                    </div>
                </div>

                {/* Advanced Chart Section */}
                <div className="relative z-10 hover:shadow-lg transition-shadow duration-300 rounded-xl">
                    <TradingChart symbol="RELIANCE.NS" userId="demo_user" />
                </div>

                {/* Holdings Table */}
                <div className="bg-white rounded-2xl border border-black/5 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300">
                    <div className="p-6 border-b border-black/5 flex items-center justify-between bg-white">
                        <h2 className="text-lg font-bold flex items-center text-[#111111]">
                            <Briefcase size={20} className="mr-2 text-[#444444]" /> Current Holdings
                        </h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-[#F8F9FA] text-[#444444] text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-bold">Asset</th>
                                    <th className="px-6 py-4 font-bold text-right">Quantity</th>
                                    <th className="px-6 py-4 font-bold text-right">Avg Price</th>
                                    <th className="px-6 py-4 font-bold text-right">Total Value</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-black/5">
                                {positions.map((pos, idx) => {
                                    const total = pos.quantity * pos.current_price;
                                    return (
                                        <tr key={idx} className="hover:bg-[#F8F9FA] transition-colors group cursor-default">
                                            <td className="px-6 py-5 font-bold text-[#111111] flex items-center">
                                                <div className="w-8 h-8 rounded-full bg-[#111111]/5 flex items-center justify-center mr-3 text-xs group-hover:bg-[#00D09C]/10 group-hover:text-[#00D09C] transition-colors">
                                                    {pos.symbol.charAt(0)}
                                                </div>
                                                {pos.symbol}
                                            </td>
                                            <td className="px-6 py-5 font-mono text-right text-[#444444]">{pos.quantity}</td>
                                            <td className="px-6 py-5 font-mono text-right text-[#444444]">₹{pos.current_price.toLocaleString()}</td>
                                            <td className="px-6 py-5 font-mono text-right font-bold text-[#111111]">₹{total.toLocaleString()}</td>
                                        </tr>
                                    );
                                })}
                                {positions.length === 0 && (
                                    <tr>
                                        <td colSpan="4" className="px-6 py-12 text-center text-[#444444]">
                                            <div className="flex flex-col items-center justify-center">
                                                <div className="w-16 h-16 bg-[#F8F9FA] rounded-full flex items-center justify-center mb-3">
                                                    <Briefcase className="text-[#444444]/50" size={24} />
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
