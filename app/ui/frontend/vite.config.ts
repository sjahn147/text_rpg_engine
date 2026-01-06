import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['react-window'],
    force: true, // 강제로 재번들링
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', 'e2e', '.idea', '.git', '.cache'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/setupTests.ts',
        '**/*.d.ts',
        '**/*.config.*',
        '**/dist/**',
        '**/coverage/**',
        'e2e/**',
      ],
      thresholds: {
        branches: 70,
        functions: 70,
        lines: 70,
        statements: 70,
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // node_modules는 vendor로 분리
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'vendor-react';
            }
            if (id.includes('framer-motion')) {
              return 'vendor-framer';
            }
            if (id.includes('zustand')) {
              return 'vendor-zustand';
            }
            if (id.includes('axios')) {
              return 'vendor-axios';
            }
            // 기타 node_modules
            return 'vendor-other';
          }
          
          // 에디터 모드 관련 코드
          if (id.includes('/modes/EditorMode') || 
              id.includes('/components/editor/') || 
              id.includes('/hooks/editor/') ||
              id.includes('/hooks/useWorldEditor') ||
              id.includes('/hooks/useUndoRedo') ||
              id.includes('/hooks/useSettings')) {
            return 'editor';
          }
          
          // 게임 모드 관련 코드
          if (id.includes('/modes/GameMode') || 
              id.includes('/components/game/') || 
              id.includes('/hooks/game/') ||
              id.includes('/screens/game/')) {
            return 'game';
          }
        },
      },
    },
    chunkSizeWarningLimit: 1000, // 1MB로 증가 (경고 임계값)
  },
})

