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
from my_codeact.test_data.jobApi import fetch,fetchAllJob,abort
from my_codeact.test_data.PSAToolbox import PSAToolbox

import tkinter
import tkinter.filedialog

import math

from IPython.display import HTML
from html import unescape
from typing import Dict, List, Optional, TypedDict,Union,Set,Tuple

import random
import json
import copy
from cloudpss.model.implements.component import Component
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
from cloudpss.model.revision import ModelRevision
from cloudpss.model.model import Model

from scipy import optimize

from string import Template

def is_number(s):
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

# # 调相机选址定容相关分析模块S_S_SyncComp
# 
# 本模块基于StabilityAnalysis模块构建。实现电网稳定问题的高级分析。实现了新增调相机、计算电压敏感度VSI、计算故障严重程度SI等功能。

class S_S_SyncComp(PSAToolbox):
    def __init__(self):
        super(S_S_SyncComp,self).__init__()
        self.compNames.update({'SyncGeneratorRouter':'SA_同步发电机',                          '_newBus_3p':'SA_三相母线',                              '_PSASP_AVR_11to12':'SA_调压器11-12型',                              '_newTransformer_3p2w':'SA_双绕组变压器',                              '_newShuntLC_3p':'SA_注入动态无功',
                              '_newGain':'SA_Gain', 'HW_PCS_TEST_Mask':'SA_PCS'})
        self.cSyncCid = 'canvas_AutoSA_Sync_Compensators'
        self.cDynQid = 'canvas_AutoSA_Dynamic_Q'
        
        
    def createSSSCACanvas(self):
        """
        Descriptions
        ----------
            创建用于调相机分析和动态注入无功的 Canvas。

        Parameters
        ----------
            无

        Output
        ----------
            无
        """
        self.createCanvas(self.cSyncCid,'新增调相机分析')
        self.createCanvas(self.cDynQid,'动态注入无功')
        
        nameTemp = 'SSSCA_Const-0'
        self.addCompInCanvas(self.compLib['_newConstant'], key = 'SSSCA_Const',canvas = self.cSyncCid,                     args = {'Name':nameTemp,"Value": "0"}, pins = {'0':'SSSCA_Const-0'},label = nameTemp)
        
        nameTemp = 'SSSCA_Const-1'
        self.addCompInCanvas(self.compLib['_newConstant'], key = 'SSSCA_Const',canvas = self.cSyncCid,                     args = {'Name':nameTemp,"Value": "1"}, pins = {'0':'SSSCA_Const-1'},label = nameTemp)
        
        nameTemp = 'SSSCA_S2M'
        argsTemp = {'Name':nameTemp, 'V0':'0', 'V1':'1', 'Time':'1'}
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'SSSCA_S2M',canvas = self.cSyncCid,                     args = argsTemp, pins = {'0':'@SSSCA_S2M'},label = nameTemp)
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'SSSCA_L2N',canvas = self.cSyncCid,                     args = argsTemp, pins = {'0':'@SSSCA_L2N'},label = nameTemp)


        self.newLinePos(self.cSyncCid)
         
    def getXInterval(self, xData: list, x: float):
        """
        Descriptions
        ----------
            使用二分查找法获取 `xData` 中 `x` 所在区间的索引。

        Parameters
        ----------
            xData (list): 一维有序数据列表。
            x (float): 要查找的值。

        Output
        ----------
            int: `x` 所在区间的起始索引。
        """
        nsize = len(xData)
        upperLimit = nsize-1;
        lowerLimit = 0;
        z = math.floor((upperLimit+lowerLimit) / 2);
        while (z>=0 or z< (nsize-1)):
            if(xData[z]>x):
                if(z<=0):
                    z = 0;
                    break;
                else:
                    upperLimit = z;
                    z = math.floor((upperLimit+lowerLimit) / 2);
            elif(xData[z+1]<x):
                if(z+1>=(nsize-1)):
                    z = (nsize-1);
                    break;
                else:
                    lowerLimit = z+1;
                    z = math.floor((upperLimit+lowerLimit) / 2);
            elif(xData[z]<=x and xData[z+1]>=x):
                break;
            else:
                z = 0;
                break;
        return z;
    
    def calculateDV(self, jobName: str, voltageMeasureK: Optional[int] = 0, result:Optional[object] = None, Ts: Optional[float] = 4, dT0: Optional[float] = 0.5, judge: Optional[List] = [[0.1, 3, 0.75, 1.25], [3, 999, 0.95, 1.05]], VminR: Optional[float] = 0.2, VmaxR: Optional[float] = 1.8, ValidName: Optional[List] = None):
        """
        Descriptions
        ----------
            计算电压偏差（DV），评估电压暂态稳定性。

        Parameters
        ----------
            jobName (str): 仿真任务的名称。
            voltageMeasureK (int,optional): 电压测量通道的键，默认为0。
            result (Result, optional): 仿真结果对象。默认为 `None`，表示使用 `runner.result`。
            Ts (float, optional): 仿真开始时间。默认为 `4`。
            dT0 (float, optional): 计算初始电压平均值的时间范围。默认为 `0.5`。
            judge (list, optional): 电压裕度判断条件，格式为 `[[t_start, t_end, lower_bound, upper_bound], ...]`。默认值 `[[0.1,3,0.75,1.25],[3,999,0.95,1.05]]`。
            VminR (float, optional): 稳定电压恢复的最小比例。默认为 `0.2`。
            VmaxR (float, optional): 稳定电压恢复的最大比例。默认为 `1.8`。
            ValidName (list, optional): 用于筛选有效通道的名称列表。默认为 `None`。

        Output
        ----------
            tuple: 包含电压上限裕度列表 (`list`)、电压下限裕度列表 (`list`)和有效通道索引列表 (`list`)。
        """
        job = self.project.getModelJob(jobName)[0]
        step_time = float(job['args']['step_time'])
        end_time = float(job['args']['end_time'])
        if(result==None):
            result = self.runner.result
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
#         plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
#         pdtV = 1 / plotFV;
        
        dVUj = []
        dVLj = []
        
        ValidNum = [i for i in range(len(Vresults))]
        
