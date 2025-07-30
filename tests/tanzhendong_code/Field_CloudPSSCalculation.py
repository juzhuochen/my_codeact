#comment: 导入os模块，用于操作系统相关功能，比如文件路径操作
import os
#comment: 导入pandas库，通常用于数据处理和分析
import pandas as pd
#comment: 导入time模块，用于处理时间相关功能
import time
#comment: 导入sys模块，提供对解释器使用或维护的一些变量的访问，以及与解释器强烈交互的函数，例如sys.path来修改模块搜索路径
import sys
#comment: 导入cloudpss库，这是一个与CloudPSS平台交互的自定义库
import cloudpss
#comment: 从cloudpss.model.implements.component模块中导入Component类，用于表示模型中的组件
from cloudpss.model.implements.component import Component
#comment: 导入math模块，提供数学函数
import math
#comment: 导入numpy库，通常用于科学计算，特别是数组操作
import numpy as np
#comment: 从jobApi1模块导入fetch, fetchAllJob, abort函数，可能用于管理CloudPSS上的仿真作业
from jobApi1 import fetch,fetchAllJob,abort
#comment: 从CaseEditToolbox模块导入CaseEditToolbox类，用于编辑仿真案例
from CaseEditToolbox import CaseEditToolbox
#comment: 从CaseEditToolbox模块导入is_number函数，用于判断一个字符串是否能转换为数字
from CaseEditToolbox import is_number
#comment: 从PSAToolbox模块导入PSAToolbox类，用于电力系统分析工具箱功能
from PSAToolbox import PSAToolbox
# from convertToComtrade import convertToComtrade
#comment: 导入json模块，用于JSON数据的编码和解码
import json
#comment: 导入random模块，用于生成随机数
import random
#comment: 导入re模块，用于正则表达式操作
import re
#comment: 导入copy模块，用于对象的复制
import copy
#comment: 导入subprocess模块，用于创建新进程
import subprocess

#comment: 导入nest_asyncio模块，允许嵌套asyncio事件循环
import nest_asyncio
#comment: 应用nest_asyncio补丁，解决在某些环境（如Jupyter notebooks）中运行asyncio代码的问题
nest_asyncio.apply()


# # configs

#comment: 定义一个名为edgeJson0的字典，表示一个边的基本配置，用于创建连接线
edgeJson0 = {'attrs': {'line': {'sourceMarker': {'args': {'cx': 0, 'r': 0.5},
    'name': 'circle'},
   'stroke': 'var(--stroke)',
   'strokeWidth': 'var(--stroke-width)',
   'targetMarker': {'args': {'cx': 0, 'r': 0.5}, 'name': 'circle'}},
  'lines': {'connection': True, 'strokeLinejoin': 'round'},
  'root': {'style': {'--stroke': 'var(--edge-electrical-stroke,var(--edge-stroke))',
    '--stroke-opacity': 1,
    '--stroke-width': 2}}},
 'canvas': 'canvas_0',
 'id': 'edge_C6e3Y9BL2qLf',
 'router': {'name': 'normal'},
 'shape': 'diagram-edge',
 'source': {'anchor': {'name': 'center'},
  'cell': 'component_new_transformer_3_p_2_w_1',
  'port': '0'},
 'target': {'anchor': {'args': {'dx': '40%', 'dy': '0%', 'rotate': True},
   'name': 'center'},
  'cell': 'canvas_0_1088',
  'port': '0',
  'selector': '> path:nth-child(2)'},
 'vertices': [],
 'zIndex': 7}


