from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from utils.logger import logger
from utils.element_locator import ElementLocator
from config.settings import settings
import allure
import time
import os
from pathlib import Path


class BasePage:
    """页面基类"""

    def __init__(self, page_name, page):
        self.page = page  # 页面对象
        self.page_name = page_name  # 页面名
        self.locator = ElementLocator()  # 元素定位器
        self.locators = self.locator.load_locators()  # 获取所有页面元素
        self.settings = settings  # 配置项
        self.wait_timeout = self.settings.IMPLICIT_WAIT
        self._db_utils = None
        self.page_manager = None

        self.page.set_default_timeout(self.wait_timeout)

    def set_page_manager(self, page_manager):
        self.page_manager = page_manager

    def get_element_locator(self, element_name):
        page_name_str = self.find_element_page(element_name)
        return self.locator.get_locator(page_name_str, element_name)

    def set_db_utils(self, db_utils):
        self._db_utils = db_utils
        logger.debug(f"页面 '{self.page_name}' 已注入数据库连接")

    @allure.step("打开页面: {url}")
    def open(self, url):
        logger.info(f"打开页面: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        logger.info(f"页面打开成功: {url}")

    # ==================== 查找元素 ====================
    def find_element(self, element_name):
        by, value = self.get_element_locator(element_name)
        is_hidden = element_name.startswith("hidden_")
        by = by.lower()
        if by == "id":
            loc = self.page.locator(f"#{value}")
        elif by == "xpath":
            loc = self.page.locator(f"xpath={value}")
        elif by == "css":
            loc = self.page.locator(value)
        elif by == "name":
            loc = self.page.locator(f"[name='{value}']")
        else:
            loc = self.page.locator(value)
        loc = loc.first  # 如果找到多个元素,则返回第一个

        try:
            if is_hidden:
                loc.wait_for(state="attached")
            else:
                loc.wait_for(state="visible")
            return loc
        except PlaywrightTimeoutError:
            error_msg = f"元素查找超时: {element_name}"
            logger.error(error_msg)
            self.take_screenshot(f"元素查找超时-{element_name}")
            raise PlaywrightTimeoutError(error_msg)
        except Exception as e:
            error_msg = f"元素{element_name}查找失败: {e}"
            logger.error(error_msg)
            self.take_screenshot(f"元素查找失败-{element_name}")
            raise e

    # ==================== 输入文本 ====================
    @allure.step("对元素【{element_name}】输入文本: {text}")
    def input_text(self, element_name, text, clear_first=True):
        logger.info(f"元素【{element_name}】输入: {text}")
        loc = self.find_element(element_name)
        if clear_first:
            loc.fill("")
        loc.fill(str(text))

    # ==================== 点击元素====================
    @allure.step("点击元素: {element_name}")
    def element_click(self, element_name):
        loc = self.find_element(element_name)
        loc.scroll_into_view_if_needed()

        try:
            loc.click()
            logger.info(f"点击成功: {element_name}")
        except Exception as e:
            err_msg = str(e).lower()
            # 遮挡时，尝试JavaScript点击
            if "click intercepted" in err_msg or "not clickable" in err_msg or "pointer-intercept" in err_msg:
                logger.warning(f"元素被遮挡/不可点击，启用 JS 点击: {element_name}")
                self.page.evaluate("""(el) => {
                    el.scrollIntoView({ block: "center" });
                    el.click();
                }""", loc.element_handle())
                logger.info(f"JS 点击完成: {element_name}")
            else:
                logger.error(f"点击失败: {element_name} => {e}")
                raise

    # ==================== 获取文本 ====================
    @allure.step("获取元素文本: {element_name}")
    def get_text(self, element_name):
        loc = self.find_element(element_name)
        return loc.text_content().strip()

    # ==================== 获取输入框值 ====================
    @allure.step("获取元素值: {element_name}")
    def get_element_value(self, element_name):
        loc = self.find_element(element_name)
        return loc.input_value().strip()

    # ==================== 判断元素是否存在====================
    def is_element_present(self, element_name):
        try:
            self.find_element(element_name)
            return True
        except PlaywrightTimeoutError:
            return False

    # ==================== 截图 ====================
    @allure.step("页面截图")
    def take_screenshot(self, name="screenshot"):
        screenshot_dir = self.settings.SCREENSHOT_PATH
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)

        self.page.screenshot(path=filepath, full_page=True)
        logger.info(f"截图已保存: {filepath}")

        allure.attach.file(
            filepath,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )

    # ==================== 查找元素所属页面 ====================
    def find_element_page(self, element_name):
        for page_name, elements in self.locators.items():
            if element_name in elements:
                return page_name
        return None

    # ==================== 键盘向下 ====================
    @allure.step("键盘向下按键 {data} 次")
    def keyboard_down(self, data):
        times = int(data)
        for _ in range(times):
            self.page.keyboard.press("ArrowDown")
        logger.info(f"向下按键 {times} 次")

    # ==================== 键盘向上 ====================
    @allure.step("键盘向上按键 {data} 次")
    def keyboard_up(self, data):
        times = int(data)
        for _ in range(times):
            self.page.keyboard.press("ArrowUp")
        logger.info(f"向上按键 {times} 次")

    # ==================== 回车键 ====================
    @allure.step("按下 Enter 键")
    def keyboard_enter(self):
        self.page.keyboard.press("Enter")
        logger.info("按下 Enter 键")

    # ==================== 上传文件 ====================
    @allure.step("上传文件: {data}")
    def upload_file(self, element_name, data):
        if not Path(data).exists():
            raise FileNotFoundError(f"文件不存在: {data}")

        abs_path = str(Path(data).resolve())
        loc = self.find_element(element_name)
        loc.set_input_files(abs_path)
        logger.info(f"文件上传成功: {abs_path}")
        time.sleep(3)

    # ==================== 等待元素值/文本变化 ====================
    @allure.step("等待元素【{element_name}】的【{real_action}】等于【{expected_value}】")
    def wait_for_element_value(self, element_name, real_action, expected_value):
        timeout = self.settings.EXPLICIT_WAIT
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                if real_action == "value":
                    val = self.get_element_value(element_name)
                elif real_action == "text":
                    val = self.get_text(element_name)
                else:
                    val = self.get_element_value(element_name)

                if val.strip() == str(expected_value).strip():
                    logger.info(f"值匹配成功: {expected_value}")
                    return
            except PlaywrightTimeoutError:
                pass
            time.sleep(1)

        error_msg = f"等待超时: {element_name} 期望={expected_value}"
        self.take_screenshot(f"等待值超时-{element_name}")
        raise Exception(error_msg)

    # ==================== 等待元素出现 ====================
    def wait_for_element_appear(self, element_name):
        total_wait = self.settings.WAIT_ELEMENT_APPEAR
        refresh_interval = self.settings.REFRESH_TIME
        start_time = time.time()
        last_refresh_time = start_time

        while time.time() - start_time < total_wait:
            if self.is_element_present(element_name):
                logger.info(f"元素已出现: {element_name}")
                return True

            if time.time() - last_refresh_time >= refresh_interval:
                logger.info("刷新页面继续等待...")
                self.page.reload()
                last_refresh_time = time.time()

            time.sleep(2)

        error_msg = f"等待元素出现超时: {element_name}"
        self.take_screenshot(f"等待元素超时-{element_name}")
        raise Exception(error_msg)

    # ==================== 数据库验证（无修改） ====================
    @allure.step("执行 SQL 验证")
    def verify_mysql_data(self, sql: str, expected: str):
        logger.info(f"执行 SQL: {sql}")
        result = self._db_utils.execute_query(sql)
        allure.attach(str(result), "SQL 查询结果", allure.attachment_type.TEXT)

        if not self.parse_and_verify_expected(result, expected):
            raise AssertionError(f"数据库验证失败，期望结果: {expected}")
        logger.info("数据库验证通过")

    def parse_and_verify_expected(self, result, expected):
        if expected.lower() in ["empty", "[]", "null", "none"]:
            return len(result) == 0
        if expected.startswith("count:"):
            return len(result) == int(expected.split(":")[1])
        if expected.startswith("count>:"):
            return len(result) > int(expected.split(":")[1])
        if expected.startswith("contains:"):
            v = expected.split(":", 1)[1]
            return any(v in str(val) for row in result for val in row.values())
        if "=" in expected:
            return self.verify_field_values(result, expected)
        if len(result) == 1 and len(result[0]) == 1:
            return str(list(result[0].values())[0]) == expected
        return len(result) > 0

    @staticmethod
    def verify_field_values(result, expected):
        expect_dict = dict(kv.split("=", 1) for kv in expected.split(","))
        for row in result:
            if all(str(row[k]).strip() == v.strip() for k, v in expect_dict.items()):
                return True
        return False

    @allure.step("执行数据库更新 SQL")
    def execute_mysql_update(self, sql: str):
        rows = self._db_utils.execute_update(sql)
        logger.info(f"更新完成，影响行数: {rows}")
        return rows