#         V0 = []
        for k in range(len(Vresults)):
            ts = Ts - dT0;
            te = Ts;
        
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];
            name = Vresults[k]['name'];
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
#             V0.append(Vaverage)
            
            dVUj_temp = 9999999;
            dVLj_temp = 9999999;

            for j in judge:
                ts = Ts+j[0]
                te = Ts+j[1]
                if(ts>end_time):
                    ts = end_time;
                if(te>end_time):
                    te = end_time;  

                msV = self.getXInterval(vx,ts);
                meV = self.getXInterval(vx,te);
                dVUj_temp = min(dVUj_temp,j[3]*Vaverage - max(vy[msV:meV]))
                dVLj_temp = min(dVLj_temp,min(vy[msV:meV]) - j[2]*Vaverage)

            dVUj.append(dVUj_temp)
            dVLj.append(dVLj_temp)
            
            ts = end_time - dT0;
            te = end_time;

            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            if(max(vy[msV:meV])<VminR * Vaverage or min(vy[msV:meV])>VmaxR * Vaverage):
                ValidNum.remove(k)
            if(ValidName!= None):
                flag = 0
                for jj in ValidName:
                    if(jj in name):
                        flag = 1;
                if(flag==0):
                    ValidNum.remove(k)

        # self.draw_DUDV(dVUj,dVLj)
        return {"电压上限裕度":dVUj,"电压下限裕度":dVLj,"有效通道索引":ValidNum}
        # return dVUj,dVLj,ValidNum

    def calculateSI(self, jobName: str, voltageMeasureK: str, result: Optional[object] = None, Ts: Optional[float] = 4, dT0: Optional[float] = 0.5, Tinterval: Optional[float] = 0.11, T1: Optional[float] = 3, dV1: Optional[float] = 0.25, dV2: Optional[float] = 0.1, VminR: Optional[float] = 0.2, VmaxR: Optional[float] = 1.8):
        """
        Descriptions
        ----------
            计算故障严重程度指标（SI）。

        Parameters
        ----------
            jobName (str): 仿真任务的名称。
            voltageMeasureK (str): 电压测量通道的键。
            result (Result, optional): 仿真结果对象。默认为 `None`，表示使用 `runner.result`。
            Ts (float, optional): 扰动发生时间。默认为 `4`。
            dT0 (float, optional): 计算初始电压平均值的时间范围。默认为 `0.5`。
            Tinterval (float, optional): 故障清除后，计算积分开始的时间偏移。默认为 `0.11`。
            T1 (float, optional): 计算 SI 时，积分时间窗的长度。默认为 `3`。
            dV1 (float, optional): 第一阶段电压偏差阈值。默认为 `0.25`。
            dV2 (float, optional): 第二阶段电压偏差阈值。默认为 `0.1`。
            VminR (float, optional): 稳定电压恢复的最小比例。默认为 `0.2`。
            VmaxR (float, optional): 稳定电压恢复的最大比例。默认为 `1.8`。

        Output
        ----------
            tuple: 包含故障严重程度指标 SI (`float`) 和有效通道索引列表 (`list`)。
        """
        
        job = self.project.getModelJob(jobName)[0]
        step_time = float(job['args']['step_time'])
        end_time = float(job['args']['end_time'])
        if(result==None):
            result = self.runner.result
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
#         plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
#         pdtV = 1 / plotFV;
        
        ValidNum = [i for i in range(len(Vresults))]
        
