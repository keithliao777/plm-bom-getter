"""
测试 src.services
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services import PLMBomService
from src.config import Config
from src.models import ProductSearchResult, BomSearchResult
from src.exceptions import ChromeConnectionError


class TestPLMBomService:
    """测试 PLMBomService"""

    def test_service_init(self):
        """测试服务初始化"""
        service = PLMBomService()
        assert service.config is not None
        assert service.repository is not None

    def test_service_with_custom_config(self, tmp_path):
        """测试使用自定义配置"""
        config = Config(output_dir=tmp_path)
        service = PLMBomService(config)
        assert service.config.output_dir == tmp_path

    def test_verify_customer_model_exact_match(self):
        """测试客标型号精确匹配"""
        service = PLMBomService()
        data = [
            ["30001234", "产品1", "", "", "", "N3D"],
            ["30001235", "产品2", "", "", "", "NC20"],
            ["30001236", "产品3", "", "", "", "N3D PRO"],
        ]
        result = service._verify_customer_model(data, "N3D")
        assert len(result) == 2
        assert result[0][0] == "30001234"
        assert result[1][0] == "30001236"

    def test_verify_customer_model_case_insensitive(self):
        """测试客标型号大小写不敏感"""
        service = PLMBomService()
        data = [
            ["30001234", "产品1", "", "", "", "n3d"],
            ["30001235", "产品2", "", "", "", "NC20"],
        ]
        result = service._verify_customer_model(data, "N3D")
        assert len(result) == 1

    def test_verify_customer_model_partial_match(self):
        """测试客标型号部分匹配"""
        service = PLMBomService()
        data = [
            ["30001234", "产品1", "", "", "", "N3D"],
            ["30001235", "产品2", "", "", "", "N3D-X"],
            ["30001236", "产品3", "", "", "", "NX30"],
        ]
        result = service._verify_customer_model(data, "N3D")
        assert len(result) == 2

    def test_verify_customer_model_no_match(self):
        """测试客标型号无匹配"""
        service = PLMBomService()
        data = [
            ["30001234", "产品1", "", "", "", "N3D"],
            ["30001235", "产品2", "", "", "", "NC20"],
        ]
        result = service._verify_customer_model(data, "XYZ")
        assert len(result) == 0

    def test_verify_customer_model_empty_data(self):
        """测试空数据"""
        service = PLMBomService()
        result = service._verify_customer_model([], "N3D")
        assert len(result) == 0

    @patch('src.services.PLMRepository')
    def test_search_products_success(self, mock_repo_class):
        """测试搜索成品料号成功"""
        mock_repo = Mock()
        mock_repo.search_by_customer_model.return_value = (
            ["物料号", "描述", "", "", "", "客标型号"],
            [
                ["30001234", "产品1", "", "", "", "N3D"],
                ["30001235", "产品2", "", "", "", "N3D"],
            ]
        )
        mock_repo.CUSTOMER_MODEL_COLUMN = 5

        service = PLMBomService()
        service.repository = mock_repo

        result = service.search_products("N3D")

        assert result.success is True
        assert result.customer_model == "N3D"
        assert result.total_rows == 2

    @patch('src.services.PLMRepository')
    def test_search_products_connection_error(self, mock_repo_class):
        """测试搜索成品料号连接错误"""
        mock_repo = Mock()
        mock_repo.search_by_customer_model.side_effect = ChromeConnectionError("Not connected")

        service = PLMBomService()
        service.repository = mock_repo

        result = service.search_products("N3D")

        assert result.success is False
        assert result.error is not None

    @patch('src.services.PLMRepository')
    def test_search_bom_success(self, mock_repo):
        """测试查询BOM成功"""
        mock_repo.search_bom_by_material.return_value = (
            ["层级", "父阶料号", "顺序号", "子阶料号", "物料分类", "物料描述", "用量"],
            [
                ["1", "30008018", "0002", "10028838", "电线电缆", "电源线", "1"],
                ["1", "30008018", "0004", "10023859", "线材", "网线", "1"],
            ]
        )

        service = PLMBomService()
        service.repository = mock_repo

        result = service.search_bom("30008018")

        assert result.success is True
        assert result.material_number == "30008018"
        assert result.total_rows == 2

    @patch('src.services.PLMRepository')
    def test_search_bom_empty_result(self, mock_repo):
        """测试查询BOM无数据"""
        mock_repo.search_bom_by_material.return_value = ([], [])

        service = PLMBomService()
        service.repository = mock_repo

        result = service.search_bom("30009999")

        assert result.success is True
        assert result.total_rows == 0
