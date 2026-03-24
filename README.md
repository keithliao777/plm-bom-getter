# PLM-BOM Getter Skill

使用 Chrome MCP 直连方式从 PLM 系统获取成品料号和完整 BOM 数据。

## 功能特性

- ✅ 根据产品型号查询成品料号（支持单个/批量）
- ✅ 根据成品料号获取完整 BOM（支持单个/批量）
- ✅ 自动保存为 Excel 和 JSON 格式
- ✅ 精确匹配产品型号（处理下拉列表多选）
- ✅ 批量处理自动生成汇总报告

## 安装方法

### 方法 1：直接下载
```bash
git clone https://github.com/YOUR_USERNAME/plm-bom-getter.git
```

### 方法 2：使用 OpenClaw
将技能包导入 OpenClaw 技能目录。

## 使用方法

### 查询成品料号
```
请查询产品型号 N3D 的成品料号
```

### 获取完整 BOM
```
请获取成品料号 30007324 的完整 BOM
```

### 批量操作
```
请获取以下料号的 BOM：30007324, 30007392, 30007433
```

## 输出示例

### 成品料号清单
| 物料号 | 描述 | 生命周期 | 物料分类 | 品牌类别 | 更新日期 |
|--------|------|---------|---------|---------|---------|
| 30007324 | 家用无线路由器，N3D... | 量产 | 家用无线路由器 | netis | 2025-04-24 |

### BOM 数据
| 层级 | 父阶料号 | 顺序号 | 子阶料号 | 物料描述 | 用量 |
|------|---------|--------|---------|---------|------|
| 1 | 30007324 | 0010 | 10022645 | 外置电缆，网线 | 1 |
| 2 | 20009550 | 0010 | 10021040 | 组装件，塑胶机壳 | 1 |

## 文件结构

```
plm-bom-getter/
├── SKILL.md                    # 技能主文档
├── scripts/
│   ├── search_part_number.py   # 料号查询脚本
│   └── get_bom.py              # BOM 获取脚本
├── references/
│   ├── plm_guide.md            # PLM 系统操作指南
│   ├── bom_structure.md        # BOM 数据结构说明
│   └── faq.md                  # 常见问题解决方案
├── assets/                     # 资源文件（可选）
├── auto_upload.ps1             # GitHub 自动上传脚本
└── upload_to_github.bat        # GitHub 上传批处理
```

## 上传到 GitHub

### 自动上传（推荐）
```powershell
# 1. 编辑 auto_upload.ps1，修改 GITHUB_USERNAME 为您的 GitHub 用户名
# 2. 运行脚本
.\auto_upload.ps1
```

### 手动上传
```bash
cd plm-bom-getter
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/plm-bom-getter.git
git push -u origin main
```

## 系统要求

- Chrome 浏览器
- OpenClaw Chrome MCP 服务
- PLM 系统访问权限（内网环境）
- Python 3.7+
- pandas 库

## 注意事项

1. **内网访问**: PLM 系统仅在内网环境可访问
2. **精确匹配**: 产品型号搜索时选择完全匹配的选项
3. **等待时间**: BOM 数据加载需要 5-10 秒
4. **文件保存**: 默认保存到 `C:\Users\Administrator\.openclaw\plm-exports\`

## 常见问题

### Q: 搜索产品型号时没有下拉选项？
A: 检查输入是否正确，或尝试点击输入框后再输入。

### Q: BOM 数据加载不完整？
A: 增加等待时间至 10 秒，或检查网络状态。

### Q: 如何区分成品料号和半成品料号？
A: 
- 成品料号：3000 开头
- 半成品料号：2000 开头
- 原材料：1000 开头

## 版本历史

### v1.0 (2026-03-24)
- ✅ 初始版本
- ✅ 支持产品型号查询成品料号
- ✅ 支持成品料号获取完整 BOM
- ✅ 支持单个和批量操作
- ✅ 自动保存为 Excel 和 JSON

## 许可证

本技能仅供内部使用。

## 联系方式

如有问题，请联系技能创建者。
