# comment: 要添加一个新单元，输入 '# %%'
# comment: 要添加一个新的标记单元，输入 '# %% [markdown]'
# %% [markdown]
# # comment: import
# comment: 所需库文件，可自行对照缺少的库

# %%
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
# comment: 从 jobApi 导入 fetch、fetchAllJob、abort 函数
from jobApi import fetch,fetchAllJob,abort
# comment: 从 PSAToolbox 导入 PSAToolbox 类
from PSAToolbox import PSAToolbox

import tkinter
import tkinter.filedialog

import math

from IPython.display import HTML
from html import unescape

import random
import json
import copy
# comment: 从 cloudpss.model.implements.component 导入 Component 类
from cloudpss.model.implements.component import Component
# comment: 从 cloudpss.runner.result 导入 Result、PowerFlowResult、EMTResult 类
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
# comment: 从 cloudpss.model.revision 导入 ModelRevision 类
from cloudpss.model.revision import ModelRevision
# comment: 从 cloudpss.model.model 导入 Model 类
from cloudpss.model.model import Model

from scipy import optimize

from string import Template

# comment: 定义一个名为 is_number 的函数，用于判断给定字符串 s 是否能转换为数字
def is_number(s):
    # comment: 尝试将字符串 s 转换为浮点数
    try:
        float(s)
        # comment: 如果成功转换，返回 True
        return True
    except ValueError:
        # comment: 如果转换失败（ValueError），则跳过
        pass

    # comment: 尝试使用 unicodedata 模块处理 unicode 数字
    try:
        import unicodedata
        # comment: 尝试将字符串 s 转换为数字字符
        unicodedata.numeric(s)
        # comment: 如果成功转换，返回 True
        return True
    except (TypeError, ValueError):
        # comment: 如果转换失败（TypeError 或 ValueError），则跳过
        pass

    # comment: 如果以上所有尝试都失败，返回 False
    return False


# %% [markdown]
# # comment: 调相机选址定容相关分析模块S_S_SyncComp
# # comment: 本模块基于StabilityAnalysis模块构建。实现电网稳定问题的高级分析。实现了新增调相机、计算电压敏感度VSI、计算故障严重程度SI等功能。

# comment: 定义 S_S_SyncComp 类，继承自 PSAToolbox
class S_S_SyncComp(PSAToolbox):
    # comment: 类的初始化方法
    def __init__(self):
        # comment: 调用父类 PSAToolbox 的初始化方法
        super(S_S_SyncComp,self).__init__()
        # comment: 更新 compNames 属性，添加自定义组件的名称映射
        self.compNames.update({'SyncGeneratorRouter':'SA_同步发电机',                          '_newBus_3p':'SA_三相母线',                              '_PSASP_AVR_11to12':'SA_调压器11-12型',                              '_newTransformer_3p2w':'SA_双绕组变压器',                              '_newShuntLC_3p':'SA_注入动态无功',
                              '_newGain':'SA_Gain', 'HW_PCS_TEST_Mask':'SA_PCS'})
        # comment: 定义调相机画布的 ID
        self.cSyncCid = 'canvas_AutoSA_Sync_Compensators'
        # comment: 定义动态注入无功画布的 ID
        self.cDynQid = 'canvas_AutoSA_Dynamic_Q'
        
        
    # comment: 创建 SSSCACAvas 方法，用于创建调相机分析的画布
    def createSSSCACanvas(self):
        # comment: 创建调相机分析画布
        self.createCanvas(self.cSyncCid,'新增调相机分析')
        # comment: 创建动态注入无功画布
        self.createCanvas(self.cDynQid,'动态注入无功')
        
        # comment: 添加一个名为 'SSSCA_Const-0' 的常量组件，值为 "0"
        nameTemp = 'SSSCA_Const-0'
        # comment: 在画布 self.cSyncCid 中添加 '_newConstant' 类型的组件
        self.addCompInCanvas(self.compLib['_newConstant'], key = 'SSSCA_Const',canvas = self.cSyncCid,                     args = {'Name':nameTemp,"Value": "0"}, pins = {'0':'SSSCA_Const-0'},label = nameTemp)
        
        # comment: 添加一个名为 'SSSCA_Const-1' 的常量组件，值为 "1"
        nameTemp = 'SSSCA_Const-1'
        # comment: 在画布 self.cSyncCid 中添加 '_newConstant' 类型的组件
        self.addCompInCanvas(self.compLib['_newConstant'], key = 'SSSCA_Const',canvas = self.cSyncCid,                     args = {'Name':nameTemp,"Value": "1"}, pins = {'0':'SSSCA_Const-1'},label = nameTemp)
        
        # comment: 添加名为 'SSSCA_S2M' 的阶跃信号发生器组件
        nameTemp = 'SSSCA_S2M'
        argsTemp = {'Name':nameTemp, 'V0':'0', 'V1':'1', 'Time':'1'}
        # comment: 在画布 self.cSyncCid 中添加 '_newStepGen' 类型的组件
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'SSSCA_S2M',canvas = self.cSyncCid,                     args = argsTemp, pins = {'0':'@SSSCA_S2M'},label = nameTemp)
        # comment: 添加名为 'SSSCA_L2N' 的阶跃信号发生器组件
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'SSSCA_L2N',canvas = self.cSyncCid,                     args = argsTemp, pins = {'0':'@SSSCA_L2N'},label = nameTemp)

        # comment: 生成新的线路位置
        self.newLinePos(self.cSyncCid)
        
        
    # comment: 获取 xData 中 x 所在区间的索引
    def getXInterval(self, xData,x):
        nsize = len(xData)
        upperLimit = nsize-1;
        lowerLimit = 0;
        z = math.floor((upperLimit+lowerLimit) / 2);
        # comment: 使用二分查找法
        while (z>=0 or z< (nsize-1)):
            # comment: 如果 xData[z] 大于 x
            if(xData[z]>x):
                # comment: 如果 z 小于等于 0，则设置 z 为 0 并跳出
                if(z<=0):
                    z = 0;
                    break;
                # comment: 否则，更新 upperLimit 并重新计算 z
                else:
                    upperLimit = z;
                    z = math.floor((upperLimit+lowerLimit) / 2);
            # comment: 如果 xData[z+1] 小于 x
            elif(xData[z+1]<x):
                # comment: 如果 z+1 大于等于 nsize-1，则设置 z 为 nsize-1 并跳出
                if(z+1>=(nsize-1)):
                    z = (nsize-1);
                    break;
                # comment: 否则，更新 lowerLimit 并重新计算 z
                else:
                    lowerLimit = z+1;
                    z = math.floor((upperLimit+lowerLimit) / 2);
            # comment: 如果 x 落在 xData[z] 和 xData[z+1] 之间，则跳出
            elif(xData[z]<=x and xData[z+1]>=x):
                break;
            # comment: 其他情况，设置 z 为 0 并跳出
            else:
                z = 0;
                break;
        # comment: 返回找到的索引 z
        return z;
    
    # comment: 计算电压偏差（DV）
    def calculateDV(self,jobName, voltageMeasureK, result = None, Ts = 4, dT0 = 0.5, judge = [[0.1,3,0.75,1.25],[3,999,0.95,1.05]],VminR = 0.2, VmaxR = 1.8, ValidName = None):
        # comment: 获取指定仿真任务的 Job 信息
        job = self.project.getModelJob(jobName)[0]
        # comment: 获取仿真步长
        step_time = float(job['args']['step_time'])
        # comment: 获取仿真结束时间
        end_time = float(job['args']['end_time'])
        # comment: 如果未提供结果，则使用 runner 的当前结果
        if(result==None):
            result = self.runner.result
        # comment: 获取电压测量数据
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
#         plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
#         pdtV = 1 / plotFV;
        
        dVUj = []
        dVLj = []
        
        # comment: 初始化有效通道列表
        ValidNum = [i for i in range(len(Vresults))]
        
