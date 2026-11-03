/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fbf8f4',
          100: '#f6f0e6',
          200: '#ede1cd',
          300: '#e1cca8',
          400: '#d3b27e',
          500: '#c59a59',
          600: '#b28347',
          700: '#94673b',
          800: '#795434',
          900: '#64452e',
        },
        sage: {
          50: '#f4f7f5',
          100: '#e5eee7',
          200: '#cedecf',
          500: '#5f8a65',
          600: '#486e4e',
        },
        coral: {
          50: '#fff5f3',
          100: '#ffe8e4',
          500: '#f05a3f',
          600: '#dc4227',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['Cal Sans', 'Cabinet Grotesk', 'Plus Jakarta Sans', 'sans-serif']
      },
      animation: {
        'fade-in': 'fadeIn 0.8s ease-out forwards',
        'float-slow': 'float 6s ease-in-out infinite',
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.85', transform: 'scale(1.02)' },
        }
      }
    },
  },
  plugins: [],
}

