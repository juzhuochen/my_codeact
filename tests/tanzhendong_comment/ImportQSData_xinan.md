# ImportQSData_xinan.py 脚本说明

## 模块说明
`ImportQSData_xinan.py` 脚本主要功能是导入西南电网的 QS (Quick Stability) 数据到 CloudPSS 平台，并进行相应的处理、初始化、拓扑分析和项目保存。它集成了数据读取、组件创建与修改、网络拓扑处理、潮流初值设置以及最终的项目保存等一系列操作，旨在自动化 QS 数据到 CloudPSS 模型的转换过程。

## 类清单
- `CaseEditToolbox`: 用于编辑 CloudPSS 仿真案例的工具箱，管理项目配置、组件操作、拓扑刷新和计算任务运行。

## 模块级函数清单
- `_initialize_project`: 初始化 CloudPSS 项目的配置，包括设置连接参数、加载组件库、设置初始条件、清除特定组件并刷新拓扑。
- `_clean_and_set_initial_values`: 清理项目中的孤立网络，并根据 QS 数据为母线设置潮流初值，包括电压幅值和相角。
- `analysis_and_save`: 运行 CloudPSS 的交流分网拓扑分析计算，并保存处理后的项目。
- `ImportQSData_xinan`: 脚本的主入口函数，协调调用其他辅助函数，完成 QS 数据的导入、处理和项目保存的整个流程。

## 类与方法详细说明

### 类名：`CaseEditToolbox`
- **功能**：提供一系列工具和接口，用于程序化地编辑和管理 CloudPSS 仿真案例。它允许开发者与 CloudPSS 平台进行交互，执行诸如配置设置、组件操作、拓扑刷新和任务运行等功能。
- **方法**：
  在所提供的代码片段中，`CaseEditToolbox` 实例 `ce` 调用了以下方法，但这些方法并非在此脚本中定义，而是 `CaseEditToolbox` 库自带的方法：
  #### 方法：`setConfig`
  - **功能**：设置 `CaseEditToolbox` 实例与 CloudPSS 平台交互所需的配置参数。
  - **参数**：
    - `tk` (`str`): 用于身份验证或API访问的令牌。
    - `apiURL` (`str`): CloudPSS 计算服务的API URL。
    - `username` (`str`): 用于登录 CloudPSS 的用户名。
    - `projectKey` (`str`): 项目的唯一标识符。
    - `comLibName` (`str`, optional): 组件库文件名，默认为 'saSource.json'。
  - **返回值**：
    - `None`

  #### 方法：`setInitialConditions`
  - **功能**：设置项目的初始条件，为后续操作（如拓扑刷新）做准备。
  - **参数**：
    - 无
  - **返回值**：
    - `None`

  #### 方法：`getComponentsByRid`
  - **功能**：根据组件的 RID (Resource ID) 获取项目中所有匹配的组件。
  - **参数**：
    - `rid` (`str`): 组件的资源 ID。
  - **返回值**：
    - `dict`: 一个字典，键为组件的 ID，值为组件对象。

  #### 方法：`createCanvas`
  - **功能**：在项目中创建一个新的画布。
  - **参数**：
    - `canvasName` (`str`): 新画布的名称。
    - `aliasName` (`str`): 新画布的别名。
  - **返回值**：
    - `None`

  #### 方法：`refreshTopology`
  - **功能**：刷新项目的拓扑信息，通常在组件添加、删除或修改后调用，以更新内部图结构。
  - **参数**：
    - 无
  - **返回值**：
    - `None`

  #### 方法：`generateNetwork`
  - **功能**：基于当前项目数据生成网络结构，供后续拓扑分析或潮流计算使用。
  - **参数**：
    - 无
  - **返回值**：
    - `None`

  #### 方法：`setCompLabelDict`
  - **功能**：构建或更新组件标签到组件 ID 的映射字典，方便通过标签快速查找组件。
  - **参数**：
    - 无
  - **返回值**：
    - `None`

  #### 方法：`getComponentByKey`
  - **功能**：根据组件的唯一键（ID）获取组件对象。
  - **参数`**：
    - `key` (`str`): 组件的唯一标识符。
  - **返回值**：
    - `object`: 对应的组件对象。

  #### 方法：`getModelJob`
  - **功能**：获取项目中指定名称的计算方案（Job）。
  - **参数`**：
    - `jobName` (`str`): 计算方案的名称。
  - **返回值`**：
    - `list`: 包含匹配计算方案对象的列表。

  #### 方法：`run`
  - **功能`**：运行一个给定的计算方案。
  - **参数`**：
    - `job` (`object`): 要运行的计算方案对象。
  - **返回值`**：
    - `object`: 任务运行器对象，可以查询任务状态和结果。

  #### 方法：`saveProject`
  - **功能`**：保存当前项目。
  - **参数`**：
    - `projectKey` (`str`): 保存后项目的唯一标识符。
    - `name` (`str`, optional): 保存后项目的名称。
  - **返回值`**：
    - `None`

## 模块级函数说明

### 函数名：`_initialize_project`
- **功能**：初始化 CloudPSS 项目的配置，包括设置连接参数、加载组件库、设置初始条件。它还会清除项目中特定的无功补偿和串补组件，并刷新拓扑。如果需要，还会生成并保存 iGraph 相关信息。
- **参数**：
  - `job` (`object`): 任务对象，用于记录日志和发送消息。
  - `projectKey` (`str`): 项目的唯一标识符。
  - `qspath` (`str`): Quick Stability (QS) 数据文件的路径。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例，用于操作 CloudPSS 项目。
- **返回值**：
  - `tuple`: 包含 `busLabelDict` (母线标签到键的字典), `mergedG` (合并后的 iGraph 图), `mergeDict` (合并字典), 和 `generateTopoSP` (是否生成拓扑 SP 的标志) 的元组。

### 函数名：`_clean_and_set_initial_values`
- **功能**：该函数用于清理 CloudPSS 项目中的孤立网络（即不包含任何电源的连通分量），并根据 QS 数据为剩余母线设置潮流初值（电压幅值和相角）。它还会识别 QS 数据中存在但在 PS 中不存在的母线，以及 PS 中存在但在 QS 数据中不存在的母线。
- **参数**：
  - `job` (`object`): 任务对象，用于记录日志。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例，用于操作 CloudPSS 项目。
  - `qspath` (`str`): Quick Stability (QS) 数据文件的路径。
  - `T3WCentDict` (`dict`): 三绕组变压器中心点字典，键是变压器标签，值是中心点母线的标签。
- **返回值**：
  - `None`

### 函数名：`analysis_and_save`
- **功能**：运行 CloudPSS 中的交流分网计算方案，并将计算结果应用于项目，最后保存修改后的项目。
- **参数**：
  - `job` (`object`): 任务对象，用于记录日志。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例，用于操作 CloudPSS 项目。
  - `projectKey` (`str`): 项目的唯一标识符。
- **返回值**：
  - `None`

### 函数名：`ImportQSData_xinan`
- **功能**：这是一个主入口函数，它协调整个 QS 数据导入和处理流程。它会初始化项目，依次调用内部辅助函数来处理交流线路、串补、变压器、母线、发电机、负荷、并联补偿器和直流线路数据。最后，它会清理孤立网络、设置潮流初值，并运行拓扑分析和保存项目。
- **参数**：
  - `job` (`object`): 任务对象，用于记录日志。
  - `projectKey` (`str`, optional): 项目的唯一标识符，默认为 'xinan20230731-1_All'。
  - `qspath` (`str`, optional): Quick Stability (QS) 数据文件的路径，默认为 './QSFiles0810/'。
- **返回值**：
  - `None`