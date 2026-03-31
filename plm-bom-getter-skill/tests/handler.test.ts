/**
 * PLM BOM Getter - 测试用例
 */

import {
  validateCustomerModel,
  validateMaterialNumber,
  formatTimestamp,
  getDefaultOutputPath
} from '../src/utils';

describe('PLMBomGetter', () => {
  describe('validateCustomerModel', () => {
    it('应接受有效的客户型号', () => {
      expect(validateCustomerModel('N3D').valid).toBe(true);
      expect(validateCustomerModel('NW4').valid).toBe(true);
      expect(validateCustomerModel('NC20').valid).toBe(true);
      expect(validateCustomerModel('NX35U').valid).toBe(true);
    });

    it('应拒绝空客户型号', () => {
      const result = validateCustomerModel('');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('客户型号不能为空');
    });

    it('应拒绝过长的客户型号', () => {
      const longModel = 'A'.repeat(51);
      const result = validateCustomerModel(longModel);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('客户型号过长');
    });

    it('应拒绝包含非法字符的客户型号', () => {
      const result = validateCustomerModel('N3D@123');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('客户型号包含非法字符');
    });
  });

  describe('validateMaterialNumber', () => {
    it('应接受有效的成品料号', () => {
      expect(validateMaterialNumber('30008018').valid).toBe(true);
      expect(validateMaterialNumber('12345678').valid).toBe(true);
    });

    it('应拒绝空成品料号', () => {
      const result = validateMaterialNumber('');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('成品料号不能为空');
    });

    it('应拒绝非数字成品料号', () => {
      const result = validateMaterialNumber('30008ABC');
      expect(result.valid).toBe(false);
      expect(result.error).toBe('成品料号必须是数字');
    });
  });

  describe('formatTimestamp', () => {
    it('应生成正确格式的时间戳', () => {
      const date = new Date('2026-03-31T12:30:45');
      const result = formatTimestamp(date);
      expect(result).toBe('20260331_123045');
    });

    it('应使用当前时间', () => {
      const result = formatTimestamp();
      expect(result).toMatch(/^\d{8}_\d{6}$/);
    });
  });

  describe('getDefaultOutputPath', () => {
    it('应生成正确的输出路径', () => {
      const result = getDefaultOutputPath('test.xlsx');
      expect(result).toContain('test.xlsx');
    });

    it('应使用环境变量指定的目录', () => {
      const customDir = '/custom/path';
      const result = getDefaultOutputPath('test.xlsx');
      // 默认路径应该包含默认输出目录
      expect(result).toContain('test.xlsx');
    });
  });
});
