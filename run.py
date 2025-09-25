import os
# import sys
import pytest
# from utils.logger import logger


# def main():
#     try:
#         # 运行测试，返回退出码
#         exit_code = pytest.main([
#             'test_from_yaml.py',
#             '-v',
#             '--junitxml=test-results.xml'
#         ])
#         # pytest.main() 返回退出码：0-成功，1-失败，其他-错误
#         sys.exit(exit_code)
#
#     except Exception as e:
#         print(f"执行测试时发生错误: {e}")
#         sys.exit(2)  # 使用2表示执行错误


if __name__ == '__main__':
    pytest.main()
    os.system("allure generate ./reports/temp -o ./reports/allure-reports --clean")
