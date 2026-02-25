/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'groww-green': '#00D09C',
                'groww-red': '#EB5B3C',
                'groww-dark': '#111111',
                'groww-gray': '#444444',
                'groww-light-gray': '#F0F2F6',
                // Aliases for pages that use inline hex directly
                'brand-green': '#00D09C',
                'brand-red': '#EB5B3C',
            },
            fontFamily: {
                sans: ['DM Sans', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
        },
    },
    plugins: [],
}
