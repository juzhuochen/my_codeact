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

# 单次计算vsi
if __name__ == '__main__':
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODgxNCwidXNlcm5hbWUiOiJzbHhuZyIsInNjb3BlcyI6WyJtb2RlbDo5ODM2NyIsImZ1bmN0aW9uOjk4MzY3IiwiYXBwbGljYXRpb246MzI4MzEiXSwicm9sZXMiOlsic2x4bmciXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzczOTk1ODkzLCJub3RlIjoidG9vbHMiLCJpYXQiOjE3NDI4OTE4OTN9.vWGL5XKqgWX28ZvumCKpeeYWvIRl7wadNINK-tbN3pP5s0ilIbJpBXrJPefkKytntPr96Y2VVF7NBvkYbGcFvQ'
    apiURL = 'https://cloudpss.net/'
    username ='slxng' #用户名
    projectKey = 'IEEE39' #项目名称
    # projectKey = 'xibei-1025-tzd-new'
    # projectKey = 'xibei-20221027-TZD-cut'
    # projectKey = 'ieee9_ZsTest_1'
    # projectKey = 'xinan2025_withHVDC_noFault'
    cloudpss.setToken(tk)
    os.environ['CLOUDPSS_API_URL'] = apiURL
    
    with open('saSource.json', "r", encoding='utf-8') as f:
        compLib = json.load(f)
        
    
    print('正在进行初始化...')
    sa = SA.S_S_SyncComp()
    sa.setConfig(tk,apiURL,username,projectKey);
    sa.setInitialConditions()
    sa.createSACanvas()
    sa.createSSSCACanvas()
    # sa.createJob('powerFlow')
    # sa.createConfig()
    
    # 以下内容适合没有潮流结果的情形
    
    # print('正在计算初始潮流...')
    
    # sa.runProject(jobName='CA潮流计算方案', configName='CA参数方案', showLogs = True)
    # path = 'results/'+ projectKey
    # folder = os.path.exists(path)
    # if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
    #     os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
        
    # pfresultID = sa.runner.id;
    # pfresult = sa.runner.result
    
    # 以下内容适合有潮流结果的情形
    
    # pfresultID = 'ecb63ec5-f424-402c-8d68-f9769ef2996c'
    # r = cjob.fetch(pfresultID)
    # pfresult = nest_asyncio.asyncio.run(r).result
    
    # 设置VSI计算
    print('进行VSI计算的相关设置...')
    
    busLabels1 =['newBus_3p-9',
                 'newBus_3p-8',
                 'newBus_3p-7',
                 'newBus_3p-26',
                 'newBus_3p-30']
                
                
    busLabelArea = [busLabels1]
    busLabels = []
    busLabelArea0 = []
    for i in busLabelArea:
        icopy = i.copy()
        for j in i:
            if(j not in sa.compLabelDict.keys()):
                icopy.remove(j)

        busLabels = busLabels + icopy;
        busLabelArea0.append(icopy)
    print(busLabelArea)
    
#     busLabels = busLabelsRikaze + busLabelsNaqu + busLabelsLasa + busLabelsLinzhi + busLabelsShannan;
    
    busKeys = []
    for i in busLabels:
        for j in sa.compLabelDict[i].keys():
            if(sa.project.getComponentByKey(j).definition=='model/CloudPSS/_newBus_3p'):

                busKeys.append(j)
                break
    # busKeys1 = []
    # for i in range(len(busKeys)):
    #     if(sa.project.getComponentByKey(busKeys[i]).definition=='model/CloudPSS/_newBus_3p'):
    #         busKeys1.append(busKeys[i])
    # busKeys = busKeys1
        

#     measureBusLabels = ['藏德燃220-1','藏德吉220-2','藏雄牵220','藏乌牵220','藏露牵220','藏妥牵220','藏那牵220','藏嘎牵220','藏藏安220-1','藏藏那220-1',
#                         '藏扎牵220','藏联牵220','藏托牵220','藏安牵220','藏乌玛220-1']
    
    Ts  = 8
    dT  = 1.5
    ddT = 0.5

    busKeys = None
    busLabels = None
    
    VSIQKeys = sa.addVSIQSource(busKeys)
    # VSIQKeys = sa.addVSIQSource(busKeys, V = 220, S = 100, Ts = Ts, dT = dT, ddT = ddT)
    
    jobName = 'SA_电磁暂态仿真'
    timeend = 10;
    sa.createJob('emtps', name = jobName,args = {'begin_time': 0,'end_time': 30,'step_time': 0.00005})
    # sa.createJob('emtps', name = jobName,args = {'begin_time': 0,'end_time': 30,'step_time': 0.00005})

    sa.createJob('powerFlow', name = 'SA_潮流计算')
    sa.createConfig(name = 'SA_参数方案')

    voltageMeasureK, dQMeasureK = sa.addVSIMeasure('SA_电磁暂态仿真',VSIQKeys, VMin = 0.6, VMax = 300)
    print(voltageMeasureK)
    print(voltageMeasureK)
    # voltageMeasureK, dQMeasureK = sa.addVSIMeasure('SA_电磁暂态仿真',VSIQKeys, VMin = 0.6, VMax = 300,freq = 100,Nbus = len(busKeys), dT = dT, Ts = Ts)
    # 开始仿真
    print('开始仿真...')
    sa.runProject('SA_电磁暂态仿真', 'SA_参数方案')
    print('仿真完成，正在存储数据...')
    path = 'results/'+ projectKey
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
        
    # Result.dump(sa.runner.result,path+'/VSIresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')
    VSIresult = sa.runner.result
    
    VSIresultDict = sa.calculateVSI('SA_电磁暂态仿真', voltageMeasureK, dQMeasureK, busLabels);
    
    fname = 'results/'+ projectKey + '/VSIresultDict_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.json'
    with open(fname, "w", encoding='utf-8') as f:
        f.write(json.dumps(VSIresultDict, indent=4))
    # 绘制VSI折线图
    fig = go.Figure()
    k=1
    # Add traces
    ckeytemp = VSIresult.getPlotChannelNames(k)
    # for pk in ckeytemp[1500:1510]:
    for pk in ckeytemp:
        if(True):
        # if('资阳' in pk):
            x = VSIresult.getPlotChannelData(k,pk)['x']
            y = VSIresult.getPlotChannelData(k,pk)['y']
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
    fig.show()

    # 绘制VSI柱状图

    VSIresult = VSIresultDict
    busNames = [i for i in VSIresult["VSIi"].keys()]
    busVSIis = [VSIresult["VSIi"][i] for i in busNames]

    trace = go.Bar(x = busNames,  y=busVSIis)
    layout_basic = go.Layout(
                title = 'VSIi',
    #             xaxis = go.XAxis(domain = [0,1])
        )
    fig = go.Figure(data = trace)
    fig.show()

