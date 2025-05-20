// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  // React plugin to handle JSX
  plugins: [react()],
  
  // Resolve configuration
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  
  // Explicitly set the entry point
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: resolve(__dirname, 'src/tisit/dashboard/index.html'),
    },
  },
  
  // Force JSX parsing for .js files in the dashboard directory
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
      },
    },
  },
  
  // Server configuration
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  
  // Define environment variables
  define: {
    'process.env.REACT_APP_TISIT_API_URL': JSON.stringify('http://localhost:8000'),
  },
});