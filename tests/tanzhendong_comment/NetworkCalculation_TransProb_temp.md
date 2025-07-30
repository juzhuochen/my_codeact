# "NetworkCalculation_TransProb_temp.py"脚本说明

## 模块说明
该Python脚本主要用于电力系统网络计算中的阻抗和导纳矩阵分析，特别是针对复杂的电力系统组件（如输电线路、变压器、发电机、负载等）进行建模和计算。它集成了矢量拟合（Vector Fitting）技术，用于系统频率响应的近似和模型降阶。此外，脚本还包含了用于特征值/特征向量计算的牛顿-拉夫逊和Levenberg-Marquardt迭代方法。它利用了`cloudpss`和`CaseEditToolbox`库与CloudPSS平台交互，读取项目配置和组件信息。

## 类清单
- `CaseEditToolbox` (从外部库导入)
- `PSAToolbox` (从外部库导入)

## 模块级函数清单
- `loadConfigFile`
- `CalY_Comp`
- `CalY_All`
- `CalZ_All`
- `NRstep`
- `LMstep`
- `NRstep_Large`
- `eigenMat_NR`
- `plotFitting`
- `vectorfit_Z`
- `mor_single`

## 类与方法详细说明
### 类名：`CaseEditToolbox`
- **功能**：用于编辑CloudPSS平台上的案例，包括加载配置、初始化条件、创建画布以及获取项目组件等。
- **方法**：
  #### 方法：`setConfig`
  - **功能**：设置CloudPSS案例编辑器的配置信息。
  - **参数**：
    - `token` (`str`): 用于认证的API Token。
    - `apiURL` (`str`): CloudPSS API 的 URL。
    - `username` (`str`): CloudPSS 用户名。
    - `projectKey` (`str`): CloudPSS 项目的唯一标识符。
    - `comLibName` (`str`, optional): 组件库文件名，默认为'saSource.json'。
  - **返回值**：
    - `None`
  #### 方法：`setInitialConditions`
  - **功能**：初始化案例的各项条件。
  - **参数**：
    - 无
  - **返回值**：
    - `None`
  #### 方法：`createSACanvas`
  - **功能**：创建案例的SA（状态分析）画布。
  - **参数**：
    - 无
  - **返回值**：
    - `None`
  #### 方法：`getComponentsByRid`
  - **功能**：根据资源ID（rid）获取项目中相应类型的所有组件。
  - **参数**：
    - `rid` (`str`): 组件的资源ID。
  - **返回值**：
    - `list`: 符合指定rid的组件列表。
  #### 方法：`getComponentByKey`
  - **功能**：根据唯一键（key）获取项目中的特定组件。
  - **参数**：
    - `key` (`str`): 组件的唯一键。
  - **返回值**：
    - `object`: 对应的组件对象。

### 类名：`PSAToolbox`
- **功能**：提供电力系统分析相关的工具和功能。
- **方法**：
  （此脚本中未直接展示`PSAToolbox`的自有方法调用，其功能主要通过对象实例化和外部引用表示。）

## 模块级函数说明
### 函数名：`loadConfigFile`
- **功能**：加载CloudPSS项目的配置文件，并初始化 `CaseEditToolbox` 实例。它会读取 `saSource.json` 文件以获取组件库信息，并设置项目的基础配置。
- **参数**：
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例。
  - `opts` (`dict`): 包含配置选项的字典，如 `token`, `apiURL`, `username`, `projectKey`。
- **返回值**：
  - `None`

### 函数名：`CalY_Comp`
- **功能**：计算单个电力系统组件在给定频率下的导纳矩阵。支持的组件类型包括输电线路、两绕组和三绕组变压器、三相指数负载、同步发电机、戴维南等效电源、并联电容/电抗器以及与风机相关的网关。
- **参数**：
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例，用于获取组件信息。
  - `key` (`str`): 组件的唯一标识符。
  - `freq` (`float`): 当前计算的频率 (Hz)。
  - `opts` (`dict`): 包含额外选项的字典，如`BusList`（母线列表）和`PMSG_FDNE_Z`（风机模型数据）。
