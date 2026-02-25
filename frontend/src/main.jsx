import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './Layout.jsx'
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

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route element={<Layout />}>
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
        </BrowserRouter>
    </React.StrictMode>,
)
