# setup_drivers.py
import os
import requests
import zipfile
import platform
import sys
from utils.logger import logger


class DriverManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.architecture()[0]
        self.mirrors = [
            {
                'name': '官方镜像',
                'base_url': 'https://storage.googleapis.com/chrome-for-testing-public'
            }
        ]

    def get_chrome_version(self):
        """获取已安装的Chrome版本"""
        try:
            if self.system == "windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                return version
            elif self.system == "darwin":  # macOS
                cmd = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
                output = os.popen(cmd).read().strip()
                return output.split()[-1]
            else:  # linux
                cmd = 'google-chrome --version'
                output = os.popen(cmd).read().strip()
                return output.split()[-1]
        except Exception as e:
            logger.warning(f"获取Chrome版本失败: {e}")
            return "131.0.6778.87"  # 返回一个稳定版本作为默认

    def get_download_url(self, version, mirror):
        """根据系统和架构构建下载URL"""
        if self.system == "windows":
            return f"{mirror['base_url']}/{version}/win64/chromedriver-win64.zip"
        elif self.system == "darwin":
            if platform.machine().lower() == "arm64":
                return f"{mirror['base_url']}/{version}/mac-arm64/chromedriver-mac-arm64.zip"
            else:
                return f"{mirror['base_url']}/{version}/mac-x64/chromedriver-mac-x64.zip"
        else:  # linux
            return f"{mirror['base_url']}/{version}/linux64/chromedriver-linux64.zip"

    def download_file(self, url, filepath):
        """下载文件"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            sys.stdout.write(f"\r下载进度: {percent:.1f}%")
                            sys.stdout.flush()

            print()  # 换行
            return True
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False

    def extract_driver(self, zip_path, extract_to):
        """解压驱动文件"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 查找chromedriver文件
                for file_info in zip_ref.filelist:
                    if 'chromedriver' in file_info.filename.lower():
                        # 提取文件
                        extracted_path = zip_ref.extract(file_info, extract_to)

                        # 重命名文件
                        final_name = "chromedriver.exe" if self.system == "windows" else "chromedriver"
                        final_path = os.path.join(extract_to, final_name)

                        # 如果目标文件已存在，先删除
                        if os.path.exists(final_path):
                            os.remove(final_path)

                        os.rename(extracted_path, final_path)

                        # 在Unix系统上添加执行权限
                        if self.system != "windows":
                            os.chmod(final_path, 0o755)

                        logger.info(f"驱动已解压到: {final_path}")
                        return final_path

            raise Exception("在ZIP文件中未找到chromedriver")
        except Exception as e:
            logger.error(f"解压失败: {e}")
            return None

    def download_chromedriver(self):
        """下载ChromeDriver"""
        # 获取Chrome版本
        chrome_version = self.get_chrome_version()
        logger.info(f"检测到Chrome版本: {chrome_version}")

        # 创建drivers目录
        os.makedirs("drivers", exist_ok=True)
        zip_path = os.path.join("drivers", "chromedriver.zip")

        # 尝试不同的镜像源
        for mirror in self.mirrors:
            logger.info(f"尝试从 {mirror['name']} 下载...")

            download_url = self.get_download_url(chrome_version, mirror)
            logger.info(f"下载URL: {download_url}")

            if self.download_file(download_url, zip_path):
                logger.info("下载成功，正在解压...")
                driver_path = self.extract_driver(zip_path, "drivers")

                if driver_path:
                    # 清理临时文件
                    if os.path.exists(zip_path):
                        os.remove(zip_path)

                    logger.info("ChromeDriver 安装完成!")
                    return driver_path
                else:
                    logger.error(f"{mirror['name']} 解压失败")
            else:
                logger.warning(f"{mirror['name']} 下载失败")

        # 所有镜像都失败
        logger.error("所有镜像源都失败了，请检查网络连接或手动下载")
        return None


def main():
    manager = DriverManager()
    driver_path = manager.download_chromedriver()

    if driver_path:
        print(f"\n✅ ChromeDriver 已成功安装到: {driver_path}")
        print("现在你可以运行测试了!")
    else:
        print("\n❌ ChromeDriver 安装失败")
        print("请尝试手动下载:")
        print("1. 访问: https://registry.npmmirror.com/binary.html?path=chromedriver/")
        print("2. 下载对应版本的 chromedriver")
        print("3. 解压到项目根目录的 'drivers' 文件夹中")


if __name__ == "__main__":
    main()
