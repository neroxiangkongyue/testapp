from typing import Generator

def counter() -> Generator[int, str, str]:
    """一个简单的计数器生成器"""
    count = 0
    while True:
        # 接收外部发送的值，并产生当前计数值
        received = yield count
        if received == "stop":
            break  # 跳出循环
        count += 1
    return "计数结束"  # 最终返回值

# 使用示例
gen = counter()
print(type(gen))
print(next(gen))  # 输出: 0 (产生值)
print(gen.send("continue"))  # 输出: 1 (发送值并产生新值)
print(gen.send("continue"))  # 输出: 2
try:
    print(gen.send("stop"))  # 发送"stop"，触发break
except StopIteration as e:
    print(e.value)  # 输出: "计数结束" (获取最终返回值)