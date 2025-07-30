# "Xinan_Short.py"程序的说明文档

## 一、功能描述

`Xinan_Short` 类是一个用于处理电力系统相关的 CloudPSS 仿真和潮流计算任务的工具。它封装了电磁暂态仿真和潮流计算的各个步骤，旨在简化用户与 CloudPSS 平台的交互，实现电力系统故障分析、潮流状态计算以及QSS数据导入等功能，从而支持电力系统运行和规划中的关键分析需求。

## 二、逻辑步骤及对应函数

1.  **环境和工具箱初始化：** 在执行任何电力系统仿真或计算任务之前，程序会首先加载电网元件库信息，并基于提供的访问凭证（如访问令牌、API 地址、用户名、项目密钥等）初始化一个电力系统分析工具箱。这一步骤确保了后续所有操作都能正确地与CloudPSS平台进行交互，并能识别和处理电网模型中的各种组件。（对应函数：`Xinan_Short.__init__`, `Xinan_Short._load_component_library`, `Xinan_Short._initialize_psa_toolbox`）

2.  **电磁暂态仿真准备：** 当需要进行电磁暂态仿真时，程序会首先初始化仿真环境并创建一个新的仿真画布。接着，它会根据用户指定的故障类型、故障线路名称、故障发生在线路的侧别以及故障的起始和清除时间，在电力系统模型中设置N-1接地故障。随后，程序会识别与故障线路相关的其他线路，并为这些线路添加三相瞬时电流和电流有效值的测量通道，以便在仿真过程中监测关键电气量。最后，系统会配置并保存电磁暂态仿真作业，以备后续执行。（对应函数：`Xinan_Short.prepare_emt_simulation`）

3.  **运行电磁暂态仿真：** 在电磁暂态仿真作业配置完成后，程序将启动该仿真。在仿真执行期间，程序会持续监测仿真进度，并定期刷新作业状态以防止超时。它还会实时获取仿真结果，包括绘图通道的数据，并将收到的消息（例如仿真过程中的日志和事件）打印出来，直到仿真任务完全结束。（对应函数：`Xinan_Short.run_emt_simulation`）

4.  **执行潮流计算：** 为了分析电力系统的稳态运行情况，程序可以执行潮流计算。它通过调用外部模块中的特定函数来启动潮流计算过程，在计算完成后，会读取并解析一个包含潮流计算结果的文件。该文件中的数据，例如母线电压、相角以及有功和无功不平衡量，将被格式化成表格，并展示到用户界面上，以便进行与原始QS数据或仿真结果的对比。（对应函数：`Xinan_Short.perform_power_flow_calculation`）

5.  **导入 QS 数据：** 在进行电力系统分析之前，可能需要将现有的电力系统数据（通常以 QS 格式存储）导入到CloudPSS项目中。程序会调用一个专门的外部模块函数来完成这一数据导入操作，将 QS 文件中的电网拓扑、元件参数等信息加载到当前工作项目中，为后续的仿真和计算任务提供基础数据。（对应函数：`Xinan_Short.import_qs_data`）

## 三、主要流程

```python
    # 获取当前的 CloudPSS 作业实例
    job = cloudpss.currentJob()
    
    # 初始化敏感信息，使用占位符
    token_val = TOKEN_PLACEHOLDER
    api_url_val = API_URL_PLACEHOLDER
    username_val = USERNAME_PLACEHOLDER
    # 从作业参数中获取 projectKey，如果不存在则使用占位符
    project_key_val = job.args.get('projectKey', PROJECT_KEY_PLACEHOLDER)
    qspath_val = QS_FILES_PATH_PLACEHOLDER

    # 创建 Xinan_Short 类的实例
    xinan_processor = Xinan_Short(job, token_val, api_url_val, username_val, project_key_val, qspath_val)

    # 检查作业参数 'Type' 的值，执行不同的业务逻辑
    # 如果脚本作为主程序运行
    if __name__ == '__main__':
        if str(job.args.get('Type','1')) == "0":
            # 第一步：获取电磁暂态仿真参数
            # 从作业参数 'FT1' 中获取故障类型，默认为 "ABC"
            fault_type = job.args.get('FT1', 'ABC')
            # 从作业参数 'LineName1' 中获取线路名称，默认为 'AC407567'
            line_name = job.args.get('LineName1', LINE_NAME_PLACEHOLDER)
            # 从作业参数 'Side1' 中获取故障侧，默认为 '0'
            side = job.args.get('Side1', '0')
            # 从作业参数 'Ts1' 中获取故障开始时间，默认为 '3'
            ts = job.args.get('Ts1', '3')
            # 从作业参数 'Tc1' 中获取故障清除时间，默认为 '3.06'
            tc = job.args.get('Tc1', '3.06')          

            # 第二步：准备电磁暂态仿真
            emt_job_config = xinan_processor.prepare_emt_simulation(fault_type, line_name, side, ts, tc)

            # 第三步：运行电磁暂态仿真
            xinan_processor.run_emt_simulation(emt_job_config)

        elif str(job.args.get('Type','1')) == "1":
            # 第一步：执行潮流计算
            xinan_processor.perform_power_flow_calculation()

        elif str(job.args.get('Type','1')) == "99":
            # 第一步：导入 QS 数据
            xinan_processor.import_qs_data()
        
        else:
            job.log(f"Unknown 'Type' parameter: {job.args.get('Type','1')}. No action performed.")
```