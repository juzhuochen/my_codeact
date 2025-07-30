#comment: 导入 os 模块，用于操作系统相关功能，如文件路径操作
import os
#comment: 导入 pandas 库，用于数据处理和分析，主要用于数据框操作
import pandas as pd
#comment: 导入 time 模块，用于时间相关功能，如时间戳和延时
import time
#comment: 导入 sys 模块，用于系统相关功能，如访问命令行参数和模块路径
import sys,os

#comment: cloudpss 库，可能是用于电力系统仿真或相关云平台交互的自定义库
import cloudpss
#comment: igraph 库，用于图结构创建和操作，常用于表示网络拓扑
import igraph as ig# type: ignore
#comment: plotly.graph_objects 模块，用于创建交互式图表
import plotly.graph_objects as go
# from itertools import combinations
# from fuzzywuzzy import process
#comment: 导入 time 模块，再次导入，可能是在开发过程中冗余的导入
import time
#comment: 导入 numpy 库，用于数值计算，特别是数组和矩阵操作
import numpy as np
#comment: 导入 pandas 库，再次导入，可能是在开发过程中冗余的导入
import pandas as pd
#comment: 从 jobApi1 导入 fetch, fetchAllJob, abort 等函数，用于与作业（job）API 交互
from jobApi1 import fetch,fetchAllJob,abort# type: ignore
#comment: 从 CaseEditToolbox 导入 CaseEditToolbox 类，用于案例编辑工具箱功能
from CaseEditToolbox import CaseEditToolbox# type: ignore
#comment: 从 CaseEditToolbox 导入 is_number 函数，用于判断是否为数字
from CaseEditToolbox import is_number# type: ignore
#comment: 导入 json 模块，用于 JSON 数据的编码和解码
import json
#comment: 导入 math 模块，用于数学运算，如圆周率
import math
#comment: 导入 copy 模块，用于对象的浅复制和深复制
import copy
#comment: 从 CaseEditToolbox 导入 is_number 函数，再次导入，可能是在开发过程中冗余的导入
from CaseEditToolbox import is_number# type: ignore
#comment: 导入 re 模块，用于正则表达式操作
import re
#comment: 从 ImportQSData_xinan_2 导入所有内容，可能包含数据读取和处理相关的函数或类
from ImportQSData_xinan_2 import *

# 存在MergedG信息时注释本块

