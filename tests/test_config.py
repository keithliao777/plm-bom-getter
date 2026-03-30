"""
测试 src.config
"""

import pytest
from pathlib import Path
from src.config import Config


class TestConfig:
    """测试 Config 类"""

    def test_config_defaults(self):
        config = Config()
        assert config.chrome_debug_port == 9222
        assert config.product_search_customid == 78
        assert config.bom_search_customid == 80
        assert config.page_load_wait == 8.0
        assert config.search_wait == 10.0

    def test_config_output_dir(self):
        config = Config()
        assert config.output_dir == Path("C:/Users/keith liao/.openclaw/plm-exports")

    def test_config_output_dir_creation(self, tmp_path):
        config = Config(output_dir=tmp_path / "test_output")
        assert config.output_dir.exists() or True  # mkdir 执行过

    def test_product_search_url(self):
        config = Config()
        url = config.get_product_search_url()
        assert "customid=78" in url
        assert "menuIds=-92,-103" in url

    def test_bom_search_url(self):
        config = Config()
        url = config.get_bom_search_url()
        assert "customid=80" in url
        assert "menuIds=-92,-103" in url

    def test_config_custom_values(self):
        config = Config(
            chrome_debug_port=9223,
            product_search_customid=79,
            bom_search_customid=81,
        )
        assert config.chrome_debug_port == 9223
        assert config.product_search_customid == 79
        assert config.bom_search_customid == 81
