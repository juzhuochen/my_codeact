# comment: 导入 IPython 库，用于获取 IPython shell 实例，以便运行魔术命令。
from IPython import get_ipython

# comment: 导入 cloudpss 库，用于与 CloudPSS 平台进行交互。
import cloudpss
# comment: 导入 os 模块，用于与操作系统交互，例如设置环境变量。
import os
# comment: 导入 time 模块，用于处理时间相关的功能，例如暂停执行。
import time
# comment: 导入 json 模块，用于处理 JSON 格式的数据。
import json
# comment: 导入 re 模块，用于正则表达式操作。
import re
# comment: 导入 numpy 库，用于进行科学计算，特别是数组操作。
import numpy as np
# comment: 运行 IPython 魔术命令 '%matplotlib'，启用 Matplotlib 的交互式绘图模式。
get_ipython().run_line_magic('matplotlib', '')
# comment: 导入 matplotlib.pyplot 模块，用于创建静态、动态和交互式的可视化。
import matplotlib as mpl
# comment: 导入 matplotlib.pyplot 模块，用于创建绘图。
import matplotlib.pyplot as plt
# comment: 导入 plotly.graph_objects 模块，用于创建交互式图表。
import plotly.graph_objects as go
# comment: 导入 pandas 库，用于数据分析和处理，特别是表格数据。
import pandas as pd

# comment: 导入 tkinter 库，用于创建 GUI 应用程序。
import tkinter
# comment: 导入 tkinter.filedialog 模块，用于文件选择对话框。
import tkinter.filedialog

# comment: 导入 math 模块，用于数学运算。
import math

# comment: 从 IPython.display 导入 HTML 类，用于在 IPython 环境中显示 HTML 内容。
from IPython.display import HTML
# comment: 从 html 模块导入 unescape 函数，用于解码 HTML 实体。
from html import unescape

# comment: 导入 random 模块，用于生成随机数。
import random
# comment: 导入 json 模块，用于 JSON 数据处理。
import json
# comment: 导入 copy 模块，用于创建对象的浅拷贝和深拷贝。
import copy
# comment: 从 cloudpss.model.implements.component 导入 Component 类，表示 CloudPSS 中的组件。
from cloudpss.model.implements.component import Component
# comment: 从 cloudpss.runner.result 导入 Result, PowerFlowResult, EMTResult，用于处理仿真结果。
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
# comment: 从 cloudpss.model.revision 导入 ModelRevision 类，表示 CloudPSS 模型版本。
from cloudpss.model.revision import ModelRevision
# comment: 从 cloudpss.model.model 导入 Model 类，表示 CloudPSS 模型。
from cloudpss.model.model import Model

# comment: 从 scipy.optimize 导入 optimize 模块，用于优化算法。
from scipy import optimize

# comment: 从 string 模块导入 Template 类，用于字符串模板。
from string import Template

# comment: 定义一个名为 is_number 的函数，用于检查给定的字符串是否可以转换为数字。
def is_number(s):
    # comment: 尝试将字符串 s 转换为浮点数。
    try:
        float(s)
        # comment: 如果成功，返回 True。
        return True
    # comment: 捕获 ValueError 异常，表示转换失败。
    except ValueError:
        pass

    # comment: 尝试使用 unicodedata 模块将字符串 s 转换为数字字符的数值。
    try:
        import unicodedata
        unicodedata.numeric(s)
        # comment: 如果成功，返回 True。
        return True
    # comment: 捕获 TypeError 或 ValueError 异常。
    except (TypeError, ValueError):
        pass

    # comment: 所有尝试失败，返回 False。
    return False

# comment: 定义一个名为 CaseAnalysis 的类，用于案例分析。
class CaseAnalysis:
    # comment: 类的构造函数。
    def __init__(self):
        """
            comment: 模块初始化。包括cloudpss库初始化、几个字典的定义。
        """
        # comment: 初始化配置字典。
        self.config = {};
        # comment: 设置 CloudPSS 令牌的默认值。
        self.config['token']='123';
        # comment: 设置 CloudPSS API URL 的默认值。
        self.config['apiURL']='cloudpss.net';
        # comment: 设置模型的默认名称。
        self.config['model']='test';
        # comment: 设置用户名的默认值。
        self.config['username']='admin';
        
        # comment: 设置组件库文件名的默认值。
        self.config['comLibName'] = 'saSource.json';
        # comment: 初始化项目对象。
        self.project = 0;
        
        # comment: 初始化组件库字典。
        self.compLib = {};
        # comment: 初始化组件计数字典。
        self.compCount = {}
        # comment: 初始化位置字典。
        self.pos = {}
        
        # comment: 初始化组件标签字典。
        self.compLabelDict = {}
        # comment: 初始化通道引脚字典。
        self.channelPinDict = {}

        # comment: 调用初始化作业配置的函数。
        self.initJobConfig()
        
    # comment: 定义一个名为 initJobConfig 的函数，用于初始化作业配置。
    def initJobConfig(self):
        """
            comment: EMTP计算的参数：
                comment: 'task_queue'：清华32：taskManager_RT， 成都32：taskManager_turbol
                comment: 'solver_option': 正常：'0'， CPU_turbol：‘7’
                comment: 'n_cpu': '1'，‘2’，‘4’，‘8’，‘16’，'32'
                comment: output_channels:[['ss1', '200', '1000', '1', 'canvas_167_8,canvas_167_9']]
            
        """
        # comment: 定义 EMTP 初始作业配置。
        self.emtpJob_Init = {'args': {'begin_time': 0,
                'debug': 0,
                'end_time': 10,
                'initial_type': 0,
                'load_snapshot': 0,
                'load_snapshot_name': '',
                'max_initial_time': 1,
                'mergeBusNode': 0,
                'n_cpu': 16,
                'output_channels': [],
                'ramping_time': 0,
                'save_snapshot': 0,
                'save_snapshot_name': 'snapshot',
                'save_snapshot_time': 1,
                'solver': 0,
                'solver_option': 7,
                'step_time': 0.0001,
                'task_cmd': '',
                'task_queue': 'taskManager'},
            'name': 'CA电磁暂态仿真方案',
            'rid': 'job-definition/cloudpss/emtp'}

        # comment: 定义潮流计算初始作业配置。
        self.pfJob_Init = {'args': {'CheckInput': 1,
                'MaxIteration': 30,
                'ShowRunLog': 2,
                'SkipPF': 0,
                'UseBusAngleAsInit': 1,
                'UseBusVoltageAsInit': 1,
                'UseReactivePowerLimit': 1,
                'UseVoltageLimit': 1},
            'name': 'CA潮流计算方案',
            'rid': 'job-definition/cloudpss/power-flow'}

          
        # comment: 定义项目配置的初始设置。
        self.proj_Config_Init = {'args': {}, 'name': 'CA参数方案', 'pins': {}}
        
    # comment: 定义一个名为 createJob 的函数，用于创建新的作业（仿真方案）。
    def createJob(self, stype, name = None, args = None):
        """
            comment: stype为'emtp'或'powerFlow'
            comment: name为计算方案名称
            comment: args可以不填全，填需要更新的参数即可。
            
        """
        # comment: 初始化一个空的作业模板字典。
        jobtemp = {}
        # comment: 如果作业类型是 'emtp'，则复制 EMTP 初始作业配置。
        if(stype=='emtp'):
            jobtemp = copy.deepcopy(self.emtpJob_Init)
        # comment: 如果作业类型是 'powerFlow'，则复制潮流计算初始作业配置。
        elif(stype=='powerFlow'):
            jobtemp = copy.deepcopy(self.pfJob_Init)
        # comment: 如果提供了作业名称，则更新作业模板的名称。
        if(name!=None):
            jobtemp['name'] = name;
        # comment: 如果提供了参数，则更新作业模板的参数。
        if(args!=None):
            jobtemp['args'].update(args);
        # comment: 将创建的作业添加到项目中。
        self.project.addJob(jobtemp)
        
    # comment: 定义一个名为 createConfig 的函数，用于创建新的参数方案。
    def createConfig(self, name = None, args = None, pins = None):
        """
            comment: name为参数方案名称
            comment: args可以不填全，填需要更新的参数即可。
            
        """
        # comment: 复制项目配置的初始设置。
        configtemp = copy.deepcopy(self.proj_Config_Init)
        # comment: 如果提供了名称，则更新配置的名称。
        if(name!=None):
            configtemp['name'] = name;
        # comment: 如果提供了参数，则更新配置的参数。
        if(args!=None):
            configtemp['args'].update(args);
        # comment: 如果提供了引脚，则更新配置的引脚。
        if(pins!=None):
            configtemp['pins'].update(pins);
        # comment: 将创建的配置添加到项目中。
        self.project.addConfig(configtemp)
        
    # comment: 定义一个名为 addOutputs 的函数，用于向 EMTP 计算方案中增加输出通道。
    def addOutputs(self, jobName, channels):
        """
            comment: 往EMTP的计算方案中增加一行输出。channels的格式为：
            comment: [输出图像名称, 输出频率, 输出图像类型, 图像宽度, 输出通道key]
            comment: 例如：
            comment: ['outputFigName', '200', '1000', '1', 'canvas_167_8,canvas_167_9,canvas_167_111']
        """
        # comment: 获取指定名称的作业。
        job = self.project.getModelJob(jobName)
        # comment: 检查作业是否存在且是 EMTP 类型。
        if(job!=[] and job[0]['rid']==self.emtpJob_Init['rid']):
            # comment: 将输出通道添加到作业的参数中。
            job[0]['args']['output_channels'].append(channels)
        # comment: 返回新增输出通道的索引。
        return len(job[0]['args']['output_channels']) - 1;
    # comment: 定义一个名为 runProject 的函数，用于运行仿真项目。
    def runProject(self, jobName, configName,showLogs = False, apiUrl = None,websocketErrorTime = None):
        """
            comment: 运行仿真。会一直运行，直到仿真结束。
            comment: 结果保存在self.runner.result中
            comment: 返回值为runner的状态。
        """
