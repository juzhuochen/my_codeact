#comment: 导入 os 模块，用于操作系统相关功能，如环境变量设置
import os
#comment: 导入 pandas 库，通常用于数据处理和分析
import pandas as pd
#comment: 导入 time 模块，用于时间相关操作，如延时
import time
#comment: 导入 sys 模块，用于访问系统特定的参数和功能
import sys
#comment: 导入 cloudpss 库，这是一个自定义的库，可能用于与 CloudPSS 平台进行交互
import cloudpss
#comment: 导入 math 模块，提供数学函数
import math
#comment: 导入 cmath 模块，提供复数数学函数
import cmath
#comment: 导入 numpy 库，用于科学计算，特别是数组和矩阵操作
import numpy as np
#comment: 从 numpy.linalg 导入 lg，通常是线性代数模块的别名
import numpy.linalg as lg
#comment: 从 jobApi1 导入 fetch, fetchAllJob, abort 三个函数，可能与作业管理相关 (假设这个库已安装或路径已配置)
try:
    from jobApi1 import fetch,fetchAllJob,abort
except ImportError:
    print("Warning: 'jobApi1' module not found. Some functionalities might be unavailable.")
#comment: 从 cloudpss.runner.result 导入 Result, PowerFlowResult, EMTResult，用于处理仿真结果
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
#comment: 导入 json 模块，用于处理 JSON 数据格式
import json
#comment: 导入 random 模块，用于生成随机数
import random
#comment: 导入 re 模块，用于正则表达式操作
import re
#comment: 导入 nest_asyncio 库，用于在已经运行的事件循环中运行 asyncio 代码
import nest_asyncio
#comment: 应用 nest_asyncio 补丁，允许嵌套使用 asyncio 事件循环
nest_asyncio.apply()
#comment: 导入 copy 模块，用于创建对象的副本
import copy
#comment: 从 cloudpss.job.job 导入 Job 类，并重命名为 cjob，可能用于表示 CloudPSS 平台上的一个任务
from cloudpss.job.job import Job as cjob


#comment: 定义一个函数 is_number，用于判断输入是否可以转换为数字
def is_number(s):
    #comment: 如果输入 s 是一个列表，则返回 False，因为它不是单个数字
    if(isinstance(s,list)):
        return False
    #comment: 尝试将 s 转换为浮点数
    try:
        float(s)
        #comment: 如果成功转换，则返回 True
        return True
    #comment: 如果发生 ValueError，表示无法直接转换为浮点数
    except ValueError:
        pass

    #comment: 再次尝试，使用 unicodedata.numeric 转换为数字
    try:
        import unicodedata
        #comment: unicodedata.numeric 可以处理一些特殊字符表示的数字
        unicodedata.numeric(s)
        #comment: 如果成功转换，则返回 True
        return True
    #comment: 如果发生 TypeError 或 ValueError，表示无法转换为数字
    except (TypeError, ValueError):
        pass

    #comment: 如果上述尝试都失败，则返回 False
    return False

