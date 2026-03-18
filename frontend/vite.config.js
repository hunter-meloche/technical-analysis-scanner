import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => ({
  base: command === 'serve' ? '/' : '/finance/technical/',
  plugins: [react()],
  server: {
    port: 5176,
    proxy: {
      '/api': 'http://localhost:8104',
    },
  },
}))
