# -*- coding: utf-8 -*-
"""
PLM 成品料号查询工具
根据产品型号查询成品料号并保存为 Excel
"""

import json
import pandas as pd
from datetime import datetime
import os

def save_part_numbers_to_excel(part_numbers_data, model_name, output_dir=None):
    """
    将成品料号数据保存为 Excel 文件
    
    Args:
        part_numbers_data: 料号数据列表
        model_name: 产品型号
        output_dir: 输出目录，默认为 C:\Users\Administrator\.openclaw\plm-exports\
    
    Returns:
        output_path: 保存的文件路径
    """
    if output_dir is None:
        output_dir = r"C:\Users\Administrator\.openclaw\plm-exports"
    
    # 创建目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    today = datetime.now().strftime('%Y%m%d')
    filename = f"{model_name}_成品料号清单_{today}.xlsx"
    output_path = os.path.join(output_dir, filename)
    
    # 保存为 Excel
    df = pd.DataFrame(part_numbers_data)
    df.to_excel(output_path, index=False)
    
    print(f"已保存至：{output_path}")
    print(f"共 {len(part_numbers_data)} 个料号")
    
    return output_path


def filter_finished_goods(materials):
    """
    筛选成品料号（3000 开头）
    
    Args:
        materials: 物料列表
    
    Returns:
        成品料号列表
    """
    return [item for item in materials if item.get('物料号', '').startswith('3000')]


if __name__ == "__main__":
    # 测试数据
    test_data = [
        {
            '物料号': '30007324',
            '描述': '家用无线路由器，N3D，netis，EU',
            '生命周期': '量产',
            '物料分类': '家用无线路由器',
            '品牌类别': '海外自有品牌-netis',
            '客标型号': 'N3D',
            '更新日期': '2025-04-24'
        }
    ]
    
    output_path = save_part_numbers_to_excel(test_data, 'N3D')
    print(f"测试完成：{output_path}")
