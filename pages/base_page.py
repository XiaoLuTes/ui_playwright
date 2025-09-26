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
        self.wait_timeout = 15
        self.locators = self.locator.load_locators()
        self.settings = settings

    def get_element_locator(self, element_name):
        """获取元素定位器"""
        page_name_str = self.find_element_page(element_name)
        return self.locator.get_locator(page_name_str, element_name)

    @allure.step("打开页面: {url}")
    def open(self, url):
        """
        :param url: 要打开的完整URL
        """
        logger.info(f"正在打开页面: {url}")
        self.driver.get(url)
        logger.info(f"页面已成功打开: {url}")

    def find_element(self, element_name, action):
        """查找元素"""
        locator = self.get_element_locator(element_name)
        timeout = self.wait_timeout
        is_hidden_action = action.startswith("hidden_")

        if is_hidden_action:
            #  兼容隐藏元素(action标识以hidden_开头)
            try:
                return WebDriverWait(self.driver, timeout).until(
                    ec.presence_of_element_located(locator)
                )
            except TimeoutException:
                error_msg = f"隐藏元素查找超时: {element_name}"
                logger.error(error_msg)
                self.take_screenshot(f"隐藏元素查找超时-{element_name}")
                raise TimeoutException(error_msg)
        else:
            try:
                return WebDriverWait(self.driver, timeout).until(
                    ec.visibility_of_element_located(locator)
                )
            #  等待元素可见
            except TimeoutException:
                error_msg = f"元素查找超时: {element_name}"
                logger.error(error_msg)
                self.take_screenshot(f"元素查找超时-{element_name}")
                raise TimeoutException(error_msg)

    @allure.step("对元素输入文本: {element_name}")
    def input_text(self, element_name, action, text):
        """输入文本"""
        logger.info(f"在元素 {element_name} 输入: {text}")
        element_id = self.find_element(element_name, action)
        element_id.clear()
        element_id.send_keys(text)

    @allure.step("点击元素: {element_name}")
    def element_click(self, element_name, action):
        """点击元素"""
        element = self.find_element(element_name, action)
        element.click()
        logger.info(f"点击元素: {element_name}")

    @allure.step("获取元素文本: {element_name}")
    def get_text(self, element_name, action):
        """获取元素文本"""
        element = self.find_element(element_name, action)
        return element.text

    @allure.step("校验元素值: {element_name}")
    def get_element_value(self, element_name, action):
        """获取元素值"""
        element = self.find_element(element_name, action)
        return element.get_attribute('value')

    @allure.step("检查元素是否存在: {element_name}")
    def is_element_present(self, element_name, action):
        """检查元素是否存在"""
        try:
            self.find_element(element_name, action)
            return True
        except TimeoutException:
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
        for _ in range(times):  # 按下多少次什么箭头
            actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        logger.info(f"输入向下指令: {times}次")
        # time.sleep(3) # 等待元素显现

    @allure.step("模拟键盘向上按键")
    def keyboard_up(self, data):
        """模拟键盘输入向下，用于选择框滑动，使元素可见"""
        actions = ActionChains(self.driver)
        times = int(data)
        for _ in range(times):  # 按下多少次什么箭头
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
    def upload_file(self, element_name, data, action):
        """
        使用已封装的find_element方法上传文件
        :param element_name: 文件输入元素
        :param data: 要上传的文件路径
        :param action: 动作，这里用来判断是否是隐藏的元素
        :return: Boolean 表示是否上传成功
        """
        allure.attach(f"上传文件: {data}", f"到元素: {element_name}")
        try:
            # 确保文件存在
            if not os.path.exists(data):
                error_msg = f"文件不存在: {data}"
                raise FileNotFoundError(error_msg)
            # 获取文件的绝对路径（更可靠）
            absolute_path = os.path.abspath(data)
            allure.attach("文件绝对路径", absolute_path, allure.attachment_type.TEXT)
            file_input = self.find_element(element_name, action)
            # 确保元素是文件输入类型
            input_type = file_input.get_attribute("type")
            if input_type and input_type.lower() != "file":
                allure.attach("警告", f"元素类型不是'file',而是'{input_type}'", allure.attachment_type.TEXT)
            # 发送文件路径
            file_input.send_keys(absolute_path)
        except FileNotFoundError as e:
            # 文件不存在异常
            error_msg = f"文件错误: {str(e)}"
            allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
            self.take_screenshot(f"file_not_found_{os.path.basename(data)}")
            raise
        except TimeoutException as e:
            # 元素查找超时异常
            error_msg = f"文件输入元素查找超时: {str(e)}"
            allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
            self.take_screenshot(f"file_input_timeout_{element_name[0]}_{element_name[1]}")
            raise
        except Exception as e:
            # 其他未知异常
            error_msg = f"文件上传过程中发生未知错误: {str(e)}"
            allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
            self.take_screenshot(f"file_upload_error_{os.path.basename(data)}")
            raise
