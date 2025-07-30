#comment: 导入 os 模块，用于操作系统相关功能
import os, sys

#comment: 将父目录添加到系统路径中，以便导入同级或上级目录的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
#comment: 导入 cloudpss 库，用于与 CloudPSS 平台交互
import cloudpss
#comment: 导入 time 模块，用于时间相关操作，例如 sleep
import time
#comment: 导入 threading 模块，用于多线程编程
import threading
#comment: 定义 fetch 函数，用于获取特定作业的信息
def fetch(id,**kwargs):
    #comment: 定义 GraphQL 查询字符串，用于获取作业的输出和上下文
    query = '''query ($input:JobInput!){
        job(input:$input){
            output
            context
        }
    }'''
    #comment: 定义 GraphQL 查询的变量，包含作业 ID
    variables = {
        'input': {
            "id":id
            
        }
    }
    #comment: 调用 cloudpss.utils.graphql_request 发送 GraphQL 请求
    r = cloudpss.utils.graphql_request(query, variables)
    #comment: 检查 GraphQL 响应中是否存在错误，如果存在则抛出异常
    if 'errors' in r:
        raise Exception(r['errors'])
    #comment: 从响应中提取作业数据
    job = r['data']['job']
    #comment: 初始化 cloudpss.Runner 对象，用于管理作业状态和监听事件
    #comment: id: 作业的唯一标识符
    #comment: job['output']: 作业的输出数据
    #comment: '': 空字符串，此处可能为预留参数或不常用参数
    #comment: {"rid":job['context'][0].replace('function/CloudPSS/','job-definition/cloudpss/')}: 构造一个包含 'rid' 的字典，其中 'rid' 是从作业上下文转换而来，用于指定Runner的资源ID
    #comment: {}, {}, {}: 空字典，可能用于传递其他配置或参数
    #comment: **kwargs: 传递额外的关键字参数给 Runner 构造函数
    runner = cloudpss.Runner(id,job['output'], '', {"rid":job['context'][0].replace(
                                    'function/CloudPSS/','job-definition/cloudpss/')}, {}, '', {},
                    {}, **kwargs)

    #comment: 创建一个 threading.Event 对象，用于线程间的通信（在此函数中未使用事件的wait/set功能）
    event = threading.Event()
    #comment: 创建一个后台线程，目标函数是 runner 的私有方法 _Runner__listen，用于监听作业状态更新
    thread = threading.Thread(target=runner._Runner__listen, kwargs=kwargs)
    #comment: 将线程设置为守护线程，主程序退出时自动终止此线程
    thread.setDaemon(True)
    #comment: 启动监听线程
    thread.start()

    #comment: 循环等待，直到监听线程的状态变为正常（即开始监听）
    while not runner._Runner__listenStatus():
        #comment: 每隔 0.1 秒检查一次
        time.sleep(0.1)
    #comment:pass 语句，表示此处没有其他操作，等待循环结束
    pass
    #comment: 返回初始化好的 Runner 对象
    return runner

#comment: 定义 fetchAllJob 函数，用于获取所有作业的信息
def fetchAllJob(status=None,limit=10,**kwargs):
    #comment: 定义 GraphQL 查询字符串，用于获取作业列表
    query = '''
    query ($input: JobsInput!) {
        jobs(input: $input) {
            items {
                id
                status
                context
            }
            count
            total
            cursor
        }
    }
    '''
    #comment: 初始化 status 变量
    s=None
    #comment: 如果提供了 status 参数，则将其格式化为 GraphQL 查询所需的 "or" 数组形式
    if status is not None:
        s= ["or",status]
    #comment: 定义 GraphQL 查询的变量，包含排序、游标、限制和状态过滤条件
    variables = {
        "input": {
            "orderBy": [
                "createTime<" #comment: 按创建时间降序排列
            ],
            "cursor": [], #comment: 游标，用于分页
            "limit": limit, #comment: 限制返回的作业数量
            "status": s #comment: 状态过滤条件
        }
    }
    #comment: 调用 cloudpss.utils.graphql_request 发送 GraphQL 请求
    r = cloudpss.utils.graphql_request(query, variables)
    #comment: 检查 GraphQL 响应中是否存在错误，如果存在则抛出异常
    if 'errors' in r:
        raise Exception(r['errors'])
    #comment: 返回作业列表
    return r['data']['jobs']['items']
    
#comment: 定义 abort 函数，用于中止指定 ID 的作业
def abort(id: str):
    #comment: 定义 GraphQL mutation 字符串，用于中止作业
    query='''
        mutation ($input: AbortJobInput!){
            abortJob(input: $input) {
                id
            }
        }
    '''    
    
    #comment: 定义 GraphQL mutation 的变量，包含作业 ID 和超时时间
    variables = {
    "input": {
        "id": id, #comment: 要中止的作业 ID
        "timeout": 10 #comment: 超时时间，单位秒
        }
    }
    #comment: 调用 cloudpss.utils.graphql_request 发送 GraphQL mutation 请求
    r = cloudpss.utils.graphql_request(query, variables)
    #comment: 返回请求的响应
    return r