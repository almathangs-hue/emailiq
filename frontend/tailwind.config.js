/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#f0f4ff",
          100: "#dde8ff",
          500: "#3b5bdb",
          600: "#2f4ac4",
          700: "#243aad",
        },
      },
    },
  },
  plugins: [],
};
