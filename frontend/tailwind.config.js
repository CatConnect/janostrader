/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg:      '#050810',
        card:    '#0b1220',
        edge:    '#132030',
        teal:    '#1fffd4',
        emerald: '#00e087',
        rose:    '#ff4f6a',
        amber:   '#ffb82e',
        ink:     '#e4ecf7',
        dim:     '#647d96',
      },
      fontFamily: {
        mono: ["'SF Mono'", 'ui-monospace', "'Cascadia Code'", 'monospace'],
        sans: ['system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
