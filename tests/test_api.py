#!/usr/bin/env python3
"""测试图片上传 API"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查端点"""
    print("=" * 50)
    print("测试 1: 健康检查")
    print("=" * 50)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_image_upload():
    """测试图片上传端点"""
    print("\n" + "=" * 50)
    print("测试 2: 图片上传 API")
    print("=" * 50)
    
    # 创建一个简单的测试图片（1x1 像素的 PNG）
    import base64
    # 最小的有效 PNG 文件
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    
    # 保存测试图片
    with open("/tmp/test_image.png", "wb") as f:
        f.write(png_data)
    
    try:
        # 使用正确的 multipart/form-data 格式
        files = {"files": ("test_image.png", open("/tmp/test_image.png", "rb"), "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/agent/extract/image",
            files=files,
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        try:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"响应文本: {response.text[:1000]}")
        return response.status_code, response.json() if response.headers.get('content-type', '').startswith('application/json') else None
    except Exception as e:
        print(f"错误: {e}")
        return None, None

def test_config_status():
    """测试配置状态端点"""
    print("\n" + "=" * 50)
    print("测试 3: 配置状态检查")
    print("=" * 50)
    try:
        response = requests.get(f"{BASE_URL}/api/agent/config", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json()
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_config_test():
    """测试配置有效性"""
    print("\n" + "=" * 50)
    print("测试 4: 配置有效性测试")
    print("=" * 50)
    try:
        response = requests.post(f"{BASE_URL}/api/agent/config/test", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.json()
    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    print("开始测试图片上传功能...")
    print(f"目标 URL: {BASE_URL}")
    
    # 测试健康检查
    health_ok = test_health()
    
    # 测试配置状态
    config_status = test_config_status()
    
    # 测试配置有效性
    config_test = test_config_test()
    
    # 测试图片上传
    upload_status, upload_response = test_image_upload()
    
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"图片上传状态码: {upload_status}")
    if config_status and config_status.get('data'):
        data = config_status.get('data', {})
        print(f"LLM API Key: {data.get('llm', {}).get('api_key', '未知')[:20]}...")
        print(f"Vision API Key: {data.get('vision', {}).get('api_key', '未知')[:20]}...")
    if config_test:
        print(f"配置测试: {config_test.get('message', '未知')}")
    if upload_response:
        print(f"上传结果: {upload_response.get('message', '未知')}")
        print(f"上传成功: {upload_response.get('success', False)}")
