import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/asr': 'http://127.0.0.1:8000',
      '/intent': 'http://127.0.0.1:8000',
      '/response': 'http://127.0.0.1:8000',
      '/tts': 'http://127.0.0.1:8000',
      '/voicebot': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    }
  }
})
