#comment: 导入 numpy 库，并将其别名为 np，用于进行科学计算
import numpy as np
#comment: 从 numpy.linalg 模块导入 lg，用于进行线性代数运算，如矩阵求逆
import numpy.linalg as lg

#comment: 定义一个别名 nax 用于 np.newaxis，常用于在数组中增加维度
nax = np.newaxis
#comment: 从 vectfit3 库导入 vectfit3, full2full, ss2pr 函数，这些函数可能用于矢量拟合或状态空间模型转换
from vectfit3 import vectfit3, full2full, ss2pr# type: ignore
#comment: 从 time 模块导入 time 函数，用于测量时间
from time import time
# # %matplotlib
#comment: 导入 matplotlib.pyplot 库，并将其别名为 plt，用于绘图
import matplotlib.pyplot as plt
#comment: 导入 math 库，提供数学函数
import math 
#comment: 导入 cmath 库，提供复数数学函数
import cmath
#comment: 导入 scipy 库，用于科学计算
import scipy as sp
#comment: 从 scipy.constants 模块导入 const，提供物理常数
from scipy import constants as const
#comment: 从 scipy.integrate 模块导入 scii，用于数值积分
from scipy import integrate as scii
#comment: 从 scipy.special 模块导入 spp，提供特殊函数
import scipy.special as spp
#comment: 导入 scipy.ndimage 库，用于多维图像处理
import scipy.ndimage
#comment: 从 scipy.optimize 模块导入 sco，用于优化算法
from scipy import optimize as sco
#comment: 导入 scipy.signal 库，用于信号处理
import scipy.signal
#comment: 导入 os 模块，用于操作系统相关功能
import os
#comment: 导入 tkinter 库，用于创建 GUI 应用程序
import tkinter
#comment: 从 tkinter.filedialog 模块导入 tkinter.filedialog，用于文件选择对话框
import tkinter.filedialog
#comment: 导入 csv 模块，用于 CSV 文件读写
import csv
#comment: 导入 cloudpss 库，可能是一个与 CloudPSS 平台交互的库
import cloudpss
#comment: 从 CaseEditToolbox 库导入 CaseEditToolbox 类，用于案例编辑
from CaseEditToolbox import CaseEditToolbox# type: ignore
#comment: 从 CaseEditToolbox 库导入 is_number 函数，用于判断是否为数字
from CaseEditToolbox import is_number# type: ignore
#comment: 从 PSAToolbox 库导入 PSAToolbox 类
from PSAToolbox import PSAToolbox # type: ignore
#comment: 导入 json 库，用于 JSON 数据处理
import json
#comment: 导入 nest_asyncio 库，用于解决 asyncio 嵌套事件循环的问题
import nest_asyncio
#comment: 调用 nest_asyncio.apply() 应用补丁，允许嵌套的异步事件循环
nest_asyncio.apply()


#comment: 定义一个函数 loadConfigFile，用于加载配置文件
def loadConfigFile(ce, opts):
    #comment: 使用 with 语句打开 saSource.json 文件，以utf-8编码读取
    with open('saSource.json', "r", encoding='utf-8') as f:
        #comment: 使用 json.load() 从文件中加载 JSON 数据到 compLib 变量
        compLib = json.load(f)
    #comment: 设置 ce (CaseEditToolbox) 实例的配置，包括 token, apiURL, username, projectKey，并指定组件库名称
    ce.setConfig(opts['token'],opts['apiURL'],opts['username'],opts['projectKey'], comLibName = 'saSource.json');
    #comment: 设置 generateG 标志为 True，表示生成 iGraph 信息
    generateG = True;
    #comment: 将 generateG 赋值给 ce.config['iGraph']
    ce.config['iGraph'] = generateG  #  生成iGraph信息，已有iGraph信息时注释本块
    #comment: 设置 deleteEdges 标志为 True，表示删除边
    ce.config['deleteEdges'] = True
    #comment: 调用 ce 实例的 setInitialConditions() 方法进行初始化
    ce.setInitialConditions() # 进行初始化
    #comment: 调用 ce 实例的 createSACanvas() 方法创建 SA 画布
    ce.createSACanvas()
    #comment: 获取 CloudPSS 项目中所有 'model/CloudPSS/_newBus_3p' 类型的组件，并将其列表赋值给 opts['BusList']
    opts['BusList'] = list(ce.project.getComponentsByRid('model/CloudPSS/_newBus_3p'))
    #comment: 获取 CloudPSS 项目中所有 'model/CloudPSS/_newTransformer_3p3w' 类型的组件，并将其列表赋值给 opts['Trans3pList']
    opts['Trans3pList'] = list(ce.project.getComponentsByRid('model/CloudPSS/_newTransformer_3p3w'))
    #comment: 打印消息，表示算例加载完成
    print('载入算例完成！')

