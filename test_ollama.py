#!/usr/bin/env python3
"""
測試 Ollama 模型
"""

import requests
import json
import time

def test_ollama():
    """測試 Ollama 模型"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3:8b",
        "prompt": "請用一句話介紹你自己",
        "stream": False
    }
    
    print("🧪 測試 Ollama 模型...")
    print(f"📝 提示: {payload['prompt']}")
    print("⏳ 等待回應...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 模型回應成功！")
            print(f"🤖 回應: {result.get('response', '').strip()}")
            return True
        else:
            print(f"❌ 錯誤狀態碼: {response.status_code}")
            print(f"📄 回應: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 請求超時，模型可能還在載入中")
        return False
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False

def main():
    print("🤖 Ollama 模型測試")
    print("=" * 30)
    
    # 檢查服務
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama 服務運行正常")
            models = response.json().get('models', [])
            llama3_found = any('llama3:8b' in model['name'] for model in models)
            if llama3_found:
                print("✅ llama3:8b 模型已安裝")
            else:
                print("❌ llama3:8b 模型未找到")
                return
        else:
            print("❌ Ollama 服務回應異常")
            return
    except:
        print("❌ 無法連接到 Ollama 服務")
        return
    
    # 測試模型（重試3次）
    for attempt in range(3):
        print(f"\n🔄 嘗試 {attempt + 1}/3")
        if test_ollama():
            print("\n🎉 模型測試成功！")
            print("💡 現在可以使用 AI 分析功能了")
            return
        else:
            if attempt < 2:
                print("⏳ 等待 10 秒後重試...")
                time.sleep(10)
    
    print("\n❌ 模型測試失敗")
    print("💡 可能的原因：")
    print("1. 模型還在載入中（首次載入需要時間）")
    print("2. 記憶體不足")
    print("3. Ollama 服務問題")

if __name__ == "__main__":
    main()