#         V0 = []
        # comment: 遍历每个电压测量结果
        for k in range(len(Vresults)):
            # comment: 计算初始时间范围
            ts = Ts - dT0;
            te = Ts;
        
            # comment: 获取当前通道的 x 和 y 值
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];
            # comment: 获取通道名称
            name = Vresults[k]['name'];
            # comment: 获取初始时间段内的索引
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 计算初始电压平均值
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
#             V0.append(Vaverage)
            
            # comment: 初始化电压偏差裕度
            dVUj_temp = 9999999;
            dVLj_temp = 9999999;

            # comment: 根据判断条件计算电压裕度
            for j in judge:
                ts = Ts+j[0]
                te = Ts+j[1]
                # comment: 确保时间不超过仿真结束时间
                if(ts>end_time):
                    ts = end_time;
                if(te>end_time):
                    te = end_time;  

                # comment: 获取当前时间段内的索引
                msV = self.getXInterval(vx,ts);
                meV = self.getXInterval(vx,te);
                # comment: 更新电压上限裕度
                dVUj_temp = min(dVUj_temp,j[3]*Vaverage - max(vy[msV:meV]))
                # comment: 更新电压下限裕度
                dVLj_temp = min(dVLj_temp,min(vy[msV:meV]) - j[2]*Vaverage)

            # comment: 添加当前通道的电压裕度
            dVUj.append(dVUj_temp)
            dVLj.append(dVLj_temp)
            
            # comment: 计算仿真结束时间附近的索引
            ts = end_time - dT0;
            te = end_time;

            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 检查结束时间电压是否在有效范围内
            if(max(vy[msV:meV])<VminR * Vaverage or min(vy[msV:meV])>VmaxR * Vaverage):
                ValidNum.remove(k) # comment: 如果不在，则将此通道从有效列表中移除
            # comment: 如果指定了 ValidName，则检查通道名称是否包含任一有效名称
            if(ValidName!= None):
                flag = 0
                for jj in ValidName:
                    if(jj in name):
                        flag = 1;
                # comment: 如果不包含，则将此通道从有效列表中移除
                if(flag==0):
                    ValidNum.remove(k)
        # comment: 返回电压上限裕度、电压下限裕度以及有效通道列表
        return dVUj,dVLj,ValidNum

    # comment: 计算故障严重程度指标（SI）
    def calculateSI(self,jobName, voltageMeasureK, result = None, Ts = 4, dT0 = 0.5, Tinterval = 0.11, T1 = 3, dV1 = 0.25, dV2 = 0.1, VminR = 0.2, VmaxR = 1.8):
        # comment: 获取指定仿真任务的 Job 信息
        job = self.project.getModelJob(jobName)[0]
        # comment: 获取仿真步长
        step_time = float(job['args']['step_time'])
        # comment: 获取仿真结束时间
        end_time = float(job['args']['end_time'])
        # comment: 如果未提供结果，则使用 runner 的当前结果
        if(result==None):
            result = self.runner.result
        # comment: 获取电压测量数据
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
#         plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
#         pdtV = 1 / plotFV;
        
        # comment: 初始化有效通道列表
        ValidNum = [i for i in range(len(Vresults))]
        
