from pages.base_page import BasePage
from utils.logger import logger
from config.settings import settings
import allure


class LoginPage(BasePage):
    """
    登录页面对象 - 封装登录页面相关操作
    继承自BasePage
    """

    # 元素定位器 - 使用元组(By, value)格式
    # USERNAME_INPUT = ("id", "username")
    # PASSWORD_INPUT = ("id", "password")
    # LOGIN_BUTTON = ("id", "loginBtn")
    # ERROR_MSG = ("css selector", ".error-message")
    # SUCCESS_MSG = ("css selector", ".welcome-message")

    def __init__(self, driver):
        """初始化登录页面"""
        super().__init__(self, driver)
        # 获取配置
        self.config = settings
        # load_locator = ElementLocator()
        # self.locator = load_locator.load_locators()["login_page"]

    @allure.step("导航到登录页面")
    def navigate_to_login(self):
        """打开登录页面"""
        login_url = self.config.URL
        logger.info(f"开始导航到登录页面: {login_url}")
        self.open(login_url)
        logger.info(f"已导航到登录页面: {login_url}")
