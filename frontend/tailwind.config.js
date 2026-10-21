/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#0a0d14',
          card: '#111726',
          border: '#1f293d',
          accent: '#00ffb2',
          danger: '#ff3366',
          warning: '#ffaa00',
          info: '#00b4d8'
        }
      }
    },
  },
  plugins: [],
}
