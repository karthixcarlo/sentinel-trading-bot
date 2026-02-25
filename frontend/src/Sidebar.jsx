import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard, BarChart2, Compass, Briefcase, Zap,
    Terminal, Bot, Settings as SettingsIcon, Cpu, LogOut
} from 'lucide-react';
import { useAuth } from './AuthContext';

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

export default function Sidebar() {
    return (
        <div className="w-64 bg-white border-r border-groww-gray/20 h-screen fixed top-0 left-0 hidden md:flex flex-col shadow-sm z-40">
            {/* Logo */}
            <div className="p-6 border-b border-groww-gray/10">
                <h1 className="text-2xl font-bold text-groww-dark flex items-center">
                    <Cpu className="text-groww-green mr-2" size={24} /> Sentinel
                </h1>
                <p className="text-xs text-groww-gray mt-1 font-mono">v2.0 Beta</p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) =>
                            `flex items-center px-4 py-3 rounded-lg font-bold transition-colors text-sm ${isActive
                                ? 'bg-groww-light-gray text-groww-dark'
                                : 'text-groww-gray hover:bg-groww-light-gray/50 hover:text-groww-dark'
                            }`
                        }
                    >
                        <Icon size={18} className="mr-3 flex-shrink-0" />
                        {label}
                    </NavLink>
                ))}
            </nav>

            {/* User Info */}
            <div className="p-4 border-t border-groww-gray/10">
                <div className="flex items-center">
                    <div className="w-8 h-8 rounded-full bg-groww-green/20 text-groww-green flex items-center justify-center font-bold mr-3 text-sm">
                        D
                    </div>
                    <div>
                        <p className="text-sm font-bold text-groww-dark">Demo User</p>
                        <p className="text-xs text-groww-gray">demo@sentinel.ai</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
