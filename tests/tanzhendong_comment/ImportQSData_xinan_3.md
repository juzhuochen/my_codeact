# ImportQSData_xinan_3.py 脚本说明

## 模块说明
`ImportQSData_xinan_3.py` 脚本是一个用于处理电力系统仿真数据（可能来自 `PSASP` 或类似系统）并将其导入到 `CloudPSS` 平台项目的工具。它通过读取特定的 `QS` (Quick Start 或 Quick Simulation) 格式文本文件来获取电力系统元件（如交流线路、串联补偿器、变压器和母线）的参数和拓扑信息。脚本的主要功能包括：

- **交流线路处理**：读取线路数据，识别和更新 `CloudPSS` 项目中现有线路的参数，或将其置为关断状态。同时，它支持根据 `UQSLine.txt` 文件内容新增线路和相应的母线。
- **串联补偿器处理**：读取串联补偿器数据，并在 `CloudPSS` 项目中新增对应的串联电容器元件。
- **变压器处理**：处理双绕组和三绕组变压器数据。它会更新 `CloudPSS` 项目中现有变压器的参数，或将其置为关断状态。同时，根据 `UQStsf.txt` 文件内容新增变压器和相应的母线，并处理三绕组变压器的中心节点信息。
- **母线处理**：读取母线数据，更新 `CloudPSS` 项目中母线的电压和相角，并处理三绕组变压器中心节点的母线信息。
- **日志记录**：将处理过程中发现的问题（如 `QS` 中有但 `PSASP` 中没有的元件、被关断的元件、新增的元件等）记录到日志文件和 `CloudPSS` 作业日志中。

该脚本依赖 `pandas`、`numpy`、`igraph`、`plotly` 等库进行数据处理、图结构操作和可视化，以及与 `CloudPSS` 平台交互的自定义库 `cloudpss` 和 `jobApi1`，以及 `CaseEditToolbox` 进行项目元件的编辑操作。

## 类清单
本脚本中没有在模块级别定义类。所有的操作都是通过导入的 `CaseEditToolbox` 类的实例方法以及模块级函数完成的。

## 模块级函数清单
- `_process_ac_lines`
- `_process_series_compensators`
- `_process_transformers`
- `_process_buses`

## 类与方法详细说明
本脚本中没有自定义类，所有使用的类都是从外部库导入的。

## 模块级函数说明

### 函数名：`_process_ac_lines`
- **功能**：处理电力系统中的交流线路数据。它会读取 `acline.txt` 和 `UQSLine.txt` 文件，根据读到的信息更新 `CloudPSS` 项目中现有交流线路的参数（如电阻、电抗、导纳、Vbase），或将其置为关断状态。同时，根据 `UQSLine.txt` 中新增线路的信息，在项目中添加新的线路和必要的母线。函数还会记录处理过程中遇到的问题和新增的元件数量。
- **参数**：
  - `job` (`cloudpss.Job`): CloudPSS作业对象，用于记录日志和消息。
  - `qspath` (`str`): QS文件的路径，包含 `acline.txt` 和 `UQSLine.txt` 等。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 实例，用于操作 CloudPSS 项目中的元件。
  - `busLabelDict` (`dict`): 母线标签字典，键是母线名称，值可能是其他相关信息。
  - `linebus_SP` (`dict`): 线路母线特殊处理映射，用于处理特定 IEEE 母线名称到 PS 母线名称的映射。
- **返回值**：
  - `tuple`:
    - `list`: 更新后的母线列表。
    - `dict`: 电压基准字典。
    - `dict`: 包含处理结果日志的 JSON 对象。
    - `str`: 最后处理的 IEEE 起始母线名称 (此返回值可能不准确，因为它是循环内的局部变量)。
    - `str`: 最后处理的 IEEE 终止母线名称 (此返回值可能不准确，因为它是循环内的局部变量)。

### 函数名：`_process_series_compensators`
- **功能**：处理电力系统中的串联补偿器数据。它会读取 `cs.txt` 文件，根据其中的信息在 `CloudPSS` 项目中新增串联电容器元件。同时，如果涉及到新的母线，也会创建对应的母线。
- **参数**：
  - `job` (`cloudpss.Job`): CloudPSS作业对象，用于记录日志。
  - `qspath` (`str`): QS文件的路径，包含 `cs.txt`。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 实例，用于操作 CloudPSS 项目中的元件。
  - `busList` (`list`): 当前的母线列表。
  - `VbaseDict` (`dict`): 电压基准字典。
- **返回值**：
  - `None`

### 函数名：`_process_transformers`
- **功能**：处理电力系统中的变压器数据，包括双绕组变压器和三绕组变压器。它会读取 `2wTsf.txt`、`3wTsf.txt` 和 `UQStsf.txt` 文件，根据读到的信息更新 `CloudPSS` 项目中现有变压器的参数（如电压基准、电阻、电抗），或将其置为关断状态。同时，根据 `UQStsf.txt` 中新增变压器（双绕组和三绕组）的信息，在项目中添加新的变压器和必要的母线，并处理三绕组变压器的中心节点信息。
- **参数**：
  - `job` (`cloudpss.Job`): CloudPSS作业对象，用于记录日志和消息。
  - `qspath` (`str`): QS文件的路径，包含 `2wTsf.txt`、`3wTsf.txt` 和 `UQStsf.txt`。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 实例，用于操作 CloudPSS 项目中的元件。
  - `busLabelDict` (`dict`): 母线标签字典，键是母线名称，值可能是其他相关信息。
  - `linebus_SP` (`dict`): 线路母线特殊处理映射，用于处理特定 IEEE 母线名称到 PS 母线名称的映射。
  - `T3WCentDict` (`dict`): 三绕组变压器中心节点字典，用于存储和更新三绕组变压器及其中心节点的关系。
  - `ieeebusi` (`str`): IEEE 起始母线名称（可能来自上一个函数的返回值，本函数中局部变量的值可能覆盖它）。
  - `ieeebusj` (`str`): IEEE 终止母线名称（可能来自上一个函数的返回值，本函数中局部变量的值可能覆盖它）。
- **返回值**：
  - `dict`: 更新后的三绕组变压器中心节点字典。

### 函数名：`_process_buses`
- **功能**：处理电力系统中的母线数据。它会读取 `bus.txt` 文件，并根据其中的信息更新 `CloudPSS` 项目中母线的电压标幺值和相角。同时，它还会检查母线在 `QS` 和 `PS` 中是否存在差异，并处理三绕组变压器中心节点对应的母线信息。
- **参数**：
  - `job` (`cloudpss.Job`): CloudPSS作业对象，用于记录日志。
  - `qspath` (`str`): QS文件的路径，包含 `bus.txt`。
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 实例，用于操作 CloudPSS 项目中的元件。
  - `T3WCentDict` (`dict`): 三绕组变压器中心节点字典，用于关联三绕组变压器和其对应的中心母线。
- **返回值**：
  - `None`