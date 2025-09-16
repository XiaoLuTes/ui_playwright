from utils.logger import logger
from .base_page import BasePage
import allure
from utils.element_locator import ElementLocator

class DashboardPage(BasePage):
    """仪表盘页面对象"""

    def __init__(self, driver):
        super().__init__(driver, "dashboard_page")
        load_locator = ElementLocator()
        self.locator = load_locator.load_locators()

    @allure.step("验证登录成功")
    def verify_login_success(self, locator, expected):
        """验证登录成功"""
        locator_text = self.get_text(locator)   # 获取元素的文本
        expected_text = f"{expected}"   # 获取预期文本
        assert expected_text in locator_text, f"文本内容不符: {expected}"

    @allure.step("退出登录")
    def logout(self):
        """退出登录"""
        self.element_click("logout_button", "logout")
        logger.info("已退出登录")
