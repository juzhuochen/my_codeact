# `Xinan_SyncAnalysis_1.py`程序的说明文档

## 一、功能描述
该程序旨在通过集成CloudPSS平台，实现电力系统的同步稳定性分析，特别关注在N-2接地故障场景下的电磁暂态（EMTP）仿真。它提供了一套从环境初始化、故障配置、仿真设置到结果运行和保存的自动化流程，帮助用户分析电力系统在特定故障条件下的动态响应和稳定性表现。

## 二、逻辑步骤及对应函数

1.  **初始化CloudPSS环境和同步分析实例**：在开始任何仿真分析之前，需要配置与CloudPSS平台的连接，包括设置访问令牌、API地址、用户名和项目密钥，并加载必要的组件库文件，从而建立一个可进行系统分析的环境，并创建同步分析（SA）实例，为后续的高级操作如画布创建和初始条件设置做好准备（对应函数：`Xinan_SyncAnalysis_1.initialize_cloudpss_environment`）。

2.  **配置故障场景**：在环境准备就绪后，需要定义具体的仿真试验条件。这一步骤涉及选择两条线路作为故障点，并精确设定故障的发生时间、持续时间以及故障结束时间，同时指定故障的类型，例如接地故障。通过这样的配置，程序能够模拟真实世界中线路因短路等原因导致的异常状态，为后期的EMTP仿真提供具体的场景输入（对应函数：`Xinan_SyncAnalysis_1.configure_fault_scenario`）。

3.  **设置仿真作业和参数方案**：在故障场景确立后，需要针对性地创建和配置仿真作业。这包括定义EMTP仿真的名称、总仿真时长、仿真计算的步长，并指定用于执行任务的队列、所选用的求解器以及分配的CPU核心数量。此外，还会同时创建一个潮流计算作业和一个通用的参数方案，这些设置共同决定了仿真如何运行和哪些数据将被处理，为高效和准确的仿真奠定基础（对应函数：`Xinan_SyncAnalysis_1.setup_simulation_jobs_and_configs`）。

4.  **添加电压量测点**：为了在仿真过程中获取关键的动态数据以供后续分析，需要明确指定需要监测的电压点。这一步骤是向EMTP仿真作业中添加测量配置，特别针对不同电压等级（如220kV以上、110kV和10kV以下）的节点，设置采样频率，并为这些量测曲线指定易于识别的名称。通过这些量测点，可以精确捕捉到系统在故障期间的电压波动情况，为稳定性评估提供核心数据（对应函数：`Xinan_SyncAnalysis_1.add_voltage_measurement_points`）。

5.  **运行仿真并保存结果**：完成所有前期设置后，程序会启动预先配置的电磁暂态仿真作业，并根据指定的参数方案进行计算。仿真完成后，其产生的详细结果数据会被自动打包，并保存到本地文件系统中的特定目录下，文件命名会包含时间戳以便于区分和管理。这一过程最终产出可供工程师进行后续分析和稳态评估的仿真结果文件（对应函数：`Xinan_SyncAnalysis_1.run_simulation_and_save_results`）。

## 三、主要流程（main 函数流程描述）

    #comment: 敏感信息占位符
    token_ph = 'YOUR_ACCESS_TOKEN'
    api_url_ph = 'http://YOUR_CLOUD_PSS_IP_ADDRESS/'
    username_ph = 'YOUR_USERNAME'
    project_key_ph = 'YOUR_PROJECT_KEY' # 或者 'ANOTHER_PROJECT_KEY'

    #comment: 实例化分析器
    analyser = Xinan_SyncAnalysis_1(token_ph, api_url_ph, username_ph, project_key_ph)

    # 第一步：初始化CloudPSS环境和SA实例
    # comment: 加载组件库并设置CloudPSS认证信息
    try:
        analyser.initialize_cloudpss_environment()
    except Exception as e:
        print(f"环境初始化失败: {e}")
        return

    # 第二步：配置故障场景
    # comment: 设置N-2接地故障，模拟线路宕机事件
    n_2_line_labels = ['AC701004','AC701003']
    fault_start_time = 0
    fault_duration = 4
    fault_end_time = 4.09
    fault_type = 7 # 通常表示接地故障
    try:
        analyser.configure_fault_scenario(n_2_line_labels, fault_start_time, fault_duration, fault_end_time, fault_type)
    except Exception as e:
        print(f"故障场景配置失败: {e}")
        return

    # 第三步：设置仿真作业和参数方案
    # comment: 定义EMTP仿真作业的名称、时间、步长等参数
    emtp_job_name = 'SA_电磁暂态仿真'
    time_end = 30
    step_time = 0.00005
    task_queue = 'taskManager'
    solver_option = 7
    n_cpu = 16
    try:
        analyser.setup_simulation_jobs_and_configs(emtp_job_name, time_end, step_time, task_queue, solver_option, n_cpu)
    except Exception as e:
        print(f"仿真作业设置失败: {e}")
        return

    # 第四步：添加电压量测点
    # comment: 为不同电压等级的节点添加电压测量配置，以便后续分析波形
    try:
        analyser.add_voltage_measurement_points(emtp_job_name)
    except Exception as e:
        print(f"电压量测点添加失败: {e}")
        return

    # 第五步：运行仿真并保存结果
    # comment: 启动EMTP仿真并将其结果保存到本地文件系统
    try:
        result_path = analyser.run_simulation_and_save_results(emtp_job_name)
        print(f"同步分析流程执行完毕，结果文件：{result_path}")
    except Exception as e:
        print(f"仿真运行或结果保存失败: {e}")
        return