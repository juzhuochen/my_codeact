# ImportQSData_xinan_2.py 脚本说明

## 模块说明
`ImportQSData_xinan_2.py` 脚本主要提供了与 CloudPSS 平台交互以进行电力系统仿真数据处理和分析的功能。它包含了图数据结构操作（特别是节点合并）、QS (仿真原始数据) 文件读取与解析、以及基于拓扑结构或仿真结果查找相关电力系统组件（如母线、输电线路）等核心功能。此外，脚本还集成了日志消息发送机制，方便在 CloudPSS 作业环境中进行信息输出。

## 类清单
- `CaseEditToolbox`: 从外部模块导入，用于仿真案例编辑工具箱。(本脚本无直接定义，为导入外部类)

## 模块级函数清单
- `merge`: 合并图中指定的节点。
- `mergeGraph`: 根据特定规则合并图中的节点。
- `ReadQSInfo`: 读取 QS (仿真原始数据) 文件信息。
- `findBusInStation`: 查找同一场站内具有相同电压等级的母线。
- `getNetworkNeighbor_E`: 获取网络中节点的邻居子图。
- `find_nearest`: 在数组中找到与给定值最接近的元素的索引。
- `getSameStationBuses`: 获取同一场站内所有通过 P=0, Q=0 线路连接的母线。
- `jobmessage`: 向 CloudPSS 作业发送日志消息。

## 类与方法详细说明
本脚本没有直接定义类，所有类均从外部模块导入，例如 `CaseEditToolbox`。

## 模块级函数说明

### 函数名：`merge`
- **功能**：合并图中的指定节点列表为一个新的节点，并更新相关属性和邻接关系。
- **参数**：
  - `G` (`igraph.Graph`): 待操作的图对象。
  - `nList` (`list`): 包含待合并的 `igraph.Vertex` 对象的列表。
- **返回值**：
  - `dict`: 一个字典，表示合并后的节点映射关系，键为被合并节点的原名称，值为合并后新节点的名称。

### 函数名：`mergeGraph`
- **功能**：根据特定规则（例如，低阻抗传输线）合并图中的节点，创建简化后的图结构。
- **参数**：
  - `ce` (`CaseEditToolbox`): 仿真案例编辑工具箱对象，用于获取组件信息。
  - `g` (`igraph.Graph`): 原始图对象。
- **返回值**：
  - `tuple`: 包含两个元素的元组，第一个是合并后的图 `mergedG` (`igraph.Graph`)，第二个是合并字典 `mergeDict` (`dict`)。

### 函数名：`ReadQSInfo`
- **功能**：读取指定 QS (仿真原始数据) 文件并解析其内容，根据文件类型返回结构化的信息字典。
- **参数**：
  - `qsfile` (`str`): QS 文件的路径。
  - `type` (`str`, optional): 文件类型，可选值为 'line' (输电线路), '2wT' (两绕组变压器), '3wT' (三绕组变压器), 'bus' (母线)，或其他自定义类型。默认为 `None`。
  - `encoding` (`str`, optional): 文件编码。默认为 "gb2312"。
- **返回值**：
  - `dict`: 包含文件信息的字典，键为表头（或预定义键），值为对应列的数据列表。

### 函数名：`findBusInStation`
- **功能**：查找在合并图中与给定母线 ID 属于同一场站且具有相同电压等级的所有母线。
- **参数**：
  - `ce` (`CaseEditToolbox`): 仿真案例编辑工具箱对象。
  - `mergedG` (`igraph.Graph`): 合并后的图对象。
  - `mergeDict` (`dict`): 合并字典，用于将原始节点名称映射到合并后的节点名称。
  - `busid` (`str`): 目标母线的 ID（通常是 CloudPSS 组件的键）。
- **返回值**：
  - `list`: 包含所有符合条件的母线 ID (键) 的列表。

### 函数名：`getNetworkNeighbor_E`
- **功能**：根据指定的深度和过滤条件，从网络中获取给定顶点的邻居子图，并配置子图中节点的样式。
- **参数**：
  - `ce` (`CaseEditToolbox`): 仿真案例编辑工具箱对象，用于获取网络形状配置。
  - `vid` (`str`): 起始顶点的 ID。
  - `nn` (`int`): 邻居的层数（广度优先搜索深度）。
  - `chooseRIDList` (`list`, optional): 包含允许的 `rid` (资源ID) 的列表。如果非空，则只保留这些 rid 的节点。默认为 `[]`。
  - `exceptRIDList` (`list`, optional): 包含要排除的 `rid` 的列表。
  - `network` (`igraph.Graph`, optional): 要操作的网络图。如果 `None`，则使用 `ce.g`。默认为 `None`。
- **返回值**：
  - `igraph.Graph`: 包含配置好样式的子图。

### 函数名：`find_nearest`
- **功能**：在给定数组中找到与指定值最接近的元素的索引。
- **参数**：
  - `array` (`list` or `numpy.ndarray`): 待搜索的数值数组。
  - `value` (`float` or `int`): 目标数值。
- **返回值**：
  - `int`: 最接近元素的索引。

### 函数名：`getSameStationBuses`
- **功能**：递归地查找和收集在电力系统中通过功率流为 P=0, Q=0 的支路连接的所有“同一场站”的母线。
- **参数**：
  - `BusResDict` (`dict`): 母线结果字典 (此函数未使用，可能为预留参数或历史遗留)。
  - `BranchResDict` (`dict`): 支路结果字典，键为母线名称，值为连接到该母线的支路列表，每个支路包含 'P' (有功功率), 'Q' (无功功率) 和 'Opp' (对侧母线名称) 等信息。
  - `busSet` (`set`): 用于跟踪已访问母线的集合，避免死循环和重复。
  - `name` (`str`): 当前处理的母线名称。
- **返回值**：
  - `set`: 包含所有“同一场站”母线名称的集合。

### 函数名：`jobmessage`
- **功能**：向 CloudPSS 作业发送日志消息，支持不同日志级别和 HTML 格式。
- **参数**：
  - `job` (`cloudpss.Job`): CloudPSS 作业实例对象。
  - `content` (`str`): 日志消息的内容。
  - `level` (`str`, optional): 日志级别，可选值为 `'critical'`、`'error'`、`'warning'`、`'info'`、`'verbose'`、`'debug'`。默认为 `'info'`。
  - `html` (`bool`, optional): 指示 `content` 是否为 HTML 格式。默认为 `False`。
  - `key` (`str`, optional): 消息的唯一标识符，用于更新或放置到容器中。默认为 `None`。
  - `verb` (`str`, optional): 操作动词，通常为 `'append'` 表示追加消息。默认为 `'append'`。
- **返回值**：
  - `None`