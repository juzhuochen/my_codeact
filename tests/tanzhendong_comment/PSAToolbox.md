# PSAToolbox.py 脚本说明

## 模块说明
`PSAToolbox.py` 脚本定义了一个 `PSAToolbox` 类，继承自 `CaseEditToolbox`，旨在提供一套用于电力系统安全分析（PSA）的工具集。它封装了在 CloudPSS 仿真平台中进行故障设置（如接地故障、N-1/N-k 故障）、安控策略元件添加以及仿真输出量测配置的功能。该工具箱极大地简化了用户在 CloudPSS 环境中搭建和执行复杂电力系统暂态稳定和安全分析仿真的流程。

## 类清单
- `PSAToolbox`: 用于电力系统安全分析的工具箱，继承自 `CaseEditToolbox`。

## 模块级函数清单
- `is_number`

## 类与方法详细说明

### 类名：`PSAToolbox`
- **功能**：提供电力系统安全分析（PSA）相关的功能，包括自动化故障设置、安控策略元件添加和输出量测配置。
- **方法**：
  #### 方法：`__init__`
  - **功能**：`PSAToolbox` 类的构造函数。初始化父类 `CaseEditToolbox` 并定义内部使用的画布 ID 和常用组件名称映射。
  - **参数**：
    - 无
  - **返回值**：
    - 无
  #### 方法：`createSACanvas`
  - **功能**：创建或初始化用于安全分析相关的画布，包括故障设置画布、安控策略画布和额外输出画布，并在故障画布上添加接地点组件。
  - **参数**：
    - 无
  - **返回值**：
    - 无
  #### 方法：`setGroundFault`
  - **功能**：在指定引脚设置接地故障，并可选择添加故障电阻和电感。
  - **参数**：
    - `pinName` (`str`): 发生故障的引脚名称。
    - `fault_start_time` (`float`): 故障开始时间。
    - `fault_end_time` (`float`): 故障结束时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherParas` (`dict`, optional): 其他故障参数字典。默认为 `None`。
    - `Inductor` (`float`, optional): 故障接地电感值。默认为 `None`。
  - **返回值**：
    - `tuple`: 包含接地故障电阻组件的 ID (`str`) 和标签 (`str`)。
  #### 方法：`setBreaker_3p`
  - **功能**：在两个母线之间设置三相断路器。
  - **参数**：
    - `busName1` (`str`): 第一个母线的名称。
    - `busName2` (`str`): 第二个母线的名称。
    - `ctrlSigName` (`str`, optional): 控制断路器状态的信号名称。默认为 `None`。
    - `OtherParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - `tuple`: 包含断路器组件的 ID (`str`) 和标签 (`str`)。
  #### 方法：`setN_1`
  - **功能**：设置N-1故障，即切除一条传输元件（如线路）通过添加受控断路器。
  - **参数**：
    - `transKey` (`str`): 传输元件（如线路）的 Key。
    - `cut_time` (`float` or `list`): 切除时间，可以是单个时间点或包含两个时间点的列表（用于两端切除）。
    - `OtherBreakerParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - 无
  #### 方法：`setN_k`
  - **功能**：设置N-k故障，即同时切除 k 条传输元件（如线路）通过添加受控断路器。
  - **参数**：
    - `transKeys` (`list`): 传输元件（如线路）的 Key 列表。
    - `cut_time` (`float`): 切除时间。
    - `OtherBreakerParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - `dict`: 存储 N-k 切除线路信息，键为 `transKey`，值为共同的控制信号名称。
  #### 方法：`setCutFault`
  - **功能**：设置切除故障，即切除任意指定组件的某个引脚，通过添加受控断路器。
  - **参数**：
    - `compKey` (`str`): 组件的 Key。
    - `cut_time` (`float`): 切除时间。
    - `pin` (`str`, optional): 要切除的组件引脚名称。默认为 `'0'`。
    - `OtherBreakerParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - 无
  #### 方法：`setN_1_GroundFault`
  - **功能**：设置 N-1 接地故障，即在切除一条线路的同时，在该线路的某个位置发生接地故障。
  - **参数**：
    - `transKey` (`str`): 传输元件（如线路）的 Key。
    - `side` (`float`): 故障发生在线路上的位置（0表示一端，1表示另一端，0到1之间表示在线路中间）。
    - `fault_start_time` (`float`): 故障开始时间。
    - `cut_time` (`float`): 线路切除时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherFaultParas` (`dict`, optional): 其他故障参数字典。默认为 `None`。
    - `OtherBreakerParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - 无
  #### 方法：`setN_2_GroundFault`
  - **功能**：设置N-2接地故障，即同时切除两条线路，并在其中一条线路的某个位置发生接地故障。
  - **参数**：
    - `transKey1` (`str`): 第一条传输元件的 Key。
    - `transKey2` (`str`): 第二条传输元件的 Key。
    - `side` (`float`): 故障发生在线路上的位置（0表示一端，1表示另一端，0到1之间表示在线路中间）。
    - `fault_start_time` (`float`): 故障开始时间。
    - `cut_time` (`float`): 线路切除时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherFaultParas` (`dict`, optional): 其他故障参数字典。默认为 `None`。
    - `OtherBreakerParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - 无
  #### 方法：`setN_k_GroundFault`
  - **功能**：设置 N-k 接地故障，即同时切除 k 条线路，并在第一条被切除线路的某个位置发生接地故障。
  - **参数**：
    - `transKeys` (`list`): 传输元件（如线路）的 Key 列表。
    - `side` (`float`): 故障发生在线路上的位置（0表示一端，1表示另一端，0到1之间表示在线路中间）。
    - `fault_start_time` (`float`): 故障开始时间。
    - `cut_time` (`float`): 线路切除时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherFaultParas` (`dict`, optional): 其他故障参数字典。默认为 `None`。
    - `OtherBreakerParas` (`dict`, optional): 其他断路器参数字典。默认为 `None`。
  - **返回值**：
    - 无
  #### 方法：`addChannel`
  - **功能**：为指定的引脚添加输出通道，用于在仿真过程中监测和输出该引脚上的信号。
  - **参数**：
    - `pinName` (`str`): 需要添加输出通道的引脚名称。
    - `dim` (`int`): 输出通道的维度（例如，1代表单相，3代表三相）。
    - `channelName` (`str`, optional): 输出通道的名称。如果为 `None`，则使用 `pinName`。默认为 `None`。
  - **返回值**：
    - `tuple`: 包含通道组件的 ID (`str`) 和标签 (`str`)。
  #### 方法：`addVoltageMeasures`
  - **功能**：增加对母线电压的量测配置，可根据电压范围、名称集合或指定 Key 筛选母线。
  - **参数**：
    - `jobName` (`str`): 关联的仿真任务名称。
    - `VMin` (`float`, optional): 筛选母线的最小电压值。默认为 `None`。
    - `VMax` (`float`, optional): 筛选母线的最大电压值。默认为 `None`。
    - `NameSet` (`set` or `list`, optional): 筛选母线的名称集合。默认为 `None`。
    - `Keys` (`list`, optional): 预筛选的母线 Key 列表。默认为 `None`。
    - `freq` (`int`, optional): 采样频率，默认为 200 Hz。
    - `PlotName` (`str`, optional): 绘图名称。默认为 `None`。
  - **返回值**：
    - `dict`: 筛选出的母线组件字典，键为组件 Key，值为 `Component` 对象。
  #### 方法：`addBusFrequencyMonitors`
  - **功能**：为指定的母线增加频率监测功能，通过添加 PLL (锁相环) 和 ChannelDeMerge (分线器) 组件。
  - **参数**：
    - `busKeys` (`list`): 需要监测频率的母线 Key 列表。
  - **返回值**：
    - `list`: 添加的 PLL 组件的 Key 列表。
  #### 方法：`addComponentOutputMeasures`
  - **功能**：根据组件的参数条件，增加对特定组件输出的量测配置。
  - **参数**：
    - `jobName` (`str`): 关联的仿真任务名称。
    - `compRID` (`str`): 组件的 Resource ID。
    - `measuredKey` (`str`): 要量测的组件参数的 Key。
    - `conditions` (`list`): 筛选组件的条件列表，每个条件是一个字典，包含 'arg' (参数名), 'Min' (最小值), 'Max' (最大值), 'Set' (集合)。
    - `compList` (`list`, optional): 预筛选的组件 Key 列表。默认为 `None`。
    - `dim` (`int`, optional): 输出通道的维度。默认为 1。
    - `curveName` (`str`, optional): 曲线名称。如果为 `None`，则使用 `measuredKey`。
    - `plotName` (`str`, optional): 绘图名称。默认为 `None`。
    - `freq` (`int`, optional): 采样频率，默认为 200 Hz。
  - **返回值**：
    - `dict`: 筛选出的组件字典，键为组件 Key，值为 `Component` 对象。
  #### 方法：`addComponentPinOutputMeasures`
  - **功能**：根据组件的引脚参数条件，增加对特定组件引脚输出的量测配置。
  - **参数**：
    - `jobName` (`str`): 关联的仿真任务名称。
    - `compRID` (`str`): 组件的 Resource ID。
    - `measuredKey` (`str`): 要量测的组件引脚的 Key。
    - `conditions` (`list`): 筛选组件的条件列表，每个条件是一个字典，包含 'arg' (参数名), 'Min' (最小值), 'Max' (最大值), 'Set' (集合)。
    - `compList` (`list`, optional): 预筛选的组件 Key 列表。默认为 `None`。
    - `dim` (`int`, optional): 输出通道的维度。默认为 1。
    - `curveName` (`str`, optional): 曲线名称。如果为 `None`，则使用 `measuredKey`。
    - `plotName` (`str`, optional): 绘图名称。默认为 `None`。
    - `freq` (`int`, optional): 采样频率，默认为 200 Hz。
  - **返回值**：
    - `dict`: 筛选出的组件字典，键为组件 Key，值为 `Component` 对象。

## 模块级函数说明
### 函数名：`is_number`
- **功能**：检查一个字符串是否可以被转换为浮点数（即是否代表一个数字）。
- **参数**：
  - `s` (`str`): 待检查的字符串。
- **返回值**：
  - `bool`: 如果字符串能被转换为浮点数则返回 `True`，否则返回 `False`。