#         comment: 尝试运行项目，处理可能的异常。
#         try:
        # comment: 获取指定名称的作业和配置。
        job = self.project.getModelJob(jobName)[0]
        config = self.project.getModelConfig(configName)[0]

        # comment: 打印开始仿真的消息。
        print("Starting Simulation...")
        # comment: 尝试启动运行器最多 5 次。
        for i in range(5):
            try:
                # comment: 如果提供了 API URL，则使用指定的 URL 运行项目。
                if(apiUrl!=None):
                    self.runner=self.project.run(job=job,config=config,apiUrl=apiUrl) # comment: 运行项目
                # comment: 否则，直接运行项目。
                else:
                    self.runner=self.project.run(job=job,config=config)
                # comment: 打印运行器已启动的消息。
                print("Runner started...")
                # comment: 启动成功后跳出循环。
                break
                
            # comment: 捕获启动运行器时可能发生的异常。
            except Exception as e:
                # comment: 打印启动失败并重试的消息。
                print("Start runner failed, restarting..." + str(e))
                # comment: 暂停 60 秒后重试。
                time.sleep(60)

        # comment: 如果是 EMTP 作业，获取结束时间。
        if(job['rid']==self.emtpJob_Init['rid']):
            endstime = float(job['args']['end_time'])
        # comment: 记录开始时间。
        time_start=time.time()
        # comment: 初始化结束时间。
        time_end=0;
        # comment: 打印仿真开始和当前运行器状态。
        print('Start simulation. Runner Status:'+str(self.runner.status()))
        # comment: 循环检查运行器状态，直到仿真结束或出错。
        while self.runner.status()<1:
            # comment: 更新当前时间。
            time_end = time.time();
            # comment: 如果 showLogs 为 True，则打印运行日志。
            if(showLogs):
                for log in self.runner.result.getLogs():
                    if('data' in log.keys() and 'content' in log['data'].keys()):
                        print(log['data']['content'])
            # comment: 如果是 EMTP 作业且有绘图通道数据，则显示仿真进度。
            if(job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)!=None):
                # comment: 获取第一个绘图通道的键。
                ckeytemp = self.runner.result.getPlotChannelNames(0)[0]
                # comment: 获取最后一个时间点。
                stime = self.runner.result.getPlotChannelData(0,ckeytemp)['x'][-1]

                # comment: 打印进度、耗时和运行器状态。
                print('Progress: Now: '+str(round(stime,2))+ ', All: '+str(endstime)+'. Time cost:',time_end-time_start,'. Runner Status:',self.runner.status())
                # comment: 如果当前时间已达到结束时间，则跳出循环。
                if(round(stime,2)==endstime):
                    break;
        #     comment: print(runner.result.getLogs())
            # comment: 否则，只打印耗时和运行器状态。
            else:
                print('Time cost:',time_end-time_start,'. Runner Status:',self.runner.status())
            # comment: 暂停 10 秒。
            time.sleep(10)
            # comment: 如果运行器状态为 -1（出错）。
            if self.runner.status()==-1:
                # comment: 打印仿真出错消息。
                print('仿真出错了，可能是websocket问题。')
                # comment: 如果设置了 websocketErrorTime 且是 EMTP 作业且有绘图通道数据。
                if(websocketErrorTime!=None and job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)!=None):
                    # comment: 如果当前时间远小于结束时间，则尝试重新运行。
                    if(stime < endstime - websocketErrorTime):
                        print('准备重新运行仿真。Current Time：'+str(round(stime,2)))
                        time.sleep(15)
                        # comment: 递归调用 runProject 重新运行仿真。
                        self.runProject(jobName, configName,showLogs, apiUrl, websocketErrorTime)
                        # comment: 返回运行器状态。
                        return self.runner.status()
                # comment: 如果设置了 websocketErrorTime 且是 EMTP 作业但没有绘图通道数据。
                elif(websocketErrorTime!=None and job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)==None):
                    # comment: 打印准备重新运行仿真的消息。
                    print('准备重新运行仿真。Current Time：None')
                    # comment: 重新运行仿真。
                    self.runProject(jobName, configName,showLogs, apiUrl, websocketErrorTime)
                # comment: 返回 -1 表示仿真出错。
                return -1
        
        # comment: 返回最终的运行器状态。
        return self.runner.status()
#         comment: except:
#         comment:     print('runProject 程序出错')
#         comment:     return -2
    # comment: 定义一个名为 getRunnerLogs 的函数，用于获取运行器的日志。
    def getRunnerLogs(self):
        """
            comment: 读取runner.result.getLogs()
        """
        # comment: 返回运行器结果的日志。
        return self.runner.result.getLogs()


    
    # comment: 定义一个名为 saveResult 的函数，用于保存仿真结果到文件。
    def saveResult(self, filePath = None, fileName = None):
        """
            comment: 存储结果数据文件。fileName=None时数据文件名为Temp.cjob.
            comment: ca.saveResult('results/','MyResult.cjob')
        """
        # comment: 如果文件名未指定，则默认为 'Temp.cjob'。
        if(fileName == None):
            fileName = 'Temp.cjob'
        # comment: 如果指定了文件路径，则将路径添加到文件名中。
        if(filePath!=None):
            fileName = filePath + fileName;
        # comment: 将运行器结果转储到指定文件。
        Result.dump(self.runner.result,fileName)


    # comment: 定义一个名为 plotResult 的函数，用于绘制 EMTP 仿真结果。
    def plotResult(self, result = None, k=None):
        """
            comment: 画图，仅限于EMTP。作出第k个坐标系的图。
            comment: 用法如下：
            comment: ca.plotResult(0)
            comment: ca.plotResult(ca.runner.result,0)
            comment: ca.plotResult(Result.load(file),0)
        """
        # comment: 如果结果未指定，则使用当前运行器的结果。
        if(result==None):
            result = self.runner.result;
        
        # comment: 创建一个 Plotly Figure 对象。
        fig = go.Figure()
        # comment: 如果 k 未指定，则默认为 0。
        if k == None:
            k=0
        # comment: 获取第 k 个坐标系的通道名称。
        ckeytemp = result.getPlotChannelNames(k)
        # comment: 遍历每个通道并添加散点图轨迹。
        for pk in ckeytemp:
            # comment: 获取通道的 x 轴数据。
            x = result.getPlotChannelData(k,pk)['x']
            # comment: 获取通道的 y 轴数据。
            y = result.getPlotChannelData(k,pk)['y']
            # comment: 向图中添加轨迹，模式为 'lines'，并设置名称。
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
        # comment: 显示图表。
        fig.show()
        
    # comment: 定义一个名为 displayPFResult 的函数，用于显示潮流计算结果。
    def displayPFResult(self, k = None):
        """
            comment: 输出表格，仅限于Power Flow。
            comment: runner.result.getBuses解析：
            comment: x=runner.result.getBuses()
            comment: x[0]['data']['title'] 
            comment: x[0]['data']['columns'][0~n]['name']
            comment: x[0]['data']['columns'][0~n]['data']
        """
        
        # comment: 如果 k 为 None 或 k 为 0，则显示母线结果。
        if(k == None or k==0):
            # comment: 创建一个空的 pandas DataFrame。
            data = pd.DataFrame()
            # comment: 获取母线数据。
            x=self.runner.result.getBuses()
            # comment: 遍历母线数据的列，并添加到 DataFrame 中。
            for y in x[0]['data']['columns']:
                data[y['name']] = y['data']
            # comment: 将 DataFrame 转换为 HTML 字符串。
            s = data.to_html();
            # comment: 解码 HTML 实体。
            s = unescape(s)
            # comment: 将 HTML 字符串转换为 IPython HTML 对象并显示。
            s = HTML(s)
            display(s)
        # comment: 如果 k 为 None 或 k 为 1，则显示支路结果。
        if(k==None or k==1):
            # comment: 创建一个空的 pandas DataFrame。
            data = pd.DataFrame()
            # comment: 获取支路数据。
            x=self.runner.result.getBranches()
            # comment: 遍历支路数据的列，并添加到 DataFrame 中。
            for y in x[0]['data']['columns']:
                data[y['name']] = y['data']
            # comment: 将 DataFrame 转换为 HTML 字符串。
            s = data.to_html();
            # comment: 解码 HTML 实体。
            s = unescape(s)
            # comment: 将 HTML 字符串转换为 IPython HTML 对象并显示。
            s = HTML(s)
            display(s)
    
    # comment: 定义一个名为 initCanvasPos 的函数，用于初始化画布的坐标位置。
    def initCanvasPos(self, canvas):
        """
            comment: 初始化某图层的坐标。
        """
        # comment: 为指定画布创建一个新的位置字典。
        self.pos[canvas] = {}
        # comment: 设置 x 方向的增量。
        self.pos[canvas]['dx'] = 20;
        # comment: 设置 y 方向的增量。
        self.pos[canvas]['dy'] = 20;
        # comment: 设置起始 x 坐标。
        self.pos[canvas]['x0'] = 20;
        # comment: 设置起始 y 坐标。
        self.pos[canvas]['y0'] = 20;
        # comment: 初始化当前 x 坐标。
        self.pos[canvas]['x'] = self.pos[canvas]['x0'];
        # comment: 初始化当前 y 坐标。
        self.pos[canvas]['y'] = self.pos[canvas]['y0'];
        
        # comment: 初始化最大 y 方向增量。
        self.pos[canvas]['maxdy'] = 0;
        
    
    # comment: 定义一个名为 getRevision 的函数，用于获取当前项目的修订版本。
    def getRevision(self, file = None):
        """
            comment: return：当前的project.revision.toJSON()
        """
        # comment: 深度复制当前项目的修订版本为 JSON 格式。
        r1 = copy.deepcopy(self.project.revision.toJSON());
        # comment: 如果指定了文件路径，则将修订版本写入文件。
        if file!=None:
            with open(file, "w", encoding='utf-8') as f:
                f.write(json.dumps(r1, indent=4))
        # comment: 返回修订版本。
        return r1
    
    # comment: 定义一个名为 loadRevision 的函数，用于加载项目的修订版本。
    def loadRevision(self, revision = None, file = None):
        """
            comment: loadRevision(self, revision = None, file = None)
            comment: revision:某revision的json格式。
            comment: file:读取文件名。
            comment: 两个参数选其一即可
        """
        # comment: 如果提供了修订版本（JSON 格式），则加载它。
        if(revision!=None):
            self.project.revision = ModelRevision(revision);
        # comment: 如果提供了文件路径，则从文件加载修订版本。
        else:
            with open(file, "r", encoding='utf-8') as f:
                # comment: 从文件中加载 JSON 数据。
                f = json.load(f) # 修正：这里应该是 f = json.load(f) 而不是 f = json.load(file)
                # comment: 使用加载的数据创建 ModelRevision 对象并赋值给 project.revision。
                self.project.revision = ModelRevision(f); # 修正：这里应该是 f 而不是 revision

    
    # comment: 定义一个名为 setConfig 的函数，用于配置 CloudPSS 模块。
    def setConfig(self,token = None, apiURL = None, username = None, model = None, comLibName = None):
        """
            comment: 配置模块。
            comment: token从cloudpss平台中申请。
            comment: apiURL为域名。
            comment: username为用户名。
            comment: project为算例名称（不带/model/username）
            comment: comLibName默认为'saSource.json'。
        """
        
        # comment: 如果提供了 token，则更新配置中的 token。
        if(token != None):
            self.config['token']=token;
        # comment: 如果提供了 apiURL，则更新配置中的 apiURL。
        if(apiURL != None):
            self.config['apiURL']=apiURL;
        # comment: 如果提供了 username，则更新配置中的 username。
        if(username!=None):
            self.config['username']=username;
        # comment: 如果提供了 model，则更新配置中的 model。
        if(model!=None):
            self.config['model']=model;
        # comment: 如果提供了 comLibName，则更新配置中的 comLibName。
        if(comLibName!=None):
            self.config['comLibName']=comLibName;    
