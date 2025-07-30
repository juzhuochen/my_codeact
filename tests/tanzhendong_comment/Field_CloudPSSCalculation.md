# "Field_CloudPSSCalculation.py"程序的说明文档

## 一、功能描述

`Field_CloudPSSCalculation.py` 程序旨在实现一个自动化流程，用于在CloudPSS平台上执行场路耦合仿真。它通过集成模型配置、Exchange元件的导入与连接、仿真运行、结果数据的处理以及与外部有限元（FE）计算的交互，解决了不同仿真软件间数据传递和协同仿真的问题。

## 二、逻辑步骤及对应函数

1.  **准备环境与工具**: 在进行任何仿真操作之前，需要创建一个专门用于管理CloudPSS平台交互的实例。此步骤将使用提供的凭据（如认证令牌、API地址、用户名）和项目信息（项目密钥）来初始化内部工具箱，并加载仿真所需的组件库，为后续在CloudPSS上执行仿真任务打下基础。
    （对应函数：`Field_CloudPSSCalculation.initialize_cloudpss_toolbox`）

2.  **导入外部耦合模型**: 为了实现场路耦合，系统需要将预先定义的外部耦合模型（以Exchange JSON文件形式存在）整合到CloudPSS仿真项目中。此过程包括读取这些JSON文件，解析其中定义的输入输出参数，然后动态地在CloudPSS画布上创建对应的Exchange元件，以及用于数据分发和汇聚的辅助元件（分线器和集线器），并自动建立它们之间的连接，确保数据流的正确性。
    （对应函数：`Field_CloudPSSCalculation.import_exchange_components`）

3.  **保存仿真项目**: 在完成所有模型元件的添加和连接后，必须将当前在本地构建的仿真项目结构保存到CloudPSS平台。这一步是将配置好的模型持久化到云端，以便后续可以进行仿真运行，确保所有模型设置和连接关系都被正确记录。
    （对应函数：`Field_CloudPSSCalculation.save_cloudpss_project`）

4.  **执行云端仿真**: 一旦仿真项目成功保存到CloudPSS平台，就可以启动实际的仿真计算。此步骤会配置Exchange元件的输出通道以捕获关键数据，然后触发CloudPSS平台上的仿真作业。仿真完成后，系统会自动从仿真结果中提取出与Exchange元件相关的输入数据，并将其处理后保存为本地的CSV文件，以便进行后续分析或作为其他工具的输入。
    （对应函数：`Field_CloudPSSCalculation.run_cloudpss_simulation`）

5.  **启动有限元分析**: 场路耦合需要有限元计算来验证和完善。在CloudPSS仿真结果产生后，系统将调用一个独立的外部Python脚本来执行有限元分析。这个外部脚本会利用之前仿真生成的关键数据作为输入，执行其自身的计算逻辑。这一步是实现整个场路耦合循环的关键环节，其结果将影响后续的迭代。
    （对应函数：`Field_CloudPSSCalculation.run_finite_element_calculation`）

## 三、主要流程

```python
    print('Starting the main workflow.')

    # 替换敏感信息为占位符
    token_placeholder = 'CLOOUDPSS_TOKEN_PLACEHOLDER'
    api_url_placeholder = 'CLOUDPSS_API_URL_PLACEHOLDER'
    username_placeholder = 'CLOUDPSS_USERNAME_PLACEHOLDER'
    project_key_placeholder = 'CLOUDPSS_PROJECT_KEY_PLACEHOLDER'
    fe_python_path_placeholder = 'FE_PYTHON_EXE_PATH_PLACEHOLDER' # 例如 D:/Simdroid/bin/python.exe
    fe_main_script_placeholder = './CloudPassMain0129.py' # 有限元计算主脚本路径
    fe_input_data_path_placeholder = './data/New电缆迭代步模型_调控闭环.ibe' # 有限元计算输入数据路径
    fe_param_placeholder = '1' # 有限元计算参数

    #comment: 定义Exchange文件的路径列表
    exchange_files_list = ['./Exchange_cable.json']

    # comment: 第一步：创建 Field_CloudPSSCalculation 类的实例
    # 实例化类，传入所有必要参数，敏感信息使用占位符
    cloudpss_calculator = Field_CloudPSSCalculation(
        token=token_placeholder,
        api_url=api_url_placeholder,
        username=username_placeholder,
        project_key=project_key_placeholder,
        exchange_models_rid='model/admin/model_exchange', # 示例RID，如果需要也替换为占位符
        job_name='电磁暂态仿真方案 1', # 仿真作业名称
        config_name='参数方案 1', # 仿真配置名称
        fe_python_path=fe_python_path_placeholder,
        fe_main_script=fe_main_script_placeholder,
        fe_input_data_path=fe_input_data_path_placeholder,
        fe_param=fe_param_placeholder
    )
    print("Step 1: Initialized Field_CloudPSSCalculation instance.")

    # comment: 第二步：初始化 CloudPSS Toolbox
    # 配置与CloudPSS平台交互所需的工具箱
    cloudpss_calculator.initialize_cloudpss_toolbox()
    print("Step 2: CloudPSS Toolbox initialized.")

    # comment: 第三步：导入 Exchange 元件到 CloudPSS 模型
    # 将预定义的Exchange模型文件导入到CloudPSS的仿真项目中，并生成对应的分线器、集线器和连接关系
    ex_model_ids = cloudpss_calculator.import_exchange_components(exchange_files_list)
    print(f"Step 3: Exchange components imported. Model IDs: {ex_model_ids}")

    # comment: 第四步：保存 CloudPSS 项目
    # 将当前配置好的项目保存到CloudPSS平台，以便后续仿真
    cloudpss_calculator.save_cloudpss_project()
    print("Step 4: CloudPSS project saved.")

    # comment: 第五步：运行 CloudPSS 仿真
    # 启动在CloudPSS平台上配置好的仿真作业，并处理仿真结果，将特定输出保存到本地CSV文件
    cloudpss_calculator.run_cloudpss_simulation()
    print("Step 5: CloudPSS simulation completed and results processed.")

    # comment: 第六步：运行有限元计算
    # 调用外部程序执行有限元分析，该程序将使用仿真结果作为输入
    return_code, output = cloudpss_calculator.run_finite_element_calculation()
    print(f"Step 6: Finite element calculation completed with return code {return_code}.")
    # print(f"FE Calculation Output:\n{output}") # 可以选择打印完整输出

    print("Main workflow completed successfully.")
```