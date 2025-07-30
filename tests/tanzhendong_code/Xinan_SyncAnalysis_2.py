# comment: 导入StabilityAnalysis模块，别名为SA。根据注释，这里实际导入的是S_S_SyncComp。
import S_S_SyncComp as SA
# import ReadSOT as rs #comment: 注释掉的导入语句，未被使用。

import cloudpss #comment: 导入cloudpss库，用于与CloudPSS平台交互。
import os #comment: 导入os模块，用于操作系统相关功能，如文件路径操作。
import time #comment: 导入time模块，用于处理时间相关功能。
import json #comment: 导入json模块，用于JSON数据的编码和解码。
import re #comment: 导入re模块，用于正则表达式操作。
import numpy as np #comment: 导入numpy库，别名为np，用于科学计算，特别是数组操作。
import numpy.linalg as LA #comment: 从numpy.linalg导入linalg模块，别名为LA，用于线性代数运算。

# %matplotlib #comment: 这是一个Jupyter/IPython的魔术命令，用于配置matplotlib的后端，在这里作为普通注释。
import matplotlib as mpl #comment: 导入matplotlib库，别名为mpl，用于绘图。
import matplotlib.pyplot as plt #comment: 导入matplotlib.pyplot模块，别名为plt，用于绘制2D图表。
import plotly.graph_objects as go #comment: 导入plotly.graph_objects模块，别名为go，用于创建交互式图表。
from plotly.subplots import make_subplots #comment: 从plotly.subplots导入make_subplots函数，用于创建子图。
import plotly.io as pio #comment: 导入plotly.io模块，别名为pio，用于设置plotly的输入输出。
from scipy import interpolate #comment: 从scipy导入interpolate模块，用于插值。

import pandas as pd #comment: 导入pandas库，别名为pd，用于数据处理和分析。

import tkinter #comment: 导入tkinter库，用于创建图形用户界面。
import tkinter.filedialog #comment: 导入tkinter.filedialog模块，用于文件对话框。

import math #comment: 导入math模块，用于数学函数。

from IPython.display import HTML #comment: 从IPython.display导入HTML，用于在Jupyter环境中显示HTML内容。
from html import unescape #comment: 从html导入unescape函数，用于解码HTML实体。

import random #comment: 导入random模块，用于生成随机数。
import json #comment: 重复导入json模块，已在前面导入过。
import copy #comment: 导入copy模块，用于创建对象的副本。
from cloudpss.model.implements.component import Component #comment: 从cloudpss.model.implements.component导入Component类。
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult) #comment: 从cloudpss.runner.result导入Result, PowerFlowResult, EMTResult类，用于处理仿真结果。
from cloudpss.model.revision import ModelRevision #comment: 从cloudpss.model.revision导入ModelRevision类。
from cloudpss.model.model import Model #comment: 从cloudpss.model.model导入Model类。


from scipy import optimize #comment: 从scipy导入optimize模块，用于优化算法。

from cloudpss.job.job import Job as cjob #comment: 从cloudpss.job.job导入Job类，别名为cjob。
import nest_asyncio #comment: 导入nest_asyncio库，用于允许嵌套的asyncio事件循环。
nest_asyncio.apply() #comment: 应用nest_asyncio补丁，解决异步编程中事件循环嵌套的问题。