#comment: 定义函数 CalY_Comp，用于计算单个组件的导纳矩阵
def CalY_Comp(ce, key, freq, opts):
    #comment: 根据 key 获取 CloudPSS 项目中的组件
    comp = ce.project.getComponentByKey(key)
    #comment: 获取该组件在拓扑结构中的顶层信息
    top = ce.topo['components']['/'+key]
    #comment: 初始化一个空列表 A，用于存储连接的母线索引
    A = []
    #comment: 初始化一个空列表 pinName，用于存储连接的引脚名称
    pinName = []
    # print(key)
    # sourceflag = 0
    #comment: 遍历与当前组件相邻的节点
    for i in ce.g.vs.find('/'+key).neighbors():
        #comment: 如果相邻节点的 rid 是三相母线
        if(i['rid']=='model/CloudPSS/_newBus_3p'):
            # print(i['name'][1:])
            #comment: 将母线名称（去除第一个字符）在 BusList 中的索引添加到 A
            A.append(opts['BusList'].index(i['name'][1:]))
            #comment: 获取连接母线组件的引脚 '0' 的名称，并添加到 pinName
            pinName.append(ce.project.getComponentByKey(i['name'][1:]).pins['0'])
    #comment: 如果组件定义是 TranssmissionLineRouter (输电线路)
    if(comp.definition == 'model/CloudPSS/TranssmissionLineRouter'):
        # PI型电路
        #comment: 如果连接的母线数量不等于 2，则打印错误信息
        if(len(A) != 2):
            print('error:'+key+' lenA!=2')
        #comment: 获取基准电压 (Vbase)
        V = float(top['args']['Vbase'])
        #comment: 获取基准视在功率 (Sbase)
        Sbase = float(top['args']['Sbase'])
        #comment: 获取线路长度 (Length)
        L = float(top['args']['Length'])
        #comment: 计算线路的电阻 R1
        R1 = float(top['args']['R1pu']) * (V**2 / Sbase) * L
        #comment: 计算线路的电抗 X1
        X1 = 1j * float(top['args']['X1pu']) * (V**2 / Sbase) / 50 * freq * L;
        #comment: 计算线路的对地导纳 B1
        B1 = 1j * float(top['args']['B1pu']) * Sbase / (V**2) / 50 * freq * L;
        
        #comment: 构建输电线路的 PI 型导纳矩阵
        ycomp = np.eye(2) * B1/2 + np.mat([[1,-1],[-1,1]])/(R1 + X1)
        
    #comment: 如果组件定义是 _newTransformer_3p2w (三相两绕组变压器)
    elif(comp.definition == 'model/CloudPSS/_newTransformer_3p2w'):
        #comment: 如果连接的母线数量不等于 2，则打印错误信息
        if(len(A) != 2):
            print('error:'+key+' lenA!=2')
        # print((pinName,comp.pins['0'],comp.pins['1']))
        #comment: 初始化相角 theta 为 0
        theta = 0;

        #comment: 判断变压器绕组的连接方式（Yd或Dy）以及引线方向，计算相角 theta
        if(top['args']['YD1'] == '0' and top['args']['YD2'] == '1'):
                if(top['args']['Lead'] == '1'):
                    theta = math.pi/6;
                else:
                    theta = -math.pi/6;
        elif(top['args']['YD1'] == '1' and top['args']['YD2'] == '0'):
                if(top['args']['Lead'] == '1'):
                    theta = -math.pi/6;
                else:
                    theta = math.pi/6;
        #comment: 根据引脚连接顺序确定主侧和副侧电压以及匝比 k
        if(pinName[0] == comp.pins['0']):
            V1 = float(top['args']['V1'])
            V2 = float(top['args']['V2'])
            k = V1 / V2;
            theta = -theta; # 反转相角
        else:
            V1 = float(top['args']['V2'])
            V2 = float(top['args']['V1'])
            k = V1 / V2;
            
        #comment: 获取基准视在功率 Tmva
        Sbase = float(top['args']['Tmva'])
        #comment: 计算等效电感 L
        L = float(top['args']['Xl']) * V1**2 / Sbase / 50 / 2 / math.pi
        #comment: 计算等效电阻 R
        R = float(top['args']['Rl']) * V1**2 / Sbase

        #comment: 构建电感矩阵 Lb，考虑匝比和相角
        Lb = np.mat([[1,-k*np.exp(1j*theta)],[-k*np.exp(-1j*theta),k**2]])/L
        #comment: 构建电阻矩阵 Rb
        Rb = np.diag([R/2,R/2/(k**2)])
        #comment: 计算变压器的导纳矩阵 ycomp
        ycomp = lg.inv(1j * 2*math.pi * freq * np.eye(2) + Lb@Rb) @ Lb

    #comment: 如果组件定义是 _newTransformer_3p3w (三相三绕组变压器)
    elif(comp.definition == 'model/CloudPSS/_newTransformer_3p3w'):
        #comment: 如果连接的母线数量不等于 3，则打印错误信息
        if(len(A) != 3):
            print('error:'+key+' lenA!=3')

        #comment: 初始化三相导纳矩阵 ycomp 为零矩阵
        ycomp = np.zeros((3,3),dtype=complex)
        #comment: 获取三个绕组中最大的基准视在功率
        Sbase = max(float(top['args']['Tmva1']),float(top['args']['Tmva2']),float(top['args']['Tmva3']))
        #comment: 计算三个绕组的等效电感 L01, L02, L03
        L01 = (float(top['args']['Xl12']) + float(top['args']['Xl13']) - float(top['args']['Xl23']))/2 *float(top['args']['V1'])**2/ Sbase / 50 / 2 / math.pi
        L02 = (float(top['args']['Xl12']) + float(top['args']['Xl23']) - float(top['args']['Xl13']))/2 *float(top['args']['V1'])**2/ Sbase / 50 / 2 / math.pi
        L03 = (float(top['args']['Xl23']) + float(top['args']['Xl13']) - float(top['args']['Xl12']))/2 *float(top['args']['V1'])**2/ Sbase / 50 / 2 / math.pi

        #comment: 计算三个绕组的等效电阻 R01, R02, R03
        R01 = (float(top['args']['Rl12']) + float(top['args']['Rl13']) - float(top['args']['Rl23']))/2 *float(top['args']['V1'])**2/ Sbase
        R02 = (float(top['args']['Rl12']) + float(top['args']['Rl23']) - float(top['args']['Rl13']))/2 *float(top['args']['V2'])**2/ Sbase
        R03 = (float(top['args']['Rl23']) + float(top['args']['Rl13']) - float(top['args']['Rl12']))/2 *float(top['args']['V3'])**2/ Sbase

        #comment: 初始化三个绕组的相角
        theta01 = 0;
        theta02 = 0;
        theta03 = 0;

        #comment: 根据 YD 连接方式设置相角
        if(top['args']['YD1'] == '1'):
            theta01 = math.pi/6;
        if(top['args']['YD2'] == '1'):
            theta02 = math.pi/6;
        if(top['args']['YD3'] == '1'):
            theta03 = math.pi/6;
        #comment: 根据引线方向调整相角
        if(top['args']['Lead'] == '2'):
            theta01 = -theta01;
            theta02 = -theta02;
            theta03 = -theta03;
        
        #comment: 根据连接的引脚名称获取其在组件引脚列表中的索引
        Pindex = [[comp.pins['0'],comp.pins['1'],comp.pins['2']].index(x) for x in pinName]
        #comment: 获取三个绕组的额定电压列表
        V0list = [float(top['args']['V1']),float(top['args']['V2']),float(top['args']['V3'])]
        #comment: 获取实际使用的三个绕组电压
        V1 = V0list[Pindex[0]]
        V2 = V0list[Pindex[1]]
        V3 = V0list[Pindex[2]]
        #comment: 计算匝比 k12 和 k13
        k12 = V1 / V2;
        k13 = V1 / V3;
        #comment: 计算匝比的平方和交叉项
        k22 = k12 * k12;
        k23 = k12 * k13;
        k33 = k13 * k13;
        #comment: 获取相角列表
        THT0 = [theta01,theta02,theta03]
        #comment: 获取实际使用的三个绕组相角
        theta1 = THT0[Pindex[0]]
        theta2 = THT0[Pindex[1]]
        theta3 = THT0[Pindex[2]]
                
        #comment: 获取实际使用的电感 L1, L2, L3
        temp = [L01,L02,L03]
        L1 = temp[Pindex[0]]
        L2 = temp[Pindex[1]]
        L3 = temp[Pindex[2]]
        #comment: 获取实际使用的电阻 R1, R2, R3
        temp = [R01,R02,R03]
        R1 = temp[Pindex[0]]
        R2 = temp[Pindex[1]]
        R3 = temp[Pindex[2]]

        #comment: 计算中间变量 LL，用于构建电感矩阵
        LL = L1 * L2 + L2 * L3 + L1 * L3;
        #comment: 计算电感矩阵的元素
        LL1 = (L2 + L3) / LL;
        LL2 = (L1 + L3) * k22 / LL;
        LL3 = (L1 + L2) * k33 / LL;
        LL12 = -k12 * L3 / LL;
        LL13 = -k13 * L2 / LL;
        LL23 = -k23 * L1 / LL;
        #comment: 构建电感矩阵 Lb
        Lb = np.mat([[LL1, LL12,LL13],
                        [LL12,LL2, LL23],
                        [LL13,LL23, LL3]])
        #comment: 构建电阻矩阵 Rb
        Rb = np.diag([R1,R2,R3])

        # print(LL)
        # print(Lb)
        # print(Rb)

        #comment: 计算三绕组变压器的导纳矩阵 ycomp
        ycomp = lg.inv(1j * 2*math.pi * freq * np.eye(3) + Lb@Rb) @ Lb
 
        
    #comment: 如果组件定义是 _newExpLoad_3p (三相指数负载)
    elif(comp.definition == 'model/CloudPSS/_newExpLoad_3p'):
        #comment: 如果连接的母线数量不等于 1，则打印错误信息
        if(len(A) != 1):
            print('error:'+key+' lenA!=1')
        #comment: 计算负载电压 V
        V = float(top['args']['v']) * float(top['args']['Vi'])
        #comment: 获取有功功率 P
        P = float(top['args']['p'])
        #comment: 获取无功功率 Q
        Q = float(top['args']['q'])
        #comment: 计算等效电导 G
        G = P/V**2;
        #comment: 根据无功功率 Q 的正负计算等效电纳 B
        if(Q>=0):
            B =  -1j * Q / (V ** 2) * 50 / freq;
        else:
            B =  -1j * Q / (V ** 2) / 50 * freq;
        # B=0
        #comment: 计算负载的导纳 ycomp
        ycomp = B + G

    #comment: 如果组件定义是 SyncGeneratorRouter (同步发电机)
    elif(comp.definition == 'model/CloudPSS/SyncGeneratorRouter'):
        #comment: 如果连接的母线数量不等于 1，则打印错误信息
        if(len(A) != 1):
            print('error:'+key+' lenA!=1')
        #comment: 计算额定电压 V
        V = float(top['args']['V']) * math.sqrt(3)
        #comment: 获取额定视在功率 S
        S = float(top['args']['Smva'])
        #comment: 获取参数类型 ParamType
        ParamType = int(top['args']['ParamType'])
        #comment: 如果参数类型是 0 (表示使用 Xd, Xls 等参数)
        if(ParamType == 0):
            #comment: 计算定子电阻 Rs
            Rs = float(top['args']['Rs']) * V**2 / S
            #comment: 计算漏电感 Lls
            Lls = float(top['args']['Xls']) * V**2 / S / 50 / 2 / math.pi
            #comment: 计算 d 轴同步电感 Ld (注意这里是 Xd 减去漏电抗，再计算电感，可能存在逻辑错误，应为Xd对应电感)
            Ld = float(top['args']['Xd']) * V**2 / S / 50 / 2 / math.pi - Lls
            #comment: 计算励磁绕组漏电感 Lfd
            Lfd = float(top['args']['Xlfd']) * V**2 / S / 50 / 2 / math.pi
            #comment: 计算阻尼绕组漏电感 Lkd
            Lkd = float(top['args']['Xlkd']) * V**2 / S / 50 / 2 / math.pi
            #comment: 计算同步电感 Ls
            Ls = Lls + 1/(1/Ld + 1/Lfd + 1/Lkd)
            #comment: 计算同步电抗 Xs
            Xs = 1j * 2*math.pi * freq * Ls
            #comment: 计算发电机导纳 ycomp
            ycomp = 1/(Rs+Xs)
            # ycomp = 0
        # sourceflag = 1
    #comment: 如果组件定义是 Thevenin_3p (戴维南等效电源)
    elif(comp.definition == 'model/CloudPSS/Thevenin_3p'):
        #comment: 如果连接的母线数量不等于 1，则打印错误信息
        if(len(A) != 1):
            print('error:'+key+' lenA!=1')
        #comment: 获取等效电阻 R1
        R1 = float(top['args']['R1'])
        #comment: 计算等效电抗 X1
        X1 = 1j * float(top['args']['X1']) / float(top['args']['f']) * freq
        #comment: 计算等效导纳 ycomp
        ycomp = 1/(R1+X1)
    #comment: 如果组件定义是 _newShuntLC_3p (并联电容/电抗器)
    elif(comp.definition == 'model/CloudPSS/_newShuntLC_3p'):
        #comment: 如果连接的母线数量不等于 1，则打印错误信息
        if(len(A) != 1):
            print('error:'+key+' lenA!=1')
        #comment: 获取电压 V
        V = float(top['args']['v'])
        #comment: 获取频率 f
        f = float(top['args']['freq'])
        #comment: 计算等效电纳 B1 (基于额定无功功率 S 和电压 V)
        B1 = float(top['args']['s']) / (V**2)
        #comment: 根据额定无功功率 S 的正负调整 B1 的频率依赖性
        if(float(top['args']['s']) >= 0):
            B1 = -1j * B1 *f / freq
        else:
            B1 = -1j * B1 *freq / f
        # G = 1/V**2;
        #comment: 计算组件的导纳 ycomp (这里似乎只有 B1，没有 G 或其他部分)
        ycomp = B1 

    #comment: 如果组件定义是 GW_mask_power_flow (网关掩码潮流，可能与风机相关)
    elif(comp.definition == 'model/admin/GW_mask_power_flow'):
        #comment: 如果连接的母线数量不等于 1，则打印错误信息
        if(len(A) != 1):
            print('error:'+key+' lenA!=1')
        #comment: 从 opts 中获取 PMSG_FDNE_Z 数据
        PMSG_FDNE_Z = opts['PMSG_FDNE_Z']
        #comment: 初始化阻抗 Z 为 0
        Z = 0;
        #comment: 根据 PMSG_FDNE_Z 中的数据（可能包含极点和残差）计算阻抗 Z
        for i in range(len(PMSG_FDNE_Z.keys())-2):
            Z += PMSG_FDNE_Z[i][0][0]/((2j*math.pi*freq)-PMSG_FDNE_Z['Poles'][i])
        #comment: 添加常数项到阻抗 Z
        Z += PMSG_FDNE_Z['Const'][0][0]
        #comment: 调整阻抗 Z，考虑风机数量和 PCC 电压
        Z = Z / float(top['args']['WT_Num']) * float(top['args']['Vpcc'])**2
        #comment: 计算组件的导纳 ycomp
        ycomp = 1/Z
    #comment: 如果组件定义不是以上任何一种
    else:
        #comment: 将 A 和 ycomp 设置为 None
        A = None
        ycomp = None
    
    #comment: 返回计算出的组件导纳 ycomp 和连接的母线索引 A
    return ycomp, A

