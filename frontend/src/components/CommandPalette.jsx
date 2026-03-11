import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search, LayoutDashboard, BarChart2, Compass, Briefcase, Zap,
    Terminal, Bot, Settings, Play, Square, TrendingUp
} from 'lucide-react';
import { BASE_URL } from '../api';

const PAGES = [
    { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, keywords: 'home overview portfolio' },
    { id: 'market', label: 'Market', path: '/market', icon: BarChart2, keywords: 'chart candle ohlcv' },
    { id: 'discover', label: 'Discover', path: '/discover', icon: Compass, keywords: 'explore sector stocks' },
    { id: 'portfolio', label: 'Portfolio', path: '/portfolio', icon: Briefcase, keywords: 'holdings positions pnl' },
    { id: 'trade', label: 'Trade Executor', path: '/trade', icon: Zap, keywords: 'buy sell order' },
    { id: 'god-mode', label: 'God Mode', path: '/god-mode', icon: Terminal, keywords: 'neural feed agent thoughts' },
    { id: 'autonomous', label: 'Autonomous Control', path: '/autonomous', icon: Bot, keywords: 'agent start stop' },
    { id: 'settings', label: 'Control Center', path: '/settings', icon: Settings, keywords: 'risk appetite config' },
];

const ACTIONS = [
    { id: 'start-agent', label: 'Start Autonomous Agent', icon: Play, keywords: 'start run agent autonomous', action: 'start' },
    { id: 'stop-agent', label: 'Stop Autonomous Agent', icon: Square, keywords: 'stop halt agent autonomous', action: 'stop' },
];

const POPULAR_TICKERS = [
    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'ITC', 'SBIN',
    'BHARTIARTL', 'KOTAKBANK', 'WIPRO', 'TATAMOTORS', 'SUNPHARMA',
    'MARUTI', 'TATASTEEL', 'HCLTECH', 'BAJFINANCE', 'LT', 'AXISBANK',
];

