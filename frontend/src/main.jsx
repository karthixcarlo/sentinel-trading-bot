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
import { ErrorBoundary } from './components/ErrorBoundary.jsx'
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
                    <Route element={<ProtectedRoute><ErrorBoundary fallbackMessage="The app encountered an unexpected error. Click below to retry."><Layout /></ErrorBoundary></ProtectedRoute>}>
                        <Route path="/dashboard" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
                        <Route path="/market" element={<ErrorBoundary><Market /></ErrorBoundary>} />
                        <Route path="/discover" element={<ErrorBoundary><Discover /></ErrorBoundary>} />
                        <Route path="/analyze/:ticker" element={<ErrorBoundary><Analyze /></ErrorBoundary>} />
                        <Route path="/portfolio" element={<ErrorBoundary><Portfolio /></ErrorBoundary>} />
                        <Route path="/trade" element={<ErrorBoundary><TradeExecutor /></ErrorBoundary>} />
                        <Route path="/god-mode" element={<ErrorBoundary><GodMode /></ErrorBoundary>} />
                        <Route path="/autonomous" element={<ErrorBoundary><AutonomousControl /></ErrorBoundary>} />
                        <Route path="/settings" element={<ErrorBoundary><Settings /></ErrorBoundary>} />
                    </Route>
                </Routes>
            </AuthProvider>
        </BrowserRouter>
        </ThemeProvider>
    </React.StrictMode>,
)
