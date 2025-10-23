import os


class Settings:
    """支持环境变量覆盖的配置类"""

    def __init__(self):
        # 环境配置
        self.ENV = self._get_env_var("ENV", "测试环境")

        # 不同环境的基础URL配置
        self.BASE_URL = {
            "生产环境": "https://admin.gsrtech.com",
            "预生产环境": "https://stage-admin.gsrtech.com/",
            "测试环境": "https://test-admin.gsrtech.com/"
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

        # 报告和截图配置
        self.REPORT_PATH = self._get_env_var("REPORT_PATH", "reports/")
        self.SCREENSHOT_ON_FAILURE = self._get_env_var("SCREENSHOT_ON_FAILURE", "True").lower() == "true"
        self.REPORT_ALLURE = self._get_env_var("REPORT_ALLURE", "./reports/allure-results")
        self.CLEAN_HISTORY = self._get_env_var("CLEAN_HISTORY", "True").lower() == "true"
        self.LOG_LEVEL = self._get_env_var("LOG_LEVEL", "INFO")
        self.LOG_FILE = self._get_env_var("LOG_FILE", "./report.log")
        self.SCREENSHOT_PATH = self._get_env_var("SCREENSHOT_PATH", "./reports/screenshots")

        # 项目管理
        self.PROJECT_CONFIGS = {
            "招聘平台新建岗位": {
                "PAGE_NAME": "pt_new_position",
                "TESTCASES_PATH": "./testcases/pt_new_position/pt_testcases.yaml",
                "ELEMENT_LOCATORS": "./config/locators/new_position_element_locators.yaml",
                "description": "招聘平台非eor岗位全流程"
            },
            "招聘平台新建编制": {
                "PAGE_NAME": "pt_new_preparation",
                "TESTCASES_PATH": "./testcases/pt_new_preparation/new_preparation.yaml",
                "ELEMENT_LOCATORS": "./config/locators/new_preparation_element_locators.yaml",
                "description": "招聘平台新发起编制流程"
            }
        }
        # 获取当前项目
        self.project_name = self._get_env_var("PROJECT_NAME", '招聘平台新建岗位')
        # 获取当前项目配置
        self.project_config = self.get_current_project_config(self.project_name)
        # 测试用例文件位置(根据项目获取)
        self.TESTCASES = self.project_config["TESTCASES_PATH"]
        # 页面名称(根据项目获取)
        self.PAGE_NAME = self.project_config["PAGE_NAME"]
        # 元素定位器地址
        self.ELEMENT_LOCATORS = self.project_config["ELEMENT_LOCATORS"]

        # 打印当前配置（用于调试）
        # self._print_current_config()

    def _get_env_var(self, var_name: str, default: str) -> str:
        """从环境变量获取配置，如果没有则使用默认值"""
        return os.getenv(var_name, default)

    def get_current_project_config(self, project_name):
        default_project = "招聘平台新建岗位"
        if project_name in self.PROJECT_CONFIGS:
            return self.PROJECT_CONFIGS[project_name]
        else:
            return self.PROJECT_CONFIGS[default_project]

    def get_available_projects(self):
        """获取所有可用项目列表"""
        return list(self.PROJECT_CONFIGS.keys())

    # def _print_current_config(self):
    #     """打印当前配置"""
    #     print("=" * 50)
    #     print("当前测试配置:")
    #     print(f"环境: {self.ENV}")
    #     print(f"测试项目：{self.project_name}")
    #     print(f"测试用例文件: {self.TESTCASES}")
    #     print(f"元素定位器文件: {self.ELEMENT_LOCATORS}")
    #     print(f"基础URL: {self.URL}")
    #     print(f"浏览器: {self.BROWSER}, 无头模式: {self.HEADLESS}")
    #     print("=" * 50)


settings = Settings()
