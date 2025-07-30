# Xinan_SyncAnalysis_3.py程序的说明文档

## 一、功能描述
这个程序旨在封装一套针对特定电网区域（如西藏电网）的电力系统同步分析流程，特别关注故障场景下的系统稳定性。它通过集成CloudPSS平台进行潮流计算和电磁暂态（EMT）仿真，模拟如N-2接地故障和负荷切除等事件，并在此基础上分析系统响应。最终，该程序能够帮助工程师评估电网在复杂扰动下的稳定裕度，并通过增加SVC等措施来探讨改善稳定性的方案。

## 二、逻辑步骤及对应函数

1.  **初始化分析环境**：程序启动时，首先会根据提供的认证信息（如令牌、API地址、用户名和项目密钥）配置与CloudPSS平台的连接，并加载电力系统组件库。同时，它会创建一个用于稳定分析的画布和必要的初始操作对象，为后续的仿真准备好基础环境。
    （对应函数：`Xinan_SyncAnalysis_3.__init__`）

2.  **设定故障及应对措施**：完成环境初始化后，程序会定义并设置一个特定的故障场景，例如模拟N-2线路接地故障，并通过在预定时间切除特定区域的负荷（如那曲地区）来模拟对故障的应对措施。这为后续的仿真提供了具体的扰动情景。
    （对应函数：`Xinan_SyncAnalysis_3.setup_fault_and_load_shedding`）

3.  **定义仿真任务**：接着，程序会创建并配置不同类型的仿真任务，包括用于计算系统稳态运行点的潮流计算作业，以及用于模拟系统动态响应的电磁暂态仿真作业。在此过程中，还会指定仿真的时间范围、步长、求解器选项等参数，并设定在EMT仿真结果中需要监测的关键电压测量点，以便后续分析。
    （对应函数：`Xinan_SyncAnalysis_3.create_and_configure_jobs`）

4.  **获取系统稳态数据**：在进行动态仿真之前，程序会尝试获取系统的稳态潮流数据。这可以通过两种方式实现：一是运行CloudPSS平台上的潮流计算作业来生成最新的潮流结果；二是加载一个预先保存的潮流结果文件。无论哪种方式，获取到的潮流数据都会被回写到项目模型中，作为后续电磁暂态仿真的初始条件，确保仿真能够从一个合理的稳态点开始。
    （对应函数：`Xinan_SyncAnalysis_3.run_power_flow_and_load_result`）

5.  **实施控制策略并执行动态仿真**：依赖于已获得的潮流数据，程序将进行控制策略的实施，例如在特定母线位置添加无功补偿装置（如SVC）以改善系统稳定性。随后，程序会根据设定的故障情景和初始潮流条件，在CloudPSS平台上运行电磁暂态仿真，模拟系统在扰动下的详细动态行为，以评估控制策略的效果。
    （对应函数：`Xinan_SyncAnalysis_3.add_svc_and_run_emtp_simulation`）

6.  **保存与可视化分析结果**：仿真完成后，程序会将产生的动态仿真结果保存到本地文件系统中，方便后续的数据追溯和分析。同时，它会自动生成并绘制关键的系统响应曲线图，例如电压曲线，以便直观地展示系统在故障情景下的动态特性和恢复情况，为工程决策提供可视化依据。
    （对应函数：`Xinan_SyncAnalysis_3.save_and_plot_results`）

## 三、主要流程

    # comment: 敏感信息占位符
    token_placeholder = 'YOUR_AUTH_TOKEN_PLACEHOLDER'
    api_url_placeholder = 'https://your.cloudpss.api.url.com/'
    username_placeholder = 'your_username_placeholder'
    project_key_placeholder = 'your_project_key_placeholder' # For example: '2025Tibet_WinterHigh_Nofault2'

    # 第一步：初始化分析器对象
    # 创建Xinan_SyncAnalysis_3的实例，并传入敏感信息占位符
    analyzer = Xinan_SyncAnalysis_3(token_placeholder, api_url_placeholder,
                                     username_placeholder, project_key_placeholder)

    # 第二步：设置故障和负荷切除情景
    # 调用setup_fault_and_load_shedding函数，配置N-2接地故障和那曲地区负荷切除
    analyzer.setup_fault_and_load_shedding()

    # 第三步：创建和配置仿真作业
    # 调用create_and_configure_jobs函数，设置电磁暂态仿真和潮流计算作业参数
    analyzer.create_and_configure_jobs()

    # 第四步：运行或加载潮流计算结果
    # 调用run_power_flow_and_load_result函数，获取潮流计算结果
    # 可以选择提供一个默认的潮流结果文件路径，或者让用户手动选择
    # default_pf_path_example = 'path/to/your/pfresult_2024_01_01_12_00_00.cjob'
    analyzer.run_power_flow_and_load_result()

    # 第五步：添加SVC并运行EMT仿真
    # 调用add_svc_and_run_emtp_simulation函数，在潮流结果的基础上添加SVC装置并执行EMT仿真
    analyzer.add_svc_and_run_emtp_simulation()

    # 第六步：保存并绘制仿真结果
    # 调用save_and_plot_results函数，将仿真结果保存到本地并绘制相关曲线
    analyzer.save_and_plot_results()