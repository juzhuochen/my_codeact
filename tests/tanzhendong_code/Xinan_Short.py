# %%
import os
import pandas as pd
import time
import sys, os
import cloudpss
import math
import time
import numpy as np
import pandas as pd
from jobApi1 import fetch, fetchAllJob, abort
from CaseEditToolbox import CaseEditToolbox
from CaseEditToolbox import is_number
from PSAToolbox import PSAToolbox
import json
import random
import re

"""
敏感信息占位符定义：
    TOKEN_PLACEHOLDER: 访问令牌占位符
    API_URL_PLACEHOLDER: CloudPSS API URL 占位符
    PROJECT_KEY_PLACEHOLDER: 项目密钥占位符
    USERNAME_PLACEHOLDER: 用户名占位符
    QS_FILES_PATH_PLACEHOLDER: QS 文件路径占位符
    LINE_NAME_PLACEHOLDER: 默认线路名称占位符
"""
TOKEN_PLACEHOLDER = 'YOUR_ACCESS_TOKEN_HERE'
API_URL_PLACEHOLDER = 'YOUR_CLOUD_PSS_API_URL_HERE'
PROJECT_KEY_PLACEHOLDER = 'YOUR_PROJECT_KEY_HERE'
USERNAME_PLACEHOLDER = 'YOUR_USERNAME_HERE'
QS_FILES_PATH_PLACEHOLDER = './QSFiles_Placeholder/'
LINE_NAME_PLACEHOLDER = 'DEFAULT_LINE_NAME_HERE'

