/**
 * TanStack Query (Vue Query) 配置
 *
 * 优势：
 * - 自动缓存与去重：相同请求不会重复发送
 * - 后台刷新：stale 数据在后台自动更新
 * - 乐观更新：先更新UI，再确认服务端
 * - 分页/无限滚动：内置支持
 */

import { QueryClient } from '@tanstack/vue-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2, // 2分钟内数据视为新鲜
      gcTime: 1000 * 60 * 10,   // 10分钟后垃圾回收（原cacheTime）
      retry: 2,
      refetchOnWindowFocus: true,
    },
    mutations: {
      retry: 1,
    },
  },
})

export { useQuery, useMutation, useInfiniteQuery } from '@tanstack/vue-query'
