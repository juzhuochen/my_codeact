import S_S_SyncComp as SA
import cloudpss
import os
import time
import json
import re
import numpy as np
import numpy.linalg as LA
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from scipy import interpolate
import pandas as pd
import tkinter
import tkinter.filedialog
import math
from IPython.display import HTML
from html import unescape
import random
import copy
from cloudpss.model.implements.component import Component
from cloudpss.runner.result import (Result, PowerFlowResult, EMTResult)
from cloudpss.model.revision import ModelRevision
from cloudpss.model.model import Model
from scipy import optimize
from cloudpss.job.job import Job as cjob
import nest_asyncio

# 应用 nest_asyncio 补丁，允许在已运行的事件循环中嵌套 asyncio 事件循环。
nest_asyncio.apply()

# 定义占位符字符串
PLACEHOLDER_TOKEN = "YOUR_AUTH_TOKEN"
PLACEHOLDER_API_URL = "YOUR_API_URL"
PLACEHOLDER_USERNAME = "YOUR_USERNAME"
PLACEHOLDER_PROJECT_KEY = "YOUR_PROJECT_KEY"

class Xinan_SyncAnalysis_4:
    """
    Xinan_SyncAnalysis_4 类用于封装西南电网的电磁暂态仿真分析流程。
    它集成了CloudPSS平台的交互、模型配置、仿真执行、结果处理和可视化等功能。

    属性:
    - token (str): CloudPSS 认证令牌。
    - api_url (str): CloudPSS API 的 URL。
    - username (str): CloudPSS 用户名。
    - project_key (str): CloudPSS 项目密钥。
    - sa (SA.S_S_SyncComp): S_S_SyncComp 模块的实例，用于与 CloudPSS 平台进行交互。
    - comp_lib (dict): 从 'saSource.json' 文件加载的组件库配置。
    - result_path (str): 仿真结果存储的根路径。
    - emtp_job_name (str): 电磁暂态仿真作业的名称。
    """

    def __init__(self, token, api_url, username, project_key, comp_lib_path='saSource.json'):
        """
        初始化 Xinan_SyncAnalysis_4 类的实例。

        参数:
        - token (str): CloudPSS 认证令牌。
        - api_url (str): CloudPSS API 的 URL。
        - username (str): CloudPSS 用户名。
        - project_key (str): CloudPSS 项目密钥。
        - comp_lib_path (str): 组件库 JSON 文件的路径。
        """
        #comment: 定义 CloudPSS 的认证 token。
        self.token = token
        #comment: 定义 CloudPSS API 的 URL。
        self.api_url = api_url
        #comment: 定义 CloudPSS 用户名。
        self.username = username
        #comment: 定义 CloudPSS 项目密钥。
        self.project_key = project_key
        self.sa = None
        self.comp_lib = self._load_comp_lib(comp_lib_path)
        self.result_path = ''
        self.emtp_job_name = 'SA_电磁暂态仿真'

    def _load_comp_lib(self, path):
        """
        私有方法：从 JSON 文件加载组件库。

        参数:
        - path (str): 组件库 JSON 文件的路径。

        返回:
        - dict: 加载的组件库内容。
        """
        #comment: 打开 'saSource.json' 文件并加载 JSON 内容到 compLib 变量。
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)

    def initialize_cloudpss_env(self):
        """
        初始化 CloudPSS 环境，包括设置 token、API URL，并配置 SA 实例。

        无参数。

        无返回。
        """
        #comment: 设置 CloudPSS 的认证 token。
        cloudpss.setToken(self.token)
        #comment: 设置 CLOUDPSS_API_URL 环境变量。
        os.environ['CLOUDPSS_API_URL'] = self.api_url

        #comment: 打印初始化消息。
        print('正在进行初始化...')
        #comment: 创建 S_S_SyncComp 类的实例。
        self.sa = SA.S_S_SyncComp()
        #comment: 配置 SA 实例的 token、API URL、用户名和项目密钥。
        self.sa.setConfig(self.token, self.api_url, self.username, self.project_key)
        #comment: 设置 SA 实例的初始条件。
        self.sa.setInitialConditions()
        #comment: 创建 SA 实例的画布。
        self.sa.createSACanvas()
        #comment: 创建 SA 实例的 SSSCACanvas。
        self.sa.createSSSCACanvas()

        #comment: 创建一个名为 'SA_潮流计算' 的电力潮流计算任务。
        self.sa.createJob('powerFlow', name='SA_潮流计算')
        #comment: 创建一个名为 'SA_参数方案' 的配置。
        self.sa.createConfig(name='SA_参数方案')

        #comment: 构建结果文件路径。
        self.result_path = 'results/' + self.project_key + '/SSresults_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '/'
        #comment: 检查路径是否存在。
        folder = os.path.exists(self.result_path)
        #comment: 如果文件夹不存在，则创建它。
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            #comment: 创建文件夹，包括所有缺失的父目录。
            os.makedirs(self.result_path)            #makedirs 创建文件时如果路径不存在会创建这个路径
        print(f"初始化完成，结果将保存到: {self.result_path}")

    def configure_fault_and_simulation(self, fault_type='N-1_ground', fault_args=None, end_time=10):
        """
        配置故障场景并设置电磁暂态仿真作业。

        参数:
        - fault_type (str): 故障类型，可选 'N-1_ground' (单相接地故障) 或 'N-2_ground' (两相接地故障)。
        - fault_args (dict): 故障的特定参数，例如线路ID、故障位置、起始时间、结束时间和故障阻抗。
                             对于 'N-1_ground': {'component_id': str, 'fault_location': float, 'start_time': float, 'end_time': float, 'impedance': float}
                             对于 'N-2_ground': {'component_id_1': str, 'component_id_2': str, 'fault_location': float, 'start_time': float, 'end_time': float, 'impedance': float}
        - end_time (int): 仿真结束时间。

        无返回。
        """
        #comment: 设置故障部分
        if fault_type == 'N-1_ground':
            #comment: 设置单相接地故障，指定传输线路、故障位置、故障起始时间、结束时间和故障阻抗。
            # 默认参数以匹配原脚本，可根据fault_args覆盖
            comp_id = fault_args.get('component_id', 'comp_TranssmissionLineRouter_4106')
            loc = fault_args.get('fault_location', 0)
            start_t = fault_args.get('start_time', 4)
            end_t = fault_args.get('end_time', 4.1)
            imp = fault_args.get('impedance', 7)
            self.sa.setN_1_GroundFault(comp_id, loc, start_t, end_t, imp)
            print(f"已设置单相接地故障: {comp_id} 在 {loc} 处从 {start_t} 到 {end_t} with {imp} Ohm")
        elif fault_type == 'N-2_ground':
            #comment: 设置两相接地故障。注意：这里是注释掉的。
            # self.sa.setN_2_GroundFault('comp_TranssmissionLineRouter_705','comp_TranssmissionLineRouter_706',1,4,4.1,7)
            comp_id_1 = fault_args.get('component_id_1', 'comp_TranssmissionLineRouter_705')
            comp_id_2 = fault_args.get('component_id_2', 'comp_TranssmissionLineRouter_706')
            loc = fault_args.get('fault_location', 1)
            start_t = fault_args.get('start_time', 4)
            end_t = fault_args.get('end_time', 4.1)
            imp = fault_args.get('impedance', 7)
            self.sa.setN_2_GroundFault(comp_id_1, comp_id_2, loc, start_t, end_t, imp)
            print(f"已设置两相接地故障: {comp_id_1} 和 {comp_id_2} 在 {loc} 处从 {start_t} 到 {end_t} with {imp} Ohm")
        else:
            print("未知的故障类型，未设置故障。")

        #comment: 设置仿真作业及其输出通道信息
        #comment: 定义仿真结束时间。
        timeend = end_time
        #comment: 创建一个名为 jobName 的电磁暂态仿真作业，并设置仿真参数。
        self.sa.createJob('emtp', name = self.emtp_job_name, args = {'begin_time': 0,'end_time': timeend,'step_time': 0.00005,\
            #comment: 'task_queue': 'taskManager_turbo1','solver_option': 7,'n_cpu': 16}) # 任务队列、求解器选项、CPU核数，这里是注释掉的备选配置
               'task_queue': 'taskManager','solver_option': 7,'n_cpu': 32}) # 实际使用的任务队列、求解器选项、CPU核数
        print(f"已配置电磁暂态仿真作业: {self.emtp_job_name}, 结束时间: {timeend}s")

    def add_measurements(self, bus_id_prefix='川'):
        """
        添加仿真过程中的测量点，特别是总线电压测量。

        参数:
        - bus_id_prefix (str): 用于筛选总线的标签前缀。

        返回:
        - list: 添加的电压测量点的关键ID列表。
        """
        #comment: 初始化一个空列表来存储关键信息。
        keys = []
        #comment: 遍历项目中所有 RID 为 'model/CloudPSS/_newBus_3p' 的组件。
        for ii, jj in self.sa.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
            #comment: 如果组件的标签字符以 '川' 开头，将其键添加到 keys 列表中。
            if(bus_id_prefix in jj.label[:len(bus_id_prefix)]):
                keys.append(ii)
        #comment: 添加电压测量，设置名称、最小/最大电压、频率、绘图名称和关键点。
        measuredBus = self.sa.addVoltageMeasures(self.emtp_job_name, VMin=0.5, VMax=1100, freq=100, PlotName='220kV以上电压曲线', Keys=keys)
        print(f"已添加电压测量点，共 {len(measuredBus)} 个")

        #comment: 添加组件引脚输出测量（有功功率），指定作业名称、组件 RID、引脚名称、绘图名称和频率。注意：这里是注释掉的。
        # self.sa.addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'P', [], plotName = '储能有功功率曲线', freq = 200)
        #comment: 添加组件引脚输出测量（无功功率）。注意：这里是注释掉的。
        # self.sa.addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'Q', [], plotName = '储能无功功率曲线', freq = 200)

        return measuredBus

    def run_emtp_simulation(self):
        """
        执行电磁暂态仿真作业。

        无参数。

        返回:
        - Result: 仿真运行结果对象。
        """
        #comment: 打印开始仿真消息。
        print('开始仿真...')
        #comment: 运行电磁暂态仿真。
        self.sa.runProject(self.emtp_job_name, 'SA_参数方案')
        #comment: 打印仿真完成和数据存储消息。
        print('仿真完成，正在存储数据...')

        #comment: 将仿真结果 dump 到文件。注意：这里是注释掉的。
        # Result.dump(sa.runner.result,self.result_path+'/SSresult_'+ str(0) +'.cjob')
        #comment: 获取仿真运行器的 ID。
        ss_result_id = self.sa.runner.id
        #comment: 打印仿真结果 ID。
        print(f"仿真结果ID: {ss_result_id}")
        #comment: 获取仿真运行器的结果。
        ss_result = self.sa.runner.result
        #comment: 打印数据存储完成消息。
        print('数据存储完成...')
        return ss_result

    def analyze_and_visualize_results(self, ss_result):
        """
        分析仿真结果，计算电压偏差并进行可视化。

        参数:
        - ss_result (Result): 仿真运行结果对象。

        无返回。
        """
        #comment: 定义判断标准，包含时间段、电压下限和上限。
        # judgement = [[0,0.5,0.2,1.2],[0.5,1,0.2,1.15],[1,2,0.391,1.1],[2,999,0.9,1.1]]
        #comment: 备用判断标准，注释掉。
        # judgement = [[0,0.5,0.2,1.1],[0.5,1,0.2,1.1],[1,2,0.391,1.1],[2,999,0.9,1.1]]
        #comment: 最终使用的判断标准。
        judgement = [[0.5, 3, 0.8, 1.2], [3, 999, 0.95, 1.05]]
        #comment: 计算电压偏差，获取电压上限偏差、电压下限偏差和有效数量。
        dVUj, dVLj, ValidNumI = self.sa.calculateDV(self.emtp_job_name, 0, result=ss_result, Ts=4, dT0=0.5, judge=judgement, VminR=0.5, VmaxR=1.5)
        #comment: 找出电压上限偏差小于 0 的索引。
        mm = [i for i in range(len(dVUj)) if dVUj[i] < 0]
        #comment: 找出电压下限偏差小于 0 的索引。
        nn = [i for i in range(len(dVLj)) if dVLj[i] < 0]
        #comment: 打印电压上限偏差小于 0 的索引。
        print(f"电压上限偏差小于0的索引: {mm}")
        #comment: 打印电压下限偏差小于 0 的索引。
        print(f"电压下限偏差小于0的索引: {nn}")

        #comment: 创建一个 Plotly Figure 对象。
        fig = go.Figure()
        #comment: 初始化计数器 k。
        k = 0
        #comment: 获取绘图通道名称。
        ckeytemp = ss_result.getPlotChannelNames(k)

        #comment: 遍历 mm 中指定的通道键。
        print("以下是电压不合格点的曲线:")
        for pk in [ckeytemp[i] for i in mm]:
        #comment: 遍历所有通道键。注意：这里是注释掉的。
        # for pk in ckeytemp:
            #comment: 如果通道名称不包含 '北塔'，则跳过。注意：这里是注释掉的。
            # if('北塔' not in pk):
            #     continue
            #comment: 获取通道的 x 轴数据。
            x = ss_result.getPlotChannelData(k, pk)['x']
            #comment: 获取通道的 y 轴数据。
            y = ss_result.getPlotChannelData(k, pk)['y']
            #comment: 向图表添加散点图轨迹，设置 x、y 值、模式和名称。
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
        #comment: 显示图表。
        fig.show()

