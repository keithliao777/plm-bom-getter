"""
自定义异常
"""


class PLMBomError(Exception):
    """PLM BOM 获取基础异常"""
    pass


class ChromeConnectionError(PLMBomError):
    """Chrome 连接异常"""
    pass


class PageLoadError(PLMBomError):
    """页面加载异常"""
    pass


class ElementNotFoundError(PLMBomError):
    """元素未找到异常"""
    pass


class SearchTimeoutError(PLMBomError):
    """搜索超时异常"""
    pass


class DataExtractionError(PLMBomError):
    """数据提取异常"""
    pass
