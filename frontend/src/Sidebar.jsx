import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard, BarChart2, Compass, Briefcase, Zap,
    Terminal, Bot, Settings as SettingsIcon, Cpu, LogOut, Command, Sun, Moon
} from 'lucide-react';
import { useAuth } from './AuthContext';
import { useTheme } from './ThemeContext';

const NAV_ITEMS = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/market', icon: BarChart2, label: 'Market' },
    { to: '/discover', icon: Compass, label: 'Discover' },
    { to: '/portfolio', icon: Briefcase, label: 'Portfolio' },
    { to: '/trade', icon: Zap, label: 'Trade' },
    { to: '/god-mode', icon: Terminal, label: 'God Mode' },
    { to: '/autonomous', icon: Bot, label: 'Autonomous' },
    { to: '/settings', icon: SettingsIcon, label: 'Control Center' },
];

export default function Sidebar({ onCommandPalette }) {
    const { user, signOut } = useAuth();
    const { isDark, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const displayEmail = user?.email || 'demo@sentinel.ai';
    const displayName = user ? displayEmail.split('@')[0] : 'Demo User';
    const avatar = displayName.charAt(0).toUpperCase();

    const handleLogout = async () => {
        if (signOut) await signOut();
        navigate('/auth');
    };

    return (
        <div className="w-64 bg-dark-bg border-r border-dark-border h-screen fixed top-0 left-0 hidden md:flex flex-col z-40">
            {/* Logo */}
            <div className="p-6 border-b border-dark-border">
                <h1 className="text-2xl font-bold text-dark-text flex items-center">
                    <Cpu className="text-accent-green mr-2" size={24} /> Sentinel
                </h1>
                <p className="text-xs text-dark-muted mt-1 font-mono">v3.0</p>
            </div>

            {/* Theme Toggle + Quick Search */}
            <div className="px-4 pt-4 flex items-center gap-2">
                <button
                    onClick={toggleTheme}
                    title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                    aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                    className="p-2 rounded-lg border border-dark-border text-dark-muted
                        hover:border-accent-green/30 hover:text-accent-green transition-all duration-200"
                >
                    {isDark ? <Sun size={16} /> : <Moon size={16} />}
                </button>
            </div>

            <div className="px-4 pt-2">
                <button
                    onClick={onCommandPalette}
                    aria-label="Open command palette"
                    className="w-full flex items-center px-3 py-2 rounded-lg border border-dark-border text-dark-muted text-xs
                        hover:border-accent-green/30 hover:text-dark-text transition-colors"
                >
                    <Command size={13} className="mr-2" />
                    <span className="flex-1 text-left">Search...</span>
                    <kbd className="text-[10px] bg-dark-bg px-1.5 py-0.5 rounded border border-dark-border font-mono">⌘K</kbd>
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center px-4 py-2.5 rounded-lg font-semibold transition-all duration-200 text-sm ${isActive
                                ? 'bg-accent-green/10 text-accent-green'
                                : 'text-dark-muted hover:bg-dark-hover hover:text-dark-text'
                            }`
                        }
                    >
                        <Icon size={18} className="mr-3 flex-shrink-0" />
                        {label}
                    </NavLink>
                ))}
            </nav>

            {/* User Info + Logout */}
            <div className="p-4 border-t border-dark-border">
                <div className="flex items-center justify-between">
                    <div className="flex items-center min-w-0">
                        <div className="w-8 h-8 rounded-full bg-accent-green/15 text-accent-green flex items-center justify-center font-bold mr-3 text-sm flex-shrink-0">
                            {avatar}
                        </div>
                        <div className="min-w-0">
                            <p className="text-sm font-bold text-dark-text truncate">{displayName}</p>
                            <p className="text-xs text-dark-muted truncate">{displayEmail}</p>
                        </div>
                    </div>
                    {user && (
                        <button
                            onClick={handleLogout}
                            title="Log out"
                            aria-label="Log out"
                            className="ml-2 p-1.5 rounded-lg text-dark-muted hover:text-accent-red hover:bg-accent-red/10 transition-colors flex-shrink-0"
                        >
                            <LogOut size={15} />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
