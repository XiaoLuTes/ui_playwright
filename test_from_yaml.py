import pytest
import allure
from utils.logger import logger
from utils.page_manager import PageManager
from utils.yaml_load import YamlLoad
from utils.executor import Executor

data_loader = YamlLoad()
test_cases = data_loader.load_test_cases()


@allure.feature("YAML驱动登录测试")
class TestLoginFromYAML:
    """从YAML文件加载的登录功能测试"""

    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self, driver):
        """测试类级别初始化"""
        self.driver = driver
        self.page_manager = PageManager(driver)
        self.executor = Executor(driver, self.page_manager)

        # 初始化所有页面
        project_pages = self.page_manager.initialize_project_pages()
        logger.info(f"初始化完成，已注册页面: {list(project_pages.keys())}")

        self.try_login()

        yield

    @pytest.mark.parametrize("test_case", [pytest.param(tc, id=str(tc['id'])) for tc in test_cases])
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

    def try_login(self):
        """尝试登陆"""
        try:
            login_page = self.page_manager.get_page("gsr_admin_page")
            if hasattr(login_page, 'perform_login'):
                # 导航到登录页面
                self.page_manager.navigate_to_page("gsr_admin_page")
                # 执行登录
                login_page.perform_login()
        except Exception as e:
            # 如果是其他页面，跳过登录
            if "gsr_admin_page" not in self.page_manager.pages:
                logger.info("当前项目不需要登录，跳过登录步骤")
                return
            if hasattr(self, 'driver'):
                from pages.base_page import BasePage
                BasePage("error", self.driver).take_screenshot("登录失败")
            pytest.fail(f"登录失败: 测试中止{str(e)}")
