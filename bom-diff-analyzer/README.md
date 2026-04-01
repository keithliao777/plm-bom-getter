# BOM 差异分析工具

基于产品描述解析和逐层 BOM 比较，自动识别多型号产品之间的 BOM 差异，并智能判断差异的合理性。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据

确保有以下文件：

- **BOM 文件目录**：包含多个 BOM Excel 文件，命名格式 `料号_BOM_*.xlsx`
- **产品描述文件**：Excel 文件，包含列：物料号、描述

### 3. 运行分析

```bash
python skill.py ^
    --bom-directory "C:\PLM\NX30\By_CPU\MT7981B" ^
    --products-file "C:\PLM\NX30\NX30_products_20260331_151559.xlsx" ^
    --standard-pn "30006913" ^
    --output-directory "C:\PLM\NX30" ^
    --output-filename "01_BOM 差异详细对比表.xlsx"
```

## 项目结构

```
bom-diff-analyzer/
├── SKILL.md           # Skill 说明文档
├── skill.py           # 主入口
├── src/
│   ├── __init__.py
│   ├── config.py      # 配置
│   ├── exceptions.py  # 异常定义
│   ├── models.py      # 数据模型
│   ├── parser.py      # BOM 解析
│   ├── analyzer.py    # 差异分析
│   └── reporter.py     # 报告生成
├── tests/
│   ├── test_parser.py
│   ├── test_analyzer.py
│   └── test_reporter.py
├── requirements.txt
└── README.md
```

## 运行测试

```bash
pytest tests/ -v
```

## 输出示例

```
✓ BOM 差异分析完成，发现 12 条异常差异，建议优先处理
  输出文件: C:\PLM\NX30\01_BOM 差异详细对比表.xlsx
  总差异数: 196
    - 正常差异: 95
    - 异常差异: 12
    - 需确认差异: 89
```
