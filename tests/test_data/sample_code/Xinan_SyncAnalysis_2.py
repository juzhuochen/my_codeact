# import StabilityAnalysis as SA
import S_S_SyncComp as SA
# import ReadSOT as rs

import cloudpss
import os
import time
import json
import re
import numpy as np
import numpy.linalg as LA
from IPython.display import display, HTML
# %matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from scipy import interpolate

import pandas as pd

import tkinter
import tkinter.filedialog

import math

from IPython.display import HTML
from html import unescape

import random
import json
import copy
from cloudpss.model.implements.component import Component
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
from cloudpss.model.revision import ModelRevision
from cloudpss.model.model import Model


from scipy import optimize

from cloudpss.job.job import Job as cjob
import nest_asyncio
nest_asyncio.apply()

## 用于交流断面最大受电能力分析
if __name__ == '__main__':
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODgxNCwidXNlcm5hbWUiOiJzbHhuZyIsInNjb3BlcyI6WyJtb2RlbDo5ODM2NyIsImZ1bmN0aW9uOjk4MzY3IiwiYXBwbGljYXRpb246MzI4MzEiXSwicm9sZXMiOlsic2x4bmciXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzczOTk1ODkzLCJub3RlIjoidG9vbHMiLCJpYXQiOjE3NDI4OTE4OTN9.vWGL5XKqgWX28ZvumCKpeeYWvIRl7wadNINK-tbN3pP5s0ilIbJpBXrJPefkKytntPr96Y2VVF7NBvkYbGcFvQ'
    apiURL = 'https://cloudpss.net/'
    username ='slxng' #用户名
    projectKey = 'IEEE039_newtest' #项目名称

    with open('saSource.json', "r", encoding='utf-8') as f:
        compLib = json.load(f)

    sa = SA.S_S_SyncComp()
    sa.setConfig(tk,apiURL,username,projectKey);
    sa.setInitialConditions()
    sa.createSACanvas()
    # N_2LineLabel1 = ['藏年楚-藏色麦Ι线','藏年楚-藏色麦ΙΙ线'];
    # N_2LineLabel1 = ['TLine_3p-22','TLine_3p-20'] #许木-墨竹
    # N_2LineLabel1 = ['藏那曲500-藏乌玛塘II线','藏那曲500-藏乌玛塘I线']

    # N_2LineLabel1 = ['藏多林-藏雅上II线','藏多林-藏雅上I线']
    # N_2LineLabel1 = ['藏曲布雄220-1_藏多林220','藏曲布雄220-2_藏多林220-1']
    # N_2LineLabel1 = ['AC900056','藏甲孜110-2_藏多林110-2_2'] #多林-甲孜，实际为多林-日喀则

    # N_2LineLabel1 = ['藏那曲11-藏黑河11','藏那曲12-藏黑河12']
    # N_2LineLabel1 = ['藏那曲11-藏德开11','藏那曲12-藏德开11']
    
    # N_2LineLabel1 = ['藏多林--藏查务I线','藏多林--藏查务II线']

    # N_2LineLabel1 = ['藏多林--藏查务I线','藏多林--藏查务II线']
    
    # N_2LineKey1 = []
    # for i in N_2LineLabel1:
    #     N_2LineKey1.append([j for j in sa.compLabelDict[i].keys()][0])
    
    N_1LineLabel1 = 'TLine_3p-22';
    N_1LineKey1 = [j for j in sa.compLabelDict[N_1LineLabel1].keys()][0]

    # sa.setN_2_GroundFault(N_2LineKey1[0], N_2LineKey1[1], 0, 4, 4.09, 7,OtherFaultParas = {'chg':'0.05'})
    sa.setN_1_GroundFault(N_1LineKey1, 0, 4, 4.09, 7)


    # 添加调相机
    # busLabels = ['藏乃琼220-1'];
    # busKeys = []
    # for i in busLabels:
    #     busKeys.append([j for j in sa.compLabelDict[i].keys()][0])
        
    # S0 = 20;#各个调相机的初始容量
    # Q = [S0 for i in range(len(busLabels))]
    # Syncids = []
    # for bPtr in range(len(busKeys)):
    #     ids = sa.addSyncComp(busKeys[bPtr], pfresult, syncArgs = {"Smva": str(Q[bPtr])})
    #     Syncids.append(ids[0])
    #     [Syncid1,Busid1,Transid1,AVRid1,Gainid1]


    sa.createJob('emtps', name = 'SA_电磁暂态仿真', args = {'begin_time': 0,'end_time': 10,'step_time': 0.00002})
    sa.createJob('powerFlow', name = 'SA_潮流计算')
    sa.createConfig(name = 'SA_参数方案')
    
    sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 220, freq = 200, PlotName = '220kV以上电压曲线')
    sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 110, VMax = 120, freq = 200, PlotName = '110kV电压曲线')
    sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 0.01, VMax = 10, freq = 200, PlotName = '10kV以下电压曲线')
    sa.runProject(jobName='电磁暂态仿真方案 1', configName='SA_参数方案')
    # 林芝负荷大小

    # sa.project.getComponentByKey('canvas_0_440').args['p'] = 1
    # sa.project.getComponentByKey('canvas_0_440').args['q'] = 0

    # sa.project.getComponentByKey('57fcbbab-abf7-48df-9bb9-2ca82c17f5fe').args['P0'] = 50
    # sa.project.getComponentByKey('57fcbbab-abf7-48df-9bb9-2ca82c17f5fe').args['q'] = -20

    # sa.project.getModelJob('SA_潮流计算')[0]['args']['url'] = 'https://internal.cloudpss.net/graphql';
    # sa.runProject(jobName='SA_潮流计算', configName='SA_参数方案',apiUrl = 'https://orange.local.cloudpss.net/')
    # sa.runProject(jobName='SA_潮流计算', configName='SA_参数方案')

    # index = sa.runner.result.getBranches()[0]['data']['columns'][0]['data'].index('canvas_0_105');
    # p = sa.runner.result.getBranches()[0]['data']['columns'][2]['data'][index]
    # q = sa.runner.result.getBranches()[0]['data']['columns'][3]['data'][index]
    # display([2 * p,2 * q])
    # sa.displayPFResult()
    # print('正在回写潮流数据...')
    # sa.runner.result.powerFlowModify(sa.project)
    # print(sa.runner.id)

    # sa.createSSSCACanvas()
    
    # pfresult = sa.runner.result;
    # busLabels = ['newBus_3p-8','newBus_3p-7'];
    # busKeys = []
    # for i in busLabels:
    #     busKeys.append([j for j in sa.compLabelDict[i].keys()][0])
        
    # S0 = 1;#各个调相机的初始容量
    # Q = [200,50]
    # Syncids = []
    # for bPtr in range(len(busKeys)):
    #     ids = sa.addSyncComp(busKeys[bPtr], pfresult, syncArgs = {"Smva": str(Q[bPtr])})
    #     Syncids.append(ids[0])

    # # sa.saveProject()
    # # sa.project.getModelJob('SA_电磁暂态仿真')[0]['args']['url'] = 'https://internal.cloudpss.net/graphql';
    # sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案')

    # sa.plotResult(k=0)

    # path = 'results/'+ projectKey
    # folder = os.path.exists(path)
    # if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
    #     os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

    # # Result.dump(sa.runner.result,path+'/SAresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')


