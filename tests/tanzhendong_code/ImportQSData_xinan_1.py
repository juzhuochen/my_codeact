# %%
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
from jobApi1 import fetch,fetchAllJob,abort # type: ignore
from CaseEditToolbox import CaseEditToolbox# type: ignore
from CaseEditToolbox import is_number# type: ignore
import json
import math
import copy
from CaseEditToolbox import is_number# type: ignore
import re


#comment: 定义函数getSameStationBuses，用于抓取同场站内所有res之和
def getSameStationBuses(BusResDict,BranchResDict,busSet,name):
    #comment: 将当前母线名称添加到母线集合中
    busSet.add(name)
    #comment: 如果当前母线名称不在支路结果字典的键中，则直接返回母线集合
    if(name not in BranchResDict.keys()):
        return busSet
    #comment: 遍历与当前母线相连的支路
    for j in BranchResDict[name]:
        #comment: 如果支路的有功和无功为零（表示该支路可能是连接同场站内母线的），且对侧母线不在母线集合中
        if(j['P']==0 and j['Q']==0):
            if(j['Opp'] in busSet):
                #comment: 如果对侧母线已在集合中，则跳过
                continue
            else:
                #comment: 将对侧母线添加到母线集合中
                busSet.add(j['Opp'])
                #comment: 递归调用getSameStationBuses函数，继续查找同场站内的其他母线
                busSet = getSameStationBuses(BusResDict,BranchResDict,busSet,j['Opp'])
    #comment: 返回包含同场站内所有母线的集合
    return busSet


