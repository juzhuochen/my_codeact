#comment: 导入 os 模块，用于操作系统相关功能，如文件路径操作
import os
#comment: 导入 pandas 库，用于数据处理和分析，主要用于创建和操作 DataFrame
import pandas as pd
#comment: 导入 time 模块，用于处理时间相关的功能，如暂停执行
import time
#comment: 导入 sys 模块，用于访问系统特定的参数和功能
import sys

#comment: 导入 cloudpss 库，用于与 CloudPSS 平台进行交互
import cloudpss
#comment: 导入 math 模块，用于数学运算，如平方根
import math
#comment: 导入 cmath 模块，用于复数数学运算
import cmath
#comment: 导入 numpy 库，用于科学计算，特别是数组和矩阵操作
import numpy as np
#comment: 导入 numpy.linalg 模块，用于线性代数运算，如求逆
import numpy.linalg as lg
#comment: 导入 jobApi1 模块中的特定函数，用于作业管理
from jobApi1 import fetch,fetchAllJob,abort
#comment: 从 cloudpss.runner.result 模块导入结果类，用于处理仿真结果
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 导入 json 模块，用于处理 JSON 数据格式
import json
#comment: 导入 random 模块，用于生成随机数
import random
#comment: 导入 re 模块，用于正则表达式操作
import re
#comment: 导入 nest_asyncio 模块，用于在事件循环中嵌套运行 asyncio
import nest_asyncio
#comment: 应用 nest_asyncio 补丁，允许在已经运行的事件循环中运行新的事件循环
nest_asyncio.apply()
#comment: 导入 copy 模块，用于对象的复制
import copy
#comment: 从 cloudpss.job.job 模块导入 Job 类并重命名为 cjob
from cloudpss.job.job import Job as cjob

#comment: 定义一个名为 is_number 的函数，用于判断输入是否为数字
def is_number(s):
    #comment: 检查输入 s 是否为列表类型，如果是则返回 False
    if isinstance(s, list):
        return False
    #comment: 尝试将 s 转换为浮点数
    try:
        float(s)
        #comment: 如果转换成功，则返回 True
        return True
    #comment: 捕获 ValueError 异常
    except ValueError:
        #comment: 如果发生 ValueError，则跳过
        pass

    #comment: 尝试使用 unicodedata 模块将 s 转换为数字
    try:
        import unicodedata
        unicodedata.numeric(s)
        #comment: 如果转换成功，则返回 True
        return True
    #comment: 捕获 TypeError 或 ValueError 异常
    except (TypeError, ValueError):
        #comment: 如果发生异常，则跳过
        pass

    #comment: 如果以上尝试都失败，则返回 False
    return False

