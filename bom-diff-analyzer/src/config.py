"""
配置模块

定义配置类和默认值处理
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """BOM 差异分析配置"""
    # 默认输出文件名
    default_output_filename: str = "01_BOM 差异详细对比表.xlsx"

    # BOM 文件名模式（用于从文件名提取料号）
    bom_filename_pattern: str = "_BOM_"

    # Excel 列索引（基于 BOM 文件结构）
    bom_layer_col: int = 0          # 层级列
    bom_parent_pn_col: int = 1     # 父阶料号列
    bom_mat_code_col: int = 3      # 子阶料号（物料号）列
    bom_mat_desc_col: int = 5       # 物料描述列

    # 产品文件列索引
    product_pn_col: int = 0         # 物料号列
    product_desc_col: int = 1      # 描述列

    # BOM 层级范围
    layer_range: range = None       # 默认为 None，由 analyzer 设置

    def __post_init__(self):
        if self.layer_range is None:
            self.layer_range = range(5, 0, -1)  # 5,4,3,2,1