#comment: 定义函数 CalY_All，用于计算整个电力系统的节点导纳矩阵
def CalY_All(ce, freq, opts):
    # 地缆
    #comment: 定义圆周率 pi
    pi = math.pi;
    #comment: 计算角频率 w
    w = 2*pi*freq;
    
    # NN = len(opts['BusList']) + len(opts['Trans3pList'])
    #comment: 系统中的节点数量 NN，这里是母线的数量
    NN = len(opts['BusList'])
    #comment: 定义电源组件的 RID 列表
    SourceDefinitions = ['model/CloudPSS/SyncGeneratorRouter','model/CloudPSS/Thevenin_3p']
    #comment: 初始化节点导纳矩阵 Ynet 为零矩阵
    Ynet = np.zeros((NN,NN),dtype = complex);
    # print('NN'+str(NN))
    # SFlags = []
    #comment: 遍历 CloudPSS 拓扑图中的所有节点名称
    for i in ce.g.vs['name']:
        #comment: 如果当前节点是三相母线，则跳过
        if(ce.g.vs.find(i)['rid']=='model/CloudPSS/_newBus_3p'):
            continue
        #comment: 初始化 flag 为 0
        flag = 0
        #comment: 如果当前节点没有连接到任何三相母线，则跳过
        if 'model/CloudPSS/_newBus_3p' not in [j['rid'] for j in ce.g.vs.find(i).neighbors()]:
            continue
        
        #comment: 初始化组件导纳 ycomp 为 0
        ycomp = 0;
        #comment: 调用 CalY_Comp 函数计算当前组件的导纳和连接信息
        ycomp,A = CalY_Comp(ce, i[1:], freq, opts)
        #comment: 如果 A (连接信息) 不为 None
        if(A != None):
            # print(Ynet[A,np.mat(A).T])
            # print(ycomp)
            #comment: 将计算出的组件导纳 ycomp 添加到总体的节点导纳矩阵 Ynet 中
            Ynet[A,np.mat(A).T] = Ynet[A,np.mat(A).T] + ycomp


    #comment: 返回构建好的节点导纳矩阵 Ynet
    return Ynet;
            
