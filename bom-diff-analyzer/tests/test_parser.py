"""
parser 模块单元测试
"""

import pytest
from src.parser import parse_product_desc, get_layer_materials
from src.models import ProductInfo
from src.config import Config


class TestParseProductDesc:
    """测试产品描述解析"""

    def test_parse_netis_ax1800(self):
        """测试解析 netis AX1800 产品描述"""
        desc = (
            '家用无线路由器，NX30，netis，EU，越南，V4.0，APP版，'
            'MT7981B+MT7976C+MT7531AE，7583，S242，AX1800，'
            '1GE_WAN+3GE_LAN+5*5dBi天线，12V/1.5A，DC2.1*5.5*11.5mm'
        )
        result = parse_product_desc(desc)

        assert result.brand == 'netis'
        assert result.region == 'EU'
        assert result.chipset == 'MT7981B+MT7976C+MT7531AE'
        assert result.spec == 'AX1800'
        assert result.power == '12V/1.5A'

    def test_parse_stonet_ax3000(self):
        """测试解析 stonet AX3000 产品描述"""
        desc = (
            '家用无线路由器，NX30，stonet，EU，V2，V4.0，APP版，'
            'MT7981B+MT7976C+MT7531AE，7583，S242，AX3000，'
            '1GE_WAN+3GE_LAN+5*5dBi天线，12V/1A，DC2.1*5.5*9.5mm'
        )
        result = parse_product_desc(desc)

        assert result.brand == 'stonet'
        assert result.region == 'EU'
        assert result.chipset == 'MT7981B+MT7976C+MT7531AE'
        assert result.spec == 'AX3000'
        assert result.power == '12V/1A'

    def test_parse_mova_linc0(self):
        """测试解析 MOVA LINC0 产品描述"""
        desc = (
            '家用无线路由器，NX30，追觅MOVA LINC0，EU，V2，V4.0，APP版，'
            'MT7981B+MT7976C+MT7531AE，7583，S242，AX3000，'
            '1GE_WAN+3GE_LAN+5*5dBi天线，12V/1A，DC2.1*5.5*9.5mm'
        )
        result = parse_product_desc(desc)

        assert result.brand == 'MOVA LINC0'
        assert result.region == 'EU'
        assert result.chipset == 'MT7981B+MT7976C+MT7531AE'
        assert result.spec == 'AX3000'
        assert result.power == '12V/1A'

    def test_parse_us_region(self):
        """测试解析 US 地区"""
        desc = '家用无线路由器，NX30，netis，US，美洲'
        result = parse_product_desc(desc)

        assert result.region == 'US'

    def test_parse_empty_desc(self):
        """测试解析空描述"""
        result = parse_product_desc('')
        assert result.brand == ''
        assert result.region == ''

    def test_parse_none_desc(self):
        """测试解析 None"""
        result = parse_product_desc(None)
        assert result.brand == ''
        assert result.region == ''


class TestGetLayerMaterials:
    """测试 BOM 层级物料提取"""

    @pytest.fixture
    def sample_bom_df(self):
        """创建示例 BOM DataFrame"""
        import pandas as pd
        data = [
            [1, '30008065', '0010', '10023859', '网线', '外置网线...'],
            [1, '30008065', '0020', '10022645', '网线', '外置网线...'],
            [2, '30008065', '0010', '50000422', '包装纸板', '包装纸板...'],
            [5, '30008065', '0010', '20018631', '贴片电容', '10uF...'],
            [5, '30008065', '0020', '20018632', '贴片电阻', '10K...'],
        ]
        return pd.DataFrame(data)

    def test_get_layer_1_materials(self, sample_bom_df):
        """测试提取层级 1 的物料"""
        config = Config()
        result = get_layer_materials(sample_bom_df, 1, config)

        assert len(result) == 2
        assert '10023859' in result
        assert '10022645' in result

    def test_get_layer_5_materials(self, sample_bom_df):
        """测试提取层级 5 的物料"""
        config = Config()
        result = get_layer_materials(sample_bom_df, 5, config)

        assert len(result) == 2
        assert '20018631' in result
        assert '20018632' in result

    def test_get_nonexistent_layer(self, sample_bom_df):
        """测试提取不存在的层级"""
        config = Config()
        result = get_layer_materials(sample_bom_df, 3, config)

        assert len(result) == 0
