#comment: 导入StabilityAnalysis模块，AS SA表示给模块取一个别名SA
import S_S_SyncComp as SA
#comment: 导入cloudpss库，用于与CloudPSS平台交互
import cloudpss
#comment: 导入os模块，用于操作系统相关功能，如文件路径操作
import os
#comment: 导入time模块，提供时间相关功能
import time
#comment: 导入json模块，用于处理JSON数据
import json
#comment: 导入re模块，提供正则表达式操作
import re
#comment: 导入numpy库，用于进行科学计算，尤其是数组和矩阵操作
import numpy as np
#comment: 导入numpy.linalg模块，封装了线性代数操作
import numpy.linalg as LA

#comment: 导入matplotlib库，用于绘图
import matplotlib as mpl
#comment: 导入matplotlib.pyplot模块，常用的绘图接口
import matplotlib.pyplot as plt
#comment: 导入plotly.graph_objects模块，用于创建交互式图表
import plotly.graph_objects as go
#comment: 从plotly.subplots导入make_subplots函数，用于创建子图
from plotly.subplots import make_subplots
#comment: 导入plotly.io模块，用于输入输出操作，如保存图表
import plotly.io as pio
#comment: 导入scipy.interpolate模块，用于插值
from scipy import interpolate

#comment: 导入pandas库，用于数据分析和处理
import pandas as pd

#comment: 导入tkinter库，用于创建图形用户界面
import tkinter
#comment: 导入tkinter.filedialog模块，用于文件对话框
import tkinter.filedialog

#comment: 导入math模块，提供数学函数
import math

#comment: 从IPython.display导入HTML，用于在Jupyter Notebook中显示HTML内容
from IPython.display import HTML
#comment: 从html模块导入unescape函数，用于解码HTML实体
from html import unescape

#comment: 导入random模块，用于生成随机数
import random
#comment: 导入json模块，用于处理JSON数据（重复导入，可以删除）
import json
#comment: 导入copy模块，用于复制对象
import copy
#comment: 从cloudpss.model.implements.component导入Component类
from cloudpss.model.implements.component import Component
#comment: 从cloudpss.runner.result导入Result, PowerFlowResult, EMTResult类
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 从cloudpss.model.revision导入ModelRevision类
from cloudpss.model.revision import ModelRevision
#comment: 从cloudpss.model.model导入Model类
from cloudpss.model.model import Model

#comment: 从scipy.optimize导入optimize模块，用于优化算法
from scipy import optimize

#comment: 从cloudpss.job.job导入Job类，并取别名为cjob
from cloudpss.job.job import Job as cjob
#comment: 导入nest_asyncio库，用于嵌套asyncio事件循环
import nest_asyncio
#comment: 应用nest_asyncio，允许在现有事件循环中运行新的事件循环
nest_asyncio.apply()

