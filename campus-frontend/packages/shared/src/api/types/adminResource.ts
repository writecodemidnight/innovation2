/**
 * 管理端资源池类型定义
 */

/** 资源 */
export interface AdminResource {
  id: number;
  name: string;
  resourceType: string;
  description?: string;
  capacity?: number;
  availableCount: number;
  totalCount: number;
  unit?: string;
  location?: string;
  managerId?: number;
  status: string;
  constraints?: string;
  createdAt: string;
  updatedAt?: string;
}

/** 资源请求 */
export interface ResourceRequest {
  name: string;
  resourceType: string;
  description?: string;
  capacity?: number;
  totalCount?: number;
  unit?: string;
  location?: string;
  status?: string;
}

/** 资源统计 */
export interface ResourceStats {
  totalResources: number;
  typeDistribution: Record<string, number>;
  statusDistribution: Record<string, number>;
}
