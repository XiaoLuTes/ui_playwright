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
        project_pages = self.page_manager.initialize_project_pages()
        logger.info(f"初始化完成，已注册页面: {list(project_pages.keys())}")

        # self.try_login()

        yield

    @pytest.mark.parametrize("test_case", [pytest.param(tc, id=str(tc['id'])) for tc in test_cases])
    def test_login_scenarios(self, test_case):
        """
        参数化测试用例 - 从YAML文件加载测试场景
        :param test_case: 测试用例字典
        """
        # 设置Allure报告中的测试用例名称
        allure.dynamic.title(f"{test_case['id']} - {test_case['name']}")
        result = self.executor.execute_test_case(test_case)
        assert result, f"测试用例 {test_case['id']} 执行失败: {result}"
