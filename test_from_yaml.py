import pytest
import allure
# from pages.dashboard_page import DashboardPage
from utils.yaml_load import YamlLoad
from utils.executor import Executor
from pages.login_page import LoginPage
from utils.logger import logger


data_loader = YamlLoad()
test_cases = data_loader.load_test_cases()

@allure.feature("YAML驱动登录测试")
class TestLoginFromYAML:
    """从YAML文件加载的登录功能测试"""

    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self, driver):
        """测试类级别初始化"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        # self.dashboard_page = DashboardPage(driver)   # 导航页

        # 初始化测试执行器
        self.executor = Executor(driver)

        # 注册页面对象
        self.executor.register_page("login_page", self.login_page)
        # self.executor.register_page("dashboard_page", self.dashboard_page)    # 导航页

        # 导航到登录页面
        self.login_page.navigate_to_login()
        logger.info("测试类初始化完成")
        # board页面先验证登录成功
        # self.dashboard_page.verify_login_success()    # 导航页

        yield

    @pytest.mark.parametrize("test_case", [pytest.param(tc, id=tc['id']) for tc in test_cases])
    def test_login_scenarios(self, test_case):
        """
        参数化测试用例 - 从YAML文件加载测试场景
        :param test_case: 测试用例字典
        """
        # 设置Allure报告中的测试用例名称
        allure.dynamic.title(f"{test_case['id']} - {test_case['name']}")

        # 执行测试用例
        result = self.executor.execute_test_case(test_case)

        # 断言测试结果
        assert result, f"测试用例 {test_case['id']} 执行失败: {result}"
