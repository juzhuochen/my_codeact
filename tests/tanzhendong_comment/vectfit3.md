# vectfit3.py 脚本说明

## 模块说明
`vectfit3.py` 模块实现了一种快速松弛向量拟合（Fast Relaxed Vector Fitting）算法，用于将频域响应函数 `f(s)` 近似为状态空间模型 `f(s) = C*(s*I-A)^(-1)*B + D + s*E`。该模块主要包含一个核心函数 `vectfit3` 和两个辅助函数 `ss2pr` 和 `tri2full`。`vectfit3` 函数能够处理单元素或向量化的频域响应，并支持不同的渐近项处理、极点稳定性控制以及复杂的或实数的状态空间模型输出。辅助函数则用于在状态空间模型和极点-残差模型之间进行转换，以及将矩阵下三角部分的拟合结果扩展到完整的矩阵模型。

**注意：此代码限制用于非商业用途。**

## 类清单
该脚本未定义任何类。

## 模块级函数清单
- `vectfit3`: 快速松弛向量拟合算法的核心实现。
- `ss2pr`: 将状态空间模型转换为极点-残差模型。
- `tri2full`: 将拟合矩阵下三角部分的有理模型转换为完整矩阵的状态空间模型。

## 类与方法详细说明
该脚本未定义任何类，因此没有类与方法的详细说明。

## 模块级函数说明

### 函数名：`vectfit3`
- **功能**：通过快速松弛向量拟合算法，将频域响应函数 `f(s)` 近似为状态空间模型 `f(s) = C*(s*I-A)^(-1)*B + D + s*E`。该函数执行极点识别和残差识别，并提供了多种可选配置来控制拟合过程，包括极点稳定性、渐近项处理和绘图选项。
- **参数**：
  - `f` (`numpy.ndarray`): 待拟合的频率响应函数（或向量），维度为 `(Nc, Ns)`，其中 `Nc` 是向量元素的数量，`Ns` 是频率样本的数量。
  - `s` (`numpy.ndarray`): 频率点向量 `[rad/sec]`，维度为 `(Ns)`。
  - `poles` (`numpy.ndarray`): 初始极点向量 `[rad/sec]`，维度为 `(N)`。
  - `weight` (`numpy.ndarray`): 用于加权系统矩阵行的数组。可用于在期望的频率样本处获得更高精度。如果不需要加权，可使用 `np.ones((1,Ns))`。维度可以是 `(1, Ns)`（所有向量元素通用加权）或 `(Nc, Ns)`（向量元素独立加权）。
  - `opts` (`dict`, optional): 包含拟合选项的字典。默认为 `None`。
    - `opts['relax']` (`bool`): `True` 使用松弛非平凡性约束；`False` 使用“标准”向量拟合的非平凡性约束。
    - `opts['stable']` (`bool`): `True` 不稳定极点保持不变；`False` 不稳定极点通过“翻转”到左半平面使其稳定。
    - `opts['asymp']` (`int`): 0: 拟合时 `D=0`, `E=0`；1: 拟合时 `D!=0`, `E=0`；2: 拟合时 `D!=0`, `E~=0`。
    - `opts['skip_pole']` (`bool`): `True` 跳过极点识别部分，即使用初始极点识别 `(C,D,E)`；`False` 不跳过。
    - `opts['skip_res']` (`bool`): `True` 跳过残差识别部分，即只识别极点 `(A)`，`C,D,E` 返回零；`False` 不跳过。
    - `opts['cmplx_ss']` (`bool`): `True` 返回的状态空间模型具有实数和复共轭参数（`A` 是对角的）；`False` 返回的状态空间模型只具有实数参数（`A` 是带有2x2块的方阵）。
    - `opts['spy1']` (`bool`): `True` 在极点识别后绘制幅度函数。
    - `opts['spy2']` (`bool`): `True` 在残差识别后绘制幅度函数和相位角。
    - `opts['logx']` (`bool`): `True` 绘图时使用对数 x 轴。
    - `opts['logy']` (`bool`): `True` 绘图时使用对数 y 轴。
    - `opts['errplot']` (`bool`): `True` 在幅度图中包含偏差。
    - `opts['phaseplot']` (`bool`): `True` 同时显示相位角图。
    - `opts['legend']` (`bool`): `True` 在图表中包含图例。
    - `opts['block']` (`bool`): `True` 绘图时阻塞程序执行（必须关闭图表才能继续）。
