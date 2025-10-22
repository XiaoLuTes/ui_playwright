# config/settings.py
import os
from typing import Dict, Any


class Settings:
    """支持环境变量覆盖的配置类"""

    def __init__(self):
        # 环境配置
        self.ENV = self._get_env_var("ENV", "dev")

        # 不同环境的基础URL配置
        self.BASE_URL = {
            "production": "https://admin.gsrtech.com/login",
            "staging": "https://stage-admin.gsrtech.com/",
            "dev": "https://test-admin.gsrtech.com/"
        }
        self.URL = self._get_env_var("URL", self.BASE_URL[self.ENV])

        # 浏览器配置
        self.BROWSER = self._get_env_var("BROWSER", "chrome")
        self.HEADLESS = self._get_env_var("HEADLESS", "False").lower() == "true"

        # 窗口大小处理
        window_size_str = self._get_env_var("WINDOW_SIZE", "1920,1080")
        self.WINDOW_SIZE = tuple(map(int, window_size_str.split(',')))

        # 等待时间设置
        self.IMPLICIT_WAIT = int(self._get_env_var("IMPLICIT_WAIT", "15"))
        self.EXPLICIT_WAIT = int(self._get_env_var("EXPLICIT_WAIT", "30"))

        # 测试用户凭证
        self.VALID_USER = {
            "username": self._get_env_var("VALID_USERNAME", "testuser@example.com"),
            "password": self._get_env_var("VALID_PASSWORD", "P@ssw0rd123")
        }

        # 报告和截图配置
        self.REPORT_PATH = self._get_env_var("REPORT_PATH", "reports/")
        self.SCREENSHOT_ON_FAILURE = self._get_env_var("SCREENSHOT_ON_FAILURE", "True").lower() == "true"
        self.REPORT_ALLURE = self._get_env_var("REPORT_ALLURE", "./reports/allure-results")
        self.CLEAN_HISTORY = self._get_env_var("CLEAN_HISTORY", "True").lower() == "true"
        self.LOG_LEVEL = self._get_env_var("LOG_LEVEL", "INFO")
        self.LOG_FILE = self._get_env_var("LOG_FILE", "./report.log")
        self.SCREENSHOT_PATH = self._get_env_var("SCREENSHOT_PATH", "./reports/screenshots")

        # 文件位置 - 可以通过Jenkins环境变量修改需要执行的测试用例文件
        self.TESTCASES = self._get_env_var("TESTCASES_PATH", "./testcases/pt/pt_testcases.yaml")
        self.ELEMENT_LOCATORS = self._get_env_var("ELEMENT_LOCATORS_PATH", "./config/element_locators.yaml")

        # 打印当前配置（用于调试）
        self._print_current_config()

    def _get_env_var(self, var_name: str, default: str) -> str:
        """从环境变量获取配置，如果没有则使用默认值"""
        return os.getenv(var_name, default)

    def _print_current_config(self):
        """打印当前配置（用于调试）"""
        print("=" * 50)
        print("当前测试配置:")
        print(f"环境: {self.ENV}")
        print(f"测试用例文件: {self.TESTCASES}")
        print(f"元素定位器文件: {self.ELEMENT_LOCATORS}")
        print(f"基础URL: {self.URL}")
        print(f"浏览器: {self.BROWSER}, 无头模式: {self.HEADLESS}")
        print("=" * 50)


settings = Settings()