#         V0 = []
        SI = 0; # comment: 初始化 SI
        # comment: 遍历每个电压测量结果
        for k in range(len(Vresults)):
            # comment: 计算初始时间范围
            ts = Ts - dT0;
            te = Ts;
        
            # comment: 获取当前通道的 x 和 y 值
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];

            # comment: 获取初始时间段内的索引
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 计算初始电压平均值
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
#             V0.append(Vaverage)

            # comment: 计算仿真结束时间附近的索引
            ts = end_time - dT0;
            te = end_time;
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 检查结束时间电压是否在有效范围内
            if(max(vy[msV:meV])<VminR * Vaverage or min(vy[msV:meV])>VmaxR * Vaverage):
                ValidNum.remove(k) # comment: 如果不在，则将此通道从有效列表中移除
                continue # comment: 跳过当前通道，继续下一个

            # comment: 计算 Tinterval 和 T1 后的时间段索引
            ts = Ts + Tinterval;
            te = Ts + Tinterval + T1;
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);

            # comment: 累加 SI 值，计算在 (1-dV1) 和 (1+dV1) 之外的电压点比例
            SI += len([i for i in vy[msV:meV] if (i < (1-dV1)*Vaverage or i > (1+dV1)*Vaverage)]) / (meV-msV);
            # comment: 累加 SI 值，计算在 (1-dV2) 和 (1+dV2) 之外的电压点比例（从 meV 之后开始）
            SI += len([i for i in vy[meV:] if (i < (1-dV2)*Vaverage or i > (1+dV2)*Vaverage)]) / len(vy[meV:]);

        # comment: 根据有效通道数量计算平均 SI 值
        SI = SI / len(ValidNum);

        # comment: 返回 SI 值和有效通道列表
        return SI,ValidNum
    
    # comment: 计算电压敏感度指标（VSI）
    def calculateVSI(self, jobName, voltageMeasureK, dQMeasureK, busLabels, result = None, busNum = None, Ts = 4, dT = 1, ddT = 0.5):
        
        # comment: 获取指定仿真任务的 Job 信息
        job = self.project.getModelJob(jobName)[0]
        # comment: 获取仿真步长
        step_time = float(job['args']['step_time'])
        # comment: 如果未提供结果，则使用 runner 的当前结果
        if(result==None):
            result = self.runner.result
        # comment: 获取电压测量数据
        Vresults = result.getPlot(voltageMeasureK)['data']['traces']
        # plotFV = float(job['args']['output_channels'][voltageMeasureK][1]);
        # pdtV = 1 / plotFV;

        # comment: 如果未指定母线数量，则从仿真结束时间和 Ts 和 dT 计算
        if (busNum == None):
            busNum = (float(job['args']['end_time']) - Ts) / dT;

        # comment: 获取无功功率测量数据
        Qresults = result.getPlot(dQMeasureK)['data']['traces']
        # comment: 获取 Q 通道名称列表
        QChannelNames = [self.project.getComponentByKey(i).pins['0'] for i in \
            self.project.getModelJob(jobName)[0]['args']['output_channels'][dQMeasureK]['4']];
        print(QChannelNames) # comment: 打印 Q 通道名称
        # comment: 创建 QMap，用于将通道索引映射到母线编号
        QMap1 = [int(re.search('#SA_VSI_DQ_(.*?)$',QChannelNames[i]).group(1)) for i in range(busNum)];
        QMap = [QMap1.index(i) for i in range(busNum)];


            

        # plotFQ = float(job['args']['output_channels'][dQMeasureK][1]);
        # pdtQ = 1 / plotFQ;


        VSIij = [] # comment: 初始化二维 VSI 列表
        VSIi = [] # comment: 初始化一维 VSI 列表



        # comment: 计算结束时间附近的参考电压平均值
        ts = float(job['args']['end_time']) - dT + ddT ;
        te = float(job['args']['end_time']);
        V0 = []
        # comment: 遍历每个电压测量结果
        for k in range(len(Vresults)):
            vx = Vresults[k]['x'];
            vy = Vresults[k]['y'];
            # comment: 如果数据为空，则填充 0
            if(vy[0]==None):
                vy = [0 for i in range(len(vy))]
            # comment: 获取时间段索引
            msV = self.getXInterval(vx,ts);
            meV = self.getXInterval(vx,te);
            # comment: 计算平均电压
            Vaverage = sum(vy[msV:meV]) / len(vy[msV:meV])
            V0.append(Vaverage) # comment: 添加到 V0 列表

        # comment: 获取电压测量通道名称
        Mnames = result.getPlotChannelNames(voltageMeasureK)
        # comment: 遍历每个母线
        for n in range(busNum):
            # comment: 计算当前母线对应的无功注入时间段
            ts = Ts + dT * n;
            te = Ts + dT * n + ddT;

            # comment: 计算注入前的时间段
            ts0 = Ts + dT * n - ddT;
            te0 = Ts + dT * n;
        #             msV = int(ts / pdtV)
        #             meV = int(te / pdtV)
        #             msQ = int(ts / pdtQ)
        #             meQ = int(te / pdtQ)

            # comment: 获取 Q 数据的 x 和 y 值
            Qx = Qresults[QMap[n]]['x']
            Qy = Qresults[QMap[n]]['y']

            # comment: 获取 Q 数据的时间段索引
            msQ = self.getXInterval(Qx,ts);
            meQ = self.getXInterval(Qx,te);

        #             Qaverage = sum(Qy[msQ:meQ]) / (meQ - msQ)
            Qaverage = Qy[meQ-1] # comment: 使用 Q 数据的末尾值作为平均值
            
            V1 = [] # comment: 初始化 V1 列表
            
            # comment: 遍历每个电压测量结果
            for k in range(len(Vresults)):
                vx = Vresults[k]['x'];
                vy = Vresults[k]['y'];
                # comment: 如果数据为空，则填充 0 并打印警告
                if(vy[0]==None):
                    print(Mnames[k])
                    vy = [0 for i in range(len(vy))]
                # comment: 获取注入后和注入前的时间段索引
                msV = self.getXInterval(vx,ts);
                meV = self.getXInterval(vx,te);
                msV0 = self.getXInterval(vx,ts0);
                meV0 = self.getXInterval(vx,te0);
        #                 Vtemp = V0[k] - max(vy[msV:meV]) 
                
                # comment: 计算电压变化量除以无功变化量，得到 VSI 值
                Vtemp = sum(vy[msV0:meV0]) / (meV0 - msV0) - sum(vy[msV:meV]) / (meV - msV)
                V1.append(Vtemp / Qaverage) # comment: 将 VSI 值添加到 V1 列表
            VSIij.append(V1) # comment: 将 V1 添加到 VSIij 列表
            VSIi.append(sum(V1) / len(V1)) # comment: 计算平均 VSI 并添加到 VSIi 列表


        VSIiDict = {} # comment: 初始化 VSIi 字典
        VSIijDict = {} # comment: 初始化 VSIij 字典
        # comment: 填充 VSIiDict 和 VSIijDict
        for i in range(len(busLabels)):
            VSIiDict[busLabels[i]] = VSIi[i]
            VSIijDict[busLabels[i]] = {}
            for j in range(len(Mnames)):
                VSIijDict[busLabels[i]][Mnames[j]] = VSIij[i][j]
        # comment: 将 VSIiDict 和 VSIijDict 封装到 VSIresultDict
        VSIresultDict = {'VSIi':VSIiDict,'VSIij':VSIijDict}
        # comment: 返回 VSI 结果字典
        return VSIresultDict
        
        
    # comment: 添加 VSI 量测
    def addVSIMeasure(self, jobName,VSIQkeys,VMin = None, VMax = None, NameSet = None, NameKeys = None, freq = None,Nbus = 10,  dT = 0.5, Ts = 4):
        '''
            jobName: 仿真Job名字
            添加VSI的量测，包括量测引脚的添加、在Job中添加输出通道
            可以用Vmin，VMax，NameSet，NameKeys来筛选用于电压量测的母线，各条件取交集。
            freq为输出频率。
        '''
        # comment: 获取指定仿真任务的 Job 信息
        job = self.project.getModelJob(jobName)[0]
        
        
        # comment: 添加电压量测并获取筛选后的母线列表
        screenedBus = self.addVoltageMeasures(jobName, VMin, VMax, NameSet, NameKeys, freq, PlotName = 'VSI_节点电压量测');
        # comment: 获取电压量测的输出通道索引
        voltageMeasureK = len(job['args']['output_channels']) - 1;
        
        # comment: 更新仿真结束时间
        job['args']['end_time'] = Nbus * dT + Ts;

        # comment: 添加无功功率测量，指定组件类型、引脚、组件列表和绘图名称
        self.addComponentOutputMeasures(jobName, 'model/CloudPSS/_newShuntLC_3p', 'Q', [],compList = VSIQkeys, dim = 1, plotName = 'VSI_动态注入无功量测', freq = freq)
        
        # id1, label = self.addChannel('#SA_VSI_DQ',1)
        # self.addOutputs(jobName, {'0':'VSI_动态注入无功量测', '1':freq, '2':'compressed', '3':1, '4':[id1]})
        # comment: 计算无功功率量测的输出通道索引
        dQMeasureK = voltageMeasureK + 1;

        # comment: 返回电压量测索引、无功量测索引和筛选后的母线列表
        return voltageMeasureK, dQMeasureK, screenedBus
        
    
    # comment: 添加 VSI 无功源
    def addVSIQSource(self, busKeys, V = 220, S = 1, Ts = 4, dT = 1, ddT = 0.5):
        '''
            busKeys:{busKey1, busKey2}
            V:添加的动态注入无功源的基准电压，单位为kV
            S:添加的动态注入无功源的基准无功，单位为MVar
            dT:对每个母线测试时所占用的仿真时长,s
        '''
        signalDict = {}
        VSIQKeys = []
        
        # comment: 遍历每个母线键
        for k in range(len(busKeys)):
            busK = busKeys[k];
