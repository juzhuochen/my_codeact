# StabilityAnalysis.py 脚本说明

## 模块说明

`StabilityAnalysis.py` 脚本是一个用于 CloudPSS 平台进行电力系统稳定分析的 Python 类库。它封装了与 CloudPSS 平台交互的常用功能，包括模型的加载、参数的配置、仿真任务的创建与运行、仿真结果的可视化和保存等。该模块提供了基础的案例分析功能 `CaseAnalysis`，以及在此基础上针对稳定性分析扩展的 `StabilityAnalysis` 和 `S_S_SyncComp` 类，用于处理故障设置、N-1/N-2 故障分析、电压敏感度计算和同步补偿器建模等高级功能。此外，脚本还包含了一些辅助函数，用于获取组件库信息和组件参数/引脚数据。

## 类清单

- **`CaseAnalysis`**: 基础案例分析类，提供与 CloudPSS 模型、仿真作业和配置交互的核心功能，如增删改查模型元件、运行仿真、保存结果等。
- **`StabilityAnalysis`**: 继承自 `CaseAnalysis`，扩展了电力系统稳定性分析相关的特定功能，如设置接地故障、N-1/N-2 故障、添加测量通道等。
- **`S_S_SyncComp`**: 继承自 `StabilityAnalysis`，专注于同步补偿器（Sync Compensator）相关的分析，包括电压敏感度指标（VSI）计算和同步补偿器建模等。

## 模块级函数清单

- `is_number(s)`
- `getCompLib(tk, apiURL, spr, compDefLib={}, name=None)`
- `fetchCompData(rids=None)`
- `genParaDict(zdmToken, internalapiurl, projName)`

## 类与方法详细说明