#         V0 = []
        SI = 0;
        for k in range(len(Vresults)):
            ts = Ts - dT0;
            te = Ts;
        
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];

            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
#             V0.append(Vaverage)

            ts = end_time - dT0;
            te = end_time;
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            if(max(vy[msV:meV])<VminR * Vaverage or min(vy[msV:meV])>VmaxR * Vaverage):
                ValidNum.remove(k)
                continue

            ts = Ts + Tinterval;
            te = Ts + Tinterval + T1;
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);

            SI += len([i for i in vy[msV:meV] if (i < (1-dV1)*Vaverage or i > (1+dV1)*Vaverage)]) / (meV-msV);
            SI += len([i for i in vy[meV:] if (i < (1-dV2)*Vaverage or i > (1+dV2)*Vaverage)]) / len(vy[meV:]);

        SI = SI / len(ValidNum);

        return SI,ValidNum
    def draw_DUDV(self,dVUj:list,dVLj:list):
        """
        Descriptions    
        ----------
            绘制DUDV折线图
        Parameters
        ----------              
            dVUj (list): 电压上限裕度列表
            dVLj (list): 电压下限裕度列表     
        Output
        ----------  
            None
        """
        mm= [i for i in range(len(dVUj)) if dVUj[i]<0]
        nn= [i for i in range(len(dVLj)) if dVLj[i]<0]
        print(mm)
        print(nn)
        
        fig = go.Figure()
        k=0
        SSresult = self.runner.result
        # Add traces
        ckeytemp = SSresult.getPlotChannelNames(k)
        rr=SSresult
        m = mm
        for pk in [ckeytemp[i] for i in m]:

            x = rr.getPlotChannelData(k,pk)['x']
            y = rr.getPlotChannelData(k,pk)['y']
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=pk))
        fig.show()
    def calculateVSI(self, jobName: str, voltageMeasureK: int, dQMeasureK: int, busLabels: Optional[list] = None, result: Optional[object] = None, busNum: Optional[int] = None, Ts: Optional[float] = 8, dT: Optional[float] = 1.5, ddT: Optional[float] = 0.5):
        """
        Descriptions
        ----------
            计算电压敏感度指标（VSI）。

        Parameters
        ----------
            jobName (str): 仿真任务的名称。
            voltageMeasureK (int): 电压测量通道的键。
            dQMeasureK (int): 无功功率测量通道的键。
            busLabels (list): 母线标签列表,默认为None,表示所有母线。
            result (Result, optional): 仿真结果对象。默认为 `None`，表示使用 `runner.result`。
            busNum (int, optional): 母线数量。默认为 `None`，将根据仿真结束时间计算。
            Ts (float, optional): 仿真开始时间。默认为 `8`。
            dT (float, optional): 每个母线测试所占用的仿真时长。默认为 `1.5`。
            ddT (float, optional): 无功注入持续时间。默认为 `0.5`。

        Output
        ----------
            dict: 包含 VSIi（每个母线的平均 VSI）和 VSIij（每个母线对其他所有母线的 VSI）的字典。
        """   
        if busLabels is None or len(busLabels) == 0:
            busLabels = list(self.project.getComponentsByRid('model/CloudPSS/_newBus_3p').keys())
        voltageMeasureK = int(voltageMeasureK)
        dQMeasureK = int(dQMeasureK)
        
        job = self.project.getModelJob(jobName)[0]
        step_time = float(job['args']['step_time'])
        if(result==None):
            result = self.runner.result
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
        # plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
        # pdtV = 1 / plotFV;
        
        if (busNum == None):
            busNum = (float(job['args']['end_time']) - Ts) / dT;
            # busNum = len(busLabels)
        busNum = int(busNum);
        Qresults = result.getPlot(dQMeasureK)['data']['traces']
        QChannelNames = [self.project.getComponentByKey(i).pins['0'] for i in \
            self.project.getModelJob(jobName)[0]['args']['output_channels'][dQMeasureK]['4']];
        # return 1
        print(QChannelNames)
        QMap1 = [int(re.search('#SA_VSI_DQ_(.*?)$',QChannelNames[i]).group(1)) for i in range(busNum)];
        # return busNum
        QMap = [QMap1.index(i) for i in range(busNum)];

        
            

        # plotFQ = float(job['args']['output_channels'][dQMeasureK][1]);
        # pdtQ = 1 / plotFQ;


        VSIij = []
        VSIi = []



        ts = float(job['args']['end_time']) - dT + ddT ;
        te = float(job['args']['end_time']);
        V0 = []
        for k in range(len(Vresults)):
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];
            if(vy[0]==None):
                vy = [0 for i in range(len(vy))]
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
            V0.append(Vaverage)

        Mnames = result.getPlotChannelNames(voltageMeasureK)
        for n in range(busNum):
            ts = Ts + dT * n;
            te = Ts + dT * n + ddT;

            ts0 = Ts + dT * n - ddT;
            te0 = Ts + dT * n;
        #             msV = int(ts / pdtV)
        #             meV = int(te / pdtV)
        #             msQ = int(ts / pdtQ)
        #             meQ = int(te / pdtQ)

            Qx = Qresults[QMap[n]]['x']
            Qy = Qresults[QMap[n]]['y']

            msQ = self.getXInterval(Qx,ts);
            meQ = self.getXInterval(Qx,te);

        #             Qaverage = sum(Qy[msQ:meQ]) / (meQ - msQ)
            Qaverage = Qy[meQ-1]
            
            V1 = []
            
            for k in range(len(Vresults)):
                vx = Vresults[k]['x'];
                vy = Vresults[k]['y'];
                if(vy[0]==None):
                    print(Mnames[k])
                    vy = [0 for i in range(len(vy))]
                msV = self.getXInterval(vx,ts);
                meV = self.getXInterval(vx,te);
                msV0 = self.getXInterval(vx,ts0);
                meV0 = self.getXInterval(vx,te0);
        #                 Vtemp = V0[k] - max(vy[msV:meV]) 
                
                Vtemp = sum(vy[msV0:meV0]) / (meV0 - msV0) - sum(vy[msV:meV]) / (meV - msV)
                V1.append(Vtemp / Qaverage)
            VSIij.append(V1)
            VSIi.append(sum(V1) / len(V1))


        VSIiDict = {}
        VSIijDict = {}
        for i in range(len(busLabels)):
            VSIiDict[busLabels[i]] = VSIi[i]
            VSIijDict[busLabels[i]] = {}
            for j in range(len(Mnames)):
                VSIijDict[busLabels[i]][Mnames[j]] = VSIij[i][j]
        VSIresultDict = {'VSIi':VSIiDict,'VSIij':VSIijDict}
        return VSIresultDict

    def addVSIMeasure(self, jobName: str, VSIQkeys: list, VMin: Optional[float] = 0.6, VMax: Optional[float] = 300, NameSet: Optional[Set] = None, NameKeys: Optional[List] = None, freq: Optional[float] = 100, Nbus: Optional[int] = None, dT: Optional[float] = 1.5, Ts: Optional[float] = 8):
        """
        Descriptions
        ----------
            在仿真 Job 中添加 VSI 相关的量测，包括电压量测和无功功率量测。

        Parameters
        ----------
            jobName (str): 仿真任务的名称。
            VSIQkeys (list): VSI 无功源组件的键列表。
            VMin (float, optional): 筛选电压量测母线的最小电压。默认为 `None`。
            VMax (float, optional): 筛选电压量测母线的最大电压。默认为 `None`。
            NameSet (set, optional): 筛选电压量测母线的名称集合。默认为 `None`。
            NameKeys (list, optional): 筛选电压量测母线的名称关键字列表。默认为 `None`。
            freq (float, optional): 输出通道的测量频率。默认为 `None`。
            Nbus (int, optional): 要添加 VSI 测量功能的母线数量。默认为 `10`。
            dT (float, optional): 每个母线测试所占用的仿真时长。默认为 `0.5`。
            Ts (float, optional): 仿真开始时间。默认为 `8`。

        Output
        ----------
            tuple: 包含电压量测的输出通道索引 (`int`)、无功量测的输出通道索引 (`int`)。
        """
        job = self.project.getModelJob(jobName)[0]

        Nbus = len(VSIQkeys)
        
        screenedBus = self.addVoltageMeasures(jobName, VMin, VMax, NameSet, NameKeys, freq, PlotName = 'VSI_节点电压量测');
        voltageMeasureK = len(job['args']['output_channels']) - 1;
        
        job['args']['end_time'] = Nbus * dT + Ts;

        self.addComponentOutputMeasures(jobName, 'model/CloudPSS/_newShuntLC_3p', 'Q', [],compList = VSIQkeys, dim = 1, plotName = 'VSI_动态注入无功量测', freq = freq)
        
        # id1, label = self.addChannel('#SA_VSI_DQ',1)
        # self.addOutputs(jobName, {'0':'VSI_动态注入无功量测', '1':freq, '2':'compressed', '3':1, '4':[id1]})
        dQMeasureK = voltageMeasureK + 1;

        return voltageMeasureK, dQMeasureK

    def addVSIQSource(self, busKeys: Optional[list] = None, V: Optional[float] = 220, S: Optional[float] = 100, Ts: Optional[float] = 8, dT: Optional[float] = 1.5, ddT: Optional[float] = 0.5):
        """
        Descriptions
        ----------
            为电压敏感度分析添加动态注入无功源（shuntLC 组件和断路器）。

        Parameters
        ----------
            busKeys (list): 需要添加无功源的母线键列表,如果为None，表示为所有的母线添加无功源。
            V (float, optional): 动态注入无功源的基准电压（kV）。默认为 `220`。
            S (float, optional): 动态注入无功源的基准无功（MVar）。默认为 `100`。
            Ts (float, optional): 仿真开始时间。默认为 `8`。
            dT (float, optional): 对每个母线测试时所占用的仿真时长（s）。默认为 `1.5`。
            ddT (float, optional): 无功注入持续时间。默认为 `0.5`。

        Output
        ----------
            list: VSI 无功源的组件 ID 列表。
        """

        signalDict = {}
        VSIQKeys = []
        

        if busKeys is None:
            busKeys = list(self.project.getComponentsByRid('model/CloudPSS/_newBus_3p').keys())

        for k in range(len(busKeys)):
            busK = busKeys[k]
