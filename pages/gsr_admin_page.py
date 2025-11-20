import time
from selenium.common import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pages.base_page import BasePage
from utils.logger import logger
from config.settings import Settings
import allure


class GsrAdminPage(BasePage):
    """
    管理端页面对象 - 封装登录页面相关操作
    继承自BasePage
    """

    def __init__(self, page_name, driver):
        """初始化登录页面"""
        super().__init__(page_name, driver)
        # 获取配置
        self.logger = logger
        self.settings = Settings()

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

    @allure.step("执行登录操作")
    def perform_login(self):
        """执行登录操作"""
        try:
            self.input_text("username_input", self.settings.USER)
            self.input_text("password_input", self.settings.PASSWORD)
            self.input_text("code_input", '1')
            self.element_click("login_button")
            # 等待登录成功 - 检查登录后页面元素
            self.is_element_present("talent_button")
            self.logger.info("登录成功")
            # 如果提供了executor，则在登录成功后注册项目所需的页面对象
            # if executor:
            #     self.register_project_pages(executor)
            return True
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            self.take_screenshot("登录失败")
            raise e

    def ensure_logged_in(self):
        """确保用户已登录"""
        login_url = self.settings.URL
        try:
            # 检查是否已经登录（通过检查登录后的元素是否存在）
            self.open(login_url)
            if (self.is_element_present("talent_button", 5) or
                    self.is_element_present("user_part", 5)):
                self.logger.info("用户已登录")
                return True
            else:
                self.logger.info("用户未登录，开始执行登录")
                # 导航到登录页面
                self.navigate_to_login()
                # 执行登录
                return self.perform_login()
        except Exception as e:
            self.logger.error(f"确保登录状态失败: {str(e)}")
            self.take_screenshot("确保登录状态失败")
            raise e
