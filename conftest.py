import pytest
from utils.browser import Browser
from utils.logger import logger
import allure
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def browser():
    """
    pytest session级fixture - 在整个测试会话期间只创建一次浏览器实例
    用于管理浏览器的生命周期
    """
    # 创建浏览器实例
    browser_manager = Browser()
    # 返回浏览器实例(不在此处获取driver)
    yield browser_manager
    # 测试会话结束后关闭浏览器
    browser_manager.quit_driver()
    logger.info("测试会话结束，浏览器已关闭")

@pytest.fixture(scope="function")
def driver(browser):
    """
    pytest 函数级fixture - 每个测试函数执行前获取driver
    :param browser: 浏览器管理实例
    """
    # 获取WebDriver实例
    driver = browser.get_driver()
    yield driver
    # 测试函数结束后清理cookies
    driver.delete_all_cookies()
    logger.info("已清除浏览器cookies")

@pytest.fixture(scope="function")
def login_page(driver):
    """
    pytest 函数级fixture - 为每个测试函数提供登录页面实例
    :param driver: WebDriver实例
    """
    # 创建登录页面实例
    return LoginPage(driver)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # call参数由框架传递
    """
    pytest钩子函数 - 用于获取测试结果并在失败时截图
    """
    # 执行测试并获取结果
    outcome = yield
    rep = outcome.get_result()

    # 检查是否是测试函数的调用阶段且测试失败
    if rep.when == "call" and rep.failed:
        # 获取driver实例(如果存在)
        driver = getattr(item.funcargs.get('driver'), 'driver', None)
        if driver:
            # 在失败时截图
            screenshot_name = f"failure_{rep.nodeid.replace('::', '_')}"
            try:
                # 使用Allure附加截图
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=screenshot_name,
                    attachment_type=allure.attachment_type.PNG
                )
                logger.info(f"测试失败，已截图: {screenshot_name}")
            except Exception as e:
                logger.error(f"截图失败: {str(e)}")
