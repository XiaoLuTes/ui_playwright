from playwright.sync_api import sync_playwright
from utils.logger import logger
from config.settings import settings

class BrowserEngine:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self):
        self.playwright = sync_playwright().start()

        browser_type = settings.BROWSER.lower()
        headless = settings.HEADLESS
        slow_mo = settings.SLOW_MO

        if browser_type in ["chrome", "chromium"]:
            self.browser = self.playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
        elif browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(headless=headless, slow_mo=slow_mo)
        elif browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(headless=headless, slow_mo=slow_mo)
        else:
            raise Exception(f"不支持的浏览器: {browser_type}")

        self.context = self.browser.new_context(
            locale="zh-CN",
            viewport=settings.BROWSER_VIEWPORT
        )
        self.context.set_default_timeout(settings.IMPLICIT_WAIT * 1000)
        self.page = self.context.new_page()

        logger.info("Playwright 浏览器启动完成")
        return self.page

    def stop_browser(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Playwright 浏览器已关闭")
