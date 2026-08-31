# UI 自动化测试框架

基于 **Playwright + Pytest + YAML 数据驱动** 的 Web UI 自动化测试框架，支持多项目切换、OCR 验证码自动识别、数据库校验、失败截图与日志留证。

---

## 一、技术栈

| 组件 | 说明 |
|---|---|
| Playwright | 浏览器自动化（Chromium） |
| Pytest | 测试框架（参数化驱动） |
| PyYAML | 用例与定位器配置（YAML 格式） |
| ddddocr / OpenCV | 验证码 OCR 识别 |
| pymysql | 数据库校验 |
| Allure | 测试报告（可选） |

## 二、目录结构

```
ui_playwright/
├── run.py                     # 入口脚本（执行 pytest）
├── test_from_yaml.py          # pytest 测试类（参数化加载用例）
├── conftest.py                # pytest fixture（session 级浏览器）
├── pytest.ini                 # pytest 配置
├── requirements.txt           # 依赖清单
├── README.md                  # 本文档
├── 超时配置说明.md             # 超时配置速查表
│
├── config/
│   ├── settings.py            # 全局配置（环境/账号/项目/超时/路径）
│   └── locators/              # 元素定位器（按页面/项目分文件）
│       ├── gsr_admin_page.yaml
│       ├── new_position_element_locators.yaml
│       ├── pt_new_position_v2.yaml
│       ├── attendance_and_leave.yaml
│       └── flutter.yaml
│
├── pages/                     # 页面对象层
│   ├── base_page.py           # 页面操作基类（查找/点击/输入/上传/等待/截图）
│   ├── gsr_admin_page.py      # 管理端页面对象（含 OCR 自动登录）
│   └── flutter_page.py        # Flutter 页面（已废弃，勿用）
│
├── utils/                     # 工具层
│   ├── browser.py             # 浏览器引擎（单例）
│   ├── executor.py            # 动作执行器（YAML 动作 → 页面方法）
│   ├── yaml_load.py           # 用例加载 + 测试结果回写
│   ├── page_manager.py        # 页面注册与导航管理
│   ├── element_locator.py     # 元素定位器读取
│   ├── captcha_ocr.py         # 验证码 OCR 识别
│   ├── database.py            # 数据库操作（查询/更新）
│   ├── common.py              # 通用工具（变量替换/截图）
│   └── logger.py              # 日志配置（按天切割）
│
├── testcases/                 # 测试用例（YAML 数据驱动）
│   ├── pt_new_position/       # 招聘平台（旧版）
│   ├── pt_new_position_v2/    # 招聘平台（维护版，当前在用）
│   ├── pt_new_preparation/    # 招聘准备
│   ├── smoke_login/           # 冒烟登录
│   ├── attendance_and_leave/  # 考勤请假
│   └── template.yaml          # 用例模板
│
└── reports/                   # 产物目录
    ├── logs/                  # 运行日志（按天）
    ├── logs_error/            # 错误日志（按天）
    ├── screenshots/           # 失败截图
    ├── temp/                  # Allure 临时文件
    └── test_results/          # 测试结果（每次运行汇总一个 YAML 文件）
```

## 三、环境准备

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器（首次）
playwright install chromium
```

> 若本机已安装 Chrome，`config/settings.py` 中可配置浏览器可执行文件路径，优先复用本机 Chrome。

## 四、配置说明（config/settings.py）

### 4.1 多项目切换

```python
CURRENT_PROJECT = "招聘平台新建岗位-维护版"   # ← 切换项目在这里改
```

每个项目在 `PROJECT_CONFIGS` 中配置：

```python
"招聘平台新建岗位-维护版": {
    "PAGE_NAME": ["gsr_admin_page"],          # 涉及的页面对象
    "ELEMENT_LOCATORS": "./config/locators/pt_new_position_v2.yaml",  # 定位器文件
    "TESTCASES_PATH": "./testcases/pt_new_position_v2/pt_testcases_v2.yaml",  # 用例文件
}
```

### 4.2 超时配置（详见 `超时配置说明.md`）

| 配置 | 默认值 | 单位 | 用途 |
|---|---|---|---|
| `IMPLICIT_WAIT` | 15000 | 毫秒 | page 全局默认超时（元素操作兜底）|
| `EXPLICIT_WAIT` | 30 | 秒 | 等待元素值变化的总超时 |
| `TIME_FIND` | 3000 | 毫秒 | 轮询单次查找超时 |
| `REFRESH_INTERVAL` | 5 | 秒 | 等待值变化时的页面刷新间隔 |
| `REFRESH_TIME` | 15 | 秒 | 等待元素出现时的页面刷新间隔 |
| `WAIT_ELEMENT_APPEAR` | 120 | 秒 | 等待元素出现的总超时 |
| `DB_TIMEOUT` | 20 | 秒 | 数据库连接超时 |

> 所有超时配置均支持环境变量覆盖（`_get_env_var`）。

### 4.3 环境变量覆盖

配置项可通过同名环境变量覆盖，例如：

```bash
# Windows PowerShell
$env:EXPLICIT_WAIT = "60"
python run.py
```

## 五、编写测试用例

### 5.1 用例文件格式（testcases/*.yaml）

```yaml
test_cases:
  - id: 招聘平台-1              # 用例 ID（唯一）
    name: 创建不启用ai岗位       # 用例名称
    steps:                      # 步骤列表
      - step_name: 打开登录页    # 步骤名称
        element: username_input  # 元素名（引用定位器文件中的定义）
        action: input            # 动作
        data: '{username}'       # 输入内容（支持变量）
        expected: true           # 可选：输入后校验
