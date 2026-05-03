#!/usr/bin/env python3
"""
本地 AI 模型安裝和設定腳本
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

class AISetup:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3:8b"  # 使用較小的模型以節省資源
        
    def check_ollama_installed(self):
        """檢查 Ollama 是否已安裝"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_ollama_cli(self):
        """檢查 Ollama CLI 是否可用"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def install_ollama_windows(self):
        """Windows 系統安裝 Ollama"""
        print("🔧 正在為 Windows 系統安裝 Ollama...")
        
        # 下載 Ollama
        ollama_url = "https://ollama.com/download/OllamaSetup.exe"
        setup_file = "OllamaSetup.exe"
        
        try:
            print(f"📥 下載 Ollama 安裝程式...")
            response = requests.get(ollama_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(setup_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r⬇️  下載進度: {percent:.1f}%", end="", flush=True)
            
            print(f"\n✅ 下載完成: {setup_file}")
            print(f"🚀 請手動執行 {setup_file} 來安裝 Ollama")
            print(f"💡 安裝完成後，請重新執行此腳本")
            
            return True
            
        except Exception as e:
            print(f"❌ 下載失敗: {e}")
            return False
    
    def pull_model(self):
        """下載 AI 模型"""
        print(f"🤖 正在下載模型: {self.model_name}")
        
        try:
            # 使用 ollama CLI 下載模型
            result = subprocess.run(['ollama', 'pull', self.model_name], 
                                  capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"✅ 模型 {self.model_name} 下載成功")
                return True
            else:
                print(f"❌ 模型下載失敗: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 模型下載超時，請檢查網路連接")
            return False
        except Exception as e:
            print(f"❌ 下載過程發生錯誤: {e}")
            return False
    
    def test_model(self):
        """測試模型是否正常運作"""
        print(f"🧪 測試模型: {self.model_name}")
        
        try:
            # 使用 ollama CLI 測試
            prompt = "請用一句話介紹你自己"
            result = subprocess.run(['ollama', 'run', self.model_name, prompt], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ 模型測試成功")
                print(f"🤖 回應: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ 模型測試失敗: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 測試過程發生錯誤: {e}")
            return False
    
    def install_python_dependencies(self):
        """安裝 Python 依賴"""
        print("📦 安裝 Python 依賴...")
        
        dependencies = [
            'requests>=2.25.0',
            'ollama>=0.1.0'
        ]
        
        for dep in dependencies:
            try:
                print(f"📥 安裝 {dep}...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {dep} 安裝成功")
                else:
                    print(f"❌ {dep} 安裝失敗: {result.stderr}")
                    return False
                    
            except Exception as e:
                print(f"❌ 安裝 {dep} 時發生錯誤: {e}")
                return False
        
        return True
    
    def create_config_file(self):
        """建立設定檔"""
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
            
            print("✅ 設定檔 ai_config.json 建立成功")
            return True
            
        except Exception as e:
            print(f"❌ 建立設定檔失敗: {e}")
            return False
    
    def run_setup(self):
        """執行完整安裝流程"""
        print("🚀 開始本地 AI 模型安裝...")
        print("=" * 50)
        
        # 檢查系統
        print("🔍 檢查系統環境...")
        
        # 檢查 Ollama CLI
        if not self.check_ollama_cli():
            print("❌ Ollama CLI 未安裝")
            
            if sys.platform == "win32":
                if not self.install_ollama_windows():
                    print("❌ Ollama 安裝失敗")
                    return False
                print("⏸️  請安裝 Ollama 後重新執行此腳本")
                return False
            else:
                print("❌ 不支援的作業系統，請手動安裝 Ollama")
                print("💡 請訪問 https://ollama.com/download")
                return False
        
        # 檢查 Ollama 服務
        if not self.check_ollama_installed():
            print("❌ Ollama 服務未運行")
            print("💡 請啟動 Ollama 應用程式")
            return False
        
        print("✅ Ollama 已安裝並運行")
        
        # 安裝 Python 依賴
        if not self.install_python_dependencies():
            print("❌ Python 依賴安裝失敗")
            return False
        
        # 下載模型
        if not self.pull_model():
            print("❌ 模型下載失敗")
            return False
        
        # 測試模型
        if not self.test_model():
            print("❌ 模型測試失敗")
            return False
        
        # 建立設定檔
        if not self.create_config_file():
            print("❌ 設定檔建立失敗")
            return False
        
        print("=" * 50)
        print("🎉 本地 AI 模型安裝完成！")
        print(f"📝 模型: {self.model_name}")
        print(f"🌐 服務地址: {self.ollama_url}")
        print("⚙️  設定檔: ai_config.json")
        print("💡 現在可以使用 AI 分析功能了！")
        
        return True

def main():
    """主函數"""
    print("🤖 Outlook 郵件資料庫 - AI 模型安裝工具")
    print("=" * 50)
    
    # 檢查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return
    
    # 執行安裝
    setup = AISetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎯 下一步:")
        print("1. 執行 python email_analyzer.py 測試 AI 分析功能")
        print("2. 啟動網頁介面: python web_app.py")
        print("3. 在網頁介面中使用 AI 分析功能")
    else:
        print("\n❌ 安裝失敗，請檢查錯誤訊息並重試")

if __name__ == "__main__":
    main()
