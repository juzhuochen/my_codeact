import os
import pandas as pd
import time
import sys,os

#sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
import cloudpss
import igraph as ig# type: ignore
import plotly.graph_objects as go
# from itertools import combinations
# from fuzzywuzzy import process
import time
import numpy as np
import pandas as pd
from jobApi1 import fetch,fetchAllJob,abort# type: ignore
from CaseEditToolbox import CaseEditToolbox# type: ignore
from CaseEditToolbox import is_number# type: ignore
import json
import math
import copy
from CaseEditToolbox import is_number# type: ignore
import re
from ImportQSData_xinan_2 import *
from ImportQSData_xinan_3 import _process_ac_lines, _process_series_compensators, _process_transformers, _process_buses
from ImportQSData_xinan_4 import _process_generators, _process_loads, _process_shunts, _process_dc_lines, ReadQSInfo, findBusInStation
# 存在MergedG信息时注释本块

def _initialize_project(job, projectKey, qspath, ce):
    #comment: 定义一个名为 _initialize_project 的函数，用于初始化项目配置
    #comment: job: 任务对象，用于记录日志
    #comment: projectKey: 项目的唯一标识符
    #comment: qspath: QS数据文件的路径
    #comment: ce: CaseEditToolbox 实例，用于编辑案例

    """
    初始化项目配置，设置初始条件，并处理拓扑刷新。
    """
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInNjb3BlcyI6W10sInR5cGUiOiJhcHBseSIsImV4cCI6MTcxODc2MzYzMCwiaWF0IjoxNjg3NjU5NjMwfQ.1h5MVO8PATPT5ujlb1J9CAJzwqMWhzDagDk9IQ1gbNhA2TtOLRqYnlyZ0N2atQY1t_agxvYK4Nr4xX1aJYt1lA'
    #comment: 定义一个令牌字符串，可能用于身份验证或API访问
    apiURL = 'http://cloudpss-calculate.local.ddns.cloudpss.net/'
    #comment: 定义CloudPSS计算服务的API URL
    username = 'admin' #用户名
    #comment: 定义用户名

    with open('saSource.json', "r", encoding='utf-8') as f:
    #comment: 打开并读取 'saSource.json' 文件，该文件可能包含组件库信息
        compLib = json.load(f)
        #comment: 将JSON数据加载到 compLib 变量中
    ce.setConfig(tk,apiURL,username,projectKey, comLibName = 'saSource.json');
    #comment: 设置CaseEditToolbox的配置，包括令牌、API URL、用户名、项目密钥和组件库文件名
    
    jobmessage(job,'项目初始化...',key="logs",verb='append')
    #comment: 发送项目初始化消息到作业日志
    generateG = False;
    #comment: 设置是否生成iGraph信息的标志，如果已有则不生成
    ce.config['iGraph'] = generateG  #  生成iGraph信息，已有iGraph信息时注释本块
    #comment: 更新ce配置中的iGraph生成选项
    ce.setInitialConditions() # 进行初始化
    #comment: 设置项目的初始条件

    # 生成母线label-key的字典
    #comment: 初始化一个字典用于存储母线标签到键的映射
    busLabelDict = {}
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
    #comment: 遍历项目中所有RID为 'model/CloudPSS/_newBus_3p' 的组件（即母线）
        busLabelDict[j.label] = i
        #comment: 将母线的标签作为键，母线的ID作为值存入字典

    ce.config['iGraph'] = generateG  #  生成iGraph信息，已有iGraph信息时注释本块
    #comment: 再次更新ce配置中的iGraph生成选项（确保设置生效）

    generateTopoSP = False
    #comment: 设置是否生成拓扑SP的标志
    ce.createCanvas('AddedCanvas','AddedCanvas')
    #comment: 创建一个名为 'AddedCanvas' 的画布

    # 直接删除所有无功补偿
    #comment: 遍历并删除项目中所有RID为 'model/CloudPSS/_newShuntLC_3p' 的无功补偿组件
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newShuntLC_3p').items():
        ce.project.revision.implements.diagram.cells.pop(i)
        #comment: 从项目的图表修订中移除该组件
    # 直接删除所有串补
    #comment: 遍历并删除项目中所有RID为 'model/CloudPSS/newCapacitorRouter' 的串补组件
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/newCapacitorRouter').items():
        ce.project.revision.implements.diagram.cells.pop(i)
        #comment: 从项目的图表修订中移除该组件

    time.sleep(5)
    #comment: 暂停5秒，等待操作完成
    ce.refreshTopology()
    #comment: 刷新项目拓扑
    
    if(generateG):
    #comment: 如果需要生成图信息
        mergedG,mergeDict = mergeGraph(ce,ce.g)
        #comment: 调用 mergeGraph 函数合并图，并获取合并后的图和合并字典

    if(generateG):
    #comment: 如果需要生成图信息
        ce.g.save('CEG2.gml')
        #comment: 保存 ce.g 到 GML 文件
        mergedG.save('mergedG2.gml')
        #comment: 保存 mergedG 到 GML 文件
        with open("./mergeDict2.json","w",encoding='utf-8') as f:
        #comment: 打开并写入 'mergeDict2.json' 文件
            f.write(json.dumps(mergeDict, indent=4, ensure_ascii=False))
            #comment: 将 mergeDict 以JSON格式写入文件
    #comment: 定义网络形状配置，包括不同组件的颜色、形状、大小和标签大小
    ce.NetShapeConfig = {'model/CloudPSS/_newBus_3p':{'color':'cyan','shape':'circle','size':8,'label_size':10},
                    'model/CloudPSS/_newTransformer_3p2w':{'color':'darkolivegreen','shape':'triangle-up','size':8,'label_size':10},
                    'model/CloudPSS/_newTransformer_3p3w':{'color':'darkolivegreen','shape':'triangle-up','size':8,'label_size':10},
                    'model/CloudPSS/TranssmissionLineRouter':{'color':'gold','shape':'square-open','size':8,'label_size':10},
                    'model/CloudPSS/SyncGeneratorRouter':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                    'model/admin/WGSource':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                    'model/CloudPSS/PVStation':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                    'model/CloudPSS/_newACVoltageSource_3p':{'color':'plum','shape':'diamond','size':8,'label_size':10},
                    'model/admin/DCLine':{'color':'orange','shape':'square','size':10,'label_size':10}
                    }
    ce.g = ig.load('CEG2.gml')
    #comment: 从文件加载 igraph 对象 ce.g
    mergedG = ig.load('mergedG2.gml')
    #comment: 从文件加载 igraph 对象 mergedG
    with open('./mergeDict2.json', "r", encoding='utf-8') as f:
    #comment: 打开并读取 'mergeDict2.json' 文件
        mergeDict = json.load(f)
        #comment: 将JSON数据加载到 mergeDict 变量中
    containsDict = {}
    #comment: 初始化一个字典用于存储合并后的节点包含的原始节点信息
    for i,j in mergeDict.items():
    #comment: 遍历 mergeDict
        if(j not in containsDict.keys()):
        #comment: 如果合并后的节点名称 j 不在 containsDict 的键中
            containsDict[j] = []
            #comment: 则初始化一个空列表
        containsDict[j].append(i)
        #comment: 将原始节点名称 i 添加到合并后的节点 j 的列表中
    mergedG.vs['contains'] = [containsDict[i] if containsDict[i]!=[] else None for i in mergedG.vs['name']]
    #comment: 为 mergedG 的顶点属性添加 'contains'，存储合并后的节点包含的原始节点列表
    return busLabelDict, mergedG, mergeDict, generateTopoSP
    #comment: 返回母线标签字典、合并后的图、合并字典和拓扑生成SP标志

