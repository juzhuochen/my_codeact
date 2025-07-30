#comment: 导入 os 模块，用于操作系统相关功能
import os
#comment: 导入 pandas 库，用于数据处理和分析
import pandas as pd
#comment: 导入 time 模块，用于时间相关功能
import time
#comment: 导入 sys 模块，用于系统相关功能，如路径添加
import sys,os

#sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
#comment: 导入 cloudpss 库，用于与 CloudPSS 平台交互
import cloudpss
#comment: 导入 igraph 库，用于图结构处理，并对其类型进行忽略，避免类型检查报错
import igraph as ig# type: ignore
#comment: 导入 plotly.graph_objects 模块，用于创建交互式图表
import plotly.graph_objects as go
# from itertools import combinations
#comment: 导入 fuzzywuzzy 库的 process 模块，用于模糊字符串匹配
from fuzzywuzzy import process# type: ignore
#comment: 导入 time 模块，用于时间相关功能 (重复导入，可优化)
import time
#comment: 导入 numpy 库，用于数值计算
import numpy as np
#comment: 导入 pandas 库，用于数据处理和分析 (重复导入，可优化)
import pandas as pd
#comment: 从 jobApi1 模块导入 fetch, fetchAllJob, abort 函数，用于作业管理，并对其类型进行忽略
from jobApi1 import fetch,fetchAllJob,abort# type: ignore
#comment: 从 CaseEditToolbox 模块导入 CaseEditToolbox 类，用于仿真案例编辑工具箱，并对其类型进行忽略
from CaseEditToolbox import CaseEditToolbox# type: ignore
#comment: 从 CaseEditToolbox 模块导入 is_number 函数，用于判断是否为数字，并对其类型进行忽略
from CaseEditToolbox import is_number# type: ignore
#comment: 导入 json 模块，用于 JSON 数据处理
import json
#comment: 导入 math 模块，用于数学运算
import math
#comment: 导入 copy 模块，用于对象拷贝
import copy
#comment: 从 CaseEditToolbox 模块导入 is_number 函数 (重复导入，可优化)
from CaseEditToolbox import is_number# type: ignore
#comment: 导入 re 模块，用于正则表达式操作
import re



# 存在MergedG信息时注释本块
#comment: 定义 merge 函数，用于合并图中的节点
def merge(G, nList):
    #comment: 初始化一个空集合 nbs，用于存储所有待合并节点的邻居
    nbs = set()
    #comment: 初始化一个空列表 contains，用于存储待合并节点的包含信息
    contains = []
    #comment: 初始化一个空字典 md，用于存储合并后的节点映射关系
    md = {}
    #comment: 遍历 nList 中的每个节点 n
    for n in nList:
        #comment: 将当前节点 n 的所有邻居（包括前驱和后继）添加到 nbs 集合中
        nbs = nbs.union(set(n.neighbors()))
        #comment: 检查节点 n 是否有 'contains' 属性，并且该属性不为 None
        if('contains' not in n.attribute_names() or n['contains']==None):
            #comment: 如果没有 'contains' 属性或为 None，则将节点的名称添加到 contains 列表中
            contains.append(n['name'])
        else:
            #comment: 如果有 'contains' 属性且不为 None，则将其值（通常是一个列表）与当前的 contains 列表合并
            contains = contains + n['contains']
    #comment: 更新 md 字典，将 contains 列表中的每个元素映射到 nList 中第一个节点的名称
    md.update({c:nList[0]['name'] for c in contains})
        
    #comment: 获取 nList 中第一个节点的属性
    attr = nList[0].attributes()
    #comment: 移除属性中的 'name' 键
    attr.pop('name')
    #comment: 将合并后的 contains 列表添加到属性中
    attr['contains'] = contains
    #comment: 获取 nList 中第一个节点的名称作为新节点的名称
    name = nList[0]['name']
    #comment: 在图 G 中添加一个新的顶点，并指定其名称
    gn = G.add_vertex(name)
    #comment: 更新新顶点的属性
    gn.update_attributes(attr)
    # print(gn)
    #comment: 遍历 nbs 集合中的每个邻居节点 i
    for i in nbs:
        #comment: 在邻居节点 i 和新合并的节点 gn 之间添加一条边
        G.add_edge(i.index,gn.index)
    #comment: 删除 nList 中所有原来的节点
    G.delete_vertices([n.index for n in nList])
    #comment: 返回合并字典 md
    return md
