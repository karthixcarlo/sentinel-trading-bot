/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Theme-aware palette (driven by CSS variables)
                'dark-bg':     'rgb(var(--color-bg) / <alpha-value>)',
                'dark-card':   'rgb(var(--color-card) / <alpha-value>)',
                'dark-hover':  'rgb(var(--color-hover) / <alpha-value>)',
                'dark-border': 'rgb(var(--color-border) / <alpha-value>)',
                'dark-text':   'rgb(var(--color-text) / <alpha-value>)',
                'dark-muted':  'rgb(var(--color-muted) / <alpha-value>)',

                // Accent colors (same in both themes)
                'accent-green': '#00D09C',
                'accent-red':   '#EB5B3C',
                'accent-blue':  '#3B82F6',
                'accent-amber': '#F59E0B',
                'accent-purple':'#8B5CF6',

                // Legacy aliases (now theme-aware)
                'groww-green':      '#00D09C',
                'groww-red':        '#EB5B3C',
                'groww-dark':       'rgb(var(--color-text) / <alpha-value>)',
                'groww-gray':       'rgb(var(--color-muted) / <alpha-value>)',
                'groww-light-gray': 'rgb(var(--color-card) / <alpha-value>)',
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