#         comment: self.setInitialConditions(); # 这行被注释掉了，表示不在此处自动调用。
    
    # comment: 定义一个名为 setInitialConditions 的函数，用于模块初始化。
    def setInitialConditions(self):
        """
            comment: 模块初始化。需要在完成setConfig后手动调用。
        """
        # comment: 设置 CloudPSS 的访问令牌。
        cloudpss.setToken(self.config['token'])
        # comment: 设置 CloudPSS API 的 URL 环境变量。
        os.environ['CLOUDPSS_API_URL'] = self.config['apiURL']
        # comment: 从 CloudPSS 平台获取指定的模型项目。
        self.project = cloudpss.Model.fetch('model/'+self.config['username']+'/'+self.config['model'])
        # comment: 打开组件库文件并加载 JSON 数据。
        with open(self.config['comLibName'], "r", encoding='utf-8') as f:
            self.compLib = json.load(f)
        # comment: 初始化组件计数字典，所有组件类型计数归零。
        self.compCount = {key:0 for key in self.compLib.keys()}
        # comment: 调用设置组件标签字典的函数。
        self.setCompLabelDict()
        # comment: 调用设置通道引脚字典的函数。
        self.setChannelPinDict()
    
    # comment: 定义一个名为 setCompLabelDict 的函数，用于从元件 label 生成指向元件的字典。
    def setCompLabelDict(self):
        """
            comment: 从元件label指向元件的字典生成
            comment: self.compLabelDict[label]={key1:Comp1,key2:Comp2}
        """
        # comment: 初始化组件标签字典。
        self.compLabelDict = {}
        # comment: 遍历项目中所有组件的键。
        for key in self.project.getAllComponents().keys():
            # comment: 获取当前组件对象。
            comptemp = self.project.getComponentByKey(key)
            # comment: 如果组件的形状是 'diagram-component'。
            if(comptemp.shape=='diagram-component'):
                # comment: 获取组件的标签。
                label = comptemp.label;
                # comment: 如果标签不在字典中，则创建一个新的子字典。
                if(label not in self.compLabelDict.keys()):
                    self.compLabelDict[label] = {}
                # comment: 将组件添加到对应标签的字典中。
                self.compLabelDict[label][key] = comptemp;
            
    # comment: 定义一个名为 setChannelPinDict 的函数，用于从输出通道的 pin 生成指向通道元件的 key 的字典。
    def setChannelPinDict(self):
        """
            comment: 从输出通道的pin指向通道元件的key的字典生成
            comment: self.channelPinDict[pin] = key;    
        """
        # comment: 初始化通道引脚字典。
        self.channelPinDict = {}
        # comment: 遍历所有 '_newChannel' 类型组件的键。
        for key in self.project.getComponentsByRid('model/CloudPSS/_newChannel').keys():
            # comment: 获取当前组件对象。
            comptemp = self.project.getComponentByKey(key)
            # comment: 获取组件的 '0' 号引脚。
            pin0 = comptemp.pins['0'];
            # comment: 将引脚和对应的组件键添加到字典中。
            self.channelPinDict[pin0] = key;    
    
    # comment: 定义一个名为 addComp 的函数，用于向项目中添加元件。
    def addComp(self,compJson,id1 = None,canvas = None, position = None, args = None, pins = None, label = None):
        """
            comment: 增添元件。
            comment: compJson为元件的Json
            comment: id1为元件的key。
            comment: canvas为元件所处图层。
            comment: position为增添的位置，如{'x':12,'y':49}
            comment: args为元件需要更新的参数。
            comment: pins为元件需要更新的引脚。
            comment: label为新增元件的label。
        """
        
        # comment: 深度复制元件的 JSON 数据。
        compJson1 = copy.deepcopy(compJson)
        
        # comment: 如果提供了 id1，则更新元件的 ID。
        if id1!=None:
            compJson1['id'] = id1;
        # comment: 如果提供了位置，则更新元件的位置。
        if position!=None:
            compJson1['position'] = position;
        # comment: 如果提供了画布，则更新元件所属的画布。
        if canvas!=None:
            compJson1['canvas'] = canvas;
        # comment: 如果提供了参数，则更新元件的参数。
        if args!=None:
            compJson1['args'].update(args)
        # comment: 如果提供了引脚，则更新元件的引脚。
        if pins!=None:
            compJson1['pins'].update(pins)
        # comment: 如果提供了标签，则更新元件的标签。
        if label!=None:
            compJson1['label'] = label
#         comment: print(compJson1)
        # comment: 使用修改后的 JSON 数据创建 Component 对象。
        comp = Component(compJson1)
#         comment: print(comp)
        # comment: 将新创建的组件添加到项目的修订版本中。
        self.project.revision.implements.diagram.cells[compJson1['id']]=comp
    
    # comment: 定义一个名为 addxPos 的函数，用于更新当前画布的 x 坐标。
    def addxPos(self, canvas, compJson, MaxX = None):
        """
            comment: 更新x轴坐标
            comment: MaxX为最大横坐标。x坐标超过MaxX时则换行。
        """
        
        # comment: 将当前 x 坐标增加元件的宽度。
        self.pos[canvas]['x'] = self.pos[canvas]['x'] + compJson['size']['width'];
        # comment: 更新最大 y 方向增量，取当前和元件高度的最大值。
        self.pos[canvas]['maxdy'] = max(self.pos[canvas]['maxdy'],compJson['size']['height'])
        # comment: 如果设置了 MaxX 且当前 x 坐标超过 MaxX，则换行。
        if(MaxX != None and MaxX < self.pos[canvas]['x']):
            self.newLinePos(canvas)
        
    # comment: 定义一个名为 newLinePos 的函数，用于在画布中换行。
    def newLinePos(self, canvas):
        """
            comment: 在图层中换行
        """
        # comment: 将 x 坐标重置为起始 x 坐标。
        self.pos[canvas]['x'] = self.pos[canvas]['x0']
        # comment: 将 y 坐标向下移动一个行高。
        self.pos[canvas]['y'] = self.pos[canvas]['y'] + self.pos[canvas]['dy'] + self.pos[canvas]['maxdy']
        # comment: 重置最大 y 方向增量。
        self.pos[canvas]['maxdy'] = 0;
        
    # comment: 定义一个名为 addCompInCanvas 的函数，用于在指定的画布中添加元件。
    def addCompInCanvas(self,compJson,key,canvas, addN = None, args = None, pins = None, label = None,dX = 10, MaxX = None):
        """
            comment: 在图纸中新增元件，包括添加元件、为元件key及标签增添后缀_n，更新坐标位置的功能。
            comment: addN默认为True，代表将会自动添加后缀。
            comment: MaxX为换行相关参数，为图纸中的一行元件最宽距离。一般可取500
            
        """
        # comment: 如果 addN 未指定，默认设置为 True。
        if(addN == None):
            addN = True
        
        # comment: 复制当前画布的 x 和 y 坐标。
        posTemp = {k: v for k, v in self.pos[canvas].items() if k in ['x','y']}
        
        
        # comment: 如果键不在组件计数字典中，则初始化为 0。
        if(key not in self.compCount.keys()):
            self.compCount[key] = 0;
        # comment: 如果 addN 为 True，则增加组件计数并生成带后缀的 ID。
        if(addN):
            self.compCount[key]+=1;
            id1Temp = key+'_'+str(self.compCount[key]);
        # comment: 否则，直接使用键作为 ID。
        else:
            id1Temp = key;
        # comment: 如果标签未指定，则默认为生成的 ID。
        if (label==None):
            label = id1Temp;
        # comment: 如果 addN 为 True，则为标签添加后缀。
        if(addN):
            label = label + '_'+str(self.compCount[key]);
            
        # comment: 复制参数字典。
        argsCopy = args.copy()
        # comment: 如果参数中包含 'Name' 且 addN 为 True，则为 Name 添加后缀。
        if('Name' in argsCopy.keys() and addN):
            argsCopy['Name'] = argsCopy['Name'] + '_' + str(self.compCount[key]);
        
        # comment: 调用 addComp 方法添加元件到项目中。
        self.addComp(compJson,id1Temp,canvas, posTemp, argsCopy, pins, label)
        # comment: 更新 x 坐标。
        self.addxPos(canvas, compJson, MaxX)
        # comment: 在元件的 x 坐标后额外增加 dX。
        self.pos[canvas]['x'] = self.pos[canvas]['x'] + dX;

