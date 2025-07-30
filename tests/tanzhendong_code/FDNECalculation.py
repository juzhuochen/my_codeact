# %%
#comment: 导入 numpy 库，用于进行科学计算，尤其是数组操作
import numpy as np
#comment: 从 numpy.linalg 导入 lg，用于进行线性代数运算，如矩阵求逆、特征值分解等
import numpy.linalg as lg
#comment: 定义 nax，用于在 numpy 数组操作中添加新维度
nax = np.newaxis
#comment: 从 vectfit3 模块导入 vectfit3, full2full, tri2full, ss2pr 函数，这些是向量拟合相关的核心函数
# 假设 vectfit3 模块已在环境中或当前目录
from vectfit3 import vectfit3, full2full, tri2full, ss2pr
#comment: 从 RPdriver 模块导入 RPdriver 类，可能用于无源性强制执行
# 假设 RPdriver 模块已在环境中或当前目录
from RPdriver import RPdriver
#comment: 从 time 模块导入 time 函数，用于计时
from time import time

#comment: 导入 math 模块，提供数学函数
import math
#comment: 导入 cmath 模块，提供复数数学函数
import cmath
#comment: 导入 scipy.constants 模块并命名为 const，提供物理常数
from scipy import constants as const
#comment: 导入 os 模块，提供与操作系统交互的功能
import os
#comment: 导入 re 模块，提供正则表达式操作
import re
#comment: 导入 matplotlib.pyplot 模块
import matplotlib.pyplot as plt
#comment: 导入 tkinter 库，用于创建图形用户界面
import tkinter
#comment: 导入 tkinter.filedialog 模块，用于文件选择对话框
import tkinter.filedialog

