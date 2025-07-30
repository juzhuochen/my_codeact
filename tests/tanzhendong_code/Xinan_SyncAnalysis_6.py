#comment: 导入StabilityAnalysis模块，别名为SA。该模块在实际代码中被替换为S_S_SyncComp。
# import StabilityAnalysis as SA
#comment: 导入S_S_SyncComp模块，别名为SA，用于同步补偿分析。
import S_S_SyncComp as SA
#comment: 导入ReadSOT模块，当前代码中未被使用。
# import ReadSOT as rs

#comment: 导入cloudpss库，用于与CloudPSS平台交互。
import cloudpss
#comment: 导入os模块，用于操作系统相关功能，如文件路径操作。
import os
#comment: 导入time模块，用于时间相关功能，如获取当前时间。
import time
#comment: 导入json模块，用于处理JSON数据。
import json
#comment: 导入re模块，用于正则表达式操作。
import re
#comment: 导入numpy库，别名为np，用于数值计算。
import numpy as np
#comment: 导入numpy.linalg模块，别名为LA，用于线性代数计算。
import numpy.linalg as LA

# %matplotlib
#comment: 导入matplotlib库，别名为mpl，用于绘图。
import matplotlib as mpl
#comment: 导入matplotlib.pyplot模块，别名为plt，用于绘制静态图。
import matplotlib.pyplot as plt
#comment: 导入plotly.graph_objects模块，别名为go，用于创建交互式图表。
import plotly.graph_objects as go
#comment: 从plotly.subplots导入make_subplots函数，用于创建子图。
from plotly.subplots import make_subplots
#comment: 导入plotly.io模块，别名为pio，用于图表输入输出。
import plotly.io as pio
#comment: 从scipy.interpolate导入interpolate模块，用于插值。
from scipy import interpolate

#comment: 导入pandas库，别名为pd，用于数据分析和处理。
import pandas as pd

#comment: 导入tkinter库，用于创建图形用户界面。
import tkinter
#comment: 导入tkinter.filedialog模块，用于文件对话框。
import tkinter.filedialog

#comment: 导入math模块，用于数学函数。
import math

#comment: 从IPython.display导入HTML，用于在Jupyter环境中显示HTML内容。
from IPython.display import HTML
#comment: 从html模块导入unescape，用于HTML实体解码。
from html import unescape

#comment: 导入random模块，用于生成随机数。
import random
#comment: 导入copy模块，用于对象拷贝。
import copy
#comment: 从cloudpss.model.implements.component导入Component类。
from cloudpss.model.implements.component import Component
#comment: 从cloudpss.runner.result导入Result, PowerFlowResult, EMTResult类。
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 从cloudpss.model.revision导入ModelRevision类。
from cloudpss.model.revision import ModelRevision
#comment: 从cloudpss.model.model导入Model类。
from cloudpss.model.model import Model

#comment: 从scipy导入optimize模块，用于优化算法。
from scipy import optimize

#comment: 从cloudpss.job.job导入Job类，别名为cjob。
from cloudpss.job.job import Job as cjob
#comment: 导入nest_asyncio库，用于在已运行的事件循环中嵌套asyncio。
import nest_asyncio
#comment: 应用nest_asyncio，允许嵌套asyncio事件循环。
nest_asyncio.apply()

