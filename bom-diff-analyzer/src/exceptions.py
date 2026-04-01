"""
异常定义模块

定义 BOM 差异分析过程中的各类异常
"""


class BomDiffAnalyzerError(Exception):
    """BOM 差异分析基础异常"""
    pass


class FileReadError(BomDiffAnalyzerError):
    """文件读取异常"""
    pass


class FileWriteError(BomDiffAnalyzerError):
    """文件写入异常"""
    pass


class InvalidInputError(BomDiffAnalyzerError):
    """输入参数无效异常"""
    pass


class BomParseError(BomDiffAnalyzerError):
    """BOM 解析异常"""
    pass


class ProductParseError(BomDiffAnalyzerError):
    """产品描述解析异常"""
    pass
