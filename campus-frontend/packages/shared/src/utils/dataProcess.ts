/**
 * 数据处理工具函数
 * 用于大数据量的处理和转换
 */

/** 防抖函数 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return function (...args: Parameters<T>) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** 节流函数 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  interval: number
): (...args: Parameters<T>) => void {
  let lastTime = 0;
  return function (...args: Parameters<T>) {
    const now = Date.now();
    if (now - lastTime >= interval) {
      lastTime = now;
      fn(...args);
    }
  };
}

/** 分批处理数组 */
export function batchProcess<T, R>(
  items: T[],
  processor: (item: T) => R,
  batchSize: number = 100
): R[] {
  const results: R[] = [];
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    results.push(...batch.map(processor));
  }
  return results;
}

/** 异步分批处理 */
export async function asyncBatchProcess<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  batchSize: number = 10,
  delayMs: number = 0
): Promise<R[]> {
  const results: R[] = [];
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
    if (delayMs > 0 && i + batchSize < items.length) {
      await sleep(delayMs);
    }
  }
  return results;
}

/** 延迟函数 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/** 数组去重 */
export function unique<T>(arr: T[], key?: keyof T): T[] {
  if (!key) return [...new Set(arr)];
  const seen = new Set();
  return arr.filter(item => {
    const k = item[key];
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

/** 数组分组 */
export function groupBy<T>(arr: T[], key: keyof T): Record<string, T[]> {
  return arr.reduce((groups, item) => {
    const groupKey = String(item[key]);
    if (!groups[groupKey]) groups[groupKey] = [];
    groups[groupKey].push(item);
    return groups;
  }, {} as Record<string, T[]>);
}

/** 数组排序 */
export function sortBy<T>(arr: T[], key: keyof T, order: 'asc' | 'desc' = 'asc'): T[] {
  return [...arr].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
}

/** 树形结构转换 */
export function toTree<T extends { id: number; parentId: number | null; children?: T[] }>(
  items: T[]
): T[] {
  const map = new Map<number, T>();
  const roots: T[] = [];

  items.forEach(item => {
    map.set(item.id, { ...item, children: [] });
  });

  items.forEach(item => {
    const node = map.get(item.id)!;
    if (item.parentId === null || !map.has(item.parentId)) {
      roots.push(node);
    } else {
      const parent = map.get(item.parentId)!;
      if (!parent.children) parent.children = [];
      parent.children.push(node);
    }
  });

  return roots;
}

/** 扁平化树形结构 */
export function flattenTree<T extends { children?: T[] }>(tree: T[]): T[] {
  const result: T[] = [];
  const stack = [...tree];

  while (stack.length > 0) {
    const node = stack.shift()!;
    const { children, ...rest } = node;
    result.push(rest as T);
    if (children) {
      stack.unshift(...children);
    }
  }

  return result;
}

/** 搜索过滤 */
export function fuzzySearch<T>(
  items: T[],
  keyword: string,
  keys: (keyof T)[]
): T[] {
  if (!keyword) return items;
  const lowerKeyword = keyword.toLowerCase();
  return items.filter(item =>
    keys.some(key =>
      String(item[key]).toLowerCase().includes(lowerKeyword)
    )
  );
}

/** 分页处理 */
export function paginate<T>(items: T[], page: number, size: number): T[] {
  const start = (page - 1) * size;
  return items.slice(start, start + size);
}
