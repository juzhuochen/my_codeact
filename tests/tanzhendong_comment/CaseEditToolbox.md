# CaseEditToolbox.py 脚本说明

## 模块说明
`CaseEditToolbox.py` 脚本提供了一套用于与 CloudPSS 平台交互的工具集，旨在简化电力系统仿真案例的编辑、管理和运行。它封装了对 CloudPSS 模型、组件、算例配置、作业运行以及结果处理等多个方面的操作，使得用户可以通过 Python 脚本高效地自动化仿真流程。模块内部还包含了图形化界面的文件选择功能、网络拓扑分析及绘制功能。

## 类清单
- `CaseEditToolbox`: 该脚本的核心类，提供了管理 CloudPSS 仿真项目、模型编辑、作业配置、仿真运行及结果处理等一系列高级功能。

## 模块级函数清单
- `is_number`: 判断输入参数是否可以转换为数字。

## 类与方法详细说明

### 类名：`CaseEditToolbox`
- **功能**：管理 CloudPSS 仿真项目，包括模型加载、组件操作、作业配置、仿真运行、结果可视化及项目保存等。
- **方法**：
  #### 方法：`__init__`
  - **功能**：初始化 `CaseEditToolbox` 类的实例。设置默认配置参数，并调用 `initJobConfig` 方法初始化作业配置。
  - **参数**：无
  - **返回值**：无

  #### 方法：`initJobConfig`
  - **功能**：初始化不同类型（EMTP、PowerFlow、EMTS）仿真作业的默认参数和配置。
  - **参数**：无
  - **返回值**：无

  #### 方法：`createJob`
  - **功能**：创建新的仿真作业（EMTP、PowerFlow 或 EMTS），并将其添加到当前项目中。
  - **参数**：
    - `stype` (`str`): 作业类型，可选 `'emtp'`、`'powerFlow'` 或 `'emtps'`。
    - `name` (`str`, optional): 作业的名称。默认为 `None`。
    - `args` (`dict`, optional): 需要更新的作业参数字典。默认为 `None`。
  - **返回值**：无

  #### 方法：`createConfig`
  - **功能**：创建新的项目配置，并将其添加到当前项目中。
  - **参数**：
    - `name` (`str`, optional): 配置的名称。默认为 `None`。
    - `args` (`dict`, optional): 需要更新的配置参数字典。默认为 `None`。
    - `pins` (`dict`, optional): 需要更新的引脚参数字典。默认为 `None`。
  - **返回值**：无

  #### 方法：`addOutputs`
  - **功能**：向指定的 EMTP 或 EMTS 计算方案中添加输出通道。
  - **参数**：
    - `jobName` (`str`): 需要添加输出通道的作业名称。
    - `channels` (`list`): 包含输出通道信息的列表，格式为 `[输出图像名称, 输出频率, 输出图像类型, 图像宽度, 输出通道key]`。
  - **返回值**：
    - `int`: 新增输出通道的索引。

  #### 方法：`runProject`
  - **功能**：运行项目仿真，直到仿真结束。仿真结果保存在 `self.runner.result` 中。
  - **参数**：
    - `jobName` (`str`): 要运行的作业名称。
    - `configName` (`str`): 要使用的配置名称。
    - `showLogs` (`bool`, optional): 是否在控制台显示实时日志。默认为 `False`。
    - `plotRun` (`int`, optional): 实时绘图通道的索引，如果小于 0 则不实时绘图。默认为 `-1`。
    - `apiUrl` (`str`, optional): CloudPSS API 的 URL。默认为 `None`，使用默认配置。
    - `websocketErrorTime` (`int`, optional): WebSocker 报错后重新运行仿真前的等待时间（仅对 EMTP 有效）。默认为 `None`。
    - `sleepTime` (`int`, optional): 轮询仿真状态的间隔时间（秒）。默认为 `10`。
  - **返回值**：
    - `int`: Runner 的最终状态码。

  #### 方法：`getRunnerLogs`
  - **功能**：获取当前 `runner` 的所有日志信息。
  - **参数**：无
  - **返回值**：
    - `list`: 包含日志条目的列表。

  #### 方法：`saveResult`
  - **功能**：将仿真结果数据保存到文件中。
  - **参数**：
    - `filePath` (`str`, optional): 保存结果的文件路径。默认为 `None`。
    - `fileName` (`str`, optional): 保存结果的文件名。如果为 `None`，则默认为 `'Temp.cjob'`。
  - **返回值**：无

  #### 方法：`live_plot`
  - **功能**：实时绘制仿真数据。主要用于 Jupyter Notebook 环境，显示动态图。
  - **参数**：
    - `data_dict` (`dict`): 包含绘图数据的字典，键为曲线标签，值为包含 'x' 和 'y' 列表的字典。
    - `figsize` (`tuple`, optional): 图片的尺寸。默认为 `(7, 5)`。
    - `title` (`str`, optional): 图片的标题。默认为 `''`。
  - **返回值**：无

  #### 方法：`plotResult`
  - **功能**：绘制 EMTP 仿真结果的图表。支持 Matplotlib 和 Plotly 两种绘图工具。
  - **参数**：
    - `result` (`Result` or `str`, optional): 仿真结果对象或结果 ID。如果为 `None`，则使用 `self.runner.result`。
    - `k` (`int`, optional): 要绘制的坐标系索引。如果为 `None`，则默认为 `0`。
  - **返回值**：无

  #### 方法：`displayPFResult`
  - **功能**：显示潮流计算的表格结果（母线和支路数据）。
  - **参数**：
    - `k` (`int`, optional): 要显示的表格类型。`0` 表示母线结果，`1` 表示支路结果。如果为 `None`，则显示所有（母线和支路）结果。
  - **返回值**：无

  #### 方法：`initCanvasPos`
  - **功能**：初始化指定画布的组件布局坐标。
  - **参数**：
    - `canvas` (`str`): 画布的键值。
  - **返回值**：无

  #### 方法：`getRevision`
  - **功能**：获取当前项目修订版本的 JSON 格式数据。
  - **参数**：
    - `file` (`str`, optional): 如果指定，则将修订版本数据保存到该文件中。默认为 `None`。
  - **返回值**：
    - `dict`: 当前项目修订版本的 JSON 数据。

  #### 方法：`loadRevision`
  - **功能**：从 JSON 数据或文件加载修订版本到当前项目。
  - **参数**：
    - `revision` (`dict`, optional): JSON 格式的修订版本数据。与 `file` 参数二选一。
    - `file` (`str`, optional): 包含修订版本 JSON 数据的文件路径。与 `revision` 参数二选一。
  - **返回值**：无

  #### 方法：`setConfig`
  - **功能**：配置 `CaseEditToolbox` 模块的连接参数和模型信息。
  - **参数**：
    - `token` (`str`, optional): CloudPSS 平台的 API token。
    - `apiURL` (`str`, optional): CloudPSS API 的 URL 域名。
    - `username` (`str`, optional): CloudPSS 用户名。
    - `model` (`str`, optional): 目标模型的名称。
    - `comLibName` (`str`, optional): 组件库文件名称。
  - **返回值**：无

  #### 方法：`setInitialConditions`
  - **功能**：在完成 `setConfig` 后手动调用，用于初始化 CloudPSS 连接、加载模型和组件库，并根据配置执行拓扑处理。
  - **参数**：无
  - **返回值**：无

  #### 方法：`refreshTopology`
  - **功能**：刷新并获取当前模型的拓扑信息。
  - **参数**：无
  - **返回值**：无

  #### 方法：`getEdgeTopoPinNum`
  - **功能**：获取给定边组件的拓扑引脚号。
  - **参数**：
    - `cid` (`str`): 组件的唯一 ID (key)。
  - **返回值**：
    - `str`: 拓扑引脚号，或 `'0'` (如果未找到或发生问题)。

  #### 方法：`deleteEdges`
  - **功能**：删除当前项目中的边组件（形状为 `diagram-edge`），并根据拓扑信息设置连接引脚的名称。
  - **参数**：无
  - **返回值**：无

  #### 方法：`generateNetwork`
  - **功能**：根据模型的拓扑信息生成 `igraph` 网络图，并设置顶点属性。
  - **参数**：
    - `centerRID` (`list`, optional): 优先作为中心节点的组件 RID 列表。默认为 `['model/CloudPSS/_newBus_3p']`。
  - **返回值**：无

  #### 方法：`getNetworkNeighbor`
  - **功能**：从生成的网络图中获取指定节点的 N 层邻居子图。
  - **参数**：
    - `vid` (`str`): 目标节点的 ID 或标签。
    - `nn` (`int`): 查询的邻居层数。
    - `chooseRIDList` (`list`, optional): 过滤结果，只保留 RID 在此列表中的节点。默认为 `[]`。
    - `network` (`igraph.Graph`, optional): 要操作的网络图。如果为 `None`，则使用 `self.g`。
  - **返回值**：
    - `igraph.Graph`: 包含目标节点及其指定层数邻居的子图。

  #### 方法：`plotNetwork`
  - **功能**：使用 Plotly 绘制生成的网络图。
  - **参数**：
    - `a` (`igraph.Graph`): 要绘制的 igraph 图对象。
    - `showlabel` (`bool`, optional): 是否显示节点的标签。默认为 `False`。
    - `show` (`bool`, optional): 是否立即显示图表。默认为 `True`。
  - **返回值**：
    - `plotly.graph_objects.Figure`: 生成的 Plotly 图形对象。

  #### 方法：`setCompLabelDict`
  - **功能**：生成一个字典，以组件的 `label` 作为键，值为包含与该 `label` 对应的组件 `key` 和组件对象的字典。
  - **参数**：无
  - **返回值**：无

  #### 方法：`setChannelPinDict`
  - **功能**：生成一个字典，以输出通道的引脚号作为键，值为对应的通道组件 `key`。
  - **参数**：无
  - **返回值**：无

  #### 方法：`addComp`
  - **功能**：向项目中添加一个新的组件。
  - **参数**：
    - `compJson` (`dict`): 组件的 JSON 数据（通常从组件库中获取）。
    - `id1` (`str`, optional): 新组件的唯一 ID (key)。如果为 `None`，则使用 `compJson` 中的 `id`。
    - `canvas` (`str`, optional): 组件所属的画布。如果为 `None`，则使用 `compJson` 中的 `canvas`。
    - `position` (`dict`, optional): 组件在画布上的位置，格式如 `{'x':12, 'y':49}`。如果为 `None`，则使用 `compJson` 中的 `position`。
    - `args` (`dict`, optional): 需要更新的组件参数。默认为 `None`。
    - `pins` (`dict`, optional): 需要更新的组件引脚。默认为 `None`。
    - `label` (`str`, optional): 新组件的标签。如果为 `None`，则使用 `compJson` 中的 `label`。
  - **返回值**：无

  #### 方法：`addxPos`
  - **功能**：更新画布上组件的 x 轴坐标，并处理换行逻辑。
  - **参数**：
    - `canvas` (`str`): 画布的键值。
    - `compJson` (`dict`): 组件的 JSON 数据（包含 `size` 信息）。
    - `MaxX` (`int`, optional): 最大横坐标。当 x 坐标超过此值时，将触发换行。默认为 `None`。
  - **返回值**：无

  #### 方法：`newLinePos`
  - **功能**：在指定画布中强制换行，重置 x 坐标并增加 y 坐标。
  - **参数**：
    - `canvas` (`str`): 画布的键值。
  - **返回值**：无

  #### 方法：`addCompInCanvas`
  - **功能**：在指定画布中新增元件，并根据规则自动添加 key 和标签后缀，同时更新坐标位置。
  - **参数**：
    - `compJson` (`dict`): 组件的 JSON 数据。
    - `key` (`str`): 组件的 ID 前缀。
    - `canvas` (`str`): 组件所属的画布。
    - `addN` (`bool`, optional): 是否自动为组件 ID 添加序列号后缀。默认为 `True`。
    - `addN_label` (`bool`, optional): 是否自动为组件标签添加序列号后缀。默认为 `False`。
    - `args` (`dict`, optional): 需要更新的组件参数。默认为 `None`。
    - `pins` (`dict`, optional): 需要更新的组件引脚。默认为 `None`。
    - `label` (`str`, optional): 新组件的标签。如果为 `None`，则使用生成的 ID 作为标签。
    - `dX` (`int`, optional): 在当前 x 坐标上额外增加的偏移量。默认为 `10`。
    - `MaxX` (`int`, optional): 最大横坐标。当 x 坐标超过此值时，将触发换行。默认为 `None`。
  - **返回值**：
    - `tuple`: 一个元组，包含生成的新组件 ID 和标签。

  #### 方法：`createCanvas`
  - **功能**：在项目中新增一个画布（图纸）。
  - **参数**：
    - `canvas` (`str`): 新画布的键值。
    - `name` (`str`): 新画布的显示名称。
  - **返回值**：无

  #### 方法：`screenCompByArg`
  - **功能**：根据指定组件类型和参数条件筛选项目中的组件。
  - **参数**：
    - `compRID` (`str`): 要筛选的组件的 RID (如 `'model/CloudPSS/_newShuntLC_3p'`)。
    - `conditions` (`list` or `dict`): 筛选条件列表。每个条件为字典，包含 `'arg'` (参数名或 `'label'`), `'Min'` (最小值), `'Max'` (最大值), `'Set'` (允许的值集合)。
    - `compList` (`list`, optional): 如果不为空，则只在此列表中的组件键中进行筛选。默认为 `None`。
  - **返回值**：
    - `dict`: 筛选后符合条件的组件字典，键为组件 ID，值为组件对象。

  #### 方法：`saveProject`
  - **功能**：保存当前项目到 CloudPSS 平台。
  - **参数**：
    - `newID` (`str`): 新项目的 ID (key)。
    - `name` (`str`, optional): 新项目的显示名称。默认为 `None`。
    - `desc` (`str`, optional): 新项目的描述。默认为 `None`。
  - **返回值**：
    - `dict`: 保存操作的结果信息。

  #### 方法：`getCompLib`
  - **功能**：从 CloudPSS 平台获取指定源项目中的组件，并将其保存为本地 JSON 格式的组件库文件。
  - **参数**：
    - `tk` (`str`): CloudPSS 平台的 API token。
    - `apiURL` (`str`): CloudPSS API 的 URL。
    - `spr` (`str`): 源项目的 ID (key)。
    - `compDefLib` (`dict`, optional): 组件定义库，用于映射 RID 到更友好的组件名。默认为空字典，将使用默认定义。
    - `name` (`str`, optional): 保存组件库的文件名。如果为 `None`，则默认为 `'saSource.json'`。
  - **返回值**：
    - `dict`: 构建的组件库字典。

  #### 方法：`fetchCompData`
  - **功能**：根据组件 RID 从 CloudPSS 平台获取组件的详细数据（包括参数、引脚、文档等）。
  - **参数**：
    - `rids` (`list`): 需要获取数据的组件 RID 列表。
  - **返回值**：
    - `dict`: 包含每个组件详细数据的字典，键为组件 RID。

  #### 方法：`genParaDict`
  - **功能**：生成项目的参数字典和引脚字典，包含所有组件的参数和引脚的详细元数据。
  - **参数**：
    - `zdmToken` (`str`): CloudPSS 平台的 API token。
    - `internalapiurl` (`str`): CloudPSS 内部 API 的 URL。
    - `projName` (`str`): 项目的名称或 ID (key)。
  - **返回值**：
    - `tuple`: 包含两个字典的元组。第一个是参数字典 (`ParaDict`)，第二个是引脚字典 (`PinDict`)。

## 模块级函数说明

### 函数名：`is_number`
- **功能**：判断给定的字符串是否可以转换为数字（浮点数或Unicode数字）。
- **参数**：
  - `s` (`str`): 要判断的字符串。
- **返回值**：
  - `bool`: 如果字符串可以转换为数字，则返回 `True`；否则返回 `False`。
