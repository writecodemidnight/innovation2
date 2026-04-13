import { createSSRApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

// 导入 uni-ui 组件
import uniIcons from '@dcloudio/uni-ui/lib/uni-icons/uni-icons.vue';
import uniLoadMore from '@dcloudio/uni-ui/lib/uni-load-more/uni-load-more.vue';
import uniCard from '@dcloudio/uni-ui/lib/uni-card/uni-card.vue';
import uniTag from '@dcloudio/uni-ui/lib/uni-tag/uni-tag.vue';

export function createApp() {
  const app = createSSRApp(App);
  const pinia = createPinia();

  app.use(pinia);

  // 注册全局组件
  app.component('uni-icons', uniIcons);
  app.component('uni-load-more', uniLoadMore);
  app.component('uni-card', uniCard);
  app.component('uni-tag', uniTag);

  return { app };
}
