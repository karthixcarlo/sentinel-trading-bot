import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext.jsx'
import { ThemeProvider } from './ThemeContext.jsx'
import { supabase } from './supabaseClient.js'
import Layout from './Layout.jsx'
import Auth from './Auth.jsx'
import Dashboard from './Dashboard.jsx'
import Market from './Market.jsx'
import Discover from './Discover.jsx'
import Analyze from './Analyze.jsx'
import Portfolio from './Portfolio.jsx'
import TradeExecutor from './TradeExecutor.jsx'
import GodMode from './GodMode.jsx'
import AutonomousControl from './AutonomousControl.jsx'
import Settings from './Settings.jsx'
import './index.css'

function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    if (loading) {
        return (
            <div className="min-h-screen bg-dark-bg flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-accent-green/30 border-t-accent-green rounded-full animate-spin" />
            </div>
        );
    }
    // Demo mode (no Supabase configured), demo user bypass, or authenticated — allow through
    if (!supabase || user) return children;
    return <Navigate to="/auth" replace />;
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ThemeProvider>
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/auth" element={<Auth />} />
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/market" element={<Market />} />
                        <Route path="/discover" element={<Discover />} />
                        <Route path="/analyze/:ticker" element={<Analyze />} />
                        <Route path="/portfolio" element={<Portfolio />} />
                        <Route path="/trade" element={<TradeExecutor />} />
                        <Route path="/god-mode" element={<GodMode />} />
                        <Route path="/autonomous" element={<AutonomousControl />} />
                        <Route path="/settings" element={<Settings />} />
                    </Route>
                </Routes>
            </AuthProvider>
        </BrowserRouter>
        </ThemeProvider>
    </React.StrictMode>,
)
