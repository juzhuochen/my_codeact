import asyncio
from jupyter_client.manager import AsyncKernelManager

async def execute_sequential_tasks():
    # 启动内核并连接客户端
    km = AsyncKernelManager(kernel_name='python3')
    await km.start_kernel()
    kc = km.client()
    kc.start_channels()

    print("开始顺序执行任务...")

    try:
        # 任务列表：每个任务是一个 Python 代码字符串
        tasks = [
            'x = 10',
            'y = x * 2',  # 依赖于上一个任务定义的 x
            'print(f"x={x}, y={y}")'
        ]

        for i, code in enumerate(tasks):
            print(f"\n任务 {i+1} 开始执行:")
            print("执行代码:", code)

            msg_id = kc.execute(code)

            while True:
                try:
                    msg = await kc.get_iopub_msg(timeout=10)
                    parent_id = msg['parent_header'].get('msg_id')

                    if parent_id != msg_id:
                        continue

                    msg_type = msg['msg_type']
                    content = msg['content']

                    if msg_type == 'status' and content['execution_state'] == 'idle':
                        print("任务完成，进入 idle 状态。")
                        break

                    elif msg_type == 'stream':
                        print("输出:", content['text'].strip())

                    elif msg_type == 'error':
                        print("发生错误:")
                        print("错误类型:", content['ename'])
                        print("错误信息:", content['evalue'])
                        print("Traceback:")
                        for line in content['traceback']:
                            print("  ", line)
                        raise RuntimeError(f"任务 {i+1} 执行失败")

                except asyncio.TimeoutError:
                    print("等待响应超时")
                    break

        print("\n所有任务执行完成")

    finally:
        kc.stop_channels()
        await km.shutdown_kernel()

# 启动异步任务
asyncio.run(execute_sequential_tasks())
print("Done.")