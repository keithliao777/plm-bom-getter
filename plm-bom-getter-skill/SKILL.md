# PLM BOM Getter Skill

从 PLM 系统 (oa.netcoretec.com) 获取 BOM 数据的自动化工具。

## 功能描述

- **按客户型号搜索成品料号**：输入客户型号（如 N3D、NW4），获取所有匹配的成品料号
- **按成品料号查询 BOM**：输入成品料号，获取完整的多层 BOM 结构
- **批量获取**：支持获取某型号下所有成品料号的 BOM 数据

## 使用场景

### Use when...
- PM 需要快速比对不同产品的 BOM 差异
- 需要导出 PLM 系统中的物料清单数据
- 需要批量获取某客户型号下所有产品的 BOM

### Don't use when...
- PLM 系统不可访问或未登录
- Chrome 浏览器未启用远程调试端口 (9222)
- 需要获取单层 BOM（当前仅支持多层）

## 前置条件

### 1. Chrome 浏览器准备
```bash
# 启动 Chrome 并启用远程调试
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Users\keith liao\AppData\Local\Temp\chrome-debug
```

### 2. 环境要求
- Python 3.10+
- Chrome/Chromium 浏览器
- ChromeDriver (已配置在 `C:/Users/keith liao/.cache/selenium/chromedriver/`)

## 工作流程

### Step 1: 连接 PLM 系统
```
工具: Bash
命令: python -c "from src.services import PLMBomService; ..."
条件: Chrome 必须在端口 9222 监听
产出: 与 Chrome 建立 Selenium 连接
```

### Step 2: 执行操作
```
分支判断:
  IF action == "search-products"
    THEN 执行客户型号搜索
  IF action == "search-bom"
    THEN 执行 BOM 查询
  IF action == "full-search"
    THEN 执行完整搜索（搜索 + 所有 BOM）
```

### Step 3: 处理结果
```
产出:
  - Excel 文件 (BOM 数据)
  - TXT 文件 (成品料号列表)
  - 控制台输出 (摘要信息)
```

## 命令格式

### 搜索成品料号
```
/plm-bom-getter search-products N3D
```

### 查询 BOM
```
/plm-bom-getter search-bom 30008018
```

### 完整搜索
```
/plm-bom-getter full-search NW4
```

## 输入/输出示例

### search-products 输入
```json
{
  "action": "search-products",
  "customer_model": "N3D"
}
```

### search-products 输出
```json
{
  "success": true,
  "data": {
    "customer_model": "N3D",
    "total_rows": 2,
    "part_numbers": ["30008018", "30008019"],
    "files": {
      "products": "C:/Users/keith liao/.openclaw/plm-exports/N3D_products_20260331.xlsx",
      "part_numbers": "C:/Users/keith liao/.openclaw/plm-exports/N3D_part_numbers_20260331.txt"
    }
  }
}
```

### search-bom 输入
```json
{
  "action": "search-bom",
  "material_number": "30008018"
}
```

### search-bom 输出
```json
{
  "success": true,
  "data": {
    "material_number": "30008018",
    "total_rows": 155,
    "files": {
      "bom": "C:/Users/keith liao/.openclaw/plm-exports/30008018_BOM_20260331.xlsx"
    }
  }
}
```

## 边界案例

| 场景 | 输入 | 预期行为 |
|------|------|----------|
| 无效客户型号 | `XXXXX` | 返回空列表，无文件生成 |
| 无效料号 | `99999999` | BOM 查询返回 0 条 |
| Chrome 未启动 | 端口 9222 无监听 | 抛出 `ChromeConnectionError` |
| PLM 会话过期 | 页面显示重新登录 | 提示用户重新登录 |

## 错误处理

```typescript
// 错误类型
enum SkillError {
  CHROME_NOT_RUNNING = "Chrome 未启动或端口 9222 未监听",
  PLM_SESSION_EXPIRED = "PLM 会话过期，请重新登录",
  ELEMENT_NOT_FOUND = "页面元素未找到",
  SEARCH_TIMEOUT = "搜索超时"
}
```

## 输出文件位置

默认输出目录: `C:/Users/keith liao/.openclaw/plm-exports/`

文件命名规则:
- 产品数据: `{customer_model}_products_{timestamp}.xlsx`
- 料号列表: `{customer_model}_part_numbers_{timestamp}.txt`
- BOM 数据: `{material_number}_BOM_{timestamp}.xlsx`

## 技术实现

- **语言**: Python 3.10+
- **浏览器自动化**: Selenium 4.41.0
- **数据处理**: Pandas + openpyxl
- **架构**: 分层设计 (Repository → Service → CLI)
