import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpRight, ArrowDownRight, Search, Activity, TrendingUp, Filter } from 'lucide-react';
import TradingChart from './components/TradingChart';
import { BASE_URL } from './api';

export default function Discover() {
    const navigate = useNavigate();
    const [marketData, setMarketData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('ALL'); // 'ALL', 'GAINERS', 'LOSERS'

    useEffect(() => {
        setLoading(true);
        fetch(`${BASE_URL}/api/market/discover`)
            .then(res => res.json())
            .then(data => {
                setMarketData(Array.isArray(data) ? data : []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching live market data:", err);
                setMarketData([]);
                setLoading(false);
            });
    }, []);

    const filteredData = (Array.isArray(marketData) ? marketData : []).filter(stock => {
        const matchesSearch = stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
            stock.name.toLowerCase().includes(searchTerm.toLowerCase());

        if (filter === 'GAINERS') return matchesSearch && stock.change > 0;
        if (filter === 'LOSERS') return matchesSearch && stock.change < 0;
        return matchesSearch;
    });

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-groww-light-gray text-groww-gray">
                <Activity className="animate-spin mb-4" size={32} />
                <p>Scanning the NSE Universe...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-groww-light-gray font-sans text-groww-dark p-6">

            {/* Header & Controls */}
            <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-groww-dark flex items-center">
                        <TrendingUp className="mr-3 text-groww-green" size={28} /> Stock Discovery
                    </h1>
                    <p className="text-groww-gray mt-1">Explore live NSE equities and uncover new opportunities.</p>
                </div>

                <div className="flex items-center gap-3">
                    {/* Filter Pills */}
                    <div className="flex bg-[#0A0A0A] rounded-lg border border-groww-gray/20 p-1">
                        {['ALL', 'GAINERS', 'LOSERS'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-2 rounded-md text-sm font-bold transition-colors ${filter === f
                                    ? 'bg-groww-green text-white'
                                    : 'text-groww-gray hover:bg-groww-light-gray/50'
                                    }`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>
                </div>
            </header>

            {/* Professional Candlestick Chart */}
            <div className="mb-8">
                <TradingChart symbol="RELIANCE.NS" userId="demo_user" />
            </div>

            {/* Search Bar */}
            <div className="relative mb-8 max-w-2xl bg-[#0A0A0A] border-2 border-groww-gray/20 rounded-xl overflow-hidden focus-within:border-groww-green transition-colors shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="text-groww-gray" size={20} />
                </div>
                <input
                    type="text"
                    placeholder="Search by company name or symbol (e.g., RELIANCE, TCS)..."
                    className="w-full pl-12 pr-4 py-4 text-groww-dark font-medium border-none focus:outline-none focus:ring-0"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            {/* Grid of Stock Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {filteredData.map((stock) => {
                    const isPositive = stock.change >= 0;
                    return (
                        <div
                            key={stock.symbol}
                            className="bg-[#0A0A0A] p-6 rounded-xl border border-groww-gray/20 shadow-sm hover:shadow-md hover:border-groww-green transition-all cursor-pointer group"
                            // Navigate to the dynamic analyzer routing page
                            onClick={() => navigate(`/analyze/${stock.symbol}`)}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="font-bold text-lg text-groww-dark">{stock.symbol}</h3>
                                    <p className="text-sm text-groww-gray mt-1">{stock.name}</p>
                                </div>
                                <button className="bg-groww-light-gray text-groww-dark hover:bg-groww-green hover:text-white px-3 py-1 text-xs font-bold rounded-full transition-colors opacity-0 group-hover:opacity-100">
                                    Analyze
                                </button>
                            </div>

                            <div className="flex items-end justify-between mt-6">
                                <span className="text-2xl font-mono font-bold text-groww-dark">₹{stock.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                                <div className={`flex items-center text-sm font-bold ${isPositive ? 'text-groww-green' : 'text-groww-red'}`}>
                                    {isPositive ? <ArrowUpRight size={16} className="mr-1" /> : <ArrowDownRight size={16} className="mr-1" />}
                                    {isPositive ? '+' : ''}{stock.change}%
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {filteredData.length === 0 && (
                <div className="bg-[#0A0A0A] rounded-xl border border-groww-gray/20 p-12 text-center shadow-sm">
                    <Filter className="mx-auto h-12 w-12 text-groww-gray mb-4 opacity-50" />
                    <h3 className="text-lg font-bold text-groww-dark">No stocks found</h3>
                    <p className="text-groww-gray mt-2">Try adjusting your search terms or filters.</p>
                </div>
            )}

        </div>
    );
}
