import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'

function getBackendPort(): number {
  const configPath = resolve(__dirname, '../data/config.json')
  if (existsSync(configPath)) {
    try {
      const cfg = JSON.parse(readFileSync(configPath, 'utf-8'))
      if (typeof cfg.port === 'number') return cfg.port
    } catch { /* brug default */ }
  }
  return 8765
}

const backendPort = getBackendPort()

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
      },
    },
  },
})
