# Xinan_SyncAnalysis_8.py 程序的说明文档

## 一、功能描述

`Xinan_SyncAnalysis_8` 类旨在用于电网的稳定分析和静止无功补偿器（SVC）优化配置。它封装了与CloudPSS平台进行交互的多个环节，包括模型设置、故障定义、仿真执行、结果分析，并集成了一个基本的粒子群优化（PSO）算法，以寻找到在特定故障场景下能提升系统稳定性的最优SVC容量配置，最终解决电网特定状况下稳定性的问题。

## 二、逻辑步骤及对应函数

1.  在开始任何分析和优化工作之前，首先需要建立与外部平台的连接，并对分析系统进行实例化。这包括提供必要的身份认证信息和平台API地址，并且加载预定义的组件库，确保系统能够识别和操作电网模型中的各种设备，为后续的所有操作奠定基础。
    （对应函数：`Xinan_SyncAnalysis_8.__init__`函数）

2.  接下来，要为电网仿真设定初始运行条件，并模拟一个特定的N-2接地故障场景。这需要在已连接的电网模型中设置电力系统的初始稳定状态，并定义哪些线路将发生故障、故障持续多长时间以及故障何时被清除等具体参数。这个步骤的结果是创建了一个包含预设故障的仿真画布，以便在模拟中观察故障对电网稳定性的影响。
    （对应函数：`Xinan_SyncAnalysis_8.setup_initial_conditions_and_fault`函数）

3.  完成故障设置后，需要配置具体的仿真任务并确定需要测量的关键电气量。这包括创建用于计算电网稳态运行情况的潮流计算任务，以及用于分析故障发生时电网动态响应的电磁暂态仿真任务。同时，为了评估系统稳定性，需要指定在哪些电压等级的重要母线进行电压测量，以便在仿真结束后获取详细的电压曲线数据，并将所有结果保存到指定位置。
    （对应函数：`Xinan_SyncAnalysis_8.configure_simulations_and_measures`函数）

4.  为了进行SVC优化配置，需要在特定的电网母线安装静止无功补偿器，并为优化算法设定参数。这涉及识别可在哪些母线进行SVC安装，从而确定优化变量的维度，并为粒子群优化算法配置其核心参数，例如搜索范围、迭代次数、群大小以及相关的权重和加速系数。这个步骤的成果是为优化过程准备好了所有必要的输入数据和算法策略。
    （对应函数：`Xinan_SyncAnalysis_8.prepare_svc_buses_and_pso_config`函数）

5.  在模型中实际引入静止无功补偿器设备，并准备粒子群优化算法的初始状态。这包括根据此前确定的母线信息，在电网模型中具体添加SVC设备并赋初始容量值。如果之前有执行过优化，也可以选择加载历史优化记录，使算法从上次中断的地方继续，否则将初始化算法的所有内部变量，为即将开始的迭代优化奠定基础。
    （对应函数：`Xinan_SyncAnalysis_8.add_svcs_and_load_pso_state`函数）

6.  启动粒子群优化算法的单次迭代过程。在每次迭代中，算法会根据当前粒子的容量配置，更新模型中的静止无功补偿器参数，然后执行电磁暂态仿真，并计算评估系统稳定性的指标。依据这个稳定性指标，算法会更新每个粒子的最优历史位置以及整个粒子群的全局最优位置，并根据这些信息调整粒子的速度和容量，以向更优的解空间前进。
    （对应函数：`Xinan_SyncAnalysis_8.run_pso_iteration`函数）

7.  在优化过程结束后，将所有优化迭代的历史数据保存下来。这涉及将粒子群优化算法在每次迭代中产生的关键信息，如粒子的容量配置、个体最优解、全局最优解以及对应的系统稳定性指标等，归档到文件中。这样做能够方便后续对优化过程进行回溯、分析和可视化，从而验证优化效果或为后续研究提供数据。
    （对应函数：`Xinan_SyncAnalysis_8.save_pso_history`函数）

## 三、主要流程

