from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from utils.logger import logger
from utils.element_locator import ElementLocator
from config.settings import settings
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import allure
import time
import os


class BasePage:
    """页面基类 - 支持从YAML文件获取元素定位器"""

    def __init__(self, page_name, driver):
        self.driver = driver
        self.page_name = page_name
        self.locator = ElementLocator()
        self.locators = self.locator.load_locators()
        self.settings = settings
        self.wait_timeout = self.settings.IMPLICIT_WAIT
        self.hidden_wait_timeout = self.settings.HIDDEN_FIND_WAIT
        self.db_timeout = self.settings.DB_TIMEOUT
        self._db_utils = None
        self.page_manager = None

    def set_page_manager(self, page_manager):
        """引用页面管理器"""
        self.page_manager = page_manager

    def get_element_locator(self, element_name):
        """获取元素定位器"""
        page_name_str = self.find_element_page(element_name)
        return self.locator.get_locator(page_name_str, element_name)

    def set_db_utils(self, db_utils):
        """设置数据库工具实例"""
        self._db_utils = db_utils
        logger.debug(f"页面 '{self.page_name}' 设置数据库工具")

    @allure.step("打开页面: {url}")
    def open(self, url):
        """
        :param url: 要打开的完整URL
        """
        logger.info(f"正在打开页面: {url}")
        self.driver.get(url)
        logger.info(f"页面已成功打开: {url}")

    def find_element(self, element_name):
        """查找元素"""
        locator = self.get_element_locator(element_name)
        timeout = self.wait_timeout
        hidden_timeout = self.hidden_wait_timeout
        is_hidden_element = element_name.startswith("hidden_")

        if is_hidden_element:
            #  兼容隐藏元素(action标识以hidden_开头)
            try:
                return WebDriverWait(self.driver, timeout).until(
                    ec.presence_of_element_located(locator))
            except TimeoutException:
                error_msg = f"隐藏元素查找超时: {element_name}"
                logger.error(error_msg)
                self.take_screenshot(f"隐藏元素查找超时-{element_name}")
                raise TimeoutException(error_msg)
        else:
            try:
                return WebDriverWait(self.driver, timeout).until(
                    ec.visibility_of_element_located(locator))
            except TimeoutException:
                error_msg = f"元素查找超时: {element_name},尝试查找是否为隐藏元素"
                logger.warning(error_msg)
                # 兼容隐藏元素，action未以hidden_开头(直接使用会导致框架效率过低)
                try:
                    find_hidden_element = WebDriverWait(self.driver, hidden_timeout).until(
                        ec.presence_of_element_located(locator))
                    logger.info(f"查找到隐藏元素：{element_name}")
                    return find_hidden_element
                except TimeoutException:
                    error_msg = f"尝试查找隐藏元素失败: {element_name}"
                    logger.error(error_msg)
                    self.take_screenshot(f"元素查找超时-{element_name}")
                    raise TimeoutException(error_msg)

    @allure.step("对元素输入文本: {text}")
    def input_text(self, element_name, text, clear_first=True):
        """输入文本"""
        logger.info(f"在元素 {element_name} 输入: {text}")
        element_id = self.find_element(element_name)
        if clear_first:
            # element_id.clear()
            current_value = element_id.get_attribute("value")
            if current_value:
                logger.info(f"输入框存在内容:'{current_value}',开始清空输入框内容")
                element_id.send_keys(Keys.CONTROL + 'a')
                element_id.send_keys(Keys.DELETE)
        element_id.send_keys(text)

    @allure.step("点击元素: {element_name}")
    def element_click(self, element_name):
        """点击元素"""
        element_is_true = self.find_element(element_name)
        if element_is_true:
            try:
                element = self.wait_for_element_clickable(element_name)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                logger.info(f"已滚动到元素: {element_name}")
                # 防止其他元素遮挡导致无法点击
                element.click()
                logger.info(f"点击元素: {element_name}")
            except Exception as e:
                e_str = str(e)
                error_msg = f"点击元素失败: {element_name}, 错误：{e_str}"
                logger.error(error_msg)
                if "element click intercepted" in e_str or "not clickable" in e_str:
                    logger.info("检测到元素被遮挡，尝试使用JavaScript点击")
                    try:
                        element_retry = self.find_element(element_name)
                        self.driver.execute_script("arguments[0].click();", element_retry)
                        logger.info(f"通过JavaScript点击成功: {element_name}")
                    except Exception as js_e:
                        js_error_msg = f"尝试JavaScript点击失败: {element_name}, 错误: {str(js_e)}"
                        logger.error(js_error_msg)
                        self.take_screenshot(f"尝试JavaScript点击失败-{element_name}")
                        raise Exception(js_error_msg)
                else:
                    # 其他类型的错误，直接截图并抛出
                    self.take_screenshot(f"点击失败-{element_name}")
                    raise e

    @allure.step("获取元素文本: {element_name}")
    def get_text(self, element_name):
        """获取元素文本"""
        element = self.find_element(element_name)
        return element.text

    @allure.step("校验元素值: {element_name}")
    def get_element_value(self, element_name):
        """获取元素值"""
        element = self.find_element(element_name)
        return element.get_attribute('value')

    def is_element_present(self, element_name, timeout=None):
        """检查元素是否存在"""
        locator = self.get_element_locator(element_name)
        if timeout is None:
            timeout = self.wait_timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                ec.visibility_of_element_located(locator))
            logger.info(f"查找到元素：{element_name}")
            return True
        except TimeoutException:
            logger.info(f"未找到指定元素: {element_name}")
            return False

    @allure.step("截图")
    def take_screenshot(self, name="screenshot"):
        """截图"""
        screenshot_dir = self.settings.SCREENSHOT_PATH
        os.makedirs(screenshot_dir, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)

        self.driver.save_screenshot(filepath)
        logger.info(f"已截图: {filepath}")

        allure.attach.file(
            filepath,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )

    def find_element_page(self, element_name):
        """查找元素所在的页面"""
        for page_name, elements in self.locators.items():
            if element_name in elements:
                return page_name
        return None

    @allure.step("模拟键盘向下按键")
    def keyboard_down(self, data):
        """模拟键盘输入向下，用于选择框滑动，使元素可见"""
        actions = ActionChains(self.driver)
        times = int(data)
        for _ in range(times):
            actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        logger.info(f"输入向下指令: {times}次")

    @allure.step("模拟键盘向上按键")
    def keyboard_up(self, data):
        """模拟键盘输入向下，用于选择框滑动，使元素可见"""
        actions = ActionChains(self.driver)
        times = int(data)
        for _ in range(times):
            actions.send_keys(Keys.ARROW_UP)
        actions.perform()
        logger.info(f"输入向下指令: {times}次")

    @allure.step("点击enter键")
    def keyboard_enter(self):
        """点击enter键"""
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        logger.info(f"点击enter键")

    @allure.step("上传文件: {data} 到元素: {element_name}")
    def upload_file(self, element_name, data):
        """
        使用已封装的find_element方法上传文件
        :param element_name: 文件输入元素
        :param data: 要上传的文件路径
        :return: Boolean 表示是否上传成功
        """
        try:
            # 确保文件存在
            if not os.path.exists(data):
                error_msg = f"文件不存在: {data}"
                raise FileNotFoundError(error_msg)
            # 获取文件的绝对路径
            absolute_path = os.path.abspath(data)
            allure.attach(absolute_path, "文件绝对路径", allure.attachment_type.TEXT)
            file_input = self.find_element(element_name)
            # 确保元素是文件输入类型
            input_type = file_input.get_attribute("type")
            if input_type and input_type.lower() != "file":
                allure.attach(f"元素类型不是file',而是'{input_type}'", f"警告", allure.attachment_type.TEXT)
            # 发送文件路径
            file_input.send_keys(absolute_path)
            # 等待5秒确保上传成功
            time.sleep(5)
        except FileNotFoundError as e:
            # 文件不存在异常
            error_msg = f"文件错误: {str(e)}"
            allure.attach(error_msg, "错误信息", allure.attachment_type.TEXT)
            self.take_screenshot(f"文件不存在_{os.path.basename(data)}")
            raise
        except TimeoutException as e:
            # 元素查找超时异常
            error_msg = f"文件输入元素查找超时: {str(e)}"
            allure.attach(error_msg, "错误信息", allure.attachment_type.TEXT)
            self.take_screenshot(f"文件上传超时_{element_name}")
            raise
        except Exception as e:
            # 其他异常
            error_msg = f"文件上传过程中发生未知错误: {str(e)}"
            allure.attach(error_msg, "错误信息", allure.attachment_type.TEXT)
            self.take_screenshot(f"未知错误_{os.path.basename(data)}")
            raise

    def wait_for_element_clickable(self, element_name):
        # 等待元素可点击状态
        locator = self.get_element_locator(element_name)
        wait_time = self.settings.IMPLICIT_WAIT
        try:
            wait = WebDriverWait(self.driver, wait_time)
            return wait.until(ec.element_to_be_clickable(locator))
        except TimeoutException:
            logger.error(f"元素{wait_time}秒后仍为不可点击状态{element_name}")
            raise

    @allure.step("等待元素{element_name}的{real_action}变更为{expected_value}")
    def wait_for_element_value(self, element_name, real_action, expected_value):
        # 等待元素值或文本变化
        try:
            self.find_element(element_name)
        except TimeoutException:
            error_msg = f"元素查找失败: {element_name}"
            logger.error(error_msg)
            self.take_screenshot(f"元素查找失败-{element_name}")
            raise TimeoutException(error_msg)

        timeout = self.settings.EXPLICIT_WAIT
        refresh_time = self.settings.REFRESH_TIME
        start_time = time.time()

        def value_equals(_):
            """
            获取元素当前值与期望值比较
            :param _:
            :return: True or False
            """
            if real_action == "value":
                old_value = self.get_element_value(element_name)
            elif real_action == "text":
                old_value = self.get_text(element_name)
            else:
                old_value = self.get_element_value(element_name)
            return old_value == str(expected_value)

        try:
            while time.time() - start_time < timeout:
                try:
                    WebDriverWait(self.driver, refresh_time).until(value_equals)
                    logger.info(f"元素 {element_name} 的值已变为: {expected_value}")
                    break
                except TimeoutException:
                    if time.time() - start_time > timeout:
                        raise
                    try:
                        self.find_element(element_name)
                        logger.info(f"等待{refresh_time}秒后元素值不符合{expected_value},刷新页面后继续等待")
                        self.driver.refresh()
                        time.sleep(2)
                    except TimeoutException:
                        error_msg = "元素在等待过程中消失"
                        logger.error(error_msg)
                        self.take_screenshot(f"元素在等待过程中消失-{element_name}")
                        raise TimeoutException(error_msg)

        except TimeoutException:
            if real_action == "value":
                current_value = self.get_element_value(element_name)
            elif real_action == "text":
                current_value = self.get_text(element_name)
            else:
                current_value = self.get_element_value(element_name)
            error_msg = f"等待元素值变化超时: {element_name}, 期望: {expected_value}, 实际: {current_value}"
            logger.error(error_msg)
            self.take_screenshot(f"等待元素值变化超时-{element_name}")
            raise TimeoutException(error_msg)

    @allure.step("执行数据库验证")
    def verify_mysql_data(self, sql: str, expected: str):
        """
        执行SQL查询并验证结果
        Args:
            sql (str): 要执行的SQL查询语句
            expected (str): 期望的结果，支持多种格式
        """
        try:
            # 记录开始执行的日志
            logger.info(f"执行SQL验证: {sql}")
            logger.info(f"期望结果: {expected}")
            result = self._db_utils.execute_query(sql)
            allure.attach(str(result), "SQL执行结果", allure.attachment_type.TEXT)
            verification_passed = self.parse_and_verify_expected(result, expected)
            if verification_passed:
                logger.info("数据库验证成功")
            else:
                # 验证失败，准备错误信息
                error_msg = f"数据库验证失败: SQL={sql}, 期望={expected}, 实际结果={result}"
                raise AssertionError(error_msg)

        except TimeoutError as e:
            # 处理超时错误
            error_msg = f"数据库验证超时: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot("数据库验证超时")
            raise
        except Exception as e:
            # 处理其他所有异常
            error_msg = f"数据库验证执行失败: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot("数据库验证异常")
            raise

    def parse_and_verify_expected(self, result, expected: str) -> bool:
        """
        解析期望结果并进行验证
        Args:
            result: 数据库查询结果
            expected (str): 期望结果字符串
        Returns:
            bool: 验证是否通过
        """
        # 如果expected为空
        if expected.lower() in ["empty", "[]", "null", "none"]:
            return len(result) == 0

        # expected以count:开头(需要计数)
        if expected.startswith("count:"):
            expected_count = int(expected.split(":")[1].strip())
            return len(result) == expected_count

        # expected以count>开头(大于某数)
        if expected.startswith("count>:"):
            min_count = int(expected.split(":")[1].strip())
            return len(result) > min_count

        # expected以contains:开头(包含)
        if expected.startswith("contains:"):
            expected_value = expected.split(":", 1)[1].strip()
            return self.verify_contains(result, expected_value)

        # 字段值验证 - 格式: "字段=值" 或 "字段1=值1,字段2=值2"
        if "=" in expected and not expected.startswith(("count", "contains")):
            return self.verify_field_values(result, expected)

        # 直接值比较（用于单值查询）- 当结果只有一行一列时
        if len(result) == 1 and len(result[0]) == 1:
            actual_value = list(result[0].values())[0]
            return str(actual_value) == expected

        # 都不包含情况下，检查结果是否非空
        return len(result) > 0

    @staticmethod
    def verify_contains(result, expected_value: str) -> bool:
        """
        验证结果中包含特定值
        """
        for row in result:
            # 遍历每一行中的每个值
            for value in row.values():
                # 检查期望值是否出现在当前值的字符串形式中
                if expected_value in str(value):
                    return True
        return False

    @staticmethod
    def verify_field_values(result, expected: str) -> bool:
        """
        验证字段值
        Args:
            result: 数据库查询结果
            expected (str): 期望的字段值对
        Returns:
            bool: 是否有行匹配所有期望的字段值
        """
        # 解析期望的字段值对
        expected_pairs = {}  # 创建空字典存储字段值对
        for pair in expected.split(","):  # 按逗号分割多个字段值对
            if "=" in pair:
                key, value = pair.split("=", 1)  # 按等号分割字段名和值
                expected_pairs[key.strip()] = value.strip()
        if not expected_pairs:
            return False
        # 检查是否有行匹配所有期望的字段值
        for row in result:
            match = True  # 假设当前行匹配
            for field, expected_value in expected_pairs.items():
                if field not in row or str(row[field]) != expected_value:
                    match = False
                    break
            if match:
                return True
        return False

    @allure.step("执行数据库更新操作")
    def execute_mysql_update(self, sql: str):
        """
        执行数据库更新操作（INSERT, UPDATE, DELETE）
        Args:
            sql (str): 要执行的SQL语句
        Returns:
            int: 影响的行数
        """
        try:
            logger.info(f"执行数据库更新: {sql}")
            affected_rows = self._db_utils.execute_update(sql, timeout=self.db_timeout)
            logger.info(f"数据库更新成功，影响行数: {affected_rows}")
            return affected_rows  # 返回影响的行数
        except TimeoutError as e:
            # 处理超时错误
            error_msg = f"数据库更新超时: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot("数据库更新超时")
            raise
        except Exception as e:
            error_msg = f"数据库更新执行失败: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot("数据库更新失败")
            raise  # 重新抛出异常

    def wait_for_element_appear(self, element_name):
        start_time = time.time()
        last_refresh_time = start_time
        total_timeout = self.settings.WAIT_ELEMENT_APPEAR
        refresh_interval = self.settings.REFRESH_TIME
        attempt_count = 0
        logger.info(f"开始等待元素出现: {element_name}, 总超时时间: {total_timeout}秒")

        while (time.time() - start_time) < total_timeout:
            attempt_count += 1
            current_time = time.time()
            elapsed_time = current_time - start_time
            logger.debug(f"第{attempt_count}次尝试查找元素: {element_name}, 已等待{elapsed_time:.1f}秒")
            # 使用原有的方法检查元素是否存在
            if self.is_element_present(element_name, timeout=3):
                total_elapsed = time.time() - start_time
                logger.info(f"成功找到元素: {element_name}, 总耗时{total_elapsed:.1f}秒, 共尝试{attempt_count}次")
                return True
            if current_time - last_refresh_time >= refresh_interval:
                logger.info(f"刷新页面，已等待{elapsed_time:.1f}秒")
                try:
                    self.driver.refresh()
                    last_refresh_time = time.time()
                except Exception as e:
                    logger.warning(f"刷新页面时出现异常: {e}")
            time.sleep(2)

        error_msg = f"在{total_timeout}秒总超时时间内未找到元素: {element_name}, 共尝试{attempt_count}次"
        self.take_screenshot(f"等待元素{element_name}出现超时")
        logger.error(error_msg)
        raise TimeoutException(error_msg)