export default function CommandPalette({ open, onClose }) {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef(null);
    const navigate = useNavigate();

    const filteredPages = PAGES.filter(p =>
        `${p.label} ${p.keywords}`.toLowerCase().includes(query.toLowerCase())
    );

    const filteredActions = ACTIONS.filter(a =>
        `${a.label} ${a.keywords}`.toLowerCase().includes(query.toLowerCase())
    );

    const filteredTickers = query.length >= 1
        ? POPULAR_TICKERS.filter(t => t.toLowerCase().startsWith(query.toLowerCase())).slice(0, 5)
        : [];

    const allResults = [
        ...filteredPages.map(p => ({ type: 'page', ...p })),
        ...filteredActions.map(a => ({ type: 'action', ...a })),
        ...filteredTickers.map(t => ({ type: 'ticker', id: t, label: `${t}.NS`, icon: TrendingUp, path: `/market?ticker=${t}.NS` })),
    ];

    const handleSelect = useCallback(async (item) => {
        onClose();
        setQuery('');
        if (item.type === 'action') {
            const endpoint = item.action === 'start' ? '/api/agent/start' : '/api/agent/stop';
            try { await fetch(`${BASE_URL}${endpoint}`, { method: 'POST' }); } catch {}
        } else {
            navigate(item.path);
        }
    }, [navigate, onClose]);

    useEffect(() => {
        if (open) {
            setQuery('');
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }, [open]);

    useEffect(() => { setSelectedIndex(0); }, [query]);

    const handleKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(i => Math.min(i + 1, allResults.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(i => Math.max(i - 1, 0));
        } else if (e.key === 'Enter' && allResults[selectedIndex]) {
            handleSelect(allResults[selectedIndex]);
        } else if (e.key === 'Escape') {
            onClose();
        }
    };

    return (
        <AnimatePresence>
            {open && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.15 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                        onClick={onClose}
                    />

                    {/* Palette */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -20 }}
                        transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                        className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-lg z-50"
                    >
                        <div className="bg-dark-card border border-dark-border rounded-2xl shadow-2xl shadow-black/40 overflow-hidden">
                            {/* Search Input */}
                            <div className="flex items-center px-4 border-b border-dark-border">
                                <Search size={18} className="text-dark-muted flex-shrink-0" />
                                <input
                                    ref={inputRef}
                                    value={query}
                                    onChange={e => setQuery(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Search pages, tickers, or actions..."
                                    className="flex-1 bg-transparent border-none outline-none px-3 py-4 text-sm text-dark-text placeholder:text-dark-muted/50"
                                />
                                <kbd className="text-[10px] text-dark-muted bg-dark-bg px-1.5 py-0.5 rounded border border-dark-border font-mono">ESC</kbd>
                            </div>

                            {/* Results */}
                            <div className="max-h-72 overflow-y-auto p-2">
                                {allResults.length === 0 && (
                                    <p className="text-center text-dark-muted text-sm py-8">No results found</p>
                                )}

                                {filteredPages.length > 0 && (
                                    <div className="mb-1">
                                        <p className="text-[10px] font-bold text-dark-muted uppercase tracking-wider px-3 py-1.5">Pages</p>
                                        {filteredPages.map((item, i) => {
                                            const globalIdx = i;
                                            const Icon = item.icon;
                                            return (
                                                <button
                                                    key={item.id}
                                                    onClick={() => handleSelect({ type: 'page', ...item })}
                                                    className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors
                                                        ${selectedIndex === globalIdx ? 'bg-accent-green/10 text-accent-green' : 'text-dark-text hover:bg-dark-hover'}`}
                                                >
                                                    <Icon size={16} className="mr-3 flex-shrink-0" />
                                                    {item.label}
                                                </button>
                                            );
                                        })}
                                    </div>
                                )}

                                {filteredActions.length > 0 && (
                                    <div className="mb-1">
                                        <p className="text-[10px] font-bold text-dark-muted uppercase tracking-wider px-3 py-1.5">Actions</p>
                                        {filteredActions.map((item, i) => {
                                            const globalIdx = filteredPages.length + i;
                                            const Icon = item.icon;
                                            return (
                                                <button
                                                    key={item.id}
                                                    onClick={() => handleSelect({ type: 'action', ...item })}
                                                    className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm transition-colors
                                                        ${selectedIndex === globalIdx ? 'bg-accent-green/10 text-accent-green' : 'text-dark-text hover:bg-dark-hover'}`}
                                                >
                                                    <Icon size={16} className="mr-3 flex-shrink-0" />
                                                    {item.label}
                                                </button>
                                            );
                                        })}
                                    </div>
                                )}

                                {filteredTickers.length > 0 && (
                                    <div>
                                        <p className="text-[10px] font-bold text-dark-muted uppercase tracking-wider px-3 py-1.5">Tickers</p>
                                        {filteredTickers.map((t, i) => {
                                            const globalIdx = filteredPages.length + filteredActions.length + i;
                                            return (
                                                <button
                                                    key={t}
                                                    onClick={() => handleSelect({ type: 'ticker', path: `/market?ticker=${t}.NS` })}
                                                    className={`w-full flex items-center px-3 py-2.5 rounded-lg text-sm font-mono transition-colors
                                                        ${selectedIndex === globalIdx ? 'bg-accent-green/10 text-accent-green' : 'text-dark-text hover:bg-dark-hover'}`}
                                                >
                                                    <TrendingUp size={16} className="mr-3 flex-shrink-0" />
                                                    {t}<span className="text-dark-muted">.NS</span>
                                                </button>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="px-4 py-2.5 border-t border-dark-border flex items-center justify-between text-[10px] text-dark-muted">
                                <div className="flex items-center gap-3">
                                    <span><kbd className="bg-dark-bg px-1 py-0.5 rounded border border-dark-border font-mono">↑↓</kbd> Navigate</span>
                                    <span><kbd className="bg-dark-bg px-1 py-0.5 rounded border border-dark-border font-mono">↵</kbd> Select</span>
                                </div>
                                <span>Sentinel Command Palette</span>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
