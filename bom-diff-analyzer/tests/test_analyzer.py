"""
analyzer 模块单元测试
"""

import pytest
import pandas as pd
from src.analyzer import compare_layer, is_diff_reasonable, _analyze_diff_reason
from src.models import ProductInfo
from src.config import Config


class TestCompareLayer:
    """测试 BOM 层级比较"""

    @pytest.fixture
    def std_df(self):
        """标准 BOM"""
        data = [
            [1, '30008065', '0010', '10023859', '网线', '外置网线...'],
            [1, '30008065', '0020', '10022645', '网线', '外置网线...'],
            [5, '30008065', '0010', '20018631', '贴片电容', '10uF...'],
        ]
        return pd.DataFrame(data)

    @pytest.fixture
    def other_df(self):
        """比较 BOM"""
        data = [
            [1, '30008066', '0010', '10023859', '网线', '外置网线...'],  # 相同
            [1, '30008066', '0020', '10022646', '网线', '另一网线...'],  # 不同
            [5, '30008066', '0010', '20018631', '贴片电容', '10uF...'],  # 相同
            [5, '30008066', '0020', '20018632', '贴片电阻', '10K...'],   # 新增
        ]
        return pd.DataFrame(data)

    def test_compare_increased_material(self, std_df, other_df):
        """测试检测增加的物料"""
        config = Config()
        result = compare_layer(std_df, other_df, 5, config)

        # 应该有 1 个增加（20018632）
        increased = [d for d in result if d['diff_type'] == '增加']
        assert len(increased) == 1
        assert increased[0]['mat_code'] == '20018632'

    def test_compare_decreased_material(self, std_df, other_df):
        """测试检测减少的物料"""
        config = Config()
        result = compare_layer(std_df, other_df, 1, config)

        # 层级 1 减少: 10022645（其他 BOM 中是 10022646）
        decreased = [d for d in result if d['diff_type'] == '减少']
        assert len(decreased) == 1
        assert decreased[0]['mat_code'] == '10022645'


class TestIsDiffReasonable:
    """测试差异合理性判断"""

    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def same_desc_parsed(self):
        """相同产品描述"""
        desc = '家用无线路由器，NX30，netis，EU，MT7981B+MT7976C+MT7531AE，AX1800'
        info = parse_product_desc(desc)
        return {'30006913': info, '30006914': info}

    @pytest.fixture
    def diff_brand_parsed(self):
        """不同品牌"""
        desc1 = '家用无线路由器，NX30，netis，EU，MT7981B+MT7976C+MT7531AE，AX1800'
        desc2 = '家用无线路由器，NX30，stonet，EU，MT7981B+MT7976C+MT7531AE，AX1800'
        return {
            '30006913': parse_product_desc(desc1),
            '30006914': parse_product_desc(desc2)
        }

    @pytest.fixture
    def sample_df(self):
        """示例 BOM DataFrame"""
        data = [
            [1, '30006913', '0010', '10023859', '网线', '彩盒...'],
            [5, '30006913', '0010', '20018631', '贴片', 'SMT...'],
        ]
        return pd.DataFrame(data)

    def test_same_desc_should_be_abnormal(self, same_desc_parsed, sample_df, config):
        """产品描述完全相同但 BOM 有差异应为异常"""
        result, note = is_diff_reasonable(
            layer=5,
            mat_code='20018631',
            diff_type='增加',
            diff_reason='物料增加',
            std_pn='30006913',
            other_pn='30006914',
            parsed_descs=same_desc_parsed,
            mat_desc='贴片物料',
            config=config
        )
        assert result == '异常'

    def test_diff_brand_with_box_normal(self, diff_brand_parsed, sample_df, config):
        """品牌不同 + 彩盒差异应为正常"""
        result, note = is_diff_reasonable(
            layer=1,
            mat_code='10023859',
            diff_type='增加',
            diff_reason='包装物料增加',
            std_pn='30006913',
            other_pn='30006914',
            parsed_descs=diff_brand_parsed,
            mat_desc='彩盒包装材料',
            config=config
        )
        assert result == '正常'
        assert '包装' in note

    def test_diff_brand_with_pcba_normal(self, diff_brand_parsed, sample_df, config):
        """品牌不同 + PCBA 差异应为正常"""
        result, note = is_diff_reasonable(
            layer=5,
            mat_code='20018631',
            diff_type='增加',
            diff_reason='PCBA 物料增加',
            std_pn='30006913',
            other_pn='30006914',
            parsed_descs=diff_brand_parsed,
            mat_desc='SMT 贴片物料',
            config=config
        )
        assert result == '正常'


def parse_product_desc(desc: str) -> ProductInfo:
    """辅助函数：解析产品描述"""
    from src.parser import parse_product_desc as parser_func
    return parser_func(desc)


class TestAnalyzeDiffReason:
    """测试差异原因分析"""

    def test_box_reason(self):
        """彩盒类差异"""
        result = _analyze_diff_reason(1, '10000001', '增加', '彩盒包装')
        assert '包装' in result

    def test_pcba_reason(self):
        """PCBA 类差异"""
        result = _analyze_diff_reason(5, '20000001', '增加', 'SMT 贴片物料')
        assert 'PCBA' in result

    def test_power_reason(self):
        """电源类差异"""
        result = _analyze_diff_reason(2, '30000001', '增加', '电源适配器 12V')
        assert '电源' in result
