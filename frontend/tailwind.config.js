/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: '#14263D', 50: '#EEF2F7', 100: '#D9E1EC', 200: '#B3C2D6', 300: '#7F95B3', 400: '#4C6589', 500: '#2A4263', 600: '#1C3250', 700: '#14263D', 800: '#0E1B2C', 900: '#08111C' },
        ink: { DEFAULT: '#536579', 50: '#F3F5F8', 100: '#E4E8EE', 200: '#C9D1DB', 300: '#A3AFBD', 400: '#7A889A', 500: '#536579', 600: '#435263', 700: '#34404D', 800: '#252E38', 900: '#171D24' },
        paper: { DEFAULT: '#F7F9FC', 2: '#EEF2F7' },
        teal: { DEFAULT: '#317F86', 50: '#EDF6F6', 100: '#D3E9EA', 200: '#A6D1D4', 300: '#72B3B8', 400: '#4A979D', 500: '#317F86', 600: '#28686E', 700: '#205358', 800: '#183F43', 900: '#0F2A2D' },
        amber: { DEFAULT: '#D6A34A', 50: '#FBF5EA', 100: '#F5E7CC', 200: '#EBD09B', 300: '#E0B96E', 400: '#D6A34A', 500: '#B98A34', 600: '#936C27', 700: '#6E511D', 800: '#4A3613', 900: '#271C0A' },
      },
      fontFamily: {
        sans: ['"Inter Variable"', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        serif: ['"Source Serif 4"', 'Georgia', 'Cambria', 'serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(20,38,61,0.06), 0 1px 1px rgba(20,38,61,0.04)',
        lift: '0 12px 32px -8px rgba(20,38,61,0.22), 0 4px 10px -4px rgba(20,38,61,0.12)',
      },
    },
  },
  plugins: [],
}