# comment: 添加 shuntLC (并联电抗器/电容器)
            tempID = 'SA_newShuntLC_3p_'+str(k);
            nameTemp = self.compNames['_newShuntLC_3p']+str(k)
            # comment: 构建 shuntLC 的参数
            argsTemp = {'Name':nameTemp,'Dim':'3', 'v':str(float(self.project.getComponentByKey(busK).args['V'])*float(self.project.getComponentByKey(busK).args['VBase'])), 's':str(-S), "Q": '#SA_VSI_DQ_'+str(k)}
            pinsTemp = {"0": 'SA_VSI_C_'+str(k)}
            
            # comment: 在画布 self.cDynQid 中添加 '_newShuntLC_3p' 类型的组件
            id1, label = self.addCompInCanvas(self.compLib['_newShuntLC_3p'], key = tempID, canvas = self.cDynQid,                     args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
            VSIQKeys.append(id1) # comment: 将组件 ID 添加到 VSIQKeys 列表
# comment: 添加众多开关
            
            tempID = 'SA_VSI_Breaker_'+str(k);
            nameTemp = 'SA_VSI分析_断路器_'+str(k);
            ctrlSigName = '@SA_VSI分析_断路器_'+str(k);
            argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '0'}
            
            # comment: 获取母线的引脚名称
            pinName = self.project.getComponentByKey(busK).pins['0']
            pinsTemp = {"0": pinName,"1": 'SA_VSI_C_'+str(k)}
        
            # comment: 在画布 self.cDynQid 中添加 '_newBreaker_3p' 类型的组件 (断路器)
            id1, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = tempID, canvas = self.cDynQid,                         args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 添加开关信号源
            nameTemp = 'SA_VSI分析_断路器_信号'
            argsTemp = {'Name':nameTemp, 'INIT':'0', 'Drop':'1', 'T1':str(Ts + k * dT), 'T2':str(Ts + k * dT + ddT)}
            # comment: 在画布 self.cDynQid 中添加 '_newDropGen' 类型的组件 (信号发生器)
            ids, labes = self.addCompInCanvas(self.compLib['_newDropGen'], key = 'SA_VSI_Breaker_Sig',canvas = self.cDynQid,                         args = argsTemp, pins = {'0':ctrlSigName},label = nameTemp, MaxX = 500)
            
        # comment: 生成新的线路位置
        self.newLinePos(self.cDynQid)
        # comment: 返回 VSIQKeys 列表
        return VSIQKeys

        
    # comment: 添加静态无功补偿器（SVC）
    def addSVC(self, busKey, S = 1, Ts = 4, Te = 999):
        '''
            busKeys:{busKey1, busKey2}
            V:添加的动态注入无功源的基准电压，单位为kV
            S:添加的动态注入无功源的基准无功，单位为MVar
            dT:对每个母线测试时所占用的仿真时长,s
        '''
        # comment: 获取母线的基础电压
        V = float(self.project.getComponentByKey(busKey).args['VBase']);
        # comment: 获取母线的引脚名称
        busPin = self.project.getComponentByKey(busKey).pins['0'];
        
        # comment: 获取母线名称
        busName = self.project.getComponentByKey(busKey).label;
        switchPin = 'SVC_Switch_'+busName; # comment: 定义 SVC 开关的引脚名称
