#!/usr/bin/env python3
"""
SkillsBuilder Portable Bootstrap
Dynamically configures the Library environment for any project directory.
"""

import os
import sys
import subprocess
import io

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_banner():
    print("="*60)
    print("   SkillsBuilder AI - Industrial Knowledge Library (Portable)")
    print("   Pattern: Karpathy Library + Hermes Evolution v2.0")
    print("="*60)

def main_menu():
    print("\n[功能選單]")
    print("1. 🚀 啟動同步與知識合成 (Ingestion & Synthesis)")
    print("2. 📊 生成全域洞察報告 (Knowledge Products)")
    print("3. 🧠 執行自進化質量審計 (Hermes Nudging)")
    print("4. 🛠️  初始化此目錄為圖書館架構 (Init Structure)")
    print("5. 📂 接入外部文件資料 (Universal Ingestor)")
    print("6. 🎓 執行領域知識預習 (Domain Analyst)")
    print("Q. 退出")
    
    choice = input("\n請選擇操作: ").strip().lower()
    return choice

def run_script(script_name, args=[]):
    script_path = os.path.join('core', script_name)
    if not os.path.exists(script_path):
        print(f"❌ 錯誤: 找不到核心組件 {script_name}")
        return
    
    cmd = [sys.executable, script_path] + args
    print(f"正在執行: {' '.join(cmd)}...")
    subprocess.run(cmd)

if __name__ == "__main__":
    print_banner()
    
    while True:
        choice = main_menu()
        if choice == '1':
            limit = input("請輸入掃描上限 (預設 20): ").strip() or "20"
            run_script('wiki_builder.py', [limit])
        elif choice == '2':
            run_script('wiki_master_builder.py')
        elif choice == '3':
            run_script('hermes_nudge.py')
        elif choice == '4':
            os.makedirs('wiki', exist_ok=True)
            os.makedirs('raw/emails', exist_ok=True)
            os.makedirs('raw/incoming', exist_ok=True)
            print("✅ 已完成目錄初始化。")
        elif choice == '5':
            run_script('universal_ingestor.py')
        elif choice == '6':
            run_script('domain_analyst.py')
        elif choice == 'q':
            print("👋 再見！")
            break
        else:
            print("⚠️ 無效的選擇。")
