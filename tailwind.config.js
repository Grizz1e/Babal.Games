/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/{templates,static}/*/*.{html,js}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#6366f1',
        'secondary': '#818cf8',
      }
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
  ],
  darkMode: 'selector',
}

