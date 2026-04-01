"""
报告生成模块

实现 Excel 报告生成和统计计算
"""

from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import Config
from src.models import Statistics, DiffItem
from src.exceptions import FileWriteError


def generate_excel_report(
    diff_items: list[DiffItem],
    output_directory: str,
    output_filename: str,
    config: Optional[Config] = None
) -> str:
    """
    生成 Excel 差异报告

    Args:
        diff_items: 差异项列表
        output_directory: 输出目录
        output_filename: 输出文件名
        config: 配置对象

    Returns:
        str: 输出文件完整路径

    Raises:
        FileWriteError: 文件写入失败
    """
    if config is None:
        config = Config()

    # 构建输出路径
    output_dir = Path(output_directory)
    if not output_dir.exists():
        raise FileWriteError(f"输出目录不存在: {output_directory}")

    output_file = output_dir / output_filename

    # 转换为 DataFrame
    data = []
    for item in diff_items:
        data.append({
            '比较层级': f'层级 {item.layer}',
            '标准料号': item.std_pn,
            '标准描述': item.std_desc,
            '比较料号': item.other_pn,
            '比较描述': item.other_desc,
            '差异类型': item.diff_type,
            '物料号': item.mat_code,
            '差异描述': f"{item.diff_type} {item.mat_desc}",
            '差异原因': item.diff_reason,
            '差异判断': item.diff_judgment,
            '判断说明': item.judgment_note,
        })

    df = pd.DataFrame(data)

    # 排序：比较料号↑ → 比较层级↑ → 差异类型↑ → 物料号↑
    if len(df) > 0:
        # 定义排序顺序
        layer_order = {'层级 1': 1, '层级 2': 2, '层级 3': 3, '层级 4': 4, '层级 5': 5}
        diff_type_order = {'增加': 1, '减少': 2}

        df['_layer_num'] = df['比较层级'].map(layer_order)
        df['_diff_type_order'] = df['差异类型'].map(diff_type_order)

        df = df.sort_values(
            by=['比较料号', '_layer_num', '_diff_type_order', '物料号'],
            ascending=[True, True, True, True]
        )

        # 删除排序辅助列
        df = df.drop(columns=['_layer_num', '_diff_type_order'])

    # 输出 Excel
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
    except Exception as e:
        raise FileWriteError(f"写入 Excel 文件失败: {output_file}, 错误: {e}")

    return str(output_file)


def calculate_statistics(diff_items: list[DiffItem]) -> Statistics:
    """
    计算统计信息

    Args:
        diff_items: 差异项列表

    Returns:
        Statistics: 统计信息
    """
    stats = Statistics()

    stats.total_differences = len(diff_items)

    for item in diff_items:
        if item.diff_judgment == '正常':
            stats.normal_count += 1
        elif item.diff_judgment == '异常':
            stats.abnormal_count += 1
        elif item.diff_judgment == '需确认':
            stats.review_count += 1

    return stats


def get_abnormal_items(diff_items: list[DiffItem], limit: int = 5) -> list[DiffItem]:
    """
    获取异常差异列表（前 N 条）

    Args:
        diff_items: 差异项列表
        limit: 返回数量限制

    Returns:
        list[DiffItem]: 异常差异列表
    """
    abnormal = [item for item in diff_items if item.diff_judgment == '异常']
    return abnormal[:limit]


def generate_message(statistics: Statistics) -> str:
    """
    生成执行结果说明

    Args:
        statistics: 统计信息

    Returns:
        str: 结果说明消息
    """
    if statistics.abnormal_count > 0:
        return f"BOM 差异分析完成，发现 {statistics.abnormal_count} 条异常差异，建议优先处理"
    elif statistics.review_count > 0:
        return f"BOM 差异分析完成，发现 {statistics.review_count} 条需确认差异，建议人工审核"
    else:
        return f"BOM 差异分析完成，所有 {statistics.total_differences} 条差异均为正常差异"
