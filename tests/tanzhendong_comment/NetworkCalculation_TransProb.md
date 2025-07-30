# NetworkCalculation_TransProb.py 程序的说明文档

## 一、功能描述

该程序旨在对电力系统网络进行全面的特性计算和瞬态分析。它通过配置 CloudPSS 平台接口、在频域计算并拟合网络导纳矩阵和传播函数、确定系统稳态工况，并最终计算特定扰动下的时域电压响应，进而帮助分析和理解电力系统在不同频率和时间尺度下的行为。

## 二、逻辑步骤及对应函数

1.  **初始化与默认配置加载**：在开始任何电力系统分析之前，系统会首先创建一个核心分析器的实例，并加载一套预定义的默认参数配置。这些参数涵盖了从 CloudPSS 平台连接信息（如API令牌、URL、用户名和项目密钥）到仿真细节（如频率范围、拟合误差、极点数量、权重设置以及矢量拟合的各种选项）。这个步骤确保了分析工具具备运行所需的基本设定，以便进行后续的计算、数据拟合以及结果可视化。
    对应函数：`NetworkCalculation_TransProb.__init__` 和 `NetworkCalculation_TransProb._default_options`

2.  **仿真环境配置与参数更新**：程序会根据特定的仿真需求，对加载的默认配置进行进一步的自定义和更新。这包括重新设定CloudPSS的认证信息、调整目标误差、矢量拟合行为（例如是否包含常数项、稳定极点等）、基频、特征值计算的迭代上限和收敛精度、以及频域矩阵拟合的详细参数（如极点数量、允许误差、不同频率区间的权重及其风格）。此外，还会更新用于频域分析的频率点范围和稳态基频。完成此步骤后，系统将具备所有必要的定制化参数，可以与CloudPSS平台建立连接并执行具体的仿真任务。
    对应函数：`NetworkCalculation_TransProb.configure_simulation`

3.  **频域矩阵计算与拟合**：在完成仿真环境的配置后，程序将着手进行电力系统网络在不同频率下的阻抗（Z）和导纳（Y）矩阵的计算。此过程会遍历预设的频率范围，对每个频率点计算系统的全网络矩阵。为了后续的时域分析，特别是为了将复杂的频域响应转化为简洁的状态空间模型，程序会利用矢量拟合技术对计算出的Z矩阵进行逼近。这个拟合过程旨在用一组极点、残数和常数项来精确描述频域特性，从而为时域响应计算打下基础。如果需要，此步骤还可以选择性地显示拟合结果的图形化视图，以便于验证拟合的准确性。
    对应函数：`NetworkCalculation_TransProb.calculate_frequency_domain_matrices`

4.  **稳态工况分析**：在进行瞬态分析之前，系统会计算网络在稳态基频下的初始电气量（电流和电压）分布。这个过程首先确定哪些母线是与电源相连的，然后根据系统在基频下的阻抗矩阵和已知的母线电压，通过最小二乘法求解网络的初始电流。此步骤旨在建立一个可靠的初始运行点，为后续的瞬态扰动模拟提供准确的起始条件。
    对应函数：`NetworkCalculation_TransProb.calculate_stable_case`

5.  **特征传播函数 H 矩阵的计算**：为了更好地理解和分析电力系统中的电压传播特性，系统将计算并形成特征传播函数 H 矩阵。这个矩阵是在每个频率点上，通过将当前频率下的网络阻抗矩阵与参考电压进行适当归一化处理而得到的。H 矩阵的计算及其随频率的变化，对于深入分析系统中的谐振、阻尼以及电压稳定性具有重要意义。此步骤的结果将包含H矩阵及其模态信息，为后续的时域响应计算提供重要的输入。
    对应函数：`NetworkCalculation_TransProb.calculate_h_matrix`

6.  **时域电压响应计算**：在完成了频域拟合和稳态工况初始化之后，程序将模拟在特定母线注入电流扰动时，网络中各母线的电压随时间的变化。这个过程涉及到将频域拟合得到的系统模型（极点、残数、常数项）转换到时域，并通过对电流扰动的卷积操作来计算电压响应。通过定义注入电流的起始时间、结束时间、指数衰减常数以及仿真步长，系统能够精细地捕捉到瞬态过程中的电压动态行为。
    对应函数：`NetworkCalculation_TransProb.calculate_time_domain_response` 和 `NetworkCalculation_TransProb._calculate_time_Icurve_V0`

