#comment: 导入StabilityAnalysis模块，该模块似乎已被重命名为S_S_SyncComp
import S_S_SyncComp as SA
#comment: 导入cloudpss库，用于与CloudPSS平台交互
import cloudpss
#comment: 导入os模块，用于操作系统相关功能，如路径操作
import os
#comment: 导入time模块，用于时间相关操作
import time
#comment: 导入json模块，用于JSON数据的编码和解码
import json
#comment: 导入re模块，用于正则表达式操作
import re
#comment: 导入numpy库，用于进行数值计算，尤其是数组和矩阵操作
import numpy as np
#comment: 从numpy库中导入linalg模块，用于线性代数运算
import numpy.linalg as LA

# # %matplotlib
#comment: 导入matplotlib库，用于绘制图表
import matplotlib as mpl
#comment: 导入matplotlib.pyplot模块，用于绘制2D图形
import matplotlib.pyplot as plt
#comment: 导入plotly.graph_objects模块，用于创建交互式图表
import plotly.graph_objects as go
#comment: 从plotly.subplots模块导入make_subplots函数，用于创建多子图布局
from plotly.subplots import make_subplots
#comment: 导入plotly.io模块，用于I/O操作，如图片导出
import plotly.io as pio
#comment: 从scipy.interpolate模块导入interpolate，用于插值
from scipy import interpolate

#comment: 导入pandas库，用于数据分析和处理
import pandas as pd

#comment: 导入tkinter库，用于创建图形用户界面
import tkinter
#comment: 从tkinter.filedialog模块导入filedialog，用于文件选择对话框
import tkinter.filedialog

#comment: 导入math模块，用于数学函数
import math

#comment: 从IPython.display模块导入HTML，用于在Jupyter Notebook中显示HTML内容
from IPython.display import HTML
#comment: 从html模块导入unescape，用于HTML实体解码
from html import unescape

#comment: 导入random模块，用于生成随机数
import random
#comment: 导入json模块，再次导入以确保可用性
import json
#comment: 导入copy模块，用于对象复制
import copy
#comment: 从cloudpss.model.implements.component模块导入Component类
from cloudpss.model.implements.component import Component
#comment: 从cloudpss.runner.result模块导入Result, PowerFlowResult, EMTResult类，用于处理仿真结果
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 从cloudpss.model.revision模块导入ModelRevision类
from cloudpss.model.revision import ModelRevision
#comment: 从cloudpss.model.model模块导入Model类
from cloudpss.model.model import Model

#comment: 从scipy模块导入optimize，用于优化算法
from scipy import optimize

#comment: 从cloudpss.job.job模块导入Job类并重命名为cjob
from cloudpss.job.job import Job as cjob
#comment: 导入nest_asyncio库，用于解决异步代码在某些环境（如Jupyter）中嵌套运行的问题
import nest_asyncio
#comment: 应用nest_asyncio补丁
nest_asyncio.apply()