### 类名: `CaseAnalysis`
- **功能**：基础案例分析类，提供与 CloudPSS 模型、仿真作业和配置交互的核心功能。它允许用户加载、创建和修改模型，定义和运行仿真方案（EMTP 和潮流），以及处理和保存仿真结果。
- **方法**：
  #### 方法：`__init__`
  - **功能**：类构造函数，初始化配置字典、项目对象、组件库、组件计数、位置信息以及通道引脚字典。并调用 `initJobConfig` 初始化作业配置。
  - **参数**：无
  - **返回值**：无

  #### 方法：`initJobConfig`
  - **功能**：初始化 EMTP 和潮流计算的默认作业配置，以及项目参数方案的初始设置。
  - **参数**：无
  - **返回值**：无

  #### 方法：`createJob`
  - **功能**：根据指定类型（'emtp' 或 'powerFlow'）创建新的仿真作业方案，并可自定义名称和参数。
  - **参数**：
    - `stype` (`str`): 作业类型，'emtp' 或 'powerFlow'。
    - `name` (`str`, optional): 计算方案名称。默认为 `None`。
    - `args` (`dict`, optional): 需要更新的参数字典。默认为 `None`。
  - **返回值**：无

  #### 方法：`createConfig`
  - **功能**：创建新的项目参数方案，并可自定义名称、参数和引脚。
  - **参数**：
    - `name` (`str`, optional): 参数方案名称。默认为 `None`。
    - `args` (`dict`, optional): 需要更新的参数字典。默认为 `None`。
    - `pins` (`dict`, optional): 需要更新的引脚字典。默认为 `None`。
  - **返回值**：无

  #### 方法：`addOutputs`
  - **功能**：向指定的 EMTP 计算方案中增加输出通道配置。
  - **参数**：
    - `jobName` (`str`): EMTP 计算方案的名称。
    - `channels` (`list`): 输出通道配置，格式为 `[输出图像名称, 输出频率, 输出图像类型, 图像宽度, 输出通道key]`。
  - **返回值**：
    - `int`: 新增输出通道的索引。

  #### 方法：`runProject`
  - **功能**：运行指定的仿真项目，直到仿真结束。仿真结果将保存在 `self.runner.result` 中。该方法支持重试机制和日志显示，并能处理 websocket 连接错误。
  - **参数**：
    - `jobName` (`str`): 要运行的作业（仿真方案）名称。
    - `configName` (`str`): 要使用的配置（参数方案）名称。
    - `showLogs` (`bool`, optional): 是否在控制台显示仿真日志。默认为 `False`。
    - `apiUrl` (`str`, optional): CloudPSS API 的 URL。默认为 `None` (使用默认配置)。
    - `websocketErrorTime` (`float`, optional): 当 websocket 出错时，如果当前仿真时间远小于此值，则尝试重新运行。默认为 `None`。
  - **返回值**：
    - `int`: 运行器的最终状态码。

  #### 方法：`getRunnerLogs`
  - **功能**：获取当前运行器的日志。
  - **参数**：无
  - **返回值**：
    - `list`: 运行器日志的列表。

  #### 方法：`saveResult`
  - **功能**：将仿真结果保存到指定的文件中。
  - **参数**：
    - `filePath` (`str`, optional): 文件保存路径。默认为 `None`。
    - `fileName` (`str`, optional): 结果文件名。如果为 `None`，则默认为 'Temp.cjob'。
  - **返回值**：无

  #### 方法：`plotResult`
  - **功能**：绘制 EMTP 仿真结果，生成 Plotly 交互式图表。
  - **参数**：
    - `result` (`cloudpss.runner.result.Result`, optional): 仿真结果对象。如果为 `None`，则使用 `self.runner.result`。
    - `k` (`int`, optional): 要绘制的输出通道组的索引。默认为 `None` (绘制第一个组)。
  - **返回值**：无

  #### 方法：`displayPFResult`
  - **功能**：以表格形式显示潮流计算结果（母线数据和支路数据）。
  - **参数**：
    - `k` (`int`, optional): 显示的表格类型。`0` 表示母线结果，`1` 表示支路结果。如果为 `None`，则显示所有结果。
  - **返回值**：无 (直接通过 IPython.display 显示 HTML 表格)。

  #### 方法：`initCanvasPos`
  - **功能**：初始化指定画布上元件的布局坐标系统。
  - **参数**：
    - `canvas` (`str`): 画布的键名。
  - **返回值**：无

  #### 方法：`getRevision`
  - **功能**：获取当前项目的修订版本（JSON 格式）。
  - **参数**：
    - `file` (`str`, optional): 如果提供，将修订版本写入指定文件。默认为 `None`。
  - **返回值**：
    - `dict`: 当前项目的修订版本 JSON 数据。

  #### 方法：`loadRevision`
  - **功能**：从 JSON 数据或文件中加载项目的修订版本。
  - **参数**：
    - `revision` (`dict`, optional): 要加载的修订版本 JSON 数据。两个参数 `revision` 和 `file` 选其一即可。
    - `file` (`str`, optional): 要读取的修订版本文件名。
  - **返回值**：无

  #### 方法：`setConfig`
  - **功能**：配置 CloudPSS 模块的连接参数，如 token、API URL、用户名、模型名称和组件库文件名。
  - **参数**：
    - `token` (`str`, optional): CloudPSS 平台访问令牌。默认为 `None`。
    - `apiURL` (`str`, optional): CloudPSS API 的域名。默认为 `None`。
    - `username` (`str`, optional): CloudPSS 用户名。默认为 `None`。
    - `model` (`str`, optional): CloudPSS 算例名称（不带 `/model/username`）。默认为 `None`。
    - `comLibName` (`str`, optional): 组件库文件名。默认为 `None` (使用默认值 `saSource.json`)。
  - **返回值**：无

  #### 方法：`setInitialConditions`
  - **功能**：在完成 `setConfig` 后手动调用，用于初始化 CloudPSS 模块。它设置 CloudPSS 令牌和 API URL，获取模型项目，并加载组件库和初始化内部字典。
  - **参数**：无
  - **返回值**：无

  #### 方法：`setCompLabelDict`
  - **功能**：从项目中元件的标签生成指向元件的字典，方便通过标签查找元件。
  - **参数**：无
  - **返回值**：无

  #### 方法：`setChannelPinDict`
  - **功能**：从输出通道的引脚（pin）生成指向通道元件 key 的字典。
  - **参数**：无
  - **返回值**：无

  #### 方法：`addComp`
  - **功能**：向项目的修订版本中添加新的元件。
  - **参数**：
    - `compJson` (`dict`): 元件的 JSON 数据。
    - `id1` (`str`, optional): 元件的 key。如果为 `None`，则使用 `compJson` 中的 ID。
    - `canvas` (`str`, optional): 元件所属的画布 key。如果为 `None`，则使用 `compJson` 中的画布。
    - `position` (`dict`, optional): 元件在画布中的位置，如 `{'x':12,'y':49}`。如果为 `None`，则使用 `compJson` 中的位置。
    - `args` (`dict`, optional): 需要更新的元件参数字典。默认为 `None`。
    - `pins` (`dict`, optional): 需要更新的元件引脚字典。默认为 `None`。
    - `label` (`str`, optional): 新增元件的标签。默认为 `None`。
  - **返回值**：无

  #### 方法：`addxPos`
  - **功能**：更新当前画布的 x 坐标，并根据 `MaxX` 参数实现自动换行。
  - **参数**：
    - `canvas` (`str`): 画布的键名。
    - `compJson` (`dict`): 元件的 JSON 数据 (用于获取元件宽度和高度)。
    - `MaxX` (`float`, optional): 最大横坐标。当 x 坐标超过此值时，将触发换行。默认为 `None`。
  - **返回值**：无

  #### 方法：`newLinePos`
  - **功能**：在指定的画布中进行换行操作，将 x 坐标重置并增加 y 坐标。
  - **参数**：
    - `canvas` (`str`): 画布的键名。
  - **返回值**：无

  #### 方法：`addCompInCanvas`
  - **功能**：在指定的画布中新增元件，包括添加元件、为元件 key 及标签增添后缀（可选）、更新坐标位置的功能。
  - **参数**：
    - `compJson` (`dict`): 元件的 JSON 数据。
    - `key` (`str`): 元件的基础 key。
    - `canvas` (`str`): 元件所属的画布 key。
    - `addN` (`bool`, optional): 是否自动为元件 key 和标签添加后缀 `_n`。默认为 `True`。
    - `args` (`dict`, optional): 需要更新的元件参数字典。默认为 `None`。
    - `pins` (`dict`, optional): 需要更新的元件引脚字典。默认为 `None`。
    - `label` (`str`, optional): 新增元件的标签。如果 `None`，将根据 key 自动生成。
    - `dX` (`float`, optional): 在元件 x 坐标后额外增加的距离，用于控制元件间距。默认为 `10`。
    - `MaxX` (`float`, optional): 最大横坐标，用于控制换行。一般可取 500。默认为 `None`。
  - **返回值**：
    - `tuple`: 包含生成的元件 ID (`str`) 和标签 (`str`)。

  #### 方法：`createCanvas`
  - **功能**：新增一个图纸（画布）到项目中，并初始化其坐标布局。
  - **参数**：
    - `canvas` (`str`): 新画布的键名。
    - `name` (`str`): 新画布的显示名称。
  - **返回值**：无

  #### 方法：`screenCompByArg`
  - **功能**：通过参数值筛选指定 RID 的元件。
  - **参数**：
    - `compRID` (`str`): 元件的 RID，如 `'model/CloudPSS/_newShuntLC_3p'`。
    - `conditions` (`list` or `dict`): 筛选条件列表。
      每个条件字典包含：
      - `'arg'` (`str`): 要筛选的参数名。
      - `'Min'` (`float`/`str`/`None`): 参数值的最小值。
      - `'Max'` (`float`/`str`/`None`): 参数值的最大值。
      - `'Set'` (`list`/`None`): 参数值必须包含在其中的集合。
    - `compList` (`list`, optional): 如果不为空，则仅从该列表中提供的元件 key 中进行筛选。默认为 `None`。
  - **返回值**：
    - `dict`: 筛选后的元件字典，key 为元件 key，value 为元件对象。

  #### 方法：`saveProject`
  - **功能**：保存当前的仿真算例（项目）到 CloudPSS 平台。
  - **参数**：
    - `newID` (`str`): 新的项目 ID。
    - `name` (`str`, optional): 项目的名称。默认为 `None`。
    - `desc` (`str`, optional): 项目的描述。默认为 `None`。
  - **返回值**：
    - `str`: 保存成功后的项目 RID。

