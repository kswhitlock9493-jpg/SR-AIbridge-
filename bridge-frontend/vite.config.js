import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Development server configuration
  server: {
    port: 3000,
    host: true,
    open: true,
    cors: true,
  },
  
  // Build configuration for production
  build: {
    outDir: 'build',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
  
  // Environment variables configuration
  envPrefix: ['VITE_', 'REACT_APP_'],
  
  // Base configuration for deployment
  base: '/',
  
  // Optimization for production
  define: {
    // Enable production optimizations
    __DEV__: false,
  },
  
  // Preview server configuration (for 'vite preview')
  preview: {
    port: 4173,
    host: true,
  },
  
  // Resolve configuration
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})