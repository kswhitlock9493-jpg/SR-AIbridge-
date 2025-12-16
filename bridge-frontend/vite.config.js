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
    // Proxy API calls to BRH backend during development
    proxy: {
      '/api': {
        target: process.env.VITE_BRH_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Don't rewrite - backend expects /api prefix
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // Proxy root-level endpoints (agents, fleet, etc.)
      '/agents': {
        target: process.env.VITE_BRH_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/fleet': {
        target: process.env.VITE_BRH_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/armada': {
        target: process.env.VITE_BRH_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // WebSocket proxy for real-time updates
      '/ws': {
        target: process.env.VITE_BRH_BACKEND_WS || 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
  
  // Build configuration for production (Netlify + BRH)
  build: {
    outDir: 'dist',
    sourcemap: true, // Enable source maps for debugging
    minify: 'terser',
    // Netlify SPA routing optimization
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
      external: [], // No external dependencies for static build
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
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
    // Proxy for preview mode too
    proxy: {
      '/api': {
        target: process.env.VITE_BRH_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Don't rewrite - backend expects /api prefix
        // rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  
  // Resolve configuration
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})