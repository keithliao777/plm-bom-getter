/**
 * PLM BOM Getter - OpenClaw Skill Entry Point
 *
 * 实现 ISkill 接口，提供 PLM 系统 BOM 数据获取功能
 */

import { ISkill, SkillContext, SkillResult } from '@openclaw/sdk';
import { PLMBomHandler } from './handler';

export class PLMBomGetterSkill implements ISkill {
  private handler: PLMBomHandler;
  private initialized: boolean = false;

  constructor() {
    this.handler = new PLMBomHandler();
  }

  /**
   * 初始化 Skill
   */
  async init(context: SkillContext): Promise<void> {
    if (this.initialized) {
      return;
    }

    // 检查环境
    const chromePort = process.env.CHROME_DEBUG_PORT || '9222';
    context.logger.info(`PLM BOM Getter 初始化，Chrome 调试端口: ${chromePort}`);

    this.initialized = true;
  }

  /**
   * 获取 Skill 描述
   */
  getDescription(): string {
    return '从 PLM 系统获取 BOM 数据 - 支持按客户型号搜索成品料号，按料号查询多层 BOM';
  }

  /**
   * 获取可用工具列表
   */
  getTools(): SkillTool[] {
    return [
      {
        name: 'search-products',
        description: '按客户型号搜索成品料号',
        parameters: {
          type: 'object',
          properties: {
            customer_model: {
              type: 'string',
              description: '客户型号 (如 N3D, NW4, NC20)',
              required: true
            }
          }
        }
      },
      {
        name: 'search-bom',
        description: '按成品料号查询 BOM',
        parameters: {
          type: 'object',
          properties: {
            material_number: {
              type: 'string',
              description: '成品料号 (如 30008018)',
              required: true
            }
          }
        }
      },
      {
        name: 'full-search',
        description: '搜索产品并获取所有 BOM',
        parameters: {
          type: 'object',
          properties: {
            customer_model: {
              type: 'string',
              description: '客户型号 (如 N3D, NW4)',
              required: true
            }
          }
        }
      }
    ];
  }

  /**
   * 执行 Skill 操作
   */
  async execute(input: SkillInput, context: SkillContext): Promise<SkillResult> {
    const { action, customer_model, material_number } = input;

    try {
      // 初始化
      await this.init(context);

      // 连接 PLM
      context.logger.info('连接到 PLM 系统...');
      await this.handler.connect();

      let result: any;

      // 执行对应操作
      switch (action) {
        case 'search-products':
          if (!customer_model) {
            return {
              success: false,
              error: '缺少参数: customer_model'
            };
          }
          result = await this.handler.searchProducts(customer_model);
          break;

        case 'search-bom':
          if (!material_number) {
            return {
              success: false,
              error: '缺少参数: material_number'
            };
          }
          result = await this.handler.searchBom(material_number);
          break;

        case 'full-search':
          if (!customer_model) {
            return {
              success: false,
              error: '缺少参数: customer_model'
            };
          }
          result = await this.handler.fullSearch(customer_model);
          break;

        default:
          return {
            success: false,
            error: `未知操作: ${action}`
          };
      }

      // 断开连接
      await this.handler.disconnect();

      return {
        success: true,
        data: result
      };

    } catch (error: any) {
      context.logger.error(`执行失败: ${error.message}`);

      // 尝试断开连接
      try {
        await this.handler.disconnect();
      } catch (e) {
        // 忽略断开错误
      }

      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 销毁 Skill
   */
  async destroy(): Promise<void> {
    if (this.handler) {
      await this.handler.disconnect();
    }
    this.initialized = false;
  }
}

// 导出 Skill 实例工厂函数
export function createSkill(): ISkill {
  return new PLMBomGetterSkill();
}