class Field_CloudPSSCalculation:
    """
    Field_CloudPSSCalculation 类用于封装与CloudPSS平台进行场路耦合仿真相关的操作。
    它集成了模型配置、Exchange元件导入、仿真运行、结果处理以及外部有限元计算的逻辑。

    属性:
    - token (str): CloudPSS API的认证令牌。敏感信息，会被替换为占位符。
    - api_url (str): CloudPSS API的URL地址。敏感信息，会被替换为占位符。
    - username (str): CloudPSS平台的用户名称。敏感信息，会被替换为占位符。
    - project_key (str): CloudPSS项目中当前操作的项目唯一标识。
    - comp_lib_path (str): 组件库JSON文件的路径。
    - psatoolbox (PSAToolbox): PSAToolbox类的实例，用于与CloudPSS交互的核心工具。
    - exchange_files (list): 包含待导入的Exchange JSON文件路径的列表。
    - _exchange_models_rid (str): Exchange模型的资源ID。敏感信息，会被替换为占位符。
    - _sa_project_suffix (str): 用于保存SA项目名称的后缀。
    - _job_name (str): 仿真作业的名称。
    - _config_name (str): 仿真配置的名称。
    -_fe_python_path (str): 有限元计算所用的Python解释器路径。
    -_fe_main_script (str): 有限元计算的主脚本路径。
    -_fe_input_data_path (str): 有限元计算的输入数据路径。
    -_fe_param (str): 传递给有限元计算脚本的参数。
    """
    def __init__(self, token, api_url, username, project_key, comp_lib_path='saSource.json',
                 exchange_models_rid='MODEL_EXCHANGE_RID_PLACEHOLDER', # 替换为占位符
                 sa_project_suffix='SA', job_name='SIMULATION_JOB_NAME_PLACEHOLDER', # 替换为占位符
                 config_name='SIMULATION_CONFIG_NAME_PLACEHOLDER', # 替换为占位符
                 fe_python_path='FE_PYTHON_PATH_PLACEHOLDER', # 替换为占位符
                 fe_main_script='FE_MAIN_SCRIPT_PLACEHOLDER', # 替换为占位符
                 fe_input_data_path='FE_INPUT_DATA_PATH_PLACEHOLDER', # 替换为占位符
                 fe_param='FE_PARAM_PLACEHOLDER'): # 替换为占位符
        """
        初始化 Field_CloudPSSCalculation 类的实例。

        参数:
            token (str): CloudPSS API的认证令牌。
            api_url (str): CloudPSS API的URL地址。
            username (str): CloudPSS平台的用户名称。
            project_key (str): CloudPSS项目中当前操作的项目唯一标识。
            comp_lib_path (str, optional): 组件库JSON文件的路径。默认为 'saSource.json'。
            exchange_models_rid (str, optional): Exchange模型的资源ID。
            sa_project_suffix (str, optional): 用于生成SA项目名的后缀。
            job_name (str, optional): 仿真作业的名称。
            config_name (str, optional): 仿真配置的名称。
            fe_python_path (str, optional): 有限元计算所用的Python解释器路径。
            fe_main_script (str, optional): 有限元计算的主脚本路径。
            fe_input_data_path (str, optional): 有限元计算的输入数据路径。
            fe_param (str, optional): 传递给有限元计算脚本的参数。
        """
        self.token = token
        self.api_url = api_url
        self.username = username
        self.project_key = project_key
        self.comp_lib_path = comp_lib_path
        self.psatoolbox = None
        self.exchange_files = [] # 初始化为空列表，因为这个通常在外部传入，或者在其他方法中设置
        self._exchange_models_rid = exchange_models_rid
        self._sa_project_suffix = sa_project_suffix
        self._job_name = job_name
        self._config_name = config_name
        self._fe_python_path = fe_python_path
        self._fe_main_script = fe_main_script
        self._fe_input_data_path = fe_input_data_path
        self._fe_param = fe_param

    def initialize_cloudpss_toolbox(self):
        """
        初始化并配置 PSAToolbox 实例。

        功能:
            加载组件库，设置CloudPSS连接信息，初始化仿真条件，并创建SA画布。

        参数:
            无

        返回:
            PSAToolbox: 配置好的PSAToolbox实例。
        """
        #comment: 打开并读取saSource.json文件，加载组件库
        with open(self.comp_lib_path, "r", encoding='utf-8') as f:
            comp_lib = json.load(f)
        #comment: 创建PSAToolbox实例
        ce = PSAToolbox()
        #comment: 配置PSAToolbox实例的连接信息和项目信息
        ce.setConfig(self.token, self.api_url, self.username, self.project_key, comLibName=self.comp_lib_path, compLib=comp_lib)
        #comment: 设置是否生成iGraph信息
        generate_graph = False
        #comment: 将iGraph生成选项赋值给ce.config['iGraph']
        ce.config['iGraph'] = generate_graph  # 生成iGraph信息，已有iGraph信息时注释本块
        #comment: 设置是否删除边
        ce.config['deleteEdges'] = False # 初始导入时通常不删除边
        #comment: 设置初始条件
        ce.setInitialConditions() # 进行初始化
        #comment: 创建SA画布
        ce.createSACanvas()
        self.psatoolbox = ce
        return ce

    def import_exchange_components(self, exchange_file_paths):
        """
        导入并处理Exchange文件，将Exchange元件及其相关的分线器、集线器添加到CloudPSS模型中。

        功能:
            读取Exchange JSON文件，解析其中定义的输入输出参数，
            根据参数动态生成并在画布上添加“Exchange”元件、
            用于输入的“集线器”(_ChannelMerge)和用于输出的“分线器”(_ChannelDeMerge)，
            并自动连接这些元件。

        参数:
            exchange_file_paths (list): 包含Exchange JSON文件路径的列表。

        返回:
            list: 包含每个导入Exchange模型及其关联的分线器和集线器ID的列表。
                  每个子列表的格式为: [exchange元件id, 输出分线器id, 输入集线器id]。
        """
        self.exchange_files = exchange_file_paths
        ce = self.psatoolbox
        if not ce:
            raise ValueError("PSAToolbox not initialized. Call initialize_cloudpss_toolbox first.")

        exchange_jsons = []
        #comment: 遍历exchangeFiles列表中的每一个文件路径
        for n in self.exchange_files:
            #comment: 打开文件并以UTF-8编码读取
            with open(n, "r", encoding='utf-8') as f:
                #comment: 解析JSON文件内容
                exchange_json = json.load(f)
                #comment: 将解析后的JSON添加到exchangeJsons列表
                exchange_jsons.append(exchange_json)
                #comment: 打印导入的文件名
                print(f'Import {n}')
        #comment: 生成一个临时时间戳，用于创建唯一ID
        temp_time = time.strftime("%Y%m%d%H%M%S", time.localtime())+str(random.randint(100,999))
        #comment: 初始化一个空列表，用于存储Exchange模型ID
        ex_model_ids = []

        #comment: 检查ce对象是否包含countLabel属性，如果没有则初始化它
        if('countLabel' not in dir(ce)):
            ce.countLabel = {}
        #comment: 遍历exchangeJsons列表中的每一个Exchange JSON对象
        for j in range(len(exchange_jsons)):
            #comment: 初始化一个临时列表，用于存储当前Exchange元件的ID信息
            ex_model_id_temp = [] #[exchange元件id，输出分线器id，输入集线器id]
            #comment: 获取当前的Exchange JSON对象
            ex_json = exchange_jsons[j]
            #comment: 生成一个临时的唯一ID后缀
            extemp_id = '_newTHD_'+temp_time+'_'+str(j);


            # exchange元件参数处理
            #comment: 初始化PinInName列表，用于存储输入引脚的名称和属性
            pin_in_name = []
            #comment: 遍历exJson中InputPara的键值对
            for k,o in ex_json['InputPara'].items():
                #comment: 为每个输入参数创建一个字典条目，包含名称、类型、维度和随机ID
                pin_in_name.append({"0": k, "1": o['Name'], "2": o['Type'], "3": str(o['Dim']), "ɵid": random.randint(10000000,99999999)})
            #comment: 初始化PinOutName列表，用于存储输出引脚的名称和属性
            pin_out_name = []
            #comment: 遍历exJson中OutputPara的键值对
            for k,o in ex_json['OutputPara'].items():
                #comment: 遍历每个输出参数内部的键值对
                for p,q in o.items():
                    #comment: 如果键是'Name'则跳过
                    if(p=='Name'):
                        continue
                    #comment: 为每个输出参数的子项创建一个字典条目，包含名称、类型、维度和随机ID
                    pin_out_name.append({"0": k, "1": p, "2": str(q[0]), "3": str(q[1]), "ɵid": random.randint(10000000,99999999)})
            # print(exPinOutName)
            # print(exPinInName)
            # 添加exchange元件
            #comment: 准备Exchange元件的参数字典
            ex_args_temp = {
                    "DimIn": sum([i['Dim'] for i in ex_json['InputPara'].values()]), #comment: 计算总输入维度
                    "DimOut": sum([sum([i[j][0] for j in i.keys() if j != 'Name']) for i in ex_json['OutputPara'].values()]), #comment: 计算总输出维度
                    "FileDir": ex_json['Path'], #comment: 设置文件目录
                    "Name": ex_json['ID'], #comment: 设置名称
                    "PinInName": pin_in_name, #comment: 设置输入引脚名称
                    "PinOutName": pin_out_name #comment: 设置输出引脚名称
                }
            #comment: 准备Exchange元件的引脚字典，预留Input和Output口
            ex_pins_temp = {
                "Input": "",
                "Output":""
            }


            # 添加分线器_out
            #comment: 生成输出分线器的临时ID
            outtemp_id = extemp_id+'_DeMerge';
            #comment: 生成输出分线器的名称
            outname_temp = ex_json['ID']+'_DeMerge';
            #comment: 初始化OutTemp列表，用于存储输出分线器的输出引脚配置
            out_temp = []
            #comment: 初始化posx，用于计算引脚的起始位置
            posx = 0
            #comment: 遍历PinOutName列表中的每一个输出引脚
            for i in range(len(pin_out_name)):
                #comment: 为每个输出引脚创建配置字典
                out_temp.append({
                    "0": pin_out_name[i]['0']+'.'+pin_out_name[i]['1'], #comment: 组合父名称和子名称作为引脚名
                    "1": str(posx), #comment: 引脚的起始位置
                    "2": "0", #comment: 固定值
                    "3": pin_out_name[i]['2'], #comment: 引脚的维度
                    "4": "1", #comment: 固定值
                    "ɵid": i+1 #comment: 随机ID
                })

                #comment: 更新posx为下一个引脚的起始位置
                posx += int(pin_out_name[i]['2'])

            #comment: 调整_ChannelDeMerge组件在组件库中的高度，以适应引脚数量
            ce.compLib['_ChannelDeMerge']['size']['height'] = 20 + 20*len(pin_out_name)
            #comment: 准备输出分线器的参数字典
            out_args_temp = {
                "InDimX": str(posx), #comment: 输入维度X
                "InDimY": "1", #comment: 输入维度Y
                "InName": "In", #comment: 输入引脚名称
                "Out": out_temp} #comment: 输出引脚配置
            #comment: 准备输出分线器的引脚字典，预留InName口
            out_pins_temp = {"InName": ""}
            #comment: 为每个输出引脚添加一个ID口
            for i in range(len(pin_out_name)):
                out_pins_temp[f'id-{i+1}'] = ""


            # 添加集线器_in
            #comment: 生成输入集线器的临时ID
            intemp_id = extemp_id+'_Merge';
            #comment: 生成输入集线器的名称
            inname_temp = ex_json['ID']+'_Merge';
            #comment: 初始化InTemp列表，用于存储输入集线器的输入引脚配置
            in_temp = []
            #comment: 初始化posx，用于计算引脚的起始位置
            posx = 0
            #comment: 遍历PinInName列表中的每一个输入引脚
            for i in range(len(pin_in_name)):
                #comment: 为每个输入引脚创建配置字典
                in_temp.append({
                    "0": pin_in_name[i]['0']+'.'+pin_in_name[i]['1'], #comment: 组合父名称和子名称作为引脚名
                    "1": str(posx), #comment: 引脚的起始位置
                    "2": "0", #comment: 固定值
                    "3": pin_in_name[i]['3'], #comment: 引脚的维度
                    "4": "1", #comment: 固定值
                    "ɵid": i+1 #comment: 随机ID
                })
                #comment: 更新posx为下一个引脚的起始位置
                posx += int(pin_in_name[i]['3'])

            #comment: 准备输入集线器的参数字典
            in_args_temp = {
                "OutDimX": str(posx), #comment: 输出维度X
                "OutDimY": "1", #comment: 输出维度Y
                "OutName": "Out", #comment: 输出引脚名称
                "In": in_temp} #comment: 输入引脚配置
            #comment: 准备输入集线器的引脚字典，预留OutName口
            in_pins_temp = {"OutName": ""}
            #comment: 为每个输入引脚添加一个ID口
            for i in range(len(pin_in_name)):
                in_pins_temp[f'id-{i+1}'] = ""
            #comment: 调整_ChannelMerge组件在组件库中的高度，以适应引脚数量
            ce.compLib['_ChannelMerge']['size']['height'] = 20 + 20*len(pin_in_name)

            # 正式添加元件
            #comment: 在画布上添加_ChannelMerge（集线器）元件
            inid1, label = ce.addCompInCanvas(ce.compLib['_ChannelMerge'], key = intemp_id, canvas = ce.cPSAid,args = in_args_temp, pins = in_pins_temp, label = inname_temp, MaxX = 500,
                                            addN = False, addN_label = False)
            #comment: 在画布上添加model_exchange（Exchange）元件
            exid1, exlabel = ce.addCompInCanvas(ce.compLib['model_exchange'], key = extemp_id, canvas = ce.cPSAid, args = ex_args_temp, pins = ex_pins_temp, label = ex_json['ID'], MaxX = 500,
                                            addN = False, addN_label = False)
            #comment: 在画布上添加_ChannelDeMerge（分线器）元件
            outid1, label = ce.addCompInCanvas(ce.compLib['_ChannelDeMerge'], key = outtemp_id, canvas = ce.cPSAid,args = out_args_temp, pins = out_pins_temp, label = outname_temp, MaxX = 500,
                                            addN = False, addN_label = False)

            #comment: 将Exchange元件的ID添加到临时列表中
            ex_model_id_temp.append(exid1)
            #comment: 将输出分线器的ID添加到临时列表中
            ex_model_id_temp.append(outid1)
            #comment: 将输入集线器的ID添加到临时列表中
            ex_model_id_temp.append(inid1)

            # 用连接线相连
            #comment: 复制一份基础的edgeJson0用于创建连接线
            edgeJson1 = copy.deepcopy(edgeJson0)
            #comment: 设置连接线的源元件ID为Exchange元件ID
            edgeJson1['source']['cell'] = ex_model_id_temp[0]
            #comment: 设置连接线的源引脚为'Output'
            edgeJson1['source']['port'] = 'Output'
            #comment: 设置连接线的目标元件ID为输出分线器ID
            edgeJson1['target']['cell'] = ex_model_id_temp[1]
            #comment: 设置连接线的目标引脚为'InName'
            edgeJson1['target']['port'] = 'InName'
            #comment: 设置连接线的ID
            edgeJson1['id'] = extemp_id + '_edge1'
            #comment: 设置连接线所在的画布ID
            edgeJson1['canvas'] = ce.cPSAid
            #comment: 创建一个Component对象表示这条连接线
            ecomp = Component(edgeJson1)
            #comment: 将连接线添加到项目中的diagram cells
            ce.project.revision.implements.diagram.cells[edgeJson1['id']]=ecomp

            #comment: 复制一份基础的edgeJson0用于创建第二条连接线
            edgeJson1 = copy.deepcopy(edgeJson0)
            #comment: 设置连接线的源元件ID为Exchange元件ID
            edgeJson1['source']['cell'] = ex_model_id_temp[0]
            #comment: 设置连接线的源引脚为'Input'
            edgeJson1['source']['port'] = 'Input'
            #comment: 设置连接线的目标元件ID为输入集线器ID
            edgeJson1['target']['cell'] = ex_model_id_temp[2]
            #comment: 设置连接线的目标引脚为'OutName'
            edgeJson1['target']['port'] = 'OutName'
            #comment: 设置连接线的ID
            edgeJson1['id'] = extemp_id + '_edge2'
            #comment: 设置连接线所在的画布ID
            edgeJson1['canvas'] = ce.cPSAid
            #comment: 创建一个Component对象表示这条连接线
            ecomp = Component(edgeJson1)
            #comment: 将连接线添加到项目中的diagram cells
            ce.project.revision.implements.diagram.cells[edgeJson1['id']]=ecomp

            #comment: 将当前处理的Exchange模型ID列表添加到总的exModelIDs列表中
            ex_model_ids.append(ex_model_id_temp)
            #comment: 刷新画布上的元件布局
            ce.newLinePos(ce.cPSAid)

        return ex_model_ids

    def save_cloudpss_project(self):
        """
        保存当前的CloudPSS项目到平台。

        功能:
            将当前PSAToolbox实例中的项目配置保存到CloudPSS平台。
            项目名称将基于实例化时传入的 project_key 和 _sa_project_suffix 组合。

        参数:
            无

        返回:
            None
        """
        ce = self.psatoolbox
        if not ce:
            raise ValueError("PSAToolbox not initialized. Call initialize_cloudpss_toolbox first.")

        #comment: 保存项目到CloudPSS平台，并设置项目名称
        ce.saveProject(self.project_key + self._sa_project_suffix, name=ce.project.name + self._sa_project_suffix)
        print(f"Project '{ce.project.name + self._sa_project_suffix}' saved successfully.")

    def run_cloudpss_simulation(self):
        """
        在CloudPSS平台运行仿真，并处理仿真结果。

        功能:
            配置Exchange元件的输入通道以进行数据输出，保存项目，
            启动仿真，获取仿真结果（特别是Exchange元件对应的输入数据），
            并将数据处理后保存为CSV文件。

        参数:
            无

        返回:
            None
        """
        ce = self.psatoolbox
        if not ce:
            raise ValueError("PSAToolbox not initialized. Call initialize_cloudpss_toolbox first.")
        if not self.exchange_files:
            raise ValueError("No exchange files provided. Call import_exchange_components first.")

        print('Starting CloudPSS simulation...')

        # comment: 打开并读取第一个Exchange文件，加载其JSON内容
        with open(self.exchange_files[0], "r", encoding='utf-8') as f:
            exchange_json = json.load(f)

        # comment: 设置是否删除边 (运行时通常删除)
        ce.config['deleteEdges'] = True

        # comment: 初始化计数器
        count = 0
        # comment: 遍历项目中所有RID为exRID的组件
        # 获取所有Exchange模型实例
        exchange_components = ce.project.getComponentsByRid(self._exchange_models_rid)
        if not exchange_components:
            print(f"No components found with RID: {self._exchange_models_rid}. Skipping channel setup.")

        for i, j in exchange_components.items():
            # comment: 为Exchange组件的输入引脚添加通道
            id1, temp1 = ce.addChannel(j.pins['Input'], int(j.args['DimIn']), channelName=i)
            # comment: 构造通道信息字典，用于输出配置
            channelinfo = {'0': f'场路耦合结果导出{count}',  # comment: 名称
                           '1': 1000,  # comment: 采样点个数阈值
                           '2': 1000,  # comment: 保存周期
                           '3': 1,  # comment: 倍率
                           '4': [id1],  # comment: 通道ID列表
                           'ɵid': random.randint(10000000, 99999999)}  # comment: 随机ID

            # comment: 将通道信息添加到输出配置中
            ce.addOutputs(self._job_name, channelinfo)
            # comment: 计数器加1
            count += 1
        # comment: 保存项目到CloudPSS平台，并设置项目名称
        ce.saveProject(self.project_key + self._sa_project_suffix, name=ce.project.name + self._sa_project_suffix)

        print(f"Running simulation job: {self._job_name}, config: {self._config_name}")
        # comment: 运行仿真项目
        ce.runProject(jobName=self._job_name, configName=self._config_name, plotRun=0, sleepTime=0.1)

        # comment: 获取仿真结果中的绘图数量
        plot_number = len(ce.runner.result.getPlots())
        # comment: 初始化循环变量
        k = 0
        # comment: 再次遍历项目中所有RID为exRID的组件
        for i, j in exchange_components.items():
            # comment: 获取当前Exchange组件对应的绘图数据
            plot_input = ce.runner.result.getPlot(plot_number - count + k)
            # comment: 初始化数据列表
            data_list = []
            # comment: 初始化列名列表
            cols = []
            # comment: 初始化内部计数器
            cc = 0
            # comment: 遍历Exchange组件的输入引脚名称信息
            for q in j.args['PinInName']:
                # comment: 遍历引脚的维度
                for d in range(int(q['3'])):
                    # comment: 获取绘图数据中的轨迹
                    trace = plot_input['data']['traces'][cc]
                    # comment: 将时间数据添加到datalist
                    data_list.append(trace['x'])
                    # comment: 将列名'Time'添加到cols
                    cols.append('Time')
                    # comment: 将Y轴数据（仿真结果）添加到datalist
                    data_list.append(trace['y'])
                    # cols.append(q['0'] + '.' + q['1'] + '-' + str(d))
                    # comment: 将引脚名称添加到cols
                    cols.append(q['0']) # Simplified column name
                    # comment: 内部计数器加1
                    cc += 1
            # comment: 使用datalist和cols创建DataFrame
            df = pd.DataFrame(data_list, index=cols)
            # comment: 转置DataFrame
            df = df.transpose()
            # df.to_csv(fileDir + j.label +'.csv')
            # comment: 将DataFrame保存为CSV文件
            # 确保目录存在
            output_dir = os.path.dirname(exchange_json['Path'])
            if not os.path.exists(output_dir) and output_dir:
                os.makedirs(output_dir)
            df.to_csv(os.path.join(output_dir, 'CurrentOut.csv')) # 使用第一个fileDir作为输出路径
            print(f"Simulation results saved to {os.path.join(output_dir, 'CurrentOut.csv')}")
            # comment: 外部循环变量加1
            k += 1

    def run_finite_element_calculation(self):
        """
        调用外部Python脚本执行有限元计算。

        功能:
            通过subprocess模块执行一个独立的Python脚本，该脚本负责有限元分析。
            脚本的路径、输入数据路径和参数都由类初始化时设置的属性决定。

        参数:
            无

        返回:
            int: 子进程的返回码。0通常表示成功。
            str: 子进程的完整输出。
        """
        print('Starting finite element calculation...')

        # comment: 使用subprocess.Popen启动外部程序（Python解释器执行CloudPassMain0129.py），并传递ibe文件路径和参数
        # 确保 fe_main_script 是绝对路径
        fe_main_script_abs = os.path.abspath(self._fe_main_script)
        fe_input_data_path_abs = os.path.abspath(self._fe_input_data_path)

        cmd = [
            self._fe_python_path,
            fe_main_script_abs,
            fe_input_data_path_abs,
            self._fe_param
        ]
        
        print(f"Executing FE command: {' '.join(cmd)}")

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        full_output = []
        # comment: 读取子进程的输出，逐行处理
        curline = process.stdout.readline()
        # comment: 循环直到子进程输出结束
        while(curline != b''):
            try:
                decoded_line = curline.decode("gb2312", errors='replace').strip()
                print(decoded_line)
                full_output.append(decoded_line)
            except Exception as e:
                print(f"Decoding error: {e}, Raw: {curline}")
                full_output.append(str(curline).strip())
            # comment: 读取下一行输出
            curline = process.stdout.readline()

        # comment: 等待子进程结束
        process.wait()
        # comment: 打印子进程的返回码
        print(f"Finite element calculation finished with return code: {process.returncode}")
        return process.returncode, "\n".join(full_output)


