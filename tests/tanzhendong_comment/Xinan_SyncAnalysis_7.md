# Xinan_SyncAnalysis_7.py"程序的说明文档

## 一、功能描述

该程序旨在通过CloudPSS平台，自动化执行批量电力系统N-1故障仿真，特别是针对发电机切出引起的频率稳定性进行分析，通过模拟不同故障场景下系统的响应，评估其稳定性并保存详细仿真结果。

## 二、逻辑步骤及对应函数

1.  **准备环境**: 在开始进行仿真前，需要明确CloudPSS的访问凭证（令牌、API地址、用户名）和项目标识，这些信息将确保后续所有操作都在正确的环境中进行，并且拥有相应的权限。（对应函数：`Xinan_SyncAnalysis_7.__init__`函数）

2.  **设置仿真分析实例**: 在环境准备就绪后，需要初始化一个专门用于稳定性分析的工具，这包括配置与CloudPSS平台的连接参数，设定仿真的初始状态，以及为不同类型的仿真（如电磁暂态仿真和潮流计算）创建专用的工作区域和任务。同时，还需要定义一个配置方案来统一管理仿真参数。（对应函数：`Xinan_SyncAnalysis_7.initialize_stability_analysis`函数）

3.  **加载组件库与定义监测区域**: 为了能够识别和操作电力系统中的各个元件，需要从预设的文件中加载整个系统模型的组件信息。同时，为了后续分析系统在故障下的表现，还需要根据预设的规则，在特定地理区域内随机抽样选择一部分母线进行重点监测，并记录下这些监测点的信息以便后续使用。（对应函数：`Xinan_SyncAnalysis_7.load_component_library_and_define_areas`函数）

4.  **准备故障场景**: 在系统模型和监测点都准备好之后，需要明确哪些是N-1故障分析中关注的潜在故障对象，通常是一组可能被切出的发电机或重要线路。这一步将这些具有业务意义的故障标签转换为系统内部可以识别的组件标识符列表，为后续执行具体的切出故障操作做好准备。（对应函数：`Xinan_SyncAnalysis_7.prepare_fault_scenarios`函数）

5.  **配置并运行单个故障场景仿真**: 对于每一个预设的故障场景，系统会首先在其启动时便模拟该故障（例如，切除特定的发电机或线路）。紧接着，为了捕捉故障发生后系统的动态响应，会在预先设定的监测母线上添加电压信号输出，并通过特殊的信号处理模块（如PLL和通道分解器）进一步提取和配置需要测量的频率信号。完成配置后，系统便会启动电磁暂态仿真，并在仿真结束后将所有关键数据保存到指定的位置，以便后续进行频率稳定性分析。（对应函数：`Xinan_SyncAnalysis_7.configure_simulation_outputs`函数和`Xinan_SyncAnalysis_7.run_simulation_and_save_results`函数）

## 三、主要流程

```python
    # comment: 定义 CloudPSS 的访问令牌
    # 敏感信息替换为占位符
    token = 'YOUR_CLOUD_PSS_TOKEN'
    # comment: 定义 CloudPSS API 的 URL
    # 敏感信息替换为占位符
    api_url = 'YOUR_CLOUD_PSS_API_URL'
    # comment: 定义 CloudPSS 用户名
    # 敏感信息替换为占位符
    username = 'YOUR_USERNAME'
    # comment: 定义项目密钥
    # 敏感信息替换为占位符
    project_key = 'YOUR_PROJECT_KEY'

    # comment: 定义 N-1 故障对象的标签列表 (Moved here for main to control the iteration)
    # This list will be passed to a class method for processing
    n_1_labels = [
        ['新nls铝业四期G1'],
        ['山能盛鲁G1'],
        ['陕清水G1'],
        ['青拉西瓦G3'],
        ['宁方家庄G2'],
        ['甘昌西一690华', '甘安马中电一69', '甘安四龙源二69', '甘桥东二690东'],
        ['新hm景峡西风G1', '新hm景峡西风G2', '新w柴窝堡西汇G2', '新w柴窝堡西汇G1', '新zd中电投老君庙南风G1',
         '新zd三峡北塔山风G1']
    ]

    # 第一步：创建 Xinan_SyncAnalysis_7 类的实例
    # comment: 创建 Xinan_SyncAnalysis_7 类的实例
    analysis_instance = Xinan_SyncAnalysis_7(token, api_url, username, project_key)

    # 第二步：初始化稳定性分析设置
    # comment: 调用 initialize_stability_analysis 函数，初始化稳定性分析实例，包括配置、画布和作业创建。
    analysis_instance.initialize_stability_analysis()

    # 第三步：加载组件库并定义需要测量的区域
    # comment: 调用 load_component_library_and_define_areas 函数，从文件加载组件库并确定要进行测量的母线区域。
    analysis_instance.load_component_library_and_define_areas()

    # 第四步：准备故障场景数据
    # comment: 调用 prepare_fault_scenarios 函数，解析 N-1 故障对象的标签，生成内部使用的故障键列表。
    analysis_instance.prepare_fault_scenarios()

    # 第五步：遍历所有故障场景，配置仿真输出并运行仿真
    # comment: 遍历 N_1Keys 中的每个故障场景，逐个配置仿真输出，包括设置故障和添加测量信号，然后运行仿真并保存结果。
    for n_k_ptr in range(len(n_1_labels)): # Use n_1_labels length for iteration
        # 为了每次仿真都在一个“干净”的环境下进行，这里需要重新初始化sa实例。
        # 注意：这里和原始脚本行为一致，每次循环都创建新的SA实例，但这不是一个原子性的函数，因此这里在main函数中处理。
        # 如果SA实例的内部状态在每次仿真中不应该有前次循环的残留，重新创建是必要的。
        analysis_instance.initialize_stability_analysis() # Re-initialize SA for each scenario
        analysis_instance.configure_simulation_outputs(n_k_ptr)
        analysis_instance.run_simulation_and_save_results(n_k_ptr, n_1_labels)
```