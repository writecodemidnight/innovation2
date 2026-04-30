<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app';
import { useUserStore } from '@/stores/user';

onLaunch(() => {
  console.log('App Launch');

  // 初始化用户登录状态
  const userStore = useUserStore();
  userStore.init();
});

onShow(() => {
  console.log('App Show');
});

onHide(() => {
  console.log('App Hide');
});
</script>

<style lang="scss">
/* 全局样式 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: #333;
  background-color: #f5f5f5;
}

/* 安全区域适配 */
.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

/* 通用布局 */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.flex-1 {
  flex: 1;
}

/* 文本省略 */
.ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 卡片样式 */
.card {
  background: #fff;
  border-radius: 12rpx;
  margin: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 按钮样式 */
.btn-primary {
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  color: #fff;
  border-radius: 40rpx;
  padding: 24rpx 48rpx;
  font-size: 28rpx;
  font-weight: 500;
}

/* 间距 */
.mt-8 { margin-top: 8rpx; }
.mt-16 { margin-top: 16rpx; }
.mt-24 { margin-top: 24rpx; }
.mb-8 { margin-bottom: 8rpx; }
.mb-16 { margin-bottom: 16rpx; }
.mb-24 { margin-bottom: 24rpx; }
</style>
