# comment: 导入 StabilityAnalysis 模块，并将其别名为 SA
# import StabilityAnalysis as SA
import S_S_SyncComp as SA
# import ReadSOT as rs

# comment: 导入 cloudpss 库
import cloudpss
# comment: 导入 os 模块，用于操作系统相关功能
import os
# comment: 导入 time 模块，用于处理时间相关功能
import time
# comment: 导入 json 模块，用于处理 JSON 数据
import json
# comment: 导入 re 模块，用于正则表达式操作
import re
# comment: 导入 numpy 库，并将其别名为 np，用于数值计算
import numpy as np
# comment: 导入 numpy.linalg 模块，并将其别名为 LA，用于线性代数运算
import numpy.linalg as LA

# %matplotlib
# comment: 导入 matplotlib 库，并将其别名为 mpl，用于绘图
import matplotlib as mpl
# comment: 导入 matplotlib.pyplot 模块，并将其别名为 plt，用于绘图
import matplotlib.pyplot as plt
# comment: 导入 plotly.graph_objects 模块，并将其别名为 go，用于创建交互式图表
import plotly.graph_objects as go
# comment: 导入 plotly.subplots 中的 make_subplots 函数，用于创建子图
from plotly.subplots import make_subplots
# comment: 导入 plotly.io 模块，并将其别名为 pio，用于输入输出操作
import plotly.io as pio
# comment: 导入 scipy.interpolate 模块，用于插值
from scipy import interpolate

# comment: 导入 pandas 库，并将其别名为 pd，用于数据分析
import pandas as pd

# comment: 导入 tkinter 库，用于创建 GUI 应用程序
import tkinter
# comment: 导入 tkinter.filedialog 模块，用于文件对话框
import tkinter.filedialog

# comment: 导入 math 模块，用于数学函数
import math

# comment: 从 IPython.display 导入 HTML，用于在 Jupyter Notebook 中显示 HTML 内容
from IPython.display import HTML
# comment: 从 html 模块导入 unescape，用于解码 HTML 实体
from html import unescape

# comment: 导入 random 模块，用于生成随机数
import random
# comment: 导入 json 模块，用于处理 JSON 数据
import json
# comment: 导入 copy 模块，用于复制对象
import copy
# comment: 从 cloudpss.model.implements.component 导入 Component 类
from cloudpss.model.implements.component import Component
# comment: 从 cloudpss.runner.result 导入 Result, PowerFlowResult, EMTResult 类
from cloudpss.runner.result import (Result, PowerFlowResult, EMTResult)
# comment: 从 cloudpss.model.revision 导入 ModelRevision 类
from cloudpss.model.revision import ModelRevision
# comment: 从 cloudpss.model.model 导入 Model 类
from cloudpss.model.model import Model

# comment: 从 scipy 导入 optimize 模块，用于优化算法
from scipy import optimize

# comment: 从 cloudpss.job.job 导入 Job 类，并将其别名为 cjob
from cloudpss.job.job import Job as cjob
# comment: 导入 nest_asyncio 库
import nest_asyncio
# comment: 应用 nest_asyncio 库，允许事件循环嵌套
nest_asyncio.apply()


