/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Dark-first palette (Groww / TradingView inspired)
                'dark-bg':     '#0B0F19',
                'dark-card':   '#131722',
                'dark-hover':  '#1E2230',
                'dark-border': '#1E2636',
                'dark-text':   '#E1E5EA',
                'dark-muted':  '#6B7280',

                // Accent colors
                'accent-green': '#00D09C',
                'accent-red':   '#EB5B3C',
                'accent-blue':  '#3B82F6',
                'accent-amber': '#F59E0B',
                'accent-purple':'#8B5CF6',

                // Legacy aliases (backwards compat during migration)
                'groww-green':      '#00D09C',
                'groww-red':        '#EB5B3C',
                'groww-dark':       '#E1E5EA',
                'groww-gray':       '#6B7280',
                'groww-light-gray': '#1E2230',
                'brand-green':      '#00D09C',
                'brand-red':        '#EB5B3C',
            },
            fontFamily: {
                sans: ['DM Sans', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-slow': 'pulse 3s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
                slideUp: { '0%': { opacity: '0', transform: 'translateY(8px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
            },
        },
    },
    plugins: [],
}