```python
def main():
    """
    主函数，编排Xinan_SyncAnalysis_8类的操作流程。
    """
    # comment: 定义占位符敏感数据
    token_ph = 'YOUR_ACCESS_TOKEN_PLACEHOLDER'
    api_url_ph = 'https://your.cloudpss.api.url.placeholder/'
    username_ph = 'your_username_placeholder'
    project_key_ph = 'YOUR_PROJECT_KEY_PLACEHOLDER'

    # comment: 第一步：初始化分析器实例并设置基本配置
    print("\n--- 第一步：初始化分析器实例并设置基本配置 ---")
    sync_analysis = Xinan_SyncAnalysis_8(token_ph, api_url_ph, username_ph, project_key_ph)


    # comment: 第二步：设置初始条件和仿真故障
    print("\n--- 第二步：设置初始条件和仿真故障 ---")
    n2_line_labels = ['AC900203', 'AC900202']
    n1_line_label = '藏夏玛—藏德吉开关站' # 原始代码中N-1线路没有实际用于故障设置
    fault_parameters = {
        'fault_line_idx1': 0,
        'fault_line_idx2': 1,
        'fault_start': 0,
        'fault_duration': 1.5,
        'clear_time': 1.56,
        'fault_type': 7,
        'other_fault_paras': {'chg': '1'}
    }
    setup_info = sync_analysis.setup_initial_conditions_and_fault(n2_line_labels, n1_line_label, fault_parameters)


    # comment: 第三步：配置仿真任务和电压测量
    print("\n--- 第三步：配置仿真任务和电压测量 ---")
    emtp_args = {
        'begin_time': 0, 'end_time': 6, 'step_time': 0.00002,
        'task_queue': 'taskManager', 'solver_option': 7, 'n_cpu': 16
    }
    voltage_measure_configs = [
        {'vmin': 220, 'freq': 200, 'plot_name': '220kV以上电压曲线'},
        {'vmin': 110, 'vmax': 120, 'freq': 200, 'plot_name': '110kV电压曲线'}
    ]
    results_save_path = sync_analysis.configure_simulations_and_measures(emtp_args, voltage_measure_configs)
    print(f"仿真结果将保存至: {results_save_path}")


    # comment: 第四步：准备SVC安装母线信息和PSO配置
    print("\n--- 第四步：准备SVC安装母线信息和PSO配置 ---")
    bus_labels_by_area = [
        ['藏曲布雄220-1', '藏多林220'],
        ['藏德吉220-2', '藏藏那220-1', '藏安牵220'],
        ['藏西城220-1', '藏东城220-1', '藏旁多220-1', '藏曲哥220-1', '藏乃琼220-1'],
        ['藏老虎嘴220-1', '藏朗县220-1', '藏卧龙220-1', '藏巴宜220'],
        ['藏昌珠220-1', '藏吉雄220-1']
    ]
    svc_capacity_range = (0.1, 200) # Qmin, Qmax
    pso_hyperparameters = {
        "C1": 2, "C2": 2, "W": 0.6, "vmax": 30, "SI0": 0.05, "W0": 99999, "iter_num": 10
    }
    pso_setup_info = sync_analysis.prepare_svc_buses_and_pso_config(bus_labels_by_area,
                                                                   svc_capacity_range,
                                                                   pso_hyperparameters)
    # 获取初始的Q和V矩阵
    initial_Q_matrix = pso_setup_info['Qinit']
    # initial_V_matrix = pso_setup_info['Vinit'] # 原始代码中的Vinit在add_svcs_and_load_pso_state中被覆盖


    # comment: 第五步：添加SVC设备并初始化/加载PSO状态
    print("\n--- 第五步：添加SVC设备并初始化/加载PSO状态 ---")
    # 模拟Qhistory的加载，由于没有实际的Qhistory文件，这里用一个空列表开始
    # 在实际应用中，这里会尝试从文件加载，如果存在的话
    # 例如：try: with open('results/YOUR_PROJECT_KEY_PLACEHOLDER/PSO_Qhistory_latest.json', 'r') as f: q_history_mock = json.load(f) except FileNotFoundError: q_history_mock = []
    # 为了演示，我们将直接跳过加载，从头开始
    q_history_mock_data = [] # 假设没有历史数据，从头开始优化

    pso_state = sync_analysis.add_svcs_and_load_pso_state(initial_Q_matrix, pso_history=q_history_mock_data)
    # 将SVC的ID存储起来，方便后续使用
    sync_ids_actual = pso_state['sync_ids']


    # comment: 第六步：执行粒子群优化迭代（这里只运行一次迭代，如果需要完整迭代，需要循环）
    print("\n--- 第六步：执行粒子群优化迭代 ---")
    q_history_list = [] # 用于存储每次迭代的QData
    # 原始代码中迭代次数为1，但pso_hyperparameters中定义了iter_num=10，这里为了符合原始逻辑，只执行一次
    # 如果要运行完整的PSO迭代，需要一个for循环：for _ in range(sync_analysis._pso_config["iter_num"]):
    
    # 准备迭代参数
    iteration_params = {
        'sync_ids': sync_ids_actual,
        'Q_matrix': pso_state['Q_matrix'],
        'V_matrix': pso_state['V_matrix'],
        'QpBest': pso_state['QpBest'],
        'pBest': pso_state['pBest'],
        'QgBest': pso_state['QgBest'],
        'gBest': pso_state['gBest']
    }
    
    # 执行一次迭代
    updated_pso_state = sync_analysis.run_pso_iteration(iteration_params, token_ph, api_url_ph)
    q_history_list.append(updated_pso_state['QData_current_iter']) # 将当前迭代的QData添加到历史列表

    print(f"当前迭代结束后的全局最优适应度 gBest: {updated_pso_state['gBest']}")
    print(f"当前迭代结束后的全局最优容量配置 QgBest: {updated_pso_state['QgBest']}")


    # comment: 第七步：保存优化迭代历史
    print("\n--- 第七步：保存优化迭代历史 ---")
    sync_analysis.save_pso_history(q_history_list)
    print("所有操作完成。")


# comment: 主程序入口
if __name__ == '__main__':
    main()
```