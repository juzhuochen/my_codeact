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


## 用于粒子群定容SVC

if __name__ == '__main__':
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODgxNCwidXNlcm5hbWUiOiJzbHhuZyIsInNjb3BlcyI6WyJtb2RlbDo5ODM2NyIsImZ1bmN0aW9uOjk4MzY3IiwiYXBwbGljYXRpb246MzI4MzEiXSwicm9sZXMiOlsic2x4bmciXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzczOTk1ODkzLCJub3RlIjoidG9vbHMiLCJpYXQiOjE3NDI4OTE4OTN9.vWGL5XKqgWX28ZvumCKpeeYWvIRl7wadNINK-tbN3pP5s0ilIbJpBXrJPefkKytntPr96Y2VVF7NBvkYbGcFvQ'
    apiURL = 'https://cloudpss.net/'
    username ='slxng' #用户名
    projectKey = 'IEEE39' #项目名称

    print('正在进行初始化...')
    with open('saSource.json', "r", encoding='utf-8') as f:
        compLib = json.load(f)

    sa = SA.S_S_SyncComp()
    sa.setConfig(tk,apiURL,username,projectKey);
    sa.setInitialConditions()
    sa.createSACanvas()
    # N_2LineLabel1 = ['藏年楚-藏色麦Ι线','藏年楚-藏色麦ΙΙ线'];
    N_2LineLabel1 = ['TLine_3p-22','TLine_3p-20'] #许木-墨竹
    # N_2LineLabel1 = ['藏那曲500-藏乌玛塘II线','藏那曲500-藏乌玛塘I线']
    
    N_2LineKey1 = []
    for i in N_2LineLabel1:
        N_2LineKey1.append([j for j in sa.compLabelDict[i].keys()][0])
    


    sa.setN_2_GroundFault(N_2LineKey1[0], N_2LineKey1[1], 0, 1.5, 1.56, 7, OtherFaultParas = {'chg':'1'})

    sa.createSACanvas()
    sa.createSSSCACanvas()
    
    sa.createJob('powerFlow', name = 'SA_潮流计算')
    sa.createConfig(name = 'SA_参数方案')
    
    path = 'results/'+ projectKey + '/SSresults_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'/'
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

    sa.createJob('emtp', name = 'SA_电磁暂态仿真', args = {'begin_time': 0,'end_time': 6,'step_time': 0.00002})
        # 'task_queue': 'taskManager_turbo1','solver_option': 7,'n_cpu': 16})
    sa.createJob('powerFlow', name = 'SA_潮流计算')
    sa.createConfig(name = 'SA_参数方案')
    
    sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 220, freq = 200, PlotName = '220kV以上电压曲线')
    sa.addVoltageMeasures('SA_电磁暂态仿真', VMin = 110, VMax = 120, freq = 200, PlotName = '110kV电压曲线')

    
     # 林芝负荷大小

    # sa.project.getComponentByKey('component_new_exp_load_3_p_1').args['p'] = 1
    # sa.project.getComponentByKey('component_new_exp_load_3_p_1').args['q'] = 0

    # sa.project.getComponentByKey('57fcbbab-abf7-48df-9bb9-2ca82c17f5fe').args['P0'] = 100
    # sa.project.getComponentByKey('57fcbbab-abf7-48df-9bb9-2ca82c17f5fe').args['q'] = 0



    # sa.runProject(jobName='SA_潮流计算', configName='SA_参数方案')
    # # index = sa.runner.result.getBranches()[0]['data']['columns'][0]['data'].index('63ff5639-f1e7-4511-ae56-1e0d2abd9d48');
    # # p = sa.runner.result.getBranches()[0]['data']['columns'][2]['data'][index]
    # # q = sa.runner.result.getBranches()[0]['data']['columns'][3]['data'][index]

    # # display([2 * p,2 * q])

    # path = 'results/'+ projectKey
    # folder = os.path.exists(path)
    # if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
    #     os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
        
    # Result.dump(sa.runner.result,path+'/pfresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')
    # pfresult = sa.runner.result
    
    # 以下内容适合有潮流结果的情形
    
    # print('需要手动读取潮流结果...')
    # root = tkinter.Tk()    # 创建一个Tkinter.Tk()实例
    # # root.withdraw()       # 将Tkinter.Tk()实例隐藏
    # default_dir = r"文件路径"
    # file_path = tkinter.filedialog.askopenfilename(title=u'选择潮流文件', initialdir=(os.path.expanduser(default_dir)))
    # # file_path = 'results/2025Tibet_WinterHigh_Nofault/pfresult2021_10_14_12_02_22'
    # root.destroy()
    # pfresult = PowerFlowResult.load(file_path)


    # print('正在回写潮流数据...')
    # pfresult.powerFlowModify(sa.project)


    # 设置SVC安装地点
    print('进行选址定容计算的相关设置...')
    # busLabelsRikaze = ['藏曲布雄220-1','藏多林220']
    # busLabelsNaqu = ['藏德吉220-2','藏藏那220-1','藏安牵220']
    # busLabelsLasa = ['藏西城220-1','藏东城220-1','藏旁多220-1','藏曲哥220-1','藏乃琼220-1']
    # busLabelsLinzhi = [ '藏老虎嘴220-1','藏朗县220-1','藏卧龙220-1','藏巴宜220']
    # busLabelsShannan = ['藏昌珠220-1','藏吉雄220-1']

    busLabelArea = [['newBus_3p-9' , 'newBus_3p-8' ], ['newBus_3p-35' , 'newBus_3p-32'] , ['newBus_3p-37']]
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
        busKeys.append([j for j in sa.compLabelDict[i].keys()][0])



    # busLabels = ['藏乃琼220-1','藏西城220-1'];
    # busKeys = []
    # for i in busLabels:
    #     busKeys.append([j for j in sa.compLabelDict[i].keys()][0])


    # 粒子群算法参数设置
    PSOConfig = {"C1":2,
                "C2":2,
                "W":0.6,
                "dim":len(busKeys),
                "size":1,
                "iter_num":10,
                "Qmax":200,
                "Qmin":0.1,
                "vmax":30,
                "SI0":0.05,
                "W0":99999}

    # 初始值
    Qinit = []
    with open('results/'+ projectKey +'/QInit10.txt', "r", encoding='utf-8') as f:
        string = f.read().strip()
        for i in string.split("\n"):
            QinitTemp = [];
            for j in i.split(" "):
                    QinitTemp.append(float(j));
            Qinit.append(QinitTemp)

    # Q = np.array(Qinit) * 20;
    Q = np.array(Qinit);

    Vinit = []
    with open('results/'+ projectKey +'/VInit10.txt', "r", encoding='utf-8') as f:
        string = f.read().strip()
        for i in string.split("\n"):
            VinitTemp = [];
            for j in i.split(" "):
                    VinitTemp.append(float(j));
            Vinit.append(VinitTemp)

    # V = np.array(Vinit) * PSOConfig["vmax"];
    V = np.array(Vinit)
    
    Syncids = []
    for bPtr in range(len(busKeys)):
        # ids = sa.addSyncComp(busKeys[bPtr], pfresult, syncArgs = {"Smva": str(Q[bPtr])})
        ids = sa.addSVC(busKeys[bPtr], S = -Q[0][bPtr], Ts = 1.56, Te = 999)
        Syncids.append(ids[0])

    for j in range(PSOConfig["size"]):
        for i in range(len(busLabels)):
            Q[j][i] = 0.1;
            V[j][i] = random.random() * PSOConfig["vmax"];

    QDicts = [] #[{"藏许木-1":20,xxxx:xxx},{"藏许木-1":20,xxxx:xxx}]
    VDicts = []
    for j in range(PSOConfig["size"]):
        QDict = {}
        VDict = {}
        for i in range(len(busLabels)):
            QDict[busLabels[i]] = Q[j][i]
            VDict[busLabels[i]] = V[j][i]
        QDicts.append(QDict);
        VDicts.append(VDict);
    Qhistory = [] #所有历史量[{"QDicts":QDicts,"VDicts":VDicts,"F":F, "QpBest":QpBest, "pBest":pBest, "QgBest":QgBest, gBest:gBest,"busLabels":busLabels}]
    QpBest = copy.deepcopy(QDicts) # [{"藏许木-1":20,xxxx:xxx},{"藏山南-1":20,xxxx:xxx}] #粒子中最优
    pBest = [PSOConfig["W0"] for i in range(PSOConfig["size"])] #[20,50]
    QgBest = {} # {"藏许木-1":20,xxxx:xxx}
    gBest = 9999999;

    #已有Qhistory:
    # QDicts = copy.deepcopy(Qhistory[-1]['QDicts'])
    # VDicts = copy.deepcopy(Qhistory[-1]['VDicts'])
    # QpBest = copy.deepcopy(Qhistory[-1]['QpBest']) # [{"藏许木-1":20,xxxx:xxx},{"藏山南-1":20,xxxx:xxx}] #粒子中最优
    # pBest = copy.deepcopy(Qhistory[-1]['pBest']) #[20,50]
    # QgBest = copy.deepcopy(Qhistory[-1]['QgBest']) # {"藏许木-1":20,xxxx:xxx}
    # gBest = Qhistory[-1]['gBest']

    Q = np.array([[Qhistory[-1]['QgBest'][i] for i in Qhistory[-1]['busLabels']] for j in range(PSOConfig['size'])])
    V = np.array([[Qhistory[-1]['QgBest'][i] for i in Qhistory[-1]['busLabels']] for j in range(PSOConfig['size'])])

    



    F = [PSOConfig["W0"] for i in range(PSOConfig["size"])] #[20 50]

    for Iter in range(1):

        F = [PSOConfig["W0"] for i in range(PSOConfig["size"])];
        QData = {};
        QData["QDicts"] = copy.deepcopy(QDicts);
        QData["VDicts"] = copy.deepcopy(VDicts);
        QData["busLabels"] = busLabels;
        SIs = [];
        for PSOIter in range(PSOConfig["size"]):
            
            for i in range(len(Q[PSOIter])):
                sa.project.getComponentByKey(Syncids[i]).args['s'] = - Q[PSOIter][i]

            

            # 开始仿真
            # sa.project.getModelJob('SA_电磁暂态仿真')[0]['args']['url'] = 'https://internal.cloudpss.net/graphql';

            # sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案')
            sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案') #'http://10.112.10.135/'
            # sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案',apiUrl = 'http://10.112.10.135/')
        
            SI,ValidNumI = sa.calculateSI('SA_电磁暂态仿真', 0, Ts = 1.5, dT0 = 0.5, Tinterval = 0.3, T1 = 2.5, dV1 = 0.25, dV2 = 0.05, VminR = 0.7, VmaxR = 1.3)
            print("SI,ValidNumI:"+str(SI) + str(len(ValidNumI)))
            SIs.append(SI);
            if(SI < PSOConfig["SI0"]):
                F[PSOIter] = sum(Q[PSOIter]);
            else:
                # F[PSOIter] = PSOConfig["W0"];
                F[PSOIter] = (1 + SI) * (len(busKeys)*PSOConfig["Qmax"] + sum(Q[PSOIter]));
            
            if(pBest[PSOIter] > F[PSOIter]):
                pBest[PSOIter] = F[PSOIter];
                QpBest[PSOIter] = copy.deepcopy(QDicts[PSOIter]);

        gBestHist = gBest;
        gBest = min(pBest);
        bestPSOIter = pBest.index(gBest)
        QgBest = copy.deepcopy(QDicts[bestPSOIter]);

        QpBestTemp = np.array([[i[j] for j in busLabels] for i in QpBest]);
        QgBestTemp = np.array([QgBest[j] for j in busLabels]);

        for PSOIter in range(PSOConfig["size"]):
            V[PSOIter] = PSOConfig["W"] * V[PSOIter] + PSOConfig["C1"]*random.random()*(QpBestTemp[PSOIter] - Q[PSOIter])\
                + PSOConfig["C2"]*random.random()*(QgBestTemp - Q[PSOIter]);

            V[PSOIter][np.where(V[PSOIter]>PSOConfig["vmax"])] = PSOConfig["vmax"]
            V[PSOIter][np.where(V[PSOIter]<-PSOConfig["vmax"])] = -PSOConfig["vmax"]

            # V[PSOIter][np.where(Q[PSOIter]>PSOConfig["Qmax"])] = - abs(V[PSOIter][np.where(Q[PSOIter]>PSOConfig["Qmax"])])
            # V[PSOIter][np.where(Q[PSOIter]<PSOConfig["Qmin"])] = abs(V[PSOIter][np.where(Q[PSOIter]<PSOConfig["Qmin"])])

            V[PSOIter][np.where(Q[PSOIter]>PSOConfig["Qmax"])] = 0
            V[PSOIter][np.where(Q[PSOIter]<PSOConfig["Qmin"])] = 0

            Q[PSOIter] = Q[PSOIter] + V[PSOIter];
            Q[PSOIter][np.where(Q[PSOIter]>PSOConfig["Qmax"])] = PSOConfig["Qmax"];
            Q[PSOIter][np.where(Q[PSOIter]<PSOConfig["Qmin"])] = PSOConfig["Qmin"];

            

        
        QData["F"] = F;
        QData["QpBest"] = copy.deepcopy(QpBest);
        QData["QgBest"] = copy.deepcopy(QgBest);
        QData["pBest"] = pBest;
        QData["gBest"] = gBest;
        QData["SI"] = SIs;

        QDicts = []
        VDicts = []
        for j in range(PSOConfig["size"]):
            QDict = {}
            VDict = {}
            for i in range(len(busLabels)):
                QDict[busLabels[i]] = Q[j][i]
                VDict[busLabels[i]] = V[j][i]
            QDicts.append(QDict);
            VDicts.append(VDict);

        Qhistory.append(QData);

        fnameQ = path+'/PSO_Qhistory_'+'.json'
        with open(fnameQ, "w", encoding='utf-8') as f:
            f.write(json.dumps(Qhistory, indent=4))
        print('Q迭代过程保存为：'+fnameQ)
        
        # if(max(abs(gBestHist-gBest)) < 0.1):
        #     print('迭代已经收敛，结束仿真计算。总迭代次数：Q = '+str(Iter+1))


#     desc = '此为自动暂稳分析程序生成的仿真算例。\n作者：谭镇东；\n日期与时间：'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+\
#             '\n' + sa.project.description
#     sa.saveProject(projectKey+'Auto_SA',sa.project.name+'_自动暂稳分析',desc = desc + sa.project.description )
    
