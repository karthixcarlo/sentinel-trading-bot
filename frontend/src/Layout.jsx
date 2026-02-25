import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import CopilotSidebar from './components/CopilotSidebar';

export default function Layout() {
    return (
        <div className="flex bg-groww-light-gray min-h-screen font-sans">
            <Sidebar />
            <main className="flex-1 md:ml-64 relative">
                <Outlet />
            </main>
            <CopilotSidebar />
        </div>
    );
}