# 添加shuntLC
            tempID = 'SA_newShuntLC_3p_'+str(k)
            nameTemp = self.compNames['_newShuntLC_3p']+str(k)
            argsTemp = {'Name':nameTemp,'Dim':'3', 'v':str(float(self.project.getComponentByKey(busK).args['V'])*float(self.project.getComponentByKey(busK).args['VBase'])), 's':str(-S), "Q": '#SA_VSI_DQ_'+str(k)}
            pinsTemp = {"0": 'SA_VSI_C_'+str(k)}
            
            id1, label = self.addCompInCanvas(self.compLib['_newShuntLC_3p'], key = tempID, canvas = self.cDynQid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
            VSIQKeys.append(id1)
# 添加众多开关
            
            tempID = 'SA_VSI_Breaker_'+str(k)
            nameTemp = 'SA_VSI分析_断路器_'+str(k)
            ctrlSigName = '@SA_VSI分析_断路器_'+str(k)
            argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '0'}
            
            pinName = self.project.getComponentByKey(busK).pins['0']
            pinsTemp = {"0": pinName,"1": 'SA_VSI_C_'+str(k)}
        
            id1, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = tempID, canvas = self.cDynQid,                         args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# 添加开关信号源
            nameTemp = 'SA_VSI分析_断路器_信号'
            argsTemp = {'Name':nameTemp, 'INIT':'0', 'Drop':'1', 'T1':str(Ts + k * dT), 'T2':str(Ts + k * dT + ddT)}
            ids, labes = self.addCompInCanvas(self.compLib['_newDropGen'], key = 'SA_VSI_Breaker_Sig',canvas = self.cDynQid,                         args = argsTemp, pins = {'0':ctrlSigName},label = nameTemp, MaxX = 500)
            
        self.newLinePos(self.cDynQid)
        return VSIQKeys

    def addSVC(self, busKey: str, S: Optional[float] = 1, Ts: Optional[float] = 4, Te: Optional[float] = 999):
        """
        Descriptions
        ----------
            添加静态无功补偿器（SVC）到指定母线。

        Parameters
        ----------
            busKey (str): SVC 将要连接的母线键。
            S (float, optional): SVC 的额定视在功率（MVar）。默认为 `1`。
            Ts (float, optional): SVC 启用时间（s）。默认为 `4`。
            Te (float, optional): SVC 禁用时间（s）。默认为 `999`。

        Output
        ----------
            list: 添加的 SVC 相关组件（shuntLC、断路器、信号发生器）的 ID 列表。
        """
        V = float(self.project.getComponentByKey(busKey).args['VBase']);
        busPin = self.project.getComponentByKey(busKey).pins['0'];
        
        busName = self.project.getComponentByKey(busKey).label;
        switchPin = 'SVC_Switch_'+busName;
