# Xinan_SyncAnalysis_2.py 程序的说明文档

## 一、功能描述

`Xinan_SyncAnalysis_2` 类是一个用于自动化进行交流断面最大受电能力分析的Python工具。它旨在通过与CloudPSS平台交互，实现从系统模型初始化、故障配置、潮流计算、同步调相机添加，到最终电磁暂态仿真运行及结果保存的整个流程，以评估电力系统在特定运行条件下（如N-2故障）的最大受电能力和暂态稳定性。

## 二、逻辑步骤及对应函数

### 业务逻辑与函数映射

1.  **准备分析环境与平台连接**
    在执行任何分析之前，首先需要建立与CloudPSS平台的连接，这包括提供有效的认证凭据（如令牌、API地址、用户名）和项目标识。通过这些信息初始化一个关键的CloudPSS交互实例，并加载用于识别组件的本地库数据，同时为后续的仿真在平台创建必要的分析画布，以便在CloudPSS上进行可视化和操作。这一步骤旨在为后续所有操作提供基础的运行环境和数据支持。
    *(对应函数: `Xinan_SyncAnalysis_2.__init__` 和 `Xinan_SyncAnalysis_2.initialize_system`)*

2.  **规划故障场景与仿真任务**
    在系统环境准备就绪后，需要定义具体的分析任务和故障情景。这包括设定电网的特定故障模式（例如N-2故障，模拟两条线路同时失效），以及为不同类型的仿真（如电磁暂态仿真和潮流计算）创建和配置对应的作业。同时，为了后续的结果分析，还需要指定需要测量的电压点，并根据实际需求调整系统中的负荷参数。这一步骤是为接下来即将进行的仿真奠定基础，明确仿真的目标和条件。
    *(对应函数: `Xinan_SyncAnalysis_2.configure_faults_and_jobs`)*

3.  **执行潮流计算并校准系统状态**
    配置好仿真任务后，首先进行潮流计算。这个计算将确定系统在故障发生前的稳态运行点，包括各节点的电压、功率等信息。计算完成后，需要将这些潮流数据回写到仿真模型中，以确保后续的暂态仿真能够基于准确的初始运行状态进行，同时也会对特定节点的有功和无功功率进行初步检查，以验证潮流计算的合理性。
    *(对应函数: `Xinan_SyncAnalysis_2.run_power_flow_analysis`)*

4.  **根据潮流结果配置补偿设备**
    潮流计算结果提供了系统在稳态下的运行详情。依据这些结果，可以有效地在特定母线上接入同步调相机等进行无功补偿的设备。这些设备的容量会根据预设的列表进行分配和添加，以帮助维持系统电压稳定，并为后续的暂态仿真提供更实际的初始系统配置，增强系统的稳定性。
    *(对应函数: `Xinan_SyncAnalysis_2.add_synchronous_compensators`)*

5.  **执行暂态仿真并记录分析结果**
    完成系统配置和补偿设备添加后，便可以启动电磁暂态仿真。这个仿真将详细模拟系统在故障发生、发展和清除过程中的动态响应，包括电压、电流、频率等的变化。仿真完成后，生成的结果将进行可视化，并被持久化存储到本地文件中，以便后续的详细分析和报告。这一步骤是整个分析流程的核心，旨在获取系统在扰动下的详细动态行为。
    *(对应函数: `Xinan_SyncAnalysis_2.run_emtp_analysis_and_save_results`)*

## 三、主要流程

```python
def main():
    """
    主函数，用于组织和执行电力系统交流断面最大受电能力分析流程。
    """
    # comment: 用于交流断面最大受电能力分析
    print("开始执行交流断面最大受电能力分析...")

    # Sensitive data placeholders
    token = "YOUR_CLOUD_PSS_TOKEN_PLACEHOLDER"
    api_url = "https://internal.cloudpss.net/"
    username = "USERNAME_PLACEHOLDER"
    project_key = "2025Tibet_WinterHigh_Nofault1_PLACEHOLDER"

    # 第一步：创建分析类实例并初始化系统环境
    print("第一步：创建分析类实例并初始化系统环境...")
    analysis = Xinan_SyncAnalysis_2(token_placeholder=token,
                                    api_url_placeholder=api_url,
                                    username_placeholder=username,
                                    project_key_placeholder=project_key)
    sa_instance = analysis.initialize_system()
    print("系统初始化完成。")

    # 第二步：配置故障场景和仿真作业
    print("第二步：配置故障场景和仿真作业...")
    analysis.configure_faults_and_jobs(sa_instance)
    print("故障和作业配置完成。")

    # 第三步：运行潮流计算并处理潮流数据
    print("第三步：运行潮流计算并处理潮流数据...")
    power_flow_result = analysis.run_power_flow_analysis(sa_instance)
    print("潮流计算完成并回写数据。")

    # 第四步：根据潮流结果添加同步调相机
    print("第四步：根据潮流结果添加同步调相机...")
    sync_ids = analysis.add_synchronous_compensators(sa_instance, power_flow_result)
    print(f"调相机添加完成，ID: {sync_ids}")

    # 第五步：运行电磁暂态仿真并保存结果
    print("第五步：运行电磁暂态仿真并保存结果...")
    emtp_result = analysis.run_emtp_analysis_and_save_results(sa_instance)
    print("电磁暂态仿真完成，结果已保存。")
    
    print("交流断面最大受电能力分析流程全部执行完毕。")
```