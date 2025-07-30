#comment: 从 typing 模块导入 OrderedDict，用于创建有序字典。
from typing import OrderedDict
#comment: 导入 PSAToolbox 库，用于进行电力系统分析。
import PSAToolbox as SA
# import ReadSOT as rs

#comment: 导入 cloudpss 库，用于与 CloudPSS 平台交互。
import cloudpss
#comment: 导入 os 模块，用于文件系统操作。
import os
#comment: 导入 time 模块，用于时间相关操作。
import time
#comment: 导入 json 模块，用于处理 JSON 数据。
import json
#comment: 导入 re 模块，用于正则表达式操作。
import re
#comment: 导入 numpy 库，用于科学计算和数组操作。
import numpy as np
#comment: 从 numpy.linalg 模块导入 LA, 用于线性代数运算。
import numpy.linalg as LA

# %matplotlib
#comment: 导入 matplotlib 库，用于绘图。
import matplotlib as mpl
#comment: 从 matplotlib.pyplot 导入 plt，用于创建和管理图形。
import matplotlib.pyplot as plt
#comment: 从 matplotlib.path 导入 mplPath, 用于路径操作。
import matplotlib.path as mplPath


#comment: 设置 matplotlib 的字体为 SimHei (黑体)，以支持中文显示。
plt.rcParams['font.sans-serif']=['SimHei']
#comment: 设置 matplotlib Axes 的 unicode_minus 为 False，解决负号显示问题。
plt.rcParams['axes.unicode_minus']=False
#comment: 导入 plotly.graph_objects 模块，用于创建交互式图表。
import plotly.graph_objects as go
#comment: 从 plotly.subplots 导入 make_subplots，用于创建子图。
from plotly.subplots import make_subplots
#comment: 导入 plotly.io 模块，用于输入输出操作。
import plotly.io as pio
#comment: 从 scipy 模块导入 interpolate, 用于插值。
from scipy import interpolate

#comment: 导入 pandas 库，用于数据处理和分析。
import pandas as pd

#comment: 导入 tkinter 库，用于创建图形用户界面。
import tkinter
#comment: 导入 tkinter.filedialog 模块，用于文件对话框。
import tkinter.filedialog

#comment: 导入 math 模块，提供数学函数。
import math

#comment: 从 IPython.display 导入 HTML，用于在 Jupyter Notebook 中显示 HTML 内容。
from IPython.display import HTML
#comment: 从 html 模块导入 unescape，用于解码 HTML 实体。
from html import unescape

#comment: 导入 random 模块，用于生成随机数。
import random
#comment: 导入 json 模块，用于 JSON 数据的序列化和反序列化。
import json
#comment: 导入 copy 模块，用于创建对象的副本。
import copy
#comment: 从 cloudpss.model.implements.component 导入 Component 类。
from cloudpss.model.implements.component import Component
#comment: 从 cloudpss.runner.result 导入 Result, PowerFlowResult, EMTResult 类，用于处理仿真结果。
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 从 cloudpss.model.revision 导入 ModelRevision 类。
from cloudpss.model.revision import ModelRevision
#comment: 从 cloudpss.model.model 导入 Model 类。
from cloudpss.model.model import Model

#comment: 导入 nest_asyncio 模块。
import nest_asyncio
#comment: 应用 nest_asyncio 补丁，允许在已经运行的事件循环中运行新的事件循环。
nest_asyncio.apply()

#comment: 从 cloudpss.job.job 导入 Job 类，并重命名为 cjob。
from cloudpss.job.job import Job as cjob

#comment: 从 OAT 模块导入所有内容。假设 OAT 模块存在于同一目录或可导入路径中。
from OAT import OAT # 导入OAT类，而不是所有内容，以便更清晰地使用