#comment: 定义 mergeGraph 函数，根据特定规则合并图中的节点
def mergeGraph(ce, g):
    #comment: 复制原始图 g 得到 mergedG，用于后续操作
    mergedG = g.copy()
    #comment: 初始化 mergeDict，将图中所有节点的名称映射回自身，作为初始合并字典
    mergeDict = {i:i for i in g.vs['name']}
    #comment: 遍历原始图 g 中的每个顶点 i
    for i in list(g.vs):
        #comment: 初始化空列表 nList，用于存放待合并的节点
        nList = []
        #comment: 初始化 flag 为 0
        flag = 0

        #comment: 检查当前节点 i 的 'rid' 是否为 'model/CloudPSS/TranssmissionLineRouter'
        if(i['rid']=='model/CloudPSS/TranssmissionLineRouter'):
            #comment: 获取节点 i 对应的组件的参数
            args = ce.project.getComponentByKey(i['name'][1:]).args
            # if(float(args['X1pu'])*float(args['B1pu'])==0 and float(args['X1pu'])<=1e-4):
            #comment: 检查传输线组件的 X1pu * Length 是否小于等于 1e-4，表示其阻抗极小
            if(float(args['X1pu'])*float(args['Length'])<=1e-4):
                #comment: 如果满足条件，设置 flag 为 1
                flag = 1
        #comment: 如果 flag 为 1 (表示是低阻抗传输线)
        if(flag==1):
            #comment: 遍历当前节点 i 的所有邻居节点 j
            for j in i.neighbors():
                #comment: 检查邻居节点 j 的 'rid' 是否为 'model/CloudPSS/_newBus_3p' (即母线)
                if(j['rid']=='model/CloudPSS/_newBus_3p'):
                    #comment: 将邻居节点（在 mergedG 中根据 mergeDict 找到对应的节点）添加到 nList
                    nList.append(mergedG.vs.find(mergeDict[j['name']]))
                    # print([n['name'] for n in nList])
            #comment: 将当前节点 i（在 mergedG 中根据 mergeDict 找到对应的节点）添加到 nList
            nList.append(mergedG.vs.find(mergeDict[i['name']]))
            #comment: 调用 merge 函数合并 nList 中的节点，并获取更新的合并字典
            upd = merge(mergedG,nList)
            #comment: 更新总的 mergeDict
            mergeDict.update(upd)
    #comment: 返回合并后的图 mergedG 和合并字典 mergeDict
    return mergedG,mergeDict



