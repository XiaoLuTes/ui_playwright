import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage
from utils.logger import logger
from config.settings import Settings


class GsrAdminPage(BasePage):
    """管理端页面"""

    def __init__(self, page_name, page):
        super().__init__(page_name, page)
        self.settings = Settings()

    @allure.step("导航到登录页面")
    def navigate_to_login(self, max_retry=3):
        login_url = self.settings.URL

        for attempt in range(max_retry):
            try:
                logger.info(f"导航到登录页面 第 {attempt + 1}/{max_retry} 次")
                self.open(login_url)
                # 等待用户名输入框出现（自动等待）
                self.find_element("username_input")
                logger.info("成功进入登录页面")
                return True

            except PlaywrightTimeoutError:
                logger.warning(f"登录页面加载超时，重试中 {attempt + 1}/{max_retry}")
                if attempt == max_retry - 1:
                    logger.error("所有重试均失败")
                    raise
                self.page.wait_for_timeout(5000)

            except Exception as e:
                logger.error(f"打开页面异常: {str(e)}")
                if attempt == max_retry - 1:
                    raise
                self.page.wait_for_timeout(3000)

        return False

    @allure.step("执行登录操作")
    def perform_login(self):
        try:
            # 输入账号
            self.input_text("username_input", self.settings.USER)
            # 输入密码
            self.input_text("password_input", self.settings.PASSWORD)
            # 输入验证码
            self.input_text("code_input", '1')
            # 点击登录
            self.element_click("login_button")
            self.is_element_present("talent_button")
            return True

        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            self.take_screenshot("登录失败")
            raise

    @allure.step("确保已登录状态")
    def ensure_logged_in(self):
        try:
            self.open(self.settings.URL)
            # 5秒内检查是否已登录（元素存在即代表已登录）
            if ((self.is_element_present("talent_button")) or
                    (self.is_element_present("user_part"))):
                logger.info("当前已处于登录状态")
                return True
            logger.info("未登录，开始自动登录流程")
            self.navigate_to_login()
            return self.perform_login()

        except Exception as e:
            logger.error(f"登录状态检查失败: {str(e)}")
            self.take_screenshot("登录状态异常")
            raise