```

### 5.2 支持的动作列表

| 动作 | 必填项 | 说明 |
|---|---|---|
| `input` | element / action / data | 输入文本，`expected: true` 校验输入成功，`clear_first` 控制是否先清空（默认清空）|
| `click` | element / action | 点击元素 |
| `check_text` | element / action / data | 校验元素文本是否包含 data |
| `check_exists` | element / action / data | 校验元素存在与否，data 填 `存在` 或 `不存在` |
| `wait_exists` | element / action | 等待元素出现（最长 `WAIT_ELEMENT_APPEAR`，每 `REFRESH_TIME` 刷新页面）|
| `wait_text` / `wait_value` | element / action / data | 等待元素文本/值变为 data（最长 `EXPLICIT_WAIT`，每 `REFRESH_INTERVAL` 刷新页面）|
| `upload` | element / action / data | 上传文件（input 类型元素，data 为相对路径）|
| `wait` | action / data | 固定等待，data 为秒数 |
| `up` / `down` | element / action / data | 键盘上/下方向键，data 为次数 |
| `enter` | element / action | 回车键（表单多选场景）|
| `sql` | action / data / expected | 执行查询 SQL 并校验 |
| `sql_update` | action / data / expected | 执行更新 SQL 并校验 |
| `screenshot` | action | 主动截图 |

### 5.3 可用变量

| 变量 | 说明 |
|---|---|
| `{replace_num}` | 时间戳随机数（同一次运行内固定）|
| `{username}` / `{password}` | settings 中配置的账号密码 |
| `{customer}` / `{owner}` | settings 中配置的客户/负责人 |

### 5.4 元素定位器格式（config/locators/*.yaml）

```yaml
gsr_admin_page:                # 页面名（与 settings 中 PAGE_NAME 对应）
  username_input:              # 元素名（用例中引用）
    by: id                     # 定位方式：id / xpath / css / name
    value: username            # 定位表达式
  hidden_upload:               # 隐藏元素：名称前加 hidden_
    by: xpath
    value: //input[@type='file']
```

## 六、运行测试

```bash
# 方式一：入口脚本（推荐）
python run.py

# 方式二：pytest 直接运行
python -m pytest -v

# 方式三：只跑指定用例
python -m pytest -v -k "招聘平台"
```

运行前确认 `config/settings.py` 中 `CURRENT_PROJECT` 指向目标项目。

## 七、测试结果与报告

| 产物 | 位置 | 说明 |
|---|---|---|
| 测试结果汇总 | `reports/test_results/<项目>_<批次>.yaml` | 每次运行一个文件，含全部用例的通过/失败结果 |
| 失败截图 | `reports/screenshots/` | 每个失败场景自动截图留证 |
| 运行日志 | `reports/logs/UI_log_日期.log` | 按天切割 |
| 错误日志 | `reports/logs_error/UI_error_log_日期.log` | 按天切割 |

> 测试结果**不会写回用例源文件**，用例 YAML 保持只读，git diff 干净。

## 八、注意事项

1. **登录依赖 OCR**：`gsr_admin_page.py` 自动识别验证码，失败自动重试 3 次；测试环境不稳定时可能出现登录失败，属于环境问题而非脚本问题。
2. **wait_text / wait_value 会刷新页面**：等待期间按 `REFRESH_INTERVAL` 刷新页面拉取最新状态；请勿在"填写表单中途"使用（刷新会清空表单）。
3. **用例间避免隐式依赖**：新建用例时，前置数据建议通过接口造数或 SQL 准备，不要依赖前序用例的执行结果。
4. **凭据安全**：`settings.py` 中当前为明文账号密码（测试环境），建议后续迁移至 `.env` 文件并加入 `.gitignore`。

## 九、常见问题

**Q: 元素查找超时（15 秒）？**
A: 多为测试环境响应慢或页面未加载完成；可临时调大 `IMPLICIT_WAIT`，或检查定位器是否因页面改版失效。

**Q: 登录失败/验证码识别失败？**
A: 确认测试环境可用；截图位于 `reports/screenshots/登录失败-*.png`，可查看实际页面状态。

**Q: 结果文件里某些用例 result 为空？**
A: 说明该用例因环境问题中断未执行完；重新运行即可，结果会累积写入同一批次文件。
