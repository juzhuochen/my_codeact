import numpy as np
import numpy.linalg as lg

nax = np.newaxis
from vectfit3 import vectfit3, full2full, ss2pr  # type: ignore
from time import time
import matplotlib.pyplot as plt
import math
import cmath
import scipy as sp
from scipy import constants as const
from scipy import integrate as scii
import scipy.special as spp
import scipy.ndimage
from scipy import optimize as sco
import scipy.signal
import os
import tkinter
import tkinter.filedialog
import csv
import cloudpss
from CaseEditToolbox import CaseEditToolbox  # type: ignore
from CaseEditToolbox import is_number  # type: ignore
from PSAToolbox import PSAToolbox  # type: ignore
import json
import nest_asyncio

nest_asyncio.apply()
from NetworkCalculation_TransProb_temp import *  # 假设此模块包含CalZ_All, eigenMat_NR, plotFitting等函数


class NetworkCalculation_TransProb:
    """
    该类用于封装电力系统网络特性计算和瞬态分析的逻辑。
    它包含配置管理、频域矩阵计算、矢量拟合、时间域响应计算等功能。

    属性:
    opts (dict): 存储各种配置参数，如API令牌、URL、频率范围、拟合参数等。
    ce (PSAToolbox): CloudPSS仿真工具箱实例，用于与CloudPSS平台交互。
    """

    def __init__(self, opts=None):
        """
        初始化 NetworkCalculation_TransProb 类。

        参数:
        opts (dict, optional): 用户提供的配置选项。如果未提供，则使用默认配置。
        """
        if opts is None:
            self.opts = self._default_options()
        else:
            self.opts = opts
        self.ce = PSAToolbox()
        self.res = {}  # 存储所有计算结果

    def _default_options(self):
        """
        设置默认的选项参数。

        返回:
        dict: 包含所有默认配置的字典。
        """
        opts = {}

        # comment: 设置 CloudPSS 的 API 令牌
        opts['token'] = 'YOUR_CLOUD_PSS_API_TOKEN'
        # comment: 设置 CloudPSS 的 API URL
        opts['apiURL'] = 'YOUR_CLOUD_PSS_API_URL'
        # comment: 设置 CloudPSS 的用户名
        opts['username'] = 'YOUR_USERNAME'  # 用户名
        # comment: 设置 CloudPSS 项目的 Key
        opts['projectKey'] = 'YOUR_PROJECT_KEY'

        # comment: 设置是否进行 I0 计算
        opts['I0Calculation'] = True

        # comment: 设置频率范围，从 0.5Hz 到 1MHz，共 101 个点，对数分布
        opts['Freq'] = np.logspace(math.log10(0.5), 6, 101)
        # comment: 设置基准频率
        opts['f0'] = 50
        # EigenValue Setting
        # comment: 设置特征值计算的最大迭代次数
        opts['EigMaxIter'] = 10
        # comment: 设置特征值计算的收敛误差
        opts['EigEps'] = 1e-8
        # curve fitting setting
        # comment: 设置目标误差
        opts['target_eps'] = 0.002

        # opts['NpYc'] = 20
        # opts['ErYc'] = 0.002
        # opts['WeightYc0'] = 1; # F<0.9F0
        # opts['WeightYc1'] = 1000; # F=0.9~1.1F0
        # opts['WeightYc2'] = 1; # F>1.1F0
        # opts['WeightStyleYc'] = 1; # 1 for ones, 2 for 1/abs(f), 3 for 1/sqrt(abs(f))

        # comment: 设置 H 矩阵的极点数量
        opts['NpH'] = 20
        # comment: 设置 H 矩阵的拟合误差
        opts['ErH'] = 0.002

        # comment: 设置 H 矩阵的拟合权重：F<0.9F0 时的权重
        opts['WeightH0'] = 1  # F<0.9F0
        # comment: 设置 H 矩阵的拟合权重：F=0.9~1.1F0 时的权重
        opts['WeightH1'] = 1000  # F=0.9~1.1F0
        # comment: 设置 H 矩阵的拟合权重：F>1.1F0 时的权重
        opts['WeightH2'] = 1  # F>1.1F0
        # comment: 设置 H 矩阵的权重风格：1 表示全为 1，2 表示 1/abs(f)，3 表示 1/sqrt(abs(f))
        opts['WeightStyleH'] = 1  # 1 for ones, 2 for 1/abs(f), 3 for 1/sqrt(abs(f))
        # comment: 设置权重中的小误差项，防止除零
        opts['Weight_eps'] = 1e-10

        # opts['NiterYc1'] = 5
        # opts['NiterYc2'] = 3
        # comment: 设置 H 矩阵拟合的第一阶段迭代次数
        opts['NiterH1'] = 5
        # comment: 设置 H 矩阵拟合的第二阶段迭代次数
        opts['NiterH2'] = 3

        # comment: 设置是否显示 Yc 矩阵的矢量拟合结果视图
        opts['ViewYcVF'] = False
        # comment: 设置是否显示 H 矩阵的矢量拟合结果视图
        opts['ViewHVF'] = False

        # comment: 初始化矢量拟合选项字典
        opts['vfopts'] = {}
        # comment: 设置矢量拟合是否使用松弛的非平凡性约束（relaxation）
        opts['vfopts']['relax'] = True  # Use vector fitting with relaxed non-triviality constraint
        # comment: 设置矢量拟合是否强制稳定极点
        opts['vfopts']['stable'] = True  # Enforce stable poles
        # comment: 设置矢量拟合是否包含常数项 D，不包含 E * s 项 (asymp=2 表示只拟合D，不拟合E*s)
        opts['vfopts']['asymp'] = 2  # Fitting includes D(constant), not include E * s
        # comment: 设置矢量拟合是否不绘制第一阶段的图
        opts['vfopts']['spy1'] = False  # No plotting
        # comment: 设置矢量拟合是否显示拟合结果的幅度图
        opts['vfopts']['spy2'] = True
        # comment: 设置矢量拟合结果图的 X 轴是否使用对数刻度
        opts['vfopts']['logx'] = True
        # comment: 设置矢量拟合结果图的 Y 轴是否使用对数刻度
        opts['vfopts']['logy'] = True
        # comment: 设置矢量拟合结果图是否显示误差曲线
        opts['vfopts']['errplot'] = True
        # comment: 设置矢量拟合结果图是否显示相位曲线
        opts['vfopts']['phaseplot'] = True

        # comment: 设置矢量拟合是否跳过极点选择
        opts['vfopts']['skip_pole'] = False
        # comment: 设置矢量拟合是否跳过残差计算
        opts['vfopts']['skip_res'] = True
        # comment: 设置矢量拟合是否生成对角化 A 矩阵的状态空间模型
        opts['vfopts']['cmplx_ss'] = True  # =1 --> Will generate state space model with diagonal A
        # comment: 设置矢量拟合结果图是否显示图例
        opts['vfopts']['legend'] = True
        # comment: 设置矢量拟合结果图是否阻塞式显示
        opts['vfopts']['block'] = True

        # comment: 返回配置字典
        return opts

    def _read_pscad_data(self, filename=None):
        """
        读取 PSCAD 输出的 .clo 文件，解析其中的矩阵拟合参数。

        参数:
        filename (str, optional): PSCAD .clo 文件的路径。如果为 None，则弹出文件选择对话框。

        返回:
        dict: 包含解析出的 Yc 矩阵拟合参数的字典。
        """
        # comment: 如果文件名为空，则弹出文件选择对话框
        if filename is None:
            root = tkinter.Tk()  # 创建一个Tkinter.Tk()实例
            default_dir = r"文件路径"
            # comment: 弹出文件选择对话框，选择 .clo 文件
            filename = tkinter.filedialog.askopenfilename(title=u'选择clo文件',
                                                          initialdir=(os.path.expanduser(default_dir)))
            root.destroy()
        # comment: 打开文件并读取内容
        stream = open(filename, 'r')
        cloDataRaw = stream.read()
        # comment: 按行分割，去除首尾空格
        cloData = [i.strip() for i in cloDataRaw.splitlines()]
        # comment: 将可转换为数字的字符串转换为浮点数
        cloData = [float(i) if is_number(i) else i for i in cloData]

        # Basic
        # comment: 获取导体数量
        NoCond = int(cloData[cloData.index('Number of ports:') + 1])  # 导体数量
        # comment: 获取 Yc 矩阵的留数数量
        NoYcRP = int(cloData[cloData.index('Residues and poles:') + 1])  # Yc 矩阵的留数数量
        # comment: 计算 Y 矩阵信息起始位置
        pos_Y = cloData.index('Residues and poles:') + 2  # Y 矩阵信息起始位置
        # comment: 计算 Yc 矩阵常数项信息起始位置
        pos_Ycconstant = pos_Y - 1 + NoCond + 2 * NoYcRP * NoCond + 2 * NoCond ** 2 * NoYcRP  # Yc 矩阵信息起始位置

        # Yc
        YcDict = {}
        # comment: 从读取的数据中解析 Y 矩阵的极点
        Y_poles = np.array(
            [cloData[pos_Y + 2 * (NoCond + 1) * jy] + 1j * cloData[pos_Y + 2 * (NoCond + 1) * jy + 1] for jy in
             range(NoYcRP)])
        # comment: 将极点存储到 YcDict
        YcDict["Poles"] = Y_poles
        # comment: 初始化 Y 矩阵的残差数组
        Yres = np.zeros((NoYcRP, NoCond, NoCond), dtype=complex)
        # comment: 遍历读取的数据，解析 Y 矩阵的残差
        for ii in range(NoCond):
            for jj in range(NoCond):
                for kk in range(NoYcRP):
                    Yres[kk][ii][jj] = cloData[pos_Y + 2 + 2 * jj + 2 * (NoCond + 1) * kk + ii * (
                            2 * (NoCond + 1) * NoYcRP + 1)] + \
                                       1j * cloData[pos_Y + 3 + 2 * jj + 2 * (NoCond + 1) * kk + ii * (
                                2 * (NoCond + 1) * NoYcRP + 1)]
        # comment: 将残差存储到 YcDict
        for kk in range(NoYcRP):
            YcDict[kk] = Yres[kk]

        # comment: 初始化 Yc 矩阵的常数项
        YcConstant = np.zeros((NoCond, NoCond), dtype=float)
        # comment: 遍历读取的数据，解析 Yc 矩阵的常数项
        for ii in range(NoCond):
            for jj in range(NoCond):
                YcConstant[ii][jj] = cloData[pos_Ycconstant + ii * NoCond + jj]

        # comment: 将常数项存储到 YcDict
        YcDict["Const"] = YcConstant

        # comment: 返回解析出的 YcDict
        return YcDict

    def configure_simulation(self):
        """
        配置仿真环境，加载 CloudPSS 项目配置文件，并更新 opts。
        """
        # Load the configuration file
        # comment: 创建 PSAToolbox 实例
        # self.ce = PSAToolbox() # Already initialized in __init__
        # comment: 更新 CloudPSS 的 API 令牌
        self.opts['token'] = 'YOUR_RUNTIME_CLOUD_PSS_API_TOKEN'
        # comment: 更新 CloudPSS 的 API URL
        self.opts['apiURL'] = 'YOUR_RUNTIME_CLOUD_PSS_API_URL'
        # comment: 更新 CloudPSS 的用户名
        self.opts['username'] = 'YOUR_RUNTIME_USERNAME'
        # comment: 更新 CloudPSS 项目的 Key
        self.opts['projectKey'] = 'YOUR_RUNTIME_PROJECT_KEY'
        # comment: 更新目标误差
        self.opts['target_eps'] = 0.002
        # comment: 更新矢量拟合选项：只包含 D 项（常数项）
        self.opts['vfopts']['asymp'] = 1
        # comment: 更新矢量拟合选项：使用松弛约束
        self.opts['vfopts']['relaxed'] = True
        # comment: 更新矢量拟合选项：强制稳定极点
        self.opts['vfopts']['stable'] = True
        # comment: 更新矢量拟合选项：显示拟合结果的幅度图
        self.opts['vfopts']['spy2'] = True
        # comment: 更新矢量拟合选项：不绘制第一阶段的图
        self.opts['vfopts']['spy1'] = False
        # comment: 更新矢量拟合选项：不显示误差曲线
        self.opts['vfopts']['errplot'] = False
        # comment: 更新矢量拟合选项：X 轴使用对数刻度
        self.opts['vfopts']['logx'] = True
        # comment: 更新矢量拟合选项：Y 轴使用对数刻度
        self.opts['vfopts']['logy'] = True

        # comment: 更新基频
        self.opts['f0'] = 50
        # comment: 更新特征值计算的最大迭代次数
        self.opts['EigMaxIter'] = 2000
        # comment: 更新特征值计算的收敛误差
        self.opts['EigEps'] = 1e-9

        # comment: 更新 Yc 矩阵的极点数量
        self.opts['NpYc'] = 30
        # comment: 更新 H 矩阵的极点数量
        self.opts['NpH'] = 20
        # comment: 更新 Yc 矩阵的拟合误差
        self.opts['ErYc'] = 0.02
        # comment: 更新 H 矩阵的拟合误差
        self.opts['ErH'] = 0.002
        # comment: 更新 Yc 矩阵的拟合权重
        self.opts['WeightYc0'] = 1
        self.opts['WeightYc1'] = 3
        self.opts['WeightYc2'] = 1
        # comment: 更新 Yc 矩阵的权重风格
        self.opts['WeightStyleYc'] = 0

        # comment: 更新 H 矩阵的拟合权重
        self.opts['WeightH0'] = 1
        self.opts['WeightH1'] = 1
        self.opts['WeightH2'] = 1
        # comment: 更新 H 矩阵的权重风格
        self.opts['WeightStyleH'] = 0

        # comment: 更新权重中的小误差项
        self.opts['Weight_eps'] = 1e-20

        # comment: 更新 Yc 矩阵拟合的第一阶段迭代次数
        self.opts['NiterYc1'] = 5
        # comment: 更新 Yc 矩阵拟合的第二阶段迭代次数
        self.opts['NiterYc2'] = 3
        # comment: 更新 H 矩阵拟合的第一阶段迭代次数
        self.opts['NiterH1'] = 10
        # comment: 更新 H 矩阵拟合的第二阶段迭代次数
        self.opts['NiterH2'] = 3

        # comment: 更新是否显示 Yc 矩阵的矢量拟合结果视图
        self.opts['ViewYcVF'] = False
        # comment: 更新是否显示 H 矩阵的矢量拟合结果视图
        self.opts['ViewHVF'] = True

        # comment: 更新是否进行 I0 计算
        self.opts['I0Calculation'] = False
        # comment: 更新频率范围，从 0.5Hz 到 100kHz，共 1001 个点，对数分布
        freqs = np.logspace(np.log10(0.5), 5, 1001)
        # comment: 将更新后的频率赋值给 opts
        self.opts['Freq'] = freqs
        # comment: 设置稳态基频
        self.opts['fws'] = 50

        # comment: 加载配置文件
        loadConfigFile(self.ce, self.opts)

    def calculate_frequency_domain_matrices(self):
        """
        计算并拟合网络在频域的 Z 矩阵，并存储相关结果。
        此函数将计算每个频率点的Z和Y矩阵，并进行Z矩阵的矢量拟合。

        输出:
        res (dict): 包含计算结果的字典，包括 Z, Y, lmd, NpYc, RYc, CYc, EYc, fws 等。
        """
        # comment: 初始化 Z, Y, Ti, TiI, lmd, EigErr, Zm 列表
        Z_list = []
        Y_list = []
        Ti_list = []
        TiI_list = []
        lmd_list = []
        EigErr_list = []
        Zm_list = []

        # comment: 获取频率数组
        freqs = self.opts['Freq']

        # comment: 设置 constT 标志为 True
        constT = True
        # comment: 打印计算频域 Z 和 Y 矩阵的开始信息
        print('开始计算频域Z和Y矩阵...')

        # comment: 读取 Pscad 数据文件 PMSG_FDNE_Z.txt
        PMSG_FDNE_Z = self._read_pscad_data(filename='PMSG_FDNE_Z.txt')
        # comment: 将读取的数据存储到 opts 中
        self.opts['PMSG_FDNE_Z'] = PMSG_FDNE_Z
        # comment: 在基频 opts['f0'] 下计算全网络的 Znet0 和 Ynet0 矩阵
        Znet0, Ynet0 = CalZ_All(self.ce, self.opts['f0'], self.opts)
        # comment: 对 Znet0 进行特征值分解
        [eig0D, Ti0] = lg.eig(Znet0)
        # comment: 对特征值按绝对值降序排序，并获取排序索引
        idx = np.argsort(-abs(eig0D))
        # comment: 根据排序索引重新排列特征值和特征向量
        eig0 = eig0D[idx]
        Ti0 = Ti0[:, idx]
        # comment: 计算特征向量矩阵的逆
        TiI0 = lg.inv(Ti0)
        # comment: 打印开始计算频域特征根的信息
        print('开始计算频域特征根...')
        # comment: 遍历每个频率点
        for i in range(len(freqs)):
            # Calculate Y and Z
            # comment: 在当前频率下计算全网络的 Znet 和 Ynet 矩阵
            Znet, Ynet = CalZ_All(self.ce, freqs[i], self.opts)
            # comment: 将 Znet 和 Ynet 添加到相应的列表中
            Z_list.append(Znet)
            Y_list.append(Ynet)

            # comment: 获取当前 Znet 的导体数量
            Nc = Znet.shape[0]

            # comment: 如果 constT 为 True (此部分代码实际执行)
            # comment: 使用初始的特征向量矩阵 Ti0 和其逆 TiI0 计算当前 Znet 的特征值
            eign = np.diag(TiI0 @ Znet @ Ti0)
            # comment: 将特征值添加到 lmd 列表
            lmd_list.append(eign)  # EigenValues
            # comment: 创建特征值对角矩阵 Zmtemp
            Zmtemp = np.diag(eign)
            # comment: 将 Zmtemp 添加到 Zm 列表
            Zm_list.append(Zmtemp)
        # comment: 获取导体数量 (基于第一个 Zm 矩阵的维度)
        Nc = len(Zm_list[0])  # N.o.conductors.
        # comment: 获取频率点数量
        Ns = len(freqs)  # N.o.frequencys
        # comment: 将结果存储到 results 字典中
        self.res['Nc'] = Nc
        self.res['Ns'] = Ns
        self.res['Freq'] = freqs
        self.res['Z'] = Z_list
        self.res['Y'] = Y_list
        self.res['Ti'] = Ti_list  # Placeholder, not calculated with constT=True
        self.res['TiI'] = TiI_list  # Placeholder, not calculated with constT=True
        self.res['lmd'] = lmd_list
        self.res['EigErr'] = EigErr_list  # Placeholder, not calculated
        self.res['Zm'] = Zm_list

        # comment: 打印开始拟合 Z 矩阵的信息
        print('开始拟合Z矩阵...')
        # comment: 调用 self._vector_fit_Z 函数进行拟合

        # comment: 复制 opts['vfopts']，以便修改不影响原始配置
        vfopts_copy = self.opts['vfopts'].copy()
        # comment: 获取目标误差
        target_eps = self.opts['target_eps']

        # comment: 打印开始拟合 Yc 矩阵的信息
        print('   --------Start fitting Yc----------  ')

        # comment: 获取 Yc 矩阵拟合的权重参数
        Weight0 = self.opts['WeightYc0']  # F<0.9F0
        Weight1 = self.opts['WeightYc1']  # F=0.9~1.1F0
        Weight2 = self.opts['WeightYc2']  # F>1.1F0

        # comment: 初始化频率权重数组
        weightFreq = np.zeros(Ns)
        # comment: 定义频率范围的比例因子
        c0 = 0.08  # Changed from 0.8 as per original code, to match common practice for weighting
        c1 = 1.2
        # comment: 根据频率范围设置权重
        weightFreq[self.res['Freq'] < c0 * self.opts['f0']] = Weight0
        weightFreq[np.logical_and(self.res['Freq'] >= c0 * self.opts['f0'],
                                  self.res['Freq'] <= c1 * self.opts['f0'])] = Weight1
        weightFreq[self.res['Freq'] > c1 * self.opts['f0']] = Weight2

        # comment: 将权重频率存储到 res 中
        self.res['weightFreq'] = weightFreq

        # comment: 设置矢量拟合选项：只包含 D 项（常数项）
        # self.opts['vfopts']['asymp'] = 1 # This overwrite the opts['vfopts']['asymp'] defined in __init__, so keep it here.

        # comment: 获取 Z 矩阵数据
        matList = self.res['Z']
        # comment: 计算复数频率 s = j * 2 * pi * f
        s = 1j * 2 * math.pi * self.res['Freq']
        # comment: 获取极点数量 NpYc (NpYc 在这里应该是 opts['NpYc'])
        N_poles = self.opts['NpYc']

        tell = -1
        # comment: 初始化 f 数组，用于存储 Z 矩阵的扁平化元素
        f = np.zeros((Nc * Nc, Ns), dtype=complex)
        # comment: 遍历 Z 矩阵的每个元素，并将其扁平化存储到 f 数组中
        for col in range(Nc):
            for row in range(Nc):
                tell = tell + 1
                for k in range(Ns):
                    f[tell, k] = matList[k][row, col]  # stacking elements into a single vector

        # comment: The vectorfit3 function will update the 'fit' object directly and also return it.
        # comment: It needs s, f, N, weightFreq.
        # comment: The fitting results (poles, residues, D, E) will be stored in fit.
        # comment: Execute vector fitting using vectorfit3
        fitYc = vectfit3(s, f, N_poles, w=weightFreq, opts=self.opts['vfopts'])

        # comment: 将扁平化后的数据 f 存储到 res 中
        self.res['f'] = f
        self.res['fitYc'] = fitYc
        self.res['PYc'] = fitYc.poles
        self.res['RYc'] = np.reshape(fitYc.res, (Nc, Nc, N_poles))
        self.res['CYc'] = np.reshape(fitYc.D, (Nc, Nc))
        self.res['EYc'] = np.reshape(fitYc.E, (Nc, Nc))

        # comment: 如果 ViewYcVF 为 True，则绘制拟合结果
        if (self.opts['ViewYcVF']):
            plotFitting(s, f, fitYc, self.opts['vfopts'])

        # comment: 将 opts['fws'] (稳态基频) 存储到 results 中
        self.res['fws'] = self.opts['fws']

        print('完成频域Z矩阵计算与拟合.')

    def calculate_stable_case(self):
        """
        计算网络在稳态基频下的初始电流 (I0) 和电压 (V0) 分布，以及基频阻抗矩阵 (Z0)。
        此函数根据 opts['I0Calculation'] 决定是否进行 I0 计算。

        输出:
        res (dict): 更新的计算结果字典，包含 I0, V0, Z0 (如果适用)。
        """
        # comment: 打印开始常量初始化的信息
        print('开始常量初始化...')
        SFlags = []
        # comment: 获取导体数量
        Nc = self.res['Nc']
        # comment: 初始化 V0 数组
        V0 = np.zeros(Nc, dtype=complex)
        # comment: 判断是否选择了特定的母线
        if ('SelectBuses' not in self.opts.keys() or self.opts['SelectBuses'] == []):
            # comment: 如果没有，则使用所有母线
            BusList = self.opts['BusList']
            BusList_N = BusList
        else:
            # comment: 如果有，则使用选择的母线
            BusList = self.opts['SelectBuses']
            BusList_N = set(BusList)
            # comment: 获取选择母线的邻居母线，形成完整的节点列表
            for j in BusList:
                BusList_N = BusList_N | set([x['name'][1:] for x in self.ce.g.vs.find('/' + j).neighbors()])

        # comment: 打印最终的母线列表
        print("Initial BusList_N:", BusList_N)
        # for i in self.ce.g.vs['name']:

        # comment: 遍历 BusList_N 中的每个母线
        for i0 in BusList_N:
            # comment: 构造完整的节点路径
            i = '/' + i0
            # comment: 获取对应组件
            comp = self.ce.project.getComponentByKey(i[1:])
            # comment: 获取拓扑信息
            top = self.ce.topo['components'][i]
            # comment: 如果是三相母线
            if (comp.definition == 'model/CloudPSS/_newBus_3p'):
                # comment: 获取该母线在 BusList 中的索引
                try:
                    a = BusList.index(i[1:])
                except ValueError:
                    # If bus not in original BusList (e.g., it's a neighbor not directly selected)
                    # For now, skip this bus's voltage setting if not in BusList
                    print(f"Warning: Bus {i[1:]} found via neighbors, but not in original BusList. Skipping V0 setting.")
                    continue
                # comment: 计算母线电压幅值和相角
                v = float(top['args']['VBase']) * float(top['args']['V']) * math.sqrt(2 / 3)
                theta = float(top['args']['Theta']) * math.pi / 180
                # comment: 设置 V0 数组中的电压值
                V0[a] = v * np.exp(1j * theta)
            # comment: 检查当前节点是否连接到_newBus_3p类型的组件 (如果不是母线本身的节点)
            if 'model/CloudPSS/_newBus_3p' not in [j['rid'] for j in self.ce.g.vs.find(i).neighbors()]:
                continue
            # if(comp.definition=='model/CloudPSS/_newTransformer_3p3w'):
            #     a = opts['Trans3pList'].index(i[1:]) + len(opts['BusList'])
            #     V0[a] = float(top['args']['pf_V'])*np.exp(1j*math.pi/180*float(top['args']['pf_Theta']))

            # comment: 初始化源标志
            sourceflag = 0

            # comment: 如果组件定义是源类型（Thevenin, SyncGeneratorRouter, DCLine, GW_mask_power_flow）
            if (comp.definition in ['model/CloudPSS/Thevenin_3p', 'model/CloudPSS/SyncGeneratorRouter',
                                    'model/admin/DCLine', 'model/admin/GW_mask_power_flow']):
                sourceflag = 1
            # comment: 如果是源，则寻找其连接的母线并将索引添加到 SFlags
            if (sourceflag == 1):
                for j in self.ce.g.vs.find(i).neighbors():
                    if (j['rid'] == 'model/CloudPSS/_newBus_3p'):
                        # print(i['name'][1:])
                        a = BusList.index(j['name'][1:])
                        if (a not in SFlags):
                            SFlags.append(a)

        # comment: 对 SFlags 进行排序
        SFlags = [SFlags[i] for i in np.argsort(SFlags)]
        # comment: 打印 SFlags 列表
        print("SFlags:", SFlags)
        # comment: 如果不进行 I0 计算，则直接返回 V0
        if (not self.opts['I0Calculation']):
            self.res['V0'] = V0
        else:
            # calculate I0
            # comment: 计算基频下的 Z0 和 Y0 矩阵
            Z0, Y0 = CalZ_All(self.ce, self.opts['f0'], self.opts)
            # comment: 获取 SFlags 中的元素数量
            Ni = len(SFlags)
            # comment: 从 Z0 中提取与 SFlags 相关的列
            Z00 = Z0[:, SFlags]
            # comment: 构建实部和虚部形式的 Z0ri 矩阵
            Z0ri = np.zeros((2 * Nc, 2 * Ni))
            Z0ri[:Nc, :Ni] = np.real(Z00)
            Z0ri[Nc:, Ni:] = np.real(Z00)
            Z0ri[:Nc, Ni:] = -np.imag(Z00)
            Z0ri[Nc:, :Ni] = np.imag(Z00)

            # comment: 构建实部和虚部形式的 Vri 向量
            Vri = np.zeros(2 * Nc)
            Vri[:Nc] = np.real(V0)
            Vri[Nc:] = np.imag(V0)

            # comment: 使用最小二乘法求解 I0ri
            I0ri = lg.lstsq(Z0ri, Vri, rcond=-1)[0]
            # comment: 将 I0ri 转换回复数形式的 I0
            I0 = np.zeros(Nc, dtype=complex)
            I0[SFlags] = I0ri[:Ni] + 1j * I0ri[Ni:]
            # comment: 将计算结果存储到 self.res 中
            self.res['I0'] = I0
            self.res['V0'] = V0
            self.res['Z0'] = Z0
        print('完成常量初始化.')

    def calculate_h_matrix(self):
        """
        计算并存储特征传播函数 H 矩阵及其模态信息。
        H 矩阵用于后续的时域响应计算。

        输出:
        res (dict): 更新的计算结果字典，包含 H, Hlmd, Hm, Vr。
        """
        # comment: 打印开始计算特性矩阵的信息
        print('开始计算特性矩阵。')
        # comment: 从结果 res 中获取 Z 矩阵、导体数量和频率点数量
        Z = self.res['Z']
        Nc = self.res['Nc']
        Ns = self.res['Ns']
        # comment: 获取频率数组
        freqs = self.res['Freq']
        # comment: 初始化 H 矩阵列表
        H = []
        # comment: 初始化 Vr 向量
        Vr = np.zeros(Nc)
        # comment: 判断是否选择了特定的母线
        if ('SelectBuses' not in self.opts.keys() or self.opts['SelectBuses'] == []):
            # comment: 如果没有，则使用所有母线
            BusList = self.opts['BusList']
        else:
            # comment: 如果有，则使用选择的母线
            BusList = self.opts['SelectBuses']
        # comment: 遍历 BusList，获取每个母线的 VBase 值，并存储到 Vr 中
        for i in range(len(BusList)):
            # comp = ce.project.getComponentByKey(BusList[i])
            # comment: 获取拓扑信息
            top = self.ce.topo['components']['/' + BusList[i]]
            # comment: 将 VBase 赋值给 Vr
            Vr[i] = float(top['args']['VBase'])
        # for i in range(len(opts['Trans3pList'])):
        #     Vr[i+len(BusList)] = 1
        # comment: 将 Vr 存储到结果 res 中
        self.res['Vr'] = Vr

        # comment: 找到频率大于等于 f0 的第一个频率点的索引
        kf0 = next(x for x in range(Ns) if freqs[x] >= self.opts['f0'])
        # print(np.diag(Z[kf0]))
        # comment: 计算 H 矩阵在基频点的初始值
        Htemp = Z[kf0] / np.diag(Z[kf0]) * Vr / Vr[:, nax]
        # comment: 对 Htemp 进行特征值分解
        [eig0D, Ti0] = lg.eig(Htemp)
        # comment: 对特征值按绝对值降序排序，并获取排序索引
        idx = np.argsort(-abs(eig0D))
        # comment: 根据排序索引重新排列特征值和特征向量
        eig0 = eig0D[idx]
        Ti0 = Ti0[:, idx]
        # comment: 计算特征向量矩阵的逆
        TiI0 = lg.inv(Ti0)
        # comment: 初始化 Hm 和 Hlmd 列表
        Hm = []
        Hlmd = []
        # comment: 遍历每个 Z 矩阵
        for i in range(len(Z)):
            # comment: 计算当前频率下的 H 矩阵
            Htemp = Z[i] / np.diag(Z[i])[nax, :] * Vr[nax, :] / Vr[:, nax]
            # comment: 将 Htemp 添加到 H 列表
            H.append(Htemp)
            # comment: 使用初始的特征向量矩阵 Ti0 和其逆 TiI0 计算当前 Htemp 的特征值
            Heig = np.diag(TiI0 @ Htemp @ Ti0)
            # comment: 将特征值添加到 Hlmd 列表
            Hlmd.append(Heig)  # EigenValues
            # comment: 创建特征值对角矩阵 Hmtemp
            Hmtemp = np.diag(Heig)
            # comment: 将 Hmtemp 添加到 Hm 列表
            Hm.append(Hmtemp)
        # comment: 将 H, Hlmd, Hm 存储到结果 res 中
        self.res['H'] = H
        self.res['Hlmd'] = Hlmd
        self.res['Hm'] = Hm
        # comment: 获取目标误差
        target_eps = self.opts['target_eps']

        # comment: 打印开始拟合 H 矩阵的信息
        print('   --------Start fitting H----------  ')
        # comment: The vectorfit3 function for H matrix is not explicitly called here.
        # comment: If fitting H matrix is required, it should be called similar to Yc fitting.
        print('完成特性矩阵计算.')

    def calculate_time_domain_response(self, node_injection, t_start=0.2, t_end=0.3, tau=0.03, tend=1, deltaT=0.01):
        """
        计算网络在特定电流注入下的时域电压响应。

        参数:
        node_injection (str): 注入电流的母线键名 (例如 'component_new_bus_3_p_3')。
        t_start (float): 注入电流开始时间。
        t_end (float): 注入电流结束时间。
        tau (float): 电流注入的指数变化时间常数。
        tend (float): 仿真总时长。
        deltaT (float): 时间步长。

        输出:
        tuple: (time (np.array), Vcurve (np.array), Icurve (np.array))
               包含时间数组，计算出的电压曲线和电流曲线。
        """
        # comment: 获取时间点数量
        Nt = int(tend / deltaT)
        # comment: 创建时间数组
        Time0 = deltaT * np.array([i for i in range(Nt)])

        # comment: 从 res 中获取极点 (减去 fws 的调整)
        poles = self.res['PYc'] - 2j * math.pi * self.res['fws']

        # comment: 计算极点数量
        Np = len(poles)
        # comment: 获取 Z 矩阵的残差、常数项和 E 项
        RZs = self.res['RYc']
        CZs = self.res['CYc']
        # comment: 假设这里EZs是EZc，因为EZc通常是与电感相关的系数
        EZs = self.res['EYc']
        # comment: 获取导体数量
        Nc = self.res['Nc']
        # comment: 获取时间点数量
        # Nt already defined

        # comment: 初始化电压曲线 Vcurve 和历史电压 Vhis
        Vcurve = np.zeros((Nc, Nt), dtype=complex)
        Vhis = np.zeros((Nc, Nt), dtype=complex)

        # comment: 获取母线列表
        if ('SelectBuses' not in self.opts.keys() or self.opts['SelectBuses'] == []):
            BusList = self.opts['BusList']
        else:
            BusList = self.opts['SelectBuses']

        # comment: 获取特定母线 node_injection 的索引
        node_idx = BusList.index(node_injection)

        # comment: 初始化电流曲线 Icurve，并添加稳态电流和注入电流
        Icurve = self.res['I0'][:, nax] * np.ones((Nc, Nt), dtype=complex)
        # comment: 调用私有辅助函数 _calculate_time_Icurve_V0
        Icurve[node_idx, :] += self._calculate_time_Icurve_V0(node_idx, Time0, t_start, t_end, tau)

        # comment: 遍历每个极点
        for cp in range(len(poles)):
            # comment: 计算指数函数项
            Ztemp = np.exp(poles[cp] * Time0)[nax, :]
            # comment: 对电流曲线进行卷积操作，模拟电感效应 (这里模式选择'nearest'，原点调整为中心)
            # Ensure the convolution works correctly for all phases
            for i in range(Nc):
                Vhis[i, :] = scipy.ndimage.convolve1d(Icurve[i, :], Ztemp[0, :], axis=-1, mode='nearest',
                                                     origin=0)  # Use 1D conv for each row

            # comment: 对 Vhis 进行操作，插入Vhis[:,0]作为第一列 (adjust for convolution result)
            Vhis_shifted = np.insert(Vhis[:, :-1], 0, Vhis[:, 0].flatten(), axis=1) # Shifted to align for difference calculation

            # comment: 根据矢量拟合的残差项计算电压曲线的贡献
            term1 = -1 / poles[cp] * RZs[:, :, cp] @ (
                    (-np.exp(poles[cp] * deltaT) - (1 - np.exp(poles[cp] * deltaT) / poles[cp] / deltaT)) * Vhis_shifted
                    + (1 + (1 - np.exp(poles[cp] * deltaT) / poles[cp] / deltaT)) * Vhis
            )
            Vcurve += term1

        # comment: 添加常数项和 E*s 项的贡献
        Vcurve += (CZs + 2j * math.pi * self.res['fws'] * EZs) @ Icurve

        # comment: 初始化 IcurveTemp
        IcurveTemp = np.zeros((Nc, Nt), dtype=complex)
        # comment: 将 Icurve 错位赋值给 IcurveTemp
        IcurveTemp[:, 1:] = Icurve[:, :-1]
        # comment: 添加 E 项的微分贡献
        Vcurve += EZs @ (Icurve - IcurveTemp) / deltaT

        print("完成时域响应计算.")
        return Time0, Vcurve, Icurve

    def _calculate_time_Icurve_V0(self, node_idx, timearray, t0, t1, tau):
        """
        计算特定节点在指定时间段内的注入电流曲线。

        参数:
        node_idx (int): 注入电流的母线索引。
        timearray (np.array): 完整的时间数组。
        t0 (float): 注入电流开始时间。
        t1 (float): 注入电流结束时间。
        tau (float): 电流注入的指数变化时间常数。

        返回:
        np.array: 生成的注入电流曲线。
        """
        # comment: 获取时间点数量
        Nt = len(timearray)
        # comment: 计算时间步长
        deltaT = timearray[1] - timearray[0]
        # comment: 获取节点 node 的初始电压 V0
        V0 = self.res['V0'][node_idx]
        # comment: 获取初始阻抗 Z0
        Z0 = self.res['Z0']

        # comment: 初始化电流曲线 Icurve
        Icurve = np.zeros(Nt, dtype=complex)
        # comment: 计算电流幅值 I1 (这里是 V0 / Z0_self)
        I1 = -V0 / Z0[node_idx, node_idx]
        # print(I1)
        # print(np.logical_and(time<t1,time>=t0))
        # comment: 计算时间点 t1-t0 对应的索引数量
        # Nt1 = int((t1-t0)/deltaT) # Not directly used for slicing, boolean indexing is better
        # comment: 获取 t0 到 t1 之间的时间点
        mask_t0_t1 = np.logical_and(timearray < t1, timearray >= t0)
        time1 = timearray[mask_t0_t1]
        # comment: 在 t0 到 t1 之间，电流呈指数上升趋势
        Icurve[mask_t0_t1] = I1 * (1 - np.exp(-1 / tau * (time1 - t0)))
        # comment: 获取大于等于 t1 的时间点
        mask_t2 = timearray >= t1
        time2 = timearray[mask_t2]
        # comment: 在 t1 之后，电流呈指数衰减趋势
        Icurve[mask_t2] = I1 * (1 - np.exp(-1 / tau * (t1 - t0))) * np.exp(-1 / tau * (time2 - t1))
        # comment: 返回计算得到的电流曲线
        return Icurve

    def get_results(self):
        """
        获取所有计算结果。

        返回:
        dict: 包含所有计算结果的字典。
        """
        return self.res

    def plot_time_domain_voltage(self, time, Vcurve, target_bus_key1, target_bus_key2):
        """
        绘制指定节点在时域的电压幅值曲线。

        参数:
        time (np.array): 时间数组。
        Vcurve (np.array): 计算出的电压曲线。
        target_bus_key1 (str): 第一个目标母线的键名。
        target_bus_key2 (str): 第二个目标母线的键名。
        """
        plt.figure()
        # comment: 定义复数 'a'
        a = np.exp(1j * 2 / 3 * math.pi)
        # comment: 定义 Clarke 变换矩阵 T
        T = np.mat([[1, 1, 1], [1, a, a ** 2], [1, a ** 2, a]]) / 3
        # comment: 获取母线列表
        BusList = self.opts['BusList']
        # comment: 计算从 target_bus_key1 到 target_bus_key2 的最短路径
        shortpath0 = self.ce.g.get_all_shortest_paths(self.ce.g.vs.find('/' + target_bus_key1).index,
                                                      self.ce.g.vs.find('/' + target_bus_key2).index)
        # comment: 从最短路径中筛选出在 BusList 中的节点索引
        shortpath = [BusList.index(self.ce.g.vs[i]['name'][1:]) for i in shortpath0[0] if
                     self.ce.g.vs[i]['name'][1:] in BusList]
        # comment: 创建绘图
        # plt.figure() # Already created
        # comment: 初始化 handles 和 labels 列表
        handles = []
        labels = []
        # for i in range(3):
        # plt.plot(Time, abs(Vcp[i,:]+Vcurvep[i,:].A.flatten()))
        # plt.plot(time, np.real(Vcurvep[i,:].A.flatten()*np.exp(1j*2*math.pi*self.res['fws']*time)))
        # for j in range(33):
        # comment: 遍历最短路径中的每个节点
        for j in shortpath:
            # comment: 对电压曲线进行 Clarke 逆变换
            Vcurvep = lg.inv(T)[:, 1] @ Vcurve[j, :][nax, :]
            # comment: 绘制电压幅值与时间的关系曲线
            plt.plot(time, np.abs(Vcurvep[0, :].A.flatten()) * np.sqrt(3 / 2),
                     label=self.ce.project.getComponentByKey(BusList[j]).label)
            # plt.plot(time, np.angle(Vcurvep[0,:].A.flatten())*180/np.pi,label=self.ce.project.getComponentByKey(BusList[j]).label)
        # plt.plot(Time, Vcurve[i,:].T)
        # plt.xlim([0.1,0.4])
        # comment: 显示图例，设置字体
        plt.legend(prop={'family': 'SimHei'})
        # comment: 显示图形
        plt.show()
        print("电压时域曲线绘制完成.")

    def plot_frequency_domain_h_matrix_magnitude(self, target_bus_key1, target_bus_key2):
        """
        绘制指定节点间 H 矩阵的幅频响应曲线。

        参数:
        target_bus_key1 (str): 第一个目标母线的键名，通常作为参考节点。
        target_bus_key2 (str): 第二个目标母线的键名。
        """
        plt.figure()
        # comment: 再次计算从 target_bus_key1 到 target_bus_key2 的最短路径
        shortpath0 = self.ce.g.get_all_shortest_paths(self.ce.g.vs.find('/' + target_bus_key1).index,
                                                      self.ce.g.vs.find('/' + target_bus_key2).index)
        # comment: 从最短路径中筛选出在 opts['BusList'] 中的节点索引
        shortpath = [self.opts['BusList'].index(self.ce.g.vs[i]['name'][1:]) for i in shortpath0[0] if
                     self.ce.g.vs[i]['name'][1:] in self.opts['BusList']]
        freqs = self.res['Freq']
        # comment: 遍历最短路径中的部分节点，绘制 H 矩阵的幅值与频率的关系曲线
        for k in shortpath[2:11]:  # Example: plot for specific nodes within the path
            plt.plot(freqs, 5 * np.array([np.abs(self.res['H'][i][k, shortpath[0]]) for i in range(len(freqs))]),
                     label=str(self.ce.project.getComponentByKey(self.opts['BusList'][k]).label))
        # comment: 显示图例，设置字体
        plt.legend(prop={'family': 'SimHei'})
        # comment: X 轴使用对数刻度
        plt.xscale('log')
        # comment: 设置 Y 轴范围
        plt.ylim([0, 1])
        # comment: 显示图形
        plt.show()
        print("H矩阵幅频响应曲线绘制完成.")

    def plot_time_domain_current(self, time):
        """
        绘制时域电流幅值曲线。

        参数:
        time (np.array): 时间数组。
        """
        plt.figure()
        # comment: 绘制电流幅值与时间的关系曲线
        # Assuming Icurve is available in self.res after calculate_time_domain_response
        if 'Icurve' in self.res:
            plt.plot(time, np.abs(self.res['Icurve'][self.opts['BusList'].index('YOUR_BUS_KEY_FOR_PLOTTING_CURRENT'), :]))
        else:
            print("Error: Icurve not found in results. Please run calculate_time_domain_response first.")
        # plt.plot(Time, Vcurve[i,:].T)
        # plt.xlim([2.95,3.3])
        # comment: 显示图形
        plt.show()
        print("电流时域曲线绘制完成.")