- **返回值**：
  - `dict`: `SER` 字典，包含状态空间模型参数：
    - `SER['A']` (`numpy.ndarray`): `A` 矩阵 (`N,N`)。如果 `opts['cmplx_ss']==True`，则为对角复数；否则为带有2x2块的实数方阵。
    - `SER['B']` (`numpy.ndarray`): `B` 矩阵 (`N`)。如果 `opts['cmplx_ss']==True`，则为全1列向量；否则包含0、1、2。
    - `SER['C']` (`numpy.ndarray`): `C` 矩阵 (`Nc,N`)。如果 `opts['cmplx_ss']==True`，则为复数；否则为实数。
    - `SER['D']` (`numpy.ndarray`): 常数项 (`Nc`)。如果 `opts['asymp']==1` 或 `2` 则不为 `None`。
    - `SER['E']` (`numpy.ndarray`): 比例项 (`Nc`)。如果 `opts['asymp']==2` 则不为 `None`。
  - `numpy.ndarray`: `poles` 新的极点向量 (`N`)。
  - `float`: `rmserr` `f(s)` 近似值的均方根误差。如果 `opts['skip_res']==True` 则返回0。
  - `numpy.ndarray`: `fit` 在采样点处的有理近似结果 (`Nc,Ns`)。如果 `opts['skip_res']==True` 则返回 `None`。

### 函数名：`ss2pr`
- **功能**：将具有公共极点集的状态空间模型转换为极点-残差模型。
- **参数**：
  - `SER` (`dict`): 状态空间模型，必须是 `vectfit3` 函数的输出格式。`options['cmplx_ss']` 参数确定的两种格式都有效。也可接受 `tri2full` 的输出（此时 `tri` 需设为 `True`）。
  - `tri` (`bool`): `False` 表示假设输入来自 `vectfit3` (向量值)；`True` 表示假设输入来自 `tri2full` (矩阵值)。
- **返回值**：
  - `numpy.ndarray`: `R` 残差。如果 `tri=False`，维度为 `(Nc,N)`；如果 `tri=True`，维度为 `(Nc,Nc,N)`。
  - `numpy.ndarray`: `a` 极点 (`N`)。
  - `numpy.ndarray` or `None`: `D` 常数项。如果 `SER['D']==None` 则为 `None`。
  - `numpy.ndarray` or `None`: `E` 线性项。如果 `SER['E']==None` 则为 `None`。

### 函数名：`tri2full`
- **功能**：将表示矩阵下三角部分的有理模型转换为完整矩阵的状态空间模型。
- **参数**：
  - `SER` (`dict`): `vectfit3` 拟合方阵下三角部分时的输出结构，需使用公共极点集。`options['cmplx_ss']` 参数确定的两种格式都有效。
- **返回值**：
  - `dict`: `SER` 字典，包含完整矩阵的状态空间模型参数（带有公共极点集）：
    - `SER['A']` (`numpy.ndarray`): 扩展后的 `A` 矩阵。
    - `SER['B']` (`numpy.ndarray`): 扩展后的 `B` 矩阵。
    - `SER['C']` (`numpy.ndarray`): 扩展后的 `C` 矩阵。
    - `SER['D']` (`numpy.ndarray`): 扩展后的 `D` 矩阵。
    - `SER['E']` (`numpy.ndarray`): 扩展后的 `E` 矩阵。