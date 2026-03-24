# PLM 系统操作指南

## 系统访问

### URL 地址
- **物料查询页面**: `http://oa.netcoretec.com/wui/index.html#/main/cube/search?customid=78`
- **BOM 查询页面**: `http://oa.netcoretec.com/wui/index.html#/main/cube/search?customid=80`

### 登录要求
- 需要内网环境访问
- 使用公司账号登录

---

## 页面元素说明

### 物料查询页面

| 元素 | Ref | 说明 |
|------|-----|------|
| 客标型号输入框 | e3946 | 输入产品型号进行搜索 |
| 搜索按钮 | e199 | 执行搜索操作 |
| 结果表格 | e199 | 显示搜索结果 |

### BOM 查询页面

| 元素 | Ref | 说明 |
|------|-----|------|
| 顶层料号输入框 | e273 | 输入成品料号 |
| 层级选择 | e165-e177 | 选择 BOM 层级（多层/1-6 层） |
| 结果表格 | e199 | 显示 BOM 数据 |

---

## 操作注意事项

### 1. 下拉列表处理

在物料查询页面输入产品型号后，系统会显示下拉列表：

**可能的情况**：
- 输入"N3D"，下拉显示：N3D, N3D-V2, N3D-Pro
- 输入"NX31"，下拉显示：NX31

**处理原则**：
1. 优先选择与输入**完全匹配**的选项
2. 如果没有完全匹配，提示用户确认
3. 不要选择近似型号

### 2. 数据加载等待

| 操作 | 等待时间 | 说明 |
|------|---------|------|
| 页面加载 | 5 秒 | 确保页面完全加载 |
| 输入后 | 2 秒 | 确保输入完成 |
| 搜索后 | 5 秒 | 等待后端数据返回 |
| BOM 加载 | 5-10 秒 | 复杂 BOM 需要更长时间 |

### 3. 数据提取

使用 JavaScript 提取表格数据：

```javascript
() => {
    const rows = document.querySelectorAll('.ant-table-tbody > tr');
    const data = [];
    for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            data.push({
                物料号：cells[0].textContent.trim(),
                描述：cells[1].textContent.trim(),
                生命周期：cells[2].textContent.trim(),
                物料分类：cells[3].textContent.trim(),
                品牌类别：cells[4].textContent.trim(),
                客标型号：cells[5].textContent.trim(),
                更新日期：cells[6].textContent.trim()
            });
        }
    }
    return JSON.stringify(data, null, 2);
}
```

---

## 错误处理

### 超时错误
```python
try:
    browser.act(...)
except TimeoutError:
    # 重新获取快照
    browser.snapshot(...)
    # 重试
    browser.act(...)
```

### 元素未找到
```python
try:
    browser.act(ref="e273", ...)
except Exception as e:
    # 重新获取快照获取最新 ref
    browser.snapshot(...)
    # 使用新 ref 重试
```

---

## 相关文档

- [BOM 数据结构说明](bom_structure.md)
- [常见问题解决方案](faq.md)
