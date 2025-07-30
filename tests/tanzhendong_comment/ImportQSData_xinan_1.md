# "ImportQSData_xinan_1.py"脚本说明

## 模块说明
该脚本主要用于执行电力系统潮流计算，并对计算结果进行分析、可视化和保存。它利用CloudPSS平台提供的API进行模型操作，包括潮流不平衡量计算、潮流计算，以及结果数据的提取和处理。脚本能够识别同场站的母线，计算场站的总不平衡量，并生成详细的日志文件和电压对比文件。

## 类清单
- `CaseEditToolbox`: 用于与CloudPSS平台交互，进行模型编辑、运行和结果获取的工具箱。

## 模块级函数清单
- `getSameStationBuses`: 抓取同场站内所有母线（Bus）的集合。
- `PFCalculate`: 执行潮流计算，包括不平衡量计算和潮流求解，并对结果进行分析和保存。
- `jobmessage`: 发送日志消息到CloudPSS作业UI。

## 类与方法详细说明
### 类：`CaseEditToolbox`
- **功能**：提供与CloudPSS平台交互的功能，用于电力系统模型的编辑、参数设置、仿真运行和结果获取。
- **方法**：
  #### 方法：`setConfig`
  - **功能**：配置`CaseEditToolbox`实例的连接参数。
  - **参数**：
    - `tk` (`str`): API token。
    - `apiURL` (`str`): API的URL。
    - `username` (`str`): 用户名。
    - `projectKey` (`str`): 项目键。
    - `comLibName` (`str`): 组件库名称，默认为'saSource.json'。
  - **返回值**：
    - `None`
  #### 方法：`setInitialConditions`
  - **功能**：进行初始化设置。
  - **参数**：
    - 无
  - **返回值**：
    - `None`
  #### 方法：`getModelJob`
  - **功能**：获取指定名称的模型作业。
  - **参数**：
    - `jobName` (`str`): 作业名称。
  - **返回值**：
    - `list`: 包含模型作业信息的列表。
  #### 方法：`getComponentByKey`
  - **功能**：根据key获取组件。
  - **参数**：
    - `key` (`str`): 组件的唯一标识符。
  - **返回值**：
    - `object`: 对应的组件对象。
  #### 方法：`run`
  - **功能**：运行模型作业。
  - **参数**：
    - `job` (`dict`): 包含作业信息的字典。
  - **返回值**：
    - `Runner`: 作业运行器对象。
  #### 方法：`saveProject`
  - **功能**：保存当前项目为新名称。
  - **参数**：
    - `newKey` (`str`): 新项目的key。
    - `name` (`str`): 新项目的名称。
  - **返回值**：
    - `None`
  *注意：上述方法基于代码中对`ce`对象的使用推断，实际`CaseEditToolbox`的完整API请参考其官方文档。*

## 模块级函数说明
### 函数名：`getSameStationBuses`
- **功能**：递归地查找给定母线所属的同一场站内的所有母线。判断依据是母线之间存在有功和无功均为零的支路连接，这通常意味着这些母线属于同一个物理场站。
- **参数**：
  - `BusResDict` (`dict`): 包含所有母线结果的字典，键为母线名称。
  - `BranchResDict` (`dict`): 包含所有支路结果的字典，键为母线名称，值为与该母线相连的支路列表。
  - `busSet` (`set`): 用于存储已找到的同场站母线集合，初始为空集合。
  - `name` (`str`): 当前要检查的母线名称。
- **返回值**：
  - `set`: 包含同场站内所有母线名称的集合。

### 函数名：`PFCalculate`
- **功能**：执行电力系统的潮流计算，包括不平衡量计算和潮流求解，并将结果保存到CSV文件。同时，它还会对潮流结果进行分析，计算并输出每个厂站的功率不平衡量，以及母线电压对比信息。
- **参数**：
  - `job` (`object`): CloudPSS作业对象，用于发送日志消息。
  - `projectKey` (`str`): 要分析的算例的项目key，默认为'xinan20230731-1_All_QS'。
  - `qspath` (`str`): 潮流计算结果文件保存路径，默认为'./QSFiles0810'。
- **返回值**：
  - `None`

### 函数名：`jobmessage`
- **功能**：发送结构化的JSON日志消息到CloudPSS作业的UI界面，以便用户实时查看任务进度和信息。
- **参数**：
  - `job` (`object`): CloudPSS作业对象，通过其`print`方法发送消息。
  - `content` (`str`): 要发送的日志内容的字符串。
  - `level` (`str`): 日志级别，如'info', 'warning', 'error'等，默认为'info'。
  - `html` (`bool`): 指示`content`是否为HTML格式，默认为`False`。
  - `key` (`str`): 消息的唯一标识符，用于UI端对特定消息进行更新或定位，默认为`None`。
  - `verb` (`str`): 对消息的操作类型，如'append'（追加），默认为'append'。
- **返回值**：
  - `None`
