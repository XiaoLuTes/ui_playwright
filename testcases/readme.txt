testcase.yaml文件格式：(测试用例)
1、id    测试用例id
2、name  测试用例名称
3、steps 测试用例步骤
    step_name   测试步骤名称(方便问题定位)
    element     元素名称(在config.element_locators.yaml文件统一管理、定义，这里引用)
    action      动作(目前封装了： input        输入
                                            必填项：element\action\data(需要输入的内容)

                               check_text   检查文本
                                            必填项：element\action\data(需要校验的内容)

                               click        点击
                                            必填项：element\action

                               check_exists 检查元素是否存在
                                            必填项：element\action\data('存在' or '不存在')

                               up           输入向上指令(同键盘向上按钮)
                                            必填项：element\action\data(int,需要几次就填几)

                               down         输入向下指令(同键盘向下按钮)
                                            必填项：element\action\data(int,需要几次就填几)

                               enter        点击enter键(主要用于表单多选进行选择)
                                            必填项：element\action

                               upload       上传文件
                                            必填项：element\action\data(文件路径,当前框架下的相对路径)
                                            元素未隐藏时使用该方法,element必须是input类型的元素

                               hidden_upload上传文件
                                            必填项：element\action\data(文件路径,当前框架下的相对路径)
                                            元素隐藏时使用该方法
                                            用例里element必须是input类型的元素,元素管理不用加hidden_前缀

                               wait         等待(例如文件上传等场景)
                                            必填：action\data(等待时长,填整数)

    data        输入文本
    expected    预期(只在input时使用,可输入true或false,校验当前元素所输入的文本是否正确)


element_locators.yaml文件格式:(元素定位器)
login_page      实例login_page,如果需要从login动作开始测试，元素都可以放在下面
    username_input:     元素名称(给到testcase-step使用的元素名称)
    by:                 定位方式(如'id'、'xpath'、'css'等)
    value:              定位内容(定位表达式)
