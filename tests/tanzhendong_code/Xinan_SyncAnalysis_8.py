# comment: 导入StabilityAnalysis模块，命名为SA，但实际代码中使用S_S_SyncComp
import S_S_SyncComp as SA
# comment: 导入cloudpss库，用于与CloudPSS平台交互
import cloudpss
# comment: 导入os模块，用于操作系统相关功能，如路径操作
import os
# comment: 导入time模块，用于时间相关操作，如获取当前时间
import time
# comment: 导入json模块，用于JSON数据的编码和解码
import json
# comment: 导入re模块，用于正则表达式操作
import re
# comment: 导入numpy库，用于数值计算，特别是数组和矩阵操作
import numpy as np
# comment: 从numpy.linalg导入LA，用于线性代数运算
import numpy.linalg as LA

# comment: 导入matplotlib.pyplot模块，用于绘制图表，命名为plt
import matplotlib.pyplot as plt
# comment: 导入plotly.graph_objects模块，用于创建交互式图表，命名为go
import plotly.graph_objects as go
# comment: 从plotly.subplots导入make_subplots，用于创建子图
from plotly.subplots import make_subplots
# comment: 导入plotly.io模块，用于输入输出操作，如保存图表
import plotly.io as pio
# comment: 从scipy.interpolate导入interpolate，用于插值
from scipy import interpolate

# comment: 导入pandas库，用于数据处理和分析
import pandas as pd

# comment: 导入tkinter库，用于创建GUI界面
import tkinter
# comment: 从tkinter导入filedialog模块，用于文件选择对话框
import tkinter.filedialog

# comment: 导入math模块，用于数学函数
import math

# comment: 从IPython.display导入HTML，用于在Jupyter Notebook中显示HTML内容
from IPython.display import HTML
# comment: 从html导入unescape，用于HTML实体解码
from html import unescape

# comment: 导入random模块，用于生成随机数
import random
# comment: 导入copy模块，用于创建对象的浅拷贝和深拷贝
import copy
# comment: 从cloudpss.model.implements.component导入Component类
from cloudpss.model.implements.component import Component
# comment: 从cloudpss.runner.result导入Result, PowerFlowResult, EMTResult类，用于处理仿真结果
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
# comment: 从cloudpss.model.revision导入ModelRevision类
from cloudpss.model.revision import ModelRevision
# comment: 从cloudpss.model.model导入Model类
from cloudpss.model.model import Model

# comment: 从scipy导入optimize模块，用于优化算法
from scipy import optimize

# comment: 从cloudpss.job.job导入Job类，命名为cjob
from cloudpss.job.job import Job as cjob
# comment: 导入nest_asyncio，用于在已经运行的事件循环中运行新的事件循环
import nest_asyncio
# comment: 应用nest_asyncio补丁
nest_asyncio.apply()


