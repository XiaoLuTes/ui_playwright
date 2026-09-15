import pytest
import sys
import os
import glob

from config.settings import settings
from utils.common import read_yaml
from utils.wecom import notify


def collect_result_summary():
    """收集最近一次运行的结果统计（读取 reports/test_results 下最新的批次文件）
    :return: (统计文本, 失败用例名列表, 结果文件路径)
    """
    files = glob.glob("reports/test_results/*.yaml")
    if not files:
        return "无结果文件", [], None
    latest = max(files, key=os.path.getmtime)          # 最新的批次结果文件
    data = read_yaml(latest) or {}
    cases = data.get("test_cases", [])
    total = len(cases)
    passed = sum(1 for c in cases if str(c.get("result", "")) == "通过")
    failed = [str(c.get("name", "")) for c in cases
              if str(c.get("result", "")).startswith("失败")]
    summary = f"通过 {passed} 失败 {len(failed)} 共 {total}"
    return summary, failed, latest


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

    # ===== 企业微信通知（会话结束时聚合发送一条；未配置 WECOM_WEBHOOK 则静默跳过）=====
    try:
        webhook = os.environ.get("WECOM_WEBHOOK", "")
        summary, failed_cases, result_file = collect_result_summary()
        report_url = os.environ.get("BUILD_URL", "") or None
        notify(
            webhook,
            settings.CURRENT_PROJECT,
            summary,
            failed_cases,
            [result_file] if result_file else None,
            report_url,
        )
    except Exception as e:
        print(f"[通知] 发送异常（不影响执行结果）: {e}")

    # 生成报告
    # print("\n测试完成，正在生成 Allure 报告...")
    # os.system("allure generate ./reports/temp -o ./reports/allure-reports --clean")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
