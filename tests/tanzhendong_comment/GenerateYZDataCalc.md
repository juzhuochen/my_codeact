# GenerateYZDataCalc.py程序的说明文档

## 一、功能描述
`GenerateYZDataCalc` 类实现的功能是针对电力系统进行频率扫描和稳定性分析，特别是为了研究电网中大型并网风电场接口处的阻抗和相位特性。该功能通过自动化在CloudPSS平台上运行一系列电磁暂态仿真，模拟在不同运行工况和系统参数配置下，向风电场注入谐波电流的情况，以此来获取系统对不同频率扰动的响应（即阻抗-频率特性曲线），最终将结果保存，供后续分析使用。它解决了手动进行大量仿真和数据处理的繁琐问题，并为电力系统稳定性评估提供了关键数据。

## 二、逻辑步骤及对应函数

1.  **初始化系统参数与环境配置**：在开始任何仿真之前，需要初始化CloudPSS平台的连接信息（如访问令牌、API地址、用户名和项目密钥）以及加载必要的组件库配置。同时，明确指定要进行频率扫描的目标模块及其端口，以及其他相关模块的标签。此外，需设定频率扫描模块的详细参数，包括注入谐波电流的幅值百分比，并确定结果数据的存储路径。最后，为了进行正交实验设计（OAT），定义一系列关键参数的取值范围或离散值，并生成所有待测试的实验案例集合。这些参数和配置将作为后续所有仿真工作的基础。
    *   **对应函数**：`GenerateYZDataCalc.__init__`

2.  **准备CloudPSS仿真平台环境与项目**：在执行具体仿真任务前，需要与CloudPSS平台建立连接，并设置项目操作所需的初始条件。这包括配置CloudPSS客户端的认证信息，以及在平台上创建一个用于仿真的画布。在此阶段，系统会识别出被测试组件和风力发电机组组件在项目中的唯一标识，为后续参数修改和模块添加做好准备。
    *   **对应函数**：`GenerateYZDataCalc.prepare_environment_and_project`

3.  **动态调整模型参数并集成扫频模块**：为了模拟不同运行工况和系统特性，需要根据当前实验案例的具体参数配置，动态修改CloudPSS项目中风力发电机组模块的各项参数，例如风机数量、有功/无功功率参考值、变压器电抗以及直流侧电压控制器的增益等。同时，在此步骤中，会在模型中集成一个谐波连续注入电流的扫频模块，该模块的注入电流幅值会根据风电场当前的运行功率进行计算和设定。扫频模块的引脚会被正确连接到被测试模块，并配置好所有需要进行数据输出的通道，以确保仿真结果的完整性。
    *   **对应函数**：`GenerateYZDataCalc.modify_model_parameters`

4.  **执行潮流计算与电磁暂态仿真**：在模型和参数准备就绪后，首先需要进行潮流计算以确定系统的稳态运行点。潮流计算成功收敛是后续电磁暂态仿真的前提，确保系统处于稳定状态。如果潮流计算不收敛，则说明当前参数配置下系统无法达到稳定运行，仿真会中止。潮流计算完成并回写数据后，系统会进一步启动电磁暂态（EMTP）仿真，该仿真将按照预设的扫频模块参数进行，模拟不同频率谐波注入时的系统动态响应，直至设定的仿真结束时间。此阶段的核心是获取系统在不同频率下的动态行为数据。
    *   **对应函数**：`GenerateYZDataCalc.run_simulations`

5.  **提取并解析仿真结果数据**：仿真完成后，需要从海量的仿真结果数据中精确提取出所需的阻抗和相位信息。这包括根据预设的扫频阶段和采样频率，从仿真结果中识别并抽取对应频率点下的阻抗幅值和相位角度数据。数据提取会针对正序、负序和零序分量分别进行，并通过对每个频率步长内的数据进行统计处理（例如求平均），以获得每个频率点唯一的阻抗和相位值，最终形成频率-阻抗-相位的完整特征曲线。
    *   **对应函数**：`GenerateYZDataCalc.process_simulation_results`

6.  **持久化仿真分析结果**：在完成所有数据提取和处理后，将当前实验案例下的频率、阻抗和相位数据以及本次实验所采用的所有OAT参数配置信息，按照预设的文件命名规范，以JSON格式保存到指定的输出路径。如果仿真过程中出现任何异常，错误信息也会被记录在结果文件中，以便后续的故障排查和分析。这一步骤确保了每一次实验的结果都被妥善存储，便于后续的数据分析、可视化和报告生成。
    *   **对应函数**：`GenerateYZDataCalc.save_results`

## 三、主要流程

```python
    #comment: 实例化 GenerateYZDataCalc 类。
    generator = GenerateYZDataCalc()

    #comment: 打印开始迭代的消息。
    print('Starting Iter...')

    #comment: 将 OATDict 和 OATCases 数据保存到 OAT.json 文件中。
    # 确保保存路径存在
    folder = os.path.exists(generator._output_path)
    if not folder:
        os.makedirs(generator._output_path)
    with open(generator._output_path + 'OAT.json', "w", encoding='utf-8') as f:
        f.write(json.dumps({'OATDict': generator._oat_dict, 'OATCases': generator._oat_cases}, indent=4, ensure_ascii=False))

    #comment: 遍历 OatCasess 中的每个实验案例。
    for oati in range(len(generator._oat_cases)):
    # for oati in range(13): # 用于调试，限制迭代次数
        current_oat_case = generator._oat_cases[oati]
        print(f"Processing OAT Case {oati+1}/{len(generator._oat_cases)}: {current_oat_case}")

        try:
            #comment: 第一步：调用 prepare_environment_and_project 函数，准备 CloudPSS 仿真环境。
            sa_instance, tested_key, wind_ge_key = generator.prepare_environment_and_project()

            #comment: 第二步：调用 modify_model_parameters 函数，根据当前实验案例修改模型参数并添加扫频模块。
            sa_instance, harm_id, output_channel_ids, time_end = generator.modify_model_parameters(
                sa_instance, tested_key, wind_ge_key, current_oat_case
            )

            #comment: 第三步：调用 run_simulations 函数，运行潮流计算和电磁暂态仿真。
            sa_result = generator.run_simulations(sa_instance, output_channel_ids, time_end)

            #comment: 第四步：调用 process_simulation_results 函数，处理仿真结果，提取频率、阻抗和相位数据。
            F, Z, Ph = generator.process_simulation_results(sa_result)

            #comment: 第五步：调用 save_results 函数，保存结果到 JSON 文件。
            generator.save_results(F, Z, Ph, current_oat_case, oati)

        except Exception as e:
            #comment: 捕获异常，并保存错误信息。
            print(f"Error processing OAT Case {oati}: {e}")
            generator.save_results(None, None, None, current_oat_case, oati, error_message=str(e))
        
        # 可选：清理 sa_instance 以释放资源或为下次迭代做准备
        # sa_instance.clear_project() # 假设StabilityAnalysis有这样的清理方法
```