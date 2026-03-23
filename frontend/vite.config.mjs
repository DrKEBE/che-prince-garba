
// frontend\vite.config.mjs 
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const isDev = env.VITE_DEV_MODE === 'true';
  
  return {
    plugins: [react()],
    server: {
      port: 3000,
      host: true,
      strictPort: true,
      proxy: {
        // Proxy pour le backend API
        '/api/v1': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            // Logs uniquement en mode dev
            if (isDev) {
              proxy.on('proxyReq', (proxyReq, req, _res) => {
                console.log('[VITE PROXY]', req.method, req.url);
              });
            }
          },
        },
        // Proxy pour les routes de développement
        '/dev': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
        // Proxy pour les fichiers uploadés
        '/uploads': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    // VOTRE CONFIGURATION EXISTANTE CI-DESSOUS
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            ui: ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled'],
            charts: ['recharts', 'chart.js', 'react-chartjs-2'],
            forms: ['formik', 'yup'],
            utils: ['date-fns', 'framer-motion', 'react-hot-toast'],
          },
        },
      },
    },
    optimizeDeps: {
      include: ['@mui/material', '@mui/icons-material'],
    },
  };
});