### 类名: `StabilityAnalysis`
- **功能**：继承自 `CaseAnalysis`，扩展了电力系统稳定性分析相关的特定功能。它允许用户设置各种类型的故障（如接地故障、N-1/N-2 故障等），并添加定制的测量输出通道。
- **方法**：
  #### 方法：`__init__`
  - **功能**：构造函数，调用父类 `CaseAnalysis` 的构造函数，并定义稳定性分析相关的画布 ID 和常用组件名称映射。
  - **参数**：无
  - **返回值**：无

  #### 方法：`createSACanvas`
  - **功能**：创建稳定性分析所需的画布，包括故障设置画布和额外输出通道画布，并初始化接地点元件。
  - **参数**：无
  - **返回值**：无

  #### 方法：`setGroundFault`
  - **功能**：在指定引脚设置三相接地故障。
  - **参数**：
    - `pinName` (`str`): 要设置故障的引脚名称。
    - `fault_start_time` (`float`): 故障开始时间。
    - `fault_end_time` (`float`): 故障结束时间。
    - `fault_type` (`str`): 故障类型（例如 '三相短路接地'）。
    - `OtherParas` (`dict`, optional): 其他需要更新的故障参数。默认为 `None`。
  - **返回值**：
    - `tuple`: 包含新添加的接地故障组件的 ID (`str`) 和标签 (`str`)。

  #### 方法：`setBreaker_3p`
  - **功能**：在两个母线之间设置三相断路器。
  - **参数**：
    - `busName1` (`str`): 第一个母线的引脚名称。
    - `busName2` (`str`): 第二个母线的引脚名称。
    - `ctrlSigName` (`str`, optional): 断路器的控制信号名称。默认为 `None`。
    - `OtherParas` (`dict`, optional): 其他需要更新的断路器参数。默认为 `None`。
  - **返回值**：
    - `tuple`: 包含新添加的三相断路器组件的 ID (`str`) 和标签 (`str`)。

  #### 方法：`setN_1`
  - **功能**：模拟 N-1 故障，通过在传输线（或变压器）两侧添加断路器并控制其切除时间，实现切除一条线路的效果。
  - **参数**：
    - `transKey` (`str`): 要切除的传输线（或变压器）的组件 Key。
    - `cut_time` (`float`): 线路切除的时间。
    - `OtherBreakerParas` (`dict`, optional): 其他需要更新的断路器参数。默认为 `None`。
  - **返回值**：无

  #### 方法：`setCutFault`
  - **功能**：模拟切除一个元件的故障，通过在该元件的引脚处设置断路器并控制其切除时间。
  - **参数**：
    - `compKey` (`str`): 要切除的元件的组件 Key。
    - `cut_time` (`float`): 元件切除的时间。
    - `OtherBreakerParas` (`dict`, optional): 其他需要更新的断路器参数。默认为 `None`。
  - **返回值**：无

  #### 方法：`setN_1_GroundFault`
  - **功能**：模拟 N-1 接地故障，即切除一条线路并在其一侧设置接地故障。
  - **参数**：
    - `transKey` (`str`): 要切除的传输线组件 Key。
    - `side` (`int`): 在传输线的哪一侧设置接地故障（`0` 或 `1`）。
    - `fault_start_time` (`float`): 故障开始时间。
    - `cut_time` (`float`): 线路切除时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherFaultParas` (`dict`, optional): 其他需要更新的接地故障参数。默认为 `None`。
    - `OtherBreakerParas` (`dict`, optional): 其他需要更新的断路器参数。默认为 `None`。
  - **返回值**：无

  #### 方法：`setN_2_GroundFault`
  - **功能**：模拟 N-2 接地故障，即切除两条线路并在其中一条线路的一侧设置接地故障。
  - **参数**：
    - `transKey1` (`str`): 第一条要切除的传输线组件 Key。
    - `transKey2` (`str`): 第二条要切除的传输线组件 Key。
    - `side` (`int`): 在第一条传输线的哪一侧设置接地故障（`0` 或 `1`）。
    - `fault_start_time` (`float`): 故障开始时间。
    - `cut_time` (`float`): 线路切除时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherFaultParas` (`dict`, optional): 其他需要更新的接地故障参数。默认为 `None`。
    - `OtherBreakerParas` (`dict`, optional): 其他需要更新的断路器参数。默认为 `None`。
  - **返回值**：无

  #### 方法：`setN_k_GroundFault`
  - **功能**：模拟 N-k 接地故障，即切除多条线路并在其中第一条线路的一侧设置接地故障。
  - **参数**：
    - `transKeys` (`list`): 包含所有要切除的传输线组件 Key 的列表。
    - `side` (`int`): 在 `transKeys` 中第一条传输线的哪一侧设置接地故障（`0` 或 `1`）。
    - `fault_start_time` (`float`): 故障开始时间。
    - `cut_time` (`float`): 线路切除时间。
    - `fault_type` (`str`): 故障类型。
    - `OtherFaultParas` (`dict`, optional): 其他需要更新的接地故障参数。默认为 `None`。
    - `OtherBreakerParas` (`dict`, optional): 其他需要更新的断路器参数。默认为 `None`。
  - **返回值**：无

  #### 方法：`addChannel`
  - **功能**：添加一个新的输出通道用于测量特定信号，如果通道已存在则更新其名称。
  - **参数**：
    - `pinName` (`str`): 要测量的信号引脚名称。
    - `dim` (`int`): 测量信号的维度（例如 `1` 代表标量，`3` 代表三相）。
    - `channelName` (`str`, optional): 输出通道的显示名称。如果为 `None`，则默认为 `pinName`。
  - **返回值**：
    - `tuple`: 包含通道的 ID (`str`) 和标签 (`str`)。

  #### 方法：`addVoltageMeasures`
  - **功能**：根据电压基准和名称筛选母线，并添加其电压量测输出通道到指定的 EMTP 作业中。
  - **参数**：
    - `jobName` (`str`): EMTP 作业的名称。
    - `VMin` (`float`, optional): 母线电压基准的最小值。默认为 `None`。
    - `VMax` (`float`, optional): 母线电压基准的最大值。默认为 `None`。
    - `NameSet` (`list`, optional): 母线名称必须包含在其中的集合。默认为 `None`。
    - `Keys` (`list`, optional): 如果不为 `None`，则只从这些母线 Key 中进行筛选。默认为 `None`。
    - `freq` (`int`, optional): 输出频率。默认为 `None` (使用默认值 `200`)。
    - `PlotName` (`str`, optional): 绘图的名称。默认为 `None` (自动生成名称)。
  - **返回值**：
    - `dict`: 筛选后的母线字典，key 为母线 key，value 为母线组件对象。

  #### 方法：`addComponentOutputMeasures`
  - **功能**：通过参数筛选元件，并为这些元件的指定输出参数添加测量通道到 EMTP 作业中。
  - **参数**：
    - `jobName` (`str`): EMTP 作业的名称。
    - `compRID` (`str`): 元件的 RID，如 `'model/CloudPSS/_newShuntLC_3p'`。
    - `measuredKey` (`str`): 要输出的参数键名。
    - `conditions` (`list` or `dict`): 筛选条件列表。与 `screenCompByArg` 中的条件格式相同。
    - `compList` (`list`, optional): 如果不为空，则仅从该列表中提供的元件 key 中进行筛选。默认为 `None`。
    - `dim` (`int`, optional): 测量信号的维度。默认为 `1`。
    - `curveName` (`str`, optional): 曲线的名称。如果为 `None`，则默认为 `measuredKey`。
    - `plotName` (`str`, optional): 绘图的名称。默认为 `None`。
    - `freq` (`int`, optional): 量测信号的输出频率。默认为 `200`。
  - **返回值**：
    - `dict`: 筛选后的元件字典，key 为元件 key，value 为元件对象。

