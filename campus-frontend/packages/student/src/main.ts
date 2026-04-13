import { createSSRApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

// 引入Vant组件
import {
  Button,
  Cell,
  CellGroup,
  Card,
  Image,
  Uploader,
  Toast,
  Dialog,
  Loading,
  NavBar,
  Tab,
  Tabs,
  List,
  PullRefresh,
  Empty,
  Tag,
  Rate,
  Field,
  Form,
  Stepper,
  Calendar,
  Popup,
  ActionSheet,
  Swipe,
  SwipeItem,
  Search,
  Icon,
  Divider,
  NoticeBar,
  Badge,
  Collapse,
  CollapseItem,
} from 'vant';
import 'vant/lib/index.css';

export function createApp() {
  const app = createSSRApp(App);
  const pinia = createPinia();

  app.use(pinia);

  // 注册Vant组件
  app
    .use(Button)
    .use(Cell)
    .use(CellGroup)
    .use(Card)
    .use(Image)
    .use(Uploader)
    .use(Toast)
    .use(Dialog)
    .use(Loading)
    .use(NavBar)
    .use(Tab)
    .use(Tabs)
    .use(List)
    .use(PullRefresh)
    .use(Empty)
    .use(Tag)
    .use(Rate)
    .use(Field)
    .use(Form)
    .use(Stepper)
    .use(Calendar)
    .use(Popup)
    .use(ActionSheet)
    .use(Swipe)
    .use(SwipeItem)
    .use(Search)
    .use(Icon)
    .use(Divider)
    .use(NoticeBar)
    .use(Badge)
    .use(Collapse)
    .use(CollapseItem);

  return { app };
}
