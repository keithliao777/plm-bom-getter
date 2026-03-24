# -*- coding: utf-8 -*-
"""
PLM BOM 获取工具
根据成品料号获取完整 BOM 数据并保存为 Excel 和 JSON
"""

import json
import pandas as pd
from datetime import datetime
import os

def save_bom_to_excel_and_json(bom_data, part_number, output_dir=None):
    """
    将 BOM 数据保存为 Excel 和 JSON 文件
    
    Args:
        bom_data: BOM 数据列表
        part_number: 成品料号
        output_dir: 输出目录，默认为 C:\Users\Administrator\.openclaw\plm-exports\BOM\
    
    Returns:
        json_path: JSON 文件路径
        excel_path: Excel 文件路径
    """
    if output_dir is None:
        output_dir = rf"C:\Users\Administrator\.openclaw\plm-exports\BOM\{part_number}"
    
    # 创建目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    today = datetime.now().strftime('%Y%m%d')
    json_filename = f"BOM_{part_number}_data.json"
    excel_filename = f"BOM_{part_number}_{today}.xlsx"
    
    json_path = os.path.join(output_dir, json_filename)
    excel_path = os.path.join(output_dir, excel_filename)
    
    # 保存 JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(bom_data, f, ensure_ascii=False, indent=2)
    
    # 保存 Excel
    df = pd.DataFrame(bom_data)
    df.to_excel(excel_path, index=False)
    
    print(f"BOM 文件已保存：")
    print(f"  JSON: {json_path}")
    print(f"  Excel: {excel_path}")
    print(f"共 {len(bom_data)} 行数据")
    
    return json_path, excel_path


def extract_bom_from_html(html_table):
    """
    从 HTML 表格中提取 BOM 数据
    
    Args:
        html_table: HTML 表格数据
    
    Returns:
        BOM 数据列表
    """
    bom_data = []
    
    for row in html_table:
        cells = row.get('cells', [])
        if len(cells) >= 6:
            bom_data.append({
                '层级': cells[0].get('text', '').strip(),
                '父阶料号': cells[1].get('text', '').strip(),
                '顺序号': cells[2].get('text', '').strip(),
                '子阶料号': cells[3].get('text', '').strip(),
                '物料描述': cells[4].get('text', '').strip(),
                '用量': cells[5].get('text', '').strip(),
                '优选等级': cells[6].get('text', '').strip() if len(cells) > 6 else '',
                '位号': cells[7].get('text', '').strip() if len(cells) > 7 else '',
                '替代组': cells[8].get('text', '').strip() if len(cells) > 8 else '',
                '组合': cells[9].get('text', '').strip() if len(cells) > 9 else ''
            })
    
    return bom_data


if __name__ == "__main__":
    # 测试数据
    test_data = [
        {
            '层级': '1',
            '父阶料号': '30007324',
            '顺序号': '0010',
            '子阶料号': '10022645',
            '物料描述': '外置电缆，网线，CAT5e',
            '用量': '1',
            '优选等级': '慎选'
        }
    ]
    
    json_path, excel_path = save_bom_to_excel_and_json(test_data, '30007324')
    print(f"测试完成：{json_path}, {excel_path}")
