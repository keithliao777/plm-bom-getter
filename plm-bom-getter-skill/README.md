# PLM BOM Getter Skill

从 PLM 系统 (oa.netcoretec.com) 获取 BOM 数据的 OpenClaw Skill。

## 功能

- **按客户型号搜索成品料号**：输入客户型号（如 N3D、NW4），获取所有匹配的成品料号
- **按成品料号查询 BOM**：输入成品料号，获取完整的多层 BOM 结构
- **批量获取**：支持获取某型号下所有成品料号的 BOM 数据

## 安装

```bash
openclaw skills install ./plm-bom-getter-skill
```

## 前置条件

### 1. Chrome 浏览器

启动 Chrome 并启用远程调试：

```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Users\keith liao\AppData\Local\Temp\chrome-debug

# Linux/Mac
google-chrome --remote-debugging-port=9222
```

### 2. Python 依赖

```bash
pip install selenium==4.41.0 pandas==2.2.3 openpyxl==3.1.5
```

### 3. ChromeDriver

确保 ChromeDriver 与 Chrome 版本匹配，并位于默认路径：
`C:/Users/keith liao/.cache/selenium/chromedriver/win64/146.0.7680.165/chromedriver.exe`

## 使用方式

### OpenClaw 命令

```bash
# 搜索成品料号
/plm-bom-getter search-products N3D

# 查询 BOM
/plm-bom-getter search-bom 30008018

# 完整搜索
/plm-bom-getter full-search NW4
```

### 代码调用

```typescript
import { createSkill } from 'plm-bom-getter-skill';

const skill = createSkill();
const result = await skill.execute({
  action: 'search-products',
  customer_model: 'N3D'
});
```

## 配置

配置文件 `config.json`（可选）：

```json
{
  "chrome_debug_port": 9222,
  "chromedriver_path": "C:/Users/keith liao/.cache/selenium/chromedriver/win64/146.0.7680.165/chromedriver.exe",
  "output_dir": "C:/Users/keith liao/.openclaw/plm-exports"
}
```

## 输出

### 文件输出

默认输出目录：`C:/Users/keith liao/.openclaw/plm-exports/`

| 文件类型 | 命名规则 | 说明 |
|----------|----------|------|
| 产品数据 | `{customer_model}_products_{timestamp}.xlsx` | 完整产品信息 |
| 料号列表 | `{customer_model}_part_numbers_{timestamp}.txt` | 每行一个料号 |
| BOM 数据 | `{material_number}_BOM_{timestamp}.xlsx` | BOM 明细 |

### 返回数据格式

```json
{
  "success": true,
  "data": {
    "customer_model": "N3D",
    "total_rows": 2,
    "part_numbers": ["30008018", "30008019"],
    "files": {
      "products": "...",
      "part_numbers": "..."
    }
  }
}
```

## 错误处理

| 错误类型 | 说明 | 处理方式 |
|----------|------|----------|
| `ChromeConnectionError` | Chrome 未启动或端口错误 | 启动 Chrome 并启用调试端口 |
| `PLMSessionExpired` | PLM 会话过期 | 重新登录 PLM |
| `ElementNotFoundError` | 页面元素未找到 | 等待页面加载或检查 PLM 版本 |
| `SearchTimeoutError` | 搜索超时 | 增加等待时间 |

## 开发

```bash
# 安装依赖
npm install

# 构建
npm run build

# 测试
npm test
```

## 许可

MIT License
