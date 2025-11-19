import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager
from config.settings import Settings
from utils.logger import logger


class Browser:
    """
    浏览器管理类 - 负责浏览器的初始化和销毁
    支持多种浏览器和配置选项
    """

    def __init__(self):
        # 获取配置实例
        # self.config = ConfigReader()
        self.settings = Settings()
        # WebDriver实例占位符
        self.driver = None

    def get_driver(self):
        if self.driver is not None:
            return self.driver
        browser_name = self.settings.BROWSER
        headless = self.settings.HEADLESS
        logger.info(f"正在初始化浏览器: {browser_name}, 无头模式: {headless}")
        # 根据浏览器类型创建不同的驱动
        if browser_name == "chrome":
            # 配置Chrome选项
            chrome_options = webdriver.ChromeOptions()
            if headless:
                chrome_options.add_argument("--headless=new")  # 新版无头模式
            chrome_options.add_argument("--no-sandbox")  # 禁用沙箱
            chrome_options.add_argument("--disable-dev-shm-usage")  # 禁用/dev/shm使用

            driver_path = self._get_chrome_driver_path()
            logger.info(f"使用本地ChromeDriver: {driver_path}")

            self.driver = webdriver.Chrome(
                service=ChromeService(driver_path),
                options=chrome_options
            )

            # 使用WebDriver Manager自动管理驱动程序
            # logger.info(f"正在配置webdriver-chrome")
            # self.driver = webdriver.Chrome(
            #     service=ChromeService(ChromeDriverManager().install()),
            #     options=chrome_options
            # )
        # elif browser_name == "firefox":
        #     # 配置Firefox选项
        #     firefox_options = webdriver.FirefoxOptions()
        #     if headless:
        #         firefox_options.add_argument("--headless")

            # 使用WebDriver Manager自动管理驱动程序
            # logger.info(f"正在配置webdriver-firefox")
            # self.driver = webdriver.Firefox(
            #     service=FirefoxService(GeckoDriverManager().install()),
            #     options=firefox_options
            # )
        else:
            # 不支持的浏览器类型抛出异常
            raise ValueError(f"不支持的浏览器类型: {browser_name}")

        # 配置浏览器超时设置
        # self.driver.implicitly_wait(self.settings.IMPLICIT_WAIT)  # 隐式超时
        self.driver.set_page_load_timeout(self.settings.EXPLICIT_WAIT)  # 显式超时
        # 设置浏览器窗口大小
        (width, height) = self.settings.WINDOW_SIZE
        logger.info(f"设置浏览器窗口大小为{width}x{height}")
        self.driver.set_window_size(width, height)
        logger.info(f"浏览器初始化完成: {browser_name}")
        return self.driver

    def quit_driver(self):
        """关闭浏览器并退出驱动"""
        if self.driver:
            logger.info("正在关闭浏览器...")
            try:
                self.driver.quit()
                logger.info("浏览器已成功关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错: {str(e)}")
            finally:
                self.driver = None

    @staticmethod
    def _get_chrome_driver_path():
        """获取ChromeDriver路径"""
        # 检查项目内的drivers目录
        project_driver_path = "./drivers/chromedriver-win64/chromedriver.exe"  # Windows
        if os.path.exists(project_driver_path):
            return project_driver_path

        project_driver_path = "./drivers/chromedriver/chromedriver"  # Linux/Mac
        if os.path.exists(project_driver_path):
            return project_driver_path

        # 检查系统PATH
        import shutil
        if shutil.which("chromedriver"):
            return "chromedriver"

        raise FileNotFoundError(
            "未找到ChromeDriver。请运行 get_drivers.py 或手动下载驱动。"
        )

# Browser().get_driver()
