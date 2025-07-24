
import io
import os
import sys
from typing import Dict, List, Optional, TypedDict,Union,Set,Tuple
import cloudpss
from contextlib import asynccontextmanager
import time

from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel
from my_codeact.test_data.CaseEditToolBox import CaseEditToolbox



import math

from IPython.display import HTML
from html import unescape

import random
import copy
from cloudpss.model.implements.component import Component
from cloudpss.runner.result import (Result,PowerFlowResult,EMTResult)
from cloudpss.model.revision import ModelRevision
from cloudpss.model.model import Model


#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

class PSAToolbox(CaseEditToolbox):
    def __init__(self):
        super(PSAToolbox,self).__init__()
        
        self.cFid = 'canvas_AutoSA_Fault'
        self.cPSAid = 'canvas_AutoSA_PSA'
        self.cOid = 'canvas_AutoSA_ExtraOutput'
        self.compNames = {'_newFaultResistor_3p':'SA_接地故障',  '_newBreaker_3p':'SA_三相断路器', 'GND':'接地点(用于稳定分析)','_newStepGen':'阶跃信号'}
         
    def createSACanvas(self):
        """
        Descriptions
        ----------
            创建或初始化用于安全分析相关的画布，包括故障设置画布、安控策略画布和额外输出画布，并在故障画布上添加接地点组件。

        Parameters
        ----------
            无

        Output
        ----------
            无
        """
        canvas0 = [i['key'] for i in self.project.revision.implements.diagram.canvas]
        if(self.cFid not in canvas0):
            self.createCanvas(self.cFid,'故障相关设置')
        else:
            self.initCanvasPos(self.cFid)
        if(self.cOid not in canvas0):
            self.createCanvas(self.cOid,'暂态分析所需输出通道')
        else:
            self.initCanvasPos(self.cOid)
        if(self.cPSAid not in canvas0):
            self.createCanvas(self.cPSAid,'安控策略新增元件')
        else:
            self.initCanvasPos(self.cPSAid)

        nameTemp = self.compNames['GND']
        self.addCompInCanvas(self.compLib['GND'], key = 'AutoSA_GND',canvas = self.cFid,                     args = {'Name':nameTemp}, pins = {'0':'GND'},label = nameTemp)
        self.newLinePos(self.cFid)
    
    def setGroundFault(self, pinName:str, fault_start_time:Optional[float] = 4, fault_end_time:Optional[float] = 4.09,  fault_type_index:Optional[int] = 7, OtherParas:Optional[Dict] = None, Inductor:Optional[float] = None):
        """
        Descriptions
        ----------
            在指定引脚设置接地故障，并可选择添加故障电阻和电感。

        Parameters
        ----------
            pinName (str): 发生故障的引脚名称。
            fault_start_time (float): 故障开始时间。
            fault_end_time (float): 故障结束时间。
            fault_type_index (int): 故障类型索引，默认为7。
            OtherParas (dict, optional): 其他故障参数字典。默认为 `None`，字典可选的key为Init、chg、fct、I、V，分别表示初始电阻、故障期间电阻、故障清除时刻、三相电阻故障电流、三相电阻故障电压。
            Inductor (float, optional): 故障接地电感值。默认为 `None`。

        Output
        ----------
            tuple: 包含接地故障电阻组件的 ID (`str`) 和标签 (`str`)。

        Examples
        ----------
        >>> # 在 'PinA' 上设置一个从 0.1s 到 0.5s 的接地故障
        >>> setGroundFault(pinName='PinA',fault_start_time=0.1,fault_end_time=0.5)
        """       
        nameTemp = self.compNames['_newFaultResistor_3p']
        argsTemp = {'Name':nameTemp, 'fs':str(fault_start_time), 'fe':str(fault_end_time),'ft':str(fault_type_index)}
        if(OtherParas != None):
            argsTemp.update(OtherParas)
        if(Inductor == None):
            id1, label = self.addCompInCanvas(self.compLib['_newFaultResistor_3p'], key = 'SA_Ground_Fault',canvas = self.cFid, args = argsTemp, pins = {'0':pinName,'1':'GND'},label = nameTemp)
        else:
            id1, label = self.addCompInCanvas(self.compLib['_newFaultResistor_3p'], key = 'SA_Ground_Fault',canvas = self.cFid, args = argsTemp, pins = {'0':pinName,'1':pinName+'IndTemp'},label = nameTemp)
            nameTempInd = self.compNames['newInductorRouter']
            argsTempInd = {
                "Dim": "3",
                "I": "",
                "L": str(Inductor),
                "NIM": "1",
                "Name": nameTempInd,
                "V": ""
            }
            id2, label2 = self.addCompInCanvas(self.compLib['newInductorRouter'], key = 'SA_Ground_Ind',canvas = self.cFid, args = argsTempInd, pins = {'0':pinName+'IndTemp','1':'GND'},label = nameTempInd)

        return id1, label
        
    def setBreaker_3p(self, busPinName1:str, busPinName2:str, ctrlSigName:Optional[str] = None, OtherParas:Optional[Dict] = None):
        """
        Descriptions
        ----------
            在两个母线之间设置三相断路器。

        Parameters
        ----------
            busPinName1 (str): 第一个母线的名称。
            busPinName2 (str): 第二个母线的名称。
            ctrlSigName (str, optional): 控制断路器状态的信号名称。默认为 `None`。
            OtherParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            tuple: 包含断路器组件的 ID (`str`) 和标签 (`str`)。
        """
        nameTemp = self.compNames['_newBreaker_3p']
        argsTemp = {'Name':nameTemp, 'ctrlsignal':ctrlSigName, 'Init': '1', 'Status': ''}
        if(OtherParas != None):
            argsTemp.update(OtherParas)
        id1, label = self.addCompInCanvas(self.compLib['_newBreaker_3p'], key = 'SA_Breaker_3p',canvas = self.cFid, args = argsTemp, pins = {'0':busPinName1,'1': busPinName2},label = nameTemp)
         
        # return 1
        return id1, label

    def setN_1(self, transKey:str, cut_time:Union[List,float], OtherBreakerParas:Optional[Dict] = None):
        """
        Descriptions
        ----------
            设置N-1故障，即切除一条传输元件（如线路）通过添加受控断路器。

        Parameters
        ----------
            transKey (str): 传输元件（如线路）的 Key。
            cut_time (float or list): 切除时间，可以是单个时间点或包含两个时间点的列表（用于两端切除）。
            OtherBreakerParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            无
        """
        transComp = self.project.getComponentByKey(transKey)
        transPin = transComp.pins.copy()
        transName = transComp.args['Name']
        transComp.pins['0'] = 'BreakerPin_'+ transName + '_0';
        transComp.pins['1'] = 'BreakerPin_'+ transName + '_1';
        SigName = '@Sig_Breaker_'+transName;
        
        if(not isinstance(cut_time,list)):
            id1, label1 = self.setBreaker_3p(transComp.pins['0'], transPin['0'], ctrlSigName = SigName, OtherParas = OtherBreakerParas)
            id2, label2 = self.setBreaker_3p(transComp.pins['1'], transPin['1'], ctrlSigName = SigName, OtherParas = OtherBreakerParas)
            nameTemp = self.compNames['_newStepGen']
            argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time)}
            ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig',canvas = self.cFid, args = argsTemp, pins = {'0':SigName},label = nameTemp)
        else:
            id1, label1 = self.setBreaker_3p(transComp.pins['0'], transPin['0'], ctrlSigName = SigName + '1', OtherParas = OtherBreakerParas)
            id2, label2 = self.setBreaker_3p(transComp.pins['1'], transPin['1'], ctrlSigName = SigName + '2', OtherParas = OtherBreakerParas)
            nameTemp = self.compNames['_newStepGen']
            argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time[0])}
            ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig',canvas = self.cFid, args = argsTemp, pins = {'0':SigName + '1'},label = nameTemp)

            argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time[1])}
            ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig',canvas = self.cFid, args = argsTemp, pins = {'0':SigName + '2'},label = nameTemp)

        self.newLinePos(self.cFid)

    # wangyongkang
    def setN_k(self, transKeys:List, cut_time:float, OtherBreakerParas:Optional[Dict] = None):
        """
        Descriptions
        ----------
            设置N-k故障，即同时切除 k 条传输元件（如线路）通过添加受控断路器。

        Parameters
        ----------
            transKeys (list): 传输元件（如线路）的 Key 列表。
            cut_time (float): 切除时间。
            OtherBreakerParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            dict: 存储 N-k 切除线路信息，键为 `transKey`，值为共同的控制信号名称。
        """
        if(not isinstance(transKeys,list)):
            transKeys = eval(transKeys)
        SigName = '@Sig_Breaker_N_k'+ transKeys[0];
        N_k_CutLine = {}
        for i in range(len(transKeys)):
            transComp = self.project.getComponentByKey(transKeys[i])
            transPin = transComp.pins.copy()
            transName = transComp.args['Name']
            transComp.pins['0'] = 'BreakerPin_'+ transName + '_0';
            transComp.pins['1'] = 'BreakerPin_'+ transName + '_1';
            id1, label1 = self.setBreaker_3p(transComp.pins['0'], transPin['0'], ctrlSigName = SigName, OtherParas = OtherBreakerParas)
            id2, label2 = self.setBreaker_3p(transComp.pins['1'], transPin['1'], ctrlSigName = SigName, OtherParas = OtherBreakerParas)
            N_k_CutLine.update({transKeys[i] : SigName})
            
        nameTemp = self.compNames['_newStepGen']
        argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time)}
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig_N_k',canvas = self.cFid, args = argsTemp, pins = {'0':SigName},label = nameTemp)
        
        return N_k_CutLine

    def setCutFault(self, compKey:str, cut_time:float, pin:Optional[str] ='0',OtherBreakerParas:Optional[Dict] = None):
        """
        Descriptions
        ----------
            设置切除故障，即切除任意指定组件的某个引脚，通过添加受控断路器。

        Parameters
        ----------
            compKey (str): 组件的 Key。
            cut_time (float): 切除时间。
            pin (str, optional): 要切除的组件引脚名称。默认为 `'0'`。
            OtherBreakerParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            无
        Examples
        ----------
        >>> # 在4.06秒时切除元件"comp1"
        >>> setCutFault(compKey='comp1',cut_time=4.06)
        """
        compComp = self.project.getComponentByKey(compKey)
        compPin = compComp.pins.copy()
        if('Name' in compComp.args.keys()):
            compName = compComp.args['Name']
        else:
            compName = compComp.label
        compComp.pins[pin] = 'BreakerPin_'+ compName + '_0';
        SigName = '@Sig_Cutoff_'+compName;
        id1, label1 = self.setBreaker_3p(compComp.pins[pin], compPin[pin], ctrlSigName = SigName, OtherParas = OtherBreakerParas)
        
        nameTemp = self.compNames['_newStepGen']
        argsTemp = {'Name':nameTemp, 'V0':'1', 'V1':'0', 'Time':str(cut_time)}
        ids, labes = self.addCompInCanvas(self.compLib['_newStepGen'], key = 'Sig',canvas = self.cFid, args = argsTemp, pins = {'0':SigName},label = nameTemp)
        self.newLinePos(self.cFid)
        
    def setN_1_GroundFault(self, transKey:str,side:Optional[float] = 0, fault_start_time:Optional[float] = 4, cut_time:Optional[float] = 4.06, fault_type_index:Optional[int] = 7, OtherFaultParas:Optional[Dict] = None, OtherBreakerParas:Optional[Dict] = None):   
        """
        Descriptions
        ----------
            设置 N-1 接地故障，即在切除一条线路的同时，在该线路的某个位置发生接地故障。

        Parameters
        ----------
            transKey (str): 传输元件（如线路）的 Key。
            side (float, optional): 故障发生在线路上的位置（0表示一端，1表示另一端，0到1之间表示在线路中间）可选,默认为0。
            fault_start_time (float, optional): 故障开始时间，默认为4。
            cut_time (float, optional): 线路切除时间，默认为4.06。
            fault_type_index (int, optional): 故障类型索引，默认为7。
            OtherFaultParas (dict, optional): 其他故障参数字典。默认为 `None`，字典可选的key为Init、chg、fct、I、V，分别表示初始电阻、故障期间电阻、故障清除时刻、三相电阻故障电流、三相电阻故障电压。
            OtherBreakerParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            无
        """ 
        self.setN_1(transKey, cut_time, OtherBreakerParas)
        transComp = self.project.getComponentByKey(transKey)
        # side = float(side)
        if(side>1e-10 and side < 1-1e-10):
            
            compCopy = copy.deepcopy(transComp.toJSON())
            comp = Component(compCopy)
            comp.position['x']+=10
            comp.position['y']-=10
            comp.id = comp.id + '_addFault'

            # comp.pins['0'] = comp.id + '_TempPin'
            
            comp.pins['0'] = comp.pins['1']
            comp.pins['1'] = comp.id + '_TempPin'


            comp.args['Length'] = str(float(transComp.args['Length']['source'] if isinstance(transComp.args['Length'],dict) else transComp.args['Length']) * (1-side))
            comp.args['ModelType'] = '0'
            comp.args['Decoupled'] = '0'
            comp.label = comp.label + '_Opp'
            self.project.revision.implements.diagram.cells[comp.id]=comp

            transComp.args['Length'] = str(float(transComp.args['Length']['source'] if isinstance(transComp.args['Length'],dict) else transComp.args['Length']) * side)
            transComp.pins['1'] = comp.id + '_TempPin'
            transComp.args['ModelType'] = '0'
            transComp.args['Decoupled'] = '0'
            self.setGroundFault(transComp.pins['1'], fault_start_time, 99999,  fault_type_index, OtherParas = OtherFaultParas)
        elif(int(side)==0 or int(side)==1):
            self.setGroundFault(transComp.pins[str(int(side))], fault_start_time, 99999,  fault_type_index, OtherParas = OtherFaultParas)
    
    def setN_2_GroundFault(self, transKey1:str, transKey2:str,side:Optional[float] = 0, fault_start_time:Optional[float] = 4, cut_time:Optional[float] = 4.06, fault_type_index:Optional[int] = 7, OtherFaultParas:Optional[Dict] = None, OtherBreakerParas:Optional[Dict] = None):   
        """
        Descriptions
        ----------
            设置N-2接地故障，即同时切除两条线路，并在其中一条线路的某个位置发生接地故障。

        Parameters
        ----------
            transKey1 (str): 第一条传输元件的 Key。
            transKey2 (str): 第二条传输元件的 Key。
            side (float, optional): 故障发生在线路上的位置（0表示一端，1表示另一端，0到1之间表示在线路中间）可选,默认为0。即需要在元件的那个引脚上或元件上设置接地故障。
            fault_start_time (float, optional): 故障开始时间，默认为4。
            cut_time (float, optional): 线路切除时间，默认为4.06。
            fault_type_index (int, optional): 故障类型索引，默认为7。
            OtherFaultParas (dict, optional): 其他故障参数字典。默认为 `None`，字典可选的key为Init、chg、fct、I、V，分别表示初始电阻、故障期间电阻、故障清除时刻、三相电阻故障电流、三相电阻故障电压。
            OtherBreakerParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            无
        """  
        self.setN_1(transKey1, cut_time, OtherBreakerParas)
        self.setN_1(transKey2, cut_time, OtherBreakerParas)
        
        transComp = self.project.getComponentByKey(transKey1)
        if(side>1e-10 and side < 1-1e-10):
            
            compCopy = copy.deepcopy(transComp.toJSON())
            comp = Component(compCopy)
            comp.position['x']+=10
            comp.position['y']-=10
            comp.id = comp.id + '_addFault'
            # comp.pins['0'] = comp.id + '_TempPin'
            comp.pins['0'] = comp.pins['1']
            comp.pins['1'] = comp.id + '_TempPin'
            comp.args['Length'] = str(float(transComp.args['Length']['source'] if isinstance(transComp.args['Length'],dict) else transComp.args['Length']) * (1-side))
            comp.args['ModelType'] = '0'
            comp.args['Decoupled'] = '0'
            self.project.revision.implements.diagram.cells[comp.id]=comp

            transComp.args['Length'] = str(float(transComp.args['Length']['source'] if isinstance(transComp.args['Length'],dict) else transComp.args['Length']) * side)
            transComp.pins['1'] = comp.id + '_TempPin'
            transComp.args['ModelType'] = '0'
            transComp.args['Decoupled'] = '0'
            self.setGroundFault(transComp.pins['1'], fault_start_time, 99999,  fault_type_index, OtherParas = OtherFaultParas)
        elif(int(side)==0 or int(side)==1):
            self.setGroundFault(transComp.pins[str(int(side))], fault_start_time, 99999,  fault_type_index, OtherParas = OtherFaultParas)

        return "故障设置完成"
    def setN_k_GroundFault(self, transKeys:List,side:Optional[float] = 0, fault_start_time:Optional[float] = 4, cut_time:Optional[float] = 4.06,fault_type_index:Optional[int] = 7, OtherFaultParas:Optional[Dict] = None, OtherBreakerParas:Optional[Dict] = None):   
        """
        Descriptions
        ----------
            设置 N-k 接地故障，即同时切除 k 条线路，并在第一条被切除线路的某个位置发生接地故障。

        Parameters
        ----------
            transKeys (list): 传输元件（如线路）的 Key 列表。
            side (float, optional): 故障发生在线路上的位置（0表示一端，1表示另一端，0到1之间表示在线路中间）可选,默认为0。
            fault_start_time (float, optional): 故障开始时间，默认为4。
            cut_time (float, optional): 线路切除时间，默认为4.06。
            fault_type_index (int, optional): 故障类型索引，默认为7。0表示无故障，1-7分别表示A相、B相、C相、AB相、BC相、AC相、ABC相故障
            OtherFaultParas (dict, optional): 其他故障参数字典。默认为 `None`，字典可选的key为Init、chg、fct、I、V，分别表示初始电阻、故障期间电阻、故障清除时刻、三相电阻故障电流、三相电阻故障电压。
            OtherBreakerParas (dict, optional): 其他断路器参数字典。默认为 `None`。

        Output
        ----------
            无
        """  
        for i in range(len(transKeys)):
            self.setN_1(transKeys[i], cut_time, OtherBreakerParas)
        transComp = self.project.getComponentByKey(transKeys[0])
        if(side>1e-10 and side < 1-1e-10):
            
            compCopy = copy.deepcopy(transComp.toJSON())
            comp = Component(compCopy)
            comp.position['x']+=10
            comp.position['y']-=10
            comp.id = comp.id + '_addFault'
            # comp.pins['0'] = comp.id + '_TempPin'
            comp.pins['0'] = comp.pins['1']
            comp.pins['1'] = comp.id + '_TempPin'
            comp.args['Length'] = str(float(transComp.args['Length']['source'] if isinstance(transComp.args['Length'],dict) else transComp.args['Length']) * (1-side))
            comp.args['ModelType'] = '0'
            comp.args['Decoupled'] = '0'
            self.project.revision.implements.diagram.cells[comp.id]=comp

            transComp.args['Length'] = str(float(transComp.args['Length']['source'] if isinstance(transComp.args['Length'],dict) else transComp.args['Length']) * side)
            transComp.pins['1'] = comp.id + '_TempPin'
            transComp.args['ModelType'] = '0'
            transComp.args['Decoupled'] = '0'
            self.setGroundFault(transComp.pins['1'], fault_start_time, 99999,  fault_type_index, OtherParas = OtherFaultParas)
        elif(int(side)==0 or int(side)==1):
            self.setGroundFault(transComp.pins[str(int(side))], fault_start_time, 99999,  fault_type_index, OtherParas = OtherFaultParas)
            # print(str(side))
            # return transComp.pins[str(side)]
        return "故障设置完成"
    def addChannel(self, pinName:str, dim:Optional[int] = 1, channelName:Optional[str] = None):
        """
        Descriptions
        ----------
            为指定的引脚添加输出通道，用于在仿真过程中监测和输出该引脚上的信号。

        Parameters
        ----------
            pinName (str): 需要添加输出通道的引脚名称。
            dim (int): 输出通道的维度（例如，1代表单相，3代表三相），默认为1。
            channelName (str, optional): 输出通道的名称。如果为 `None`，则使用 `pinName`。默认为 `None`。

        Output
        ----------
            tuple: 包含通道组件的 ID (`str`) 和标签 (`str`)。
        """
        if pinName not in self.channelPinDict.keys():
            
            if(channelName == None):
                channelName = pinName;
            channelID = 'SA_outputChannel';

            argsTemp = {'Name':channelName, 'Dim':dim}
            id1, label = self.addCompInCanvas(self.compLib['_newChannel'], key = channelID, canvas = self.cOid, args = argsTemp, pins = {'0':pinName},label = channelName,addN_label=False, MaxX = 500)
            self.channelPinDict[pinName] = id1;
            
        else:
            channelComp = self.project.getComponentByKey(self.channelPinDict[pinName])
            if(channelName != None):
                channelComp.args['Name'] = channelName;
                channelComp.label = channelName;
            id1 = channelComp.id;
            label = channelComp.label
        
        return id1, label
    
    # 增加电压量测
    def addVoltageMeasures(self,jobName:str, VMin:Optional[float] = None, VMax:Optional[float] = None, NameSet:Union[Set,List] = None, Keys:Optional[list] = None, freq:Optional[int] = 200, PlotName:Optional[str] = None):
        """
        Descriptions
        ----------
            增加对母线电压的量测配置，可根据电压范围、名称集合或指定 Key 筛选母线。

        Parameters
        ----------
            jobName (str): 关联的仿真任务名称。
            VMin (float, optional): 筛选母线的最小电压值。默认为 `None`。
            VMax (float, optional): 筛选母线的最大电压值。默认为 `None`。
            NameSet (set or list, optional): 筛选母线的名称集合。默认为 `None`。
            Keys (list, optional): 预筛选的母线 Key 列表。默认为 `None`。
            freq (int, optional): 采样频率，默认为 200 Hz。
            PlotName (str, optional): 绘图名称。默认为 `None`。

        Output
        ----------
            dict: 筛选出的母线组件字典，键为组件 Key，值为 `Component` 对象。
        Examples
        --------
        >>> # 量测220kV以上母线的电压
        >>> addVoltageMeasures('SA_电磁暂态仿真', VMin = 220, PlotName = '220kV以上电压曲线')

        >>> # 量测110kV母线的电压
        >>> addVoltageMeasures('SA_电磁暂态仿真', VMin = 110,, VMax = 120 PlotName = '110kV电压曲线')
        
        >>> # 量测10kV以下的母线电压
        >>> addVoltageMeasures('SA_电磁暂态仿真', VMin = 0.01, Vmax = 10, PlotName = '10kV以下电压曲线')

        """
        VCondition = {'arg':'VBase','Min':None,'Max':None,'Set':None}
        plotName = 'Voltage:'
        if VMin!=None:
            VCondition['Min'] = VMin;
            plotName = plotName+str(VMin)+'-'
        else:
            plotName = plotName+'0-'
        if VMax!=None:
            VCondition['Max'] = VMax;
            plotName = plotName+str(VMax)
        else:
            plotName = plotName+'Inf'
        
        if(PlotName!= None):
            plotName = PlotName;
            
            
        NCondition = {'arg':'Name','Min':None,'Max':None,'Set':None}
        if NameSet!=None:
            NCondition['Set'] = NameSet;
        screenedBus = self.screenCompByArg('model/CloudPSS/_newBus_3p', [VCondition,NCondition], compList = Keys);
         
        outputChannels = []
        for k in screenedBus.keys():
            p = screenedBus[k].args['Vrms'];
            if(p==''):
                p = '#'+screenedBus[k].label+'.Vrms'
                screenedBus[k].args['Vrms'] = p;
            
            id1, label = self.addChannel(p,1)
            outputChannels.append(id1)
            
        if(freq ==None):
            freq = 200;
        self.addOutputs(jobName, {'0':plotName, '1':freq, '2':'compressed', '3':1, '4':outputChannels})    
        
        return screenedBus
    
    def addBusFrequencyMonitors(self, busKeys:List): # 增加母线频率监测
        """
        Descriptions
        ----------
            为指定的母线增加频率监测功能，通过添加 PLL (锁相环) 和 ChannelDeMerge (分线器) 组件。

        Parameters
        ----------
            busKeys (list): 需要监测频率的母线 Key 列表。

        Output
        ----------
            list: 添加的 PLL 组件的 Key 列表。
        """
        PLLKeys = []
        tempTime = time.strftime("%Y%m%d%H%M%S", time.localtime())+str(random.randint(100,999))
        
        for k in range(len(busKeys)):
            
            busK = busKeys[k];
            blabel = self.project.getComponentByKey(busK).pins['0']
            if(blabel == ''):
                blabel = self.project.getComponentByKey(busK).args['Name']
            if(blabel == ''):
                blabel = self.project.getComponentByKey(busK).label
            
    # 添加PLL
            tempID = '_newPLL_'+tempTime+'_'+str(k);
            nameTemp = tempID
            argsTemp = {'Name':nameTemp,'Dim':'3', 'Voltage':str(float(self.project.getComponentByKey(busK).args['V'])*float(self.project.getComponentByKey(busK).args['VBase'])*math.sqrt(2/3)),
                        'F':self.project.getComponentByKey(busK).args['Freq'],
                        'Fo':"#"+busK+tempID+'.Freq'}
            PLLpinsTemp = {"0": busK+tempID+'.a',"1": busK+tempID+'.b',"2": busK+tempID+'.c',"3": blabel+'.Theta'}
            
            id1, label = self.addCompInCanvas(self.compLib['_newPLL'], key = tempID, canvas = self.cPSAid, args = argsTemp, pins = PLLpinsTemp, label = nameTemp, MaxX = 500)
            PLLKeys.append(id1)
    # 添加分线器
            tempID = 'SA_DeMerge_'+tempTime+str(k);
            nameTemp = 'SA_DeMerge_'+tempTime+str(k);
            argsTemp = {"Out": [
                {
                    "0": "Out[1]",
                    "1": "0",
                    "2": "0",
                    "3": "1",
                    "4": "1",
                    "ɵid": 1
                },
                {
                    "0": "Out[2]",
                    "1": "1",
                    "2": "0",
                    "3": "1",
                    "4": "1",
                    "ɵid": 2
                },
                {
                    "0": "Out[3]",
                    "1": "2",
                    "2": "0",
                    "3": "1",
                    "4": "1",
                    "ɵid": 3
                }
            ]}
            if(self.project.getComponentByKey(busK).args['Vabc'] == ''):
                self.project.getComponentByKey(busK).args['Vabc'] = '#'+busK+'.Vabc'
            pinName = self.project.getComponentByKey(busK).args['Vabc']

            pinsTemp = {"InName": pinName,"id-1": PLLpinsTemp['0'], "id-2": PLLpinsTemp['1'], "id-3": PLLpinsTemp['2']}
        
            id1, label = self.addCompInCanvas(self.compLib['_ChannelDeMerge'], key = tempID, canvas = self.cPSAid,args = argsTemp, pins = pinsTemp, label = nameTemp, MaxX = 500)
        return PLLKeys
    def addComponentOutputMeasures_relative(self, jobName:str, compRID:str, measuredKey:str, reference:str, conditions:Dict, compList:Optional[list] = None,type:Optional[str] ='arg', angle:Optional[Tuple]=None, dim:Optional[int] = 1, curveName:Optional[str] = None, plotName:Optional[str] = None, freq:Optional[int] = 200):
        """
        Descriptions
        ----------
            根据参考组件和指定条件，添加组件输出量测。
            此方法根据组件相对于参考组件的量测值创建输出通道。它支持基于参数和引脚的量测，并允许可选的角度转换。

        Parameters
        ----------
            jobName (str): 与输出关联的任务名称。
            compRID (str): 要筛选的组件的资源 ID。
            measuredKey (str): 要评估的量测的 Key。
            reference (str): 参考组件的 Key。
            conditions (dict): 用于筛选组件的条件。
            compList (list, optional): 要筛选的组件列表。默认为 None。
            type (str, optional): 量测类型（'arg' 用于参数，'pin' 用于引脚）。默认为 'arg'。
            angle (tuple, optional): 指定角度转换的元组（输入单位，输出单位）。默认为 None。
            dim (int, optional): 输出通道的维度。默认为 1。
            curveName (str, optional): 要使用的曲线名称。默认为 None。
            plotName (str, optional): 要创建的绘图名称。默认为 None。
            freq (int, optional): 输出通道的频率。默认为 200。

        Output
        ----------
            dict: 符合指定条件的已筛选组件字典。
        """
        refComp = self.project.getComponentByKey(reference);
        if(type=='arg'):
            screenedComps = self.screenCompByArg(compRID, conditions, compList = compList);
            p = refComp.args[measuredKey];
            if(p==''):
                p = '#ABS_'+refComp.label+'.' + curveName;
                refComp.args[measuredKey] = p;
        elif(type=='pin'):
            screenedComps = self.screenCompByArg(compRID, conditions, compList = compList);
            p = refComp.pins[measuredKey];
            if(p==''):
                p = '#ABS_'+refComp.label+'.' + curveName;
                refComp.pins[measuredKey] = p;
        
        
        
        SumKeys = []
        tempTime = time.strftime("%Y%m%d%H%M%S", time.localtime())+str(random.randint(100,999))

        outputChannels = []
        if(curveName == None):
            curveName = measuredKey;
        for k in screenedComps.keys():
            p = screenedComps[k].args[measuredKey];
            if(p==''):
                p = '#ABS_'+screenedComps[k].label+'.' + curveName;
                screenedComps[k].args[measuredKey] = p;
            # 添加减法器
            tempID = '_newSum_'+tempTime+'_'+str(k);
            nameTemp = tempID
            argsTemp = {}
            if(angle!=None):
                ptemp = '#REL_'+screenedComps[k].label+'.' + curveName
            else:
                ptemp = '#'+screenedComps[k].label+'.' + curveName
            pfinal = '#'+screenedComps[k].label+'.' + curveName
            if(type=='arg'):
                sumPinsTemp = {
                    "3": screenedComps[k].args[measuredKey],
                    "5": refComp.args[measuredKey],
                    "7": ptemp
                }
            elif(type=='pin'):
                sumPinsTemp = {
                    "3": screenedComps[k].pins[measuredKey],
                    "5": refComp.pins[measuredKey],
                    "7": ptemp
                }
            
            id1, label = self.addCompInCanvas(self.compLib['_newSum'], key = tempID, canvas = self.cPSAid, args = argsTemp, pins = sumPinsTemp, label = nameTemp, MaxX = 500)
            SumKeys.append(id1)

            # 添加角度转换
            if(angle!=None):
                tempID = '_newAngRes_'+tempTime+'_'+str(k);
                nameTemp = tempID
                argsTemp = {"IPUnit": str(angle[0]),
                            "OPUnit": str(angle[1]),
                            "Range": "0"}
                angPinsTemp = {
                    "0": ptemp,
                    "1": pfinal
                }
                
                id1, label = self.addCompInCanvas(self.compLib['_newAngleResolver'], key = tempID, canvas = self.cPSAid,
                                                   args = argsTemp, pins = angPinsTemp, label = nameTemp, MaxX = 500)
                SumKeys.append(id1)

            
            id1, label = self.addChannel(pfinal,dim, channelName=screenedComps[k].label+'.' + curveName)
            outputChannels.append(id1)
            
        if(freq ==None):
            freq = 200;
        self.addOutputs(jobName, {'0':plotName, '1':freq, '2':'compressed', '3':1, '4':outputChannels}) 

        return screenedComps

    def addComponentOutputMeasures(self, jobName:str, compRID:str, measuredKey:str, conditions:List, compList:Optional[list] = None, dim:Optional[int] = 1, curveName:Optional[str] = None, plotName:Optional[str] = None, freq:Optional[int] = 200):
        """
        Descriptions
        ----------
            根据组件的参数条件，增加对特定组件输出的量测配置。

        Parameters
        ----------
            jobName (str): 关联的仿真任务名称。
            compRID (str): 组件的ID。
            measuredKey (str): 要量测的组件参数的 Key。
            conditions (list): 筛选组件的条件列表，每个条件是一个字典，包含 'arg' (参数名), 'Min' (最小值), 'Max' (最大值), 'Set' (集合)。
            compList (list, optional): 预筛选的组件 Key 列表。默认为 `None`。
            dim (int, optional): 输出通道的维度。默认为 1。
            curveName (str, optional): 曲线名称。如果为 `None`，则使用 `measuredKey`。
            plotName (str, optional): 绘图名称。默认为 `None`。
            freq (int, optional): 采样频率，默认为 `200 Hz`。

        Output
        ----------
            dict: 筛选出的组件字典，键为组件 Key，值为 `Component` 对象。
        Examples
        --------
        >>> addComponentOutputMeasures('SA_电磁暂态仿真', 'model/CloudPSS/_newPLL', 'Fo', [], compList = PLLKeys, plotName = plotNames[pa], freq = 200)

        """   
    

        screenedComps = self.screenCompByArg(compRID, conditions, compList = compList)
        outputChannels = []
        if(curveName == None):
            curveName = measuredKey
        for k in screenedComps.keys():
            p = screenedComps[k].args[measuredKey]
            if(p==''):
                p = '#'+screenedComps[k].label+'.' + curveName
                screenedComps[k].args[measuredKey] = p
            
            id1, label = self.addChannel(p,dim)
            outputChannels.append(id1)
            
        if(freq ==None):
            freq = 200
        self.addOutputs(jobName, {'0':plotName, '1':freq, '2':'compressed', '3':1, '4':outputChannels})    

        return screenedComps

    def addComponentPinOutputMeasures(self, jobName:str, compRID:str, measuredKey:str, conditions:List, compList:Optional[list] = None, dim:Optional[int] = 1, curveName:Optional[str] = None, plotName:Optional[str] = None, freq:Optional[int] = 200):
        """
        Descriptions
        ----------
            根据组件的引脚参数条件，增加对特定组件引脚输出的量测配置。

        Parameters
        ----------
            jobName (str): 关联的仿真任务名称。
            compRID (str): 组件的 Resource ID。
            measuredKey (str): 要量测的组件引脚的 Key。
            conditions (list): 筛选组件的条件列表，每个条件是一个字典，包含 'arg' (参数名), 'Min' (最小值), 'Max' (最大值), 'Set' (集合)。
            compList (list, optional): 预筛选的组件 Key 列表。默认为 `None`。
            dim (int, optional): 输出通道的维度。默认为 1。
            curveName (str, optional): 曲线名称。如果为 `None`，则使用 `measuredKey`。
            plotName (str, optional): 绘图名称。默认为 `None`。
            freq (int, optional): 采样频率，默认为 200 Hz。

        Output
        ----------
            dict: 筛选出的组件字典，键为组件 Key，值为 `Component` 对象。
        Examples
        --------
        >>> addComponentPinOutputMeasures('SA_电磁暂态仿真', 'model/admin/HW_PCS_TEST_Mask', 'P', [], plotName = '储能有功功率曲线', freq = 200)

        """
        screenedComps = self.screenCompByArg(compRID, conditions, compList = compList);
        outputChannels = []
        if(curveName == None):
            curveName = measuredKey;
        for k in screenedComps.keys():
            try:
                p = screenedComps[k].pins[measuredKey];
            except:
                print(screenedComps[k])
                print(screenedComps[k].pins)
            if(p==''):
                p = screenedComps[k].label+'.' + curveName;
                screenedComps[k].pins[measuredKey] = p;
            
            id1, label = self.addChannel(p,dim)
            outputChannels.append(id1)
            
        if(freq ==None):
            freq = 200;
        self.addOutputs(jobName, {'0':plotName, '1':freq, '2':'compressed', '3':1, '4':outputChannels})    

        return screenedComps
    