class Xinan_Short:
    """
    Xinan_Short 类用于处理电力系统相关的 CloudPSS 仿真和潮流计算任务。
    它封装了电磁暂态仿真和潮流计算的各个步骤，提供了模块化的接口。

    属性:
        job: cloudpss.currentJob() 对象，用于与 CloudPSS 作业系统交互，例如记录日志、显示进度和输出结果。
        token (str): 用于身份验证的访问令牌。
        api_url (str): CloudPSS API 的基础 URL。
        username (str): CloudPSS 用户名。
        project_key (str): 当前操作的项目密钥，用于标识 CloudPSS 中的特定项目。
        qspath (str): QS 文件的存储路径，用于潮流计算的数据导入。
        component_library (dict): 从 'saSource.json' 加载的组件库信息。
        psa_toolbox (PSAToolbox): PSAToolbox 实例，用于电力系统分析操作。
    """
    def __init__(self, job, token, api_url, username, project_key, qspath):
        """
        初始化 Xinan_Short 类的一个新实例。

        参数:
            job: cloudpss.currentJob() 对象。
            token (str): 访问令牌。
            api_url (str): CloudPSS API URL。
            username (str): 用户名。
            project_key (str): 项目密钥。
            qspath (str): QS 文件路径。
        """
        self.job = job
        self.token = token
        self.api_url = api_url
        self.username = username
        # 从作业参数中提取项目密钥，并替换为占位符
        self.project_key = re.match('.*?/.*?/(.*)', project_key).group(1) if project_key else PROJECT_KEY_PLACEHOLDER
        self.qspath = qspath
        self.component_library = self._load_component_library()
        self.psa_toolbox = self._initialize_psa_toolbox()

    def _load_component_library(self):
        """
        加载并返回 'saSource.json' 文件中的组件库信息。

        返回:
            dict: 加载的组件库字典。
        """
        with open('saSource.json', "r", encoding='utf-8') as f:
            return json.load(f)

    def _initialize_psa_toolbox(self):
        """
        初始化 PSAToolbox 类的实例，并进行配置。

        返回:
            PSAToolbox: 配置好的 PSAToolbox 实例。
        """
        ce = PSAToolbox()
        # 配置 PSAToolbox，设置令牌、API URL、用户名、项目密钥和组件库名称
        ce.setConfig(self.token, self.api_url, self.username, self.project_key, comLibName='saSource.json')
        # 配置 PSAToolbox 的 iGraph 生成选项
        ce.config['iGraph'] = False  #  生成iGraph信息，已有iGraph信息时注释本块
        # 配置是否删除边
        ce.config['deleteEdges'] = False
        return ce
    
    def prepare_emt_simulation(self, fault_type_str, line_name, side, ts, tc):
        """
        准备电磁暂态 (EMT) 仿真，包括初始化、创建画布、设置故障和添加测量通道。

        参数:
            fault_type_str (str): 故障类型字符串，例如 "ABC", "A", "B", "AB" 等。
            line_name (str): 发生故障的线路名称。
            side (str): 故障发生在线路的哪一侧 ("0" 或 "1")。
            ts (str): 故障开始时间。
            tc (str): 故障清除时间。

        返回:
            dict: 配置好的 EMT 仿真作业字典。
        """
        self.job.log('Start EMT Simulation Preparation')
        self.psa_toolbox.setInitialConditions() # 进行初始化
        self.psa_toolbox.createSACanvas()
        self.job.log('Initialized and Canvas Created')

        # 定义故障类型列表
        ft_list = ["None","A","B","AB","C","AC","BC","ABC"]
        # 获取作业参数 'FT1' 对应的故障类型索引
        fault_type_index = ft_list.index(fault_type_str)

        # 构建传输线路由器和母线的标签到ID的字典
        trans_dict = {j.label:i for i,j in self.psa_toolbox.project.getComponentsByRid('model/CloudPSS/TranssmissionLineRouter').items()}
        # 注意：原代码中 BusDict 与 TransDict 相同，此处假定 BusDict 实际应对应 Bus 类型组件，如果实际应用中无此类型，则需要调整。
        # 这里为保持与原代码一致性，仍然使用TransDict作为BusDict的来源，但建议根据实际模型结构进行调整。
        bus_dict = {j.label:i for i,j in self.psa_toolbox.project.getComponentsByRid('model/CloudPSS/TranssmissionLineRouter').items()}
        
        # 获取作业参数 'LineName1' 对应的传输线ID
        target_line_id = trans_dict.get(line_name, None)
        if target_line_id is None:
            self.job.log(f"Error: Line '{line_name}' not found in project components.")
            raise ValueError(f"Line '{line_name}' not found.")

        # 初始化一个集合用于存储相关线路
        relevant_lines = set()
        # 获取选中线路的引脚（pins）
        picked_pins = set([self.psa_toolbox.project.getComponentByKey(target_line_id).pins['0'],
                           self.psa_toolbox.project.getComponentByKey(target_line_id).pins['1']])
        self.job.print(list(picked_pins))

        # 遍历所有传输线，如果其任一引脚与选中线路的引脚关联，则加入到 relevant_lines 集合
        for i in trans_dict.values():
            comp = self.psa_toolbox.project.getComponentByKey(i)
            if 'pins' in comp and '0' in comp.pins and '1' in comp.pins: # 确保有pins属性
                if comp.pins['0'] in picked_pins or comp.pins['1'] in picked_pins:
                    relevant_lines.add(i)
            else:
                self.job.log(f"Warning: Component {i} does not have expected 'pins' structure and will be skipped for related line detection.")


        self.job.print(list(relevant_lines))

        # 设置 N-1 接地故障
        self.psa_toolbox.setN_1_GroundFault(target_line_id, side, ts, tc, fault_type_index, OtherFaultParas=None, OtherBreakerParas=None)
        self.job.log('Fault Set')

        # 定义用于短路点附近线路三相瞬时电流的通道配置
        channels_abc = {'0': '短路点附近线路三相瞬时电流(kA)',
                    '1': 1000, '2': 1000, '3': 1, '4': [], 'ɵid':random.randint(10000000,99999999)}
        # 定义用于短路点附近线路电流有效值的通道配置
        channels_rms = {'0': '短路点附近线路电流有效值(kA)',
                    '1': 1000, '2': 1000, '3': 1, '4': [], 'ɵid':random.randint(10000000,99999999)}
        
        # 遍历相关线路，添加对应的电流测量通道
        for lid in relevant_lines:
            # 获取当前线路组件
            comp = self.psa_toolbox.project.getComponentByKey(lid)
            
            # 添加 Is 的三相瞬时电流通道
            # 如果线路的 Is 参数为空，则生成新的通道标签并赋值
            if comp.args.get('Is', '') == '':
                new_label_is = "#" + comp.label + '.Is'
                comp.args['Is'] = new_label_is
            else:
                new_label_is = comp.args['Is']
            is_abc, _ = self.psa_toolbox.addChannel(new_label_is, 3, channelName=new_label_is)
            channels_abc['4'].append(is_abc)

            # 添加 Ir 的三相瞬时电流通道
            if comp.args.get('Ir', '') == '':
                new_label_ir = "#" + comp.label + '.Ir'
                comp.args['Ir'] = new_label_ir
            else:
                new_label_ir = comp.args['Ir']
            ir_abc, _ = self.psa_toolbox.addChannel(new_label_ir, 3, channelName=new_label_ir)
            channels_abc['4'].append(ir_abc)

            # 添加 Isrms 的瞬时电流有效值通道
            if comp.args.get('Isrms', '') == '':
                new_label_isrms = "#" + comp.label + '.Isrms'
                comp.args['Isrms'] = new_label_isrms
            else:
                new_label_isrms = comp.args['Isrms']
            is_rms, _ = self.psa_toolbox.addChannel(new_label_isrms, 1, channelName=new_label_isrms)
            channels_rms['4'].append(is_rms)

            # 添加 Irrms 的瞬时电流有效值通道
            if comp.args.get('Irrms', '') == '':
                new_label_irrms = "#" + comp.label + '.Irrms'
                comp.args['Irrms'] = new_label_irrms
            else:
                new_label_irrms = comp.args['Irrms']
            ir_rms, _ = self.psa_toolbox.addChannel(new_label_irrms, 1, channelName=new_label_irrms)
            channels_rms['4'].append(ir_rms)

        # 将三相瞬时电流通道配置添加到输出
        self.psa_toolbox.addOutputs('电磁暂态仿真方案 2', channels_abc)
        # 将电流有效值通道配置添加到输出
        self.psa_toolbox.addOutputs('电磁暂态仿真方案 2', channels_rms)
        self.job.log('Channels Added')

        # 获取名为 '电磁暂态仿真方案 2' 的仿真作业配置
        job_emt = self.psa_toolbox.project.getModelJob('电磁暂态仿真方案 2')[0]
        # 保存项目
        self.psa_toolbox.saveProject(self.project_key + '_emt_prepared')
        
        return job_emt

    def run_emt_simulation(self, job_emt_config):
        """
        运行电磁暂态仿真并监控其进度和结果。

        参数:
            job_emt_config (dict): 配置好的 EMT 仿真作业字典。
        """
        self.job.log('Running EMT Simulation')
        time_start = time.time()
        self.psa_toolbox.runner = self.psa_toolbox.project.run(job=job_emt_config)
        
        # 获取仿真结束时间
        end_time = float(job_emt_config['args']['end_time'])

        # 循环等待仿真完成
        while not self.psa_toolbox.runner.status():
            # 续期作业，防止超时
            self.job.feedDog()

            # 获取当前时间
            time_end = time.time()
            # 如果有绘图通道数据
            if self.psa_toolbox.runner.result.getPlotChannelNames(0):
                # 获取第一个绘图通道的键
                ckeytemp = self.psa_toolbox.runner.result.getPlotChannelNames(0)[0]
                # 获取仿真时间
                stime = self.psa_toolbox.runner.result.getPlotChannelData(0,ckeytemp)['x'][-1]
                # 更新作业进度
                self.job.progress(stime / end_time)
            
            # 遍历仿真结果中的消息并打印
            for message in self.psa_toolbox.runner.result:
                if message['type'] != 'plot':
                    continue
                self.job.print(message)
            # 短暂暂停
            time.sleep(0.1)

        # 仿真完成后，再次遍历仿真结果中的消息并打印
        for message in self.psa_toolbox.runner.result:
            self.job.print(message)
        
        # 更新作业进度为 100%
        self.job.progress(1)
        self.job.log('EMT Simulation Finished')

    def perform_power_flow_calculation(self):
        """
        执行潮流计算，并处理输出结果。
        """
        self.job.log('Starting Power Flow Calculation')
        # 从 ImportQSData_xinan_1 模块导入 PFCalculate 函数
        from ImportQSData_xinan_1 import PFCalculate

        # 调用 PFCalculate 函数进行潮流计算
        PFCalculate(self.job, self.project_key, qspath=self.qspath)
        self.job.log("Power flow calculation initiated.", key="test1")

        # 打开并读取 'Vcompare.txt' 文件
        try:
            with open('Vcompare.txt','r',encoding='gb2312') as f:
                # 读取文件的第一行作为表头
                line = f.readline()
                keys = []
                info_dict = {}
                # 解析第一行作为信息字典的键
                for data1 in line.strip('\n').split('\t'):
                    info_dict[data1.strip(' ')] = []
                    keys.append(data1.strip(' '))
                
                # 逐行读取文件内容填充信息字典
                for line in f.readlines():     
                    line_cells = line.strip('\n').split('\t')
                    # 清除每个单元格的空白
                    line_cells = [cell.strip(' ') for cell in line_cells]
                    
                    for d in range(len(keys)):
                        if d < len(line_cells): # 检查索引是否越界
                            data1 = line_cells[d]
                            # 如果数据是数字，则转换为浮点数
                            if is_number(data1):
                                data1 = float(data1)
                            info_dict[keys[d]].append(data1)
                        else:
                            # 处理数据不完整的情况，例如填充None或默认值
                            info_dict[keys[d]].append(None) 

                # 定义表格列
                c1 = {'name':'<b>母线名</b>', 'type':'html', 'data': info_dict.get('Name', [])}
                c2 = {'name': "<b>QS文件电压V [p.u.]</b>", 'type': 'number', 'data': info_dict.get('V0', [])} 
                c3 = {'name': "<b>QS文件相角Ang [Deg]</b>", 'type': 'number', 'data': info_dict.get('Ang0', [])}
                c4 = {'name': "<b>潮流收敛电压V [p.u.]</b>", 'type': 'number', 'data': info_dict.get('V', [])}
                c5 = {'name': "<b>潮流收敛相角Ang [Deg]</b>", 'type': 'number', 'data': info_dict.get('Ang', [])}
                c6 = {'name': "<b>QS有功不平衡量 [MW]</b>", 'type': 'number', 'data': info_dict.get('DP', [])}
                c7 = {'name': "<b>QS无功不平衡量 [MVar]</b>", 'type': 'number', 'data': info_dict.get('DQ', [])} 
                
                # 将数据作为表格输出到 CloudPSS 界面
                self.job.table([c1,c2,c4,c3,c5,c6,c7],title='潮流结果对比表',key='table-3')
        except FileNotFoundError:
            self.job.log("Error: Vcompare.txt not found. Power flow comparison data is unavailable.")
        except Exception as e:
            self.job.log(f"An error occurred during power flow result processing: {e}")

        self.job.progress(1)
        self.job.log('Power Flow Calculation Finished')

    def import_qs_data(self):
        """
        导入 QS 数据到 CloudPSS 项目。
        """
        self.job.log('Starting QS Data Import')
        # 从 ImportQSData_xinan 模块导入 ImportQSData_xinan 函数
        from ImportQSData_xinan import ImportQSData_xinan
        # 调用 ImportQSData_xinan 函数进行数据导入
        ImportQSData_xinan(self.job, projectKey=self.project_key, qspath=self.qspath)
        self.job.progress(1)
        self.job.log('QS Data Import Finished')


