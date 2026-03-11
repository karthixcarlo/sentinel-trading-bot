import React, { useState, useEffect, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './Sidebar';
import CopilotSidebar from './components/CopilotSidebar';
import CommandPalette from './components/CommandPalette';
import ReasoningEngine from './components/ReasoningEngine';

const pageVariants = {
    initial: { opacity: 0, y: 6 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -4 },
};

export default function Layout() {
    const [cmdOpen, setCmdOpen] = useState(false);
    const location = useLocation();

    const openCommandPalette = useCallback(() => setCmdOpen(true), []);

    // Global Cmd/Ctrl+K listener
    useEffect(() => {
        const handler = (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setCmdOpen(prev => !prev);
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, []);

    return (
        <div className="flex bg-dark-bg min-h-screen font-sans">
            <Sidebar onCommandPalette={openCommandPalette} />

            <main className="flex-1 md:ml-64 relative">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={location.pathname}
                        variants={pageVariants}
                        initial="initial"
                        animate="animate"
                        exit="exit"
                        transition={{ duration: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
                    >
                        <Outlet />
                    </motion.div>
                </AnimatePresence>
            </main>

            <CopilotSidebar />
            <ReasoningEngine />
            <CommandPalette open={cmdOpen} onClose={() => setCmdOpen(false)} />
        </div>
    );
}