class Xinan_SyncAnalysis_6:
    """
    Xinan_SyncAnalysis_6 类用于执行电力系统同步补偿分析，包括初始化、调相机选址定容、仿真执行和结果分析。

    属性:
    - token (str): CloudPSS 认证令牌。
    - api_url (str): CloudPSS API 的 URL。
    - username (str): CloudPSS 用户名。
    - project_key (str): CloudPSS 项目密钥。
    - sa (S_S_SyncComp): S_S_SyncComp 类的实例，用于进行同步补偿分析。
    - comp_lib (dict): 组件库字典。
    - result_path (str): 结果文件保存路径。
    - vsi_result_dict (dict): VSI 结果字典，包含VSIi和VSIij。
    - candidate_bus_labels (list): 候选母线标签列表。
    - judgement_criteria (list): 电压稳定性评估判别标准。
    - sync_comp_info (dict): 存储添加的同步补偿器的相关信息，包括ID和容量。
    """
    def __init__(self, token, api_url, username, project_key, comp_lib_path='saSource.json'):
        """
        初始化 Xinan_SyncAnalysis_6 类的实例。

        参数:
        - token (str): CloudPSS 认证令牌。
        - api_url (str): CloudPSS API 的 URL。
        - username (str): CloudPSS 用户名。
        - project_key (str): CloudPSS 项目密钥。
        - comp_lib_path (str): 组件库文件路径。
        """
        #comment: 将敏感信息替换为占位符。
        self.token = token # 'PLACEHOLDER_TOKEN'
        self.api_url = api_url # 'PLACEHOLDER_API_URL'
        self.username = username # 'PLACEHOLDER_USERNAME'
        self.project_key = project_key # 'PLACEHOLDER_PROJECT_KEY'

        #comment: 设置CloudPSS的认证token。
        cloudpss.setToken(self.token)
        #comment: 设置CloudPSS API的URL环境变量。
        os.environ['CLOUDPSS_API_URL'] = self.api_url

        #comment: 打开并加载saSource.json文件中的组件库。
        with open(comp_lib_path, "r", encoding='utf-8') as f:
            self.comp_lib = json.load(f)

        #comment: 打印初始化信息。
        print('正在进行初始化...')
        #comment: 创建S_S_SyncComp类的实例。
        self.sa = SA.S_S_SyncComp()
        #comment: 设置S_S_SyncComp实例的配置，包括token、API URL、用户名和项目密钥。
        self.sa.setConfig(self.token, self.api_url, self.username, self.project_key)
        #comment: 设置初始条件。
        self.sa.setInitialConditions()
        #comment: 创建同步补偿分析画布。
        self.sa.createSACanvas()
        #comment: 创建子系统同步补偿分析画布。
        self.sa.createSSSCACanvas()

        #comment: 创建一个名为“SA_潮流计算”的潮流计算作业。
        self.sa.createJob('powerFlow', name='SA_潮流计算')
        #comment: 创建一个名为“SA_参数方案”的配置方案。
        self.sa.createConfig(name='SA_参数方案')

        #comment: 定义结果文件的保存路径，包含项目密钥和当前时间戳。
        self.result_path = 'results/' + self.project_key + '/SSresults_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '/'
        #comment: 检查指定的路径是否存在。
        folder = os.path.exists(self.result_path)
        #comment: 如果路径不存在，则创建该路径。
        if not folder:
            os.makedirs(self.result_path)
        
        self.vsi_result_dict = {}
        self.candidate_bus_labels = []
        self.judgement_criteria = []
        self.sync_comp_info = {'Syncids': [], 'Tranids': [], 'BusKeys': []}

    def load_and_set_vsi_data(self, vsi_file_path):
        """
        加载VSI数据并设置到类属性中。

        参数:
        - vsi_file_path (str): VSI 结果文件的路径。此路径应指向一个JSON文件。
        """
        #comment: 提示用户需要手动读取VSI结果文件。
        print('需要手动读取VSIij结果...')
        # commented out original file path selection via tkinter
        # file_path = tkinter.filedialog.askopenfilename(title=u'选择VSIresult文件', initialdir=(os.path.expanduser(default_dir)))
        #comment: 打开并加载VSI结果文件。
        with open(vsi_file_path, "r", encoding='utf-8') as f:
            self.vsi_result_dict = json.load(f)

    def select_and_configure_buses(self, initial_bus_labels):
        """
        选择并配置调相机安装的候选母线。

        参数:
        - initial_bus_labels (list[list[str]]): 初始候选母线标签列表，可能包含多个区域的母线。

        返回:
        - list[str]: 经过筛选和处理后的最终母线键列表，用于安装调相机。
        """
        #comment: 打印开始设置调相机选址定容的信息。
        print('进行选址定容计算的相关设置...')

        #comment: 初始化总母线标签列表。
        final_bus_labels = []
        #comment: 初始化区域母线标签列表（用于存储实际存在的母线）。
        actual_bus_label_areas = []

        #comment: 遍历每个母线区域。
        for area_labels in initial_bus_labels:
            #comment: 复制当前母线区域列表。
            area_labels_copy = area_labels.copy()
            #comment: 遍历区域内的每个母线标签。
            for label in area_labels:
                #comment: 如果母线标签不在sa.compLabelDict中，则从复制列表中移除。
                if label not in self.sa.compLabelDict.keys():
                    area_labels_copy.remove(label)

            #comment: 将有效母线标签添加到总母线标签列表。
            final_bus_labels.extend(area_labels_copy)
            #comment: 将有效区域母线标签添加到区域母线标签列表。
            actual_bus_label_areas.append(area_labels_copy)

        self.candidate_bus_labels = final_bus_labels
        #comment: 打印最终有效的区域母线标签。
        print("有效候选母线区域：", actual_bus_label_areas)

        #comment: 初始化母线键列表。
        bus_keys = []
        #comment: 遍历每个有效的母线标签。
        for label in self.candidate_bus_labels:
            #comment: 遍历该母线标签对应的所有组件键。
            for comp_key in self.sa.compLabelDict[label].keys():
                #comment: 如果组件的定义是'_newBus_3p'（三相新母线），则将其键添加到母线键列表并跳出内层循环。
                if self.sa.project.getComponentByKey(comp_key).definition == 'model/CloudPSS/_newBus_3p':
                    bus_keys.append(comp_key)
                    break
        self.sync_comp_info['BusKeys'] = bus_keys
        return bus_keys

    def add_sync_compensators(self, initial_mva_capacity=10):
        """
        根据选定的母线添加同步补偿器到模型中。

        参数:
        - initial_mva_capacity (float): 各个调相机的初始MVA容量。

        返回:
        - list: 包含Syncids和Tranids的列表，分别表示同步补偿器和变压器的ID。
        """
        #comment: 初始化调相机的容量列表Q，每个调相机的初始容量为initial_mva_capacity。
        Q = [initial_mva_capacity for _ in range(len(self.sync_comp_info['BusKeys']))]

        #comment: 初始化同步补偿器ID列表。
        sync_ids = []
        #comment: 初始化变压器ID列表。
        tran_ids = []

        #comment: 遍历每个母线键。
        for b_ptr, bus_key in enumerate(self.sync_comp_info['BusKeys']):
            #comment: 定义一个电力潮流结果ID。
            # This pfresultID is hardcoded and considered sensitive, replacing with placeholder.
            pf_result_id = 'PLACEHOLDER_PF_RESULT_ID' # 'ecb63ec5-f424-402c-8d68-f9769ef2996c'
            #comment: 异步获取电力潮流结果。
            r = cjob.fetch(pf_result_id)
            #comment: 运行异步任务并获取结果。
            pf_result = nest_asyncio.asyncio.run(r).result

            K = 30
            KA = 14.2
            #comment: 如果是第一个母线，设置不同的K和KA值。
            if b_ptr == 0:
                K = 2
                KA = 10
            #comment: 在指定的母线添加同步补偿器，并设置容量和AVR参数。
            ids = self.sa.addSyncComp(bus_key, pf_result, syncArgs={"Smva": str(Q[b_ptr])}, AVRArgs={"K": str(K), "KA": str(KA)})
            #comment: 将同步补偿器的ID添加到列表中。
            sync_ids.append(ids[0])
            #comment: 将变压器的ID添加到列表中。
            tran_ids.append(ids[2]) # [Syncid1,Busid1,Transid1,AVRid1,Gainid1]

        self.sync_comp_info['Syncids'] = sync_ids
        self.sync_comp_info['Tranids'] = tran_ids
        return Q

    def configure_simulation_and_faults(self, judgement_criteria, job_name='SA_电磁暂态仿真', time_end=10, step_time=0.00005):
        """
        配置仿真作业、故障设置和测量通道。

        参数:
        - judgement_criteria (list): 电压稳定性评估的判别标准，格式为 [[Vmin_range_start, Vmin_range_end, dVLj_threshold, dVUj_threshold], ...]
        - job_name (str): 仿真作业名称。
        - time_end (int): 仿真结束时间。
        - step_time (float): 仿真步长。
        """
        self.judgement_criteria = judgement_criteria
        #comment: 设置N-2接地故障，模拟线路断开。
        # These component IDs are hardcoded, replacing with placeholders.
        self.sa.setN_2_GroundFault('PLACEHOLDER_COMP_ID_1', 'PLACEHOLDER_COMP_ID_2', 1, 4, 4.1, 7) # 'comp_TranssmissionLineRouter_3418','comp_TranssmissionLineRouter_3419'

        #comment: 定义仿真作业名称。
        #comment: 定义仿真结束时间。
        #comment: 创建一个电磁暂态仿真作业，设置仿真时间范围、步长、任务队列和CPU核数。
        self.sa.createJob('emtp', name=job_name, args={
            'begin_time': 0, 'end_time': time_end, 'step_time': step_time,
            'task_queue': 'taskManager', 'solver_option': 7, 'n_cpu': 32
        })

        #comment: 初始化键列表。
        keys = []
        #comment: 遍历项目中所有'_newBus_3p'类型的组件。
        for ii, jj in self.sa.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
            #comment: 如果母线标签以'川'开头，则将其键添加到列表中。
            if '川' in jj.label[:1]:
                keys.append(ii)
        #comment: 添加电压测量点，用于在电磁暂态仿真中监测电压。
        self.sa.addVoltageMeasures(job_name, VMin=0.5, VMax=300, freq=100, PlotName='220kV以上电压曲线', Keys=keys)

        #comment: 添加组件输出测量，用于监测调相机的无功功率。
        self.sa.addComponentOutputMeasures(job_name, 'model/CloudPSS/SyncGeneratorRouter', 'QT_o', [], compList=self.sync_comp_info['Syncids'], plotName='调相机无功功率曲线', freq=200)

    def iterative_optimization(self, max_iterations=20, speed_factor=0.2, convergence_threshold=0.5):
        """
        执行迭代求解，优化调相机容量。

        参数:
        - max_iterations (int): 最大迭代次数。
        - speed_factor (float): 迭代加速比。
        - convergence_threshold (float): 收敛判断阈值。

        返回:
        - dict: Q历史记录，包含每次迭代的调相机容量。
        """
        Q = [float(self.sa.project.getComponentByKey(sync_id).args['Smva']) for sync_id in self.sync_comp_info['Syncids']]
        
        #comment: 初始化Q历史记录字典。
        Qhistory = {}
        #comment: 初始化Q字典，将母线标签与初始容量U对应。
        QDict = {}
        #comment: 填充Q字典。
        for i in range(len(self.candidate_bus_labels)):
            QDict[self.candidate_bus_labels[i]] = Q[i]
        #comment: 将初始QDict存入Qhistory，键为0。
        Qhistory[0] = QDict

        #comment: 初始化任务ID列表。
        taskIDs = []
        ValidNum = [] # Initialize ValidNum

        #comment: 开始迭代求解，最多迭代max_iterations次。
        for iteration in range(max_iterations):
            #comment: 打印开始仿真的信息。
            print(f'开始仿真 (迭代 {iteration + 1}/{max_iterations})...')
            #comment: 运行电磁暂态仿真作业。
            self.sa.runProject('SA_电磁暂态仿真', 'SA_参数方案')
            #comment: 打印仿真完成和数据存储的信息。
            print('仿真完成，正在存储数据...')

            #comment: 将当前仿真任务的ID添加到任务ID列表。
            taskIDs.append(self.sa.runner.id)
            #comment: 获取仿真结果。
            ss_result = self.sa.runner.result
            #comment: 打印数据存储完成信息。
            print('数据存储完成...')

            #comment: 计算电压变化量dVUj和dVLj，以及有效母线数量ValidNumI。
            dVUj, dVLj, ValidNumI = self.sa.calculateDV('SA_电磁暂态仿真', 0, result=ss_result, Ts=4, dT0=0.5, judge=self.judgement_criteria, VminR=0.5, VmaxR=1.5, ValidName=['川'])

            #comment: 如果是第一次迭代，将ValidNumI赋值给ValidNum。
            if iteration == 0:
                ValidNum = ValidNumI
            else:
                 # Update ValidNum for subsequent iterations (union of valid buses from prev and current)
                 ValidNum = sorted(list(set(ValidNum) | set(ValidNumI)))


            # 算线性规划
            #comment: 获取仿真结果中的绘图通道名称。
            channels = ss_result.getPlotChannelNames(0)
            #comment: 将母线标签作为SSNames。
            SSNames = self.candidate_bus_labels
            #comment: 设置线性规划的目标函数系数，每个调相机容量变化成本为1。
            c = [1 for _ in range(len(SSNames))]
            #comment: 初始化线性规划的约束矩阵A。
            A = []
            #comment: 初始化线性规划的约束向量b。
            b = []
            #comment: 设置线性规划变量的边界，表示容量变化范围。
            bounds = [(-Q[i] + 0.1, -Q[i] + 800) for i in range(len(SSNames))]

            VSIi = self.vsi_result_dict['VSIi']
            VSIij = self.vsi_result_dict['VSIij']
            
            #comment: 遍历有效母线。
            for i in ValidNum:
                #comment: 获取母线名称。
                busName = channels[i]
                #comment: 初始化当前约束的系数列表。
                Ai = []
                #comment: 如果母线名称不在VSIij的键中，则跳过。
                if busName not in VSIij[SSNames[0]].keys():
                    continue
                #comment: 遍历所有调相机名称，构建约束系数Ai。
                for k_name in SSNames:
                    # 使用speed_factor来调整线性规划系数
                    Ai.append(-VSIij[k_name][busName] / speed_factor)
                #comment: 将Ai添加到约束矩阵A。
                A.append(Ai)
                #comment: 将当前母线的电压变化最小值添加到约束向量b。
                b.append(min(dVLj[i], dVUj[i]))

            #comment: 运行线性规划求解。
            if A and b: # Ensure A and b are not empty to avoid errors
                res = optimize.linprog(c, A, b, bounds=bounds)
            else:
                print("线性规划约束矩阵为空，跳过优化。")
                break
                
            #comment: 更新调相机容量Q，Q = 原Q + 线性规划求解出的容量变化量res.x。
            Q = (np.array(Q) + res.x).tolist()

            #comment: 遍历每个调相机更新其在项目中的容量参数。
            for i in range(len(Q)):
                #comment: 更新同步补偿器的Smva（额定容量）参数。
                self.sa.project.getComponentByKey(self.sync_comp_info['Syncids'][i]).args['Smva'] = str(Q[i])
                #comment: 更新变压器的Tmva（额定容量）参数。
                self.sa.project.getComponentByKey(self.sync_comp_info['Tranids'][i]).args['Tmva'] = str(Q[i])

            #comment: 打印当前迭代次数。
            print(f'Iter:{iteration + 1}')
            #comment: 打印当前调相机容量。
            print(f'Q:{Q}')
            #comment: 打印调相机容量的变化量。
            print(f'DQ:{res.x.tolist()}')
            #comment: 打印线性规划求解结果信息。
            print(res.message)
            #comment: 重新初始化QDict。
            QDict = {}
            #comment: 填充QDict，存储当前迭代的调相机容量。
            for i in range(len(self.candidate_bus_labels)):
                QDict[self.candidate_bus_labels[i]] = Q[i]
            #comment: 将当前迭代的QDict存入Qhistory。
            Qhistory[iteration + 1] = QDict

            # comment: 判断容量变化量的最大绝对值是否小于convergence_threshold，如果收敛则结束迭代。
            if max(abs(res.x)) < convergence_threshold:
                #comment: 打印收敛信息、总迭代次数和任务ID。
                print(f'迭代已经收敛，结束仿真计算。总迭代次数：{iteration + 1}')
                print('TaskID:')
                print(taskIDs)
                break

            #comment: 找出dVUj中负值的索引。
            mm = [i for i in range(len(dVUj)) if dVUj[i] < 0]
            #comment: 找出dVLj中负值的索引。
            nn = [i for i in range(len(dVLj)) if dVLj[i] < 0]
            #comment: 打印mm。
            print(f"kVUj<0 的母线索引: {mm}")
            #comment: 打印nn。
            print(f"kVLj<0 的母线索引: {nn}")
            #comment: 合并mm和nn，获取所有电压异常的母线索引集合。
            m = set(mm) | set(nn)
            #comment: 打印电压异常母线的名称。
            print(f"电压异常母线: {[channels[i] for i in m]}")
            #comment: 创建一个plotly图形对象。
            fig = go.Figure()
            #comment: 获取仿真结果中的绘图通道名称。
            # rr = ss_result # This line seems redundant as ss_result is already the result object
            #comment: 遍历电压异常的母线。
            for pk in [channels[i] for i in m]:
                #comment: 获取当前母线的电压时间序列数据x和y。
                x = ss_result.getPlotChannelData(0, pk)['x']
                y = ss_result.getPlotChannelData(0, pk)['y']
                #comment: 向图中添加电压曲线，模式为线条。
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
            #comment: 显示图表。
            fig.show()

        return Qhistory

