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


# ## 用于储能设备选址定容
if __name__ == '__main__':
    
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODgxNCwidXNlcm5hbWUiOiJzbHhuZyIsInNjb3BlcyI6WyJtb2RlbDo5ODM2NyIsImZ1bmN0aW9uOjk4MzY3IiwiYXBwbGljYXRpb246MzI4MzEiXSwicm9sZXMiOlsic2x4bmciXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzczOTk1ODkzLCJub3RlIjoidG9vbHMiLCJpYXQiOjE3NDI4OTE4OTN9.vWGL5XKqgWX28ZvumCKpeeYWvIRl7wadNINK-tbN3pP5s0ilIbJpBXrJPefkKytntPr96Y2VVF7NBvkYbGcFvQ'
    apiURL = 'https://cloudpss.net/'
    username ='slxng' #用户名
    projectKey = 'IEEE39' #项目名称
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
    
    
    # 以下内容适合有VSIij信息的情形
    print('需要手动读取VSIij结果...')
#     file_path = tkinter.filedialog.askopenfilename(title=u'选择VSIresult文件', initialdir=(os.path.expanduser(default_dir)))
    file_path = 'results\\IEEE39\\VSIresultDict_2025_07_02_15_36_34.json'
    # file_path = '.\\results\\xinan2025_withHVDC_noFault\\VSIresultDict_2024_01_03_14_04_21.json'
    with open(file_path, "r", encoding='utf-8') as f:
        VSIresultDict = json.load(f)
        
    VSIi = VSIresultDict['VSIi']
    VSIij = VSIresultDict['VSIij']
    # root.destroy()
    
    # 设置调相机安装地点
    print('进行选址定容计算的相关设置...')
    busLabels1=['newBus_3p-9','newBus_3p-8','newBus_3p-7','newBus_3p-26']
   
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
    print(busLabelArea0)

    busKeys = []
    for i in busLabels:
        for j in sa.compLabelDict[i].keys():
            if(sa.project.getComponentByKey(j).definition=='model/CloudPSS/_newBus_3p'):

                busKeys.append(j)
                break

    # 开始添加储能设备
    S0 = 10;#各个调相机的初始容量
    Q = [S0 for i in range(len(busLabels))]

    

    Syncids = [] # 调相机id列表
    Tranids = [] # 

    pfresultID = 'e794f071-2c97-4b4d-b549-ba3e7298c34c'
    r = cjob.fetch(pfresultID)
    # pfresult = nest_asyncio.asyncio.run(r).result
    while not r.status():
        time.sleep(2)
    pfresult = r.result

    for bPtr in range(len(busKeys)):


        K = 30 # 调相机AVR增益
        KA = 14.2 # 调相机AVR时间常数
        if(bPtr == 0):
            K = 2
            KA = 10
        ids = sa.addSyncComp(busKeys[bPtr], pfresult, syncArgs = {"Smva": str(Q[bPtr])}, AVRArgs = {"K":str(K),"KA":str(KA)})
        Syncids.append(ids[0])
        Tranids.append(ids[2])
        #[Syncid1,Busid1,Transid1,AVRid1,Gainid1]

    judgement = [[0,0.5,0.2,1.2],[0.5,1,0.2,1.15],[1,2,0.391,1.1],[2,999,0.9,1.1]]
    judgement = [[0,0.5,0.2,1.1],[0.5,1,0.2,1.1],[1,2,0.391,1.1],[2,999,0.9,1.1]]
    judgement = [[0.5,2,0.85,1.15],[2,999,0.9,1.1]]
    judgement = [[0.5,3,0.8,1.2],[3,999,0.95,1.05]]
    judgement = [[0.5,3,0.75,1.25],[3,999,0.9,1.1]]
    
    # 设置故障

    sa.setN_2_GroundFault('canvas_0_134','canvas_0_126',1,4,4.1,7)

    # 设置仿真作业及其输出通道信息
    jobName = 'SA_电磁暂态仿真'
    timeend = 10;
    sa.createJob('emtps', name = jobName, args = {'begin_time': 0,'end_time': timeend,'step_time': 0.00005})
    
    keys = []
    measuredBus = sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 0.6, freq = 100, PlotName = '220kV以上电压曲线')

    # sa.addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'P', [], plotName = '调相机有功功率曲线', freq = 200)
    # sa.addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'Q', [], plotName = '调相机无功功率曲线', freq = 200)
    
    sa.addComponentOutputMeasures('SA_电磁暂态仿真', 'model/CloudPSS/SyncGeneratorRouter', 'QT_o', [], compList = Syncids,plotName = '调相机无功功率曲线', freq = 200)