#comment: 定义 ReadQSInfo 函数，用于读取 QS 文件信息
def ReadQSInfo(qsfile, type = None, encoding = "gb2312"):
    #comment: 初始化一个空字典 infoDict，用于存储读取到的信息
    infoDict = {}
    #comment: 以指定编码和只读模式打开 QS 文件
    with open(qsfile,"r",encoding=encoding) as f:        
        #comment: 如果 type 为 'line'，则定义输电线路信息的键
        if(type == 'line'):
            keys = ['id','psline','note','ison','busi','busj','ieeeName','busi1','busj1','declaration','ieeebusi','ieeebusj','r','x','b','Vbase']
            #comment: 为每个键在 infoDict 中创建一个空列表
            for k in keys:
                infoDict[k] = []
            #comment: 读取文件的第一行 (通常是标题行)
            line = f.readline();
        #comment: 如果 type 为 '2wT' (两绕组变压器)，则定义其信息的键
        elif(type == '2wT'):
            keys = ['id','psName','ison','busi','busj','ieeeName','busi1','busj1','declaration',
                    'ieeebusi','ieeebusj','I_off','J_off','ki','kj','Vbasei','Vbasej','Vbasek',
                    'ri','xi','rj','xj','rk','xk']
            #comment: 为每个键在 infoDict 中创建一个空列表
            for k in keys:
                infoDict[k] = []
            #comment: 读取文件的第一行
            line = f.readline();
        #comment: 如果 type 为 '3wT' (三绕组变压器)，则定义其信息的键
        elif(type == '3wT'):
            keys = ['id','psName','ison','busi','busj','busk','ieeeName','busi1','busj1','busk1',
                    'declaration','ieeebusi','ieeebusj','ieeebusk','I_off','J_off','K_off','ki',
                    'kj','kk','Vbasei','Vbasej','Vbasek','Ri','Xi','Rj','Xj','Rk','Xk']
            #comment: 为每个键在 infoDict 中创建一个空列表
            for k in keys:
                infoDict[k] = []
        #comment: 如果 type 为 'bus'，则定义母线信息的键
        elif(type == 'bus'):
            keys = ['psBus','ieeeBus','busName','v','theta','busbar','cid','QScid','nPS','nActive','Vbase']
            #comment: 为每个键在 infoDict 中创建一个空列表
            for k in keys:
                infoDict[k] = []
            #comment: 读取文件的第一行
            line = f.readline();
        #comment: 如果 type 为其他或未指定
        else:
            #comment: 读取文件的第一行
            line = f.readline();
            #comment: 初始化空列表 keys
            keys = []
            # print(line)
            #comment: 遍历第一行按制表符分割后的每个单元格，作为信息的键
            for data1 in line.strip('\n').split('\t'):
                #comment: 为每个键在 infoDict 中创建一个空列表
                infoDict[data1.strip(' ')] = []
                #comment: 将键添加到 keys 列表中
                keys.append(data1.strip(' '))
        #comment: 打印所有解析出的键
        print(keys)
        #comment: 遍历文件中的每一行（实际数据行）
        for line in f.readlines():     
            # print(line)
            #comment: 去除行尾换行符并按制表符分割，得到单元格列表
            lineCell = line.strip('\n').split('\t')
            #comment: 遍历每个单元格，去除首尾空格
            for cell1 in range(len(lineCell)):
                lineCell[cell1] = lineCell[cell1].strip(' ')
            #comment: 如果单元格数量多于键的数量且 type 为 'load'，则跳过当前行 (这部分逻辑可能存在问题，因为前面判断了 load 的情况，这里又跳过)
            if(len(lineCell)>len(keys) and type=='load'):
                #comment: 继续下一行
                continue
                # ysb = [0,1,2,4,5]
                # for d in range(len(keys)-1):
                #     data1 = lineCell[d]
                #     if(is_number(data1)):
                #         data1 = float(data1)
                #     infoDict[keys[ysb[d]]][-1]=data1
            #comment: 如果 type 为 'line' (输电线路)
            elif(type=='line'):
                #comment: 如果单元格数量少于键的数量
                if(len(lineCell)<len(keys)):
                    #comment: 遍历前 len(keys)-4 个单元格
                    for d in range(len(keys)-4):
                        data1 = lineCell[d]
                        #comment: 如果数据是数字，则转换为浮点数
                        if(is_number(data1)):
                            data1 = float(data1)
                        #comment: 将数据添加到 infoDict 对应键的列表中
                        infoDict[keys[d]].append(data1)
                    #comment: 为最后四个键添加默认值 0
                    infoDict[keys[-4]].append(0)
                    infoDict[keys[-3]].append(0)
                    infoDict[keys[-2]].append(0)
                    infoDict[keys[-1]].append(0)
                #comment: 如果单元格数量足够
                else:
                    # print((lineCell[-2],lineCell[-4],is_number(lineCell[-2]),is_number(lineCell[-4])))
                    #comment: 遍历所有键对应的单元格
                    for d in range(len(keys)):
                        
                        #comment: 如果当前行单元格数量少于键的数量，打印该行 (用于调试)
                        if len(lineCell)<len(keys):
                            print(lineCell)
                        data1 = lineCell[d]
                        #comment: 如果数据是数字，则转换为浮点数
                        if(is_number(data1)):
                            data1 = float(data1)
                        #comment: 如果数据为空字符串，则设置为 0
                        elif(data1 == ''):
                            data1 = 0
                        #comment: 将数据添加到 infoDict 对应键的列表中
                        infoDict[keys[d]].append(data1) 
                #comment: 如果倒数第二个单元格为空字符串
                if (lineCell[-2] == ''):
                    #comment: 将最后四个键的最后一个值设置为 0
                    infoDict[keys[-4]][-1] = 0
                    infoDict[keys[-3]][-1] = 0
                    infoDict[keys[-2]][-1] = 0
                    infoDict[keys[-1]][-1] = 0
                else:
                    #comment: 将倒数第二个键的最后一个值乘以 2 (可能表示 B1pu)
                    infoDict[keys[-2]][-1] = 2*infoDict[keys[-2]][-1]
            #comment: 对于其他类型的文件 (bus, 2wT, 3wT 等，非 load 和 line 的情况)
            else:
                #comment: 遍历所有键对应的单元格
                for d in range(len(keys)):
                    #comment: 如果当前行单元格数量少于键的数量，打印该行 (用于调试)
                    if len(lineCell)<len(keys):
                        print(lineCell)
                    data1 = lineCell[d]
                    #comment: 如果数据是数字，则转换为浮点数
                    if(is_number(data1)):
                        data1 = float(data1)
                    #comment: 将数据添加到 infoDict 对应键的列表中
                    infoDict[keys[d]].append(data1) 
    #comment: 返回存储了文件信息的字典
    return infoDict


