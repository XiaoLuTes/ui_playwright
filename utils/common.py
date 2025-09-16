import yaml


def read_yaml(file_path):
    # 读取方法
    with open(file_path, mode='r', encoding="utf-8") as a:
        value = yaml.load(stream=a, Loader=yaml.FullLoader)
        return value
