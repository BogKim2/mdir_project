/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#080c0a',
          surface: '#0d1410',
          panel: '#111a14',
          green: '#00ff9d',
          cyan: '#00e5ff',
          orange: '#ff6b35',
          dim: '#1a2e1f',
          text: '#c8d8cc',
          muted: '#4a6b52',
          border: '#1e3525',
        }
      },
      fontFamily: {
        mono: ['"Fira Code"', '"JetBrains Mono"', 'monospace'],
        display: ['"Syne"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
      },
      animation: {
        'cursor-blink': 'blink 1s step-end infinite',
        'scan': 'scan 8s linear infinite',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'slide-up': 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'fade-in': 'fadeIn 0.8s ease forwards',
        'draw': 'draw 2s ease forwards',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 255, 157, 0.3)' },
          '50%': { boxShadow: '0 0 60px rgba(0, 255, 157, 0.6)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(40px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
