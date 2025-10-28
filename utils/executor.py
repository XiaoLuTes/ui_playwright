import time
from conftest import driver
from utils.logger import logger
import allure
from utils.element_locator import ElementLocator
from utils.yaml_load import YamlLoad
from pages.base_page import BasePage


class Executor:
    def __init__(self, driver):
        self.test_result = None  # 用于写入测试结果
        self.driver = driver  # 实例主体
        self.data_loader = ElementLocator()
        self.locators = self.data_loader.load_locators()    # 用于页面元素定位器引用
        self.base_page = BasePage(self, driver)        # 引用页面操作
        self.page_mapping = {}  # 用于注册页面对象
        self.yaml_load = YamlLoad()   # 用于yaml用例引用
        self.page_name = None
        self._db_utils = None  # 数据库工具

    def _ensure_database_connection(self):
        """确保数据库连接建立"""
        if self._db_utils is None:
            from utils.database import DatabaseUtils
            logger.info("创建数据库连接")
            self._db_utils = DatabaseUtils()
            self._db_utils.connect()

            # 设置到所有已注册的页面
            for page_name, page in self.page_mapping.items():
                page.set_db_utils(self._db_utils)
                logger.debug(f"设置数据库连接到页面: {page_name}")

    def _close_database_connection(self):
        """关闭数据库连接"""
        if self._db_utils:
            try:
                self._db_utils.close()
            except Exception as e:
                logger.warning(f"关闭数据库连接时发生错误: {e}")
            finally:
                self._db_utils = None
            # 清除所有页面的数据库引用
            for page_name, page in self.page_mapping.items():
                page.set_db_utils(None)

    def register_page(self, page_name, page_object):
        """注册页面对象"""
        self.page_mapping[page_name] = page_object
        logger.info(f"注册页面对象: {page_name}")
        if self._db_utils:
            page_object.set_db_utils(self._db_utils)
            logger.info(f"注册数据库对象")

    def execute_test_case(self, test_case):
        """
        执行单个测试用例
        :param test_case: 测试用例字典
        :return: 执行结果 (True/False)
        """
        page_object = None
        test_case_id = test_case['id']
        test_case_name = test_case['name']

        logger.info(f"开始执行测试用例: {test_case_id} - {test_case_name}")

        try:
            # 执行测试步骤
            for step in test_case['steps']:
                step_name = step['step_name']
                element_name = step['element']
                action = step['action']
                data = step.get('data', '')
                expected = step.get('expected', '')

                # 查找元素所在的页面
                if element_name is not None:
                    page_name = self.find_element_page(element_name)
                    if not page_name:
                        raise Exception(f"找不到元素 {element_name} 对应的页面")

                # 获取页面对象
                    page_object = self.page_mapping.get(page_name)
                    if not page_object:
                        raise Exception(f"未注册页面对象: {page_name}")

                # 执行步骤
                with allure.step(f"步骤{step_name}"):
                    # , {element_name} - {action}: {data}
                    self.execute_step(page_object, step_name, element_name, action, data, expected)

            # 测试结果为通过
            self.yaml_load.update_test_result(test_case_id, "通过")
            logger.info(f"测试用例执行通过: {test_case_id}")
            return True

        except Exception as e:
            # 测试结果为失败
            error_msg = str(e)
            self.yaml_load.update_test_result(test_case_id, f"失败: {error_msg}")
            logger.error(f"测试用例执行失败: {test_case_id} - {error_msg}")
            return False
        finally:
            self._close_database_connection()
            logger.info(f"测试用例:{test_case_id}执行完成")

    def execute_step(self, page_object, step_name, element_name, action, data, expected):
        """执行单个测试步骤"""
        # time.sleep(1)   # 等待1秒
        with allure.step("步骤参数"):
            # 记录步骤参数作为附件
            parameters = {
                'element_name': element_name,
                'action': action,
                'data': data,
                'expected': expected
            }
            allure.attach(
                str(parameters),
                "步骤参数",
                allure.attachment_type.TEXT
            )
        logger.info(f"执行步骤: {step_name}")
        if action == "input":
            page_object.input_text(element_name, data)
            if expected:
                actual_value = page_object.get_element_value(element_name)
                data_str = str(data)
                if data_str not in actual_value:
                    raise Exception(f"步骤'{step_name}'输入验证失败: 预期包含 '{data_str}', 实际: '{actual_value}'")

        elif action == "click":
            page_object.element_click(element_name)

        elif action == "check_text":
            actual_text = page_object.get_text(element_name)
            data_str = str(data)
            if data_str not in actual_text:
                raise Exception(f"文本检查失败: 步骤'{step_name}'预期包含 '{data_str}', 实际: '{actual_text}'")

        elif action == "down":
            page_object.keyboard_down(data)

        elif action == "up":
            page_object.keyboard_up(data)

        elif action == "enter":
            page_object.keyboard_enter()

        elif action == "check_exists":
            exists = page_object.is_element_present(element_name)
            if data == "存在" and not exists:
                raise Exception(f"步骤'{step_name}'校验失败, {element_name}元素应存在,实际不存在")
            elif data == "不存在" and exists:
                raise Exception(f"步骤'{step_name}'校验失败: {element_name}元素应不存在,实际存在")
            elif data == "不存在" and not exists:
                logger.info(f"步骤'{step_name}'校验成功: {element_name}元素不存在")
            elif data == "存在" and exists:
                logger.info(f"步骤'{step_name}'校验成功: {element_name}元素存在")
            else:
                raise Exception(f"无法识别, 步骤：{step_name}, 判断：{data}, 应为'存在'or'不存在'")

        elif action == "upload":
            page_object.upload_file(element_name, data)

        elif action == "wait":
            time.sleep(int(data))

        elif action == "screenshot":
            screenshot_name = data if data is not None else step_name
            page_object.take_screenshot(screenshot_name)

        elif action == "wait_text":
            page_object.wait_for_element_value(element_name, "text", data)

        elif action == "wait_value":
            page_object.wait_for_element_value(element_name, "value", data)

        elif action == "sql":
            # 遇到mysql步骤时，确保数据库连接已建立
            self._ensure_database_connection()
            page_object.verify_mysql_data(data, expected)

        elif action == "sql_update":
            # 遇到mysql_update步骤时，确保数据库连接已建立
            self._ensure_database_connection()
            result = page_object.execute_mysql_update(data)
            if expected and str(result) != expected:
                raise AssertionError(f"数据库更新影响行数不匹配，期望: {expected}, 实际: {result}")

        else:
            raise Exception(f"步骤'{step_name}'不支持的操作类型: {action}")

    def find_element_page(self, element_name):
        """查找元素所在的页面"""
        for page_name, elements in self.locators.items():
            if element_name in elements:
                return page_name
        return None