class Xinan_SyncAnalysis_8:
    """
    Xinan_SyncAnalysis_8 类用于执行电网稳定分析和SVC优化配置的整个流程。
    它封装了与CloudPSS平台交互、仿真配置、故障设置、结果分析以及简单的粒子群优化算法。

    属性:
        _sa (S_S_SyncComp): S_S_SyncComp 类的实例，用于与CloudPSS平台进行同步补偿器相关的交互和分析。
        _bus_labels_all (list): 所有需要考虑的母线标签列表，用于SVC的配置。
        _bus_keys_all (list): 所有需要考虑的母线在CloudPSS模型中的唯一标识（key）列表。
        _project_key (str): CloudPSS平台的项目密钥，用于标识特定的电网模型项目。
        _results_path (str): 仿真结果和优化历史数据保存的根路径。
        _pso_config (dict): 粒子群优化算法的配置参数，包括加速系数、惯性权重、维度、粒子数量、迭代次数、SVC容量范围等。
    """
    def __init__(self, token_placeholder, api_url_placeholder, username_placeholder, project_key_placeholder,
                 comp_lib_file='saSource.json'):
        """
        初始化 Xinan_SyncAnalysis_8 类的实例。

        参数:
            token_placeholder (str): CloudPSS平台的访问令牌占位符。
            api_url_placeholder (str): CloudPSS API的URL占位符。
            username_placeholder (str): CloudPSS用户名占位符。
            project_key_placeholder (str): CloudPSS项目密钥占位符。
            comp_lib_file (str): 包含组件库信息的JSON文件路径。
        """
        # comment: 实例化S_S_SyncComp类
        self._sa = SA.S_S_SyncComp()
        # comment: 设置SA实例的配置信息，包括token、API URL、用户名和项目密钥
        self._sa.setConfig(token_placeholder, api_url_placeholder, username_placeholder, project_key_placeholder)
        self._project_key = project_key_placeholder

        # comment: 打印初始化信息
        print('正在进行初始化...')
        # comment: 打开saSource.json文件，加载组件库
        with open(comp_lib_file, "r", encoding='utf-8') as f:
            compLib = json.load(f)
        # 补充：这里原始代码中加载的compLib没有被存储或直接使用，如果需要在SA实例中使用，可能需要sa.loadCompLib(compLib)

        self._bus_labels_all = []
        self._bus_keys_all = []
        self._pso_config = {}
        self._results_path = ''

    def setup_initial_conditions_and_fault(self, n2_line_labels, n1_line_label, fault_params):
        """
        设置仿真模型的初始条件，并配置N-2接地故障。

        参数:
            n2_line_labels (list): N-2故障线路的标签列表（例如 ['AC900203','AC900202']）。
            n1_line_label (str): N-1线路的标签（未使用，保留以匹配原始逻辑）。
            fault_params (dict): 故障参数字典，包括故障线路、故障时长、切除时间等。
                例如: {'fault_line_idx1': 0, 'fault_line_idx2': 1, 'fault_start': 0,
                       'fault_duration': 1.5, 'clear_time': 1.56, 'fault_type': 7,
                       'other_fault_paras': {'chg': '1'}}
        输出:
            dict: 包含N-2故障线路的key，N-1线路的key以及更新后的sa实例。
        """
        # comment: 设置初始条件
        self._sa.setInitialConditions()
        # comment: 创建SA画布
        self._sa.createSACanvas()
        # comment: 创建SSSCACanvas
        self._sa.createSSSCACanvas()

        # comment: 初始化N-2线路的key列表
        n2_line_keys = []
        # comment: 遍历N-2线路标签，获取对应的组件key
        for label in n2_line_labels:
            if label in self._sa.compLabelDict:
                n2_line_keys.append([key for key in self._sa.compLabelDict[label].keys()][0])
            else:
                print(f"警告：N-2线路标签 '{label}' 不存在于组件字典中。")

        # comment: 获取N-1线路对应的组件key
        n1_line_key = None
        if n1_line_label in self._sa.compLabelDict:
            n1_line_key = [key for key in self._sa.compLabelDict[n1_line_label].keys()][0]
        else:
            print(f"警告：N-1线路标签 '{n1_line_label}' 不存在于组件字典中。")
        
        # comment: 设置N-2接地故障，包括故障线路、故障时长、切除时间等参数
        if len(n2_line_keys) >= 2:
            self._sa.setN_2_GroundFault(n2_line_keys[fault_params['fault_line_idx1']],
                                        n2_line_keys[fault_params['fault_line_idx2']],
                                        fault_params['fault_start'],
                                        fault_params['fault_duration'],
                                        fault_params['clear_time'],
                                        fault_params['fault_type'],
                                        OtherFaultParas=fault_params['other_fault_paras'])
        else:
            print("错误：N-2故障线路key不足，无法设置故障。")

        # comment: 再次创建SA画布
        self._sa.createSACanvas()

        return {
            'n2_line_keys': n2_line_keys,
            'n1_line_key': n1_line_key,
            'sa_instance': self._sa # 返回sa实例，以便后续操作
        }

    def configure_simulations_and_measures(self, emtp_args, voltage_measure_configs):
        """
        配置潮流计算和电磁暂态仿真任务，并添加电压测量点。

        参数:
            emtp_args (dict): 电磁暂态仿真参数，例如：
                              {'begin_time': 0, 'end_time': 6, 'step_time': 0.00002,
                               'task_queue': 'taskManager', 'solver_option': 7, 'n_cpu': 16}
            voltage_measure_configs (list): 包含电压测量配置的字典列表，例如：
                                            [{'vmin': 220, 'freq': 200, 'plot_name': '220kV以上电压曲线'},
                                             {'vmin': 110, 'vmax': 120, 'freq': 200, 'plot_name': '110kV电压曲线'}]
        输出:
            str: 结果保存路径。
        """
        # comment: 创建名为'SA_潮流计算'的潮流计算任务
        self._sa.createJob('powerFlow', name='SA_潮流计算')
        # comment: 创建名为'SA_参数方案'的配置方案
        self._sa.createConfig(name='SA_参数方案')

        # comment: 定义结果保存路径
        self._results_path = 'results/' + self._project_key + '/SSresults_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '/'
        # comment: 检查路径是否存在
        folder = os.path.exists(self._results_path)
        # comment: 如果路径不存在，则创建
        if not folder:                   
            os.makedirs(self._results_path)            

        # comment: 创建名为'SA_电磁暂态仿真'的电磁暂态仿真任务，并设置仿真参数
        self._sa.createJob('emtp', name='SA_电磁暂态仿真', args=emtp_args)
        # comment: 添加电压测量，根据配置添加不同电压范围的测量
        for config in voltage_measure_configs:
            self._sa.addVoltageMeasures('SA_电磁暂态仿真', VMin=config['vmin'], VMax=config.get('vmax'),
                                        freq=config['freq'], PlotName=config['plot_name'])
        
        return self._results_path

    def prepare_svc_buses_and_pso_config(self, bus_labels_by_area, svc_capacity_range, pso_hyperparams):
        """
        准备SVC安装的母线信息，并设置粒子群优化算法的参数。

        参数:
            bus_labels_by_area (list): 按区域划分的母线标签列表的列表。例如：
                                       [['藏曲布雄220-1','藏多林220'], ['藏德吉220-2','藏藏那220-1']] ...
            svc_capacity_range (tuple): SVC容量范围 (Qmin, Qmax)。
            pso_hyperparams (dict): PSO超参数，例如：
                                    {'C1': 2, 'C2': 2, 'W': 0.6, 'vmax': 30, 'SI0': 0.05, 'W0': 99999}
        输出:
            dict: 包含处理后的母线标签、母线key、SVC初始容量、初始速度、以及PSO配置。
        """
        # comment: 初始化总母线标签列表
        bus_labels = []
        # comment: 初始化区域内存在的母线标签列表（用于过滤掉不存在的标签）
        bus_label_area_filtered = []
        # comment: 遍历每个区域的母线标签
        for area_labels in bus_labels_by_area:
            current_area_filtered = [label for label in area_labels if label in self._sa.compLabelDict.keys()]
            bus_labels.extend(current_area_filtered)
            bus_label_area_filtered.append(current_area_filtered)
        self._bus_labels_all = bus_labels # 存储到实例属性

        # comment: 打印处理后的区域内存在的母线标签
        print("处理后的SVC安装母线区域：", bus_label_area_filtered)

        # comment: 初始化母线key列表
        bus_keys = []
        # comment: 遍历总母线标签，获取对应的组件key
        for label in bus_labels:
            bus_keys.append([key for key in self._sa.compLabelDict[label].keys()][0])
        self._bus_keys_all = bus_keys # 存储到实例属性

        # comment: 粒子群算法参数设置
        q_min, q_max = svc_capacity_range
        self._pso_config = {
            "C1": pso_hyperparams["C1"],                  # comment: 加速度系数C1
            "C2": pso_hyperparams["C2"],                  # comment: 加速度系数C2
            "W": pso_hyperparams["W"],                 # comment: 惯性权重W
            "dim": len(self._bus_keys_all),      # comment: 搜索空间的维度，即母线数量
            "size": 1,                # comment: 粒子群大小 (原始代码设定为1，如果需要多粒子，此处需修改)
            "iter_num": pso_hyperparams.get("iter_num", 10),           # comment: 迭代次数
            "Qmax": q_max,              # comment: SVC最大容量
            "Qmin": q_min,              # comment: SVC最小容量
            "vmax": pso_hyperparams["vmax"],               # comment: 粒子最大速度
            "SI0": pso_hyperparams["SI0"],              # comment: 稳定目标SI
            "W0": pso_hyperparams["W0"]              # comment: 惩罚因子
        }

        # comment: 初始SVC容量Qinit
        # 从文件加载Qinit和Vinit，替换为占位符，因为这是历史数据
        Qinit_data = np.random.rand(self._pso_config['size'], self._pso_config['dim']) * (q_max - q_min) + q_min
        Vinit_data = np.random.rand(self._pso_config['size'], self._pso_config['dim']) * (pso_hyperparams["vmax"] * 2) - pso_hyperparams["vmax"]

        return {
            'bus_labels': bus_labels,
            'bus_keys': bus_keys,
            'Qinit': Qinit_data,
            'Vinit': Vinit_data,
            'pso_config': self._pso_config
        }

    def add_svcs_and_load_pso_state(self, initial_Q_values, pso_history=None):
        """
        在模型中添加SVC设备，并加载粒子群算法的历史状态（如果提供）。

        参数:
            initial_Q_values (np.ndarray): 初始的SVC容量值数组。
            pso_history (list, optional): 粒子群优化历史数据列表，用于恢复上次运行的状态。
                                        如果为None，则初始化PSO状态。
        输出:
            dict: 包含SVC的ID列表、初始化后的Q和V矩阵、粒子群的最优解和适应度等信息。
        """
        # comment: 初始化同步补偿器ID列表
        sync_ids = []
        # comment: 遍历每个母线，添加SVC（同步补偿器），并获取其ID
        for bptr in range(len(self._bus_keys_all)):
            # comment: 添加SVC，并设置初始容量
            # 注意：原始代码Q[0][bptr]意味着所有粒子初始容量相同，这里也遵循
            ids = self._sa.addSVC(self._bus_keys_all[bptr], S=-initial_Q_values[0][bptr], Ts=1.56, Te=999)
            # comment: 将SVC的ID添加到Syncids列表
            sync_ids.append(ids[0])

        Q = initial_Q_values
        V = np.random.rand(self._pso_config['size'], self._pso_config['dim']) * (self._pso_config["vmax"] * 2) - self._pso_config["vmax"] # 初始化V

        QpBest = [{} for _ in range(self._pso_config['size'])]
        pBest = [self._pso_config["W0"] for _ in range(self._pso_config['size'])]
        QgBest = {}
        gBest = self._pso_config["W0"]

        if pso_history:
            # comment: 模拟从已有的Qhistory中加载历史数据
            # comment: 复制QDicts
            QDicts = copy.deepcopy(pso_history[-1]['QDicts'])
            # comment: 复制VDicts
            VDicts = copy.deepcopy(pso_history[-1]['VDicts'])
            # comment: 复制粒子最优解QpBest
            QpBest = copy.deepcopy(pso_history[-1]['QpBest'])
            # comment: 复制粒子最优适应度pBest
            pBest = copy.deepcopy(pso_history[-1]['pBest'])
            # comment: 复制全局最优解QgBest
            QgBest = copy.deepcopy(pso_history[-1]['QgBest'])
            # comment: 复制全局最优适应度gBest
            gBest = pso_history[-1]['gBest']

            # comment: 根据历史数据重新初始化Q和V，这里Q和V都初始化为QgBest
            # 确保QgBest中的key是bus_labels_all中的
            Q = np.array([[QgBest.get(label, 0) for label in self._bus_labels_all] for _ in range(self._pso_config['size'])])
            V = np.array([[QgBest.get(label, 0) for label in self._bus_labels_all] for _ in range(self._pso_config['size'])])

            print(f"从历史文件加载PSO状态，gBest: {gBest}")
        else:
            # 初始化PBest和QpBest
            for i in range(self._pso_config['size']):
                for j in range(len(self._bus_labels_all)):
                    QpBest[i][self._bus_labels_all[j]] = Q[i][j]
            # 初始化QgBest (取第一个粒子作为初始全局最优，或者更合理地根据F值初始化)
            QgBest = copy.deepcopy(QpBest[0])


        return {
            'sync_ids': sync_ids,
            'Q_matrix': Q,
            'V_matrix': V,
            'QpBest': QpBest,
            'pBest': pBest,
            'QgBest': QgBest,
            'gBest': gBest
        }

    def run_pso_iteration(self, iter_params, token_placeholder, api_url_placeholder):
        """
        执行粒子群优化算法的一次迭代。

        参数:
            iter_params (dict): 包含粒子群算法当前状态的字典，包括：
                                'sync_ids': SVC的ID列表
                                'Q_matrix': 当前所有粒子的容量矩阵
                                'V_matrix': 当前所有粒子的速度矩阵
                                'QpBest': 粒子个体最优容量字典列表
                                'pBest': 粒子个体最优适应度列表
                                'QgBest': 全局最优容量字典
                                'gBest': 全局最优适应度
            token_placeholder (str): CloudPSS平台的访问令牌占位符。
            api_url_placeholder (str): CloudPSS API的URL占位符。
        输出:
            dict: 更新后的粒子群算法状态，用于下次迭代或保存。
        """
        sync_ids = iter_params['sync_ids']
        Q = iter_params['Q_matrix']
        V = iter_params['V_matrix']
        QpBest = iter_params['QpBest']
        pBest = iter_params['pBest']
        QgBest = iter_params['QgBest']
        gBest = iter_params['gBest']

        # comment: 初始化适应度函数值
        F = [self._pso_config["W0"] for _ in range(self._pso_config["size"])]
        # comment: 创建QData字典用于存储本次迭代的数据
        QData = {}
        # comment: 复制QDicts到QData (这里需要根据Q_matrix重新构建)
        current_QDicts = []
        current_VDicts = []
        for i in range(self._pso_config['size']):
            q_dict_temp = {self._bus_labels_all[j]: Q[i][j] for j in range(len(self._bus_labels_all))}
            v_dict_temp = {self._bus_labels_all[j]: V[i][j] for j in range(len(self._bus_labels_all))}
            current_QDicts.append(q_dict_temp)
            current_VDicts.append(v_dict_temp)

        QData["QDicts"] = copy.deepcopy(current_QDicts)
        QData["VDicts"] = copy.deepcopy(current_VDicts)
        # comment: 将busLabels添加到QData
        QData["busLabels"] = self._bus_labels_all
        # comment: 初始化SI列表
        SIs = []

        # comment: 遍历粒子群中的每个粒子
        for pso_iter_idx in range(self._pso_config["size"]):
            # comment: 更新每个SVC的容量
            for i in range(len(self._bus_keys_all)): # 使用bus_keys_all确保顺序一致
                self._sa.project.getComponentByKey(sync_ids[i]).args['s'] = -Q[pso_iter_idx][i]

            # comment: 设置CloudPSS仿真任务的URL
            # 注意：原始代码中这里将URL硬编码，根据要求替换为占位符或通过参数传递
            self._sa.project.getModelJob('SA_电磁暂态仿真')[0]['args']['url'] = api_url_placeholder

            # comment: 运行电磁暂态仿真
            self._sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案', apiUrl=api_url_placeholder)

            # comment: 计算系统稳定指标SI
            # 这里的Ts, dT0, Tinterval, T1, dV1, dV2, VminR, VmaxR 都是硬编码值，
            # 考虑是否需要从PSOConfig或其他地方进行参数化。
            SI, ValidNumI = self._sa.calculateSI('SA_电磁暂态仿真', 0, Ts=1.5, dT0=0.5, Tinterval=0.3,
                                                 T1=2.5, dV1=0.25, dV2=0.05, VminR=0.7, VmaxR=1.3)
            # comment: 打印SI和有效测量点数量
            print(f"粒子 {pso_iter_idx+1} - SI: {SI}, 有效测量点数量: {len(ValidNumI)}")
            # comment: 将SI添加到SIs列表
            SIs.append(SI)

            # comment: 根据SI值计算适应度，如果SI小于设定的阈值，则适应度为SVC容量之和
            if SI < self._pso_config["SI0"]:
                F[pso_iter_idx] = sum(Q[pso_iter_idx])
            # comment: 否则，适应度为(1 + SI) * (总最大容量 + SVC容量之和)
            else:
                F[pso_iter_idx] = (1 + SI) * \
                                  (len(self._bus_keys_all) * self._pso_config["Qmax"] + sum(Q[pso_iter_idx]))

            # comment: 更新粒子最优解和适应度
            if pBest[pso_iter_idx] > F[pso_iter_idx]:
                pBest[pso_iter_idx] = F[pso_iter_idx]
                QpBest[pso_iter_idx] = copy.deepcopy(current_QDicts[pso_iter_idx])

        # comment: 保存当前全局最优适应度
        # gBestHist = gBest # 原始代码中保存了，但本次迭代是PSOIter=0，所以没用
        # comment: 更新全局最优适应度
        new_gBest = min(pBest)
        if new_gBest < gBest: # 只有当找到更好的全局最优时才更新
            gBest = new_gBest
            # comment: 获取全局最优粒子索引
            best_pso_iter_index = pBest.index(gBest)
            # comment: 复制全局最优解QDict
            QgBest = copy.deepcopy(current_QDicts[best_pso_iter_index])

        # comment: 将QpBest转换为numpy数组
        QpBestTemp = np.array([[q_dict.get(label, 0) for label in self._bus_labels_all] for q_dict in QpBest])
        # comment: 将QgBest转换为numpy数组
        QgBestTemp = np.array([QgBest.get(label, 0) for label in self._bus_labels_all])

        # comment: 更新每个粒子的速度和位置
        for pso_iter_idx in range(self._pso_config["size"]):
            # comment: 更新速度
            V[pso_iter_idx] = self._pso_config["W"] * V[pso_iter_idx] + \
                              self._pso_config["C1"] * random.random() * (QpBestTemp[pso_iter_idx] - Q[pso_iter_idx]) + \
                              self._pso_config["C2"] * random.random() * (QgBestTemp - Q[pso_iter_idx])

            # comment: 限制速度在最大速度范围内
            V[pso_iter_idx][np.where(V[pso_iter_idx] > self._pso_config["vmax"])] = self._pso_config["vmax"]
            V[pso_iter_idx][np.where(V[pso_iter_idx] < -self._pso_config["vmax"])] = -self._pso_config["vmax"]

            # comment: 根据容量限制调整速度 (注意：这部分逻辑在标准PSO中不常见，一般是更新位置后再限制)
            # V[pso_iter_idx][np.where(Q[pso_iter_idx] > self._pso_config["Qmax"])] = 0 # 原始代码有
            # V[pso_iter_idx][np.where(Q[pso_iter_idx] < self._pso_config["Qmin"])] = 0 # 原始代码有

            # comment: 更新位置（容量）
            Q[pso_iter_idx] = Q[pso_iter_idx] + V[pso_iter_idx]
            # comment: 限制容量在最大容量范围内
            Q[pso_iter_idx][np.where(Q[pso_iter_idx] > self._pso_config["Qmax"])] = self._pso_config["Qmax"]
            # comment: 限制容量在最小容量范围内
            Q[pso_iter_idx][np.where(Q[pso_iter_idx] < self._pso_config["Qmin"])] = self._pso_config["Qmin"]

        # comment: 将适应度F添加到QData
        QData["F"] = F
        # comment: 复制QpBest到QData
        QData["QpBest"] = copy.deepcopy(QpBest)
        # comment: 复制QgBest到QData
        QData["QgBest"] = copy.deepcopy(QgBest)
        # comment: 将pBest添加到QData
        QData["pBest"] = pBest
        # comment: 将gBest添加到QData
        QData["gBest"] = gBest
        # comment: 将SIs添加到QData
        QData["SI"] = SIs

        return {
            'Q_matrix': Q,
            'V_matrix': V,
            'QpBest': QpBest,
            'pBest': pBest,
            'QgBest': QgBest,
            'gBest': gBest,
            'QData_current_iter': QData # 返回本次迭代的QData，用于Qhistory
        }

    def save_pso_history(self, q_history_list):
        """
        保存粒子群优化算法的迭代历史数据到JSON文件。

        参数:
            q_history_list (list): 包含每次迭代QData的列表。
        """
        # comment: 构建保存Qhistory的文件名
        fname_q = self._results_path + 'PSO_Qhistory_' + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.json'
        # comment: 将Qhistory保存为JSON文件
        with open(fname_q, "w", encoding='utf-8') as f:
            f.write(json.dumps(q_history_list, indent=4))
        # comment: 打印保存信息
        print('Q迭代过程保存为：' + fname_q)


