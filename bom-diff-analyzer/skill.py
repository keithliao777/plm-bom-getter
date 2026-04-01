#!/usr/bin/env python3
"""
BOM 差异分析技能 - 主入口

基于产品描述解析和逐层 BOM 比较，自动识别多型号产品之间的 BOM 差异，
并智能判断差异的合理性（正常/异常/需确认）。

用法:
    python skill.py --bom-directory <BOM目录> --products-file <产品文件>
                    --standard-pn <标准料号> --output-directory <输出目录>
                    [--output-filename <输出文件名>]

示例:
    python skill.py ^
        --bom-directory "C:\\PLM\\NX30\\By_CPU\\MT7981B" ^
        --products-file "C:\\PLM\\NX30\\NX30_products_20260331_151559.xlsx" ^
        --standard-pn "30006913" ^
        --output-directory "C:\\PLM\\NX30" ^
        --output-filename "01_BOM 差异详细对比表.xlsx"
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.config import Config
from src.models import AnalyzerResult, ProductInfo, DiffItem
from src.exceptions import (
    BomDiffAnalyzerError,
    FileReadError,
    InvalidInputError,
)
from src.parser import (
    read_products_file,
    read_all_boms,
    parse_product_desc,
)
from src.analyzer import (
    compare_layer,
    is_diff_reasonable,
    build_diff_reason_description,
)
from src.reporter import (
    generate_excel_report,
    calculate_statistics,
    get_abnormal_items,
    generate_message,
)


def validate_inputs(
    bom_directory: str,
    products_file: str,
    standard_pn: str,
    output_directory: str
) -> None:
    """
    验证输入参数

    Args:
        bom_directory: BOM 目录
        products_file: 产品文件路径
        standard_pn: 标准料号
        output_directory: 输出目录

    Raises:
        InvalidInputError: 参数无效
    """
    if not bom_directory or not Path(bom_directory).exists():
        raise InvalidInputError(f"BOM 目录不存在或为空: {bom_directory}")

    if not products_file or not Path(products_file).exists():
        raise InvalidInputError(f"产品文件不存在或为空: {products_file}")

    if not standard_pn:
        raise InvalidInputError("标准料号不能为空")

    if not output_directory or not Path(output_directory).exists():
        raise InvalidInputError(f"输出目录不存在或为空: {output_directory}")


def bom_diff_analyzer(
    bom_directory: str,
    products_file: str,
    standard_pn: str,
    output_directory: str,
    output_filename: Optional[str] = None,
    config: Optional[Config] = None
) -> AnalyzerResult:
    """
    BOM 差异分析主函数

    Args:
        bom_directory: BOM 文件目录
        products_file: 成品料号清单文件
        standard_pn: 标准料号（作为比较基准）
        output_directory: 输出文件目录
        output_filename: 输出文件名（可选，默认 01_BOM 差异详细对比表.xlsx）
        config: 配置对象（可选）

    Returns:
        AnalyzerResult: 分析结果
    """
    if config is None:
        config = Config()

    # 使用默认值
    if output_filename is None:
        output_filename = config.default_output_filename

    try:
        # 1. 验证输入
        validate_inputs(bom_directory, products_file, standard_pn, output_directory)

        # 2. 读取产品描述
        product_descriptions = read_products_file(products_file, config)

        # 检查标准料号是否在产品文件中
        if standard_pn not in product_descriptions:
            return AnalyzerResult(
                status='error',
                error=f"标准料号 {standard_pn} 不在产品文件 {products_file} 中"
            )

        # 解析所有产品描述
        parsed_descs: dict[str, ProductInfo] = {}
        for pn, desc in product_descriptions.items():
            parsed_descs[pn] = parse_product_desc(desc)

        # 3. 读取所有 BOM 文件
        all_boms = read_all_boms(bom_directory, config)

        # 检查标准 BOM 是否存在
        if standard_pn not in all_boms:
            return AnalyzerResult(
                status='error',
                error=f"标准料号 {standard_pn} 的 BOM 文件未在目录 {bom_directory} 中找到"
            )

        # 4. 逐层比较 BOM
        diff_items: list[DiffItem] = []

        for pn, df in all_boms.items():
            if pn == standard_pn:
                continue

            if pn not in parsed_descs:
                continue

            std_df = all_boms[standard_pn]

            for layer in config.layer_range:
                differences = compare_layer(std_df, df, layer, config)

                for diff in differences:
                    # 判断差异合理性
                    judgment, note = is_diff_reasonable(
                        layer,
                        diff['mat_code'],
                        diff['diff_type'],
                        diff['reason'],
                        standard_pn,
                        pn,
                        parsed_descs,
                        diff['mat_desc'],
                        config
                    )

                    # 构建差异原因描述
                    diff_reason = build_diff_reason_description(
                        layer,
                        diff['mat_code'],
                        diff['diff_type'],
                        standard_pn,
                        pn,
                        parsed_descs,
                        std_df,
                        df,
                        config
                    )

                    diff_items.append(DiffItem(
                        layer=layer,
                        std_pn=standard_pn,
                        std_desc=product_descriptions.get(standard_pn, ''),
                        other_pn=pn,
                        other_desc=product_descriptions.get(pn, ''),
                        diff_type=diff['diff_type'],
                        mat_code=diff['mat_code'],
                        mat_desc=diff['mat_desc'],
                        diff_reason=diff_reason,
                        diff_judgment=judgment,
                        judgment_note=note
                    ))

        # 5. 生成 Excel 报告
        output_file = generate_excel_report(
            diff_items,
            output_directory,
            output_filename,
            config
        )

        # 6. 计算统计信息
        statistics = calculate_statistics(diff_items)

        # 7. 获取异常差异
        abnormal = get_abnormal_items(diff_items, limit=5)

        # 8. 返回结果
        return AnalyzerResult(
            status='success',
            output_file=output_file,
            statistics=statistics,
            abnormal_items=abnormal,
            message=generate_message(statistics)
        )

    except InvalidInputError as e:
        return AnalyzerResult(status='error', error=f"输入参数错误: {e}")
    except FileReadError as e:
        return AnalyzerResult(status='error', error=f"文件读取错误: {e}")
    except BomDiffAnalyzerError as e:
        return AnalyzerResult(status='error', error=str(e))
    except Exception as e:
        return AnalyzerResult(status='error', error=f"分析失败: {e}")


def main() -> int:
    """
    命令行主入口
    """
    parser = argparse.ArgumentParser(
        description='BOM 差异分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--bom-directory', '-d',
        required=True,
        help='BOM 文件目录（必填）'
    )

    parser.add_argument(
        '--products-file', '-p',
        required=True,
        help='成品料号清单文件（必填）'
    )

    parser.add_argument(
        '--standard-pn', '-s',
        required=True,
        help='标准料号，作为比较基准（必填）'
    )

    parser.add_argument(
        '--output-directory', '-o',
        required=True,
        help='输出文件目录（必填）'
    )

    parser.add_argument(
        '--output-filename', '-f',
        default=None,
        help='输出文件名（可选，默认 01_BOM 差异详细对比表.xlsx）'
    )

    args = parser.parse_args()

    result = bom_diff_analyzer(
        bom_directory=args.bom_directory,
        products_file=args.products_file,
        standard_pn=args.standard_pn,
        output_directory=args.output_directory,
        output_filename=args.output_filename
    )

    # 输出结果
    if result.status == 'success':
        print(f"✓ {result.message}")
        print(f"  输出文件: {result.output_file}")
        print(f"  总差异数: {result.statistics.total_differences}")
        print(f"    - 正常差异: {result.statistics.normal_count}")
        print(f"    - 异常差异: {result.statistics.abnormal_count}")
        print(f"    - 需确认差异: {result.statistics.review_count}")

        if result.abnormal_items:
            print()
            print("异常差异列表（前 5 条）:")
            for item in result.abnormal_items:
                print(f"  - 料号 {item.other_pn}, 物料 {item.mat_code}: {item.judgment_note}")
    else:
        print(f"✗ 分析失败: {result.error}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
