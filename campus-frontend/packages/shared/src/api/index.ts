/**
 * API模块统一导出
 */

export * from './types';
export * from './endpoints';

// 导出uni客户端（供小程序和H5使用）
export * from './client';

// axios 客户端仅供 PC 端使用，需要单独导入
// import { axiosClient } from '@campus/shared/api/client.axios'