def main():
    """
    主函数，编排Xinan_SyncAnalysis_8类的操作流程。
    """
    # comment: 定义占位符敏感数据
    token_ph = 'YOUR_ACCESS_TOKEN_PLACEHOLDER'
    api_url_ph = 'https://your.cloudpss.api.url.placeholder/'
    username_ph = 'your_username_placeholder'
    project_key_ph = 'YOUR_PROJECT_KEY_PLACEHOLDER'

    # comment: 第一步：初始化分析器实例并设置基本配置
    print("\n--- 第一步：初始化分析器实例并设置基本配置 ---")
    sync_analysis = Xinan_SyncAnalysis_8(token_ph, api_url_ph, username_ph, project_key_ph)


    # comment: 第二步：设置初始条件和仿真故障
    print("\n--- 第二步：设置初始条件和仿真故障 ---")
    n2_line_labels = ['AC900203', 'AC900202']
    n1_line_label = '藏夏玛—藏德吉开关站' # 原始代码中N-1线路没有实际用于故障设置
    fault_parameters = {
        'fault_line_idx1': 0,
        'fault_line_idx2': 1,
        'fault_start': 0,
        'fault_duration': 1.5,
        'clear_time': 1.56,
        'fault_type': 7,
        'other_fault_paras': {'chg': '1'}
    }
    setup_info = sync_analysis.setup_initial_conditions_and_fault(n2_line_labels, n1_line_label, fault_parameters)


    # comment: 第三步：配置仿真任务和电压测量
    print("\n--- 第三步：配置仿真任务和电压测量 ---")
    emtp_args = {
        'begin_time': 0, 'end_time': 6, 'step_time': 0.00002,
        'task_queue': 'taskManager', 'solver_option': 7, 'n_cpu': 16
    }
    voltage_measure_configs = [
        {'vmin': 220, 'freq': 200, 'plot_name': '220kV以上电压曲线'},
        {'vmin': 110, 'vmax': 120, 'freq': 200, 'plot_name': '110kV电压曲线'}
    ]
    results_save_path = sync_analysis.configure_simulations_and_measures(emtp_args, voltage_measure_configs)
    print(f"仿真结果将保存至: {results_save_path}")


    # comment: 第四步：准备SVC安装母线信息和PSO配置
    print("\n--- 第四步：准备SVC安装母线信息和PSO配置 ---")
    bus_labels_by_area = [
        ['藏曲布雄220-1', '藏多林220'],
        ['藏德吉220-2', '藏藏那220-1', '藏安牵220'],
        ['藏西城220-1', '藏东城220-1', '藏旁多220-1', '藏曲哥220-1', '藏乃琼220-1'],
        ['藏老虎嘴220-1', '藏朗县220-1', '藏卧龙220-1', '藏巴宜220'],
        ['藏昌珠220-1', '藏吉雄220-1']
    ]
    svc_capacity_range = (0.1, 200) # Qmin, Qmax
    pso_hyperparameters = {
        "C1": 2, "C2": 2, "W": 0.6, "vmax": 30, "SI0": 0.05, "W0": 99999, "iter_num": 10
    }
    pso_setup_info = sync_analysis.prepare_svc_buses_and_pso_config(bus_labels_by_area,
                                                                   svc_capacity_range,
                                                                   pso_hyperparameters)
    # 获取初始的Q和V矩阵
    initial_Q_matrix = pso_setup_info['Qinit']
    # initial_V_matrix = pso_setup_info['Vinit'] # 原始代码中的Vinit在add_svcs_and_load_pso_state中被覆盖


    # comment: 第五步：添加SVC设备并初始化/加载PSO状态
    print("\n--- 第五步：添加SVC设备并初始化/加载PSO状态 ---")
    # 模拟Qhistory的加载，由于没有实际的Qhistory文件，这里用一个空列表开始
    # 在实际应用中，这里会尝试从文件加载，如果存在的话
    # 例如：try: with open('results/YOUR_PROJECT_KEY_PLACEHOLDER/PSO_Qhistory_latest.json', 'r') as f: q_history_mock = json.load(f) except FileNotFoundError: q_history_mock = []
    # 为了演示，我们将直接跳过加载，从头开始
    q_history_mock_data = [] # 假设没有历史数据，从头开始优化

    pso_state = sync_analysis.add_svcs_and_load_pso_state(initial_Q_matrix, pso_history=q_history_mock_data)
    # 将SVC的ID存储起来，方便后续使用
    sync_ids_actual = pso_state['sync_ids']


    # comment: 第六步：执行粒子群优化迭代（这里只运行一次迭代，如果需要完整迭代，需要循环）
    print("\n--- 第六步：执行粒子群优化迭代 ---")
    q_history_list = [] # 用于存储每次迭代的QData
    # 原始代码中迭代次数为1，但pso_hyperparameters中定义了iter_num=10，这里为了符合原始逻辑，只执行一次
    # 如果要运行完整的PSO迭代，需要一个for循环：for _ in range(sync_analysis._pso_config["iter_num"]):
    
    # 准备迭代参数
    iteration_params = {
        'sync_ids': sync_ids_actual,
        'Q_matrix': pso_state['Q_matrix'],
        'V_matrix': pso_state['V_matrix'],
        'QpBest': pso_state['QpBest'],
        'pBest': pso_state['pBest'],
        'QgBest': pso_state['QgBest'],
        'gBest': pso_state['gBest']
    }
    
    # 执行一次迭代
    updated_pso_state = sync_analysis.run_pso_iteration(iteration_params, token_ph, api_url_ph)
    q_history_list.append(updated_pso_state['QData_current_iter']) # 将当前迭代的QData添加到历史列表

    print(f"当前迭代结束后的全局最优适应度 gBest: {updated_pso_state['gBest']}")
    print(f"当前迭代结束后的全局最优容量配置 QgBest: {updated_pso_state['QgBest']}")


    # comment: 第七步：保存优化迭代历史
    print("\n--- 第七步：保存优化迭代历史 ---")
    sync_analysis.save_pso_history(q_history_list)
    print("所有操作完成。")


# comment: 主程序入口
if __name__ == '__main__':
    main()