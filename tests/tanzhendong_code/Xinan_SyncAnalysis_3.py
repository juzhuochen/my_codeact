#comment: 导入StabilityAnalysis模块，别名为SA。但此处实际导入的是S_S_SyncComp
import S_S_SyncComp as SA
# import ReadSOT as rs
#comment: 导入cloudpss库
import cloudpss
#comment: 导入os模块，用于操作系统相关功能
import os
#comment: 导入time模块，用于时间相关功能
import time
#comment: 导入json模块，用于JSON数据的编码和解码
import json
#comment: 导入re模块，用于正则表达式操作
import re
#comment: 导入numpy库，别名为np，用于数值计算
import numpy as np
#comment: 导入numpy.linalg模块，别名为LA，用于线性代数运算
import numpy.linalg as LA

# %matplotlib
#comment: 导入matplotlib库，别名为mpl，用于数据可视化
import matplotlib as mpl
#comment: 导入matplotlib.pyplot模块，别名为plt，用于绘图
import matplotlib.pyplot as plt
#comment: 导入plotly.graph_objects模块，别名为go，用于创建图表对象
import plotly.graph_objects as go
#comment: 导入plotly.subplots模块中的make_subplots函数，用于创建子图
from plotly.subplots import make_subplots
#comment: 导入plotly.io模块，别名为pio，用于输入输出操作
import plotly.io as pio
#comment: 导入scipy.interpolate模块，用于插值
from scipy import interpolate

#comment: 导入pandas库，别名为pd，用于数据分析和处理
import pandas as pd

#comment: 导入tkinter库，用于创建GUI
import tkinter
#comment: 导入tkinter.filedialog模块，用于文件对话框
import tkinter.filedialog

#comment: 导入math模块，用于数学函数
import math

#comment: 从IPython.display导入HTML，用于在Jupyter环境中显示HTML内容
from IPython.display import HTML
#comment: 从html导入unescape，用于HTML实体解码
from html import unescape

#comment: 导入random模块，用于生成随机数
import random
#comment: 导入json模块
import json
#comment: 导入copy模块，用于对象拷贝
import copy
#comment: 从cloudpss.model.implements.component导入Component类
from cloudpss.model.implements.component import Component
#comment: 从cloudpss.runner.result导入Result, PowerFlowResult, EMTResult类
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 从cloudpss.model.revision导入ModelRevision类
from cloudpss.model.revision import ModelRevision
#comment: 从cloudpss.model.model导入Model类
from cloudpss.model.model import Model

#comment: 从scipy导入optimize模块，用于优化算法
from scipy import optimize

#comment: 从cloudpss.job.job导入Job类，别名为cjob
from cloudpss.job.job import Job as cjob
#comment: 导入nest_asyncio库，用于嵌套asyncio事件循环
import nest_asyncio
#comment: 应用nest_asyncio补丁
nest_asyncio.apply()

