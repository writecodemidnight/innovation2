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
        meta: { title: '概览', icon: 'Odometer' },
      },
      {
        path: 'activities',
        name: 'ActivityList',
        component: () => import('@/views/activity/list.vue'),
        meta: { title: '活动列表', icon: 'List' },
      },
      {
        path: 'activities/apply',
        name: 'ActivityApply',
        component: () => import('@/views/activity/apply.vue'),
        meta: { title: '申报活动', icon: 'Plus' },
      },
      {
        path: 'activities/:id',
        name: 'ActivityDetail',
        component: () => import('@/views/activity/detail.vue'),
        meta: { title: '活动详情', hidden: true },
      },
      {
        path: 'activities/:id/edit',
        name: 'ActivityEdit',
        component: () => import('@/views/activity/apply.vue'),
        meta: { title: '编辑活动', hidden: true },
      },
      {
        path: 'resources/calendar',
        name: 'ResourceCalendar',
        component: () => import('@/views/resource/calendar.vue'),
        meta: { title: '资源日历', icon: 'Calendar' },
      },
      {
        path: 'resources/apply',
        name: 'ResourceApply',
        component: () => import('@/views/resource/apply.vue'),
        meta: { title: '预约资源', icon: 'OfficeBuilding' },
      },
      {
        path: 'resources/status',
        name: 'ResourceStatus',
        component: () => import('@/views/resource/status.vue'),
        meta: { title: '预约状态', icon: 'DocumentChecked' },
      },
      {
        path: 'reports/radar',
        name: 'ReportRadar',
        component: () => import('@/views/report/radar.vue'),
        meta: { title: '效果分析', icon: 'PieChart' },
      },
      {
        path: 'reports/feedback',
        name: 'ReportFeedback',
        component: () => import('@/views/report/feedback.vue'),
        meta: { title: '反馈汇总', icon: 'ChatLineRound' },
      },
      {
        path: 'funds',
        name: 'FundList',
        component: () => import('@/views/fund/list.vue'),
        meta: { title: '资金管理', icon: 'Money' },
      },
      {
        path: 'funds/apply',
        name: 'FundApply',
        component: () => import('@/views/fund/apply.vue'),
        meta: { title: '申请资金', hidden: true },
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
  history: createWebHistory('/club'),
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