# 添加shuntLC
        tempID = 'SA_SVC';
        nameTemp = 'SA_SVC'+busName
        argsTemp = {'Name':nameTemp,'Dim':'3', 'v':str( V), 's':str(S)}
        pinsTemp = {"0": switchPin}
        
        id1, label = self.addCompInCanvas(self.compLib['_newShuntLC_3p'], key = tempID, canvas = self.cDynQid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        self.newLinePos(self.cDynQid)
        
# 添加开关
        tempID = 'SA_SVC_Breaker';
        nameTemp = 'SA_SVC_Breaker'+busName;
        ctrlSigName = '@SVC_'+busName;
        argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '0'}
        
        pinsTemp = {"0": busPin,"1": switchPin}
    
        id2, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = tempID, canvas = self.cDynQid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# 添加开关信号源
        nameTemp = 'SA_VSI分析_断路器_信号'
        argsTemp = {'Name':nameTemp, 'INIT':'0', 'Drop':'1', 'T1':str(Ts), 'T2':str(Te)}
        ids, labes = self.addCompInCanvas(self.compLib['_newDropGen'], key = 'SA_SVC_Breaker_Sig',canvas = self.cDynQid, args = argsTemp, pins = {'0':ctrlSigName},label = nameTemp, MaxX = 500)
            
        self.newLinePos(self.cDynQid)

        return [id1,id2,ids]

    def addPCSComp(self, busKey: str, S: Optional[float] = 10, PCSArgs: Optional[Dict] = None):
        """
        Descriptions
        ----------
            添加 PCS (Power Conversion System) 组件到指定母线。

        Parameters
        ----------
            busKey (str): PCS 将要连接的母线键。
            S (float, optional): PCS 的额定功率（MVar）。默认为 `10`。
            PCSArgs (dict, optional): PCS 组件的详细参数字典，用于覆盖默认参数。默认为 `None`。

        Output
        ----------
            list: 添加的 PCS 组件的 ID 列表。
        """
        '''
            busKeys:{busKey1, busKey2}
            S:添加的动态注入无功源的基准无功，单位为MVar
        '''
        V = float(self.project.getComponentByKey(busKey).args['VBase'])*float(self.project.getComponentByKey(busKey).args['V']);
        busPin = self.project.getComponentByKey(busKey).pins['0'];
        busName = self.project.getComponentByKey(busKey).label;
        pinsTemp = {"AC": busPin, "P": busPin + ".SA_PCS_P", "Q": busPin + ".SA_PCS_Q"};

        tempID = 'SA_HW_PCS';
        nameTemp = self.compNames['HW_PCS_TEST_Mask']
        
        argsTemp = self.compLib['HW_PCS_TEST_Mask'];
        if(PCSArgs!=None):
            argsTemp.update(PCSArgs);
        argsTemp['Num'] = str(S/0.2);
        argsTemp['Vpcc'] = str(V)
        ids, labes = self.addCompInCanvas(self.compLib['HW_PCS_TEST_Mask'], key = tempID,canvas = self.cDynQid, args = argsTemp, pins = pinsTemp,label = nameTemp, MaxX = 500)
        self.newLinePos(self.cDynQid)
        return ids

    def addSyncComp(self, busKey: str, pfResult:object, syncArgs: Optional[Dict] = None, transArgs: Optional[Dict] = None, busArgs: Optional[Dict] = None, AVRComp: Optional[Dict] = None, AVRArgs: Optional[Dict] = None):
        """
        Descriptions
        ----------
            在指定母线处添加同步调相机及其相关组件（母线、变压器、AVR、增益模块）。

        Parameters
        ----------
            busKey (str): 调相机将要连接的母线键。
            pfResult (PowerFlowResult): 潮流计算结果对象，用于获取母线的电压幅值和相角。
            syncArgs (dict, optional): 同步发电机组件的详细参数字典。默认为 `None`。
            transArgs (dict, optional): 变压器组件的详细参数字典，例如 `{"Smva": "额定容量","X1": "正序漏电抗","Rl": "正序漏电阻"}`。默认为 `None`。
            busArgs (dict, optional): 新增母线组件的详细参数字典。默认为 `None`。
            AVRComp (dict, optional): AVR 组件的定义字典。默认为 `None`，使用默认的 PSASP 11-12 型 AVR。
            AVRArgs (dict, optional): AVR 组件的详细参数字典。默认为 `None`。

        Output
        ----------
            list: 新增所有组件（同步调相机、母线、变压器、AVR、增益模块）的 ID 列表。
        """
        