#comment: 定义一个处理交流线路的函数
#comment: job: CloudPSS作业对象，用于日志记录
#comment: qspath: QS文件路径
#comment: ce: CaseEditToolbox实例，用于操作项目元件
#comment: busLabelDict: 母线标签字典
#comment: linebus_SP: 线路母线特殊处理映射
def _process_ac_lines(job, qspath, ce, busLabelDict, linebus_SP):
    #comment: 构建 acline.txt 文件的完整路径
    qsfile = qspath + 'acline.txt'
    #comment: 读取 acline.txt 文件中的信息到 infoDict，指定编码和类型
    infoDict = ReadQSInfo(qsfile,encoding='utf-8',type='line')
    #comment: 初始化 LineDict，用于存储处理后的线路信息
    LineDict = {}
    #comment: 遍历 infoDict 中的每条线路数据
    for i in range(len(infoDict['psline'])):
        #comment: 获取线路的 PS 命名
        psline = infoDict['psline'][i]
        #comment: 获取线路的启用状态
        ison = infoDict['ison'][i]
        
        #comment: 获取线路的起始母线 PS 命名
        busi = infoDict['busi'][i]
        #comment: 获取线路的终止母线 PS 命名
        busj = infoDict['busj'][i]

        #comment: 获取线路的起始母线 IEEE 命名
        ieeebusi = infoDict['ieeebusi'][i]
        #comment: 获取线路的终止母线 IEEE 命名
        ieeebusj = infoDict['ieeebusj'][i]

        #comment: 获取线路的电阻值
        r = infoDict['r'][i]
        #comment: 获取线路的电抗值
        x = infoDict['x'][i]
        #comment: 获取线路的导纳值
        b = infoDict['b'][i]
        #comment: 获取线路的基准电压
        Vbase = infoDict['Vbase'][i]
        #comment: 如果起始母线的 IEEE 命名存在于 special_processing 映射中，则更新起始母线 PS 命名
        if(ieeebusi in linebus_SP.keys()):
            busi = linebus_SP[ieeebusi]
        #comment: 如果终止母线的 IEEE 命名存在于 special_processing 映射中，则更新终止母线 PS 命名
        if(ieeebusj in linebus_SP.keys()):
            busj = linebus_SP[ieeebusj]

        #comment: 再次获取线路的启用状态，可能冗余
        ison = infoDict['ison'][i]
        #comment: 获取线路的 IEEE 名称
        ieeeName = infoDict['ieeeName'][i]
        #comment: 默认线路类型为 'long'
        type='long'
        #comment: 如果 IEEE 名称是特定值，则线路类型为 'short'
        if(ieeeName in ['短接线','站内线','LGJQ-500-7.5']):
            type = 'short'
        
        #comment: 如果当前线路 PS 命名不在 LineDict 中，则初始化其条目并添加 ids 列表
        if(psline not in LineDict.keys()):
            LineDict[psline] = {'ids':[]}
        
        #comment: 更新 LineDict 中当前线路的信息
        LineDict[psline].update({'type':type,'ison':ison,'busi':busi,'busj':busj,'ieeebusi':ieeebusi,'ieeebusj':ieeebusj,'r':r,'b':b,'x':x,'Vbase':Vbase})

        #comment: 将当前行的 id 添加到 LineDict 中对应线路的 ids 列表
        LineDict[psline]['ids'].append(infoDict['id'][i])
    
    #comment: 构建 UQSLine.txt 文件的完整路径
    qsfile = qspath + 'UQSLine.txt'
    #comment: 读取 UQSLine.txt 文件中的信息到 ULineinfoDict
    ULineinfoDict = ReadQSInfo(qsfile,encoding='utf-8')

    #comment: 定义交流线路元件的 RID 类型
    LineRIDType = ['model/CloudPSS/TranssmissionLineRouter']
    #comment: 初始化标签列表，用于收集现有线路的标签
    labelList = []
    #comment: 初始化 QS 中有但 PS 中没有的线路列表
    QS1PS0List = []
    #comment: 初始化需要关断的线路列表（PS 中找到，但 QS 中 ison 为 0）
    setOffList = []
    #comment: 初始化需要关断的线路列表（PS 中找到，但 QS 中不存在或需要删除）
    setOffList1 = []
    #comment: 初始化新增线路列表
    AddedLineList = []
    #comment: 初始化连接母线集合
    connectedBus = set()
    #comment: 设置元件标签字典，用于快速查找元件
    ce.setCompLabelDict()
    #comment: 遍历项目中所有 TranssmissionLineRouter 类型的元件，收集其标签
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/TranssmissionLineRouter').items():
        if(j.label not in labelList):
            labelList.append(j.label)
    #comment: 获取母线标签字典的所有键 (母线名称)
    busList = list(busLabelDict.keys())
    #comment: 定义新增线路的 ID 前缀
    LineIDNew = 'AddedLines_'
    #comment: 初始化线路计数器
    LineNum1 = 0

    #comment: 初始化母线输入集合
    busIn = set()

    #comment: 遍历 LineDict 中的每条线路 (label 为线路名称，val 为线路属性)
    for label,val in LineDict.items():
        #comment: 将线路的起始和终止母线添加到 busIn 集合，用于统计涉及的母线
        busIn.add(val['busi'])
        busIn.add(val['busj'])
        #comment: 初始化 linecomp 为 None
        linecomp = None
        #comment: 如果当前线路标签不在现有线路标签列表 (labelList) 中
        if(label not in labelList):
            #comment: 如果该线路在 QS 中为启用状态且类型为 'long'
            if(val['ison']==1 and val['type'] == 'long'):
                #comment: 打印并记录该线路在 PS 中不存在的信息
                print(label+' 线路不存在！');
                jobmessage(job,label+' 线路不存在！',key="logs",verb='append')
                QS1PS0List.append(label)
            #comment: 继续处理下一条线路
            continue
        #comment: 如果线路标签存在，遍历 ce.compLabelDict 中该标签对应的元件
        for i,j in ce.compLabelDict[label].items():
            #comment: 如果元件的定义是线路类型，则将其赋值给 linecomp
            if(j.definition in LineRIDType):
                linecomp = j
        #comment: 如果线路在 QS 中为禁用状态 (ison == 0)
        if(val['ison']==0):
            #comment: 设置元件的 enabled 属性为 False
            linecomp.props['enabled']=False
            #comment: 从项目修订中删除该元件
            ce.project.revision.implements.diagram.cells.pop(linecomp.id)
            #comment: 将该线路标签添加到 setOffList (关断列表)
            setOffList.append(label)
        #comment: 如果线路为启用状态
        else:
            #comment: 如果线路的电抗值大于 1e-9 (非零)
            if(val['x'] > 1e-9):
                #comment: 获取线路的长度参数
                ltemp = float(linecomp.args['Length']);
                #comment: 如果 X1pu * B1pu 等于 0 且 X1pu * 长度小于等于 1e-4，设置 Zero 参数为 '0'
                if(float(linecomp.args['X1pu'])*float(linecomp.args['B1pu'])==0 and float(linecomp.args['X1pu'])*ltemp<=1e-4):
                    linecomp.args['Zero'] = '0'
                #comment: 设置 ModelType 和 Decoupled 参数为 '0'
                linecomp.args['ModelType'] = '0'
                linecomp.args['Decoupled'] = '0'
                #comment: 设置 Length 参数为 '1'
                linecomp.args['Length'] = '1'
                #comment: 更新线路的 R1pu (电阻)、X1pu (电抗)、B1pu (导纳) 和 Vbase (基准电压) 参数
                linecomp.args['R1pu'] = str(val['r'])
                linecomp.args['X1pu'] = str(val['x'])
                linecomp.args['B1pu'] = str(val['b'])
                linecomp.args['Vbase'] = str(val['Vbase'])
                #comment: 更新线路的 R0pu、X0pu、B0pu 参数，乘以长度
                linecomp.args['R0pu'] = str(ltemp*float(linecomp.args['R0pu']))
                linecomp.args['X0pu'] = str(ltemp*float(linecomp.args['X0pu']))
                linecomp.args['B0pu'] = str(ltemp*float(linecomp.args['B0pu']))

    #comment: 遍历项目中所有 TranssmissionLineRouter
    for key,comp in ce.project.getComponentsByRid('model/CloudPSS/TranssmissionLineRouter').items():
        #comment: 标志是否需要删除当前元件
        deleteThis = True
        #comment: 如果元件标签存在于 LineDict 中，则不需要删除
        if(comp.label in LineDict.keys()):
            deleteThis = False
        #comment: 如果需要删除 (元件标签不在 LineDict 中)
        if(deleteThis):
            #comment: 将该元件标签添加到 setOffList1 (待删除或关断列表)
            setOffList1.append(comp.label)
            #comment: 从项目修订中删除该元件
            ce.project.revision.implements.diagram.cells.pop(key)

    #comment: 定义电压基准字典，将标称电压映射到实际基准电压
    VbaseDict = {220:230,500:525,110:115,35:37}
    #comment: 定义新增母线 ID 前缀
    AddBusID0 = 'AddedBuses'
    #comment: 定义新增线路 ID 前缀
    AddLineID0 = 'AddedLines'
    #comment: 初始化新增母线列表
    AddedBuses = []
    #comment: 遍历 ULineinfoDict 中的每条线路信息 (待新增线路)
    for i in range(len(ULineinfoDict['Name'])):
        #comment: 如果线路的起始或终止母线有一个是关断的，则跳过
        if(ULineinfoDict['I_off'][i]+ULineinfoDict['J_off'][i]>=1):
            continue
        #comment: 如果起始母线不在现有母线列表中
        if(ULineinfoDict['psNameI'][i] not in busList):
            #comment: 获取新母线的元件 JSON 定义
            compJson = ce.compLib['_newBus_3p']
            #comment: 设置新母线标签
            label = ULineinfoDict['psNameI'][i]
            #comment: 获取新母线的基准电压
            VBase = ULineinfoDict['Vbase'][i]
            #comment: 如果基准电压在 VbaseDict 中，更新为映射值
            if(VBase in VbaseDict.keys()):
                VBase = VbaseDict[VBase]
            #comment: 设置新母线的参数
            args = {
                "Name": label,
                "VBase": str(VBase),
            }
            #comment: 设置新母线的引脚连接
            pins= {
                "0": label
            }
            #comment: 在画布上添加新母线元件
            ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
            #comment: 将新母线添加到 AddedBuses 列表
            AddedBuses.append(label)
            #comment: 将新母线添加到 busList
            busList.append(label)
        #comment: 如果终止母线不在现有母线列表中 (类似起始母线处理)
        if(ULineinfoDict['psNameJ'][i] not in busList):
            compJson = ce.compLib['_newBus_3p']
            label = ULineinfoDict['psNameJ'][i]
            VBase = ULineinfoDict['Vbase'][i]
            if(VBase in VbaseDict.keys()):
                VBase = VbaseDict[VBase]
            args = {
                "Name": label,
                "VBase": str(VBase),
            }
            pins= {
                "0": label
            }
            ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
            AddedBuses.append(label)
            busList.append(label)

        #comment: 获取新线路的元件 JSON 定义
        compJson = ce.compLib['TranssmissionLineRouter']
        #comment: 获取新线路的基准电压
        VBase = ULineinfoDict['Vbase'][i]
        #comment: 如果基准电压在 VbaseDict 中，更新为映射值
        if(VBase in VbaseDict.keys()):
            VBase = VbaseDict[VBase]
        #comment: 设置新线路标签
        label = ULineinfoDict['Name'][i]
        #comment: 设置新线路的参数
        args = {
            "Name": label,
            "Vbase": str(VBase),
            'Length':'1',
            'ModelType':'0',
            'Decoupled':'0',
            'Zero':'0',
            'R1pu':str(ULineinfoDict['r'][i]),
            'X1pu':str(abs(ULineinfoDict['x'][i])),
            'B1pu':str(ULineinfoDict['b/2'][i]*2)
        }
        #comment: 设置新线路的引脚连接
        pins= {
            "0": ULineinfoDict['psNameI'][i],
            "1": ULineinfoDict['psNameJ'][i]
        }
        #comment: 在画布上添加新线路元件
        ce.addCompInCanvas(compJson,AddLineID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
        #comment: 将新线路添加到 AddedLineList
        AddedLineList.append(label)

    #comment: 初始化日志 JSON 对象
    logJson = {}
    #comment: 更新日志 JSON，记录 QS 中有但 PS 中没有的传输线和关断的传输线
    logJson.update({'QS有PSASP无的传输线':QS1PS0List,'关断的传输线':setOffList})
    #comment: 将日志 JSON 写入 logJson.json 文件，以美观的格式输出
    with open("./logJson.json","w",encoding='utf-8') as f:
        f.write(json.dumps(logJson, indent=4, ensure_ascii=False))

    #comment: 打印 QS1PS0List 的分隔符和长度信息
    print('————————————————————QS1PS0List————————————————————')
    print(len(QS1PS0List))
    #comment: 通过 jobmessage 记录 QS 有但 PS 无的线路数量
    jobmessage(job,"线路汇总-QS有PS无: {0}".format(len(QS1PS0List)),key="logs",verb='append')
    #comment: 打印 setOffList 的分隔符和长度信息
    print('————————————————————setOffList————————————————————')
    print(len(setOffList))
    #comment: 打印 setOffList1 的分隔符和长度信息 (待删除或关断的线路)
    print('————————————————————setOffList1————————————————————')
    print(len(setOffList1))
    #comment: 通过 jobmessage 记录设为关断的线路数量
    jobmessage(job,"线路汇总-置为关断: {0}".format(len(setOffList1)),key="logs",verb='append')
    #comment: 打印 AddedLineList 的分隔符和长度信息
    print('————————————————————AddedLineList————————————————————')
    print(len(AddedLineList))
    #comment: 通过 jobmessage 记录新增线路的数量
    jobmessage(job,"线路汇总-新增线路: {0}".format(len(AddedLineList)),key="logs",verb='append')
    #comment: 打印 AddedBuses 的分隔符和长度信息
    print('————————————————————AddedBuses————————————————————')
    print(len(AddedBuses))
    #comment: 通过 jobmessage 记录新增母线的数量
    jobmessage(job,"线路汇总-新增母线: {0}".format(len(AddedBuses)),key="logs",verb='append')
    #comment: 返回更新后的母线列表、电压基准字典、日志 JSON、IEEE 起始母线和 IEEE 终止母线 (这部分返回可能不完全正确，因为 ieeebusi 和 ieeebusj 是循环内的局部变量，这里的值是最后一次循环的值)
    return busList, VbaseDict, logJson,ieeebusi,ieeebusj

#comment: 定义一个处理串联补偿器的函数
#comment: job: CloudPSS作业对象
#comment: qspath: QS文件路径
#comment: ce: CaseEditToolbox实例
#comment: busList: 当前的母线列表
#comment: VbaseDict: 电压基准字典
def _process_series_compensators(job, qspath, ce, busList, VbaseDict):
    #comment: 构建 cs.txt 文件的完整路径
    qsfile = qspath + 'cs.txt'
    #comment: 读取 cs.txt 文件中的信息到 CSinfoDict
    CSinfoDict = ReadQSInfo(qsfile,encoding='utf-8')
    
    #comment: 定义新增母线 ID 前缀
    AddBusID0 = 'AddedBuses'
    #comment: 定义新增串补 ID 前缀
    AddCSID0 = 'AddedCSs'
    #comment: 初始化新增母线列表
    AddedBuses = []
    #comment: 遍历 CSinfoDict 中的每条串补信息
    for i in range(len(CSinfoDict['lineName'])):
        #comment: 如果串补状态为 0 (禁用)，则跳过
        if(CSinfoDict['status'][i]==0):
            continue
        #comment: 如果串补的起始母线不在当前母线列表中
        if(CSinfoDict['I_PSname'][i] not in busList):
            #comment: 获取新母线的元件 JSON 定义
            compJson = ce.compLib['_newBus_3p']
            #comment: 设置新母线标签
            label = CSinfoDict['I_PSname'][i]
            #comment: 获取新母线的基准电压
            VBase = CSinfoDict['Vbase'][i]
            #comment: 设置新母线的参数
            args = {
                "Name": label,
                "VBase": str(VBase),
            }
            #comment: 设置新母线的引脚连接
            pins= {
                "0": label
            }
            #comment: 在画布上添加新母线元件
            ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
            #comment: 将新母线添加到 AddedBuses 列表
            AddedBuses.append(label)
            #comment: 将新母线添加到 busList
            busList.append(label)
        #comment: 如果串补的终止母线不在当前母线列表中 (类似起始母线处理)
        if(CSinfoDict['J_PSname'][i] not in busList):
            compJson = ce.compLib['_newBus_3p']
            label = CSinfoDict['J_PSname'][i]
            VBase = CSinfoDict['Vbase'][i]
            args = {
                "Name": label,
                "VBase": str(VBase),
            }
            pins= {
                "0": label
            }
            ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
            AddedBuses.append(label)
            busList.append(label)
        
        #comment: 如果串补的电抗值小于 0 (表示是电容)
        if(CSinfoDict['x'][i] < 0):
            #comment: 获取新电容的元件 JSON 定义
            compJson = ce.compLib['newCapacitorRouter']
            #comment: 获取新电容的基准电压
            VBase = CSinfoDict['Vbase'][i]
            #comment: 如果基准电压在 VbaseDict 中，更新为映射值
            if(VBase in VbaseDict.keys()):
                VBase = VbaseDict[VBase]
            #comment: 设置新电容标签
            label = CSinfoDict['lineName'][i]
            #comment: 设置新电容的参数 (计算电容值 C)
            args = {
                "C": str(-1/math.pi/100/CSinfoDict['x'][i] * 1e6), # 假设频率为 50Hz，C = 1/(2*pi*f*Xc)，Xc = -x
                "Dim": "1",
                "Name": label,
                "V": ""
            }
            #comment: 设置新电容的引脚连接
            pins= {
                "0": CSinfoDict['I_PSname'][i],
                "1": CSinfoDict['J_PSname'][i]
            }
            #comment: 在画布上添加新电容元件
            ce.addCompInCanvas(compJson,AddCSID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                                pins = pins, label = label,dX = 10, MaxX = 500)

#comment: 定义一个处理变压器的函数
#comment: job: CloudPSS作业对象
#comment: qspath: QS文件路径
#comment: ce: CaseEditToolbox实例
#comment: busLabelDict: 母线标签字典
#comment: linebus_SP: 线路母线特殊处理映射
#comment: T3WCentDict: 三绕组变压器中心节点字典
#comment: ieeebusi: IEEE 起始母线
#comment: ieeebusj: IEEE 终止母线
def _process_transformers(job, qspath, ce, busLabelDict, linebus_SP, T3WCentDict,ieeebusi,ieeebusj):
    # 双绕组变压器
    #comment: 构建 2wTsf.txt 文件的完整路径
    qsfile = qspath + '2wTsf.txt'
    #comment: 读取 2wTsf.txt 文件中的信息到 infoDict，指定编码和类型
    infoDict = ReadQSInfo(qsfile,encoding='UTF-8',type='2wT')
    #comment: 初始化 T2WDict，用于存储处理后的双绕组变压器信息
    T2WDict = {}
    #comment: 遍历 infoDict 中的每条双绕组变压器数据
    for i in range(len(infoDict['psName'])):
        #comment: 获取变压器的 PS 命名
        psName = infoDict['psName'][i]
        #comment: 获取变压器的一次侧母线 PS 命名
        busi = infoDict['busi'][i]
        #comment: 获取变压器的二次侧母线 PS 命名
        busj = infoDict['busj'][i]
        #comment: 如果一次侧的 IEEE 命名存在于 special_processing 映射中，则更新一次侧母线 PS 命名
        if(ieeebusi in linebus_SP.keys()):
            busi = linebus_SP[ieeebusi]
        #comment: 如果二次侧的 IEEE 命名存在于 special_processing 映射中，则更新二次侧母线 PS 命名
        if(ieeebusj in linebus_SP.keys()):
            busj = linebus_SP[ieeebusj]

        #comment: 如果当前变压器 PS 命名不在 T2WDict 中，则初始化其条目并添加 ids 列表
        if(psName not in T2WDict.keys()):
            T2WDict[psName] = {'ids':[]}
        
        #comment: 更新 T2WDict 中当前变压器的所有信息
        T2WDict[psName].update({j:infoDict[j][i] for j in infoDict.keys()})
        #comment: 将当前行的 id 添加到 T2WDict 中对应变压器的 ids 列表
        T2WDict[psName]['ids'].append(infoDict['id'][i])
        
    #comment: 定义双绕组变压器元件的 RID 类型
    LineRIDType = ['model/CloudPSS/_newTransformer_3p2w']
    #comment: 初始化标签列表，用于收集现有双绕组变压器的标签
    labelList = []
    #comment: 初始化 QS 中有但 PS 中没有的双绕组变压器列表
    QS1PS0List = []
    #comment: 初始化需要关断的双绕组变压器列表（PS 中找到，但 QS 中 I_off 和 J_off 都为 1）
    setOffList = []
    #comment: 初始化需要关断的双绕组变压器列表（PS 中找到，但 QS 中不存在或需要删除）
    setOffList1 = []
    #comment: 初始化新增线路列表 (此命名在此上下文可能不准确，应为新增变压器列表)
    AddedLineList = []
    #comment: 初始化连接母线集合
    connectedBus = set()
    #comment: 设置元件标签字典
    ce.setCompLabelDict()
    #comment: 遍历项目中所有 _newTransformer_3p2w 类型的元件，收集其标签
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p2w').items():
        if(j.label not in labelList):
            labelList.append(j.label)
    #comment: 获取母线标签字典的所有键 (母线名称)
    busList = busLabelDict.keys()
    #comment: 定义新增双绕组变压器的 ID 前缀
    LineIDNew = 'AddedT2Ws_'
    #comment: 初始化线路计数器
    LineNum1 = 0

    #comment: 初始化母线输入集合
    busIn = set()

    #comment: 遍历 T2WDict 中的每个双绕组变压器 (label 为变压器名称，val 为变压器属性)
    for label,val in T2WDict.items():
        #comment: 将变压器的一次侧和二次侧母线添加到 busIn 集合
        busIn.add(val['busi'])
        busIn.add(val['busj'])
        #comment: 初始化 linecomp 为 None
        linecomp = None
        #comment:如果当前变压器标签不在现有变压器标签列表 (labelList) 中
        if(label not in labelList):
            #comment: 如果该变压器在 QS 中为启用状态
            if(val['ison']==1):
                #comment: 打印并记录该双绕组变压器在 PS 中不存在的信息
                print(label+' 双绕组变压器不存在！');
                QS1PS0List.append(label)
            #comment: 继续处理下一条变压器
            continue
        #comment: 如果变压器标签存在，遍历 ce.compLabelDict 中该标签对应的元件
        for i,j in ce.compLabelDict[label].items():
            #comment: 如果元件的定义是双绕组变压器类型，则将其赋值给 linecomp
            if(j.definition in LineRIDType):
                linecomp = j
        #comment: 如果变压器的 I_off 和 J_off 字段之和大于等于 2 (表示两端都关断)
        if((val['I_off']==1) + (val['J_off']==1) >= 2):
            #comment: 设置元件的 enabled 属性为 False
            linecomp.props['enabled']=False
            #comment: 从项目修订中删除该元件
            ce.project.revision.implements.diagram.cells.pop(linecomp.id)
            #comment: 将该变压器标签添加到 setOffList (关断列表)
            setOffList.append(label)
        #comment: 如果变压器为启用状态
        else:
            #comment: 获取变压器的引脚连接 (端口名称)
            linecompPins = [linecomp.pins['0'],linecomp.pins['1']];
            #comment: 找到一次侧母线在引脚中的索引
            flagi = linecompPins.index(val['busi'])
            #comment: 找到二次侧母线在引脚中的索引
            flagj = linecompPins.index(val['busj'])
            #comment: 处理一次侧和二次侧的变比 ki 和 kj，如果为 0 则设为 1
            ki = 1 if val['ki']==0 else val['ki']
            kj = 1 if val['kj']==0 else val['kj']
            #comment: 更新变压器的 V1 和 V2 参数 (电压基准)
            linecomp.args['V'+str(flagi+1)] = val['Vbasei']*ki
            linecomp.args['V'+str(flagj+1)] = val['Vbasej']*kj
            #comment: 根据 flaigi 确定 k0 的值
            k0 = [ki,kj][flagi]
            if(flagi==0):
                k0 = 1;
            #comment: 更新变压器的 Rl (电阻) 和 Xl (电抗) 参数，并进行变比修正
            linecomp.args['Rl'] = val['ri']/(k0**2)
            linecomp.args['Xl'] = val['xi']/(k0**2)
            
    #comment: 遍历项目中所有 _newTransformer_3p2w 类型的元件
    for key,comp in ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p2w').items():
        #comment: 标志是否需要删除当前元件
        deleteThis = True
        #comment: 如果元件标签存在于 T2WDict 中，则不需要删除
        if(comp.label in T2WDict.keys()):
            deleteThis = False
        #comment: 如果需要删除 (元件标签不在 T2WDict 中)
        if(deleteThis):
            #comment: 将该元件标签添加到 setOffList1 (待删除或关断列表)
            setOffList1.append(comp.label)
            #comment: 从项目修订中删除该元件
            ce.project.revision.implements.diagram.cells.pop(key)
    #comment: 打印 setOffList 长度信息
    print('________________setOffList_______________')
    print(len(setOffList))
    
    #comment: 打印 setOffList1 长度信息
    print('________________setOffList1_______________')
    print(len(setOffList1))
    #comment: 打印 QS1PS0List 内容
    print(QS1PS0List)
    #comment: 通过 jobmessage 记录变压器处理结果的通用消息
    jobmessage(job,"变压器处理结果：",key="logs",verb='append')
    #comment: 通过 jobmessage 记录关断双绕组变压器的数量
    jobmessage(job,"关断双绕组变压器: {0}".format(len(setOffList1)),key="logs",verb='append')

    # 三绕组变压器
    #comment: 构建 3wTsf.txt 文件的完整路径
    qsfile = qspath + '3wTsf.txt'
    #comment: 读取 3wTsf.txt 文件中的信息到 infoDict，指定编码和类型
    infoDict = ReadQSInfo(qsfile,encoding='UTF-8',type='3wT')
    #comment: 初始化 T3WDict，用于存储处理后的三绕组变压器信息
    T3WDict = {}
    #comment: 遍历 infoDict 中的每条三绕组变压器数据
    for i in range(len(infoDict['psName'])):
        #comment: 获取变压器的 PS 命名
        psName = infoDict['psName'][i]
        #comment: 获取变压器的一次侧母线 PS 命名
        busi = infoDict['busi'][i]
        #comment: 获取变压器的二次侧母线 PS 命名
        busj = infoDict['busj'][i]
        #comment: 如果一次侧的 IEEE 命名存在于 special_processing 映射中，则更新一次侧母线 PS 命名
        if(ieeebusi in linebus_SP.keys()):
            busi = linebus_SP[ieeebusi]
        #comment: 如果二次侧的 IEEE 命名存在于 special_processing 映射中，则更新二次侧母线 PS 命名
        if(ieeebusj in linebus_SP.keys()):
            busj = linebus_SP[ieeebusj]
        #comment: 如果当前变压器 PS 命名不在 T3WDict 中，则初始化其条目并添加 ids 列表
        if(psName not in T3WDict.keys()):
            T3WDict[psName] = {'ids':[]}
        
        #comment: 更新 T3WDict 中当前变压器的所有信息
        T3WDict[psName].update({j:infoDict[j][i] for j in infoDict.keys()})
        #comment: 将当前行的 id 添加到 T3WDict 中对应变压器的 ids 列表
        T3WDict[psName]['ids'].append(infoDict['id'][i])

    #comment: 定义三绕组变压器元件的 RID 类型
    LineRIDType = ['model/CloudPSS/_newTransformer_3p3w']
    #comment: 初始化标签列表，用于收集现有三绕组变压器的标签
    labelList = []
    #comment: 初始化 QS 中有但 PS 中没有的三绕组变压器列表
    QS1PS0List = []
    #comment: 初始化需要关断的三绕组变压器列表
    setOffList = []
    #comment: 初始化需要关断的三绕组变压器列表（PS 中找到，但 QS 中不存在或需要删除）
    setOffList1 = []
    #comment: 初始化新增线路列表 (此命名在此上下文可能不准确，应为新增变压器列表)
    AddedLineList = []
    #comment: 初始化连接母线集合
    connectedBus = set()
    #comment: 设置元件标签字典
    ce.setCompLabelDict()
    #comment: 遍历项目中所有 _newTransformer_3p3w 类型的元件，收集其标签
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p3w').items():
        if(j.label not in labelList):
            labelList.append(j.label)
    #comment: 获取母线标签字典的所有键 (母线名称)
    busList = busLabelDict.keys()
    #comment: 定义新增三绕组变压器的 ID 前缀
    LineIDNew = 'AddedT3Ws_'
    #comment: 初始化线路计数器
    LineNum1 = 0

    #comment: 初始化母线输入集合
    busIn = set()

    #comment: 遍历 T3WDict 中的每个三绕组变压器 (label 为变压器名称，val 为变压器属性)
    for label,val in T3WDict.items():
        #comment: 将变压器的三侧母线添加到 busIn 集合
        busIn.add(val['busi'])
        busIn.add(val['busj'])
        busIn.add(val['busk'])
        #comment: 初始化 linecomp 为 None
        linecomp = None
        #comment: 如果当前变压器标签不在现有变压器标签列表 (labelList) 中
        if(label not in labelList):
            #comment: 如果该变压器在 QS 中为启用状态，且至少有两端关断
            if((val['I_off']==1) + (val['J_off']==1) + (val['K_off']==1) >= 2):
                #comment: 打印并记录该三绕组变压器在 PS 中不存在的信息
                print(label+' 三绕组变压器不存在！');
                QS1PS0List.append(label)
            #comment: 继续处理下一条变压器
            continue
        #comment: 如果变压器标签存在，遍历 ce.compLabelDict 中该标签对应的元件
        for i,j in ce.compLabelDict[label].items():
            #comment: 如果元件的定义是三绕组变压器类型，则将其赋值给 linecomp
            if(j.definition in LineRIDType):
                linecomp = j
        #comment: 如果变压器的 I_off, J_off 和 K_off 字段之和大于等于 2 (表示至少两端关断)
        if((val['I_off']==1) + (val['J_off']==1) + (val['K_off']==1) >= 2):
            #comment: 设置元件的 enabled 属性为 False
            linecomp.props['enabled']=False
            #comment: 从项目修订中删除该元件
            ce.project.revision.implements.diagram.cells.pop(linecomp.id)
            #comment: 将该变压器标签添加到 setOffList (关断列表)
            setOffList.append(label)
        #comment: 如果变压器为启用状态
        else:
            #comment: 获取变压器的引脚连接 (端口名称)
            linecompPins = [linecomp.pins['0'],linecomp.pins['1'],linecomp.pins['2']];
            #comment: 找到一次侧、二次侧和三次侧母线在引脚中的索引
            flagi = linecompPins.index(val['busi'])
            flagj = linecompPins.index(val['busj'])
            flagk = linecompPins.index(val['busk'])

            #comment: 更新变压器的 V1, V2, V3 参数 (电压基准和变比)
            linecomp.args['V'+str(flagi+1)] = val['Vbasei']*(1 if val['ki']==0 else val['ki'])
            linecomp.args['V'+str(flagj+1)] = val['Vbasej']*(1 if val['kj']==0 else val['kj'])
            linecomp.args['V'+str(flagk+1)] = val['Vbasek']*(1 if val['kk']==0 else val['kk'])
            #comment: 更新变压器的 Rl12, Rl23, Rl13 (电阻) 参数，根据相应侧的电阻之和
            linecomp.args['Rl' + str(min(flagi,flagj)+1) + str(max(flagi,flagj)+1)] = str(abs(val['Ri']+val['Rj']))
            linecomp.args['Rl' + str(min(flagj,flagk)+1) + str(max(flagj,flagk)+1)] = str(abs(val['Rj']+val['Rk']))
            linecomp.args['Rl' + str(min(flagi,flagk)+1) + str(max(flagi,flagk)+1)] = str(abs(val['Ri']+val['Rk']))
            #comment: 更新变压器的 Xl12, Xl23, Xl13 (电抗) 参数，根据相应侧的电抗之和
            linecomp.args['Xl' + str(min(flagi,flagj)+1) + str(max(flagi,flagj)+1)] = str(abs(val['Xi']+val['Xj']))
            linecomp.args['Xl' + str(min(flagj,flagk)+1) + str(max(flagj,flagk)+1)] = str(abs(val['Xj']+val['Xk']))
            linecomp.args['Xl' + str(min(flagi,flagk)+1) + str(max(flagi,flagk)+1)] = str(abs(val['Xi']+val['Xk']))
            
    #comment: 遍历项目中所有 _newTransformer_3p3w 类型的元件
    for key,comp in ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p3w').items():
        #comment: 标志是否需要删除当前元件
        deleteThis = True
        #comment: 如果元件标签存在于 T3WDict 中，则不需要删除
        if(comp.label in T3WDict.keys()):
            deleteThis = False
        #comment: 如果需要删除 (元件标签不在 T3WDict 中)
        if(deleteThis):
            #comment: 将该元件标签添加到 setOffList1 (待删除或关断列表)
            setOffList1.append(comp.label)
            #comment: 从项目修订中删除该元件
            ce.project.revision.implements.diagram.cells.pop(key)
    #comment: 打印 setOffList 长度信息
    print('________________setOffList_______________')
    print(len(setOffList))
    #comment: 打印 setOffList1 长度信息
    print('________________setOffList1_______________')
    print(len(setOffList1))
    #comment: 打印 QS1PS0List 内容
    print(QS1PS0List)
    #comment: 通过 jobmessage 记录关断三绕组变压器的数量
    jobmessage(job,"关断三绕组变压器: {0}".format(len(setOffList1)),key="logs",verb='append')

    #comment: 构建 UQStsf.txt 文件的完整路径
    qsfile = qspath + 'UQStsf.txt'
    #comment: 读取 UQStsf.txt 文件中的信息到 UTSinfoDict (待新增变压器信息)
    UTSinfoDict = ReadQSInfo(qsfile,encoding='utf-8')

    #comment: 读取 TW3.csv 文件，加载三绕组变压器的中心节点信息
    df = pd.read_csv("./QSSpecial/TW3.csv",encoding="utf-8")
    #comment: 丢弃第一行 (通常是表头)
    df.drop(0)
    #comment: 将数据转换为 NumPy 数组
    dfa = np.array(df)
    #comment: 更新 T3WCentDict，将变压器名称映射到其中心节点
    T3WCentDict.update({dfa[i,1]:dfa[i,9] for i in range(len(dfa[:,1]))})

    #comment: 定义电压基准字典
    VbaseDict = {220:230,500:525,110:115,35:37}
    #comment: 定义新增母线 ID 前缀
    AddBusID0 = 'AddedBuses'
    #comment: 定义新增变压器 ID 前缀
    AddTSID0 = 'AddedTransformers'
    #comment: 初始化新增母线列表
    AddedBuses = []
    #comment: 初始化新增双绕组变压器列表
    AddedT2Ws = []
    #comment: 初始化新增三绕组变压器列表
    AddedT3Ws = []
    #comment: 获取项目中所有 _newBus_3p 类型元件的标签作为当前母线列表
    busList = [j.label for j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').values()]

    #comment: 遍历 UTSinfoDict 中的每条待新增变压器信息
    for i in range(len(UTSinfoDict['Name'])):
        #comment: 如果一次侧母线不在当前母线列表中，则创建并添加新母线
        if(UTSinfoDict['psNameI'][i] not in busList):
            compJson = ce.compLib['_newBus_3p']
            label = UTSinfoDict['psNameI'][i]
            VBase = UTSinfoDict['Vi_base'][i]
            args = {
                "Name": label,
                "VBase": str(VBase),
            }
            pins= {
                "0": label
            }
            ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
            AddedBuses.append(label)
            busList.append(label)
        #comment: 如果二次侧母线不在当前母线列表中，则创建并添加新母线
        if(UTSinfoDict['psNameJ'][i] not in busList):
            compJson = ce.compLib['_newBus_3p']
            label = UTSinfoDict['psNameJ'][i]
            VBase = UTSinfoDict['Vj_base'][i]
            args = {
                "Name": label,
                "VBase": str(VBase),
            }
            pins= {
                "0": label
            }
            ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                            pins = pins, label = label,dX = 10, MaxX = 500)
            AddedBuses.append(label)
            busList.append(label)

        #comment: 判断是否为三绕组变压器 (K 侧不为 'null'，且 I 和 J 侧也不为 'null')
        if(UTSinfoDict['psNameK'][i] != 'null' and UTSinfoDict['psNameI'][i] != 'null' and UTSinfoDict['psNameJ'][i] != 'null'):
            #comment: 如果三次侧母线不在当前母线列表中，则创建并添加新母线
            if(UTSinfoDict['psNameK'][i] not in busList):
                compJson = ce.compLib['_newBus_3p']
                label = UTSinfoDict['psNameK'][i]
                VBase = UTSinfoDict['Vk_base'][i]
                args = {
                    "Name": label,
                    "VBase": str(VBase),
                }
                pins= {
                    "0": label
                }
                ce.addCompInCanvas(compJson,AddBusID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                                pins = pins, label = label,dX = 10, MaxX = 500)
                AddedBuses.append(label)
                busList.append(label)
            #comment: 获取三绕组变压器的元件 JSON 定义
            compJson = ce.compLib['_newTransformer_3p3w']
            #comment: 计算三侧的电压基准 (考虑变比)
            VBaseI = UTSinfoDict['Vi_base'][i]*UTSinfoDict['ki'][i]
            VBaseJ = UTSinfoDict['Vj_base'][i]*UTSinfoDict['kj'][i]
            VBaseK = UTSinfoDict['Vk_base'][i]*UTSinfoDict['kk'][i]
            #comment: 设置新三绕组变压器标签
            label = UTSinfoDict['Name'][i]
            #comment: 设置新三绕组变压器的参数
            args = {
                "Name": label,
                'V1':str(VBaseI),
                'V2':str(VBaseJ),
                'V3':str(VBaseK),
                'Xl12':str(UTSinfoDict['Xi'][i]+UTSinfoDict['Xj'][i]),
                'Xl23':str(UTSinfoDict['Xk'][i]+UTSinfoDict['Xj'][i]),
                'Xl13':str(UTSinfoDict['Xi'][i]+UTSinfoDict['Xk'][i]),
                'Rl12':str(UTSinfoDict['Ri'][i]+UTSinfoDict['Rj'][i]),
                'Rl23':str(UTSinfoDict['Rk'][i]+UTSinfoDict['Rj'][i]),
                'Rl13':str(UTSinfoDict['Ri'][i]+UTSinfoDict['Rk'][i]),
                'pf_V':'1',
                'pf_Theta':'0'
            }
            #comment: 设置新三绕组变压器的引脚连接
            pins= {
                "0": UTSinfoDict['psNameI'][i],
                "1": UTSinfoDict['psNameJ'][i],
                "2": UTSinfoDict['psNameK'][i]
            }
            #comment: 在画布上添加新三绕组变压器元件
            ce.addCompInCanvas(compJson,AddTSID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                                pins = pins, label = label,dX = 10, MaxX = 500)
            #comment: 将新三绕组变压器添加到 AddedT3Ws 列表
            AddedT3Ws.append(label)
            #comment: 更新三绕组变压器中心节点字典
            T3WCentDict[label] = UTSinfoDict['psNameN'][i]
        #comment: 否则 (可能是双绕组变压器，即 K 侧为 'null')
        else:
            #comment: 如果 K 侧为 'null'
            if(UTSinfoDict['psNameK'][i] == 'null'):
                #comment: 计算一次侧和二次侧的电压基准 (考虑变比)
                VBaseI = UTSinfoDict['Vi_base'][i]*UTSinfoDict['ki'][i]
                VBaseJ = UTSinfoDict['Vj_base'][i]*UTSinfoDict['kj'][i]
                
                #comment: 计算变压器的等效电抗和电阻
                Xl = (UTSinfoDict['Xi'][i] + UTSinfoDict['Xj'][i])
                Rl = (UTSinfoDict['Ri'][i] + UTSinfoDict['Rj'][i])
                
                #comment: 设置引脚连接
                pin0 = UTSinfoDict['psNameI'][i]
                pin1 = UTSinfoDict['psNameJ'][i]
            #comment: 如果 J 侧为 'null' (这部分逻辑在正常的 2W/3W 判断中可能不典型，但保留原始代码逻辑)
            elif(UTSinfoDict['psNameJ'][i] == 'null'):
                #comment: 计算一次侧和三次侧的电压基准 (考虑变比)
                VBaseI = UTSinfoDict['Vi_base'][i]*UTSinfoDict['ki'][i]
                VBaseJ = UTSinfoDict['Vk_base'][i]*UTSinfoDict['kk'][i]
                
                #comment: 计算变压器的等效电抗和电阻
                Xl = UTSinfoDict['Xi'][i] + UTSinfoDict['Xk'][i]
                Rl = UTSinfoDict['Ri'][i] + UTSinfoDict['Rk'][i]

                #comment: 设置引脚连接
                pin0 = UTSinfoDict['psNameI'][i]
                pin1 = UTSinfoDict['psNameK'][i]
            #comment: 获取双绕组变压器的元件 JSON 定义
            compJson = ce.compLib['_newTransformer_3p2w']
            #comment: 设置新双绕组变压器标签
            label = UTSinfoDict['Name'][i]
            #comment: 设置新双绕组变压器的参数
            args = {
                "Name": label,
                'V1':str(VBaseI),
                'V2':str(VBaseJ),
                'Xl':str(Xl),
                'Rl':str(Rl)
            }
            #comment: 设置新双绕组变压器的引脚连接
            pins= {
                "0": pin0,
                "1": pin1
            }
            #comment: 在画布上添加新双绕组变压器元件
            ce.addCompInCanvas(compJson,AddTSID0,'AddedCanvas', addN = True, addN_label = False,args = args, 
                                pins = pins, label = label,dX = 10, MaxX = 500)
            #comment: 将新双绕组变压器添加到 AddedT2Ws 列表
            AddedT2Ws.append(label)
    #comment: 打印 AddedT3Ws 列表
    print('AddedT3Ws')
    print(AddedT3Ws)
    #comment: 打印 AddedT2Ws 列表
    print('AddedT2Ws')
    print(AddedT2Ws)
    #comment: 通过 jobmessage 记录新增双绕组变压器的数量
    jobmessage(job,"新增双绕组变压器: {0}".format(len(AddedT2Ws)),key="logs",verb='append')
    #comment: 通过 jobmessage 记录新增三绕组变压器的数量
    jobmessage(job,"新增三绕组变压器: {0}".format(len(AddedT3Ws)),key="logs",verb='append')
    #comment: 返回更新后的 T3WCentDict
    return T3WCentDict

#comment: 定义一个处理母线的函数
#comment: job: CloudPSS作业对象
#comment: qspath: QS文件路径
#comment: ce: CaseEditToolbox实例
#comment: T3WCentDict: 三绕组变压器中心节点字典
def _process_buses(job, qspath, ce, T3WCentDict):
    #comment: 构建 bus.txt 文件的完整路径
    qsfile = qspath + 'bus.txt'
    #comment: 读取 bus.txt 文件中的信息到 infoDict，指定编码和类型
    infoDict = ReadQSInfo(qsfile,encoding='utf-8',type = 'bus')
    #comment: 初始化 busqsDict，用于存储读取的母线 QS 信息
    busqsDict = {}
    #comment: 设置元件标签字典
    ce.setCompLabelDict()
    #comment: 初始化 bus_SP 字典，此处假设此变量在其他地方加载或不用于此部分
    bus_SP = {} # Assuming this is loaded elsewhere or not needed for this part
    #comment: 初始化在 PS 中不存在的母线列表
    noBusInPS = []
    #comment: 遍历 infoDict 中的每条母线数据
    for i in range(len(infoDict['psBus'])):
        #comment: 获取母线的 PS 命名
        psBus = infoDict['psBus'][i]
        #comment: 获取母线的名称
        busName = infoDict['busName'][i]
        #comment: 获取母线的 IEEE 命名
        ieeeBus = infoDict['ieeeBus'][i]
        #comment: 获取母线的基准电压
        Vbase = infoDict['Vbase'][i]
        #comment: 如果 IEEE 命名存在于 bus_SP 映射中，则更新 PS 命名
        if(ieeeBus in bus_SP.keys()):
            psBus = bus_SP[ieeeBus]
        #comment: 获取母线的电压标幺值
        v = infoDict['v'][i]
        #comment: 获取母线的相角 (弧度转换为角度)
        theta = infoDict['theta'][i] * 180/math.pi
        #comment: 如果当前母线 PS 命名不在 busqsDict 中，则初始化其条目并添加 ids 和 contains 列表
        if(psBus not in busqsDict.keys()):
            busqsDict[psBus] = {'ids':[],'contains':[]}
        #comment: 更新 busqsDict 中当前母线的信息
        busqsDict[psBus].update({'ieeeBus':ieeeBus,'busName':busName,'v':v,'theta':theta,'VB':Vbase})
        #comment: 将当前行的 id 添加到 busqsDict 中对应母线的 ids 列表
        busqsDict[psBus]['ids'].append(i)
        #comment: 如果母线不在 ce.compLabelDict 中，也不在 T3WCentDict 的值中 (说明在 PS 中不存在)
        if(psBus not in ce.compLabelDict.keys() and psBus not in T3WCentDict.values()):
            #comment: 将该母线添加到 noBusInPS 列表
            noBusInPS.append(psBus)
    #comment: 打印 noBusInPS 列表信息
    print('——————noBusInPS——————')
    print(noBusInPS)
    #comment: 初始化 busPS2QSDict，用于存储 PS 母线到 QS 母线的映射
    busPS2QSDict = {}
    #comment: 初始化在 QS 中不存在的母线列表
    noBusInQS = []

    #comment: 遍历项目中所有 _newBus_3p 类型的元件 (PS 中的母线)
    for i,comp in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
        #comment: 如果元件标签存在于 busqsDict 中 (表示在 QS 中有对应项)
        if(comp.label in busqsDict.keys()):
            #comment: 将 PS 母线的 key 映射到其标签 (这里直接映射到自身，因为 j 只是 key)
            busPS2QSDict[i] = i;
        #comment: 否则 (在 QS 中没有对应项)
        else:
            #comment: 将该母线标签添加到 noBusInQS 列表
            noBusInQS.append(comp.label)

            
    #comment: 打印 noBusInQS 列表信息
    print('——————noBusInQS——————')
    print(noBusInQS)
    #comment: 构建 3wTsf.txt 文件的完整路径 (再次读取三绕组变压器信息，可能为获取其内部连接点)
    qsfile = qspath + '3wTsf.txt'
    #comment: 读取 3wTsf.txt 文件中的信息到 infoDict
    infoDict = ReadQSInfo(qsfile,encoding='UTF-8',type = '3wT')
    #comment: 初始化 busTW3Dict，用于存储三绕组变压器的详细信息，以 PS 命名为键
    busTW3Dict = {}
    #comment: 遍历 infoDict 中的每条三绕组变压器数据
    for i in range(len(infoDict['psName'])):
        #comment: 初始化当前变压器的条目
        busTW3Dict[infoDict['psName'][i]] = {}
        #comment: 将当前变压器的所有信息存储到 busTW3Dict 中
        for j in infoDict.keys():
            busTW3Dict[infoDict['psName'][i]][j] = infoDict[j][i]
        
    #comment: 初始化 VBProbs 列表，用于记录电压基准存在问题的母线
    VBProbs = []
    #comment: 遍历 busPS2QSDict 中的每个映射对 (ps_key 到 qs_key, 实际上这里 qs_key 仍然是 ps_key)
    for i,j in busPS2QSDict.items():
        #comment: 获取 PS 中母线的当前基准电压
        V0 = float(ce.project.getComponentByKey(i).args['VBase'])
        #comment: 获取母线标签 (在 PS 和 QS 中应该一致)
        label = ce.project.getComponentByKey(busPS2QSDict[j]).label
        #comment: 获取 QS 中母线的基准电压
        V1 = busqsDict[label]['VB']
        #comment: 获取 QS 中母线的电压标幺值
        v = busqsDict[label]['v']
        #comment: 如果电压标幺值为 0，则设为 1 (避免除以 0 或标幺值为 0 带来问题)
        if(v ==0):
            v = 1

        #comment: 如果 QS 中母线的基准电压大于 0.0001 (有效值)
        if(busqsDict[label]['VB'] >0.0001):
            #comment: 更新 PS 中母线的基准电压
            ce.project.getComponentByKey(i).args['VBase'] = str(busqsDict[label]['VB'])
        #comment: 否则 (基准电压无效)
        else:
            #comment: 将该母线标签添加到 VBProbs 列表
            VBProbs.append(ce.project.getComponentByKey(i).label)
        #comment: 更新 PS 中母线的电压标幺值和相角
        ce.project.getComponentByKey(i).args['V'] = str(v)
        ce.project.getComponentByKey(i).args['Theta'] = str(busqsDict[label]['theta'])
            
    #comment: 初始化 NoT3WQS 列表
    NoT3WQS = []
    #comment: 遍历项目中所有 _newTransformer_3p3w 类型的元件 (三绕组变压器)
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p3w').items():
        #comment: 如果变压器标签存在于 T3WCentDict 中，并且其中心节点在 busqsDict 中 (表示有对应的 QS 母线信息)
        if(j.label in T3WCentDict.keys() and T3WCentDict[j.label] in busqsDict.keys()):
            #comment: 获取中心节点的电压标幺值
            v = busqsDict[T3WCentDict[j.label]]['v'] 
            #comment: 如果电压标幺值为 0，则设为 1
            if(v ==0):
                v = 1
            
            #comment: 更新三绕组变压器的 pf_V 和 pf_Theta 参数 (参与潮流计算的电压和相角)
            j.args['pf_V'] = str(v)
            j.args['pf_Theta'] = str(busqsDict[T3WCentDict[j.label]]['theta'])