#comment: 定义一个类 JudgeEMTPProblem_1，用于处理同步发电机模型参数的校验和修正
class JudgeEMTPProblem_1:
    """
    该类用于从CloudPSS平台获取指定的同步发电机模型，
    并对其内部的等效电路参数进行计算和校验。
    它包含以下功能：
    - 初始化CloudPSS连接配置。
    - 获取指定项目中的同步发电机组件。
    - 对每个同步发电机组件，根据其基本参数计算其等效电路参数。
    - 针对计算出的等效电路参数，校验其合理性，并尝试修正可能存在的错误参数。
    - 如果发电机模型为PD模型，进一步校验其稳定性条件。

    属性:
    - token (str): CloudPSS平台的认证令牌。
    - api_url (str): CloudPSS API的URL地址。
    - username (str): 用于获取模型的用户名。
    - project_key (str): CloudPSS平台上的项目唯一标识符。
    - delta_t (float): 仿真时间步长。
    - change_error (bool): 控制是否允许修正模型中检测到的不合理参数。
    - project_model (cloudpss.Model): 从CloudPSS平台获取到的项目模型对象。
    """
    def __init__(self, token, api_url, username, project_key, delta_t=0.00005, change_error=True):
        """
        初始化 JudgeEMTPProblem_1 类的实例。

        参数:
        - token (str): CloudPSS平台的认证令牌。
        - api_url (str): CloudPSS API的URL地址。
        - username (str): 用于获取模型的用户名。
        - project_key (str): CloudPSS平台上的项目唯一标识符。
        - delta_t (float, optional): 仿真时间步长，默认为 0.00005。
        - change_error (bool, optional): 控制是否允许修正模型中检测到的不合理参数，默认为 True。
        """
        #comment: 初始化 CloudPSS 认证令牌和 API URL
        self.token = token
        self.api_url = api_url
        self.username = username
        self.project_key = project_key
        #comment: 设置时间步长
        self.delta_t = delta_t
        #comment: 设置是否修正错误参数的标志
        self.change_error = change_error
        #comment: 初始化项目模型，在 connect_cloudpss 方法中获取
        self.project_model = None

    def connect_cloudpss(self):
        """
        设置CloudPSS的认证信息并连接到平台，获取指定的项目模型。

        功能:
        - 设置CloudPSS的认证令牌。
        - 设置CLOUDPSS_API_URL环境变量。
        - 从CloudPSS平台获取指定项目模型。

        参数:
        - 无

        返回:
        - cloudpss.Model: 成功获取到的项目模型对象。

        异常:
        - 如果连接失败或模型不存在，可能会抛出 cloudpss 相关的异常。
        """
        print('Connecting to CloudPSS...')
        #comment: 设置 CloudPSS 的认证令牌
        cloudpss.setToken(self.token)
        #comment: 设置 CLOUDPSS_API_URL 环境变量
        os.environ['CLOUDPSS_API_URL'] = self.api_url
        #comment: 从 CloudPSS 平台获取指定项目模型
        project = cloudpss.Model.fetch(f'model/{self.username}/{self.project_key}')
        print(f"Successfully fetched project: {self.project_key}")
        self.project_model = project
        return project

    def calculate_equivalent_circuit_parameters(self, component):
        """
        根据同步发电机组件的基本参数，计算其等效电路参数。

        参数:
        - component (cloudpss.Component): 同步发电机组件对象。

        返回:
        - dict: 包含计算出的等效电路参数的字典。
                如果计算过程中出现非正数，或者模型类型为PD/VBR且出现问题，
                则返回 None，并可能重置组件参数。
        """
        #comment: 获取组件的 ID
        comp_id = component.id
        #comment: 获取组件的标签（名称）
        label = component.label

        #comment: 获取并转换为浮点数：定子电阻 Rs
        ra = float(component.args['Rs_2'])
        #comment: 获取并转换为浮点数：定子漏抗 Xls
        xl = float(component.args['Xls_2'])
        #comment: 获取并转换为浮点数：直轴同步电抗 Xd
        xd = float(component.args['Xd_2'])
        #comment: 获取并转换为浮点数：直轴暂态电抗 Xdp
        xdp = float(component.args['Xdp_2'])
        #comment: 获取并转换为浮点数：直轴次暂态电抗 Xdpp
        xdpp = float(component.args['Xdpp_2'])
        #comment: 获取并转换为浮点数：交轴同步电抗 Xq
        xq = float(component.args['Xq_2'])
        #comment: 获取并转换为浮点数：交轴暂态电抗 Xqp
        xqp = float(component.args['Xqp_2'])
        #comment: 获取并转换为浮点数：交轴次暂态电抗 Xqpp
        xqpp = float(component.args['Xqpp_2'])
        #comment: 获取并转换为浮点数：直轴开路暂态时间常数 Td0p
        Td0p = float(component.args['Td0p_2'])
        #comment: 获取并转换为浮点数：直轴开路次暂态时间常数 Td0pp
        Td0pp = float(component.args['Td0pp_2'])
        #comment: 获取并转换为浮点数：交轴开路暂态时间常数 Tq0p
        Tq0p = float(component.args['Tq0p_2'])
        #comment: 获取并转换为浮点数：交轴开路次暂态时间常数 Tq0pp
        Tq0pp = float(component.args['Tq0pp_2'])
        #comment: 获取并转换为整数：同步发电机模型类型
        MType = int(component.args['ModelType'])
        #comment: 获取并转换为浮点数：额定频率 f
        f = float(component.args['freq'])
        #comment: 计算角频率 ω = 2πf
        w = 2 * math.pi * f
        #comment: 将定子电阻 ra 赋值给 Rs
        Rs = ra
        #comment: 将定子漏抗 xl 赋值给 Xls
        Xls = xl
        #comment: 将交轴同步电抗 xq 赋值给 Xq
        Xq = xq
        #comment: 将直轴同步电抗 xd 赋值给 Xd
        Xd = xd
        #comment: 计算直轴励磁电抗 Xad = Xd - Xls
        Xad = xd - xl
        #comment: 计算交轴励磁电抗 Xaq = Xq - Xls
        Xaq = xq - xl

        #comment: 计算励磁绕组漏抗 Xlfd
        Xlfd = Xad * Xad / (xd - xdp) - Xad
        #comment: 计算励磁绕组电阻 Rfd
        Rfd = (Xlfd + Xad) / (w * Td0p)

        #comment: 判断直轴次暂态电抗与暂态电抗是否接近（xdp ≈ xdpp）
        if (abs(xdp - xdpp) < 1e-6):
            #comment: 如果接近，设置直轴阻尼绕组漏抗 Xlkd 为一个很大的值（表示不存在或影响很小）
            Xlkd = 1e6
            #comment: 设置直轴阻尼绕组电阻 Rkd 为一个很大的值
            Rkd = 1e6
        else:
            #comment: 否则，计算直轴阻尼绕组漏抗 Xlkd
            Xlkd = (xdp - xl) ** 2 / (xdp - xdpp) + xl - xdp
            #comment: 计算直轴阻尼绕组电阻 Rkd
            Rkd = (xdp - xl) ** 2 / (xdp - xdpp) / (w * Td0pp)

        #comment: 判断交轴暂态电抗与同步电抗是否接近，或时间常数 Tq0p 是否很小/很大
        if ((abs(xq - xqp) < 1e-6) or (Tq0p < 1e-6) or (xqp < 1e-6) or (Tq0p > 500)):
            #comment: 如果满足条件，设置交轴阻尼绕组1漏抗 Xlkq1 为一个很大的值
            Xlkq1 = 1e6
            #comment: 设置交轴阻尼绕组1电阻 Rkq1 为一个很大的值
            Rkq1 = 1e6
            #comment: 将交轴暂态电抗 xqp 设为交轴同步电抗 xq
            xqp = xq
        else:
            #comment: 否则，计算交轴阻尼绕组1漏抗 Xlkq1
            Xlkq1 = Xaq * Xaq / (xq - xqp) - Xaq
            #comment: 计算交轴阻尼绕组1电阻 Rkq1
            Rkq1 = (Xlkq1 + Xaq) / (w * Tq0p)

        #comment: 判断交轴次暂态电抗与暂态电抗是否接近，或时间常数 Tq0pp 是否很小
        if ((abs(xqp - xqpp) < 1e-6) or (Tq0pp < 1e-6)):
            #comment: 如果满足条件，设置交轴阻尼绕组2漏抗 Xlkq2 为一个很大的值
            Xlkq2 = 1e6
            #comment: 设置交轴阻尼绕组2电阻 Rkq2 为一个很大的值
            Rkq2 = 1e6
        else:
            #comment: 否则，计算交轴阻尼绕组2漏抗 Xlkq2
            Xlkq2 = (xqp - xl) ** 2 / (xqp - xqpp) + xl - xqp
            #comment: 计算交轴阻尼绕组2电阻 Rkq2
            Rkq2 = (xqp - xl) ** 2 / (xqp - xqpp) / (w * Tq0pp)

        #comment: 将计算得到的等效电路参数存入字典
        calculated_params = {
            'label': label,
            'Rs': Rs,
            'Xls': Xls,
            'Xq': Xq,
            'Xd': Xd,
            'Rfd': Rfd,
            'Xlfd': Xlfd,
            'Rkd': Rkd,
            'Xlkd': Xlkd,
            'Rkq1': Rkq1,
            'Xlkq1': Xlkq1,
            'Rkq2': Rkq2,
            'Xlkq2': Xlkq2,
            'MType': MType,
            'w': w,
            'Xdpp_orig': xdpp, # 原始次暂态电抗用于后续计算校验
            'Xqpp_orig': xqpp,
            'xdp_orig': xdp,
            'xqp_orig': xqp,
            'xl_orig': xl
        }
        return calculated_params

    def validate_and_correct_parameters(self, component, calculated_params):
        """
        校验计算出的等效电路参数的合理性，如果发现不合理（非正数），
        则根据 self.change_error 标志尝试修正组件参数。

        参数:
        - component (cloudpss.Component): 原始的同步发电机组件对象。
        - calculated_params (dict): 包含计算出的等效电路参数的字典。

        返回:
        - bool: 如果所有参数合理或已修正成功返回 True，否则返回 False。
        """
        label = calculated_params['label']
        Rs = calculated_params['Rs']
        Xls = calculated_params['Xls']
        Xq = calculated_params['Xq']
        Xd = calculated_params['Xd']
        Rfd = calculated_params['Rfd']
        Xlfd = calculated_params['Xlfd']
        Rkd = calculated_params['Rkd']
        Xlkd = calculated_params['Xlkd']
        Rkq1 = calculated_params['Rkq1']
        Xlkq1 = calculated_params['Xlkq1']
        Rkq2 = calculated_params['Rkq2']
        Xlkq2 = calculated_params['Xlkq2']
        w = calculated_params['w']
        xdp = calculated_params['xdp_orig']
        xdpp = calculated_params['Xdpp_orig']
        xqp = calculated_params['xqp_orig']
        xqpp = calculated_params['Xqpp_orig']
        xl = calculated_params['xl_orig']
        Xd = calculated_params['Xd']


        #comment: 计算交轴磁化电抗 Xmq = Xq - Xls
        Xmq = Xq - Xls
        #comment: 计算直轴磁化电抗 Xmd = Xd - Xls
        Xmd = Xd - Xls
        #comment: 计算交轴磁化电感 Lmq = Xmq / w
        Lmq = Xmq / w
        #comment: 计算直轴磁化电感 Lmd = Xmd / w
        Lmd = Xmd / w
        #comment: 计算交轴阻尼绕组1漏电感 Llkq1 = Xlkq1 / w
        Llkq1=Xlkq1/w
        #comment: 计算交轴阻尼绕组2漏电感 Llkq2 = Xlkq2 / w
        Llkq2=Xlkq2/w
        #comment: 计算直轴阻尼绕组漏电感 Llkd = Xlkd / w
        Llkd = Xlkd/w
        #comment: 计算励磁绕组漏电感 Llfd = Xlfd / w
        Llfd = Xlfd/w

        #comment: 将所有待检查的参数放入一个列表
        params_to_check = [Llkq1, Llkq2, Llkd, Llfd, Lmq, Lmd, Rfd, Rkd, Rkq1, Rkq2]
        #comment: 检查所有计算出的电感和电阻是否合理（非正数）
        if min(params_to_check) <= 0:
            print(f'电机模型问题 (参数非正数): {label} - 参数值: {params_to_check}')
            #comment: 如果有不合理的参数，打印错误信息
            #comment: 如果允许修改错误参数
            if self.change_error:
                print(f"正在尝试为 {label} 修正错误参数为默认值...")
                #comment: 重新设置组件的参数为一组默认值（兜底值），防止后续计算出错
                component.args['Rs_2'] = str(0)
                component.args['Xls_2'] = str(0.189)
                component.args['Xd_2'] = str(2.18)
                component.args['Xdp_2'] = str(0.302)
                component.args['Xdpp_2'] = str(0.24)
                component.args['Xq_2'] = str(2.14)
                component.args['Xqp_2'] = str(0.48)
                component.args['Xqpp_2'] = str(0.24)
                component.args['Td0p_2'] = str(8.54)
                component.args['Td0pp_2'] = str(0.025)
                component.args['Tq0p_2'] = str(2)
                component.args['Tq0pp_2'] = str(0.04)
                print(f"参数已重置为默认值。")
                return False # 标记为修正过，需要重新处理
            else:
                return False # 不修正，直接返回失败

        return True

    def validate_and_correct_pd_model(self, component, calculated_params):
        """
        如果电机模型类型为 PD 模型，进一步校验其稳定性条件，并尝试修正。

        参数:
        - component (cloudpss.Component): 原始的同步发电机组件对象。
        - calculated_params (dict): 包含计算出的等效电路参数的字典。

        返回:
        - bool: 如果PD模型稳定性条件满足或已修正成功返回 True，否则返回 False。
        """
        label = calculated_params['label']
        MType = calculated_params['MType']
        w = calculated_params['w']
        Rfd = calculated_params['Rfd']
        Xlfd = calculated_params['Xlfd']
        Rkd = calculated_params['Rkd']
        Xlkd = calculated_params['Xlkd']
        Rkq1 = calculated_params['Rkq1']
        Xlkq1 = calculated_params['Xlkq1']
        Rkq2 = calculated_params['Rkq2']
        Xlkq2 = calculated_params['Xlkq2']
        Xd = calculated_params['Xd']
        Xq = calculated_params['Xq']
        Xls = calculated_params['Xls'],

        #comment: 如果电机模型类型为 0 (PD模型)
        if MType == 0:  # PD模型
            #comment: 计算交轴磁化电抗 Xmq = Xq - Xls
            Xmq = Xq - Xls[0] # Xls是一个元组，这里解包
            #comment: 计算直轴磁化电抗 Xmd = Xd - Xls
            Xmd = Xd - Xls[0]
            #comment: 计算交轴磁化电感 Lmq = Xmq / w
            Lmq = Xmq / w
            #comment: 计算直轴磁化电感 Lmd = Xmd / w
            Lmd = Xmd / w
            #comment: 计算交轴阻尼绕组1漏电感 Llkq1 = Xlkq1 / w
            Llkq1=Xlkq1/w
            #comment: 计算交轴阻尼绕组2漏电感 Llkq2 = Xlkq2 / w
            Llkq2=Xlkq2/w
            #comment: 计算直轴阻尼绕组漏电感 Llkd = Xlkd / w
            Llkd = Xlkd/w
            #comment: 计算励磁绕组漏电感 Llfd = Xlfd / w
            Llfd = Xlfd/w

            #comment: 计算直轴次暂态电感的倒数，再取倒数得到 Lmdpp
            Lmdpp = (1./Lmd + 1./Llfd + 1./Llkd)**(-1)
            #comment: 计算交轴次暂态电感的倒数，再取倒数得到 Lmqpp
            Lmqpp = (1./Lmq + 1./Llkq1 + 1./Llkq2)**(-1)


            #comment: 尝试执行以下代码块，处理 PD 模型参数
            try:
                #comment: 计算等效阻抗 Zmq
                Zmq = 2 / self.delta_t * Lmq
                #comment: 计算等效阻抗 Zmd
                Zmd = 2 / self.delta_t * Lmd

                #comment: 计算等效阻抗 Zlkq1
                Zlkq1 = Rkq1 + 2 / self.delta_t * Llkq1
                #comment: 计算等效阻抗 Zlkq2
                Zlkq2 = Rkq2 + 2 / self.delta_t * Llkq2

                #comment: 计算等效阻抗 Zlfd
                Zlfd = Rfd + 2 / self.delta_t * Llfd
                #comment: 计算等效阻抗 Zlkd1
                Zlkd1 = Rkd + 2 / self.delta_t * Llkd
                #comment: 计算交轴等效阻抗 Zq_2
                Zq_2 = 1 / (1 / Zmq + 1 / Zlkq1 + 1 / Zlkq2)
                #comment: 计算直轴等效阻抗 Zd_2
                Zd_2 = 1 / (1 / Zmd + 1 / Zlfd + 1 / Zlkd1)

                #comment: 检查 Zq_2 是否为零或接近于零，避免除以零
                if abs(Zq_2) < 1e-9: # 检查是否接近0
                    print(f'PD模型问题: {label} - Zq_2 接近零，无法计算 Zlkq3。')
                    if self.change_error:
                         print(f"正在尝试为 {label} 修正错误参数为默认值...")
                         # 重新设置组件的参数为一组默认值
                         self.reset_component_params(component)
                         print(f"参数已重置为默认值。")
                         return False
                    return False
                #comment: 计算等效阻抗 Zlkq3
                Zlkq3 = 1 / (1 / Zd_2 - 1 / Zq_2)

                #comment: 计算电感 Lc (此处可能有问题或为特定模型处理)
                Lc = (Zlkq3 - w / (1 / Lmq + 1 / Llkq1 + 1 / Llkq2)) / (w + 2 / self.delta_t)
                #comment: 将 Lc 赋值给 Llkq3
                Llkq3 = Lc
                #comment: 计算电阻 Rkq3
                Rkq3 = Zlkq3 - 2 / self.delta_t * Lc

                #comment: 检查 Llkq3 或 Rkq3 是否非正数
                if Llkq3 <= 0 or Rkq3 <= 0:
                    #comment: 打印 PD 模型参数问题信息
                    print(f'PD模型问题 (Llkq3或Rkq3非正数): {label} - Llkq3: {Llkq3}, Rkq3: {Rkq3}')
                    if self.change_error:
                        print(f"正在尝试为 {label} 修正错误参数为默认值...")
                        self.reset_component_params(component)
                        print(f"参数已重置为默认值。")
                        return False
                    return False

                #comment: 构建电阻矩阵 Rr
                Rr = np.diag([Rkq1,Rkq2,Rkq3,Rfd,Rkd])
                #comment: 构建电感矩阵 Lr
                Lr = np.mat([[Llkq1 + Lmq,Lmq,Lmq,0,0],
                    [Lmq,Llkq2+Lmq,Lmq,0,0],
                    [Lmq,Lmq,Llkq3+Lmq,0,0],
                    [0,0,0,Llfd+Lmd,Lmd],
                    [0,0,0,Lmd,Llkd+Lmd]])
                #comment: 计算 Q 矩阵，这通常是梯形积分法中的一个系数矩阵
                Q = (2/self.delta_t*Lr + Rr)**(-1)*(2/self.delta_t*Lr - Rr)
                
                #comment: 检查 Q 矩阵特征值是否超出范围（>1 或 <0），或 Llkq3_corrected 是否为零
                eig_vals = lg.eigvals(Q)
                if np.any(eig_vals > 1 + 1e-9) or np.any(eig_vals < - 1e-9) or Llkq3 <= 1e-9: # 增加一个小容差进行比较
                    print(f'PD模型问题 (Q矩阵特征值或Llkq3不合理): {label} - 特征值: {eig_vals}, Llkq3: {Llkq3}')
                    if self.change_error:
                        print(f"正在尝试为 {label} 修正错误参数为默认值...")
                        self.reset_component_params(component)
                        print(f"参数已重置为默认值。")
                        return False
                    return False

            #comment: 捕获异常，处理 PD 模型参数计算中的错误
            except Exception as e:
                print(f'PD模型问题 (计算异常): {label} - 错误信息: {e}')
                #comment: 如果允许修改错误参数
                if self.change_error:
                    print(f"正在尝试为 {label} 修正错误参数为默认值...")
                    self.reset_component_params(component)
                    print(f"参数已重置为默认值。")
                    return False
                return False
        return True

    def validate_and_correct_vbr_model(self, component, calculated_params):
        """
        如果电机模型类型为 VBR 模型 (MType == 1)，校验其稳定性条件，并尝试修正。

        参数:
        - component (cloudpss.Component): 原始的同步发电机组件对象。
        - calculated_params (dict): 包含计算出的等效电路参数的字典。

        返回:
        - bool: 如果VBR模型稳定性条件满足或已修正成功返回 True，否则返回 False。
        """
        label = calculated_params['label']
        MType = calculated_params['MType']
        w = calculated_params['w']
        Rfd = calculated_params['Rfd']
        Xlfd = calculated_params['Xlfd']
        Rkd = calculated_params['Rkd']
        Xlkd = calculated_params['Xlkd']
        Rkq1 = calculated_params['Rkq1']
        Xlkq1 = calculated_params['Xlkq1']
        Rkq2 = calculated_params['Rkq2']
        Xlkq2 = calculated_params['Xlkq2']
        Xd = calculated_params['Xd']
        Xq = calculated_params['Xq']
        Xls = calculated_params['Xls'],

        #comment: 如果电机模型类型为 1 (VBR模型)
        if MType == 1:
            #comment: 计算交轴磁化电抗 Xmq = Xq - Xls
            Xmq = Xq - Xls[0] # Xls是一个元组，这里解包
            #comment: 计算直轴磁化电抗 Xmd = Xd - Xls
            Xmd = Xd - Xls[0]
            #comment: 计算交轴磁化电感 Lmq = Xmq / w
            Lmq = Xmq / w
            #comment: 计算直轴磁化电感 Lmd = Xmd / w
            Lmd = Xmd / w
            #comment: 计算交轴阻尼绕组1漏电感 Llkq1 = Xlkq1 / w
            Llkq1=Xlkq1/w
            #comment: 计算交轴阻尼绕组2漏电感 Llkq2 = Xlkq2 / w
            Llkq2=Xlkq2/w
            #comment: 计算直轴阻尼绕组漏电感 Llkd = Xlkd / w
            Llkd = Xlkd/w
            #comment: 计算励磁绕组漏电感 Llfd = Xlfd / w
            Llfd = Xlfd/w

            #comment: 计算直轴次暂态电感的倒数，再取倒数得到 Lmdpp
            Lmdpp = (1./Lmd + 1./Llfd + 1./Llkd)**(-1)
            #comment: 计算交轴次暂态电感的倒数，再取倒数得到 Lmqpp
            Lmqpp = (1./Lmq + 1./Llkq1 + 1./Llkq2)**(-1)

            #comment: 尝试执行以下代码块，处理 VBR 模型参数
            try:
                #comment: 构建 K1 矩阵，这通常是一个状态矩阵的一部分
                K1 = np.array([
                    [ (-Rkq1/Llkq1+Rkq1/Llkq1/Llkq1*Lmqpp), (Rkq1/Llkq1/Llkq2*Lmqpp), 0, 0],
                    [(Rkq2/Llkq1/Llkq2*Lmqpp), (-Rkq2/Llkq2+Rkq2/Llkq2/Llkq2*Lmqpp), 0, 0],
                    [0, 0, (-Rfd/Llfd+Rfd/Llfd/Llfd*Lmdpp), (Rfd/Llfd/Llkd*Lmdpp)],
                    [0, 0, (Rkd/Llfd/Llkd*Lmdpp), (-Rkd/Llkd+Rkd/Llkd/Llkd*Lmdpp)]
                ])
                
                #comment: 计算 Pflux 矩阵，这可能与状态空间模型的时间离散化有关
                Pflux = (2.0/self.delta_t*np.eye(4)-K1) @ np.linalg.inv((2.0/self.delta_t*np.eye(4)+K1)) # 使用 @ 运算符进行矩阵乘法
                #comment: 检查 Pflux 矩阵的特征值是否大于等于 1
                eig_vals = lg.eigvals(Pflux)
                if np.any(eig_vals >= 1 + 1e-9): # 增加一个小容差
                    print(f'VBR模型问题 (Pflux矩阵特征值不合理): {label} - 特征值: {eig_vals}')
                    if self.change_error:
                        print(f"正在尝试为 {label} 修正错误参数为默认值...")
                        self.reset_component_params(component)
                        print(f"参数已重置为默认值。")
                        return False
                    return False
            #comment: 捕获异常，处理 VBR 模型参数计算中的错误
            except Exception as e:
                print(f'VBR模型问题 (计算异常): {label} - 错误信息: {e}')
                #comment: 如果允许修改错误参数
                if self.change_error:
                    print(f"正在尝试为 {label} 修正错误参数为默认值...")
                    self.reset_component_params(component)
                    print(f"参数已重置为默认值。")
                    return False
                return False
        return True

    def reset_component_params(self, component):
        """
        将组件的参数重置为一组预设的默认值。

        参数:
        - component (cloudpss.Component): 需要重置参数的组件对象。
        """
        component.args['Rs_2'] = str(0)
        component.args['Xls_2'] = str(0.189)
        component.args['Xd_2'] = str(2.18)
        component.args['Xdp_2'] = str(0.302)
        component.args['Xdpp_2'] = str(0.24)
        component.args['Xq_2'] = str(2.14)
        component.args['Xqp_2'] = str(0.48)
        component.args['Xqpp_2'] = str(0.24)
        component.args['Td0p_2'] = str(8.54)
        component.args['Td0pp_2'] = str(0.025)
        component.args['Tq0p_2'] = str(2)
        component.args['Tq0pp_2'] = str(0.04)

    def process_all_generators(self):
        """
        遍历项目中所有同步发电机，计算并校验其等效电路参数及模型稳定性。

        功能:
        - 遍历项目中所有类型为 'model/CloudPSS/SyncGeneratorRouter' 的组件。
        - 对每个发电机，调用内部方法计算等效参数，并进行参数合理性及模型类型校验。
        - 记录所有成功处理的发电机的等效电路数据。

        参数:
        - 无

        返回:
        - list: 包含所有成功处理的发电机的等效电路参数字典的列表。
        """
        if not self.project_model:
            print("Error: Project model not loaded. Please call connect_cloudpss first.")
            return []

        processed_generators_data = []
        #comment: 遍历项目中所有类型为 'model/CloudPSS/SyncGeneratorRouter' 的组件
        generator_components = self.project_model.getComponentsByRid('model/CloudPSS/SyncGeneratorRouter')
        
        if not generator_components:
            print("No SyncGeneratorRouter components found in the project.")
            return []

        for i, original_component in generator_components.items():
            # 使用 copy.deepcopy 复制组件，避免在循环中直接修改原始组件导致迭代问题
            j = copy.deepcopy(original_component)
            print(f"\nProcessing generator: {j.label}")
            
            # 使用一个循环处理修正后的参数，直到参数合理或不再允许修正
            for attempt in range(3): # 尝试最多3次
                calculated_params = self.calculate_equivalent_circuit_parameters(j)
                if not calculated_params:
                    print(f"Warning: Failed to calculate initial parameters for {j.label}.")
                    break # 无法计算，跳过此组件

                # 校验并修正基本参数
                is_params_valid = self.validate_and_correct_parameters(j, calculated_params)
                if not is_params_valid:
                    if self.change_error and attempt < 2: # 如果允许修正且未达到最大尝试次数，则重新计算参数
                        print(f"Retrying parameter calculation for {j.label} after reset...")
                        continue # 继续下一次循环，重新计算
                    else:
                        print(f"Failed to fix parameters for {j.label} after multiple attempts or correction disallowed.")
                        break # 无法修正，跳过此组件

                # 基本参数已有效，现在重新计算以便后续模型校验使用最新的参数
                calculated_params = self.calculate_equivalent_circuit_parameters(j)
                if not calculated_params: # 再次检查计算是否成功
                    print(f"Warning: Failed to recalculate parameters after parameter correction for {j.label}.")
                    break
                
                MType = int(j.args['ModelType']) # 获取模型类型

                # 根据模型类型校验和修正特定模型
                model_check_passed = True
                if MType == 0: # PD模型
                    model_check_passed = self.validate_and_correct_pd_model(j, calculated_params)
                elif MType == 1: # VBR模型
                    model_check_passed = self.validate_and_correct_vbr_model(j, calculated_params)
                
                if not model_check_passed:
                    if self.change_error and attempt < 2:
                        print(f"Retrying model check for {j.label} after reset...")
                        continue # 继续下一次循环，重新计算
                    else:
                        print(f"Failed to fix model {('PD' if MType == 0 else 'VBR')} for {j.label} after multiple attempts or correction disallowed.")
                        break # 无法修正，跳过此组件
                
                # 如果所有校验都通过，则跳出尝试循环
                print(f"Generator {j.label} parameters and model check passed.")
                processed_generators_data.append(calculated_params)
                break # 成功处理，跳出循环

            # 将可能被修改的组件参数写回原始模型对象
            original_component.args = j.args
        
        return processed_generators_data


