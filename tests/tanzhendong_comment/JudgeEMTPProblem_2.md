# JudgeEMTPProblem_2.py 程序的说明文档

## 一、功能描述

该Python程序旨在通过与CloudPSS平台交互，获取直流线路模型，计算并评估其电气参数，同时计算换流站侧的无功功率和相关参数，以支持电力系统仿真和分析。

## 二、逻辑步骤及对应函数

1.  **准备环境与连接平台**：在进行任何模型操作之前，需要配置好与 CloudPSS 平台的连接凭据，包括访问令牌、API 地址、用户名和项目密钥。成功配置后，程序将能够验证自身身份并准备好访问平台资源。
    （对应函数：`JudgeEMTPProblem_2.__init__` 和 `JudgeEMTPProblem_2.initialize_cloudpss_connection`）

2.  **获取仿真模型**：完成平台连接初始化后，程序会根据预设的项目密钥从 CloudPSS 平台检索特定的仿真模型。这个模型是后续所有参数计算和分析的基础，它包含了直流线路和换流站的详细结构和初始参数。
    （对应函数：`JudgeEMTPProblem_2.fetch_cloudpss_model`）

3.  **计算直流线路参数**：获取模型后，程序会识别模型中所有与直流线路相关的组件，并对每个组件的初始参数进行深度复制和数据类型转换。接着，它会基于直流线路的运行状态和各组件的原始参数，运用一系列电气公式（如基于功率平衡、电压关系和变压器特性的计算）来推导和更新直流线路的多种运行参数，例如无功功率、直流电流、变压器变比、换相电抗以及换流器触发角和关断角。这些计算结果将被存储，以便后续评估和分析。
    （对应函数：`JudgeEMTPProblem_2.calculate_dc_line_parameters`）

4.  **计算换流站功率**：前一步已经获得了直流线路的各项参数，在此基础上，程序会进一步模拟并计算换流站（包括整流侧和逆变侧）在特定直流电压、功率和运行角度（如点燃角、熄弧角）条件下的有功和无功功率。这个步骤会考虑变压器的额定参数、档位设置以及线路电阻等因素，最终得出整流侧和逆变侧的详细功率数据。
    （对应函数：`JudgeEMTPProblem_2.calculate_converter_station_power`）

5.  **展示计算结果**：完成所有参数和功率的计算后，程序会将计算所得的整流侧和逆变侧的 P-Q 节点信息（有功功率和无功功率）清晰地输出，以便查阅和分析，这是对之前所有计算结果的集中呈现。
    （对应函数：`JudgeEMTPProblem_2.display_results`）

## 三、主要流程

```python
    # comment: 打印开始信息
    print('Start')

    # comment: 第一步：初始化 JudgeEMTPProblem_2 类的实例，并替换敏感信息为占位符。
    # comment: 定义一个名为 JudgeEMTPProblem_2 的类，用于处理直流线路参数计算和换流站功率计算
    # comment: 替换以下敏感数据为占位符
    token_placeholder = 'YOUR_TOKEN_HERE'
    api_url_placeholder = 'http://YOUR_API_URL_HERE/'
    username_placeholder = 'YOUR_USERNAME_HERE'
    # comment: 考虑到原始脚本中 projectKey 有多次更新，这里使用一个示例project key
    project_key_placeholder = 'YOUR_PROJECT_KEY_HERE' 
    
    problem_solver = JudgeEMTPProblem_2(
        token=token_placeholder,
        api_url=api_url_placeholder,
        username=username_placeholder,
        project_key=project_key_placeholder
    )

    # comment: 第二步：调用 initialize_cloudpss_connection 函数，初始化 CloudPSS 连接设置。
    problem_solver.initialize_cloudpss_connection()

    # comment: 第三步：调用 fetch_cloudpss_model 函数，从 CloudPSS 获取模型。
    problem_solver.fetch_cloudpss_model()

    # comment: 第四步：调用 calculate_dc_line_parameters 函数，计算直流线路参数。
    problem_solver.calculate_dc_line_parameters()

    # comment: 第五步：调用 calculate_converter_station_power 函数，计算换流站侧功率参数。
    problem_solver.calculate_converter_station_power()

    # comment: 第六步：调用 display_results 函数，显示计算结果。
    problem_solver.display_results()

    print('End of script.')
```