### 类名: `S_S_SyncComp`
- **功能**：继承自 `StabilityAnalysis`，特化用于同步补偿器（Sync Compensator）相关的分析。它提供了计算电压敏感度指标（VSI）、故障严重程度指标（SI）以及在模型中添加同步补偿器等高级功能。
- **方法**：
  #### 方法：`__init__`
  - **功能**：构造函数，调用父类 `StabilityAnalysis` 的构造函数，并扩展了同步补偿器和动态无功相关的组件名称映射。
  - **参数**：无
  - **返回值**：无

  #### 方法：`createSSSCACanvas`
  - **功能**：创建同步补偿器和动态无功相关的画布，并初始化一些常用常量和信号组件。
  - **参数**：无
  - **返回值**：无

  #### 方法：`getXInterval`
  - **功能**：在有序数据 `xData` 中，查找给定值 `x` 所在区间的起始索引。
  - **参数**：
    - `xData` (`list`): 有序的 X 轴数据列表。
    - `x` (`float`): 要查找的值。
  - **返回值**：
    - `int`: 找到的区间起始索引。

  #### 方法：`calculateDV`
  - **功能**：计算电压偏差指标 (DV)，用于评估仿真结果中电压的暂态和稳态恢复性能。
  - **参数**：
    - `jobName` (`str`): 仿真作业名称。
    - `voltageMeasureK` (`int`): 电压测量在输出通道列表中的索引。
    - `result` (`cloudpss.runner.result.Result`, optional): 仿真结果对象。如果为 `None`，则使用 `self.runner.result`。
    - `Ts` (`float`, optional): 仿真开始分析的时间点。默认为 `4`。
    - `dT0` (`float`, optional): 初始电压计算的时间窗长度。默认为 `0.5`。
    - `Tinterval` (`float`, optional): 暂态分析开始相对于 `Ts` 的延迟。默认为 `0.11`。
    - `T1` (`float`, optional): 暂态分析的时间窗长度。默认为 `3`。
    - `dV1` (`float`, optional): 暂态期间电压允许偏差的百分比。默认为 `0.25`。
    - `dV2` (`float`, optional): 稳态期间电压允许偏差的百分比。默认为 `0.1`。
    - `VminR` (`float`, optional): 稳态恢复最低电压与初始电压的比值。默认为 `0.2`。
    - `VmaxR` (`float`, optional): 稳态恢复最高电压与初始电压的比值。默认为 `1.8`。
  - **返回值**：
    - `tuple`: 包含电压上限偏差列表 (`dVUj`), 电压下限偏差列表 (`dVLj`), 和有效数据点索引列表 (`ValidNum`)。

  #### 方法：`calculateSI`
  - **功能**：计算故障严重程度指标 (SI)，用于量化仿真过程中电压偏离正常范围的程度。
  - **参数**：
    - `jobName` (`str`): 仿真作业名称。
    - `voltageMeasureK` (`int`): 电压测量在输出通道列表中的索引。
    - `result` (`cloudpss.runner.result.Result`, optional): 仿真结果对象。如果为 `None`，则使用 `self.runner.result`。
    - `Ts` (`float`, optional): 仿真开始分析的时间点。默认为 `4`。
    - `dT0` (`float`, optional): 初始电压计算的时间窗长度。默认为 `0.5`。
    - `Tinterval` (`float`, optional): 暂态分析开始相对于 `Ts` 的延迟。默认为 `0.11`。
    - `T1` (`float`, optional): 暂态分析的时间窗长度。默认为 `3`。
    - `dV1` (`float`, optional): 暂态期间电压允许偏差的百分比。默认为 `0.25`。
    - `dV2` (`float`, optional): 稳态期间电压允许偏差的百分比。默认为 `0.1`。
    - `VminR` (`float`, optional): 稳态恢复最低电压与初始电压的比值。默认为 `0.2`。
    - `VmaxR` (`float`, optional): 稳态恢复最高电压与初始电压的比值。默认为 `1.8`。
  - **返回值**：
    - `tuple`: 包含故障严重程度指标 (`SI`, `float`) 和有效数据点索引列表 (`ValidNum`)。

  #### 方法：`calculateVSI`
  - **功能**：计算电压敏感度指标 (VSI)，用于评估母线电压对动态无功注入的敏感程度。
  - **参数**：
    - `jobName` (`str`): 仿真作业名称。
    - `voltageMeasureK` (`int`): 电压测量在输出通道列表中的索引。
    - `dQMeasureK` (`int`): 动态无功测量在输出通道列表中的索引。
    - `result` (`cloudpss.runner.result.Result`, optional): 仿真结果对象。如果为 `None`，则使用 `self.runner.result`。
    - `busNum` (`int`, optional): 要分析的母线数量。如果为 `None`，则根据仿真时间自动计算。默认为 `None`。
    - `Ts` (`float`, optional): 无功注入开始时间。默认为 `4`。
    - `dT` (`float`, optional): 对每个母线测试时所占用的仿真时长。默认为 `1`。
    - `ddT` (`float`, optional): 无功注入持续时间。默认为 `0.5`。
  - **返回值**：
    - `tuple`: 包含 VSIij (每个母线在每个时间段的电压敏感度) 和 VSIi (每个时间段的平均电压敏感度)。

  #### 方法：`addVSIMeasure`
  - **功能**：添加 VSI 相关的测量，包括电压量测和动态无功注入量测，并可在指定 Job 中添加输出通道。
  - **参数**：
    - `jobName` (`str`): 仿真 Job 名称。
    - `VMin` (`float`, optional): 用于电压量测的母线电压基准最小值。默认为 `None`。
    - `VMax` (`float`, optional): 用于电压量测的母线电压基准最大值。默认为 `None`。
    - `NameSet` (`list`, optional): 用于电压量测的母线名称集合。默认为 `None`。
    - `NameKeys` (`list`, optional): 用于电压量测的母线 Key 列表。默认为 `None`。
    - `freq` (`int`, optional): 输出频率。默认为 `None` (使用默认值 `200`)。
    - `Nbus` (`int`, optional): 母线数量，用于调整 Job 的结束时间。默认为 `10`。
    - `dT` (`float`, optional): 对每个母线测试时所占用的仿真时长。默认为 `0.5`。
    - `Ts` (`float`, optional): 无功注入开始时间。默认为 `4`。
  - **返回值**：
    - `tuple`: 包含电压测量索引 (`voltageMeasureK`), 动态无功测量索引 (`dQMeasureK`), 和筛选后的母线字典 (`screenedBus`)。

  #### 方法：`addVSIQSource`
  - **功能**：为 VSI 分析添加动态无功源，包括并联电容/电感和控制其启停的一系列开关及信号源。
  - **参数**：
    - `busKeys` (`list`): 母线 key 的列表，用于指定动态无功注入的位置。
    - `V` (`float`, optional): 动态注入无功源的基准电压（kV）。默认为 `220`。
    - `S` (`float`, optional): 动态注入无功源的基准无功（MVar）。默认为 `1`。
    - `Ts` (`float`, optional): 信号开始时间。默认为 `4`。
    - `dT` (`float`, optional): 对每个母线测试时所占用的仿真时长（s）。默认为 `1`。
    - `ddT` (`float`, optional): 动态无功注入的持续时间。默认为 `0.5`。
  - **返回值**：无

  #### 方法：`addSVC`
  - **功能**：向指定母线添加静态无功补偿器 (SVC)，包括 SVC 器件和控制其开关的断路器及信号源。
  - **参数**：
    - `busKey` (`str`): 要添加 SVC 的母线 Key。
    - `S` (`float`, optional): SVC 的额定视在功率（MVar）。默认为 `1`。
    - `Ts` (`float`, optional): SVC 投入时间。默认为 `4`。
    - `Te` (`float`, optional): SVC 切除时间。默认为 `999`。
  - **返回值**：
    - `list`: 包含添加的 SVC 相关组件 ID 的列表 `[id1, id2, ids]`。

  #### 方法：`addSyncComp`
  - **功能**：向指定母线添加同步补偿器，包括同步发电机、与其相连的母线、变压器、以及 AVR（自动电压调节器）和增益块等。
  - **参数**：
    - `busKey` (`str`): 要添加同步补偿器的母线 Key。
    - `pfResult` (`cloudpss.runner.result.PowerFlowResult`): 潮流计算结果，用于获取母线电压信息。
    - `syncArgs` (`dict`, optional): 同步发电机的参数字典，如 `{"Smva": "额定容量", "V": "额定相电压有效值", "freq": "额定频率"}`。默认为 `None`。
    - `transArgs` (`dict`, optional): 变压器的参数字典，如 `{"Smva": "额定容量", "X1": "正序漏电抗", "Rl": "正序漏电阻"}`。默认为 `None`。
    - `busArgs` (`dict`, optional): 同步补偿器内部母线的参数字典。默认为 `None`。
    - `AVRComp` (`dict`, optional): AVR 组件的 JSON 定义。如果为 `None`，则使用默认的 `_PSASP_AVR_11to12`。
    - `AVRArgs` (`dict`, optional): AVR 的参数字典。默认为 `None`。
  - **返回值**：
    - `list`: 包含添加的同步补偿器相关组件 ID 的列表 `[Syncid1, Busid1, Transid1, AVRid1, Gainid1]`。