#         comment: print([id1Temp,canvas, posTemp, argsCopy, pins, label])
        
        # comment: 返回生成的元件 ID 和标签。
        return id1Temp, label
    
    # comment: 定义一个名为 createCanvas 的函数，用于新增图纸（画布）。
    def createCanvas(self,canvas,name):
        """
            comment: 新增图纸。
        """
        # comment: 将新的画布信息添加到项目的修订版本中。
        self.project.revision.implements.diagram.canvas.append({'key': canvas, 'name': name})
        # comment: 初始化新画布的坐标位置。
        self.initCanvasPos(canvas)
    
    # comment: 定义一个名为 screenCompByArg 的函数，用于通过参数筛选元件。
    def screenCompByArg(self, compRID, conditions, compList = None):
        """
            comment: 通过参数来筛选元件。
            comment: compRID如'model/CloudPSS/_newShuntLC_3p'
            comment: conditions:[{'arg':'Vrms', 'Min': 20, 'Max':500, 'Set':None},{'arg':'Name', 'Min': None, 'Max':None, 'Set':['藏123','川321']}]
            comment: compList:['compKey1','compKey2'...]不为空时仅从compList中挑选
        """
        
        # comment: 从项目中获取指定 RID 的所有组件。
        comps = self.project.getComponentsByRid(compRID)
        # comment: 初始化筛选后的组件字典。
        screenedComps = {}
        # comment: 如果 conditions 不是列表，则将其转换为包含单个字典的列表。
        if not isinstance(conditions,list):
            conditions = [conditions]
        
        # comment: 如果提供了 compList，则只从 compList 中筛选组件。
        if(compList!=None):
            # comment: 计算 comps.keys() 和 compList 的交集，得到要筛选的键。
            screenedKeys = set(comps.keys()) & set(compList);
            # comment: 基于交集创建新的 comps 字典。
            comps = dict([(key, comps.get(key, None)) for key in screenedKeys])
            
        # comment: 遍历筛选后的组件中的每个组件。
        for k in comps.keys():
            # comment: 初始化标志为 True。
            flag = True;
            # comment: 遍历每个筛选条件。
            for c in conditions:
                # comment: 获取组件对应参数的值。
                a = comps[k].args[c['arg']]
                # comment: 每次检查前将标志重置为 True。
                flag = True;
                # comment: 获取条件的最小值、最大值和集合。
                Min = c['Min']
                Max = c['Max']
                Set = c['Set']
                # comment: 如果参数 'a' 是数字，且 Min 和 Max 也是数字或 None。
                if is_number(a) and ( Min == None or is_number(Min)) and (Max == None or is_number(Max)):
                    # comment: 如果 Min 不为空且 'a' 小于 Min，则设置标志为 False 并跳出循环。
                    if(Min!=None and float(Min) > float(a)):
                        flag = False;
                        break
                    # comment: 如果 Max 不为空且 'a' 大于 Max，则设置标志为 False 并跳出循环。
                    if(Max!=None and float(Max) < float(a)):
                        flag = False;  
                        break
                    # comment: 如果 Set 不为空且 'a' 不在 Set 中，则设置标志为 False 并跳出循环。
                    if(Set!=None and (a not in Set)):
                        flag = False;
                        break
                # comment: 如果参数 'a' 不是数字，或者 Min/Max 不是数字。
                else:
                    # comment: 如果 Min 不为空且 'a' 小于 Min，则设置标志为 False 并跳出循环。
                    if(Min!=None and Min > a):
                        flag = False;
                        break
                    # comment: 如果 Max 不为空且 'a' 大于 Max，则设置标志为 False 并跳出循环。
                    if(Max!=None and Max < a):
                        flag = False;  
                        break
                    # comment: 如果 Set 不为空且 'a' 不在 Set 中，则设置标志为 False 并跳出循环。
                    if(Set!=None and (a not in Set)):
                        flag = False;
                        break

            # comment: 如果所有条件都满足，则将组件添加到 screenedComps 字典中。
            if(flag):
                screenedComps[k] = comps[k];
        # comment: 返回筛选后的组件。
        return screenedComps
                
    
    # comment: 定义一个名为 saveProject 的函数，用于保存算例（项目）。
    def saveProject(self, newID, name = None, desc = None):
        """
            comment: 保存算例。一种使用的例子：
            comment: desc = '此为自动暂稳分析程序生成的仿真算例。\n' + ca.model.description 
            comment: ca.saveProject(projectKey+'Auto_SA',sa.model.name+'_自动暂稳分析',desc = desc + sa.model.description )
        """
        # comment: 如果提供了名称，则更新项目的名称。
        if(name!=None):
            self.project.name = name;
        # comment: 如果提供了描述，则更新项目的描述。
        if(desc!=None):
            self.project.description = desc;
        # comment: 保存项目并返回结果。
        return self.project.save(newID)
        # comment: return 'model/'+self.config['username']+'/'+newID


# comment: 定义一个名为 StabilityAnalysis 的类，继承自 CaseAnalysis。
class StabilityAnalysis(CaseAnalysis):
    # comment: 类的构造函数。
    def __init__(self):
        # comment: 调用父类 CaseAnalysis 的构造函数。
        super(StabilityAnalysis,self).__init__()
        # comment: 定义故障相关的画布 ID。
        self.cFid = 'canvas_AutoSA_Fault'
        # comment: 定义额外输出相关的画布 ID。
        self.cOid = 'canvas_AutoSA_ExtraOutput'
        # comment: 定义常用组件的名称映射。
        self.compNames = {'_newFaultResistor_3p':'SA_接地故障',                          '_newBreaker_3p':'SA_三相断路器',                          'GND':'接地点(用于稳定分析)',                          '_newStepGen':'阶跃信号'}
        

        
    # comment: 定义一个名为 createSACanvas 的函数，用于创建稳定性分析相关的画布。
    def createSACanvas(self):
        # comment: 创建故障相关的画布。
        self.createCanvas(self.cFid,'故障相关设置')
        # comment: 创建额外输出相关的画布。
        self.createCanvas(self.cOid,'暂态分析所需输出通道')
        
        # comment: 获取接地点组件的名称。
        nameTemp = self.compNames['GND']
        # comment: 在故障画布中添加接地点组件。
        self.addCompInCanvas(self.compLib['GND'], key = 'AutoSA_GND',canvas = self.cFid,                     args = {'Name':nameTemp}, pins = {'0':'GND'},label = nameTemp)
        # comment: 在故障画布中换行。
        self.newLinePos(self.cFid)
    
    # comment: 定义一个名为 setGroundFault 的函数，用于设置接地故障。
    def setGroundFault(self, pinName, fault_start_time, fault_end_time,  fault_type, OtherParas = None):
        # comment: 获取接地故障组件的名称。
        nameTemp = self.compNames['_newFaultResistor_3p']
        # comment: 初始化接地故障的参数字典。
        argsTemp = {'Name':nameTemp, 'fs':str(fault_start_time), 'fe':str(fault_end_time),'ft':str(fault_type)}
        # comment: 如果提供了其他参数，则更新参数字典。
        if(OtherParas != None):
            argsTemp.update(OtherParas)
        # comment: 在故障画布中添加接地故障组件。
        id1, label = self.addCompInCanvas(self.compLib['_newFaultResistor_3p'], key = 'SA_Ground_Fault',canvas = self.cFid, args = argsTemp, pins = {'0':pinName,'1':'GND'},label = nameTemp)
        # comment: 返回新添加组件的 ID 和标签。
        return id1, label
        
    # comment: 定义一个名为 setBreaker_3p 的函数，用于设置三相断路器。
    def setBreaker_3p(self, busName1, busName2, ctrlSigName = None, OtherParas = None):
        # comment: 获取三相断路器组件的名称。
        nameTemp = self.compNames['_newBreaker_3p']
        # comment: 初始化断路器参数字典。
        argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '1'}
        # comment: 如果提供了其他参数，则更新参数字典。
        if(OtherParas != None):
            argsTemp.update(OtherParas)
        # comment: 在故障画布中添加三相断路器组件。
        id1, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = 'SA_Breaker_3p',canvas = self.cFid, args = argsTemp, pins = {'0':busName1,'1': busName2},label = nameTemp)
         
        # comment: 返回新添加组件的 ID 和标签。
        return id1, label

    # comment: 定义一个名为 setN_1 的函数，用于设置 N-1 故障（切除一条线路）。
    def setN_1(self, transKey, cut_time, OtherBreakerParas = None):
        # comment: 获取传输线（或变压器）组件。
        transComp = self.project.getComponentByKey(transKey)
        # comment: 复制传输线组件的引脚。
        transPin = transComp.pins.copy()
        # comment: 获取传输线组件的名称。
        transName = transComp.args['Name']
        # comment: 修改传输线组件的引脚，连接到断路器。
        transComp.pins['0'] = 'BreakerPin_'+ transName + '_0';
        transComp.pins['1'] = 'BreakerPin_'+ transName + '_1';
        # comment: 定义断路器控制信号名称。
        SigName = '@Sig_Breaker_'+transName;
        
        # comment: 在传输线引脚 0 和新的断路器引脚之间设置断路器。
        id1, label1 = self.setBreaker_3p(transComp.pins['0'], transPin['0'], ctrlSigName = SigName, OtherBreakerParas = OtherBreakerParas)
        # comment: 在传输线引脚 1 和新的断路器引脚之间设置断路器。
        id2, label2 = self.setBreaker_3p(transComp.pins['1'], transPin['1'], ctrlSigName = SigName, OtherBreakerParas = OtherBreakerParas)
        
        # comment: 获取阶跃信号发生器组件的名称。
        nameTemp = self.compNames['_newStepGen']
        # comment: 初始化阶跃信号发生器参数，用于控制断路器的切除时间。
        argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time)}
        # comment: 在故障画布中添加阶跃信号发生器。
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig',canvas = self.cFid, args = argsTemp, pins = {'0':SigName},label = nameTemp)
        # comment: 在故障画布中换行。
        self.newLinePos(self.cFid)

    # comment: 定义一个名为 setCutFault 的函数，用于设置切除故障（切除一个元件）。
    def setCutFault(self, compKey, cut_time, OtherBreakerParas = None):
        # comment: 获取要切除的组件。
        compComp = self.project.getComponentByKey(compKey)
        # comment: 复制组件的引脚。
        compPin = compComp.pins.copy()
        # comment: 获取组件的名称。
        compName = compComp.args['Name']
        # comment: 修改组件的引脚，连接到断路器。
        compComp.pins['0'] = 'BreakerPin_'+ compName + '_0';
        # comment: 定义切除控制信号名称。
        SigName = '@Sig_Cutoff_'+compName;
        # comment: 在组件引脚和新的断路器引脚之间设置断路器。
        id1, label1 = self.setBreaker_3p(compComp.pins['0'], compPin['0'], ctrlSigName = SigName, OtherBreakerParas = OtherBreakerParas)
        
        # comment: 获取阶跃信号发生器组件的名称。
        nameTemp = self.compNames['_newStepGen']
        # comment: 初始化阶跃信号发生器参数，用于控制断路器的切除时间。
        argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time)}
        # comment: 在故障画布中添加阶跃信号发生器。
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig',canvas = self.cFid, args = argsTemp, pins = {'0':SigName},label = nameTemp)
        # comment: 在故障画布中换行。
        self.newLinePos(self.cFid)
        
    # comment: 定义一个名为 setN_1_GroundFault 的函数，用于设置 N-1 接地故障。
    def setN_1_GroundFault(self, transKey,side, fault_start_time, cut_time, fault_type, OtherFaultParas = None, OtherBreakerParas = None):    
        # comment: 设置 N-1 故障（切除传输线）。
        self.setN_1(transKey, cut_time, OtherBreakerParas)
        # comment: 获取传输线组件。
        transComp = self.project.getComponentByKey(transKey)
        # comment: 在传输线的一侧设置接地故障。
        self.setGroundFault(transComp.pins[str(side)], fault_start_time, 99999,  fault_type, OtherParas = OtherFaultParas)
    
    # comment: 定义一个名为 setN_2_GroundFault 的函数，用于设置 N-2 接地故障。
    def setN_2_GroundFault(self, transKey1, transKey2, side, fault_start_time, cut_time, fault_type, OtherFaultParas = None, OtherBreakerParas = None):    
        # comment: 设置第一个传输线的 N-1 故障。
        self.setN_1(transKey1, cut_time, OtherBreakerParas)
        # comment: 设置第二个传输线的 N-1 故障。
        self.setN_1(transKey2, cut_time, OtherBreakerParas)
        
        # comment: 获取第一个传输线组件。
        transComp = self.project.getComponentByKey(transKey1)
        # comment: 在第一个传输线的一侧设置接地故障。
        self.setGroundFault(transComp.pins[str(side)], fault_start_time, 99999,  fault_type, OtherParas = OtherFaultParas)

    # comment: 定义一个名为 setN_k_GroundFault 的函数，用于设置 N-k 接地故障。
    def setN_k_GroundFault(self, transKeys, side, fault_start_time, cut_time, fault_type, OtherFaultParas = None, OtherBreakerParas = None):    
        # comment: 遍历所有传输线，并为每条传输线设置 N-1 故障。
        for i in range(len(transKeys)):
            self.setN_1(transKeys[i], cut_time, OtherBreakerParas)
        # comment: 获取列表中的第一条传输线组件。
        transComp = self.project.getComponentByKey(transKeys[0])
        # comment: 在第一条传输线的一侧设置接地故障。
        self.setGroundFault(transComp.pins[str(side)], fault_start_time, 99999,  fault_type, OtherParas = OtherFaultParas)
        
    
    # comment: 定义一个名为 addChannel 的函数，用于添加输出通道。
    def addChannel(self, pinName, dim, channelName = None):
        # comment: 如果引脚名称不在通道引脚字典中（即该通道尚未添加）。
        if pinName not in self.channelPinDict.keys():
            
            # comment: 如果通道名称未指定，则默认为引脚名称。
            if(channelName == None):
                channelName = pinName;
            # comment: 定义通道 ID。
            channelID = 'SA_outputChannel';

            # comment: 初始化通道参数。
            argsTemp = {'Name':channelName, 'Dim':dim}
            # comment: 在额外输出画布中添加新的通道组件。
            id1, label = self.addCompInCanvas(self.compLib['_newChannel'], key = channelID, canvas = self.cOid, args = argsTemp, pins = {'0':pinName},label = channelName, MaxX = 500)
            # comment: 将引脚名称和新添加的通道 ID 映射到通道引脚字典中。
            self.channelPinDict[pinName] = id1;
            
        # comment: 如果引脚名称已在通道引脚字典中（即通道已存在）。
        else:
            # comment: 获取已存在的通道组件。
            channelComp = self.project.getComponentByKey(self.channelPinDict[pinName])
            # comment: 如果提供了新的通道名称，则更新组件的名称和标签。
            if(channelName != None):
                channelComp.args['Name'] = channelName;
                channelComp.label = channelName;
            # comment: 获取组件的 ID 和标签。
            id1 = channelComp.id;
            label = channelComp.label
        
        # comment: 返回通道的 ID 和标签。
        return id1, label
    
    # comment: 定义一个名为 addVoltageMeasures 的函数，用于添加电压量测输出。
    def addVoltageMeasures(self,jobName, VMin = None, VMax = None, NameSet = None, Keys = None, freq = None, PlotName = None):
        # comment: 初始化电压条件的字典。
        VCondition = {'arg':'VBase','Min':None,'Max':None,'Set':None}
        # comment: 初始化绘图名称。
        plotName = 'Voltage:'
        # comment: 如果提供了 VMin，则设置电压条件的 Min 值，并更新绘图名称。
        if VMin!=None:
            VCondition['Min'] = VMin;
            plotName = plotName+str(VMin)+'-'
        # comment: 否则，绘图名称后缀为 '0-'。
        else:
            plotName = plotName+'0-'
        # comment: 如果提供了 VMax，则设置电压条件的 Max 值，并更新绘图名称。
        if VMax!=None:
            VCondition['Max'] = VMax;
            plotName = plotName+str(VMax)
        # comment: 否则，绘图名称后缀为 'Inf'。
        else:
            plotName = plotName+'Inf'
        
        # comment: 如果提供了 PlotName，则使用该名称作为最终绘图名称。
        if(PlotName!= None):
            plotName = PlotName;
            
            
        # comment: 初始化名称条件的字典。
        NCondition = {'arg':'Name','Min':None,'Max':None,'Set':None}
        # comment: 如果提供了 NameSet，则设置名称条件的 Set 值。
        if NameSet!=None:
            NCondition['Set'] = NameSet;
        # comment: 根据电压和名称条件筛选母线组件。
        screenedBus = self.screenCompByArg('model/CloudPSS/_newBus_3p', [VCondition,NCondition], compList = Keys);
        
        # comment: 初始化输出通道列表。
        outputChannels = []
        # comment: 遍历筛选后的母线。
        for k in screenedBus.keys():
            # comment: 获取母线的 Vrms 参数。
            p = screenedBus[k].args['Vrms'];
            # comment: 如果 Vrms 参数为空，则构建其默认表达式并更新。
            if(p==''):
                p = '#'+screenedBus[k].label+'.Vrms'
                screenedBus[k].args['Vrms'] = p;
            
            # comment: 添加通道，并将其 ID 添加到输出通道列表中。
            id1, label = self.addChannel(p,1)
            outputChannels.append(id1)
            
        # comment: 如果频率未指定，则默认为 200。
        if(freq ==None):
            freq = 200;
        # comment: 将输出通道配置添加到作业中。
        self.addOutputs(jobName, {'0':plotName, '1':freq, '2':'compressed', '3':1, '4':outputChannels})    
        
        # comment: 返回筛选后的母线。
        return screenedBus

    # comment: 定义一个名为 addComponentOutputMeasures 的函数，用于通过参数筛选并添加元件输出测量。
    def addComponentOutputMeasures(self, jobName, compRID, measuredKey, conditions, compList = None, dim = 1, curveName = None, plotName = None, freq = 200):
        """
            comment: 通过参数来筛选新增元件输出。
            comment: compRID如'model/CloudPSS/_newShuntLC_3p'
            comment: measuredKey: 要输出的参数键名
            comment: conditions:[{'arg':'Vrms', 'Min': 20, 'Max':500, 'Set':None},{'arg':'Name', 'Min': None, 'Max':None, 'Set':['藏123','川321']}]
            comment: compList:['compKey1','compKey2'...]不为空时仅从compList中挑选
            comment: freq:量测信号的输出频率

        """
        # comment: 根据提供的条件筛选组件。
        screenedComps = self.screenCompByArg(compRID, conditions, compList = compList);
        # comment: 初始化输出通道列表。
        outputChannels = []
        # comment: 如果 curveName 未指定，则默认为 measuredKey。
        if(curveName == None):
            curveName = measuredKey;
        # comment: 遍历筛选后的组件。
        for k in screenedComps.keys():
            # comment: 获取组件中 measuredKey 对应的参数值。
            p = screenedComps[k].args[measuredKey];
            # comment: 如果参数值为空，则构建其默认表达式并更新。
            if(p==''):
                p = '#'+screenedComps[k].label+'.' + curveName;
                screenedComps[k].args[measuredKey] = p;
            
            # comment: 添加通道并将其 ID 添加到输出通道列表中。
            id1, label = self.addChannel(p,dim)
            outputChannels.append(id1)
            
        # comment: 如果频率未指定，则默认为 200。
        if(freq ==None):
            freq = 200;
        # comment: 将输出通道配置添加到作业中。
        self.addOutputs(jobName, {'0':plotName, '1':freq, '2':'compressed', '3':1, '4':outputChannels})    

        # comment: 返回筛选后的组件。
        return screenedComps


