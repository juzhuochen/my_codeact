# "Xinan_SyncAnalysis_4.py"程序的说明文档

## 一、功能描述

Xinan_SyncAnalysis_4 类旨在封装西南电网的电磁暂态仿真分析流程，通过集成CloudPSS平台的能力，实现对电力系统模型的上传、配置、故障场景设置、仿真执行、结果数据处理和可视化，以分析电力系统在故障条件下的动态响应和电压偏差。

## 二、逻辑步骤及对应函数

1.  **初始化环境与分析器实例：** 在开始任何仿真前，首先需要提供CloudPSS平台的认证凭据（令牌、API URL、用户名和项目密钥）来创建一个仿真分析器实例。此步骤准备了与CloudPSS平台交互的基础对象，并加载了进行仿真分析所需的基础组件库配置，为后续的所有操作奠定基础。（对应函数：`Xinan_SyncAnalysis_4.__init__`）

2.  **建立与CloudPSS平台的连接：** 在分析器实例创建后，需要使用先前提供的认证凭据来初始化CloudPSS的工作环境，包括设置认证令牌、配置API访问地址，并准备好在CloudPSS平台上进行操作的SA（系统分析）实例。这一步还包括创建用于电力潮流计算和参数配置的任务容器，以及设定本地存储仿真结果的路径，确保仿真结果能够被妥善保存。（对应函数：`Xinan_SyncAnalysis_4.initialize_cloudpss_env`）

3.  **配置特定故障场景与仿真设置：** 在环境准备就绪后，接下来需要根据具体的分析需求定义电力系统中的故障类型（例如单相接地故障或两相接地故障），并提供故障发生的具体参数，如故障所在的线路、发生位置、起止时间以及故障阻抗。同时，也在此步骤中设定整个电磁暂态仿真的总时长和求解器相关的配置，以规划仿真覆盖的时间范围和计算资源。（对应函数：`Xinan_SyncAnalysis_4.configure_fault_and_simulation`）

4.  **指定系统量测点：** 为了在仿真过程中收集关键的电力系统数据，例如母线电压，需要识别并添加需要监测的测量点。通常可以根据特定的命名规则（如母线ID的前缀）来批量选择感测对象，使得仿真结果能够重点反映特定区域或设备的状态。（对应函数：`Xinan_SyncAnalysis_4.add_measurements`）

5.  **执行电磁暂态仿真：** 在完成所有配置后，启动电磁暂态仿真任务。此过程会将配置好的模型和仿真参数提交到CloudPSS平台进行计算，等待平台返回系统的动态响应数据。此步骤是整个分析的核心，负责生成后续结果分析所依赖的原始数据。（对应函数：`Xinan_SyncAnalysis_4.run_emtp_simulation`）

6.  **分析并可视化仿真结果：** 仿真完成后，获取并处理返回的仿真结果数据。该步骤会根据预设的电压偏差判断标准，对仿真过程中母线电压的变化进行评估，识别出电压超出允许范围的不合格点。最后，会将这些关键的电压曲线通过图表形式进行可视化展示，便于用户直观地观察和分析电力系统的故障响应特性。（对应函数：`Xinan_SyncAnalysis_4.analyze_and_visualize_results`）

## 三、主要流程

```python
    # comment: 定义 CloudPSS 的认证 token。
    tk = PLACEHOLDER_TOKEN
    # comment: 定义 CloudPSS API 的 URL。
    apiURL = PLACEHOLDER_API_URL
    # comment: 定义 CloudPSS 用户名。
    username = PLACEHOLDER_USERNAME
    # comment: 定义 CloudPSS 项目密钥。
    projectKey = PLACEHOLDER_PROJECT_KEY

    # 初始化分析器
    # 第一步：创建 Xinan_SyncAnalysis_4 对象，初始化仿真分析器
    print("第一步：创建 Xinan_SyncAnalysis_4 对象，初始化仿真分析器...")
    analyser = Xinan_SyncAnalysis_4(token=tk, api_url=apiURL, username=username, project_key=projectKey)
    print("分析器对象创建成功。")

    # 第二步：初始化 CloudPSS 环境和项目
    print("\n第二步：初始化 CloudPSS 环境和项目...")
    analyser.initialize_cloudpss_env()
    print("CloudPSS 环境和项目初始化完成。")

    # 第三步：配置故障场景和仿真参数
    print("\n第三步：配置故障场景和仿真参数...")
    fault_args = {
        'component_id': 'comp_TranssmissionLineRouter_4106',
        'fault_location': 0,
        'start_time': 4,
        'end_time': 4.1,
        'impedance': 7
    }
    analyser.configure_fault_and_simulation(fault_type='N-1_ground', fault_args=fault_args, end_time=10)
    print("故障和仿真参数配置完成。")

    # 第四步：添加测量点
    print("\n第四步：添加测量点...")
    measured_buses = analyser.add_measurements(bus_id_prefix='川')
    print(f"已添加关键测量点共 {len(measured_buses)} 个。")

    # 第五步：运行电磁暂态仿真
    print("\n第五步：运行电磁暂态仿真...")
    ss_result = analyser.run_emtp_simulation()
    print("电磁暂态仿真运行完成。")

    # 第六步：分析和可视化仿真结果
    print("\n第六步：分析和可视化仿真结果...")
    analyser.analyze_and_visualize_results(ss_result)
    print("仿真结果分析和可视化完成。")
```