#comment: 定义函数 CalZ_All，用于计算整个电力系统的节点阻抗矩阵
def CalZ_All(ce, freq, opts):
    #comment: 调用 CalY_All 函数计算节点导纳矩阵 Ynet
    Ynet = CalY_All(ce, freq, opts)
    #comment: 计算节点阻抗矩阵 Znet (Ynet 的逆矩阵)
    Znet = lg.inv(Ynet)
    #comment: 如果 opts 中没有 'SelectBuses' 或者 'SelectBuses' 是空列表
    if('SelectBuses' not in opts.keys() or opts['SelectBuses'] == []):
        #comment: 直接返回 Znet 和 Ynet
        return Znet,Ynet
    #comment: 否则，根据 'SelectBuses' 筛选出子矩阵
    else:
        #comment: 获取所选母线在 BusList 中的索引列表
        nodelist = [opts['BusList'].index(i) for i in opts['SelectBuses']]
        #comment: 返回筛选后的 Znet 和 Ynet 子矩阵
        return Znet[nodelist,:][:,nodelist],Ynet[nodelist,:][:,nodelist]

#comment: 定义函数 NRstep，实现牛顿-拉夫逊 (Newton-Raphson) 方法的一个迭代步骤
def NRstep(x, target):
    #comment: 获取向量 x 的长度
    n = len(x);
    #comment: 工作维度 n-1
    n = n-1;
    #comment: 截取 x 的前 n 个元素作为 t (特征向量部分)
    t = x[:n];
    #comment: x 的最后一个元素作为 lmd (特征值部分)
    lmd = x[n];
    #comment: 初始化 F 向量为零，长度为 n+1
    F = np.zeros(n+1,dtype=complex);
    #comment: 计算 F 的前 n 个元素 (特征向量残差)
    F[0:n] = (target - lmd*np.eye(n)) @ t;
    #comment: 计算 F 的最后一个元素 (特征向量归一化残差)
    F[n] = lg.norm(t)**2 - 1;
    #comment: 初始化雅可比矩阵 J 为零，大小为 (n+1)x(n+1)
    J = np.zeros((n+1,n+1),dtype=complex);
    #comment: 填充 J 的左上角部分 (关于特征向量的偏导)
    J[:n,:n] = (target - lmd*np.eye(n));
    #comment: 填充 J 的右上角部分 (关于特征值的偏导)
    J[:n,n] = -t;
    #comment: 填充 J 的左下角部分 (归一化条件关于特征向量的偏导)
    J[n,:n] = 2 * t;
    #comment: J 的右下角部分为 0 (归一化条件关于特征值的偏导)
    J[n,n] = 0;
    
    #comment: 计算下一步的 xn (x - J_inv @ F)
    xn = x - lg.solve(J,F);

    #comment: 返回 xn 和 F
    return xn,F

#comment: 定义函数 LMstep，实现 Levenberg-Marquardt (LM) 方法的一个迭代步骤
def LMstep(x, target,sigma):
    #comment: 获取向量 x 的长度
    n = len(x);
    #comment: 工作维度 n-1
    n = n-1;
    #comment: 截取 x 的前 n 个元素作为 t (特征向量部分)
    t = x[:n];
    #comment: x 的最后一个元素作为 lmd (特征值部分)
    lmd = x[n];
    #comment: 初始化 F 向量为零，长度为 n+1
    F = np.zeros(n+1,dtype=complex);

    #comment: 计算 F 的前 n 个元素 (特征向量残差)
    F[0:n] = (target - lmd*np.eye(n)) @ t;
    # F[n] = lg.norm(t)**2 - 1; #comment: 注释掉的原始归一化条件
    #comment: 计算 F 的最后一个元素 (特征向量归一化残差)，使用 sum(t*t) 等价于 norm(t)**2
    F[n] = np.sum(t*t) - 1;
    #comment: 初始化雅可比矩阵 J 为零，大小为 (n+1)x(n+1)
    J = np.zeros((n+1,n+1),dtype=complex);
    #comment: 填充 J 的左上角部分
    J[:n,:n] = (target - lmd*np.eye(n));
    #comment: 填充 J 的右上角部分
    J[:n,n] = -t;
    #comment: 填充 J 的左下角部分
    J[n,:n] = 2 * t;
    #comment: J 的右下角部分为 0
    J[n,n] = 0;

    #comment: 计算 H 矩阵 (J^H @ J)
    H = J.T.conj() @ J;
    
    #comment: 计算下一步的 xn (x - (H + sigma * diag(diag(H)))_inv @ J^H @ F) (LM 更新规则)
    xn = x - lg.solve(H+sigma * np.diag(np.diag(H)),J.T.conj()@F);
    
    #comment: 从 xn 中重新提取 t (特征向量部分)
    t = xn[:n];
    #comment: 从 xn 中重新提取 lmd (特征值部分)
    lmd = xn[n];
    #comment: 重新计算 F (用于评估收敛性或下一步迭代)
    F[0:n] = (target - lmd*np.eye(n)) @ t;
    F[n] = np.sum(t*t) - 1;
    
    #comment: 返回 xn 和 F
    return xn,F

