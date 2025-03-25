/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'black': '#201e1fff',
        'dark-gray': '#424242ff',
        'dim-gray': '#615b5bff',
        'gray': '#737373ff',
        'light-gray': '#b3b3b3ff',
        'black-overlay': '#00000059',
      }
    },
  },
  plugins: [],
}

