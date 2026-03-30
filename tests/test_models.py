"""
测试 src.models
"""

import pytest
from src.models import (
    SearchResult,
    ProductSearchResult,
    BomSearchResult,
    ProductInfo,
    BomItem,
)


class TestSearchResult:
    """测试 SearchResult 基类"""

    def test_search_result_success(self):
        result = SearchResult(success=True, total_rows=10)
        assert result.success is True
        assert result.total_rows == 10
        assert result.error is None

    def test_search_result_failure(self):
        result = SearchResult(success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"


class TestProductSearchResult:
    """测试 ProductSearchResult"""

    def test_product_search_result(self):
        result = ProductSearchResult(
            success=True,
            customer_model="N3D",
            total_rows=2,
            header=["物料号", "描述"],
            data=[["30001234", "产品1"], ["30001235", "产品2"]],
        )
        assert result.success is True
        assert result.customer_model == "N3D"
        assert result.total_rows == 2
        assert len(result.data) == 2
        assert result.files == {}

    def test_product_search_result_files(self):
        result = ProductSearchResult(
            success=True,
            customer_model="NC20",
            total_rows=1,
            files={"products": "/path/to/file.xlsx"},
        )
        assert result.files["products"] == "/path/to/file.xlsx"


class TestBomSearchResult:
    """测试 BomSearchResult"""

    def test_bom_search_result(self):
        result = BomSearchResult(
            success=True,
            material_number="30008018",
            total_rows=155,
        )
        assert result.success is True
        assert result.material_number == "30008018"
        assert result.total_rows == 155

    def test_bom_search_result_empty(self):
        result = BomSearchResult(success=True, material_number="30009999", total_rows=0)
        assert result.total_rows == 0


class TestProductInfo:
    """测试 ProductInfo"""

    def test_product_info(self):
        product = ProductInfo(
            material_number="30001234",
            description="测试产品",
            customer_model="N3D",
        )
        assert product.material_number == "30001234"
        assert product.description == "测试产品"
        assert product.customer_model == "N3D"


class TestBomItem:
    """测试 BomItem"""

    def test_bom_item(self):
        item = BomItem(
            level="1",
            parent_part_number="30008018",
            sequence="0002",
            child_part_number="10028838",
            material_category="电线电缆",
            material_description="电源线",
            quantity="1",
        )
        assert item.level == "1"
        assert item.quantity == "1"
        assert item.preferred_level == ""
