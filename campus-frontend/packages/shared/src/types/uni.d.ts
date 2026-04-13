/**
 * uni-app 全局类型声明
 * 用于在共享包中使用 uni API
 */

// 简单的 uni 类型定义
declare interface Uni {
  request(options: {
    url: string;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'OPTIONS' | 'HEAD';
    data?: any;
    header?: Record<string, string>;
    timeout?: number;
    withCredentials?: boolean;
    success?: (result: { data: any; statusCode: number; header: Record<string, string> }) => void;
    fail?: (error: { errMsg: string }) => void;
    complete?: () => void;
  }): void;
  getStorageSync(key: string): any;
  setStorageSync(key: string, data: any): void;
  getSystemInfoSync(): {
    statusBarHeight?: number;
    [key: string]: any;
  };
  navigateTo(options: { url: string; success?: () => void; fail?: () => void }): void;
  redirectTo(options: { url: string; success?: () => void; fail?: () => void }): void;
  switchTab(options: { url: string; success?: () => void; fail?: () => void }): void;
  navigateBack(options?: { delta?: number }): void;
  showToast(options: { title: string; icon?: 'success' | 'loading' | 'none'; duration?: number }): void;
  showModal(options: {
    title?: string;
    content?: string;
    showCancel?: boolean;
    confirmText?: string;
    success?: (res: { confirm: boolean; cancel: boolean }) => void;
  }): void;
  showLoading(options: { title: string; mask?: boolean }): void;
  hideLoading(): void;
  chooseImage(options: {
    count?: number;
    sizeType?: ('original' | 'compressed')[];
    sourceType?: ('album' | 'camera')[];
    success?: (res: { tempFilePaths: string[]; tempFiles: any[] }) => void;
    fail?: () => void;
  }): void;
  uploadFile(options: {
    url: string;
    filePath: string;
    name: string;
    header?: Record<string, string>;
    formData?: Record<string, any>;
    success?: (res: { data: string; statusCode: number }) => void;
    fail?: (err: any) => void;
  }): void;
}

declare const uni: Uni;

// 浏览器环境
declare const window: Window & typeof globalThis;
declare const localStorage: Storage;

// ImportMeta 扩展
declare interface ImportMeta {
  env: Record<string, string | undefined>;
}
