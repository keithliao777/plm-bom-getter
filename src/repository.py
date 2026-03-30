"""
数据访问层 - Selenium 操作
"""

import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from src.config import Config
from src.exceptions import (
    ChromeConnectionError,
    ElementNotFoundError,
    DataExtractionError,
)


class PLMRepository:
    """PLM 数据访问层"""

    CUSTOMER_MODEL_COLUMN = 5  # 客标型号列索引

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.driver: Optional[webdriver.Chrome] = None

    def connect(self) -> None:
        """连接到 Chrome 浏览器"""
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.config.chrome_debug_port}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        try:
            service = Service(executable_path=self.config.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            raise ChromeConnectionError(f"无法连接到 Chrome: {e}")

    def disconnect(self) -> None:
        """断开 Chrome 连接"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.driver is not None

    def _extract_table_data(self) -> tuple[list[str], list[list[str]]]:
        """
        从页面提取表格数据

        Returns:
            tuple: (header, data)
        """
        if not self.driver:
            raise ChromeConnectionError("未连接到 Chrome")

        try:
            # 提取表头
            header = self.driver.execute_script("""
                var headers = document.querySelectorAll('.ant-table-thead th');
                var headerData = [];
                headers.forEach(function(th) {
                    headerData.push(th.innerText.trim());
                });
                return headerData;
            """)

            # 提取数据行
            data = self.driver.execute_script("""
                var results = [];
                var rows = document.querySelectorAll('.ant-table-tbody tr');
                rows.forEach(function(row) {
                    var cells = row.querySelectorAll('td');
                    var rowData = [];
                    cells.forEach(function(cell) {
                        rowData.push(cell.innerText.trim());
                    });
                    if (rowData.some(c => c.length > 0)) {
                        results.push(rowData);
                    }
                });
                return results;
            """)

            return header, data

        except Exception as e:
            raise DataExtractionError(f"提取表格数据失败: {e}")

    def _click_customer_model_input(self) -> None:
        """点击客标型号输入框"""
        if not self.driver:
            raise ChromeConnectionError("未连接到 Chrome")

        self.driver.execute_script("""
            var labels = document.querySelectorAll('.cube-quicksearch-label');
            if (labels.length >= 6) {
                var label = labels[5];
                var container = label.closest('div[style*=inline-block]');
                if (container) {
                    var antSelect = container.querySelector('.ant-select');
                    if (antSelect) antSelect.click();
                }
            }
        """)
        time.sleep(1.5)

    def _clear_input(self) -> None:
        """清空输入框"""
        if not self.driver:
            raise ChromeConnectionError("未连接到 Chrome")

        self.driver.execute_script("""
            var clearBtns = document.querySelectorAll(
                '.ant-select-selection__clear, .anticon-close, [class*=clear]'
            );
            clearBtns.forEach(function(btn) {
                if (btn.offsetParent !== null) btn.click();
            });
            var selectedItems = document.querySelectorAll('.ant-select-selection__choice');
            selectedItems.forEach(function(item) {
                var removeBtn = item.querySelector('.ant-select-selection__choice__remove');
                if (removeBtn) removeBtn.click();
            });
        """)
        time.sleep(0.5)

    def _input_text(self, text: str) -> None:
        """输入文本到搜索框"""
        if not self.driver:
            raise ChromeConnectionError("未连接到 Chrome")

        search_input = self.driver.find_element(By.CSS_SELECTOR, ".ant-select-search__field")
        search_input.click()
        time.sleep(0.3)
        search_input.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.2)
        search_input.send_keys(Keys.DELETE)
        time.sleep(0.5)
        search_input.send_keys(text)

    def search_by_customer_model(self, customer_model: str, wait_time: int = 10) -> tuple[list[str], list[list[str]]]:
        """
        按客户型号搜索成品料号

        Args:
            customer_model: 客户型号
            wait_time: 等待时间（秒）

        Returns:
            tuple: (header, data)
        """
        if not self.driver:
            raise ChromeConnectionError("未连接到 Chrome")

        # 导航到搜索页面
        url = self.config.get_product_search_url()
        self.driver.get(url)
        time.sleep(self.config.page_load_wait)
        self.driver.switch_to.default_content()

        # 点击客标型号输入框
        self._click_customer_model_input()

        # 清空输入框
        self._clear_input()

        # 输入客户型号
        self._input_text(customer_model)

        # 等待3秒
        time.sleep(3)

        # 按回车
        search_input = self.driver.find_element(By.CSS_SELECTOR, ".ant-select-search__field")
        search_input.send_keys(Keys.RETURN)

        # 等待搜索结果
        for _ in range(wait_time):
            time.sleep(1)

        # 提取数据
        return self._extract_table_data()

    def search_bom_by_material(self, material_number: str, wait_time: int = 10) -> tuple[list[str], list[list[str]]]:
        """
        按成品料号查询BOM

        Args:
            material_number: 成品料号
            wait_time: 等待时间（秒）

        Returns:
            tuple: (header, data)
        """
        if not self.driver:
            raise ChromeConnectionError("未连接到 Chrome")

        # 导航到BOM查询页面
        url = self.config.get_bom_search_url()
        self.driver.get(url)
        time.sleep(self.config.page_load_wait)
        self.driver.switch_to.default_content()

        # 选择"多层"选项 (index 0)
        # 注意：页面可能已经记住了上次的选择状态
        self.driver.execute_script("""
            var radios = document.querySelectorAll('.ant-radio-wrapper');
            if (radios.length > 0 && !radios[0].classList.contains('ant-radio-wrapper-checked')) {
                radios[0].click();
            }
        """)
        time.sleep(1)

        # 点击父阶料号输入框
        self.driver.execute_script("""
            var assoc = document.querySelector('.wea-associative-search .ant-select');
            if (assoc) assoc.click();
        """)
        time.sleep(2)

        # 输入物料号
        self._input_text(material_number)

        # 等待3秒
        time.sleep(3)

        # 按回车
        search_input = self.driver.find_element(By.CSS_SELECTOR, ".ant-select-search__field")
        search_input.send_keys(Keys.RETURN)

        # 等待搜索结果
        for _ in range(wait_time):
            time.sleep(1)

        # 提取数据
        return self._extract_table_data()
