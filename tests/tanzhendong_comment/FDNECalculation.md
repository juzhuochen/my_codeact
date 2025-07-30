# "FDNECalculation.py"程序的说明文档

## 一、功能描述（目标是什么）

该程序旨在实现基于频域数据的网络提取（FDNE）功能，通过向量拟合技术，将复杂的频域测量数据转换为紧凑的状态空间模型（State-Space Model）。这个模型可用于电路仿真、系统分析和信号完整性验证等领域。程序还包含了无源性强制执行（Passivity Enforcement）这一关键步骤，确保提取出的模型满足物理系统的无源性要求，从而避免仿真不稳定性和非物理现象。

## 二、逻辑步骤及对应函数（业务逻辑 + 函数映射）

1.  **数据初始化和默认配置：** 在启动所有功能之前，系统会初始化其内部状态，并设置一系列默认的操作参数，这些参数涵盖了数据处理、向量拟合算法以及无源性强制执行等方面的配置，为后续的计算提供基础设置。这些默认选项是可调整的，以适应不同的计算需求。
    （对应函数：`FDNECalculation.__init__` 和 `FDNECalculation._default_options`）

2.  **原始数据加载：** 接下来，需要从指定的文件中读取频域测量数据。该过程支持不同格式的输入，例如Y/Z参数或更复杂的Harm格式数据。系统会根据所选的格式解析文件内容，提取出频率信息以及相应的导纳（Y）或阻抗（Z）矩阵。如果输入是阻抗数据，系统会自动将其转换为导纳矩阵，以便后续的统一处理，为核心的向量拟合过程做好数据准备。
    （对应函数：`FDNECalculation.load_data`，`FDNECalculation._calculate_yz_data` 和 `FDNECalculation._load_harm_data`）

3.  **核心配置更新：** 在数据完全加载并准备就绪之后，为了确保计算过程能够精确地满足特定需求，系统允许用户在程序执行前调整其内部配置选项。这些可更新的参数包括但不限于向量拟合的细节（如是否启用渐进项、极点稳定性约束、绘图模式等）以及无源性强制执行的具体条件（如频率范围、迭代次数）。通过对这些参数的灵活配置，可以优化算法的性能和模型的准确性。
    （对应函数：通过直接修改`FDNECalculation.opts`属性来实现）

4.  **执行向量拟合（模型提取）：** 数据和配置都准备好后，系统会启动核心的向量拟合过程。首先，通过分析原始导纳矩阵（Y），寻找一个变换矩阵来优化其条件数，使得变换后的矩阵更易于处理。然后，利用先进的向量拟合算法对这个变换后的导纳矩阵进行拟合，目标是将其表示为一个紧凑的状态空间模型，该模型包含了系统的极点、残差以及常数项和线性项等关键参数。这一步是整个频域网络提取的核心，旨在于在高精度下捕捉系统的动态行为。
    （对应函数：`FDNECalculation.perform_vector_fitting`，`FDNECalculation._calculate_transform_matrix` 和 `FDNECalculation._vectorfit_yc`）

5.  **可选的无源性强制执行：** 在获得初步的状态空间模型后，为了确保该模型在物理上的合理性（即能够稳定地描述物理系统），系统可以选择性地执行无源性强制执行。这一过程会检查模型是否满足无源性条件，如果发现违反，则通过迭代优化算法对模型参数进行调整，直到模型满足无源性要求。这一步对于生成可用于仿真和分析的可靠模型至关重要，它能避免在后续应用中出现非物理行为或仿真不稳定。
    （对应函数：`FDNECalculation.enforce_passivity`）

6.  **结果输出：** 完成所有计算和优化之后，系统将最终的状态空间模型参数和相关的计算结果进行格式化。这些结果可以被整理成易于阅读的文本形式，也可以选择性地保存到指定的文件中。这为用户提供了清晰的模型摘要，方便进行后续的数据分析或与其他工具集成。
    （对应函数：`FDNECalculation.get_formatted_output` 和 `FDNECalculation.write_results_to_file`）