class GenerateYZDataCalc:
    """
    GenerateYZDataCalc 类用于进行电力系统稳定性分析，特别关注阻抗和相位的频率特性。
    它集成了 CloudPSS 平台，通过自动化仿真和数据处理，生成不同参数配置下的阻抗-频率特性数据。

    属性:
        _token (str): CloudPSS 平台的访问令牌。
        _api_url (str): CloudPSS 平台的 API 地址。
        _username (str): CloudPSS 平台的用户名。
        _project_key (str): CloudPSS 平台中的项目密钥，标识具体操作的项目。
        _comp_lib (dict): 组件库配置，从 'saSource.json' 文件加载。
        _tested_label (str): 被扫频模块在 CloudPSS 模型中的标签。
        _tested_pin (str): 被扫频模块的特定端口。
        _wind_ge_label (str): 风力发电机组模块在 CloudPSS 模型中的标签。
        _args_harm (dict): 扫频模块的参数配置。
        _harm_mag (float): 注入谐波电流的百分比。
        _output_path (str): 结果保存的根路径。
        _oat_dict (OrderedDict): 正交实验设计参数范围或离散值。
        _oat_cases (list): 根据 _oat_dict 生成的正交实验案例列表。
        _sa_instance (SA.StabilityAnalysis): StabilityAnalysis 类的实例，用于与 CloudPSS 交互。
    """
    def __init__(self):
        #comment: 定义 CloudPSS 的 API 令牌。使用占位符。
        self._token = 'PLACEHOLDER_CLOUD_PSS_TOKEN'
        #comment: 定义 CloudPSS 的 API URL。使用占位符。
        self._api_url = 'PLACEHOLDER_CLOUD_PSS_API_URL'
        #comment: 定义 CloudPSS 的用户名。使用占位符。
        self._username = 'PLACEHOLDER_CLOUD_PSS_USERNAME'
        #comment: 定义 CloudPSS 的项目密钥。使用占位符。
        self._project_key = 'PLACEHOLDER_CLOUD_PSS_PROJECT_KEY'

        #comment: 打开 saSource.json 文件，读取组件库配置。
        with open('saSource.json', "r", encoding='utf-8') as f:
            self._comp_lib = json.load(f)

        #comment: 设置被扫频的模块标签。
        self._tested_label = '风场等值模型I：PMSG网侧变流器模型1'
        #comment: 设置被扫频的模块端口。
        self._tested_pin = '0'
        #comment: 设置风力发电机组标签。
        self._wind_ge_label = '风场等值模型I：PMSG网侧变流器模型1'

        #comment: 设置扫频模块的参数字典 argsHarm。
        self._args_harm = {
            "Mag": 2000, "InitTime": 10, "RampTime": 1, "Sequence": 1,
            "InitVal1": 10, "EndVal1": 40, "DeltaStep1": 1, "DeltaTime1": 5,
            "InitVal2": 0, "EndVal2": 60, "DeltaStep2": 5, "DeltaTime2": 3,
            "InitVal3": 0, "EndVal3": 80, "DeltaStep3": 1, "DeltaTime3": 2,
            "RampRatio": 0.2, "UnitTest": 0
        }
        #comment: 设置注入谐波电流的百分比 (例如 3%)。
        self._harm_mag = 0.03
        
        #comment: 定义结果保存的路径，包含项目密钥和当前时间戳。
        self._output_path = 'results/' + self._project_key + '/HarmFre_' + time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '/'
        
        #comment: 定义一个有序字典 OATDict，包含不同参数的范围或离散值，用于正交实验设计。
        self._oat_dict = OrderedDict([('Pset', [0.2, 0.91/1.5, 1]),
                                      ('Qset', [0, 0.1, -0.1]),
                                      ('Sset', [0.5, 1, 1.5]),
                                      ('SCR', [1.34, 2, 4]),
                                      ('Pro1', [1, 10, 50]),
                                      ('Int1', [0.1, 0.01, 0.0005])])
        #comment: 创建 OAT 类的实例。
        oat_instance = OAT()
        #comment: 根据 OATDict 生成正交实验表，每个元素是一个字典，代表一组实验参数。
        self._oat_cases = oat_instance.genSets(self._oat_dict)
        
        #comment: 初始化 StabilityAnalysis 实例
        self._sa_instance = SA.StabilityAnalysis()

    def prepare_environment_and_project(self):
        """
        准备仿真环境和 CloudPSS 项目。
        包括设置 CloudPSS 配置，创建画布，并加载组件信息。

        参数:
            无

        返回:
            tuple: 包含 StabilityAnalysis 实例和项目相关组件键的元组。
                   - sa_instance (SA.StabilityAnalysis): 已配置的 StabilityAnalysis 实例。
                   - tested_key (str): 被测试组件的键。
                   - wind_ge_key (str): 风力发电机组组件的键。
        """
        #comment: 设置 sa 实例的配置，包括令牌、API URL、用户名和项目密钥。
        self._sa_instance.setConfig(self._token, self._api_url, self._username, self._project_key)
        #comment: 设置初始条件。
        self._sa_instance.setInitialConditions()
        #comment: 创建 SA 画布。
        self._sa_instance.createSACanvas()

        #comment: 获取 testedLabel 对应组件的键。
        tested_key = list(self._sa_instance.compLabelDict[self._tested_label].keys())[0]
        #comment: 获取 WindGeLabel 对应组件的键。
        wind_ge_key = list(self._sa_instance.compLabelDict[self._wind_ge_label].keys())[0]

        return self._sa_instance, tested_key, wind_ge_key

    def modify_model_parameters(self, sa_instance, tested_key, wind_ge_key, current_oat_case):
        """
        根据当前正交实验案例修改模型参数，并添加扫频模块。

        参数:
            sa_instance (SA.StabilityAnalysis): 已配置的 StabilityAnalysis 实例。
            tested_key (str): 被测试组件的键。
            wind_ge_key (str): 风力发电机组组件的键。
            current_oat_case (dict): 当前正交实验的参数配置。

        返回:
            tuple: 包含修改后的 StabilityAnalysis 实例、扫频模块ID和输出通道ID列表的元组。
                   - sa_instance (SA.StabilityAnalysis): 修改后的 StabilityAnalysis 实例。
                   - harm_id (str): 扫频模块的ID。
                   - output_channel_ids (list): 输出通道ID的列表。
                   - time_end (float): 仿真结束时间。
        """
        #comment: 通过键获取 testedLabel 对应的组件对象。
        temp_comp = sa_instance.project.getComponentByKey(tested_key)
        #comment: 通过键获取 WindGeLabel 对应的组件对象。
        wind_comp = sa_instance.project.getComponentByKey(wind_ge_key)

        #comment: 打印正在修改参数的消息。
        print('Changing Parameters...')
        #comment: 基于正交实验表修改 wind_comp 组件的参数。
        #comment: 修改风机数量 WT_Num。
        wind_comp.args['WT_Num'] = str(round(current_oat_case['Sset'] * float(wind_comp.args['WT_Num'])))
        #comment: 修改有功功率参考值 Pref_WF。
        wind_comp.args['Pref_WF'] = str(current_oat_case['Pset'] * float(wind_comp.args['WT_Num']) * 1.5)
        #comment: 修改功率因数有功分量 pf_P。
        wind_comp.args['pf_P'] = wind_comp.args['Pref_WF']
        #comment: 修改变压器电抗 Xtrans。
        wind_comp.args['Xtrans'] = str(float(wind_comp.args['Vpcc'])**2 / (1.5) / current_oat_case['SCR'])
        #comment: 修改无功功率参考值 Qref_WF。
        wind_comp.args['Qref_WF'] = str(current_oat_case['Qset'] * float(wind_comp.args['WT_Num']) * 1.5)
        #comment: 修改功率因数无功分量 pf_Q。
        wind_comp.args['pf_Q'] = wind_comp.args['Qref_WF']
        #comment: 修改直流侧电压控制器比例增益 Kp_udc。
        wind_comp.args['Kp_udc'] = str(current_oat_case['Pro1'])
        #comment: 修改直流侧电压控制器积分增益 Ki_udc。
        wind_comp.args['Ki_udc'] = str(current_oat_case['Int1'])

        #comment: 根据有功功率和无功功率计算初始电流 I0。
        I0 = np.sqrt(float(wind_comp.args['Pref_WF'])**2 + float(wind_comp.args['Qref_WF'])**2) / float(wind_comp.args['Vpcc']) * np.sqrt(2/3) * 1000
        #comment: 设置扫频模块的 Mag (注入电流幅值)。
        args_harm_str = {i: str(j) for (i,j) in self._args_harm.items()}
        args_harm_str['Mag'] = str(I0 * self._harm_mag)

        #comment: 设置扫频模块的名称。
        name_harm = 'SA扫频模块_I'
        #comment: 定义扫频模块的引脚连接。
        pins_harm = {
            'Freq': name_harm + '.F', 'Neg': name_harm + '.Neg', 'Ph': name_harm + '.Ph',
            'Phn': name_harm + '.Phn', 'Php': name_harm + '.Php', 'Pos': temp_comp.pins[self._tested_pin],
            'Z': name_harm + '.Z', 'Zn': name_harm + '.Zn', 'Zp': name_harm + '.Zp'
        }
        #comment: 修改 testedPin 处的连接到扫频模块的 Neg 端。
        temp_comp.pins[self._tested_pin] = name_harm + '.Neg'
        #comment: 在画布中添加谐波连续注入电流模块。
        harm_id, label = sa_instance.addCompInCanvas(
            sa_instance.compLib['Harmonic_continuous_injection_I'],
            key='Harmonic_continuous_injection_I', canvas=sa_instance.cFid,
            args=args_harm_str, pins=pins_harm, label=name_harm
        )
        #comment: 更新画布中的新线路位置。
        sa_instance.newLinePos(sa_instance.cFid)

        #comment: 设置输出通道字典和 ID 列表。
        output_channel_ids = []
        #comment: 遍历扫频模块的引脚，添加输出通道。
        for pin_name in pins_harm.keys():
            #comment: 跳过 Pos 和 Neg 引脚。
            if pin_name in ['Pos', 'Neg']:
                continue
            #comment: 添加输出通道。
            channel_id, channel_label = sa_instance.addChannel(pins_harm[pin_name], 1)
            #comment: 将通道 ID 添加到 output_channel_ids 列表。
            output_channel_ids.append(channel_id)

        #comment: 根据扫频模块参数计算仿真时间点。
        time1 = self._args_harm['InitTime']
        time2 = time1 + ((self._args_harm['EndVal1'] - self._args_harm['InitVal1']) / self._args_harm['DeltaStep1'] + 1) * self._args_harm['DeltaTime1']
        time3 = time2 - self._args_harm['DeltaTime2'] + ((self._args_harm['EndVal2'] - self._args_harm['EndVal1']) / self._args_harm['DeltaStep2'] + 1) * self._args_harm['DeltaTime2']
        time_end = time3 - self._args_harm['DeltaTime3'] + ((self._args_harm['EndVal3'] - self._args_harm['EndVal2']) / self._args_harm['DeltaStep3'] + 1) * self._args_harm['DeltaTime3']

        return sa_instance, harm_id, output_channel_ids, time_end

    def run_simulations(self, sa_instance, output_channel_ids, time_end):
        """
        运行潮流计算和电磁暂态仿真。

        参数:
            sa_instance (SA.StabilityAnalysis): 已配置的 StabilityAnalysis 实例。
            output_channel_ids (list): 输出通道ID的列表。
            time_end (float): 仿真结束时间。

        返回:
            SA.runner.result: 仿真结果对象。
        
        抛出:
            Exception: 如果潮流计算不收敛。
        """
        #comment: 设置仿真采样频率。
        sample_freq = 100
        plot_name = 'SA频率分析'

        #comment: 定义电磁暂态仿真作业名称。
        job_name_emtp = 'SA_电磁暂态仿真'
        #comment: 创建电磁暂态仿真作业。
        sa_instance.createJob(
            'emtp', name=job_name_emtp,
            args={'begin_time': 0, 'end_time': time_end, 'step_time': 0.0001,
                  'task_queue': 'taskManager', 'solver_option': 7, 'n_cpu': 8}
        )
        #comment: 创建潮流计算作业。
        job_name_pf = 'SA_潮流计算'
        sa_instance.createJob('powerFlow', name=job_name_pf)
        #comment: 创建参数方案配置。
        config_name = 'SA_参数方案'
        sa_instance.createConfig(name=config_name)
        #comment: 添加输出通道配置到暂态仿真作业。
        sa_instance.addOutputs(job_name_emtp, {'0': plot_name, '1': str(sample_freq), '2': 'compressed', '3': 1, '4': output_channel_ids})

        #comment: 尝试运行潮流计算。
        try:
            #comment: 运行潮流计算作业。
            message = sa_instance.runProject(jobName=job_name_pf, configName=config_name, showLogs=True)
            #comment: 打印正在回写潮流数据消息。
            print('正在回写潮流数据...')
            #comment: 修改项目，写入潮流结果。
            sa_instance.runner.result.powerFlowModify(sa_instance.project)
        #comment: 如果潮流计算失败，捕获异常。
        except Exception as e:
            #comment: 打印潮流不收敛消息。
            print(f'潮流不收敛！错误: {e}')
            raise Exception('Power flow did not converge.')

        #comment: 运行电磁暂态仿真，开始扫频。
        sa_instance.runProject(jobName=job_name_emtp, configName=config_name)
        #comment: 获取仿真结果。
        sa_result = sa_instance.runner.result
        
        return sa_result

    def process_simulation_results(self, sa_result):
        """
        处理仿真结果，提取阻抗和相位数据。

        参数:
            sa_result (SA.runner.result): 仿真结果对象。

        返回:
            tuple: 包含频率、阻抗和相位数据的元组。
                   - F (np.array): 频率数组。
                   - Z (np.array): 阻抗数组。
                   - Ph (np.array): 相位数组。
        """
        args_harm = self._args_harm
        sample_freq = 100 # 采样频率，与 run_simulations 中的设置保持一致

        #comment: 计算不同扫频阶段的步数。
        N1 = round((args_harm['EndVal1'] - args_harm['InitVal1'] + 1) / args_harm['DeltaStep1'])
        N2 = round((args_harm['EndVal2'] - args_harm['EndVal1']) / args_harm['DeltaStep2'])
        N3 = round((args_harm['EndVal3'] - args_harm['EndVal2']) / args_harm['DeltaStep3'])

        #comment: 计算总步数。
        N = N1 + N2 + N3
        #comment: 初始化阻抗和相位的 numpy 数组。
        Z = np.zeros((N, 3))
        Ph = np.zeros((N, 3))
        #comment: 初始化频率的 numpy 数组。
        F = np.zeros(N)

        #comment: 再次计算仿真阶段的时间点。
        time1 = args_harm['InitTime']
        time2 = time1 + ((args_harm['EndVal1'] - args_harm['InitVal1']) / args_harm['DeltaStep1'] + 1) * args_harm['DeltaTime1']
        time3 = time2 - args_harm['DeltaTime2'] + ((args_harm['EndVal2'] - args_harm['EndVal1']) / args_harm['DeltaStep2'] + 1) * args_harm['DeltaTime2']
        # time_end = time3 - args_harm['DeltaTime3'] + ((args_harm['EndVal3'] - args_harm['EndVal2']) / args_harm['DeltaStep3'] + 1) * args_harm['DeltaTime3'] # 此处time_end已在前面计算，不再重复

        #comment: 定义数据抽取比例。
        rate = 0.1
        
        #comment: 获取第一个绘图的通道名称。
        # 这里默认sa_result.getPlotChannelNames(0)可以获取到所有通道名
        k = 0 # 绘图索引，通常是 0
        channel_names = sa_result.getPlotChannelNames(k)
        
        #comment: 初始化输出通道字典。
        output_channels_map = {}
        #comment: 遍历通道名称，填充 output_channels_map 字典，映射到对应的正序、负序、零序阻抗和相位。
        for name in channel_names:
            if 'Zn' in name:
                output_channels_map['Zn'] = name
            elif 'Zp' in name:
                output_channels_map['Zp'] = name
            elif 'Z' in name and 'Zp' not in name and 'Zn' not in name: # 确保是总Z
                output_channels_map['Z'] = name
            elif 'Php' in name:
                output_channels_map['Php'] = name
            elif 'Phn' in name:
                output_channels_map['Phn'] = name
            elif 'Ph' in name and 'Php' not in name and 'Phn' not in name: # 确保是总Ph
                output_channels_map['Ph'] = name
            elif 'F' in name:
                output_channels_map['Freq'] = name

        #comment: 获取频率通道的名称。
        F_name = output_channels_map['Freq']
        #comment: 获取相位通道的名称列表。
        Ph_names = [output_channels_map['Ph'], output_channels_map['Phn'], output_channels_map['Php']]
        #comment: 获取阻抗通道的名称列表。
        Z_names = [output_channels_map['Z'], output_channels_map['Zn'], output_channels_map['Zp']]

        #comment: 遍历三种序列（零序、负序、正序）。
        for i in range(3):
            #comment: 计算第一阶段的起始采样点位置。
            pos = round(sample_freq * time1)
            #comment: 计算每一步的采样点间隔。
            step = round(sample_freq * args_harm['DeltaTime1'])
            #comment: 遍历第一阶段的 N1 步。
            for j in range(N1):
                #comment: 从结果中提取频率数据，并计算平均值。
                F_temp = sa_result.getPlotChannelData(k, F_name)['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                F[j] = np.sum(F_temp) / len(F_temp) if F_temp else 0
                #comment: 从结果中提取阻抗数据，并计算平均值。
                Z_temp = sa_result.getPlotChannelData(k, Z_names[i])['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                Z[j, i] = np.sum(Z_temp) / len(Z_temp) if Z_temp else 0
                #comment: 从结果中提取相位数据，并计算平均值。
                Ph_temp = sa_result.getPlotChannelData(k, Ph_names[i])['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                Ph[j, i] = np.sum(Ph_temp) / len(Ph_temp) if Ph_temp else 0

            #comment: 计算第二阶段的起始采样点位置。
            pos = round(sample_freq * time2)
            #comment: 计算每一步的采样点间隔。
            step = round(sample_freq * args_harm['DeltaTime2'])
            #comment: 遍历第二阶段的 N2 步。
            for j in range(N2):
                #comment: 从结果中提取频率数据，并计算平均值。
                F_temp = sa_result.getPlotChannelData(k, F_name)['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                F[N1 + j] = np.sum(F_temp) / len(F_temp) if F_temp else 0
                #comment: 从结果中提取阻抗数据，并计算平均值。
                Z_temp = sa_result.getPlotChannelData(k, Z_names[i])['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                Z[N1 + j, i] = np.sum(Z_temp) / len(Z_temp) if Z_temp else 0
                #comment: 从结果中提取相位数据，并计算平均值。
                Ph_temp = sa_result.getPlotChannelData(k, Ph_names[i])['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                Ph[N1 + j, i] = np.sum(Ph_temp) / len(Ph_temp) if Ph_temp else 0

            #comment: 计算第三阶段的起始采样点位置。
            pos = round(sample_freq * time3)
            #comment: 计算每一步的采样点间隔。
            step = round(sample_freq * args_harm['DeltaTime3'])
            #comment: 遍历第三阶段的 N3 步。
            for j in range(N3):
                #comment: 从结果中提取频率数据，并计算平均值。
                F_temp = sa_result.getPlotChannelData(k, F_name)['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                F[N1 + N2 + j] = np.sum(F_temp) / len(F_temp) if F_temp else 0
                #comment: 从结果中提取阻抗数据，并计算平均值。
                Z_temp = sa_result.getPlotChannelData(k, Z_names[i])['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                Z[N1 + N2 + j, i] = np.sum(Z_temp) / len(Z_temp) if Z_temp else 0
                #comment: 从结果中提取相位数据，并计算平均值。
                Ph_temp = sa_result.getPlotChannelData(k, Ph_names[i])['y'][pos + step * (j+1) - 1 - round(rate * step) : pos + step * (j+1) - 1]
                Ph[N1 + N2 + j, i] = np.sum(Ph_temp) / len(Ph_temp) if Ph_temp else 0
        
        return F, Z, Ph

    def save_results(self, F, Z, Ph, current_oat_case, oat_case_index, error_message=None):
        """
        将仿真结果保存到 JSON 文件。

        参数:
            F (np.array): 频率数组。
            Z (np.array): 阻抗数组。
            Ph (np.array): 相位数组。
            current_oat_case (dict): 当前正交实验的参数配置。
            oat_case_index (int): 当前正交实验的索引。
            error_message (str, optional): 如果发生错误，则为错误消息。默认为 None。

        返回:
            None
        """
        #comment: 检查路径是否存在。
        folder = os.path.exists(self._output_path)
        #comment: 如果文件夹不存在，则创建它。
        if not folder:
            os.makedirs(self._output_path)

        #comment: 初始化保存数据的字典。
        data_save = {}
        #comment: 将频率数据转换为列表并保存。
        data_save['F'] = F.tolist() if F is not None else None
        #comment: 将阻抗数据转换为列表并保存。
        data_save['Z'] = Z.tolist() if Z is not None else None
        #comment: 将相位数据转换为列表并保存。
        data_save['Ph'] = Ph.tolist() if Ph is not None else None
        #comment: 将 OATDict 转换为字典并保存。
        data_save['OATDict'] = dict(self._oat_dict)
        #comment: 将当前 OATCase 转换为字典并保存。
        data_save['OATCases'] = dict(current_oat_case)
        #comment: 保存当前迭代索引。
        data_save['i'] = oat_case_index
        #comment: 保存错误消息。
        data_save['Message'] = error_message if error_message else 'Success'

        #comment: 根据 OATCase 的 JSON 字符串生成文件名，移除特殊字符。
        filename = json.dumps(current_oat_case).translate(
            str.maketrans({' ': '', '{': '', '}': '', '"': '', ':': '_', ',': '_'})
        )
        #comment: 将频谱数据保存到 JSON 文件。
        with open(self._output_path + filename + '.json', "w", encoding='utf-8') as f:
            f.write(json.dumps(data_save, indent=4, ensure_ascii=False))

def main():
    """
    主函数，用于执行阻抗和相位数据生成的所有步骤。
    """
    #comment: 实例化 GenerateYZDataCalc 类。
    generator = GenerateYZDataCalc()

    #comment: 打印开始迭代的消息。
    print('Starting Iter...')

    #comment: 将 OATDict 和 OATCases 数据保存到 OAT.json 文件中。
    # 确保保存路径存在
    folder = os.path.exists(generator._output_path)
    if not folder:
        os.makedirs(generator._output_path)
    with open(generator._output_path + 'OAT.json', "w", encoding='utf-8') as f:
        f.write(json.dumps({'OATDict': generator._oat_dict, 'OATCases': generator._oat_cases}, indent=4, ensure_ascii=False))

    #comment: 遍历 OatCasess 中的每个实验案例。
    for oati in range(len(generator._oat_cases)):
    # for oati in range(13): # 用于调试，限制迭代次数
        current_oat_case = generator._oat_cases[oati]
        print(f"Processing OAT Case {oati+1}/{len(generator._oat_cases)}: {current_oat_case}")

        try:
            #comment: 第一步：调用 prepare_environment_and_project 函数，准备 CloudPSS 仿真环境。
            sa_instance, tested_key, wind_ge_key = generator.prepare_environment_and_project()

            #comment: 第二步：调用 modify_model_parameters 函数，根据当前实验案例修改模型参数并添加扫频模块。
            sa_instance, harm_id, output_channel_ids, time_end = generator.modify_model_parameters(
                sa_instance, tested_key, wind_ge_key, current_oat_case
            )

            #comment: 第三步：调用 run_simulations 函数，运行潮流计算和电磁暂态仿真。
            sa_result = generator.run_simulations(sa_instance, output_channel_ids, time_end)

            #comment: 第四步：调用 process_simulation_results 函数，处理仿真结果，提取频率、阻抗和相位数据。
            F, Z, Ph = generator.process_simulation_results(sa_result)

            #comment: 第五步：调用 save_results 函数，保存结果到 JSON 文件。
            generator.save_results(F, Z, Ph, current_oat_case, oati)

        except Exception as e:
            #comment: 捕获异常，并保存错误信息。
            print(f"Error processing OAT Case {oati}: {e}")
            generator.save_results(None, None, None, current_oat_case, oati, error_message=str(e))
        
        # 可选：清理 sa_instance 以释放资源或为下次迭代做准备
        # sa_instance.clear_project() # 假设StabilityAnalysis有这样的清理方法

#comment: 检查当前脚本是否作为主程序运行。
if __name__ == '__main__':
    main()