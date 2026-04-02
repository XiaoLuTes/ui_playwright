import pytest
import sys
import os


def main():
    # 自动创建报告目录
    os.makedirs("reports/temp", exist_ok=True)
    os.makedirs("reports/screenshots", exist_ok=True)
    # 执行测试
    exit_code = pytest.main([
        "-vs",
        "--alluredir=./reports/temp",
        "--clean-alluredir"
    ])

    # 生成报告
    # print("\n测试完成，正在生成 Allure 报告...")
    # os.system("allure generate ./reports/temp -o ./reports/allure-reports --clean")
    # print("\n打开报告服务...")
    # os.system("allure serve ./reports/temp")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
