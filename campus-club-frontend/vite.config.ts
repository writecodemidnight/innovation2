import { defineConfig, type UserConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver, VantResolver } from 'unplugin-vue-components/resolvers'

// 多入口配置
const getEntries = (mode: string) => {
  const entries: Record<string, string> = {
    student: resolve(__dirname, 'src/student/main.ts'),
    club: resolve(__dirname, 'src/club/main.ts'),
    admin: resolve(__dirname, 'src/admin/main.ts'),
  }

  // 如果指定了特定模式，只返回对应入口
  if (mode === 'student') return { student: entries.student }
  if (mode === 'club') return { club: entries.club }
  if (mode === 'admin') return { admin: entries.admin }

  return entries
}

export default defineConfig(({ mode }) => {
  const entries = getEntries(mode)

  return {
    plugins: [
      vue(),
      AutoImport({
        resolvers: [ElementPlusResolver(), VantResolver()],
        imports: ['vue', 'vue-router', 'pinia'],
        dts: 'src/auto-imports.d.ts',
      }),
      Components({
        resolvers: [
          ElementPlusResolver({ importStyle: 'sass' }),
          VantResolver(),
        ],
        dts: 'src/components.d.ts',
      }),
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@student': resolve(__dirname, 'src/student'),
        '@club': resolve(__dirname, 'src/club'),
        '@admin': resolve(__dirname, 'src/admin'),
        '@common': resolve(__dirname, 'src/common'),
      },
    },
    build: {
      rollupOptions: {
        input: entries,
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name?.split('.') || []
            const ext = info[info.length - 1]
            if (/\.css$/i.test(assetInfo.name || '')) {
              return 'assets/[name]-[hash][extname]'
            }
            return 'assets/[name]-[hash][extname]'
          },
        },
      },
      outDir: `dist/${mode}`,
    },
    server: {
      port: mode === 'student' ? 3001 : mode === 'club' ? 3002 : 3003,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @use "@/styles/variables.scss" as *;
          `,
        },
      },
    },
  } as UserConfig
})