#         nameTemp = 'SSSCA_同步调相机'
#         argsTemp = {'Name':nameTemp, 'VT_o':str(fault_start_time), 'fe':str(fault_end_time),'ft':str(fault_type)}
        
        data = pd.DataFrame()
        pfBusResult=pfResult.getBuses() 
        pfBusIndex = pfBusResult[0]['data']['columns'][0]['data'].index(busKey);
        vm = pfBusResult[0]['data']['columns'][2]['data'][pfBusIndex];
        va = pfBusResult[0]['data']['columns'][3]['data'][pfBusIndex];
        VB = float(self.project.getComponentByKey(busKey).args['VBase'])
        
#         if(name==None):
#             name = '新调相机';
        
#         busName = name+'-母线';
#         transName = name+'-变压器';
#         avrName = name+'-AVR';
#         syncName = name+'-电机';

# 处理同步电机
        tempID = 'SA_Sync';
        nameTemp = self.compNames['SyncGeneratorRouter']
        
        
        if(tempID not in self.compCount.keys()):
            self.compCount[tempID] = 0;
        count = self.compCount[tempID] + 1;
        nameCount = nameTemp + "_" + str(count)
        syncName = nameCount;
        argsTemp = {'Name':syncName+'.L2N', 'V0':'0', 'V1':'1', 'Time':'2'}
        ids, label = self.addCompInCanvas(self.compLib['_newStepGen'], key = tempID+'_L2N',canvas = self.cSyncCid,  args = argsTemp, pins = {'0':'@'+syncName+'.L2N'},label = syncName+'.L2N')
        argsTemp = {'Name':syncName+'.S2M', 'V0':'0', 'V1':'1', 'Time':'1'}
        ids, label = self.addCompInCanvas(self.compLib['_newStepGen'], key = tempID+'_S2M',canvas = self.cSyncCid,  args = argsTemp, pins = {'0':'@'+syncName+'.S2M'},label = syncName+'.S2M')

        argsTemp = {'Name':nameTemp,'pf_P':'0', 'pf_Q':'0', 'pf_V':str(vm), 'pf_Theta':str(va),
                   "V_mag": str(vm), "V_ph": str(va), "AP": "0", "RP": "0",
                   "s2m_o": "","l2n_o": "","Tm0_o": "","wr_o": "","theta_o": "",
                   "loadangle_o": "","loadangle_so": "","IT_o": "","PT_o": "","QT_o": "","IT_inst": "",
                   "VT_o":'#'+syncName+'.VT', "Ef0_o":'#'+syncName+'.Ef0',
                   'StartupType':'4','s2m':'@'+syncName+'.S2M','l2n':'@'+syncName+'.L2N','BusType':'0'}
        if(syncArgs!=None):
            argsTemp.update(syncArgs);
        
        pinsTemp = {"0": syncName,
                    "1": "",
                    "2": "SSSCA_Const-0",
                    "3": syncName+".Te",
                    "4": syncName+".Ef",
                    "5": syncName+".If"}
        
        Syncid1, label = self.addCompInCanvas(self.compLib['SyncGeneratorRouter'], key = tempID, canvas = self.cSyncCid,  args = argsTemp, pins = pinsTemp, label = syncName, MaxX = 500)
        
        VBSync = float(self.project.getComponentByKey(Syncid1).args['V']['source'] if isinstance(self.project.getComponentByKey(Syncid1).args['V'],dict) else self.project.getComponentByKey(Syncid1).args['V']) * math.sqrt(3);

        syncMVA = self.project.getComponentByKey(Syncid1).args['Smva'];
        