#comment: 定义 findBusInStation 函数，用于查找同一场站内具有相同电压等级的母线
def findBusInStation(ce, mergedG,mergeDict,busid):
    # 找到同场站内的同电压等级母线，可将其视为同母线进行处理。
    #comment: 初始化空列表 buses，用于存储找到的母线 ID
    buses = []
    #comment: 获取 CE 对象中图的所有节点名称
    ceNames = ce.g.vs['name']
    #comment: 获取 CE 项目中所有组件的键
    allkeys = ce.project.getAllComponents().keys()
    #comment: 检查合并图中 busid 对应节点的 'contains' 属性是否为 None，如果是则直接返回空列表
    if(mergedG.vs.find(mergeDict['/'+busid])['contains'] == None):
        return buses
    #comment: 遍历合并图中 busid 对应节点的 'contains' 属性中的每个元素 i
    for i in mergedG.vs.find(mergeDict['/'+busid])['contains']:
        #comment: 如果元素 i 不在 ceNames 中，则跳过
        if(i not in ceNames):
            continue
        #comment: 如果元素 i 对应的节点的 'rid' 不是 'model/CloudPSS/_newBus_3p' (即不是母线)，则跳过
        if(ce.g.vs.find(i)['rid']!='model/CloudPSS/_newBus_3p'):
            continue
        #comment: 如果元素 i 的键（去掉前缀 '/'）不在所有组件键中，则跳过
        if(i[1:] not in allkeys):
            continue
        #comment: 获取当前元素 i 对应的组件对象
        comp = ce.project.getComponentByKey(i[1:])
        #comment: 检查当前组件的 VBase 是否与 busid 对应组件的 VBase 相同
        if(comp.args['VBase'] == ce.project.getComponentByKey(busid).args['VBase']):
            #comment: 如果相同，则将组件的键添加到 buses 列表中
            buses.append(i[1:])
    #comment: 返回找到的同场站同电压等级的母线列表
    return buses


