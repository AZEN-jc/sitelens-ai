import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: { host: '127.0.0.1', proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: { environment: 'jsdom', globals: true },
})
