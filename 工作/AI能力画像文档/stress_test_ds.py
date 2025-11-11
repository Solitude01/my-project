import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Tuple

# --- 配置参数 ---
API_BASE_URL = "http://10.30.44.159:8000/v1"
MODEL_ID = "Qwen3-8B"
API_KEY = "0"  # 您提供的秘钥，如果接口不需要，可留空或设为None
ENDPOINT = f"{API_BASE_URL}/chat/completions"

# 测试并发数（线程数）：这是模拟同时发起请求的用户数
CONCURRENT_USERS = 10 

# 总请求次数：测试将发送的总请求量
TOTAL_REQUESTS = 50

# 测试负载：使用一个适中长度的请求，便于测试TPM
TEST_PAYLOAD = {
    "model": MODEL_ID,
    "messages": [
        {"role": "user", "content": "请用中文写一篇关于人工智能在生物医药领域应用的短文，篇幅控制在300字左右。"}
    ],
    "max_tokens": 1024,  # 允许最大输出Token数
    "temperature": 0.7,
    "stream": False
}

# --- 测试函数 ---
def call_deepseek_api(request_data: Dict[str, Any]) -> Tuple[float, int, int, str]:
    """向 DeepSeek API 发送请求并返回结果信息"""
    headers = {
        "Content-Type": "application/json",
    }
    # 仅在 API KEY 非空且不为 '0' 时添加 Authorization Header
    if API_KEY and API_KEY != '0':
        headers["Authorization"] = f"Bearer {API_KEY}"

    start_time = time.time()
    
    try:
        response = requests.post(ENDPOINT, headers=headers, json=request_data, timeout=60)
        latency = time.time() - start_time
        status_code = response.status_code
        
        # 尝试从响应头中获取 Token 使用信息 (如果接口支持)
        prompt_tokens = int(response.headers.get('X-Ratelimit-Tokens-Used', 0))
        
        # 如果是成功响应，尝试从 JSON body 中获取 token 信息
        if response.status_code == 200:
            data = response.json()
            usage = data.get('usage', {})
            # 优先使用 body 中的精确 token 数
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # 返回精确的总 Token 数
            return latency, status_code, total_tokens, "Success"

        elif response.status_code == 429:
            # 命中速率限制，返回 0 Token
            return latency, status_code, 0, "RateLimit Exceeded (429)"

        else:
            # 其他错误，返回 0 Token
            return latency, status_code, 0, f"Error: {response.text[:100]}"
            
    except requests.exceptions.RequestException as e:
        latency = time.time() - start_time
        return latency, 0, 0, f"Exception: {e}"

# --- 主执行函数 ---
def run_stress_test():
    print(f"--- DeepSeek-R1 本地部署压力测试 ---")
    print(f"目标接口: {ENDPOINT}")
    print(f"并发数: {CONCURRENT_USERS}")
    print(f"总请求数: {TOTAL_REQUESTS}")
    print("-" * 40)

    start_full_time = time.time()
    all_results = []

    # 使用线程池发起并发请求
    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        # 为每个请求提交一个任务
        futures = [executor.submit(call_deepseek_api, TEST_PAYLOAD) for _ in range(TOTAL_REQUESTS)]
        
        # 实时监控进度
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            all_results.append(result)
            if (i + 1) % 50 == 0 or (i + 1) == TOTAL_REQUESTS:
                 print(f"进度: {i + 1}/{TOTAL_REQUESTS} 完成...")
            

    total_duration = time.time() - start_full_time

    # --- 结果分析 ---
    latencies = [r[0] for r in all_results]
    total_tokens = sum(r[2] for r in all_results if r[1] == 200) # 仅计算成功的Token
    success_requests = sum(1 for r in all_results if r[1] == 200)
    rate_limit_errors = sum(1 for r in all_results if r[1] == 429)
    other_errors = TOTAL_REQUESTS - success_requests - rate_limit_errors

    # 计算指标
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    rpm = (TOTAL_REQUESTS / total_duration) * 60
    tpm = (total_tokens / total_duration) * 60

    print("\n" + "=" * 40)
    print("           压力测试报告           ")
    print("=" * 40)
    print(f"测试总耗时: {total_duration:.2f} 秒")
    print(f"成功请求数: {success_requests} ({(success_requests / TOTAL_REQUESTS) * 100:.1f}%)")
    print(f"429 错误数: {rate_limit_errors}")
    print(f"其他错误数: {other_errors}")
    print("-" * 40)
    print(f"平均响应时间: {avg_latency:.4f} 秒")
    print(f"实际 RPM (每分钟请求数): {rpm:.2f}")
    print(f"实际 TPM (每分钟令牌数): {tpm:.2f}")
    print("-" * 40)

    # 打印一些错误详情 (可选)
    print("部分错误详情:")
    for _, status, _, msg in all_results:
        if status not in [200, 429] and status != 0:
             print(f"  状态码 {status}: {msg}")
    
    # 确定瓶颈的初步建议
    if rate_limit_errors > 0:
        print("\n**初步结论：API 接口已配置硬性速率限制 (429)。**")
        print("建议：请联系管理员提高 API 限制或调整您的并发/总请求数。")
    elif rpm > 0 and success_requests < TOTAL_REQUESTS * 0.9:
        print("\n**初步结论：服务器性能或网络出现瓶颈。**")
        print("建议：检查服务器 CPU/GPU 利用率，并尝试减少并发数或负载。")
    elif rpm > 0:
        print("\n**初步结论：成功达到此并发下的稳定吞吐量。**")
        print("建议：继续增加并发数 (CONCURRENT_USERS) 和总请求数 (TOTAL_REQUESTS) 以找到真正的上限。")


if __name__ == "__main__":
    run_stress_test()