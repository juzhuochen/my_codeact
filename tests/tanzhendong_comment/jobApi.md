# jobApi.py 脚本说明

## 模块说明
`jobApi.py` 脚本提供了一系列与 CloudPSS 平台作业（Job）管理相关的实用工具函数。它通过 GraphQL API 与 CloudPSS 后端进行交互，实现了获取作业输出、监听作业状态、获取作业列表以及中止作业等功能，方便开发者在 Python 项目中集成 CloudPSS 的作业管理能力。

## 类清单
*   `cloudpss.Runner`: 管理作业状态和实时更新的类。虽然 `jobApi.py` 中没有定义这个类，但它在 `fetch` 函数中被实例化并使用，是作业状态监听的核心。

## 模块级函数清单
*   `fetch`
*   `fetchAllJob`
*   `abort`

## 类与方法详细说明

### 类名：`cloudpss.Runner` (外部库类，此处仅作功能说明)
- **功能**：用于管理 CloudPSS 作业的生命周期、状态监听和实时数据更新。
- **方法**：
    #### 方法：`_Runner__listen` (私有方法，通过 `fetch` 函数间接调用)
    - **功能**：在单独的线程中监听 CloudPSS 作业的实时状态和输出更新。
    - **参数**：
        - `kwargs` (`dict`): 传递给监听方法的额外关键字参数。
    - **返回值**：
        - `None`

    #### 方法：`_Runner__listenStatus` (私有方法，通过 `fetch` 函数间接调用)
    - **功能**：检查作业监听线程是否已经启动并处于监听状态。
    - **参数**：
        - 无
    - **返回值**：
        - `bool`: 如果监听已启动则返回 `True`，否则返回 `False`。

## 模块级函数说明

### 函数名：`fetch`
- **功能**：获取指定 ID 作业的输出和上下文信息，并启动一个后台线程持续监听该作业的状态更新。返回一个 `cloudpss.Runner` 对象，通过该对象可以访问作业的实时更新数据。
- **参数**：
    - `id` (`str`): 要获取和监听的作业的唯一 ID。
    - `**kwargs` (`dict`): 传递给 `cloudpss.Runner` 构造函数和其内部监听线程的额外关键字参数, 例如认证信息。
- **返回值**：
    - `cloudpss.Runner`: 初始化并已开始监听的 Runner 对象，用于访问作业的实时状态和数据。

### 函数名：`fetchAllJob`
- **功能**：获取 CloudPSS 平台上所有符合条件的作业列表。可以根据作业状态进行过滤，并限制返回的数量。
- **参数**：
    - `status` (`list[str]`, optional): 一个包含作业状态字符串的列表，例如 `["READY", "RUNNING"]`，用于过滤作业。如果为 `None`，则不按状态过滤。
    - `limit` (`int`, optional): 限制返回的作业数量，默认为 10。
    - `**kwargs` (`dict`): 传递给 `cloudpss.utils.graphql_request` 的额外关键字参数。
- **返回值**：
    - `list[dict]`: 一个包含作业信息的字典列表，每个字典包含 `id`, `status`, `context` 等键。

### 函数名：`abort`
- **功能**：中止指定 ID 的 CloudPSS 作业。
- **参数**：
    - `id` (`str`): 要中止的作业的唯一 ID。
- **返回值**：
    - `dict`: GraphQL 请求的原始响应结果，通常包含被中止作业的 ID。
