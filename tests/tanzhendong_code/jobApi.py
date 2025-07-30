#comment: 导入 os 模块，用于操作系统相关功能
import os, sys

#comment: 将父目录添加到 sys.path 中，以便可以导入父目录中的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
#comment: 导入 cloudpss 库
import cloudpss
#comment: 导入 time 模块，用于时间相关操作
import time
#comment: 导入 threading 模块，用于多线程操作
import threading
#comment: 定义 fetch 函数，用于获取指定作业的输出和上下文信息
def fetch(id,**kwargs):
    #comment: 定义 GraphQL 查询字符串，用于获取作业信息
    query = '''query ($input:JobInput!){
        job(input:$input){
            output
            context
        }
    }'''
    #comment: 定义 GraphQL 查询变量
    variables = {
        'input': {
            "id":id
            
        }
    }
    #comment: 调用 cloudpss.utils.graphql_request 发送 GraphQL 请求
    r = cloudpss.utils.graphql_request(query, variables)
    #comment: 检查请求结果中是否存在错误
    if 'errors' in r:
        #comment: 如果存在错误，则抛出异常
        raise Exception(r['errors'])
    #comment: 从响应中提取作业信息
    job = r['data']['job']
    #comment: 初始化 cloudpss.Runner 对象，用于管理作业状态和实时更新
    runner = cloudpss.Runner(id,job['output'], '', {"rid":job['context'][0].replace(
                                    'function/CloudPSS/','job-definition/cloudpss/')}, {}, '', {},
                    {}, **kwargs)

    #comment: 创建一个 threading.Event 对象，用于线程间的通信（此处未使用）
    event = threading.Event()
    #comment: 创建一个新的线程，目标函数为 runner._Runner__listen，用于监听作业状态
    thread = threading.Thread(target=runner._Runner__listen, kwargs=kwargs)
    #comment: 将该线程设置为守护线程，主程序退出时该线程也会随之退出
    thread.setDaemon(True)
    #comment: 启动线程
    thread.start()

    #comment: 循环等待，直到 Runner 对象的监听状态变为 True
    while not runner._Runner__listenStatus():
        #comment: 每 0.1 秒检查一次
        time.sleep(0.1)
    #comment: pass 语句，表示什么都不做
    pass
    #comment: 返回初始化并已开始监听的 runner 对象
    return runner


#comment: 定义 fetchAllJob 函数，用于获取所有作业的列表
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
    #comment: 初始化状态变量
    s=None
    #comment: 如果提供了状态参数，则将其格式化为 GraphQL 查询所需的格式
    if status is not None:
        s= ["or",status]
    #comment: 定义 GraphQL 查询变量
    variables = {
        "input": {
            "orderBy": [
                "createTime<" #comment: 按创建时间降序排序
            ],
            "cursor": [], #comment: 游标，用于分页查询
            "limit": limit, #comment: 限制返回的作业数量
            "status": s #comment: 查询的作业状态
        }
    }
    #comment: 调用 cloudpss.utils.graphql_request 发送 GraphQL 请求
    r = cloudpss.utils.graphql_request(query, variables)
    #comment: 检查请求结果中是否存在错误
    if 'errors' in r:
        #comment: 如果存在错误，则抛出异常
        raise Exception(r['errors'])
    #comment: 返回作业列表
    return r['data']['jobs']['items']
    
    
#comment: 定义 abort 函数，用于中止指定作业
def abort(id: str):
    #comment: 定义 GraphQL mutation 字符串，用于中止作业
    query='''
        mutation ($input: AbortJobInput!){
            abortJob(input: $input) {
                id
            }
        }
    '''    
    
    #comment: 定义 GraphQL mutation 变量
    variables = {
    "input": {
        "id": id, #comment: 要中止的作业 ID
        "timeout": 10 #comment: 超时时间
        }
    }
    #comment: 调用 cloudpss.utils.graphql_request 发送 GraphQL 请求
    r = cloudpss.utils.graphql_request(query, variables)
    #comment: 返回请求结果
    return r