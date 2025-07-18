#!/usr/bin/env python3
"""
Gemini API 测试脚本
用于验证 Gemini API 的各个端点功能
"""

import requests
import json
import time
from typing import Dict, Any, List
import sys

class GeminiAPITester:
    def __init__(self, base_url: str = "http://192.168.3.7:8000", api_key: str = "sk-145253"):
        """
        初始化API测试器
        
        Args:
            base_url: API服务器的基础URL
            api_key: 可选的API密钥，用于认证
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # 支持两种认证方式
        if api_key:
            # 方式1: 使用x-goog-api-key请求头
            self.headers["x-goog-api-key"] = api_key
            # 方式2: 使用Authorization Bearer (备用)
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def test_list_models(self) -> Dict[str, Any]:
        """测试获取模型列表"""
        print("=" * 50)
        print("测试获取模型列表")
        print("=" * 50)
        
        # 测试两个端点
        endpoints = [
            "/gemini/v1beta/models",
            "/v1beta/models"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"\n测试端点: {endpoint}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ 成功获取模型列表")
                    print(f"模型数量: {len(data.get('models', []))}")
                    
                    # 显示前几个模型
                    models = data.get('models', [])
                    for i, model in enumerate(models[:3]):
                        print(f"  {i+1}. {model.get('name', 'N/A')} - {model.get('displayName', 'N/A')}")
                    
                    if len(models) > 3:
                        print(f"  ... 还有 {len(models) - 3} 个模型")
                    
                    return data
                else:
                    print(f"❌ 请求失败: {response.text}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
        
        return {}
    
    def test_generate_content(self, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """测试内容生成"""
        print("\n" + "=" * 50)
        print("测试内容生成")
        print("=" * 50)
        
        # 构建请求数据
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "你好，请简单介绍一下你自己。"
                        }
                    ]
                }
            ],
            "generation_config": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1000
            }
        }
        
        endpoints = [
            f"/gemini/v1beta/models/{model_name}:generateContent",
            f"/v1beta/models/{model_name}:generateContent"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"\n测试端点: {endpoint}")
            print(f"使用模型: {model_name}")
            
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=request_data,
                    timeout=60
                )
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ 成功生成内容")
                    
                    # 显示生成的内容
                    candidates = data.get('candidates', [])
                    if candidates:
                        content = candidates[0].get('content', {})
                        parts = content.get('parts', [])
                        if parts:
                            text = parts[0].get('text', '')
                            print(f"生成的内容:\n{text}")
                    
                    return data
                else:
                    print(f"❌ 请求失败: {response.text}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
        
        return {}
    
    def test_stream_generate_content(self, model_name: str = "gemini-2.0-flash") -> None:
        """测试流式内容生成"""
        print("\n" + "=" * 50)
        print("测试流式内容生成")
        print("=" * 50)
        
        # 构建请求数据
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "写一篇800字的论文"
                        }
                    ]
                }
            ],
            "generation_config": {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 500
            }
        }
        
        endpoints = [
            f"/gemini/v1beta/models/{model_name}:streamGenerateContent",
            f"/v1beta/models/{model_name}:streamGenerateContent"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"\n测试端点: {endpoint}")
            print(f"使用模型: {model_name}")
            
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=request_data,
                    stream=True,
                    timeout=60
                )
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ 开始接收流式内容:")
                    print("-" * 30)
                    
                    full_text = ""
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  # 移除 'data: ' 前缀
                                if data_str.strip() != '[DONE]':
                                    try:
                                        data = json.loads(data_str)
                                        candidates = data.get('candidates', [])
                                        if candidates:
                                            content = candidates[0].get('content', {})
                                            parts = content.get('parts', [])
                                            if parts:
                                                text = parts[0].get('text', '')
                                                if text:
                                                    print(text, end='', flush=True)
                                                    full_text += text
                                    except json.JSONDecodeError:
                                        continue
                    
                    print("\n" + "-" * 30)
                    print(f"✅ 流式内容生成完成，总长度: {len(full_text)} 字符")
                    return
                else:
                    print(f"❌ 请求失败: {response.text}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
    
    def test_count_tokens(self, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """测试Token计数"""
        print("\n" + "=" * 50)
        print("测试Token计数")
        print("=" * 50)
        
        # 构建请求数据
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "这是一个测试文本，用于计算token数量。"
                        }
                    ]
                }
            ]
        }
        
        endpoints = [
            f"/gemini/v1beta/models/{model_name}:countTokens",
            f"/v1beta/models/{model_name}:countTokens"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"\n测试端点: {endpoint}")
            print(f"使用模型: {model_name}")
            
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=request_data,
                    timeout=30
                )
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ 成功计算Token")
                    
                    total_tokens = data.get('totalTokens', 0)
                    print(f"总Token数: {total_tokens}")
                    
                    return data
                else:
                    print(f"❌ 请求失败: {response.text}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
        
        return {}
    
    def test_with_image(self, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """测试带图片的内容生成"""
        print("\n" + "=" * 50)
        print("测试带图片的内容生成")
        print("=" * 50)
        
        # 构建包含图片的请求数据
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "请描述这张图片中的内容。"
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                            }
                        }
                    ]
                }
            ],
            "generation_config": {
                "temperature": 0.7,
                "max_output_tokens": 500
            }
        }
        
        endpoints = [
            f"/gemini/v1beta/models/{model_name}:generateContent",
            f"/v1beta/models/{model_name}:generateContent"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"\n测试端点: {endpoint}")
            print(f"使用模型: {model_name}")
            
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=request_data,
                    timeout=60
                )
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ 成功处理图片内容")
                    
                    # 显示生成的内容
                    candidates = data.get('candidates', [])
                    if candidates:
                        content = candidates[0].get('content', {})
                        parts = content.get('parts', [])
                        if parts:
                            text = parts[0].get('text', '')
                            print(f"生成的内容:\n{text}")
                    
                    return data
                else:
                    print(f"❌ 请求失败: {response.text}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {str(e)}")
        
        return {}
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Gemini API测试")
        print(f"目标服务器: {self.base_url}")
        print(f"API密钥: {'已设置' if self.api_key else '未设置'}")
        
        # 测试列表
        tests = [
            ("获取模型列表", self.test_list_models),
            ("内容生成", lambda: self.test_generate_content()),
            ("流式内容生成", lambda: self.test_stream_generate_content()),
            ("Token计数", lambda: self.test_count_tokens()),
            ("图片内容生成", lambda: self.test_with_image()),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                if result:
                    results[test_name] = "成功"
                else:
                    results[test_name] = "失败"
            except Exception as e:
                print(f"❌ 测试异常: {str(e)}")
                results[test_name] = f"异常: {str(e)}"
        
        # 显示测试结果摘要
        print("\n" + "=" * 60)
        print("测试结果摘要")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅" if result == "成功" else "❌"
            print(f"{status} {test_name}: {result}")
        
        success_count = sum(1 for result in results.values() if result == "成功")
        total_count = len(results)
        
        print(f"\n总体结果: {success_count}/{total_count} 测试通过")
        
        if success_count == total_count:
            print("🎉 所有测试都通过了！")
        else:
            print("⚠️  部分测试失败，请检查服务器配置和网络连接")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini API 测试脚本")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="API服务器的基础URL (默认: http://localhost:8000)")
    parser.add_argument("--api-key", default="sk-145253", help="API密钥 (可选)")
    parser.add_argument("--test", choices=["models", "generate", "stream", "tokens", "image", "all"], 
                       default="stream", help="指定要运行的测试 (默认: all)")
    
    args = parser.parse_args()
    
    # 创建测试器
    tester = GeminiAPITester(args.base_url, args.api_key)
    
    # 根据参数运行指定测试
    if args.test == "models":
        tester.test_list_models()
    elif args.test == "generate":
        tester.test_generate_content()
    elif args.test == "stream":
        tester.test_stream_generate_content()
    # elif args.test == "tokens":
    #     tester.test_count_tokens()
    # elif args.test == "image":
    #     tester.test_with_image()
    # elif args.test == "all":
    #     tester.run_all_tests()


if __name__ == "__main__":
    main() 