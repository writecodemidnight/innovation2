/**
 * API模块统一导出
 */

export * from './types';
export * from './endpoints';

// 导出原uni客户端（供小程序用）
export * from './client';

// 导出axios客户端（供PC端用）
export * from './client.axios';