class Xinan_SyncAnalysis_3:
    """
    Xinan_SyncAnalysis_3 类用于封装西藏电网的同步分析流程。
    它集成了CloudPSS平台的稳定分析功能，包括模型设置、故障模拟、潮流计算、EMT仿真及结果处理。

    属性:
    - token (str): 用于CloudPSS认证的令牌。
    - api_url (str): CloudPSS API的URL。
    - username (str): CloudPSS平台的用户名。
    - project_key (str): CloudPSS项目Key，用于标识特定的项目。
    - comp_lib (dict): 组件库，从JSON文件加载。
    - sa (SA.S_S_SyncComp): S_S_SyncComp的实例，用于执行稳定分析操作。
    - pf_result (PowerFlowResult): 潮流计算结果对象。
    """

    def __init__(self, token_placeholder="YOUR_AUTH_TOKEN", api_url_placeholder="YOUR_API_URL",
                 username_placeholder="YOUR_USERNAME", project_key_placeholder="YOUR_PROJECT_KEY"):
        """
        初始化Xinan_SyncAnalysis_3类实例。

        Args:
            token_placeholder (str): CloudPSS认证令牌的占位符。
            api_url_placeholder (str): CloudPSS API URL的占位符。
            username_placeholder (str): CloudPSS用户名的占位符。
            project_key_placeholder (str): CloudPSS项目Key的占位符。
        """
        self.token = token_placeholder
        self.api_url = api_url_placeholder
        self.username = username_placeholder
        self.project_key = project_key_placeholder
        self.comp_lib = self._load_component_library('saSource.json')
        self.sa = SA.S_S_SyncComp()
        self.sa.setConfig(self.token, self.api_url, self.username, self.project_key)
        self.sa.setInitialConditions()
        self.sa.createSACanvas()
        self.pf_result = None

    def _load_component_library(self, file_path):
        """
        私有方法：加载组件库。

        Args:
            file_path (str): 组件库JSON文件的路径。

        Returns:
            dict: 加载的组件库数据。
        """
        #comment: 打开指定的JSON文件并加载组件库数据
        with open(file_path, "r", encoding='utf-8') as f:
            return json.load(f)

    def setup_fault_and_load_shedding(self):
        """
        配置故障情景和负荷切除。
        包括N-2接地故障设置和那曲地区负荷切除。
        """
        #comment: 定义线路标签1（许木-墨竹）
        N_2LineLabel1 = ['AC900203', 'AC900202'] #许木-墨竹

        #comment: 初始化N_2LineKey1列表
        N_2LineKey1 = []
        #comment: 遍历线路标签，获取对应的组件Key
        for i in N_2LineLabel1:
            N_2LineKey1.append([j for j in self.sa.compLabelDict[i].keys()][0])

        #comment: 定义线路标签2
        N_1LineLabel1 = '藏夏玛—藏德吉开关站'
        #comment: 获取对应线路标签的组件Key
        N_1LineKey1 = [j for j in self.sa.compLabelDict[N_1LineLabel1].keys()][0]

        #comment: 设置N-2接地故障，指定线路Key、故障开始时间、结束时间等参数
        self.sa.setN_2_GroundFault(N_2LineKey1[0], N_2LineKey1[1], 0, 4, 4.06, 7, OtherFaultParas = {'chg':'1'})
        # self.sa.setN_1_GroundFault(N_1LineKey1, 0, 4, 4.09, 7)

        #切除那曲负荷
        #comment: 定义那曲地区的负荷标签列表
        NaquLoads = ['藏乌玛塘35','藏藏那10_0','藏藏那35-3_0','藏安牵220_0','藏托牵220_0','藏联牵220_0','藏扎牵220_0','藏藏安10-1_0','藏嘎牵220_0','藏那牵220_0',
        '藏妥牵220_0','藏露牵220_0','藏乌牵220_0','藏雄牵220_0','藏德吉10_0','藏双湖10_0','藏双湖35_0','藏多玛10_0','藏多玛35_0','藏青龙10_0','藏聂荣10_0','藏黑河Y1_0',
        '藏比如10_0','藏巴青10_0','藏索县10_0','藏达塘10_0','藏曲卡10_0','藏那曲中心10_0','藏嘉黎10_0','藏夏玛10_0','藏班戈10_0','藏那曲中35_0']

        #comment: 初始化那曲负荷的Keys列表
        NaquLoadsKeys = []
        #comment: 遍历那曲负荷标签，尝试获取对应的组件Key，如果不存在则打印错误信息
        for i in NaquLoads:
            try:
                NaquLoadsKeys.append([j for j in self.sa.compLabelDict[i].keys()][0])
            except KeyError: # 修正为KeyError，更精确地捕获字典键不存在的异常
                print(f"Error: Component '{i}' not found in compLabelDict.")
                continue;
        #comment: 遍历那曲负荷Keys，为每个负荷设置切除故障
        for i in range(len(NaquLoadsKeys)):
            self.sa.setCutFault(NaquLoadsKeys[i], 4.06)

    def create_and_configure_jobs(self):
        """
        创建并配置CloudPSS仿真作业（潮流计算和电磁暂态仿真）。
        """
        #comment: 创建电磁暂态仿真作业，并设置参数
        self.sa.createJob('emtp', name = 'SA_电磁暂态仿真', args = {'begin_time': 0,'end_time': 5,'step_time': 0.00002,\
               'task_queue': 'taskManager','solver_option': 7,'n_cpu': 32})
        #comment: 创建潮流计算作业
        self.sa.createJob('powerFlow', name = 'SA_潮流计算')
        #comment: 创建参数方案配置
        self.sa.createConfig(name = 'SA_参数方案')

        #comment: 为电磁暂态仿真结果添加电压测量点（220kV以上）
        self.sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 220, freq = 200, PlotName = '220kV以上电压曲线')
        #comment: 为电磁暂态仿真结果添加电压测量点（110kV）
        self.sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 110, VMax = 120, freq = 200, PlotName = '110kV电压曲线')

    def run_power_flow_and_load_result(self, default_pf_result_path=None):
        """
        运行潮流计算或加载已有的潮流计算结果。

        Args:
            default_pf_result_path (str, optional): 默认的潮流结果文件路径。
                                                   如果提供，将尝试直接加载；否则弹出文件选择对话框。

        Returns:
            PowerFlowResult: 潮流计算结果对象。
        """
        # A. 潮流计算运行
        # self.sa.runProject(jobName='SA_潮流计算', configName='SA_参数方案')
        # comment: 以下为保存潮流结果的示例，如果需要运行潮流计算则取消注释
        # path = 'results/'+ self.project_key
        # folder = os.path.exists(path)
        # if not folder: #判断是否存在文件夹如果不存在则创建为文件夹
        #     os.makedirs(path) #makedirs 创建文件时如果路径不存在会创建这个路径
        # Result.dump(self.sa.runner.result,path+'/pfresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')
        # self.pf_result = self.sa.runner.result

        # B. 加载潮流结果 (当前脚本采用的方式)
        #comment: 提示用户手动读取潮流结果
        print('需要手动读取潮流结果...')
        if default_pf_result_path:
            file_path = default_pf_result_path
            print(f"Loading power flow result from default path: {file_path}")
        else:
            #comment: 创建Tkinter主窗口实例
            root = tkinter.Tk()    # 创建一个Tkinter.Tk()实例
            root.withdraw()       # 将Tkinter.Tk()实例隐藏
            #comment: 定义默认目录
            default_dir = r"file_path_placeholder" # Placeholder for security
            #comment: 打开文件选择对话框，让用户选择潮流文件
            file_path = tkinter.filedialog.askopenfilename(title=u'选择潮流文件', initialdir=(os.path.expanduser(default_dir)))
            #comment: 销毁Tkinter主窗口
            root.destroy()

        if file_path:
            #comment: 从选择的文件路径加载潮流结果
            self.pf_result = PowerFlowResult.load(file_path)
            #comment: 打印回写潮流数据的提示
            print('正在回写潮流数据...')
            #comment: 将潮流结果回写到项目模型
            self.pf_result.powerFlowModify(self.sa.project)
        else:
            print("No power flow file selected. Unable to proceed with EMT simulation without power flow data.")
            self.pf_result = None
        return self.pf_result

    def add_svc_and_run_emtp_simulation(self):
        """
        添加SVC装置并运行电磁暂态仿真。
        此步骤依赖于之前加载的潮流计算结果。
        """
        if not self.pf_result:
            print("Power flow result not loaded. Cannot add SVC and run EMT simulation.")
            return

        #comment: 创建SSSCACanvas
        self.sa.createSSSCACanvas()

        #comment: 定义母线标签
        busLabels = ['藏乃琼220-1','藏西城220-1']
        #comment: 初始化busKeys列表
        busKeys = []
        #comment: 遍历母线标签，获取对应的组件Key
        for i in busLabels:
            busKeys.append([j for j in self.sa.compLabelDict[i].keys()][0])

        #comment: 定义SVC的Q值 (容量)
        Q = [250, 1]
        #comment: 初始化Syncids列表 (用于存储添加的SVC实例的ID)
        Syncids = []
        #comment: 遍历母线Keys，添加SVC装置
        for bPtr in range(len(busKeys)):
            # ids = sa.addSyncComp(busKeys[bPtr], pfresult, syncArgs = {"Smva": str(Q[bPtr])}) # Original commented out line
            ids = self.sa.addSVC(busKeys[bPtr], S = -Q[bPtr], Ts = 4.06, Te = 999)
            Syncids.append(ids[0])

        #comment: 获取电磁暂态仿真作业，并设置其URL
        # Note: The original URL 'http://10.112.10.135/' appears to be an internal IP.
        # It's replaced with a placeholder as per sensitivity requirement.
        emtp_job_url = "INTERNAL_EMTP_JOB_URL_PLACEHOLDER"
        self.sa.project.getModelJob('SA_电磁暂态仿真')[0]['args']['url'] = emtp_job_url
        #comment: 运行项目中的电磁暂态仿真作业
        self.sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案', apiUrl=emtp_job_url)

    def save_and_plot_results(self):
        """
        保存仿真结果并绘制图表。
        """
        #comment: 绘制结果
        self.sa.plotResult(k=0)

        #comment: 定义结果文件路径
        path = 'results/'+ self.project_key
        #comment: 检查路径是否存在
        folder = os.path.exists(path)
        #comment: 如果路径不存在，则创建文件夹
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

        #comment: 将仿真结果保存到指定路径
        Result.dump(self.sa.runner.result, path+'/SAresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')
        print(f"Simulation results saved to: {path}/SAresult_{time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())}.cjob")


