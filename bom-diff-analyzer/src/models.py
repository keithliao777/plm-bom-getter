"""
数据模型模块

定义 BOM 差异分析相关的数据结构
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductInfo:
    """产品描述解析后的信息"""
    brand: str = ""          # 品牌
    region: str = ""         # 地区
    chipset: str = ""        # 芯片方案
    spec: str = ""          # 产品规格
    power: str = ""          # 电源规格


@dataclass
class DiffItem:
    """单条差异项"""
    layer: int                          # 比较层级
    std_pn: str                         # 标准料号
    std_desc: str                        # 标准版产品描述
    other_pn: str                        # 比较料号
    other_desc: str                       # 比较版产品描述
    diff_type: str                       # 差异类型：增加 / 减少
    mat_code: str                        # 物料号
    mat_desc: str                         # 物料描述
    diff_reason: str                      # 差异原因
    diff_judgment: str                    # 差异判断：正常 / 异常 / 需确认
    judgment_note: str = ""               # 判断说明


@dataclass
class Statistics:
    """统计信息"""
    total_differences: int = 0           # 总差异数
    normal_count: int = 0                 # 正常差异数量
    abnormal_count: int = 0               # 异常差异数量
    review_count: int = 0                  # 需确认差异数量


@dataclass
class AnalyzerResult:
    """分析结果"""
    status: str                            # 状态：success / error
    output_file: str = ""                   # 输出文件路径
    statistics: Statistics = field(default_factory=Statistics)
    abnormal_items: list[DiffItem] = field(default_factory=list)
    message: str = ""                       # 结果说明
    error: Optional[str] = None             # 错误信息（仅 error 时有值）
