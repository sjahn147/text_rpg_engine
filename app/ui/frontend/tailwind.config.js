/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'game-bg': '#e8f4f8',
        'game-bg-dark': '#d0e8f2',
        'game-bg-light': '#b8dce8',
        'game-surface': 'rgba(255, 255, 255, 0.15)',
        'game-primary': 'rgba(255, 255, 255, 0.25)',
        'game-primary-light': 'rgba(255, 255, 255, 0.4)',
        'game-accent': '#ffffff',
        'game-text': '#000000',
        'game-text-secondary': 'rgba(0, 0, 0, 0.7)',
        'game-input': 'rgba(255, 255, 255, 0.1)',
        'game-border': 'rgba(0, 0, 0, 0.1)',
      },
      fontFamily: {
        'game': ['Noto Serif JP', 'Noto Serif KR', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

