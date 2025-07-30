# "NetworkCalculation.py"程序的说明文档

## 一、功能描述

`NetworkCalculation` 类旨在为电力系统工程师或分析人员提供一套全面的工具，用于执行电力系统的频域分析、潮流计算和暂态仿真。它能够从CloudPSS平台加载系统配置，计算不同频率下的网络导纳和阻抗矩阵，确定稳定运行工况下的电压和电流，并模拟系统在特定扰动下的动态响应，最终通过数据可视化展示分析结果。这解决了在电力系统设计、评估和故障分析中，对系统频率特性和瞬态行为进行深入理解的复杂问题。

## 二、逻辑步骤及对应函数

### 1. 初始化分析环境

在开始任何电力系统分析之前，需要首先准备好分析环境。这个步骤会创建一个包含系统分析所需基本参数和默认配置的实例，例如CloudPSS平台的API令牌、URL、用户名以及分析所需的频率范围、基准频率、收敛标准等。这些配置为后续的所有计算奠定了基础，确保分析能够顺利进行并具备一致性。

（对应函数：`NetworkCalculation.__init__` 函数）

### 2. 加载网络模型与配置

为了对一个具体的电力系统进行分析，需要导入其网络拓扑结构和各组件的详细参数。这个步骤通过读取预先存储的系统模型文件（例如JSON格式的组件库），然后设置与CloudPSS平台的交互参数（如API令牌和项目密钥），并初始化系统画布。此操作还会识别并记录系统中的所有总线和三绕组变压器，为后续的矩阵构建提供必要的节点信息。

（对应函数：`NetworkCalculation.load_network_config` 函数）

### 3. 计算系统频域特性

在分析电力系统的频率响应时，需要确定系统在不同频率下的行为。这个步骤会遍历预设的整个频率范围，针对每个频率点，计算系统中所有线路、变压器和负载等组件在该频率下的导纳。接着，将这些组件导纳汇聚成整个网络的导纳矩阵，并通过求逆得到网络的阻抗矩阵。这个过程产出的阻抗和导纳矩阵集合，是进一步进行稳态和暂态分析的基础，揭示了系统在不同频率下的传递特性。

（对应函数：`NetworkCalculation.calculate_frequency_response` 函数）

### 4. 确定系统稳定运行点

在进行暂态仿真前，必须首先明确系统在扰动发生前的稳定运行状态。这个步骤通过在基准频率（例如50Hz）下构建整个网络的导纳矩阵及其逆矩阵（即阻抗矩阵），然后识别系统中的所有电源连接点。利用这些信息，通过求解线性方程组，来计算出在稳定工况下，各节点的电压和流经电源连接点的电流。这个稳定运行点是进行后续动态仿真和扰动分析的起始状态。

（对应函数：`NetworkCalculation.calculate_stable_operating_point` 函数）

### 5. 模拟系统暂态响应

为了理解电力系统在遭受扰动（如故障或负载突变）后的动态行为，需要进行时域仿真。这个步骤通过在稳定运行点电流的基础上，在特定故障总线上叠加一个定义的瞬态电流扰动。然后，利用系统在频域分析中获得的阻抗矩阵的模态特征（如极点和残差），通过模拟物理过程中的卷积操作，计算出系统在仿真持续时间内的电压和电流随时间变化的曲线。这提供了系统动态稳定性和瞬态过电压/过电流的关键洞察。

（对应函数：`NetworkCalculation.simulate_time_domain_response` 函数）

### 6. 分析系统模态特性

为了深入理解电力系统的振荡模式和稳定性，需要计算其特性矩阵。这个步骤基于系统在所有频率下的阻抗矩阵，通过特定归一化处理构建特性矩阵。接着，计算特性矩阵在基准频率下的特征值和特征向量，这些特征值和特征向量揭示了系统的固有振荡模式和阻尼特性。通过对每个频率点重复此过程，可以得到特性矩阵随频率变化的特征值，这有助于识别潜在的谐振点和系统薄弱环节。

（对应函数：`NetworkCalculation.calculate_characteristic_matrix` 函数）

### 7. 可视化分析结果

为了直观地呈现复杂的分析结果，需要将计算出的数据绘制成易于理解的图表。这个步骤会将系统仿真得到的电压和电流的时间响应曲线，以及特性矩阵随频率变化的幅值，通过图表形式展示出来。此外，还可以绘制网络的拓扑结构图，帮助分析人员更清晰地理解系统连接。这些可视化图表是评估系统性能、诊断问题和制定改进方案的重要依据。