class Xinan_SyncAnalysis_2:
    """
    Xinan_SyncAnalysis_2 类用于封装交流断面最大受电能力分析的相关功能。
    它集成了CloudPSS平台的交互、系统设置、故障配置、仿真运行和结果处理等步骤。

    属性:
        _token (str): CloudPSS平台的认证令牌，用于API认证。
        _api_url (str): CloudPSS平台的API基础URL。
        _username (str): CloudPSS平台的用户名。
        _project_key (str): 当前分析所针对的项目Key，用于标识CloudPSS上的具体项目。
        _sa (SA.S_S_SyncComp): S_S_SyncComp类的实例，封装了与CloudPSS项目交互的核心逻辑，例如设置项目、创建作业等。
        _comp_lib (dict): 从saSource.json加载的组件库数据，可能包含组件的标签、类型等信息。
        _power_flow_result (Result): 潮流计算的仿真结果对象。
        _emtp_result (Result): 电磁暂态仿真的仿真结果对象。
    """
    def __init__(self, token_placeholder="YOUR_CLOUD_PSS_TOKEN", 
                 api_url_placeholder="YOUR_API_URL", 
                 username_placeholder="YOUR_USERNAME", 
                 project_key_placeholder="YOUR_PROJECT_KEY"):
        """
        构造函数，初始化分析类实例。

        参数:
            token_placeholder (str): CloudPSS平台的认证令牌占位符。
            api_url_placeholder (str): CloudPSS平台的API基础URL占位符。
            username_placeholder (str): CloudPSS平台的用户名占位符。
            project_key_placeholder (str): 项目Key占位符。
        """
        self._token = token_placeholder # comment: CloudPSS平台认证令牌。
        self._api_url = api_url_placeholder # comment: CloudPSS API的基础URL。
        self._username = username_placeholder # comment: CloudPSS的用户名。
        self._project_key = project_key_placeholder # comment: CloudPSS项目的Key。

        self._sa = None # comment: S_S_SyncComp实例，稍后初始化。
        self._comp_lib = None # comment: 组件库数据，稍后加载。
        self._power_flow_result = None # comment: 用于存储潮流计算结果。
        self._emtp_result = None # comment: 用于存储电磁暂态计算结果。

    def _load_component_library(self, file_path="saSource.json"):
        """
        加载组件库数据。

        参数:
            file_path (str): 组件库JSON文件的路径。

        返回:
            dict: 加载的组件库数据。
        """
        with open(file_path, "r", encoding='utf-8') as f: #comment: 打开名为'saSource.json'的文件，以UTF-8编码读取。
            comp_lib = json.load(f) #comment: 从文件中加载JSON数据，存储到compLib变量中。
        return comp_lib

    def initialize_system(self):
        """
        初始化系统设置，包括API配置、初始条件和画布创建。
        这个方法包含了原脚本中sa实例的创建、配置和画布设置等。

        返回:
            SA.S_S_SyncComp: 已经初始化并配置好的S_S_SyncComp实例。
        """
        self._comp_lib = self._load_component_library("saSource.json") #comment: 加载组件库数据。
        sa = SA.S_S_SyncComp() #comment: 创建S_S_SyncComp类的实例，赋值给sa。
        sa.setConfig(self._token, self._api_url, self._username, self._project_key) #comment: 设置sa实例的配置，包括令牌、API URL、用户名和项目Key。
        sa.setInitialConditions() #comment: 设置初始条件。
        sa.createSACanvas() #comment: 创建SA的Canvas（画布）。
        self._sa = sa #comment: 将初始化的sa实例存储到类属性中。
        sa.createSSSCACanvas() #comment: 创建SSSCACanvas（状态空间稳定度分析画布）。
        return sa

    def configure_faults_and_jobs(self, sa_instance):
        """
        配置故障情景和仿真作业。这个方法集成了原脚本中故障设置、作业创建、电压测量添加和负荷修改等。

        参数:
            sa_instance (SA.S_S_SyncComp): 已经初始化好的S_S_SyncComp实例。

        返回:
            None
        """
        # comment: N-2故障配置
        N_2LineLabel1 = ['AC900203','AC900202'] # comment: 定义一个包含两条线路标签的列表，表示许木-墨竹线。
        N_2LineKey1 = [] #comment: 初始化一个空列表，用于存储线路的Key。
        for i in N_2LineLabel1: #comment: 遍历N_2LineLabel1中的每个线路标签。
            N_2LineKey1.append([j for j in sa_instance.compLabelDict[i].keys()][0]) #comment: 根据线路标签获取对应的组件Key，并将其第一个Key添加到N_2LineKey1列表中。
        sa_instance.setN_2_GroundFault(N_2LineKey1[0], N_2LineKey1[1], 0, 4, 4.09, 7,OtherFaultParas = {'chg':'0.05'}) #comment: 设置N-2接地故障，指定两条线路的Key、故障时间、清除时间、发生时间和清除时间，并增加其他故障参数。
        
        # comment: 作业配置
        sa_instance.createJob('emtp', name = 'SA_电磁暂态仿真', args = {'begin_time': 0,'end_time': 10,'step_time': 0.00002,\
               'task_queue': 'taskManager','solver_option': 7,'n_cpu': 32}) #comment: 创建一个名为'SA_电磁暂态仿真'的电磁暂态（EMTP）仿真作业，并设置其参数。
        sa_instance.createJob('powerFlow', name = 'SA_潮流计算') #comment: 创建一个名为'SA_潮流计算'的潮流计算作业。
        sa_instance.createConfig(name = 'SA_参数方案') #comment: 创建一个名为'SA_参数方案'的配置。
        
        # comment: 电压测量配置
        sa_instance.addVoltageMeasures('SA_电磁暂态仿真', VMin = 220, freq = 200, PlotName = '220kV以上电压曲线') #comment: 为'SA_电磁暂态仿真'作业添加电压测量，指定最小电压、频率和绘图名称。
        sa_instance.addVoltageMeasures('SA_电磁暂态仿真', VMin = 110, VMax = 120, freq = 200, PlotName = '110kV电压曲线') #comment: 为'SA_电磁暂态仿真'作业添加电压测量，指定最小电压、最大电压、频率和绘图名称。

        # comment: 负荷修改
        # 林芝负荷大小 #comment: 注释：林芝负荷大小的设置。
        # 敏感信息替换为占位符
        sa_instance.project.getComponentByKey("COMPONENT_LOAD_KEY_1").args['p'] = 1 #comment: 通过Key获取指定负荷组件，并将其有功功率'p'设置为1。
        sa_instance.project.getComponentByKey("COMPONENT_LOAD_KEY_1").args['q'] = 0 #comment: 通过Key获取指定负荷组件，并将其无功功率'q'设置为0。
        sa_instance.project.getComponentByKey("COMPONENT_LOAD_KEY_2").args['P0'] = 50 #comment: 通过Key获取另一个组件，并将其初始有功功率'P0'设置为50。
        sa_instance.project.getComponentByKey("COMPONENT_LOAD_KEY_2").args['q'] = -20 #comment: 通过Key获取同一个组件，并将其无功功率'q'设置为-20。

    def run_power_flow_analysis(self, sa_instance):
        """
        运行潮流计算并处理结果。

        参数:
            sa_instance (SA.S_S_SyncComp): 已经初始化好的S_S_SyncComp实例。

        返回:
            Result: 潮流计算的仿真结果对象。
        """
        # sa_instance.project.getModelJob('SA_潮流计算')[0]['args']['url'] = "ANOTHER_API_URL_PLACEHOLDER"; #comment: 注释掉的代码，用于修改潮流计算作业的URL。
        sa_instance.runProject(jobName='SA_潮流计算', configName='SA_参数方案') #comment: 运行项目，执行名为'SA_潮流计算'的作业，并使用'SA_参数方案'配置。

        # comment: 潮流计算结果处理
        # 敏感信息替换为占位符
        index = sa_instance.runner.result.getBranches()[0]['data']['columns'][0]['data'].index("NODE_KEY_FOR_POWER_FLOW") #comment: 从潮流计算结果中获取特定节点的索引。
        p = sa_instance.runner.result.getBranches()[0]['data']['columns'][2]['data'][index] #comment: 根据索引获取该节点的有功功率。
        q = sa_instance.runner.result.getBranches()[0]['data']['columns'][3]['data'][index] #comment: 根据索引获取该节点的无功功率。
        display([2 * p,2 * q]) #comment: 显示计算得到的有功功率和无功功率的两倍值。
        print('正在回写潮流数据...') #comment: 打印提示信息，表示正在回写潮流数据。
        sa_instance.runner.result.powerFlowModify(sa_instance.project) #comment: 将潮流计算结果回写到项目模型中。
        self._power_flow_result = sa_instance.runner.result #comment: 将当前运行结果赋值给pfresult变量并存储到类属性中。
        return sa_instance.runner.result

    def add_synchronous_compensators(self, sa_instance, pf_result):
        """
        添加同步调相机到系统模型中。

        参数:
            sa_instance (SA.S_S_SyncComp): 已经初始化好的S_S_SyncComp实例。
            pf_result (Result): 潮流计算的仿真结果对象，用于同步调相机的初始化。

        返回:
            list: 添加的同步调相机ID列表。
        """
        busLabels = ['藏乃琼220-1','藏西城220-1'] #comment: 定义需要添加调相机的母线标签列表。
        busKeys = [] #comment: 初始化一个空列表，用于存储母线的Key。
        for i in busLabels: #comment: 遍历母线标签列表。
            busKeys.append([j for j in sa_instance.compLabelDict[i].keys()][0]) #comment: 根据母线标签获取对应的组件Key，并将其第一个Key添加到busKeys列表中。
            
        S0 = 1 #comment: 设置调相机的初始容量，这里的值为1，但实际Q列表被硬编码。
        Q = [200,50] #comment: 定义各个调相机的容量列表。
        Syncids = [] #comment: 初始化一个空列表，用于存储同步机ID。
        for bPtr in range(len(busKeys)): #comment: 遍历busKeys列表的索引。
            ids = sa_instance.addSyncComp(busKeys[bPtr], pf_result, syncArgs = {"Smva": str(Q[bPtr])}) #comment: 为每个母线添加同步机组件，指定母线Key、潮流结果以及同步机参数（容量）。
            Syncids.append(ids[0]) #comment: 将新添加同步机的第一个ID添加到Syncids列表中。
        return Syncids

    def run_emtp_analysis_and_save_results(self, sa_instance):
        """
        运行电磁暂态仿真并保存结果。

        参数:
            sa_instance (SA.S_S_SyncComp): 已经初始化好的S_S_SyncComp实例。

        返回:
            Result: 电磁暂态仿真的仿真结果对象。
        """
        # 敏感信息替换为占位符
        sa_instance.project.getModelJob('SA_电磁暂态仿真')[0]['args']['url'] = "ANOTHER_API_URL_PLACEHOLDER_FOR_EMTP" #comment: 修改电磁暂态仿真作业的API URL。
        sa_instance.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案',apiUrl = "ANOTHER_API_URL_PLACEHOLDER_FOR_EMTP_RUN") #comment: 运行项目，执行名为'SA_电磁暂态仿真'的作业，并使用'SA_参数方案'配置，指定API URL。

        sa_instance.plotResult(k=0) #comment: 绘制仿真结果，参数k=0可能表示绘制第一个结果集。

        path = 'results/'+ self._project_key #comment: 定义结果保存的路径，包含项目Key。
        folder = os.path.exists(path) #comment: 检查路径是否存在。
        if not folder: #comment: 如果路径不存在。
            os.makedirs(path) #comment: 创建该路径下的所有目录。

        Result.dump(sa_instance.runner.result,path+'/SAresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob') #comment: 将当前的仿真结果保存到指定路径下的.cjob文件中，文件名包含时间戳。
        self._emtp_result = sa_instance.runner.result # comment: 将电磁暂态仿真结果存储到类属性中。
        return sa_instance.runner.result