- **返回值**：
  - `tuple`:
    - `numpy.ndarray` (`complex`): 计算出的组件导纳矩阵。
    - `list`: 连接的母线索引列表，如果组件没有连接到母线，则为 `None`。

### 函数名：`CalY_All`
- **功能**：计算整个电力系统在给定频率下的节点导纳矩阵。它遍历拓扑图中的所有组件，并调用 `CalY_Comp` 计算其贡献。
- **参数**：
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例。
  - `freq` (`float`): 当前计算的频率 (Hz)。
  - `opts` (`dict`): 包含额外选项的字典，如`BusList`。
- **返回值**：
  - `numpy.ndarray` (`complex`): 整个系统的节点导纳矩阵。

### 函数名：`CalZ_All`
- **功能**：计算整个电力系统在给定频率下的节点阻抗矩阵。它首先调用 `CalY_All` 获取导纳矩阵，然后求逆得到阻抗矩阵。如果 `opts` 中指定了 `SelectBuses`，则返回子系统的阻抗/导纳矩阵。
- **参数**：
  - `ce` (`CaseEditToolbox`): `CaseEditToolbox` 的实例。
  - `freq` (`float`): 当前计算的频率 (Hz)。
  - `opts` (`dict`): 包含额外选项的字典，如 `BusList` 和 `SelectBuses`（需要选择的母线列表）。
- **返回值**：
  - `tuple`:
    - `numpy.ndarray` (`complex`): 整个系统或所选子系统的节点阻抗矩阵。
    - `numpy.ndarray` (`complex`): 整个系统或所选子系统的节点导纳矩阵。

### 函数名：`NRstep`
- **功能**：实现牛顿-拉夫逊（Newton-Raphson）方法，用于单个特征值和特征向量的迭代更新。它计算残差F和雅可比矩阵J，然后求解线性方程组以更新变量。
- **参数**：
  - `x` (`numpy.ndarray` (`complex`)): 当前迭代的变量向量，包含特征向量和特征值。
  - `target` (`numpy.ndarray` (`complex`)): 目标矩阵，用于特征值问题 `(target - lambda*I) * t = 0`。
- **返回值**：
  - `tuple`:
    - `numpy.ndarray` (`complex`): 下一步迭代的变量向量。
    - `numpy.ndarray` (`complex`): 更新后的残差向量。

### 函数名：`LMstep`
- **功能**：实现Levenberg-Marquardt（LM）方法，用于单个特征值和特征向量的迭代更新。它基于牛顿-拉夫逊方法，并引入了一个阻尼参数`sigma`以提高收敛性。
- **参数**：
  - `x` (`numpy.ndarray` (`complex`)): 当前迭代的变量向量，包含特征向量和特征值。
  - `target` (`numpy.ndarray` (`complex`)): 目标矩阵。
  - `sigma` (`float`): LM 方法的阻尼参数。
- **返回值**：
  - `tuple`:
    - `numpy.ndarray` (`complex`): 下一步迭代的变量向量。
    - `numpy.ndarray` (`complex`): 更新后的残差向量。

### 函数名：`NRstep_Large`
- **功能**：实现用于处理多个特征值和特征向量的牛顿-拉夫逊迭代步骤。它将所有特征向量元素和特征值组合成一个大型变量向量进行求解。
- **参数**：
  - `target` (`numpy.ndarray` (`complex`)): 目标矩阵。
  - `eig0` (`numpy.ndarray` (`complex`)): 初始的特征值向量。
  - `Ti0` (`numpy.ndarray` (`complex`)): 初始的特征向量矩阵。
- **返回值**：
  - `tuple`:
    - `numpy.ndarray` (`complex`): 更新后的特征值向量。
    - `numpy.ndarray` (`complex`): 更新后的特征向量矩阵。
    - `float`: 残差的L2范数，用于判断收敛。