#comment: 定义函数 NRstep_Large，用于多特征值/特征向量的牛顿-拉夫逊迭代步骤 (可能处理较大的系统)
def NRstep_Large(target, eig0, Ti0):
    # 将所有的S合在一起
    # x: T11, T21,T31,lambda1, T12,T22,T32, lambda2...

    #comment: 获取特征值的数量 n (也代表矩阵的维度)
    n = len(eig0);
    #comment: 计算总状态变量数 N (n*n 个特征向量元素 + n 个特征值)
    N = n*n;
    #comment: 初始化残差向量 F
    F = np.zeros(N+n,dtype=complex);
    #comment: 初始化雅可比矩阵 J
    J = np.zeros((N+n,N+n),dtype=complex);
    #comment: 初始化状态变量向量 x
    x = np.zeros(N+n,dtype=complex);
    
    #comment: 遍历每个特征值和特征向量
    for i in range(n):
        #comment: 获取第 i 个特征向量 t
        t = Ti0[:,i];
        #comment: 获取第 i 个特征值 lmd
        lmd = eig0[i];
        #comment: 将特征向量 t 存入 x 中相应位置
        x[(n*i):(n*i+n)] = t;
        #comment: 将特征值 lmd 存入 x 中相应位置 (在特征向量之后)
        x[N+i] = lmd;
        #comment: 计算特征方程的残差部分
        F[(n*i):(n*i+n)] = (target - lmd*np.eye(n)) @ t;
        #comment: 计算特征向量归一化条件的残差部分
        F[N+i] = lg.norm(t)**2 - 1;
        # F[N+i] = lg.det(Ti0)-1; #comment: 备用的行列式归一化条件 (当前注释掉)
        #comment: 填充雅可比矩阵 J 对应特征向量部分的偏导
        J[(n*i):(n*i+n),(n*i):(n*i+n)] = (target - lmd*np.eye(n));
        #comment: 填充雅可比矩阵 J 对应特征值部分的偏导
        J[(n*i):(n*i+n),N+i] = - t;

        #comment: 填充雅可比矩阵 J 归一化条件关于特征向量的偏导
        J[N+i,(n*i):(n*i+n)] = 2*t;

                
    #comment: 计算下一步的 xn (x - J_inv @ F)
    xn = x - lg.solve(J,F);
    #comment: 从 xn 中提取更新后的特征值 eig
    eig = xn[N:];
    #comment: 初始化更新后的特征向量矩阵 Ti
    Ti = np.zeros((n,n),dtype=complex);
    #comment: 从 xn 中提取更新后的特征向量并填充到 Ti
    for i in range(n):
        Ti[:,i] = xn[(n*i):(n*i+n)];
        

    # print(abs(J[0,:]))
    # print(F)
    #comment: 返回更新后的特征值、特征向量矩阵以及残差范数 (用于判断收敛)
    return eig, Ti, lg.norm(F)

#comment: 定义函数 eigenMat_NR，用于使用牛顿-拉夫逊或 Levenberg-Marquardt 方法计算矩阵的特征值和特征向量
def eigenMat_NR(target, eig0, Ti0, opts):
    
    #comment: 初始化一个字典 opts1，用于存储计算选项，设置默认最大迭代次数和收敛误差
    opts1 = {}
    opts1['EigMaxIter'] = 10;
    opts1['EigEps'] = 1e-8;
    #comment: 使用传入的 opts 更新 opts1
    opts1.update(opts);
    
    #comment: 获取最大迭代次数
    maxIter = opts1['EigMaxIter'] 
    #comment: 获取收敛误差
    eps = opts1['EigEps']
    
    # 目标矩阵先除以二范数以适配eps
    #comment: 计算目标矩阵的二范数
    TN = lg.norm(target);
    # target1 = target / TN; #comment: 原始代码中将目标矩阵归一化，但目前注释掉
    # eig1 = eig0 / TN;     #comment: 原始代码中将特征值归一化，但目前注释掉

    #comment: 使用原始的目标矩阵和特征值
    target1 = target;
    eig1 = eig0;
    
    #comment: 定义方法的类型，这里设置为 1，表示使用 LM 方法
    type = 1
    #comment: 如果 type 为 0 (牛顿-拉夫逊方法)
    if(type==0):
        # 目前从文献中找到的NR法求连续变化的矩阵特征值方法有缺陷，可能会出现重复的Ti列向量。暂不采用了。
        #comment: 获取矩阵维度
        n = len(eig1);
        #comment: 初始化特征值数组 eigL
        eigL = np.zeros(n,dtype=complex);
        #comment: 初始化特征向量矩阵 Ti
        Ti = np.zeros((n,n),dtype=complex);
        #comment: 初始化单次迭代的状态变量 x
        x = np.zeros(n+1, dtype=complex)
        # print(eig1)
        # print(target1)
        #comment: 遍历每个特征值/特征向量对进行迭代
        for k in range(n):
            #comment: 获取当前特征值和特征向量
            lmd = eig1[k];
            Tik = Ti0[:,k];
            #comment: 填充 x
            x[:n] = Tik;
            x[n] = lmd;
            #comment: 初始化残差 F 为较大值
            F = 999;
            # print([k,lmd,Tik,x])
            #comment: 进行迭代直到收敛或达到最大迭代次数
            for Iter in range(maxIter):
                #comment: 执行 NR 迭代步骤
                xn, F = NRstep(x, target1);
                #comment: 检查收敛条件
                if(np.sum(np.abs(F)) < eps*lg.norm(target)):
                    break
                #comment: 更新 x
                x = xn;
            # print([k,xn,F,Tik])
            #comment: 更新 eigL 和 Ti
            eigL[k] = xn[n];
            Ti[:,k] = xn[:n];
            # if(np.sum(np.abs(F)) > eps):
            #     print('column '+str(k)+' failes to converge for eigenvalue calculation. error='+str(np.sum(np.abs(F)))+"---"+str(eps));
        #comment: 计算特征分解的误差
        err = lg.norm(lg.solve(Ti , target1) @ Ti - np.diag(eigL));
        # eigL = eigL * TN;

    #comment: 如果 type 为 1 (Levenberg-Marquardt 方法)
    elif(type==1):
        # LM方法
        #comment: 获取矩阵维度
        n = len(eig1);
        #comment: 初始化特征值数组 eigL
        eigL = np.zeros(n,dtype=complex);
        #comment: 初始化特征向量矩阵 Ti
        Ti = np.zeros((n,n),dtype=complex);
        #comment: 初始化单次迭代的状态变量 x
        x = np.zeros(n+1, dtype=complex)
        # print(eig1)
        # print(target1)
        #comment: 遍历每个特征值/特征向量对进行迭代
        for k in range(n):
            #comment: 获取当前特征值和特征向量
            lmd = eig1[k];
            Tik = Ti0[:,k];
            #comment: 填充 x
            x[:n] = Tik;
            x[n] = lmd;
            #comment: 初始化残差 F 和 F_old 为较大值
            F = 999;
            Fold=F;
            # print([k,lmd,Tik,x])
            #comment: 初始化 LM 参数 sigma
            sigma = 1e-4;
            #comment: 进行迭代直到收敛或达到最大迭代次数
            for Iter in range(maxIter):
                #comment: 执行 LM 迭代步骤
                xn, F = LMstep(x, target1, sigma);
                #comment: 检查收敛条件
                if(lg.norm(F) < eps*lg.norm(target)*1e-3):
                    break
                #comment: 根据残差范数调整 sigma (LM 算法的核心)
                if(lg.norm(F)< Fold and sigma > 1e-14) :
                    sigma = sigma / 10;
                elif(lg.norm(F)> Fold and sigma < 1):
                    sigma = sigma * 5;
                #comment: 更新 Fold
                Fold = lg.norm(F);

                #comment: 更新 x
                x = xn;
            # print([k,xn,F,Tik])
            #comment: 更新 eigL 和 Ti
            eigL[k] = xn[n];
            Ti[:,k] = xn[:n];
            # if(lg.norm(F) > eps*lg.norm(target)):
            #     print('column '+str(k)+' failes to converge for eigenvalue calculation. error='+str(lg.norm(F))+"---"+str(eps));
        #comment: 尝试计算特征分解的误差，如果 Ti 不可逆则捕获异常
        try:
            err = lg.norm(lg.solve(Ti , target1) @ Ti - np.diag(eigL));
        # comment: 打印 Ti 如果发生异常
        except:
            print(Ti)
        # err = lg.norm(F);
        # eigL = eigL * TN;

    #comment: 如果 type 为 2 (大型系统牛顿-拉夫逊方法，一次性处理所有特征值/向量)
    elif(type==2):
        # 目标矩阵先除以二范数以适配eps
        #comment: 计算目标矩阵的二范数
        TN = lg.norm(target);
        #comment: 使用原始的目标矩阵和特征值/特征向量
        target1 = target;
        eig1 = eig0;
        Ti = Ti0;
        #comment: 初始化 Fold 为较大值
        Fold = 999999;
        #comment: 进行迭代直到收敛或达到最大迭代次数
        for Iter in range(maxIter):
            #comment: 执行大型 NR 迭代步骤
            eig1, Ti ,F= NRstep_Large(target1, eig1, Ti)
            #comment: 检查收敛条件
            if(F < eps * TN):
                break
            #comment: 调整 sigma (这里的 sigma 似乎没有在 NRstep_Large 中使用，但在此处作为 LM 风格的步长调整)
            if(F< Fold and sigma > 1e-14) :
                sigma = sigma * 0.1;
            elif(sigma < 1e5):
                sigma = sigma * 10;
        #comment: 计算特征分解的误差
        err = lg.norm(lg.solve(Ti , target1) @ Ti - np.diag(eig1));
        #comment: 将 eig1 赋值给 eigL
        eigL = eig1;

    #comment: 返回计算出的特征值、特征向量矩阵和误差
    return eigL, Ti, err


