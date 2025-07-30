import os
import pandas as pd
import time
import sys,os

#sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
#comment: 导入 cloudpss 库，用于与 CloudPSS api 进行交互
import cloudpss
#comment: 导入 igraph 库，用于图结构操作 (type: ignore 忽略类型检查报错)
import igraph as ig# type: ignore
#comment: 导入 plotly.graph_objects 库，用于创建交互式图表
import plotly.graph_objects as go
# from itertools import combinations
# from fuzzywuzzy import process
#comment: 导入 time 模块，用于时间相关操作
import time
#comment: 导入 numpy 库，用于数值计算
import numpy as np
#comment: 导入 pandas 库，用于数据处理和分析
import pandas as pd
#comment: 从 jobApi1 模块导入 fetch, fetchAllJob, abort 函数 (type: ignore 忽略类型检查报错)
from jobApi1 import fetch,fetchAllJob,abort# type: ignore
#comment: 从 CaseEditToolbox 模块导入 CaseEditToolbox 类 (type: ignore 忽略类型检查报错)
from CaseEditToolbox import CaseEditToolbox# type: ignore
#comment: 从 CaseEditToolbox 模块导入 is_number 函数 (type: ignore 忽略类型检查报错)
from CaseEditToolbox import is_number# type: ignore
#comment: 导入 json 模块，用于处理 JSON 数据
import json
#comment: 导入 math 模块，用于数学运算
import math
#comment: 导入 copy 模块，用于对象拷贝
import copy
#comment: 从 CaseEditToolbox 模块导入 is_number 函数 (type: ignore 忽略类型检查报错)
from CaseEditToolbox import is_number# type: ignore
#comment: 导入 re 模块，用于正则表达式操作
import re
#comment: 从 ImportQSData_xinan_2 模块导入所有内容
from ImportQSData_xinan_2 import *

# 存在MergedG信息时注释本块

