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
# import nest_asyncio
# nest_asyncio.apply()

## 计算单次DUDV

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
    
    sa.createJob('powerFlow', name = 'SA_潮流计算')
    sa.createConfig(name = 'SA_参数方案')
    
    path = 'results/'+ projectKey + '/SSresults_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'/'
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

    
    # 设置故障
    # sa.project.getComponentByKey('component_new_fault_resistor_3_p_1').args['ft'] = '7';
    sa.setN_1_GroundFault('canvas_0_134')
    # sa.setN_1_GroundFault('canvas_0_134',0,4,4.1,7)
    # sa.setN_2_GroundFault('comp_TranssmissionLineRouter_705','comp_TranssmissionLineRouter_706',1,4,4.1,7)
    # 设置仿真作业及其输出通道信息
    jobName = 'SA_电磁暂态仿真'
    timeend = 10;
    sa.createJob('emtps', name = jobName)
    keys = []
    # for ii,jj in sa.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
    #     if('川' in jj.label[:1]):
    #         keys.append(ii)
    # measuredBus = sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 0.5, VMax = 1100, freq = 100, PlotName = '220kV以上电压曲线',Keys=keys)
    measuredBus = sa.addVoltageMeasures('SA_电磁暂态仿真', VMin =220, freq = 100, PlotName = '220kV以上电压曲线')
    # measuredBus = sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 0.5, VMax = 1100, freq = 100, PlotName = '220kV以上电压曲线')

    # sa.addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'P', [], plotName = '储能有功功率曲线', freq = 200)
    # sa.addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'Q', [], plotName = '储能无功功率曲线', freq = 200)
    
#     RVTemp = sa.getRevision(file = None):获取以及保存算例的revision
#     sa.loadRevision(revision = RVTemp):载入revision

    # 开始更新潮流
    # print('正在进行潮流初始化...')
    # sa.runProject('SA_潮流计算', 'SA_参数方案')
    # print('正在回写潮流数据...')
    # sa.runner.result.powerFlowModify(sa.project)

    print('开始仿真...')
    sa.runProject('SA_电磁暂态仿真', 'SA_参数方案')
    print('仿真完成，正在存储数据...')
    
    
    # Result.dump(sa.runner.result,path+'/SSresult_'+ str(0) +'.cjob')
    SSresultID = sa.runner.id
    print(SSresultID)
    SSresult = sa.runner.result
    print('数据存储完成...')
        
    # 电压裕度判断条件
    # judgement = [[0,0.5,0.2,1.2],[0.5,1,0.2,1.15],[1,2,0.391,1.1],[2,999,0.9,1.1]]
    # # judgement = [[0,0.5,0.2,1.1],[0.5,1,0.2,1.1],[1,2,0.391,1.1],[2,999,0.9,1.1]]
    # judgement = [[0.5,3,0.8,1.2],[3,999,0.95,1.05]]

    dVUj,dVLj,ValidNumI = sa.calculateDV('SA_电磁暂态仿真', 0, result = SSresult, Ts = 4, dT0 = 0.5, VminR = 0.5, VmaxR = 1.5)
    
    mm= [i for i in range(len(dVUj)) if dVUj[i]<0]
    nn= [i for i in range(len(dVLj)) if dVLj[i]<0]
    print(mm)
    print(nn)
    
    fig = go.Figure()
    k=0
    # Add traces
    ckeytemp = SSresult.getPlotChannelNames(k)
    rr=SSresult
    m = mm
    for pk in [ckeytemp[i] for i in m]:
    # for pk in ckeytemp:
        # if('北塔' not in pk):
        #     continue
        x = rr.getPlotChannelData(k,pk)['x']
        y = rr.getPlotChannelData(k,pk)['y']
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
    fig.show()