（对应函数：`NetworkCalculation.plot_results` 函数）

## 三、主要流程

```python
    # 第一步：初始化 NetworkCalculation 类的实例，并获取默认配置。
    print("------- 开始电力系统分析流程 -------")
    calculator = NetworkCalculation()
    
    # 原始脚本的频率设置
    # freqs = np.append(np.append(np.linspace(10,40,16),np.linspace(45,200,32)),np.linspace(300,2000,18))
    # calculator.opts['Freq'] = freqs # Overwrite default Freq with this specific set
    # calculator.opts['fws'] = 50 # Set fundamental frequency

    # 第二步：加载网络配置文件和拓扑结构。
    calculator.load_network_config()

    # 第三步：计算系统在不同频率下的阻抗和导纳矩阵。
    calculator.calculate_frequency_response()

    # 第四步：计算稳定工况下的节点电压和电流。
    calculator.calculate_stable_operating_point()

    # 第五步：模拟系统在特定扰动下的时域响应，计算电压和电流时间曲线。
    # 定义扰动参数
    perturb_node_key = 'PLACEHOLDER_BUS_FOR_PERTURBATION' # 'component_new_bus_3_p_3'
    # The original script does not explicitly use `res['PYc']`, `res['RYc']`, etc.
    # which are typically outputs of a vector fitting step (e.g., from `vectfit3`).
    # If these are necessary for `simulate_time_domain_response` to be accurate,
    # a `vectfit3` step (or similar modal analysis method) needs to be added before this.
    # For now, `simulate_time_domain_response` is called assuming `res` has placeholders or will be properly initialized.
    
    # Placeholder for potential vector fitting step if needed:
    # try:
    #     poles, res_mat = vectfit3(calculator.opts['Freq'], calculator.Z, **calculator.opts['vfopts'])
    #     calculator.res['PYc'] = poles # Example assignment, needs to match actual vectfit3 output structure
    #     calculator.res['RYc'] = res_mat # Example
    #     calculator.res['fws'] = calculator.opts['f0'] # Fundamental frequency
    #     # Add C and E terms if vectfit3 provides them and they are critical.
    # except Exception as e:
    #     print(f"Warning: Vector fitting failed or not implemented. Time domain simulation may be approximate. Error: {e}")

    # Set some dummy values for `PYc`, `RYc`, `CYc`, `EYc` if vector fitting is not integrated,
    # to allow the `simulate_time_domain_response` to run without immediate errors.
    # In a real scenario, these should come from a proper modal analysis.
    num_nodes = calculator.res['Nc']
    num_poles = 1 # Example: just one pole for very basic test
    calculator.res['PYc'] = np.array([-10 + 500j]) # A dummy pole
    calculator.res['RYc'] = np.ones((num_nodes, num_nodes, num_poles), dtype=complex) # Dummy residue
    calculator.res['CYc'] = np.zeros((num_nodes, num_nodes), dtype=complex) # Dummy constant term
    calculator.res['EYc'] = np.zeros((num_nodes, num_nodes), dtype=complex) # Dummy E*s term
    calculator.res['fws'] = calculator.opts['f0'] # Set fundamental frequency for time domain

    calculator.simulate_time_domain_response(calculator.res['I0'], perturb_node_key, 
                                              t_start=0.2, t_end_perturb=0.3, tau=0.03,
                                              total_sim_time=1.0, delta_t=0.01)

    # 第六步：计算系统的特性矩阵，用于模态分析。
    calculator.calculate_characteristic_matrix()

    # 第七步：绘制所有计算结果，包括电压时间曲线、特性矩阵频率响应和电流时间曲线。
    current_plot_node_key = 'PLACEHOLDER_NODE_FOR_CURRENT_PLOT' # 'canvas_0_10'
    calculator.plot_results(voltage_trace_nodes=None, H_matrix_trace_nodes=None) # Using default paths
    # Or, to be explicit with nodes:
    # calculator.plot_results(voltage_trace_nodes=[perturb_node_key, 'another_bus_key'],
    #                         H_matrix_trace_nodes=[perturb_node_key, 'yet_another_bus_key'])

    print("------- 电力系统分析流程完成 -------")
```