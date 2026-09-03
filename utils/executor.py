import time
from utils.logger import logger
import allure
from utils.element_locator import ElementLocator
from utils.page_manager import PageManager
from utils.yaml_load import YamlLoad
from config.settings import settings
from utils.common import VariableStore
import json


class Executor:
    def __init__(self, page, page_manager=None):
        self.test_result = None
        self.page = page  # 这里从 driver 改成 playwright page 对象
        self.data_loader = ElementLocator()
        self.locators = self.data_loader.load_locators()
        self.page_manager = PageManager(page)
        self.yaml_load = YamlLoad()
        self.settings = settings
        self.page_name = None
        self._db_utils = None

        if page_manager is not None:
            self.page_manager = page_manager
            logger.info("执行器使用外部页面管理器")
        else:
            self.page_manager = PageManager(page)
            logger.info("执行器创建新的页面管理器")

    def _ensure_database_connection(self):
        """确保数据库连接建立"""
        if self._db_utils is None:
            from utils.database import DatabaseUtils
            logger.info("创建数据库连接")
            self._db_utils = DatabaseUtils()
            self._db_utils.connect()

            for page_name, page in self.page_manager.pages.items():
                page.set_db_utils(self._db_utils)
                logger.info(f"设置数据库连接到页面: {page_name}")

    def _close_database_connection(self):
        """关闭数据库连接"""
        if self._db_utils:
            try:
                self._db_utils.database_close()
            except Exception as e:
                logger.warning(f"关闭数据库连接错误: {e}")
            finally:
                self._db_utils = None

            for page_name, page in self.page_manager.pages.items():
                page.set_db_utils(None)
        else:
            logger.info("未建立数据库链接，无需关闭")

    def register_page(self, page_name, page_object=None):
        """注册页面对象"""
        if page_object:
            self.page_manager.pages[page_name] = page_object
        else:
            self.page_manager.register_page(page_name)

        if self._db_utils and page_object:
            page_object.set_db_utils(self._db_utils)
            logger.info("注册数据库对象到页面")

    def execute_test_case(self, test_case):
        """
        执行单个测试用例
        """
        test_case_page = test_case['page']
        page_object = self.page_manager.get_page(test_case_page)

        if not page_object:
            raise Exception(f"未注册页面对象: {test_case_page}")

        test_case_id = test_case['id']
        test_case_name = test_case['name']
        logger.info(f"开始执行测试用例: {test_case_id} - {test_case_name}")

        try:
            if test_case_page:
                logger.info(f"导航到页面: {test_case_page}")
                if not self.page_manager.navigate_to_page(test_case_page):
                    raise Exception(f"无法导航到指定页面: {test_case_page}")
            else:
                logger.info(f"使用默认页面: {self.settings.DEFAULT_PAGE_NAME}")
                self.page_manager.navigate_to_page(self.settings.DEFAULT_PAGE_NAME)

            # 执行步骤
            for step in test_case['steps']:
                step_name = step['step_name']
                element_name = step['element']
                action = step['action']
                data = step.get('data', '')
                expected = step.get('expected', '')

                with allure.step(f"步骤：{step_name}"):
                    self.execute_step(page_object, step_name, element_name, action, data, expected)

            self.yaml_load.update_test_result(test_case_id, "通过")
            logger.info(f"测试用例执行通过: {test_case_id}")
            return True

        except Exception as e:
            error_msg = str(e)
            self.yaml_load.update_test_result(test_case_id, f"失败: {error_msg}")
            logger.error(f"测试用例执行失败: {test_case_id} | {error_msg}")
            return False

        finally:
            self._close_database_connection()
            logger.info(f"测试用例 {test_case_id} 执行完成")

    def execute_step(self, page_object, step_name, element_name, action, data, expected):
        """执行测试步骤"""
        # 运行时变量替换
        data = VariableStore.render(data)
        expected = VariableStore.render(expected)
        with allure.step("步骤参数"):
            parameters = {
                'element_name': element_name,
                'action': action,
                'data': data,
                'expected': expected
            }
            allure.attach(str(parameters), "步骤参数", allure.attachment_type.TEXT)

        logger.info(f"执行步骤: {step_name} | 动作: {action}")

        # ====================== 标准动作（Playwright 自动等待）======================
        if action == "input":
            page_object.input_text(element_name, data)
            if expected:
                actual_value = page_object.get_element_value(element_name, screenshot_on_error=True)
                if str(data) not in actual_value:
                    page_object.take_screenshot(f"{element_name}_文本检查失败")
                    raise Exception(f"输入验证失败：预期'{data}'，实际'{actual_value}'")

        elif action == "click":
            page_object.element_click(element_name)

        elif action == "check_text":
            actual_text = page_object.get_text(element_name, screenshot_on_error=True)
            if str(data) not in actual_text:  # 包含内容即可，并非==
                page_object.take_screenshot(f"{element_name}_文本检查失败")
                raise Exception(f"文本不匹配：预期包含'{data}'，实际'{actual_text}'")

        elif action == "check_value":
            actual_value = page_object.get_element_value(element_name, screenshot_on_error=True)
            if str(data) not in actual_value:
                page_object.take_screenshot(f"{element_name}_文本检查失败")
                raise Exception(f"输入验证失败：预期'{data}'，实际'{actual_value}'")

        elif action == "save_text":
            # 保存元素文本为变量（data 字段是变量名）
            value = page_object.get_text(element_name, screenshot_on_error=True)
            VariableStore.set_variable(data, value)
            logger.info(f"已保存文本变量 [{data}] = {value}")

        elif action == "save_value":
            # 保存元素值（表单元素）为变量（data 字段是变量名）
            value = page_object.get_element_value(element_name, screenshot_on_error=True)
            VariableStore.set_variable(data, value)
            logger.info(f"已保存值变量 [{data}] = {value}")

        elif action == "down":
            page_object.keyboard_down(data)

        elif action == "up":
            page_object.keyboard_up(data)

        elif action == "enter":
            page_object.keyboard_enter()

        elif action == "check_exists":
            exists = page_object.is_element_present(element_name)
            if data == "存在" and not exists:
                page_object.take_screenshot(f"{element_name}_不存在")
                raise Exception(f"元素应存在但未找到: {element_name}")
            elif data == "不存在" and exists:
                raise Exception(f"元素应不存在但找到: {element_name}")

        elif action == "wait_exists":
            page_object.wait_for_element_appear(element_name)

        elif action == "download":
            # data = 保存的文件名（如 template.xlsx），下载到 reports/downloads
            save_path = page_object.download_file(element_name, data)
            # 路径存入变量，变量名取data(最终: data:save_path)
            VariableStore.set_variable(data, save_path)
            logger.info(f"下载完成并记录路径: {save_path}")

        elif action == "edit_excel":
            # data = 文件路径（变量引用或直接路径）；expected = 填写配置 JSON
            cfg = json.loads(expected)
            # 防止data未被替换变量
            file_path = VariableStore.get_variable(data, data)
            edit_path = page_object.edit_excel(file_path, cfg)
            logger.info(f"Excel编辑完成: {edit_path}")

        elif action == "upload":
            page_object.upload_file(element_name, data)

        elif action == "wait":
            time.sleep(int(data))

        elif action == "screenshot":
            name = data or step_name
            page_object.take_screenshot(name)

        elif action == "wait_text":
            page_object.wait_for_element_value(element_name, "text", data)

        elif action == "wait_value":
            page_object.wait_for_element_value(element_name, "value", data)

        elif action == "sql":
            self._ensure_database_connection()
            page_object.verify_mysql_data(data, expected)

        elif action == "sql_update":
            self._ensure_database_connection()
            result = page_object.execute_mysql_update(data)
            if expected and str(result) != expected:
                raise AssertionError(f"SQL行数不匹配 预期:{expected} 实际:{result}")

        # ====================== Flutter/坐标动作（保留兼容）======================
        # elif action == "flutter_click":
        #     page_object.click_by_relative_coordinates(element_name)
        #
        # elif action == "flutter_input":
        #     page_object.input_text_by_coordinates(element_name, data)
        #
        # elif action == "flutter_upload":
        #     page_object.upload_file_by_coordinates(element_name, data)
        #
        # elif action == "flutter_drag":
        #     page_object.drag_and_drop(element_name, data)

        else:
            raise Exception(f"不支持的操作类型: {action}")
