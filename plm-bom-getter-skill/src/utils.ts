/**
 * PLM BOM Getter - 工具函数
 */

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * 验证客户型号格式
 */
export function validateCustomerModel(model: string): ValidationResult {
  if (!model || model.trim().length === 0) {
    return { valid: false, error: '客户型号不能为空' };
  }

  if (model.length > 50) {
    return { valid: false, error: '客户型号过长' };
  }

  // 客户型号通常为字母数字组合
  const validPattern = /^[A-Za-z0-9_-]+$/;
  if (!validPattern.test(model)) {
    return { valid: false, error: '客户型号包含非法字符' };
  }

  return { valid: true };
}

/**
 * 验证成品料号格式
 */
export function validateMaterialNumber(material: string): ValidationResult {
  if (!material || material.trim().length === 0) {
    return { valid: false, error: '成品料号不能为空' };
  }

  // 成品料号通常为数字
  const validPattern = /^\d+$/;
  if (!validPattern.test(material)) {
    return { valid: false, error: '成品料号必须是数字' };
  }

  return { valid: true };
}

/**
 * 格式化日期时间
 */
export function formatTimestamp(date: Date = new Date()): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}_${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
}

/**
 * 生成默认输出路径
 */
export function getDefaultOutputPath(filename: string): string {
  const outputDir = process.env.PLM_OUTPUT_DIR || 'C:/Users/keith liao/.openclaw/plm-exports';
  return `${outputDir}/${filename}`;
}
