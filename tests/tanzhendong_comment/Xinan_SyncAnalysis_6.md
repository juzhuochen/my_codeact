# Xinan_SyncAnalysis_6.py程序的说明文档

## 一、功能描述
该 Python 脚本 `Xinan_SyncAnalysis_6.py` 旨在通过迭代优化算法，为电力系统中的调相机进行选址定容，以提升系统的电压稳定性。它通过加载历史电力潮流分析（VSI）数据，识别潜在的电压薄弱点，并在这些薄弱母线处添加同步补偿器。随后，通过多次电磁暂态仿真和线性规划，逐步调整调相机的容量，直至系统电压达到稳定标准或容量变化收敛，从而为电力系统规划和运行提供决策支持。

## 二、逻辑步骤及对应函数

1.  **初始化分析环境**：程序启动后，首先初始化CloudPSS平台的用户认证信息和API接口设置，并加载预定义的组件库。同时，它会创建进行同步补偿分析所需的画布和作业配置，为后续的仿真和计算做好准备。所有计算结果的保存路径也会在此步骤中确定。
    （对应函数：`Xinan_SyncAnalysis_6.__init__`函数）

2.  **载入电压稳定性指标数据**：在开始调相机选址定容之前，需要手动加载历史的电压稳定性指标（VSI）结果数据。这些数据通常来自对系统电压稳定性的初步评估，其中包含了各母线和线路之间的电压敏感性信息，是后续确定薄弱母线和优化调相机容量的重要依据。
    （对应函数：`Xinan_SyncAnalysis_6.load_and_set_vsi_data`函数）

3.  **确定调相机候选安装位置**：根据预设的区域划分和初始候选母线列表，程序会从加载的系统中筛选出实际存在的、且符合要求的母线作为调相机的潜在安装位置。这个筛选过程确保了调相机只被考虑安装在有效的、可访问的母线上，为后续的容量计算奠定基础。
    （对应函数：`Xinan_SyncAnalysis_6.select_and_configure_buses`函数）

4.  **在指定位置添加初始调相机**：在确定了候选母线后，程序会在每个选定的母线位置上添加一个具有初始额定容量的同步补偿器（即调相机）。这个步骤模拟了调相机的实际接入，并根据电力潮流计算结果为其设置了初始的自动电压调节器（AVR）参数，为后续的仿真和优化提供了初始模型。
    （对应函数：`Xinan_SyncAnalysis_6.add_sync_compensators`函数）

5.  **准备仿真环境和故障场景**：为了评估调相机对系统电压稳定性的影响，需要配置一个电磁暂态仿真作业。此步骤包括定义仿真时间范围、计算步长、CPU核数等，并设置特定的N-2接地故障，以模拟实际电力系统可能遇到的极端运行条件。同时，还会设置在重要母线和调相机上安装测量通道，以便在仿真过程中监测电压和无功功率的变化，为后续的电压稳定性评估提供数据。
    （对应函数：`Xinan_SyncAnalysis_6.configure_simulation_and_faults`函数）

6.  **迭代优化调相机容量**：这是核心的优化过程。程序会循环执行仿真、结果分析和容量调整，直到系统电压满足判别标准或调相机容量变化达到收敛条件。每次迭代中，首先运行前一步配置好的电磁暂态仿真作业，获取系统在故障扰动下的电压响应数据。接着，根据仿真结果计算出各母线的电压变化量，并结合电压稳定性指标数据，构建一个线性规划问题来微调每个调相机的容量。调整后的容量会立即更新到仿真模型中，以便进行下一轮迭代。在这个过程中，程序会持续监测关键母线的电压曲线，并在发现电压异常时进行可视化展示，帮助用户理解优化过程。
    （对应函数：`Xinan_SyncAnalysis_6.iterative_optimization`函数）

## 三、主要流程

```python
def main():
    """
    主函数，编排同步补偿分析的整个流程。
    """
    #comment: 定义CloudPSS的认证token。
    # All sensitive information moved to placeholders
    token = 'PLACEHOLDER_TOKEN'
    #comment: 定义CloudPSS API的URL。
    api_url = 'PLACEHOLDER_API_URL'
    #comment: 定义CloudPSS的用户名。
    username = 'PLACEHOLDER_USERNAME'
    #comment: 最终使用的项目密钥。
    project_key = 'PLACEHOLDER_PROJECT_KEY'

    # 第一步：初始化分析器
    # 创建 Xinan_SyncAnalysis_6 类的实例，并完成基础设置
    print("第一步：初始化分析器，并设置CloudPSS认证信息和项目基础配置。")
    sync_analyzer = Xinan_SyncAnalysis_6(token, api_url, username, project_key)

    # 第二步：加载VSI结果数据
    # 指定VSI结果文件的路径，并加载数据
    print("\n第二步：加载VSI结果数据。")
    # This path is hardcoded and considered sensitive, replacing with placeholder.
    vsi_file_path = 'PLACEHOLDER_VSI_FILE_PATH' # '.\\results\\xinan2025_withHVDC_noFault\\VSIresultDict_2024_01_03_14_04_21.json'
    sync_analyzer.load_and_set_vsi_data(vsi_file_path)

    # 第三步：选择并配置调相机安装母线
    print("\n第三步：选择并配置调相机安装母线。")
    #comment: 定义第一组候选母线标签。
    initial_candidate_bus_labels = [['川瀑布沟500',
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
                                     '川眉山西220']]
    sync_analyzer.select_and_configure_buses(initial_candidate_bus_labels)

    # 第四步：添加同步补偿器到模型
    print("\n第四步：添加同步补偿器到模型。")
    initial_compensator_capacity = 10  # 各个调相机的初始容量
    initial_Q = sync_analyzer.add_sync_compensators(initial_compensator_capacity)
    print(f"初始调相机容量: {initial_Q}")

    # 第五步：配置仿真作业和故障
    print("\n第五步：配置仿真作业、故障设置和测量通道。")
    #comment: 判别标准，用于电压稳定性评估。
    judgement = [[0.5, 3, 0.75, 1.25], [3, 999, 0.9, 1.1]]
    sync_analyzer.configure_simulation_and_faults(judgement)

    # 第六步：迭代优化调相机容量
    print("\n第六步：执行迭代求解，优化调相机容量。")
    Q_history = sync_analyzer.iterative_optimization(max_iterations=20, speed_factor=0.2, convergence_threshold=0.5)
    print("\n最终调相机容量迭代历史:", Q_history)
```