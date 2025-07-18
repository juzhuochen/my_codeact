"""使用示例：集成jupyter_client的CodeAct"""

from langchain_ollama import ChatOllama
from my_codeact.core.state import create_initial_state
from my_codeact.core.subgraph import CodeActAgent, create_codeact_agent

# 示例1：展示详细执行过程
def example_detailed_output():
    """展示详细的代码执行过程"""
    model = ChatOllama(model="mistral:7b")
    
    with CodeActAgent(model=model, use_jupyter=True) as agent:
        # 测试包含多种输出的代码
        task = """
        请执行以下任务，展示完整的执行过程:
        1. 创建一个随机的整数数字列表，大小为99个元素
        2. 计算列表的数字和以及最大最小值
        3. 输出结果
        """
        
        initial_state = create_initial_state(
            messages=[{"role": "user", "content": task}]
        )
        
        print("=== 开始执行任务 ===")
        result = agent.invoke(initial_state)
        print(result)
        print("\n=== 任务完成 ===")


# 示例2：展示不同类型的输出
def example_different_outputs():
    """展示不同类型的输出效果"""
    model = ChatOllama(model="mistral:7b")
    
    test_cases = [
        {
            "name": "纯计算(返回值)",
            "task": "计算 2**10 的值"
        },
        {
            "name": "print输出",
            "task": "使用print输出九九乘法表的前3行"
        },
        {
            "name": "混合输出",
            "task": "创建一个列表，打印它，然后返回它的长度"
        },
        {
            "name": "可视化输出",
            "task": "创建一个简单的matplotlib图表"
        }
    ]
    
    with CodeActAgent(model=model, use_jupyter=True, max_iterations=2) as agent:
        for case in test_cases:
            print(f"\n{'='*50}")
            print(f"测试: {case['name']}")
            print(f"{'='*50}")
            
            initial_state = create_initial_state(
                messages=[{"role": "user", "content": case['task']}]
            )
            
            try:
                result = agent.invoke(initial_state)
                
                # 只打印最后的助手回复和执行结果
                for msg in result["messages"]:
                    if msg["role"] == "assistant":
                        print(f"\n🤖 助手回复:\n{msg['content']}")
                    elif "执行完成" in msg["content"]:
                        print(f"\n📋 执行结果:\n{msg['content']}")
                        
            except Exception as e:
                print(f"❌ 执行失败: {e}")


if __name__ == "__main__":
    print("=== 详细执行过程示例 ===")
    example_detailed_output()
    
    #print("\n=== 不同输出类型示例 ===") 
   # example_different_outputs()
    exit()


# 示例2：使用上下文管理器（推荐用于生产环境）
def example_context_manager():
    """使用上下文管理器的示例"""
    model = ChatOllama(model="mistral:7b")
    
    # 使用上下文管理器确保资源清理
    with CodeActAgent(
        model=model,
        use_jupyter=True,
        kernel_name='python3',
        timeout=30,
        max_iterations=10
    ) as agent:
        
        # 测试多个任务
        tasks = [
            "创建一个包含1到10的列表",
            "计算这个列表的平均值",
            "使用matplotlib画一个简单的图表"
        ]
        
        for task in tasks:
            print(f"\n执行任务: {task}")
            
            initial_state = create_initial_state(
                messages=[{"role": "user", "content": task}]
            )
            
            try:
                result = agent.invoke(initial_state)
                print("结果:", result["messages"][-1]["content"])
            except Exception as e:
                print(f"任务失败: {e}")


# 示例3：测试魔法命令
def example_magic_commands():
    """测试jupyter魔法命令"""
    model = ChatOllama(model="mistral:7b")
    
    with CodeActAgent(model=model, use_jupyter=True) as agent:
        # 测试bash命令
        bash_task = "使用bash命令查看当前目录的文件列表"
        initial_state = create_initial_state(
            messages=[{"role": "user", "content": bash_task}]
        )
        
        result = agent.invoke(initial_state)
        print("Bash命令结果:", result["messages"][-1]["content"])


# 示例4：比较jupyter和简单执行器
def example_comparison():
    """比较jupyter执行器和简单执行器"""
    model = ChatOllama(model="mistral:7b")
    
    test_code = """
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    result = np.sum(arr)
    print(f"数组和: {result}")
    """
    
    initial_state = create_initial_state(
        messages=[{"role": "user", "content": f"执行以下代码:\n{test_code}"}]
    )
    
    print("=== 使用Jupyter执行器 ===")
    with CodeActAgent(model=model, use_jupyter=True) as jupyter_agent:
        try:
            result = jupyter_agent.invoke(initial_state)
            print("成功:", result["messages"][-1]["content"])
        except Exception as e:
            print("失败:", e)
    
    print("\n=== 使用简单执行器 ===")
    simple_agent = create_codeact_agent(model=model, use_jupyter=False)
    try:
        result = simple_agent.invoke(initial_state)
        print("成功:", result["messages"][-1]["content"])
    except Exception as e:
        print("失败:", e)


# 示例5：错误处理和重试
def example_error_handling():
    """测试错误处理和重试机制"""
    model = ChatOllama(model="mistral:7b")
    
    with CodeActAgent(model=model, use_jupyter=True) as agent:
        # 故意制造一个错误
        error_task = "执行这个有错误的代码: print(undefined_variable)"
        initial_state = create_initial_state(
            messages=[{"role": "user", "content": error_task}]
        )
        
        result = agent.invoke(initial_state)
        print("错误处理结果:", result["messages"][-1]["content"])


if __name__ == "__main__":
    # 运行示例
    print("=== 简单使用示例 ===")
    example_detailed_output()
    pass
    print("\n=== 上下文管理器示例 ===")
    example_context_manager()
    
    print("\n=== 魔法命令示例 ===")
    example_magic_commands()
    
    print("\n=== 比较示例 ===")
    example_comparison()
    
    print("\n=== 错误处理示例 ===")
    example_error_handling()