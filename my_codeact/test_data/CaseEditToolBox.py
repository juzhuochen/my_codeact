
import csv
from datetime import datetime
from typing import Dict, List, Optional, TypedDict,Union,Set,Tuple
import cloudpss
import os
import time
import json
import re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
# from jobApi import fetch,fetchAllJob,abort

import igraph as ig
from itertools import combinations
import plotly.figure_factory as ff
import tkinter
import tkinter.filedialog

import math

from IPython.display import display, HTML
from html import unescape


import random
import json
import copy
from cloudpss.model.implements.component import Component
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
from cloudpss.model.revision import ModelRevision
from cloudpss.model.model import Model

from scipy import optimize

from string import Template

import plotly.io as pio
pio.renderers.default = "browser"


def is_number(s: str) -> bool:
    """
    Descriptions
    ----------
        判断一个字符串是否可以转换为数字。

    Parameters
    ----------
        s (str): 待判断的字符串。

    Returns
    -------
        bool: 如果可以转换为数字则返回 `True`，否则返回 `False`。
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

class CaseEditToolbox:
    def __init__(self):
        """
            模块初始化。包括cloudpss库初始化、几个字典的定义。
        """
        self.config = {};
        self.config['token']='123';
        self.config['apiURL']='cloudpss.net';
        self.config['model']='test';
        self.config['username']='admin';
        
        self.config['comLibName'] = 'saSource.json';
        self.config['plotTool'] = 'plotly'; #matplotlib, plotly
        self.config['iGraph'] = True; # Generate iGraph network
        self.config['deleteEdges'] = False; # Delete edges (shape=diagram-edges components) in network, and set pin-name connection
        self.project = 0;
        
        self.compLib = {};
        self.compCount = {}
        self.pos = {}

        self.topo = None
        self.g = None
        self.current_canvas = None
        
        self.compLabelDict = {}
        self.channelPinDict = {}
        self.runner = None
        self.initJobConfig()
        
    def initJobConfig(self):
        """
            EMTP计算的参数：
                'task_queue'：清华32：taskManager_RT， 成都32：taskManager_turbol
                'solver_option': 正常：'0'， CPU_turbol：‘7’
                'n_cpu': '1'，‘2’，‘4’，‘8’，‘16’，'32'
                output_channels:[['ss1', '200', '1000', '1', 'canvas_167_8,canvas_167_9']]
            
        """
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

        self.emtpsJob_Init = {'args': {'@debug': '',
                '@priority': 0,
                '@queue': 1,
                '@tres': 'cpu=1',#逻辑核心数
                'begin_time': 0,
                'comm': [],
                'comm_freq': 1,
                'comm_protocol': 0,
                'comm_type': 0,
                'ctrlparallel_option': 0,
                'debug': 0,
                'dev_id': 1,
                'dev_num': 1,
                'end_time': 30,
                'event_option': 0,
                'init_cfg': 0,
                'initial_type': 0,
                'kernel_option': 1,
                'load_snapshot': '0',
                'load_snapshot_name': '',
                'max_initial_time': 1,
                'mergeBusNode': 0,
                'multi_dev_partition': [],
                'n_cpu': 1, #实际使用的核心数
                'n_ele_cpu': 1,
                'only_partition': 0,
                'output_channels': [],
                'partition_info': [{'0': 0, '1': '', '2': '', 'ɵid': 25021700}],
                'partition_msg_output': 1,
                'partition_option': 0,
                'ramping_time': 0,
                'realtime_timeout': 10,
                'save_snapshot': 0,
                'save_snapshot_name': 'snapshot',
                'save_snapshot_time': 1,
                'sim_option': 0,
                'snapshot_cfg': 0,
                'solver': 0,
                'solver_option': 0, # 0:常规，1:分网，2:CPU-turbo
                'step_time': 0.00005,
                'task_cmd': '',},
                'name': 'CA电磁暂态仿真方案_新',
                'rid': 'function/CloudPSS/emtps'}

        self.proj_Config_Init = {'args': {}, 'name': 'CA参数方案', 'pins': {}}
        
    def createJob(self, stype: Optional[str] = 'emtps', name: Optional[str] = None, args: Optional[Dict] = None):
        """
        Descriptions
        ----------
            创建一个计算方案。

        Parameters
        ----------
            stype (str): 为'emtps'或'powerFlow'，表示电磁暂态仿真或潮流计算。
            name (str, optional): 计算方案名称。默认为 `None`。
            args (dict, optional): 计算方案的配置。可以不填全，填需要更新的参数即可。默认为 `None`。如果stype为emtps，则字典可选的key为：begin_time、end_time、step_time、solver_option、n_cpu、@queue、@tres等，分别表示开始时间、结束时间、积分步长、计算选项、核心数、任务队列、计算资源。
        
        Examples
        --------
        >>> 创建一个名为'SA_电磁暂态仿真'的电磁暂态仿真计算方案，步长为0.00005秒，开始时间为0秒，结束时间为30秒，
        >>> createJob('emtp', name = 'SA_电磁暂态仿真', args = {'begin_time': 0,'end_time': 30,'step_time': 0.00005})
        """
        jobtemp = {}
        if(stype=='emtp'):
            jobtemp = copy.deepcopy(self.emtpJob_Init)
        elif(stype=='powerFlow'):
            jobtemp = copy.deepcopy(self.pfJob_Init)
        elif(stype=='emtps'):
            jobtemp = copy.deepcopy(self.emtpsJob_Init)
        if(name!=None):
            jobtemp['name'] = name;
        if(args!=None):
            jobtemp['args'].update(args);
        self.project.addJob(jobtemp)

        return "计算方案已创建"
        
    def createConfig(self, name: Optional[str] = None, args: Optional[Dict] = None, pins: Optional[Dict] = None):
        """
        Descriptions
        ----------
            创建一个参数方案。

        Parameters
        ----------
            name (str, optional): 参数方案名称。默认为 `None`。
            args (dict, optional): 参数方案的配置。可以不填全，填需要更新的参数即可。默认为 `None`。
            pins (dict, optional): 引脚配置。默认为 `None`。
            
        """
        configtemp = copy.deepcopy(self.proj_Config_Init)
        if(name!=None):
            configtemp['name'] = name;
        if(args!=None):
            configtemp['args'].update(args);
        if(pins!=None):
            configtemp['pins'].update(pins);
        self.project.addConfig(configtemp)
        return "参数方案已创建"
        
    def addOutputs(self, jobName: str, channels: list):
        """
        Descriptions
        ----------
            在EMTPS的计算方案中增加输出通道。

        Parameters
        ----------
            jobName (str): 计算方案的名称。
            channels (list): 需要配置的输出通道，格式为：[输出图像名称, 输出频率, 输出图像类型, 图像宽度, 输出通道key]。例如：['outputFigName', '200', '1000', '1', 'canvas_167_8,canvas_167_9,canvas_167_111']
        
        Returns
        -------
            int: 输出通道的数量。
        """
        job = self.project.getModelJob(jobName)
        if(job!=[] and job[0]['rid']==self.emtpJob_Init['rid']):
            job[0]['args']['output_channels'].append(channels)
        elif(job!=[] and job[0]['rid']==self.emtpsJob_Init['rid']):
            job[0]['args']['output_channels'].append(channels)
        return len(job[0]['args']['output_channels']) - 1;
    def runProject(self, jobName: str, configName: str, showLogs: bool = False, apiUrl: Optional[str] = None, websocketErrorTime: Optional[float] = None):
        """
        Descriptions
        ----------
            运行仿真。会一直运行，直到仿真结束。

        Parameters
        ----------
            jobName (str): 计算方案名称。
            configName (str): 参数方案名称。
            showLogs (bool, optional): 是否显示日志。默认为 `False`。
            apiUrl (str, optional): API的URL。默认为 `None`。
            websocketErrorTime (float, optional): WebSocket错误时间。默认为 `None`。
        
        Returns
        -------
            str: 运行结果id。
        """
        job = self.project.getModelJob(jobName)[0]
        config = self.project.getModelConfig(configName)[0]

        # return job,config
        for i in range(5):
            try:
                if(apiUrl!=None):
                    self.runner=self.project.run(job=job,config=config,apiUrl=apiUrl) # 运行项目
                else:
                    self.runner=self.project.run(job=job,config=config)
                # return("Runner started...")
                break
                
            except Exception as e:
                print("Start runner failed, restarting..." + str(e))
                time.sleep(60)
        # return "Start runner failed..." 
        if(job['rid']==self.emtpsJob_Init['rid']):
            endstime = float(job['args']['end_time'])
        time_start=time.time()
        time_end=0;
        print('Start simulation. Runner Status:'+str(self.runner.status()))
        while self.runner.status()<1:
            time_end = time.time();
            if(showLogs):
                for log in self.runner.result.getLogs():
                    if('data' in log.keys() and 'content' in log['data'].keys()):
                        print(log['data']['content'])
            if(job['rid']in [self.emtpJob_Init['rid'],self.emtpsJob_Init['rid']] and self.runner.result.getPlot(0)!=None):
                ckeytemp = self.runner.result.getPlotChannelNames(0)[0]
                stime = self.runner.result.getPlotChannelData(0,ckeytemp)['x'][-1]

                print('Progress: Now: '+str(round(stime,2))+ ', All: '+str(endstime)+'. Time cost:',time_end-time_start,'. Runner Status:',self.runner.status())
                if(round(stime,2)==endstime):
                    break;
        #     print(runner.result.getLogs())
            else:
                print('Time cost:',time_end-time_start,'. Runner Status:',self.runner.status())
                # if(time_end-time_start > 30):
                #     break;
            time.sleep(10)
            if self.runner.status()==-1:
                print('仿真出错了，可能是websocket问题。')
                if(websocketErrorTime!=None and job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)!=None):
                    if(stime < endstime - websocketErrorTime):
                        print('准备重新运行仿真。Current Time：'+str(round(stime,2)))
                        time.sleep(15)
                        self.runProject(jobName, configName,showLogs, apiUrl, websocketErrorTime)
                        return self.runner.status()
                elif(websocketErrorTime!=None and job['rid']==self.emtpJob_Init['rid'] and self.runner.result.getPlotChannelNames(0)==None):
                    print('准备重新运行仿真。Current Time：None')
                    self.runProject(jobName, configName,showLogs, apiUrl, websocketErrorTime)
                return -1
        
        return self.runner.id
    
    def getRunnerLogs(self):
        """
        Descriptions
        ----------
            读取runner.result.getLogs()。
        
        Returns
        -------
            list: 运行日志。
        """
        return self.runner.result.getLogs()

    def saveResult(self, filePath: Optional[str] = None):
        """
        Descriptions
        ----------
            保存仿真结果id。

        Parameters
        ----------
            filePath (str, optional): 保存的路径，为None时保存在当前文件夹下。默认为 `None`。
        """
        if filePath is None or filePath == '':
            file_path = 'runner_ids.csv'
        else:
            file_path = os.path.join(filePath,'runner_ids.csv')
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Runner ID', 'Timestamp', 'Model RID', 'Model Name'])
            writer.writerow([
                self.runner.id,  # 仿真结果ID
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                self.project.rid,  # 模型的rid
                self.project.name # 模型名称
            ])
        return file_path
        # if(fileName == None):
        #     fileName = 'Temp.cjob'
        # if(filePath!=None):
        #     fileName = filePath + fileName;
        # Result.dump(self.runner.result,fileName)
        # return self.runner.result
        

    def plotResult(self, result: Optional[object] = None, k: Optional[int] = None):
        """
        Descriptions
        ----------
            画图，仅限于EMTPS(电磁暂态仿真)。作出第k个坐标系的图。

        Parameters
        ----------
            result (object, optional): 仿真结果。默认为 `None`。
            k (int, optional): 第k个坐标系。默认为 `None`。

        Examples
        --------
            ca.plotResult(0)
            ca.plotResult(ca.runner.result,0)
            ca.plotResult(Result.load(file),0)
        """
        if(result==None):
            result = self.runner.result
        elif (isinstance(result,str)):
            results_flow = cloudpss.Job.fetch(result);
            while not results_flow.status():
                time.sleep(2)
            result = results_flow.result
        if(self.config['plotTool']=='plotly'):
            fig = go.Figure()
            if k == None:
                k=0
            # Add traces
            ckeytemp = result.getPlotChannelNames(k)
            for pk in ckeytemp:
                x = result.getPlotChannelData(k,pk)['x']
                y = result.getPlotChannelData(k,pk)['y']
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
            fig.update_layout(
                title=result.getPlot(k)['data']['title'],     # 主标题
                xaxis_title="x Axis Title",  # 2个坐标轴的标题
                yaxis_title="y Axis Title",
            )
            fig.show()
            # return x
        else:
            fig = plt.figure(figsize=(6, 3))
            plt.title(result.getPlot(k)['data']['title'], fontproperties="Euclid")
            ckeytemp = result.getPlotChannelNames(k)
            handles = []

            for pk in ckeytemp:
                x = result.getPlotChannelData(k, pk)['x']
                y = result.getPlotChannelData(k, pk)['y']
                hd, = plt.plot(x, y, label=pk)
                handles.append(hd)

            plt.xlabel('Time / s', fontproperties="Euclid")
            plt.ylabel('Value', fontproperties="Euclid")
            plt.legend(handles=handles)
            plt.show()
       
    def displayPFResult(self, k: Optional[int] = None):
        """
        Descriptions
        ----------
            输出表格，仅限于Power Flow(潮流计算)。

        Parameters
        ----------
            k (int, optional): 表格索引。默认为 `None`。

        Notes
        -----
            runner.result.getBuses解析：
            x=runner.result.getBuses()
            x[0]['data']['title'] 
            x[0]['data']['columns'][0~n]['name']
            x[0]['data']['columns'][0~n]['data']
        """
        
        # if(k == None or k==0):
        #     data = pd.DataFrame()
        #     x=self.runner.result.getBuses()
        #     for y in x[0]['data']['columns']:
        #         data[y['name']] = y['data']
        #     s = data.to_html();
        #     s = unescape(s)
        #     s = HTML(s)
        #     display(s)
        # if(k==None or k==1):
        #     data = pd.DataFrame()
        #     x=self.runner.result.getBranches()
        #     for y in x[0]['data']['columns']:
        #         data[y['name']] = y['data']
        #     s = data.to_html();
        #     s = unescape(s)
        #     s = HTML(s)
        #     display(s)
        if k is None or k == 0:
            self.show_table_plotly(self.runner.result.getBuses(), title="Bus Data")

        if k is None or k == 1:
            self.show_table_plotly(self.runner.result.getBranches(), title="Branch Data")  
    def show_table_plotly(self,data_dict, title=None):
        """将自定义格式数据转为 DataFrame 并用 Plotly 显示"""
        df = pd.DataFrame()
        for col in data_dict[0]['data']['columns']:
            df[col['name']] = col['data']
        fig = ff.create_table(df)
        if title:
            fig.update_layout(title_text=title, title_x=0.5)
        fig.show()

    def initCanvasPos(self, canvas: str):
        """
        Descriptions
        ----------
            初始化某图层的坐标。

        Parameters
        ----------
            canvas (str): 为指定图纸的key。
        """
        self.pos[canvas] = {}
        self.pos[canvas]['dx'] = 20;
        self.pos[canvas]['dy'] = 20;
        self.pos[canvas]['x0'] = 20;
        self.pos[canvas]['y0'] = 20;
        self.pos[canvas]['x'] = self.pos[canvas]['x0'];
        self.pos[canvas]['y'] = self.pos[canvas]['y0'];
        
        self.pos[canvas]['maxdy'] = 0;
         
    def getRevision(self, file: Optional[str] = None):
        """
        Descriptions
        ----------
            获取当前项目版本信息的json格式。

        Parameters
        ----------
            file (str, optional): 可选，如果需要保存到本地，则指定文件路径。默认为 `None`。
            
        Returns
        -------
            dict: 当前的project.revision.toJSON()。
        """
        r1 = copy.deepcopy(self.project.revision.toJSON());

        # if file!=None:
        #     with open(file, "w", encoding='utf-8') as f:
        #         f.write(json.dumps(r1, indent=4))

        
        if file!=None:
            os.makedirs(file, exist_ok=True)
            file = os.path.join(file,'revision.json')
            with open(file, "w", encoding='utf-8') as f:
                f.write(json.dumps(r1, indent=4))
        return r1
    
    def loadRevision(self, revision: Optional[Dict] = None, file: Optional[str] = None):
        """
        Descriptions
        ----------
            加载指定版本信息，提供直接上传某revision的json格式或读取版本文件两张方式。两个参数选其一即可。
        
        Parameters
        ----------
            revision (dict, optional): 某revision的json格式。默认为 `None`。
            file (str, optional): 读取文件名。默认为 `None`。
        """
        if(revision!=None):
            self.project.revision = ModelRevision(revision);
        else:
            with open(file, "r", encoding='utf-8') as f:
                f = json.load(file)
                self.project.revision = ModelRevision(revision);

    def setConfig(self,token: Optional[str] = None, apiURL: Optional[str] = None, username: Optional[str] = None, model: Optional[str] = None, comLibName: Optional[str] = None, iGraph: Optional[bool] = None):
        """
        Descriptions
        ----------
            配置模块，用于初始化。

        Parameters
        ----------
            token (str, optional): 从cloudpss平台中申请。默认为 `None`。
            apiURL (str, optional): 域名。默认为 `None`。
            username (str, optional): 用户名。默认为 `None`。
            model (str, optional): 算例名称（不带/model/username）。默认为 `None`。
            comLibName (str, optional): 默认为'saSource.json'。默认为 `None`。
            iGraph (bool, optional): 是否生成iGraph网络。默认为 `None`。
        """
        
        if(token != None):
            self.config['token']=token;
        if(apiURL != None):
            self.config['apiURL']=apiURL;
        if(username!=None):
            self.config['username']=username;
        if(model!=None):
            self.config['model']=model;
        if(comLibName!=None):
            self.config['comLibName']=comLibName;        
        if(iGraph!=None):
            self.config['iGraph']=iGraph;
   
    def setInitialConditions(self):
        """
        Descriptions
        ----------
            模块初始化。需要在完成setConfig后手动调用。
        """
        cloudpss.setToken(self.config['token'])
        os.environ['CLOUDPSS_API_URL'] = self.config['apiURL']
        print('正在获取算例...')
        self.project = cloudpss.Model.fetch('model/'+self.config['username']+'/'+self.config['model'])
        with open(self.config['comLibName'], "r", encoding='utf-8') as f:
            self.compLib = json.load(f)
        self.compCount = {key:0 for key in self.compLib.keys()}
        if (self.config['deleteEdges']):
            print('正在获取拓扑信息...')
            self.refreshTopology()
            print('正在替换引脚连接关系...')
            self.deleteEdges()
        print('正在初始化...')
        self.setCompLabelDict()
        self.setChannelPinDict()
        self.current_canvas = self.project.revision.implements.diagram.canvas[0]['key']
        self.initCanvasPos(self.current_canvas)

        # if(self.config['iGraph'] == True):
        #     print('正在生成iGraph图（耗时较长，可在config中设置iGraph为False以关闭该功能）...')
        #     self.refreshTopology()
        #     self.generateNetwork()
        #     self.NetShapeConfig = {'model/CloudPSS/_newBus_3p':{'color':'cyan','shape':'circle','size':8,'label_size':10},
        #         'model/CloudPSS/_newTransformer_3p2w':{'color':'darkolivegreen','shape':'triangle-up','size':8,'label_size':10},
        #         'model/CloudPSS/_newTransformer_3p3w':{'color':'darkolivegreen','shape':'triangle-up','size':8,'label_size':10},
        #         'model/CloudPSS/TranssmissionLineRouter':{'color':'gold','shape':'square-open','size':8,'label_size':10},
        #         'model/CloudPSS/SyncGeneratorRouter':{'color':'plum','shape':'diamond','size':8,'label_size':10},
        #         'model/admin/WGSource':{'color':'plum','shape':'diamond','size':8,'label_size':10},
        #         'model/CloudPSS/PVStation':{'color':'plum','shape':'diamond','size':8,'label_size':10},
        #         'model/CloudPSS/_newACVoltageSource_3p':{'color':'plum','shape':'diamond','size':8,'label_size':10},
        #         'model/admin/DCLine':{'color':'orange','shape':'square','size':10,'label_size':10}
        #         }

    def refreshTopology(self):
        """
        Descriptions
        ----------
            刷新拓扑。
        """
        revision = cloudpss.ModelRevision.create(self.project.revision)
        # revision = nest_asyncio.asyncio.run(cloudpss.ModelRevision.create(self.project.revision))
        self.topo = cloudpss.ModelTopology.fetch(revision['hash'], 'emtp', self.project.configs[self.project.context['currentConfig']],maximumDepth = 0).toJSON()
    #### 有问题
    def getEdgeTopoPinNum(self,cid: str):
        """
        Descriptions
        ----------
            获取边的拓扑引脚编号。

        Parameters
        ----------
            cid (str): 元件ID。
            
        Returns
        -------
            str: 拓扑引脚编号。
        """
        j = self.project.getComponentByKey(cid)
        for st in range(2):
            
            sourcetarget=[j.source, j.target][st]
            if('cell' not in sourcetarget.keys()):
                continue
            c0 = sourcetarget['cell']
            c = '/'+c0
            if('port' not in sourcetarget.keys()):
                return self.getEdgeTopoPinNum(self.project,self.topo,c0)
            if(c in self.topo['components'].keys()):
                return self.topo['components'][c]['pins'][sourcetarget['port']]
            return '0'          
    #### 有问题  
    def deleteEdges(self):
        """
        Descriptions
        ----------
            删除网络中的边（shape=diagram-edges的元件），并设置引脚名称连接。
        """
        self.topoPinNameDict = {}
        for i,j in self.topo['components'].items():
            for p,k in j['pins'].items():
                if(k==''):
                    continue
                if(int(k) not in self.topoPinNameDict.keys()):
                    self.topoPinNameDict[int(k)] = []
                pname = self.project.getComponentByKey(i[1:]).pins[p]
                if(pname!='' and pname not in self.topoPinNameDict[int(k)]):
                    self.topoPinNameDict[int(k)].append(pname)
            for k in j['args'].values():
                if(str(k) in self.topo['mappings']['in'].keys()):
                    kk = self.topo['mappings']['in'][k]
                elif(str(k) in self.topo['mappings']['out'].keys()):
                    kk = self.topo['mappings']['out'][k]
                else:
                    continue
                if(int(kk) not in self.topoPinNameDict.keys()):
                    self.topoPinNameDict[int(kk)] = []
                    pname = self.project.getComponentByKey(i[1:]).pins[p]
                    if(pname!='' and pname not in self.topoPinNameDict[int(kk)]):
                        self.topoPinNameDict[int(kk)].append(pname)
        count = 0
        pinName0 = 'AutoAddPin'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_'
        for i,j in self.topoPinNameDict.items():
            if(j==[]):
                j.append(pinName0+str(count))
                count = count+1
        print('finish 1')
        topoPinEdgeDict = {}
        for i,j in self.project.getAllComponents().items():
            if(j.shape != 'diagram-edge'):
                continue
            p = self.getEdgeTopoPinNum(i)
            if(p not in topoPinEdgeDict.keys()):
                topoPinEdgeDict[p] = []
            if(i not in topoPinEdgeDict[p]):
                topoPinEdgeDict[p].append(i)
        for tped_ptr in topoPinEdgeDict.keys():
            for i in topoPinEdgeDict[tped_ptr]:
                j = self.project.getComponentByKey(i)
                if(j.shape != 'diagram-edge'):
                    continue
                for st in range(2):
                    sourcetarget=[j.source, j.target][st]
                    if(('cell' not in sourcetarget.keys()) or ('port' not in sourcetarget.keys())):
                        continue
                    if(self.project.getComponentByKey(sourcetarget['cell']).pins[sourcetarget['port']]==''):
                        self.project.getComponentByKey(sourcetarget['cell']).pins[sourcetarget['port']] = self.topoPinNameDict[int(tped_ptr)][0]
                self.project.revision.implements.diagram.cells.pop(i)

    def generateNetwork(self,vid : Optional[str] = None,nn : Optional[int] = None,chooseRIDList: Optional[List] = [],centerRID:Optional[List] = ['model/CloudPSS/_newBus_3p'],showlabel = False, show = True):
        """
        获取网络中指定节点的邻居节点子图。

        Args
            vid:  节点的ID。
            nn:   邻居的跳数。
            chooseRIDList:  一个 RID 列表，用于筛选邻居顶点。只有 RID 在这个列表中的邻居顶点才会被包含在子图中。
            centerRID: 指定中心元件的RID列表，用于确定边的连接方式。一个元件 RID (Resource Identifier) 的列表。RID 用于唯一标识元件的类型。centerRID 用于在构建网络时，确定边的连接方式。默认值是 ['model/CloudPSS/_newBus_3p']，这意味着默认情况下，母线（Bus）会被认为是网络的中心节点，其他元件会与母线建立连接。
            showlabel:  是否显示节点标签。
            show: 是否显示图形。
        """
        self.g = ig.Graph(directed = False)
        self.topoPinCompDict = {}
        for i,j in self.topo['components'].items():
            self.g.add_vertex(i,rid = j['definition'])
            for p,k in j['pins'].items():
                if(k==''):
                    continue
                if(int(k) not in self.topoPinCompDict.keys()):
                    self.topoPinCompDict[int(k)] = []
                if(i not in self.topoPinCompDict[int(k)]):
                    self.topoPinCompDict[int(k)].append(i)
            for k in j['args'].values():
                if(str(k) in self.topo['mappings']['in'].keys()):
                    kk = self.topo['mappings']['in'][k]
                elif(str(k) in self.topo['mappings']['out'].keys()):
                    kk = self.topo['mappings']['out'][k]
                else:
                    continue
                if(int(kk) not in self.topoPinCompDict.keys()):
                    self.topoPinCompDict[int(kk)] = []
                    if(i not in self.topoPinCompDict[int(kk)]):
                        self.topoPinCompDict[int(kk)].append(i)
        ess = []
        es=[]
        value = []
        for i,j in self.topoPinCompDict.items():
            if(len(j)<2):
                continue
            for centerrid in centerRID:
                if(centerrid in [self.topo['components'][k]['definition'] for k in j]):
                    index = [self.topo['components'][k]['definition'] for k in j].index(centerrid);
                    es = [(j[k],j[index]) for k in range(len(j)) if k != index]
                    break
            else:
                es = list(combinations(j, 2))
                
            ess = ess + es
            value = value + [i for k in range(len(es))]
        
        self.g.add_edges(ess,attributes= {'value':value})
        self.g.vs['label'] = [self.topo['components'][i]['label'] for i in self.g.vs['name']]
        self.g.vs['shape'] = 'circle-dot'
        self.g.vs['size'] = 2
        if vid is not None and nn is not None:
            a = self.getNetworkNeighbor(vid,nn,chooseRIDList,self.g)
            self.plotNetwork(a,showlabel, show)

    def getNetworkNeighbor(self,vid: str, nn: int, chooseRIDList: list = [], network: Optional[object] = None):
        """
        Descriptions
        ----------
            获取网络中指定节点的邻居节点子图。

        Parameters
        ----------
            vid (str): 节点的ID。
            nn (int): 邻居的跳数。
            chooseRIDList (list, optional): 一个 RID 列表，用于筛选邻居顶点。只有 RID 在这个列表中的邻居顶点才会被包含在子图中。默认为 `[]`。
            network (igraph.Graph, optional): 要分析的网络。默认为 `None`。
            
        Returns
        -------
            igraph.Graph: 邻居节点子图。
        """
        if not vid.startswith('/'):
                vid = '/' + vid
        if(network == None):
            network = self.g
        flag = 1
        if(vid in network.vs['name']):
            a = network.vs.find(vid) 
        else:
            flag=0
            a = network.vs.find(label=vid,rid = 'model/CloudPSS/_newBus_3p') 
        b = set([a])
        for k in range(nn):
            b0 = b.copy()
            for ii in b:
                c = set(ii.neighbors())
                b0 = b0.union(c)
            b = b0
        if(chooseRIDList!=[]):
            b = set(i for i in b if i['rid'] in chooseRIDList)
        sg = network.subgraph(b)
        # sg.vs['label'] = [self.topo['components'][i]['label'] for i in sg.vs['name']]
        # sg.vs['shape'] = 'circle-dot'
        # sg.vs['size'] = 2
        
        for ii in self.NetShapeConfig.keys():
            jj = self.NetShapeConfig[ii]
            bb = sg.vs.select(rid = ii);
            bb['color'] = jj['color']
            bb['shape'] = jj['shape']
            bb['size'] = jj['size']
            bb['font'] = 'SimHei'
            bb['label_size'] = jj['label_size']

        if(vid in network.vs['name']):
            a = sg.vs.find(vid) 
        else:
            flag=0
            a = sg.vs.find(label=vid,rid = 'model/CloudPSS/_newBus_3p') 
        a['color'] = 'chocolate'
        # plotNetwork(sg)
        return sg

    def plotNetwork(self, a: object, showlabel: bool = False, show: bool = True):
        """
        Descriptions
        ----------
            绘制网络图。

        Parameters
        ----------
            a (igraph.Graph): 要绘制的网络。
            showlabel (bool, optional): 是否显示节点标签。默认为 `False`。
            show (bool, optional): 是否显示图形。默认为 `True`。
        """
        labels=list(a.vs['label'])
        N=len(labels)
        E=[e.tuple for e in a.es]# list of edges
        layt = a.layout_kamada_kawai()
        Xn=[layt[k][0] for k in range(N)]
        Yn=[layt[k][1] for k in range(N)]
        Xe=[]
        Ye=[]
        for e in E:
            Xe+=[layt[e[0]][0],layt[e[1]][0], None]
            Ye+=[layt[e[0]][1],layt[e[1]][1], None]

        trace1=go.Scatter(x=Xe,
                    y=Ye,
                    mode='lines',
                    line= dict(color='rgb(210,210,210)', width=1),
                    hoverinfo='none'
                    )
        if(showlabel):
            mode = 'markers+text';
        else:
            mode = 'markers'
        trace2=go.Scatter(x=Xn,
                    y=Yn,
                    mode=mode,
                    name='ntw',
                    marker=dict(symbol=a.vs.get_attribute_values('shape'),
                                                size=[5 if i ==None else i for i in a.vs.get_attribute_values('size') ],
                                                color=['#6959CD' if i ==None else i for i in a.vs.get_attribute_values('color') ],
                                                line=dict(color='rgb(50,50,50)', width=0.5)
                                                ),
                    text=labels
                    )

        axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
                )

        width=800
        height=800
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

        data=[trace1, trace2]
        fig=go.Figure(data=data, layout=layout)
        if(show):
            fig.show()
        return fig

    def setCompLabelDict(self):
        """
        Descriptions
        ----------
            从元件label指向元件的字典生成。
            self.compLabelDict[label]={key1:Comp1,key2:Comp2}
        """
        self.compLabelDict = {}
        for key in self.project.getAllComponents().keys():
            comptemp = self.project.getComponentByKey(key)
            if('diagram-component' in comptemp.shape):
                label = comptemp.label;
                if(label not in self.compLabelDict.keys()):
                    self.compLabelDict[label] = {}
                self.compLabelDict[label][key] = comptemp;
            
    def setChannelPinDict(self):
        """
        Descriptions
        ----------
            从输出通道的pin指向通道元件的key的字典生成。
            self.channelPinDict[pin] = key;    
        """
        self.channelPinDict = {}
        for key in self.project.getComponentsByRid('model/CloudPSS/_newChannel').keys():
            comptemp = self.project.getComponentByKey(key)
            pin0 = comptemp.pins['0'];
            self.channelPinDict[str(pin0)] = key;    
    
    def addComp(self, compJson: Dict, id1: Optional[str] = None, canvas: Optional[str] = None, position: Optional[Dict] = None, args: Optional[Dict] = None, pins: Optional[Dict] = None, label: Optional[str] = None):
        """
        Descriptions
        ----------
            增加元件。

        Parameters
        ----------
            compJson (dict): 元件的JSON数据。
            id1 (str, optional): 元件的key。默认为 `None`。
            canvas (str, optional): 元件所在的图层（图纸）。默认为 `None`。
            position (dict, optional): 元件的位置。默认为 `None`。
            args (dict, optional): 元件的参数。默认为 `None`。
            pins (dict, optional): 元件的引脚。默认为 `None`。
            label (str, optional): 元件的标签。默认为 `None`。
        """
        
        compJson1 = copy.deepcopy(compJson)
        
        if id1!=None:
            compJson1['id'] = id1;
        if position!=None:
            compJson1['position'] = position;
        if canvas!=None:
            compJson1['canvas'] = canvas;
        if args!=None:
            compJson1['args'].update(args)
        if pins!=None:
            compJson1['pins'].update(pins)
        if label!=None:
            compJson1['label'] = label
#         print(compJson1)
        comp = Component(compJson1)
#         print(comp)
        self.project.revision.implements.diagram.cells[compJson1['id']]=comp
    
    def addxPos(self, canvas: str, compJson: Dict, MaxX: Optional[float] = None):
        """
        Descriptions
        ----------
            用于更新元件在 x 轴上的坐标，并检查是否需要换行。

        Parameters
        ----------
            canvas (str): 当前图纸的key。
            compJson (dict): 要添加的元件的JSON。
            MaxX (float, optional): 最大横坐标，超过则换行。默认为 `None`。
        """
        
        self.pos[canvas]['x'] = self.pos[canvas]['x'] + compJson['size']['width'];
        self.pos[canvas]['maxdy'] = max(self.pos[canvas]['maxdy'],compJson['size']['height'])
        if(MaxX != None and MaxX < self.pos[canvas]['x']):
            self.newLinePos(canvas)
        
    def newLinePos(self, canvas: str):
        """
        Descriptions
        ----------
            用于在图纸中执行换行操作，即将下一个元件的坐标设置为新行的起始位置。

        Parameters
        ----------
            canvas (str): 当前图纸的key。
        """
        self.pos[canvas]['x'] = self.pos[canvas]['x0']
        self.pos[canvas]['y'] = self.pos[canvas]['y'] + self.pos[canvas]['dy'] + self.pos[canvas]['maxdy']
        self.pos[canvas]['maxdy'] = 0;
        
    def addCompInCanvas(self, compJson: str, key: str, canvas: str, addN: Optional[bool] = None, addN_label: Optional[bool] = None, args: Optional[Dict] = None, pins: Optional[Dict] = None, label: Optional[str] = None, dX: int = 10, MaxX: Optional[float] = None):
        """
        Descriptions
        ----------
            在图纸中新增元件，包括添加元件、为元件key及标签添加后缀、更新坐标位置等功能。

        Parameters
        ----------
            compJson (str): 元件的定义。
            key (str): 元件的key前缀。
            canvas (str): 元件所在的画布。
            addN (bool, optional): 是否自动添加后缀。默认为 `None`。
            addN_label (bool, optional): 是否给标签添加后缀。默认为 `None`。
            args (dict, optional): 元件的参数。默认为 `None`。
            pins (dict, optional): 元件的引脚。默认为 `None`。
            label (str, optional): 元件的标签。默认为 `None`。
            dX (int, optional): 元件之间的x轴间距。默认为 `10`。
            MaxX (float, optional): 换行参数，图纸中一行元件的最大宽度。默认为 `None`。
    
        """
        if(addN == None):
            addN = True
        if(addN_label == None):
            addN_label = False
        posTemp = {k: v for k, v in self.pos[canvas].items() if k in ['x','y']}
        
        
        if(key not in self.compCount.keys()):
            self.compCount[key] = 0;
        if(addN):
            self.compCount[key]+=1;
            id1Temp = key+'_'+str(self.compCount[key]);
        else:
            id1Temp = key;
        if (label==None):
            label = id1Temp;
        if(addN_label):
            label = label + '_'+str(self.compCount[key]);
            
        argsCopy = args.copy()
        if('Name' in argsCopy.keys() and addN_label):
            argsCopy['Name'] = argsCopy['Name'] + '_' + str(self.compCount[key]);
        
        self.addComp(compJson,id1Temp,canvas, posTemp, argsCopy, pins, label)
        self.addxPos(canvas, compJson, MaxX)
        self.pos[canvas]['x'] = self.pos[canvas]['x'] + dX;

#         print([id1Temp,canvas, posTemp, argsCopy, pins, label])
        
        return id1Temp, label
    
    def createCanvas(self, canvas: str, name: str):
        """
        Descriptions
        ----------
            新增图纸。

        Parameters
        ----------
            canvas (str): 图纸的key。
            name (str): 图纸的名称。
        """
        self.project.revision.implements.diagram.canvas.append({'key': canvas, 'name': name})
        self.initCanvasPos(canvas)
    
    def screenCompByArg(self, compRID: str, conditions: list, compList: Optional[list] = None):
        """
        Descriptions
        ----------
            通过参数筛选元件。

        Parameters
        ----------
            compRID (str): 元件的RID。如'model/CloudPSS/_newShuntLC_3p'。
            conditions (list): 筛选条件列表。如[{'arg':'Vrms', 'Min': 20, 'Max':500, 'Set':None},{'arg':'Name', 'Min': None, 'Max':None, 'Set':['藏123','川321']}]。
            compList (list, optional): 可选，如果提供了 compList，则函数只会从这个列表中筛选元件。默认为 `None`。
        """
        
        comps = self.project.getComponentsByRid(compRID)
        screenedComps = {}
        if not isinstance(conditions,list):
            conditions = [conditions]
        
        if(compList!=None):
            screenedKeys = set(comps.keys()) & set(compList);
            comps = dict([(key, comps.get(key, None)) for key in screenedKeys])
            
        for k in comps.keys():
            flag = True;
            for c in conditions:
                if(c['arg']=='label'):
                    a = comps[k].label
                else:
                    a = comps[k].args[c['arg']]
                

                flag = True;
                Min = c['Min']
                Max = c['Max']
                Set = c['Set']
                if is_number(a) and ( Min == None or is_number(Min)) and (Max == None or is_number(Max)):
                    if(Min!=None and float(Min) > float(a)):
                        flag = False;
                        break
                    if(Max!=None and float(Max) < float(a)):
                        flag = False;  
                        break
                    if(Set!=None and (a not in Set)):
                        flag = False;
                        break
                else:
                    if(Min!=None and Min > a):
                        flag = False;
                        break
                    if(Max!=None and Max < a):
                        flag = False;  
                        break
                    if(Set!=None and (a not in Set)):
                        flag = False;
                        break

            if(flag):
                screenedComps[k] = comps[k];
        return screenedComps        

    def saveProject(self, newID: str, name: Optional[str] = None, desc: Optional[str] = None):
        """
        Descriptions
        ----------
            保存算例。

        Parameters
        ----------
            newID (str): 新的算例ID。
            name (str, optional): 算例的名称。默认为 `None`。
            desc (str, optional): 算例的描述。默认为 `None`。
    
        Examples
        --------
            desc = '此为自动暂稳分析程序生成的仿真算例。\\n' + ca.model.description 
            ca.saveProject(projectKey+'Auto_SA',sa.model.name+'_自动暂稳分析',desc = desc + sa.model.description )
        """
        if(name!=None):
            self.project.name = name;
        if(desc!=None):
            self.project.description = desc;
        return self.project.save(newID)
        # return 'model/'+self.config['username']+'/'+newID
