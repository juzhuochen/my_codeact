# S_S_SyncComp.py 脚本说明

## 模块说明
`S_S_SyncComp.py` 脚本定义了一个名为 `S_S_SyncComp` 的 Python 类，该类继承自 `PSAToolbox`，专门用于电力系统稳定分析中的调相机（Synchronous Compensator）选址定容。它实现了电网稳定问题的高级分析功能，包括新增调相机、计算电压敏感度指标（VSI）、计算故障严重程度指标（SI）以及添加动态无功补偿器（SVC）和 PCS（Power Conversion System）等。此外，脚本还包含了一些辅助函数，用于获取 CloudPSS 组件库、抓取组件数据以及生成参数和引脚字典，旨在辅助电力系统仿真和分析。

## 类清单
*   `S_S_SyncComp`: 继承自 `PSAToolbox`，用于电力系统稳定分析，特别是调相机相关的分析功能。

## 模块级函数清单
*   `is_number`: 判断字符串是否能转换为数字。
*   `getCompLib`: 获取 CloudPSS 平台的组件库。
*   `fetchCompData`: 获取指定 RID 的组件数据。
*   `genParaDict`: 生成 CloudPSS 组件的参数字典和引脚字典。
*   `merge_and_deduplicate`: 合并字符串内容并进行去重。

## 类与方法详细说明

