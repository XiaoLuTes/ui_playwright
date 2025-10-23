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
        hidden_timeout = self.hidden_wait_timeout
        is_hidden_action = action.startswith("hidden_")

        if is_hidden_action:
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
                logger.error(error_msg)
                # 兼容隐藏元素，action未以hidden_开头(直接使用会导致框架效率过低)
                try:
                    return WebDriverWait(self.driver, hidden_timeout).until(
                        ec.presence_of_element_located(locator))
                except TimeoutException:
                    error_msg = f"尝试查找隐藏元素失败: {element_name}"
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
        if element:
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
                        element_retry = self.find_element(element_name, action)
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
        try:
            # 确保文件存在
            if not os.path.exists(data):
                error_msg = f"文件不存在: {data}"
                raise FileNotFoundError(error_msg)
            # 获取文件的绝对路径
            absolute_path = os.path.abspath(data)
            allure.attach(absolute_path, "文件绝对路径", allure.attachment_type.TEXT)
            file_input = self.find_element(element_name, action)
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
