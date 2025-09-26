import os
import pytest
import subprocess
import sys
from pathlib import Path


def find_project_root():
    """查找项目根目录"""
    current = Path.cwd()

    # 查找包含 pytest.ini 的目录
    for parent in [current] + list(current.parents):
        if (parent / "pytest.ini").exists():
            return parent
    return current


def main():
    # 找到项目根目录
    project_root = find_project_root()
    print(f"项目根目录: {project_root}")

    # 切换到项目根目录
    os.chdir(project_root)
    print(f"当前工作目录: {Path.cwd()}")

    # 设置路径
    results_dir = project_root / "reports" / "temp"
    report_dir = project_root / "reports" / "allure-reports"

    # 运行 pytest
    exit_code = pytest.main()

    # 生成报告
    if results_dir.exists() and any(results_dir.iterdir()):
        cmd = f"allure generate {results_dir} -o {report_dir} --clean"
        subprocess.run(cmd, shell=True)
        if (report_dir / "index.html").exists():
            print("报告生成成功")
        else:
            print("报告生成失败")
    return exit_code


if __name__ == '__main__':
    sys.exit(main())

# if __name__ == '__main__':
#     pytest.main()
#     os.system("allure generate ./reports/temp -o ./reports/allure-reports --clean")