#comment: 当脚本作为主程序运行时执行以下代码块
def main():
    """
    脚本的主执行函数。
    负责初始化类，并按顺序调用类中的方法来完成业务逻辑。
    """
    print('Start script execution.')

    #comment: 替换敏感信息为占位符
    auth_token = 'YOUR_CLOUDPS_AUTH_TOKEN'
    api_endpoint = 'http://cloudpss-api.example.com/' # 替换为真实的API地址
    user_name = 'your_username' # 替换为真实的用户名
    project_identifier = 'your_project_key' # 替换为真实的项目Key

    #comment: 实例化 JudgeEMTPProblem_1 类
    # 第一步：创建 JudgeEMTPProblem_1 类的实例，初始化所需参数
    print("\n第一步：创建 JudgeEMTPProblem_1 类的实例，初始化所需参数。")
    generator_validator = JudgeEMTPProblem_1(
        token=auth_token,
        api_url=api_endpoint,
        username=user_name,
        project_key=project_identifier,
        delta_t=0.00005,
        change_error=True
    )

    # 第二步：连接到 CloudPSS 平台并获取项目模型
    print("\n第二步：连接到 CloudPSS 平台并获取指定项目模型。")
    try:
        generator_validator.connect_cloudpss()
    except Exception as e:
        print(f"Error connecting to CloudPSS or fetching project: {e}")
        return # 连接失败，终止后续操作

    # 第三步：处理项目中所有同步发电机组件，并进行参数计算、校验和潜在修正
    print("\n第三步：处理项目中所有同步发电机组件，并进行参数计算、校验和潜在修正。")
    all_processed_data = generator_validator.process_all_generators()

    # 第四步：输出处理结果统计
    print("\n第四步：输出处理结果统计。")
    if all_processed_data:
        print(f"\n成功处理了 {len(all_processed_data)} 个同步发电机组件。")
        print("以下是部分处理后的参数示例:")
        for idx, data in enumerate(all_processed_data[:3]): # 仅打印前3个示例
            print(f"  Generator {idx+1} ({data['label']}): Rs={data['Rs']:.4f}, Xls={data['Xls']:.4f}, Xd={data['Xd']:.4f}, Xq={data['Xq']:.4f}")
            # print(json.dumps(data, indent=2)) # 如果想看完整数据结构
            
    else:
        print("\n未能成功处理任何同步发电机组件，或项目中没有相关组件。")

    # 第五步 (可选): 将更新后的项目模型保存回 CloudPSS (如果模型参数已修改)
    # 注意：实际项目中，这通常需要用户明确的保存操作，这里仅作为示例提供
    print("\n第五步：(可选)将更新后的项目模型保存回 CloudPSS。")
    try:
        # 仅当 project_model 存在且可能被修改时才尝试保存
        if generator_validator.project_model:
            print(f"Note: To save changes to CloudPSS, project_model.save() would be called here.")
            # 例如: generator_validator.project_model.save() # 这将需要适当的权限和API支持
    except Exception as e:
        print(f"Error saving project model: {e}")

    print('\nScript execution finished.')

#comment: 当脚本作为主程序运行时执行以下代码块
if __name__ == '__main__':
    main()