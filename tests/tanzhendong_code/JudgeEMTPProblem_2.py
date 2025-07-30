# comment: 导入 os 模块，用于操作系统相关功能，例如文件路径操作
import os
# comment: 导入 pandas 库，通常用于数据处理和分析
import pandas as pd
# comment: 导入 time 模块，用于时间相关功能
import time
# comment: 导入 sys 模块，提供对解释器使用或维护的变量的访问，以及与解释器强烈交互的函数
import sys,os

# comment: 导入 cloudpss 库，这是一个自定义的库，用于与 CloudPSS 平台交互
import cloudpss
# comment: 导入 math 模块，提供数学函数
import math
# comment: 导入 cmath 模块，提供复数数学函数
import cmath
# comment: 导入 numpy 库，通常用于科学计算，特别是数组操作
import numpy as np
# comment: 导入 numpy.linalg 模块，提供线性代数操作
import numpy.linalg as lg
# comment: 从 jobApi1 导入 fetch, fetchAllJob, abort 函数，用于作业管理
# from jobApi1 import fetch,fetchAllJob,abort # 假设 jobApi1 是一个非标准库，暂时注释掉，避免运行报错
# comment: 从 cloudpss.runner.result 导入 Result, PowerFlowResult, EMTResult，用于处理仿真结果
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
# comment: 导入 json 模块，用于处理 JSON 数据
import json
# comment: 导入 random 模块，用于生成随机数
import random
# comment: 导入 re 模块，用于正则表达式操作
import re
# comment: 导入 nest_asyncio 库，通常用于在已运行的事件循环中运行新的事件循环，以解决异步框架的嵌套问题
import nest_asyncio
# comment: 应用 nest_asyncio，允许嵌套使用 asyncio 事件循环
nest_asyncio.apply()
# comment: 导入 copy 模块，用于创建对象的副本
import copy
# comment: 从 cloudpss.job.job 导入 Job 类，并将其重命名为 cjob，表示 CloudPSS 作业对象
from cloudpss.job.job import Job as cjob

# comment: 定义一个名为 is_number 的函数
def is_number(s):
    """
    检查输入是否可以转换为数字（浮点数或Unicode数字）。

    Args:
        s: 待检查的输入。

    Returns:
        True 如果可以转换为数字，否则 False。
    """
    # comment: 检查输入 s 是否为列表类型
    if(isinstance(s,list)):
        # comment: 如果是列表，则返回 False，表示不是一个数字
        return False
    # comment: 尝试将 s 转换为浮点数
    try:
        # comment: 尝试转换
        float(s)
        # comment: 如果成功，则返回 True
        return True
    # comment: 捕获 ValueError 异常，表示转换失败
    except ValueError:
        # comment: 如果发生 ValueError，则pass，继续尝试下一段代码
        pass

    # comment: 尝试使用 unicodedata 判断 s 是否为数字
    try:
        # comment: 导入 unicodedata 模块，如果之前没有导入，这里会尝试导入
        import unicodedata
        # comment: 尝试将 s 转换为数字
        unicodedata.numeric(s)
        # comment: 如果成功，则返回 True
        return True
    # comment: 捕获 TypeError 或 ValueError 异常
    except (TypeError, ValueError):
        # comment: 如果发生异常，则pass
        pass

    # comment: 如果所有尝试都失败，则返回 False
    return False

