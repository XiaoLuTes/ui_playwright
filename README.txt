testcase.yaml文件格式：(测试用例)
1、id    测试用例id
2、name  测试用例名称
3、steps 测试用例步骤
    step_name   测试步骤名称
    element     元素(在config.element_locators.yaml文件统一管理、定义，这里引用)
    action      动作,目前封装了： input        输入文本
                                            必填项：element\action\data(需要输入的内容)
                                            可选项:expected,返回value文本,校验是否输入成功
                               check_text   检查文本,返回元素的text文本
                                            必填项：element\action\data(需要校验的内容)
                               click        点击元素
                                            必填项：element\action
                               check_exists 检查元素是否存在
                                            必填项：element\action\data('存在' or '不存在')
                               up           输入向上指令(同键盘向上按钮)
                                            必填项：element\action\data(int,需要几次就填几)
                               down         输入向下指令(同键盘向下按钮)
                                            必填项：element\action\data(int,需要几次就填几)
                               enter        点击enter键(主要用于表单多选进行选择)
                                            必填项：element\action
                               upload       上传文件(元素未隐藏时使用该方法,必须是input类型的元素)
                                            必填项：element\action\data(文件路径,当前框架下的相对路径)
                               wait         等待(例如文件上传等场景)
                                            必填：action\data(等待时长,填整数,单位为秒)
                               wait_text    等待元素text变更
                               wait_value   等待元素value变更
                                            (调用的同一个方法)
                               sql        执行sql语句(查询)
                                            必填项：action\data(具体的sql)
                                                    expected(预期结果)可为空,代表查询数据为空
                               sql_update 执行sql语句(更新)
                                            必填项：action\data(具体的sql)\expected(预期结果)
                                                    expected(预期结果)可为空,代表查询数据为空
    data        输入文本
                可用变量：
                        {replace_num}       提取时间戳作为随机数(每次测试仅生成一次)
                        {username}          setting里设置的用户名
                        {password}          setting里设置的密码
    expected    预期(只在input、mysql、mysql_update时使用)
                    1、input时，可输入true,校验当前元素所输入的文本是否正确
                    2、sql、sql_update时：
                             1、为空("empty", "[]", "null", "none"),只要返回有一条数据就判断通过
                             2、count(=,>),计数,结果总数为多少行
                             3、contains:,包含,只要返回的所有行的任一值包含就判断通过
                             4、多条件判断(template_id=1,template_name=全局模板)
                                某一行需要同时满足多个条件,多个条件用','分割
    clear_first 是否需要先清空输入栏,默认为是(只在input时使用)

element_locators.yaml文件格式:(元素定位器)
login_page      实例名称，用于项目管理
    username_input:     元素名称(给到testcase-step使用的元素名称)
        by:             定位方式(如'id'、'xpath'、'css'等)
        value:          定位内容(定位表达式)
    hidden_      元素隐藏时使用,元素名称前+'hidden_';例如：'hidden_upload'