class FDNECalculation:
    """
    FDNECalculation 类用于执行频域网络提取 (FDNE) 的计算，
    包括数据加载、向量拟合、模型降阶以及可选的无源性强制执行。

    属性:
    - opts (dict): 存储计算过程中的各种配置选项。
    - freqs (numpy.ndarray): 输入数据的频率数组。
    - Ys (numpy.ndarray): 输入数据的Y（导纳）或Z（阻抗）矩阵数组，已转换为Y矩阵形式。
    - calculation_results (dict): 存储计算、拟合和无源性强制执行后的所有结果。
                                  示例键值对:
                                  - 'Nc': 端口数量
                                  - 'Ns': 频率点数量
                                  - 'Yc': 变换后的 Yc 矩阵
                                  - 'Y': 原始 Y 矩阵
                                  - 'Q': 变换矩阵
                                  - 'Freq': 频率数组
                                  - 'weightFreq': 频率权重
                                  - 'SER': 状态空间模型 (A, B, C, D, E)
                                  - 'PYc': Yc 的极点
                                  - 'RYc': Yc 的残差
                                  - 'CYc': Yc 的常数项
                                  - 'EYc': Yc 的线性项
                                  - 'fitYc': Yc 的拟合数据
                                  - 'RMSErrYc': Yc 的均方根误差
                                  - 'PY': 最终模型的极点
                                  - 'RY': 最终模型的残差
                                  - 'CY': 最终模型的常数项
                                  - 'EY': 最终模型的线性项
    - rp_driver_log (dict): 无源性强制执行过程中的日志信息。
    """

    def __init__(self):
        """
        构造函数，初始化 FDNECalculation 类的实例。
        设置默认选项，并初始化存储结果和日志的字典。
        """
        self.opts = self._default_options()
        self.freqs = None
        self.Ys = None
        self.calculation_results = {}
        self.rp_driver_log = {}

    def _default_options(self):
        """
        comment: 定义 defaultOptions 函数，用于设置默认参数选项。
        """
        opts = {};

        #comment: 设置曲线拟合的目标误差
        opts['target_eps'] = 0.002;
        #comment: 设置 Yc 拟合中使用的极点数量
        opts['NpYc'] = 20
        #comment: 设置 Yc 拟合的误差容忍度
        opts['ErYc'] = 0.002
        #comment: 设置权重列表，用于频域加权，格式为 [[频率1, 权重1], [频率2, 权重2], ...]
        opts['Weighting'] = [[0,1],[48,3],[51, 1]];
        #comment: 设置权重因子，影响误差计算中权重的敏感度
        opts['WeightFactor'] = 0.5;

        #comment: 设置 Yc 拟合的第一阶段迭代次数
        opts['NiterYc1'] = 5
        #comment: 设置 Yc 拟合的第二阶段迭代次数
        opts['NiterYc2'] = 3
        
        #comment: 设置是否显示 Yc 向量拟合的可视化结果
        opts['ViewYcVF'] = False;
        
        #comment: 初始化一个空的字典，用于存储向量拟合的详细选项
        opts['vfopts'] = {};
        #comment: 设置向量拟合是否使用松弛的非平凡性约束
        opts['vfopts']['relax']=True;      #Use vector fitting with relaxed non-triviality constraint
        #comment: 设置向量拟合是否强制极点稳定
        opts['vfopts']['stable']=True;     #Enforce stable poles
        #comment: 设置渐近行为：1 表示拟合包含常数项 D，不包含 E * s 项
        opts['vfopts']['asymp'] = 1;      #Fitting includes D(constant), not include E * s 
        #comment: 设置是否禁用第一级绘图
        opts['vfopts']['spy1']=False;       #No plotting
        #comment: 设置是否启用第二级绘图
        opts['vfopts']['spy2']=True; 
        #comment: 设置 X 轴是否使用对数刻度
        opts['vfopts']['logx']=True; 
        #comment: 设置 Y 轴是否使用对数刻度
        opts['vfopts']['logy']=True; 
        #comment: 设置是否绘制误差图
        opts['vfopts']['errplot']=True;
        #comment: 设置是否绘制相位图
        opts['vfopts']['phaseplot']=True;

        #comment: 设置是否跳过极点计算
        opts['vfopts']['skip_pole']=False; 
        #comment: 设置是否跳过残差计算
        opts['vfopts']['skip_res']=True;
        #comment: 设置是否生成对角化 A 矩阵的状态空间模型
        opts['vfopts']['cmplx_ss']=True;  # =1 --> Will generate state space model with diagonal A
        #comment: 设置是否显示图例
        opts['vfopts']['legend']=True;
        #comment: 设置绘图是否阻塞，即显示后暂停程序执行
        opts['vfopts']['block'] = True;

        #comment: 新增无源性强制执行相关选项
        opts['EnabPassEnf'] = False; #comment: 是否启用无源性强制执行
        opts['StartPass'] = 0; #comment: 无源性检查起始频率
        opts['EndPass'] = 1e10; #comment: 无源性检查结束频率
        opts['Nint'] = 21; #comment: 无源性检查频率点数量
        opts['type'] = 'Y'; #comment: 数据类型
        opts['Niter_out_Pass'] = 5; #comment: 无源性外层迭代次数
        opts['Niter_in_Pass'] = 2; #comment: 无源性内层迭代次数

        #comment: 特征值计算设置
        opts['EigMaxIter'] = 20;
        opts['EigEps'] = 1e-8;

        #comment: 返回包含所有默认选项的字典
        return opts

    def _is_number(self, s):
        """
        comment: 定义 is_number 函数，用于检查输入字符串是否可以转换为浮点数
        """
        try:
            float(s)
            #comment: 如果成功，返回 True
            return True
        #comment: 如果转换失败（捕获 ValueError 异常），则继续尝试其他转换方式
        except ValueError:
            pass
        
        #comment: 尝试使用 unicodedata 模块的 numeric 方法检查字符串是否表示数字
        try:
            import unicodedata
            unicodedata.numeric(s)
            #comment: 如果成功，返回 True
            return True
        #comment: 如果转换再次失败（捕获 TypeError 或 ValueError 异常），则返回 False
        except (TypeError, ValueError):
            pass
        
        #comment: 如果所有尝试都失败，则返回 False
        return False

    def _calculate_yz_data(self, ZYData, data_type='Y'):
        """
        comment: 定义 CalYZData 函数，用于处理原始 Y/Z 矩阵数据并返回频率和 Y/Z 矩阵
        """
        #comment: 从 ZYData 中提取端口数量 Nc，假设其在第二个列表的第一个元素
        Nc = int(ZYData[1][0]); # 端口数量
        #comment: 从 ZYData 中提取极点数量 Ns，假设其在第三个列表的第一个元素
        Ns = int(ZYData[2][0]); # 极点数量
        #comment: 定义数据正式开始的行数偏移
        SP = 4; #数据正式开始位置

        #comment: 初始化一个 numpy 数组 freqs，用于存储频率
        freqs = np.zeros(Ns);
        #comment: 初始化一个 numpy 数组 ZYs，用于存储 Y/Z 矩阵，数据类型为复数
        ZYs = np.zeros((Nc, Nc, Ns),dtype=complex);

        #comment: 循环遍历每个极点（频率点）
        for i in range(Ns):
            #comment: 提取当前频率
            freqs[i] = ZYData[SP + i * (Nc * Nc + 1)][0]
            #comment: 嵌套循环，提取当前频率下的 Y/Z 矩阵元素
            for j in range(Nc):
                for k in range(Nc):
                    #comment: 提取实部和虚部并构成复数，存入 ZYs 数组
                    ZYs[j,k,i] = ZYData[SP + i * (Nc * Nc + 1) + 1 + j * Nc + k][0] + 1j * ZYData[SP + i * (Nc * Nc + 1) + 1 + j * Nc + k][1];
        
        #comment: 如果类型是 'Z' (阻抗)，则将 Z 矩阵转换为 Y 矩阵（导纳矩阵），即求逆
        if(data_type=='Z'):
            for i in range(Ns):
                ZYs[:,:,i] = lg.inv(ZYs[:,:,i]);

        #comment: 返回频率数组和 Y/Z 矩阵数组
        return freqs, ZYs

    def load_data(self, filename=None, data_type='Y', data_format='YZ'):
        """
        comment: 加载频响数据，支持 Y/Z 数据和 Harm 数据。
        参数:
        - filename (str, optional): 数据文件路径。如果为 None，则弹出文件选择对话框。
        - data_type (str, optional): 数据类型，'Y' 表示导纳，'Z' 表示阻抗。
                                     当 data_format 为 'YZ' 时有效。
        - data_format (str, optional): 数据格式，'YZ' 表示 Y/Z 格式数据，'Harm' 表示 Harm 格式数据。
        """
        if filename is None:
            root = tkinter.Tk()
            root.withdraw() # 隐藏主窗口
            #comment: 敏感信息替换：文件路径占位符
            default_dir = "FILE_PATH_PLACEHOLDER"
            filename = tkinter.filedialog.askopenfilename(title=u'选择输入文件', initialdir=(os.path.expanduser(default_dir)))
            root.destroy()
            
        #comment: 如果用户取消选择文件，则退出函数
        if not filename:
            print("未选择文件，操作取消。")
            return

        with open(filename, 'r') as stream:
            ZYDataRaw = stream.read()
            ZYData = [[float(j) if self._is_number(j) else j for j in re.split(r'\s+', i.strip())] for i in ZYDataRaw.splitlines()]

        if data_format == 'YZ':
            self.freqs, self.Ys = self._calculate_yz_data(ZYData, data_type)
        elif data_format == 'Harm':
            self.freqs, self.Ys = self._load_harm_data(ZYData)
        else:
            raise ValueError(f"不支持的数据格式: {data_format}")

    def _load_harm_data(self, ZYData):
        """
        comment: 定义 LoadHarmData 函数，用于加载特定格式的 Harm 数据
        """
        #comment: 初始化变量和列表用于解析数据
        NsPoss = []; #comment: 存储每个极点数据起始行的索引
        #comment: 遍历数据行，查找长度为 3 的行（通常表示频率和Z11的实部虚部），记录其索引
        for i in range(1,len(ZYData)):
            if(len(ZYData[i])==3):
                NsPoss.append(i);
        #comment: 极点数量 Ns 等于记录的起始行数量
        Ns = len(NsPoss)
        #comment: 数据行块的长度 Nc
        Nc = NsPoss[1] - NsPoss[0];
        #comment: 初始化频率数组
        freqs = np.zeros(Ns);
        #comment: 初始化 Z 矩阵数组，类型为复数
        Zs = np.zeros((Nc, Nc, Ns),dtype=complex);

        #comment: 循环遍历每个极点数据块
        for i in range(Ns):
            #comment: 提取频率
            freqs[i] = ZYData[NsPoss[i]][0];
            #comment: 嵌套循环，提取 Z 矩阵的元素
            for j in range(Nc):
                #comment: 如果是第一行（通常是 Z11）
                if(j==0):
                    #comment: 提取 Z11 的实部和虚部
                    Zs[0,0,i] = ZYData[NsPoss[i]][1] + 1j*ZYData[NsPoss[i]][2];
                #comment: 对于后续的行，提取 Z 矩阵的下三角/对称部分元素
                else:
                    for k in range(j+1):
                        #comment: 提取实部和虚部
                        Zs[j,k,i] = ZYData[NsPoss[i]+j][2*k] + 1j * ZYData[NsPoss[i]+j][2*k+1];
                        #comment: 由于 Z 矩阵通常是对称的，直接复制到对称位置
                        Zs[k,j,i] = ZYData[NsPoss[i]+j][2*k] + 1j * ZYData[NsPoss[i]+j][2*k+1];
        
        #comment: 将 Z 矩阵转换为 Y 矩阵（求逆）
        for i in range(Ns):
            Zs[:,:,i] = lg.inv(Zs[:,:,i]);

        #comment: 返回频率和转换后的 Y 矩阵
        return freqs, Zs


    def _calculate_transform_matrix(self, Ys):
        """
        comment: 定义 calculateTransformMatrix 函数，用于计算使导纳矩阵条件数最大的频率点以及相应的变换矩阵 Q
        """
        #comment: 初始化最大条件数 ks0 和对应频率点的索引 f0
        ks0 = 0;
        f0 = 0;
        #comment: 遍历每个频率点的导纳矩阵
        for i in range(Ys.shape[2]):
            #comment: 计算当前导纳矩阵的特征值 w 和特征向量 v
            w, v = lg.eig(Ys[:,:,i])
            #comment: 计算条件数 ks（最大特征值绝对值与最小特征值绝对值之比）
            ks = max(np.abs(w)) / min(np.abs(w));
            #comment: 如果当前条件数大于已记录的最大条件数
            if(ks > ks0):
                #comment: 更新 f0 和 ks0
                f0 = i;
                ks0 = ks;
        #comment: 在条件数最大的频率点 f0 处，重新计算特征值 w 和特征向量 v
        w, v = lg.eig(Ys[:,:,f0])
        #comment: 初始化变换矩阵 T0，与特征向量 v 的形状相同
        T0 = np.zeros(v.shape);
        #comment: 遍历每个特征向量（列）
        for i in range(v.shape[1]):
            #comment: 获取当前特征向量
            vcol = v[:,i];
            #comment: 计算旋转角度 theta，用于使得特征向量的旋转使得其变为实数（或最小化虚部）
            theta = 1/2*math.atan2(2 * sum(vcol.real * vcol.imag), sum(vcol.real**2 - vcol.imag**2))
            #comment: 计算旋转后的向量实部平方和
            ft1 = sum((vcol.real*math.sin(theta) + vcol.imag*math.cos(theta))**2)
            #comment: 计算旋转角度为 theta + pi/2 后的向量实部平方和
            ft2 = sum((vcol.real*math.sin(theta + math.pi/2) + vcol.imag*math.cos(theta + math.pi/2))**2)
            #comment: 如果 ft2 小于 ft1，说明 theta + pi/2 是更好的旋转角度
            if(ft2 < ft1):
                theta = theta + math.pi/2;
            #comment: 将特征向量旋转 theta 角度使其变为实数向量，并存入 T0
            T0[:,i] = np.real(vcol * cmath.exp(1j * theta));
        
        #comment: 对 T0 进行奇异值分解 (SVD)
        U, S, V = lg.svd(T0, full_matrices =True); 
        #comment: 计算正交变换矩阵 Q = U * V.conj().T
        Q = U@V.T.conj()

        #comment: 返回条件数最大的频率点索引 f0 和变换矩阵 Q
        return f0, Q

    def _lm_step(self, x, target, sigma, dtype=float):
        """
        comment: 定义 LMstep 函数，执行 Levenberg-Marquardt 算法的一个步长
        """
        #comment: 获取输入向量 x 的长度
        n = len(x);
        #comment: 减去 1，因为 x 最后一个元素是 lambda
        n = n-1;
        #comment: 提取前 n 个元素作为 t (特征向量)
        t = x[:n];
        #comment: 提取最后一个元素作为 lmd (特征值)
        lmd = x[n];
        #comment: 初始化 F 向量，用于存储方程组的残差
        F = np.zeros(n+1,dtype=dtype);

        #comment: 计算 F 的前 n 个分量 (A - lambda * I) * t
        F[0:n] = (target - lmd*np.eye(n)) @ t;
        # F[n] = lg.norm(t)**2 - 1; #comment: 这一行被注释，表示 t 的范数减 1，为标准化条件
        #comment: 计算 F 的最后一个分量，t 的平方和减 1 (另一种标准化条件)
        F[n] = np.sum(t*t) - 1;
        #comment: 初始化雅可比矩阵 J
        J = np.zeros((n+1,n+1),dtype=dtype);
        #comment: 填充 J 的左上角 (A - lambda * I)
        J[:n,:n] = (target - lmd*np.eye(n));
        #comment: 填充 J 的右上角 -t
        J[:n,n] = -t;
        #comment: 填充 J 的左下角 2 * t (来自标准化条件对 t 的偏导)
        J[n,:n] = 2 * t;
        #comment: 填充 J 的右下角 0 (来自标准化条件对 lambda 的偏导)
        J[n,n] = 0;

        #comment: 计算近似 Hessian 矩阵 H = J.T * J
        H = J.T.conj() @ J;
        
        #comment: 计算下一步的 xn = x - (H + sigma * diag(diag(H)))^-1 * J.T * F
        xn = x - lg.solve(H+sigma * np.diag(np.diag(H)),J.T.conj()@F);
        
        #comment: 从 xn 中提取新的 t 和 lmd
        t = xn[:n];
        lmd = xn[n];
        #comment: 更新 F 的前 n 个分量
        F[0:n] = (target - lmd*np.eye(n)) @ t;
        #comment: 更新 F 的最后一个分量
        F[n] = np.sum(t*t) - 1;
        
        #comment: 返回更新后的 xn 和对应的 F
        return xn,F

    def _nr_step(self, x, target, dtype=float):
        """
        comment: 定义 NRstep 函数，执行牛顿-拉夫逊 (Newton-Raphson) 算法的一个步长
        """
        #comment: 获取输入向量 x 的长度
        n = len(x);
        #comment: 减去 1，因为 x 最后一个元素是 lambda
        n = n-1;
        #comment: 提取前 n 个元素作为 t (特征向量)
        t = x[:n];
        #comment: 提取最后一个元素作为 lmd (特征值)
        lmd = x[n];
        #comment: 初始化 F 向量，用于存储方程组的残差
        F = np.zeros(n+1,dtype=dtype);
        #comment: 计算 F 的前 n 个分量 (A - lambda * I) * t
        F[0:n] = (target - lmd*np.eye(n)) @ t;
        #comment: 计算 F 的最后一个分量，t 的范数平方减 1 (标准化条件)
        F[n] = lg.norm(t)**2 - 1;
        #comment: 初始化雅可比矩阵 J
        J = np.zeros((n+1,n+1),dtype=dtype);
        #comment: 填充 J 的左上角 (A - lambda * I)
        J[:n,:n] = (target - lmd*np.eye(n));
        #comment: 填充 J 的右上角 -t
        J[:n,n] = -t;
        #comment: 填充 J 的左下角 2 * t (来自标准化条件对 t 的偏导)
        J[n,:n] = 2 * t;
        #comment: 填充 J 的右下角 0 (来自标准化条件对 lambda 的偏导)
        J[n,n] = 0;
        
        #comment: 计算下一步的 xn = x - J^-1 * F
        xn = x - lg.solve(J,F);

        #comment: 返回更新后的 xn 和对应的 F
        return xn,F

    def _eigen_mat_nr(self, target, eig0, Ti0, opts={}):
        """
        comment: 定义 eigenMat_NR 函数，用于使用牛顿-拉夫逊或 Levenberg-Marquardt 方法计算矩阵的特征值和特征向量
        """
        
        #comment: 定义默认选项
        opts1 = {}
        opts1['EigMaxIter'] = 10; #comment: 最大迭代次数
        opts1['EigEps'] = 1e-8; #comment: 收敛容差
        opts1['dtype'] = float; #comment: 数据类型
        #comment: 使用用户提供的 opts 更新默认选项
        opts1.update(opts);
        
        #comment: 从 opts1 中获取最大迭代次数和容差
        maxIter = opts1['EigMaxIter'] 
        eps = opts1['EigEps']
        
        # 目标矩阵先除以二范数以适配eps #comment: 这行注释表示原始代码可能曾进行归一化处理，但目前以下代码并未对target进行归一化。
        TN = lg.norm(target); #comment: 计算目标矩阵的二范数
        # target1 = target / TN; #comment: 归一化目标矩阵，但此行被注释掉
        # eig1 = eig0 / TN; #comment: 归一化初始特征值，但此行被注释掉

        target1 = target; #comment: 使用原始目标矩阵
        eig1 = eig0; #comment: 使用原始初始特征值
        
        method_type = 1 #comment: 设置算法类型，1 代表 Levenberg-Marquardt
        if(method_type==0):
            # 目前从文献中找到的NR法求连续变化的矩阵特征值方法有缺陷，可能会出现重复的Ti列向量。暂不采用了。 #comment: 这段注释解释了为何类型0（NR法）被弃用。
            n = len(eig1); #comment: 获取特征值数量
            eigL = np.zeros(n,dtype=opts1['dtype']); #comment: 初始化特征值结果数组
            Ti = np.zeros((n,n),dtype=opts1['dtype']); #comment: 初始化特征向量结果矩阵
            x = np.zeros(n+1, dtype=opts1['dtype']) #comment: 初始化迭代变量 x
            #comment: 循环计算每个特征值和特征向量
            for k in range(n):
                lmd = eig1[k]; #comment: 初始特征值
                Tik = Ti0[:,k]; #comment: 初始特征向量
                x[:n] = Tik; #comment: 将特征向量放入 x
                x[n] = lmd; #comment: 将特征值放入 x
                F = 999; #comment: 初始化 F
                #comment: 执行迭代
                for Iter in range(maxIter):
                    xn, F = self._nr_step(x, target1); #comment: 执行 NR 步长
                    if(np.sum(np.abs(F)) < eps*lg.norm(target)): #comment: 检查收敛条件
                        break
                    x = xn; #comment: 更新 x
                eigL[k] = xn[n]; #comment: 存储计算出的特征值
                Ti[:,k] = xn[:n]; #comment: 存储计算出的特征向量
                # if(np.sum(np.abs(F)) > eps): #comment: 检查是否收敛（被注释）
                #     print('column '+str(k)+' failes to converge for eigenvalue calculation. error='+str(np.sum(np.abs(F)))+"---"+str(eps));
            err = lg.norm(lg.solve(Ti , target1) @ Ti - np.diag(eigL)); #comment: 计算误差
            # eigL = eigL * TN; #comment: 反归一化特征值（被注释）

        elif(method_type==1):
            # LM方法 #comment: 类型1，使用 Levenberg-Marquardt 方法
            n = len(eig1); #comment: 获取特征值数量
            eigL = np.zeros(n,dtype=opts1['dtype']); #comment: 初始化特征值结果数组
            Ti = np.zeros((n,n),dtype=opts1['dtype']); #comment: 初始化特征向量结果矩阵
            x = np.zeros(n+1, dtype=opts1['dtype']) #comment: 初始化迭代变量 x
            #comment: 循环计算每个特征值和特征向量
            for k in range(n):
                lmd = eig1[k]; #comment: 初始特征值
                Tik = Ti0[:,k]; #comment: 初始特征向量
                x[:n] = Tik; #comment: 将特征向量放入 x
                x[n] = lmd; #comment: 将特征值放入 x
                F = 999; #comment: 初始化 F
                Fold=F; #comment: 前一次的 F 范数
                sigma = 1e-4; #comment: LM 算法的阻尼参数
                #comment: 执行迭代
                for Iter in range(maxIter):
                    xn, F = self._lm_step(x, target1, sigma); #comment: 执行 LM 步长
                    if(lg.norm(F) < eps*lg.norm(target)*1e-3): #comment: 检查收敛条件
                        break
                    if(lg.norm(F)< Fold and sigma > 1e-14) : #comment: 如果误差减小且 sigma 不太小，则减小 sigma
                        sigma = sigma / 10;
                    elif(lg.norm(F)> Fold and sigma < 1): #comment: 如果误差增大且 sigma 不太大，则增大 sigma
                        sigma = sigma * 5;
                    Fold = lg.norm(F); #comment: 更新 Fold
                    x = xn; #comment: 更新 x
                eigL[k] = xn[n]; #comment: 存储计算出的特征值
                Ti[:,k] = xn[:n]; #comment: 存储计算出的特征向量
                # if(lg.norm(F) > eps*lg.norm(target)): #comment: 检查是否收敛（被注释）
                #     print('column '+str(k)+' failes to converge for eigenvalue calculation. error='+str(lg.norm(F))+"---"+str(eps));
            err = lg.norm(lg.solve(Ti , target1) @ Ti - np.diag(eigL)); #comment: 计算误差
            # err = lg.norm(F); #comment: 另一种误差计算方式（被注释）
            # eigL = eigL * TN; #comment: 反归一化特征值（被注释）

        #comment: 返回计算出的特征值、特征向量矩阵和误差
        return eigL, Ti, err

    def _mor(self, poles, asymp, delay, s, f, weight, eps):
        """
        comment: 定义 mor 函数，执行多输入多输出 (MIMO) 情况下模型降阶 (MOR) 过程，与 mor_single 类似，但处理多通道数据
        参数:
        - poles: N #comment: 极点，数量为 N
        - asymp: 0 - not D, E; 1 - only D; 2 - D and E #comment: 渐近项选项
        - delay: N #comment: 延迟项，数量为 N
        - s: Ns #comment: 复频率，数量为 Ns
        - f: Ns #comment: 频响数据，维度为 Nc x Ns
        - weight: 1*Ns #comment: 权重，维度为 1xNs
        - eps: float #comment: 模型降阶的容差
        """

        N = len(poles); #comment: 获取极点数量
        Ns = len(s); #comment: 获取复频率点数量
        Nc = f.shape[0]; #comment: 获取通道/端口数量 (f 的第一维度)

        #comment: 初始化 cindex 数组，用于标记极点类型
        cindex = np.zeros((N), dtype=np.int_);
        m = 0; #comment: 循环计数器
        while m < N: #comment: 遍历极点
            if poles[m].imag != 0: #comment: 如果极点有虚部，说明是复数极点
                #comment: 检查当前复数极点和下一个极点是否为复共轭对
                if poles[m].real!=poles[m+1].real or poles[m].imag!=-poles[m+1].imag:
                    #comment: 如果不是复共轭对，则抛出 ValueError
                    raise ValueError('Initial poles '+str(m)+' and '+str(m+1)\
                                    +' are subsequent but not complex conjugate.')
                #comment: 标记为复共轭极点对的第一个
                cindex[m]   = 1
                #comment: 标记为复共轭极点对的第二个
                cindex[m+1] = 2
                m += 1 #comment: 跳过下一个极点
            m += 1 #comment: 移动到下一个极点

        #comment: 初始化 Dk 矩阵，用于存储基函数的值
        Dk = np.zeros((Ns,N+asymp),dtype = complex);
        #comment: 初始化 A 矩阵，用于线性最小二乘问题
        A = np.zeros((2 * Ns,N+asymp));
        #comment: 遍历极点，构建基函数
        for m in range(N):
            if cindex[m]==0: # real pole #comment: 如果是实极点
                Dk[:,m] =  np.exp( - delay[m] * s ) / (s-poles[m])
            elif cindex[m]==1: # complex pole pair, 1st part #comment: 如果是复共轭极点对的第一个
                Dk[:,m]   =  np.exp( - delay[m] * s )*(1/(s-poles[m]) +  1/(s-np.conj(poles[m])))
                Dk[:,m+1] = np.exp( - delay[m] * s ) * (1j/(s-poles[m]) - 1j/(s-np.conj(poles[m])))
        if asymp>0: #comment: 如果包含渐近项
            Dk[:,N] = 1 #comment: 对应常数项 D 的基函数为 1
            if asymp==2: #comment: 如果包含线性项 E*s
                Dk[:,N+1] = s #comment: 对应线性项 E 的基函数为 s

        #comment: 填充 A 矩阵的实部和虚部，并乘以权重
        A[:Ns,:] = weight[0,:,nax] * Dk.real
        A[Ns:,:] = weight[0,:,nax] * Dk.imag
        #comment: 初始化 B 向量，用于存储频响数据的实部和虚部，并乘以权重 (多通道)
        B = np.zeros((2*Ns,Nc))
        B[:Ns,:] = weight[0,:,nax] * f.real.T
        B[Ns:,:] = weight[0,:,nax] * f.imag.T


        # solve the linear system #comment: 求解线性系统
        #comment: 计算每列的 L2 范数用于缩放
        Escale = np.linalg.norm(A, axis=0)
        A /= Escale[nax,:] #comment: 对 A 矩阵进行列归一化

        #comment: 对 A 进行奇异值分解 (SVD)
        U, S, V = lg.svd(A, full_matrices = False);
        # print(S) #comment: 调试打印奇异值 (被注释)

        temp = 0; #comment: 临时变量，用于累积小奇异值
        rnk = len(S); #comment: 初始秩
        for i in range(len(S)): #comment: 从最小奇异值开始遍历
            if(lg.norm([abs(S[-i]),temp]) < eps * lg.norm(S)): #comment: 如果当前奇异值加上累积的小奇异值小于阈值
                temp = lg.norm([abs(S[-i]),temp]); #comment: 累积小奇异值
                S[-i] = 0; #comment: 将该奇异值置为零
                rnk -= 1; #comment: 减小秩

        #comment: 重构 A 矩阵，此处并非严格重构
        a1 = U @ np.diag(S) @ V

        # c = lg.lstsq(a1,B,rcond=-1)[0] #comment: 被注释的代码，原本用于直接求解最小二乘

        sol = np.zeros((N+asymp,Nc)) #comment: 存储最小二乘解 (多通道)
        
        nz = []; #comment: 存储非零元素的索引
        temp = 0; #comment: 临时变量，用于计数有效极点
        for i in range(N): #comment: 遍历极点
            if ((cindex[i] == 2) and (temp + 2 <= rnk)): #comment: 如果是复共轭对的第二个，且剩余秩足够处理一对
                temp += 2; #comment: 增加2个有效极点
                nz.append(i-1); #comment: 添加复共轭对的第一个极点索引
                nz.append(i); #comment: 添加复共轭对的第二个极点索引
        for i in range(N): #comment: 再次遍历极点
            if ((temp+1 <= rnk) and ((cindex[i] == 0) or (cindex[i] == 1)) and (i not in nz) ): #comment: 如果是实极点或复共轭对的第一个，且未被加入 nz 且剩余秩足够处理一个极点
                temp += 1; #comment: 增加1个有效极点
                nz.append(i); #comment: 添加极点索引

        nz = np.array(nz,dtype = int); #comment: 将 nz 转换为 numpy 数组

        #comment: 求解截断的最小二乘问题，只对有效的列进行求解
        sol1 = lg.lstsq(a1[:, nz], B, rcond=-1)[0]
        # sol[nz,0] = sol1.flatten(); #comment: 被注释的代码
        sol[nz,:] = sol1; #comment: 将求解结果赋值给 sol 对应位置 (多通道)
        sol /= Escale[:,nax] #comment: 将 sol 除以 Escale (反归一化)

        idx = nz[np.argsort(nz)] #comment: 对 nz 进行排序，得到最终有效的极点索引

        
        SERC = np.zeros((Nc,N), dtype=np.complex_) #comment: 初始化 SERC (残差) 矩阵 (Nc x N)
        poles_new = np.array([], dtype = complex) #comment: 初始化新的极点数组
        for m in range(N): #comment: 遍历原始极点

            if cindex[m]==0: #comment: 如果是实极点
                SERC[:,m] = sol[m,:].T #comment: 残差直接为 sol 中的值 (转置以匹配 Nc x N 维度)
            if cindex[m]==1 and ((m+1) in idx): #comment: 如果是复共轭对的第一个，且其配对的极点也在有效索引中
                SERC[:,m]   = sol[m,:].T + 1j*sol[m+1,:].T #comment: 计算复残差
                SERC[:,m+1] = sol[m,:].T - 1j*sol[m+1,:].T #comment: 计算共轭复残差
            elif cindex[m]==1: #comment: 如果是复共轭对的第一个，但其配对的极点不在有效索引中
                SERC[:,m] = sol[m,:].T;
                SERC[:,m+1] = sol[m,:].T;

            # if cindex[m]==2 and (m in idx) and ((m-1) not in idx): #comment: 被注释的代码
            #     idx = np.append(idx, m - 1)

            if cindex[m]==1 and (m in idx) and ((m+1) not in idx): #comment: 如果是复共轭对的第一个，但在有效索引中，而其配对的极点不在 (视为实极点处理)
                # idx = np.append(idx, m + 1) #comment: 被注释的代码
                poles_new = np.append(poles_new, poles[m].real) #comment: 将其实部加入新的极点列表
            elif m in idx: #comment: 如果极点在有效索引中
                poles_new = np.append(poles_new, poles[m]) #comment: 将极点加入新的极点列表


        idx = idx[np.argsort(idx)] #comment: 对有效索引进行排序

        #comment: 从 idx 中删除大于等于 N 的索引，得到有效残差的索引
        idxc = np.delete(idx, idx >= N )
        #comment: 提取对应常数项 D 的索引
        idxd = idx[idx==N]
        #comment: 提取对应线性项 E 的索引
        idxe = idx[idx==N+1]
        
        # poles_new = poles[idxc]; #comment: 被注释的代码

        c_new = SERC[:, idxc]; #comment: 获取新的残差 (Nc x 有效极点数)
        d_new = 0; #comment: 初始化新的 D
        e_new = 0; #comment: 初始化新的 E
        if(idxd.size!=0): #comment: 如果 D 的索引存在
            d_new = sol[N,:]; #comment: 获取新的 D (1 x Nc)
        if(idxe.size!=0): #comment: 如果 E 的索引存在
            e_new = sol[N+1,:]; #comment: 获取新的 E (1 x Nc)
        
        SER = {} #comment: 初始化新的 SER 字典
        SER['D'] = None #comment: 初始化 D 为 None
        SER['E'] = None #comment: 初始化 E 为 None
        SER['C'] = c_new #comment: 存储新的残差 C
        SER['B'] = np.ones((len(poles_new))) #comment: 存储 B (全为 1)
        if asymp>0: #comment: 如果包含渐近项
            SER['D'] = d_new #comment: 存储 D
            if asymp==2: #comment: 如果包含线性项 E*s
                SER['E'] = e_new #comment: 存储 E

        #comment: 计算拟合结果 fit
        fit = np.dot(c_new, np.exp( - delay[idxc][:,nax] * s[nax,:] ) * (1/(s[nax,:]-poles_new[:,nax])))
        if asymp>0: #comment: 如果包含渐近项
            fit += SER['D'] #comment: 加上 D
            if asymp==2: #comment: 如果包含线性项 E*s
                fit += s[nax,:] * SER['E'] #comment: 加上 E*s
        rmserr = np.sqrt(np.sum(np.abs(fit-f)**2)) / np.sqrt(Ns) # 均方根差 #comment: 计算均方根误差
        SER['A'] = np.diag(poles_new) #comment: 存储 A (对角矩阵，对角线为新的极点)

        #comment: 返回状态空间模型 SER，新的极点，均方根误差和拟合结果
        return SER, poles_new, rmserr, fit
        
    def _vectorfit_yc(self, res, eps, opts0):
        """
        comment: 定义 vectorfit_Yc 函数，用于对 Yc 矩阵进行向量拟合
        """
        #comment: 从结果字典 res 中获取 Yc 矩阵
        bigY = res['Yc']
        #comment: 将频率转换为复数角频率 s = j * 2 * pi * f
        s = 1j * 2 * math.pi * res['Freq'];
        #comment: 获取频率权重
        weightFreq = res['weightFreq'];
        #comment: 获取第一和第二阶段的迭代次数
        Niter1 = opts0['NiterYc1'];
        Niter2 = opts0['NiterYc2'];
        #comment: 获取极点数量
        N = opts0['NpYc'];
        #comment: 获取是否绘图的选项
        plot = opts0['ViewYcVF']
        #comment: 获取权重因子
        weightFactor = opts0['WeightFactor']
        #comment: 复制向量拟合选项
        opts = opts0['vfopts'].copy()

        #comment: 获取端口数量 Nc 和频率点数量 Ns
        Nc = res['Nc']
        Ns = res['Ns']
        
        #comment: 初始化 tell 变量，用于堆叠 Yc 的下三角部分
        tell = 0;
        #comment: 初始化 f 数组，用于存储 Yc 矩阵的独立元素（下三角部分，包括对角线）
        f = np.zeros((round(Nc*(Nc+1)/2),Ns), dtype=np.complex_)
        #comment: 遍历矩阵的列
        for col in range(Nc):
            #comment: 将下三角部分的元素堆叠到 f 中
            f[tell:tell+Nc-col,:] = bigY[col:Nc,col,:] # stacking elements into a single vector
            #comment: 更新 tell 的值，指向下一个元素的起始位置
            tell += Nc - col

        #comment: 初始化 g 数组，用于存储 Yc 矩阵的对角线元素
        g = np.zeros((Nc,Ns), dtype=np.complex_)
        #comment: 遍历对角线元素
        for col in range(Nc):
            g[col,:] = bigY[col,col,:] # stacking elements into a single vector

        # g = np.zeros((1,Ns), dtype=np.complex_) #comment: 被注释的代码，可能是尝试将对角线元素求和，但已弃用
        # for col in range(Nc):
        #     g = g + bigY[col,col,:] # stacking elements into a single vector

        
        # tell = -1; #comment: 被注释的代码，可能是尝试以另一种方式堆叠全矩阵元素，但已弃用
        # f = np.zeros((Nc * Nc, Ns),dtype=complex);
        # for col in range(Nc):
        #     for row in range(Nc):
        #         tell = tell+1;
        #         for k in range(Ns):
        #             f[tell, k] = matList[k][row, col]; # stacking elements into a single vector


        #Complex starting poles: #comment: 复杂起始极点
        w = s/1j; #comment: 将复数角频率 s 转换为实数频率 w (近似，因为 s 虚部为角频率)
        freqs = s.imag/2/math.pi; #comment: 实际计算频率 (Hz)

        #comment: 计算 Npcx，复杂极点对的数量
        Ncpx = math.floor(N/2);
        #comment: 如果 N 是偶数
        if(N == 2*Ncpx):
            #comment: 在对数空间均匀分布 beta 值
            bet = np.linspace(np.log10(w[0]), np.log10(w[-1]), Ncpx);
            #comment: 计算 alpha 值
            alf = -bet * 1.0e-2
            #comment: 生成复杂的起始极点对 (alpha - j*beta) 和 (alpha + j*beta)
            poles = np.concatenate(((alf-1j*bet)[:,nax],(alf+1j*bet)[:,nax]), axis=1).flatten()
        #comment: 如果 N 是奇数
        else:
            #comment: 在对数空间均匀分布 beta 值 (多一个点)
            bet = np.linspace(np.log10(w[0]), np.log10(w[-1]), Ncpx+1);
            #comment: 计算 alpha 值
            alf = -bet * 1.0e-2
            #comment: 生成起始极点，最后一个极点特殊处理 (变为实数极点)
            polestemp = np.concatenate(((alf-1j*bet)[:,nax],(alf+1j*bet)[:,nax]), axis=1).flatten()
            poles = polestemp[0:-1];
            poles[-1] = 2 * poles[-1].real;
            
        #comment: 计算 f 的绝对值作为初始权重的基础
        fw = np.abs(f)
        #comment: 对 fw 中的微小值进行处理，避免除以零或过小的值
        fw[(fw<1e-8) & (fw > 1e-15)] = 1e-8;
        fw[fw < 1e-15] = 1e3;
        #comment: 计算 g 的绝对值作为初始权重的基础
        gw = np.abs(g)
        #comment: 对 gw 中的微小值进行处理
        gw[(gw<1e-8) & (gw > 0)] = 1e-8;
        gw[gw < 1e-15] = 1e3;
        
        #comment: 计算 f 的权重，基于 fw 和 weightFactor 以及频率权重 weightFreq
        weight = 1/(np.float_power(fw,weightFactor));
        weight = weight * weightFreq[nax,:];
        
        #comment: 计算 g (对角线元素) 的权重
        weightg = 1/(np.float_power(gw,weightFactor));
        weightg = weightg * weightFreq[nax,:];
        
        #comment: 设置向量拟合选项：跳过残差计算，不跳过极点计算，不显示第二级绘图
        opts['skip_res'] = True;
        opts['skip_pole'] = False;
        opts['spy2'] = False;
        #comment: 第一阶段迭代拟合对角线元素 g，主要用于极点优化
        for iter in range(Niter1):
            [SER, poles, rmserr, fit] = vectfit3(g, s, poles, weightg, opts);

        #comment: 使用 mor 函数进行模型降阶或优化，用于进一步精炼极点。这里的 eps 参数传入的是 opts0['target_eps']。
        [SER, poles, rmserr , fit] = self._mor(poles, 1, np.zeros((N)), s, g, weightFreq[nax,:], eps)

        #comment: 再次设置向量拟合选项：跳过残差计算，不显示第二级绘图
        opts['skip_res'] = True;
        opts['spy2'] = False;
        #comment: 第二阶段迭代拟合对角线元素 g，继续极点优化
        for iter in range(Niter1):
            [SER, poles, rmserr, fit] = vectfit3(g, s, poles, weightg, opts);
        
        #comment: 如果需要绘图，则设置绘图选项并进行一次拟合，用于显示结果
        if(plot):
            opts['skip_res'] = False; #comment: 不跳过残差计算
            opts['skip_pole'] = True; #comment: 跳过极点计算
            opts['spy2'] = True; #comment: 显示第二级绘图
            vectfit3(g, s, poles, weightg, opts);

        #comment: 设置向量拟合选项：不显示第二级绘图，不跳过残差计算，跳过极点计算
        opts['spy2'] = False;
        opts['skip_res'] = False;
        opts['skip_pole'] = True;
        #comment: 对完整的独立元素 f 进行拟合，得到最终的 SER、极点、误差和拟合数据
        [SER, poles, rmserr, fit] = vectfit3(f, s, poles, weight, opts);

        #comment: 从 SER 中提取状态空间矩阵 A, B, C, D, E
        A = SER['A']; B = SER['B']; C = SER['C']; D = SER['D']; E = SER['E'];
        
        # SER = full2full(SER); #comment: 被注释的代码，可能是将 full 形式转换为 full 形式，但当前代码未调用 full2full
        #comment: 将向量拟合结果 (下三角堆叠) 转换为完整的矩阵形式状态空间模型
        SER = tri2full(SER);
        #comment: 将状态空间模型转换为极点-残差形式 (tri=True 表示输入是三维矩阵形式)
        R,a,D,E = ss2pr(SER,tri = True);

        #comment: 将残差 R 存入 SER 字典
        SER['R'] = R;
        #comment: 将极点 a (实际为 poles) 存入 SER 字典
        SER['poles'] = a;
        #comment: 检查 D 是否为 None，如果是则设置为 Nc x Nc 的零矩阵
        if(np.size(D)==1 and D==None):
            SER['D'] = np.zeros((Nc,Nc),dtype=complex);
        #comment: 否则将 D 存入 SER 字典
        else:
            SER['D'] = D;
        #comment: 检查 E 是否为 None，如果是则设置为 Nc x Nc 的零矩阵
        if(np.size(E)==1 and E==None):
            SER['E'] = np.zeros((Nc,Nc),dtype=complex);
        #comment: 否则将 E 存入 SER 字典
        else:
            SER['E'] = E;


        #comment: 将拟合结果存储到 res 字典中，这里使用 'Yc' 作为前缀
        res['RYc'] = R; #comment: 存储 Yc 的残差
        res['PYc'] = a; #comment: 存储 Yc 的极点
        res['CYc'] = D; #comment: 存储 Yc 的常数项
        res['EYc'] = SER['E']; #comment: 存储 Yc 的线性项
        res['fitYc'] = fit; #comment: 存储 Yc 的拟合数据
        #comment: 计算 Yc 的均方根误差 (RMSErrYc)，并进行归一化
        res['RMSErrYc'] = rmserr / np.sqrt(np.sum(np.abs((f)**2))) * np.sqrt(Nc*Ns);
        res['SER'] = SER; #comment: 存储完整的状态空间模型

        #comment: 返回更新后的结果字典 res
        return res

    def perform_vector_fitting(self):
        """
        comment: 执行主要的 Y/Z 矩阵拟合计算。
        输入:
        - self.freqs (numpy.ndarray): 频率数组。
        - self.Ys (numpy.ndarray): Y（导纳）矩阵数组。
        - self.opts (dict): 配置选项。
        输出:
        - self.calculation_results (dict): 存储拟合、转换和误差等结果的字典。
        """
        #comment: 计算变换矩阵 Q 和条件数最大的频率点索引 f0
        f0, Q = self._calculate_transform_matrix(self.Ys)
        #comment: 获取端口数量 Nc 和频率点数量 Ns
        Nc = self.Ys.shape[0];
        Ns = self.Ys.shape[2];
        #comment: 初始化 Ym 矩阵，用于存储经过 Q 变换后的 Y 矩阵
        Ym = np.zeros((Nc,Nc,Ns),dtype=complex);
        #comment: 对每个频率点的 Y 矩阵进行 Q 变换 (相似变换)，Ym = Q.T * Ys * Q
        for i in range(Ns):
            Ym[:,:,i] = Q.T @ self.Ys[:,:,i] @ Q;

        self.calculation_results = {} #comment: 初始化结果字典
        self.calculation_results['Nc'] = Nc; #comment: 存储端口数量
        self.calculation_results['Ns'] = Ns; #comment: 存储频率点数量
        self.calculation_results['Yc'] = Ym; #comment: 存储变换后的 Yc 矩阵
        self.calculation_results['Y'] = self.Ys; #comment: 存储原始 Y 矩阵
        self.calculation_results['Q'] = Q; #comment: 存储变换矩阵 Q
        self.calculation_results['Freq'] = self.freqs; #comment: 存储频率数组

        weightFreq = np.zeros(Ns); #comment: 初始化频率权重数组
        #comment: 根据 opts 中的 Weighting 规则设置频率权重
        for i in range(len(self.opts['Weighting'])):
            weightrange = self.opts['Weighting'][i]
            if(i==0): #comment: 第一个权重范围
                weightFreq[self.calculation_results['Freq'] < weightrange[0]] = weightrange[1];
            if(i==len(self.opts['Weighting']) - 1): #comment: 最后一个权重范围
                weightFreq[self.calculation_results['Freq'] >= weightrange[0]] = weightrange[1];
            if(i<len(self.opts['Weighting']) - 1): #comment: 中间的权重范围
                weightFreq[(self.calculation_results['Freq'] >= weightrange[0]) & (self.calculation_results['Freq'] < self.opts['Weighting'][i+1][0])] = weightrange[1];

        self.calculation_results['weightFreq'] = weightFreq; #comment: 存储频率权重

        # print('   --------Start fitting Yc----------  ') #comment: 调试信息 (被注释)

        # opts['vfopts']['asymp']  = 1     # Include only D in fitting (not E) #comment: 向量拟合选项设置 (被注释)
        #comment: 调用 vectorfit_Yc 函数对变换后的 Yc 矩阵进行向量拟合
        self.calculation_results = self._vectorfit_yc(self.calculation_results, self.opts['target_eps'], self.opts);


        self.calculation_results['PY'] = self.calculation_results['PYc'] #comment: 将 Yc 的极点赋值给 Y 的极点 (转换回原始系统)
        #comment: 将 Yc 的常数项通过 Q 变换回原始系统的常数项
        self.calculation_results['CY'] = Q @ self.calculation_results['CYc'] @ Q.T;
        #comment: 初始化 Y 的残差矩阵
        self.calculation_results['RY'] = np.zeros((Nc,Nc,len(self.calculation_results['PYc'])),dtype = np.complex_);


        #comment: 将 Yc 的残差通过 Q 变换回原始系统的残差
        for i in range(len(self.calculation_results['PYc'])):
            self.calculation_results['RY'][:,:,i] = Q @ self.calculation_results['RYc'][:,:,i] @ Q.T;

    def enforce_passivity(self):
        """
        comment: 执行无源性强制执行 (passivity enforcement) 过程。
        输入:
        - self.calculation_results (dict): 包含初始拟合结果的字典。
        - self.freqs (numpy.ndarray): 频率数组。
        - self.opts (dict): 配置选项，特别是无源性强制执行相关的参数。
        输出:
        - self.calculation_results (dict): 更新后的拟合结果，包含无源性强制后的模型参数。
        - self.rp_driver_log (dict): 无源性强制执行过程中的日志信息。
        """
        if(self.opts['EnabPassEnf'] == True):
            #comment: 创建 RPdriver 实例，用于无源性检查和强制执行
            rp_driver = RPdriver(parametertype='y', plot=False, StartF = self.opts['StartPass'], EndF = self.opts['EndPass'], Nint = self.opts['Nint'], Niter_out = self.opts['Niter_out_Pass'], Niter_in = self.opts['Niter_in_Pass'])
            #comment: 调用 rpdriver 方法执行无源性强制执行
            self.calculation_results['SER'], bigYfit_passive, opts3 = rp_driver.rpdriver(self.calculation_results['SER'], 2j*math.pi*self.freqs)
            #comment: 将状态空间模型转换为极点-残差形式
            R,a,D,E = ss2pr(self.calculation_results['SER'],tri = True);

            #comment: 初始化 aaa 数组，用于存储 Q 变换后的残差
            # aaa = np.zeros((self.calculation_results['Nc'],self.calculation_results['Nc'],len(a)),dtype = np.complex_);
            # for i in range(len(a)): #comment: 对每个极点，将残差通过 Q 变换回原始系统
            #     aaa[:,:,i] = self.calculation_results['Q'] @ R[:,:,i] @ self.calculation_results['Q'].T;
            
            #comment: 将 Yc 的常数项通过 Q 变换回原始系统的常数项
            self.calculation_results['CY'] = self.calculation_results['Q'] @ D @ self.calculation_results['Q'].T;
            #comment: 初始化 Y 的残差矩阵
            self.calculation_results['RY'] = np.zeros((self.calculation_results['Nc'],self.calculation_results['Nc'],len(a)),dtype = np.complex_);
            for i in range(len(a)): #comment: 对每个极点，将残差通过 Q 变换回原始系统
                self.calculation_results['RY'][:,:,i] = self.calculation_results['Q'] @ R[:,:,i] @ self.calculation_results['Q'].T;
            self.calculation_results['PY'] = a; #comment: 更新极点
            self.calculation_results['CY'] = D; #comment: 更新常数项
            self.calculation_results['EY'] = E; #comment: 更新线性项
            self.rp_driver_log = rp_driver.OutputLog; #comment: 将无源性强制执行的日志存储到 logs
        else:
            self.rp_driver_log = {"Passivity_Enforcement": "Disabled"}


    def get_formatted_output(self, include_list=False):
        """
        comment: 定义 getOutput 函数，用于将拟合结果格式化为输出字符串或列表。
        参数:
        - include_list (bool, optional): 如果 True，则返回列表；否则返回换行符连接的字符串。
        """
        res = self.calculation_results
        Nc = res['Nc']; #comment: 从结果字典中获取端口数量
        N = len(res['PY']); #comment: 从结果字典中获取极点数量
        clo = []; #comment: 初始化一个空列表，用于存储输出行
        clo.append(' ------ CloudPSS FDNE Constant Output ------ ') #comment: 添加文件头部信息
        clo.append(' Number of ports:') #comment: 添加端口数量标签
        clo.append(Nc) #comment: 添加端口数量
        clo.append(' Residues and poles:') #comment: 添加残差和极点标签
        for i in range(Nc): #comment: 遍历每个端口
            clo.append(N) #comment: 添加极点数量
            for j in range(N): #comment: 遍历每个极点
                clo.append(res['PY'][j].real) #comment: 添加极点的实部
                clo.append(res['PY'][j].imag) #comment: 添加极点的虚部
                for k in range(Nc): #comment: 遍历每个端口的残差
                    clo.append(res['RY'][k,i,j].real) #comment: 添加残差的实部
                    clo.append(res['RY'][k,i,j].imag) #comment: 添加残差的虚部
        
        for i in range(Nc): #comment: 遍历端口，添加常数项
            for k in range(Nc):
                clo.append(res['CY'][k,i].real) #comment: 添加常数项的实部
        clo = [str(i) for i in clo]; #comment: 将所有列表元素转换为字符串
        if(include_list): #comment: 如果 l 为 True，则返回列表
            return clo
        else: #comment: 否则，将列表元素用换行符连接成一个字符串并返回
            return "\n".join(clo)

    def write_results_to_file(self, filename="OUTPUT_FILENAME_PLACEHOLDER.txt"):
        """
        comment: 定义 outputToFile 函数，用于将拟合结果写入文件。
        参数:
        - filename (str): 输出文件路径。
        """
        clo_content = self.get_formatted_output(include_list=True)
        with open(filename, 'w') as f: #comment: 以写入模式打开文件
            for line in clo_content: #comment: 遍历输出内容列表
                f.write(line) #comment: 写入每一行
                f.write('\n') #comment: 写入换行符
        print(f"拟合结果已写入到 {filename}")

    def plot_fitting_results(self, plot_before_passivity=True):
        """
        comment: 定义 plotFitting 函数，用于绘制拟合结果和无源性强制执行后的结果。
        参数:
        - plot_before_passivity (bool): 是否绘制无源性强制执行前的拟合结果。
        """
        freq = self.calculation_results['Freq'] #comment: 获取频率
        Nc = self.calculation_results['Nc']; #comment: 获取端口数量
        Ns = self.calculation_results['Ns'] #comment: 获取频率点数量

        CYfit = np.zeros((Nc,Nc,Ns),dtype=complex) #comment: 初始化 CYfit

        for i in range(len(self.calculation_results['PY'])): #comment: 循环计算 CYfit，基于残差和极点
            CYfit += np.dot(self.calculation_results['RY'][:,:,i].flatten()[:,nax], (1/((1j*2*math.pi*freq[nax,:])-self.calculation_results['PY'][i]))).reshape([Nc,Nc,Ns])
        CYfit += self.calculation_results['CY'][:,:,nax] #comment: 加上常数项

        # Get results after passivity enforce from self.rp_driver_log if available
        # Assume self.rp_driver_log contains 'SER' key if passivity enforcement was run
        CYfit_pass = np.zeros((Nc,Nc,Ns),dtype=complex) #comment: 初始化经过无源性强制执行后的拟合结果 CYfit_pass
        
        # Check if passivity enforcement was enabled and successful
        if self.rp_driver_log and "Passivity_Enforcement" not in self.rp_driver_log: # Simple check for success (more detailed check might be needed)
             # Extract poles, residues, D, E from the SER after passivity enforcement
            # Ensure the SER from rp_driver_log is properly structured
            if 'SER' in self.rp_driver_log and self.rp_driver_log['SER'] is not None:
                final_ser = self.rp_driver_log['SER']
                # Convert SER to pole-residue form if not already
                R_pass, a_pass, D_pass, E_pass = ss2pr(final_ser, tri=True)

                for i in range(len(a_pass)): #comment: 循环计算 CYfit_pass
                    CYfit_pass += np.dot(R_pass[:,:,i].flatten()[:,nax], (1/((1j*2*math.pi*freq[nax,:])-a_pass[i]))).reshape([Nc,Nc,Ns])
                
                if D_pass is not None and D_pass.size > 0:
                    CYfit_pass += D_pass[:,:,nax] #comment: 加上常数项
                if E_pass is not None and E_pass.size > 0:
                    CYfit_pass += E_pass[:,:,nax] * (1j*2*math.pi*freq[nax,nax,:]) #comment: 加上线性项

        # Amplitude plot
        plt.figure(figsize=(10, 6)) #comment: 创建幅频特性图
        plt.title('Magnitude Response')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Magnitude')
        plt.grid(True, which="both", ls="-")

        F_flat = np.zeros((Nc*Nc,Ns),dtype=complex) #comment: 初始化 F 数组，用于存储原始数据的展平形式
        for i in range(Ns): #comment: 展平原始 Y 数据
            F_flat[:,i] = self.calculation_results['Y'][:,:,i].flatten()
        
        for i in range(Nc): #comment: 遍历端口进行绘图
            for j in range(Nc):
                if(j!=i): # comment: 跳过非对角线元素，只绘制对角线
                    continue
                f_data = F_flat[i*Nc+j,:] #comment: 获取原始数据
                
                # Plot data
                plt.plot(freq, np.abs(f_data), 'b-', label='Data' if (i == 0 and j == 0) else "") # Only label once

                if plot_before_passivity:
                    fit_orig = CYfit[i,j,:] #comment: 获取拟合数据
                    plt.plot(freq, np.abs(fit_orig), 'r--', label='FRVF (Before PE)' if (i == 0 and j == 0) else "")

                if CYfit_pass.any(): # Only plot if passivity enforcement was successful and results are available
                    fit_pass = CYfit_pass[i,j,:] #comment: 获取无源性强制执行后的拟合数据
                    plt.plot(freq, np.abs(fit_pass), 'g:', label='FRVF (After PE)' if (i == 0 and j == 0) else "")
                
        if self.opts['vfopts']['logx']:
            plt.xscale('log')
        if self.opts['vfopts']['logy']:
            plt.yscale('log')
        plt.legend()
        if self.opts['vfopts']['block']:
            plt.show(block=True)
        else:
            plt.draw()

        # Phase plot
        plt.figure(figsize=(10, 6)) #comment: 创建相频特性图
        plt.title('Phase Response')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Phase Angle [rad]')
        plt.grid(True, which="both", ls="-")

        for i in range(Nc): #comment: 遍历端口进行绘图
            for j in range(Nc):
                if(j!=i): # comment: 跳过非对角线元素，只绘制对角线
                    continue
                f_data = F_flat[i*Nc+j,:] #comment: 获取原始数据
             
                # Plot data
                plt.plot(freq, np.angle(f_data), 'b-', label='Data' if (i == 0 and j == 0) else "")

                if plot_before_passivity:
                    fit_orig = CYfit[i,j,:] #comment: 获取拟合数据
                    plt.plot(freq, np.angle(fit_orig), 'r--', label='FRVF (Before PE)' if (i == 0 and j == 0) else "")

                if CYfit_pass.any():
                    fit_pass = CYfit_pass[i,j,:] #comment: 获取无源性强制执行后的拟合数据
                    plt.plot(freq, np.angle(fit_pass), 'g:', label='FRVF (After PE)' if (i == 0 and j == 0) else "")
        
        if self.opts['vfopts']['logx']:
            plt.xscale('log')
        plt.legend()
        if self.opts['vfopts']['block']:
            plt.show(block=True)
        else:
            plt.draw()


