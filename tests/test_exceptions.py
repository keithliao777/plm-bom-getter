"""
测试 src.exceptions
"""

import pytest
from src.exceptions import (
    PLMBomError,
    ChromeConnectionError,
    PageLoadError,
    ElementNotFoundError,
    SearchTimeoutError,
    DataExtractionError,
)


class TestExceptions:
    """测试异常类"""

    def test_plm_bom_error(self):
        with pytest.raises(PLMBomError):
            raise PLMBomError("Base error")

    def test_chrome_connection_error(self):
        with pytest.raises(ChromeConnectionError):
            raise ChromeConnectionError("Cannot connect")

    def test_page_load_error(self):
        with pytest.raises(PageLoadError):
            raise PageLoadError("Page timeout")

    def test_element_not_found_error(self):
        with pytest.raises(ElementNotFoundError):
            raise ElementNotFoundError("Element not found")

    def test_search_timeout_error(self):
        with pytest.raises(SearchTimeoutError):
            raise SearchTimeoutError("Search timeout")

    def test_data_extraction_error(self):
        with pytest.raises(DataExtractionError):
            raise DataExtractionError("Data extraction failed")

    def test_exception_inheritance(self):
        """验证异常继承关系"""
        assert issubclass(ChromeConnectionError, PLMBomError)
        assert issubclass(PageLoadError, PLMBomError)
        assert issubclass(ElementNotFoundError, PLMBomError)
        assert issubclass(SearchTimeoutError, PLMBomError)
        assert issubclass(DataExtractionError, PLMBomError)