def main():
    """
    主函数，用于执行同步分析的整个流程。
    """
    # comment: 敏感信息占位符
    token_placeholder = 'YOUR_AUTH_TOKEN_PLACEHOLDER'
    api_url_placeholder = 'https://your.cloudpss.api.url.com/'
    username_placeholder = 'your_username_placeholder'
    project_key_placeholder = 'your_project_key_placeholder' # For example: '2025Tibet_WinterHigh_Nofault2'

    # 第一步：初始化分析器对象
    # 创建Xinan_SyncAnalysis_3的实例，并传入敏感信息占位符
    analyzer = Xinan_SyncAnalysis_3(token_placeholder, api_url_placeholder,
                                     username_placeholder, project_key_placeholder)

    # 第二步：设置故障和负荷切除情景
    # 调用setup_fault_and_load_shedding函数，配置N-2接地故障和那曲地区负荷切除
    analyzer.setup_fault_and_load_shedding()

    # 第三步：创建和配置仿真作业
    # 调用create_and_configure_jobs函数，设置电磁暂态仿真和潮流计算作业参数
    analyzer.create_and_configure_jobs()

    # 第四步：运行或加载潮流计算结果
    # 调用run_power_flow_and_load_result函数，获取潮流计算结果
    # 可以选择提供一个默认的潮流结果文件路径，或者让用户手动选择
    # default_pf_path_example = 'path/to/your/pfresult_2024_01_01_12_00_00.cjob'
    analyzer.run_power_flow_and_load_result()

    # 第五步：添加SVC并运行EMT仿真
    # 调用add_svc_and_run_emtp_simulation函数，在潮流结果的基础上添加SVC装置并执行EMT仿真
    analyzer.add_svc_and_run_emtp_simulation()

    # 第六步：保存并绘制仿真结果
    # 调用save_and_plot_results函数，将仿真结果保存到本地并绘制相关曲线
    analyzer.save_and_plot_results()


if __name__ == '__main__':
    main()