7.  **拟合结果可视化：** 最后，为了直观地评估模型的拟合质量和无源性强制执行的效果，系统提供了绘图功能。该功能能够绘制原始频域数据与拟合曲线的对比图，包括幅频特性和相频特性。通过对比，用户可以清晰地看到模型在宽频率范围内的准确性，以及无源性强制执行前后模型表现的变化，从而验证模型的有效性。
    （对应函数：`FDNECalculation.plot_fitting_results`）

## 三、主要流程（main 函数流程描述）

```python
    # 初始化 FDNE 计算器
    fdne_calculator = FDNECalculation()

    # 第一步：加载数据
    # 调用 load_data 方法，实现从文件加载S参数数据的功能。
    # 敏感信息替换：文件路径占位符
    fdne_calculator.load_data('./results/windFreqTest/Z_2023_11_23_16_19_52.txt', data_type='Y', data_format='YZ')
    print("第一步：数据加载完成。")

    # 第二步：更新配置选项
    # 调用 opts 属性，更新向量拟合和无源性强制执行的配置参数。
    # 根据实际需求调整这些参数
    fdne_calculator.opts['vfopts']['asymp']  = 1
    fdne_calculator.opts['vfopts']['relaxed']=True
    fdne_calculator.opts['vfopts']['stable']=True
    fdne_calculator.opts['vfopts']['spy2'] = True
    fdne_calculator.opts['vfopts']['spy1'] = False
    fdne_calculator.opts['vfopts']['errplot']=False
    fdne_calculator.opts['vfopts']['logx'] = True
    fdne_calculator.opts['vfopts']['logy'] = False
    fdne_calculator.opts['EigMaxIter'] = 20
    fdne_calculator.opts['EigEps'] = 1e-8
    fdne_calculator.opts['target_eps'] = 0.001
    fdne_calculator.opts['NpYc'] = 20
    fdne_calculator.opts['ErYc'] = 0.01
    fdne_calculator.opts['Weighting'] = [[0,1]]
    fdne_calculator.opts['WeightFactor'] = 0
    fdne_calculator.opts['NiterYc1'] = 5
    fdne_calculator.opts['NiterYc2'] = 3
    fdne_calculator.opts['ViewYcVF'] = True
    fdne_calculator.opts['EnabPassEnf'] = True  # Enable passivity enforcement
    fdne_calculator.opts['StartPass'] = 0
    fdne_calculator.opts['EndPass'] = 1e12
    fdne_calculator.opts['Nint'] = 20
    fdne_calculator.opts['Niter_out_Pass'] = 10
    fdne_calculator.opts['Niter_in_Pass'] = 2
    print("第二步：配置选项更新完成。")

    # 第三步：执行向量拟合
    # 调用 perform_vector_fitting 方法，实现对Y矩阵进行向量拟合的功能。
    fdne_calculator.perform_vector_fitting()
    print("第三步：向量拟合完成。")
    print(f"拟合结果均方根误差 (RMSErrYc): {fdne_calculator.calculation_results['RMSErrYc']}")

    # 第四步：执行无源性强制执行 (可选)
    # 调用 enforce_passivity 方法，实现对拟合模型进行无源性检查和强制的功能。
    # 仅当 opts['EnabPassEnf'] 为 True 时执行。
    fdne_calculator.enforce_passivity()
    print("第四步：无源性强制执行完成。")
    if fdne_calculator.rp_driver_log:
        print("无源性强制执行日志:", fdne_calculator.rp_driver_log)

    # 第五步：将结果写入文件
    # 调用 write_results_to_file 方法，实现将拟合数据写入特定格式文件的功能。
    # 敏感信息替换：文件路径占位符
    fdne_calculator.write_results_to_file('./results/windFreqTest/output_model.txt')
    print("第五步：结果写入文件完成。")

    # 第六步：绘制拟合结果
    # 调用 plot_fitting_results 方法，实现绘制原始数据与拟合曲线对比图的功能。
    fdne_calculator.plot_fitting_results(plot_before_passivity=True)
    print("第六步：拟合结果绘图完成。")
```