#comment: 定义函数 plotFitting，用于绘制拟合结果
def plotFitting(s, f, fit, options):
    # absolute fit plot
    #comment: 从复频率 s 的虚部计算频率 (Hz)
    freq = s.imag / (2*np.pi)
    #comment: 创建一个新的图形窗口，设置大小
    plt.figure(0,[6,3])
    #comment: 初始化 handles 和 labels 列表
    handles = []
    labels  = []
    #comment: 绘制数据幅值曲线
    handles.append(plt.plot(freq, np.abs(f.T), 'b-'));    labels.append('Data')
    #comment: 如果 options 中没有 'onlyf' 或者 'onlyf' 为 False，则绘制拟合曲线
    if('onlyf' not in options.keys() or not options['onlyf']):
        handles.append(plt.plot(freq, np.abs(fit.T), 'r--')); labels.append('FRVF')
    #comment: 如果允许绘制误差，则绘制偏差曲线
    if options['errplot']:
        handles.append(plt.plot(freq, np.abs(f-fit).T, 'g')); labels.append('Deviation')
    # plt.xlim(freq[0], freq[-1])
    # plt.xlim(20, 1000)
    # plt.ylim(1e-6*np.max(np.abs(f)),1.2*np.max(np.abs(f)))
    #comment: 如果 options 中 'logx' 为 True，则设置 x 轴为对数坐标
    if options['logx']:
        plt.xscale('log')
    #comment: 如果 options 中 'logy' 为 True，则设置 y 轴为对数坐标
    if options['logy']:
        plt.yscale('log')
    #comment: 设置 x 轴标签
    plt.xlabel('Frequency [Hz]')
    #comment: 设置 y 轴标签
    plt.ylabel('Magnitude')
    # plt.title('Approximation of f')
    #comment: 如果 options 中 'legend' 为 True，则显示图例
    if options['legend']:
        plt.legend([h[0] for h in handles], labels, loc='best')
    # phase plot
    #comment: 如果 options 中 'phaseplot' 为 True，则绘制相位图
    if options['phaseplot']:
        #comment: 创建另一个图形窗口，设置大小
        plt.figure(1,[6,3])
        #comment: 初始化 handles 和 labels 列表
        handles = []
        labels  = []
        #comment: 绘制数据相位曲线（转换为角度，并解卷绕）
        handles.append(plt.plot(freq, 180*np.unwrap(np.angle(f)).T/np.pi, 'b'))
        labels.append('Data')
        #comment: 如果 options 中没有 'onlyf' 或者 'onlyf' 为 False，则绘制拟合相位曲线
        if('onlyf' not in options.keys() or not options['onlyf']):
            handles.append(plt.plot(freq, 180*np.unwrap(np.angle(fit)).T/np.pi, 'r--'))
            labels.append('FRVF')
        # plt.xlim(freq[0], freq[-1])
        # plt.xlim(20, 200)
        #comment: 如果 options 中 'logx' 为 True，则设置 x 轴为对数坐标
        if options['logx']:
            plt.xscale('log')
        #comment: 设置 x 轴标签
        plt.xlabel('Frequency [Hz]')
        #comment: 设置 y 轴标签
        plt.ylabel('Phase angle [deg]')
        # plt.title('Approximation of f')
        #comment: 如果 options 中 'legend' 为 True，则显示图例
        if options['legend']:
            plt.legend([h[0] for h in handles], labels, loc='best')
    #comment: 如果 options 中 'block' 为 True，则显示所有图形并阻塞程序
    if options['block']:
        plt.show()
    #comment: 否则，只绘制图形但不阻塞程序
    else:
        plt.draw()