# comment: 定义 JudgeEMTPProblem_2 类
class JudgeEMTPProblem_2:
    """
    该类用于处理 CloudPSS 平台中直流线路模型相关参数的计算和评估。
    它包含初始化 CloudPSS 连接、获取模型、计算直流线路参数以及进行换流站侧计算等功能。

    属性:
        token (str): CloudPSS 平台的访问令牌。
        api_url (str): CloudPSS API 的 URL。
        username (str): CloudPSS 用户名。
        project_key (str): CloudPSS 项目的唯一标识符。
        project (cloudpss.Model): 从 CloudPSS 平台获取的模型对象。
        dc_line_components (dict): 项目中所有直流线路组件的字典。
        dc_line_params (dict): 计算后的直流线路参数，以组件ID为键。
        converter_station_params (dict): 换流站侧计算的参数。
    """
    def __init__(self, token="YOUR_TOKEN", api_url="http://YOUR_API_URL/",
                 username="YOUR_USERNAME", project_key="YOUR_PROJECT_KEY"):
        """
        初始化 JudgeEMTPProblem_2 类的实例。

        Args:
            token (str): CloudPSS 平台的访问令牌。
            api_url (str): CloudPSS API 的 URL。
            username (str): CloudPSS 用户名。
            project_key (str): CloudPSS 项目的唯一标识符。
        """
        self.token = token
        self.api_url = api_url
        self.username = username
        self.project_key = project_key
        self.project = None
        self.dc_line_components = {}
        self.dc_line_params = {}
        self.converter_station_params = {}

    def initialize_cloudpss_connection(self):
        """
        初始化 CloudPSS 连接，设置访问令牌和API URL。
        """
        # comment: 设置 CloudPSS 的访问令牌
        cloudpss.setToken(self.token)
        # comment: 设置环境变量 CLOUDPSS_API_URL
        os.environ['CLOUDPSS_API_URL'] = self.api_url
        print("CloudPSS connection initialized.")

    def fetch_cloudpss_model(self):
        """
        从 CloudPSS 平台获取指定项目键的模型对象。

        Returns:
            cloudpss.Model: 获取到的模型对象。
        """
        # comment: 从 CloudPSS 平台获取模型对象
        model_path = f'model/{self.username}/{self.project_key}'
        self.project = cloudpss.Model.fetch(model_path)
        print(f"Model '{self.project_key}' fetched successfully.")
        return self.project

    def calculate_dc_line_parameters(self):
        """
        遍历项目中所有 RID 为 'model/CloudPSS/DCLine' 的组件，
        计算并更新其直流线路相关参数。

        Returns:
            dict: 包含计算后直流线路参数的字典，以组件ID为键。
        """
        # comment: 遍历项目中所有 RID 为 'model/CloudPSS/DCLine' 的组件
        self.dc_line_components = self.project.getComponentsByRid('model/CloudPSS/DCLine')
        for i, j in self.dc_line_components.items():
            # comment: 深度复制组件的参数字典
            d = copy.deepcopy(j.args)
            # comment: 遍历参数字典的键
            for k in d.keys():
                # comment: 如果参数值是数字
                if(is_number(d[k])):
                    # comment: 将参数值转换为浮点数
                    d[k] = float(d[k]);
            # comment: 计算直流线路送端交流侧的无功功率 Q_i0
            d['Qi0'] = d['Qiin']-2*d['Qci']-d['Vi_AC']**2/d['Xfti']
            # comment: 计算直流线路受端交流侧第一回的无功功率 Q_j0
            d['Qj0']=d['Qjin']+2*d['Qcj']+d['Vj_AC']*d['Vj_AC']/d['Xftj']
            # comment: 计算直流线路受端交流侧第二回的无功功率 Q_j20
            d['Qj20']=d['Qjin2']+2*d['Qcj2']+d['Vj_AC2']*d['Vj_AC2']/d['Xftj2']
            # comment: 计算直流电流 I_DC
            d['I_DC'] = d['Piin']/d['U_DC']/2;
            # comment: 根据层级计算受端直流电压 V_j_DC
            d['Vj_DC'] = d['U_DC_H'] if d['Hierarchy']==1 else d['U_DC']-d['Rl']*d['I_DC'];
            # comment: 计算受端直流电压 V_j_DC2
            d['Vj_DC2'] = d['U_DC']-d['Rl']*d['I_DC']-d['U_DC_H'];
            # comment: 计算送端变压器变比 T_i
            d['Ti'] = 3*math.sqrt(2)*d['Vi_AC']/math.pi/d['U_DC']*math.cos(math.atan(d['Qi0']/(2*d['U_DC']*d['I_DC'])))
            # comment: 计算受端变压器变比 T_j
            d['Tj'] = 3*math.sqrt(2)*d['Vj_AC']/math.pi/d['Vj_DC']*math.cos(math.atan(abs(d['Qj0'])/(2*d['Vj_DC']*d['I_DC'])))
            # comment: 计算受端变压器变比 T_j2
            d['Tj2'] = 3*math.sqrt(2)*d['Vj_AC2']/math.pi/d['Vj_DC2']*math.cos(math.atan(abs(d['Qj20'])/(2*d['Vj_DC2']*d['I_DC'])))
            # comment: 计算送端变压器实际变比 T_i_ap
            d['Ti_ap']=d['Nbi']*d['Ti']*d['Vli']/d['Vhi']
            # comment: 计算受端变压器实际变比 T_j_ap
            d['Tj_ap']=d['Nbj']*d['Tj']*d['Vlj']/d['Vhj']
            # comment: 计算受端变压器实际变比 T_j_ap2
            d['Tj_ap2']=d['Nbj2']*d['Tj2']*d['Vlj2']/d['Vhj2']
            
            # comment: 重新计算送端无功功率 Q_i
            d['Qi'] = d['Qi0']-d['Xki']/100*(d['Qi0']**2+d['Piin']**2)/d['Vi_AC']**2*(d['Vhi']*d['Ti_ap'])**2/d['Sti']/2
            
            # comment: 重新计算受端无功功率 Q_j
            d['Qj']=d['Qj0']+d['Xkj']/100*(d['Qj0']**2+(2*d['Vj_DC']*d['I_DC'])**2)/d['Vj_AC']**2*(d['Vhj']*d['Tj_ap'])**2/d['Stj']/2
            
            # comment: 重新计算受端无功功率 Q_j2
            d['Qj2']=d['Qj20']+d['Xkj2']/100*(d['Qj20']**2+(2*d['Vj_DC2']*d['I_DC'])**2)/d['Vj_AC2']**2*(d['Vhj2']*d['Tj_ap2'])**2/d['Stj2']/2
            # comment: 计算送端换流变压器等效电抗 X_ci
            d['Xci']=d['Nbi']*d['Vli']*d['Vli']/d['Sti']*d['Xki']/100
            # comment: 计算受端换流变压器等效电抗 X_cj
            d['Xcj']=d['Nbj']*d['Vlj']*d['Vlj']/d['Stj']*d['Xkj']/100
            # comment: 计算受端换流变压器等效电抗 X_cj2
            d['Xcj2']=d['Nbj2']*d['Vlj2']*d['Vlj2']/d['Stj2']*d['Xkj2']/100
            
            # comment: 计算送端换相角电抗 X_di
            d['dxi'] = 3/math.pi*d['Nbi']*d['Xci'];
            # comment: 计算受端换相角电抗 X_dj
            d['dxj'] = 3/math.pi*d['Nbj']*d['Xcj']
            # comment: 计算受端换相角电抗 X_dj2
            d['dxj2'] = 3/math.pi*d['Nbj2']*d['Xcj2'];
            # comment: 计算送端直流电压系数 K_Udi0i
            d['KUdi0i'] = 3*math.sqrt(2)/math.pi/d['Ti']
            # comment: 计算受端直流电压系数 K_Udi0j
            d['KUdi0j'] = 3*math.sqrt(2)/math.pi/d['Tj']
            # comment: 计算受端直流电压系数 K_Udi0j2
            d['KUdi0j2'] = 3*math.sqrt(2)/math.pi/d['Tj2']
            
            # comment: 计算受端直流功率 P_j_DC
            d['Pj_DC'] = 2*d['Vj_DC']*d['I_DC'];
            
            # comment: 计算送端变流器触发角 alpha0
            d['alpha0'] = 180/math.pi*math.acos((d['U_DC']+3/math.pi*d['Nbi']*d['Xci']*d['I_DC'])/(3*math.sqrt(2)/math.pi*d['Vi_AC']/d['Ti']));
            # comment: 计算受端变流器触发角 gamma0
            d['gamma0'] = 180/math.pi*math.acos((d['Vj_DC']+3/math.pi*d['Nbj']*d['Xcj']*d['I_DC'])/(3*math.sqrt(2)/math.pi*d['Vj_AC']/d['Tj']));
            # comment: 计算受端变流器触发角 gamma02
            d['gamma02'] = 180/math.pi*math.acos((d['Vj_DC2']+3/math.pi*d['Nbj2']*d['Xcj2']*d['I_DC'])/(3*math.sqrt(2)/math.pi*d['Vj_AC2']/d['Tj2']));
            # comment: 计算受端变流器关断角 beta0
            d['beta0'] = (math.pi-math.acos(math.cos(d['gamma0']/180*math.pi)-math.sqrt(2)*d['Nbj']*d['I_DC']*d['Xcj']*d['Tj']/d['Vj_AC']))/math.pi*180
            # comment: 计算受端变流器关断角 beta02
            d['beta02'] = (math.pi-math.acos(math.cos(d['gamma02']/180*math.pi)-math.sqrt(2)*d['Nbj2']*d['I_DC']*d['Xcj2']*d['Tj2']/d['Vj_AC2']))/math.pi*180
            
            # comment: 检查 alpha0 是否为复数，如果是则打印警告信息
            if(d['alpha0'].imag!=0):
                print(i+"-"+j.label+": "+'alpha0 is complex')
            # comment: 检查 gamma0 是否为复数，如果是则打印警告信息
            if(d['gamma0'].imag!=0):
                print(i+"-"+j.label+": "+'gamma0 is complex')
            # comment: 检查 beta0 是否为复数，如果是则打印警告信息
            if(d['beta0'].imag!=0):
                print(i+"-"+j.label+": "+'beta0 is complex')
            
            self.dc_line_params[i] = d
        print("DC line parameters calculated.")
        return self.dc_line_params

    def calculate_converter_station_power(self):
        """
        计算换流站侧的无功功率和相关参数。
        
        Returns:
            dict: 包含计算后换流站侧功率参数的字典。
        """
        # comment: 定义直流电压（送端 双极）
        Vdi = 400 # 直流电压（送端 双极） ***************
        # comment: 定义直流功率（送端 双极）
        Pdi = 600 # 直流功率（送端 双极） ***************
        # comment: 定义送端给定点燃角
        alphai0 = 15 # 给定点燃角（送端 双极）
        # comment: 定义送端最小点燃角
        alphaim = 5 # 最小点燃角（送端 双极）
        # comment: 定义送端给定息弧角（不需要）
        gammai0 = 17 # 给定息弧角（送端 双极 不需要）
        # comment: 定义送端最小熄弧角（不需要）
        gammaim = 5 # 最小熄弧角（送端 双极 不需要）
        # comment: 定义受端直流电压 H 极（暂时不用）
        Vdjh = 400 # 直流电压（受端 双极 H 暂时不用）
        # comment: 定义受端直流功率 H 极（暂时不用）
        Pdjh = 600 # 直流功率（受端 双极 H 暂时不用）
        # comment: 定义受端给定点燃角 H 极（不需要）
        alphajh0 = 15 # 给定点燃角（受端 双极 H 不需要）
        # comment: 定义受端最小点燃角 H 极（不需要）
        alphajhm = 5 # 最小点燃角（受端 双极 H 不需要）
        # comment: 定义受端给定息弧角 H 极
        gammajh0 = 17 # 给定息弧角（受端 双极 H）
        # comment: 定义受端最小息弧角 H 极
        gammajhm = 17 # 最小息弧角（受端 双极 H）

        # comment: 定义送端换流器个数
        Ni = 2 # 送端换流器个数
        # comment: 定义送端变压器一次侧额定电压
        Vi1 = 220 # 变压器一次侧额定电压（送端 单个变压器）
        # comment: 定义送端变压器二次侧额定电压
        Vi2 = 157.5 # 变压器二次侧额定电压（送端 单个变压器）
        # comment: 定义送端变压器额定容量
        Sti = 300 # 变压器额定容量（送端 单个变压器）
        # comment: 定义送端变压器电阻标幺值（暂时不用）
        Rki = 0 # 变压器电阻标幺值（送端 单个变压器 暂时不用）
        # comment: 定义送端变压器电抗标幺值
        Xki = 0.144 # 变压器电抗标幺值（送端 单个变压器 暂时不用）
        # comment: 定义送端变压器一次侧电压上限
        Vi1max = 246 # 变压器一次侧电压上限（送端 单个变压器）
        # comment: 定义送端变压器一次侧电压下限
        Vi1min = 198 # 变压器一次侧电压下限（送端 单个变压器）
        # comment: 定义送端变压器一次侧档位总数
        Ksi = 0 # 变压器一次侧档位总数 为0时档位不限
        # comment: 定义送端无功补偿器容量
        Qci = 0 # 送端无功补偿器容量

        # comment: 定义受端换流器个数
        Njh = 2 # 受端换流器个数
        # comment: 定义受端 H 变压器一次侧额定电压
        Vjh1 = 363 # 变压器一次侧额定电压（受端 H 单个变压器）
        # comment: 定义受端 H 变压器二次侧额定电压
        Vjh2 = 157.0 # 变压器二次侧额定电压（受端 H 单个变压器）
        # comment: 定义受端 H 变压器额定容量
        Stjh = 300 # 变压器额定容量（受端 H 单个变压器）
        # comment: 定义受端 H 变压器电阻标幺值（暂时不用）
        Rkjh = 0 # 变压器电阻标幺值（受端 H 单个变压器 暂时不用）
        # comment: 定义受端 H 变压器电抗标幺值
        Xkjh = 0.144 # 变压器电抗标幺值（受端 H 单个变压器 暂时不用）
        # comment: 定义受端 H 变压器一次侧电压上限
        Vjh1max = 406 # 变压器一次侧电压上限（受端 H 单个变压器）
        # comment: 定义受端 H 变压器一次侧电压下限
        Vjh1min = 326 # 变压器一次侧电压下限（受端 H 单个变压器）
        # comment: 定义受端 H 变压器一次侧档位总数
        Ksjh = 0 # 变压器一次侧档位总数 为0时档位不限（受端 H 单个变压器）
        # comment: 定义受端无功补偿器容量（H）
        Qcjh = 150 # 受端无功补偿器容量（H）

        # comment: 定义直流线路电阻
        Rl = 19.03 # 直流线路电阻

        # comment: 定义送端交流电压初值
        Viac = 229.9993;
        # comment: 定义受端交流电压初值
        Vjhac = 362.8639;

        # comment: 计算送端变压器最大变比
        Timax = Vi1max/Vi2/Ni;
        # comment: 计算送端变压器最小变比
        Timin = Vi1min/Vi2/Ni;
        # comment: 初始化送端变压器每档变比变化量
        dTi = 0
        # comment: 如果送端变压器有档位调节
        if(Ksi!=0):
            # comment: 计算每档的变比变化量
            dTi = (Timax - Timin) / Ksi

        # comment: 计算受端变压器最大变比
        Tjhmax = Vjh1max/Vjh2/Njh;
        # comment: 计算受端变压器最小变比
        Tjhmin = Vjh1min/Vjh2/Njh;
        # comment: 初始化受端变压器每档变比变化量
        dTjh = 0
        # comment: 如果受端变压器有档位调节
        if(Ksjh!=0):
            # comment: 计算每档的变比变化量
            dTjh = (Tjhmax - Tjhmin) / Ksjh

        # comment: 计算直流电流
        Idc = Pdi/Vdi/2;  # 电流
        # comment: 计算受端实际直流电压
        Vdjhr = Vdi - Rl*Idc; # 受端实际直流电压
        # comment: 计算受端实际直流功率
        Pdjhr = 2*Vdjhr*Idc; # 受端实际直流功率

        # comment: 计算送端变压器有名值电抗
        Xkir = Ni*Vi2**2/Sti*Xki # 有名值计算
        # comment: 计算送端变压器有名值电阻
        Rkir = Ni*Vi2**2/Sti*Rki # 有名值计算
        # comment: 计算受端变压器有名值电抗
        Xkjhr = Njh*Vjh2**2/Stjh*Xkjh # 有名值计算
        # comment: 计算受端变压器有名值电阻
        Rkjhr = Njh*Vjh2**2/Stjh*Rkjh # 有名值计算

        # comment: 送端换流侧 (整流侧) 相关计算
        # comment: 将送端变压器档位设置为0
        Ksi = 0;
        # comment: 如果送端变压器档位为0（即无档位调节）
        if(Ksi==0):
            # comment: 计算考虑直流电压和谐波的送端电压修正值 V_di_mod
            Vdi_mod = math.pi/3/math.sqrt(2)*(Vdi + 3/math.pi*Ni*Xkir*Idc); # Viac/Ti*cos(alpha)
            # comment: 根据给定点燃角计算送端变压器变比 T_i
            Ti = math.cos(alphai0/180*math.pi) * Viac / Vdi_mod; # 计算当前状态下变压器变比
            # comment: 如果计算出的变比大于最大变比
            if(Ti>Timax):
                # comment: 将变比设置为最大值
                Ti = Timax
                # comment: 如果修正后电压高于交流电压
                if(Vdi_mod*Ti/Viac>1):
                    # comment: 打印报错信息：alpha超限
                    print('报错：alpha超限！')
                    # comment: 将 alpha 设置为最小点燃角
                    alphai = alphaim;
                # comment: 否则，计算新的 alpha
                else:
                    # comment: 计算实际点燃角
                    alphai = 180/math.pi*math.acos(Vdi_mod*Ti/Viac)
                    # comment: 如果计算出的 alpha 小于最小点燃角
                    if(alphai < alphaim):
                        # comment: 打印报错信息：alpha超限
                        print('报错：alpha超限！')
                        # comment: 将 alpha 设置为最小点燃角
                        alphai = alphaim;
            # comment: 如果计算出的变比小于最小变比
            elif(Ti<Timin):
                # comment: 将变比设置为最小值
                Ti = Timin
                # comment: 计算实际点燃角
                alphai = 180/math.pi*math.acos(Vdi_mod*Ti/Viac)
            # comment: 否则，使用给定点燃角
            else:
                # comment: 设置点燃角为给定值
                alphai = alphai0
        # comment: 计算临时变量 tempi，用于后续无功计算
        tempi = math.pi*Ti/3/math.sqrt(2)*Vdi/Viac;
        # comment: 如果 tempi 大于1，表示计算值不合理，打印错误信息
        if(tempi>1):
            print('Error：检查Ti范围是否合理')
            # comment: 将 tempi 设置为0
            tempi = 0
        # comment: 计算送端无功功率 Q_i
        Qi = - Pdi * math.sqrt(1-tempi**2)/tempi + 2*Qci

        # comment: 受端换流侧 (逆变侧) 相关计算
        # comment: 将受端变压器档位设置为0
        Ksj = 0;
        # comment: 如果受端变压器档位为0（即无档位调节）
        if(Ksj==0):
            # comment: 计算考虑直流电压和谐波的受端电压修正值 V_djh_mod
            Vdjh_mod = math.pi/3/math.sqrt(2)*(Vdjhr + 3/math.pi*Njh*Xkjhr*Idc); # Viac/Ti*cos(alpha)
            # comment: 根据给定息弧角计算受端变压器变比 T_jh
            Tjh = math.cos(gammajh0/180*math.pi) * Vjhac / Vdjh_mod; # 计算当前状态下变压器变比
            # comment: 如果计算出的变比大于最大变比
            if(Tjh>Tjhmax):
                # comment: 将变比设置为最大值
                Tjh = Tjhmax
                # comment: 如果修正后电压高于交流电压
                if(Vdjh_mod*Tjh/Vjhac>1):
                    # comment: 打印报错信息：alpha超限
                    print('报错：alpha超限！')
                    # comment: 将 gamma 设置为最小息弧角
                    gammajh = gammajhm;
                # comment: 否则，计算新的 gamma
                else:
                    # comment: 计算实际息弧角
                    gammajh = 180/math.pi*math.acos(Vdjh_mod*Tjh/Vjhac)
                    # comment: 如果计算出的 gamma 小于最小息弧角
                    if(gammajh < gammajhm):
                        # comment: 打印报错信息：alpha超限
                        print('报错：alpha超限！')
                        # comment: 将 gamma 设置为最小息弧角
                        gammajh = gammajhm;
            # comment: 如果计算出的变比小于最小变比
            elif(Tjh<Tjhmin):
                # comment: 将变比设置为最小值
                Tjh = Tjhmin
                # comment: 计算实际息弧角
                gammajh = 180/math.pi*math.acos(Vdjh_mod*Tjh/Vjhac)
            # comment: 否则，使用给定息弧角
            else:
                # comment: 设置息弧角为给定值
                gammajh = gammajh0
        # comment: 计算临时变量 tempjh，用于后续无功计算
        tempjh = math.pi*Tjh/3/math.sqrt(2)*Vdjhr/Vjhac;
        # comment: 如果 tempjh 大于1，表示计算值不合理，打印错误信息
        if(tempjh>1):
            print('Error：检查Ti范围是否合理')
            # comment: 将 tempjh 设置为0
            tempjh = 0
        # comment: 计算受端无功功率 Q_jh
        Qjh = - Pdjhr * math.sqrt(1-tempjh**2)/tempjh + 2*Qcjh

        self.converter_station_params = {
            'rectifier_P': -Pdi, # 整流侧有功功率（发电为正）
            'rectifier_Q': Qi,   # 整流侧无功功率
            'inverter_H_P': Pdjhr, # 逆变H侧有功功率（发电为正）
            'inverter_H_Q': Qjh  # 逆变H侧无功功率
        }
        print("Converter station power parameters calculated.")
        return self.converter_station_params
    
    def display_results(self):
        """
        显示计算出的换流站侧PQ节点信息。
        """
        # comment: 打印整流侧 PQ 节点的信息（发电为正）
        print('整流侧PQ节点（发电为正），P={0}MW, Q={1}MVar'.format(
            self.converter_station_params['rectifier_P'], self.converter_station_params['rectifier_Q']))
        # comment: 打印逆变 H 侧 PQ 节点的信息（发电为正）
        print('逆变H侧PQ节点（发电为正），P={0}MW, Q={1}MVar'.format(
            self.converter_station_params['inverter_H_P'], self.converter_station_params['inverter_H_Q']))
        print("Results displayed.")


