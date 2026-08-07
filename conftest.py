import pytest
from utils.browser import BrowserEngine

@pytest.fixture(scope="session")
def browser():
    engine = BrowserEngine()
    page = engine.start_browser()
    yield page
    engine.stop_browser()
