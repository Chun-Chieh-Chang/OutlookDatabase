#!/usr/bin/env python3
"""
直接 AI 設定 - 繞過 Ollama CLI 問題
"""

import requests
import json
import subprocess
import time
import os

class DirectAISetup:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3:8b"
        
    def check_service(self):
        """檢查 Ollama 服務是否運行"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama_service(self):
        """嘗試啟動 Ollama 服務"""
        print("🔍 嘗試啟動 Ollama 服務...")
        
        # 嘗試常見的安裝路徑
        possible_paths = [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe",
            r"C:\Program Files\Ollama\ollama.exe",
            r"C:\Program Files (x86)\Ollama\ollama.exe"
        ]
        
        ollama_exe = None
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                ollama_exe = expanded_path
                break
        
        if not ollama_exe:
            print("❌ 找不到 Ollama.exe，請手動啟動 Ollama 應用程式")
            return False
        
        try:
            # 啟動 Ollama 服務（背景執行）
            subprocess.Popen([ollama_exe, "serve"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # 等待服務啟動
            print("⏳ 等待 Ollama 服務啟動...")
            for i in range(30):  # 最多等待30秒
                time.sleep(1)
                if self.check_service():
                    print("✅ Ollama 服務啟動成功！")
                    return True
                if i % 5 == 0:
                    print(f"⏳ 等待中... ({i+1}/30秒)")
            
            print("❌ Ollama 服務啟動超時")
            return False
            
        except Exception as e:
            print(f"❌ 啟動 Ollama 服務失敗: {e}")
            return False
    
    def pull_model(self):
        """下載模型"""
        print(f"🤖 開始下載模型: {self.model_name}")
        
        try:
            # 使用 API 下載模型
            payload = {
                "name": self.model_name
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json=payload,
                timeout=1800  # 30分鐘超時
            )
            
            if response.status_code == 200:
                print(f"✅ 模型 {self.model_name} 下載完成")
                return True
            else:
                print(f"❌ 模型下載失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 下載模型時發生錯誤: {e}")
            return False
    
    def test_model(self):
        """測試模型"""
        print(f"🧪 測試模型: {self.model_name}")
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": "請用一句話介紹你自己",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 模型測試成功")
                print(f"🤖 回應: {result.get('response', '').strip()}")
                return True
            else:
                print(f"❌ 模型測試失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 測試模型時發生錯誤: {e}")
            return False
    
    def create_config(self):
        """建立配置檔"""
        config = {
            "ollama": {
                "url": self.ollama_url,
                "model": self.model_name,
                "timeout": 30
            },
            "analysis": {
                "max_email_length": 1000,
                "batch_size": 5,
                "cache_results": True
            }
        }
        
        try:
            with open('ai_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✅ 配置檔 ai_config.json 建立成功")
            return True
        except Exception as e:
            print(f"❌ 建立配置檔失敗: {e}")
            return False
    
    def run_setup(self):
        """執行直接設定"""
        print("🚀 開始直接 AI 設定...")
        print("=" * 50)
        
        # 檢查服務
        if not self.check_service():
            print("❌ Ollama 服務未運行")
            if not self.start_ollama_service():
                print("\n💡 請手動啟動 Ollama 應用程式")
                print("💡 然後重新執行此腳本")
                return False
        
        # 下載模型
        if not self.pull_model():
            print("❌ 模型下載失敗")
            return False
        
        # 測試模型
        if not self.test_model():
            print("❌ 模型測試失敗")
            return False
        
        # 建立配置
        if not self.create_config():
            print("❌ 配置建立失敗")
            return False
        
        print("=" * 50)
        print("🎉 直接 AI 設定完成！")
        print(f"📝 模型: {self.model_name}")
        print(f"🌐 服務地址: {self.ollama_url}")
        print("⚙️  配置檔: ai_config.json")
        print("💡 現在可以使用 AI 分析功能了！")
        
        return True

def main():
    print("🤖 Outlook 郵件資料庫 - 直接 AI 設定")
    print("=" * 50)
    
    setup = DirectAISetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎯 下一步:")
        print("1. 執行 python email_analyzer.py 測試 AI 分析功能")
        print("2. 啟動網頁介面: python web_app.py")
        print("3. 在網頁介面中使用 AI 分析功能")
    else:
        print("\n❌ 設定失敗，請檢查錯誤訊息並重試")

if __name__ == "__main__":
    main()