### 类名：`S_S_SyncComp`
- **功能**：继承自 `PSAToolbox`，提供用于电力系统稳定分析的高级功能，特别是针对调相机选址定容、电压敏感度计算和故障严重程度评估。
- **方法**：
  #### 方法：`__init__`
  - **功能**：初始化 `S_S_SyncComp` 类的实例。
  - **参数**：无
  - **返回值**：无

  #### 方法：`createSSSCACanvas`
  - **功能**：创建用于调相机分析和动态注入无功的 Canvas。
  - **参数**：无
  - **返回值**：无

  #### 方法：`getXInterval`
  - **功能**：使用二分查找法获取 `xData` 中 `x` 所在区间的索引。
  - **参数**：
    - `xData` (`list`): 一维有序数据列表。
    - `x` (`float`): 要查找的值。
  - **返回值**：
    - `int`: `x` 所在区间的起始索引。

  #### 方法：`calculateDV`
  - **功能**：计算电压偏差（DV），评估电压暂态稳定性。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `voltageMeasureK` (`str`): 电压测量通道的键。
    - `result` (`Result`, optional): 仿真结果对象。默认值为 `None`，表示使用 `runner.result`。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
    - `dT0` (`float`, optional): 计算初始电压平均值的时间范围。默认值为 `0.5`。
    - `judge` (`list`, optional): 电压裕度判断条件，格式为 `[[t_start, t_end, lower_bound, upper_bound], ...]`。默认值 `[[0.1,3,0.75,1.25],[3,999,0.95,1.05]]`。
    - `VminR` (`float`, optional): 稳定电压恢复的最小比例。默认值为 `0.2`。
    - `VmaxR` (`float`, optional): 稳定电压恢复的最大比例。默认值为 `1.8`。
    - `ValidName` (`list`, optional): 用于筛选有效通道的名称列表。默认值为 `None`。
  - **返回值**：
    - `tuple`: 包含电压上限裕度列表 (`list`)、电压下限裕度列表 (`list`)和有效通道索引列表 (`list`)。

  #### 方法：`calculateSI`
  - **功能**：计算故障严重程度指标（SI）。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `voltageMeasureK` (`str`): 电压测量通道的键。
    - `result` (`Result`, optional): 仿真结果对象。默认值为 `None`，表示使用 `runner.result`。
    - `Ts` (`float`, optional): 扰动发生时间。默认值为 `4`。
    - `dT0` (`float`, optional): 计算初始电压平均值的时间范围。默认值为 `0.5`。
    - `Tinterval` (`float`, optional): 故障清除后，计算积分开始的时间偏移。默认值为 `0.11`。
    - `T1` (`float`, optional): 计算 SI 时，积分时间窗的长度。默认值为 `3`。
    - `dV1` (`float`, optional): 第一阶段电压偏差阈值。默认值为 `0.25`。
    - `dV2` (`float`, optional): 第二阶段电压偏差阈值。默认值为 `0.1`。
    - `VminR` (`float`, optional): 稳定电压恢复的最小比例。默认值为 `0.2`。
    - `VmaxR` (`float`, optional): 稳定电压恢复的最大比例。默认值为 `1.8`。
  - **返回值**：
    - `tuple`: 包含故障严重程度指标 SI (`float`) 和有效通道索引列表 (`list`)。

  #### 方法：`calculateVSI`
  - **功能**：计算电压敏感度指标（VSI）。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `voltageMeasureK` (`str`): 电压测量通道的键。
    - `dQMeasureK` (`str`): 无功功率测量通道的键。
    - `busLabels` (`list`): 母线标签列表。
    - `result` (`Result`, optional): 仿真结果对象。默认值为 `None`，表示使用 `runner.result`。
    - `busNum` (`int`, optional): 母线数量。默认值为 `None`，将根据仿真结束时间计算。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
    - `dT` (`float`, optional): 每个母线测试所占用的仿真时长。默认值为 `1`。
    - `ddT` (`float`, optional): 无功注入持续时间。默认值为 `0.5`。
  - **返回值**：
    - `dict`: 包含 VSIi（每个母线的平均 VSI）和 VSIij（每个母线对其他所有母线的 VSI）的字典。

  #### 方法：`addVSIMeasure`
  - **功能**：在仿真 Job 中添加 VSI 相关的量测，包括电压量测和无功功率量测。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `VSIQkeys` (`list`): VSI 无功源组件的键列表。
    - `VMin` (`float`, optional): 筛选电压量测母线的最小电压。默认值为 `None`。
    - `VMax` (`float`, optional): 筛选电压量测母线的最大电压。默认值为 `None`。
    - `NameSet` (`set`, optional): 筛选电压量测母线的名称集合。默认值为 `None`。
    - `NameKeys` (`list`, optional): 筛选电压量测母线的名称关键字列表。默认值为 `None`。
    - `freq` (`float`, optional): 输出通道的测量频率。默认值为 `None`。
    - `Nbus` (`int`, optional): 要添加 VSI 测量功能的母线数量。默认值为 `10`。
    - `dT` (`float`, optional): 每个母线测试所占用的仿真时长。默认值为 `0.5`。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
  - **返回值**：
    - `tuple`: 包含电压量测的输出通道索引 (`int`)、无功量测的输出通道索引 (`int`) 和筛选后的母线列表 (`list`)。

  #### 方法：`addVSIQSource`
  - **功能**：为电压敏感度分析添加动态注入无功源（shuntLC 组件和断路器）。
  - **参数**：
    - `busKeys` (`list`): 需要添加无功源的母线键列表。
    - `V` (`float`, optional): 动态注入无功源的基准电压（kV）。默认值为 `220`。
    - `S` (`float`, optional): 动态注入无功源的基准无功（MVar）。默认值为 `1`。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
    - `dT` (`float`, optional): 对每个母线测试时所占用的仿真时长（s）。默认值为 `1`。
    - `ddT` (`float`, optional): 无功注入持续时间。默认值为 `0.5`。
  - **返回值**：
    - `list`: VSI 无功源的组件 ID 列表。

  #### 方法：`addSVC`
  - **功能**：添加静态无功补偿器（SVC）到指定母线。
  - **参数**：
    - `busKey` (`str`): SVC 将要连接的母线键。
    - `S` (`float`, optional): SVC 的额定视在功率（MVar）。默认值为 `1`。
    - `Ts` (`float`, optional): SVC 启用时间（s）。默认值为 `4`。
    - `Te` (`float`, optional): SVC 禁用时间（s）。默认值为 `999`。
  - **返回值**：
    - `list`: 添加的 SVC 相关组件（shuntLC、断路器、信号发生器）的 ID 列表。

  #### 方法：`addPCSComp`
  - **功能**：添加 PCS (Power Conversion System) 组件到指定母线。
  - **参数**：
    - `busKey` (`str`): PCS 将要连接的母线键。
    - `S` (`float`, optional): PCS 的额定功率（MVar）。默认值为 `10`。
    - `PCSArgs` (`dict`, optional): PCS 组件的详细参数字典，用于覆盖默认参数。默认值为 `None`。
  - **返回值**：
    - `list`: 添加的 PCS 组件的 ID 列表。

  #### 方法：`addSyncComp`
  - **功能**：在指定母线处添加同步调相机及其相关组件（母线、变压器、AVR、增益模块）。
  - **参数**：
    - `busKey` (`str`): 调相机将要连接的母线键。
    - `pfResult` (`PowerFlowResult`): 潮流计算结果对象，用于获取母线的电压幅值和相角。
    - `syncArgs` (`dict`, optional): 同步发电机组件的详细参数字典。默认值为 `None`。
    - `transArgs` (`dict`, optional): 变压器组件的详细参数字典，例如 `{"Smva": "额定容量","X1": "正序漏电抗","Rl": "正序漏电阻"}`。默认值为 `None`。
    - `busArgs` (`dict`, optional): 新增母线组件的详细参数字典。默认值为 `None`。
    - `AVRComp` (`dict`, optional): AVR 组件的定义字典。默认值为 `None`，使用默认的 PSASP 11-12 型 AVR。
    - `AVRArgs` (`dict`, optional): AVR 组件的详细参数字典。默认值为 `None`。
  - **返回值**：
    - `list`: 新增所有组件（同步调相机、母线、变压器、AVR、增益模块）的 ID 列表。