class Xinan_SyncAnalysis_1:
    """
    Xinan_SyncAnalysis_1 类用于执行电力系统同步分析，主要聚焦于故障场景的EMTP仿真。
    它封装了CloudPSS平台的交互逻辑，包括配置设置、模型初始化、故障设定、仿真执行和结果导出。

    属性:
        _token (str): CloudPSS平台的访问令牌，用于身份验证。
        _api_url (str): CloudPSS API的基础URL。
        _username (str): CloudPSS平台的用户名。
        _project_key (str): 在CloudPSS平台上操作的项目密钥。
        sa (SA.StabilityAnalysis): StabilityAnalysis类的实例，用于进行同步分析操作。
    """
    def __init__(self, token_placeholder="YOUR_TOKEN", api_url_placeholder="YOUR_API_URL",
                 username_placeholder="YOUR_USERNAME", project_key_placeholder="YOUR_PROJECT_KEY"):
        """
        初始化Xinan_SyncAnalysis_1类。

        Args:
            token_placeholder (str): CloudPSS平台的访问令牌占位符。
            api_url_placeholder (str): CloudPSS API的URL占位符。
            username_placeholder (str): CloudPSS用户名占位符。
            project_key_placeholder (str): CloudPSS项目密钥占位符。
        """
        self._token = token_placeholder
        self._api_url = api_url_placeholder
        self._username = username_placeholder
        self._project_key = project_key_placeholder
        self.sa = None # comment: StabilityAnalysis类的实例，将在后面的方法中初始化

    def initialize_cloudpss_environment(self, comp_lib_path='saSource.json'):
        """
        初始化CloudPSS环境和同步分析实例。

        Args:
            comp_lib_path (str): 组件库JSON文件的路径。
        
        Returns:
            None
        """
        #comment: 设置CloudPSS访问令牌
        cloudpss.setToken(self._token)
        #comment: 设置环境变量CLOUDPSS_API_URL
        os.environ['CLOUDPSS_API_URL'] = self._api_url

        #comment: 打开并读取名为'saSource.json'的JSON文件，加载组件库
        with open(comp_lib_path, "r", encoding='utf-8') as f:
            # comment: 实际中，compLib可能用于某种内部配置，这里仅为加载动作
            compLib = json.load(f)
            
        #comment: 创建StabilityAnalysis（SA）类的实例
        self.sa = SA.StabilityAnalysis()
        #comment: 设置SA实例的配置，包括令牌、API URL、用户名和项目密钥
        self.sa.setConfig(self._token, self._api_url, self._username, self._project_key)
        #comment: 设置初始条件
        self.sa.setInitialConditions()
        #comment: 创建仿真画布
        self.sa.createSACanvas()
        print("CloudPSS环境和SA实例初始化完成。")

    def configure_fault_scenario(self, line_labels, fault_start_time, fault_duration, fault_end_time, fault_type):
        """
        配置N-2接地故障场景。

        Args:
            line_labels (list): 包含两条故障线路标签的列表，例如 ['AC701004','AC701003']。
            fault_start_time (float): 故障开始时间。
            fault_duration (float): 故障持续时间。
            fault_end_time (float): 故障结束时间。
            fault_type (int): 故障类型代码，例如 7 表示接地故障。
        
        Returns:
            None
        """
        if not self.sa:
            raise RuntimeError("CloudPSS环境未初始化，请先调用 initialize_cloudpss_environment。")

        #comment: 初始化N-2故障线路的关键信息列表
        n_2_line_keys = []
        #comment: 遍历线路标签，获取每条线路对应的CloudPSS组件键
        for label in line_labels:
            if label in self.sa.compLabelDict and self.sa.compLabelDict[label]:
                n_2_line_keys.append(list(self.sa.compLabelDict[label].keys())[0])
            else:
                raise ValueError(f"线路标签 '{label}' 在组件字典中未找到。")
        
        if len(n_2_line_keys) < 2:
            raise ValueError(f"提供的线路标签不足以配置N-2故障，需要2条线路，但仅找到 {len(n_2_line_keys)} 条。")

        #comment: 设置N-2接地故障，使用获取到的线路键和故障参数（起始时间、持续时间、结束时间、故障类型）
        self.sa.setN_2_GroundFault(n_2_line_keys[0], n_2_line_keys[1], 
                                   fault_start_time, fault_duration, fault_end_time, fault_type)
        print(f"N-2接地故障场景配置完成：线路 {line_labels[0]} 和 {line_labels[1]}，故障时间 {fault_start_time} 到 {fault_end_time}。")

    
    def setup_simulation_jobs_and_configs(self, job_name='SA_电磁暂态仿真', time_end=30, step_time=0.00005,
                                          task_queue='taskManager', solver_option=7, n_cpu=16):
        """
        设置仿真作业和参数方案。

        Args:
            job_name (str): 电磁暂态仿真作业的名称。
            time_end (float): 仿真结束时间。
            step_time (float): 仿真步长。
            task_queue (str): 任务队列名称。
            solver_option (int): 求解器选项。
            n_cpu (int): CPU核心数。
        
        Returns:
            str: 电磁暂态仿真作业的名称。
        """
        if not self.sa:
            raise RuntimeError("CloudPSS环境未初始化，请先调用 initialize_cloudpss_environment。")

        #comment: 创建EMTP（电磁暂态）仿真作业
        self.sa.createJob('emtp', name=job_name, args={
           'begin_time': 0,
           'end_time': time_end,
           'step_time': step_time,
           'task_queue': task_queue,
           'solver_option': solver_option,
           'n_cpu': n_cpu
        })
        #comment: 创建潮流计算作业
        self.sa.createJob('powerFlow', name='SA_潮流计算')
        #comment: 创建参数方案
        self.sa.createConfig(name='SA_参数方案')
        print(f"仿真作业 '{job_name}' 和参数方案 'SA_参数方案' 设置完成。")
        return job_name

    def add_voltage_measurement_points(self, emtp_job_name):
        """
        添加电压量测点。

        Args:
            emtp_job_name (str): 电磁暂态仿真作业的名称，用于关联量测点。
        
        Returns:
            None
        """
        if not self.sa:
            raise RuntimeError("CloudPSS环境未初始化，请先调用 initialize_cloudpss_environment。")

        #comment: 添加电压量测点，针对220kV及以上电压等级，频率200Hz，命名为'220kV以上电压曲线'
        self.sa.addVoltageMeasures(emtp_job_name, VMin=220, freq=200, PlotName='220kV以上电压曲线')
        #comment: 添加电压量测点，针对110kV电压等级，频率200Hz，命名为'110kV电压曲线'
        self.sa.addVoltageMeasures(emtp_job_name, VMin=110, VMax=120, freq=200, PlotName='110kV电压曲线')
        #comment: 添加电压量测点，针对10kV以下电压等级，频率200Hz，命名为'10kV以下电压曲线'
        self.sa.addVoltageMeasures(emtp_job_name, VMin=0.01, VMax=10, freq=200, PlotName='10kV以下电压曲线')
        print("电压量测点添加完成。")

    def run_simulation_and_save_results(self, emtp_job_name, config_name='SA_参数方案'):
        """
        运行仿真作业并保存结果。

        Args:
            emtp_job_name (str): 要运行的电磁暂态仿真作业的名称。
            config_name (str): 要应用的参数方案名称。
        
        Returns:
            str: 仿真结果保存的完整路径。
        """
        if not self.sa:
            raise RuntimeError("CloudPSS环境未初始化，请先调用 initialize_cloudpss_environment。")

        #comment: 运行项目中的电磁暂态仿真作业，并应用之前创建的参数方案
        self.sa.runProject(jobName=emtp_job_name, configName=config_name)

        #comment: 定义结果保存路径
        path = 'results/' + self._project_key # 使用类属性中的项目密钥
        #comment: 检查结果目录是否存在
        folder = os.path.exists(path)
        #comment: 如果目录不存在，则创建该目录
        if not folder:                   #comment: 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            #comment: makedirs 创建文件时如果路径不存在会创建这个路径

        #comment: 将仿真结果保存到指定路径下的.cjob文件中，文件名包含当前时间戳
        result_file_path = os.path.join(path, f'SAresult_{time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())}.cjob')
        Result.dump(self.sa.runner.result, result_file_path)
        print(f"仿真结果已保存到：{result_file_path}")
        return result_file_path

