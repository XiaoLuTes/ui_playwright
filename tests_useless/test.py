from selenium import webdriver
from selenium.webdriver.common.by import By
import time
    # 使用JavaScript直接设置滚动位置

scroll_container = driver.find_element(By.ID, "selectContainer")
driver.execute_script("arguments[0].scrollTop = 1000", scroll_container)
# 等待一下确保滚动完成
time.sleep(0.5)
# 定位并点击目标元素
target_option = driver.find_element(By.XPATH, "//div[contains(text(), '选项 45')]")
target_option.click()



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# # 先点击选择栏以激活它
# dropdown = driver.find_element(By.ID, "selectContainer")
# dropdown.click()
# # 模拟按下多次下箭头键
# actions = ActionChains(driver)
#     for in range(40):
# # 按下40次下箭头
#         actions.send_keys(Keys.ARROW_DOWN)
#         actions.perform()
# # 现在可以定位并点击目标元素
# target_option = driver.find_element(By.XPATH, "//div[contains(text(), '选项 45')]")
# target_option.click()
