"""
配置模块
"""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """PLM BOM Getter 配置"""
    # Chrome 远程调试端口
    chrome_debug_port: int = 9222

    # ChromeDriver 路径
    chromedriver_path: str = "C:/Users/keith liao/.cache/selenium/chromedriver/win64/146.0.7680.165/chromedriver.exe"

    # PLM 系统 URL
    plm_base_url: str = "http://oa.netcoretec.com/wui/index.html"

    # 成品料号查询页面 customid
    product_search_customid: int = 78

    # BOM 查询页面 customid
    bom_search_customid: int = 80

    # 菜单路径
    menu_ids: str = "-92,-103"
    menu_path_ids: str = "-92,-128,-103"

    # 输出目录
    output_dir: Path = None

    # 页面加载等待时间（秒）
    page_load_wait: float = 8.0

    # 搜索等待时间（秒）
    search_wait: float = 10.0

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = Path("C:/Users/keith liao/.openclaw/plm-exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_product_search_url(self) -> str:
        """获取成品料号搜索URL"""
        return (
            f"{self.plm_base_url}#/main/cube/search"
            f"?customid={self.product_search_customid}"
            f"&menuIds={self.menu_ids}"
            f"&menuPathIds={self.menu_path_ids}"
        )

    def get_bom_search_url(self) -> str:
        """获取BOM搜索URL"""
        return (
            f"{self.plm_base_url}#/main/cube/search"
            f"?customid={self.bom_search_customid}"
            f"&menuIds={self.menu_ids}"
            f"&menuPathIds={self.menu_path_ids}"
        )


# 默认配置实例
default_config = Config()