# comment: 添加 shuntLC
        tempID = 'SA_SVC';
        nameTemp = 'SA_SVC'+busName
        argsTemp = {'Name':nameTemp,'Dim':'3', 'v':str( V), 's':str(S)}
        pinsTemp = {"0": switchPin}
        
        # comment: 在画布 self.cDynQid 中添加 '_newShuntLC_3p' 类型的组件 (并联电抗器/电容器)
        id1, label = self.addCompInCanvas(self.compLib['_newShuntLC_3p'], key = tempID, canvas = self.cDynQid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        # comment: 生成新的线路位置
        self.newLinePos(self.cDynQid)
        
# comment: 添加开关
        tempID = 'SA_SVC_Breaker';
        nameTemp = 'SA_SVC_Breaker'+busName;
        ctrlSigName = '@SVC_'+busName; # comment: 定义控制信号名称
        argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '0'}
        
        pinsTemp = {"0": busPin,"1": switchPin}
    
        # comment: 在画布 self.cDynQid 中添加 '_newBreaker_3p' 类型的组件 (断路器)
        id2, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = tempID, canvas = self.cDynQid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 添加开关信号源
        nameTemp = 'SA_VSI分析_断路器_信号'
        argsTemp = {'Name':nameTemp, 'INIT':'0', 'Drop':'1', 'T1':str(Ts), 'T2':str(Te)}
        # comment: 在画布 self.cDynQid 中添加 '_newDropGen' 类型的组件 (信号发生器)
        ids, labes = self.addCompInCanvas(self.compLib['_newDropGen'], key = 'SA_SVC_Breaker_Sig',canvas = self.cDynQid, args = argsTemp, pins = {'0':ctrlSigName},label = nameTemp, MaxX = 500)
            
        # comment: 生成新的线路位置
        self.newLinePos(self.cDynQid)

        # comment: 返回组件 ID 列表
        return [id1,id2,ids]

    # comment: 添加 PCS (Power Conversion System) 组件
    def addPCSComp(self, busKey, S = 10, PCSArgs = None):
        '''
            busKeys:{busKey1, busKey2}
            S:添加的动态注入无功源的基准无功，单位为MVar
        '''
        # comment: 获取母线的基础电压和标称电压
        V = float(self.project.getComponentByKey(busKey).args['VBase'])*float(self.project.getComponentByKey(busKey).args['V']);
        # comment: 获取母线的引脚名称
        busPin = self.project.getComponentByKey(busKey).pins['0'];
        # comment: 获取母线名称
        busName = self.project.getComponentByKey(busKey).label;
        # comment: 定义 PCS 引脚的连接
        pinsTemp = {"AC": busPin, "P": busPin + ".SA_PCS_P", "Q": busPin + ".SA_PCS_Q"};

        tempID = 'SA_HW_PCS';
        nameTemp = self.compNames['HW_PCS_TEST_Mask']
        
        # comment: 获取 PCS 组件的默认参数
        argsTemp = self.compLib['HW_PCS_TEST_Mask'];
        # comment: 如果提供了 PCSArgs，则更新参数
        if(PCSArgs!=None):
            argsTemp.update(PCSArgs);
        # comment: 计算 PCS 模块的数量
        argsTemp['Num'] = str(S/0.2);
        # comment: 设置 PCC (并网点) 电压
        argsTemp['Vpcc'] = str(V)
        # comment: 在画布 self.cDynQid 中添加 'HW_PCS_TEST_Mask' 类型的组件
        ids, labes = self.addCompInCanvas(self.compLib['HW_PCS_TEST_Mask'], key = tempID,canvas = self.cDynQid, args = argsTemp, pins = pinsTemp,label = nameTemp, MaxX = 500)
        # comment: 生成新的线路位置
        self.newLinePos(self.cDynQid)
        # comment: 返回组件 ID 列表
        return ids


    # comment: 添加同步调相机
    def addSyncComp(self, busKey, pfResult, syncArgs = None,transArgs = None, busArgs = None, AVRComp = None, AVRArgs = None):
        '''
            transArgs:{"Smva": "额定容量","X1": "正序漏电抗","Rl": "正序漏电阻"}
            syncArgs:{"Smva": "额定容量","V": "额定相电压有效值","freq": "额定频率"...}
        '''
        
#         nameTemp = 'SSSCA_同步调相机'
#         argsTemp = {'Name':nameTemp, 'VT_o':str(fault_start_time), 'fe':str(fault_end_time),'ft':str(fault_type)}
        
        data = pd.DataFrame()
        # comment: 获取潮流计算结果中的母线数据
        pfBusResult=pfResult.getBuses() 
        # comment: 查找对应母线的索引
        pfBusIndex = pfBusResult[0]['data']['columns'][0]['data'].index(busKey);
        # comment: 获取母线的电压幅值和相角
        vm = pfBusResult[0]['data']['columns'][2]['data'][pfBusIndex];
        va = pfBusResult[0]['data']['columns'][3]['data'][pfBusIndex];
        # comment: 获取母线的基准电压
        VB = float(self.project.getComponentByKey(busKey).args['VBase'])
        
#         if(name==None):
#             name = '新调相机';
        
#         busName = name+'-母线';
#         transName = name+'-变压器';
#         avrName = name+'-AVR';
#         syncName = name+'-电机';