#         comment: self.setGroundFault()


# # comment: 调相机选址定容相关分析模块S_S_SyncComp
# # 
# # comment: 本模块基于StabilityAnalysis模块构建。实现电网稳定问题的高级分析。实现了新增调相机、计算电压敏感度VSI、计算故障严重程度SI等功能。


# comment: 定义一个名为 S_S_SyncComp 的类，继承自 StabilityAnalysis。
class S_S_SyncComp(StabilityAnalysis):
    # comment: 类的构造函数。
    def __init__(self):
        # comment: 调用父类 StabilityAnalysis 的构造函数。
        super(S_S_SyncComp,self).__init__()
        # comment: 更新组件名称映射，添加与同步补偿器相关的组件。
        self.compNames.update({'SyncGeneratorRouter':'SA_同步发电机',                          '_newBus_3p':'SA_三相母线',                              '_PSASP_AVR_11to12':'SA_调压器11-12型',                              '_newTransformer_3p2w':'SA_双绕组变压器',                              '_newShuntLC_3p':'SA_注入动态无功',
                              '_newGain':'SA_Gain'})
        # comment: 定义同步补偿器相关画布的 ID。
        self.cSyncCid = 'canvas_AutoSA_Sync_Compensators'
        # comment: 定义动态无功相关画布的 ID。
        self.cDynQid = 'canvas_AutoSA_Dynamic_Q'
        
        
    # comment: 定义一个名为 createSSSCACanvas 的函数，用于创建同步补偿器相关的画布。
    def createSSSCACanvas(self):
        # comment: 创建同步补偿器画布。
        self.createCanvas(self.cSyncCid,'新增调相机分析')
        # comment: 创建动态无功画布。
        self.createCanvas(self.cDynQid,'动态注入无功')
        
        # comment: 添加一个常数为 0 的常量组件。
        nameTemp = 'SSSCA_Const-0'
        self.addCompInCanvas(self.compLib['_newConstant'], key = 'SSSCA_Const',canvas = self.cSyncCid,                     args = {'Name':nameTemp,"Value": "0"}, pins = {'0':'SSSCA_Const-0'},label = nameTemp)
        
        # comment: 添加一个常数为 1 的常量组件。
        nameTemp = 'SSSCA_Const-1'
        self.addCompInCanvas(self.compLib['_newConstant'], key = 'SSSCA_Const',canvas = self.cSyncCid,                     args = {'Name':nameTemp,"Value": "1"}, pins = {'0':'SSSCA_Const-1'},label = nameTemp)
        
        # comment: 添加一个阶跃信号发生器，用于 S2M 信号。
        nameTemp = 'SSSCA_S2M'
        argsTemp = {'Name':nameTemp, 'V0':'0', 'V1':'1', 'Time':'1'}
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'SSSCA_S2M',canvas = self.cSyncCid,                     args = argsTemp, pins = {'0':'@SSSCA_S2M'},label = nameTemp)
        

        # comment: 在画布中换行。
        self.newLinePos(self.cSyncCid)
        
        
    # comment: 定义一个名为 getXInterval 的函数，用于在有序数据中查找给定值 x 所在区间的起始索引。
    def getXInterval(self, xData,x):
        # comment: 获取数据长度。
        nsize = len(xData)
        # comment: 设置上限和下限。
        upperLimit = nsize-1;
        lowerLimit = 0;
        # comment: 初始化中间索引。
        z = math.floor((upperLimit+lowerLimit) / 2);
        # comment: 循环直到找到区间或超出数组范围。
        while (z>=0 or z< (nsize-1)):
            # comment: 如果当前索引处的 xData 值大于 x。
            if(xData[z]>x):
                # comment: 如果 z 已经是最左端，则设为 0。
                if(z<=0):
                    z = 0;
                    break;
                # comment: 否则，更新上限并重新计算中间索引。
                else:
                    upperLimit = z;
                    z = math.floor((upperLimit+lowerLimit) / 2);
            # comment: 如果当前索引的下一个 xData 值小于 x。
            elif(xData[z+1]<x):
                # comment: 如果 z+1 已经是最右端，则设为 nsize-1。
                if(z+1>=(nsize-1)):
                    z = (nsize-1);
                    break;
                # comment: 否则，更新下限并重新计算中间索引。
                else:
                    lowerLimit = z+1;
                    z = math.floor((upperLimit+lowerLimit) / 2);
            # comment: 如果 x 在当前索引和下一个索引之间，则找到区间。
            elif(xData[z]<=x and xData[z+1]>=x):
                break;
            # comment: 发生其他情况，设为 0。
            else:
                z = 0;
                break;
        # comment: 返回找到的区间起始索引。
        return z;
    
    # comment: 定义一个名为 calculateDV 的函数，用于计算电压偏差指标。
    def calculateDV(self,jobName, voltageMeasureK, result = None, Ts = 4, dT0 = 0.5, Tinterval = 0.11, T1 = 3, dV1 = 0.25, dV2 = 0.1, VminR = 0.2, VmaxR = 1.8):
        # comment: 获取指定作业的配置。
        job = self.project.getModelJob(jobName)[0]
        # comment: 获取步长时间。
        step_time = float(job['args']['step_time'])
        # comment: 获取结束时间。
        end_time = float(job['args']['end_time'])
        # comment: 如果结果未指定，则使用当前运行器的结果。
        if(result==None):
            result = self.runner.result
        # comment: 获取电压测量数据。
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
#         comment: plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
#         comment: pdtV = 1 / plotFV;
        
        # comment: 初始化电压上限和下限的偏差列表。
        dVUj = []
        dVLj = []
        
        # comment: 初始化有效数据点的索引列表。
        ValidNum = [i for i in range(len(Vresults))]
        
