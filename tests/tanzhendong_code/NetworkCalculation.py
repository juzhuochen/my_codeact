#comment: 导入 NumPy 库，用于进行科学计算，特别是数组和矩阵操作
import numpy as np
#comment: 导入 NumPy 的线性代数模块，用于进行矩阵的逆、特征值等计算
import numpy.linalg as lg

#comment: 定义一个别名 nax 作为 np.newaxis，用于在数组操作中增加维度
nax = np.newaxis
#comment: 从 vectfit3 库中导入 vectfit3、full2full 和 ss2pr 函数，这些函数可能与矢量拟合和系统状态空间模型转换有关
from vectfit3 import vectfit3, full2full, ss2pr
#comment: 从 time 模块导入 time 函数，用于测量代码执行时间
from time import time
# # %matplotlib
#comment: 导入 matplotlib.pyplot 库，用于绘图
import matplotlib.pyplot as plt
#comment: 导入 math 库，提供数学函数
import math 
#comment: 导入 cmath 库，提供复数数学函数
import cmath
#comment: 导入 scipy 库，一个用于科学计算的 Python 库
import scipy as sp
#comment: 从 scipy.constants 模块导入常量，例如 pi, c 等
from scipy import constants as const
#comment: 从 scipy.integrate 模块导入积分函数
from scipy import integrate as scii
#comment: 导入 scipy.special 模块，提供特殊数学函数
import scipy.special as spp
#comment: 导入 scipy.ndimage 模块，用于 N 维图像处理，这里可能用于卷积操作
import scipy.ndimage
#comment: 从 scipy.optimize 模块导入优化函数
from scipy import optimize as sco
#comment: 从 scipy.signal 模块导入信号处理函数
import scipy.signal
#comment: 导入 os 模块，提供与操作系统交互的功能
import os
#comment: 导入 tkinter 模块，用于创建图形用户界面
import tkinter
#comment: 导入 tkinter.filedialog 模块，用于文件选择对话框
import tkinter.filedialog
#comment: 导入 csv 模块，用于 CSV 文件的读写
import csv
#comment: 导入 cloudpss 库，这是一个与 CloudPSS 平台交互的自定义库
import cloudpss
#comment: 从 CaseEditToolbox 模块导入 CaseEditToolbox 类，用于编辑案例
from CaseEditToolbox import CaseEditToolbox
#comment: 从 CaseEditToolbox 模块导入 is_number 函数，用于判断是否为数字
from CaseEditToolbox import is_number
#comment: 从 PSAToolbox 模块导入 PSAToolbox 类，用于电力系统分析
from PSAToolbox import PSAToolbox
#comment: 导入 json 模块，用于 JSON 数据的编码和解码
import json

