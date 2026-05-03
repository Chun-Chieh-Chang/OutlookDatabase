#!/usr/bin/env python3
"""
Outlook 連接測試工具
"""

import win32com.client
import pythoncom
from datetime import datetime

def test_outlook_connection():
    """測試 Outlook 連接"""
    print("🔍 測試 Outlook 連接...")
    print("=" * 40)
    
    try:
        # 初始化 COM
        pythoncom.CoInitialize()
        
        # 連接到 Outlook
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        
        # 獲取收件匣
        inbox = outlook.GetDefaultFolder(6)  # 6 = 收件匣
        
        print(f"✅ 成功連接到 Outlook")
        print(f"📧 收件匣名稱: {inbox.Name}")
        print(f"📊 郵件數量: {inbox.Items.Count}")
        
        # 顯示最近幾封郵件
        print("\n📋 最近郵件:")
        for i in range(min(5, inbox.Items.Count)):
            item = inbox.Items[i+1]  # Outlook 是反向排序
            subject = item.Subject
            sender = item.SenderName if hasattr(item, 'SenderName') else '未知'
            received = item.ReceivedTime if hasattr(item, 'ReceivedTime') else '未知'
            
            print(f"{i+1}. 📝 {subject}")
            print(f"   👤 {sender}")
            print(f"   📅 {received}")
            print()
        
        # 檢查其他資料夾
        print("📁 其他資料夾:")
        folders = outlook.Folders
        for folder in folders:
            try:
                if folder.Name != "Mailbox":
                    print(f"  📂 {folder.Name}: {folder.Items.Count} 封郵件")
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        print("\n💡 可能的原因:")
        print("1. Outlook 沒有安裝")
        print("2. Outlook 沒有開啟")
        print("3. Outlook 設定問題")
        print("4. 權限不足")
        return False
    
    finally:
        # 清理 COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def get_all_folders():
    """獲取所有 Outlook 資料夾"""
    print("\n📁 獲取所有資料夾...")
    
    try:
        pythoncom.CoInitialize()
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        
        # 獲取根資料夾
        root_folder = outlook.Folders.Item(1)
        
        def list_folders(folder, level=0):
            indent = "  " * level
            try:
                print(f"{indent}📂 {folder.Name} ({folder.Items.Count} 封郵件)")
                
                # 遞迴列出子資料夾
                for subfolder in folder.Folders:
                    list_folders(subfolder, level + 1)
            except:
                pass
        
        list_folders(root_folder)
        
    except Exception as e:
        print(f"❌ 獲取資料夾失敗: {e}")
    
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def main():
    print("🔌 Outlook 連接診斷工具")
    print("=" * 40)
    
    # 測試基本連接
    if test_outlook_connection():
        # 獲取所有資料夾
        get_all_folders()
        
        print("\n✅ Outlook 連接成功！")
        print("💡 現在可以使用 outlook_db_builder.py 提取郵件")
    else:
        print("\n❌ Outlook 連接失敗")
        print("💡 請檢查:")
        print("1. Outlook 是否已安裝")
        print("2. Outlook 是否正在運行")
        print("3. 是否有正確的郵件帳號設定")

if __name__ == "__main__":
    main()
