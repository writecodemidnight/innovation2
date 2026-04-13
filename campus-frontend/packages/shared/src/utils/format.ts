/**
 * 格式化工具函数
 */

/** 格式化日期时间 */
export function formatDateTime(date: string | Date | number, format = 'YYYY-MM-DD HH:mm'): string {
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';

  const pad = (n: number) => n.toString().padStart(2, '0');

  const map: Record<string, string> = {
    'YYYY': d.getFullYear().toString(),
    'MM': pad(d.getMonth() + 1),
    'DD': pad(d.getDate()),
    'HH': pad(d.getHours()),
    'mm': pad(d.getMinutes()),
    'ss': pad(d.getSeconds()),
  };

  return format.replace(/YYYY|MM|DD|HH|mm|ss/g, match => map[match]);
}

/** 格式化日期 */
export function formatDate(date: string | Date | number): string {
  return formatDateTime(date, 'YYYY-MM-DD');
}

/** 格式化时间 */
export function formatTime(date: string | Date | number): string {
  return formatDateTime(date, 'HH:mm');
}

/** 格式化相对时间 */
export function formatRelativeTime(date: string | Date | number): string {
  const d = new Date(date);
  const now = new Date();
  const diff = now.getTime() - d.getTime();

  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  const week = 7 * day;
  const month = 30 * day;

  if (diff < minute) return '刚刚';
  if (diff < hour) return `${Math.floor(diff / minute)}分钟前`;
  if (diff < day) return `${Math.floor(diff / hour)}小时前`;
  if (diff < week) return `${Math.floor(diff / day)}天前`;
  if (diff < month) return `${Math.floor(diff / week)}周前`;

  return formatDate(date);
}

/** 格式化数字（千分位） */
export function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN');
}

/** 格式化文件大小 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/** 格式化时长 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}分钟`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) return `${hours}小时`;
  return `${hours}小时${mins}分钟`;
}

/** 格式化百分比 */
export function formatPercent(value: number, decimals = 2): string {
  return (value * 100).toFixed(decimals) + '%';
}

/** 格式化金额 */
export function formatMoney(amount: number, currency = '¥'): string {
  return `${currency}${amount.toFixed(2)}`;
}
