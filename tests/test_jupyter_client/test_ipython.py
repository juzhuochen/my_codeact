import asyncio
from jupyter_client.manager import AsyncKernelManager

async def execute_concurrent():
    """并发执行多个代码片段"""
    km = AsyncKernelManager(kernel_name='python3')
    await km.start_kernel()
    kc = km.client()
    
    # 定义多个任务（第二个任务故意写错）
    tasks = [
        'import math\nprint(f"Pi = {math.pi}")',
        'print(f"随机数: {random.randint(1, 100)}")',  # 语法错误
        'print("当前时间:", __import__("datetime").datetime.now())',
    ]
    
    async def execute_task(code, task_id):
        """执行单个任务"""
        print(f"任务 {task_id} 开始执行")
        msg_id = kc.execute(code)
        
        while True:
            try:
                msg = await kc.get_iopub_msg(timeout=5)
                msg_type = msg['msg_type']
                content = msg['content']
                parent_id = msg['parent_header'].get('msg_id')

                if parent_id != msg_id:
                    continue  # 忽略其他任务的消息

                if msg_type == 'status' and content['execution_state'] == 'idle':
                    print(f"任务 {task_id} 状态: idle（执行结束）")
                    break  # 当前执行结束

                if msg_type == 'stream':
                    print(f"任务 {task_id} 输出: {content['text'].strip()}")
                elif msg_type == 'execute_result':
                    print(f"任务 {task_id} 执行结果: {content['data']['text/plain']}")
                elif msg_type == 'error':
                    print(f"任务 {task_id} 出现错误:")
                    print("错误类型:", content['ename'])
                    print("错误信息:", content['evalue'])
                    print("Traceback:")
                    for line in content['traceback']:
                        print("  ", line)
            except asyncio.TimeoutError:
                print(f"任务 {task_id}: 超时")
                break
            except Exception as e:
                print(f"任务 {task_id} 发生异常: {e}")
                break
    
    try:
        # 并发执行所有任务
        await asyncio.gather(*[
            execute_task(code, i+1) 
            for i, code in enumerate(tasks)
        ])
    finally:
        await km.shutdown_kernel()

asyncio.run(execute_concurrent())
print("Done.")