def main():
    """
    主函数，编排 FDNECalculation 类的成员方法，完成整个FDNE分析流程。
    """
    # 初始化 FDNE 计算器
    fdne_calculator = FDNECalculation()

    # 第一步：加载数据
    # 调用 load_data 方法，实现从文件加载S参数数据的功能。
    # 敏感信息替换：文件路径占位符
    fdne_calculator.load_data('./results/windFreqTest/Z_2023_11_23_16_19_52.txt', data_type='Y', data_format='YZ')
    print("第一步：数据加载完成。")

    # 第二步：更新配置选项
    # 调用 opts 属性，更新向量拟合和无源性强制执行的配置参数。
    # 根据实际需求调整这些参数
    fdne_calculator.opts['vfopts']['asymp']  = 1
    fdne_calculator.opts['vfopts']['relaxed']=True
    fdne_calculator.opts['vfopts']['stable']=True
    fdne_calculator.opts['vfopts']['spy2'] = True
    fdne_calculator.opts['vfopts']['spy1'] = False
    fdne_calculator.opts['vfopts']['errplot']=False
    fdne_calculator.opts['vfopts']['logx'] = True
    fdne_calculator.opts['vfopts']['logy'] = False
    fdne_calculator.opts['EigMaxIter'] = 20
    fdne_calculator.opts['EigEps'] = 1e-8
    fdne_calculator.opts['target_eps'] = 0.001
    fdne_calculator.opts['NpYc'] = 20
    fdne_calculator.opts['ErYc'] = 0.01
    fdne_calculator.opts['Weighting'] = [[0,1]]
    fdne_calculator.opts['WeightFactor'] = 0
    fdne_calculator.opts['NiterYc1'] = 5
    fdne_calculator.opts['NiterYc2'] = 3
    fdne_calculator.opts['ViewYcVF'] = True
    fdne_calculator.opts['EnabPassEnf'] = True  # Enable passivity enforcement
    fdne_calculator.opts['StartPass'] = 0
    fdne_calculator.opts['EndPass'] = 1e12
    fdne_calculator.opts['Nint'] = 20
    fdne_calculator.opts['Niter_out_Pass'] = 10
    fdne_calculator.opts['Niter_in_Pass'] = 2
    print("第二步：配置选项更新完成。")

    # 第三步：执行向量拟合
    # 调用 perform_vector_fitting 方法，实现对Y矩阵进行向量拟合的功能。
    fdne_calculator.perform_vector_fitting()
    print("第三步：向量拟合完成。")
    print(f"拟合结果均方根误差 (RMSErrYc): {fdne_calculator.calculation_results['RMSErrYc']}")

    # 第四步：执行无源性强制执行 (可选)
    # 调用 enforce_passivity 方法，实现对拟合模型进行无源性检查和强制的功能。
    # 仅当 opts['EnabPassEnf'] 为 True 时执行。
    fdne_calculator.enforce_passivity()
    print("第四步：无源性强制执行完成。")
    if fdne_calculator.rp_driver_log:
        print("无源性强制执行日志:", fdne_calculator.rp_driver_log)

    # 第五步：将结果写入文件
    # 调用 write_results_to_file 方法，实现将拟合数据写入特定格式文件的功能。
    # 敏感信息替换：文件路径占位符
    fdne_calculator.write_results_to_file('./results/windFreqTest/output_model.txt')
    print("第五步：结果写入文件完成。")

    # 第六步：绘制拟合结果
    # 调用 plot_fitting_results 方法，实现绘制原始数据与拟合曲线对比图的功能。
    fdne_calculator.plot_fitting_results(plot_before_passivity=True)
    print("第六步：拟合结果绘图完成。")


if __name__ == '__main__':
    main()