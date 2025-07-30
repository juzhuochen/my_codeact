#comment: 导入 cloudpss 库，用于与 CloudPSS 平台进行交互。
import cloudpss
#comment: 导入 os 库，用于操作系统相关功能，如设置环境变量。
import os
#comment: 导入 time 库，用于处理时间相关功能，如暂停执行。
import time
#comment: 导入 json 库，用于处理 JSON 格式的数据。
import json
#comment: 导入 re 库，用于正则表达式操作。
import re
#comment: 导入 numpy 库并as np，用于进行数值计算，特别是数组和矩阵操作。
import numpy as np
#comment: 导入 matplotlib 库并as mpl，用于创建静态、交互式和动画的可视化图像。
import matplotlib as mpl
#comment: 从 matplotlib 库导入 pyplot 模块并as plt，是 matplotlib 的绘图接口。
import matplotlib.pyplot as plt
#comment: 从 plotly 库导入 graph_objects 模块并as go，用于创建交互式图表。
import plotly.graph_objects as go
#comment: 导入 pandas 库并as pd，用于数据处理和分析。
import pandas as pd
#comment: 从 jobApi 模块导入 fetch, fetchAllJob, abort 等函数，用于作业管理和数据获取。
from jobApi import fetch,fetchAllJob,abort

#comment: 导入 igraph 库并as ig，用于创建和操作图结构，进行网络分析。
import igraph as ig
#comment: 从 itertools 模块导入 combinations，用于生成迭代器的组合。
from itertools import combinations

#comment: 导入 tkinter 库，用于创建图形用户界面（GUI）。
import tkinter
#comment: 从 tkinter 库导入 filedialog 模块，用于文件选择对话框。
import tkinter.filedialog

#comment: 导入 math 库，用于数学运算。
import math

#comment: 从 IPython.display 模块导入 HTML 类，用于在 IPython 环境中显示 HTML 内容。
from IPython.display import HTML
#comment: 从 html 模块导入 unescape 函数，用于将 HTML 转义字符转换回普通字符。
from html import unescape

#comment: 导入 random 库，用于生成随机数。
import random
#comment: 导入 json 库，用于 JSON 数据处理。
import json
#comment: 导入 copy 库，用于创建对象的深拷贝和浅拷贝。
import copy
#comment: 从 cloudpss.model.implements.component 模块导入 Component 类，表示模型中的组件。
from cloudpss.model.implements.component import Component
#comment: 从 cloudpss.runner.result 模块导入 Result, PowerFlowResult, EMTResult 类，用于处理仿真结果。
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 从 cloudpss.model.revision 模块导入 ModelRevision 类，表示模型的修订版本。
from cloudpss.model.revision import ModelRevision
#comment: 从 cloudpss.model.model 模块导入 Model 类，表示 CloudPSS 中的模型。
from cloudpss.model.model import Model

#comment: 从 scipy 库导入 optimize 模块，用于优化算法。
from scipy import optimize

#comment: 从 string 模块导入 Template 类，用于字符串模板替换。
from string import Template

def is_number(s):
    #comment: 定义一个名为 is_number 的函数，用于检查给定的字符串 s 是否可以转换为数字。
    try:
        #comment: 尝试将字符串 s 转换为浮点数。
        float(s)
        #comment: 如果成功转换，返回 True。
        return True
    except ValueError:
        #comment: 如果捕获到 ValueError（表示无法转换为浮点数），则继续执行。
        pass

    try:
        #comment: 尝试导入 unicodedata 库。
        import unicodedata
        #comment: 尝试使用 unicodedata.numeric() 将字符串 s 转换为数字。
        unicodedata.numeric(s)
        #comment: 如果成功转换，返回 True。
        return True
    except (TypeError, ValueError):
        #comment: 如果捕获到 TypeError 或 ValueError，则继续执行。
        pass

    #comment: 如果所有尝试都失败，返回 False。
    return False

