import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react()
  ],
  build: {
    outDir: '../../src/rb-api/rb/api/static/',  // Adjust to FastAPI static folder
    assetsDir: 'index',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        app: './src/main.jsx',
      },
      output: {
        entryFileNames: `index/main.js`,
        assetFileNames: `index/main.[ext]`
      }
    },
  },
})
