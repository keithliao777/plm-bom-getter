"""
BOM 解析模块

实现产品描述解析和 BOM 层级物料提取
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import Config
from src.models import ProductInfo
from src.exceptions import FileReadError, BomParseError, ProductParseError


# 支持的品牌列表（按长度降序排列，确保更长关键词优先匹配）
BRAND_KEYWORDS = ['MOVA LINC0', 'netis', 'stonet', 'Digicom', 'MOVA']

# 地区关键词映射
REGION_KEYWORDS = {
    'EU': ['EU', '欧规'],
    'US': ['US', '美规'],
    '孟加拉': ['孟加拉'],
}

# 产品规格关键词
SPEC_KEYWORDS = ['AX3000', 'AX1800', 'AX6000']


def parse_product_desc(desc: str) -> ProductInfo:
    """
    解析产品描述，提取关键信息

    Args:
        desc: 产品描述字符串

    Returns:
        ProductInfo: 包含 brand/region/chipset/spec/power 的结构
    """
    if not desc or not isinstance(desc, str):
        return ProductInfo()

    desc_clean = desc.strip()
    info = ProductInfo()

    # 1. 提取品牌
    for brand in BRAND_KEYWORDS:
        if brand.lower() in desc_clean.lower():
            info.brand = brand
            break

    # 2. 提取地区
    for region, keywords in REGION_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in desc_clean.lower():
                info.region = region
                break
        if info.region:
            break

    # 3. 提取产品规格
    for spec in SPEC_KEYWORDS:
        if spec in desc_clean.upper():
            info.spec = spec
            break

    # 4. 提取芯片方案 (格式: MTxxxx+MTxxxx+MTxxxx)
    # 注意：MT 后面的编号可能是 MT7981B 这种格式（字母+数字）
    chipset_pattern = r'MT[0-9A-Za-z]+(?:[+×]MT[0-9A-Za-z]+){2}'
    chipset_match = re.search(chipset_pattern, desc_clean)
    if chipset_match:
        # 统一用 + 连接
        info.chipset = chipset_match.group().replace('×', '+')

    # 5. 提取电源规格 (格式: 12V/1.5A)
    power_pattern = r'\d+V/\d+\.?\d*A'
    power_match = re.search(power_pattern, desc_clean)
    if power_match:
        info.power = power_match.group()

    return info


def get_layer_materials(df: pd.DataFrame, layer: int, config: Optional[Config] = None) -> set[str]:
    """
    提取指定层级的物料号集合

    Args:
        df: BOM 数据 DataFrame
        layer: 层级号 (1-5)
        config: 配置对象

    Returns:
        set[str]: 物料号集合
    """
    if config is None:
        config = Config()

    layer_col = config.bom_layer_col
    mat_code_col = config.bom_mat_code_col

    # 筛选指定层级的行
    layer_data = df[df.iloc[:, layer_col].astype(str).str.strip() == str(layer)]

    if len(layer_data) == 0:
        return set()

    # 提取物料号
    mat_codes = layer_data.iloc[:, mat_code_col].astype(str).str.strip()
    # 过滤空值和非数字
    return set(mat_codes[mat_codes != ''].tolist())


def get_mat_desc(df: pd.DataFrame, mat_code: str, config: Optional[Config] = None) -> str:
    """
    根据物料号获取物料描述

    Args:
        df: BOM 数据 DataFrame
        mat_code: 物料号
        config: 配置对象

    Returns:
        str: 物料描述，未找到则返回空字符串
    """
    if config is None:
        config = Config()

    mat_code_col = config.bom_mat_code_col
    mat_desc_col = config.bom_mat_desc_col

    mask = df.iloc[:, mat_code_col].astype(str).str.strip() == str(mat_code).strip()
    matches = df[mask]

    if len(matches) > 0:
        desc = matches.iloc[0, mat_desc_col]
        return str(desc) if pd.notna(desc) else ""

    return ""


def read_products_file(filepath: str, config: Optional[Config] = None) -> dict[str, str]:
    """
    读取产品描述文件

    Args:
        filepath: 产品描述文件路径
        config: 配置对象

    Returns:
        dict: {物料号: 产品描述}

    Raises:
        FileReadError: 文件读取失败
    """
    if config is None:
        config = Config()

    try:
        df = pd.read_excel(filepath, header=0)
    except Exception as e:
        raise FileReadError(f"读取产品文件失败: {filepath}, 错误: {e}")

    products = {}
    pn_col = config.product_pn_col
    desc_col = config.product_desc_col

    for idx, row in df.iterrows():
        if idx == 0:
            continue
        if len(row) <= max(pn_col, desc_col):
            continue

        pn = str(row.iloc[pn_col]).strip()
        desc = str(row.iloc[desc_col]).strip() if pd.notna(row.iloc[desc_col]) else ""

        if pn and desc and pn != '物料号':
            products[pn] = desc

    if not products:
        raise ProductParseError(f"产品文件解析结果为空: {filepath}")

    return products


def read_all_boms(bom_directory: str, config: Optional[Config] = None) -> dict[str, pd.DataFrame]:
    """
    读取目录下所有 BOM 文件

    Args:
        bom_directory: BOM 文件目录
        config: 配置对象

    Returns:
        dict: {料号: BOM DataFrame}

    Raises:
        FileReadError: 文件读取失败
    """
    if config is None:
        config = Config()

    bom_dir = Path(bom_directory)

    if not bom_dir.exists():
        raise FileReadError(f"BOM 目录不存在: {bom_directory}")

    if not bom_dir.is_dir():
        raise FileReadError(f"路径不是目录: {bom_directory}")

    all_boms = {}
    pattern = config.bom_filename_pattern

    for f in bom_dir.glob('*.xlsx'):
        if pattern not in f.name:
            continue

        # 从文件名提取料号: 例如 30008065_BOM_20260331_180041.xlsx
        parts = f.name.split(pattern)
        if len(parts) < 2:
            continue

        pn = parts[0]

        try:
            df = pd.read_excel(f, header=0)
            all_boms[pn] = df
        except Exception as e:
            raise FileReadError(f"读取 BOM 文件失败: {f}, 错误: {e}")

    return all_boms
