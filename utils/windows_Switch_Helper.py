from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from typing import List
from utils.logger import logger


class WindowSwitchHelper:
    """
    WebDriver多窗口切换辅助类
    提供自动检测和切换新窗口的功能
    """
    def __init__(self, driver: webdriver.Remote):
        """
        初始化窗口切换助手
        Args:
            driver: WebDriver实例
        """
        self.driver = driver
        self.main_window_handle = driver.current_window_handle

    def switch_to_new_window(self, timeout: int = 10) -> bool:
        """
        切换到最新打开的窗口
        Args:
            timeout: 等待超时时间（秒）
        Returns:
            bool: 切换是否成功
        """
        try:
            # 等待新窗口出现
            WebDriverWait(self.driver, timeout).until(
                lambda driver: len(driver.window_handles) > len(self._get_initial_handles())
            )
            # 获取所有窗口句柄
            all_handles = self.driver.window_handles
            new_handles = [handle for handle in all_handles if handle not in self._get_initial_handles()]
            if new_handles:
                # 切换到最新打开的窗口（最后一个新句柄）
                self.driver.switch_to.window(new_handles[-1])
                print(f"已切换到新窗口: {self.driver.title}")
                return True
            else:
                print("未找到新窗口")
                return False

        except TimeoutException:
            print(f"在 {timeout} 秒内未检测到新窗口打开")
            return False

    def switch_to_window_by_url(self, url: str, partial_match: bool = True) -> bool:
        """
        切换到指定URL的窗口
        Args:
            url: URL或URL部分
            partial_match: 是否部分匹配
        Returns:
            bool: 切换是否成功
        """
        current_handle = self.driver.current_window_handle

        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            current_url = self.driver.current_url

            if (partial_match and url in current_url) or (not partial_match and url == current_url):
                logger.info(f"已切换到URL为 '{current_url}' 的窗口")
                return True
        self.driver.switch_to.window(current_handle)
        logger.info(f"未找到URL包含 '{url}' 的窗口")
        return False

    def wait_for_new_window_and_switch(self, expected_windows: int = 2, timeout: int = 10) -> bool:
        """
        等待新窗口打开并切换到它
        Args:
            expected_windows: 期望的窗口总数
            timeout: 等待超时时间
        Returns:
            bool: 切换是否成功
        """
        try:
            # 等待窗口数量达到预期
            WebDriverWait(self.driver, timeout).until(
                lambda driver: len(driver.window_handles) == expected_windows
            )
            # 切换到新窗口
            return self.switch_to_new_window()
        except TimeoutException:
            print(f"在 {timeout} 秒内未达到 {expected_windows} 个窗口")
            return False

    def close_current_and_switch_to_main(self) -> None:
        """关闭当前窗口并切换回主窗口"""
        self.driver.close()
        self.switch_to_main_window()
        print("已关闭当前窗口并切换回主窗口")

    def switch_to_main_window(self) -> None:
        """切换回主窗口"""
        self.driver.switch_to.window(self.main_window_handle)
        print("已切换回主窗口")

    def close_all_except_main(self) -> None:
        """关闭所有非主窗口"""
        for handle in self.driver.window_handles:
            if handle != self.main_window_handle:
                self.driver.switch_to.window(handle)
                self.driver.close()

        self.switch_to_main_window()
        print("已关闭所有非主窗口")

    def get_window_handles_info(self) -> List[dict]:
        """
        获取所有窗口的信息
        Returns:
            List[dict]: 窗口信息列表
        """
        current_handle = self.driver.current_window_handle
        windows_info = []

        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            windows_info.append({
                'handle': handle,
                'title': self.driver.title,
                'url': self.driver.current_url,
                'is_main': handle == self.main_window_handle
            })

        # 切换回原来的窗口
        self.driver.switch_to.window(current_handle)
        return windows_info

    def _get_initial_handles(self) -> List[str]:
        """获取初始窗口句柄（用于内部使用）"""
        # 这里可以根据需要扩展，比如记录所有初始窗口
        return [self.main_window_handle]
