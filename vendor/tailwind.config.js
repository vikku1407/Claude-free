/* Mirrors the tailwind.config that the Play CDN block used to hold, so the
   generated stylesheet is equivalent to what the app compiled in-browser. */
module.exports = {
  content: ['../index.html'],
  theme: {
    extend: {
      colors: {
        brand: { 50:'#f0f7ff', 100:'#e0effe', 500:'#0284c7', 600:'#0369a1', 700:'#0f172a', 800:'#1e293b', 900:'#0f172a' }
      }
    }
  },
  corePlugins: { preflight: true },
  plugins: []
};