def _clean_and_set_initial_values(job, ce,qspath,T3WCentDict):
    #comment: 定义一个名为 _clean_and_set_initial_values 的函数，用于清理孤立网络并设置母线潮流初值
    #comment: job: 任务对象
    #comment: ce: CaseEditToolbox 实例
    #comment: qspath: QS数据文件的路径
    #comment: T3WCentDict: 三绕组变压器中心点字典

    """
    清理孤立网络，并为母线赋予潮流初值。
    """
    jobmessage(job,"正在清理孤立网络...",key="logs",verb='append')
    #comment: 发送清理孤立网络的消息到作业日志
    
    ce.refreshTopology()
    #comment: 刷新项目拓扑
    ce.generateNetwork()
    #comment: 生成网络

    connection = ce.g.connected_components()
    #comment: 获取图 ce.g 的连通分量
    genRIDType0 = ['model/CloudPSS/SyncGeneratorRouter', 'model/admin/WGSource', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 定义生成器组件的RID类型列表
    deletedLabels = []
    #comment: 初始化一个列表用于存储被删除组件的标签
    setPVLabels = []
    #comment: 初始化一个列表用于存储设置为PV节点的标签
    for c in connection:
    #comment: 遍历每个连通分量
        deleteflag = 1
        #comment: 初始化删除标志，1表示可能删除
        GD = {i:[] for i in genRIDType0}
        #comment: 初始化一个字典，用于存储每个生成器类型在当前连通分量中的实例
        PQflag = 1;
        #comment: 初始化PQ标志，1表示当前连通分量中所有发电机可能都是PQ类型
        maxP = -99999;
        #comment: 初始化最大有功功率
        maxPid = ''
        #comment: 初始化最大有功功率对应的组件ID
        Ps = []
        #comment: 初始化列表用于存储有功功率值
        for gt in genRIDType0:
        #comment: 遍历每种生成器类型
            rids = ce.g.vs[c]['rid']
            #comment: 获取连通分量中顶点的RID
            names = ce.g.vs[c]['name']
            #comment: 获取连通分量中顶点的名称
            if(gt in ce.g.vs[c]['rid']):
            #comment: 如果当前生成器类型存在于连通分量中
                deleteflag = 0
                #comment: 设置删除标志为0，表示不删除此连通分量
                pos = [i for i in range(len(names)) if rids[i] == gt]
                #comment: 获取所有匹配当前生成器类型的顶点的索引
                GD[gt] = GD[gt] + [names[p] for p in pos]
                #comment: 将这些发电机的名称添加到GD字典中
                Pst = [float(ce.project.getComponentByKey(names[p][1:]).args['pf_P']) for p in pos]
                #comment: 获取这些发电机的有功功率
                typet = [ce.project.getComponentByKey(names[p][1:]).args['BusType'] for p in pos]
                #comment: 获取这些发电机的母线类型
                if('1' in typet or '2' in typet):
                #comment: 如果存在母线类型为1或2（PV或PQ）
                    PQflag = 0
                    #comment: 设置PQ标志为0，表示存在非PQ母线
                maxPt = max(Pst)
                #comment: 获取当前类型发电机的最大有功功率
                if(maxP < maxPt):
                #comment: 如果找到更大的有功功率
                    maxP = maxPt
                    #comment: 更新最大有功功率
                    mp = Pst.index(maxP)
                    #comment: 获取最大有功功率的索引
                    maxPid = names[pos[mp]][1:]
                    #comment: 更新最大有功功率对应的组件ID

        if(deleteflag):
        #comment: 如果删除标志为1，表示该连通分量是孤立网络
            for i in c:
            #comment: 遍历连通分量中的每个顶点
                comp = ce.project.getComponentByKey(ce.g.vs[i]['name'][1:])
                #comment: 获取对应的项目组件
                deletedLabels.append(comp.label)
                #comment: 将组件标签添加到删除列表
                ce.project.revision.implements.diagram.cells.pop(comp.id)
                #comment: 从项目图表修订中删除组件
        else:
        #comment: 如果不删除该连通分量
            if(PQflag):
            #comment: 如果PQ标志为1（所有发电机都被认为是PQ类型）
                ce.project.getComponentByKey(maxPid).args['BusType'] = '1'
                #comment: 将该连通分量中最大有功功率的对应母线设置为PV类型
                setPVLabels.append(ce.project.getComponentByKey(maxPid).label)
                #comment: 将其标签添加到设置为PV节点的列表
    jobmessage(job,"正在赋予母线潮流初值..",key="logs",verb='append')
    #comment: 发送正在赋予母线潮流初值的消息到作业日志
    qsfile = qspath + 'bus.txt'
    #comment: 构建bus.txt文件的完整路径
    infoDict = ReadQSInfo(qsfile,encoding='utf-8',type = 'bus')
    #comment: 从bus.txt读取QS信息，类型为母线
    busqsDict = {}
    #comment: 初始化一个字典用于存储QS母线信息
    ce.setCompLabelDict()
    #comment: 设置组件标签字典（可能用于快速查找组件）
    bus_SP = {}
    #comment: 初始化一个字典，可能用于存储SP母线信息
    noBusInPS = []
    #comment: 初始化一个列表，用于存储在QS文件中有但在PS（CloudPSS）中没有的母线
    for i in range(len(infoDict['psBus'])):
    #comment: 遍历QS母线信息
        psBus = infoDict['psBus'][i]
        #comment: 获取PS母线名称
        busName = infoDict['busName'][i]
        #comment: 获取母线名称
        ieeeBus = infoDict['ieeeBus'][i]
        #comment: 获取IEEE母线号
        Vbase = infoDict['Vbase'][i]
        #comment: 获取基准电压
        if(ieeeBus in bus_SP.keys()):
        #comment: 如果IEEE母线号在 bus_SP 中
            psBus = bus_SP[ieeeBus]
            #comment: 更新 psBus
        v = infoDict['v'][i]
        #comment: 获取电压标幺值
        theta = infoDict['theta'][i] * 180/math.pi
        #comment: 获取电压相角并转换为度
        if(psBus not in busqsDict.keys()):
        #comment: 如果 psBus 不在 busqsDict 的键中
            busqsDict[psBus] = {'ids':[],'contains':[]}
            #comment: 初始化字典项
        busqsDict[psBus].update({'ieeeBus':ieeeBus,'busName':busName,'v':v,'theta':theta,'VB':Vbase})
        #comment: 更新母线的QS信息
        busqsDict[psBus]['ids'].append(i)
        #comment: 将当前索引添加到ids列表
        if(psBus not in ce.compLabelDict.keys() and psBus not in T3WCentDict.values()):
        #comment: 如果 psBus 既不在 CloudPSS 组件标签字典中，也不在三绕组变压器中心点字典的值中
            noBusInPS.append(psBus)
            #comment: 将其添加到 noBusInPS 列表
    print('——————noBusInPS——————')
    #comment: 打印分隔符
    print(noBusInPS)
    #comment: 打印 QS 有但 PS 没有的母线列表
    jobmessage(job,"QS有PS无的母线："+str(noBusInPS),key="logs",verb='append')
    #comment: 发送QS有但PS没有的母线列表到作业日志
    busPS2QSDict = {}
    #comment: 初始化一个字典，用于存储PS母线到QS母线的映射
    noBusInQS = []
    #comment: 初始化一个列表，用于存储在PS（CloudPSS）中有但在QS文件中没有的母线

    for i,comp in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
    #comment: 遍历CloudPSS项目中所有母线组件
        if(comp.label in busqsDict.keys()):
        #comment: 如果组件的标签在QS母线信息字典中
            busPS2QSDict[i] = i;
            #comment: 将组件ID映射到自身（表示存在于QS）
        else:
        #comment: 如果组件的标签不在QS母线信息字典中
            noBusInQS.append(comp.label)
            #comment: 将其标签添加到 noBusInQS 列表
            
    print('——————noBusInQS——————')
    #comment: 打印分隔符
    print(noBusInQS)
    #comment: 打印PS有但QS没有的母线列表
    jobmessage(job,"PS有QS无的母线："+str(noBusInQS),key="logs",verb='append')
    #comment: 发送PS有但QS没有的母线列表到作业日志
    qsfile = qspath + '3wTsf.txt'
    #comment: 构建3wTsf.txt文件的完整路径
    infoDict = ReadQSInfo(qsfile,encoding='UTF-8',type = '3wT')
    #comment: 从3wTsf.txt读取QS信息，类型为三绕组变压器
    busTW3Dict = {}
    #comment: 初始化一个字典，用于存储三绕组变压器QS信息
    for i in range(len(infoDict['psName'])):
    #comment: 遍历三绕组变压器QS信息
        busTW3Dict[infoDict['psName'][i]] = {}
        #comment: 以变压器名称为键初始化字典项
        for j in infoDict.keys():
        #comment: 遍历所有QS信息字段
            busTW3Dict[infoDict['psName'][i]][j] = infoDict[j][i]
            #comment: 存储对应字段的值

    with open("./noBusInPS_QS.json","w",encoding='utf-8') as f:
    #comment: 打开并写入 'noBusInPS_QS.json' 文件
        f.write(json.dumps({'noBusInPS':noBusInPS,'noBusInQS':noBusInQS}, indent=4, ensure_ascii=False))
        #comment: 将 noBusInPS 和 noBusInQS 列表以JSON格式写入文件
  
    VBProbs = []
    #comment: 初始化一个列表，可能用于存储基准电压有问题（为0或过小）的母线
    for i,j in busPS2QSDict.items():
    #comment: 遍历PS母线到QS母线映射字典
        V0 = float(ce.project.getComponentByKey(i).args['VBase'])
        #comment: 获取CloudPSS母线的原始基准电压
        label = ce.project.getComponentByKey(busPS2QSDict[j]).label
        #comment: 获取对应QS母线的标签
        V1 = busqsDict[label]['VB']
        #comment: 获取QS母线的基准电压
        v = busqsDict[label]['v']
        #comment: 获取QS母线的电压标幺值
        if(v ==0):
        #comment: 如果电压标幺值为0
            v = 1
            #comment: 将其设置为1

        if(busqsDict[label]['VB'] >0.0001):
        #comment: 如果QS母线的基准电压大于0.0001
            ce.project.getComponentByKey(i).args['VBase'] = str(busqsDict[label]['VB'])
            #comment: 更新CloudPSS母线的基准电压
        else:
        #comment: 如果基准电压过小或为0
            VBProbs.append(ce.project.getComponentByKey(i).label)
            #comment: 将其标签添加到VBProbs列表
        ce.project.getComponentByKey(i).args['V'] = str(v)
        #comment: 更新CloudPSS母线的电压标幺值
        ce.project.getComponentByKey(i).args['Theta'] = str(busqsDict[label]['theta'])
        #comment: 更新CloudPSS母线的电压相角
    NoT3WQS = []
    #comment: 初始化一个列表，可能用于存储PS中有但在QS中没有的三绕组变压器
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p3w').items():
    #comment: 遍历CloudPSS项目中所有三绕组变压器组件
        if(j.label in T3WCentDict.keys() and T3WCentDict[j.label] in busqsDict.keys()):
        #comment: 如果变压器标签存在于三绕组变压器中心点字典中，并且其中心点母线存在于QS母线信息字典中
            v = busqsDict[T3WCentDict[j.label]]['v']
            #comment: 获取对应中心点母线的电压标幺值
            if(v ==0):
            #comment: 如果电压标幺值为0
                v = 1
                #comment: 将其设置为1
            
            j.args['pf_V'] = str(v)
            #comment: 更新三绕组变压器的电压标幺值
            j.args['pf_Theta'] = str(busqsDict[T3WCentDict[j.label]]['theta'])
            #comment: 更新三绕组变压器的电压相角
        
    ce.refreshTopology()
    #comment: 刷新项目拓扑
    ce.generateNetwork()
    #comment: 生成网络

    mergedG,mergeDict = mergeGraph(ce,ce.g)
    #comment: 调用 mergeGraph 函数合并图，并获取合并后的图和合并字典

    findBusInStation(ce,mergedG,mergeDict,'comp__newBus_3p_1264')
    #comment: 调用 findBusInStation 函数查找指定母线所在站的母线

    VAngDict = {(j.args['V']+j.args['Theta']):[] for j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').values()}
    #comment: 创建一个字典，键是电压标幺值和相角的组合，值是包含相同电压和相角母线的ID列表
    for i,j in ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p').items():
    #comment: 遍历CloudPSS项目中所有母线组件
        VAngDict[j.args['V']+j.args['Theta']].append(i)
        #comment: 将母线ID添加到对应电压和相角的列表中

    judged = set()
    #comment: 初始化一个集合用于存储已判断过的母线（避免重复判断）
    for k,m in VAngDict.items():
    #comment: 遍历VAngDict，k是电压相角组合字符串，m是母线ID列表
        message = [",".join([ce.project.getComponentByKey(n).label for n in m])]
        #comment: 构建第一个消息，包含所有具有相同V和Theta的母线标签
        flag = 0
        #comment: 初始化标志位，用于判断是否打印额外信息
        for i in m:
        #comment: 遍历每个母线ID
            buses = findBusInStation(ce,mergedG,mergeDict,i)
            #comment: 找到该母线所在站的所有母线
            buses = set(buses) | set([i])
            #comment: 将当前母线也加入到集合中
            if(i in judged):
            #comment: 如果该母线已经判断过
                continue
                #comment: 跳过
            if(len(buses) < len(m) and len(m)!=1):
            #comment: 如果该母线所在站的母线数量小于具有相同V和Theta的母线数量，并且后者不为1（即存在不同站但V和Theta相同的母线）
                judged = judged | buses
                #comment: 将当前站点内的母线标记为已判断
                message.append(",".join([ce.project.getComponentByKey(n).label for n in buses]))
                #comment: 将当前站点的母线标签添加到消息中
                flag = 1
                #comment: 设置标志位为1
        if(flag==1):
        #comment: 如果标志位为1，表示存在不同站但V和Theta相同的母线组
            print(message)
            #comment: 打印这些母线组的信息

def analysis_and_save(job, ce, projectKey):
    #comment: 定义一个名为 analysis_and_save 的函数，用于运行交流分网计算并保存项目
    #comment: job: 任务对象
    #comment: ce: CaseEditToolbox 实例
    #comment: projectKey: 项目的唯一标识符

    """
    运行交流分网计算并保存项目。
    """
    jobmessage(job,"正在进行交流分网计算...",key="logs",verb='append')
    #comment: 发送正在进行交流分网计算的消息到作业日志
    jobTopo = ce.project.getModelJob('交直流电网拓扑分析方案 1')[0]
    #comment: 获取项目中名为 '交直流电网拓扑分析方案 1' 的计算方案
    ce.runner = ce.project.run(job=jobTopo)
    #comment: 运行该计算方案
    while not ce.runner.status():
    #comment: 循环等待计算完成
        time.sleep(1)
        #comment: 每秒检查一次
    jobmessage(job,"交流分网计算完成，保存算例...",key="logs",verb='append')
    #comment: 发送交流分网计算完成并保存算例的消息到作业日志
    
    ce.runner.result.modify(ce.runner.result.db.message[4],ce.project)
    #comment: 根据计算结果修改项目（具体修改内容取决于 db.message[4]）

    ce.saveProject(projectKey+'_QS',name=ce.project.name+'_Mod')
    #comment: 保存项目，新项目密钥为 projectKey_QS，名称为原项目名称加 '_Mod'
    jobmessage(job,"保存算例完成...",key="logs",verb='append')
    #comment: 发送保存算例完成的消息到作业日志

def ImportQSData_xinan(job,projectKey = 'xinan20230731-1_All',qspath = './QSFiles0810/'):
    #comment: 定义一个名为 ImportQSData_xinan 的主函数，用于导入西南地区QS数据
    #comment: job: 任务对象
    #comment: projectKey: 项目的唯一标识符，默认为 'xinan20230731-1_All'
    #comment: qspath: QS数据文件的路径，默认为 './QSFiles0810/'
    ce = CaseEditToolbox()
    #comment: 创建 CaseEditToolbox 的实例
    linebus_SP = {}
    #comment: 初始化一个字典用于存储线路母线SP信息
    with open('./AllSP.json', "r", encoding='utf-8') as f:
    #comment: 打开并读取 'AllSP.json' 文件
        linebus_SP = json.load(f)
        #comment: 将JSON数据加载到 linebus_SP 变量中
    T3WCentDict = {}
    #comment: 初始化一个字典用于存储三绕组变压器中心点信息
    genRIDType = ['model/CloudPSS/SyncGeneratorRouter', 'model/admin/WGSource', 'model/CloudPSS/PVStation', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 定义所有生成器组件的RID类型列表
    genRIDType0 = ['SyncGeneratorRouter', 'WGSource', 'PVStation', '_newACVoltageSource_3p']
    #comment: 定义精简的生成器组件RID类型列表
    loadRIDType = ['model/CloudPSS/SyntheticLoad', 'model/CloudPSS/_newExpLoad_3p', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 定义负荷组件的RID类型列表
    DCRIDType = ['model/admin/DCLine', 'model/CloudPSS/_newExpLoad_3p', 'model/CloudPSS/_newACVoltageSource_3p']
    #comment: 定义直流线路组件的RID类型列表

    #comment: 调用 _initialize_project 函数初始化项目
    busLabelDict, mergedG, mergeDict, generateTopoSP = _initialize_project(job, projectKey, qspath, ce)
    #comment: 调用 _process_ac_lines 函数处理交流线路数据
    busList, VbaseDict, logJson,ieeebusi,ieeebusj = _process_ac_lines(job, qspath, ce, busLabelDict, linebus_SP)
    #comment: 调用 _process_series_compensators 函数处理串补数据
    _process_series_compensators(job, qspath, ce, busList, VbaseDict,)
    #comment: 调用 _process_transformers 函数处理变压器数据
    _process_transformers(job, qspath, ce, busLabelDict, linebus_SP, T3WCentDict,ieeebusi,ieeebusj)
    #comment: 调用 _process_buses 函数处理母线数据
    _process_buses(job, qspath, ce, T3WCentDict)
    #comment: 调用 _process_generators 函数处理发电机数据
    logJson = _process_generators(job, qspath, ce, busLabelDict, genRIDType, genRIDType0, generateTopoSP, logJson)
    #comment: 调用 _process_loads 函数处理负荷数据
    logJson = _process_loads(job, qspath, ce, busLabelDict, loadRIDType, generateTopoSP, logJson)
    #comment: 调用 _process_shunts 函数处理并联补偿器数据
    logJson = _process_shunts(job, qspath, ce, busLabelDict, generateTopoSP, logJson)
    #comment: 调用 _process_dc_lines 函数处理直流线路数据
    logJson = _process_dc_lines(job, qspath, ce, busLabelDict, DCRIDType, logJson)
    #comment: 调用 _clean_and_set_initial_values 函数清理孤立网络并设置初始值
    _clean_and_set_initial_values(job, ce,qspath,T3WCentDict)
    #comment: 调用 analysis_and_save 函数进行分析并保存项目
    analysis_and_save(job, ce, projectKey)