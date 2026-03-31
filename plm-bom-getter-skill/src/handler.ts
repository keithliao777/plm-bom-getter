/**
 * PLM BOM Getter - 核心业务逻辑
 *
 * 处理与 PLM 系统的交互：BOM 搜索、数据验证、文件输出
 */

import { spawn } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';

const writeFile = promisify(fs.writeFile);
const readFile = promisify(fs.readFile);

export interface ProductSearchResult {
  customer_model: string;
  total_rows: number;
  part_numbers: string[];
  files: {
    products?: string;
    part_numbers?: string;
  };
}

export interface BomSearchResult {
  material_number: string;
  total_rows: number;
  files: {
    bom?: string;
  };
}

export interface FullSearchResult {
  customer_model: string;
  products: ProductSearchResult;
  boms: BomSearchResult[];
  total_bom_rows: number;
}

export interface ExecutionResult {
  success: boolean;
  data?: any;
  error?: string;
}

/**
 * PLM BOM 处理器
 */
export class PLMBomHandler {
  private pythonPath: string = 'python';
  private connected: boolean = false;

  constructor() {
    // 尝试使用 python3
    this.pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  }

  /**
   * 连接到 PLM 系统（通过 Selenium）
   */
  async connect(): Promise<void> {
    // Python 代码会处理 Selenium 连接
    // 这里只是标记状态
    this.connected = true;
  }

  /**
   * 断开连接
   */
  async disconnect(): Promise<void> {
    this.connected = false;
  }

  /**
   * 按客户型号搜索成品料号
   */
  async searchProducts(customerModel: string): Promise<ProductSearchResult> {
    const script = `
import sys
sys.path.insert(0, '..')
from src.services import PLMBomService
from src.config import Config
import json

config = Config()
service = PLMBomService(config)
service.connect()

result = service.search_products('${customerModel}')

output = {
    'success': result.success,
    'customer_model': result.customer_model,
    'total_rows': result.total_rows,
    'part_numbers': [row[0] for row in result.data] if result.data else [],
    'files': result.files
}

service.disconnect()
print(json.dumps(output, ensure_ascii=False))
`;

    const result = await this.executePython(script);

    if (!result.success) {
      throw new Error(result.error);
    }

    const data = JSON.parse(result.output);

    return {
      customer_model: data.customer_model,
      total_rows: data.total_rows,
      part_numbers: data.part_numbers,
      files: data.files || {}
    };
  }

  /**
   * 按成品料号查询 BOM
   */
  async searchBom(materialNumber: string): Promise<BomSearchResult> {
    const script = `
import sys
sys.path.insert(0, '..')
from src.services import PLMBomService
from src.config import Config
import json

config = Config()
service = PLMBomService(config)
service.connect()

result = service.search_bom('${materialNumber}')

output = {
    'success': result.success,
    'material_number': result.material_number,
    'total_rows': result.total_rows,
    'files': result.files
}

service.disconnect()
print(json.dumps(output, ensure_ascii=False))
`;

    const result = await this.executePython(script);

    if (!result.success) {
      throw new Error(result.error);
    }

    const data = JSON.parse(result.output);

    return {
      material_number: data.material_number,
      total_rows: data.total_rows,
      files: data.files || {}
    };
  }

  /**
   * 完整搜索：搜索产品并获取所有 BOM
   */
  async fullSearch(customerModel: string): Promise<FullSearchResult> {
    // 先搜索产品
    const products = await this.searchProducts(customerModel);

    // 获取所有 BOM
    const boms: BomSearchResult[] = [];
    let totalBomRows = 0;

    for (const partNumber of products.part_numbers) {
      try {
        const bom = await this.searchBom(partNumber);
        boms.push(bom);
        totalBomRows += bom.total_rows;
      } catch (error) {
        // 单个 BOM 查询失败不影响整体
        console.error(`BOM 查询失败 ${partNumber}:`, error);
      }
    }

    return {
      customer_model: customerModel,
      products,
      boms,
      total_bom_rows: totalBomRows
    };
  }

  /**
   * 执行 Python 脚本
   */
  private async executePython(script: string): Promise<{ success: boolean; output?: string; error?: string }> {
    return new Promise((resolve) => {
      // 清理脚本中的多余空白
      const cleanScript = script.replace(/\n+/g, '\n').trim();

      const child = spawn(this.pythonPath, ['-c', cleanScript], {
        cwd: process.cwd(),
        env: {
          ...process.env,
          PYTHONPATH: process.cwd()
        }
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, output: stdout.trim() });
        } else {
          resolve({ success: false, error: stderr || `Python 脚本执行失败 (code: ${code})` });
        }
      });

      child.on('error', (err) => {
        resolve({ success: false, error: err.message });
      });

      // 超时处理 (60秒)
      setTimeout(() => {
        child.kill();
        resolve({ success: false, error: '执行超时 (60秒)' });
      }, 60000);
    });
  }
}
