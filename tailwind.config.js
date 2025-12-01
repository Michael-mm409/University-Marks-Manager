/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/templates/**/*.html", "./src/presentation/web/**/*.py"],
  safelist: [
    // Ensure hero heading sizes are always present in compiled CSS
    'text-6xl', 'text-7xl', 'text-8xl',
    'sm:text-6xl', 'md:text-7xl', 'lg:text-8xl',
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["cupcake", "dark", "cmyk"],
  },
}
