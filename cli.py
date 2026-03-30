#!/usr/bin/env python3
"""
PLM BOM Getter CLI - 命令行入口
"""

import sys
import argparse
from typing import Optional

from src import PLMBomService
from src.config import Config


def create_service() -> PLMBomService:
    """创建服务实例"""
    config = Config()
    service = PLMBomService(config)
    return service


def cmd_search_products(args) -> int:
    """搜索成品料号"""
    service = create_service()

    try:
        print(f"连接到 PLM 系统...")
        service.connect()
        print(f"已连接")

        print(f"\n搜索客户型号: {args.customer_model}")
        result = service.search_products(args.customer_model)

        if result.success:
            print(f"\n成功！找到 {result.total_rows} 条数据")
            print(f"\n成品料号列表:")
            for row in result.data:
                print(f"  {row[0]}")

            if result.files:
                print(f"\n已保存文件:")
                for key, path in result.files.items():
                    print(f"  {key}: {path}")
            return 0
        else:
            print(f"\n搜索失败: {result.error}")
            return 1

    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        service.disconnect()


def cmd_search_bom(args) -> int:
    """查询BOM"""
    service = create_service()

    try:
        print(f"连接到 PLM 系统...")
        service.connect()
        print(f"已连接")

        print(f"\n查询 BOM: {args.material}")
        result = service.search_bom(args.material)

        if result.success:
            print(f"\n成功！找到 {result.total_rows} 条 BOM 数据")

            if result.files:
                print(f"\n已保存文件:")
                for key, path in result.files.items():
                    print(f"  {key}: {path}")
            return 0
        else:
            print(f"\n查询失败: {result.error}")
            return 1

    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        service.disconnect()


def cmd_full_search(args) -> int:
    """完整搜索（产品+BOM）"""
    service = create_service()

    try:
        print(f"连接到 PLM 系统...")
        service.connect()
        print(f"已连接")

        print(f"\n搜索客户型号: {args.customer_model}")
        product_result, bom_result = service.search_products_and_bom(args.customer_model)

        if product_result.success:
            print(f"\n产品搜索成功！找到 {product_result.total_rows} 条数据")
            print(f"\n成品料号:")
            for row in product_result.data:
                print(f"  {row[0]}")

            if product_result.files:
                print(f"\n产品文件已保存:")
                for key, path in product_result.files.items():
                    print(f"  {key}: {path}")

        if bom_result and bom_result.success:
            print(f"\nBOM 查询成功！找到 {bom_result.total_rows} 条数据")

            if bom_result.files:
                print(f"\nBOM 文件已保存:")
                for key, path in bom_result.files.items():
                    print(f"  {key}: {path}")

        if not product_result.success:
            print(f"\n产品搜索失败: {product_result.error}")
            return 1

        return 0

    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        service.disconnect()


def main() -> int:
    """主入口"""
    parser = argparse.ArgumentParser(description="PLM BOM Getter")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 搜索成品料号
    parser_search = subparsers.add_parser("search", help="按客户型号搜索成品料号")
    parser_search.add_argument("customer_model", help="客户型号 (如 N3D, NC20)")

    # 查询 BOM
    parser_bom = subparsers.add_parser("bom", help="按成品料号查询 BOM")
    parser_bom.add_argument("material", help="成品料号 (如 30008018)")

    # 完整搜索
    parser_full = subparsers.add_parser("full", help="搜索产品并查询 BOM")
    parser_full.add_argument("customer_model", help="客户型号")

    args = parser.parse_args()

    if args.command == "search":
        return cmd_search_products(args)
    elif args.command == "bom":
        return cmd_search_bom(args)
    elif args.command == "full":
        return cmd_full_search(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
