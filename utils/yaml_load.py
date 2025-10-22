from utils.logger import logger
from config.settings import Settings
from utils.common import read_yaml_raw, read_yaml, write_yaml


class YamlLoad:
    def __init__(self):
        self.setting = Settings()

    def load_test_cases(self):
        """加载测试用例"""
        file_path = self.setting.TESTCASES
        try:
            data = read_yaml(file_path)
            test_cases = data.get('test_cases', [])
            logger.info(f"测试用例地址：{file_path}")
            logger.info(f"从YAML文件加载了 {len(test_cases)} 个测试用例")
            return test_cases
        except Exception as e:
            logger.error(f"加载测试用例失败: {str(e)}")
            return []

    def update_test_result(self, test_case_id, result):
        """更新测试用例结果"""
        file_path = self.setting.TESTCASES
        try:
            data = read_yaml_raw(file_path)
            # 更新测试结果
            for test_case in data['test_cases']:
                if test_case['id'] == test_case_id:
                    test_case['result'] = result
                    break
            # 写回文件
            write_yaml(file_path, data)
            logger.info(f"更新测试用例 {test_case_id} 结果为: {result}")
            return True
        except Exception as e:
            logger.error(f"更新测试结果失败: {str(e)}")
            return False
