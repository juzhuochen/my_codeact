#comment: 导入 os 模块，用于操作系统相关功能
import os
#comment: 导入 pandas 库，用于数据处理和分析
import pandas as pd
#comment: 导入 time 模块，用于时间相关功能
import time
#comment: 导入 sys 模块，用于访问系统相关参数和函数
import sys

#comment: 导入 cloudpss 库，这是一个与 CloudPSS 平台交互的 SDK
import cloudpss
#comment: 导入 math 模块，提供数学函数
import math
#comment: 导入 cmath 模块，提供复数数学函数
import cmath
#comment: 导入 numpy 库，用于科学计算，特别是数组操作
import numpy as np
#comment: 从 numpy.linalg 导入 lg，用于线性代数操作
import numpy.linalg as lg
#comment: 导入 json 模块，用于 JSON 数据的编码和解码
import json
#comment: 导入 random 模块，用于生成随机数
import random
#comment: 导入 re 模块，用于正则表达式操作
import re
#comment: 导入 nest_asyncio 模块，用于在事件循环中嵌套运行异步代码
import nest_asyncio
#comment: 应用 nest_asyncio，允许嵌套使用 asyncio 事件循环
nest_asyncio.apply()
#comment: 导入 copy 模块，用于对象的复制
import copy
# comment: 从 cloudpss.runner.result 模块导入 Result, PowerFlowResult, EMTResult 类
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
# comment: 从 cloudpss.job.job 模块导入 Job 类，并重命名为 cjob
from cloudpss.job.job import Job as cjob

#comment: 定义一个函数 is_number，用于判断输入是否为数字
def is_number(s):
    #comment: 如果输入 s 是一个列表，则返回 False
    if(isinstance(s,list)):
        return False
    #comment: 尝试将 s 转换为浮点数
    try:
        float(s)
        #comment: 如果成功转换，则返回 True
        return True
    #comment: 捕获 ValueError 异常
    except ValueError:
        #comment: 如果发生 ValueError，则忽略
        pass

    #comment: 尝试使用 unicodedata 模块将 s 转换为数字
    try:
        import unicodedata
        unicodedata.numeric(s)
        #comment: 如果成功转换，则返回 True
        return True
    #comment: 捕获 TypeError 或 ValueError 异常
    except (TypeError, ValueError):
        #comment: 如果发生异常，则忽略
        pass

    #comment: 如果以上尝试都失败，则返回 False
    return False

