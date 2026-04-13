import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/stores/user';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据监控大屏', icon: 'Monitor' },
      },
      {
        path: 'approval/pending',
        name: 'ApprovalPending',
        component: () => import('@/views/approval/pending.vue'),
        meta: { title: '待办审批', icon: 'Bell' },
      },
      {
        path: 'approval/history',
        name: 'ApprovalHistory',
        component: () => import('@/views/approval/history.vue'),
        meta: { title: '审批历史', icon: 'DocumentChecked' },
      },
      {
        path: 'resource/pool',
        name: 'ResourcePool',
        component: () => import('@/views/resource/pool.vue'),
        meta: { title: '资源池管理', icon: 'OfficeBuilding' },
      },
      {
        path: 'resource/allocation',
        name: 'ResourceAllocation',
        component: () => import('@/views/resource/allocation.vue'),
        meta: { title: '资源分配', icon: 'SetUp' },
      },
      {
        path: 'report/global',
        name: 'GlobalReport',
        component: () => import('@/views/report/index.vue'),
        meta: { title: '全局报表', icon: 'TrendCharts' },
      },
      {
        path: 'system/config',
        name: 'SystemConfig',
        component: () => import('@/views/system/config.vue'),
        meta: { title: '系统配置', icon: 'Setting' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
  },
];

const router = createRouter({
  history: createWebHistory('/admin'),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login');
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/');
  } else {
    next();
  }
});

export default router;