#comment: 定义 _process_generators 函数，用于处理发电机数据
def _process_generators(job, qspath, ce, busLabelDict, genRIDType, genRIDType0, generateTopoSP, logJson):
    """
    处理发电机数据，包括读取QS文件、匹配和更新发电机参数、处理不存在的发电机和异常P值。
    """
    #comment: 初始化 QS_genName_sp 为空字典，用于存储QS文件中的发电机名称，如果 generateTopoSP 为 True 则重新初始化
    QS_genName_sp = {} # Assuming this is loaded elsewhere or not needed for this part
    #comment: 如果 generateTopoSP 为 True，则QS_genName_sp 保持为空字典
    if(generateTopoSP):
        QS_genName_sp = {}
    #comment: 构建 QS 发电机数据文件的路径
    qsfile = qspath + 'qsGen.txt'
    #comment: 读取 QS 发电机数据文件，获取信息字典
    infoDict = ReadQSInfo(qsfile,encoding='utf-8')
    #comment: 打印信息字典的所有键
    print(infoDict.keys())
    #comment: 初始化 genDict 字典，用于存储处理后的发电机数据
    genDict = {}
    #comment: 遍历 infoDict 中的发电机数据
    for i in range(len(infoDict['psName'])):
        #comment: 获取发电机名称
        GenName = infoDict['GenName'][i]
        #comment: 获取 IEEE 母线名称
        ieeebusName = infoDict['ieeebusName'][i]
        #comment: 如果 IEEE 母线名称存在于 QS_genName_sp 中，且其值不为空，并且 psName 不在 busLabelDict 中，则使用 QS_genName_sp 中的名称
        if(ieeebusName in QS_genName_sp.keys() and QS_genName_sp[ieeebusName] != '' and infoDict['psName'][i] not in busLabelDict.keys()):
            psName = QS_genName_sp[ieeebusName]
        #comment: 否则使用 infoDict 中的 psName
        else:
            psName = infoDict['psName'][i]
            
        #comment: 获取发电机是否关断状态
        isoff = infoDict['isoff'][i]
        #comment: 获取发电机有功功率
        GenP = infoDict['GenP'][i]
        #comment: 获取发电机无功功率
        GenQ = infoDict['GenQ'][i]
        #comment: 如果 psName 不在 genDict 中，则初始化其对应的字典
        if(psName not in genDict.keys()):
            genDict[psName] = {'p':0,'q':0,'type':0,'isoff':1,'GenName':[],'ieeebusName':[]}
            #comment: 如果 'Vg' 在 infoDict 中，则更新 genDict 添加 Vg, Vg1, VB 字段
            if('Vg' in infoDict.keys()):
                genDict[psName].update({'Vg':[],'Vg1':[],'VB':[]})
            #comment: 如果 GenName 或 psName 中包含“风”字，设置发电机类型为 1
            if('风' in GenName or '风' in psName):
                genDict[psName]['type'] = 1
            #comment: 如果 GenName 或 psName 中包含“光”字，设置发电机类型为 2
            elif('光' in GenName or '光' in psName):
                genDict[psName]['type'] = 2
            #comment: 如果 GenName 或 psName 中包含“外网等值”字，设置发电机类型为 3
            elif('外网等值' in GenName or '外网等值' in psName):
                genDict[psName]['type'] = 3
        #comment: 累加发电机的有功功率
        genDict[psName]['p'] = genDict[psName]['p'] + GenP
        #comment: 累加发电机的无功功率
        genDict[psName]['q'] = genDict[psName]['q'] + GenQ
        #comment: 添加 Vg 值
        genDict[psName]['Vg'].append(infoDict['Vg'][i])
        #comment: 添加 Vg1 值
        genDict[psName]['Vg1'].append(infoDict['Vg1'][i])
        #comment: 计算并添加 VB 值（如果未关断则计算，否则为 -999）
        genDict[psName]['VB'].append(infoDict['Vg'][i]/infoDict['Vg1'][i] if isoff ==0 else -999)
        #comment: 添加发电机名称
        genDict[psName]['GenName'].append(GenName)
        #comment: 添加 IEEE 母线名称
        genDict[psName]['ieeebusName'].append(ieeebusName)
        #comment: 如果发电机未关断，则设置 isoff 状态为 0
        if(isoff == 0):
            genDict[psName]['isoff'] = 0
        
    #comment: 刷新拓扑结构
    ce.refreshTopology()
    #comment: 生成网络
    ce.generateNetwork()
    
    #comment: 初始化 labelList 列表
    labelList = []
    #comment: 初始化 QS1PS0List 列表，存储 QS 有但 PS ไม่มี 的节点
    QS1PS0List = []
    #comment: 初始化 QS1PS0GenList 列表，存储 QS 有但 PS 没有发电机的节点
    QS1PS0GenList = []
    #comment: 初始化 QS0PS1List 列表，存储 QS 没有但 PS 有的节点
    QS0PS1List = []
    #comment: 初始化 SetOffList 列表，存储被设置关断的设备
    SetOffList = []
    #comment: 初始化 PQ0List 列表，存储 PQ 值为 0 的设备
    PQ0List = []
    #comment: 初始化 PQ0IDList 列表，存储 PQ 值为 0 的设备 ID
    PQ0IDList = []
    #comment: 初始化 deleteList 列表，存储需要删除的设备
    deleteList = []
    #comment: 设置组件标签字典
    ce.setCompLabelDict()
    #comment: 遍历所有定义为 'model/CloudPSS/_newBus_3p' 的组件
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
        #comment: 如果组件的标签不在 labelList 中，则添加
        if(j.label not in labelList):
            labelList.append(j.label)
    #comment: 设置新添加发电机的 ID 前缀
    genIDNew = 'AddedGens_'
    #comment: 初始化新添加发电机的计数器
    genNum1 = 0
    #comment: 初始化 PV0 和 PV 标志
    PV0 = True
    PV = True
    #comment: 遍历 genDict 中的发电机数据
    for label,val in genDict.items():
        #comment: 初始化 machine 变量为 None
        machine = None
        #comment: 如果标签不在 labelList 中
        if(label not in labelList):
            #comment: 如果发电机未关断，打印警告信息并添加到 QS1PS0List
            if val['isoff'] == 0 :
                print(label+' 节点不存在！');
                QS1PS0List.append(label)
            #comment: 继续下一次循环
            continue
        #comment: 初始化 buscomp 变量为 None
        buscomp = None
        #comment: 遍历 ce.compLabelDict[label] 中所有组件
        for c,comp in ce.compLabelDict[label].items():
            #comment: 如果组件定义是 'model/CloudPSS/_newBus_3p'，则赋值给 buscomp
            if(comp.definition == 'model/CloudPSS/_newBus_3p'):
                buscomp = comp
            #comment: 使用正则表达式获取组件定义中的最后一个部分
            defi = re.match('.*?/.*?/(.*)',comp.definition).group(1)
            #comment: 如果 defi 不在 genRIDType0 中，则跳过
            if(defi not in genRIDType0):
                continue
            #comment: 将当前组件赋值给 machine
            machine = comp;
        #comment: 获取发电机有功功率
        Pg = val['p']
        #comment: 获取发电机无功功率
        Qg = val['q']
        #comment: 如果 Pg 大于 50，则 PV 保持 PV0 的值
        if(Pg > 50):
            PV = PV0
        #comment: 否则，PV 设置为 False
        else:
            PV = False
            
        #comment: 获取母线基础电压
        Vb0 = float(buscomp.args['VBase'])
        #comment: 如果 'Vg' 在 val 中
        if('Vg' in val.keys()):
            #comment: 查找与 Vb0 最接近的 VB 值的索引
            idx = find_nearest(val['VB'], Vb0)
            #comment: 获取对应的 Vg 值
            Vg = val['Vg'][idx]
            #comment: 获取对应的 Vg1 值
            Vg1 = val['Vg1'][idx]
            #comment: 获取对应的 Vb 值
            Vb = val['VB'][idx]
            
            #comment: 如果 Vb 与 Vb0 的相对差值大于 0.1，则 Vset 为 Vg1，PV 设置为 False
            if(abs(Vb-Vb0)/Vb > 0.1):
                Vset = Vg1;
                PV = False
            #comment: 否则，Vset 为 Vg1
            else:
                Vset = Vg1;

        #comment: 如果没有找到对应的机器组件
        if(machine==None):
            #comment: 如果发电机已关断，则跳过
            if(val['isoff'] == 1):
                continue
            #comment: 打印警告信息
            print(label+' 没有找到！')
            #comment: 将标签添加到 QS1PS0GenList
            QS1PS0GenList.append(label)
            #comment: 获取交流电压源组件的 JSON 定义
            compJson = ce.compLib['_newACVoltageSource_3p']
            #comment: 定义新组件的参数
            args = {
                "BusType": "0",
                "Name": label,
                "pf_P": str(Pg),
                "pf_Q": str(Qg),
                "Vm":buscomp.args['VBase'],
                "pf_Qmin":str(-abs(1.1*Qg)),
                "pf_Qmax":str(abs(1.1*Qg))
            }
            #comment: 如果 'Vg' 在 val 中，则更新 args 添加 pf_V 字段
            if('Vg' in val.keys() ):
                args.update({'pf_V':str(Vset)})
            #comment: 如果 PV 为 True，则将 BusType 设置为 '1'
            if(PV):
                args.update({"BusType": "1"})
            #comment: 定义新组件的引脚连接
            pins= {
                "0": "",
                "1": label
            }
            #comment: 增加发电机计数
            genNum1+=1
            #comment: 添加新组件到模型中
            ce.addComp(compJson,id1 = genIDNew+str(genNum1),canvas = buscomp.canvas, position = {'x':buscomp.position['x']+110,'y':buscomp.position['y']}, 
                    args = args, pins = pins, label = buscomp.label)

            #comment: 继续下一次循环
            continue
        #comment: 如果机器组件定义是 genRIDType0[0]
        elif(re.match('.*?/.*?/(.*)',machine.definition).group(1) == genRIDType0[0]):
            #comment: 如果 BusType 不是 '2' 并且 PV 为 True，则设置 BusType 为 '1'
            if(machine.args['BusType'] != '2' and PV):
                machine.args['BusType'] = '1'
            #comment: 否则如果 BusType 不是 '2'，则设置 BusType 为 '0'
            elif(machine.args['BusType'] != '2'):
                machine.args['BusType'] = '0'
            #comment: 否则如果 BusType 是 '2'，则设置 pf_Theta 为母线 Theta
            elif(machine.args['BusType'] == '2'):
                machine.args['pf_Theta'] = buscomp.args['Theta']
            #comment: 更新 pf_P
            machine.args['pf_P'] = str(Pg)
            #comment: 更新 pf_Q
            machine.args['pf_Q'] = str(Qg)
            #comment: 更新 V
            machine.args['V'] = str(Vb/math.sqrt(3))
            #comment: 如果 'Vg' 在 val 中，则更新 pf_V
            if('Vg' in val.keys()):
                machine.args['pf_V'] = str(Vset*Vb0/Vb)

        #comment: 如果机器组件定义是 genRIDType0[1]
        elif(re.match('.*?/.*?/(.*)',machine.definition).group(1) == genRIDType0[1]):
            #comment: 如果 BusType 不是 '2' 并且 PV 为 True，则设置 BusType 为 '1'
            if(machine.args['BusType'] != '2' and PV):
                machine.args['BusType'] = '1'
            #comment: 否则如果 BusType 不是 '2'，则设置 BusType 为 '0'
            elif(machine.args['BusType'] != '2'):
                machine.args['BusType'] = '0'
            #comment: 更新 pf_P
            machine.args['pf_P'] = str(Pg)
            #comment: 更新 pf_Q
            machine.args['pf_Q'] = str(Qg)
            #comment: 如果 'Vg' 在 val 中，则更新 pf_V
            if('Vg' in val.keys()):
                machine.args['pf_V'] = str(Vset)
        #comment: 如果机器组件定义是 genRIDType0[2]
        elif(re.match('.*?/.*?/(.*)',machine.definition).group(1) == genRIDType0[2]):
            #comment: 更新 PG0
            machine.args['PG0'] = str(Pg/float(machine.args['Sbase']))
            #comment: 更新 QG0
            machine.args['QG0'] = str(Qg/float(machine.args['Sbase']))
        #comment: 如果机器组件定义是 genRIDType0[3]
        elif(re.match('.*?/.*?/(.*)',machine.definition).group(1) == genRIDType0[3]):
            #comment: 如果 BusType 不是 '2' 并且 PV 为 True，则设置 BusType 为 '1'
            if(machine.args['BusType'] != '2' and PV):
                machine.args['BusType'] = '1'
            #comment: 否则如果 BusType 不是 '2'，则设置 BusType 为 '0'
            elif(machine.args['BusType'] != '2'):
                machine.args['BusType'] = '0'
            #comment: 更新 pf_P
            machine.args['pf_P'] = str(Pg)
            #comment: 更新 pf_Q
            machine.args['pf_Q'] = str(Qg)
            #comment: 如果 'Vg' 在 val 中并且 PV 为 True，则更新 pf_V
            if('Vg' in val.keys() and PV):
                machine.args['pf_V'] = str(Vset)
        #comment: 如果发电机已关断
        if(val['isoff']==1):
            #comment: 将标签添加到 SetOffList
            SetOffList.append(label)
            #comment: 获取 machine 邻近的组件（深度为 5，排除母线）
            RemovedComps = getNetworkNeighbor_E(ce,'/'+machine.id,5,exceptRIDList=['model/CloudPSS/_newBus_3p']).vs['name']
            #comment: 移除这些组件
            for j in RemovedComps:
                ce.project.revision.implements.diagram.cells.pop(j[1:])

    #comment: 初始化 PQ_1IDList 列表，存储 P 值为负的设备 ID
    PQ_1IDList = []
    #comment: 初始化 PBiggerSList 列表，存储 P 值大于 Sbase 的设备标签
    PBiggerSList = []       
    #comment: 遍历 genRIDType 中的所有发电机类型
    for gt in genRIDType:
        #comment: 遍历所有指定类型的组件
        for i,j in ce.project.getComponentsByRid(gt).items():
            #comment: 如果组件标签不在 genDict 中，并且组件不是新添加的交流电压源（区外等效除外），则添加到 QS0PS1List 和 deleteList
            if(j.label not in genDict.keys() and j.definition != 'model/CloudPSS/_newACVoltageSource_3p'):
                QS0PS1List.append(j.label)
                deleteList.append(i)
            #comment: 如果组件标签不在 genDict 中，并且组件是新添加的交流电压源（区外等效除外），则添加到 QS0PS1List 和 deleteList
            if(j.label not in genDict.keys() and j.definition == 'model/CloudPSS/_newACVoltageSource_3p' and '区外等效' not in j.label):
                QS0PS1List.append(j.label)
                deleteList.append(i)
            #comment: 获取组件定义中的最后一个部分
            defi = re.match('.*?/.*?/(.*)',j.definition).group(1)
            #comment: 如果定义是 genRIDType0[0]
            if(defi == genRIDType0[0]):
                #comment: 如果是 PQ 节点且 P 和 Q 都为 0，则添加到 PQ0IDList
                if (j.args['BusType']=='0' and float(j.args['pf_P'])==0 and float(j.args['pf_Q'])==0):
                    PQ0IDList.append(i)
                #comment: 如果 P 小于 0，则添加到 PQ_1IDList
                if(float(j.args['pf_P']) < 0):
                    PQ_1IDList.append(i)
                #comment: 如果 P 大于 Smva，则扩大 Smva 并添加到 PBiggerSList
                if(float(j.args['pf_P']) > float(j.args['Smva'])):
                    j.args['Smva'] = str(1.1*float(j.args['pf_P']));
                    PBiggerSList.append(j.label)
                #comment: 如果 Q 大于 pf_Qmax，则扩大 pf_Qmax
                if(float(j.args['pf_Q']) > float(j.args['pf_Qmax'])):
                    j.args['pf_Qmax'] = str(10+float(j.args['pf_Q']));
                #comment: 如果 Q 小于 pf_Qmin，则缩小 pf_Qmin
                if(float(j.args['pf_Q']) < float(j.args['pf_Qmin'])):
                    j.args['pf_Qmin'] = str(-10+float(j.args['pf_Q']));
            #comment: 如果定义是 genRIDType0[1]
            elif(defi == genRIDType0[1]):
                #comment: 如果是 PQ 节点且 P 和 Q 都为 0，则添加到 PQ0IDList
                if(j.args['BusType']=='0' and float(j.args['pf_P'])==0 and float(j.args['pf_Q'])==0):
                    PQ0IDList.append(i)
                #comment: 如果 P 小于 0，则添加到 PQ_1IDList
                if(float(j.args['pf_P']) < 0):
                    PQ_1IDList.append(i)
                #comment: 如果 P 大于 1.5 倍的 WT_Num，则扩大 WT_Num 并添加到 PBiggerSList
                if(float(j.args['pf_P']) > 1.5*float(j.args['WT_Num'])):
                    j.args['WT_Num'] = str(1.1/1.5*float(j.args['pf_P']));
                    PBiggerSList.append(j.label)
                #comment: 如果 Q 大于 pf_Qmax，则扩大 pf_Qmax
                if(float(j.args['pf_Q']) > float(j.args['pf_Qmax'])):
                    j.args['pf_Qmax'] = str(10+float(j.args['pf_Q']));
                #comment: 如果 Q 小于 pf_Qmin，则缩小 pf_Qmin
                if(float(j.args['pf_Q']) < float(j.args['pf_Qmin'])):
                    j.args['pf_Qmin'] = str(-10+float(j.args['pf_Q']));
            #comment: 如果定义是 genRIDType0[2]
            elif(defi == genRIDType0[2]):
                #comment: 如果 PG0 和 QG0 都为 0，则添加到 PQ0IDList
                if(float(j.args['PG0'])==0 and float(j.args['QG0'])==0):
                    PQ0IDList.append(i)
                #comment: 如果 PG0 小于 0，则添加到 PQ_1IDList
                if(float(j.args['PG0']) < 0):
                    PQ_1IDList.append(i)
                #comment: 如果 PG0 大于 1，则扩大 Sbase 并添加到 PBiggerSList
                if(float(j.args['PG0']) > 1):
                    s0 = float(j.args['Sbase'])
                    j.args['Sbase'] = str(1.1*float(j.args['PG0']) *float(j.args['Sbase']));
                    j.args['PG0'] = str(float(j.args['PG0']) * s0 / float(j.args['Sbase']))
                    j.args['QG0'] = str(float(j.args['QG0']) * s0 / float(j.args['Sbase']))
                    PBiggerSList.append(j.label)
            #comment: 如果定义是 genRIDType0[3]
            elif(defi == genRIDType0[3]):
                #comment: 如果是 PQ 节点且 P 和 Q 都为 0，则添加到 PQ0IDList
                if(j.args['BusType']=='0' and float(j.args['pf_P'])==0 and float(j.args['pf_Q'])==0):
                    PQ0IDList.append(i)
                #comment: 如果 Q 大于 pf_Qmax，则扩大 pf_Qmax
                if(float(j.args['pf_Q']) > float(j.args['pf_Qmax'])):
                    j.args['pf_Qmax'] = str(10+float(j.args['pf_Q']));
                #comment: 如果 Q 小于 pf_Qmin，则缩小 pf_Qmin
                if(float(j.args['pf_Q']) < float(j.args['pf_Qmin'])):
                    j.args['pf_Qmin'] = str(-10+float(j.args['pf_Q']));
    #comment: 获取 PQ 值为 0 的设备标签列表
    PQ0List = [ce.project.getComponentByKey(i).label for i in PQ0IDList]
    #comment: 合并 deleteList 和 PQ0IDList 并去重
    deleteList = set(deleteList) | set(PQ0IDList)
    #comment: 遍历 deleteList 中的设备 ID
    for i in deleteList:
        #comment: 获取设备 i 邻近的组件（深度为 5，排除母线）
        RemovedComps = getNetworkNeighbor_E(ce,'/'+ce.project.getComponentByKey(i).id,5,exceptRIDList=['model/CloudPSS/_newBus_3p']).vs['name']
        #comment: 移除这些组件
        for j in RemovedComps:
            ce.project.revision.implements.diagram.cells.pop(j[1:])

    #comment: 遍历 PQ_1IDList 中的设备 ID
    for i in PQ_1IDList:
        #comment: 获取组件
        comp = ce.project.getComponentByKey(i)
        #comment: 获取组件 i 邻近的组件（深度为 2，排除母线）
        RemovedComps = getNetworkNeighbor_E(ce,'/'+i,2,exceptRIDList=['model/CloudPSS/_newBus_3p']).vs['name']
        #comment: 获取交流电压源组件的 JSON 定义
        compJson = ce.compLib['_newACVoltageSource_3p']
        #comment: 初始化 P 和 Q
        P = ''
        Q = ''
        #comment: 获取组件定义中的最后一个部分
        defi = re.match('.*?/.*?/(.*)',comp.definition).group(1)
        #comment: 如果定义是 genRIDType0[0]，获取 P 和 Q
        if(defi == genRIDType0[0]):
            P = comp.args['pf_P']
            Q = comp.args['pf_Q']
        #comment: 如果定义是 genRIDType0[1]，获取 P 和 Q
        elif(defi == genRIDType0[1]):
            P = comp.args['pf_P']
            Q = comp.args['pf_Q']
        #comment: 如果定义是 genRIDType0[2]，计算 P 和 Q
        elif(defi == genRIDType0[2]):
            P = str(float(comp.args['PG0']) * float(comp.args['Sbase']))
            Q = str(float(comp.args['QG0']) * float(comp.args['Sbase']))
        
        #comment: 定义新组件的参数
        args = {
                "BusType": "0",
                "Name": comp.label,
                "pf_P": P,
                "pf_Q": Q,
            }
        #comment: 定义新组件的引脚连接
        pins= {
                "0": "",
                "1": comp.pins['0']
            }
        #comment: 添加新组件（替换负有功发电机为电压源）
        ce.addComp(compJson,id1 = i+'_Replace',canvas = comp.canvas, position = comp.position, args = args, pins = pins, label = comp.label)
        
        #comment: 移除旧组件
        for j in RemovedComps:
            ce.project.revision.implements.diagram.cells.pop(j[1:])

    #comment: 更新 logJson，记录处理结果
    logJson.update({'QS有PSASP无的电机母线':QS1PS0List,'QS无PSASP有的电机母线':QS0PS1List,'PSASP有母线无电机':QS1PS0GenList,'PSASP置为关断isoff的电机':SetOffList,'PSASP PQ为0':PQ0List})
    #comment: 将 logJson 写入文件
    with open("./logJson.json","w",encoding='utf-8') as f:
        f.write(json.dumps(logJson, indent=4, ensure_ascii=False))
    #comment: 打印分隔线和 QS1PS0List 的长度
    print('————————————————————QS1PS0List————————————————————')
    print(len(QS1PS0List))
    #comment: 通过 jobmessage 发送日志信息
    jobmessage(job,"电机处理结果: ",key="logs",verb='append')
    jobmessage(job,"电机QS有母线PS无母线: {0}".format(len(QS1PS0List)),key="logs",verb='append')
    #comment: 打印分隔线和 QS1PS0GenList 的长度
    print('————————————————————QS1PS0GenList————————————————————')
    print(len(QS1PS0GenList))
    jobmessage(job,"电机QS有开机PS无开机: {0}".format(len(QS1PS0GenList)),key="logs",verb='append')
    #comment: 打印分隔线和 QS0PS1List 的长度
    print('————————————————————QS0PS1List————————————————————')
    print(len(QS0PS1List))
    jobmessage(job,"电机QS无开机PS有开机: {0}".format(len(QS0PS1List)),key="logs",verb='append')
    #comment: 打印分隔线和 SetOffList 的长度
    print('————————————————————SetOffList————————————————————')
    print(len(SetOffList))
    jobmessage(job,"电机置为关机: {0}".format(len(SetOffList)),key="logs",verb='append')
    #comment: 打印分隔线和 PQ0List 的长度
    print('————————————————————PQ0List————————————————————')
    print(len(PQ0List))
    jobmessage(job,"PSASP剩余PQ为0电机: {0}".format(len(PQ0List)),key="logs",verb='append')
    #comment: 打印分隔线和 PQ_1IDList 的长度
    print('————————————————————PQ_1IDList————————————————————')
    print(len(PQ_1IDList))
    jobmessage(job,"P为负值电机，特殊处理为电压源: {0}".format(len(PQ_1IDList)),key="logs",verb='append')
    #comment: 打印分隔线和 PBiggerSList
    print('————————————————————PBiggerSList————————————————————')
    print(PBiggerSList)
    jobmessage(job,"P值较大，自动扩大容量: {0}".format(len(PBiggerSList)),key="logs",verb='append')
    #comment: 返回 logJson
    return logJson