#comment: Xinan_SyncAnalysis_5 类用于封装电力系统暂态稳定分析的整个流程。
# comment: 它包括配置CloudPSS连接、加载项目、执行潮流计算、进行VSI（电压稳定性指标）计算和结果可视化等功能。
# comment:
# comment: 属性:
# comment:     token (str): CloudPSS 平台的访问令牌。
# comment:     api_url (str): CloudPSS API 的 URL。
# comment:     username (str): 用于 CloudPSS 认证的用户名。
# comment:     project_key (str): 在 CloudPSS 平台上进行操作的项目唯一标识符。
# comment:     comp_lib (dict): 从 saSource.json 加载的组件库数据。
# comment:     sa_instance (SA.S_S_SyncComp): S_S_SyncComp 模块的实例，用于执行具体的仿真和分析操作。
# comment:     pf_result_id (str): 潮流计算结果的ID。
# comment:     pf_result (Result): 潮流计算的结果对象。
# comment:     vsi_info (dict): 包含VSI计算相关信息的字典，如母线标签、仿真参数等。
# comment:     vsi_result (Result): VSI仿真结果对象。
# comment:     vsi_result_dict (dict): 包含VSIi等计算结果的字典。
class Xinan_SyncAnalysis_5:
    def __init__(self):
        #comment: 初始化类实例，设置所有属性为None
        self.token = None
        self.api_url = None
        self.username = None
        self.project_key = None
        self.comp_lib = None
        self.sa_instance = None
        self.pf_result_id = None
        self.pf_result = None
        self.vsi_info = None
        self.vsi_result = None
        self.vsi_result_dict = None

    def setup_environment_and_initialize(self, token, api_url, username, project_key, sa_source_path='saSource.json'):
        """
        comment: 设置CloudPSS环境，加载组件库并初始化SA实例。
        comment: 功能：
        comment: 1. 设置CloudPSS的访问令牌和API URL。
        comment: 2. 加载saSource.json文件中的组件库。
        comment: 3. 初始化S_S_SyncComp类的实例，并进行基本配置。
        comment:
        comment: 参数:
        comment:     token (str): CloudPSS 认证令牌。
        comment:     api_url (str): CloudPSS API 的 URL。
        comment:     username (str): 用户名。
        comment:     project_key (str): 项目秘钥。
        comment:     sa_source_path (str): saSource.json 文件的路径。
        comment:
        comment: 输出结果:
        comment:     None
        """
        #comment: 存储敏感信息到实例属性
        self.token = token
        self.api_url = api_url
        self.username = username
        self.project_key = project_key

        #comment: 使用定义的令牌设置CloudPSS认证
        cloudpss.setToken(self.token)
        #comment: 设置环境变量CLOUDPSS_API_URL
        os.environ['CLOUDPSS_API_URL'] = self.api_url
        
        #comment: 打开并读取saSource.json文件，加载组件库
        with open(sa_source_path, "r", encoding='utf-8') as f:
            self.comp_lib = json.load(f)
            
        #comment: 打印初始化信息
        print('正在进行初始化...')
        #comment: 创建S_S_SyncComp类的实例
        self.sa_instance = SA.S_S_SyncComp()
        #comment: 配置SA实例的令牌、API URL、用户名和项目秘钥
        self.sa_instance.setConfig(self.token, self.api_url, self.username, self.project_key)
        #comment: 设置初始条件
        self.sa_instance.setInitialConditions()
        #comment: 创建SA的画布
        self.sa_instance.createSACanvas()
        #comment: 创建SSSA的画布
        self.sa_instance.createSSSCACanvas()
        #comment: 创建一个名为'powerFlow'的作业
        self.sa_instance.createJob('powerFlow')
        #comment: 创建一个配置
        self.sa_instance.createConfig()
        print('环境设置和初始化完成。')

    def perform_load_flow_and_save_result(self, job_name='CA潮流计算方案', config_name='CA参数方案', result_base_path='results/'):
        """
        comment: 执行潮流计算并保存结果。
        comment: 功能：
        comment: 1. 运行CloudPSS项目中的潮流计算作业。
        comment: 2. 获取潮流计算结果ID和结果对象。
        comment: 3. 将结果保存到指定路径。
        comment:
        comment: 参数:
        comment:     job_name (str): 潮流计算作业的名称。
        comment:     config_name (str): 潮流计算配置的名称。
        comment:     result_base_path (str): 结果保存的根路径。
        comment:
        comment: 输出结果:
        comment:     tuple: 包含潮流计算结果ID和结果对象的元组 (pf_result_id, pf_result)。
        """
        #comment: 打印正在计算初始潮流的信息
        print('正在计算初始潮流...')
        
        #comment: 运行项目，执行名为'CA潮流计算方案'的潮流计算作业，使用'CA参数方案'配置，并显示日志
        self.sa_instance.runProject(jobName=job_name, configName=config_name, showLogs=True)
        #comment: 定义结果保存路径
        path = os.path.join(result_base_path, self.project_key)
        #comment: 检查路径是否存在
        folder = os.path.exists(path)
        #comment: 如果文件夹不存在，则创建文件夹
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
            
        #comment: 获取潮流计算结果的ID
        self.pf_result_id = self.sa_instance.runner.id
        #comment: 获取潮流计算结果对象
        self.pf_result = self.sa_instance.runner.result
        
        print('潮流计算完成并保存结果。')
        return self.pf_result_id, self.pf_result

    def configure_vsi_analysis(self, bus_labels_areas, default_ts=8, default_dt=1.5, default_ddt=0.5, 
                               default_v=220, default_s=100, emtp_job_name='SA_电磁暂态仿真', emtp_time_end=10):
        """
        comment: 配置VSI分析所需参数，包括母线选择、VSI无功电源添加和EMTP仿真作业创建。
        comment: 功能：
        comment: 1. 处理输入的母线标签，筛选出有效的母线。
        comment: 2. 添加VSI无功电源到指定母线。
        comment: 3. 创建EMTP仿真作业和潮流计算作业，并配置相关参数。
        comment:
        comment: 参数:
        comment:     bus_labels_areas (list): 包含多个母线标签列表的列表。
        comment:     default_ts (int): 仿真时间间隔Ts。
        comment:     default_dt (float): 仿真持续时间dT。
        comment:     default_ddt (float): 仿真平滑时间ddT。
        comment:     default_v (int): VSI电源的额定电压。
        comment:     default_s (int): VSI电源的容量。
        comment:     emtp_job_name (str): 电磁暂态仿真作业的名称。
        comment:     emtp_time_end (int): 电磁暂态仿真结束时间。
        comment:
        comment: 输出结果:
        comment:     dict: 包含VSIQKeys、处理后的母线标签和仿真参数的字典。
        """
        #comment: 打印VSI计算设置信息
        print('进行VSI计算的相关设置...')
        
        #comment: 初始化总的母线标签列表
        bus_labels = []
        #comment: 初始化处理后的母线标签区域列表
        bus_label_area_processed = []
        #comment: 遍历母线标签区域
        for area in bus_labels_areas:
            #comment: 复制当前母线标签列表
            area_copy = area.copy()
            #comment: 遍历复制的母线标签列表
            for label in area:
                #comment: 如果母线标签不在sa.compLabelDict中，则从复制列表中移除
                if(label not in self.sa_instance.compLabelDict.keys()):
                    area_copy.remove(label)

            #comment: 将处理后的母线标签添加到总列表中
            bus_labels = bus_labels + area_copy
            #comment: 将处理后的母线标签列表添加到区域列表中
            bus_label_area_processed.append(area_copy)
        #comment: 打印处理后的母线标签区域
        print(bus_label_area_processed)
        
        #comment: 初始化母线键值列表
        bus_keys = []
        #comment: 遍历处理后的母线标签
        for label in bus_labels:
            #comment: 遍历每个母线标签对应的组件键
            for key in self.sa_instance.compLabelDict[label].keys():
                #comment: 如果组件定义是新母线模型，则将其键添加到bus_keys
                if(self.sa_instance.project.getComponentByKey(key).definition=='model/CloudPSS/_newBus_3p'):
                    bus_keys.append(key)
                    break
        
        #comment: 定义仿真相关参数：时间间隔Ts，持续时间dT，平滑时间ddT
        ts = default_ts
        dt = default_dt
        ddt = default_ddt
        
        #comment: 添加VSI无功电源，返回对应的键值
        vsi_q_keys = self.sa_instance.addVSIQSource(bus_keys, V=default_v, S=default_s, Ts=ts, dT=dt, ddT=ddt)
        
        #comment: 定义作业名称和仿真结束时间
        time_end = emtp_time_end
        #comment: 创建一个电磁暂态仿真作业，设置仿真参数
        self.sa_instance.createJob('emtp', name=emtp_job_name, args={
           'begin_time': 0,
           'end_time': time_end,
           'step_time': 0.00005,
           'task_queue': 'taskManager', #'taskManager_turbo1' if turbo else 'taskManager'
           'solver_option': 7,
           'n_cpu': 16
        })
        #comment: 创建一个名为'SA_潮流计算'的潮流计算作业
        self.sa_instance.createJob('powerFlow', name='SA_潮流计算')
        #comment: 创建一个名为'SA_参数方案'的配置
        self.sa_instance.createConfig(name='SA_参数方案')

        #comment: 存储VSI配置信息
        self.vsi_info = {
            'vsi_q_keys': vsi_q_keys,
            'bus_labels': bus_labels,
            'bus_keys': bus_keys,
            'ts': ts,
            'dt': dt,
            'ddt': ddt,
            'emtp_job_name': emtp_job_name,
            'emtp_time_end': emtp_time_end
        }
        print('VSI分析配置完成。')
        return self.vsi_info

    def execute_vsi_simulation(self, vsi_info, config_name='SA_参数方案', result_base_path='results/'):
        """
        comment: 执行VSI相关的电磁暂态仿真。
        comment: 功能：
        comment: 1. 添加VSI测量点。
        comment: 2. 运行EMTP仿真作业。
        comment: 3. 保存仿真结果。
        comment:
        comment: 参数:
        comment:     vsi_info (dict): 包含VSIQKeys、母线数量、仿真参数等信息的字典。
        comment:     config_name (str): 仿真配置的名称。
        comment:     result_base_path (str): 结果保存的根路径。
        comment:
        comment: 输出结果:
        comment:     tuple: 包含电压测量键、dQ测量键、筛选母线和VSI结果对象的元组 (voltage_measure_k, dQ_measure_k, screened_bus, vsi_result)。
        """
        vsi_q_keys = vsi_info['vsi_q_keys']
        bus_keys = vsi_info['bus_keys']
        ts = vsi_info['ts']
        dt = vsi_info['dt']
        ddt = vsi_info['ddt']
        emtp_job_name = vsi_info['emtp_job_name']

        #comment: 添加VSI测量点，并返回电压测量键、dQ测量键和筛选后的母线
        voltage_measure_k, dQ_measure_k, screened_bus = self.sa_instance.addVSIMeasure(
            emtp_job_name, vsi_q_keys, VMin=0.6, VMax=300, freq=100, Nbus=len(bus_keys), dT=dt, Ts=ts
        )
        #comment: 打印开始仿真信息
        print('开始仿真...')
        #comment: 运行'SA_电磁暂态仿真'作业，使用'SA_参数方案'配置
        self.sa_instance.runProject(emtp_job_name, config_name)
        #comment: 打印仿真完成及数据存储信息
        print('仿真完成，正在存储数据...')
        #comment: 定义结果保存路径
        path = os.path.join(result_base_path, self.project_key)
        #comment: 检查路径是否存在
        folder = os.path.exists(path)
        #comment: 如果文件夹不存在，则创建文件夹
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
            
        # Result.dump(sa.runner.result,path+'/VSIresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')
        #comment: 获取仿真结果
        self.vsi_result = self.sa_instance.runner.result
        
        print('VSI仿真执行完成。')
        return voltage_measure_k, dQ_measure_k, screened_bus, self.vsi_result

    def calculate_and_visualize_vsi(self, vsi_info, voltage_measure_k, dQ_measure_k, result):
        """
        comment: 计算VSI并绘制VSI结果图。
        comment: 功能：
        comment: 1. 调用sa_instance计算VSI指标。
        comment: 2. 绘制VSI折线图和柱状图。
        comment:
        comment: 参数:
        comment:     vsi_info (dict): 包含母线标签、仿真参数等信息的字典。
        comment:     voltage_measure_k (list): 电压测量点的键列表。
        comment:     dQ_measure_k (list): dQ测量点的键列表。
        comment:     result (Result): VSI仿真结果对象。
        comment:
        comment: 输出结果:
        comment:     dict: 包含VSIi等计算结果的字典。
        """
        bus_labels = vsi_info['bus_labels']
        bus_keys = vsi_info['bus_keys']
        ts = vsi_info['ts']
        dt = vsi_info['dt']
        ddt = vsi_info['ddt']
        emtp_job_name = vsi_info['emtp_job_name']

        #comment: 计算VSI，并返回VSI结果字典
        self.vsi_result_dict = self.sa_instance.calculateVSI(
            emtp_job_name, voltage_measure_k, dQ_measure_k, bus_labels,
            result=result, busNum=len(bus_keys), Ts=ts, dT=dt, ddT=ddt
        )
        
        #comment: 绘制VSI折线图
        fig = go.Figure()
        #comment: 初始化k为1
        k=1
        #comment: 获取通道名称
        ckeytemp = result.getPlotChannelNames(k)
        # for pk in ckeytemp[1500:1510]:
        #comment: 遍历所有通道键
        for pk in ckeytemp:
            #comment: 条件判断，始终为True，即绘制所有通道
            if(True):
            # if('资阳' in pk):
                #comment: 获取指定通道的x轴数据
                x = result.getPlotChannelData(k,pk)['x']
                #comment: 获取指定通道的y轴数据
                y = result.getPlotChannelData(k,pk)['y']
                #comment: 向图中添加折线图追踪
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
        #comment: 显示图表
        fig.show()

        #comment: 绘制VSI柱状图
        # VSIresult = VSIresultDict
        #comment: 从VSI结果字典中获取母线名称列表
        bus_names = [i for i in self.vsi_result_dict["VSIi"].keys()]
        #comment: 从VSI结果字典中获取VSIi值列表
        bus_vsi_is = [self.vsi_result_dict["VSIi"][i] for i in bus_names]

        #comment: 创建柱状图追踪
        trace = go.Bar(x=bus_names, y=bus_vsi_is)
        #comment: 创建图表布局
        layout_basic = go.Layout(
                    title = 'VSIi',
        #             xaxis = go.XAxis(domain = [0,1])
            )
        #comment: 创建一个 Figure 对象，包含柱状图数据
        fig = go.Figure(data=trace)
        #comment: 显示图表
        fig.show()

        print('VSI计算和可视化完成。')
        return self.vsi_result_dict