## 模块级函数说明

### 函数名：`is_number`
- **功能**：判断给定字符串是否可以转换为浮点数或 unicode 数字。
- **参数**：
  - `s` (`str`): 需要判断的字符串。
- **返回值**：
  - `bool`: 如果字符串能转换为数字则返回 `True`，否则返回 `False`。

### 函数名：`getCompLib`
- **功能**：从 CloudPSS 平台获取指定项目中的组件库，并将其保存为 JSON 文件。
- **参数**：
  - `tk` (`str`): CloudPSS 平台的认证 Token。
  - `apiURL` (`str`): CloudPSS API 的 URL。
  - `spr` (`str`): CloudPSS 项目的键（通常是 `model/<username>/<projectname>`）。
  - `compDefLib` (`dict`, optional): 用户自定义的组件定义库，用于映射组件的全路径到简短键。默认值为空字典。
  - `name` (`str`, optional): 保存组件库的 JSON 文件名。默认值为 `'saSource.json'`。
- **返回值**：
  - `dict`: 包含组件信息的字典。

### 函数名：`fetchCompData`
- **功能**：根据给定的组件 RID 列表，从 CloudPSS 平台批量获取组件的详细数据。
- **参数**：
  - `rids` (`list`): 待获取数据的组件 RID（Resource ID）列表。
- **返回值**：
  - `dict`: 包含组件 ID 和对应数据的字典。

### 函数名：`genParaDict`
- **功能**：从 CloudPSS 平台获取指定项目的所有组件的参数和引脚信息，并生成相应的字典。
- **参数**：
  - `zdmToken` (`str`): CloudPSS 平台的认证 Token。
  - `internalapiurl` (`str`): CloudPSS 内部 API 的 URL。
  - `projName` (`str`): CloudPSS 项目的名称或键。
- **返回值**：
  - `tuple`: 包含两个字典，第一个是参数字典 (`ParaDict`)，第二个是引脚字典 (`PinDict`)。

### 函数名：`merge_and_deduplicate`
- **功能**：合并现有内容和新内容，并对新内容中的行进行去重，确保新添加的行是独一无二的。
- **参数**：
  - `existing_content_str` (`str`): 已经存在的内容字符串。
  - `new_content_str` (`str`): 新添加的内容字符串。
  - `current_index` (`int`): 当前内容的行号计数器。
- **返回值**：
  - `tuple`: 包含合并并去重后的内容字符串 (`str`) 和更新后的行号计数器 (`int`)。
