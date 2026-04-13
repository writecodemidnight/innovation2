/**
 * 表单验证工具函数
 */

/** 邮箱验证 */
export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

/** 手机号验证（中国大陆） */
export function isPhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value);
}

/** 学号验证 */
export function isStudentId(value: string): boolean {
  return /^\d{10,12}$/.test(value);
}

/** 身份证号验证 */
export function isIdCard(value: string): boolean {
  const reg = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
  return reg.test(value);
}

/** 非空验证 */
export function isRequired(value: any): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

/** 长度验证 */
export function isLength(value: string, min: number, max: number): boolean {
  const len = value.length;
  return len >= min && len <= max;
}

/** 数值范围验证 */
export function isRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max;
}

/** URL验证 */
export function isUrl(value: string): boolean {
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

/** 验证规则类型 */
export type ValidationRule = {
  validator: (value: any) => boolean;
  message: string;
};

/** 创建必填验证 */
export function required(message = '此项必填'): ValidationRule {
  return { validator: isRequired, message };
}

/** 创建邮箱验证 */
export function email(message = '请输入有效的邮箱地址'): ValidationRule {
  return { validator: isEmail, message };
}

/** 创建手机号验证 */
export function phone(message = '请输入有效的手机号码'): ValidationRule {
  return { validator: isPhone, message };
}

/** 创建长度验证 */
export function length(min: number, max: number, message?: string): ValidationRule {
  return {
    validator: (v) => isLength(v, min, max),
    message: message || `长度需在${min}-${max}个字符之间`,
  };
}

/** 创建范围验证 */
export function range(min: number, max: number, message?: string): ValidationRule {
  return {
    validator: (v) => isRange(v, min, max),
    message: message || `数值需在${min}-${max}之间`,
  };
}

/** 执行多规则验证 */
export function validate(value: any, rules: ValidationRule[]): string | null {
  for (const rule of rules) {
    if (!rule.validator(value)) {
      return rule.message;
    }
  }
  return null;
}

/** 常用验证规则组合 */
export const Validators = {
  required: (msg?: string) => required(msg),
  email: (msg?: string) => email(msg),
  phone: (msg?: string) => phone(msg),
  studentId: (msg?: string) => ({
    validator: isStudentId,
    message: msg || '请输入有效的学号',
  }),
  password: (msg?: string) => ({
    validator: (v: string) => isLength(v, 6, 20),
    message: msg || '密码长度需在6-20个字符之间',
  }),
};
