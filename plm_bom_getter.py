#!/usr/bin/env python3
"""
PLM BOM Getter - 通过 Selenium 获取 PLM 系统 BOM 数据
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd


class PLMBOMGetter:
    """PLM BOM 获取器"""

    def __init__(self, port=9222):
        self.port = port
        self.driver = None
        self.output_dir = Path("C:/Users/keith liao/.openclaw/plm-exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def connect_to_chrome(self):
        """连接到已运行的 Chrome 浏览器"""
        options = Options()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.port}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        # 显式指定 ChromeDriver 路径
        chromedriver_path = "C:/Users/keith liao/.cache/selenium/chromedriver/win64/146.0.7680.165/chromedriver.exe"
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        print(f"已连接到 Chrome 浏览器 (端口 {self.port})")

    def search_by_customer_model(self, customer_model, wait_time=10):
        """
        通过客户型号搜索成品料号
        参数：customer_model - 客户型号（如 N3D, WF2409E 等）
        """
        print("=" * 80)
        print(f"PLM BOM Getter - 搜索客户型号：{customer_model}")
        print("=" * 80)

        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.by import By

            # 导航到成品料号查询页面 (customid=78)
            url = "http://oa.netcoretec.com/wui/index.html#/main/cube/search?customid=78&menuIds=-92,-103&menuPathIds=-92,-128,-103"
            self.driver.get(url)
            time.sleep(8)  # 等待页面加载
            self.driver.switch_to.default_content()

            # 步骤 1: 找到客标型号输入框 (第6个cube-quicksearch-label，索引5)
            print("\n步骤 1: 找到客标型号输入框...")
            self.driver.execute_script("""
                var labels = document.querySelectorAll(".cube-quicksearch-label");
                if (labels.length >= 6) {
                    var label = labels[5];  // 客标型号是第6个
                    var container = label.closest("div[style*='inline-block']");
                    if (container) {
                        var antSelect = container.querySelector(".ant-select");
                        if (antSelect) antSelect.click();
                    }
                }
            """)
            time.sleep(1.5)  # 等待输入框出现

            # 步骤 2: 点击清除按钮（如果有已选中的型号）
            print("步骤 2: 清空已选中的型号...")
            self.driver.execute_script("""
                // 查找并点击清除按钮 (ant-select-selection__clear 或类似的)
                var clearBtns = document.querySelectorAll(".ant-select-selection__clear, .anticon-close, [class*='clear']");
                clearBtns.forEach(function(btn) {
                    if (btn.offsetParent !== null) {  // 如果可见
                        btn.click();
                    }
                });

                // 另一种方式：找到已选择的项并移除
                var selectedItems = document.querySelectorAll(".ant-select-selection__choice");
                selectedItems.forEach(function(item) {
                    var removeBtn = item.querySelector(".ant-select-selection__choice__remove");
                    if (removeBtn) removeBtn.click();
                });
            """)
            time.sleep(0.5)

            # 步骤 3: 输入客户型号
            print(f"步骤 3: 输入客户型号 '{customer_model}'...")
            search_input = self.driver.find_element(By.CSS_SELECTOR, ".ant-select-search__field")

            # 确保清空输入框
            search_input.click()
            time.sleep(0.3)
            search_input.send_keys(Keys.CONTROL, 'a')
            time.sleep(0.2)
            search_input.send_keys(Keys.DELETE)
            time.sleep(0.5)

            search_input.send_keys(customer_model)
            print(f"  已输入: {customer_model}")

            # 步骤 4: 等待3秒
            print("步骤 4: 等待3秒...")
            time.sleep(3)

            # 步骤 5: 按回车键
            print("步骤 5: 按回车键...")
            search_input.send_keys(Keys.RETURN)

            # 等待搜索结果
            print(f"等待搜索结果 ({wait_time}s)...")
            for i in range(wait_time):
                time.sleep(1)
                if i % 4 == 0:
                    rows = self.driver.execute_script("return document.querySelectorAll('.ant-table-tbody tr').length;")
                    print(f"  第{i+1}秒：rows={rows}")

            # 步骤 6: 提取数据
            print("\n步骤 6: 提取数据...")

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

            header = self.driver.execute_script("""
                var headers = document.querySelectorAll('.ant-table-thead th');
                var headerData = [];
                headers.forEach(function(th) {
                    headerData.push(th.innerText.trim());
                });
                return headerData;
            """)

            print(f"表头：{header}")
            print(f"找到 {len(data)} 条数据")

            # 验证：检查客标型号列是否匹配
            # 表头顺序: ['物料号', '描述', '生命周期', '物料分类', '品牌类别', '客标型号', '更新日期', '']
            # 客标型号是索引5
            customer_model_col = 5
            verified_data = []
            not_matched = []

            for row in data:
                if len(row) > customer_model_col:
                    model = row[customer_model_col].strip()
                    if customer_model.upper() in model.upper():
                        verified_data.append(row)
                    else:
                        not_matched.append(row)

            if not_matched:
                print(f"\n警告：有 {len(not_matched)} 条数据的客标型号不匹配 '{customer_model}'")
                print(f"  这些数据的客标型号: {set(row[customer_model_col] for row in not_matched)}")

            print(f"验证后：{len(verified_data)} 条数据匹配 '{customer_model}'")

            # 保存结果
            result = {
                'success': len(verified_data) > 0,
                'customer_model': customer_model,
                'total_rows': len(verified_data),
                'header': header,
                'data': verified_data,
                'files': {}
            }

            if len(verified_data) > 0:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                # 保存完整数据到 Excel
                all_data = [header] + verified_data
                filepath = self.output_dir / f"{customer_model}_products_{timestamp}.xlsx"
                df = pd.DataFrame(all_data)
                df.to_excel(filepath, index=False, engine='openpyxl')
                result['files']['products'] = str(filepath)
                print(f"\n已保存完整数据到：{filepath}")

                # 保存成品料号列表到文本文件（每行一个料号）
                part_numbers = [row[0] for row in verified_data]  # 物料号在第一列
                txt_filepath = self.output_dir / f"{customer_model}_part_numbers_{timestamp}.txt"
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {customer_model} 成品料号列表\n")
                    f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# 共 {len(part_numbers)} 个料号\n")
                    f.write("\n")
                    for pn in part_numbers:
                        f.write(f"{pn}\n")
                result['files']['part_numbers'] = str(txt_filepath)
                print(f"已保存料号列表到：{txt_filepath}")
                print(f"\n成品料号列表：")
                for pn in part_numbers:
                    print(f"  {pn}")

            return result

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def query_bom_by_material(self, material_number, wait_time=10):
        """
        通过成品料号查询完整 BOM
        参数：material_number - 成品料号（3000xxxx）
        """
        print("=" * 80)
        print(f"PLM BOM Getter - 查询 BOM: {material_number}")
        print("=" * 80)

        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.by import By

            # 导航到 BOM 查询页面 (customid=80)
            url = "http://oa.netcoretec.com/wui/index.html#/main/cube/search?customid=80&menuIds=-92,-103&menuPathIds=-92,-128,-103"
            self.driver.get(url)
            time.sleep(8)  # 等待页面加载
            self.driver.switch_to.default_content()

            # 步骤 1: 选择"多层"选项（必须在输入前先选择层级）
            print("\n步骤 1: 选择'多层'选项...")
            self.driver.execute_script("""
                var radios = document.querySelectorAll(".ant-radio-wrapper");
                for (var i = 0; i < radios.length; i++) {
                    var text = radios[i].innerText || radios[i].textContent || "";
                    if (text.includes("多层")) {
                        radios[i].click();
                        return;
                    }
                }
            """)
            time.sleep(1)

            # 步骤 2: 点击父阶料号的 ant-select
            print("步骤 2: 点击父阶料号输入框...")
            self.driver.execute_script("""
                var assoc = document.querySelector(".wea-associative-search .ant-select");
                if (assoc) assoc.click();
            """)
            time.sleep(1)

            # 步骤 3: 找到搜索输入框并输入物料号
            print(f"步骤 3: 输入物料号 '{material_number}'...")
            search_input = self.driver.find_element(By.CSS_SELECTOR, ".ant-select-search__field")
            # 先清空输入框
            search_input.send_keys(Keys.CONTROL, 'a')
            search_input.send_keys(Keys.DELETE)
            time.sleep(0.5)
            search_input.send_keys(material_number)

            # 步骤 4: 等待3秒
            print("步骤 4: 等待3秒...")
            time.sleep(3)

            # 步骤 5: 按回车键
            print("步骤 5: 按回车键...")
            search_input.send_keys(Keys.RETURN)

            # 等待搜索结果
            print(f"等待搜索结果 ({wait_time}s)...")
            for i in range(wait_time):
                time.sleep(1)
                if i % 4 == 0:
                    rows = self.driver.execute_script("return document.querySelectorAll('.ant-table-tbody tr').length;")
                    print(f"  第{i+1}秒：rows={rows}")

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

            header = self.driver.execute_script("""
                var headers = document.querySelectorAll('.ant-table-thead th');
                var headerData = [];
                headers.forEach(function(th) {
                    headerData.push(th.innerText.trim());
                });
                return headerData;
            """)

            print(f"表头：{header}")
            print(f"找到 {len(data)} 条 BOM 数据")

            # 保存结果
            result = {
                'success': len(data) > 0,
                'material_number': material_number,
                'total_rows': len(data),
                'header': header,
                'data': data,
                'files': {}
            }

            if len(data) > 0:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                all_data = [header] + data
                filepath = self.output_dir / f"{material_number}_BOM_{timestamp}.xlsx"
                df = pd.DataFrame(all_data)
                df.to_excel(filepath, index=False, engine='openpyxl')
                result['files']['bom'] = str(filepath)
                print(f"\n已保存 BOM 到：{filepath}")

            return result

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def close(self):
        """关闭浏览器连接"""
        if self.driver:
            self.driver.quit()
            print("已关闭浏览器连接")


def main():
    print("=" * 60)
    print("PLM BOM Getter - Selenium 版本")
    print("=" * 60)

    getter = PLMBOMGetter(port=9222)

    try:
        # 连接 Chrome
        print("\n1. 连接 Chrome 浏览器...")
        getter.connect_to_chrome()

        # 测试搜索客户型号
        print("\n2. 测试搜索客户型号...")
        result = getter.search_by_customer_model("N3D")

        if result['success']:
            print(f"\n 搜索成功！找到 {result['total_rows']} 条数据")

            # 如果有结果，测试 BOM 查询
            if result['total_rows'] > 0:
                # 获取第一个料号
                first_material = result['data'][0][0] if result['data'] else None
                if first_material:
                    print(f"\n3. 测试 BOM 查询：{first_material}")
                    bom_result = getter.query_bom_by_material(first_material)
                    if bom_result['success']:
                        print(f"\n BOM 查询成功！找到 {bom_result['total_rows']} 条数据")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        getter.close()


if __name__ == "__main__":
    sys.exit(main())
