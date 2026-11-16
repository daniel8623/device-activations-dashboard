import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // During development, forward /api requests to the FastAPI server.
    // The browser sees one origin, so no CORS is needed.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})