# %%
class CaseEditToolbox:
    #comment: 定义一个名为 CaseEditToolbox 的类，用于编辑和管理仿真案例。
    def __init__(self):
        #comment: 定义类的构造函数，在创建 CaseEditToolbox 实例时自动调用。
        #comment: 初始化配置字典，包含连接信息和参数设置。
        self.config = {};
        #comment: 设置 API 访问的身份验证令牌。
        self.config['token']='123';
        #comment: 设置 API 的基础 URL。
        self.config['apiURL']='cloudpss.net';
        #comment: 设置当前使用的模型名称。
        self.config['model']='test';
        #comment: 设置用户名。
        self.config['username']='admin';
        
        #comment: 设置组件库文件的名称。
        self.config['comLibName'] = 'saSource.json';
        #comment: 设置绘图工具，可选值为 'matplotlib' 或 'plotly'。
        self.config['plotTool'] = 'matplotlib'; #matplotlib, plotly
        #comment: 设置是否生成 iGraph 网络图，默认为 False。
        self.config['iGraph'] = False; # Generate iGraph network
        #comment: 设置是否删除网络中的 'diagram-edges' 类型的组件，并设置引脚名称连接。
        self.config['deleteEdges'] = False; # Delete edges (shape=diagram-edges components) in network, and set pin-name connection
        
        #comment: 初始化项目对象，默认为 0，稍后会设置为实际的项目实例。
        self.project = 0;
        
        #comment: 初始化组件库字典。
        self.compLib = {};
        #comment: 初始化组件计数字典。
        self.compCount = {}
        #comment: 初始化组件位置字典。
        self.pos = {}
        
        #comment: 初始化组件标签字典，用于根据标签查找组件。
        self.compLabelDict = {}
        #comment: 初始化通道引脚字典，用于根据引脚查找通道组件。
        self.channelPinDict = {}

        #comment: 调用 initJobConfig 方法初始化作业配置。
        self.initJobConfig()
        
    def initJobConfig(self):
        #comment: 定义初始化作业配置的方法。
        #comment: 定义 EMTP 仿真作业的初始配置模板。
        self.emtpJob_Init = {'args': {'begin_time': 0,
                #comment: 仿真开始时间。
                'debug': 0,
                #comment: 调试模式开关。
                'end_time': 10,
                #comment: 仿真结束时间。
                'initial_type': 0,
                #comment: 初始条件类型。
                'load_snapshot': 0,
                #comment: 是否加载快照。
                'load_snapshot_name': '',
                #comment: 加载快照的名称。
                'max_initial_time': 1,
                #comment: 最大初始时间。
                'mergeBusNode': 0,
                #comment: 是否合并母线节点。
                'n_cpu': 16,
                #comment: 使用的 CPU 核心数。
                'output_channels': [],
                #comment: 输出通道列表，用于配置仿真结果的输出。
                'ramping_time': 0,
                #comment: 爬升时间。
                'save_snapshot': 0,
                #comment: 是否保存快照。
                'save_snapshot_name': 'snapshot',
                #comment: 保存快照的名称。
                'save_snapshot_time': 1,
                #comment: 保存快照的时间间隔。
                'solver': 0,
                #comment: 求解器类型。
                'solver_option': 7,
                #comment: 求解器选项，7通常表示 CPU_turbol。
                'step_time': 0.0001,
                #comment: 仿真步长。
                'task_cmd': '',
                #comment: 任务命令。
                'task_queue': 'taskManager'},
                #comment: 任务队列名称。
            'name': 'CA电磁暂态仿真方案',
            #comment: 仿真方案的名称。
            'rid': 'function/CloudPSS/emtp'}
            #comment: 仿真任务的资源 ID。

        #comment: 定义潮流计算 (Power Flow) 作业的初始配置模板。
        self.pfJob_Init = {'args': {'CheckInput': 1,
                #comment: 检查输入数据。
                'MaxIteration': 30,
                #comment: 最大迭代次数。
                'ShowRunLog': 2,
                #comment: 显示运行日志级别。
                'SkipPF': 0,
                #comment: 是否跳过潮流计算。
                'UseBusAngleAsInit': 1,
                #comment: 是否使用母线角度作为初始值。
                'UseBusVoltageAsInit': 1,
                #comment: 是否使用母线电压作为初始值。
                'UseReactivePowerLimit': 1,
                #comment: 是否使用无功功率限制。
                'UseVoltageLimit': 1},
                #comment: 是否使用电压限制。
            'name': 'CA潮流计算方案',
            #comment: 潮流计算方案的名称。
            'rid': 'job-definition/cloudpss/power-flow'}
            #comment: 潮流计算任务的资源 ID。

        #comment: 定义 EMTPS 仿真作业的初始配置模板（新版本）。
        self.emtpsJob_Init = {'args': {'@debug': '',
                '@priority': 0,
                #comment: 任务优先级。
                '@queue': 8,
                #comment: 任务队列 ID。
                '@tres': 'cpu=4',#逻辑核心数
                #comment: 任务资源要求，逻辑核心数。
                'begin_time': 0,
                #comment: 仿真开始时间。
                'comm': [],
                #comment: 通信配置。
                'comm_freq': 1,
                #comment: 通信频率。
                'comm_protocol': 0,
                #comment: 通信协议。
                'comm_type': 0,
                #comment: 通信类型。
                'ctrlparallel_option': 0,
                #comment: 控制并行选项。
                'debug': 0,
                #comment: 调试模式开关。
                'dev_id': 1,
                #comment: 设备 ID。
                'dev_num': 1,
                #comment: 设备数量。
                'end_time': 5,
                #comment: 仿真结束时间。
                'event_option': 0,
                #comment: 事件选项。
                'init_cfg': 0,
                #comment: 初始化配置。
                'initial_type': 0,
                #comment: 初始条件类型。
                'kernel_option': 1,
                #comment: 内核选项。
                'load_snapshot': '0',
                #comment: 是否加载快照。
                'load_snapshot_name': '',
                #comment: 加载快照的名称。
                'max_initial_time': 1,
                #comment: 最大初始时间。
                'mergeBusNode': 0,
                #comment: 是否合并母线节点。
                'multi_dev_partition': [],
                #comment: 多设备分区配置。
                'n_cpu': 4, #实际使用的核心数
                #comment: 实际使用的 CPU 核心数。
                'n_ele_cpu': 1,
                #comment: 电气部分使用的 CPU 核心数。
                'only_partition': 0,
                #comment: 仅分区。
                'output_channels': [],
                #comment: 输出通道列表，用于配置仿真结果的输出。
                'partition_info': [{'0': 0, '1': '', '2': '', 'ɵid': 25021700}],
                #comment: 分区信息。
                'partition_msg_output': 1,
                #comment: 分区消息输出。
                'partition_option': 0,
                #comment: 分区选项。
                'ramping_time': 0,
                #comment: 爬升时间。
                'realtime_timeout': 10,
                #comment: 实时超时时间。
                'save_snapshot': 0,
                #comment: 是否保存快照。
                'save_snapshot_name': 'snapshot',
                #comment: 保存快照的名称。
                'save_snapshot_time': 1,
                #comment: 保存快照的时间间隔。
                'sim_option': 0,
                #comment: 仿真选项。
                'snapshot_cfg': 0,
                #comment: 快照配置。
                'solver': 0,
                #comment: 求解器类型。
                'solver_option': 0, # 0:常规，1:分网，2:CPU-turbo
                #comment: 求解器选项，0代表常规。
                'step_time': 5e-05,
                #comment: 仿真步长。
                'task_cmd': '',
                #comment: 任务命令。
                'task_queue': 'taskManager'},
                #comment: 任务队列名称。
                'name': 'CA电磁暂态仿真方案_新',
                #comment: EMTPS 仿真方案的名称。
                'rid': 'function/CloudPSS/emtps'}
                #comment: EMTPS 仿真任务的资源 ID。

        #comment: 定义项目配置 (Project Config) 的初始模板。
        self.proj_Config_Init = {'args': {}, 'name': 'CA参数方案', 'pins': {}}
        #comment: 名称为“CA参数方案”，包含空的参数和引脚字典。
        
    def createJob(self, stype, name = None, args = None):
        #comment: 定义 createJob 方法，用于创建仿真作业。
        #comment: 初始化一个空的作业模板字典。
        jobtemp = {}
        #comment: 如果作业类型是 'emtp'。
        if(stype=='emtp'):
            #comment: 复制 EMTP 仿真作业的初始配置模板。
            jobtemp = copy.deepcopy(self.emtpJob_Init)
        #comment: 如果作业类型是 'powerFlow'。
        elif(stype=='powerFlow'):
            #comment: 复制潮流计算作业的初始配置模板。
            jobtemp = copy.deepcopy(self.pfJob_Init)
        #comment: 如果作业类型是 'emtps'。
        elif(stype=='emtps'):
            #comment: 复制 EMTPS 仿真作业的初始配置模板。
            jobtemp = copy.deepcopy(self.emtpsJob_Init)
        #comment: 如果提供了作业名称。
        if(name!=None):
            #comment: 更新作业模板的名称。
            jobtemp['name'] = name;
        #comment: 如果提供了作业参数。
        if(args!=None):
            #comment: 更新作业模板的参数。
            jobtemp['args'].update(args);
        #comment: 将创建的作业添加到项目中。
        self.project.addJob(jobtemp)
        
    def createConfig(self, name = None, args = None, pins = None):
        #comment: 定义 createConfig 方法，用于创建项目配置。
        #comment: 复制项目配置的初始模板。
        configtemp = copy.deepcopy(self.proj_Config_Init)
        #comment: 如果提供了配置名称。
        if(name!=None):
            #comment: 更新配置模板的名称。
            configtemp['name'] = name;
        #comment: 如果提供了配置参数。
        if(args!=None):
            #comment: 更新配置模板的参数。
            configtemp['args'].update(args);
        #comment: 如果提供了引脚配置。
        if(pins!=None):
            #comment: 更新配置模板的引脚。
            configtemp['pins'].update(pins);
        #comment: 将创建的配置添加到项目中。
        self.project.addConfig(configtemp)
        
    def addOutputs(self, jobName, channels):
        #comment: 定义 addOutputs 方法，用于向 EMTP/EMTPS 计算方案中增加输出通道。
        #comment: 根据作业名称获取对应的作业对象。
        job = self.project.getModelJob(jobName)
        #comment: 检查作业是否存在且其 RID 属于 EMTP 仿真。
        if(job!=[] and re.split('/',job[0]['rid'])[-1]==re.split('/',self.emtpJob_Init['rid'])[-1]):
            #comment: 如果是 EMTP 仿真，将通道信息添加到作业的 'output_channels' 列表中。
            job[0]['args']['output_channels'].append(channels)
        #comment: 检查作业是否存在且其 RID 属于 EMTPS 仿真。
        elif(job!=[] and re.split('/',job[0]['rid'])[-1]==re.split('/',self.emtpsJob_Init['rid'])[-1]):
            #comment: 如果是 EMTPS 仿真，将通道信息添加到作业的 'output_channels' 列表中。
            job[0]['args']['output_channels'].append(channels)
        #comment: 返回当前输出通道列表的最后一个索引。
        return len(job[0]['args']['output_channels']) - 1;
    def runProject(self, jobName, configName,showLogs = False,plotRun = -1, apiUrl = None,websocketErrorTime = None, sleepTime = 10):
        #comment: 定义 runProject 方法，用于运行仿真项目。
        #comment: 获取指定的作业对象。
        job = self.project.getModelJob(jobName)[0]
        #comment: 获取指定的配置对象。
        config = self.project.getModelConfig(configName)[0]

        #comment: 打印开始仿真信息。
        print("Starting Simulation...")
        #comment: 尝试启动仿真器最多5次。
        for i in range(5):
            try:
                #comment: 如果指定了 API URL。
                if(apiUrl!=None):
                    #comment: 使用指定的 API URL 运行项目。
                    self.runner=self.project.run(job=job,config=config,apiUrl=apiUrl) # 运行项目
                else:
                    #comment: 否则，使用默认 API URL 运行项目。
                    self.runner=self.project.run(job=job,config=config)
                #comment: 打印仿真器已启动信息。
                print("Runner started...")
                #comment: 成功启动后跳出循环。
                break
                
            except Exception as e:
                #comment: 如果启动失败，打印错误信息并重试。
                print("Start runner failed, restarting..." + str(e))
                #comment: 等待60秒后重试。
                time.sleep(60)

        #comment: 如果是 EMTP 或 EMTPS 仿真，获取仿真结束时间。
        if(job['rid']==self.emtpJob_Init['rid'] or job['rid']==self.emtpsJob_Init['rid']):
            endstime = float(job['args']['end_time'])
        #comment: 记录仿真开始时间。
        time_start=time.time()
        #comment: 初始化仿真结束时间。
        time_end=0;
        #comment: 打印当前仿真器状态。
        print('Start simulation. Runner Status:'+str(self.runner.status()))
        #comment: 循环检查仿真器状态，直到仿真完成（状态 >= 1）。
        while self.runner.status()<1:
            #comment: 如果是 EMTPS 仿真且有输出通道且 plotRun 大于等于 0。
            if(job['rid']==self.emtpsJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)!=None and plotRun>=0 ):
                #comment: 尝试获取绘图数据。
                datat = self.runner.result.getPlot(plotRun)['data']['traces']
                #comment: 将绘图数据转换为以名称为键的字典。
                datadict = {datat[i]['name']:datat[i] for i in range(len(datat))}
                #comment: 调用 live_plot 方法实时绘制结果。
                self.live_plot(datadict)
                
            #comment: 记录当前时间。
            time_end = time.time();
            #comment: 如果 showLogs 为 True。
            if(showLogs):
                #comment: 遍历并打印仿真日志。
                for log in self.runner.result.getLogs():
                    if('data' in log.keys() and 'content' in log['data'].keys()):
                        print(log['data']['content'])
            #comment: 如果是 EMTP 或 EMTPS 仿真且有输出通道。
            if((job['rid']==self.emtpJob_Init['rid'] or job['rid']==self.emtpsJob_Init['rid'])and self.runner.result.getPlotChannelNames(0)!=None):
                #comment: 获取第一个绘图通道的键。
                ckeytemp = self.runner.result.getPlotChannelNames(0)[0]
                #comment: 获取该通道的时间数据中的最后一个值，表示当前仿真时间。
                stime = self.runner.result.getPlotChannelData(0,ckeytemp)['x'][-1]

                #comment: 打印仿真进度、耗时和仿真器状态。
                print('Progress: Now: '+str(round(stime,2))+ ', All: '+str(endstime)+'. Time cost:',time_end-time_start,'. Runner Status:',self.runner.status())
                #comment: 如果当前仿真时间已达到或超过结束时间，则退出循环。
                if(round(stime,2)==endstime):
                    break;
            else:
                #comment: 如果不是 EMTP/EMTPS 仿真或没有输出通道，只打印耗时和状态。
                print('Time cost:',time_end-time_start,'. Runner Status:',self.runner.status())
            #comment: 暂停指定时间间隔（sleepTime）后继续循环。
            time.sleep(sleepTime)
            #comment: 如果仿真器状态为 -1（表示出错）。
            if self.runner.status()==-1:
                #comment: 打印错误信息，可能是 websocket 问题。
                print('仿真出错了，可能是websocket问题。')
                #comment: 如果设置了 websocketErrorTime 且是 EMTP 仿真且有输出通道。
                if(websocketErrorTime!=None and job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)!=None):
                    #comment: 如果当前仿真时间距离结束时间大于 websocketErrorTime。
                    if(stime < endstime - websocketErrorTime):
                        #comment: 打印准备重新运行仿真的信息。
                        print('准备重新运行仿真。Current Time：'+str(round(stime,2)))
                        #comment: 暂停15秒。
                        time.sleep(15)
                        #comment: 递归调用 runProject 方法重新运行仿真。
                        self.runProject(jobName, configName,showLogs, apiUrl, websocketErrorTime, sleepTime=sleepTime)
                        #comment: 返回仿真器状态。
                        return self.runner.status()
                #comment: 如果设置了 websocketErrorTime 且是 EMTP 仿真但没有输出通道。
                elif(websocketErrorTime!=None and job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)==None):
                    #comment: 打印准备重新运行仿真的信息。
                    print('准备重新运行仿真。Current Time：None')
                    #comment: 递归调用 runProject 方法重新运行仿真。
                    self.runProject(jobName, configName,showLogs, apiUrl, websocketErrorTime, sleepTime=sleepTime)
                #comment: 返回 -1 表示仿真出错。
                return -1
        
        #comment: 仿真完成后，返回仿真器最终状态。
        return self.runner.status()
    def getRunnerLogs(self):
        #comment: 定义 getRunnerLogs 方法，用于获取仿真器的运行日志。
        #comment: 返回仿真器结果对象中的日志。
        return self.runner.result.getLogs()


    
    def saveResult(self, filePath = None, fileName = None):
        #comment: 定义 saveResult 方法，用于保存仿真结果数据文件。
        #comment: 如果没有指定文件名。
        if(fileName == None):
            #comment: 默认文件名为 'Temp.cjob'。
            fileName = 'Temp.cjob'
        #comment: 如果指定了文件路径。
        if(filePath!=None):
            #comment: 将文件路径和文件名拼接起来。
            fileName = filePath + fileName;
        #comment: 将仿真结果保存到指定文件中。
        Result.dump(self.runner.result,fileName)

    def live_plot(self,data_dict, figsize=(7,5), title=''):
        #comment: 定义 live_plot 方法，用于实时绘制数据。
        #comment: 从 IPython.display 模块导入 clear_output 函数，用于清除输出。
        from IPython.display import clear_output
        #comment: 清除当前输出，并等待新输出。
        clear_output(wait=True)
        #comment: 创建一个新的 matplotlib 图形，并设置大小。
        plt.figure(figsize=figsize)
        #comment: 遍历数据字典中的每个标签和数据。
        for label,data in data_dict.items():
            #comment: 绘制数据曲线，x 轴为 'x' 值，y 轴为 'y' 值，并设置标签。
            plt.plot(data['x'],data['y'], label=label)
        #comment: 设置图形标题。
        plt.title(title)
        #comment: 显示网格线。
        plt.grid(True)
        #comment: 设置 x 轴标签为 'epoch'。
        plt.xlabel('epoch')
        #comment: 显示图例，并设置位置为左中。
        plt.legend(loc='center left') # the plot evolves to the right
        #comment: 显示图形。
        plt.show();
    def plotResult(self, result = None, k=None):
        #comment: 定义 plotResult 方法，用于绘制仿真结果。
        #comment: 如果没有提供结果对象。
        if(result==None):
            #comment: 使用当前仿真器的结果。
            result = self.runner.result;
        #comment: 如果结果是字符串类型（表示是文件路径或ID）。
        elif (isinstance(result,str)):
            #comment: 通过 fetch 函数获取结果。
            result = fetch(result);
        
        #comment: 如果配置的绘图工具是 'plotly'。
        if(self.config['plotTool']=='plotly'):
            #comment: 创建一个新的 plotly 图形对象。
            fig = go.Figure()
            #comment: 如果 k 没有指定，默认为 0。
            if k == None:
                k=0
            #comment: 获取第 k 个坐标系的所有通道名称。
            ckeytemp = result.getPlotChannelNames(k)
            #comment: 遍历每个通道。
            for pk in ckeytemp:
                #comment: 获取通道的 x 轴数据。
                x = result.getPlotChannelData(k,pk)['x']
                #comment: 获取通道的 y 轴数据。
                y = result.getPlotChannelData(k,pk)['y']
                #comment: 向图中添加散点图轨迹，模式为线条，名称为通道键。
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
            #comment: 更新图布局，设置主标题、x 轴和 y 轴标题。
            fig.update_layout(
                title=result.getPlot(k)['data']['title'],     # 主标题
                xaxis_title="x Axis Title",  # 2个坐标轴的标题
                yaxis_title="y Axis Title",
            )
            #comment: 显示 plotly 图形。
            fig.show()
        else:
            #comment: 如果配置的绘图工具不是 'plotly' (即 matplotlib)。
            #comment: 创建一个新的 matplotlib 图形，并设置大小。
            fig = plt.figure(figsize=(6, 3))
            #comment: 设置图形标题。
            plt.title(result.getPlot(k)['data']['title'])
            #comment: 获取第 k 个坐标系的所有通道名称。
            ckeytemp = result.getPlotChannelNames(k)
            #comment: 初始化 handles 列表，用于存储图例的句柄。
            handles = []
            #comment: 遍历每个通道。
            for pk in ckeytemp:
                #comment: 获取通道的 x 轴数据。
                x = result.getPlotChannelData(k,pk)['x']
                #comment: 获取通道的 y 轴数据。
                y = result.getPlotChannelData(k,pk)['y']
                #comment: 向图中添加散点图轨迹，模式为线条，名称为通道键 (这里是针对 plotly 的代码，不影响 matplotlib)。
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
                #comment: 使用 matplotlib 绘制数据曲线，并获取图例句柄。
                hd, = plt.plot(x, y, label= pk)
                #comment: 将句柄添加到 handles 列表中。
                handles.append(hd)
            #comment: 设置 x 轴标签。
            plt.xlabel('Time / s', fontproperties="Euclid")
            #comment: 设置 y 轴标签。
            plt.ylabel('Value', fontproperties="Euclid")
            #comment: 显示图例，使用 handles 列表。
            plt.legend(handles = handles)
            #comment: 显示 matplotlib 图形。
            plt.show()
            

        
    def displayPFResult(self, k = None):
        #comment: 定义 displayPFResult 方法，用于显示潮流计算结果。
        #comment: 如果 k 为 None 或 0，显示母线结果。
        if(k == None or k==0):
            #comment: 创建一个空的 pandas DataFrame。
            data = pd.DataFrame()
            #comment: 获取历史总线数据。
            x=self.runner.result.getBuses()
            #comment: 遍历总线数据中的每一列。
            for y in x[0]['data']['columns']:
                #comment: 将列数据添加到 DataFrame 中，列名为 'name'。
                data[y['name']] = y['data']
            #comment: 将 DataFrame 转换为 HTML 字符串。
            s = data.to_html();
            #comment: 解码 HTML 字符串中的转义字符。
            s = unescape(s)
            #comment: 将 HTML 字符串转换为 IPython HTML 对象并显示。
            s = HTML(s)
            #comment: 调用 display 函数显示 HTML 内容。
            display(s)
        #comment: 如果 k 为 None 或 1，显示分支结果。
        if(k==None or k==1):
            #comment: 创建一个空的 pandas DataFrame。
            data = pd.DataFrame()
            #comment: 获取历史分支数据。
            x=self.runner.result.getBranches()
            #comment: 遍历分支数据中的每一列。
            for y in x[0]['data']['columns']:
                #comment: 将列数据添加到 DataFrame 中，列名为 'name'。
                data[y['name']] = y['data']
            #comment: 将 DataFrame 转换为 HTML 字符串。
            s = data.to_html();
            #comment: 解码 HTML 字符串中的转义字符。
            s = unescape(s)
            #comment: 将 HTML 字符串转换为 IPython HTML 对象并显示。
            s = HTML(s)
            #comment: 调用 display 函数显示 HTML 内容。
            display(s)
    
    def initCanvasPos(self, canvas):
        #comment: 定义 initCanvasPos 方法，用于初始化指定图层的坐标。
        #comment: 初始化该图层的坐标字典。
        self.pos[canvas] = {}
        #comment: 设置 x 轴方向的增量。
        self.pos[canvas]['dx'] = 20;
        #comment: 设置 y 轴方向的增量。
        self.pos[canvas]['dy'] = 20;
        #comment: 设置 x 轴的起始坐标。
        self.pos[canvas]['x0'] = 20;
        #comment: 设置 y 轴的起始坐标。
        self.pos[canvas]['y0'] = 20;
        #comment: 设置当前 x 轴坐标为起始坐标。
        self.pos[canvas]['x'] = self.pos[canvas]['x0'];
        #comment: 设置当前 y 轴坐标为起始坐标。
        self.pos[canvas]['y'] = self.pos[canvas]['y0'];
        
        #comment: 初始化当前行中组件的最大高度，用于换行计算。
        self.pos[canvas]['maxdy'] = 0;
        
    
    def getRevision(self, file = None):
        #comment: 定义 getRevision 方法，用于获取当前项目的修订信息。
        #comment: 深拷贝当前项目的修订信息为 JSON 格式。
        r1 = copy.deepcopy(self.project.revision.toJSON());
        #comment: 如果指定了文件路径。
        if file!=None:
            #comment: 以写入模式打开文件，并指定 UTF-8 编码。
            with open(file, "w", encoding='utf-8') as f:
                #comment: 将修订信息以格式化的 JSON 字符串写入文件。
                f.write(json.dumps(r1, indent=4))
        #comment: 返回修订信息。
        return r1
    
    def loadRevision(self, revision = None, file = None):
        #comment: 定义 loadRevision 方法，用于加载模型修订信息。
        #comment: 如果提供了修订的 JSON 格式数据。
        if(revision!=None):
            #comment: 使用该数据创建 ModelRevision 对象并赋值给当前项目的修订。
            self.project.revision = ModelRevision(revision);
        else:
            #comment: 如果提供了文件路径。
            #comment: 以读取模式打开文件，并指定 UTF-8 编码。
            with open(file, "r", encoding='utf-8') as f:
                #comment: 从文件中加载 JSON 数据。
                data_from_file = json.load(f)
                #comment: 使用加载的数据创建 ModelRevision 对象并赋值给当前项目的修订。
                self.project.revision = ModelRevision(data_from_file);

    
    def setConfig(self,token = None, apiURL = None, username = None, model = None, comLibName = None):
        #comment: 定义 setConfig 方法，用于配置模块的连接信息和参数。
        #comment: 如果提供了 token，更新配置。
        if(token != None):
            self.config['token']=token;
        #comment: 如果提供了 apiURL，更新配置。
        if(apiURL != None):
            self.config['apiURL']=apiURL;
        #comment: 如果提供了 username，更新配置。
        if(username!=None):
            self.config['username']=username;
        #comment: 如果提供了 model，更新配置。
        if(model!=None):
            self.config['model']=model;
        #comment: 如果提供了 comLibName，更新配置。
        if(comLibName!=None):
            self.config['comLibName']=comLibName;
        
    def setInitialConditions(self):
        #comment: 定义 setInitialConditions 方法，用于初始化模块的 CloudPSS 连接和加载组件库。
        #comment: 设置 CloudPSS 的访问令牌。
        cloudpss.setToken(self.config['token'])
        #comment: 设置 CloudPSS API 的 URL 环境变量。
        os.environ['CLOUDPSS_API_URL'] = self.config['apiURL']
        #comment: 打印正在获取算例的信息。
        print('正在获取算例...')
        #comment: 从 CloudPSS 平台获取指定的模型项目。
        self.project = cloudpss.Model.fetch('model/'+self.config['username']+'/'+self.config['model'])
        #comment: 以读取模式打开组件库文件，并指定 UTF-8 编码。
        with open(self.config['comLibName'], "r", encoding='utf-8') as f:
            #comment: 从文件中加载 JSON 格式的组件库数据。
            self.compLib = json.load(f)
        #comment: 初始化组件计数，将组件库中的所有键的计数设置为 0。
        self.compCount = {key:0 for key in self.compLib.keys()}
        #comment: 如果配置为删除边元件。
        if (self.config['deleteEdges']):
            #comment: 打印正在获取拓扑信息。
            print('正在获取拓扑信息...');
            #comment: 调用 refreshTopology 方法刷新拓扑信息。
            self.refreshTopology()
            #comment: 打印正在替换引脚连接关系。
            print('正在替换引脚连接关系...')
            #comment: 调用 deleteEdges 方法删除边并设置引脚连接。
            self.deleteEdges()
        #comment: 打印正在初始化。
        print('正在初始化...')
        #comment: 调用 setCompLabelDict 方法设置组件标签字典。
        self.setCompLabelDict()
        #comment: 调用 setChannelPinDict 方法设置通道引脚字典。
        self.setChannelPinDict()
        #comment: 如果配置为生成 iGraph 网络。
        if(self.config['iGraph'] == True):
            #comment: 打印正在生成 iGraph 图（耗时较长）的信息。
            print('正在生成iGraph图（耗时较长，可在config中设置iGraph为False以关闭该功能）...')
            #comment: 再次调用 refreshTopology 方法刷新拓扑信息，以确保最新。
            self.refreshTopology()
            #comment: 调用 generateNetwork 方法生成网络图。
            self.generateNetwork()
            #comment: 定义网络图形的形状配置，用于不同 RID 的组件。
            self.NetShapeConfig = {'model/CloudPSS/_newBus_3p':{'color':'cyan','shape':'circle','size':8,'label_size':10},
                'model/CloudPSS/_newTransformer_3p2w':{'color':'darkolivegreen','shape':'triangle-up','size':8,'label_size':10},
                'model/CloudPSS/_newTransformer_3p3w':{'color':'darkolivegreen','shape':'triangle-up','size':8,'label_size':10},
                'model/CloudPSS/TranssmissionLineRouter':{'color':'gold','shape':'square-open','size':8,'label_size':10},
                'model/CloudPSS/SyncGeneratorRouter':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                'model/admin/WGSource':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                'model/CloudPSS/PVStation':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                'model/CloudPSS/_newACVoltageSource_3p':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                'model/admin/DCLine':{'color':'orange','shape':'square','size':10,'label_size':10}
                }



    def refreshTopology(self):
        #comment: 定义 refreshTopology 方法，用于刷新拓扑信息。
        #comment: 创建一个新的模型版本，使用当前项目的修订版本。
        revision = cloudpss.ModelRevision.create(self.project.revision)
        #comment: 获取拓扑信息，使用当前配置和最大深度为0。
        self.topo = cloudpss.ModelTopology.fetch(revision['hash'], 'emtp', self.project.configs[self.project.context['currentConfig']],maximumDepth = 0).toJSON()
    
    def getEdgeTopoPinNum(self,cid):
        #comment: 定义 getEdgeTopoPinNum 方法，用于获取边元素的拓扑引脚编号。
        #comment: 根据组件 ID 获取组件对象。
        j = self.project.getComponentByKey(cid)
        #comment: 遍历源和目标。
        for st in range(2):
            #comment: 获取源或目标字典。
            sourcetarget=[j.source, j.target][st]
            #comment: 如果 'cell' 键不存在于 sourcetarget 中，则跳过。
            if('cell' not in sourcetarget.keys()):
                continue
            #comment: 获取单元格 ID。
            c0 = sourcetarget['cell']
            #comment: 构造带斜杠的单元格 ID。
            c = '/'+c0
            #comment: 如果 'port' 键不存在于 sourcetarget 中。
            if('port' not in sourcetarget.keys()):
                #comment: 递归调用自身，传入项目、拓扑和单元格 ID。
                return self.getEdgeTopoPinNum(self.project,self.topo,c0)
            #comment: 如果单元格 ID 存在于拓扑的组件中。
            if(c in self.topo['components'].keys()):
                #comment: 返回对应引脚的拓扑编号。
                return self.topo['components'][c]['pins'][sourcetarget['port']]
            #comment: 如果以上条件都不满足，返回 '0'。
            return '0'
            
        
    def deleteEdges(self):
        #comment: 定义 deleteEdges 方法，用于删除边元件并替换引脚连接关系。
        #comment: 初始化拓扑引脚名称字典。
        self.topoPinNameDict = {}
        #comment: 遍历拓扑中的所有组件。
        for i,j in self.topo['components'].items():
            #comment: 遍历组件的所有引脚。
            for p,k in j['pins'].items():
                #comment: 如果引脚值为空，则跳过。
                if(k==''):
                    continue
                #comment: 如果引脚编号不在字典中，则添加。
                if(int(k) not in self.topoPinNameDict.keys()):
                    self.topoPinNameDict[int(k)] = []
                #comment: 获取引脚名称。
                pname = self.project.getComponentByKey(i[1:]).pins[p]
                #comment: 如果引脚名称不为空且不在列表中，则添加。
                if(pname!='' and pname not in self.topoPinNameDict[int(k)]):
                    self.topoPinNameDict[int(k)].append(pname)
            #comment: 遍历组件的所有参数值。
            for k in j['args'].values():
                #comment: 如果参数值存在于拓扑的输入映射中。
                if(str(k) in self.topo['mappings']['in'].keys()):
                    #comment: 获取对应的映射值。
                    kk = self.topo['mappings']['in'][k]
                #comment: 如果参数值存在于拓扑的输出映射中。
                elif(str(k) in self.topo['mappings']['out'].keys()):
                    #comment: 获取对应的映射值。
                    kk = self.topo['mappings']['out'][k]
                else:
                    #comment: 否则跳过。
                    continue
                #comment: 如果映射值不在字典中，则添加。
                if(int(kk) not in self.topoPinNameDict.keys()):
                    self.topoPinNameDict[int(kk)] = []
                    #comment: 获取引脚名称。
                    pname = self.project.getComponentByKey(i[1:]).pins[p]
                    #comment: 如果引脚名称不为空且不在列表中，则添加。
                    if(pname!='' and pname not in self.topoPinNameDict[int(kk)]):
                        self.topoPinNameDict[int(kk)].append(pname)
        #comment: 初始化计数器。
        count = 0
        #comment: 生成自动添加的引脚名前缀。
        pinName0 = 'AutoAddPin'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_'
        #comment: 遍历拓扑引脚名称字典。
        for i,j in self.topoPinNameDict.items():
            #comment: 如果列表为空。
            if(j==[]):
                #comment: 添加新的引脚名称。
                j.append(pinName0+str(count))
                #comment: 计数器递增。
                count = count+1
        #comment: 打印完成阶段1。
        print('finish 1')
        #comment: 初始化拓扑引脚边字典。
        topoPinEdgeDict = {}
        #comment: 遍历项目中的所有组件。
        for i,j in self.project.getAllComponents().items():
            #comment: 如果组件形状不是 'diagram-edge'，则跳过。
            if(j.shape != 'diagram-edge'):
                continue
            #comment: 获取边元件的拓扑引脚编号。
            p = self.getEdgeTopoPinNum(i)
            #comment: 如果引脚编号不在字典中，则添加。
            if(p not in topoPinEdgeDict.keys()):
                topoPinEdgeDict[p] = []
            #comment: 如果组件 ID 不在列表中，则添加。
            if(i not in topoPinEdgeDict[p]):
                topoPinEdgeDict[p].append(i)
        #comment: 遍历拓扑引脚边字典的键。
        for tped_ptr in topoPinEdgeDict.keys():
            #comment: 遍历每个引脚编号对应的组件 ID 列表。
            for i in topoPinEdgeDict[tped_ptr]:
                #comment: 根据组件 ID 获取组件对象。
                j = self.project.getComponentByKey(i)
                #comment: 如果组件形状不是 'diagram-edge'，则跳过。
                if(j.shape != 'diagram-edge'):
                    continue
                #comment: 遍历源和目标。
                for st in range(2):
                    #comment: 获取源或目标字典。
                    sourcetarget=[j.source, j.target][st]
                    #comment: 如果 'cell' 或 'port' 键不存在于 sourcetarget 中，则跳过。
                    if(('cell' not in sourcetarget.keys()) or ('port' not in sourcetarget.keys())):
                        continue
                    #comment: 如果源/目标单元的引脚为空。
                    if(self.project.getComponentByKey(sourcetarget['cell']).pins[sourcetarget['port']]==''):
                        #comment: 将其引脚设置为拓扑引脚名称字典中对应的值。
                        self.project.getComponentByKey(sourcetarget['cell']).pins[sourcetarget['port']] = self.topoPinNameDict[int(tped_ptr)][0]
                #comment: 从修订中移除边元件。
                self.project.revision.implements.diagram.cells.pop(i)

    def generateNetwork(self,centerRID = ['model/CloudPSS/_newBus_3p']):
        #comment: 定义 generateNetwork 方法，用于生成 iGraph 网络图。

        #comment: 创建一个无向图。
        self.g = ig.Graph(directed = False)
        #comment: 初始化拓扑引脚组件字典。
        self.topoPinCompDict = {}
        #comment: 遍历拓扑中的所有组件。
        for i,j in self.topo['components'].items():
            #comment: 向图中添加顶点，名称为组件 ID，RID 为组件定义。
            self.g.add_vertex(i,rid = j['definition'])
            #comment: 遍历组件的所有引脚。
            for p,k in j['pins'].items():
                #comment: 如果引脚值为空，则跳过。
                if(k==''):
                    continue
                #comment: 如果引脚编号不在字典中，则添加。
                if(int(k) not in self.topoPinCompDict.keys()):
                    self.topoPinCompDict[int(k)] = []
                #comment: 如果组件 ID 不在列表中，则添加。
                if(i not in self.topoPinCompDict[int(k)]):
                    self.topoPinCompDict[int(k)].append(i)
            #comment: 遍历组件的所有参数值。
            for k in j['args'].values():
                #comment: 如果参数值存在于拓扑的输入映射中。
                if(str(k) in self.topo['mappings']['in'].keys()):
                    #comment: 获取对应的映射值。
                    kk = self.topo['mappings']['in'][k]
                #comment: 如果参数值存在于拓扑的输出映射中。
                elif(str(k) in self.topo['mappings']['out'].keys()):
                    #comment: 获取对应的映射值。
                    kk = self.topo['mappings']['out'][k]
                else:
                    #comment: 否则跳过。
                    continue
                #comment: 如果映射值不在字典中，则添加。
                if(int(kk) not in self.topoPinCompDict.keys()):
                    self.topoPinCompDict[int(kk)] = []
                    #comment: 如果组件 ID 不在列表中，则添加。
                    if(i not in self.topoPinCompDict[int(kk)]):
                        self.topoPinCompDict[int(kk)].append(i)
        #comment: 初始化边列表。
        ess = []
        #comment: 初始化边值列表。
        value = []
        #comment: 遍历拓扑引脚组件字典。
        for i,j in self.topoPinCompDict.items():
            #comment: 如果列表长度小于 2，则跳过（无法形成边）。
            if(len(j)<2):
                continue
            #comment: 遍历中心 RID 列表。
            for centerrid in centerRID:
                #comment: 如果中心 RID 存在于组件定义中。
                if(centerrid in [self.topo['components'][k]['definition'] for k in j]):
                    #comment: 获取中心组件的索引。
                    index = [self.topo['components'][k]['definition'] for k in j].index(centerrid);
                    #comment: 生成以中心组件为参考的边。
                    es = [(j[k],j[index]) for k in range(len(j)) if k != index]
                    #comment: 找到中心 RID 后跳出循环。
                    break
            else:
                #comment: 如果没有找到中心 RID，则生成所有组件的两两组合。
                es = list(combinations(j, 2))
                
            #comment: 将生成的边添加到边列表中。
            ess = ess + es
            #comment: 将对应的引脚编号添加到边值列表中。
            value = value + [i for k in range(len(es))]
        
        #comment: 向图中添加边，并设置 'value' 属性为引脚编号。
        self.g.add_edges(ess,attributes= {'value':value})
        #comment: 设置图中顶点的 'label' 属性为组件的标签。
        self.g.vs['label'] = [self.topo['components'][i]['label'] for i in self.g.vs['name']]
        #comment: 设置图中顶点的默认形状。
        self.g.vs['shape'] = 'circle-dot'
        #comment: 设置图中顶点的默认大小。
        self.g.vs['size'] = 2

    def getNetworkNeighbor(self,vid,nn,chooseRIDList = [],network = None):
        #comment: 定义 getNetworkNeighbor 方法，用于获取网络中指定顶点的邻居子图。
        #comment: 如果没有指定网络，则使用当前对象的网络图。
        if(network == None):
            network = self.g
        #comment: 初始化标志为 1。
        flag = 1
        #comment: 如果 vid 存在于网络顶点的名称中。
        if(vid in network.vs['name']):
            #comment: 查找对应的顶点。
            a = network.vs.find(vid) 
        else:
            #comment: 否则，将标志设为 0，并尝试通过标签和 RID 查找顶点。
            flag=0
            a = network.vs.find(label=vid,rid = 'model/CloudPSS/_newBus_3p') 
        #comment: 初始化邻居顶点集合为包含顶点 a。
        b = set([a])
        #comment: 循环 nn 次，扩展邻居范围。
        for k in range(nn):
            #comment: 复制当前邻居集合。
            b0 = b.copy()
            #comment: 遍历邻居集合中的每个顶点。
            for ii in b:
                #comment: 获取当前顶点的邻居集合。
                c = set(ii.neighbors())
                #comment: 将邻居集合合并到 b0 中。
                b0 = b0.union(c)
            #comment: 更新 b 为新的邻居集合。
            b = b0
        #comment: 如果指定了选择 RID 列表。
        if(chooseRIDList!=[]):
            #comment: 筛选 b 中 RID 存在于选择列表中的顶点。
            b = set(i for i in b if i['rid'] in chooseRIDList)
        #comment: 从原始网络中创建包含筛选后的顶点和边的子图。
        sg = network.subgraph(b)
        #comment: 根据预定义的网络形状配置，为子图中的顶点设置颜色、形状、大小、字体和标签大小。
        for ii in self.NetShapeConfig.keys():
            jj = self.NetShapeConfig[ii]
            bb = sg.vs.select(rid = ii);
            bb['color'] = jj['color']
            bb['shape'] = jj['shape']
            bb['size'] = jj['size']
            bb['font'] = 'SimHei'
            bb['label_size'] = jj['label_size']

        #comment: 再次查找起始顶点 a，现在在子图中。
        if(vid in network.vs['name']):
            a = sg.vs.find(vid) 
        else:
            #comment: 如果之前 flag 为 0，则再次通过标签和 RID 查找顶点。
            flag=0
            a = sg.vs.find(label=vid,rid = 'model/CloudPSS/_newBus_3p') 
        #comment: 设置起始顶点 a 的颜色为 'chocolate'。
        a['color'] = 'chocolate'
        #comment: 返回生成的子图。
        return sg
    
    def plotNetwork(self,a, showlabel = False, show = True):
        #comment: 定义 plotNetwork 方法，用于绘制网络图。
        #comment: 获取图 a 中所有顶点的标签。
        labels=list(a.vs['label'])
        #comment: 获取顶点数量。
        N=len(labels)
        #comment: 获取图中所有边的元组列表。
        E=[e.tuple for e in a.es]# list of edges
        #comment: 使用 Kamada-Kawai 布局算法计算顶点位置。
        layt = a.layout_kamada_kawai()
        #comment: 获取 x 坐标。
        Xn=[layt[k][0] for k in range(N)]
        #comment: 获取 y 坐标。
        Yn=[layt[k][1] for k in range(N)]
        #comment: 初始化边 x 坐标列表。
        Xe=[]
        #comment: 初始化边 y 坐标列表。
        Ye=[]
        #comment: 遍历每条边。
        for e in E:
            #comment: 将边的起点和终点坐标添加到列表中，中间插入 None 以断开线条。
            Xe+=[layt[e[0]][0],layt[e[1]][0], None]
            Ye+=[layt[e[0]][1],layt[e[1]][1], None]

        #comment: 创建 plotly 散点图轨迹，表示边。
        trace1=go.Scatter(x=Xe,
                    y=Ye,
                    mode='lines',
                    line= dict(color='rgb(210,210,210)', width=1),
                    hoverinfo='none'
                    )
        #comment: 根据 showlabel 决定点的显示模式。
        if(showlabel):
            mode = 'markers+text';
        else:
            mode = 'markers'
        #comment: 创建 plotly 散点图轨迹，表示顶点。
        trace2=go.Scatter(x=Xn,
                    y=Yn,
                    mode=mode,
                    name='ntw',
                    marker=dict(symbol=[5 if i ==None else i for i in a.vs.get_attribute_values('shape')],
                                                size=[5 if i ==None else i for i in a.vs.get_attribute_values('size') ],
                                                color=['#6959CD' if i ==None else i for i in a.vs.get_attribute_values('color') ],
                                                line=dict(color='rgb(50,50,50)', width=0.5)
                                                ),
                    text=labels
                    )

        #comment: 定义轴的布局，隐藏轴线、网格、刻度标签和标题。
        axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

        #comment: 定义图形的宽度和高度。
        width=800
        height=800
        #comment: 定义 plotly 图形的布局。
        layout=go.Layout(
            font= dict(size=12),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            autosize=False,
            width=width,
            height=height,
            xaxis=go.layout.XAxis(axis),
            yaxis=go.layout.YAxis(axis),
            margin=go.layout.Margin(
                l=40,
                r=40,
                b=85,
                t=100,
            ),
            hovermode='closest',
            annotations=[
                dict(
                showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1,
                    xanchor='left',
                    yanchor='bottom',
                    font=dict(
                    size=14
                    )
                    )
                ]
            )

        #comment: 将轨迹和布局组合成 plotly 图形数据。
        data=[trace1, trace2]
        #comment: 创建 plotly 图形对象。
        fig=go.Figure(data=data, layout=layout)
        #comment: 如果 show 为 True，则显示图形。
        if(show):
            fig.show()
        #comment: 返回 plotly 图形对象。
        return fig

    def setCompLabelDict(self):
        #comment: 定义 setCompLabelDict 方法，用于生成组件标签到组件对象的字典。
        #comment: 初始化组件标签字典。
        self.compLabelDict = {}
        #comment: 遍历项目中所有组件的键。
        for key in self.project.getAllComponents().keys():
            #comment: 获取当前组件对象。
            comptemp = self.project.getComponentByKey(key)
            #comment: 如果组件形状包含 'diagram-component'。
            if('diagram-component' in comptemp.shape):
                #comment: 获取组件标签。
                label = comptemp.label;
                #comment: 如果标签不在字典中，则添加一个新的空字典。
                if(label not in self.compLabelDict.keys()):
                    self.compLabelDict[label] = {}
                #comment: 将组件添加到对应标签的字典中，键为组件键。
                self.compLabelDict[label][key] = comptemp;
            
    def setChannelPinDict(self):
        #comment: 定义 setChannelPinDict 方法，用于生成输出通道引脚到通道组件键的字典。
        #comment: 初始化通道引脚字典。
        self.channelPinDict = {}
        #comment: 遍历所有 RID 为 'model/CloudPSS/_newChannel' 的组件的键。
        for key in self.project.getComponentsByRid('model/CloudPSS/_newChannel').keys():
            #comment: 获取当前通道组件对象。
            comptemp = self.project.getComponentByKey(key)
            #comment: 获取通道的引脚 '0' 的值。
            pin0 = comptemp.pins['0'];
            #comment: 将通道引脚值映射到组件键。
            self.channelPinDict[str(pin0)] = key;    
    
    def addComp(self,compJson,id1 = None,canvas = None, position = None, args = None, pins = None, label = None):
        #comment: 定义 addComp 方法，用于向项目中增添元件。
        #comment: 深拷贝组件的 JSON 数据，以避免修改原始数据。
        compJson1 = copy.deepcopy(compJson)
        
        #comment: 如果提供了 id1，更新组件 JSON 中的 ID。
        if id1!=None:
            compJson1['id'] = id1;
        #comment: 如果提供了 position，更新组件 JSON 中的位置。
        if position!=None:
            compJson1['position'] = position;
        #comment: 如果提供了 canvas，更新组件 JSON 中的所属图层。
        if canvas!=None:
            compJson1['canvas'] = canvas;
        #comment: 如果提供了 args，更新组件 JSON 中的参数。
        if args!=None:
            compJson1['args'].update(args)
        #comment: 如果提供了 pins，更新组件 JSON 中的引脚。
        if pins!=None:
            compJson1['pins'].update(pins)
        #comment: 如果提供了 label，更新组件 JSON 中的标签。
        if label!=None:
            compJson1['label'] = label
        #comment: 使用更新后的 JSON 数据创建一个 Component 对象。
        comp = Component(compJson1)
        #comment: 将新创建的组件添加到项目的修订模型图中。
        self.project.revision.implements.diagram.cells[compJson1['id']]=comp
    
    def addxPos(self, canvas, compJson, MaxX = None):
        #comment: 定义 addxPos 方法，用于更新图层中 x 轴坐标，并处理换行。
        #comment: 根据组件宽度更新当前 x 坐标。
        self.pos[canvas]['x'] = self.pos[canvas]['x'] + compJson['size']['width'];
        #comment: 更新当前行中组件的最大高度。
        self.pos[canvas]['maxdy'] = max(self.pos[canvas]['maxdy'],compJson['size']['height'])
        #comment: 如果设置了 MaxX 且当前 x 坐标超出 MaxX，则执行换行操作。
        if(MaxX != None and MaxX < self.pos[canvas]['x']):
            self.newLinePos(canvas)
        
    def newLinePos(self, canvas):
        #comment: 定义 newLinePos 方法，用于在指定图层中进行换行。
        #comment: 将 x 坐标重置为起始 x 坐标。
        self.pos[canvas]['x'] = self.pos[canvas]['x0']
        #comment: 将 y 坐标向下移动一行的高度。
        self.pos[canvas]['y'] = self.pos[canvas]['y'] + self.pos[canvas]['dy'] + self.pos[canvas]['maxdy']
        #comment: 重置当前行中组件的最大高度。
        self.pos[canvas]['maxdy'] = 0;
        
    def addCompInCanvas(self,compJson,key,canvas, addN = None, addN_label = None,args = None, pins = None, label = None,dX = 10, MaxX = None):
        #comment: 定义 addCompInCanvas 方法，用于在图层中添加元件，处理命名、坐标和参数。
        #comment: 如果 addN 未指定，则默认为 True。
        if(addN == None):
            addN = True
        #comment: 如果 addN_label 未指定，则默认为 False。
        if(addN_label == None):
            addN_label = False
        #comment: 复制当前图层的 x 和 y 坐标作为添加位置。
        posTemp = {k: v for k, v in self.pos[canvas].items() if k in ['x','y']}
        
        
        #comment: 如果组件键不在计数字典中，则初始化为 0。
        if(key not in self.compCount.keys()):
            self.compCount[key] = 0;
        #comment: 如果 addN 为 True，则为组件键添加计数后缀。
        if(addN):
            self.compCount[key]+=1;
            id1Temp = key+'_'+str(self.compCount[key]);
        else:
            #comment: 否则，组件键保持不变。
            id1Temp = key;
        #comment: 如果 label 未指定，则使用生成的 id1Temp 作为 label。
        if (label==None):
            label = id1Temp;
        #comment: 如果 addN_label 为 True，则为 label 添加计数后缀。
        if(addN_label):
            label = label + '_'+str(self.compCount[key]);
            
        #comment: 创建参数的副本。
        argsCopy = args.copy()
        #comment: 如果参数中包含 'Name' 且 addN_label 为 True。
        if('Name' in argsCopy.keys() and addN_label):
            #comment: 为 'Name' 参数添加计数后缀。
            argsCopy['Name'] = argsCopy['Name'] + '_' + str(self.compCount[key]);
        
        #comment: 调用 addComp 方法实际添加元件。
        self.addComp(compJson,id1Temp,canvas, posTemp, argsCopy, pins, label)
        #comment: 更新 x 轴坐标，并处理可能的换行。
        self.addxPos(canvas, compJson, MaxX)
        #comment: 在当前 x 轴坐标上增加一个额外的偏移量 dX。
        self.pos[canvas]['x'] = self.pos[canvas]['x'] + dX;

        #comment: 返回生成的组件 ID 和标签。
        return id1Temp, label
    
    def createCanvas(self,canvas,name):
        #comment: 定义 createCanvas 方法，用于新增图纸（画布）。
        #comment: 将新的画布信息添加到项目的修订模型图中。
        self.project.revision.implements.diagram.canvas.append({'key': canvas, 'name': name})
        #comment: 初始化新画布的坐标。
        self.initCanvasPos(canvas)
    
    def screenCompByArg(self, compRID, conditions, compList = None):
        #comment: 定义 screenCompByArg 方法，用于通过参数条件筛选元件。
        #comment: 获取指定 RID 的所有组件。
        comps = self.project.getComponentsByRid(compRID)
        #comment: 初始化筛选后的组件字典。
        screenedComps = {}
        #comment: 如果 conditions 不是列表，则将其转换为列表。
        if not isinstance(conditions,list):
            conditions = [conditions]
        
        #comment: 如果提供了 compList。
        if(compList!=None):
            #comment: 找出 comps 键和 compList 的交集。
            screenedKeys = set(comps.keys()) & set(compList);
            #comment: 根据交集中的键重新构建 comps 字典。
            comps = dict([(key, comps.get(key, None)) for key in screenedKeys])
            
        #comment: 遍历筛选后的组件键。
        for k in comps.keys():
            #comment: 初始化标志为 True。
            flag = True;
            #comment: 遍历所有筛选条件。
            for c in conditions:
                #comment: 如果参数名称是 'label'。
                if(c['arg']=='label'):
                    #comment: 获取组件的标签。
                    a = comps[k].label
                else:
                    #comment: 否则，获取组件的对应参数值。
                    a = comps[k].args[c['arg']]
                
                #comment: 重新设置标志为 True。
                flag = True;
                #comment: 获取条件的最小值、最大值和集合。
                Min = c['Min']
                Max = c['Max']
                Set = c['Set']
                #comment: 如果参数值 a 是数字，并且 Min 和 Max 也是数字（或 None）。
                if is_number(a) and ( Min == None or is_number(Min)) and (Max == None or is_number(Max)):
                    #comment: 如果 Min 不为 None 且 a 小于 Min，则标志设为 False 并跳出循环。
                    if(Min!=None and float(Min) > float(a)):
                        flag = False;
                        break
                    #comment: 如果 Max 不为 None 且 a 大于 Max，则标志设为 False 并跳出循环。
                    if(Max!=None and float(Max) < float(a)):
                        flag = False;  
                        break
                    #comment: 如果 Set 不为 None 且 a 不在 Set 中，则标志设为 False 并跳出循环。
                    if(Set!=None and (a not in Set)):
                        flag = False;
                        break
                else:
                    #comment: 如果参数值 a 不是数字或 Min/Max 不全是数字，则进行字符串比较。
                    #comment: 如果 Min 不为 None 且 a 小于 Min，则标志设为 False 并跳出循环。
                    if(Min!=None and Min > a):
                        flag = False;
                        break
                    #comment: 如果 Max 不为 None 且 a 大于 Max，则标志设为 False 并跳出循环。
                    if(Max!=None and Max < a):
                        flag = False;  
                        break
                    #comment: 如果 Set 不为 None 且 a 不在 Set 中，则标志设为 False 并跳出循环。
                    if(Set!=None and (a not in Set)):
                        flag = False;
                        break

            #comment: 如果所有条件都满足（flag 仍为 True）。
            if(flag):
                #comment: 将该组件添加到筛选后的组件字典中。
                screenedComps[k] = comps[k];
        #comment: 返回筛选后的组件字典。
        return screenedComps
                
    
    def saveProject(self, newID, name = None, desc = None):
        #comment: 定义 saveProject 方法，用于保存算例项目。
        #comment: 如果提供了名称，更新项目的名称。
        if(name!=None):
            self.project.name = name;
        #comment: 如果提供了描述，更新项目的描述。
        if(desc!=None):
            self.project.description = desc;
        #comment: 调用项目对象的 save 方法，保存项目并返回结果。
        return self.project.save(newID)

    def getCompLib(self, tk, apiURL, spr, compDefLib = {}, name = None):
        #comment: 定义 getCompLib 方法，用于获取组件库并保存为 JSON 文件。
        #comment: 设置 CloudPSS 的访问令牌。
        cloudpss.setToken(tk)
        #comment: 设置 CloudPSS API 的 URL 环境变量。
        os.environ['CLOUDPSS_API_URL'] = apiURL
        #comment: 获取指定的 CloudPSS 模型项目。
        sproject = cloudpss.Model.fetch(spr)
        #comment: 初始化组件库字典。
        compLib = {}
        #comment: 如果 compDefLib 为空，则定义默认的组件定义库。
        if compDefLib=={}:
            #comment: 定义默认组件 RID 到名称的映射。
            compDefLib = {'GND':'model/CloudPSS/GND',
                    '_newChannel':'model/CloudPSS/_newChannel',
                    '_newBreaker_3p':'model/CloudPSS/_newBreaker_3p',
                    '_newShuntLC_3p':'model/CloudPSS/_newShuntLC_3p',
                    'newCapacitorRouter':'model/CloudPSS/newCapacitorRouter',
                    '_newFaultResistor_3p':'model/CloudPSS/_newFaultResistor_3p',
                    'SyncGeneratorRouter':'model/CloudPSS/SyncGeneratorRouter',
                    '_newBus_3p':'model/CloudPSS/_newBus_3p',
                    '_PSASP_AVR_11to12':'model/CloudPSS/_PSASP_AVR_11to12',
                    '_newTransformer_3p2w':'model/CloudPSS/_newTransformer_3p2w',
                    '_newStepGen':'model/CloudPSS/_newStepGen',
                    '_newConstant':'model/CloudPSS/_newConstant',
                    '_newGain':'model/CloudPSS/_newGain',
                    '_newDropGen':'model/CloudPSS/_newDropGen'}
        #comment: 创建组件定义库的反向映射（RID 到名称）。
        compDefLib_inv = {v: k for k, v in compDefLib.items()}
        #comment: 遍历项目中的所有组件键。
        for i in sproject.getAllComponents().keys():
            #comment: 将组件转换为 JSON 格式。
            comp = sproject.getAllComponents()[i].toJSON()
            #comment: 如果组件形状包含 'diagram-component'。
            if('diagram-component' in comp['shape']):
                #comment: 深拷贝组件 JSON。
                compcp = copy.deepcopy(comp);
                #comment: 移除 'style' 键（可能包含不需要导出的信息）。
                compcp['style'] = {}
                #comment: 如果组件定义 RID 不在反向映射中。
                if(comp['definition'] not in compDefLib_inv.keys()):
                    #comment: 使用正则表达式从定义 RID 中提取名称。
                    pattern = '[^/]*/[^/]*/([^/]*)$'
                    zone = re.search(pattern,comp['definition']);
                    #comment: 将组件添加到组件库，键为提取的名称。
                    compLib[zone.group(1)] = compcp;
                else:
                    #comment: 如果 RID 在反向映射中，则使用映射中的名称作为键。
                    compLib[compDefLib_inv[comp['definition']]] = compcp;
        #comment: 如果没有指定文件名，则默认为 'saSource.json'。
        if(name==None):
            name = 'saSource.json'
        #comment: 以写入模式打开文件，并指定 UTF-8 编码。
        with open(name, "w", encoding='utf-8') as f:
            #comment: 将组件库以格式化的 JSON 字符串写入文件。
            f.write(json.dumps(compLib, indent=4))
        #comment: 返回生成的组件库。
        return compLib

    def fetchCompData(self, rids=None):
        #comment: 定义 fetchCompData 方法，用于从 CloudPSS 获取组件的详细数据。
        #comment: 定义 GraphQL 查询的模板字符串。
        MODE_TEMPLATE = Template("""${model}:model(input:{ rid: "${rid}" }) {
                    rid,                    
                    name,                    
                    description,                    
                    tags,                   
                    revision {                         
                        parameters                        
                        pins                        
                        documentation                    
                    } 
                }""")
        #comment: 如果没有指定 rids，则抛出异常。
        if rids is None:
            raise Exception('rids must be specified')
        #comment: 初始化模型列表。
        models = []
        #comment: 初始化计数器。
        i = 0
        #comment: 遍历每个 RID。
        for rid in rids:
            #comment: 计数器递增。
            i += 1
            #comment: 使用模板生成 GraphQL 查询字符串，并添加到模型列表中。
            models.append(
                MODE_TEMPLATE.safe_substitute(model='model' + str(i), rid=rid))

        #comment: 构建完整的 GraphQL 查询。
        query = "query { %s }" % ' '.join(models)

        #comment: 发送 GraphQL 请求并获取数据。
        data = cloudpss.utils.graphql_request(query, {})

        #comment: 返回数据中的 'data' 部分。
        return data['data']


    def genParaDict(self, zdmToken,internalapiurl,projName):
        #comment: 定义 genParaDict 方法，用于生成参数字典和引脚字典。
        #comment: 初始化参数字典。
        ParaDict = {}
        #comment: 初始化引脚字典。
        PinDict = {}
        
        #comment: 设置 CloudPSS 的访问令牌。
        cloudpss.setToken(zdmToken)
        #comment: 设置 CloudPSS API 的 URL 环境变量。
        os.environ['CLOUDPSS_API_URL'] = internalapiurl
        #comment: 获取指定的 CloudPSS 模型项目。
        prjtmp = cloudpss.Model.fetch(projName)
        #comment: 获取项目中所有组件的字典。
        allcomp = prjtmp.getAllComponents();
        #comment: 初始化所有组件 RID 的列表。
        allcompList = []
        
        
        #comment: 遍历所有组件。
        for cmp in allcomp.keys():
            #comment: 将组件转换为 JSON 格式。
            cmpJSN = allcomp[cmp].toJSON()
            #comment: 将组件的定义 RID 添加到列表中。
            allcompList.append(cmpJSN['definition']);
        #comment: 调用 fetchCompData 方法获取所有组件的原始数据。
        RawDataList = self.fetchCompData(allcompList);
        #comment: 遍历原始数据列表中的每个原始数据条目。
        for rawData in RawDataList.values():
            
            #comment: 以组件 RID 为键，初始化参数字典中的对应条目。
            ParaDict[rawData['rid']] = {}
            #comment: 将组件的显示名称添加到参数字典中。
            ParaDict[rawData['rid']]['DiscriptName'] = rawData['name']
            #comment: 以组件 RID 为键，初始化引脚字典中的对应条目。
            PinDict[rawData['rid']] = {}
            
            #comment: 如果存在修订信息。
            if(rawData['revision'] != None):
                #comment: 如果存在参数信息。
                if(rawData['revision']['parameters'] != None):
                    #comment: 遍历参数列表。
                    for item0 in rawData['revision']['parameters']:
                        #comment: 遍历参数项。
                        for item1 in item0['items']:
                            #comment: 将参数项添加到参数字典中，键为参数的 'key'。
                            ParaDict[rawData['rid']][item1['key']] = item1;
                #comment: 如果存在引脚信息。
                if(rawData['revision']['pins'] != None):
                    #comment: 遍历引脚列表。
                    for item0 in rawData['revision']['pins']:
                        #comment: 将引脚项添加到引脚字典中，键为引脚的 'key'。
                        PinDict[rawData['rid']][item0['key']] = item0;
        #comment: 返回生成的参数字典和引脚字典。
        return ParaDict,PinDict