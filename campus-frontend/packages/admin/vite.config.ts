import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import UnoCSS from 'unocss/vite';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue(), UnoCSS()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@campus/shared': resolve(__dirname, '../shared/src'),
    },
  },
  server: {
    port: 3002,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8082',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://localhost:8082/api',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  optimizeDeps: {
    include: ['@campus/shared'],
  },
});