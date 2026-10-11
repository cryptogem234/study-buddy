import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const API = process.env.API_TARGET || 'http://localhost:8000'

// Page addresses like /subjects/7 or /progress share a prefix with API paths.
// Browser page loads (which accept HTML) go to the app; data requests go to the API.
const api = {
  target: API,
  bypass: req => (req.headers.accept?.includes('text/html') ? req.url : undefined),
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/subjects': api,
      '/topics': api,
      '/quiz-attempts': api,
      '/progress': api,
      '/static': api,
      '/passages': api,
      '/passage-attempts': api,
      '/reading-progress': api,
    },
  },
})
