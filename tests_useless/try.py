import os
import allure
# from selenium.common.exceptions import TimeoutException, InvalidArgumentException
# from selenium.webdriver.common.by import By


class FileUploadHelper:
    def __init__(self, base_page):
        """
        初始化文件上传助手
        :param base_page: 包含find_element方法的页面基类实例
        """
        self.base_page = base_page
        self.driver = base_page.driver  # 获取驱动实例

    # @allure.step("上传文件: {file_path} 到元素: {file_input_locator}")
    # def upload_file(self, file_input_locator, file_path, timeout=None):
    #     """
    #     使用已封装的find_element方法上传文件
    #     :param file_input_locator: 文件输入元素的定位器(元组格式, 如(By.ID, 'file_input'))
    #     :param file_path: 要上传的文件路径
    #     :param timeout: 自定义等待超时时间(可选)
    #     :return: Boolean 表示是否上传成功
    #     """
    #     # 记录操作信息
    #     allure.attach(f"上传文件: {file_path}", f"到元素: {file_input_locator}")
    #
    #     try:
    #         # 确保文件存在
    #         if not os.path.exists(file_path):
    #             error_msg = f"文件不存在: {file_path}"
    #             allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #             raise FileNotFoundError(error_msg)
    #
    #         # 获取文件的绝对路径（更可靠）
    #         absolute_path = os.path.abspath(file_path)
    #         allure.attach("文件绝对路径", absolute_path, allure.attachment_type.TEXT)
    #
    #         # 使用已封装的find_element方法查找文件输入元素
    #         file_input = self.base_page.find_element(file_input_locator, timeout)
    #
    #         # 确保元素是文件输入类型
    #         input_type = file_input.get_attribute("type")
    #         if input_type and input_type.lower() != "file":
    #             allure.attach("警告", f"元素类型不是'file'而是'{input_type}'", allure.attachment_type.TEXT)
    #
    #         # 发送文件路径
    #         file_input.send_keys(absolute_path)
    #
    #         # 验证文件是否已选择（可选）
    #         if file_input.get_attribute("value"):
    #             success_msg = f"成功上传文件: {absolute_path}"
    #             allure.attach("成功信息", success_msg, allure.attachment_type.TEXT)
    #             return True
    #         else:
    #             warning_msg = "文件输入框值为空，上传可能未成功"
    #             allure.attach("警告信息", warning_msg, allure.attachment_type.TEXT)
    #             return False
    #
    #     except FileNotFoundError as e:
    #         # 文件不存在异常
    #         error_msg = f"文件错误: {str(e)}"
    #         allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #         self.base_page.take_screenshot(f"file_not_found_{os.path.basename(file_path)}")
    #         raise
    #     except TimeoutException as e:
    #         # 元素查找超时异常
    #         error_msg = f"文件输入元素查找超时: {str(e)}"
    #         allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #         self.base_page.take_screenshot(f"file_input_timeout_{file_input_locator[0]}_{file_input_locator[1]}")
    #         raise
    #     except InvalidArgumentException as e:
    #         # 无效参数异常（可能是无效的文件路径格式）
    #         error_msg = f"无效的文件路径参数: {str(e)}"
    #         allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #         self.base_page.take_screenshot(f"invalid_file_argument_{os.path.basename(file_path)}")
    #         raise
    #     except Exception as e:
    #         # 其他未知异常
    #         error_msg = f"文件上传过程中发生未知错误: {str(e)}"
    #         allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #         self.base_page.take_screenshot(f"file_upload_error_{os.path.basename(file_path)}")
    #         raise

    @allure.step("上传多个文件: {file_paths} 到元素: {file_input_locator}")
    def upload_multiple_files(self, file_input_locator, file_paths, timeout=None):
        """
        上传多个文件到支持多文件上传的输入框
        :param file_input_locator: 文件输入元素的定位器
        :param file_paths: 要上传的文件路径列表
        :param timeout: 自定义等待超时时间(可选)
        :return: Boolean 表示是否所有文件都上传成功
        """
        # 记录操作信息
        allure.attach(f"上传多个文件: {', '.join(file_paths)}", f"到元素: {file_input_locator}")

        # 检查所有文件是否存在
        missing_files = [fp for fp in file_paths if not os.path.exists(fp)]
        if missing_files:
            error_msg = f"以下文件不存在: {', '.join(missing_files)}"
            allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
            raise FileNotFoundError(error_msg)

        try:
            # 使用已封装的find_element方法查找文件输入元素
            file_input = self.base_page.find_element(file_input_locator, timeout)

            # 构建文件路径字符串（多个文件用换行符分隔）
            file_paths_str = "\n".join([os.path.abspath(fp) for fp in file_paths])

            # 发送所有文件路径
            file_input.send_keys(file_paths_str)

            # 验证文件是否已选择
            if file_input.get_attribute("value"):
                success_msg = f"成功上传 {len(file_paths)} 个文件"
                allure.attach("成功信息", success_msg, allure.attachment_type.TEXT)
                return True
            else:
                warning_msg = "文件输入框值为空，上传可能未成功"
                allure.attach("警告信息", warning_msg, allure.attachment_type.TEXT)
                return False

        except Exception as e:
            error_msg = f"多文件上传过程中发生错误: {str(e)}"
            allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
            self.base_page.take_screenshot(f"multi_file_upload_error_{file_input_locator[0]}_{file_input_locator[1]}")
            raise

    # @allure.step("通过JavaScript上传文件: {file_path} 到隐藏元素: {file_input_locator}")
    # def upload_file_via_js(self, file_input_locator, file_path, timeout=None):
    #     """
    #     通过JavaScript上传文件到隐藏的文件输入元素
    #     :param file_input_locator: 文件输入元素的定位器
    #     :param file_path: 要上传的文件路径
    #     :param timeout: 自定义等待超时时间(可选)
    #     :return: Boolean 表示是否上传成功
    #     """
    #     # 记录操作信息
    #     allure.attach(f"通过JS上传文件: {file_path}", f"到隐藏元素: {file_input_locator}")
    #
    #     try:
    #         # 确保文件存在
    #         if not os.path.exists(file_path):
    #             error_msg = f"文件不存在: {file_path}"
    #             allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #             raise FileNotFoundError(error_msg)
    #
    #         # 获取文件的绝对路径
    #         absolute_path = os.path.abspath(file_path)
    #         allure.attach("文件绝对路径", absolute_path, allure.attachment_type.TEXT)
    #
    #         # 使用已封装的find_element方法查找文件输入元素
    #         file_input = self.base_page.find_element(file_input_locator, timeout)
    #
    #         # 使用JavaScript设置文件输入框的值并触发change事件
    #         script = """
    #         var element = arguments[0];
    #         var filePath = arguments[1];
    #
    #         // 创建一个新的File对象
    #         var file = new File([""], filePath);
    #
    #         // 创建一个DataTransfer对象并添加文件
    #         var dataTransfer = new DataTransfer();
    #         dataTransfer.items.add(file);
    #
    #         // 设置文件列表
    #         element.files = dataTransfer.files;
    #
    #         // 触发change事件
    #         var event = new Event('change', { bubbles: true });
    #         element.dispatchEvent(event);
    #
    #         return element.files.length > 0;
    #         """
    #
    #         # 执行JavaScript
    #         result = self.driver.execute_script(script, file_input, absolute_path)
    #
    #         if result:
    #             success_msg = f"通过JS成功上传文件: {absolute_path}"
    #             allure.attach("成功信息", success_msg, allure.attachment_type.TEXT)
    #             return True
    #         else:
    #             warning_msg = "通过JS上传文件可能未成功"
    #             allure.attach("警告信息", warning_msg, allure.attachment_type.TEXT)
    #             return False
    #
    #     except Exception as e:
    #         error_msg = f"通过JS上传文件过程中发生错误: {str(e)}"
    #         allure.attach("错误信息", error_msg, allure.attachment_type.TEXT)
    #         self.base_page.take_screenshot(f"js_file_upload_error_{file_input_locator[0]}_{file_input_locator[1]}")
    #         raise