#         comment: V0 = []
        # comment: 遍历每个电压测量结果。
        for k in range(len(Vresults)):
            # comment: 计算初始电压的开始和结束时间。
            ts = Ts - dT0;
            te = Ts;
        
            # comment: 获取当前测量结果的 x 和 y 值。
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];
            # comment: 找到初始电压时间段的索引区间。
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 计算初始电压的平均值。
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
#             comment: V0.append(Vaverage)
            
            # comment: 计算暂态期间的开始和结束时间。
            ts = Ts + Tinterval;
            te = Ts + Tinterval + T1;
            # comment: 找到暂态期间的索引区间。
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 计算电压上限偏差。
            dVUj_temp = (1+dV1)*Vaverage - max(vy[msV:meV])
            # comment: 计算电压下限偏差。
            dVLj_temp = min(vy[msV:meV]) - (1-dV1)*Vaverage
            
            # comment: 考虑 T1 后持续时间的电压偏差。
            dVUj_temp = min(dVUj_temp,(1+dV2)*Vaverage - max(vy[meV:]))
            dVLj_temp = min(dVLj_temp,min(vy[meV:]) - (1-dV2)*Vaverage)
            
            # comment: 将计算的偏差添加到列表中。
            dVUj.append(dVUj_temp)
            dVLj.append(dVLj_temp)
            
            # comment: 计算稳态恢复期间的开始和结束时间。
            ts = end_time - dT0;
            te = end_time;

            # comment: 找到稳态恢复期间的索引区间。
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 如果稳态恢复期间的电压超出预设范围，则从有效数据点中移除当前点。
            if(max(vy[msV:meV])<VminR * Vaverage or min(vy[msV:meV])>VmaxR * Vaverage):
                ValidNum.remove(k)
            
        # comment: 返回电压上限偏差、下限偏差和有效数据点。
        return dVUj,dVLj,ValidNum

    # comment: 定义一个名为 calculateSI 的函数，用于计算故障严重程度指标 (SI)。
    def calculateSI(self,jobName, voltageMeasureK, result = None, Ts = 4, dT0 = 0.5, Tinterval = 0.11, T1 = 3, dV1 = 0.25, dV2 = 0.1, VminR = 0.2, VmaxR = 1.8):
        # comment: 获取指定作业的配置。
        job = self.project.getModelJob(jobName)[0]
        # comment: 获取步长时间。
        step_time = float(job['args']['step_time'])
        # comment: 获取结束时间。
        end_time = float(job['args']['end_time'])
        # comment: 如果结果未指定，则使用当前运行器的结果。
        if(result==None):
            result = self.runner.result
        # comment: 获取电压测量数据。
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
#         comment: plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
#         comment: pdtV = 1 / plotFV;
        
        # comment: 初始化有效数据点的索引列表。
        ValidNum = [i for i in range(len(Vresults))]
        
#         comment: V0 = []
        # comment: 初始化故障严重程度指标。
        SI = 0;
        # comment: 遍历每个电压测量结果。
        for k in range(len(Vresults)):
            # comment: 计算初始电压的开始和结束时间。
            ts = Ts - dT0;
            te = Ts;
        
            # comment: 获取当前测量结果的 x 和 y 值。
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];

            # comment: 找到初始电压时间段的索引区间。
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 计算初始电压的平均值。
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
#             comment: V0.append(Vaverage)

            # comment: 计算稳态恢复期间的开始和结束时间。
            ts = end_time - dT0;
            te = end_time;
            # comment: 找到稳态恢复期间的索引区间。
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 如果稳态恢复期间的电压超出预设范围，则从有效数据点中移除当前点并跳过此点。
            if(max(vy[msV:meV])<VminR * Vaverage or min(vy[msV:meV])>VmaxR * Vaverage):
                ValidNum.remove(k)
                continue

            # comment: 计算暂态期间的开始和结束时间。
            ts = Ts + Tinterval;
            te = Ts + Tinterval + T1;
            # comment: 找到暂态期间的索引区间。
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);

            # comment: 计算暂态期间电压超出 dV1 允许范围的比例，并累加到 SI。
            SI += len([i for i in vy[msV:meV] if (i < (1-dV1)*Vaverage or i > (1+dV1)*Vaverage)]) / (meV-msV);
            # comment: 计算暂态结束到结束时间段内电压超出 dV2 允许范围的比例，并累加到 SI。
            SI += len([i for i in vy[meV:] if (i < (1-dV2)*Vaverage or i > (1+dV2)*Vaverage)]) / len(vy[meV:]);

        # comment: 计算平均故障严重程度指标。
        SI = SI / len(ValidNum);

        # comment: 返回故障严重程度指标和有效数据点。
        return SI,ValidNum
    
    # comment: 定义一个名为 calculateVSI 的函数，用于计算电压敏感度指标 (VSI)。
    def calculateVSI(self, jobName, voltageMeasureK, dQMeasureK, result = None, busNum = None, Ts = 4, dT = 1, ddT = 0.5):
        
        # comment: 获取指定作业的配置。
        job = self.project.getModelJob(jobName)[0]
        # comment: 获取步长时间。
        step_time = float(job['args']['step_time'])
        # comment: 如果结果未指定，则使用当前运行器的结果。
        if(result==None):
            result = self.runner.result
        # comment: 获取电压测量数据。
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
        # comment: plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
        # comment: pdtV = 1 / plotFV;
        
        # comment: 获取动态无功测量数据。
        Qresult = result.getPlot(dQMeasureK)['data']['traces'][0]
        # comment: plotFQ = float(job['args']['output_channels'][dQMeasureK][1]);
        # comment: pdtQ = 1 / plotFQ;
        
        # comment: 获取动态无功的 x 和 y 值。
        Qx = Qresult['x']
        Qy = Qresult['y']
        
        # comment: 初始化 VSI 矩阵和 VSI 向量。
        VSIij = []
        VSIi = []
        
        # comment: 如果母线数量未指定，则根据仿真时间计算。
        if (busNum == None):
            busNum = (float(job['args']['end_time']) - Ts) / dT;
        
        # comment: 计算初始电压的开始和结束时间。
        ts = Ts - dT + ddT ;
        te = Ts;
        # comment: 初始化初始电压列表。
        V0 = []
        # comment: 遍历每个电压测量结果，计算初始电压平均值。
        for k in range(len(Vresults)):
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
            V0.append(Vaverage)
                
        # comment: 遍历指定的母线数量，计算 VSI。
        for n in range(busNum):
            # comment: 计算当前时间段的开始和结束时间。
            ts = Ts + dT * n;
            te = Ts + dT * n + ddT;
#             comment: msV = int(ts / pdtV)
#             comment: meV = int(te / pdtV)
#             comment: msQ = int(ts / pdtQ)
#             comment: meQ = int(te / pdtQ)

            # comment: 找到动态无功时间段的索引区间。
            msQ = self.getXInterval(Qx,ts);
            meQ = self.getXInterval(Qx,te);
        
#             comment: Qaverage = sum(Qy[msQ:meQ]) / (meQ - msQ)
            # comment: 获取当前动态无功值（通常是注入量）。
            Qaverage = Qy[meQ-1]
            
            # comment: 初始化 V1 列表。
            V1 = []
            
            # comment: 遍历每个电压测量结果，计算电压变化量。
            for k in range(len(Vresults)):
                vx = Vresults[k]['x'];
                vy = Vresults[k]['y'];
                msV = self.getXInterval(vx,ts);
                meV = self.getXInterval(vx,te);
#                 comment: Vtemp = V0[k] - max(vy[msV:meV]) 
                # comment: 计算电压变化量。
                Vtemp = V0[k] - sum(vy[msV:meV]) / (meV - msV)
                # comment: 计算 VSIij (电压变化 / 无功变化)。
                V1.append(Vtemp / Qaverage)
            # comment: 将 VSIij 添加到列表中。
            VSIij.append(V1)
            # comment: 计算 VSIi (平均电压敏感度)。
            VSIi.append(sum(V1) / len(V1))
        # comment: 返回 VSIish 和 VSIi。
        return VSIij, VSIi
        
        
    
    # comment: 定义一个名为 addVSIMeasure 的函数，用于添加 VSI 的量测。
    def addVSIMeasure(self, jobName,VMin = None, VMax = None, NameSet = None, NameKeys = None, freq = None,Nbus = 10,  dT = 0.5, Ts = 4):
        '''
            comment: jobName: 仿真Job名字
            comment: 添加VSI的量测，包括量测引脚的添加、在Job中添加输出通道
            comment: 可以用Vmin，VMax，NameSet，NameKeys来筛选用于电压量测的母线，各条件取交集。
            comment: freq为输出频率。
        '''
        # comment: 获取指定作业的配置。
        job = self.project.getModelJob(jobName)[0]
        
        
        # comment: 添加电压量测并获取筛选后的母线。
        screenedBus = self.addVoltageMeasures(jobName, VMin, VMax, NameSet, NameKeys, freq, PlotName = 'VSI_节点电压量测');
        # comment: 获取电压测量在输出通道列表中的索引。
        voltageMeasureK = len(job['args']['output_channels']) - 1;
        
        # comment: 更新作业的结束时间，以适应 VSI 测量的时间范围。
        job['args']['end_time'] = Nbus * dT + Ts;
        
        # comment: 添加动态无功（#SA_VSI_DQ）的输出通道。
        id1, label = self.addChannel('#SA_VSI_DQ',1)
        # comment: 将动态无功输出通道配置添加到作业中。
        self.addOutputs(jobName, {'0':'VSI_动态注入无功量测', '1':freq, '2':'compressed', '3':1, '4':[id1]})
        # comment: 获取动态无功测量在输出通道列表中的索引。
        dQMeasureK = voltageMeasureK + 1;

        # comment: 返回电压测量索引、动态无功测量索引和筛选后的母线。
        return voltageMeasureK, dQMeasureK, screenedBus
        
    
    # comment: 定义一个名为 addVSIQSource 的函数，用于添加 VSI 动态无功源。
    def addVSIQSource(self, busKeys, V = 220, S = 1, Ts = 4, dT = 1, ddT = 0.5):
        '''
            comment: busKeys:{busKey1, busKey2}
            comment: V:添加的动态注入无功源的基准电压，单位为kV
            comment: S:添加的动态注入无功源的基准无功，单位为MVar
            comment: dT:对每个母线测试时所占用的仿真时长,s
        '''
