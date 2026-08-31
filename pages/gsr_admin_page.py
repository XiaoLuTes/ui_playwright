import allure
import base64
import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage
from utils.logger import logger
from utils.captcha_ocr import solve as solve_captcha


class GsrAdminPage(BasePage):
    """管理端页面"""

    def __init__(self, page_name, page):
        super().__init__(page_name, page)

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

    @allure.step("OCR识别验证码")
    def _get_captcha_text(self):
        """从登录页抓取验证码图片并OCR识别，返回算式答案；失败返回 None"""
        try:
            img_loc = self.page.locator('img[alt="验证码"]').first
            img_loc.wait_for(state="visible", timeout=10000)
            src = img_loc.get_attribute("src")
            if not src or "," not in src:
                logger.error("验证码图片 src 无效")
                return None
            raw = base64.b64decode(src.split(",", 1)[1])
            return solve_captcha(raw)
        except Exception as e:
            logger.error(f"验证码OCR识别异常: {str(e)}")
            return None

    @allure.step("刷新验证码")
    def _refresh_captcha(self):
        """点击验证码图片刷新（OCR识别失败或登录被拒时）"""
        try:
            self.page.locator('img[alt="验证码"]').first.click(timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(1500)

    @allure.step("检查登录状态")
    def _is_logged_in(self, timeout=10000):
        """登录成功后页面跳转到系统选择页 /sys（wait_for_url 对已匹配 URL 立即返回）"""
        try:
            self.page.wait_for_url(re.compile(r"/sys"), timeout=timeout)
            return True
        except Exception:
            return False

    @allure.step("执行登录操作（OCR自动识别验证码）")
    def perform_login(self, max_retry=5):
        """输入账号密码 + OCR识别验证码登录，失败自动刷新验证码重试"""
        for attempt in range(1, max_retry + 1):
            try:
                # 输入账号
                self.input_text("username_input", self.settings.LOGIN_USER)
                # 输入密码
                self.input_text("password_input", self.settings.PASSWORD)
                # OCR 识别验证码
                captcha = self._get_captcha_text()
                if not captcha:
                    logger.warning(f"验证码识别失败，刷新重试（{attempt}/{max_retry}）")
                    self._refresh_captcha()
                    continue
                logger.info(f"验证码OCR识别结果: {captcha}")
                # 输入验证码
                self.input_text("code_input", captcha)
                # 点击登录
                self.element_click("login_button")
                # 检查登录成功
                if self._is_logged_in():
                    logger.info("登录成功")
                    return True
                logger.warning(f"登录失败（第{attempt}次，验证码可能识别错误），刷新重试")
                self.take_screenshot(f"登录失败-第{attempt}次")
                self._refresh_captcha()
            except Exception as e:
                logger.error(f"登录异常: {str(e)}")
                self.take_screenshot(f"登录异常-第{attempt}次")
                self._refresh_captcha()

        logger.error("多次登录尝试均失败")
        self.take_screenshot("登录最终失败")
        raise Exception("登录失败：多次尝试后验证码仍无法通过")

    @allure.step("确保已登录状态")
    def ensure_logged_in(self):
        try:
            self.open(self.settings.URL)
            # 已登录时打开管理端会跳转到 /sys；未登录则停留登录页（短超时，避免无效等待）
            if self._is_logged_in(timeout=5000):
                logger.info("当前已处于登录状态")
                return True
            logger.info("未登录，开始自动登录流程")
            self.navigate_to_login()
            return self.perform_login()

        except Exception as e:
            logger.error(f"登录状态检查失败: {str(e)}")
            self.take_screenshot("登录状态异常")
            raise
