# Xinan_SyncAnalysis_5.py 程序的说明文档

## 一、功能描述

`Xinan_SyncAnalysis_5` 类旨在封装和自动化电力系统暂态稳定分析的整个流程。它通过与CloudPSS平台交互，实现了从连接认证、项目管理、潮流计算、VSI（电压稳定性指标）分析到结果可视化的一系列操作，主要用于评估和分析电力系统的电压稳定性，帮助用户理解系统在不同运行条件下的表现。

## 二、逻辑步骤及对应函数

1.  **设置运行环境并初始化分析器**：在执行任何分析任务之前，需要配置与CloudPSS平台的连接参数，包括访问令牌、API地址、用户名和项目密钥，并加载必要的组件库。此步骤的成功执行将初始化内部的仿真和分析工具，为后续的计算操作做好准备。
    *对应函数：`setup_environment_and_initialize`*

2.  **执行初始潮流计算并保存结果**：在系统完成初始化后，将进行项目的初始潮流计算。这个步骤的目标是获得系统在稳态运行条件下的电压、功率分布等信息，这些潮流计算的结果将作为后续暂态分析的起始状态，并会被记录下来以供后续查询或导出。
    *对应函数：`perform_load_flow_and_save_result`*

3.  **配置VSI分析参数**：根据特定的分析需求，指定需要进行电压稳定性分析的母线。系统会根据这些指定的母线自动识别并添加特殊的无功电源，同时创建电磁暂态仿真和潮流计算的作业，并配置相关的仿真时长、时间步长等关键参数，为后续的VSI仿真奠定基础。
    *对应函数：`configure_vsi_analysis`*

4.  **执行VSI电磁暂态仿真**：在完成VSI分析参数配置后，系统会在指定母线上添加电压和无功功率的测量点。接着，会自动运行预设的电磁暂态仿真作业，模拟系统在特定扰动下的动态响应。仿真结束后，系统将自动保存生成的测量数据和仿真结果，为后续的VSI指标计算提供原始数据。
    *对应函数：`execute_vsi_simulation`*

5.  **计算并可视化VSI结果**：利用电磁暂态仿真获得的测量数据，系统将自动计算出各项VSI指标，如电压稳定性指标（VSIi）。计算完成后，结果将以交互式的折线图和柱状图形式进行展示，直观地呈现出VSI随时间的变化趋势以及各母线的稳定性水平，从而方便用户对系统电压稳定性进行评估和决策。
    *对应函数：`calculate_and_visualize_vsi`*

## 三、主要流程

```python
    #comment: 敏感信息占位符
    TOKEN_PLACEHOLDER = "YOUR_CLOUDPSS_TOKEN_HERE"
    API_URL_PLACEHOLDER = "http://YOUR_CLOUDPSS_API_URL_HERE/"
    USERNAME_PLACEHOLDER = "YOUR_USERNAME_HERE"
    PROJECT_KEY_PLACEHOLDER = "YOUR_PROJECT_KEY_HERE"

    analysis_instance = Xinan_SyncAnalysis_5()

    #comment: 第一步：配置环境并初始化分析器
    # comment: 调用 setup_environment_and_initialize 函数，完成CloudPSS连接设置、组件库加载和SA实例初始化。
    analysis_instance.setup_environment_and_initialize(
        token=TOKEN_PLACEHOLDER,
        api_url=API_URL_PLACEHOLDER,
        username=USERNAME_PLACEHOLDER,
        project_key=PROJECT_KEY_PLACEHOLDER
    )

    #comment: 第二步：执行初始潮流计算并保存结果
    # comment: 调用 perform_load_flow_and_save_result 函数，计算电力系统的初始潮流，并获取潮流计算结果。
    pf_result_id, pf_result = analysis_instance.perform_load_flow_and_save_result()

    #comment: 第三步：配置VSI分析参数
    # comment: 调用 configure_vsi_analysis 函数，设置VSI分析的母线、仿真参数以及EMTP仿真作业。
    bus_labels1 =['川瀑布沟500',
                 '川深溪沟500',
                 '川枕头坝500',
                 '川眉山西500',
                 '川修文220-II',
                 '川修文220-l',
                 '川东坡220',
                 '川东坡220-3',
                 '川爱国220',
                 '川甘眉220',
                 '天井坎220',
                 '川铁西220',
                 '川眉山西220']
    bus_label_area = [bus_labels1]
    vsi_analysis_config = analysis_instance.configure_vsi_analysis(bus_label_area, default_ts=8, default_dt=1.5, default_ddt=0.5)

    #comment: 第四步：执行VSI电磁暂态仿真
    # comment: 调用 execute_vsi_simulation 函数，运行配置好的VSI电磁暂态仿真。
    voltage_measure_k, dQ_measure_k, screened_bus, vsi_simulation_result = analysis_instance.execute_vsi_simulation(vsi_analysis_config)

    #comment: 第五步：计算并可视化VSI结果
    # comment: 调用 calculate_and_visualize_vsi 函数，处理仿真结果，计算VSI指标，并生成可视化图表。
    vsi_final_results = analysis_instance.calculate_and_visualize_vsi(
        vsi_analysis_config, voltage_measure_k, dQ_measure_k, vsi_simulation_result
    )
    print("所有分析步骤已完成。")
```