#comment: 定义 JudgeEMTPProblem_4 类，用于封装 EMTP 问题处理的逻辑
class JudgeEMTPProblem_4:
    """
    JudgeEMTPProblem_4 类用于处理 CloudPSS 平台上的电力系统模型，特别是进行电力流结果的分析，
    并将电网模型中的电压源根据其功率输出转换为 PV 站或恒功率负载。

    属性:
    tk (str): CloudPSS 平台的认证 Token。
    apiURL (str): CloudPSS 平台的 API 接口地址。
    username (str): 用于访问 CloudPSS 平台的用户名称。
    projectKey (str): 待处理的电力系统模型的唯一标识符。
    PFResultID (str): 已经完成的电力流仿真结果的 Job ID。
    project (cloudpss.Model): 从 CloudPSS 平台获取到的模型对象。
    """
    def __init__(self, tk, apiURL, username, projectKey, PFResultID):
        #comment: 初始化 CloudPSS 的认证 token
        self.tk = tk
        #comment: 初始化 CloudPSS API 的 URL
        self.apiURL = apiURL
        #comment: 初始化用户名
        self.username = username
        #comment: 初始化项目键
        self.projectKey = projectKey
        #comment: 初始化电力流结果 ID
        self.PFResultID = PFResultID
        #comment: 初始化 project 为 None，将在后续方法中加载
        self.project = None

    def initialize_cloudpss_environment(self):
        """
        初始化 CloudPSS 环境，包括设置认证 Token 和 API URL。

        Args:
            无
        Returns:
            无
        """
        #comment: 使用设置的 token 配置 CloudPSS 认证
        cloudpss.setToken(self.tk)
        #comment: 设置环境变量 CLOUDPSS_API_URL
        os.environ['CLOUDPSS_API_URL'] = self.apiURL
        print('CloudPSS environment initialized.')

    def fetch_model_and_bus_data(self):
        """
        从 CloudPSS 平台获取指定项目键对应的模型，并解析电力流结果中的母线数据。

        Args:
            无
        Returns:
            tuple: 包含 (cloudpss.Model) project 对象 和 (dict) pfbus 母线数据字典。
        """
        #comment: 从 CloudPSS 平台获取指定项目键对应的模型
        self.project = cloudpss.Model.fetch('model/' + self.username + '/' + self.projectKey)
        print(f"Model '{self.projectKey}' fetched.")

        #comment: 使用 PFResultID 获取一个作业实例
        job = cjob.fetch(self.PFResultID)
        #comment: 获取作业的结果
        Result = job.result
        #comment: 暂停执行 1 秒，等待结果完全可用
        time.sleep(1)

        #comment: 初始化一个空字典用于存储电力流母线数据
        pfbus = {}
        #comment: 获取电力流结果中的母线数据列
        pfdata = Result.getBuses()[0]['data']['columns']
        #comment: 遍历电力流母线数据，将数据组织成以母线名为键的字典
        for i in range(len(pfdata[0]['data'])):
            #comment: 将每条母线的12个数据点存储到字典中，以母线名称为键
            pfbus[pfdata[0]['data'][i]] = [pfdata[j]['data'][i] for j in range(12)]
        print("Power flow bus data fetched and parsed.")
        return self.project, pfbus

    def map_bus_pins(self):
        """
        遍历项目中所有三相新母线组件，构建母线引脚（pin）到母线组件键的映射字典。

        Args:
            无
        Returns:
            dict: busPinDict，键为母线引脚ID，值为母线组件的键。
        """
        busPinDict = {}
        #comment: 遍历项目中所有 rid 为 'model/CloudPSS/_newBus_3p' 的组件，即三相新母线
        for i, j in self.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
            #comment: 将母线组件的引脚 '0' 映射到其组件键
            busPinDict[j.pins['0']] = i
        print("Bus pins mapped to component keys.")
        return busPinDict

    def convert_voltage_sources(self, pfbus, busPinDict):
        """
        根据电力流结果，将模型中的三相交流电压源转换为 PV 站或三相恒功率负载。

        Args:
            pfbus (dict): 包含电力流母线数据的字典。
            busPinDict (dict): 母线引脚到母线组件键的映射字典。
        Returns:
            cloudpss.Model: 更新后的 project 对象。
        """
        #comment: 再次获取当前的作业实例（避免数据陈旧，确保使用最新结果）
        job = cjob.fetch(self.PFResultID)
        #comment: 获取作业的电力流结果
        PFResult = job.result
        #comment: 遍历项目中所有 rid 为 'model/CloudPSS/_newACVoltageSource_3p' 的组件，即三相交流电压源
        for i, j in self.project.getComponentsByRid('model/CloudPSS/_newACVoltageSource_3p').items():
            #comment: 获取当前电压源组件的名称
            Name = j.args['Name']
            #comment: 如果组件名称包含 '等效'，则跳过本次循环
            if '等效' in Name:
                continue
            #comment: 获取标幺值电压幅值 Vm
            Vm = float(j.args['Vm'])
            #comment: 获取电压相角 Ph
            Ph = float(j.args['Ph'])
            #comment: 获取电压源连接的母线组件的键
            try:
                busi = busPinDict[j.pins['1']]
            except KeyError:
                print(f"Warning: Pin '1' for component {i} (voltage source) not found in busPinDict. Skipping conversion.")
                continue

            #comment: 根据母线组件的键获取母线组件对象
            buscomp = self.project.getComponentByKey(busi)
            if buscomp is None:
                print(f"Warning: Bus component {busi} not found for voltage source {i}. Skipping conversion.")
                continue

            #comment: 从电力流结果中获取连接母线的有功功率 Pg
            Pg = pfbus[busi][4]
            #comment: 从电力流结果中获取连接母线上的无功功率 Qg
            Qg = pfbus[busi][5]
            #comment: 计算视在功率 S，并放大 1.2 倍
            S = np.sqrt(Pg**2 + Qg**2) * 1.2
            #comment: 打印组件标签、键、有功功率和无功功率
            print(f"Processing voltage source: {j.label}, Key: {i}, Pg: {Pg}, Qg: {Qg}")
            #comment: 如果有功功率 Pg 大于 0，则转换为 PV 站
            if Pg > 0:
                #comment: 向项目中添加一个 PVStation 组件
                self.project.addComponent('model/CloudPSS/PVStation', j.label,
                                          {"Sbase": str(S), "Vrate": buscomp.args['VBase'],
                                           "PG0": str(Pg / S), "QG0": str(Qg / S), "Vt0": buscomp.args['V'],
                                           "Init_Phase": buscomp.args['Theta']},
                                          {"0": j.pins['1']}, canvas=j.canvas, position=j.position, size=None)
                print(f"Component {j.label} converted to PVStation.")
            #comment: 如果有功功率 Pg 小于 0，则转换为三相恒功率（ExpLoad）负载
            elif Pg < 0:
                #comment: 向项目中添加一个 _newExpLoad_3p 组件
                self.project.addComponent('model/CloudPSS/_newExpLoad_3p', j.label,
                                          {"v": buscomp.args['VBase'], "p": str(-Pg), "q": str(-Qg),
                                           "Vi": buscomp.args['V']},
                                          {"0": j.pins['1']}, canvas=j.canvas, position=j.position, size=None)
                print(f"Component {j.label} converted to _newExpLoad_3p.")
            #comment: 移除原始的电压源组件
            self.project.removeComponent(i)
            print(f"Original voltage source {i} removed.")
        return self.project