def main():
    #comment: 敏感信息占位符
    TOKEN_PLACEHOLDER = "YOUR_CLOUDPSS_TOKEN_HERE"
    API_URL_PLACEHOLDER = "http://YOUR_CLOUDPSS_API_URL_HERE/"
    USERNAME_PLACEHOLDER = "YOUR_USERNAME_HERE"
    PROJECT_KEY_PLACEHOLDER = "YOUR_PROJECT_KEY_HERE"

    analysis_instance = Xinan_SyncAnalysis_5()

    #comment: 第一步：配置环境并初始化分析器
    # comment: 调用 setup_environment_and_initialize 函数，完成CloudPSS连接设置、组件库加载和SA实例初始化。
    analysis_instance.setup_environment_and_initialize(
        token=TOKEN_PLACEHOLDER,
        api_url=API_URL_PLACEHOLDER,
        username=USERNAME_PLACEHOLDER,
        project_key=PROJECT_KEY_PLACEHOLDER
    )

    #comment: 第二步：执行初始潮流计算并保存结果
    # comment: 调用 perform_load_flow_and_save_result 函数，计算电力系统的初始潮流，并获取潮流计算结果。
    pf_result_id, pf_result = analysis_instance.perform_load_flow_and_save_result()

    #comment: 第三步：配置VSI分析参数
    # comment: 调用 configure_vsi_analysis 函数，设置VSI分析的母线、仿真参数以及EMTP仿真作业。
    bus_labels1 =['川瀑布沟500',
                 '川深溪沟500',
                 '川枕头坝500',
                 '川眉山西500',
                 '川修文220-II',
                 '川修文220-l',
                 '川东坡220',
                 '川东坡220-3',
                 '川爱国220',
                 '川甘眉220',
                 '天井坎220',
                 '川铁西220',
                 '川眉山西220']
    bus_label_area = [bus_labels1]
    vsi_analysis_config = analysis_instance.configure_vsi_analysis(bus_labels_area, default_ts=8, default_dt=1.5, default_ddt=0.5)

    #comment: 第四步：执行VSI电磁暂态仿真
    # comment: 调用 execute_vsi_simulation 函数，运行配置好的VSI电磁暂态仿真。
    voltage_measure_k, dQ_measure_k, screened_bus, vsi_simulation_result = analysis_instance.execute_vsi_simulation(vsi_analysis_config)

    #comment: 第五步：计算并可视化VSI结果
    # comment: 调用 calculate_and_visualize_vsi 函数，处理仿真结果，计算VSI指标，并生成可视化图表。
    vsi_final_results = analysis_instance.calculate_and_visualize_vsi(
        vsi_analysis_config, voltage_measure_k, dQ_measure_k, vsi_simulation_result
    )
    print("所有分析步骤已完成。")

if __name__ == '__main__':
    main()