#comment: 定义函数 vectorfit_Z，用于对阻抗或导纳数据进行矢量拟合 (Vector Fitting)
def vectorfit_Z(res, eps, opts0, Type = 'Z'):
    #comment: 根据 Type (Z 或 H) 选择要拟合的矩阵列表和特征值
    if(Type =='Z'):
        matList = res['Z']
        lmd = res['lmd']
    elif(Type =='H'):
        matList = res['H']
        lmd = res['Hlmd']
    #comment: 将频率转换为复频率 s = j*omega
    s = 1j * 2 * math.pi * res['Freq'];
    #comment: 获取权重频率
    weightFreq = res['weightFreq'];
    #comment: 获取第一阶段迭代次数
    Niter1 = opts0['NiterYc1'];
    #comment: 获取第二阶段迭代次数
    Niter2 = opts0['NiterYc2'];
    #comment: 获取拟合极点数量 N
    N = opts0['NpYc'];
    #comment: 获取是否可视化拟合过程的选项
    plot = opts0['ViewYcVF']
    #comment: 复制 vfopts 配置，防止修改原始字典
    opts = opts0['vfopts'].copy()

    #comment: 获取矩阵的列数 Nc 和采样点数 Ns
    Nc = res['Nc']
    Ns = res['Ns']
    #comment: 初始化 tell 为 -1
    tell = -1;
    #comment: 初始化拟合数据 f，大小为 (Nc*Nc) x Ns，用于将矩阵展平为向量
    f = np.zeros((Nc * Nc, Ns),dtype=complex);

    # flag = []
    
    #comment: 遍历矩阵的每个元素，并将其展平到 f 中
    for col in range(Nc):
        for row in range(Nc):
            tell = tell+1;
            for k in range(Ns):
                f[tell, k] = matList[k][row, col]; # stacking elements into a single vector

                # if(cmath.isnan(f[tell, k]) or cmath.isinf(f[tell, k])):
                #     flag.append([k, col, row, N])

    #Complex starting poles:
    #comment: 将复频率 s 转换为实数频率 w
    w = s/1j;
    #comment: 计算频率 Hertz
    freqs = s.imag/2/math.pi;
    
    #comment: 计算复共轭极点对的数量 Ncpx
    Ncpx = math.floor(N/2);
    #comment: 根据极点数量 N 的奇偶性生成初始极点
    if(N == 2*Ncpx):
        #comment: 如果 N 是偶数，生成 Ncpx 对复共轭极点
        bet = np.linspace(np.log10(w[0]), np.log10(w[-1]), Ncpx);
        alf = -bet * 1.0e-2
        poles = np.concatenate(((alf-1j*bet)[:,nax],(alf+1j*bet)[:,nax]), axis=1).flatten()
        print(poles)
    else:
        #comment: 如果 N 是奇数，生成 Ncpx 对复共轭极点和一个实极点
        bet = np.linspace(np.log10(w[0]), np.log10(w[-1]), Ncpx+1);
        alf = -bet * 1.0e-2
        polestemp = np.concatenate(((alf-1j*bet)[:,nax],(alf+1j*bet)[:,nax]), axis=1).flatten()
        poles = polestemp[0:-1];
        poles[-1] = 2 * poles[-1].real;
        
    # weight = 1/(np.float_power(np.abs(f),0)+weight_eps);
    # for i in range(weight.shape[0]):
    #     weight[i,:] = weight[i,:] * weightFreq;
    
    #comment: 设置权重矩阵，这里直接使用 weightFreq
    weight = weightFreq[nax,:];
        

    #Forming(weighted) column sum:
    
    #comment: 初始化 g 矩阵
    g = np.zeros((Nc,Ns),dtype=complex);
    #comment: 遍历矩阵的列，将特征值 lmd 填充到 g 中 (疑似计算对角线或某个特定列作为拟合目标)
    for col in range(Nc):
        for k in range(Ns):
            # g[0,k] = np.trace(matList[k]) #comment: 注释掉的原始代码，可能用于计算迹
            g[col,k] = lmd[k][col] #comment: 使用特征值 lmd 作为拟合目标

            # g[0,k] = np.sum(matList[k]) #comment: 注释掉的原始代码，可能用于计算和
    #comment: 权重 g，直接使用 weightFreq
    weight_g = weightFreq[nax,:];

    #comment: 设置 vectfit3 的选项
    opts['skip_res'] = True; #comment: 跳过残差计算 (在第一阶段)
    # opts['skip_res'] = False;
    opts['spy2'] = False; #comment: 关闭 spy 绘图
    opts['asymp'] = 2; #comment: 设置渐近线数量 (D 和 E 项)
    #comment: 执行第一阶段矢量拟合迭代
    for iter in range(Niter1):
        [SER, poles, rmserr, fit] = vectfit3(g, s, poles, weight_g, opts);

    #comment: 调用 mor_single 进行模型降阶 (可能用于精炼极点)
    [SER, poles, rmserr , fit] = mor_single(poles, 1, np.zeros((N)), s, g, weight_g, eps)

    #comment: 重新设置 vectfit3 选项，再次执行第一阶段矢量拟合
    opts['skip_res'] = True;
    opts['spy2'] = False;
    for iter in range(Niter1):
        [SER, poles, rmserr, fit] = vectfit3(g, s, poles, weight_g, opts);

    #comment: 调整 vectfit3 选项，执行最终的拟合 (跳过残差计算和极点更新)
    opts['skip_res'] = False; #comment: 计算残差
    opts['skip_pole'] = True; #comment: 跳过极点更新
    [SER, poles, rmserr, fit] = vectfit3(f, s, poles, weight, opts);

        
    #comment: 从 SER 对象中提取 A, B, C, D, E 矩阵
    A = SER['A']; B = SER['B']; C = SER['C']; D = SER['D']; E = SER['E'];
    #comment: 调用 full2full 转换状态空间模型
    SER = full2full(SER);
    #comment: 调用 ss2pr 转换为部分分数形式 (R, a, D, E)
    R,a,D,E = ss2pr(SER,tri = True);

    #comment: 根据 Type 将拟合结果存入 res 字典
    if(Type =='Z'):
        res['RYc'] = R;
        res['PYc'] = a;
        res['CYc'] = D;
        res['EYc'] = E;
        res['fitYc'] = fit;
        res['RMSErrYc'] = rmserr;
    elif(Type =='H'):
        res['RH'] = R;
        res['PH'] = a;
        res['CH'] = D;
        res['EH'] = E;
        res['fitH'] = fit;
        res['RMSErrH'] = rmserr;
    
    
    #comment: 返回更新后的 res 字典
    return res


