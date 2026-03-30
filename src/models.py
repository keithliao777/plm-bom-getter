"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchResult:
    """搜索结果基类"""
    success: bool
    total_rows: int = 0
    error: Optional[str] = None


@dataclass
class ProductSearchResult(SearchResult):
    """成品料号搜索结果"""
    customer_model: str = ""
    header: list = field(default_factory=list)
    data: list = field(default_factory=list)
    files: dict = field(default_factory=dict)


@dataclass
class BomSearchResult(SearchResult):
    """BOM搜索结果"""
    material_number: str = ""
    header: list = field(default_factory=list)
    data: list = field(default_factory=list)
    files: dict = field(default_factory=dict)


@dataclass
class ProductInfo:
    """产品信息"""
    material_number: str
    description: str = ""
    lifecycle: str = ""
    material_category: str = ""
    brand_category: str = ""
    customer_model: str = ""
    update_date: str = ""


@dataclass
class BomItem:
    """BOM项目"""
    level: str
    parent_part_number: str
    sequence: str
    child_part_number: str
    material_category: str
    material_description: str
    quantity: str
    preferred_level: str = ""
    position: str = ""
    alternative_group: str = ""
    combination: str = ""
