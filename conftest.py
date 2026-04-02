import pytest
from playwright.sync_api import sync_playwright
from config.settings import settings

@pytest.fixture(scope="session")
def browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=settings.HEADLESS,  # 无头模式
        slow_mo=settings.SLOW_MO  # 单次操作延迟
    )
    context = browser.new_context()

    page = context.new_page()
    page.set_default_timeout(settings.IMPLICIT_WAIT)  # 设置超时时间
    page.set_viewport_size(settings.BROWSER_VIEWPORT)  # 设置分辨率

    yield page

    context.close()
    browser.close()
    playwright.stop()