class Xinan_SyncAnalysis_7:
    """
    该类用于执行批量切机N-1故障仿真和频率稳定性分析。
    属性:
    - token (str): CloudPSS 访问令牌。
    - api_url (str): CloudPSS API 的 URL。
    - username (str): CloudPSS 用户名。
    - project_key (str): 项目密钥，用于指定在CloudPSS上的操作项目。
    - sa (SA.StabilityAnalysis): StabilityAnalysis 类的实例，用于进行稳定性分析操作。
    - comp_lib (dict): 组件库，从saSource.json加载。
    """

    def __init__(self, token, api_url, username, project_key):
        """
        初始化 Xinan_SyncAnalysis_7 类的新实例。
        Args:
            token (str): CloudPSS 的访问令牌。
            api_url (str): CloudPSS API 的 URL。
            username (str): CloudPSS 用户名。
            project_key (str): 项目密钥。
        """
        self.token = token
        self.api_url = api_url
        self.username = username
        self.project_key = project_key
        self.sa = None
        self.comp_lib = {}
        self.measured_areas = {}
        self.n_1_keys = []
        self.plot_names = ['宁夏区域电压曲线', '新疆区域电压曲线', '甘肃区域电压曲线', '陕西区域电压曲线', '青海区域电压曲线']
        self.plot_t = ['宁', '新', '甘', '陕', '青']

    def initialize_stability_analysis(self):
        """
        初始化稳定性分析实例，设置配置、初始条件、创建画布和作业。
        功能：
        - 创建 StabilityAnalysis 实例。
        - 设置 CloudPSS 配置。
        - 设置初始条件。
        - 创建 SA 画布和 SSSCA 画布。
        - 创建电磁暂态仿真和潮流计算作业。
        - 创建配置方案。
        """
        # comment: 创建 StabilityAnalysis 类的实例
        self.sa = SA.S_S_SyncComp()
        # comment: 设置 CloudPSS 的配置，包括令牌、API URL、用户名和项目密钥
        self.sa.setConfig(self.token, self.api_url, self.username, self.project_key)
        # comment: 设置初始条件
        self.sa.setInitialConditions()
        # comment: 创建 SA 画布
        self.sa.createSACanvas()
        # comment: 创建 SSSCACanvas 画布，用于同步补偿分析
        self.sa.createSSSCACanvas()
        # comment: 创建名为 'SA_电磁暂态仿真' 的电磁暂态仿真作业，并设置其参数
        self.sa.createJob('emtp', name='SA_电磁暂态仿真', args={'begin_time': 0, 'end_time': 15, 'step_time': 0.00005,
                                                                 'task_queue': 'taskManager', 'solver_option': 7,
                                                                 'n_cpu': 16, 'task_cmd': 'cloudpssrun'})

        # comment: 创建名为 'SA_潮流计算' 的潮流计算作业
        self.sa.createJob('powerFlow', name='SA_潮流计算')
        # comment: 创建名为 'SA_参数方案' 的配置方案
        self.sa.createConfig(name='SA_参数方案')

    def load_component_library_and_define_areas(self):
        """
        加载组件库，并定义分析区域。
        功能：
        - 从 'saSource.json' 文件加载组件库。
        - 定义 FC_Areas 列表，代表不同的地理区域。
        - 随机选择并记录每个区域用于测量的母线，存储在 MeasuredAreas 中，并保存到文件。
        """
        # comment: 打开 'saSource.json' 文件，以读模式（"r"）读取组件库，并将其解析为 JSON
        with open('saSource.json', "r", encoding='utf-8') as f:
            self.comp_lib = json.load(f)

        # comment: 定义区域列表
        fc_areas = ['国', '宁', '山', '新', '榆', '甘', '西', '陕', '青']
        # FC_Areas = ['G', 'L', 'b', '等'] # 备用示例

        # comment: 初始化 MeasuredAreas 字典
        self.measured_areas = {}
        # comment: 定义需要优先测量的区域列表
        measured_a_first = ['宁', '新', '甘', '陕', '青']
        # MeasuredAFirst = ['b','G'] # 备用示例

        # comment: 遍历优先测量区域
        for i in measured_a_first:
            # comment: 为每个区域初始化一个空列表
            self.measured_areas[i] = []
            # comment: 创建一个临时列表 aaa
            aaa = []
            # comment: 根据区域和电压基准筛选母线，并添加到 aaa 中

            # note: 这里的筛选逻辑复杂且重复，考虑将其重构为辅助函数以提高可读性和减少重复代码
            # 为了保持原有逻辑和注释，此处暂时保留。
            # 这是原始脚本中的筛选逻辑，筛选不同电压等级的母线
            aaa.append(self.sa.screenCompByArg('model/CloudPSS/_newBus_3p',
                                                [{'arg': 'Name', 'Min': i, 'Max': None if fc_areas[-1] == i else fc_areas[fc_areas.index(i) + 1], 'Set': None},
                                                 {'arg': 'VBase', 'Min': '700', 'Max': None, 'Set': None}]))
            aaa.append(self.sa.screenCompByArg('model/CloudPSS/_newBus_3p',
                                                [{'arg': 'Name', 'Min': i, 'Max': None if fc_areas[-1] == i else fc_areas[fc_areas.index(i) + 1], 'Set': None},
                                                 {'arg': 'VBase', 'Min': '450', 'Max': '699', 'Set': None}]))
            aaa.append(self.sa.screenCompByArg('model/CloudPSS/_newBus_3p',
                                                [{'arg': 'Name', 'Min': i, 'Max': None if fc_areas[-1] == i else fc_areas[fc_areas.index(i) + 1], 'Set': None},
                                                 {'arg': 'VBase', 'Min': '150', 'Max': '449', 'Set': None}]))
            aaa.append(self.sa.screenCompByArg('model/CloudPSS/_newBus_3p',
                                                [{'arg': 'Name', 'Min': i, 'Max': None if fc_areas[-1] == i else fc_areas[fc_areas.index(i) + 1], 'Set': None},
                                                 {'arg': 'VBase', 'Min': '90', 'Max': '149', 'Set': None}]))
            aaa.append(self.sa.screenCompByArg('model/CloudPSS/_newBus_3p',
                                                [{'arg': 'Name', 'Min': i, 'Max': None if fc_areas[-1] == i else fc_areas[fc_areas.index(i) + 1], 'Set': None},
                                                 {'arg': 'VBase', 'Min': '0.01', 'Max': '1', 'Set': None}]))
            # comment: 遍历 aaa 中的每个子列表
            for j in range(len(aaa)):
                # comment: 计算概率 p
                p = 20 / (len(aaa[j]) + 0.01)
                # comment: 如果 p 小于 0.05，则设置为 0.05
                if p < 0.05:
                    p = 0.05
                # comment: 遍历每个母线键
                for k in aaa[j].keys():
                    # comment: 根据概率随机选择母线，并添加到 MeasuredAreas 中
                    if random.random() <= p:
                        self.measured_areas[i].append(k)

        # comment: 将 MeasuredAreas 字典写入 JSON 文件
        output_path = 'results/' + self.project_key + '/'
        os.makedirs(output_path, exist_ok=True)  # Add exist_ok=True to prevent error if dir exists
        with open(output_path + 'MeasuredAreas.json', "w", encoding='utf-8') as f:
            f.write(json.dumps(self.measured_areas, indent=4))

    def prepare_fault_scenarios(self):
        """
        准备 N-1 故障场景的数据。
        功能：
        - 定义N-1故障对象的标签列表。
        - 根据标签列表转换为组件的键列表，存储在 self.n_1_keys 中。
        """
        # comment: 定义 N-1 故障对象的标签列表
        n_1_labels = [
            ['新nls铝业四期G1'],
            ['山能盛鲁G1'],
            ['陕清水G1'],
            ['青拉西瓦G3'],
            ['宁方家庄G2'],
            ['甘昌西一690华', '甘安马中电一69', '甘安四龙源二69', '甘桥东二690东'],
            ['新hm景峡西风G1', '新hm景峡西风G2', '新w柴窝堡西汇G2', '新w柴窝堡西汇G1', '新zd中电投老君庙南风G1',
             '新zd三峡北塔山风G1']
        ]
        # N_1Labels = [['新zd北塔山三峡六师风三G1'], # 备用示例
        #             ['新zd北塔山三峡六师风三G1aa'],
        #             ['新zd北塔山三峡六师风三G1','新zd北塔山三峡六师风三G1aa']
        #            ]
        # N_1Labels = [['Gen1B-4'], # 备用示例
        #             ['Gen1B-4'],
        #             ['Gen风A-0','Gen风B-0']
        #            ]
        # N_kLineLabel = [['AC701218','AC701217']] # 备用示例

        # comment: 初始化 N_1Keys 列表
        self.n_1_keys = []
        # comment: 遍历 N_1Labels 中的每个标签组
        for k_label_group in n_1_labels:
            # comment: 初始化 N_1KeysTemp 列表
            n_1_keys_temp = []
            # comment: 遍历标签组中的每个标签
            for label in k_label_group:
                # comment: 遍历组件标签字典中对应标签的键
                if label in self.sa.compLabelDict: # Add check for key existence
                    for comp_key in self.sa.compLabelDict[label].keys():
                        # comment: 如果组件定义是同步发电机、光伏电站或潮流掩码，则添加到 N_1KeysTemp 中并跳出循环
                        if (self.sa.project.getComponentByKey(comp_key).definition in
                                ['model/CloudPSS/SyncGeneratorRouter', 'model/CloudPSS/PVStation',
                                 'model/admin/GW_mask_power_flow']):
                            n_1_keys_temp.append(comp_key)
                            break
            # comment: 将 N_1KeysTemp 添加到 N_1Keys 中
            self.n_1_keys.append(n_1_keys_temp)

    def configure_simulation_outputs(self, n_k_ptr):
        """
        为给定的故障场景配置仿真输出，包括设置切除故障和添加测量信号。
        Args:
            n_k_ptr (int): 当前故障场景的索引。
        功能：
        - 根据 self.n_1_keys 设置切除故障。
        - 为选择的母线添加电压信号输出。
        - 为母线添加 PLL 和通道分解器，并配置测量输出。
        """
        # comment: 为当前故障场景中的每个键设置切除故障
        if n_k_ptr < len(self.n_1_keys): # Ensure index is valid
            for i in self.n_1_keys[n_k_ptr]:
                self.sa.setCutFault(i, 4) # 4 represents a specific fault type

        # comment: 打印信息 "Adding Outputs..."
        print("Adding Outputs...")

        # comment: 读取测量区域数据
        with open('results/' + self.project_key + '/MeasuredAreas.json', "r", encoding='utf-8') as f:
            self.measured_areas = json.load(f)

        # comment: 遍历绘图区域，配置母线电压输出
        for pa in range(len(self.plot_t)):
            # comment: 获取当前区域的母线键
            bus_keys = self.measured_areas[self.plot_t[pa]]
            # comment: 遍历每个母线键
            for k in range(len(bus_keys)):
                bus_k = bus_keys[k]
                # comment: 为母线的 Vabc 参数设置输出信号
                self.sa.project.getComponentByKey(bus_k).args['Vabc'] = '#' + self.sa.project.getComponentByKey(
                    bus_k).label + '.Vabc'

        # comment: 再次遍历绘图区域，添加 PLL 和通道分解器
        for pa in range(len(self.plot_t)):
            # comment: 初始化 PLLKeys 列表
            pll_keys = []
            # comment: 获取当前区域的母线键
            bus_keys = self.measured_areas[self.plot_t[pa]]
            # comment: 遍历每个母线键
            for k in range(len(bus_keys)):
                bus_k = bus_keys[k]

                # 添加PLL
                # comment: 定义临时的 PLL ID
                temp_id_pll = 'SA_PLL_' + str(k)
                # comment: 定义临时的 PLL 名称
                name_temp_pll = '_newPLL_' + str(k)
                # comment: 定义 PLL 的参数，包括名称、维度、电压和频率
                bus_component = self.sa.project.getComponentByKey(bus_k)
                
                # Check if 'V' and 'VBase' keys exist before access
                voltage_val = 0.0
                if 'V' in bus_component.args and 'VBase' in bus_component.args:
                    voltage_val = float(bus_component.args['V']) * float(bus_component.args['VBase']) * math.sqrt(2 / 3)

                args_temp_pll = {'Name': name_temp_pll, 'Dim': '3',
                               'Voltage': str(voltage_val),
                               'Fo': "#" + bus_component.label + '.Freq'}
                # comment: 定义 PLL 的引脚连接
                pins_temp_pll = {"0": 'SA_VA_' + str(pa) + '_' + str(k), "1": 'SA_VB_' + str(pa) + '_' + str(k),
                               "2": 'SA_VC_' + str(pa) + '_' + str(k), "3": ''}

                # comment: 在画布中添加一个新的 PLL 组件
                id1, label = self.sa.addCompInCanvas(self.comp_lib['_newPLL'], key=temp_id_pll, canvas=self.sa.cDynQid,
                                                       args=args_temp_pll, pins=pins_temp_pll, label=name_temp_pll,
                                                       MaxX=500)
                # comment: 将新添加的 PLL ID 添加到 PLLKeys 列表中
                pll_keys.append(id1)

                # 添加分线器
                # comment: 定义临时的通道分解器 ID
                temp_id_channel_demerge = 'SA_ChannelDeMerge_' + str(k)
                # comment: 定义临时的通道分解器名称
                name_temp_channel_demerge = 'SA__ChannelDeMerge_' + str(k)
                # comment: 定义通道分解器的参数，用于输出配置
                args_temp_channel_demerge = {"Out": [
                    {
                        "0": "Out[1]",
                        "1": "0",
                        "2": "0",
                        "3": "1",
                        "4": "1",
                        "ɵid": 1
                    },
                    {
                        "0": "Out[2]",
                        "1": "1",
                        "2": "0",
                        "3": "1",
                        "4": "1",
                        "ɵid": 2
                    },
                    {
                        "0": "Out[3]",
                        "1": "2",
                        "2": "0",
                        "3": "1",
                        "4": "1",
                        "ɵid": 3
                    }
                ]
                }
                # comment: 获取母线 Vabc 信号的引脚名称
                # Ensure 'Vabc' key exist
                pin_name = bus_component.args.get('Vabc', '')
                if pin_name.startswith('#'):
                    pin_name = pin_name[1:] # Remove the '#' prefix for clarity if needed later

                # comment: 定义通道分解器的引脚连接
                pins_temp_channel_demerge = {"InName": "#"+pin_name, "id-1": 'SA_VA_' + str(pa) + '_' + str(k),
                                             "id-2": 'SA_VB_' + str(pa) + '_' + str(k),
                                             "id-3": 'SA_VC_' + str(pa) + '_' + str(k)}

                # comment: 在画布中添加一个新的通道分解器组件
                id1, label = self.sa.addCompInCanvas(self.comp_lib['_ChannelDeMerge'], key=temp_id_channel_demerge,
                                                       canvas=self.sa.cDynQid, args=args_temp_channel_demerge,
                                                       pins=pins_temp_channel_demerge,
                                                       label=name_temp_channel_demerge, MaxX=500)

            # comment: 在画布上创建新的线段位置
            self.sa.newLinePos(self.sa.cDynQid)
            # comment: 如果 PLLKeys 不为空
            if pll_keys:
                # comment: 添加组件输出测量，测量 PLL 的 Fo 信号，用于绘图
                self.sa.addComponentOutputMeasures('SA_电磁暂态仿真', 'model/CloudPSS/_newPLL', 'Fo', [],
                                                    compList=pll_keys, plotName=self.plot_names[pa], freq=200)

    def run_simulation_and_save_results(self, n_k_ptr, n_1_labels):
        """
        运行仿真并保存结果。
        Args:
            n_k_ptr (int): 当前故障场景的索引。
            n_1_labels (list): N-1 故障对象的标签列表。
        功能：
        - 执行电磁暂态仿真。
        - 将仿真结果保存到指定路径。
        """
        # comment: 定义结果文件路径，包含时间戳
        path = 'results/' + self.project_key + '/SSresults_' + time.strftime("%Y_%m_%d_%H_%M_%S",
                                                                            time.localtime()) + '/'
        # comment: 定义另一个结果文件路径 (Although not used in saving, retain for context)
        # path1 = 'results/' + self.project_key + '/'

        # comment: 检查路径是否存在
        folder = os.path.exists(path)
        # comment: 如果文件夹不存在，则创建它
        if not folder:
            os.makedirs(path)  # makespan 创建文件时如果路径不存在会创建这个路径

        # comment: 打印信息 "Start Simulation..."
        print("Start Simulation...")
        # comment: 运行项目仿真，指定作业名称和配置名称
        self.sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案', showLogs=True)
        # comment: 将仿真结果保存到文件中
        
        # Ensure n_k_ptr is a valid index for n_1_labels before accessing
        scenario_label = "unknown_scenario"
        if n_k_ptr < len(n_1_labels):
            scenario_label = str(n_1_labels[n_k_ptr])

        EMTResult.dump(self.sa.runner.result, path + scenario_label + '.cjob')