def main():
    """
    主函数，用于创建 JudgeEMTPProblem_2 类的实例并执行业务逻辑。
    """
    # comment: 打印开始信息
    print('Start')

    # comment: 第一步：初始化 JudgeEMTPProblem_2 类的实例，并替换敏感信息为占位符。
    # comment: 定义一个名为 JudgeEMTPProblem_2 的类，用于处理直流线路参数计算和换流站功率计算
    # comment: 替换以下敏感数据为占位符
    token_placeholder = 'YOUR_TOKEN_HERE'
    api_url_placeholder = 'http://YOUR_API_URL_HERE/'
    username_placeholder = 'YOUR_USERNAME_HERE'
    # comment: 考虑到原始脚本中 projectKey 有多次更新，这里使用一个示例project key
    project_key_placeholder = 'YOUR_PROJECT_KEY_HERE' 
    
    problem_solver = JudgeEMTPProblem_2(
        token=token_placeholder,
        api_url=api_url_placeholder,
        username=username_placeholder,
        project_key=project_key_placeholder
    )

    # comment: 第二步：调用 initialize_cloudpss_connection 函数，初始化 CloudPSS 连接设置。
    problem_solver.initialize_cloudpss_connection()

    # comment: 第三步：调用 fetch_cloudpss_model 函数，从 CloudPSS 获取模型。
    problem_solver.fetch_cloudpss_model()

    # comment: 第四步：调用 calculate_dc_line_parameters 函数，计算直流线路参数。
    problem_solver.calculate_dc_line_parameters()

    # comment: 第五步：调用 calculate_converter_station_power 函数，计算换流站侧功率参数。
    problem_solver.calculate_converter_station_power()

    # comment: 第六步：调用 display_results 函数，显示计算结果。
    problem_solver.display_results()

    print('End of script.')

# comment: 判断当前脚本是否作为主程序运行
if __name__ == '__main__':
    main()