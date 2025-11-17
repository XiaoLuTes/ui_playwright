import pytest
from utils.browser import Browser
from utils.logger import logger


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
    browser_manager.quit_driver()
    logger.info("测试会话结束，浏览器已关闭")

@pytest.fixture(scope="session")
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
