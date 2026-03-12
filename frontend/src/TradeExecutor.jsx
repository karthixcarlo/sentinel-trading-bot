import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Zap, AlertCircle, CheckCircle, ArrowLeft, ChevronDown } from 'lucide-react';
import { BASE_URL } from './api';

export default function TradeExecutor() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const [symbol, setSymbol] = useState(searchParams.get('symbol') || '');
    const [action, setAction] = useState(searchParams.get('action') || 'BUY');
    const [quantity, setQuantity] = useState(1);
    const [orderType, setOrderType] = useState('MARKET');
    const [limitPrice, setLimitPrice] = useState('');
    const [portfolio, setPortfolio] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const [previewPrice, setPreviewPrice] = useState(null);

    const refreshPortfolio = () => {
        fetch(`${BASE_URL}/api/portfolio/demo_user/detail`)
            .then(r => { if (!r.ok) throw new Error('non-2xx'); return r.json(); })
            .then(setPortfolio)
            .catch(() => setPortfolio({ cash: 100000, portfolio_value: 100000, positions: [] }));
    };

    useEffect(() => { refreshPortfolio(); }, []);

    // Debounced live price preview
    useEffect(() => {
        if (!symbol || symbol.length < 2) { setPreviewPrice(null); return; }
        const t = setTimeout(() => {
            fetch(`${BASE_URL}/api/market/ohlcv/${symbol}.NS`)
                .then(r => r.json())
                .then(data => {
                    if (data.ohlc && data.ohlc.length > 0)
                        setPreviewPrice(data.ohlc[data.ohlc.length - 1].close);
                }).catch(() => setPreviewPrice(null));
        }, 600);
        return () => clearTimeout(t);
    }, [symbol]);

    const execPrice = orderType === 'MARKET' ? (previewPrice || 0) : parseFloat(limitPrice || 0);
    const totalCost = quantity * execPrice;
    const brokerage = +(totalCost * 0.0003).toFixed(2);
    const finalAmt = +(totalCost + (action === 'BUY' ? brokerage : -brokerage)).toFixed(2);
    const cash = portfolio?.cash || 0;
    const insufficientFunds = action === 'BUY' && cash < finalAmt && execPrice > 0;

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!symbol.trim()) return;
        setSubmitting(true);
        setResult(null);
        try {
            const body = {
                user_id: 'demo_user',
                symbol: symbol.toUpperCase().trim(),
                action,
                quantity: parseInt(quantity),
                order_type: orderType,
                limit_price: orderType === 'LIMIT' ? parseFloat(limitPrice) : null,
            };
            const res = await fetch(`${BASE_URL}/api/trade/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await res.json();
            if (res.ok) {
                setResult({ ok: true, message: data.message });
                setSymbol(''); setQuantity(1); setLimitPrice(''); setPreviewPrice(null);
                refreshPortfolio();
            } else {
                setResult({ ok: false, message: data.detail || 'Trade failed' });
            }
        } catch (err) {
            setResult({ ok: false, message: `Connection error: ${err.message}` });
        }
        setSubmitting(false);
    };

    const isBuy = action === 'BUY';

    return (
        <div className="min-h-screen bg-groww-light-gray p-6 lg:p-10 font-sans text-groww-dark">
            <div className="max-w-3xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <button onClick={() => navigate(-1)} className="flex items-center text-groww-gray hover:text-groww-dark font-bold mb-4 text-sm transition-colors">
                        <ArrowLeft size={18} className="mr-1.5" /> Back
                    </button>
                    <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center gap-3">
                        <Zap size={30} className="text-groww-green" /> Trade Executor
                    </h1>
                    <p className="text-groww-gray mt-1 text-sm">Execute market or limit orders on your portfolio</p>
                </div>

                {/* Portfolio Snapshot */}
                {portfolio && (
                    <div className="grid grid-cols-3 gap-4">
                        {[
                            { label: 'Cash Available', value: `₹${portfolio.cash.toLocaleString('en-IN', { maximumFractionDigits: 0 })}` },
                            { label: 'Portfolio Value', value: `₹${portfolio.portfolio_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}` },
                            { label: 'Positions', value: portfolio.positions.length },
                        ].map(m => (
                            <div key={m.label} className="bg-[#0A0A0A] rounded-xl border border-groww-gray/10 p-4 shadow-sm text-center">
                                <p className="text-xs text-groww-gray font-medium mb-1">{m.label}</p>
                                <p className="text-lg font-bold font-mono text-groww-dark">{m.value}</p>
                            </div>
                        ))}
                    </div>
                )}

                {/* Result Banner */}
                {result && (
                    <div className={`flex items-start p-4 rounded-xl border text-sm font-medium ${result.ok ? 'bg-groww-green/10 border-groww-green/20 text-groww-green' : 'bg-groww-red/10 border-groww-red/20 text-groww-red'}`}>
                        {result.ok
                            ? <CheckCircle size={18} className="mr-2 flex-shrink-0 mt-0.5" />
                            : <AlertCircle size={18} className="mr-2 flex-shrink-0 mt-0.5" />}
                        <span>{result.message}</span>
                    </div>
                )}

                {/* Trade Form */}
                <form onSubmit={handleSubmit} className="bg-[#0A0A0A] rounded-2xl border border-groww-gray/10 shadow-sm p-8 space-y-6">

                    {/* BUY / SELL Toggle */}
                    <div>
                        <label className="block text-xs font-bold text-groww-gray uppercase tracking-wider mb-3">Order Side</label>
                        <div className="flex rounded-xl overflow-hidden border border-groww-gray/10">
                            <button type="button" onClick={() => setAction('BUY')}
                                className={`flex-1 py-3 font-bold text-sm transition-colors ${isBuy ? 'bg-groww-green text-white' : 'bg-groww-light-gray text-groww-gray hover:bg-groww-gray/10'}`}>
                                BUY
                            </button>
                            <button type="button" onClick={() => setAction('SELL')}
                                className={`flex-1 py-3 font-bold text-sm transition-colors ${!isBuy ? 'bg-groww-red text-white' : 'bg-groww-light-gray text-groww-gray hover:bg-groww-gray/10'}`}>
                                SELL
                            </button>
                        </div>
                    </div>

                    {/* Symbol input */}
                    <div>
                        <label className="block text-xs font-bold text-groww-gray uppercase tracking-wider mb-3">Stock Symbol</label>
                        <div className="relative">
                            <input
                                value={symbol}
                                onChange={e => setSymbol(e.target.value.toUpperCase())}
                                placeholder="e.g. RELIANCE, TCS, INFY"
                                required
                                className="w-full px-4 py-3.5 border border-groww-gray/20 rounded-xl text-groww-dark font-bold focus:outline-none focus:border-groww-green focus:ring-2 focus:ring-groww-green/20 placeholder:font-normal placeholder:text-groww-gray/40 transition-all"
                            />
                            {previewPrice && (
                                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-groww-green bg-groww-green/10 px-3 py-1 rounded-lg">
                                    LTP: ₹{previewPrice.toLocaleString('en-IN')}
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {/* Quantity */}
                        <div>
                            <label className="block text-xs font-bold text-groww-gray uppercase tracking-wider mb-3">Quantity</label>
                            <input type="number" min={1} value={quantity} onChange={e => setQuantity(e.target.value)} required
                                className="w-full px-4 py-3.5 border border-groww-gray/20 rounded-xl font-bold text-groww-dark focus:outline-none focus:border-groww-green focus:ring-2 focus:ring-groww-green/20 transition-all" />
                        </div>

                        {/* Order Type */}
                        <div>
                            <label className="block text-xs font-bold text-groww-gray uppercase tracking-wider mb-3">Order Type</label>
                            <div className="relative">
                                <select value={orderType} onChange={e => setOrderType(e.target.value)}
                                    className="w-full px-4 py-3.5 border border-groww-gray/20 rounded-xl font-bold text-groww-dark appearance-none focus:outline-none focus:border-groww-green focus:ring-2 focus:ring-groww-green/20 transition-all bg-[#0A0A0A]">
                                    <option value="MARKET">Market Order</option>
                                    <option value="LIMIT">Limit Order</option>
                                </select>
                                <ChevronDown size={16} className="absolute right-4 top-1/2 -translate-y-1/2 text-groww-gray pointer-events-none" />
                            </div>
                        </div>
                    </div>

                    {/* Limit Price */}
                    {orderType === 'LIMIT' && (
                        <div>
                            <label className="block text-xs font-bold text-groww-gray uppercase tracking-wider mb-3">Limit Price (₹)</label>
                            <input type="number" step="0.01" min="0.01" value={limitPrice} onChange={e => setLimitPrice(e.target.value)} required
                                className="w-full px-4 py-3.5 border border-groww-gray/20 rounded-xl font-bold text-groww-dark focus:outline-none focus:border-groww-green focus:ring-2 focus:ring-groww-green/20 transition-all" />
                        </div>
                    )}

                    {/* Order Summary */}
                    {execPrice > 0 && (
                        <div className="bg-groww-light-gray rounded-xl p-4 space-y-2 text-sm border border-groww-gray/10">
                            <p className="font-bold text-groww-gray uppercase tracking-wider text-xs mb-3">Order Summary</p>
                            {[
                                ['Execution Price', `₹${execPrice.toLocaleString('en-IN')}`],
                                ['Quantity', `${quantity} shares`],
                                ['Gross Amount', `₹${totalCost.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`],
                                ['Brokerage (0.03%)', `₹${brokerage.toFixed(2)}`],
                            ].map(([label, val]) => (
                                <div key={label} className="flex justify-between">
                                    <span className="text-groww-gray">{label}</span>
                                    <span className="font-mono font-bold text-groww-dark">{val}</span>
                                </div>
                            ))}
                            <div className="flex justify-between pt-2 border-t border-groww-gray/10">
                                <span className="font-bold text-groww-dark">{isBuy ? 'Total Cost' : 'Net Proceeds'}</span>
                                <span className={`font-mono font-bold text-base ${insufficientFunds ? 'text-groww-red' : 'text-groww-dark'}`}>
                                    ₹{finalAmt.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                                </span>
                            </div>
                            {insufficientFunds && (
                                <p className="text-groww-red text-xs font-bold flex items-center">
                                    <AlertCircle size={12} className="mr-1" />
                                    Insufficient funds — need ₹{(finalAmt - cash).toLocaleString('en-IN', { maximumFractionDigits: 0 })} more
                                </p>
                            )}
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={submitting || insufficientFunds}
                        className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${submitting || insufficientFunds
                                ? 'bg-groww-gray/20 text-groww-gray cursor-not-allowed'
                                : isBuy
                                    ? 'bg-groww-green text-white hover:opacity-90 shadow-lg shadow-groww-green/20'
                                    : 'bg-groww-red text-white hover:opacity-90 shadow-lg shadow-groww-red/20'
                            }`}
                    >
                        {submitting ? 'Executing…' : `Place ${action} Order`}
                    </button>
                </form>

            </div>
        </div>
    );
}