#comment: 定义 _process_loads 函数，用于处理负荷数据
def _process_loads(job, qspath, ce, busLabelDict, loadRIDType, generateTopoSP, logJson):
    """
    处理负荷数据，包括读取QS文件、匹配和更新负荷参数、处理不存在的负荷和异常P值。
    """
    #comment: 初始化 QS_loadName_sp 为空字典，用于存储QS文件中的负荷名称，如果 generateTopoSP 为 True 则重新初始化
    QS_loadName_sp = {} # Assuming this is loaded elsewhere or not needed for this part
    #comment: 如果 generateTopoSP 为 True，则 QS_loadName_sp 保持为空字典
    if(generateTopoSP):
        QS_loadName_sp = {}
    #comment: 构建 QS 负荷数据文件的路径
    qsfile = qspath + 'qsLoad.txt'
    #comment: 读取 QS 负荷数据文件，获取信息字典
    infoDict = ReadQSInfo(qsfile,type = 'load',encoding='utf-8')
    #comment: 打印信息字典的所有键
    print(infoDict.keys())
    #comment: 初始化 loadDict 字典，用于存储处理后的负荷数据
    loadDict = {}
    #comment: 遍历 infoDict 中的负荷数据
    for i in range(len(infoDict['psName'])):
        #comment: 获取负荷名称
        LoadName = infoDict['LoadName'][i]
        #comment: 获取 IEEE 母线名称
        ieeebusName = infoDict['ieeebusName'][i]
        #comment: 如果 IEEE 母线名称存在于 QS_loadName_sp 中，且其值不为空，并且 psName 不在 busLabelDict 中，则使用 QS_loadName_sp 中的名称
        if(ieeebusName in QS_loadName_sp.keys() and QS_loadName_sp[ieeebusName] != ''  and infoDict['psName'][i] not in busLabelDict.keys()):
            psName = QS_loadName_sp[ieeebusName]
        #comment: 否则使用 infoDict 中的 psName
        else:
            psName = infoDict['psName'][i]

        #comment: 获取负荷是否关断状态
        isoff = infoDict['isoff'][i]
        #comment: 获取负荷有功功率
        Pl = infoDict['Pl'][i]
        #comment: 获取负荷无功功率
        Ql = infoDict['Ql'][i]
        #comment: 如果 psName 不在 loadDict 中，则初始化其对应的字典
        if(psName not in loadDict.keys()):
            loadDict[psName] = {'p':0,'q':0,'isoff':1,'LoadName':[],'ieeebusName':[]}
        #comment: 累加负荷的有功功率
        loadDict[psName]['p'] = loadDict[psName]['p'] + Pl
        #comment: 累加负荷的无功功率
        loadDict[psName]['q'] = loadDict[psName]['q'] + Ql
        #comment: 添加负荷名称
        loadDict[psName]['LoadName'].append(LoadName)
        #comment: 添加 IEEE 母线名称
        loadDict[psName]['ieeebusName'].append(ieeebusName)
        #comment: 如果负荷未关断，则设置 isoff 状态为 0
        if(isoff == 0):
            loadDict[psName]['isoff'] = 0
        
    #comment: 定义负荷的 RID 类型列表
    loadRIDType = ['model/CloudPSS/SyntheticLoad', 'model/CloudPSS/_newExpLoad_3p', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 初始化 labelList 列表
    labelList = []
    #comment: 初始化 QS1PS0List 列表，存储 QS 有但 PS ไม่มี 的节点
    QS1PS0List = []
    #comment: 初始化 QS1PS0LoadList 列表，存储 QS 有但 PS 没有负荷的节点
    QS1PS0LoadList = []
    #comment: 初始化 QS0PS1List 列表，存储 QS 没有但 PS 有的节点
    QS0PS1List = []
    #comment: 初始化 SetOffList 列表，存储被设置关断的设备
    SetOffList = []
    #comment: 初始化 PQ0List 列表，存储 PQ 值为 0 的设备
    PQ0List = []
    #comment: 初始化 PQ0IDList 列表，存储 PQ 值为 0 的设备 ID
    PQ0IDList = []
    #comment: 初始化 deleteList 列表，存储需要删除的设备
    deleteList = []
    #comment: 初始化 PQ_1List 列表，存储 P 值为负的设备标签
    PQ_1List = []
    #comment: 初始化 PQ_1IDList 列表，存储 P 值为负的设备 ID
    PQ_1IDList = []

    #comment: 设置组件标签字典
    ce.setCompLabelDict()
    #comment: 初始化 Psum, Psum1, Psum2 为 0
    Psum = 0
    Psum1 = 0
    Psum2 = 0
    #comment: 获取所有组件的键
    AllCompKeys = ce.project.getAllComponents().keys()
    #comment: 遍历所有定义为 'model/CloudPSS/_newBus_3p' 的组件
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
        #comment: 如果组件的标签不在 labelList 中，则添加
        if(j.label not in labelList):
            labelList.append(j.label)
    #comment: 遍历 loadDict 中的负荷数据
    for label,val in loadDict.items():
        #comment: 初始化 machine 变量为 None
        machine = None
        #comment: 如果标签不在 labelList 中
        if(label not in labelList):
            #comment: 打印警告信息
            print(label+' 节点不存在！');
            #comment: 累加 Psum
            Psum += val['p']
            #comment: 将标签添加到 QS1PS0List
            QS1PS0List.append(label)
            #comment: 继续下一次循环
            continue
            
        #comment: 遍历与母线关联的邻居组件
        for c in ce.g.vs.find(label=label,rid='model/CloudPSS/_newBus_3p').neighbors():
            #comment: 如果邻居组件的 ID 不在 AllCompKeys 中，则跳过
            if(c['name'][1:] not in AllCompKeys):
                continue
            #comment: 获取组件
            comp = ce.project.getComponentByKey(c['name'][1:])
            #comment: 如果组件定义不在 loadRIDType 中，则跳过
            if(comp.definition not in loadRIDType):
                continue
            #comment: 将当前组件赋值给 machine
            machine = comp;
        
        #comment: 如果没有找到对应的机器组件
        if(machine==None):
            #comment: 将标签添加到 QS1PS0LoadList
            QS1PS0LoadList.append(label)
            #comment: 继续下一次循环
            continue
        #comment: 如果机器组件定义是 loadRIDType[0] (SyntheticLoad)
        elif(machine.definition == loadRIDType[0]):
            #comment: 累加 Psum
            Psum += val['p']
            #comment: 累加 Psum1
            Psum1 += val['p']
            #comment: 更新 P0
            machine.args['P0'] = str(val['p'])
            #comment: 更新 Q0
            machine.args['Q0'] = str(val['q'])
        #comment: 如果机器组件定义是 loadRIDType[1] (ExpLoad)
        elif(machine.definition == loadRIDType[1]):
            #comment: 累加 Psum
            Psum += val['p']
            
            #comment: 更新 p
            machine.args['p'] = str(val['p'])
            #comment: 更新 q
            machine.args['q'] = str(val['q'])
        #comment: 如果机器组件定义是 loadRIDType[2] (ACVoltageSource)
        elif(machine.definition == loadRIDType[2]):
            #comment: 累加 Psum
            Psum += val['p']
            #comment: 更新 pf_P
            machine.args['pf_P'] = str(float(machine.args['pf_P'])-val['p'])
            #comment: 更新 pf_Q
            machine.args['pf_Q'] = str(float(machine.args['pf_Q'])-val['q'])
        
        #comment: 如果负荷已关断
        if(val['isoff']==1):
            #comment: 将标签添加到 SetOffList
            SetOffList.append(label)
            #comment: 获取 machine 邻近的组件（深度为 2，排除母线）
            RemovedComps = getNetworkNeighbor_E(ce,'/'+machine.id,2,exceptRIDList=['model/CloudPSS/_newBus_3p']).vs['name']
            #comment: 移除这些组件
            for j in RemovedComps:
                ce.project.revision.implements.diagram.cells.pop(j[1:])
    #comment: 暂停 5 秒
    time.sleep(5)
    #comment: 刷新拓扑结构
    ce.refreshTopology()

    #comment: 遍历 loadRIDType 中的所有负荷类型
    for gt in loadRIDType:
        #comment: 遍历所有指定类型的组件
        for i,j in ce.project.getComponentsByRid(gt).items():
            #comment: 如果是交流电压源，则母线标签为 pin 1 的值
            if(gt == 'model/CloudPSS/_newACVoltageSource_3p'):
                buslabel = j.pins['1']
            #comment: 否则，母线标签为 pin 0 的值
            else:
                buslabel = j.pins['0']
            #comment: 如果母线标签不在 loadDict 中，并且组件不是新添加的交流电压源，则添加到 QS0PS1List 和 deleteList，并跳过
            if(buslabel not in loadDict.keys() and j.definition != 'model/CloudPSS/_newACVoltageSource_3p'):

                QS0PS1List.append(buslabel)
                deleteList.append(i)
                continue
            #comment: 如果组件定义是 loadRIDType[0]
            if(j.definition == loadRIDType[0]):
                #comment: 如果 P0 和 Q0 都为 0，则添加到 PQ0IDList
                if(ce.topo['components']['/'+i]['args']['P0']=='0' and ce.topo['components']['/'+i]['args']['Q0']=='0'):
                    PQ0IDList.append(i)
                #comment: 如果 P0 小于 0，则添加到 PQ_1IDList
                if(float(ce.topo['components']['/'+i]['args']['P0']) < 0):
                    PQ_1IDList.append(i)
            #comment: 如果组件定义是 loadRIDType[1]
            elif(j.definition == loadRIDType[1]):
                #comment: 如果 p 和 q 都为 0，则添加到 PQ0IDList
                if(ce.topo['components']['/'+i]['args']['p']=='0' and ce.topo['components']['/'+i]['args']['q']=='0'):
                    PQ0IDList.append(i)
                #comment: 如果 p 小于 0，则添加到 PQ_1IDList
                if(float(ce.topo['components']['/'+i]['args']['p']) < 0):
                    PQ_1IDList.append(i)
            #comment: 如果组件定义是 loadRIDType[2] (交流电压源) 且 pf_P 和 pf_Q 都为 0，则添加到 PQ0IDList
            elif(j.definition == loadRIDType[2] and ce.topo['components']['/'+i]['args']['pf_P']=='0' and ce.topo['components']['/'+i]['args']['pf_Q']=='0'):
                PQ0IDList.append(i)
    #comment: 获取 PQ 值为 0 的设备标签列表
    PQ0List = [ce.project.getComponentByKey(i).label for i in PQ0IDList]
    #comment: 合并 deleteList 和 PQ0IDList 并去重
    deleteList = set(deleteList)|set(PQ0IDList)
    #comment: 遍历 deleteList 中的设备 ID
    for i in deleteList:
        #comment: 获取设备 i 邻近的组件（深度为 2，排除母线）
        RemovedComps = getNetworkNeighbor_E(ce,'/'+i,2,exceptRIDList=['model/CloudPSS/_newBus_3p']).vs['name']
        #comment: 移除这些组件
        for j in RemovedComps:
            ce.project.revision.implements.diagram.cells.pop(j[1:])
    #comment: 获取 P 值为负的设备标签列表
    PQ_1List = [ce.project.getComponentByKey(i).label for i in PQ_1IDList]
    #comment: 遍历 PQ_1IDList 中的设备 ID
    for i in PQ_1IDList:
        #comment: 获取组件
        comp = ce.project.getComponentByKey(i)
        #comment: 获取组件 i 邻近的组件（深度为 2，排除母线）
        RemovedComps = getNetworkNeighbor_E(ce,'/'+i,2,exceptRIDList=['model/CloudPSS/_newBus_3p']).vs['name']
        #comment: 获取交流电压源组件的 JSON 定义
        compJson = ce.compLib['_newACVoltageSource_3p']
        #comment: 初始化 P 和 Q
        P = ''
        Q = ''
        #comment: 如果组件定义是 loadRIDType[0]，计算 P 和 Q
        if(comp.definition == loadRIDType[0]):
            P = str(-float(comp.args['P0']))
            Q = str(-float(comp.args['Q0']))
        #comment: 如果组件定义是 loadRIDType[1]，计算 P 和 Q
        elif(comp.definition == loadRIDType[1]):
            P = str(-float(comp.args['p']))
            Q = str(-float(comp.args['q']))
        #comment: 如果组件定义是 loadRIDType[2]，直接获取 P 和 Q
        elif(comp.definition == loadRIDType[2]):
            P = comp.args['pf_P']
            Q = comp.args['pf_Q']
        
        #comment: 定义新组件的参数
        args = {
                "BusType": "0",
                "Name": comp.args['Name'],
                "pf_P": P,
                "pf_Q": Q,
            }
        #comment: 定义新组件的引脚连接
        pins= {
                "0": "",
                "1": comp.pins['0']
            }
        #comment: 添加新组件（替换负有功负荷为电压源）
        ce.addComp(compJson,id1 = i+'_Replace',canvas = comp.canvas, position = comp.position, args = args, pins = pins, label = comp.label)
        
        #comment: 移除旧组件
        for j in RemovedComps:
            ce.project.revision.implements.diagram.cells.pop(j[1:])

    #comment: 设置组件标签字典
    ce.setCompLabelDict()
    #comment: 生成新负荷的 ID 前缀
    LoadIDNew = 'LoadNew_'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_';
    #comment: 生成新交流负荷的 ID 前缀
    LoadIDNew2 = 'LoadACNew_'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_';
    #comment: 初始化新负荷计数器
    LoadNum1 = 0
    #comment: 初始化新交流负荷计数器
    LoadNum2 = 0
    #comment: 定义发电机 RID 类型列表
    genRIDType = ['model/CloudPSS/SyncGeneratorRouter', 'model/admin/WGSource', 'model/CloudPSS/PVStation', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 遍历 QS1PS0LoadList 中的标签
    for i in QS1PS0LoadList:
        #comment: 查找母线顶点
        busVS = ce.g.vs.find(label=i,rid='model/CloudPSS/_newBus_3p')
        #comment: 获取母线 ID
        busid = busVS['name'][1:]
        #comment: 获取母线组件
        buscomp = ce.project.getComponentByKey(busid)
        #comment: 获取负荷值
        val = loadDict[i]
        #comment: 初始化 genComp 为 None
        genComp = None
        #comment: 遍历与母线关联的组件
        for j,k in ce.compLabelDict[i].items():
            #comment: 如果组件定义在 genRIDType 中，则赋值给 genComp 并跳出循环
            if(k.definition in genRIDType):
                genComp = k
                break
        #comment: 累加 Psum
        Psum += val['p']

        #comment: 如果存在发电机组件并且负荷的有功功率小于等于 0
        if(genComp!=None and val['p'] <= 0):
            #comment: 如果是同步发电机
            if(genComp.definition == 'model/CloudPSS/SyncGeneratorRouter'):

                #comment: 如果发电机有功功率减去负荷有功功率小于 0，则跳过
                if(float(genComp.args['pf_P'])-val['p'] < 0):
                    continue
                #comment: 更新发电机有功功率
                genComp.args['pf_P'] = str(float(genComp.args['pf_P'])-val['p'])
                #comment: 更新发电机无功功率
                genComp.args['pf_Q'] = str(float(genComp.args['pf_Q'])-val['q'])
                #comment: 调整无功功率上下限
                if(float(genComp.args['pf_Q']) > float(genComp.args['pf_Qmax'])):
                    genComp.args['pf_Qmax'] = str(10+float(genComp.args['pf_Q']));
                if(float(genComp.args['pf_Q']) < float(genComp.args['pf_Qmin'])):
                    genComp.args['pf_Qmin'] = str(-10+float(genComp.args['pf_Q']));
            #comment: 如果是风力发电机
            elif(genComp.definition == 'model/admin/WGSource'):
                #comment: 如果发电机有功功率减去负荷有功功率小于 0，则跳过
                if(float(genComp.args['pf_P'])-val['p'] < 0):
                    continue
                #comment: 更新发电机有功功率
                genComp.args['pf_P'] = str(float(genComp.args['pf_P'])-val['p'])
                #comment: 更新发电机无功功率
                genComp.args['pf_Q'] = str(float(genComp.args['pf_Q'])-val['q'])
                #comment: 调整无功功率上下限
                if(float(genComp.args['pf_Q']) > float(genComp.args['pf_Qmax'])):
                    genComp.args['pf_Qmax'] = str(10+float(genComp.args['pf_Q']));
                if(float(genComp.args['pf_Q']) < float(genComp.args['pf_Qmin'])):
                    genComp.args['pf_Qmin'] = str(-10+float(genComp.args['pf_Q']));
            #comment: 如果是光伏电站
            elif(genComp.definition == genRIDType[2]):
                #comment: 如果发电机 PG0 减去负荷有功功率除以 Sbase 小于 0，则跳过
                if(float(genComp.args['PG0'])-val['p']/float(genComp.args['Sbase']) < 0):
                    continue
                #comment: 更新发电机 PG0
                genComp.args['PG0'] = str(float(genComp.args['PG0'])-val['p']/float(genComp.args['Sbase']))
                #comment: 更新发电机 QG0
                genComp.args['QG0'] = str(float(genComp.args['QG0'])-val['q']/float(genComp.args['Sbase']))
            #comment: 如果是交流电压源
            elif(genComp.definition == genRIDType[3]):
                #comment: 如果发电机有功功率减去负荷有功功率小于 0，则跳过
                if(float(genComp.args['pf_P'])-val['p'] < 0):
                    continue
                #comment: 更新发电机有功功率
                genComp.args['pf_P'] = str(float(genComp.args['pf_P'])-val['p'])
                #comment: 更新发电机无功功率
                genComp.args['pf_Q'] = str(float(genComp.args['pf_Q'])-val['q'])
                #comment: 调整无功功率上下限
                if(float(genComp.args['pf_Q']) > float(genComp.args['pf_Qmax'])):
                    genComp.args['pf_Qmax'] = str(10+float(genComp.args['pf_Q']));
                if(float(genComp.args['pf_Q']) < float(genComp.args['pf_Qmin'])):
                    genComp.args['pf_Qmin'] = str(-10+float(genComp.args['pf_Q']));
            
            #comment: 继续下一次循环
            continue

        #comment: 如果负荷有功功率大于等于 0
        if(val['p']>=0):
            #comment: 获取 ExpLoad 组件的 JSON 定义
            compJson = ce.compLib['_newExpLoad_3p']
            #comment: 定义新组件的参数
            args = {
                "p": str(val['p']),
                "q": str(val['q']),
                "v": buscomp.args['VBase']
            }
            #comment: 定义新组件的引脚连接
            pins= {
                    "0": buscomp.pins['0']
                }
            #comment: 增加 Psum2
            Psum2 += 1
            #comment: 添加新组件 (ExpLoad)
            ce.addComp(compJson,id1 = LoadIDNew+str(LoadNum1),canvas = buscomp.canvas, position = {'x':buscomp.position['x']+110,'y':buscomp.position['y']}, 
                    args = args, pins = pins, label = buscomp.label)
            #comment: 增加 LoadNum1
            LoadNum1 = LoadNum1+1
        #comment: 否则 (负荷有功功率小于 0)
        else:
            #comment: 获取交流电压源组件的 JSON 定义
            compJson = ce.compLib['_newACVoltageSource_3p']
            #comment: 定义新组件的参数 (作为电源)
            args = {
                "BusType": "0",
                "Name": buscomp.label,
                "pf_P": str(-val['p']),
                "pf_Q": str(-val['q']),
            }
            #comment: 定义新组件的引脚连接
            pins= {
                "0": "",
                "1": buscomp.pins['0']
            }
            #comment: 添加新组件 (ACVoltageSource)
            ce.addComp(compJson,id1 = LoadIDNew2+str(LoadNum2),canvas = buscomp.canvas, position = {'x':buscomp.position['x']+110,'y':buscomp.position['y']}, 
                    args = args, pins = pins, label = buscomp.label)
            #comment: 增加 LoadNum2
            LoadNum2 = LoadNum2+1

    #comment: 更新 logJson，记录处理结果
    logJson .update({'QS有PSASP无的负荷母线':QS1PS0List,
                    'QS无PSASP有的负荷母线':QS0PS1List,
                    'PSASP有母线无负荷':QS1PS0LoadList,
                    'PSASP置为关断isoff的负荷':SetOffList,
                    'PSASP PQ为0的负荷':PQ0List})
    #comment: 将 logJson 写入文件
    with open("./logJson.json","w",encoding='utf-8') as f:
        f.write(json.dumps(logJson, indent=4, ensure_ascii=False))

    #comment: 打印分隔线和 QS1PS0List 的长度
    print('————————————————————QS1PS0List————————————————————')
    print(len(QS1PS0List))
    #comment: 通过 jobmessage 发送日志信息
    jobmessage(job,"负荷处理结果：",key="logs",verb='append')
    jobmessage(job,"QS有PS无母线: {0}".format(len(QS1PS0List)),key="logs",verb='append')
    #comment: 打印分隔线和 QS1PS0LoadList 的长度
    print('————————————————————QS1PS0LoadList————————————————————')
    print(len(QS1PS0LoadList))
    jobmessage(job,"QS有负荷PS无负荷: {0}".format(len(QS1PS0LoadList)),key="logs",verb='append')
    #comment: 打印分隔线和 QS0PS1List 的长度
    print('————————————————————QS0PS1List————————————————————')
    print(len(QS0PS1List))
    jobmessage(job,"PS有负荷QS无负荷: {0}".format(len(QS0PS1List)),key="logs",verb='append')
    #comment: 打印分隔线和 SetOffList 的长度
    print('————————————————————SetOffList————————————————————')
    print(len(SetOffList))
    jobmessage(job,"将PS负荷置为关断: {0}".format(len(SetOffList)),key="logs",verb='append')
    #comment: 打印分隔线和 PQ0List 的长度
    print('————————————————————PQ0List————————————————————')
    print(len(PQ0List))
    jobmessage(job,"多余PQ为0的负荷: {0}".format(len(PQ0List)),key="logs",verb='append')
    #comment: 打印分隔线和 PQ_1List 的长度
    print('————————————————————PQ_1List————————————————————')
    print(len(PQ_1List))
    jobmessage(job,"负有功负荷，特殊处理为电压源: {0}".format(len(PQ_1List)),key="logs",verb='append')
    #comment: 返回 logJson
    return logJson

#comment: 定义 _process_shunts 函数，用于处理并联补偿器数据
def _process_shunts(job, qspath, ce, busLabelDict, generateTopoSP, logJson):
    """
    处理并联补偿器数据，包括读取QS文件、匹配和添加并补。
    """
    #comment: 构建 QS 补偿器数据文件的路径
    qsfile = qspath + 'qsCP.txt'
    #comment: 读取 QS 补偿器数据文件，获取信息字典
    infoDict = ReadQSInfo(qsfile,encoding='utf-8')
    #comment: 打印信息字典的所有键
    print(infoDict.keys())

    #comment: 初始化 QS_shuntName_sp 为空字典，用于存储QS文件中的并联补偿器名称，如果 generateTopoSP 为 True 则重新初始化
    QS_shuntName_sp = {} # Assuming this is loaded elsewhere or not needed for this part
    #comment: 如果 generateTopoSP 为 True，则 QS_shuntName_sp 保持为空字典
    if(generateTopoSP):
        QS_shuntName_sp = {}

    #comment: 初始化 shuntDict 字典，用于存储处理后的并联补偿器数据
    shuntDict = {}
    #comment: 遍历 infoDict 中的并联补偿器数据
    for i in range(len(infoDict['psName1'])):
        #comment: 获取补偿器名称
        Name = infoDict['Name'][i]
        #comment: 获取 IEEE 母线名称
        ieeebusName = infoDict['ieeebus1'][i]
        #comment: 如果 IEEE 母线名称存在于 QS_shuntName_sp 中，且其值不为空，并且 psName1 不在 busLabelDict 中，则使用 QS_shuntName_sp 中的名称
        if(ieeebusName in QS_shuntName_sp.keys() and QS_shuntName_sp[ieeebusName] != ''  and infoDict['psName1'][i] not in busLabelDict.keys()):
            psName = QS_shuntName_sp[ieeebusName]
        #comment: 否则使用 infoDict 中的 psName1
        else:
            psName = infoDict['psName1'][i]

        #comment: 获取补偿器是否关断状态
        isoff = infoDict['is_off'][i]
        #comment: 获取补偿器无功功率
        Q = infoDict['Q'][i]
        #comment: 如果 psName 不在 shuntDict 中，则初始化其对应的字典
        if(psName not in shuntDict.keys()):
            shuntDict[psName] = {'q':0,'isoff':1,'Name':[],'ieeebusName':[]}
        #comment: 累加补偿器的无功功率
        shuntDict[psName]['q'] = shuntDict[psName]['q'] + Q
        #comment: 添加补偿器名称
        shuntDict[psName]['Name'].append(Name)
        #comment: 添加 IEEE 母线名称
        shuntDict[psName]['ieeebusName'].append(ieeebusName)
        #comment: 如果补偿器未关断，则设置 isoff 状态为 0
        if(isoff == 0):
            shuntDict[psName]['isoff'] = 0
        
    #comment: 定义并联补偿器的 RID 类型列表
    shuntRIDType = ['model/CloudPSS/_newShuntLC_3p']
    #comment: 初始化 labelList 列表
    labelList = []
    #comment: 初始化 QS1PS0List 列表，存储 QS 有但 PS ไม่มี 的节点
    QS1PS0List = []

    #comment: 设置组件标签字典
    ce.setCompLabelDict()
    #comment: 遍历所有定义为 'model/CloudPSS/_newBus_3p' 的组件
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
        #comment: 如果组件的标签不在 labelList 中，则添加
        if(j.label not in labelList):
            labelList.append(j.label)

    #comment: 生成新并联补偿器的 ID 前缀
    ShuntIDNew = 'ShuntNew_'+time.strftime("%Y%m%d%H%M%S", time.localtime())+'_';
    #comment: 初始化新并联补偿器计数器
    ShuntNum1 = 0
    #comment: 遍历 shuntDict 中的并联补偿器数据
    for label,val in shuntDict.items():
        #comment: 初始化 machine 变量为 None
        machine = None
        #comment: 如果标签不在 labelList 中
        if(label not in labelList):
            #comment: 打印警告信息
            print(label+' 节点不存在！');
            #comment: 将标签添加到 QS1PS0List
            QS1PS0List.append(label)
            #comment: 继续下一次循环
            continue
        #comment: 如果无功功率的绝对值小于或等于一个很小的数，则跳过
        if(abs(val['q'])<=0.000001):
            continue
        #comment: 查找母线顶点
        busVS = ce.g.vs.find(label=label,rid='model/CloudPSS/_newBus_3p')
        #comment: 获取母线 ID
        busid = busVS['name'][1:]
        #comment: 获取母线组件
        buscomp = ce.project.getComponentByKey(busid)

        #comment: 获取并联补偿器组件的 JSON 定义
        compJson = ce.compLib['_newShuntLC_3p']
        #comment: 定义新组件的参数
        args = {
            "Name": label + '_AutoAdd',
            "s": str(-val['q']),
            "v": str(float(buscomp.args['VBase']) * float(buscomp.args['V']))
        }
        #comment: 定义新组件的引脚连接
        pins= {
                "0": buscomp.pins['0']
            }

        
        #comment: 添加新组件 (并联补偿器)
        ce.addComp(compJson,id1 = ShuntIDNew+str(ShuntNum1),canvas = buscomp.canvas, position = {'x':buscomp.position['x']+110,'y':buscomp.position['y']}, 
                    args = args, pins = pins, label = buscomp.label)
        #comment: 增加 ShuntNum1
        ShuntNum1 = ShuntNum1+1

    #comment: 更新 logJson，记录处理结果
    logJson .update({'QS有PSASP无的并补母线':QS1PS0List})
    #comment: 将 logJson 写入文件
    with open("./logJson.json","w",encoding='utf-8') as f:
        f.write(json.dumps(logJson, indent=4, ensure_ascii=False))

    #comment: 打印分隔线和 QS1PS0List 的长度
    print('————————————————————QS1PS0List————————————————————')
    print(len(QS1PS0List))
    #comment: 通过 jobmessage 发送日志信息
    jobmessage(job,"并补处理结果: 并补共{0}".format(len(QS1PS0List)),key="logs",verb='append')
    #comment: 返回 logJson
    return logJson

#comment: 定义 _process_dc_lines 函数，用于处理直流线路数据
def _process_dc_lines(job, qspath, ce, busLabelDict, DCRIDType, logJson):
    """
    处理直流线路数据，包括读取QS文件、更新直流线路参数和处理不存在的直流设备。
    """
    #comment: 构建 QS 换流变数据文件的路径
    qsfile = qspath + 'convert.txt'
    #comment: 读取 QS 换流变数据文件，获取信息字典
    infoDict = ReadQSInfo(qsfile,encoding = "utf-8")
    #comment: 打印信息字典的所有键
    print(infoDict.keys())

    #comment: 初始化 DCDict 字典，用于存储处理后的直流数据
    DCDict = {}
    #comment: 遍历 infoDict 中的直流数据
    for i in range(len(infoDict['qsName'])):
        #comment: 获取 IEEE 母线名称
        ieeebus = infoDict['ieeebus'][i]
        #comment: 获取 PS 名称
        psName = infoDict['qsName'][i]
        #comment: 获取交流拓扑节点
        ACToponode = infoDict['ACToponode'][i]
        #comment: 获取有功功率
        P = infoDict['Pl'][i]
        #comment: 获取无功功率
        Q = infoDict['Ql'][i]
        #comment: 如果 psName 不在 DCDict 中，则初始化其对应的字典
        if(psName not in DCDict.keys()):
            DCDict[psName] = {'p':P,'q':Q,'ieeebus':ieeebus,'ACToponode':ACToponode}
    
    #comment: 定义直流设备的 RID 类型列表
    DCRIDType = ['model/admin/DCLine', 'model/CloudPSS/_newExpLoad_3p', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 初始化 labelList 列表
    labelList = []
    #comment: 初始化 QS1PS0List 列表，存储 QS 有但 PS ไม่มี 的节点
    QS1PS0List = []
    #comment: 初始化 QS1PS0DCList 列表，存储 QS 有但 PS 没有直流设备的节点
    QS1PS0DCList = []
    #comment: 设置组件标签字典
    ce.setCompLabelDict()
    #comment: 获取所有组件的键
    AllCompKeys = ce.project.getAllComponents().keys()
    #comment: 使用 busLabelDict.keys() 初始化 labelList
    labelList = busLabelDict.keys()
    #comment: 生成新添加直流设备的 ID 前缀
    DCNewID = 'AddedDC_'
    #comment: 初始化直流设备计数器
    DCNum = 0;
    #comment: 遍历 DCDict 中的直流数据
    for label,val in DCDict.items():
        #comment: 初始化 machine 变量为 None
        machine = None
        #comment: 如果标签不在 labelList 中
        if(label not in labelList):
            #comment: 打印警告信息
            print(label+' 节点不存在！');
            #comment: 将标签添加到 QS1PS0List
            QS1PS0List.append(label)
            #comment: 继续下一次循环
            continue
        #comment: 初始化 flag 为 5
        flag = 5
        #comment: 查找母线顶点
        busid = ce.g.vs.find(label=label,rid='model/CloudPSS/_newBus_3p')['name'][1:]
        #comment: 获取母线组件
        buscomp = ce.project.getComponentByKey(busid)
        #comment: 遍历与母线关联的邻居组件
        for c in ce.g.vs.find(label=label,rid='model/CloudPSS/_newBus_3p').neighbors():
            #comment: 如果邻居组件的 ID 不在 AllCompKeys 中，则跳过
            if(c['name'][1:] not in AllCompKeys):
                continue
            #comment: 获取组件
            comp = ce.project.getComponentByKey(c['name'][1:])
            #comment: 如果组件定义不在 DCRIDType 中，则跳过
            if(comp.definition not in DCRIDType):
                continue
            #comment: 如果当前组件的 RID 类型在 DCRIDType 中的索引小于 flag
            if(DCRIDType.index(comp.definition)<flag):
                #comment: 将当前组件赋值给 machine
                machine = comp;
                #comment: 更新 flag 为当前索引
                flag = DCRIDType.index(comp.definition)
        
        #comment: 如果没有找到对应的机器组件
        if(machine==None):
            #comment: 将标签添加到 QS1PS0DCList
            QS1PS0DCList.append(label)
            #comment: 获取交流电压源组件的 JSON 定义
            compJson = ce.compLib['_newACVoltageSource_3p']
            #comment: 定义新组件的参数 (作为电源)
            args = {
                "BusType": "0",
                "Name": buscomp.label,
                "pf_P": str(-val['p']),
                "pf_Q": str(-val['q']),
            }
            #comment: 定义新组件的引脚连接
            pins= {
                "0": "",
                "1": buscomp.pins['0']
            }
            #comment: 增加直流设备计数
            DCNum+=1
            #comment: 添加新组件 (ACVoltageSource)
            ce.addComp(compJson,id1 = DCNewID+str(DCNum),canvas = buscomp.canvas, position = {'x':buscomp.position['x']+110,'y':buscomp.position['y']}, 
                    args = args, pins = pins, label = buscomp.label)
            #comment: 继续下一次循环
            continue
        #comment: 如果机器组件定义是 DCRIDType[0] (直流线路)
        elif(machine.definition == DCRIDType[0]):
            #comment: 如果 pin 0 是当前标签且有功功率大于 0
            if(machine.pins['0'] == label and val['p'] > 0):
                #comment: 更新 pf_P
                machine.args['pf_P'] = str(-val['p'])
                #comment: 更新 pf_Q
                machine.args['pf_Q'] = str(-val['q'])
                #comment: 获取直流电压
                VDC = float(machine.args['U_DC'])
                #comment: 计算直流电流
                IDC = val['p'] / VDC /2;
                #comment: 计算损耗功率
                dP = IDC**2 * float(machine.args['Rl']) * 2;
                #comment: 计算逆变侧功率
                Pinv = val['p'] - dP;
                #comment: 如果是双端直流线路，逆变侧功率减半
                if(machine.args['Hierarchy'] == '1'):
                    Pinv = Pinv / 2
                #comment: 计算逆变侧无功功率
                Qinv = Pinv * 0.4;
                #comment: 更新 pf_PINV
                machine.args['pf_PINV'] = str(Pinv)
                #comment: 更新 pf_QINV
                machine.args['pf_QINV'] = str(-Qinv)
                #comment: 更新 pf_PINV2
                machine.args['pf_PINV2'] = str(Pinv)
                #comment: 更新 pf_QINV2
                machine.args['pf_QINV2'] = str(-Qinv)
            #comment: 如果 pin 1 是当前标签且有功功率小于 0
            elif(machine.pins['1'] == label and val['p'] < 0):
                #comment: 更新 pf_PINV
                machine.args['pf_PINV'] = str(-val['p'])
                #comment: 更新 pf_QINV
                machine.args['pf_QINV'] = str(-val['q'])
                #comment: 计算总逆变侧功率
                Pinvall = -val['p']
                #comment: 如果是双端直流线路，累加 pf_PINV2
                if(machine.args['Hierarchy'] == '1'):
                    Pinvall = -val['p'] + float(machine.args['pf_PINV2'])
                #comment: 获取直流电压和电阻
                VDC = float(machine.args['U_DC'])
                R = float(machine.args['Rl'])
                #comment: 计算整流侧功率
                Pr = VDC**2/R/2 * (1-math.sqrt(1-4*R*Pinvall/VDC**2))
                #comment: 计算整流侧无功功率
                Qr = Pr * 0.4;
                #comment: 更新 pf_P
                machine.args['pf_P'] = str(-Pr)
                #comment: 更新 pf_Q
                machine.args['pf_Q'] = str(-Qr)
            #comment: 如果 pin 2 是当前标签且有功功率小于 0
            elif(machine.pins['2'] == label and val['p'] < 0):
                #comment: 更新 pf_PINV2
                machine.args['pf_PINV2'] = str(-val['p'])
                #comment: 更新 pf_QINV2
                machine.args['pf_QINV2'] = str(-val['q'])
                #comment: 计算总逆变侧功率
                Pinvall = -val['p']
                #comment: 如果是双端直流线路，累加 pf_PINV
                if(machine.args['Hierarchy'] == '1'):
                    Pinvall = -val['p'] + float(machine.args['pf_PINV'])
                #comment: 获取直流电压和电阻
                VDC = float(machine.args['U_DC'])
                R = float(machine.args['Rl'])
                #comment: 计算整流侧功率
                Pr = VDC**2/R/2 * (1-math.sqrt(1-4*R*Pinvall/VDC**2))
                #comment: 计算整流侧无功功率
                Qr = Pr * 0.4;
                #comment: 更新 pf_P
                machine.args['pf_P'] = str(-Pr)
                #comment: 更新 pf_Q
                machine.args['pf_Q'] = str(-Qr)
            #comment: 如果 pin 0 是当前标签且有功功率小于 0 (说明换流器方向反了)
            elif(machine.pins['0'] == label and val['p'] < 0):
                #comment: 复制机器组件的 JSON 数据
                compCopy = copy.deepcopy(machine.toJSON())
                #comment: 交换 i 和 j 端的参数
                machine.args['Nbi'] = compCopy['args']['Nbj']
                machine.args['Vhi'] = compCopy['args']['Vhj']
                machine.args['Vli'] = compCopy['args']['Vlj']
                machine.args['Qci'] = compCopy['args']['Qcj']
                machine.args['Sti'] = compCopy['args']['Stj']
                machine.args['Rki'] = compCopy['args']['Rkj']
                machine.args['Xki'] = compCopy['args']['Xkj']
                machine.args['Vmaxi'] = compCopy['args']['Vmaxj']
                machine.args['Vmini'] = compCopy['args']['Vminj']
                machine.args['Lsi'] = compCopy['args']['Lsj']

                machine.args['Nbj'] = compCopy['args']['Nbi']
                machine.args['Vhj'] = compCopy['args']['Vhi']
                machine.args['Vlj'] = compCopy['args']['Vli']
                machine.args['Qcj'] = compCopy['args']['Qci']
                machine.args['Stj'] = compCopy['args']['Sti']
                machine.args['Rkj'] = compCopy['args']['Rki']
                machine.args['Xkj'] = compCopy['args']['Xki']
                machine.args['Vmaxj'] = compCopy['args']['Vmaxi']
                machine.args['Vminj'] = compCopy['args']['Vmini']
                machine.args['Lsj'] = compCopy['args']['Lsi']
                
                #comment: 更新 pf_PINV
                machine.args['pf_PINV'] = str(-val['p'])
                #comment: 更新 pf_QINV
                machine.args['pf_QINV'] = str(-val['q'])

                #comment: 计算总逆变侧功率
                Pinvall = -val['p']
                #comment: 获取直流电压和电阻
                VDC = float(machine.args['U_DC'])
                R = float(machine.args['Rl'])
                #comment: 计算整流侧功率
                Pr = VDC**2/R/2 * (1-math.sqrt(1-4*R*Pinvall/VDC**2))
                #comment: 计算整流侧无功功率
                Qr = Pr * 0.4;
                #comment: 更新 pf_P
                machine.args['pf_P'] = str(-Pr)
                #comment: 更新 pf_Q
                machine.args['pf_Q'] = str(-Qr)

                #comment: 交换引脚连接
                machine.pins['0'] = compCopy['pins']['1']
                machine.pins['1'] = compCopy['pins']['0']

            #comment: 如果 pin 1 是当前标签且有功功率大于 0 (说明换流器方向反了)
            elif(machine.pins['1'] == label and val['p'] > 0):
                #comment: 复制机器组件的 JSON 数据
                compCopy = copy.deepcopy(machine.toJSON())
                #comment: 交换 i 和 j 端的参数
                machine.args['Nbi'] = compCopy['args']['Nbj']
                machine.args['Vhi'] = compCopy['args']['Vhj']
                machine.args['Vli'] = compCopy['args']['Vlj']
                machine.args['Qci'] = compCopy['args']['Qcj']
                machine.args['Sti'] = compCopy['args']['Stj']
                machine.args['Rki'] = compCopy['args']['Rkj']
                machine.args['Xki'] = compCopy['args']['Xkj']
                machine.args['Vmaxi'] = compCopy['args']['Vmaxj']
                machine.args['Vmini'] = compCopy['args']['Vminj']
                machine.args['Lsi'] = compCopy['args']['Lsj']

                machine.args['Nbj'] = compCopy['args']['Nbi']
                machine.args['Vhj'] = compCopy['args']['Vhi']
                machine.args['Vlj'] = compCopy['args']['Vli']
                machine.args['Qcj'] = compCopy['args']['Qci']
                machine.args['Stj'] = compCopy['args']['Sti']
                machine.args['Rkj'] = compCopy['args']['Rki']
                machine.args['Xkj'] = compCopy['args']['Xki']
                machine.args['Vmaxj'] = compCopy['args']['Vmaxi']
                machine.args['Vminj'] = compCopy['args']['Vmini']
                machine.args['Lsj'] = compCopy['args']['Lsi']
                
                #comment: 更新 pf_P
                machine.args['pf_P'] = str(-val['p'])
                #comment: 更新 pf_Q
                machine.args['pf_Q'] = str(-val['q'])
                #comment: 获取直流电压
                VDC = float(machine.args['U_DC'])
                #comment: 计算直流电流
                IDC = val['p'] / VDC /2;
                #comment: 计算损耗功率
                dP = IDC**2 * float(machine.args['Rl']) * 2;
                #comment: 计算逆变侧功率
                Pinv = val['p'] - dP;
                #comment: 计算逆变侧无功功率
                Qinv = Pinv * 0.4;
                #comment: 更新 pf_PINV
                machine.args['pf_PINV'] = str(Pinv)
                #comment: 更新 pf_QINV
                machine.args['pf_QINV'] = str(-Qinv)

        #comment: 如果机器组件定义是 DCRIDType[1] (ExpLoad)
        elif(machine.definition == DCRIDType[1]):
            #comment: 如果有功功率大于 0
            if(val['p'] > 0):
                #comment: 更新 p
                machine.args['p'] = str(val['p'])
                #comment: 更新 q
                machine.args['q'] = str(val['q'])
            #comment: 否则 (有功功率小于 0) (负荷变为电源)
            elif(val['p'] < 0):
                #comment: 获取交流电压源组件的 JSON 定义
                compJson = ce.compLib['_newACVoltageSource_3p']
                #comment: 定义新组件的参数 (作为电源)
                args = {
                        "BusType": "0",
                        "Name": machine.args['Name'],
                        "pf_P": str(-val['p']),
                        "pf_Q": str(-val['q']),
                    }
                #comment: 定义新组件的引脚连接
                pins= {
                        "0": "",
                        "1": machine.pins['0']
                    }
                #comment: 添加新组件
                ce.addComp(compJson,id1 = machine.id+'_DCReplace',canvas = machine.canvas, position = machine.position, args = args, pins = pins, label = machine.label)
                #comment: 移除旧组件
                ce.project.revision.implements.diagram.cells.pop(machine.id)
        #comment: 如果机器组件定义是 DCRIDType[2] (ACVoltageSource)
        elif(machine.definition == DCRIDType[2]):

            #comment: 如果有功功率大于 0 (电源变为负荷)
            if(val['p'] > 0):
                #comment: 获取 ExpLoad 组件的 JSON 定义
                compJson = ce.compLib['_newExpLoad_3p']
                #comment: 定义新组件的参数 (作为负荷)
                args = {
                    "p": str(val['p']),
                    "q": str(val['q']),
                    "v": buscomp.args['VBase']
                }
                #comment: 定义新组件的引脚连接
                pins= {
                    "0": buscomp.pins['0']
                }
                #comment: 添加新组件
                ce.addComp(compJson,id1 = machine.id+'_DCReplace',canvas = machine.canvas, position = machine.position, args = args, pins = pins, label = buscomp.label)
                #comment: 移除旧组件
                ce.project.revision.implements.diagram.cells.pop(machine.id)
            #comment: 否则 (有功功率小于 0)
            elif(val['p'] < 0):
                #comment: 更新 pf_P
                machine.args['pf_P'] = str(-val['p'])
                #comment: 更新 pf_Q
                machine.args['pf_Q'] = str(-val['q'])
    #comment: 更新 logJson，记录处理结果
    logJson .update({'QS有PSASP无的直流母线':QS1PS0List,
                    'PSASP有母线无直流设备':QS1PS0DCList})

    #comment: 初始化 setOffDCList 列表，存储被关断的直流设备
    setOffDCList = []
    #comment: 遍历所有定义为 DCRIDType[0] (直流线路) 的组件
    for key,comp in ce.project.getComponentsByRid(DCRIDType[0]).items():
        #comment: 假设需要删除
        deleteThis = True
        #comment: 如果 pin 0 或 pin 1 在 DCDict 中，则不需要删除
        if(comp.pins['0'] in DCDict.keys() or comp.pins['1'] in DCDict.keys()):
            deleteThis = False
        #comment: 如果需要删除
        if(deleteThis):
            #comment: 将标签添加到 setOffDCList
            setOffDCList.append(comp.label)
            #comment: 移除组件
            ce.project.revision.implements.diagram.cells.pop(key)

    #comment: 将 logJson 写入文件
    with open("./logJson.json","w",encoding='utf-8') as f:
        f.write(json.dumps(logJson, indent=4, ensure_ascii=False))

    #comment: 打印分隔线和 QS1PS0List 的长度
    print('————————————————————QS1PS0List————————————————————')
    print(len(QS1PS0List))
    #comment: 通过 jobmessage 发送日志信息
    jobmessage(job,"直流处理结果",key="logs",verb='append')
    jobmessage(job,"QS有PS无母线{0}".format(len(QS1PS0List)),key="logs",verb='append')
    #comment: 打印分隔线和 QS1PS0DCList 的长度
    print('————————————————————QS1PS0DCList————————————————————')
    print(len(QS1PS0DCList))
    jobmessage(job,"QS有PS无直流{0}".format(len(QS1PS0DCList)),key="logs",verb='append')
    #comment: 打印分隔线和 setOffDCList 的长度
    print('————————————————————setOffDCList————————————————————')
    print(len(setOffDCList))
    jobmessage(job,"置为关断直流{0}".format(len(setOffDCList)),key="logs",verb='append')
    #comment: 返回 logJson
    return logJson