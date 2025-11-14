import time
import os
import pyautogui
from pages.base_page import BasePage
from utils.logger import logger
import allure


class FlutterPage(BasePage):
    """
    Flutter应用页面对象 - 完全基于坐标操作
    继承自BasePage，专门用于处理无法通过元素定位的Flutter应用
    """

    def __init__(self, page_name, driver):
        """初始化Flutter页面"""
        super().__init__(page_name, driver)
        # 获取屏幕尺寸
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"屏幕分辨率: {self.screen_width}x{self.screen_height}")

    def click_by_coordinates(self, abs_x, abs_y, click_duration=0.1):
        """
        基于绝对坐标进行点击
        Args:
            abs_x: X坐标
            abs_y: Y坐标
            click_duration: 点击持续时间（秒），默认0.1秒
        """
        try:
            # 验证坐标是否在屏幕范围内
            if not (0 <= abs_x <= self.screen_width and 0 <= abs_y <= self.screen_height):
                error_msg = f"坐标超出屏幕范围: ({abs_x}, {abs_y}), 屏幕尺寸: {self.screen_width}x{self.screen_height}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"准备点击坐标: ({abs_x}, {abs_y})")
            # 使用pyautogui进行精确坐标点击
            pyautogui.click(x=abs_x, y=abs_y, duration=click_duration)
            logger.info(f"坐标点击成功: ({abs_x}, {abs_y})")
            time.sleep(0.5)  # 点击后短暂等待
            return True

        except Exception as e:
            error_msg = f"坐标点击失败: ({abs_x}, {abs_y}), 错误: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot(f"坐标点击失败-{abs_x}-{abs_y}")
            raise

    @allure.step("基于相对坐标点击: (element_name)")
    def click_by_relative_coordinates(self, element_name):
        """
        基于相对坐标进行点击（百分比）
        Args:
            element_name: 元素名称（获取x，y轴）
        """
        abs_x, abs_y = self.get_element_xy(element_name)  # 获取相对百分比
        return self.click_by_coordinates(abs_x, abs_y)

    @allure.step("基于相对坐标输入文本: (element_name) -> {text}")
    def input_text_by_coordinates(self, element_name, text, clear_first=True):
        """
        基于相对坐标进行文本输入
        Args:
            element_name:
            text: 要输入的文本
            clear_first: 是否先清空输入框，默认True
        """
        abs_x, abs_y = self.get_element_xy(element_name)
        try:

            # 先点击输入框
            self.click_by_coordinates(abs_x, abs_y)
            time.sleep(0.5)  # 等待输入框激活

            if clear_first:
                logger.info("清空输入框内容")
                pyautogui.hotkey('ctrl', 'a')  # Windows/Linux
                # pyautogui.hotkey('command', 'a')  # mac
                time.sleep(0.2)
                pyautogui.press('delete')
                time.sleep(0.4)

            # 输入文本
            logger.info(f"输入文本: {text}")
            pyautogui.write(text, interval=0.05)  # 每个字符间隔0.05秒
            logger.info(f"坐标输入成功: ({abs_x}, {abs_y}) - 文本: {text}")
            return True

        except Exception as e:
            error_msg = f"坐标输入失败: ({abs_x}, {abs_y}), 文本: {text}, 错误: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot(f"坐标输入失败-{abs_x}-{abs_y}")
            raise

    @allure.step("点击坐标后选择文件上传: ({x}, {y}) -> {file_path}")
    def upload_file_by_coordinates(self, element_name, file_path, wait_after_click=2):
        """
        基于相对坐标点击后选择文件上传
        Args:
            element_name: 元素（获取坐标）
            file_path: 要上传的文件路径
            wait_after_click: 点击后等待时间，默认2秒
        """
        abs_x, abs_y = self.get_element_xy(element_name)
        try:
            # 确保文件存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            # 获取文件的绝对路径
            absolute_path = os.path.abspath(file_path)
            logger.info(f"准备上传文件: {absolute_path}")
            self.click_by_coordinates(abs_x, abs_y)
            logger.info(f"已点击坐标 ({abs_x}, {abs_y}) 触发文件选择对话框")
            # 等待文件选择对话框打开
            time.sleep(wait_after_click)
            # 输入文件路径
            logger.info("在文件选择对话框中输入文件路径")
            pyautogui.write(absolute_path, interval=0.05)
            time.sleep(0.5)
            # 按回车确认选择
            pyautogui.press('enter')
            logger.info("按Enter键确认文件选择")
            time.sleep(3)
            logger.info(f"文件上传成功: {file_path}")
            return True

        except FileNotFoundError as e:
            error_msg = f"文件错误: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot(f"文件不存在_{os.path.basename(file_path)}")
            raise
        except Exception as e:
            error_msg = f"文件上传失败: ({abs_x}, {abs_y}), 文件: {file_path}, 错误: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot(f"文件上传失败-{abs_x}-{abs_y}")
            raise

    @allure.step("拖拽操作: 从({start_element})到({end_element})")
    def drag_and_drop(self, start_element, end_element, duration=1.0):
        """
        基于坐标进行拖拽操作
        Args:
            start_element: 起始点坐标
            end_element: 结束点坐标
            duration: 拖拽持续时间（秒），默认1秒
        """
        start_x, start_y = self.get_element_xy(start_element)
        end_x, end_y = self.get_element_xy(end_element)
        try:
            logger.info(f"开始拖拽操作: 从({start_x}, {start_y})到({end_x}, {end_y})")
            # 使用pyautogui进行拖拽
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            logger.info("拖拽操作完成")
            return True

        except Exception as e:
            error_msg = f"拖拽操作失败: 从({start_x}, {start_y})到({end_x}, {end_y}), 错误: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot(f"拖拽操作失败")
            raise

    @allure.step("滚动操作: 在({element_name})位置滚动{clicks}次")
    def scroll_at_coordinates(self, element_name, clicks, direction='down'):
        """
        在指定坐标位置进行滚动操作
        Args:
            element_name: 元素（获取绝对位置）
            clicks: 滚动次数（正数向下，负数向上）
            direction: 滚动方向 ('down' 或 'up')
        """
        abs_x, abs_y = self.get_element_xy(element_name)
        try:
            # 移动到指定位置
            pyautogui.moveTo(abs_x, abs_y)
            # 根据方向和次数进行滚动
            if direction == 'down':
                scroll_amount = abs(clicks)
            else:
                scroll_amount = -abs(clicks)
            pyautogui.scroll(scroll_amount)
            logger.info(f"在坐标({abs_x}, {abs_y})滚动完成: {clicks}次, 方向: {direction}")
            return True

        except Exception as e:
            error_msg = f"滚动操作失败: ({abs_x}, {abs_y}), 错误: {str(e)}"
            logger.error(error_msg)
            self.take_screenshot(f"滚动操作失败")
            raise

    @allure.step("获取当前鼠标位置")
    def get_current_mouse_position(self):
        """获取当前鼠标位置坐标"""
        try:
            x, y = pyautogui.position()
            logger.info(f"当前鼠标位置: ({x}, {y})")
            return x, y
        except Exception as e:
            error_msg = f"获取鼠标位置失败: {str(e)}"
            logger.error(error_msg)
            raise

    @allure.step("获取绝对坐标")
    def get_element_xy(self, element_name):
        x, y = self.get_element_locator(element_name)  # 获取相对百分比
        x = float(x)
        y = float(y)
        try:
            if not (0 <= x <= 100 and 0 <= y <= 100):
                error_msg = f"相对坐标百分比超出范围: ({x}, {y})"
                logger.error(error_msg)
                raise ValueError(error_msg)
            # 计算绝对坐标
            abs_x = int(self.screen_width * x / 100)
            abs_y = int(self.screen_height * y / 100)
            logger.info(f"相对坐标 ({x}, {y}) 转换为绝对坐标: ({abs_x}, {abs_y})")
            return abs_x, abs_y

        except Exception as e:
            error_msg = f"获取绝对坐标失败: ({x}, {y}), 错误: {str(e)}"
            logger.error(error_msg)
            raise