#comment: 定义函数 mor_single，可能用于单输入单输出 (SISO) 系统的模型降阶或残差计算
def mor_single(poles, asymp, delay, s, f, weight, eps):
    # poles: N
    # asymp: 0 - not D, E; 1 - only D; 2 - D and E
    # delay: N
    # s: Ns
    # f: Ns
    # weight: 1*Ns

    #comment: 获取极点数量 N
    N = len(poles);
    #comment: 获取采样点数量 Ns
    Ns = len(s);
    #comment: 获取函数 f 的列数 Nc
    Nc = f.shape[0]
    #comment: 初始化 cindex 数组，用于标记极点类型 (实极点、复共轭对的第一部分、复共轭对的第二部分)
    cindex = np.zeros((N), dtype=np.int_);
    #comment: 初始化计数器 m
    m = 0;
    #comment: 遍历极点，识别复共轭对
    while m < N:
        if poles[m].imag != 0:
            #comment: 如果极点是复数且不是共轭对，则抛出错误
            if poles[m].real!=poles[m+1].real or poles[m].imag!=-poles[m+1].imag:
                raise ValueError('Initial poles '+str(m)+' and '+str(m+1)\
                                 +' are subsequent but not complex conjugate.')
            #comment: 标记复共轭对的两个极点
            cindex[m]   = 1
            cindex[m+1] = 2
            m += 1
        m += 1

    #comment: 初始化 Dk 矩阵 (基函数矩阵)
    Dk = np.empty((Ns,N+asymp),dtype = complex);
    #comment: 初始化 A 矩阵 (用于线性最小二乘问题)
    A = np.zeros((2 * Ns,N+asymp));
    #comment: 遍历极点，填充 Dk 矩阵
    for m in range(N):
        if cindex[m]==0: # real pole #comment: 如果是实极点
            Dk[:,m] =  np.exp( - delay[m] * s ) / (s-poles[m])
        elif cindex[m]==1: # complex pole pair, 1st part #comment: 如果是复共轭对的第一部分
            Dk[:,m]   =  np.exp( - delay[m] * s )*(1/(s-poles[m]) +  1/(s-np.conj(poles[m])))
            Dk[:,m+1] = np.exp( - delay[m] * s ) * (1j/(s-poles[m]) - 1j/(s-np.conj(poles[m])))
    #comment: 如果有渐近项 (D 或 E)
    if asymp>0:
        Dk[:,N] = 1 #comment: D 项对应的基函数 (常数项)
        if asymp==2:
            Dk[:,N+1] = s #comment: E 项对应的基函数 (s 项)

    #comment: 填充 A 矩阵的实部和虚部，并乘以权重
    A[:Ns,:] = weight[0,:,nax] * Dk.real
    A[Ns:,:] = weight[0,:,nax] * Dk.imag
    #comment: 初始化 B 矩阵
    B = np.empty((2*Ns,Nc))
    #comment: 填充 B 矩阵的实部和虚部，并乘以权重
    B[:Ns,:] = weight[0,:,nax] * f.real.T
    B[Ns:,:] = weight[0,:,nax] * f.imag.T

    # solve the linear system
    #comment: 对 A 矩阵进行列归一化，以改善数值稳定性
    Escale = np.linalg.norm(A, axis=0)
    A /= Escale[nax,:]

    #comment: 对 A 矩阵进行奇异值分解 (SVD)
    U, S, V = lg.svd(A, full_matrices =False);

    temp = 0;
    rnk = len(S);
    #comment: 根据 eps 阈值对奇异值进行"截断"，以确定有效秩 rnk
    for i in range(len(S)):
        if(abs(S[-i]) + temp < eps * abs(S[0])):
            temp += abs(S[-i]);
            S[-i] = 0;
            rnk -= 1;

    #comment: 重构 A 矩阵，这里使用了 SVD 结果，可能用于检查
    a1 = U@np.diag(S)@V

    # c = lg.lstsq(a1,B,rcond=-1)[0] #comment: 原始使用 np.linalg.lstsq 的代码 (注释掉)

    #comment: 初始化解向量 sol
    sol = np.zeros((N+asymp,Nc))
    
    #comment: 根据 cindex 和秩 rnk 确定要保留的极点索引 nz
    nz = [];
    temp = 0;
    for i in range(N):
        if ((cindex[i] == 2) and (temp + 2 <= rnk)): #comment: 如果是复共轭对的第二部分且秩允许
            temp += 2;
            nz.append(i-1); #comment: 添加第一和第二部分极点
            nz.append(i);
    for i in range(N):
        if ((temp+1 <= rnk) and ((cindex[i] == 0) or (cindex[i] == 1)) and (i not in nz) ): #comment: 如果是实极点或复共轭对的第一部分且秩允许，并且未被添加
            temp += 1;
            nz.append(i);

    #comment: 将 nz 转换为 numpy 数组
    nz = np.array(nz,dtype = int);

    #comment: 对 A 矩阵的选定列进行最小二乘求解
    sol1 = lg.lstsq(a1[:, nz], B, rcond=-1)[0]
    #comment: 打印 sol1 (调试用)
    print(sol1)
    #comment: 将求解结果填充回 sol
    sol[nz,:] = sol1;
    #comment: 对 sol 恢复原始尺度 (乘以 Escale)
    sol /= Escale[:,nax]

    #comment: 对 nz 进行排序
    idx = nz[np.argsort(nz)]
    
    #comment: 初始化 SERC 矩阵
    SERC = np.empty((Nc,N), dtype=np.complex_)
    #comment: 初始化新的极点列表 poles_new
    poles_new = np.array([], dtype = complex)
    #comment: 遍历极点，计算新的残差 SERC 并更新 poles_new
    for m in range(N):

        if cindex[m]==0: #comment: 实极点
            SERC[:,m] = sol[m,:]
        if cindex[m]==1 and ((m+1) in idx): #comment: 复共轭对的第一部分，且第二部分在索引中
            SERC[:,m]   = sol[m,:] + 1j*sol[m+1,:]
            SERC[:,m+1] = sol[m,:] - 1j*sol[m+1,:]
        elif cindex[m]==1: #comment: 复共轭对的第一部分，但第二部分不在索引中 (可能不完整)
            SERC[:,m]  = sol[m,:];
            SERC[:,m+1]  = sol[m,:];

        # if cindex[m]==2 and (m in idx) and ((m-1) not in idx):
        #     idx = np.append(idx, m - 1)

        if cindex[m]==1 and (m in idx) and ((m+1) not in idx): #comment: 如果是复共轭对第一部分，且在索引中，但第二部分不在索引中
            # idx = np.append(idx, m + 1)
            poles_new = np.append(poles_new, poles[m].real) #comment: 添加实部作为极点
        elif m in idx: #comment: 如果在索引中
            poles_new = np.append(poles_new, poles[m]) #comment: 添加原始极点


    #comment: 再次对 idx 进行排序
    idx = idx[np.argsort(idx)]

    
    #comment: 分离出与极点相关的索引 idxc、D 项相关的索引 idxd、E 项相关的索引 idxe
    idxc = np.delete(idx, idx >= N )
    idxd = idx[idx==N]
    idxe = idx[idx==N+1]
    
    # poles_new = poles[idxc];

    #comment: 获取新的残差 c_new
    c_new = SERC[:, idxc];
    #comment: 初始化 D, E 项
    d_new = 0;
    e_new = 0;
    #comment: 如果 D 项的索引存在，则从 sol 中获取 d_new
    if(idxd.size!=0):
        d_new = sol[N,:];
    #comment: 如果 E 项的索引存在，则从 sol 中获取 e_new
    if(idxe.size!=0):
        e_new = sol[N+1,:];
    
    #comment: 构建 SER 字典 (状态空间模型或部分分数模型)
    SER = {}
    SER['D'] = None
    SER['E'] = None
    SER['C'] = c_new
    SER['B'] = np.ones((len(poles_new)))
    #comment: 根据 asymp 参数设置 D 和 E 项
    if asymp>0:
        SER['D'] = d_new
        if asymp==2:
            SER['E'] = e_new

    #comment: 计算拟合结果 fit
    fit = np.dot(c_new, np.exp( - delay[idxc][:,nax] * s[nax,:] ) * (1/(s[nax,:]-poles_new[:,nax])))
    #comment: 如果有 D 或 E 项，则添加到 fit 中
    if asymp>0:
        fit += SER['D']
        if asymp==2:
            fit += s[nax,:] * SER['E']
    #comment: 计算均方根误差 (RMSErr)
    rmserr = np.sqrt(np.sum(np.abs(fit-f)**2)) / np.sqrt(Ns) # 均方根差
    #comment: 设置 SER 的 A 项 (极点构成的对角矩阵)
    SER['A'] = np.diag(poles_new)

    #comment: 返回 SER 对象, 新的极点, 均方根误差 和 拟合结果
    return SER, poles_new, rmserr, fit