# comment: 处理同步电机
        tempID = 'SA_Sync';
        # comment: 获取同步发电机组件的名称
        nameTemp = self.compNames['SyncGeneratorRouter']
        
        
        # comment: 统计组件数量
        if(tempID not in self.compCount.keys()):
            self.compCount[tempID] = 0;
        count = self.compCount[tempID] + 1;
        nameCount = nameTemp + "_" + str(count)
        syncName = nameCount;
        # comment: 添加同步电机 L2N 阶跃信号发生器
        argsTemp = {'Name':syncName+'.L2N', 'V0':'0', 'V1':'1', 'Time':'2'}
        ids, label = self.addCompInCanvas(self.compLib['_newStepGen'], key = tempID+'_L2N',canvas = self.cSyncCid,  args = argsTemp, pins = {'0':'@'+syncName+'.L2N'},label = syncName+'.L2N')
        # comment: 添加同步电机 S2M 阶跃信号发生器
        argsTemp = {'Name':syncName+'.S2M', 'V0':'0', 'V1':'1', 'Time':'1'}
        ids, label = self.addCompInCanvas(self.compLib['_newStepGen'], key = tempID+'_S2M',canvas = self.cSyncCid,  args = argsTemp, pins = {'0':'@'+syncName+'.S2M'},label = syncName+'.S2M')

        # comment: 构建同步电机的参数
        argsTemp = {'Name':nameTemp,'pf_P':'0', 'pf_Q':'0', 'pf_V':str(vm), 'pf_Theta':str(va),
                   "V_mag": str(vm), "V_ph": str(va), "AP": "0", "RP": "0",
                   "s2m_o": "","l2n_o": "","Tm0_o": "","wr_o": "","theta_o": "",
                   "loadangle_o": "","loadangle_so": "","IT_o": "","PT_o": "","QT_o": "","IT_inst": "",
                   "VT_o":'#'+syncName+'.VT', "Ef0_o":'#'+syncName+'.Ef0',
                   'StartupType':'4','s2m':'@'+syncName+'.S2M','l2n':'@'+syncName+'.L2N','BusType':'0'}
        # comment: 如果提供了 syncArgs，则更新参数
        if(syncArgs!=None):
            argsTemp.update(syncArgs);
        
        # comment: 定义同步电机的引脚连接
        pinsTemp = {"0": syncName,
                    "1": "",
                    "2": "SSSCA_Const-0",
                    "3": syncName+".Te",
                    "4": syncName+".Ef",
                    "5": syncName+".If"}
        
        # comment: 在画布 self.cSyncCid 中添加 'SyncGeneratorRouter' 类型的组件
        Syncid1, label = self.addCompInCanvas(self.compLib['SyncGeneratorRouter'], key = tempID, canvas = self.cSyncCid,  args = argsTemp, pins = pinsTemp, label = syncName, MaxX = 500)
        
        # comment: 计算同步电机的基准电压 (VBSync)
        VBSync = float(self.project.getComponentByKey(Syncid1).args['V']) * math.sqrt(3);

        syncMVA = self.project.getComponentByKey(Syncid1).args['Smva'];
        
# comment: 处理母线
        tempID = 'SA_Sync_Bus';
        nameTemp = self.compNames['_newBus_3p']
        # comment: 构建新的母线参数
        argsTemp = {'Name':nameTemp,'Freq':'50', 'VBase':str(VBSync), 'V':str(vm), 'Theta':str(va),"Vabc": "","Vrms": ""}
        # comment: 如果提供了 busArgs，则更新参数
        if(busArgs!=None):
            argsTemp.update(busArgs);
        # comment: 定义母线的引脚连接
        pinsTemp = {"0": syncName}
        # comment: 在画布 self.cSyncCid 中添加 '_newBus_3p' 类型的组件
        Busid1, label = self.addCompInCanvas(self.compLib['_newBus_3p'], key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp + "_" + str(count), MaxX = 500)
        
# comment: 处理变压器
        tempID = 'SA_Transformer_3p2w';
        nameTemp = self.compNames['_newTransformer_3p2w']
        # comment: 构建变压器参数
        argsTemp = {'Name':nameTemp, 'V1':str(VBSync), 'V2':str(VB), 'Xl':'0.1', 'Rl':'0', 'Tmva':str(100)}
        # comment: 如果提供了 transArgs，则更新参数
        if(transArgs!=None):
            argsTemp.update(transArgs);
            
        # comment: 获取连接母线的引脚名称
        busName = self.project.getComponentByKey(busKey).pins['0']
        # comment: 定义变压器的引脚连接
        pinsTemp = {"0": syncName,"1": busName}
        # comment: 在画布 self.cSyncCid 中添加 '_newTransformer_3p2w' 类型的组件
        Transid1, label = self.addCompInCanvas(self.compLib['_newTransformer_3p2w'], key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp + "_" + str(count), MaxX = 500)
        
