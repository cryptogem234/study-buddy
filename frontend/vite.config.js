import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/subjects': 'http://localhost:8000',
      '/topics': 'http://localhost:8000',
      '/quiz-attempts': 'http://localhost:8000',
      '/progress': 'http://localhost:8000',
    },
  },
})
