import yaml
import time

def read_yaml_raw(file_path):
    # 读取方法
    with open(file_path, mode='r', encoding="utf-8") as a:
        value = yaml.load(stream=a, Loader=yaml.FullLoader)
        return value

def read_yaml(file_path):
    """
    读取YAML文件并替换 {replace_num} 为时间戳
    """
    with open(file_path, mode='r', encoding="utf-8") as a:
        content = a.read()
        # 替换 {replace_num} 为时间戳
        timestamp = int(time.time() * 1000)
        content = content.replace('{replace_num}', str(timestamp))
        # 加载YAML
        value = yaml.load(stream=content, Loader=yaml.FullLoader)
        return value