# comment: 处理 AVR (自动电压调节器)
        tempID = 'SA_PSASP_AVR_11to12';
        # comment: 如果未提供 AVRComp，则使用默认的 AVR 组件
        if(AVRComp==None):
            AVRComp = self.compLib['_PSASP_AVR_11to12'];
            nameTemp = self.compNames['_PSASP_AVR_11to12']
            # comment: 定义 AVR 的引脚连接 (PSSAP 11-12 型)
            pinsTemp = {"0": syncName+".Vref",
                        "1": "SSSCA_Const-0",
                        "2": '#'+syncName+'.VT',
                        "3": '#'+syncName+'.Ef0',
                        "4": syncName+".If",
                        "5": '@'+syncName+'.S2M',
                        "6": syncName+".Vref0",
                        "7": syncName+".Ef" }
        # comment: 如果提供了 AVRComp，则解析其定义获取名称
        else:
            definition = AVRComp["definition"]
            nameTemp = definition.split('/')[-1]
        argsTemp = {}
        # comment: 如果提供了 AVRArgs，则更新参数
        if(AVRArgs!=None):
            argsTemp.update(AVRArgs);
        # comment: 在画布 self.cSyncCid 中添加 AVR 组件
        AVRid1, label = self.addCompInCanvas(AVRComp, key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
# comment: 处理 newGain (增益模块)
        tempID = 'SA_newGain';
        nameTemp = self.compNames['_newGain']
        argsTemp = {'G':'1'} # comment: 设置增益为 1
        # comment: 定义增益模块的引脚连接
        pinsTemp = {"0": syncName+".Vref0",
                    "1": syncName+".Vref"}
        # comment: 在画布 self.cSyncCid 中添加 '_newGain' 类型的组件
        Gainid1, label = self.addCompInCanvas(self.compLib['_newGain'], key = tempID, canvas = self.cSyncCid, args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        
        
        # comment: 生成新的线路位置
        self.newLinePos(self.cSyncCid)
        
        # comment: 返回所有新增组件的 ID 列表
        return [Syncid1,Busid1,Transid1,AVRid1,Gainid1]

# %% [markdown]
# # comment: OtherData
# %% [markdown]
# ## comment: getCompLib

# %%
# comment: 定义 getCompLib 函数，用于获取组件库
def getCompLib(tk, apiURL, spr, compDefLib = {}, name = None):
    # comment: 设置 CloudPSS 的认证 token
    cloudpss.setToken(tk)
    # comment: 设置 CloudPSS API 的 URL 环境变量
    os.environ['CLOUDPSS_API_URL'] = apiURL
    # comment: 从 CloudPSS 平台获取指定项目
    sproject = cloudpss.Model.fetch(spr)
    compLib = {} # comment: 初始化组件库字典
    # comment: 如果 compDefLib 为空，则初始化默认组件定义库
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
    # comment: 反转 compDefLib，用于查找键
    compDefLib_inv = {v: k for k, v in compDefLib.items()}
    # comment: 遍历项目中的所有组件
    for i in sproject.getAllComponents().keys():
        comp = sproject.getAllComponents()[i].toJSON() # comment: 将组件转换为 JSON 格式
        # comment: 检查组件是否为图表组件
        if('diagram-component' in comp['shape']):
            compcp = copy.deepcopy(comp); # comment: 深度复制组件
            compcp['style'] = {} # comment: 清空样式
            # comment: 如果组件定义不在反转的定义库中
            if(comp['definition'] not in compDefLib_inv.keys()):
                pattern = '[^/]*/[^/]*/([^/]*)$' # comment: 定义正则表达式模式
                zone = re.search(pattern,comp['definition']); # comment: 搜索匹配的区域
                compLib[zone.group(1)] = compcp; # comment: 将组件添加到组件库
            else:
                compLib[compDefLib_inv[comp['definition']]] = compcp; # comment: 使用已知的键添加组件
    # comment: 如果名称为空，则设置为 'saSource.json'
    if(name==None):
        name = 'saSource.json'
    # comment: 将组件库保存为 JSON 文件
    with open(name, "w", encoding='utf-8') as f:
        f.write(json.dumps(compLib, indent=4))
    # comment: 返回组件库
    return compLib

# %% [markdown]
# ## comment: fetchCompData

# %%
# comment: 定义 GraphQL 查询模板，用于获取模型数据
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


# comment: 定义 fetchCompData 函数，用于获取指定 RID 的组件数据
def fetchCompData(rids=None):

    # comment: 如果未指定 rids，则抛出异常
    if rids is None:
        raise Exception('rids must be specified')
    models = [] # comment: 初始化模型列表
    i = 0
    # comment: 遍历每个 RID，生成 GraphQL 查询字符串
    for rid in rids:
        i += 1
        models.append(
            MODE_TEMPLATE.safe_substitute(model='model' + str(i), rid=rid))

    query = "query { %s }" % ' '.join(models) # comment: 拼接完整的 GraphQL 查询字符串

    # comment: 发送 GraphQL 请求获取数据
    data = cloudpss.utils.graphql_request(query, {})

    # comment: 返回数据部分
    return data['data']



# %% [markdown]
# ## comment: ParaDict

# %%
# comment: 定义 genParaDict 函数，用于生成参数字典和引脚字典
def genParaDict(zdmToken,internalapiurl,projName):
    ParaDict = {} # comment: 初始化参数字典
    PinDict = {} # comment: 初始化引脚字典
    
#     zdmToken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzMsInVzZXJuYW1lIjoiQ2xvdWRQU1MiLCJzY29wZXMiOlsidW5rbm93biJdLCJ0eXBlIjoiU0RLIiwiZXhwIjoxNjYxNTgwNDc4LCJpYXQiOjE2MzAwNDQ0MjR9.KWqs-InItjYIGmXC-zKUGqPxBZZyxj52DHt_q7ftdP3eUM65a5ZJgQVn6hYpHEJYRShB_u_nOD5MivHdsnZsYf-F8U3Jyhel9BBVUkKA3LzbaEQgPHFAg50ftVW86HXnUlUC2oiV_uleH_g8tt9N__RGTnMV3VDl23Ie9uICQnI'
#     internalapiurl = 'https://internal.cloudpss.net/';
#     projName = 'model/greyd/AllMachineCtrlComp';
    # comment: 设置 CloudPSS 的认证 token
    cloudpss.setToken(zdmToken)
    # comment: 设置 CloudPSS API 的 URL 环境变量
    os.environ['CLOUDPSS_API_URL'] = internalapiurl
    # comment: 获取指定项目
    prjtmp = cloudpss.Model.fetch(projName)
    allcomp = prjtmp.getAllComponents(); # comment: 获取项目中的所有组件
    allcompList = [] # comment: 初始化所有组件定义列表
    
    
    
    
    # comment: 遍历所有组件，将它们的定义添加到 allcompList
    for cmp in allcomp.keys():
        cmpJSN = allcomp[cmp].toJSON()
        allcompList.append(cmpJSN['definition']);
    # comment: 批量获取组件的原始数据
    RawDataList = fetchCompData(allcompList);
    # comment: 遍历原始数据列表，填充 ParaDict 和 PinDict
    for rawData in RawDataList.values():
        
        # print(rawData)
        
        
        ParaDict[rawData['rid']] = {}
        ParaDict[rawData['rid']]['DiscriptName'] = rawData['name']
        PinDict[rawData['rid']] = {}
        
#         rawData['revision']['parameters'][0]['name']
#         print(rawData)
        # comment: 遍历参数，添加到 ParaDict
        for item0 in rawData['revision']['parameters']:
            for item1 in item0['items']:
                ParaDict[rawData['rid']][item1['key']] = item1;
        # comment: 遍历引脚，添加到 PinDict
        for item0 in rawData['revision']['pins']:
            PinDict[rawData['rid']][item0['key']] = item0;
            
            
            
    #     ParaDict[rawData['rid']]['DiscriptName'] = rawData['revision']['parameters'][0]['name']
    #     ParaDict[rawData['rid']] = rawData['revision']['parameters'][0]
    #     print(rawData['rid'])
    #     print(rawData['revision']['parameters'][0].keys())
    #     print(rawData['revision']['parameters'][0]['items'][1])
#     ParaDict['model/CloudPSS/_PSASP_PSS_5']
    # comment: 返回参数字典和引脚字典
    return ParaDict,PinDict
# comment: 初始化S_S_SyncComp
S_S_SyncComp = ""

# comment: 将第一个代码块内容整理成字符串 (三、主要流程)
content_main_process = """
1、job = cloudpss.function.currentJob()
2、cloudpss.setToken('YOUR_CLOUDPSS_AUTH_TOKEN')
3、os.environ['CLOUDPSS_API_URL'] = 'YOUR_CLOUDPSS_API_URL'
4、print("第一步：获取 CloudPSS 模型...")
5、model = cloudpss.Model.fetch('YOUR_CLOUDPSS_MODEL_RID')
6、print("模型获取成功。")
"""

# comment: 将第二个代码块内容整理成字符串 (第一步：创建 CloudPSSSimulationHandler 类的实例)
content_create_handler = """
7、print("--- 第一步：创建CloudPSSSimulationHandler类的实例 ---")
8、handler = CloudPSSSimulationHandler()
9、print("CloudPSSSimulationHandler实例创建成功。")
"""

# comment: 将第三个代码块内容整理成字符串 (initialize_environment 函数)
content_initialize_env = """
10、def initialize_environment():
11、import os
12、import pandas as pd
13、import time
14、import sys, os
15、import cloudpss
16、import math
17、import numpy as np
18、from jobApi1 import fetch, fetchAllJob, abort
19、from CaseEditToolbox import CaseEditToolbox
20、from CaseEditToolbox import is_number
21、from PSAToolbox import PSAToolbox
22、import json
23、import random
24、import re
25、import nest_asyncio
26、nest_asyncio.apply()
"""

# comment: 将第四个代码块内容整理成字符串 (initialize_cloudpss 函数)
content_initialize_cloudpss = """
27、def initialize_cloudpss():
28、tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInNjb3BlcyI6W10sInR5cGUiOiJhcHBseSIsImV4cCI6MTcxODc2MzYzMCwiaWF0IjoxNjg3NjU5NjMwfQ.1h5MVO8PATPT5ujlb1J9CAJzwqMWhzDagDk9IQ1gbNhA2TtOLRqYnlyZ0N2atQY1t_agxvYK4Nr4xX1aJYt1lA'
29、apiURL = 'http://cloudpss-calculate.local.ddns.cloudpss.net/'
30、username = 'admin'
31、projectKey = 'QS_20230515_1530_Mod'
32、with open('saSource.json', 'r', encoding='utf-8') as f:
33、compLib = json.load(f)
34、ce = PSAToolbox()
35、ce.setConfig(tk, apiURL, username, projectKey, comLibName='saSource.json')
36、return ce
"""

# comment: 合并和去重函数
# comment: 定义 merge_and_deduplicate 函数，用于合并和去重代码内容
def merge_and_deduplicate(existing_content_str, new_content_str, current_index):
    # comment: 将现有内容按行分割并去空白，存入集合以便快速查找
    existing_lines_set = set(line.strip() for line in existing_content_str.split('\n') if line.strip())
    
    # comment: 将新内容按行分割并去空白
    new_lines = [line.strip() for line in new_content_str.split('\n') if line.strip()]
    
    # comment: 存储独有的新行
    unique_new_lines = []
    # comment: 遍历新内容行，如果不在现有内容中，则添加到 unique_new_lines
    for line in new_lines:
        if line not in existing_lines_set:
            unique_new_lines.append(line)
    
    # comment: 如果没有新的独有行，则直接返回原内容和索引
    if not unique_new_lines:
        return existing_content_str, current_index
    
    # comment: 构建合并后的内容
    merged_content = existing_content_str
    # comment: 如果合并内容不为空且不是以换行符结尾，则添加换行符
    if merged_content and not merged_content.endswith('\n'):
        merged_content += '\n' 

    # comment: 遍历独有的新行，添加到合并内容中并更新索引
    for line in unique_new_lines:
        current_index += 1
        # comment: 避免连续的空行出现在输出中
        if line: 
            merged_content += f"{current_index}、{line}\n"
    
    # comment: 返回合并后的内容和新索引
    return merged_content, current_index

# comment: 首次循环，S_S_SyncComp为空
index_counter = 0

# comment: 处理第一个代码块
S_S_SyncComp, index_counter = merge_and_deduplicate(S_S_SyncComp, content_main_process, index_counter)
# comment: 处理第二个代码块
S_S_SyncComp, index_counter = merge_and_deduplicate(S_S_SyncComp, content_create_handler, index_counter)
# comment: 处理第三个代码块
S_S_SyncComp, index_counter = merge_and_deduplicate(S_S_SyncComp, content_initialize_env, index_counter)
# comment: 处理第四个代码块
S_S_SyncComp, index_counter = merge_and_deduplicate(S_S_SyncComp, content_initialize_cloudpss, index_counter)

print(S_S_SyncComp)