#!/usr/bin/env python3
"""
快速 Outlook 郵件提取工具 - 專為大量郵件優化
"""

import win32com.client
import sqlite3
import datetime
import os
import time

# Configuration
DB_NAME = 'emails.db'
FOLDER_NAME = '收件匣'
ACCOUNT_NAME = 'mike.chen@mouldex.com.tw'
MAX_EMAILS = 50  # 只處理最近 50 封郵件

def init_db():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            entry_id TEXT PRIMARY KEY,
            subject TEXT,
            sender_name TEXT,
            sender_email TEXT,
            received_time TEXT,
            body TEXT,
            folder TEXT
        )
    ''')
    conn.commit()
    return conn

def get_outlook_folder(namespace, account_name, folder_name):
    """Get the specific Outlook folder from the correct account."""
    try:
        root_folder = namespace.Folders.Item(account_name)
        folder = root_folder.Folders.Item(folder_name)
        return folder
    except Exception as e:
        print(f"❌ 無法存取資料夾: {e}")
        return None

def extract_emails_fast():
    """快速提取郵件 - 優化版本"""
    print("🚀 快速 Outlook 郵件提取工具")
    print("=" * 40)
    
    start_time = time.time()
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        print(f"❌ 連接 Outlook 失敗: {e}")
        return

    inbox = get_outlook_folder(outlook, ACCOUNT_NAME, FOLDER_NAME)
    if not inbox:
        return
    
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # 最新郵件優先

    conn = init_db()
    c = conn.cursor()

    print(f"📧 找到 {len(messages)} 封郵件")
    print(f"⚡ 快速模式：只處理最近 {MAX_EMAILS} 封")
    
    count = 0
    new_count = 0
    
    for msg in messages:
        if count >= MAX_EMAILS:
            break
            
        try:
            if msg.Class == 43:  # MailItem
                entry_id = msg.EntryID
                
                # 檢查是否已存在
                c.execute("SELECT entry_id FROM emails WHERE entry_id = ?", (entry_id,))
                if c.fetchone():
                    count += 1
                    continue
                
                # 快速提取基本資訊
                subject = msg.Subject or "無主旨"
                sender_name = msg.SenderName or "未知寄件者"
                
                try:
                    sender_email = msg.SenderEmailAddress
                except:
                    sender_email = "未知信箱"
                
                received_time = msg.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S')
                
                # 只提取前 200 字元的內文
                try:
                    body = msg.Body
                    if body and len(body) > 200:
                        body = body[:200] + "..."
                    elif not body:
                        body = "無內文"
                except:
                    body = "內文讀取失敗"
                
                # 插入資料庫
                c.execute('''
                    INSERT INTO emails 
                    (entry_id, subject, sender_name, sender_email, received_time, body, folder)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (entry_id, subject, sender_name, sender_email, received_time, body, FOLDER_NAME))
                
                new_count += 1
                count += 1
                
                # 每 10 封顯示進度
                if count % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"⚡ 已處理 {count} 封，新增 {new_count} 封，耗時 {elapsed:.1f} 秒")
                
        except Exception as e:
            print(f"⚠️ 跳過郵件 {count}: {e}")
            count += 1
            continue
    
    conn.commit()
    conn.close()
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 完成！")
    print(f"📊 處理了 {count} 封郵件")
    print(f"🆕 新增了 {new_count} 封郵件")
    print(f"⏱️ 總耗時: {elapsed_time:.1f} 秒")
    print(f"🚀 平均每封: {elapsed_time/count:.2f} 秒")
    print(f"📁 資料庫位置: {os.path.abspath(DB_NAME)}")

def main():
    extract_emails_fast()

if __name__ == "__main__":
    main()
