import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
// Change BACKEND_PORT if you start uvicorn on a different port
const BACKEND_PORT = 8001;

export default defineConfig({
    plugins: [react()],
    resolve: {
        conditions: ['import', 'browser', 'module', 'jsnext:main', 'jsnext'],
    },
    optimizeDeps: {
        include: ['@supabase/supabase-js'],
    },
    server: {
        port: 5173,
        open: true,
        proxy: {
            '/api': {
                target: `http://localhost:${BACKEND_PORT}`,
                changeOrigin: true,
            },
            '/ws': {
                target: `ws://localhost:${BACKEND_PORT}`,
                ws: true,
                changeOrigin: true,
            },
        },
    },
})
