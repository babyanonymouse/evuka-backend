import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      // Also proxy /ai directly if it's not under /api in urls.py?
      // Looking at backend urls.py, /ai/ask/ is likely at root or under /ai/
      // Backend project likely maps path('ai/', include('ai_assistant.urls'))
      // Let's check main urls.py later. For now, assuming /ai -> http://localhost:8000/ai
      "/ai": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/courses": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