def main():
    """
    主函数，用于orchestrate CloudPSS场路耦合计算的整个流程。
    """
    print('Starting the main workflow.')

    # 替换敏感信息为占位符
    token_placeholder = 'CLOOUDPSS_TOKEN_PLACEHOLDER'
    api_url_placeholder = 'CLOUDPSS_API_URL_PLACEHOLDER'
    username_placeholder = 'CLOUDPSS_USERNAME_PLACEHOLDER'
    project_key_placeholder = 'CLOUDPSS_PROJECT_KEY_PLACEHOLDER'
    fe_python_path_placeholder = 'FE_PYTHON_EXE_PATH_PLACEHOLDER' # 例如 D:/Simdroid/bin/python.exe
    fe_main_script_placeholder = './CloudPassMain0129.py' # 有限元计算主脚本路径
    fe_input_data_path_placeholder = './data/New电缆迭代步模型_调控闭环.ibe' # 有限元计算输入数据路径
    fe_param_placeholder = '1' # 有限元计算参数

    #comment: 定义Exchange文件的路径列表
    exchange_files_list = ['./Exchange_cable.json']

    # comment: 第一步：创建 Field_CloudPSSCalculation 类的实例
    # 实例化类，传入所有必要参数，敏感信息使用占位符
    cloudpss_calculator = Field_CloudPSSCalculation(
        token=token_placeholder,
        api_url=api_url_placeholder,
        username=username_placeholder,
        project_key=project_key_placeholder,
        exchange_models_rid='model/admin/model_exchange', # 示例RID，如果需要也替换为占位符
        job_name='电磁暂态仿真方案 1', # 仿真作业名称
        config_name='参数方案 1', # 仿真配置名称
        fe_python_path=fe_python_path_placeholder,
        fe_main_script=fe_main_script_placeholder,
        fe_input_data_path=fe_input_data_path_placeholder,
        fe_param=fe_param_placeholder
    )
    print("Step 1: Initialized Field_CloudPSSCalculation instance.")

    # comment: 第二步：初始化 CloudPSS Toolbox
    # 配置与CloudPSS平台交互所需的工具箱
    cloudpss_calculator.initialize_cloudpss_toolbox()
    print("Step 2: CloudPSS Toolbox initialized.")

    # comment: 第三步：导入 Exchange 元件到 CloudPSS 模型
    # 将预定义的Exchange模型文件导入到CloudPSS的仿真项目中，并生成对应的分线器、集线器和连接关系
    ex_model_ids = cloudpss_calculator.import_exchange_components(exchange_files_list)
    print(f"Step 3: Exchange components imported. Model IDs: {ex_model_ids}")

    # comment: 第四步：保存 CloudPSS 项目
    # 将当前配置好的项目保存到CloudPSS平台，以便后续仿真
    cloudpss_calculator.save_cloudpss_project()
    print("Step 4: CloudPSS project saved.")

    # comment: 第五步：运行 CloudPSS 仿真
    # 启动在CloudPSS平台上配置好的仿真作业，并处理仿真结果，将特定输出保存到本地CSV文件
    cloudpss_calculator.run_cloudpss_simulation()
    print("Step 5: CloudPSS simulation completed and results processed.")

    # comment: 第六步：运行有限元计算
    # 调用外部程序执行有限元分析，该程序将使用仿真结果作为输入
    return_code, output = cloudpss_calculator.run_finite_element_calculation()
    print(f"Step 6: Finite element calculation completed with return code {return_code}.")
    # print(f"FE Calculation Output:\n{output}") # 可以选择打印完整输出

    print("Main workflow completed successfully.")


# comment: 判断当前脚本是否作为主程序运行
if __name__ == "__main__":
    main()