# comment: 添加 shuntLC (并联电容/电感)
        # comment: 定义瞬态 ID。
        tempID = 'SA_newShuntLC_3p';
        # comment: 获取并联电容/电感组件的名称。
        nameTemp = self.compNames['_newShuntLC_3p']
        # comment: 初始化 shuntLC 的参数。
        argsTemp = {'Name':nameTemp,'Dim':'3', 'v':str( V), 's':str(-S), "Q": '#SA_VSI_DQ'}
        # comment: 初始化 shuntLC 的引脚。
        pinsTemp = {"0": 'SA_VSI_C'}
        
        # comment: 在动态无功画布中添加 shuntLC 组件。
        id1, label = self.addCompInCanvas(self.compLib['_newShuntLC_3p'], key = tempID, canvas = self.cDynQid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        # comment: 在画布中换行。
        self.newLinePos(self.cDynQid)
        
# comment: 添加众多开关
        # comment: 初始化信号字典。
        signalDict = {}
        
        # comment: 遍历所有母线键，为每个母线添加一个断路器。
        for k in range(len(busKeys)):
            busK = busKeys[k];
            # comment: 定义断路器瞬态 ID。
            tempID = 'SA_VSI_Breaker_'+str(k);
            # comment: 定义断路器名称。
            nameTemp = 'SA_VSI分析_断路器_'+str(k);
            # comment: 定义断路器控制信号名称。
            ctrlSigName = '@SA_VSI分析_断路器_'+str(k);
            # comment: 初始化断路器参数。
            argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '0'}
            
            # comment: 获取母线组件的引脚名称。
            pinName = self.project.getComponentByKey(busK).pins['0']
            # comment: 初始化断路器引脚。
            pinsTemp = {"0": pinName,"1": 'SA_VSI_C'}
        
            # comment: 在动态无功画布中添加断路器。
            id1, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = tempID, canvas = self.cDynQid,                         args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 添加开关信号源
            # comment: 定义开关信号源名称。
            nameTemp = 'SA_VSI分析_断路器_信号'
            # comment: 初始化下降阶跃信号发生器参数，用于控制断路器的开关时间。
            argsTemp = {'Name':nameTemp, 'INIT':'0', 'Drop':'1', 'T1':str(Ts + k * dT), 'T2':str(Ts + k * dT + ddT)}
            # comment: 在动态无功画布中添加下降阶跃信号发生器。
            ids, labes = self.addCompInCanvas(self.compLib['_newDropGen'], key = 'SA_VSI_Breaker_Sig',canvas = self.cDynQid,                         args = argsTemp, pins = {'0':ctrlSigName},label = nameTemp, MaxX = 500)
            
        # comment: 在画布中换行。
        self.newLinePos(self.cDynQid)

        

    # comment: 定义一个名为 addSVC 的函数，用于添加静态无功补偿器 (SVC)。
    def addSVC(self, busKey, S = 1, Ts = 4, Te = 999):
        '''
            comment: busKeys:{busKey1, busKey2}
            comment: V:添加的动态注入无功源的基准电压，单位为kV
            comment: S:添加的动态注入无功源的基准无功，单位为MVar
            comment: dT:对每个母线测试时所占用的仿真时长,s
        '''
        # comment: 获取母线的基准电压。
        V = float(self.project.getComponentByKey(busKey).args['VBase']);
        # comment: 获取母线的引脚名称。
        busPin = self.project.getComponentByKey(busKey).pins['0'];
        
        # comment: 获取母线名称。
        busName = self.project.getComponentByKey(busKey).label;
        # comment: 定义 SVC 开关引脚名称。
        switchPin = 'SVC_Switch_'+busName;
# comment: 添加 shuntLC
        # comment: 定义 SVC 组件的瞬态 ID。
        tempID = 'SA_SVC';
        # comment: 定义 SVC 组件的名称。
        nameTemp = 'SA_SVC'+busName
        # comment: 初始化 SVC 组件的参数。
        argsTemp = {'Name':nameTemp,'Dim':'3', 'v':str( V), 's':str(S)}
        # comment: 定义 SVC 组件的引脚。
        pinsTemp = {"0": switchPin}
        
        # comment: 在动态无功画布中添加 SVC 组件。
        id1, label = self.addCompInCanvas(self.compLib['_newShuntLC_3p'], key = tempID, canvas = self.cDynQid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        # comment: 在画布中换行。
        self.newLinePos(self.cDynQid)
        
# comment: 添加开关
        # comment: 定义 SVC 断路器组件的瞬态 ID。
        tempID = 'SA_SVC_Breaker';
        # comment: 定义 SVC 断路器组件的名称。
        nameTemp = 'SA_SVC_Breaker'+busName;
        # comment: 定义 SVC 断路器控制信号名称。
        ctrlSigName = '@SVC_'+busName;
        # comment: 初始化 SVC 断路器参数。
        argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '0'}
        
        # comment: 定义 SVC 断路器引脚。
        pinsTemp = {"0": busPin,"1": switchPin}
    
        # comment: 在动态无功画布中添加 SVC 断路器。
        id2, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = tempID, canvas = self.cDynQid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 添加开关信号源
        # comment: 定义开关信号源名称。
        nameTemp = 'SA_VSI分析_断路器_信号'
        # comment: 初始化下降阶跃信号发生器参数，用于控制 SVC 断路器的开关时间。
        argsTemp = {'Name':nameTemp, 'INIT':'0', 'Drop':'1', 'T1':str(Ts), 'T2':str(Te)}
        # comment: 在动态无功画布中添加下降阶跃信号发生器。
        ids, labes = self.addCompInCanvas(self.compLib['_newDropGen'], key = 'SA_SVC_Breaker_Sig',canvas = self.cDynQid, args = argsTemp, pins = {'0':ctrlSigName},label = nameTemp, MaxX = 500)
            
        # comment: 在画布中换行。
        self.newLinePos(self.cDynQid)

        # comment: 返回添加的组件 ID 列表。
        return [id1,id2,ids]


    # comment: 定义一个名为 addSyncComp 的函数，用于添加同步补偿器（包括同步发电机、相关母线、变压器和 AVR）。
    def addSyncComp(self, busKey, pfResult, syncArgs = None,transArgs = None, busArgs = None, AVRComp = None, AVRArgs = None):
        '''
            comment: transArgs:{"Smva": "额定容量","X1": "正序漏电抗","Rl": "正序漏电阻"}
            comment: syncArgs:{"Smva": "额定容量","V": "额定相电压有效值","freq": "额定频率"...}
        '''
        
#         comment: nameTemp = 'SSSCA_同步调相机'
#         comment: argsTemp = {'Name':nameTemp, 'VT_o':str(fault_start_time), 'fe':str(fault_end_time),'ft':str(fault_type)}
        
        # comment: 创建一个空的 pandas DataFrame。
        data = pd.DataFrame()
        # comment: 获取潮流计算结果中的母线信息。
        pfBusResult=pfResult.getBuses() 
        # comment: 找到指定母线键在潮流结果中的索引。
        pfBusIndex = pfBusResult[0]['data']['columns'][0]['data'].index(busKey);
        # comment: 获取母线的电压幅值。
        vm = pfBusResult[0]['data']['columns'][2]['data'][pfBusIndex];
        # comment: 获取母线的电压相角。
        va = pfBusResult[0]['data']['columns'][3]['data'][pfBusIndex];
        # comment: 获取母线的基准电压。
        VB = float(self.project.getComponentByKey(busKey).args['VBase'])
        
#         comment: if(name==None):
#         comment:     name = '新调相机';
        
#         comment: busName = name+'-母线';
#         comment: transName = name+'-变压器';
#         comment: avrName = name+'-AVR';
#         comment: syncName = name+'-电机';

