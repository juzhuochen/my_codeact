# JudgeEMTPProblem_3.py 程序的说明文档

## 一、功能描述

该程序旨在为电力系统EMTP（电磁暂态）仿真进行数据准备和模型处理。它通过与CloudPSS平台交互，获取指定的项目模型，并能根据特定业务需求（例如将电压源转换为储能系统）对模型进行修改，最终为仿真提供准备好的模型数据。其核心功能是自动化电力系统模型的配置和转换，特别是针对分布式能源接入场景。

## 二、逻辑步骤及对应函数

### 1. 初始化程序并配置环境参数

在程序执行的初始阶段，需要准备好所有必要的配置信息，包括CloudPSS平台的认证令牌、API服务地址、您的用户名以及要操作的特定项目标识符。此外，还会确定是否需要执行特定的模型转换逻辑（例如将电压源转换为储能系统），如果需要，还需要提供潮流计算结果的ID，以便后续获取必要的运行数据来指导转换过程。这些参数的设置确保了程序能够正确地连接到CloudPSS平台并了解其后续操作的具体业务需求。

（对应函数：`JudgeEMTPProblem_3.__init__`）

### 2. 连接CloudPSS平台并获取项目模型

在完成初始化参数配置后，程序会利用这些配置信息与CloudPSS平台建立连接。它会设置必要的认证信息，确保具有访问平台的权限，然后通过指定的项目标识符从平台获取该项目的完整模型数据。这一步骤是后续所有模型操作的基础，确保程序能够访问和修改正确的模型结构。

（对应函数：`JudgeEMTPProblem_3.initialize_cloudpss_env`）

### 3. 根据潮流结果进行电压源组件的改造

如果之前配置了将电压源转换为储能系统的逻辑并且提供了有效的潮流计算结果ID，程序将进入电压源改造阶段。此时，程序会首先通过提供的潮流计算结果ID获取之前仿真计算出的详细潮流数据。接着，它会遍历项目中所有的三相交流电压源组件，获取其电压幅值和相位等参数。在此基础上，程序会基于这些参数和潮流计算结果，构建一个符合储能系统（PCS）特性的组件配置。尽管当前代码示例仅展示了配置结构，实际业务逻辑将在此处完成电压源组件的移除和对应储能系统组件的添加，并更新相关的连接关系，从而实现模型层面的功能替换。

（对应函数：`JudgeEMTPProblem_3.process_voltage_source_to_pcs`）

## 三、主要流程

```python
def main():
    #comment: 打印启动信息
    print('Starting main script...')

    #comment: 定义占位符敏感数据
    TOKEN_PLACEHOLDER = 'YOUR_CLOUD_PSS_TOKEN_HERE'
    API_URL_PLACEHOLDER = 'http://cloudpss-api-url.com/' # 替换为具体API地址或占位符
    USERNAME_PLACEHOLDER = 'your_username'
    PROJECT_KEY_PLACEHOLDER = 'YOUR_PROJECT_KEY_HERE'
    PF_RESULT_ID_PLACEHOLDER = 'YOUR_POWER_FLOW_RESULT_ID_HERE' # 替换为具体结果ID或占位符

    #comment: 初始化 JudgeEMTPProblem_3 类的实例
    # 第一步：初始化类实例，包含所有配置参数
    print("\n第一步：初始化 JudgeEMTPProblem_3 类的实例，并配置相关参数。")
    # 可以根据需要调整 source_to_pcs 和 pf_result_id 的值
    # 如果 source_to_pcs 为 False，则 pf_result_id 可以为 None
    # 如果 source_to_pcs 为 True，则 pf_result_id 必须是一个有效的 ID
    source_to_pcs_flag = True # 示例：设置为 True 来演示电压源转储能部分
    instance = JudgeEMTPProblem_3(
        token=TOKEN_PLACEHOLDER,
        api_url=API_URL_PLACEHHER,
        username=USERNAME_PLACEHOLDER,
        project_key=PROJECT_KEY_PLACEHOLDER,
        source_to_pcs=source_to_pcs_flag,
        pf_result_id=PF_RESULT_ID_PLACEHOLDER if source_to_pcs_flag else None
    )

    # 第二步：初始化 CloudPSS 环境，并获取项目模型
    print("\n第二步：调用 initialize_cloudpss_env 函数，设置 CloudPSS SDK 并获取指定的项目模型。")
    project_model = instance.initialize_cloudpss_env()
    print(f"Project model obtained: {project_model.name}")

    # 第三步：处理电压源转换为储能系统（如果 enabled）
    print("\n第三步：调用 process_voltage_source_to_pcs 函数，根据配置处理电压源到储能系统的转换逻辑。")
    processed_component_info = instance.process_voltage_source_to_pcs(project_model)
    if processed_component_info:
        print("Voltage source to PCS processing initiated. Example component info:", processed_component_info)
    else:
        print("Voltage source to PCS processing skipped (Source2PCS is False).")

    # comment: 这里可以添加更多的业务逻辑步骤，例如：
    # 第四步：进行其他模型修改或验证
    # print("\n第四步：执行其他模型修改或验证功能。")
    # instance.some_other_model_modification(project_model)

    # 第五步：保存修改后的模型（如果模型有变动）
    # print("\n第五步：保存修改后的项目模型到CloudPSS平台。")
    # if project_model.has_changes():
    # project_model.save()
    # print("Project model saved.")

    # 第六步：触发仿真任务或后续分析
    # print("\n第六步：触发EMT仿真任务或进行后续分析。")
    # instance.trigger_emt_simulation(project_model)

    print('\nMain script finished.')
```