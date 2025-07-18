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

# 用于切除负荷测试
if __name__ == '__main__':
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ODgxNCwidXNlcm5hbWUiOiJzbHhuZyIsInNjb3BlcyI6WyJtb2RlbDo5ODM2NyIsImZ1bmN0aW9uOjk4MzY3IiwiYXBwbGljYXRpb246MzI4MzEiXSwicm9sZXMiOlsic2x4bmciXSwidHlwZSI6ImFwcGx5IiwiZXhwIjoxNzczOTk1ODkzLCJub3RlIjoidG9vbHMiLCJpYXQiOjE3NDI4OTE4OTN9.vWGL5XKqgWX28ZvumCKpeeYWvIRl7wadNINK-tbN3pP5s0ilIbJpBXrJPefkKytntPr96Y2VVF7NBvkYbGcFvQ'
    apiURL = 'https://cloudpss.net/'
    username ='slxng' #用户名
    projectKey = 'IEEE039' #项目名称


#     cloudpss.setToken(tk)
#     os.environ['CLOUDPSS_API_URL'] = apiURL
#     sproject = cloudpss.Project.fetch(spr)
    # prd,pid = genParaDict(tk, apiurl, spr)
    # getCompLib(tk, apiURL, spr)

    with open('saSource.json', "r", encoding='utf-8') as f:
        compLib = json.load(f)

    sa = SA.S_S_SyncComp()
    sa.setConfig(tk,apiURL,username,projectKey);
    sa.setInitialConditions()
    sa.createSACanvas()
    # N_2LineLabel1 = ['藏年楚-藏色麦Ι线','藏年楚-藏色麦ΙΙ线'];
    N_2LineLabel1 = ['TLine_3p-22','TLine_3p-20'] #许木-墨竹

    
    N_2LineKey1 = []
    for i in N_2LineLabel1:
        N_2LineKey1.append([j for j in sa.compLabelDict[i].keys()][0])
    
    # N_1LineLabel1 = '藏夏玛—藏德吉开关站';
    # N_1LineKey1 = [j for j in sa.compLabelDict[N_1LineLabel1].keys()][0]

    sa.setN_2_GroundFault(N_2LineKey1[0], N_2LineKey1[1], 0, 4, 4.06, 7, OtherFaultParas = {'chg':'1'})
    # sa.setN_1_GroundFault(N_1LineKey1, 0, 4, 4.09, 7)

    #切除那曲负荷
    # NaquLoads = ['藏那曲中心10_0','藏那曲中35_0','藏黑河Y1_0','藏扎牵220_0','藏那牵220_0','藏安牵220_0','藏托牵220_0','藏联牵220_0','藏嘎牵220_0','藏露牵220_0',
    # '藏乌牵220_0','藏妥牵220_0','藏雄牵220_0'];
    # NaquLoads = ['藏乌玛塘35','藏藏那10_0','藏藏那35-3_0','藏安牵220_0','藏托牵220_0','藏联牵220_0','藏扎牵220_0','藏藏安10-1_0','藏嘎牵220_0','藏那牵220_0',
    # '藏妥牵220_0','藏露牵220_0','藏乌牵220_0','藏雄牵220_0','藏德吉10_0','藏双湖10_0','藏双湖35_0','藏多玛10_0','藏多玛35_0','藏青龙10_0','藏聂荣10_0','藏黑河Y1_0',
    # '藏比如10_0','藏巴青10_0','藏索县10_0','藏达塘10_0','藏曲卡10_0','藏那曲中心10_0','藏嘉黎10_0','藏夏玛10_0','藏班戈10_0','藏那曲中35_0']
    NaquLoads=['newExpLoad-19','newExpLoad-7','newExpLoad-8','newExpLoad-9']
    # NaquLoads = ['藏湘电35-1_0','藏日喀则10-2_0','藏下过10_0','木尔嘎10_0','木尔嘎35_0','藏申亚10_0','藏申亚35_0','藏江孜Y2_0','藏江孜S1_0','藏和平10_0','藏卡嘎10-2_0','藏卡嘎10_0','藏藏诺Y1_0','藏如牵11_0','藏竹牵11_0','藏琼牵11_0','藏茶牵11_0','藏日牵11_0','藏申扎10_0','藏定日Y1_0','藏昂仁Y1_0','藏南木林10-2_0','藏南木林10_0','藏仁布10_0','藏萨迦Y1_0','藏亚东10_0','藏岗巴Y1_0','藏年楚10_0','藏洛扎10_0','藏康马10_45','藏甲孜35_0','藏浪卡子10_51','藏城区10_0','藏大竹卡10-2_0','藏大竹卡10-1_0','藏吉定10_0','藏拉孜10_0','藏日喀则10_73','藏甲孜10_0','藏江孜10_39','藏宇拓35_92','藏白朗35_4','藏江孜35_40']
    NaquLoadsKeys = [];
    for i in NaquLoads:
        try:
            NaquLoadsKeys.append([j for j in sa.compLabelDict[i].keys()][0])
        except:
            print('there is no '+ i)
            continue;
    for i in range(len(NaquLoadsKeys)):
        sa.setCutFault(NaquLoadsKeys[i], 4.06)
    
    sa.createJob('emtps', name = 'SA_电磁暂态仿真', args = {'begin_time': 0,'end_time': 5,'step_time': 0.00002})
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

    pfresultID = 'b240d137-4ae0-4119-8e7f-98fd229808a5'
    r = cjob.fetch(pfresultID)
    # pfresult = nest_asyncio.asyncio.run(r).result
    while not r.status():
        time.sleep(2)
    pfresult = r.result

    print('正在回写潮流数据...')
    pfresult.powerFlowModify(sa.project)

    sa.createSSSCACanvas()
    
    

    busLabels =  ['newBus_3p-8','newBus_3p-7']
    busKeys = []
    for i in busLabels:
        busKeys.append([j for j in sa.compLabelDict[i].keys()][0])
        
    S0 = 1;#各个调相机的初始容量
    Q = [250,1]
    Syncids = []
    for bPtr in range(len(busKeys)):
        # ids = sa.addSyncComp(busKeys[bPtr], pfresult, syncArgs = {"Smva": str(Q[bPtr])})
        ids = sa.addSVC(busKeys[bPtr], S = -Q[bPtr], Ts = 4.06, Te = 999)
        Syncids.append(ids[0])


    # sa.project.getModelJob('SA_电磁暂态仿真')[0]['args']['url'] = 'https://internal.cloudpss.net/graphql';
    sa.runProject(jobName='SA_电磁暂态仿真', configName='SA_参数方案')
    sa.plotResult(k=0)

    path = 'results/'+ projectKey
    folder = os.path.exists(path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径

    # Result.dump(sa.runner.result,path+'/SAresult_'+ time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.cjob')
