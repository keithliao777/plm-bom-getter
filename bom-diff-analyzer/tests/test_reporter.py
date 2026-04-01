"""
reporter 模块单元测试
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.reporter import (
    calculate_statistics,
    generate_excel_report,
    get_abnormal_items,
    generate_message,
)
from src.models import DiffItem, Statistics


class TestCalculateStatistics:
    """测试统计计算"""

    def test_calculate_with_mixed_items(self):
        """测试混合差异项的统计"""
        items = [
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30002', other_desc='desc2',
                     diff_type='增加', mat_code='10001', mat_desc='mat1',
                     diff_reason='reason1', diff_judgment='正常'),
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30002', other_desc='desc2',
                     diff_type='减少', mat_code='10002', mat_desc='mat2',
                     diff_reason='reason2', diff_judgment='异常'),
            DiffItem(layer=2, std_pn='30001', std_desc='desc1',
                     other_pn='30003', other_desc='desc3',
                     diff_type='增加', mat_code='10003', mat_desc='mat3',
                     diff_reason='reason3', diff_judgment='需确认'),
            DiffItem(layer=2, std_pn='30001', std_desc='desc1',
                     other_pn='30003', other_desc='desc3',
                     diff_type='增加', mat_code='10004', mat_desc='mat4',
                     diff_reason='reason4', diff_judgment='正常'),
        ]

        stats = calculate_statistics(items)

        assert stats.total_differences == 4
        assert stats.normal_count == 2
        assert stats.abnormal_count == 1
        assert stats.review_count == 1

    def test_calculate_empty(self):
        """测试空列表"""
        stats = calculate_statistics([])
        assert stats.total_differences == 0
        assert stats.normal_count == 0


class TestGetAbnormalItems:
    """测试异常差异获取"""

    def test_get_abnormal_with_limit(self):
        """测试获取异常差异（带限制）"""
        items = [
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30002', other_desc='desc2',
                     diff_type='增加', mat_code='10001', mat_desc='mat1',
                     diff_reason='reason1', diff_judgment='异常'),
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30003', other_desc='desc3',
                     diff_type='增加', mat_code='10002', mat_desc='mat2',
                     diff_reason='reason2', diff_judgment='异常'),
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30004', other_desc='desc4',
                     diff_type='增加', mat_code='10003', mat_desc='mat3',
                     diff_reason='reason3', diff_judgment='异常'),
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30005', other_desc='desc5',
                     diff_type='增加', mat_code='10004', mat_desc='mat4',
                     diff_reason='reason4', diff_judgment='正常'),
        ]

        result = get_abnormal_items(items, limit=2)
        assert len(result) == 2


class TestGenerateExcelReport:
    """测试 Excel 报告生成"""

    def test_generate_report(self):
        """测试报告生成"""
        items = [
            DiffItem(layer=1, std_pn='30001', std_desc='desc1',
                     other_pn='30002', other_desc='desc2',
                     diff_type='增加', mat_code='10001', mat_desc='mat1',
                     diff_reason='reason1', diff_judgment='正常'),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = generate_excel_report(
                items,
                tmpdir,
                'test_report.xlsx'
            )

            assert Path(output_file).exists()
            assert 'test_report.xlsx' in output_file


class TestGenerateMessage:
    """测试消息生成"""

    def test_message_with_abnormal(self):
        """有异常时的消息"""
        stats = Statistics(
            total_differences=10,
            normal_count=5,
            abnormal_count=3,
            review_count=2
        )
        msg = generate_message(stats)
        assert '异常差异' in msg
        assert '3' in msg

    def test_message_with_review_only(self):
        """只有需确认时的消息"""
        stats = Statistics(
            total_differences=5,
            normal_count=0,
            abnormal_count=0,
            review_count=5
        )
        msg = generate_message(stats)
        assert '需确认差异' in msg

    def test_message_all_normal(self):
        """全部正常时的消息"""
        stats = Statistics(
            total_differences=10,
            normal_count=10,
            abnormal_count=0,
            review_count=0
        )
        msg = generate_message(stats)
        assert '正常差异' in msg