def main():
    """
    主函数，编排同步补偿分析的整个流程。
    """
    #comment: 定义CloudPSS的认证token。
    # All sensitive information moved to placeholders
    token = 'PLACEHOLDER_TOKEN'
    #comment: 定义CloudPSS API的URL。
    api_url = 'PLACEHOLDER_API_URL'
    #comment: 定义CloudPSS的用户名。
    username = 'PLACEHOLDER_USERNAME'
    #comment: 最终使用的项目密钥。
    project_key = 'PLACEHOLDER_PROJECT_KEY'

    # 第一步：初始化分析器
    # 创建 Xinan_SyncAnalysis_6 类的实例，并完成基础设置
    print("第一步：初始化分析器，并设置CloudPSS认证信息和项目基础配置。")
    sync_analyzer = Xinan_SyncAnalysis_6(token, api_url, username, project_key)

    # 第二步：加载VSI结果数据
    # 指定VSI结果文件的路径，并加载数据
    print("\n第二步：加载VSI结果数据。")
    # This path is hardcoded and considered sensitive, replacing with placeholder.
    vsi_file_path = 'PLACEHOLDER_VSI_FILE_PATH' # '.\\results\\xinan2025_withHVDC_noFault\\VSIresultDict_2024_01_03_14_04_21.json'
    sync_analyzer.load_and_set_vsi_data(vsi_file_path)

    # 第三步：选择并配置调相机安装母线
    print("\n第三步：选择并配置调相机安装母线。")
    #comment: 定义第一组候选母线标签。
    initial_candidate_bus_labels = [['川瀑布沟500',
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
                                     '川眉山西220']]
    sync_analyzer.select_and_configure_buses(initial_candidate_bus_labels)

    # 第四步：添加同步补偿器到模型
    print("\n第四步：添加同步补偿器到模型。")
    initial_compensator_capacity = 10  # 各个调相机的初始容量
    initial_Q = sync_analyzer.add_sync_compensators(initial_compensator_capacity)
    print(f"初始调相机容量: {initial_Q}")

    # 第五步：配置仿真作业和故障
    print("\n第五步：配置仿真作业、故障设置和测量通道。")
    #comment: 判别标准，用于电压稳定性评估。
    judgement = [[0.5, 3, 0.75, 1.25], [3, 999, 0.9, 1.1]]
    sync_analyzer.configure_simulation_and_faults(judgement)

    # 第六步：迭代优化调相机容量
    print("\n第六步：执行迭代求解，优化调相机容量。")
    Q_history = sync_analyzer.iterative_optimization(max_iterations=20, speed_factor=0.2, convergence_threshold=0.5)
    print("\n最终调相机容量迭代历史:", Q_history)

#comment: 判断当前脚本是否作为主程序运行。
if __name__ == '__main__':
    main()