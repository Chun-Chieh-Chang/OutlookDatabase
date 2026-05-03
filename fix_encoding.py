#!/usr/bin/env python3
"""
修復編碼問題和 AI 測試
"""

import subprocess
import sys
import os
import locale

def fix_encoding():
    """修復系統編碼設定"""
    # 設定 UTF-8 編碼
    if sys.platform == "win32":
        # Windows 系統編碼修復
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        # 設定控制台編碼
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8
        except:
            pass
    
    # 設定 Python 預設編碼
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')
    
    print("✅ 編碼設定已修復")

def test_ollama_fixed():
    """修復後的 Ollama 測試"""
    import requests
    import json
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3:8b",
        "prompt": "Hello",
        "stream": False
    }
    
    print("🧪 測試 Ollama 模型（修復版）...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            if response_text:
                print("✅ 模型回應成功！")
                print(f"🤖 回應: {response_text.strip()}")
                return True
            else:
                print("❌ 模型回應為空")
                return False
        else:
            print(f"❌ 錯誤狀態碼: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False

def restart_ollama_service():
    """重新啟動 Ollama 服務"""
    print("🔄 重新啟動 Ollama 服務...")
    
    try:
        # 終止現有 Ollama 程序
        subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                      capture_output=True, text=True, encoding='utf-8')
        
        # 等待 3 秒
        import time
        time.sleep(3)
        
        # 重新啟動 Ollama
        # 嘗試找到 Ollama.exe
        possible_paths = [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Program Files\Ollama\ollama.exe"
        ]
        
        ollama_exe = None
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                ollama_exe = expanded_path
                break
        
        if ollama_exe:
            # 背景啟動 Ollama
            subprocess.Popen([ollama_exe, "serve"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            print("⏳ 等待 Ollama 服務啟動...")
            for i in range(15):  # 等待 15 秒
                time.sleep(1)
                if test_ollama_fixed():
                    print("✅ Ollama 服務重新啟動成功！")
                    return True
                if i % 3 == 0:
                    print(f"⏳ 等待中... ({i+1}/15秒)")
            
            print("❌ Ollama 服務啟動超時")
            return False
        else:
            print("❌ 找不到 Ollama.exe")
            return False
            
    except Exception as e:
        print(f"❌ 重新啟動失敗: {e}")
        return False

def main():
    print("🔧 修復編碼問題和 AI 測試")
    print("=" * 40)
    
    # 修復編碼
    fix_encoding()
    
    # 測試 Ollama
    if test_ollama_fixed():
        print("\n🎉 AI 服務正常！")
        print("💡 現在可以使用 AI 分析功能了")
    else:
        print("\n🔄 嘗試重新啟動 Ollama 服務...")
        if restart_ollama_service():
            print("✅ 修復完成！")
        else:
            print("❌ 修復失敗，請手動重新啟動 Ollama 應用程式")

if __name__ == "__main__":
    main()
