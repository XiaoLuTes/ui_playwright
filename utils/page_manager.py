from utils.logger import logger
from config.settings import settings
import importlib
from utils.windows_Switch_Helper import WindowSwitchHelper


class PageManager:
    """页面对象管理器 - 动态管理多个页面对象"""

    def __init__(self, driver):
        self.driver = driver
        self.pages = {}
        self.settings = settings

    def register_page(self, page_name, page_class=None):
        """注册页面对象"""
        if page_class is None:
            # 动态导入页面类
            page_class = self.import_page_class(page_name)
        if page_class:
            page_instance = page_class(page_name, self.driver)
            if hasattr(page_instance, 'set_page_manager'):
                page_instance.set_page_manager(self)
            self.pages[page_name] = page_instance
            logger.info(f"注册页面对象: {page_name}")
            return page_instance
        else:
            from pages.base_page import BasePage
            page_instance = BasePage(page_name, self.driver)
        self.pages[page_name] = page_instance
        logger.info(f"注册页面对象: {page_name}")
        return page_instance

    def import_page_class(self, page_name):
        """动态导入页面类"""
        try:
            class_mapping = settings.PAGE_CLASSES
            class_name = class_mapping.get(page_name)
            if not class_name:
                return None
            module_path = f"pages.{page_name}"
            module = importlib.import_module(module_path)
            page_class = getattr(module, class_name)
            return page_class
        except Exception as e:
            logger.error(f"导入页面类失败 {page_name}: {str(e)}")
            return None

    def get_page(self, page_name):
        """获取页面对象"""
        if page_name in self.pages:
            return self.pages[page_name]
        else:
            logger.warning(f"页面对象未注册: {page_name}, 尝试动态注册")
            return self.register_page(page_name)

    def initialize_project_pages(self, project_name=None):
        """初始化指定项目的所有页面"""
        if project_name is None:
            project_name = self.settings.CURRENT_PROJECT

        project_config = self.settings.PROJECT_CONFIG
        page_list = project_config.get("PAGE_NAME", [])

        for page_name in page_list:
            self.register_page(page_name)

        logger.info(f"已为项目'{project_name}'注册 {len(page_list)} 个页面对象")
        return self.pages

    def navigate_to_page(self, page_name):
        """导航到指定页面"""
        page_url = self.settings.PAGE_URLS.get(page_name)
        if page_url:
            page_obj = self.get_page(page_name)
            if page_name == "gsr_admin_page":
                page_obj.ensure_logged_in()
                WindowSwitchHelper.switch_to_window_by_url(page_obj, page_url)
            else:
                from pages.base_page import BasePage
                base_page = BasePage(page_name, self.driver)
                base_page.open(page_url)
                WindowSwitchHelper.switch_to_window_by_url(page_obj, page_url)
            return True
        else:
            logger.error(f"未找到页面 {page_name} 的URL配置")
            return False

    def get_page_manager(self):
        """获取页面管理器"""
        return self