def main():
    """
    主函数，用于执行电力网络特性计算和瞬态分析的整个流程。
    """
    # comment: 实例化 NetworkCalculation_TransProb 类，加载默认配置
    network_analyzer = NetworkCalculation_TransProb()

    # 第一步：调用 configure_simulation 函数，配置仿真环境
    network_analyzer.configure_simulation()
    print("步骤1：仿真环境配置完成。")

    # 第二步：调用 calculate_frequency_domain_matrices 函数，计算并拟合频域矩阵
    network_analyzer.calculate_frequency_domain_matrices()
    print("步骤2：频域矩阵计算与拟合完成。")

    # 第三步：调用 calculate_stable_case 函数，计算稳态工况下的初始电流和电压
    network_analyzer.calculate_stable_case()
    print("步骤3：稳态工况计算完成。")

    # 第四步：调用 calculate_h_matrix 函数，计算特性传播函数 H 矩阵
    network_analyzer.calculate_h_matrix()
    print("步骤4：H矩阵计算完成。")

    # 第五步：调用 calculate_time_domain_response 函数，计算时域响应
    # Define parameters for time domain simulation
    node_to_inject = 'component_new_bus_3_p_3' # Replace with actual bus key
    time_start_injection = 0.2
    time_end_injection = 0.3
    injection_tau = 0.03
    total_sim_time = 1
    time_step = 0.01

    time_array, Vcurve, Icurve = network_analyzer.calculate_time_domain_response(
        node_injection=node_to_inject,
        t_start=time_start_injection,
        t_end=time_end_injection,
        tau=injection_tau,
        tend=total_sim_time,
        deltaT=time_step
    )
    network_analyzer.res['Icurve'] = Icurve # Store Icurve in results for plotting
    print("步骤5：时域响应计算完成。")

    # 第六步：调用 plot_time_domain_voltage 函数，绘制时域电压曲线
    # Define target buses for plotting voltage. Replace with actual keys.
    plot_bus_key1 = 'component_new_bus_3_p_3'
    plot_bus_key2 = 'ef8377a5-b832-4b76-b025-a1dd380bd21a'
    network_analyzer.plot_time_domain_voltage(time_array, Vcurve, plot_bus_key1, plot_bus_key2)
    print("步骤6：时域电压曲线绘制完成。")

    # 第七步：调用 plot_frequency_domain_h_matrix_magnitude 函数，绘制 H 矩阵幅频响应曲线
    network_analyzer.plot_frequency_domain_h_matrix_magnitude(plot_bus_key1, plot_bus_key2)
    print("步骤7：H矩阵幅频响应曲线绘制完成。")

    # Optional: Additional plotting like current if needed
    # network_analyzer.plot_time_domain_current(time_array)


if __name__ == '__main__':
    main()