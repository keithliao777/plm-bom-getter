"""
差异分析模块

实现 BOM 层级比较和差异合理性判断
"""

from typing import Optional

import pandas as pd

from src.config import Config
from src.models import ProductInfo, DiffItem
from src.parser import (
    parse_product_desc,
    get_layer_materials,
    get_mat_desc,
)


def compare_layer(
    std_df: pd.DataFrame,
    other_df: pd.DataFrame,
    layer: int,
    config: Optional[Config] = None
) -> list[dict]:
    """
    比较两个 BOM 在指定层级的差异

    Args:
        std_df: 标准 BOM DataFrame
        other_df: 比较 BOM DataFrame
        layer: 层级号 (1-5)
        config: 配置对象

    Returns:
        list[dict]: 差异列表，每项包含 mat_code, diff_type, reason
    """
    if config is None:
        config = Config()

    std_mats = get_layer_materials(std_df, layer, config)
    other_mats = get_layer_materials(other_df, layer, config)

    differences = []

    # 增加的物料（存在于 other 但不存在于 std）
    for mat in other_mats - std_mats:
        mat_desc = get_mat_desc(other_df, mat, config)
        differences.append({
            'mat_code': mat,
            'diff_type': '增加',
            'mat_desc': mat_desc,
            'reason': _analyze_diff_reason(layer, mat, '增加', mat_desc)
        })

    # 减少的物料（存在于 std 但不存在于 other）
    for mat in std_mats - other_mats:
        mat_desc = get_mat_desc(std_df, mat, config)
        differences.append({
            'mat_code': mat,
            'diff_type': '减少',
            'mat_desc': mat_desc,
            'reason': _analyze_diff_reason(layer, mat, '减少', mat_desc)
        })

    return differences


def _analyze_diff_reason(layer: int, mat_code: str, diff_type: str, mat_desc: str) -> str:
    """
    分析差异原因描述

    Args:
        layer: 层级
        mat_code: 物料号
        diff_type: 差异类型（增加/减少）
        mat_desc: 物料描述

    Returns:
        str: 差异原因描述
    """
    # 根据物料描述关键词生成原因
    if '彩盒' in mat_desc or '外箱' in mat_desc:
        return f"包装物料{diff_type}"
    elif 'CE 宣告书' in mat_desc or 'FCC' in mat_desc:
        return f"认证文件{diff_type}"
    elif '保修贴' in mat_desc or '安装指南' in mat_desc or '说明书' in mat_desc:
        return f"文档资料{diff_type}"
    elif 'SMT' in mat_desc or 'DIP' in mat_desc or 'PCBA' in mat_desc:
        return f"PCBA 物料{diff_type}"
    elif '电源' in mat_desc:
        return f"电源{diff_type}"
    elif '天线' in mat_desc or '外壳' in mat_desc:
        return f"结构件{diff_type}"
    else:
        return f"物料{diff_type}"


def is_diff_reasonable(
    layer: int,
    mat_code: str,
    diff_type: str,
    diff_reason: str,
    std_pn: str,
    other_pn: str,
    parsed_descs: dict[str, ProductInfo],
    mat_desc: str,
    config: Optional[Config] = None
) -> tuple[str, str]:
    """
    判断差异是否合理

    Args:
        layer: 层级
        mat_code: 物料号
        diff_type: 差异类型（增加/减少）
        diff_reason: 差异原因
        std_pn: 标准料号
        other_pn: 比较料号
        parsed_descs: 解析后的产品描述字典
        mat_desc: 物料描述
        config: 配置对象

    Returns:
        tuple[str, str]: (判断结果, 判断说明)
            判断结果: '正常' / '异常' / '需确认'
    """
    if config is None:
        config = Config()

    std_info = parsed_descs.get(std_pn, ProductInfo())
    other_info = parsed_descs.get(other_pn, ProductInfo())

    # 比较产品描述的关键信息
    brand_same = std_info.brand == other_info.brand
    region_same = std_info.region == other_info.region
    chipset_same = std_info.chipset == other_info.chipset
    spec_same = std_info.spec == other_info.spec
    power_same = std_info.power == other_info.power

    # === 异常场景：产品描述完全相同，但 BOM 有差异 ===
    if brand_same and region_same and chipset_same and spec_same and power_same:
        return '异常', '产品描述完全相同，BOM 不应有差异'

    # === 正常场景：基于产品描述差异的预期 BOM 差异 ===

    # 1. 品牌不同 → 包装/标识类差异正常
    if not brand_same:
        if '彩盒' in mat_desc or '外箱' in mat_desc:
            return '正常', '品牌不同，包装必须独立'

        if 'CE 宣告书' in mat_desc or 'FCC' in mat_desc:
            if region_same:
                return '需确认', '品牌不同但地区相同，认证内容相同，确认是否可共用物料'
            else:
                return '正常', '品牌不同且地区不同，认证文件必须独立'

        if '保修贴' in mat_desc or '安装指南' in mat_desc or '说明书' in mat_desc:
            return '需确认', '品牌不同，但功能/内容可能相同，确认是否可共用物料'

        if 'SMT' in mat_desc or 'DIP' in mat_desc or 'PCBA' in mat_desc:
            return '正常', '品牌不同，PCBA 丝印/标识必须独立'

    # 2. 地区不同 → 电源/认证差异正常
    if not region_same:
        if '电源' in mat_desc or 'CE' in mat_desc or 'FCC' in mat_desc:
            return '正常', '地区不同，电源/认证要求不同'

    # 3. 规格不同 → 结构件差异正常
    if not spec_same:
        if '天线' in mat_desc or '外壳' in mat_desc:
            return '正常', '产品规格不同，结构件差异合理'

    # 4. 芯片方案不同 → 元器件差异正常
    if not chipset_same:
        if layer == 5:  # 基础元器件
            return '正常', '芯片方案不同，元器件差异合理'

    # 5. 层级 2-4 的结构件/SMT/DIP 差异，通常是正常的
    if layer in [2, 3, 4]:
        return '正常', '客户定制差异'

    # 6. 层级 1 的组装差异
    if layer == 1:
        if 'ASS' in mat_desc:
            return '正常', '组装版本差异'

    return '需确认', '需要人工审核'


def build_diff_reason_description(
    layer: int,
    mat_code: str,
    diff_type: str,
    std_pn: str,
    other_pn: str,
    parsed_descs: dict[str, ProductInfo],
    std_df: pd.DataFrame,
    other_df: pd.DataFrame,
    config: Optional[Config] = None
) -> str:
    """
    构建差异原因的完整描述

    格式: 比较料号 - 品牌 描述；标准料号 - 品牌 描述；原因说明
    """
    if config is None:
        config = Config()

    std_info = parsed_descs.get(std_pn, ProductInfo())
    other_info = parsed_descs.get(other_pn, ProductInfo())

    mat_desc = ''
    if diff_type == '增加':
        mat_desc = get_mat_desc(other_df, mat_code, config)
    else:
        mat_desc = get_mat_desc(std_df, mat_code, config)

    parts = []

    # 比较料号的描述
    if other_info.brand:
        parts.append(f"{other_pn} - {other_info.brand} {mat_desc}")
    else:
        parts.append(f"{other_pn} - {mat_desc}")

    # 标准料号的描述
    if std_info.brand:
        parts.append(f"{std_pn} - {std_info.brand} {mat_desc}")
    else:
        parts.append(f"{std_pn} - {mat_desc}")

    return "；".join(parts)
