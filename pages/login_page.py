import time
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pages.base_page import BasePage
from utils.logger import logger
from config.settings import Settings
import allure


class LoginPage(BasePage):
    """
    登录页面对象 - 封装登录页面相关操作
    继承自BasePage
    """

    def __init__(self, driver):
        """初始化登录页面"""
        super().__init__(self, driver)
        # 获取配置
        self.logger = logger
        self.settings = Settings()
        # load_locator = ElementLocator()
        # self.locator = load_locator.load_locators()["login_page"]

    @allure.step("导航到登录页面")
    def navigate_to_login(self, max_retry=3):
        """打开登录页面"""
        login_url = self.settings.URL
        locator = self.get_element_locator("username_input")
        time_out = self.settings.IMPLICIT_WAIT
        for times in range(max_retry):
            try:
                self.logger.info(f"尝试导航到登录页面 (尝试 {times + 1}/{max_retry}次登录): {login_url}")
                self.open(login_url)
                # 等待页面关键元素加载完成
                WebDriverWait(self.driver, time_out).until(
                    ec.presence_of_element_located(locator)
                )
                self.logger.info("成功导航到登录页面")
                return True

            except TimeoutException as e:
                self.logger.warning(f"导航到登录页面超时 (尝试 {times + 1}/{max_retry}次登录): {str(e)}")
                if times == max_retry - 1:
                    self.logger.error("所有重试尝试均失败")
                    raise e
                time.sleep(5)

            except Exception as e:
                self.logger.error(f"打开页面时发生错误: {str(e)}")
                if times == max_retry - 1:
                    raise e
        return False