#comment: 定义潮流计算函数PFCalculate
def PFCalculate(job,projectKey = 'xinan20230731-1_All_QS',qspath = './QSFiles0810'):
    #comment: 定义API Token
    tk = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsInNjb3BlcyI6W10sInR5cGUiOiJhcHBseSIsImV4cCI6MTcxODc2MzYzMCwiaWF0IjoxNjg3NjU5NjMwfQ.1h5MVO8PATPT5ujlb1J9CAJzwqMWhzDagDk9IQ1gbNhA2TtOLRqYnlyZ0N2atQY1t_agxvYK4Nr4x1aJYt1lA'
    #comment: 定义API URL
    apiURL = 'http://cloudpss-calculate.local.ddns.cloudpss.net/'
    #comment: 定义用户名
    username = 'admin' #用户名
    # projectKey = 'xinan20230626-YY' #被分析的算例号
    # projectKey = 'xinan20230629_All'
    # projectKey = 'xinan20230705-3_All'
    # projectKey = 'xinan20230731-1_All'
    # projectKey = 'DCLine' #被分析的算例号
    #comment: 打开并加载saSource.json文件中的组件库
    with open('saSource.json', "r", encoding='utf-8') as f:
        compLib = json.load(f)
    #comment: 实例化CaseEditToolbox
    ce = CaseEditToolbox()
    #comment: 配置CaseEditToolbox的参数，包括token, API URL, 用户名, 项目key和组件库名称
    ce.setConfig(tk,apiURL,username,projectKey, comLibName = 'saSource.json');
    
    #comment: 定义是否生成iGraph信息
    generateG = False;
    #comment: 设置ce.config中的iGraph参数
    ce.config['iGraph'] = generateG  #  生成iGraph信息，已有iGraph信息时注释本块
    #comment: 进行初始化设置
    ce.setInitialConditions() # 进行初始化

    # %%
    #comment: 发送消息到作业日志，指示正在计算潮流不平衡量
    jobmessage(job,"计算潮流不平衡量...",key="logs",verb='append')
    #comment: 获取名为'潮流计算方案 1'的模型作业
    jobPF = ce.project.getModelJob('潮流计算方案 1')[0]
    #comment: 设置潮流计算方法为'power_imbalance'
    jobPF['args']['Method'] = 'power_imbalance' # power_imbalance, power_flow
    #comment: 运行潮流计算作业
    ce.runner = ce.project.run(job=jobPF)
    #comment: 循环等待作业完成
    while not ce.runner.status():
        time.sleep(1)
    #comment: 初始化Branches列表
    Branches = []
    #comment: 获取支路数据
    data = ce.runner.result.getBranches()[0]['data']['columns']
    #comment: 遍历支路数据并提取相关信息
    for i in range(len(data[0]['data'])):
        #comment: 获取支路名称
        BranchName = ce.project.getComponentByKey(data[0]['data'][i]).label
        #comment: 获取支路起始母线名称
        busiName = ce.project.getComponentByKey(data[1]['data'][i]).label
        #comment: 获取支路有功功率Pij
        Pij = data[2]['data'][i]
        #comment: 获取支路无功功率Qij
        Qij = data[3]['data'][i]
        #comment: 获取支路终止母线名称
        busjName = ce.project.getComponentByKey(data[4]['data'][i]).label
        #comment: 获取支路反向有功功率Pji
        Pji = data[5]['data'][i]
        #comment: 获取支路反向无功功率Qji
        Qji = data[6]['data'][i]
        #comment: 获取支路有功损耗
        Ploss = data[7]['data'][i]
        #comment: 获取支路无功损耗
        Qloss = data[8]['data'][i]
        #comment: 将支路信息格式化并添加到Branches列表
        Branches.append("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(BranchName,busiName,Pij,Qij,busjName,Pji,Qji,Ploss,Qloss))
    #comment: 将Branches列表的内容写入到Branches.csv文件
    with open(qspath + "Branches.csv","w",encoding='utf-8') as f:
        f.writelines(Branches)

    #comment: 初始化Buses列表
    Buses = []
    #comment: 获取母线数据
    datab = ce.runner.result.getBuses()[0]['data']['columns']
    #comment: 遍历母线数据并提取相关信息
    for i in range(len(datab[0]['data'])):
        #comment: 获取母线名称
        BusName = ce.project.getComponentByKey(datab[0]['data'][i]).label
        #comment: 初始化节点名称
        NodeName = ''
        #comment: 如果存在节点数据，则获取节点名称
        if(datab[1]['data'][i] != ''):
            NodeName = ce.project.getComponentByKey(datab[1]['data'][i]).label
        #comment: 获取母线电压幅值Vm
        Vm = datab[2]['data'][i]
        #comment: 获取母线电压相角Va
        Va = datab[3]['data'][i]
        #comment: 获取母线发电有功功率Pgen
        Pgen = datab[4]['data'][i]
        #comment: 获取母线发电无功功率Qgen
        Qgen = datab[5]['data'][i]
        #comment: 获取母线负荷有功功率Pload
        Pload = datab[6]['data'][i]
        #comment: 获取母线负荷无功功率Qload
        Qload = datab[7]['data'][i]
        #comment: 获取母线并联有功功率Pshunt
        Pshunt = datab[8]['data'][i]
        #comment: 获取母线并联无功功率Qshunt
        Qshunt = datab[9]['data'][i]
        #comment: 获取母线有功不平衡量Pres
        Pres = datab[10]['data'][i]
        #comment: 获取母线无功不平衡量Qres
        Qres = datab[11]['data'][i]
        #comment: 将母线信息格式化并添加到Buses列表
        Buses.append("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(BusName,NodeName,Vm,Va,Pgen,Qgen,Pload,Qload,Pshunt,Qshunt,Pres,Qres))
    #comment: 将Buses列表的内容写入到Buses.csv文件
    with open(qspath + "Buses.csv","w",encoding='utf-8') as f:
        f.writelines(Buses)
    # job.print(ce.runner.result.db.message)
    #comment: 遍历runner结果中的消息，并打印到作业日志
    for i in ce.runner.result.db.message:
        #comment: 如果消息类型为'terminate'，则退出循环
        if(i['type'] == 'terminate'):
            break
        job.print(i)

    # %%
    #comment: 发送消息到作业日志，指示正在进行潮流计算
    jobmessage(job,"潮流计算...",key="logs",verb='append')
    #comment: 获取名为'潮流计算方案 1'的模型作业
    jobPF = ce.project.getModelJob('潮流计算方案 1')[0]
    #comment: 设置潮流计算方法为'power_flow'
    jobPF['args']['Method'] = 'power_flow' # power_imbalance, power_flow
    #comment: 运行潮流计算作业
    ce.runner = ce.project.run(job=jobPF)
    #comment: 循环等待作业完成
    while not ce.runner.status():
        time.sleep(1)
    #comment: 初始化Branches列表
    Branches = []
    #comment: 获取支路数据
    data = ce.runner.result.getBranches()[0]['data']['columns']
    #comment: 遍历支路数据并提取相关信息
    for i in range(len(data[0]['data'])):
        #comment: 获取支路名称
        BranchName = ce.project.getComponentByKey(data[0]['data'][i]).label
        #comment: 获取支路起始母线名称
        busiName = ce.project.getComponentByKey(data[1]['data'][i]).label
        #comment: 获取支路有功功率Pij
        Pij = data[2]['data'][i]
        #comment: 获取支路无功功率Qij
        Qij = data[3]['data'][i]
        #comment: 获取支路终止母线名称
        busjName = ce.project.getComponentByKey(data[4]['data'][i]).label
        #comment: 获取支路反向有功功率Pji
        Pji = data[5]['data'][i]
        #comment: 获取支路反向无功功率Qji
        Qji = data[6]['data'][i]
        #comment: 获取支路有功损耗
        Ploss = data[7]['data'][i]
        #comment: 获取支路无功损耗
        Qloss = data[8]['data'][i]
        #comment: 将支路信息格式化并添加到Branches列表
        Branches.append("{0},{1},{2},{3},{4},{5},{6},{7},{8}\n".format(BranchName,busiName,Pij,Qij,busjName,Pji,Qji,Ploss,Qloss))
    #comment: 将Branches列表的内容写入到Branches_solved.csv文件
    with open(qspath + "Branches_solved.csv","w",encoding='utf-8') as f:
        f.writelines(Branches)

    #comment: 初始化Buses列表
    Buses = []
    #comment: 获取母线数据
    datab = ce.runner.result.getBuses()[0]['data']['columns']
    #comment: 遍历母线数据并提取相关信息
    for i in range(len(datab[0]['data'])):
        #comment: 获取母线名称
        BusName = ce.project.getComponentByKey(datab[0]['data'][i]).label
        #comment: 初始化节点名称
        NodeName = ''
        #comment: 如果存在节点数据，则获取节点名称
        if(datab[1]['data'][i] != ''):
            NodeName = ce.project.getComponentByKey(datab[1]['data'][i]).label
        #comment: 获取母线电压幅值Vm
        Vm = datab[2]['data'][i]
        #comment: 获取母线电压相角Va
        Va = datab[3]['data'][i]
        #comment: 获取母线发电有功功率Pgen
        Pgen = datab[4]['data'][i]
        #comment: 获取母线发电无功功率Qgen
        Qgen = datab[5]['data'][i]
        #comment: 获取母线负荷有功功率Pload
        Pload = datab[6]['data'][i]
        #comment: 获取母线负荷无功功率Qload
        Qload = datab[7]['data'][i]
        #comment: 获取母线并联有功功率Pshunt
        Pshunt = datab[8]['data'][i]
        #comment: 获取母线并联无功功率Qshunt
        Qshunt = datab[9]['data'][i]
        #comment: 获取母线有功不平衡量Pres
        Pres = datab[10]['data'][i]
        #comment: 获取母线无功不平衡量Qres
        Qres = datab[11]['data'][i]
        #comment: 将母线信息格式化并添加到Buses列表
        Buses.append("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(BusName,NodeName,Vm,Va,Pgen,Qgen,Pload,Qload,Pshunt,Qshunt,Pres,Qres))
    #comment: 将Buses列表的内容写入到Buses_solved.csv文件
    with open(qspath + "Buses_solved.csv","w",encoding='utf-8') as f:
        f.writelines(Buses)
    #comment: 遍历runner结果中的消息，并打印到作业日志
    for i in ce.runner.result.db.message:
        #comment: 如果消息类型为'terminate'，则跳过当前循环
        if(i['type'] == 'terminate'):
            continue
        job.print(i)

    # %%
    #comment: 发送消息到作业日志，指示正在写回结果
    jobmessage(job,"结果写回...",key="logs",verb='append')
    #comment: 使用潮流计算结果修改项目
    ce.runner.result.powerFlowModify(ce.project)

    #comment: 发送消息到作业日志，指示正在分析结果
    jobmessage(job,"结果分析...",key="logs",verb='append')
    # %%
    #comment: 读取Buses.csv文件到DataFrame
    df = pd.read_csv(qspath + "Buses.csv",encoding="utf-8",header = None)
    #comment: 将DataFrame转换为numpy数组
    dfa = np.array(df)
    #comment: 根据母线数据创建BusResDict字典，存储母线的V, Ang, Pg, Qg, Pl, Ql, Ps, Qs, Pres, Qres等结果
    BusResDict = {dfa[i,0]:{'V':dfa[i,2],'Ang':dfa[i,3],'Pg':dfa[i,4],'Qg':dfa[i,5],
                            'Pl':dfa[i,6],'Ql':dfa[i,7],'Ps':dfa[i,8],'Qs':dfa[i,9],
                            'Pres':dfa[i,10],'Qres':dfa[i,11]} for i in range(len(dfa[:,1]))}
    #comment: 读取Branches.csv文件到DataFrame
    df = pd.read_csv(qspath + "Branches.csv",encoding="utf-8",header = None)
    #comment: 将DataFrame转换为numpy数组
    dfa = np.array(df)
    #comment: 初始化BranchResDict字典
    BranchResDict = {}
    #comment: 遍历支路数据并填充BranchResDict
    for i in range(len(dfa[:,1])):
        #comment: 如果起始母线不在字典键中，则初始化其列表
        if(dfa[i,1] not in BranchResDict.keys()):
            BranchResDict[dfa[i,1]] = []
        #comment: 如果终止母线不在字典键中，则初始化其列表
        if(dfa[i,4] not in BranchResDict.keys()):
            BranchResDict[dfa[i,4]] = []
        #comment: 添加支路信息到起始母线对应的列表中
        BranchResDict[dfa[i,1]].append({'Name':dfa[i,0],'Opp':dfa[i,4],'P':dfa[i,2],'Q':dfa[i,3],'Pop':dfa[i,5],'Qop':dfa[i,6]})
        #comment: 添加支路信息到终止母线对应的列表中
        BranchResDict[dfa[i,4]].append({'Name':dfa[i,0],'Opp':dfa[i,1],'P':dfa[i,5],'Q':dfa[i,6],'Pop':dfa[i,2],'Qop':dfa[i,3]})


    #comment: 初始化CalculateAllRes字典
    CalculateAllRes = {}
    #comment: 遍历BusResDict中的母线，计算每个母线所在厂站的总不平衡量
    for i in BusResDict.keys():
        #comment: 获取同场站的所有母线集合
        busSet = getSameStationBuses(BusResDict,BranchResDict,set(),i)
        #comment: 初始化有功和无功总和
        sumP = 0
        sumQ = 0
        #comment: 遍历同场站的母线，累加其不平衡量
        for j in busSet:
            sumP += BusResDict[j]['Pres']
            sumQ += BusResDict[j]['Qres']
        #comment: 存储当前母线所在厂站的总不平衡量
        CalculateAllRes[i] = [sumP,sumQ]
    #comment: 初始化日志列表
    Log = []
    # res = sorted(list(BusResDict.keys()), key=lambda bus: abs(BusResDict[bus]['Pres']),reverse=True)
    #comment: 根据厂站总不平衡量的绝对值之和降序排序母线
    res = sorted(list(BusResDict.keys()), key=lambda bus: abs(CalculateAllRes[bus][0]) + abs(CalculateAllRes[bus][1]),reverse=True)
    # res = sorted(list(BusResDict.keys()), key=lambda bus: abs(CalculateAllRes[bus][0]) + abs(CalculateAllRes[bus][1]),reverse=False)
    #comment: 遍历排序后的母线，生成详细日志
    for i in res:
        # if abs(CalculateAllRes[i][0]) + abs(CalculateAllRes[i][1]) > 30:
        #     continue
        #comment: 添加空行
        Log.append('\n')
        #comment: 添加母线名称分隔符
        Log.append('————————————{0}—————————————\n'.format(i))
        #comment: 添加电压和相角信息
        Log.append('电压:{0}, 相角:{1}\n'.format(BusResDict[i]['V'],BusResDict[i]['Ang']*math.pi/180))
        #comment: 添加厂站不平衡P和Q
        Log.append('厂站不平衡P:{0}\n'.format(CalculateAllRes[i][0]))
        Log.append('厂站不平衡Q:{0}\n'.format(CalculateAllRes[i][1]))
        #comment: 添加母线不平衡P和Q
        Log.append('不平衡P:{0}\n'.format(BusResDict[i]['Pres']))
        Log.append('不平衡Q:{0}\n'.format(BusResDict[i]['Qres']))
        #comment: 添加发电P和Q
        Log.append('发电P:{0}\n'.format(BusResDict[i]['Pg']))
        Log.append('发电Q:{0}\n'.format(BusResDict[i]['Qg']))
        #comment: 添加负荷P和Q
        Log.append('负荷P:{0}\n'.format(BusResDict[i]['Pl']))
        Log.append('负荷Q:{0}\n'.format(BusResDict[i]['Ql']))
        #comment: 添加并补P和Q
        Log.append('并补P:{0}\n'.format(BusResDict[i]['Ps']))
        Log.append('并补Q:{0}\n'.format(BusResDict[i]['Qs']))
        #comment: 如果当前母线没有连接任何支路，则跳过
        if(i not in BranchResDict.keys()):
            continue
        #comment: 添加支路信息标题
        Log.append('\tBranches:\n')
        #comment: 遍历与当前母线相连的支路
        for j in range(len(BranchResDict[i])):
            #comment: 获取支路对应的组件
            comp = [k for k in ce.compLabelDict[BranchResDict[i][j]['Name']].values()][0]
            #comment: 根据组件类型计算电阻、电抗和电纳
            if(comp.definition == 'model/CloudPSS/TranssmissionLineRouter'):
                r = float(comp.args['Length'])*float(comp.args['R1pu'])
                x = float(comp.args['Length'])*float(comp.args['X1pu'])
                b = float(comp.args['Length'])*float(comp.args['B1pu'])
            elif(comp.definition == 'model/CloudPSS/_newTransformer_3p2w'):
                r = float(comp.args['Rl'])
                x = float(comp.args['Xl'])
                b = 0
            elif(comp.definition == 'model/CloudPSS/_newTransformer_3p3w'):
                if(i == BranchResDict[i][j]['Name']):
                    namei = BranchResDict[i][j]['Opp']
                else:
                    namei = i
                # if(namei not in comp.pins):
                #     continue
                #comment: 根据变压器连接方式计算等效电阻和电抗
                flag = [comp.pins['0'],comp.pins['1'],comp.pins['2']].index(namei)
                temp = [['23','12','13'],['13','12','23'],['12','13','23']]
                r = (float(comp.args['Rl'+temp[flag][1]]) + float(comp.args['Rl'+temp[flag][2]])-float(comp.args['Rl'+temp[flag][0]]) )/2
                x = (float(comp.args['Xl'+temp[flag][1]]) + float(comp.args['Xl'+temp[flag][2]])-float(comp.args['Xl'+temp[flag][0]]) )/2
                b = 0
            #comment: 添加支路详细信息
            Log.append('\t{0}, 对侧母线：{1}, 有功：{2}, 无功：{3}, 电压:{4}, 相角:{5}, r:{6}, x:{7}, b:{8}\n'.format(BranchResDict[i][j]['Name'],BranchResDict[i][j]['Opp'],
                                                                BranchResDict[i][j]['P'],BranchResDict[i][j]['Q'],
                                                                BusResDict[BranchResDict[i][j]['Opp']]['V'],BusResDict[BranchResDict[i][j]['Opp']]['Ang']*math.pi/180,
                                                                r,x,b))

    #comment: 将Log列表的内容写入test.txt文件
    with open("test.txt","w") as f:
        f.writelines(Log)

    #comment: V对比
    #comment: 读取Buses_solved.csv文件到DataFrame，这是潮流计算求解后的母线数据
    df = pd.read_csv(qspath + "Buses_solved.csv",encoding="utf-8",header = None)
    #comment: 将DataFrame转换为numpy数组
    dfa = np.array(df)
    #comment: 根据求解后的母线数据创建BusResDict_solved字典，存储母线的V, Ang等结果
    BusResDict_solved = {dfa[i,0]:{'V':dfa[i,2],'Ang':dfa[i,3],'Pg':dfa[i,4],'Qg':dfa[i,5],
                            'Pl':dfa[i,6],'Ql':dfa[i,7],'Ps':dfa[i,8],'Qs':dfa[i,9],
                            'Pres':dfa[i,10],'Qres':dfa[i,11]} for i in range(len(dfa[:,1]))}
    #comment: 读取Branches_solved.csv文件到DataFrame，这是潮流计算求解后的支路数据
    df = pd.read_csv(qspath + "Branches_solved.csv",encoding="utf-8",header = None)
    #comment: 将DataFrame转换为numpy数组
    dfa = np.array(df)
    #comment: 初始化BranchResDict_solved字典
    BranchResDict_solved = {}
    #comment: 遍历求解后的支路数据并填充BranchResDict_solved
    for i in range(len(dfa[:,1])):
        #comment: 如果起始母线不在字典键中，则初始化其列表
        if(dfa[i,1] not in BranchResDict_solved.keys()):
            BranchResDict_solved[dfa[i,1]] = []
        #comment: 如果终止母线不在字典键中，则初始化其列表
        if(dfa[i,4] not in BranchResDict_solved.keys()):
            BranchResDict_solved[dfa[i,4]] = []
        #comment: 添加支路信息到起始母线对应的列表中
        BranchResDict_solved[dfa[i,1]].append({'Name':dfa[i,0],'Opp':dfa[i,4],'P':dfa[i,2],'Q':dfa[i,3],'Pop':dfa[i,5],'Qop':dfa[i,6]})
        #comment: 添加支路信息到终止母线对应的列表中
        BranchResDict_solved[dfa[i,4]].append({'Name':dfa[i,0],'Opp':dfa[i,1],'P':dfa[i,5],'Q':dfa[i,6],'Pop':dfa[i,2],'Qop':dfa[i,3]})
    # res1 = sorted(list(BusResDict_solved.keys()), key=lambda bus: abs(BusResDict[bus]['V']-BusResDict_solved[bus]['V']),reverse=True)
    #comment: 根据原始母线电压幅值升序排序母线
    res1 = sorted(list(BusResDict_solved.keys()), key=lambda bus: abs(BusResDict[bus]['V']),reverse=False)
    #comment: 初始化Vcompare列表，添加表头
    Vcompare = ['Name\tV0\tAng0\tV\tAng\tDP\tDQ\n']
    #comment: 遍历排序后的母线，生成电压对比信息
    for i in res1:
        #comment: 如果电压幅值或相角变化过大，或者有功/无功不平衡量过大，则跳过当前母线
        if(abs(BusResDict[i]['V']-BusResDict_solved[i]['V'])>0.05 or abs(BusResDict[i]['Ang']-BusResDict_solved[i]['Ang']) > 0.2 or abs(BusResDict[i]['Pres']) > 100 or abs(BusResDict[i]['Qres']) > 100):
            continue
        #comment: 添加母线名称、原始电压幅值和相角、求解后电压幅值和相角以及有功/无功不平衡量到Vcompare列表
        Vcompare.append("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(i,BusResDict[i]['V'],
                        BusResDict[i]['Ang'],BusResDict_solved[i]['V'],BusResDict_solved[i]['Ang'],CalculateAllRes[i][0],CalculateAllRes[i][1]))
    #comment: 将Vcompare列表的内容写入Vcompare.txt文件
    with open("Vcompare.txt","w",encoding='gb2312') as f:
        f.writelines(Vcompare)
    #comment: 发送消息到作业日志，指示正在保存算例
    jobmessage(job,"保存算例...",key="logs",verb='append')
    #comment: 保存当前项目为新名称
    ce.saveProject(projectKey+'_Mod',name=ce.project.name+'_Mod')
    

#comment: 定义函数jobmessage，用于发送日志消息到CloudPSS作业UI
def jobmessage(job, content, level='info', html=False, key=None,verb='append'):
    #comment: 发送结构化的JSON消息到作业日志
    job.print({
        "key": key, #comment: 消息的唯一标识符，用于更新或放置到容器中
        "version": 1, #comment: 消息版本
        "verb": verb, #comment: 操作类型，如'append'（追加）
        "type": "log", #comment: 消息类型为日志
        "data": {
            "level": level, #comment: 日志级别
            'content': str(content)+'\n', #comment: 日志内容，转换为字符串并添加换行符
            "html": html #comment: 内容是否为HTML格式
        }
    })