#comment: 定义 getNetworkNeighbor_E 函数，用于获取网络中节点的邻居子图
def getNetworkNeighbor_E(ce,vid,nn,chooseRIDList = [],exceptRIDList = [],network = None):
    #comment: 如果未指定 network，则使用 ce.g (主图)
    if(network == None):
        network = ce.g
    #comment: 初始化 flag 为 1 (未被使用)
    flag = 1
    #comment: 找到图中与 vid 对应的顶点 a
    a = network.vs.find(vid) 
    #comment: 初始化集合 b，只包含顶点 a
    b = set([a])
    #comment: 循环 nn 次，进行广度优先搜索以获取多层邻居
    for k in range(nn):
        #comment: 复制集合 b 到 b0
        b0 = b.copy()
        #comment: 遍历 b 中的每个节点 ii
        for ii in b:
            #comment: 获取节点 ii 的所有邻居
            c = set(ii.neighbors())
            #comment: 将邻居集合 c 合并到 b0 中
            b0 = b0.union(c)
        #comment: 更新 b 为 b0
        b = b0
        #comment: 再次复制 b 到 b0
        b0 = b.copy()
        #comment: 遍历 b 中的每个节点 ii
        for ii in b:
            #comment: 如果节点 ii 的 'rid' 在 exceptRIDList (排除列表) 中
            if(ii['rid'] in exceptRIDList):
                #comment: 将该节点从 b0 中移除
                b0.remove(ii)
        #comment: 更新 b 为 b0 (排除指定 RID 的节点)
        b = b0
    #comment: 如果 chooseRIDList (选择列表) 不为空
    if(chooseRIDList!=[]):
        #comment: 过滤 b，只保留 'rid' 在 chooseRIDList 中的节点
        b = set(i for i in b if i['rid'] in chooseRIDList)
    #comment: 从原始 network 中创建包含集合 b 中节点的子图
    sg = network.subgraph(b)

    #comment: 遍历 ce.NetShapeConfig 中的配置，用于设置子图中节点的样式
    for ii in ce.NetShapeConfig.keys():
        jj = ce.NetShapeConfig[ii]
        #comment: 选取子图中 'rid' 匹配 ii 的所有顶点
        bb = sg.vs.select(rid = ii);
        #comment: 设置这些顶点的颜色、形状、大小、字体和标签大小
        bb['color'] = jj['color']
        bb['shape'] = jj['shape']
        bb['size'] = jj['size']
        bb['font'] = 'SimHei'
        bb['label_size'] = jj['label_size']
    #comment: 返回配置好样式的子图
    return sg

#comment: 定义 find_nearest 函数，用于在数组中找到与给定值最接近的元素的索引
def find_nearest(array, value):
    #comment: 将输入数组转换为 numpy 数组
    array = np.asarray(array)
    #comment: 计算数组中每个元素与给定值的绝对差，并找到最小差值的索引
    idx = (np.abs(array - value)).argmin()
    #comment: 返回最接近元素的索引
    return idx

# 抓取同场站内所有res之和
#comment: 定义 getSameStationBuses 函数，用于获取同一场站内所有通过 P=0, Q=0 线路连接的母线
def getSameStationBuses(BusResDict,BranchResDict,busSet,name):
    #comment: 将当前母线名称添加到 busSet 中
    busSet.add(name)
    #comment: 如果当前母线名称不在 BranchResDict (支路结果字典) 的键中，说明没有与其相连的支路，直接返回 busSet
    if(name not in BranchResDict.keys()):
        return busSet
    #comment: 遍历 BranchResDict 中当前母线名对应的所有支路信息
    for j in BranchResDict[name]:
        #comment: 如果支路的有功功率流 P 和无功功率流 Q 都为 0 (表示低阻抗或短路线)
        if(j['P']==0 and j['Q']==0):
            #comment: 如果支路另一端的母线名称已经在 busSet 中，则跳过 (避免重复访问和死循环)
            if(j['Opp'] in busSet):
                continue
            else:
                #comment: 如果不在，则添加到 busSet 中
                busSet.add(j['Opp'])
                #comment: 递归调用 getSameStationBuses 函数，继续查找与新母线相连的同场站母线
                busSet = getSameStationBuses(BusResDict,BranchResDict,busSet,j['Opp'])
    #comment: 返回包含所有同场站母线的集合
    return busSet


#comment: 定义 jobmessage 函数，用于向作业发送日志消息
def jobmessage(job, content, level='info', html=False, key=None,verb='append'):
    '''
        发送日志消息

        :param content 日志内容

        :param level 日志级别，可选值为 `'critical'`、`'error'`、`'warning'`、`'info'`、`'verbose'`、`'debug'`

        :param html 是否为 HTML 格式

        :param key 消息 key，用于在多个消息中引用同一消息实体，以便进行更新，或将指定 key 的消息放入容器

    '''
    #comment: 通过 job 对象的 print 方法发送消息
    job.print({
        #comment: 消息的 key
        "key": key,
        #comment: 协议版本
        "version": 1,
        #comment: 操作动词，'append' 表示追加
        "verb": verb,
        #comment: 消息类型，这里是 'log'
        "type": "log",
        #comment: 消息的数据内容
        "data": {
            #comment: 日志级别
            "level": level,
            #comment: 日志内容，转换为字符串并添加换行符
            'content': str(content)+'\n',
            #comment: 是否为 HTML 格式
            "html": html
        }
    })