#comment: 定义一个类 JudgeEMTPProblem_3，用于处理和分析 CloudPSS 平台上的电力系统模型
class JudgeEMTPProblem_3:
    """
    JudgeEMTPProblem_3 类用于封装电力系统EMTP仿真前的数据准备和模型处理逻辑。
    它负责初始化 CloudPSS API 客户端，获取项目模型，并根据特定条件对模型进行修改。

    属性:
        _token (str): CloudPSS API 的认证令牌。
        _api_url (str): CloudPSS API 的服务地址。
        _username (str): CloudPSS 平台的用户名。
        _project_key (str): 待处理的 CloudPSS 项目的唯一标识符。
        _project (cloudpss.Model): 从 CloudPSS 平台获取到的项目模型对象。
        _source_to_pcs (bool): 控制是否执行电压源转储能逻辑的标志。
        _pf_result_id (str): 如果 _source_to_pcs 为 True，则表示已存在的潮流计算结果ID，用于获取结果数据。
    """
    def __init__(self, token, api_url, username, project_key, source_to_pcs=False, pf_result_id=None):
        """
        初始化 JudgeEMTPProblem_3 类的实例。

        参数:
            token (str): CloudPSS API 的认证令牌。
            api_url (str): CloudPSS API 的服务地址。
            username (str): CloudPSS 平台的用户名。
            project_key (str): 待处理的 CloudPSS 项目的唯一标识符。
            source_to_pcs (bool, optional): 是否执行电压源转储能逻辑。默认为 False。
            pf_result_id (str, optional): 潮流计算结果ID，当 source_to_pcs 为 True 时必需。默认为 None。
        """
        self._token = token
        self._api_url = api_url
        self._username = username
        self._project_key = project_key
        self._project = None
        self._source_to_pcs = source_to_pcs
        self._pf_result_id = pf_result_id

    #comment: 初始化 CloudPSS SDK 和获取项目模型
    def initialize_cloudpss_env(self):
        """
        初始化 CloudPSS SDK 的认证信息，并从平台获取指定的项目模型。

        功能:
            设置 CloudPSS SDK 的认证 Token 和 API URL 环境变量。
            从 CloudPSS 平台获取并存储指定的项目模型。

        输入参数:
            无 (使用类实例属性 self._token, self._api_url, self._username, self._project_key)。

        输出结果:
            cloudpss.Model: 返回获取到的项目模型对象。
        """
        print('Setting CloudPSS environment...')
        cloudpss.setToken(self._token)
        os.environ['CLOUDPSS_API_URL'] = self._api_url
        self._project = cloudpss.Model.fetch(f'model/{self._username}/{self._project_key}')
        print(f"Project '{self._project_key}' fetched successfully.")
        return self._project

    #comment: 处理电压源转换为储能系统
    def process_voltage_source_to_pcs(self, project):
        """
        根据 _source_to_pcs 标志和潮流计算结果，将项目中的特定电压源组件转换为储能系统组件。
        此函数会读取潮流计算结果，并基于电压源的参数构建新的储能系统组件配置。

        功能:
            如果 self._source_to_pcs 为 True，则:
                1. 通过 self._pf_result_id 获取潮流计算结果。
                2. 遍历项目中的电压源组件 ('model/CloudPSS/_newACVoltageSource_3p')。
                3. 获取电压源的电压幅值 (Vm) 和相位 (Ph)。
                4. 构建一个储能系统 (PCS) 的组件配置 compJson。
                5. (代码块未完成转换逻辑，此处仅为示例性地定义 compJson)

        输入参数:
            project (cloudpss.Model): 待处理的项目模型对象。

        输出结果:
            dict: 返回处理后的组件信息，当前实现为一个示例 compJson，实际应返回修改后的项目或相关数据。
                  如果 _source_to_pcs 为 False，则返回 None。
        """
        if self._source_to_pcs:
            print(f"Processing voltage sources to PCS using PF Result ID: {self._pf_result_id}")
            if not self._pf_result_id:
                raise ValueError("PF Result ID must be provided when source_to_pcs is True.")

            # 获取作业对象
            job = cjob.fetch(self._pf_result_id)
            # 获取作业的结果
            # 注释：此处需要进一步检查 job.result 的类型，确保它是 PowerFlowResult
            # 如果 job.result 已经是 PowerFlowResult 类型，则直接使用
            # 否则，可能需要根据其原始数据类型进行转换或解析
            PFResult = job.result 
            if not isinstance(PFResult, PowerFlowResult):
                 # 示例：如果不是PowerFlowResult，尝试从原始数据创建
                 # 具体实现取决于 job.result 的实际结构
                 print(f"Warning: job.result is of type {type(PFResult)}, not PowerFlowResult. Attempting to convert or parse.")
                 # 假设PFResult的原始数据可以被PowerFlowResult解析
                 # 实际应用中需要根据Result对象的具体结构进行调整
                 try:
                     PFResult = PowerFlowResult(job.data) # 假设job.data包含了结果数据
                 except Exception as e:
                     print(f"Failed to convert job result to PowerFlowResult: {e}")
                     # 继续使用原始result，或者抛出异常，取决于需求
                     pass # 或者抛出错误

            #comment: 定义一个 compJson 字典，表示储能系统的组件配置
            compJson = {
                "args": {
                    "CMD_CH_HVRT_ENABLE": "0",
                    "CMD_CH_HVRT_Q_COEF": "1.5",
                    "CMD_CH_LVRT_ENABLE": "0",
                    "CMD_CH_LVRT_Q_COEF": "1.5",
                    "CMD_CH_ONOFF": "1",
                    "CMD_CH_PFSET": "1",
                    "CMD_CH_PSET": 0,
                    "CMD_CH_P_MODE": "1",
                    "CMD_CH_QSET": 0,
                    "CMD_CH_Q_MODE": "0",
                    "CMD_CH_UTL_OF_I_THRE": 1.02,
                    "CMD_CH_UTL_OF_I_TIME": 1000,
                    "CMD_CH_UTL_OV_II_THRE": 1.2,
                    "CMD_CH_UTL_OV_II_TIME": 10,
                    "CMD_CH_UTL_OV_I_THRE": 1.1,
                    "CMD_CH_UTL_OV_I_TIME": 10,
                    "CMD_CH_UTL_UF_I_THRE": 0.98,
                    "CMD_CH_UTL_UF_I_TIME": 1000,
                    "CMD_CH_UTL_UV_II_THRE": 0.5,
                    "CMD_CH_UTL_UV_II_TIME": 10,
                    "CMD_CH_UTL_UV_I_THRE": 0.7,
                    "CMD_CH_UTL_UV_I_TIME": 10,
                    "Num": "100",
                    "Vpcc": "230",
                    "init_cda_count": ""
                },
                "canvas": "canvas_0",
                "context": {},
                "definition": "model/admin/HW_PCS_TEST_Mask", # 替换为占位符
                "flip": False,
                "id": "component_hw_pcs_test_mask_1",
                "label": "储能系统1",
                "pins": {
                    "AC": "",
                    "P": "",
                    "Q": ""
                },
                "position": {
                    "x": 345,
                    "y": 635
                },
                "props": {
                    "enabled": True
                },
                "shape": "diagram-component",
                "size": {
                    "height": 40,
                    "width": 70
                },
                "style": {},
                "zIndex": 24
            }
            #comment: 遍历项目中所有 RID 为 'model/CloudPSS/_newACVoltageSource_3p' 的组件
            for i,j in project.getComponentsByRid('model/CloudPSS/_newACVoltageSource_3p').items():
                Vm = j.args['Vm']
                Ph = j.args['Ph']
                name = j.id
                print(f"Found voltage source: {name}, Vm: {Vm}, Ph: {Ph}")
                # 在这里可以根据Vm, Ph和PFResult的数据来修改compJson或者进行其他操作
                # 例如，如果要把Vsource替换为PCS，需要：
                # 1. 移除 Vsource
                # 2. 添加 PCS (compJson)
                # 3. 更新连接关系
                # 这些操作会非常复杂，此处仅作为示例性地指出，需要根据实际业务逻辑完成
                # project.removeComponent(j.id)
                # project.addComponent(compJson) # 这将需要一个将dict转换为Component对象的方法
            return compJson
        return None

#comment: 定义main函数，用于组织和执行业务逻辑
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
        api_url=API_URL_PLACEHOLDER,
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

#comment: 当脚本作为主程序运行时执行main函数
if __name__ == '__main__':
    main()