## 模块级函数说明
### 函数名：`is_number`
- **功能**：检查给定的字符串是否可以转换为数字（浮点数或Unicode数字）。
- **参数**：
  - `s` (`str`): 要检查的字符串。
- **返回值**：
  - `bool`: 如果字符串可以转换为数字则返回 `True`，否则返回 `False`。

### 函数名：`getCompLib`
- **功能**：获取指定 CloudPSS 项目中的组件信息并构建组件库，可保存为 JSON 文件。
- **参数**：
  - `tk` (`str`): CloudPSS 访问令牌。
  - `apiURL` (`str`): CloudPSS API 的 URL。
  - `spr` (`str`): CloudPSS 项目的 RID（如 `'model/username/projectname'`）。
  - `compDefLib` (`dict`, optional): 用户自定义的组件定义映射，key 为组件名称，value 为 RID。默认为空字典，表示使用默认内置组件定义。
  - `name` (`str`, optional): 生成的组件库 JSON 文件名。如果为 `None`，则默认为 `'saSource.json'`。
- **返回值**：
  - `dict`: 包含组件信息的字典，key 为组件名称，value 为组件的 JSON 结构。

### 函数名：`fetchCompData`
- **功能**：根据给定的组件 RID 列表，批量从 CloudPSS 平台获取组件的详细数据（包括修订版本、参数、引脚等）。
- **参数**：
  - `rids` (`list`): 包含组件 RID 字符串的列表。
- **返回值**：
  - `dict`: 包含每个组件详细数据的字典，key 为组件 RID。
- **抛出**：
  - `Exception`: 如果 `rids` 为 `None` 或空。

### 函数名：`genParaDict`
- **功能**：生成指定 CloudPSS 项目中所有组件的参数字典和引脚字典，详细记录每个参数和引脚的元数据。
- **参数**：
  - `zdmToken` (`str`): CloudPSS 访问令牌。
  - `internalapiurl` (`str`): CloudPSS 内部 API 的 URL。
  - `projName` (`str`): CloudPSS 项目的 RID。
- **返回值**：
  - `tuple`: 包含参数字典 (`ParaDict`) 和引脚字典 (`PinDict`)。
    - `ParaDict` (`dict`): key 为组件 RID，value 为一个字典，其中包含 `DiscriptName` 和所有参数的元数据。
    - `PinDict` (`dict`): key 为组件 RID，value 为一个字典，其中包含所有引脚的元数据。