def main():
    """
    主执行函数，用于批量切机N-1故障仿真和频率稳定性分析。
    """
    # comment: 定义 CloudPSS 的访问令牌
    # 敏感信息替换为占位符
    token = 'YOUR_CLOUD_PSS_TOKEN'
    # comment: 定义 CloudPSS API 的 URL
    # 敏感信息替换为占位符
    api_url = 'YOUR_CLOUD_PSS_API_URL'
    # comment: 定义 CloudPSS 用户名
    # 敏感信息替换为占位符
    username = 'YOUR_USERNAME'
    # comment: 定义项目密钥
    # 敏感信息替换为占位符
    project_key = 'YOUR_PROJECT_KEY'

    # comment: 定义 N-1 故障对象的标签列表 (Moved here for main to control the iteration)
    # This list will be passed to a class method for processing
    n_1_labels = [
        ['新nls铝业四期G1'],
        ['山能盛鲁G1'],
        ['陕清水G1'],
        ['青拉西瓦G3'],
        ['宁方家庄G2'],
        ['甘昌西一690华', '甘安马中电一69', '甘安四龙源二69', '甘桥东二690东'],
        ['新hm景峡西风G1', '新hm景峡西风G2', '新w柴窝堡西汇G2', '新w柴窝堡西汇G1', '新zd中电投老君庙南风G1',
         '新zd三峡北塔山风G1']
    ]

    # 第一步：创建 Xinan_SyncAnalysis_7 类的实例
    # comment: 创建 Xinan_SyncAnalysis_7 类的实例
    analysis_instance = Xinan_SyncAnalysis_7(token, api_url, username, project_key)

    # 第二步：初始化稳定性分析设置
    # comment: 调用 initialize_stability_analysis 函数，初始化稳定性分析实例，包括配置、画布和作业创建。
    analysis_instance.initialize_stability_analysis()

    # 第三步：加载组件库并定义需要测量的区域
    # comment: 调用 load_component_library_and_define_areas 函数，从文件加载组件库并确定要进行测量的母线区域。
    analysis_instance.load_component_library_and_define_areas()

    # 第四步：准备故障场景数据
    # comment: 调用 prepare_fault_scenarios 函数，解析 N-1 故障对象的标签，生成内部使用的故障键列表。
    analysis_instance.prepare_fault_scenarios()

    # 第五步：遍历所有故障场景，配置仿真输出并运行仿真
    # comment: 遍历 N_1Keys 中的每个故障场景，逐个配置仿真输出，包括设置故障和添加测量信号，然后运行仿真并保存结果。
    for n_k_ptr in range(len(n_1_labels)): # Use n_1_labels length for iteration
        # 为了每次仿真都在一个“干净”的环境下进行，这里需要重新初始化sa实例。
        # 注意：这里和原始脚本行为一致，每次循环都创建新的SA实例，但这不是一个原子性的函数，因此这里在main函数中处理。
        # 如果SA实例的内部状态在每次仿真中不应该有前次循环的残留，重新创建是必要的。
        analysis_instance.initialize_stability_analysis() # Re-initialize SA for each scenario
        analysis_instance.configure_simulation_outputs(n_k_ptr)
        analysis_instance.run_simulation_and_save_results(n_k_ptr, n_1_labels)


# comment: 主执行块
if __name__ == "__main__":
    main()