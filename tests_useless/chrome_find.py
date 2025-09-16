import os
import sys
import winreg
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess


class ChromeLocator:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome浏览器位置查找工具")
        self.root.geometry("800x600")
        self.setup_ui()

    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="Chrome浏览器位置查找工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # PATH环境变量信息
        path_frame = ttk.LabelFrame(main_frame, text="PATH环境变量中的Chrome", padding="10")
        path_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5), pady=(0, 10))

        # 注册表信息
        registry_frame = ttk.LabelFrame(main_frame, text="注册表中的Chrome信息", padding="10")
        registry_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=(0, 10))

        # 配置列权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        path_frame.columnconfigure(1, weight=1)
        registry_frame.columnconfigure(1, weight=1)

        # PATH环境变量详情
        ttk.Label(path_frame, text="PATH环境变量:").grid(row=0, column=0, sticky=tk.W, pady=2)

        self.path_text = tk.Text(path_frame, height=8, width=40)
        path_scrollbar = ttk.Scrollbar(path_frame, orient=tk.VERTICAL, command=self.path_text.yview)
        self.path_text.configure(yscrollcommand=path_scrollbar.set)
        self.path_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        path_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))

        ttk.Label(path_frame, text="在PATH中找到的Chrome:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.chrome_in_path_var = tk.StringVar()
        ttk.Label(path_frame, textvariable=self.chrome_in_path_var, foreground="blue").grid(row=2, column=1,
                                                                                            sticky=(tk.W, tk.E), pady=2)

        # 注册表详情
        ttk.Label(registry_frame, text="注册表中的Chrome路径:").grid(row=0, column=0, sticky=tk.W, pady=2)

        self.registry_text = tk.Text(registry_frame, height=10, width=40)
        registry_scrollbar = ttk.Scrollbar(registry_frame, orient=tk.VERTICAL, command=self.registry_text.yview)
        self.registry_text.configure(yscrollcommand=registry_scrollbar.set)
        self.registry_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        registry_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="查找Chrome位置", command=self.find_chrome).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新信息", command=self.refresh_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出信息", command=self.export_info).pack(side=tk.LEFT, padx=5)

        # 结果框架
        result_frame = ttk.LabelFrame(main_frame, text="查找结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        self.result_text = tk.Text(result_frame, height=8, width=80)
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 配置行和列权重
        path_frame.rowconfigure(1, weight=1)
        registry_frame.rowconfigure(1, weight=1)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 初始加载数据
        self.refresh_info()

    def refresh_info(self):
        """刷新PATH环境变量信息"""
        # PATH环境变量
        self.path_text.delete(1.0, tk.END)
        path = os.getenv('PATH', '').split(os.pathsep)
        for p in path:
            self.path_text.insert(tk.END, p + '\n')

        # 检查注册表中的Chrome信息
        self.registry_text.delete(1.0, tk.END)
        chrome_paths = self.get_chrome_path_from_registry()
        for path in chrome_paths:
            self.registry_text.insert(tk.END, path + '\n')

        # 检查PATH中是否有Chrome
        self.check_chrome_in_path()

    def check_chrome_in_path(self):
        """检查PATH环境变量中是否有Chrome"""
        path = os.getenv('PATH', '').split(os.pathsep)
        chrome_paths = []

        for p in path:
            chrome_exe = os.path.join(p, 'chrome.exe')
            if os.path.exists(chrome_exe):
                chrome_paths.append(chrome_exe)

        if chrome_paths:
            self.chrome_in_path_var.set("找到: " + ", ".join(chrome_paths))
        else:
            self.chrome_in_path_var.set("未在PATH中找到chrome.exe")

    def get_chrome_path_from_registry(self):
        """从注册表中获取Chrome安装路径"""
        chrome_paths = []
        registry_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome"),
        ]

        for hive, key_path in registry_locations:
            try:
                key = winreg.OpenKey(hive, key_path)
                try:
                    # 尝试获取默认值（通常是安装路径）
                    path, _ = winreg.QueryValueEx(key, "")
                    if os.path.exists(path):
                        chrome_paths.append(f"注册表: {hive}\\{key_path}\n路径: {path}")

                    # 尝试获取其他可能的值
                    for i in range(10):
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if name.lower() == "path" or name.lower() == "installpath":
                                if os.path.exists(value):
                                    chrome_paths.append(f"注册表: {hive}\\{key_path}\n{name}: {value}")
                        except WindowsError:
                            break
                finally:
                    winreg.CloseKey(key)
            except WindowsError:
                continue

        return chrome_paths if chrome_paths else ["在注册表中未找到Chrome信息"]

    def find_chrome(self):
        """查找Chrome的安装位置"""
        self.result_text.delete(1.0, tk.END)

        results = []

        # 1. 检查常见安装路径
        common_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        results.append("常见路径检查:")
        found = False
        for path in common_paths:
            if os.path.exists(path):
                results.append(f"✅ 找到: {path}")
                found = True
        if not found:
            results.append("❌ 未在常见路径中找到Chrome")
        results.append("")

        # 2. 检查PATH环境变量
        results.append("PATH环境变量检查:")
        path = os.getenv('PATH', '').split(os.pathsep)
        found = False
        for p in path:
            chrome_exe = os.path.join(p, 'chrome.exe')
            if os.path.exists(chrome_exe):
                results.append(f"✅ 在PATH中找到: {chrome_exe}")
                found = True
        if not found:
            results.append("❌ 未在PATH中找到Chrome")
        results.append("")

        # 3. 检查注册表
        results.append("注册表检查:")
        chrome_paths = self.get_chrome_path_from_registry()
        if chrome_paths and not chrome_paths[0].startswith("在注册表中未找到"):
            for path in chrome_paths:
                results.append(f"✅ {path}")
        else:
            results.append("❌ 未在注册表中找到Chrome信息")
        results.append("")

        # 4. 使用where命令查找
        results.append("使用where命令查找:")
        try:
            where_result = subprocess.check_output(['where', 'chrome.exe']).decode().strip()
            if where_result:
                for line in where_result.split('\n'):
                    results.append(f"✅ {line}")
            else:
                results.append("❌ where命令未找到Chrome")
        except (subprocess.CalledProcessError, FileNotFoundError):
            results.append("❌ where命令执行失败")

        # 输出结果
        for line in results:
            self.result_text.insert(tk.END, line + '\n')

    def export_info(self):
        """导出信息到文件"""
        try:
            with open("chrome_locations.txt", "w", encoding="utf-8") as f:
                f.write("Chrome浏览器位置信息\n")
                f.write("=" * 50 + "\n\n")

                f.write("PATH环境变量:\n")
                f.write(self.path_text.get(1.0, tk.END))
                f.write("\n")

                f.write("注册表中的Chrome信息:\n")
                f.write(self.registry_text.get(1.0, tk.END))
                f.write("\n")

                f.write("查找结果:\n")
                f.write(self.result_text.get(1.0, tk.END))

            messagebox.showinfo("导出成功", "信息已导出到 chrome_locations.txt")
        except Exception as e:
            messagebox.showerror("导出失败", f"导出信息时出错: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChromeLocator(root)
    root.mainloop()