# comment: 处理同步电机
        # comment: 定义同步电机组件的瞬态 ID。
        tempID = 'SA_Sync';
        # comment: 获取同步发电机组件的名称。
        nameTemp = self.compNames['SyncGeneratorRouter']
        
        # comment: 如果该类型的同步电机组件尚未计数，则初始化计数器。
        if(tempID not in self.compCount.keys()):
            self.compCount[tempID] = 0;
        # comment: 增加组件计数。
        count = self.compCount[tempID] + 1;
        # comment: 生成新的组件名称。
        nameCount = nameTemp + "_" + str(count)
        syncName = nameCount;
        
        # comment: 初始化同步电机的参数。
        argsTemp = {'Name':nameTemp,'pf_P':'0', 'pf_Q':'0', 'pf_V':str(vm), 'pf_Theta':str(va),
                   "V_mag": str(vm), "V_ph": str(va), "AP": "0", "RP": "0",
                   "s2m_o": "","l2n_o": "","Tm0_o": "","wr_o": "","theta_o": "",
                   "loadangle_o": "","loadangle_so": "","IT_o": "","PT_o": "","QT_o": "","IT_inst": "",
                   "VT_o":'#'+syncName+'.VT', "Ef0_o":'#'+syncName+'.Ef0'}
        # comment: 如果提供了同步电机参数，则更新参数字典。
        if(syncArgs!=None):
            argsTemp.update(syncArgs);
        
        # comment: 定义同步电机的引脚。
        pinsTemp = {"0": syncName,
                    "1": "",
                    "2": "SSSCA_Const-0",
                    "3": syncName+".Te",
                    "4": syncName+".Ef",
                    "5": syncName+".If"}
        
        # comment: 在同步补偿器画布中添加同步发电机。
        Syncid1, label = self.addCompInCanvas(self.compLib['SyncGeneratorRouter'], key = tempID, canvas = self.cSyncCid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        # comment: 获取同步发电机的基准电压（相电压转换为线电压）。
        VBSync = float(self.project.getComponentByKey(Syncid1).args['V']) * math.sqrt(3);
        
        
# comment: 处理母线
        # comment: 定义同步伴随母线组件的瞬态 ID。
        tempID = 'SA_Sync_Bus';
        # comment: 获取三相母线组件的名称。
        nameTemp = self.compNames['_newBus_3p']
        # comment: 初始化伴随母线的参数。
        argsTemp = {'Name':nameTemp,'Freq':'50', 'VBase':str(VBSync), 'V':str(vm), 'Theta':str(va),"Vabc": "","Vrms": ""}
        # comment: 如果提供了母线参数，则更新参数字典。
        if(busArgs!=None):
            argsTemp.update(busArgs);
        # comment: 定义伴随母线的引脚。
        pinsTemp = {"0": syncName}
        # comment: 在同步补偿器画布中添加伴随母线。
        Busid1, label = self.addCompInCanvas(self.compLib['_newBus_3p'], key = tempID, canvas = self.cSyncCid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 处理变压器
        # comment: 定义变压器组件的瞬态 ID。
        tempID = 'SA_Transformer_3p2w';
        # comment: 获取双绕组变压器组件的名称。
        nameTemp = self.compNames['_newTransformer_3p2w']
        # comment: 初始化变压器的参数（高压侧和低压侧电压）。
        argsTemp = {'Name':nameTemp, 'V1':str(VBSync), 'V2':str(VB)}
        # comment: 如果提供了母线参数（此处可能应为 transArgs，但代码中使用了 busArgs），则更新参数字典。
        if(busArgs!=None):
            argsTemp.update(busArgs);
            
        # comment: 获取目标母线的引脚名称。
        busName = self.project.getComponentByKey(busKey).pins['0']
        # comment: 定义变压器的引脚。
        pinsTemp = {"0": syncName,"1": busName}
        # comment: 在同步补偿器画布中添加变压器。
        Transid1, label = self.addCompInCanvas(self.compLib['_newTransformer_3p2w'], key = tempID, canvas = self.cSyncCid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 处理AVR (自动电压调节器)
        # comment: 定义 AVR 组件的瞬态 ID。
        tempID = 'SA_PSASP_AVR_11to12';
        # comment: 如果 AVRComp 未指定，则使用默认的 PSASP_AVR_11to12。
        if(AVRComp==None):
            AVRComp = self.compLib['_PSASP_AVR_11to12'];
            # comment: 获取 AVR 组件的名称。
            nameTemp = self.compNames['_PSASP_AVR_11to12']
            # comment: 定义 AVR 组件的引脚。
            pinsTemp = {"0": syncName+".Vref",
                        "1": "SSSCA_Const-0",
                        "2": '#'+syncName+'.VT',
                        "3": '#'+syncName+'.Ef0',
                        "4": syncName+".If",
                        "5": "@SSSCA_S2M",
                        "6": syncName+".Vref0",
                        "7": syncName+".Ef" }
        # comment: 如果提供了 AVRComp，则从其定义中提取名称。
        else:
            definition = AVRComp["definition"]
            nameTemp = definition.split('/')[-1]
        # comment: 初始化 AVR 参数。
        argsTemp = {}
        # comment: 如果提供了 AVRArgs，则更新参数字典。
        if(AVRArgs!=None):
            argsTemp.update(AVRArgs);
        # comment: 在同步补偿器画布中添加 AVR 组件。
        AVRid1, label = self.addCompInCanvas(AVRComp, key = tempID, canvas = self.cSyncCid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 处理 newGain (增益块)
        # comment: 定义增益块组件的瞬态 ID。
        tempID = 'SA_newGain';
        # comment: 获取增益块组件的名称。
        nameTemp = self.compNames['_newGain']
        # comment: 初始化增益块的参数。
        argsTemp = {'G':'1'}
        # comment: 定义增益块的引脚。
        pinsTemp = {"0": syncName+".Vref0",
                    "1": syncName+".Vref"}
        # comment: 在同步补偿器画布中添加增益块。
        Gainid1, label = self.addCompInCanvas(self.compLib['_newGain'], key = tempID, canvas = self.cSyncCid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        
        # comment: 在画布中换行。
        self.newLinePos(self.cSyncCid)
        
        # comment: 返回添加的组件 ID 列表。
        return [Syncid1,Busid1,Transid1,AVRid1,Gainid1]


# # comment: OtherData

# # comment: ## getCompLib


# comment: 定义一个名为 getCompLib 的函数，用于获取组件库。
def getCompLib(tk, apiURL, spr, compDefLib = {}, name = None):
    # comment: 设置 CloudPSS 的访问令牌。
    cloudpss.setToken(tk)
    # comment: 设置 CloudPSS API 的 URL 环境变量。
    os.environ['CLOUDPSS_API_URL'] = apiURL
    # comment: 从 CloudPSS 平台获取指定的项目。
    sproject = cloudpss.Model.fetch(spr)
    # comment: 初始化组件库字典。
    compLib = {}
    # comment: 如果 compDefLib 为空，则初始化默认的组件定义库映射。
    if compDefLib=={}:
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
    # comment: 创建一个反向映射，将 rid 映射回组件名称。
    compDefLib_inv = {v: k for k, v in compDefLib.items()}
    # comment: 遍历项目中所有组件的键。
    for i in sproject.getAllComponents().keys():
        # comment: 将组件转换为 JSON 格式。
        comp = sproject.getAllComponents()[i].toJSON()
        # comment: 如果组件形状是 'diagram-component'。
        if(comp['shape']=='diagram-component'):
            # comment: 深度复制组件。
            compcp = copy.deepcopy(comp);
            # comment: 清空样式信息。
            compcp['style'] = {}
            # comment: 如果组件的定义不在反向映射中。
            if(comp['definition'] not in compDefLib_inv.keys()):
                # comment: 使用正则表达式从定义中提取区域名称。
                pattern = '[^/]*/[^/]*/([^/]*)$'
                zone = re.search(pattern,comp['definition']);
                # comment: 将组件添加到组件库中。
                compLib[zone.group(1)] = compcp;
            # comment: 否则，使用反向映射中的名称。
            else:
                compLib[compDefLib_inv[comp['definition']]] = compcp;
    # comment: 如果文件名未指定，则默认为 'saSource.json'。
    if(name==None):
        name = 'saSource.json'
    # comment: 将组件库保存为 JSON 文件。
    with open(name, "w", encoding='utf-8') as f:
        f.write(json.dumps(compLib, indent=4))
    # comment: 返回组件库。
    return compLib


# # comment: ## fetchCompData


# comment: 定义一个字符串模板，用于构建 GraphQL 查询以获取模型信息。
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


# comment: 定义一个名为 fetchCompData 的函数，用于获取组件数据。
def fetchCompData(rids=None):

    # comment: 如果 rids 未指定，则抛出异常。
    if rids is None:
        raise Exception('rids must be specified')
    # comment: 初始化模型列表。
    models = []
    # comment: 初始化计数器。
    i = 0
    # comment: 遍历每个 rid，并使用模板创建模型查询字符串。
    for rid in rids:
        i += 1
        models.append(
            MODE_TEMPLATE.safe_substitute(model='model' + str(i), rid=rid))

    # comment: 构建完整的 GraphQL 查询字符串。
    query = "query { %s }" % ' '.join(models)

    # comment: 发送 GraphQL 请求并获取数据。
    data = cloudpss.utils.graphql_request(query, {})

    # comment: 返回数据中的 'data' 部分。
    return data['data']




# # comment: ## ParaDict


# comment: 定义一个名为 genParaDict 的函数，用于生成参数和引脚字典。
def genParaDict(zdmToken,internalapiurl,projName):
    # comment: 初始化参数字典。
    ParaDict = {}
    # comment: 初始化引脚字典。
    PinDict = {}
    
#     comment: zdmToken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzMsInVzZXJuYW1lIjoiQ2xvdWRQU1MiLCJzY29wZXMiOlsidW5rbm93biJdLCJ0eXBlIjoiU0RLIiwiZXhwIjoxNjYxNTgwNDc4LCJpYXQiOjE2MzAwNDQ0MjR9.KWqs-InItjYIGmXC-zKUGqPxBZZyxj52DHt_q7ftdP3eUM65a5ZJgQVn6hYpHEJYRShB_u_nOD5MivHdsnZsYf-F8U3Jyhel9BBVUkKA3LzbaEQgPHFAg50ftVW86HXnUlUC2oiV_uleH_g8tt9N__RGTnMV3VDl23Ie9uICQnI'
#     comment: internalapiurl = 'https://internal.cloudpss.net/';
#     comment: projName = 'model/greyd/AllMachineCtrlComp';
    # comment: 设置 CloudPSS 的访问令牌。
    cloudpss.setToken(zdmToken)
    # comment: 设置 CloudPSS API 的 URL 环境变量。
    os.environ['CLOUDPSS_API_URL'] = internalapiurl
    # comment: 从 CloudPSS 平台获取指定的项目。
    prjtmp = cloudpss.Model.fetch(projName)
    # comment: 获取项目中所有组件。
    allcomp = prjtmp.getAllComponents();
    # comment: 初始化存储所有组件定义的列表。
    allcompList = []
    
    
    
    
    # comment: 遍历所有组件的键。
    for cmp in allcomp.keys():
        # comment: 将组件转换为 JSON 格式。
        cmpJSN = allcomp[cmp].toJSON()
        # comment: 将组件的定义添加到列表中。
        allcompList.append(cmpJSN['definition']);
    # comment: 批量获取组件的原始数据。
    RawDataList = fetchCompData(allcompList);
    # comment: 遍历原始数据列表中的每个组件数据。
    for rawData in RawDataList.values():
        
        # comment: print(rawData)
        
        
        # comment: 初始化当前组件的参数字典。
        ParaDict[rawData['rid']] = {}
        # comment: 将组件的名称作为描述性名称。
        ParaDict[rawData['rid']]['DiscriptName'] = rawData['name']
        # comment: 初始化当前组件的引脚字典。
        PinDict[rawData['rid']] = {}
        
#         comment: rawData['revision']['parameters'][0]['name']
#         comment: print(rawData)
        # comment: 遍历组件修订版本中的参数。
        for item0 in rawData['revision']['parameters']:
            # comment: 遍历参数中的每个子项。
            for item1 in item0['items']:
                # comment: 将参数项添加到参数字典中。
                ParaDict[rawData['rid']][item1['key']] = item1;
        # comment: 遍历组件修订版本中的引脚。
        for item0 in rawData['revision']['pins']:
            # comment: 将引脚项添加到引脚字典中。
            PinDict[rawData['rid']][item0['key']] = item0;
            
            
            
    #     comment: ParaDict[rawData['rid']]['DiscriptName'] = rawData['revision']['parameters'][0]['name']
    #     comment: ParaDict[rawData['rid']] = rawData['revision']['parameters'][0]
    #     comment: print(rawData['rid'])
    #     comment: print(rawData['revision']['parameters'][0].keys())
    #     comment: print(rawData['revision']['parameters'][0]['items'][1])
#     comment: ParaDict['model/CloudPSS/_PSASP_PSS_5']
    # comment: 返回参数字典和引脚字典。
    return ParaDict,PinDict