"""
业务逻辑层
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from src.config import Config
from src.models import ProductSearchResult, BomSearchResult
from src.repository import PLMRepository
from src.exceptions import PLMBomError


class PLMBomService:
    """PLM BOM 服务层"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.repository = PLMRepository(self.config)

    def connect(self) -> None:
        """连接到 PLM 系统"""
        self.repository.connect()

    def disconnect(self) -> None:
        """断开连接"""
        self.repository.disconnect()

    def _verify_customer_model(self, data: list[list[str]], customer_model: str) -> list[list[str]]:
        """
        验证数据中的客标型号是否匹配

        Args:
            data: 原始数据
            customer_model: 目标客户型号

        Returns:
            匹配的数据
        """
        verified = []
        for row in data:
            if len(row) > self.repository.CUSTOMER_MODEL_COLUMN:
                model = row[self.repository.CUSTOMER_MODEL_COLUMN].strip()
                if customer_model.upper() in model.upper():
                    verified.append(row)
        return verified

    def _save_to_excel(self, data: list, filepath: Path) -> None:
        """保存数据到 Excel"""
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, engine='openpyxl')

    def _save_part_numbers(self, part_numbers: list[str], customer_model: str, timestamp: str) -> str:
        """
        保存成品料号列表到文本文件

        Returns:
            文件路径
        """
        filepath = self.config.output_dir / f"{customer_model}_part_numbers_{timestamp}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {customer_model} 成品料号列表\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 共 {len(part_numbers)} 个料号\n")
            f.write("\n")
            for pn in part_numbers:
                f.write(f"{pn}\n")
        return str(filepath)

    def search_products(self, customer_model: str) -> ProductSearchResult:
        """
        按客户型号搜索成品料号

        Args:
            customer_model: 客户型号

        Returns:
            ProductSearchResult
        """
        try:
            header, data = self.repository.search_by_customer_model(customer_model)

            # 验证客标型号
            verified_data = self._verify_customer_model(data, customer_model)

            result = ProductSearchResult(
                success=True,
                customer_model=customer_model,
                total_rows=len(verified_data),
                header=header,
                data=verified_data,
            )

            # 保存文件
            if verified_data:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                # 保存完整数据到 Excel
                all_data = [header] + verified_data
                excel_path = self.config.output_dir / f"{customer_model}_products_{timestamp}.xlsx"
                self._save_to_excel(all_data, excel_path)
                result.files['products'] = str(excel_path)

                # 保存料号列表
                part_numbers = [row[0] for row in verified_data]
                txt_path = self._save_part_numbers(part_numbers, customer_model, timestamp)
                result.files['part_numbers'] = txt_path

            return result

        except PLMBomError as e:
            return ProductSearchResult(success=False, error=str(e))
        except Exception as e:
            return ProductSearchResult(success=False, error=f"搜索失败: {e}")

    def search_bom(self, material_number: str) -> BomSearchResult:
        """
        按成品料号查询BOM

        Args:
            material_number: 成品料号

        Returns:
            BomSearchResult
        """
        try:
            header, data = self.repository.search_bom_by_material(material_number)

            result = BomSearchResult(
                success=True,
                material_number=material_number,
                total_rows=len(data),
                header=header,
                data=data,
            )

            # 保存文件
            if data:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = self.config.output_dir / f"{material_number}_BOM_{timestamp}.xlsx"
                all_data = [header] + data
                self._save_to_excel(all_data, filepath)
                result.files['bom'] = str(filepath)

            return result

        except PLMBomError as e:
            return BomSearchResult(success=False, error=str(e))
        except Exception as e:
            return BomSearchResult(success=False, error=f"BOM查询失败: {e}")

    def search_products_and_bom(self, customer_model: str) -> tuple[ProductSearchResult, Optional[BomSearchResult]]:
        """
        按客户型号搜索并查询其BOM（仅第一个料号）

        Args:
            customer_model: 客户型号

        Returns:
            tuple: (产品搜索结果, BOM搜索结果)
        """
        # 搜索产品
        product_result = self.search_products(customer_model)
        if not product_result.success or product_result.total_rows == 0:
            return product_result, None

        # 获取第一个料号查询BOM
        first_material = product_result.data[0][0]
        bom_result = self.search_bom(first_material)

        return product_result, bom_result

    def search_all_boms(self, customer_model: str) -> dict:
        """
        按客户型号搜索并获取所有成品料号的BOM

        Args:
            customer_model: 客户型号

        Returns:
            dict: 包含产品搜索结果和所有BOM数据
        """
        # 搜索产品
        product_result = self.search_products(customer_model)
        if not product_result.success or product_result.total_rows == 0:
            return {
                'success': True,
                'customer_model': customer_model,
                'total_products': 0,
                'products': [],
                'boms': [],
                'total_bom_rows': 0,
                'files': product_result.files
            }

        # 获取所有成品料号
        part_numbers = [row[0] for row in product_result.data]

        # 查询所有BOM
        boms = []
        total_bom_rows = 0
        bom_files = {}

        for pn in part_numbers:
            try:
                bom_result = self.search_bom(pn)
                if bom_result.success:
                    boms.append({
                        'material_number': bom_result.material_number,
                        'total_rows': bom_result.total_rows,
                        'header': bom_result.header,
                        'data': bom_result.data
                    })
                    total_bom_rows += bom_result.total_rows
                    if bom_result.files:
                        bom_files.update(bom_result.files)
            except Exception as e:
                # 单个BOM查询失败不影响整体
                print(f"警告: BOM查询失败 {pn}: {e}")

        return {
            'success': True,
            'customer_model': customer_model,
            'total_products': len(part_numbers),
            'part_numbers': part_numbers,
            'products': product_result.data,
            'product_header': product_result.header,
            'boms': boms,
            'total_bom_rows': total_bom_rows,
            'files': {
                **product_result.files,
                **bom_files
            }
        }