def main():
    """
    主函数，用于组织和执行电力系统交流断面最大受电能力分析流程。
    """
    # comment: 用于交流断面最大受电能力分析
    print("开始执行交流断面最大受电能力分析...")

    # Sensitive data placeholders
    token = "YOUR_CLOUD_PSS_TOKEN_PLACEHOLDER"
    api_url = "https://internal.cloudpss.net/"
    username = "USERNAME_PLACEHOLDER"
    project_key = "2025Tibet_WinterHigh_Nofault1_PLACEHOLDER"

    # 第一步：创建分析类实例并初始化系统环境
    print("第一步：创建分析类实例并初始化系统环境...")
    analysis = Xinan_SyncAnalysis_2(token_placeholder=token,
                                    api_url_placeholder=api_url,
                                    username_placeholder=username,
                                    project_key_placeholder=project_key)
    sa_instance = analysis.initialize_system()
    print("系统初始化完成。")

    # 第二步：配置故障场景和仿真作业
    print("第二步：配置故障场景和仿真作业...")
    analysis.configure_faults_and_jobs(sa_instance)
    print("故障和作业配置完成。")

    # 第三步：运行潮流计算并处理潮流数据
    print("第三步：运行潮流计算并处理潮流数据...")
    power_flow_result = analysis.run_power_flow_analysis(sa_instance)
    print("潮流计算完成并回写数据。")

    # 第四步：根据潮流结果添加同步调相机
    print("第四步：根据潮流结果添加同步调相机...")
    sync_ids = analysis.add_synchronous_compensators(sa_instance, power_flow_result)
    print(f"调相机添加完成，ID: {sync_ids}")

    # 第五步：运行电磁暂态仿真并保存结果
    print("第五步：运行电磁暂态仿真并保存结果...")
    emtp_result = analysis.run_emtp_analysis_and_save_results(sa_instance)
    print("电磁暂态仿真完成，结果已保存。")
    
    print("交流断面最大受电能力分析流程全部执行完毕。")

if __name__ == '__main__':
    main()