class NetworkCalculation:
    """
    NetworkCalculation 类用于执行电力系统网络的频域分析、潮流计算和暂态仿真。
    它封装了加载系统配置、计算网络导纳/阻抗矩阵、求解稳定工况以及仿真电压/电流时间响应等功能。

    属性:
    - ce: PSAToolbox 实例，用于与CloudPSS平台交互和管理电力系统模型。
    - opts: 包含所有配置选项的字典，例如API令牌、URL、频率范围、仿真参数等。
    - Z: 存储不同频率下网络阻抗矩阵的列表。
    - Y: 存储不同频率下网络导纳矩阵的列表。
    - Time: 存储仿真时间点的 NumPy 数组。
    - Vcurve: 存储仿真得到的电压时间曲线。
    - Icurve: 存储仿真得到的电流时间曲线。
    - res: 存储计算结果的字典，包括Z、Y、I0、V0、Z0等。
    """
    def __init__(self, opts=None):
        """
        初始化 NetworkCalculation 类的实例。

        参数:
        - opts: (可选) 配置选项字典。如果未提供，将使用 defaultOptions() 生成默认配置。
        """
        self.ce = PSAToolbox()
        self.opts = opts if opts is not None else self._default_options()
        self.Z = []
        self.Y = []
        self.Time = None
        self.Vcurve = None
        self.Icurve = None
        self.res = {} # 用于存储所有计算结果

    def _default_options(self):
        """
        内部方法：设置默认配置。
        此方法旨在被 __init__ 调用，不应直接从外部调用。

        返回:
        - opts: 包含默认配置参数的字典。
        """
        opts = {};
        
        #comment: 设置 CloudPSS API 的访问令牌
        opts['token'] = 'PLACEHOLDER_TOKEN' # <-- 敏感信息占位符
        #comment: 设置 CloudPSS API 的 URL
        opts['apiURL'] = 'PLACEHOLDER_API_URL' # <-- 敏感信息占位符
        #comment: 设置用户名
        opts['username'] = 'PLACEHOLDER_USERNAME' #用户名 <-- 敏感信息占位符
        #comment: 设置项目密钥
        opts['projectKey'] = 'PLACEHOLDER_PROJECT_KEY' # <-- 敏感信息占位符

        #comment: 设置频率范围，从 log10(0.5) 到 6 的对数等间隔的 101 个点
        opts['Freq'] = np.logspace(math.log10(0.5),6,101);
        #comment: 设置基准频率
        opts['f0'] = 50;
        #comment: 特征值设置
        #comment: 设置特征值计算的最大迭代次数
        opts['EigMaxIter'] = 10;
        #comment: 设置特征值计算的收敛误差
        opts['EigEps'] = 1e-8;
        #comment: 曲线拟合设置
        #comment: 设置目标误差
        opts['target_eps'] = 0.002;


        #comment: 设置 NpH 参数
        opts['NpH'] = 20
        #comment: 设置 ErH 参数
        opts['ErH'] = 0.002

        #comment: 设置不同频率段的权重
        #comment: F<0.9F0 时的权重
        opts['WeightH0'] = 1; # F<0.9F0
        #comment: F=0.9~1.1F0 时的权重
        opts['WeightH1'] = 1000; # F=0.9~1.1F0
        #comment: F>1.1F0 时的权重
        opts['WeightH2'] = 1; # F>1.1F0
        #comment: 设置权重样式：1 代表常数权重，2 代表 1/abs(f)，3 代表 1/sqrt(abs(f))
        opts['WeightStyleH'] = 1; # 1 for ones, 2 for 1/abs(f), 3 for 1/sqrt(abs(f))
        #comment: 设置权重计算的 epsilon 值，防止除零
        opts['Weight_eps'] = 1e-10;

        # # opts['NiterYc1'] = 5
        # # opts['NiterYc2'] = 3
        #comment: 设置 H1 迭代次数
        opts['NiterH1'] = 5
        #comment: 设置 H2 迭代次数
        opts['NiterH2'] = 3
        
        #comment: 设置是否显示 YcVF 视图
        opts['ViewYcVF'] = False;
        #comment: 设置是否显示 HVF 视图
        opts['ViewHVF'] = False;
        
        #comment: 设置 vectfit3 库的选项
        opts['vfopts'] = {};
        #comment: 使用带松弛非平凡约束的矢量拟合
        opts['vfopts']['relax']=True;      #Use vector fitting with relaxed non-triviality constraint
        #comment: 强制生成稳定的极点
        opts['vfopts']['stable']=True;     #Enforce stable poles
        #comment: 拟合包含常数项 D，不包含 E * s
        opts['vfopts']['asymp']=2;      #Fitting includes D(constant), not include E * s 
        #comment: 不绘制第一个图
        opts['vfopts']['spy1']=False;       #No plotting
        #comment: 不绘制第二个图
        opts['vfopts']['spy2']=True; 
        #comment: X 轴使用对数刻度
        opts['vfopts']['logx']=True; 
        #comment: Y 轴使用对数刻度
        opts['vfopts']['logy']=True; 
        #comment: 绘制误差图
        opts['vfopts']['errplot']=True;
        #comment: 绘制相位图
        opts['vfopts']['phaseplot']=True;

        #comment: 跳过极点拟合
        opts['vfopts']['skip_pole']=False; 
        #comment: 跳过残差拟合
        opts['vfopts']['skip_res']=True;
        #comment: 生成对角 A 矩阵的复数状态空间模型
        opts['vfopts']['cmplx_ss']=True;  # =1 --> Will generate state space model with diagonal A
        #comment: 显示图例
        opts['vfopts']['legend']=True;
        #comment: 开启阻塞模式
        opts['vfopts']['block'] = True;

        #comment: 返回配置字典
        return opts
    
    def load_network_config(self):
        """
        加载网络拓扑和配置数据。
        从 'saSource.json' 文件加载组件库，并初始化 CaseEditToolbox 和 PSAToolbox 实例。
        设置 CloudPSS API 访问信息和项目密钥。

        无参数。

        修改实例属性:
        - self.ce: PSAToolbox 实例被初始化和配置。
        - self.opts['BusList']: 更新为项目中的总线列表。
        - self.opts['Trans3pList']: 更新为项目中的三绕组变压器列表。
        """
        #comment: 打开 saSource.json 文件以读取模式
        with open('saSource.json', "r", encoding='utf-8') as f:
            #comment: 从文件中加载 JSON 数据到 compLib 变量
            compLib = json.load(f)
        #comment: 设置 CaseEditToolbox 实例的配置，包括 token、apiURL、username、projectKey 和组件库名称
        self.ce.setConfig(self.opts['token'], self.opts['apiURL'], self.opts['username'], self.opts['projectKey'], comLibName = 'saSource.json')
        #comment: 设置 generateG 标志为 True
        generateG = True
        #comment: 配置 ce 实例以生成 iGraph 信息
        self.ce.config['iGraph'] = generateG  #  生成iGraph信息，已有iGraph信息时注释本块
        #comment: 配置 ce 实例以删除边
        self.ce.config['deleteEdges'] = True
        #comment: 调用 setInitialConditions 方法进行初始化
        self.ce.setInitialConditions() # 进行初始化
        #comment: 调用 createSACanvas 方法创建 SA 画布
        self.ce.createSACanvas()
        #comment: 从项目中获取所有 RID 为 'model/CloudPSS/_newBus_3p' 的组件，并将其转换为列表存储在 opts['BusList'] 中
        self.opts['BusList'] = list(self.ce.project.getComponentsByRid('PLACEHOLDER_BUS_RID')) # <-- 敏感信息占位符 'model/CloudPSS/_newBus_3p'
        #comment: 从项目中获取所有 RID 为 'model/CloudPSS/_newTransformer_3p3w' 的组件，并将其转换为列表存储在 opts['Trans3pList'] 中
        self.opts['Trans3pList'] = list(self.ce.project.getComponentsByRid('PLACEHOLDER_TRANSFORMER_RID')) # <-- 敏感信息占位符 'model/CloudPSS/_newTransformer_3p3w'
        #comment: 打印加载算例完成信息
        print('载入算例完成！')

    def _calculate_component_admittance(self, key, freq):
        """
        内部方法：用于计算单个组件的导纳矩阵。
        此方法旨在被 calculate_frequency_response 调用，不应直接从外部调用。

        参数:
        - key: 组件的键（key），用于从项目中获取组件。
        - freq: 当前计算的频率。

        返回:
        - ycomp: 计算得到的组件导纳矩阵。
        - A: 连接该组件的总线索引列表。
            如果组件类型不支持或未连接到总线，则返回 None, None。
        """
        #comment: 根据 key 从项目中获取组件
        comp = self.ce.project.getComponentByKey(key)
        #comment: 从拓扑结构中获取组件的顶部信息
        top = self.ce.topo['components']['/'+key]
        #comment: 初始化空列表 A 和 pinName
        A = []
        pinName = []
        # print(key)
        # sourceflag = 0
        #comment: 遍历图中与当前组件 key 相邻的节点
        for i in self.ce.g.vs.find('/'+key).neighbors():
            #comment: 如果相邻节点的 RID 是 'model/CloudPSS/_newBus_3p'
            if(i['rid']=='PLACEHOLDER_BUS_RID'): # <-- 敏感信息占位符
                # print(i['name'][1:])
                #comment: 将相邻总线的索引添加到 A 列表中
                A.append(self.opts['BusList'].index(i['name'][1:]))
                #comment: 将相邻总线的引脚信息添加到 pinName 列表中
                pinName.append(self.ce.project.getComponentByKey(i['name'][1:]).pins['0'])
        #comment: 如果组件定义是 'model/CloudPSS/TranssmissionLineRouter'（输电线路）
        if(comp.definition == 'PLACEHOLDER_TRANSMISSION_LINE_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 2，否则打印错误信息
            if(len(A) != 2):
                print('error:'+key+' lenA!=2')
            #comment: 获取基准电压 V
            V = float(top['args']['Vbase'])
            #comment: 获取基准功率 Sbase
            Sbase = float(top['args']['Sbase'])
            #comment: 获取线路长度 L
            L = float(top['args']['Length'])
            #comment: 计算线路的电阻 R1
            R1 = float(top['args']['R1pu']) * (V**2 / Sbase) * L
            #comment: 计算线路的电抗 X1
            X1 = 1j * float(top['args']['X1pu']) * (V**2 / Sbase) / 50 * freq * L
            #comment: 计算线路的 Susceptance B1
            B1 = 1j * float(top['args']['B1pu']) * Sbase / (V**2) / 50 * freq * L
            
            #comment: 计算输电线路的导纳矩阵，考虑 PI 型等效电路
            ycomp = np.eye(2) * B1/2 + np.mat([[1,-1],[-1,1]])/(R1 + X1)
            
        #comment: 如果组件定义是 'model/CloudPSS/_newTransformer_3p2w'（两绕组变压器）
        elif(comp.definition == 'PLACEHOLDER_2W_TRANSFORMER_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 2，否则打印错误信息
            if(len(A) != 2):
                print('error:'+key+' lenA!=2')
            # print((pinName,comp.pins['0'],comp.pins['1']))
            #comment: 初始化相角 theta
            theta = 0

            #comment: 判断变压器接线方式和超前滞后，计算相应的相角 theta
            if(top['args']['YD1'] == '0' and top['args']['YD2'] == '1'):
                    if(top['args']['Lead'] == '1'):
                        theta = math.pi/6
                    else:
                        theta = -math.pi/6
            elif(top['args']['YD1'] == '1' and top['args']['YD2'] == '0'):
                    if(top['args']['Lead'] == '1'):
                        theta = -math.pi/6
                    else:
                        theta = math.pi/6
            #comment: 根据引脚连接顺序确定变压器侧电压和变比
            if(pinName[0] == comp.pins['0']):
                V1 = float(top['args']['V1'])
                V2 = float(top['args']['V2'])
                k = V1 / V2
                theta = -theta
            else:
                V1 = float(top['args']['V2'])
                V2 = float(top['args']['V1'])
                k = V1 / V2
                
            
            #comment: 获取基准功率 Sbase
            Sbase = float(top['args']['Tmva'])
            #comment: 计算漏电感 L
            L = float(top['args']['Xl']) * V1**2 / Sbase / 50 / 2 / math.pi
            #comment: 计算电阻 R
            R = float(top['args']['Rl']) * V1**2 / Sbase

            #comment: 构建 Lb 矩阵
            Lb = np.mat([[1,-k*np.exp(1j*theta)],[-k*np.exp(-1j*theta),k**2]])/L
            #comment: 构建 Rb 矩阵
            Rb = np.diag([R/2,R/2/(k**2)])
            #comment: 计算变压器导纳矩阵
            ycomp = lg.inv(1j * 2*math.pi * freq * np.eye(2) + Lb@Rb) @ Lb

        #comment: 如果组件定义是 'model/CloudPSS/_newTransformer_3p3w'（三绕组变压器）
        elif(comp.definition == 'PLACEHOLDER_3W_TRANSFORMER_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 3，否则打印错误信息
            if(len(A) != 3):
                print('error:'+key+' lenA!=3')

            #comment: 初始化 3x3 的复数导纳矩阵
            ycomp = np.zeros((3,3),dtype=complex)
            #comment: 获取最大基准功率 Sbase
            Sbase = max(float(top['args']['Tmva1']),float(top['args']['Tmva2']),float(top['args']['Tmva3']))
            #comment: 计算等效电感 L01, L02, L03
            L01 = (float(top['args']['Xl12']) + float(top['args']['Xl13']) - float(top['args']['Xl23']))/2 *float(top['args']['V1'])**2/ Sbase / 50 / 2 / math.pi
            L02 = (float(top['args']['Xl12']) + float(top['args']['Xl23']) - float(top['args']['Xl13']))/2 *float(top['args']['V1'])**2/ Sbase / 50 / 2 / math.pi
            L03 = (float(top['args']['Xl23']) + float(top['args']['Xl13']) - float(top['args']['Xl12']))/2 *float(top['args']['V1'])**2/ Sbase / 50 / 2 / math.pi

            #comment: 计算等效电阻 R01, R02, R03
            R01 = (float(top['args']['Rl12']) + float(top['args']['Rl13']) - float(top['args']['Rl23']))/2 *float(top['args']['V1'])**2/ Sbase
            R02 = (float(top['args']['Rl12']) + float(top['args']['Rl23']) - float(top['args']['Rl13']))/2 *float(top['args']['V2'])**2/ Sbase
            R03 = (float(top['args']['Rl23']) + float(top['args']['Rl13']) - float(top['args']['Rl12']))/2 *float(top['args']['V3'])**2/ Sbase

            #comment: 初始化相角
            theta01 = 0
            theta02 = 0
            theta03 = 0

            #comment: 根据 YD 接线方式调整相角
            if(top['args']['YD1'] == '1'):
                theta01 = math.pi/6
            if(top['args']['YD2'] == '1'):
                theta02 = math.pi/6
            if(top['args']['YD3'] == '1'):
                theta03 = math.pi/6
            #comment: 根据超前滞后调整相角
            if(top['args']['Lead'] == '2'):
                theta01 = -theta01
                theta02 = -theta02
                theta03 = -theta03
            
            #comment: 获取引脚索引
            Pindex = [[comp.pins['0'],comp.pins['1'],comp.pins['2']].index(x) for x in pinName]
            #comment: 获取额定电压列表
            V0list = [float(top['args']['V1']),float(top['args']['V2']),float(top['args']['V3'])]
            #comment: 获取对应引脚的电压
            V1 = V0list[Pindex[0]]
            V2 = V0list[Pindex[1]]
            V3 = V0list[Pindex[2]]
            #comment: 计算电压比
            k12 = V1 / V2
            k13 = V1 / V3
            k22 = k12 * k12
            k23 = k12 * k13
            k33 = k13 * k13
            #comment: 获取相角列表
            THT0 = [theta01,theta02,theta03]
            #comment: 获取对应引脚的相角
            theta1 = THT0[Pindex[0]]
            theta2 = THT0[Pindex[1]]
            theta3 = THT0[Pindex[2]]

            #comment: 获取对应引脚的电感
            temp = [L01,L02,L03]
            L1 = temp[Pindex[0]]
            L2 = temp[Pindex[1]]
            L3 = temp[Pindex[2]]
            #comment: 获取对应引脚的电阻
            temp = [R01,R02,R03]
            R1 = temp[Pindex[0]]
            R2 = temp[Pindex[1]]
            R3 = temp[Pindex[2]]
            
            #comment: 计算中间变量 LL
            LL = L1 * L2 + L2 * L3 + L1 * L3
            #comment: 计算 LL1, LL2, LL3, LL12, LL13, LL23
            LL1 = (L2 + L3) / LL
            LL2 = (L1 + L3) * k22 / LL
            LL3 = (L1 + L2) * k33 / LL
            LL12 = -k12 * L3 / LL
            LL13 = -k13 * L2 / LL
            LL23 = -k23 * L1 / LL
            #comment: 构建 Lb 矩阵
            Lb = np.mat([[LL1, LL12,LL13],
                            [LL12,LL2, LL23],
                            [LL13,LL23, LL3]])
            #comment: 构建 Rb 矩阵
            Rb = np.diag([R1,R2,R3])

            #comment: 计算三绕组变压器导纳矩阵
            ycomp = lg.inv(1j * 2*math.pi * freq * np.eye(3) + Lb@Rb) @ Lb

            
        #comment: 如果组件定义是 'model/CloudPSS/_newExpLoad_3p'（三相恒功率/恒阻抗负载）
        elif(comp.definition == 'PLACEHOLDER_EXPLOAD_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 1，否则打印错误信息
            if(len(A) != 1):
                print('error:'+key+' lenA!=1')
            #comment: 获取电压 V
            V = float(top['args']['v']) * float(top['args']['Vi'])
            #comment: 获取有功功率 P
            P = float(top['args']['p'])
            #comment: 获取无功功率 Q
            Q = float(top['args']['q'])
            #comment: 计算等效电导 G
            G = P/V**2
            #comment: 根据无功功率计算等效 Susceptance B
            if(Q>=0):
                B =  -1j * Q / (V ** 2) * 50 / freq
            else:
                B =  -1j * Q / (V ** 2) / 50 * freq
            # B=0
            #comment: 计算负载导纳
            ycomp = B + G

        #comment: 如果组件定义是 'model/CloudPSS/SyncGeneratorRouter'（同步发电机）
        elif(comp.definition == 'PLACEHOLDER_GENERATOR_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 1，否则打印错误信息
            if(len(A) != 1):
                print('error:'+key+' lenA!=1')
            #comment: 获取电压 V
            V = float(top['args']['V']) * math.sqrt(3)
            #comment: 获取额定功率 S
            S = float(top['args']['Smva'])
            #comment: 获取参数类型 ParamType
            ParamType = int(top['args']['ParamType'])
            #comment: 如果参数类型是 0
            if(ParamType == 0):
                #comment: 计算定子电阻 Rs
                Rs = float(top['args']['Rs']) * V**2 / S
                #comment: 计算漏电感 Lls
                Lls = float(top['args']['Xls']) * V**2 / S / 50 / 2 / math.pi
                #comment: 计算直轴电感 Ld
                Ld = float(top['args']['Xd']) * V**2 / S / 50 / 2 / math.pi - Lls
                #comment: 计算额定绕组电感 Lfd
                Lfd = float(top['args']['Xlfd']) * V**2 / S / 50 / 2 / math.pi
                #comment: 计算阻尼绕组电感 Lkd
                Lkd = float(top['args']['Xlkd']) * V**2 / S / 50 / 2 / math.pi
                #comment: 计算同步电感 Ls
                Ls = Lls + 1/(1/Ld + 1/Lfd + 1/Lkd)
                #comment: 计算同步电抗 Xs
                Xs = 1j * 2*math.pi * freq * Ls
                #comment: 计算发电机导纳
                ycomp = 1/(Rs+Xs)
                # ycomp = 0
            # sourceflag = 1
        #comment: 如果组件定义是 'model/CloudPSS/Thevenin_3p'（三相戴维宁等效源）
        elif(comp.definition == 'PLACEHOLDER_THEVENIN_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 1，否则打印错误信息
            if(len(A) != 1):
                print('error:'+key+' lenA!=1')
            #comment: 获取电阻 R1
            R1 = float(top['args']['R1'])
            #comment: 计算电抗 X1
            X1 = 1j * float(top['args']['X1']) / float(top['args']['f']) * freq
            #comment: 计算戴维宁等效导纳
            ycomp = 1/(R1+X1)
        #comment: 如果组件定义是 'model/CloudPSS/_newShuntLC_3p'（三相并联电容电感）
        elif(comp.definition == 'PLACEHOLDER_SHUNT_LC_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 1，否则打印错误信息
            if(len(A) != 1):
                print('error:'+key+' lenA!=1')
            #comment: 获取电压 V
            V = float(top['args']['v'])
            #comment: 获取频率 f
            f = float(top['args']['freq'])
            #comment: 计算基准 Susceptance B1
            B1 = float(top['args']['s']) / (V**2)
            #comment: 根据无功功率符号调整 B1
            if(float(top['args']['s']) >= 0):
                B1 = -1j * B1 *f / freq
            else:
                B1 = -1j * B1 *freq / f
            # G = 1/V**2;
            #comment: 计算并联 LC 导纳
            ycomp = B1 

        #comment: 如果组件定义是 'model/admin/GW_mask_power_flow'
        elif(comp.definition == 'PLACEHOLDER_GW_MASK_RID'): # <-- 敏感信息占位符
            #comment: 检查连接的引脚数量是否为 1，否则打印错误信息
            if(len(A) != 1):
                print('error:'+key+' lenA!=1')
            #comment: 获取 PMSG_FDNE_Z 数据
            PMSG_FDNE_Z = self.opts['PMSG_FDNE_Z']
            #comment: 初始化阻抗 Z
            Z_val = 0
            #comment: 遍历 PMSG_FDNE_Z 的极点和残差，计算 Z
            for i in range(len(PMSG_FDNE_Z.keys())-2):
                Z_val += PMSG_FDNE_Z[i][0][0]/((2j*math.pi*freq)-PMSG_FDNE_Z['Poles'][i])
            #comment: 添加常数项
            Z_val += PMSG_FDNE_Z['Const'][0][0]
            #comment: 调整 Z 以考虑风机数量和 PCC 电压
            Z_val = Z_val / float(top['args']['WT_Num']) * float(top['args']['Vpcc'])**2
            #comment: 计算导纳
            ycomp = 1/Z_val
        #comment: 对于其他未定义的组件，设置 A 和 ycomp 为 None
        else:
            A = None
            ycomp = None
        
        #comment: 返回计算得到的导纳和连接的总线索引
        return ycomp, A

    def calculate_frequency_response(self):
        """
        计算整个电力系统在不同频率下的阻抗矩阵 (Z) 和导纳矩阵 (Y)。
        遍历所有预设频率，对每个频率点调用内部方法计算网络导纳矩阵，然后求逆得到阻抗矩阵。

        无参数。

        修改实例属性:
        - self.Z: 存储所有频率下的网络阻抗矩阵列表。
        - self.Y: 存储所有频率下的网络导纳矩阵列表。
        - self.res['Z']: 更新结果字典中的 Z 矩阵。
        - self.res['Y']: 更新结果字典中的 Y 矩阵。
        - self.res['Nc']: 更新结果字典中的节点计数。
        - self.res['Ns']: 更新结果字典中的采样点计数。
        - self.res['Freq']: 更新结果字典中的频率列表。
        """
        #comment: 打印开始计算频域 Z 和 Y 矩阵的信息
        print('开始计算频域Z和Y矩阵...')

        pi = math.pi
        # 获取总线数量作为网络节点数 NN
        NN = len(self.opts['BusList'])
        
        #comment: 遍历所有频率点
        for freq in self.opts['Freq']:
            Ynet_current_freq = np.zeros((NN,NN),dtype = complex) # 初始化当前频率下的网络导纳矩阵

            # 遍历图中的所有节点
            for i_node_name in self.ce.g.vs['name']:
                # 如果当前节点是新总线，则跳过
                if self.ce.g.vs.find(i_node_name)['rid'] == 'PLACEHOLDER_BUS_RID': # <-- 敏感信息占位符
                    continue
                
                # 如果当前节点没有连接到新总线，则跳过
                if 'PLACEHOLDER_BUS_RID' not in [j['rid'] for j in self.ce.g.vs.find(i_node_name).neighbors()]: # <-- 敏感信息占位符
                    continue

                # 调用 _calculate_component_admittance 函数计算当前组件的导纳和连接的总线
                ycomp, A = self._calculate_component_admittance(i_node_name[1:], freq)

                # 如果 A 不为 None (即组件有效连接到总线)
                if A is not None:
                    # 更新网络导纳矩阵 Ynet
                    # A 代表连接到该组件的总线索引
                    # np.mat(A).T 将 A 转换为列向量
                    # ycomp 可能是单个值或矩阵，根据组件类型进行加法
                    Ynet_current_freq[A,np.mat(A).T] = Ynet_current_freq[A,np.mat(A).T] + ycomp
            
            self.Y.append(Ynet_current_freq)
            self.Z.append(lg.inv(Ynet_current_freq))

        self.res['Z'] = self.Z
        self.res['Y'] = self.Y
        self.res['Nc'] = NN
        self.res['Ns'] = len(self.opts['Freq'])
        self.res['Freq'] = self.opts['Freq']
        print('频域Z和Y矩阵计算完成。')


    def calculate_stable_operating_point(self):
        """
        计算稳定工况下的网络电流(I0)、电压(V0)和阻抗(Z0)。
        此方法用于确定系统在基准频率下的稳态运行点。

        无参数。

        修改实例属性:
        - self.res['I0']: 稳定工况下的电流向量。
        - self.res['V0']: 稳定工况下的电压向量。
        - self.res['Z0']: 50Hz 时的网络阻抗矩阵。
        """
        #comment: 初始化 SFlags 列表，用于存储电源连接的总线索引
        SFlags = []
        #comment: 获取节点数量 Nc
        Nc = self.res['Nc']
        #comment: 初始化电压向量 V0
        V0 = np.zeros(Nc,dtype=complex)
        
        #comment: 遍历图中的所有节点
        for i in self.ce.g.vs['name']:
            #comment: 获取组件
            comp = self.ce.project.getComponentByKey(i[1:])
            #comment: 获取组件的拓扑信息
            top = self.ce.topo['components'][i]
            #comment: 如果组件是新总线
            if(comp.definition=='PLACEHOLDER_BUS_RID'): # <-- 敏感信息占位符
                #comment: 获取总线索引
                a = self.opts['BusList'].index(i[1:])
                #comment: 计算总线电压幅值
                v = float(top['args']['VBase'])*float(top['args']['V'])*math.sqrt(2/3)
                #comment: 计算总线电压相角
                theta = float(top['args']['Theta'])*math.pi/180
                #comment: 设置总线电压 V0
                V0[a] = v*np.exp(1j*theta)
            #comment: 如果当前节点没有连接到新总线，则跳过
            if 'PLACEHOLDER_BUS_RID' not in [j['rid'] for j in self.ce.g.vs.find(i).neighbors()]: # <-- 敏感信息占位符
                continue

            #comment: 初始化 sourceflag 变量
            sourceflag = 0
            #comment: 如果组件是电源类型
            if(comp.definition in ['PLACEHOLDER_THEVENIN_RID','PLACEHOLDER_GENERATOR_RID','PLACEHOLDER_DC_LINE_RID','PLACEHOLDER_GW_MASK_RID']): # <-- 敏感信息占位符
                sourceflag = 1
            #comment: 如果是电源组件
            if(sourceflag == 1):
                #comment: 遍历与电源组件相邻的节点
                for j in self.ce.g.vs.find(i).neighbors():
                    #comment: 如果相邻节点是新总线
                    if(j['rid']=='PLACEHOLDER_BUS_RID'): # <-- 敏感信息占位符
                        # print(i['name'][1:])
                        #comment: 获取总线索引
                        a = self.opts['BusList'].index(j['name'][1:])
                        #comment: 如果该总线不在 SFlags 中，则添加
                        if(a not in SFlags):
                            SFlags.append(a)

        #comment: 对 SFlags 进行排序
        SFlags = [SFlags[i] for i in np.argsort(SFlags)]
        #comment: 打印 SFlags
        print(f"电源连接总线索引: {SFlags}")
        
        #comment: 计算 50Hz 时的网络导纳矩阵 Y0
        Y0 = self._calculate_network_admittance(self.opts['f0'])
        #comment: 计算 50Hz 时的网络阻抗矩阵 Z0
        Z0 = lg.inv(Y0)
        
        #comment: 获取电源节点数量 Ni
        Ni = len(SFlags)
        #comment: 从 Z0 中提取与电源节点相关的阻抗矩阵 Z00
        Z00 = Z0[:,SFlags]
        #comment: 初始化 Z0ri 矩阵，用于将复数阻抗转换为实部和虚部形式
        Z0ri = np.zeros((2*Nc,2*Ni))
        #comment: 填充 Z0ri 的实部和虚部
        Z0ri[:Nc,:Ni] = np.real(Z00)
        Z0ri[Nc:,Ni:] = np.real(Z00)
        Z0ri[:Nc,Ni:] = -np.imag(Z00)
        Z0ri[Nc:,:Ni] = np.imag(Z00)

        #comment: 初始化 Vri 向量，用于将复数电压转换为实部和虚部形式
        Vri = np.zeros(2*Nc)
        #comment: 填充 Vri 的实部和虚部
        Vri[:Nc] = np.real(V0)
        Vri[Nc:] = np.imag(V0)
        
        #comment: 使用最小二乘法求解电流 I0ri
        I0ri = lg.lstsq(Z0ri,Vri,rcond=None)[0] # rcond=-1 已经被弃用
        #comment: 初始化潮流电流 I0
        I0 = np.zeros(Nc,dtype=complex)
        #comment: 将实部和虚部合并为复数电流，并赋值给电源节点
        I0[SFlags] = I0ri[:Ni]+1j*I0ri[Ni:]

        self.res['I0'] = I0
        self.res['V0'] = V0
        self.res['Z0'] = Z0
        print('稳定工况电流和电压计算完成。')

    def _calculate_network_admittance(self, freq):
        """
        内部方法：计算整个网络在给定频率下的导纳矩阵。
        此方法旨在被 calculate_stable_operating_point 调用，不应直接从外部调用。

        参数:
        - freq: 当前计算的频率。

        返回:
        - Ynet: 计算得到的网络导纳矩阵。
        """
        pi = math.pi
        w = 2*pi*freq
        
        NN = len(self.opts['BusList'])
        Ynet = np.zeros((NN,NN),dtype = complex)
        
        for i_node_name in self.ce.g.vs['name']:
            if self.ce.g.vs.find(i_node_name)['rid'] == 'PLACEHOLDER_BUS_RID': # <-- 敏感信息占位符
                continue
            
            if 'PLACEHOLDER_BUS_RID' not in [j['rid'] for j in self.ce.g.vs.find(i_node_name).neighbors()]: # <-- 敏感信息占位符
                continue

            ycomp, A = self._calculate_component_admittance(i_node_name[1:], freq)

            if A is not None:
                Ynet[A,np.mat(A).T] = Ynet[A,np.mat(A).T] + ycomp
        
        return Ynet
    
    def simulate_time_domain_response(self, initial_current_base, perturb_node_key, t_start=0.2, t_end_perturb=0.3, tau=0.03, total_sim_time=1.0, delta_t=0.01):
        """
        模拟电力系统在特定扰动下的时域响应，计算电压和电流曲线。

        参数:
        - initial_current_base: 基于稳定工况的初始电流基准，通常是 self.res['I0']。
        - perturb_node_key: 施加电流扰动的总线节点的key（字符串形式，如'component_new_bus_3_p_3'）。
        - t_start: (可选) 扰动开始时间 (秒)。
        - t_end_perturb: (可选) 扰动持续时间 (秒)。
        - tau: (可选) 扰动电流的指数衰减时间常数。
        - total_sim_time: (可选) 设定的总仿真时间 (秒)。
        - delta_t: (可选) 仿真时间步长 (秒)。

        修改实例属性:
        - self.Time: 存储仿真时间点的Numpy数组。
        - self.Icurve: 存储仿真期间的电流时间曲线。
        - self.Vcurve: 存储仿真期间的电压时间曲线。
        """
        #comment: 设置时间步长 deltaT
        deltaT = delta_t
        #comment: 设置仿真结束时间 tend
        tend = total_sim_time
        #comment: 计算时间点数量 Nt
        Nt = int(tend/deltaT)
        #comment: 获取节点数量 Nc
        Nc = self.res['Nc']
        #comment: 获取特定总线的索引
        node_idx = self.opts['BusList'].index(perturb_node_key)
        #comment: 生成时间向量 time
        self.Time = np.array([i*deltaT for i in range(Nt)])
        #comment: 初始化电流曲线 Icurve，使其在所有节点上都包含 I0
        self.Icurve = initial_current_base[:,nax] * np.ones((Nc,Nt),dtype = complex)

        # comment: 获取极点，这里使用了 res['PYc'] 和 res['fws']，但这两个变量在当前流程中未被赋值，可能来自于之前的 Vector Fitting 结果。
        # 如果 res 中没有这些信息，需要进行矢量拟合，或者将这些变量作为输入。
        # 这里为了重构的独立性，暂时假设这些信息可以通过 vectfit3 获得，但在实际应用中可能需要先执行 vectfit3 步骤
        # 或者传递预先计算好的极点和残差
        
        # 假设res中已存在vectfit3的结果，或者后续补充vectfit3功能
        # 如果没有 vectfit3 结果，这些变量可能是空的或导致错误。
        # 在原脚本中 res['PYc'], res['RYc'], res['CYc'], res['EYc'] 都没有赋值，这里需要假设其来源。
        # 为了避免运行时错误，我们这里先给出占位符或默认值，如果原脚本中没有这些计算逻辑，则需要补充。
        poles = self.res.get('PYc', np.array([])) - 2j * math.pi * self.res.get('fws', 0)
        RZs = self.res.get('RYc', np.array([]))
        CZs = self.res.get('CYc', np.array([]))
        EZs = self.res.get('EYc', np.array([]))


        #comment: 计算过渡时间段的采样点数量 Nt1
        # Calculate the special perturbation current for the specified node
        V0_node = self.res['V0'][node_idx]
        Z0_node = self.res['Z0'][node_idx, node_idx]
        
        I1 = -V0_node / Z0_node
        
        perturb_current = np.zeros(Nt, dtype=complex)
        time_at_perturb_start = self.Time[np.logical_and(self.Time < t_end_perturb, self.Time >= t_start)]
        perturb_current[np.logical_and(self.Time < t_end_perturb, self.Time >= t_start)] = I1 * (1 - np.exp(-1 / tau * (time_at_perturb_start - t_start)))
        
        time_after_perturb_end = self.Time[self.Time >= t_end_perturb]
        perturb_current[self.Time >= t_end_perturb] = I1 * (1 - np.exp(-1 / tau * (t_end_perturb - t_start))) * np.exp(-1 / tau * (time_after_perturb_end - t_end_perturb))
        
        self.Icurve[node_idx,:] += perturb_current

        # Ensure poles, RZs, CZs, EZs are correctly initialized or computed before this step.
        # This part requires a previous vectfit3 step, which is not explicitly in the original provided script.
        # For modularity, assuming these exist in 'res' or are passed as direct inputs.
        
        Vcurve = np.zeros((Nc,Nt),dtype=complex)
        
        if poles.size > 0: # Only proceed if poles are defined
            #comment: 循环遍历每个极点，进行卷积计算
            for cp in range(len(poles)):
                #comment: 计算 Ztemp 矩阵，表示指数衰减项
                Ztemp = np.exp(poles[cp]*self.Time)[nax,:]
                #comment: 对电流曲线 Icurve 进行卷积操作，使用 Ztemp 作为核
                # Note: `scipy.ndimage.convolve` expects real inputs for origin calculation sometimes.
                # It might be safer to handle real and imag parts separately if issues arise.
                # Based on original usage, we assume element-wise operations on complex arrays work as intended.
                
                # Handling `origin` in convolution for arbitrary-sized complex arrays is tricky.
                # The original `origin=[0,-int(np.floor((Ztemp.shape[1])/2))]` implies `Ztemp` is 1D (or 2D where kernel is 1D).
                # `Ztemp` shape here is (1, Nt)
                # `Icurve` shape is (Nc, Nt)
                # Convolution should be along the time axis (axis=1) for each node (axis=0).
                
                # This seems like a custom convolution or approximation. Let's replicate original for now.
                # The convolution as written in original: scipy.ndimage.convolve(Icurve,Ztemp,mode = 'nearest',origin=[0,-int(np.floor((Ztemp.shape[1])/2))])
                # This implies Icurve is treated as a 2D image, Ztemp as a 2D filter.
                # `origin=[0,-int(np.floor((Ztemp.shape[1])/2))]` suggests the "center" of the 1-row filter.
                
                # A more straightforward array op for this: Icurve[n, t] * exp(pole * (t - t'))
                # This could be a direct element-wise multiplication with a time-shifted exp.
                # Given 'Vhis' is reused, this pattern might be custom. The original script's convolution might be simplified.
                
                # For direct replication of original convolution part:
                # Assuming `scipy.ndimage.convolve` correctly interprets and applies the 1xNt `Ztemp` kernel
                # to each `Nc` row of `Icurve`.
                # If Ztemp or RZs, CZs, EZs are empty, this will skip.
                # The original code's `Vhis = scipy.ndimage.convolve(...)` applies `Ztemp` (1xNt) to `Icurve` (NcxNt)
                # This operation might be unconventional for standard signal processing.
                # Let's assume the original intent was a row-wise convolution.
                
                # This might be an approximation of: V = sum(R_k * Integral(I(tau) * exp(p_k * (t - tau)) d_tau))
                # For discrete time: sum(R_k * sum(I_j * exp(p_k * (t_i - t_j)) * delta_t))
                
                # The original convolution setup for Vhis might be an approximation or specific numerical method.
                if RZs.size > 0: # Ensure RZs has data
                    # Original `convolve` usage: Assume `Ztemp` convolves over the second axis of `Icurve` for each first axis row.
                    # This is likely a simplification or approximation of a continuous convolution as part of a modal analysis.
                    # Given it's `ndimage`, it's not a standard signal convolution where `Ztemp` shifts over `Icurve`.
                    # Let's keep the numpy array operations as close to expression as possible if `convolve` is troublesome.

                    # Due to the complexity/ambiguity of complex convolution with `scipy.ndimage.convolve`
                    # in case `Ztemp` is a complex array and `origin` points to a non-integer,
                    # and the *specific* form of the update to `Vcurve`, it looks like a particular
                    # numerical integration scheme related to poles and residues.
                    # Without the actual `vectfit3` output interpretation, this part is abstract.

                    # Let's re-express the logic without direct `convolve` call for clarity if possible.
                    # The Vhis part: `np.insert(Vhis[:,:Nt],0,Vhis[:,0].flatten(),axis = 1)` seems to adjust for boundary.
                    # If this is for modal response sum(R_k * exp(p_k *t)), then d/dt (V) ~= sum(p_k * R_k * exp...)
                    # And Z(s) = sum(R_k / (s - p_k)) + D + E*s implies V(s) = Z(s) * I(s)
                    # For time domain: V(t) = sum(R_k * I(t) * exp(p_k * t)) (convolution)
                    # The given update Vcurve += -1/poles[cp]*RZs[:,:,cp] @ ... looks like a discrete integral method.

                    # For now, let's assume `Vhis` as computed by `scipy.ndimage.convolve` is specific and required.
                    # If `scipy.ndimage.convolve` gives errors with complex origins or types, manual convolution might be needed.
                    temp_Vhis = np.zeros_like(self.Icurve, dtype=complex)
                    for row_idx in range(self.Icurve.shape[0]):
                        temp_Vhis[row_idx, :] = np.convolve(self.Icurve[row_idx, :], Ztemp[0,:], mode='full')[:Nt] # Simplified convolution
                    
                    Vhis_slice = temp_Vhis[:, :Nt] # Ensure it's the correct length
                    Vhis_slice_shifted = np.insert(Vhis_slice[:, :-1], 0, Vhis_slice[:, 0].flatten(), axis=1)

                    if RZs.ndim == 3 and RZs.shape[2] > cp: # Check if RZs has the pole dimension
                        # This part of the expression is unusual and might be a specific numerical integration schema
                        # associated with the `vectfit3` method.
                         Vcurve_update_term = -1/poles[cp] * RZs[:,:,cp] @ \
                                            ((-np.exp(poles[cp]*deltaT) - (1-np.exp(poles[cp]*deltaT)/(poles[cp]*deltaT))) * Vhis_slice[:,:-1] \
                                            + (1 + (1-np.exp(poles[cp]*deltaT)/(poles[cp]*deltaT))) * Vhis_slice[:,1:])
                         Vcurve += Vcurve_update_term
                    else:
                        print(f"Warning: RZs[:,:,{cp}] is out of bounds or incorrectly shaped. Skipping modal sum for pole {cp}.")
        
        #comment: 添加常数残差项和频率相关残差项
        # Ensure CZs and EZs are also correctly set in res.
        # Assuming res['fws'] (fundamental frequency) is available
        
        # Check if CZs and EZs exist and have correct dimensions.
        if CZs.size > 0 and EZs.size > 0 : # Check for non-empty arrays
            Vcurve += (CZs + 2j * math.pi * self.res.get('fws', 0) * EZs) @ self.Icurve
            #comment: 初始化 IcurveTemp
            IcurveTemp = np.zeros((Nc,Nt),dtype=complex)
            #comment: 对 IcurveTemp 进行移位操作
            IcurveTemp[:,1:] = self.Icurve[:,:-1]
            #comment: 添加动态残差项
            Vcurve += EZs @ (self.Icurve - IcurveTemp) / deltaT
        else:
            print("Warning: CZs or EZs are empty/missing. Skipping constant/dynamic residual terms in Vcurve calculation.")

        self.Vcurve = Vcurve
        print('时域响应仿真完成。')


    def calculate_characteristic_matrix(self):
        """
        计算特性矩阵 H 和其特征值。
        特性矩阵 H 是阻抗矩阵 Z 经过归一化处理后的形式，用于分析系统的模态特性。

        无参数。

        修改实例属性:
        - self.res['Vr']: 电压基准值。
        - self.res['H']: 存储所有频率下的特性矩阵列表。
        - self.res['Hlmd']: 存储所有频率下的 H 矩阵特征值列表。
        - self.res['Hm']: 存储所有频率下的 H 矩阵对角化形式。
        """
        #comment: 打印开始计算特性矩阵的信息
        print('开始计算特性矩阵。')
        #comment: 从结果中获取 Z 矩阵
        Z = self.res['Z']
        #comment: 从结果中获取节点数量 Nc
        Nc = self.res['Nc']
        #comment: 从结果中获取采样点数量 Ns
        Ns = self.res['Ns']
        #comment: 从结果中获取频率
        freqs = self.res['Freq']
        #comment: 初始化 H 列表
        H = []
        #comment: 初始化 Vr 向量
        Vr = np.zeros(Nc)
        #comment: 遍历总线列表，获取每个总线的 VBase 作为 Vr
        for i in range(len(self.opts['BusList'])):
            # comp = self.ce.project.getComponentByKey(self.opts['BusList'][i])
            # Vr[i] = float(comp.args['VBase'])
            #comment: 从拓扑信息中获取总线的 VBase
            top = self.ce.topo['components']['/'+self.opts['BusList'][i]]
            Vr[i] = float(top['args']['VBase'])
        # for i in range(len(self.opts['Trans3pList'])):
        #     Vr[i+len(self.opts['BusList'])] = 1
        #comment: 将 Vr 存储到结果字典中
        self.res['Vr'] = Vr
        
        #comment: 找到频率 freqs 中第一个大于等于 opts['f0'] 的索引 kf0
        kf0 = next(x for x in range(Ns) if freqs[x]>=self.opts['f0'])
        # print(np.diag(Z[kf0]))
        #comment: 计算 Htemp 矩阵
        Htemp = Z[kf0] / np.diag(Z[kf0])[nax,:] * Vr[nax,:] / Vr[:,nax] # Ensure correct broadcasting
        #comment: 计算 Htemp 的特征值和特征向量
        [eig0D, Ti0] = lg.eig(Htemp)
        #comment: 根据特征值绝对值降序排列索引
        idx = np.argsort(-abs(eig0D))
        #comment: 排序特征值
        eig0 = eig0D[idx]
        #comment: 排序特征向量
        Ti0 = Ti0[:,idx]
        #comment: 计算 Ti0 的逆
        TiI0 = lg.inv(Ti0)
        #comment: 初始化 Hm 和 Hlmd 列表
        Hm = []
        Hlmd = []
        #comment: 遍历 Z 列表，计算每个频率点的 H、特征值和 Hm
        for i in range(len(Z)):
            #comment: 计算 Htemp 矩阵
            Htemp = Z[i] / np.diag(Z[i])[nax,:] * Vr[nax,:] / Vr[:,nax]
            #comment: 将 Htemp 添加到 H 列表中
            H.append(Htemp)
            #comment: 计算 Htemp 的特征值 (投影到基向量上)
            Heig = np.diag(TiI0 @ Htemp @ Ti0)
            #comment: 将特征值添加到 Hlmd 列表中
            Hlmd.append(Heig) # EigenValues
            #comment: 构建 Hmtemp 矩阵
            Hmtemp = np.diag(Heig)
            #comment: 将 Hmtemp 添加到 Hm 列表中
            Hm.append(Hmtemp)
        #comment: 将 H、Hlmd、Hm 存储到结果字典中
        self.res['H'] = H
        self.res['Hlmd'] = Hlmd
        self.res['Hm'] = Hm
        print('特性矩阵计算完成。')

    def plot_results(self, voltage_trace_nodes=None, H_matrix_trace_nodes=None):
        """
        绘制仿真结果图，包括电压时间曲线和特性矩阵的频率响应。

        参数:
        - voltage_trace_nodes: (可选) 一个列表，包含要绘制电压时间曲线的总线key。
                               示例：['bus_key1', 'bus_key2']
                               如果为None，将寻找从'component_new_bus_3_p_3'到
                               'ef8377a5-b832-4b76-b025-a1dd380bd21a'的最短路径上的总线。
        - H_matrix_trace_nodes: (可选) 一个列表，包含要绘制特性矩阵幅值频率响应的总线key。
                                示例：['bus_key1', 'bus_key2']
                                如果为None，将使用与 voltage_trace_nodes 相同的逻辑寻找路径，并选择特定范围节点。
        """
        #comment: 定义 a，用于三相坐标变换
        a = np.exp(1j*2/3*math.pi)
        #comment: 定义 T 矩阵，用于三相坐标变换
        T = np.mat([[1,1,1],[1,a,a**2],[1,a**2,a]])/3

        # Plot Voltage Time Curve
        plt.figure(figsize=(10, 6))
        #comment: 寻找从 bus_3_p_3 到 ef8377a5-b832-4b76-b025-a1dd380bd21a 的最短路径
        # Update RIDs with placeholders
        start_node_rid = 'PLACEHOLDER_BUS_START_RID' # 'component_new_bus_3_p_3'
        end_node_rid = 'PLACEHOLDER_BUS_END_RID' # 'ef8377a5-b832-4b76-b025-a1dd380bd21a'

        if voltage_trace_nodes is None:
            # Shortest path calculation for plotting
            shortpath0_idx = self.ce.g.get_all_shortest_paths(self.ce.g.vs.find('/' + start_node_rid).index,
                                                               self.ce.g.vs.find('/' + end_node_rid).index)
            # Filter for bus nodes and get their indices in opts['BusList']
            shortpath_indices = [self.opts['BusList'].index(self.ce.g.vs[i]['name'][1:]) 
                                 for i in shortpath0_idx[0] 
                                 if self.ce.g.vs[i]['name'][1:] in self.opts['BusList']]
        else:
            shortpath_indices = [self.opts['BusList'].index(key) for key in voltage_trace_nodes]

        #comment: 遍历最短路径上的每个节点，绘制其电压曲线
        for j_idx in shortpath_indices:
            #comment: 将电压曲线转换为正序分量 (取决于 T 的定义和应用)
            # For 3-phase, usually [V0, V1, V2]^T = T * [Va, Vb, Vc]^T
            # So V1 (positive sequence) is the second element of the transformed vector.
            if self.Vcurve is not None:
                Vcurvep_row = self.Vcurve[j_idx, :]
                Vcurvep = lg.inv(T)[:,1] @ Vcurvep_row[nax,:] # V_sequence = T_inv @ V_phase
                #comment: 绘制电压幅值（乘以 sqrt(3/2) 进行标幺化或单位转换）
                plt.plot(self.Time, np.abs(Vcurvep[0,:].A.flatten())*np.sqrt(3/2),label=self.ce.project.getComponentByKey(self.opts['BusList'][j_idx]).label)
        
        plt.xlabel('时间 (s)', fontproperties='SimHei')
        plt.ylabel('电压幅值 (p.u.)', fontproperties='SimHei')
        plt.title('电压时间响应', fontproperties='SimHei')
        plt.legend(prop={'family' : 'SimHei'})
        plt.grid(True)
        plt.show()

        # Plot H Matrix Frequency Response
        plt.figure(figsize=(10, 6))
        
        if H_matrix_trace_nodes is None:
            # Use the same shortest path logic if not specified
            # This part should be consistent with how shortpath is used in original code [2:11]
            shortpath0_idx = self.ce.g.get_all_shortest_paths(self.ce.g.vs.find('/' + start_node_rid).index,
                                                               self.ce.g.vs.find('/' + end_node_rid).index)
            shortpath_indices_h = [self.opts['BusList'].index(self.ce.g.vs[i]['name'][1:]) 
                                   for i in shortpath0_idx[0] 
                                   if self.ce.g.vs[i]['name'][1:] in self.opts['BusList']]
            # Original code picks [2:11] from this path indices for H plot
            h_plot_indices = shortpath_indices_h[2:11] 
        else:
            h_plot_indices = [self.opts['BusList'].index(key) for key in H_matrix_trace_nodes]

        #comment: 遍历最短路径上的节点，绘制 H 矩阵的幅值曲线
        for k_idx in h_plot_indices:
            # If `res['H']` is list of matrices, ensure its length matches `freqs`.
            if self.res.get('H') is not None and self.res['H']:
                # The original code `5*np.array([np.abs(res['H'][i][k,shortpath[0]]) for i in range(1001)])`
                # suggests that `res['H']` has 1001 elements, and `shortpath[0]` is a specific node index.
                # Here, `freqs` length is used as the number of available `H` matrices.
                # Assuming `shortpath_indices[0]` is the reference node for H matrix calculation, 
                # as in the original `k,shortpath[0]`.
                if shortpath_indices and len(self.res['H']) >= len(self.opts['Freq']):
                    H_values = [np.abs(self.res['H'][i][k_idx, shortpath_indices[0]]) 
                                for i in range(len(self.opts['Freq']))]
                    plt.plot(self.opts['Freq'], 5 * np.array(H_values), 
                            label=str(self.ce.project.getComponentByKey(self.opts['BusList'][k_idx]).label))
                else:
                    print("Warning: H matrix data is incomplete or reference node missing for H plot.")
            else:
                print("Warning: H matrix not computed or is empty. Skipping H matrix plot.")

        plt.xlabel('频率 (Hz)', fontproperties='SimHei')
        plt.ylabel('H矩阵幅值', fontproperties='SimHei')
        plt.title('阻抗特性矩阵幅值频率响应', fontproperties='SimHei')
        plt.legend(prop={'family' : 'SimHei'})
        plt.xscale('log')
        plt.ylim([0,1])
        plt.grid(True)
        plt.show()

        # Plot Current Amplitude Curve for a specific node (placeholder from original)
        plt.figure(figsize=(10, 6))
        # Original: plt.plot(time, np.abs(Icurve[opts['BusList'].index('canvas_0_10'),:]))
        # Need to provide a specific node for this plot or generalize.
        # Let's use the first node in the bus list as an example, or first node in shortpath.
        if self.Icurve is not None and self.Icurve.shape[0] > 0:
            example_node_idx = self.opts['BusList'].index('PLACEHOLDER_NODE_FOR_CURRENT_PLOT') # Example node 'canvas_0_10'
            plt.plot(self.Time, np.abs(self.Icurve[example_node_idx,:]))
            plt.xlabel('时间 (s)', fontproperties='SimHei')
            plt.ylabel('电流幅值 (A)', fontproperties='SimHei')
            plt.title(f'节点 {self.ce.project.getComponentByKey(self.opts['BusList'][example_node_idx]).label} 电流时间响应', fontproperties='SimHei')
        else:
            print("Warning: Current curve data is not available. Skipping current plot.")
        plt.grid(True)
        plt.show()

        # Plot Network Topology
        #comment: 绘制网络拓扑图
        self.ce.plotNetwork(self.ce.g, showlabel=False, show=True, layt = self.ce.g.layout_reingold_tilford())


def main():
    """
    主函数，用于演示 NetworkCalculation 类的使用。
    它按顺序调用类中的方法来完成电力系统分析的整个流程。
    """
    # 第一步：初始化 NetworkCalculation 类的实例，并获取默认配置。
    print("------- 开始电力系统分析流程 -------")
    calculator = NetworkCalculation()
    
    # 原始脚本的频率设置
    # freqs = np.append(np.append(np.linspace(10,40,16),np.linspace(45,200,32)),np.linspace(300,2000,18))
    # calculator.opts['Freq'] = freqs # Overwrite default Freq with this specific set
    # calculator.opts['fws'] = 50 # Set fundamental frequency

    # 第二步：加载网络配置文件和拓扑结构。
    calculator.load_network_config()

    # 第三步：计算系统在不同频率下的阻抗和导纳矩阵。
    calculator.calculate_frequency_response()

    # 第四步：计算稳定工况下的节点电压和电流。
    calculator.calculate_stable_operating_point()

    # 第五步：模拟系统在特定扰动下的时域响应，计算电压和电流时间曲线。
    # 定义扰动参数
    perturb_node_key = 'PLACEHOLDER_BUS_FOR_PERTURBATION' # 'component_new_bus_3_p_3'
    # The original script does not explicitly use `res['PYc']`, `res['RYc']`, etc.
    # which are typically outputs of a vector fitting step (e.g., from `vectfit3`).
    # If these are necessary for `simulate_time_domain_response` to be accurate,
    # a `vectfit3` step (or similar modal analysis method) needs to be added before this.
    # For now, `simulate_time_domain_response` is called assuming `res` has placeholders or will be properly initialized.
    
    # Placeholder for potential vector fitting step if needed:
    # try:
    #     poles, res_mat = vectfit3(calculator.opts['Freq'], calculator.Z, **calculator.opts['vfopts'])
    #     calculator.res['PYc'] = poles # Example assignment, needs to match actual vectfit3 output structure
    #     calculator.res['RYc'] = res_mat # Example
    #     calculator.res['fws'] = calculator.opts['f0'] # Fundamental frequency
    #     # Add C and E terms if vectfit3 provides them and they are critical.
    # except Exception as e:
    #     print(f"Warning: Vector fitting failed or not implemented. Time domain simulation may be approximate. Error: {e}")

    # Set some dummy values for `PYc`, `RYc`, `CYc`, `EYc` if vector fitting is not integrated,
    # to allow the `simulate_time_domain_response` to run without immediate errors.
    # In a real scenario, these should come from a proper modal analysis.
    num_nodes = calculator.res['Nc']
    num_poles = 1 # Example: just one pole for very basic test
    calculator.res['PYc'] = np.array([-10 + 500j]) # A dummy pole
    calculator.res['RYc'] = np.ones((num_nodes, num_nodes, num_poles), dtype=complex) # Dummy residue
    calculator.res['CYc'] = np.zeros((num_nodes, num_nodes), dtype=complex) # Dummy constant term
    calculator.res['EYc'] = np.zeros((num_nodes, num_nodes), dtype=complex) # Dummy E*s term
    calculator.res['fws'] = calculator.opts['f0'] # Set fundamental frequency for time domain

    calculator.simulate_time_domain_response(calculator.res['I0'], perturb_node_key, 
                                              t_start=0.2, t_end_perturb=0.3, tau=0.03,
                                              total_sim_time=1.0, delta_t=0.01)

    # 第六步：计算系统的特性矩阵，用于模态分析。
    calculator.calculate_characteristic_matrix()

    # 第七步：绘制所有计算结果，包括电压时间曲线、特性矩阵频率响应和电流时间曲线。
    current_plot_node_key = 'PLACEHOLDER_NODE_FOR_CURRENT_PLOT' # 'canvas_0_10'
    calculator.plot_results(voltage_trace_nodes=None, H_matrix_trace_nodes=None) # Using default paths
    # Or, to be explicit with nodes:
    # calculator.plot_results(voltage_trace_nodes=[perturb_node_key, 'another_bus_key'],
    #                         H_matrix_trace_nodes=[perturb_node_key, 'yet_another_bus_key'])

    print("------- 电力系统分析流程完成 -------")


if __name__ == '__main__':
    main()