#comment: 主函数，用于串联所有操作。
def main():
    """
    主函数：执行西南同步分析的完整业务流程。
    """
    # comment: 定义 CloudPSS 的认证 token。
    tk = PLACEHOLDER_TOKEN
    # comment: 定义 CloudPSS API 的 URL。
    apiURL = PLACEHOLDER_API_URL
    # comment: 定义 CloudPSS 用户名。
    username = PLACEHOLDER_USERNAME
    # comment: 定义 CloudPSS 项目密钥。
    projectKey = PLACEHOLDER_PROJECT_KEY

    # 初始化分析器
    # 第一步：创建 Xinan_SyncAnalysis_4 对象，初始化仿真分析器
    print("第一步：创建 Xinan_SyncAnalysis_4 对象，初始化仿真分析器...")
    analyser = Xinan_SyncAnalysis_4(token=tk, api_url=apiURL, username=username, project_key=projectKey)
    print("分析器对象创建成功。")

    # 第二步：初始化 CloudPSS 环境和项目
    print("\n第二步：初始化 CloudPSS 环境和项目...")
    analyser.initialize_cloudpss_env()
    print("CloudPSS 环境和项目初始化完成。")

    # 第三步：配置故障场景和仿真参数
    print("\n第三步：配置故障场景和仿真参数...")
    fault_args = {
        'component_id': 'comp_TranssmissionLineRouter_4106',
        'fault_location': 0,
        'start_time': 4,
        'end_time': 4.1,
        'impedance': 7
    }
    analyser.configure_fault_and_simulation(fault_type='N-1_ground', fault_args=fault_args, end_time=10)
    print("故障和仿真参数配置完成。")

    # 第四步：添加测量点
    print("\n第四步：添加测量点...")
    measured_buses = analyser.add_measurements(bus_id_prefix='川')
    print(f"已添加关键测量点共 {len(measured_buses)} 个。")

    # 第五步：运行电磁暂态仿真
    print("\n第五步：运行电磁暂态仿真...")
    ss_result = analyser.run_emtp_simulation()
    print("电磁暂态仿真运行完成。")

    # 第六步：分析和可视化仿真结果
    print("\n第六步：分析和可视化仿真结果...")
    analyser.analyze_and_visualize_results(ss_result)
    print("仿真结果分析和可视化完成。")

#comment: 检查当前脚本是否作为主程序运行。
if __name__ == '__main__':
    main()