```output
# S_S_SyncComp.py 脚本说明

## 模块说明
`S_S_SyncComp.py` 脚本定义了一个名为 `S_S_SyncComp` 的 Python 类，该类继承自 `PSAToolbox`，专门用于电力系统稳定分析中的调相机（Synchronous Compensator）选址定容。它实现了电网稳定问题的高级分析功能，包括新增调相机、计算电压敏感度指标（VSI）、计算故障严重程度指标（SI）以及添加动态无功补偿器（SVC）和 PCS（Power Conversion System）等。此外，脚本还包含了一些辅助函数，用于获取 CloudPSS 组件库、抓取组件数据以及生成参数和引脚字典，旨在辅助电力系统仿真和分析。

## 类清单
*   `S_S_SyncComp`: 继承自 `PSAToolbox`，用于电力系统稳定分析，特别是调相机相关的分析功能。

## 模块级函数清单
*   `is_number`: 判断字符串是否能转换为数字。
*   `getCompLib`: 获取 CloudPSS 平台的组件库。
*   `fetchCompData`: 获取指定 RID 的组件数据。
*   `genParaDict`: 生成 CloudPSS 组件的参数字典和引脚字典。
*   `merge_and_deduplicate`: 合并字符串内容并进行去重。

## 类与方法详细说明

### 类名：`S_S_SyncComp`
- **功能**：继承自 `PSAToolbox`，提供用于电力系统稳定分析的高级功能，特别是针对调相机选址定容、电压敏感度计算和故障严重程度评估。
- **方法**：
  #### 方法：`__init__`
  - **功能**：初始化 `S_S_SyncComp` 类的实例。
  - **参数**：无
  - **返回值**：无

  #### 方法：`createSSSCACanvas`
  - **功能**：创建用于调相机分析和动态注入无功的 Canvas。
  - **参数**：无
  - **返回值**：无

  #### 方法：`getXInterval`
  - **功能**：使用二分查找法获取 `xData` 中 `x` 所在区间的索引。
  - **参数**：
    - `xData` (`list`): 一维有序数据列表。
    - `x` (`float`): 要查找的值。
  - **返回值**：
    - `int`: `x` 所在区间的起始索引。

  #### 方法：`calculateDV`
  - **功能**：计算电压偏差（DV），评估电压暂态稳定性。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `voltageMeasureK` (`str`): 电压测量通道的键。
    - `result` (`Result`, optional): 仿真结果对象。默认值为 `None`，表示使用 `runner.result`。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
    - `dT0` (`float`, optional): 计算初始电压平均值的时间范围。默认值为 `0.5`。
    - `judge` (`list`, optional): 电压裕度判断条件，格式为 `[[t_start, t_end, lower_bound, upper_bound], ...]`。默认值 `[[0.1,3,0.75,1.25],[3,999,0.95,1.05]]`。
    - `VminR` (`float`, optional): 稳定电压恢复的最小比例。默认值为 `0.2`。
    - `VmaxR` (`float`, optional): 稳定电压恢复的最大比例。默认值为 `1.8`。
    - `ValidName` (`list`, optional): 用于筛选有效通道的名称列表。默认值为 `None`。
  - **返回值**：
    - `tuple`: 包含电压上限裕度列表 (`list`)、电压下限裕度列表 (`list`)和有效通道索引列表 (`list`)。

  #### 方法：`calculateSI`
  - **功能**：计算故障严重程度指标（SI）。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `voltageMeasureK` (`str`): 电压测量通道的键。
    - `result` (`Result`, optional): 仿真结果对象。默认值为 `None`，表示使用 `runner.result`。
    - `Ts` (`float`, optional): 扰动发生时间。默认值为 `4`。
    - `dT0` (`float`, optional): 计算初始电压平均值的时间范围。默认值为 `0.5`。
    - `Tinterval` (`float`, optional): 故障清除后，计算积分开始的时间偏移。默认值为 `0.11`。
    - `T1` (`float`, optional): 计算 SI 时，积分时间窗的长度。默认值为 `3`。
    - `dV1` (`float`, optional): 第一阶段电压偏差阈值。默认值为 `0.25`。
    - `dV2` (`float`, optional): 第二阶段电压偏差阈值。默认值为 `0.1`。
    - `VminR` (`float`, optional): 稳定电压恢复的最小比例。默认值为 `0.2`。
    - `VmaxR` (`float`, optional): 稳定电压恢复的最大比例。默认值为 `1.8`。
  - **返回值**：
    - `tuple`: 包含故障严重程度指标 SI (`float`) 和有效通道索引列表 (`list`)。

  #### 方法：`calculateVSI`
  - **功能**：计算电压敏感度指标（VSI）。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `voltageMeasureK` (`str`): 电压测量通道的键。
    - `dQMeasureK` (`str`): 无功功率测量通道的键。
    - `busLabels` (`list`): 母线标签列表。
    - `result` (`Result`, optional): 仿真结果对象。默认值为 `None`，表示使用 `runner.result`。
    - `busNum` (`int`, optional): 母线数量。默认值为 `None`，将根据仿真结束时间计算。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
    - `dT` (`float`, optional): 每个母线测试所占用的仿真时长。默认值为 `1`。
    - `ddT` (`float`, optional): 无功注入持续时间。默认值为 `0.5`。
  - **返回值**：
    - `dict`: 包含 VSIi（每个母线的平均 VSI）和 VSIij（每个母线对其他所有母线的 VSI）的字典。

  #### 方法：`addVSIMeasure`
  - **功能**：在仿真 Job 中添加 VSI 相关的量测，包括电压量测和无功功率量测。
  - **参数**：
    - `jobName` (`str`): 仿真任务的名称。
    - `VSIQkeys` (`list`): VSI 无功源组件的键列表。
    - `VMin` (`float`, optional): 筛选电压量测母线的最小电压。默认值为 `None`。
    - `VMax` (`float`, optional): 筛选电压量测母线的最大电压。默认值为 `None`。
    - `NameSet` (`set`, optional): 筛选电压量测母线的名称集合。默认值为 `None`。
    - `NameKeys` (`list`, optional): 筛选电压量测母线的名称关键字列表。默认值为 `None`。
    - `freq` (`float`, optional): 输出通道的测量频率。默认值为 `None`。
    - `Nbus` (`int`, optional): 要添加 VSI 测量功能的母线数量。默认值为 `10`。
    - `dT` (`float`, optional): 每个母线测试所占用的仿真时长。默认值为 `0.5`。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
  - **返回值**：
    - `tuple`: 包含电压量测的输出通道索引 (`int`)、无功量测的输出通道索引 (`int`) 和筛选后的母线列表 (`list`)。

  #### 方法：`addVSIQSource`
  - **功能**：为电压敏感度分析添加动态注入无功源（shuntLC 组件和断路器）。
  - **参数**：
    - `busKeys` (`list`): 需要添加无功源的母线键列表。
    - `V` (`float`, optional): 动态注入无功源的基准电压（kV）。默认值为 `220`。
    - `S` (`float`, optional): 动态注入无功源的基准无功（MVar）。默认值为 `1`。
    - `Ts` (`float`, optional): 仿真开始时间。默认值为 `4`。
    - `dT` (`float`, optional): 对每个母线测试时所占用的仿真时长（s）。默认值为 `1`。
    - `ddT` (`float`, optional): 无功注入持续时间。默认值为 `0.5`。
  - **返回值**：
    - `list`: VSI 无功源的组件 ID 列表。

  #### 方法：`addSVC`
  - **功能**：添加静态无功补偿器（SVC）到指定母线。
  - **参数**：
    - `busKey` (`str`): SVC 将要连接的母线键。
    - `S` (`float`, optional): SVC 的额定视在功率（MVar）。默认值为 `1`。
    - `Ts` (`float`, optional): SVC 启用时间（s）。默认值为 `4`。
    - `Te` (`float`, optional): SVC 禁用时间（s）。默认值为 `999`。
  - **返回值**：
    - `list`: 添加的 SVC 相关组件（shuntLC、断路器、信号发生器）的 ID 列表。

  #### 方法：`addPCSComp`
  - **功能**：添加 PCS (Power Conversion System) 组件到指定母线。
  - **参数**：
    - `busKey` (`str`): PCS 将要连接的母线键。
    - `S` (`float`, optional): PCS 的额定功率（MVar）。默认值为 `10`。
    - `PCSArgs` (`dict`, optional): PCS 组件的详细参数字典，用于覆盖默认参数。默认值为 `None`。
  - **返回值**：
    - `list`: 添加的 PCS 组件的 ID 列表。

  #### 方法：`addSyncComp`
  - **功能**：在指定母线处添加同步调相机及其相关组件（母线、变压器、AVR、增益模块）。
  - **参数**：
    - `busKey` (`str`): 调相机将要连接的母线键。
    - `pfResult` (`PowerFlowResult`): 潮流计算结果对象，用于获取母线的电压幅值和相角。
    - `syncArgs` (`dict`, optional): 同步发电机组件的详细参数字典。默认值为 `None`。
    - `transArgs` (`dict`, optional): 变压器组件的详细参数字典，例如 `{"Smva": "额定容量","X1": "正序漏电抗","Rl": "正序漏电阻"}`。默认值为 `None`。
    - `busArgs` (`dict`, optional): 新增母线组件的详细参数字典。默认值为 `None`。
    - `AVRComp` (`dict`, optional): AVR 组件的定义字典。默认值为 `None`，使用默认的 PSASP 11-12 型 AVR。
    - `AVRArgs` (`dict`, optional): AVR 组件的详细参数字典。默认值为 `None`。
  - **返回值**：
    - `list`: 新增所有组件（同步调相机、母线、变压器、AVR、增益模块）的 ID 列表。

## 模块级函数说明

### 函数名：`is_number`
- **功能**：判断给定字符串是否可以转换为浮点数或 unicode 数字。
- **参数**：
  - `s` (`str`): 需要判断的字符串。
- **返回值**：
  - `bool`: 如果字符串能转换为数字则返回 `True`，否则返回 `False`。

### 函数名：`getCompLib`
- **功能**：从 CloudPSS 平台获取指定项目中的组件库，并将其保存为 JSON 文件。
- **参数**：
  - `tk` (`str`): CloudPSS 平台的认证 Token。
  - `apiURL` (`str`): CloudPSS API 的 URL。
  - `spr` (`str`): CloudPSS 项目的键（通常是 `model/<username>/<projectname>`）。
  - `compDefLib` (`dict`, optional): 用户自定义的组件定义库，用于映射组件的全路径到简短键。默认值为空字典。
  - `name` (`str`, optional): 保存组件库的 JSON 文件名。默认值为 `'saSource.json'`。
- **返回值**：
  - `dict`: 包含组件信息的字典。

### 函数名：`fetchCompData`
- **功能**：根据给定的组件 RID 列表，从 CloudPSS 平台批量获取组件的详细数据。
- **参数**：
  - `rids` (`list`): 待获取数据的组件 RID（Resource ID）列表。
- **返回值**：
  - `dict`: 包含组件 ID 和对应数据的字典。

### 函数名：`genParaDict`
- **功能**：从 CloudPSS 平台获取指定项目的所有组件的参数和引脚信息，并生成相应的字典。
- **参数**：
  - `zdmToken` (`str`): CloudPSS 平台的认证 Token。
  - `internalapiurl` (`str`): CloudPSS 内部 API 的 URL。
  - `projName` (`str`): CloudPSS 项目的名称或键。
- **返回值**：
  - `tuple`: 包含两个字典，第一个是参数字典 (`ParaDict`)，第二个是引脚字典 (`PinDict`)。

### 函数名：`merge_and_deduplicate`
- **功能**：合并现有内容和新内容，并对新内容中的行进行去重，确保新添加的行是独一无二的。
- **参数**：
  - `existing_content_str` (`str`): 已经存在的内容字符串。
  - `new_content_str` (`str`): 新添加的内容字符串。
  - `current_index` (`int`): 当前内容的行号计数器。
- **返回值**：
  - `tuple`: 包含合并并去重后的内容字符串 (`str`) 和更新后的行号计数器 (`int`)。
```