def main():
    """
    脚本的主入口函数，负责协调调用 Xinan_Short 类的方法来完成业务逻辑。
    """
    # 获取当前的 CloudPSS 作业实例
    job = cloudpss.currentJob()
    
    # 初始化敏感信息，使用占位符
    token_val = TOKEN_PLACEHOLDER
    api_url_val = API_URL_PLACEHOLDER
    username_val = USERNAME_PLACEHOLDER
    # 从作业参数中获取 projectKey，如果不存在则使用占位符
    project_key_val = job.args.get('projectKey', PROJECT_KEY_PLACEHOLDER)
    qspath_val = QS_FILES_PATH_PLACEHOLDER

    # 创建 Xinan_Short 类的实例
    xinan_processor = Xinan_Short(job, token_val, api_url_val, username_val, project_key_val, qspath_val)

    # 检查作业参数 'Type' 的值，执行不同的业务逻辑
    # 如果脚本作为主程序运行
    if __name__ == '__main__':
        if str(job.args.get('Type','1')) == "0":
            # 第一步：获取电磁暂态仿真参数
            # 从作业参数 'FT1' 中获取故障类型，默认为 "ABC"
            fault_type = job.args.get('FT1', 'ABC')
            # 从作业参数 'LineName1' 中获取线路名称，默认为 'AC407567'
            line_name = job.args.get('LineName1', LINE_NAME_PLACEHOLDER)
            # 从作业参数 'Side1' 中获取故障侧，默认为 '0'
            side = job.args.get('Side1', '0')
            # 从作业参数 'Ts1' 中获取故障开始时间，默认为 '3'
            ts = job.args.get('Ts1', '3')
            # 从作业参数 'Tc1' 中获取故障清除时间，默认为 '3.06'
            tc = job.args.get('Tc1', '3.06')          

            # 第二步：准备电磁暂态仿真
            emt_job_config = xinan_processor.prepare_emt_simulation(fault_type, line_name, side, ts, tc)

            # 第三步：运行电磁暂态仿真
            xinan_processor.run_emt_simulation(emt_job_config)

        elif str(job.args.get('Type','1')) == "1":
            # 第一步：执行潮流计算
            xinan_processor.perform_power_flow_calculation()

        elif str(job.args.get('Type','1')) == "99":
            # 第一步：导入 QS 数据
            xinan_processor.import_qs_data()
        
        else:
            job.log(f"Unknown 'Type' parameter: {job.args.get('Type','1')}. No action performed.")

# comment: 如果脚本作为主程序运行
if __name__ == '__main__':
    main()