# 处理母线
        tempID = 'SA_Sync_Bus';
        nameTemp = self.compNames['_newBus_3p']
        argsTemp = {'Name':nameTemp,'Freq':'50', 'VBase':str(VBSync), 'V':str(vm), 'Theta':str(va),"Vabc": "","Vrms": ""}
        if(busArgs!=None):
            argsTemp.update(busArgs);
        pinsTemp = {"0": syncName}
        Busid1, label = self.addCompInCanvas(self.compLib['_newBus_3p'], key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp + "_" + str(count), MaxX = 500)
        
# 处理变压器
        tempID = 'SA_Transformer_3p2w';
        nameTemp = self.compNames['_newTransformer_3p2w']
        argsTemp = {'Name':nameTemp, 'V1':str(VBSync), 'V2':str(VB), 'Xl':'0.1', 'Rl':'0', 'Tmva':str(100)}
        if(transArgs!=None):
            argsTemp.update(transArgs);
            
        busName = self.project.getComponentByKey(busKey).pins['0']
        pinsTemp = {"0": syncName,"1": busName}
        Transid1, label = self.addCompInCanvas(self.compLib['_newTransformer_3p2w'], key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp + "_" + str(count), MaxX = 500)
        
# 处理AVR
        tempID = 'SA_PSASP_AVR_11to12';
        if(AVRComp==None):
            AVRComp = self.compLib['_PSASP_AVR_11to12'];
            nameTemp = self.compNames['_PSASP_AVR_11to12']
            pinsTemp = {"0": syncName+".Vref",
                        "1": "SSSCA_Const-0",
                        "2": '#'+syncName+'.VT',
                        "3": '#'+syncName+'.Ef0',
                        "4": syncName+".If",
                        "5": '@'+syncName+'.S2M',
                        "6": syncName+".Vref0",
                        "7": syncName+".Ef" }
        else:
            definition = AVRComp["definition"]
            nameTemp = definition.split('/')[-1]
        argsTemp = {}
        if(AVRArgs!=None):
            argsTemp.update(AVRArgs);
        AVRid1, label = self.addCompInCanvas(AVRComp, key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# 处理newGain
        tempID = 'SA_newGain';
        nameTemp = self.compNames['_newGain']
        argsTemp = {'G':'1'}
        pinsTemp = {"0": syncName+".Vref0",
                    "1": syncName+".Vref"}
        Gainid1, label = self.addCompInCanvas(self.compLib['_newGain'], key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        
        self.newLinePos(self.cSyncCid)
        
        return [Syncid1,Busid1,Transid1,AVRid1,Gainid1]

def getCompLib(tk, apiURL, spr, compDefLib = {}, name = None):
    cloudpss.setToken(tk)
    os.environ['CLOUDPSS_API_URL'] = apiURL
    sproject = cloudpss.Model.fetch(spr)
    compLib = {}
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
    compDefLib_inv = {v: k for k, v in compDefLib.items()}
    for i in sproject.getAllComponents().keys():
        comp = sproject.getAllComponents()[i].toJSON()
        if('diagram-component' in comp['shape']):
            compcp = copy.deepcopy(comp);
            compcp['style'] = {}
            if(comp['definition'] not in compDefLib_inv.keys()):
                pattern = '[^/]*/[^/]*/([^/]*)$'
                zone = re.search(pattern,comp['definition']);
                compLib[zone.group(1)] = compcp;
            else:
                compLib[compDefLib_inv[comp['definition']]] = compcp;
    if(name==None):
        name = 'saSource.json'
    with open(name, "w", encoding='utf-8') as f:
        f.write(json.dumps(compLib, indent=4))
    return compLib

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

def fetchCompData(rids=None):

    if rids is None:
        raise Exception('rids must be specified')
    models = []
    i = 0
    for rid in rids:
        i += 1
        models.append(
            MODE_TEMPLATE.safe_substitute(model='model' + str(i), rid=rid))

    query = "query { %s }" % ' '.join(models)

    data = cloudpss.utils.graphql_request(query, {})

    return data['data']

def genParaDict(zdmToken,internalapiurl,projName):
    ParaDict = {}
    PinDict = {}
    
#     zdmToken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzMsInVzZXJuYW1lIjoiQ2xvdWRQU1MiLCJzY29wZXMiOlsidW5rbm93biJdLCJ0eXBlIjoiU0RLIiwiZXhwIjoxNjYxNTgwNDc4LCJpYXQiOjE2MzAwNDQ0MjR9.KWqs-InItjYIGmXC-zKUGqPxBZZyxj52DHt_q7ftdP3eUM65a5ZJgQVn6hYpHEJYRShB_u_nOD5MivhdsnZsYf-F8U3Jyhel9BBVUkKA3LzbaEQgPHFAg50ftVW86HXnUlUC2oiV_uleH_g8tt9N__RGTnMV3VDl23Ie9uICQnI'
#     internalapiurl = 'https://internal.cloudpss.net/';
#     projName = 'model/greyd/AllMachineCtrlComp';
    cloudpss.setToken(zdmToken)
    os.environ['CLOUDPSS_API_URL'] = internalapiurl
    prjtmp = cloudpss.Model.fetch(projName)
    allcomp = prjtmp.getAllComponents();
    allcompList = []
    
    
    
    
    for cmp in allcomp.keys():
        cmpJSN = allcomp[cmp].toJSON()
        allcompList.append(cmpJSN['definition']);
    RawDataList = fetchCompData(allcompList);
    for rawData in RawDataList.values():
        
        # print(rawData)
        
        
        ParaDict[rawData['rid']] = {}
        ParaDict[rawData['rid']]['DiscriptName'] = rawData['name']
        PinDict[rawData['rid']] = {}
        
#         rawData['revision']['parameters'][0]['name']
#         print(rawData)
        for item0 in rawData['revision']['parameters']:
            for item1 in item0['items']:
                ParaDict[rawData['rid']][item1['key']] = item1;
        for item0 in rawData['revision']['pins']:
            PinDict[rawData['rid']][item0['key']] = item0;
            
            
            
    return ParaDict,PinDict