#     RVTemp = sa.getRevision(file = None):获取以及保存算例的revision
#     sa.loadRevision(revision = RVTemp):载入revision

    # 开始更新潮流
    # print('正在进行潮流初始化...')
    # sa.runProject('SA_潮流计算', 'SA_参数方案')
    # print('正在回写潮流数据...')
    # sa.runner.result.powerFlowModify(sa.project)
    # from PSAServer import iterativeSolutionQ
    # iterativeSolutionQ(sa, busLabels, VSIresultDict,Syncids, Tranids,  Q, 0.2,judgement)

    
    # 开始迭代求解
    Speed = 0.2; # 迭代加速比
    Qhistory = {}
    QDict = {}
    for i in range(len(busLabels)):
        QDict[busLabels[i]] = Q[i]
    Qhistory[0] = QDict
    taskIDs = []
    for Iter in range(20):
    # for Iter in range(1):
        # 开始仿真
        print('开始仿真...')
        sa.runProject('SA_电磁暂态仿真', 'SA_参数方案')
        print('仿真完成，正在存储数据...')
        
        taskIDs.append(sa.runner.id)
        SSresult = sa.runner.result
        print('数据存储完成...')
        
        
        DVResult = sa.calculateDV('SA_电磁暂态仿真', 0, result = SSresult, Ts = 4, dT0 = 0.5, judge=judgement, VminR = 0.5, VmaxR = 1.5)
        dVUj = DVResult['电压上限裕度']  # 电压上限裕度
        dVLj= DVResult['电压下限裕度']  # 电压下限裕度
        ValidNumI = DVResult['有效通道索引']  # 有效母线索引
        if(Iter==0):
            ValidNum = ValidNumI
        
        # 算线性规划
        channels = SSresult.getPlotChannelNames(0)
#         channels = busLabels
        
#         SSNames = [k for k in VSIi.keys()]
        SSNames = busLabels
        c = [1 for i in range(len(SSNames))]
        A = []
        b = []
        bounds = [(-Q[i]+0.1,-Q[i]+800) for i in range(len(SSNames))]
        for i in ValidNum:
            busName = channels[i]
            Ai = []
            if(busName not in VSIij[SSNames[0]].keys()):
                continue
            for k in SSNames:
                Ai.append(-VSIij[k][busName] / Speed)
            A.append(Ai)
#             b.append(dVLj[i])
            b.append(min(dVLj[i],dVUj[i]))

#             Ai = []
#             for k in SSNames:
#                 Ai.append(VSIij[k][busName])
#             A.append(Ai)
#             b.append(dVUj[i])

        res = optimize.linprog(c, A, b, bounds=bounds)
        Q = (np.array(Q) + res.x).tolist()
        
        for i in range(len(Q)):
            # sa.project.getComponentByKey(Syncids[i]).args['Num'] = str(Q[i]/0.2)
            sa.project.getComponentByKey(Syncids[i]).args['Smva'] = str(Q[i])
            sa.project.getComponentByKey(Tranids[i]).args['Tmva'] = str(Q[i])
            
        print('Iter:'+str(Iter)) # 迭代次数
        print('Q:'+str(Q))  # 调相机容量
        print('DQ:'+str(res.x.tolist())) #  调相机容量调整量
        print(res.message)
        QDict = {}
        for i in range(len(busLabels)):
            QDict[busLabels[i]] = Q[i]
        Qhistory[Iter+1] = QDict
        
        # print('正在保存算例备份...')
        # fnameCproj = path+'/SSTempFile_'+ str(Iter) +'.cproj'
        # sa.project.dump(sa.project, fnameCproj)
        # fnameQ = path+'/SS_QDict_'+'.json'
        # with open(fnameQ, "w", encoding='utf-8') as f:
        #     f.write(json.dumps(Qhistory, indent=4))
        # print('算例备份保存为'+fnameCproj+', Q迭代过程保存为：'+fnameQ)
        
        if(max(abs(res.x)) < 0.5):
            print('迭代已经收敛，结束仿真计算。总迭代次数：Q = '+str(Iter+1))
            print('TaskID:')
            print(taskIDs)
            # Q = [[Qhistory[-1]['QDicts'][j][i] for i in Qhistory[-1]['busLabels']] for j in range(6)]
            # V = [[Qhistory[-1]['VDicts'][j][i] for i in Qhistory[-1]['busLabels']] for j in range(6)]
            # with open('results/'+ projectKey + '/QInit10.txt', "w", encoding='utf-8') as f:
            #     for i in Q: #对于双层列表中的数据
            #         i = str(list(i)).strip('[').strip(']').replace(',','').replace('\'','')+'\n' #将其中每一个列表规范化成字符串
            #         f.write(i) #写入文件
            #     f.close()

            # with open('results/'+ projectKey + '/VInit10.txt', "w", encoding='utf-8') as f:
            #     for i in V: #对于双层列表中的数据
            #         i = str(list(i)).strip('[').strip(']').replace(',','').replace('\'','')+'\n' #将其中每一个列表规范化成字符串
            #         f.write(i) #写入文件
            #     f.close()

            break

        mm= [i for i in range(len(dVUj)) if dVUj[i]<0]
        nn= [i for i in range(len(dVLj)) if dVLj[i]<0]
        print(mm)
        print(nn)
        m = set(mm) | set(nn)
        
        fig = go.Figure()
        k=0
        # Add traces
        ckeytemp = SSresult.getPlotChannelNames(k)
        rr=SSresult

        print(f"电压异常母线: {[ckeytemp[i] for i in m]}")
        for pk in [ckeytemp[i] for i in m]:

            x = rr.getPlotChannelData(k,pk)['x']
            y = rr.getPlotChannelData(k,pk)['y']
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
        fig.show()