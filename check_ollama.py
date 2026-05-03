#!/usr/bin/env python3
"""
檢查 Ollama 安裝狀態
"""

import subprocess
import requests
import sys

def check_ollama_cli():
    """檢查 Ollama CLI 是否可用"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ollama CLI 可用: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Ollama CLI 錯誤: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Ollama CLI 未找到，請確認 Ollama 已正確安裝並加入 PATH")
        return False
    except Exception as e:
        print(f"❌ 檢查 Ollama CLI 時發生錯誤: {e}")
        return False

def check_ollama_service():
    """檢查 Ollama 服務是否運行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama 服務正在運行")
            return True
        else:
            print(f"❌ Ollama 服務回應錯誤: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到 Ollama 服務，請確認服務已啟動")
        return False
    except Exception as e:
        print(f"❌ 檢查 Ollama 服務時發生錯誤: {e}")
        return False

def main():
    print("🔍 檢查 Ollama 安裝狀態")
    print("=" * 40)
    
    cli_ok = check_ollama_cli()
    service_ok = check_ollama_service()
    
    if cli_ok and service_ok:
        print("\n🎉 Ollama 安裝完成且服務正常運行！")
        print("💡 現在可以執行: python setup_ai.py 來下載模型")
    elif cli_ok and not service_ok:
        print("\n⚠️ Ollama 已安裝但服務未啟動")
        print("💡 請啟動 Ollama 應用程式")
    elif not cli_ok and service_ok:
        print("\n⚠️ Ollama 服務運行中但 CLI 不可用")
        print("💡 請檢查 PATH 環境變數設定")
    else:
        print("\n❌ Ollama 未正確安裝")
        print("💡 請重新安裝 Ollama")

if __name__ == "__main__":
    main()
