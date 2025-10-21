# import os
# import allure
# from selenium.common.exceptions import TimeoutException, InvalidArgumentException
# from selenium.webdriver.common.by import By
import time

timestamp = int(time.time() * 1000)
print(int(time.time()))
print(timestamp)
time_now = time.strftime("%y%m%d-%H:%M", time.localtime())
print(time_now)
