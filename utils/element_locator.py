from config.settings import settings
from utils.logger import logger
from utils.common import read_yaml


class ElementLocator:
    """元素定位器管理类"""

    def __init__(self):
        self.setting = settings
        self.locators = self.load_locators()

    def load_locators(self):
        """加载元素定位器"""
        file_path = self.setting.ELEMENT_LOCATORS
        try:
            data = read_yaml(file_path)
            return data
        except Exception as e:
            logger.error(f"加载元素定位器失败: {str(e)}")
            return {}

    def get_locator(self, page_name_str, element_name):
        """获取元素定位器"""
        try:
            locator_info = self.locators[page_name_str][element_name]
            return [locator_info['by'], locator_info['value']]
        except KeyError:
            logger.error(f"未找到元素定位器: {page_name_str}.{element_name}")
            raise

    def get_all_page_locators(self, page_name):
        """获取指定页面的所有元素定位器"""
        try:
            return self.locators[page_name]
        except KeyError:
            logger.error(f"未找到页面定位器: {page_name}")
            return {}