### 函数名：`eigenMat_NR`
- **功能**：使用牛顿-拉夫逊或Levenberg-Marquardt方法迭代计算给定矩阵的特征值和特征向量，直到收敛或达到最大迭代次数。
- **参数**：
  - `target` (`numpy.ndarray` (`complex`)): 目标矩阵。
  - `eig0` (`numpy.ndarray` (`complex`)): 初始的特征值向量。
  - `Ti0` (`numpy.ndarray` (`complex`)): 初始的特征向量矩阵。
  - `opts` (`dict`): 包含迭代选项的字典，如`EigMaxIter`（最大迭代次数）和`EigEps`（收敛误差）。
- **返回值**：
  - `tuple`:
    - `numpy.ndarray` (`complex`): 计算出的特征值向量。
    - `numpy.ndarray` (`complex`): 计算出的特征向量矩阵。
    - `float`: 特征分解的误差。

### 函数名：`plotFitting`
- **功能**：绘制矢量拟合结果，包括幅频特性和相频特性。支持对数坐标轴、图例、误差曲线和程序阻塞。
- **参数**：
  - `s` (`numpy.ndarray` (`complex`)): 复频率向量。
  - `f` (`numpy.ndarray` (`complex`)): 原始数据（幅值和相位）。
  - `fit` (`numpy.ndarray` (`complex`)): 拟合结果数据。
  - `options` (`dict`): 绘图选项，如`errplot`（是否绘制误差）、`logx`（x轴是否对数）、`logy`（y轴是否对数）、`legend`（是否显示图例）、`phaseplot`（是否绘制相位图）、`block`（是否阻塞程序）。
- **返回值**：
  - `None`

### 函数名：`vectorfit_Z`
- **功能**：使用矢量拟合（Vector Fitting）算法对阻抗或导纳数据进行频率响应拟合。它将矩阵数据展平为向量，并使用`vectfit3`函数进行迭代拟合，最终提取出状态空间模型参数（A, B, C, D, E）或部分分数形式的残差和极点。
- **参数：
  - `res` (`dict`): 包含输入数据的字典，如`Z`（阻抗矩阵列表）、`lmd`（特征值列表）、`Freq`（频率向量）、`weightFreq`（频率权重）、`Nc`（矩阵列数）、`Ns`（采样点数）。
  - `eps` (`float`): 拟合过程中的一个误差阈值。
  - `opts0` (`dict`): 包含矢量拟合选项的字典，如`NiterYc1`（第一阶段迭代次数）、`NiterYc2`（第二阶段迭代次数）、`NpYc`（极点数量）、`ViewYcVF`（是否可视化）、`vfopts`（传递给`vectfit3`的选项）。
  - `Type` (`str`, optional): 拟合数据的类型，可以是'Z'（阻抗）或'H'（导纳）。默认为'Z'。
- **返回值**：
  - `dict`: 更新后的`res`字典，包含拟合结果（如残差`RYc`、极点`PYc`、常数项`CYc`、频率项`EYc`、拟合数据`fitYc`、均方根误差`RMSErrYc`等）。

### 函数名：`mor_single`
- **功能**：用于SISO（单输入单输出）系统的模型降阶或残差计算。它根据给定的极点和渐近项类型，构建基函数和线性方程组，并通过最小二乘法求解残差。
- **参数**：
  - `poles` (`numpy.ndarray` (`complex`)): 系统的极点。
  - `asymp` (`int`): 渐近项数量 (0: 无D/E项, 1: 仅D项, 2: D和E项)。
  - `delay` (`numpy.ndarray` (`float`)): 延迟项，为每个极点提供。
  - `s` (`numpy.ndarray` (`complex`)): 复频率向量。
  - `f` (`numpy.ndarray` (`complex`)): 要拟合的响应数据。
  - `weight` (`numpy.ndarray` (`float`)): 频率权重。
  - `eps` (`float`): 奇异值分解中的截断误差阈值。
- **返回值**：
  - `tuple`:
    - `dict`: 包含状态空间模型参数（`A`, `C`, `D`, `E`）的`SER`对象。
    - `numpy.ndarray` (`complex`): 新的（可能减少的）极点列表。
    - `float`: 拟合的均方根误差（RMSErr）。
    - `numpy.ndarray` (`complex`): 拟合后的频率响应数据。