#comment: 定义主执行块，该代码仅在作为脚本直接运行时执行
def main():
    #comment: 敏感信息占位符
    token_ph = 'YOUR_ACCESS_TOKEN'
    api_url_ph = 'http://YOUR_CLOUD_PSS_IP_ADDRESS/'
    username_ph = 'YOUR_USERNAME'
    project_key_ph = 'YOUR_PROJECT_KEY' # 或者 'ANOTHER_PROJECT_KEY'

    #comment: 实例化分析器
    analyser = Xinan_SyncAnalysis_1(token_ph, api_url_ph, username_ph, project_key_ph)

    # 第一步：初始化CloudPSS环境和SA实例
    # comment: 加载组件库并设置CloudPSS认证信息
    try:
        analyser.initialize_cloudpss_environment()
    except Exception as e:
        print(f"环境初始化失败: {e}")
        return

    # 第二步：配置故障场景
    # comment: 设置N-2接地故障，模拟线路宕机事件
    n_2_line_labels = ['AC701004','AC701003']
    fault_start_time = 0
    fault_duration = 4
    fault_end_time = 4.09
    fault_type = 7 # 通常表示接地故障
    try:
        analyser.configure_fault_scenario(n_2_line_labels, fault_start_time, fault_duration, fault_end_time, fault_type)
    except Exception as e:
        print(f"故障场景配置失败: {e}")
        return

    # 第三步：设置仿真作业和参数方案
    # comment: 定义EMTP仿真作业的名称、时间、步长等参数
    emtp_job_name = 'SA_电磁暂态仿真'
    time_end = 30
    step_time = 0.00005
    task_queue = 'taskManager'
    solver_option = 7
    n_cpu = 16
    try:
        analyser.setup_simulation_jobs_and_configs(emtp_job_name, time_end, step_time, task_queue, solver_option, n_cpu)
    except Exception as e:
        print(f"仿真作业设置失败: {e}")
        return

    # 第四步：添加电压量测点
    # comment: 为不同电压等级的节点添加电压测量配置，以便后续分析波形
    try:
        analyser.add_voltage_measurement_points(emtp_job_name)
    except Exception as e:
        print(f"电压量测点添加失败: {e}")
        return

    # 第五步：运行仿真并保存结果
    # comment: 启动EMTP仿真并将其结果保存到本地文件系统
    try:
        result_path = analyser.run_simulation_and_save_results(emtp_job_name)
        print(f"同步分析流程执行完毕，结果文件：{result_path}")
    except Exception as e:
        print(f"仿真运行或结果保存失败: {e}")
        return

if __name__ == '__main__':
    main()