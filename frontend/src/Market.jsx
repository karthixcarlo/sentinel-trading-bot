import React, { useEffect, useState } from 'react';
import { ArrowUpRight, ArrowDownRight, TrendingUp, Activity, BarChart2, RefreshCw } from 'lucide-react';
import { BASE_URL } from './api';

const DEMO_INDICES = [
    { name: "Nifty 50", value: 22150.50, change: 1.25 },
    { name: "Bank Nifty", value: 48250.75, change: -0.85 },
    { name: "Sensex", value: 73280.30, change: 0.95 },
];

function IndexCard({ index }) {
    const isUp = index.change >= 0;
    return (
        <div className="bg-white rounded-2xl border border-black/5 p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
            <div className={`absolute top-0 right-0 w-32 h-32 rounded-bl-[100px] -mr-8 -mt-8 transition-transform group-hover:scale-110 ${isUp ? 'bg-[#00D09C]/5' : 'bg-[#EB5B3C]/5'}`}></div>
            <p className="text-sm font-medium text-[#444444] mb-1 relative z-10">{index.name}</p>
            <p className="text-3xl font-bold font-mono text-[#111111] tracking-tight relative z-10">
                {index.value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </p>
            <div className={`mt-3 flex items-center text-sm font-bold relative z-10 w-max px-2 py-1 rounded-md ${isUp ? 'text-[#00D09C] bg-[#00D09C]/10' : 'text-[#EB5B3C] bg-[#EB5B3C]/10'}`}>
                {isUp ? <ArrowUpRight size={16} className="mr-1" /> : <ArrowDownRight size={16} className="mr-1" />}
                {isUp ? '+' : ''}{index.change.toFixed(2)}%
            </div>
        </div>
    );
}

export default function Market() {
    const [indices, setIndices] = useState(DEMO_INDICES);
    const [topStocks, setTopStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState(null);
    const [tab, setTab] = useState('GAINERS');

    const fetchData = () => {
        setLoading(true);
        Promise.all([
            fetch(`${BASE_URL}/api/market/indices`).then(r => r.json()),
            fetch(`${BASE_URL}/api/market/discover`).then(r => r.json()),
        ])
            .then(([idxData, stockData]) => {
                if (Array.isArray(idxData) && idxData.length > 0) setIndices(idxData);
                if (Array.isArray(stockData)) setTopStocks(stockData);
                setLastUpdated(new Date().toLocaleTimeString('en-IN'));
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => { fetchData(); }, []);

    const filtered = [...topStocks].sort((a, b) =>
        tab === 'GAINERS' ? b.change - a.change : a.change - b.change
    ).slice(0, 8);

    return (
        <div className="min-h-screen bg-[#F8F9FA] p-6 lg:p-10 font-sans text-[#111111]">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <header className="flex flex-col md:flex-row items-start md:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#111111] flex items-center">
                            <BarChart2 size={32} className="mr-3 text-[#00D09C]" /> Market Overview
                        </h1>
                        <p className="text-[#444444] mt-1 text-sm">
                            Live NSE/BSE indices and top movers
                            {lastUpdated && <span className="ml-2 text-[#00D09C] font-mono">• {lastUpdated}</span>}
                        </p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="flex items-center px-4 py-2 bg-white border border-black/5 rounded-lg text-sm font-bold text-[#444444] hover:bg-[#F8F9FA] shadow-sm transition-colors"
                    >
                        <RefreshCw size={15} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
                        {loading ? 'Refreshing...' : 'Refresh'}
                    </button>
                </header>

                {/* Index Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {indices.map(idx => <IndexCard key={idx.name} index={idx} />)}
                </div>

                {/* Top Movers */}
                <div className="bg-white rounded-2xl border border-black/5 overflow-hidden shadow-sm">
                    <div className="p-6 border-b border-black/5 flex items-center justify-between">
                        <h2 className="text-lg font-bold text-[#111111] flex items-center">
                            <TrendingUp size={20} className="mr-2 text-[#444444]" /> Top Movers
                        </h2>
                        <div className="flex bg-[#F8F9FA] rounded-lg border border-black/5 p-1">
                            {['GAINERS', 'LOSERS'].map(t => (
                                <button key={t} onClick={() => setTab(t)}
                                    className={`px-4 py-1.5 rounded-md text-xs font-bold transition-colors ${tab === t ? 'bg-[#111111] text-white' : 'text-[#444444] hover:bg-white'}`}>
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>

                    {loading ? (
                        <div className="p-6 animate-pulse space-y-4">
                            {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-10 bg-black/5 rounded-lg" />)}
                        </div>
                    ) : (
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-[#F8F9FA] text-[#444444] text-xs uppercase tracking-wider">
                                <tr>
                                    <th className="px-6 py-4 font-bold">Stock</th>
                                    <th className="px-6 py-4 font-bold text-right">LTP</th>
                                    <th className="px-6 py-4 font-bold text-right">Change</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-black/5">
                                {filtered.map(stock => {
                                    const isUp = stock.change >= 0;
                                    return (
                                        <tr key={stock.symbol} className="hover:bg-[#F8F9FA] transition-colors">
                                            <td className="px-6 py-4">
                                                <p className="font-bold text-[#111111]">{stock.symbol}</p>
                                                <p className="text-xs text-[#444444]">{stock.name}</p>
                                            </td>
                                            <td className="px-6 py-4 text-right font-mono font-bold text-[#111111]">
                                                ₹{stock.price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <span className={`inline-flex items-center text-sm font-bold px-2 py-1 rounded-md ${isUp ? 'text-[#00D09C] bg-[#00D09C]/10' : 'text-[#EB5B3C] bg-[#EB5B3C]/10'}`}>
                                                    {isUp ? <ArrowUpRight size={14} className="mr-1" /> : <ArrowDownRight size={14} className="mr-1" />}
                                                    {isUp ? '+' : ''}{stock.change.toFixed(2)}%
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Market Hours Card */}
                <div className="bg-[#111111] text-white rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="flex items-center">
                        <div className="w-10 h-10 rounded-full bg-[#00D09C]/20 flex items-center justify-center mr-4">
                            <Activity className="text-[#00D09C]" size={20} />
                        </div>
                        <div>
                            <p className="font-bold text-lg">NSE Market Hours</p>
                            <p className="text-white/60 text-sm">Monday – Friday, 9:15 AM – 3:30 PM IST</p>
                        </div>
                    </div>
                    <div className="flex flex-col items-end">
                        <p className="text-white/60 text-xs mb-1 uppercase tracking-widest">Current Time (IST)</p>
                        <p className="font-mono text-2xl font-bold text-[#00D09C]">
                            {new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </p>
                    </div>
                </div>

            </div>
        </div>
    );
}
