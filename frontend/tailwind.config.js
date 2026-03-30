/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        saffron: {
          50: '#fff8ed',
          100: '#fff0d4',
          200: '#ffdda8',
          300: '#ffc471',
          400: '#ffa038',
          500: '#ff8511',
          600: '#f06b07',
          700: '#c75008',
          800: '#9e3f0f',
          900: '#7f3510',
        },
        temple: {
          50: '#fdf6ef',
          100: '#fae9d6',
          200: '#f4d0ac',
          300: '#edb177',
          400: '#e48940',
          500: '#de6d1f',
          600: '#cf5515',
          700: '#ac4013',
          800: '#893418',
          900: '#6f2d16',
        },
        ancient: {
          50: '#f6f5f0',
          100: '#e8e5d8',
          200: '#d3cdb4',
          300: '#b9ae89',
          400: '#a49668',
          500: '#95855a',
          600: '#806d4c',
          700: '#68553f',
          800: '#584838',
          900: '#4c3f33',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
