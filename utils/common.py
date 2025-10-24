import yaml
import time
from config.settings import settings

def read_yaml_raw(file_path):
    # 读取方法
    with open(file_path, mode='r', encoding="utf-8") as a:
        value = yaml.load(stream=a, Loader=yaml.FullLoader)
        return value

def read_yaml(file_path):
    # 读取yaml用例并把{replace_num}替换为时间戳
    with open(file_path, mode='r', encoding="utf-8") as a:
        content = a.read()
        timestamp = int(time.time() * 1000)
        username = settings.USER
        password = settings.PASSWORD
        replacements = {
            '{replace_num}': str(timestamp),
            '{username}': username,
            '{password}': password,
        }
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        values = yaml.load(stream=content, Loader=yaml.FullLoader)
        return values

def write_yaml(file_path, data):
    # 写入全局变量(替换掉原有)
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)