7.  **时域电压曲线可视化**：为了直观地展示瞬态分析的结果，程序将绘制特定母线在时域内的电压幅值曲线。通过选择感兴趣的母线（包括通过最短路径算法确定的相关母线），并将计算得到的时域电压响应数据进行适当的变换（例如Clarke变换），系统能够以图形方式呈现电压随时间的变化趋势，便于工程师分析系统的动态响应特性。
    对应函数：`NetworkCalculation_TransProb.plot_time_domain_voltage`

8.  **H 矩阵幅频响应曲线可视化**：为了深入分析网络的频率特性，程序将绘制指定母线间特征传播函数 H 矩阵的幅频响应曲线。通过选择起始和目标母线，并通过最短路径方法筛选出介于两者之间的关键母线，系统可以展示H矩阵的幅值如何随频率变化，从而揭示系统在不同频率下的传输特性和潜在的谐振模式。
    对应函数：`NetworkCalculation_TransProb.plot_frequency_domain_h_matrix_magnitude`

9.  **时域电流曲线可视化（可选）**：如果需要，程序还可以绘制之前注入的时域电流随时间变化的曲线。这有助于验证电流注入的设置是否符合预期，并作为分析电压响应的参考。
    对应函数：`NetworkCalculation_TransProb.plot_time_domain_current`

## 三、主要流程（main 函数流程描述）

```python
    # comment: 实例化 NetworkCalculation_TransProb 类，加载默认配置
    network_analyzer = NetworkCalculation_TransProb()

    # 第一步：调用 configure_simulation 函数，配置仿真环境
    network_analyzer.configure_simulation()
    print("步骤1：仿真环境配置完成。")

    # 第二步：调用 calculate_frequency_domain_matrices 函数，计算并拟合频域矩阵
    network_analyzer.calculate_frequency_domain_matrices()
    print("步骤2：频域矩阵计算与拟合完成。")

    # 第三步：调用 calculate_stable_case 函数，计算稳态工况下的初始电流和电压
    network_analyzer.calculate_stable_case()
    print("步骤3：稳态工况计算完成。")

    # 第四步：调用 calculate_h_matrix 函数，计算特性传播函数 H 矩阵
    network_analyzer.calculate_h_matrix()
    print("步骤4：H矩阵计算完成。")

    # 第五步：调用 calculate_time_domain_response 函数，计算时域响应
    # Define parameters for time domain simulation
    node_to_inject = 'component_new_bus_3_p_3' # Replace with actual bus key
    time_start_injection = 0.2
    time_end_injection = 0.3
    injection_tau = 0.03
    total_sim_time = 1
    time_step = 0.01

    time_array, Vcurve, Icurve = network_analyzer.calculate_time_domain_response(
        node_injection=node_to_inject,
        t_start=time_start_injection,
        t_end=time_end_injection,
        tau=injection_tau,
        tend=total_sim_time,
        deltaT=time_step
    )
    network_analyzer.res['Icurve'] = Icurve # Store Icurve in results for plotting
    print("步骤5：时域响应计算完成。")

    # 第六步：调用 plot_time_domain_voltage 函数，绘制时域电压曲线
    # Define target buses for plotting voltage. Replace with actual keys.
    plot_bus_key1 = 'component_new_bus_3_p_3'
    plot_bus_key2 = 'ef8377a5-b832-4b76-b025-a1dd380bd21a'
    network_analyzer.plot_time_domain_voltage(time_array, Vcurve, plot_bus_key1, plot_bus_key2)
    print("步骤6：时域电压曲线绘制完成。")

    # 第七步：调用 plot_frequency_domain_h_matrix_magnitude 函数，绘制 H 矩阵幅频响应曲线
    network_analyzer.plot_frequency_domain_h_matrix_magnitude(plot_bus_key1, plot_bus_key2)
    print("步骤7：H矩阵幅频响应曲线绘制完成。")

    # Optional: Additional plotting like current if needed
    # network_analyzer.plot_time_domain_current(time_array)
```