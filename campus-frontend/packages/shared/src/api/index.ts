/**
 * API模块统一导出
 */

export * from './types';
export * from './endpoints';

// 导出 uni-app 客户端（供小程序使用）
export { apiClient, clearTokenCache } from './client';

// axios 客户端需要单独导入：
// import { axiosClient } from '@campus/shared/api/client.axios'
// export * from './client.axios';