#comment: 主程序入口
def main():
    #comment: 打印开始信息
    print('Script Start')

    #comment: 定义敏感信息占位符
    auth_token = 'YOUR_CLOUD_PSS_AUTH_TOKEN'
    api_url = 'YOUR_CLOUD_PSS_API_URL'
    user_name = 'YOUR_USERNAME' #用户名
    project_key = 'YOUR_PROJECT_KEY'
    power_flow_result_id = 'YOUR_POWER_FLOW_RESULT_ID'

    #comment: 第一步：实例化 JudgeEMTPProblem_4 类，传入必要的初始化参数
    #comment: 负责创建一个处理EMTP问题的对象，并配置其与CloudPSS平台的连接信息。
    emtp_processor = JudgeEMTPProblem_4(auth_token, api_url, user_name, project_key, power_flow_result_id)
    print("Step 1: JudgeEMTPProblem_4 instance created.")

    #comment: 第二步：调用 initialize_cloudpss_environment 方法，初始化 CloudPSS 环境
    #comment: 负责设置CloudPSS的认证令牌和API地址，确保后续操作能正确连接到平台。
    emtp_processor.initialize_cloudpss_environment()
    print("Step 2: CloudPSS environment initialized.")

    #comment: 第三步：调用 fetch_model_and_bus_data 方法，获取模型和电力流母线数据
    #comment: 负责从CloudPSS平台加载指定的电力系统模型，并解析其电力流结果中的母线数据。
    project_model, pfbus_data = emtp_processor.fetch_model_and_bus_data()
    print("Step 3: Model and bus data fetched.")

    #comment: 第四步：调用 map_bus_pins 方法，构建母线引脚映射
    #comment: 负责识别模型中的母线组件，并创建从母线引脚到组件ID的映射，便于后续关联操作。
    bus_pin_mapping = emtp_processor.map_bus_pins()
    print("Step 4: Bus pins mapped.")

    #comment: 第五步：调用 convert_voltage_sources 方法，执行电压源转换
    #comment: 负责根据电力流结果，智能地将模型中的电压源替换为PV站或恒功率负载，调整模型拓扑。
    updated_project_model = emtp_processor.convert_voltage_sources(pfbus_data, bus_pin_mapping)
    print("Step 5: Voltage sources converted and model updated.")

    #comment: TODO: 这里可以添加保存或上传更新后模型的逻辑
    #comment: 例如：updated_project_model.save() 或 updated_project_model.upload()

    print('Script End')

if __name__ == '__main__':
    main()