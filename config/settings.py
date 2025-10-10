

class Settings:
    # 环境配置：支持多个环境切换
    ENV = "dev"  # 默认使用测试环境
    # 不同环境的基础URL配置
    BASE_URL = {
        "production": "https://prod.example.com",  # 生产环境URL
        "staging": "https://staging.example.com",  # 预生产环境URL
        "dev": "https://test-admin.gsrtech.com/"  # 测试环境URL
    }
    URL = "https://test-admin.gsrtech.com/"

    # 浏览器配置
    BROWSER = "chrome"  # 默认浏览器：chrome/firefox/edge/safari
    HEADLESS = False  # 是否使用无头模式（不显示浏览器界面）
    WINDOW_SIZE = (1920, 1080)  # 浏览器窗口大小

    # 等待时间设置（秒）
    IMPLICIT_WAIT = 15  # 隐式等待全局超时
    EXPLICIT_WAIT = 30  # 显式等待最大超时

    # 测试用户凭证
    VALID_USER = {
        "username": "testuser@example.com",  # 有效用户名
        "password": "P@ssw0rd123"  # 有效密码
    }

    # API测试配置
    API_BASE_URL = "https://api.example.com/v1"  # API基础地址
    API_KEY = "your_api_key_here"  # API认证密钥

    # 报告和截图配置
    REPORT_PATH = "reports/"  # 测试报告保存路径
    SCREENSHOT_ON_FAILURE = True  # 失败时自动截图
    REPORT_ALLURE = "./reports/allure-results"
    CLEAN_HISTORY = True
    LOG_LEVEL = "INFO"
    LOG__FILE = "./report.log"
    SCREENSHOT_PATH = './reports/screenshots'

    # 文件位置
    TESTCASES = "./testcases/testcases.yaml"
    ELEMENT_LOCATORS = "./config/element_locators.yaml"
    PAGES = '.testcases/testcases.yaml'


settings = Settings()

# print(settings.BASE_URL[settings.ENV])
