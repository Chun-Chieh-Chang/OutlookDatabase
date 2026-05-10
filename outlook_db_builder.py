import win32com.client
import sqlite3
import os
import pandas as pd
from datetime import datetime
import sys
import io

# [V4.0] 強制環境編碼對齊 (Windows Console Defense)
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def build_emails_db(db_path='emails.db', max_emails=500):
    print(f"🚀 [Ingestion] 正在啟動數據化入程序...")
    
    # 1. 建立資料庫連線
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            entry_id TEXT PRIMARY KEY,
            subject TEXT,
            sender_name TEXT,
            sender_email TEXT,
            received_time TEXT,
            body TEXT
        )
    ''')
    conn.commit()

    # 2. 獲取已存在的 EntryIDs
    cursor.execute("SELECT entry_id FROM emails")
    existing_ids = {row[0] for row in cursor.fetchall()}
    print(f"📦 資料庫現有郵件數: {len(existing_ids)}")

    # 3. 連結 Outlook
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6) # 6 = olFolderInbox
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True) # 降序排列 (最新在前)
    except Exception as e:
        print(f"❌ 無法存取 Outlook: {e}")
        return

    # 4. 數據提取循環
    new_count = 0
    total_to_scan = min(len(messages), max_emails)
    
    print(f"🔍 正在掃描最新的 {total_to_scan} 封郵件...")
    
    for i in range(1, total_to_scan + 1):
        try:
            msg = messages.Item(i)
            eid = msg.EntryID
            
            if eid not in existing_ids:
                subject = msg.Subject
                sender_name = msg.SenderName
                sender_email = msg.SenderEmailAddress
                received_time = msg.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S")
                body = msg.Body

                cursor.execute('''
                    INSERT INTO emails (entry_id, subject, sender_name, sender_email, received_time, body)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (eid, subject, sender_name, sender_email, received_time, body))
                
                new_count += 1
                if new_count % 50 == 0:
                    print(f"   -> 已提取 {new_count} 封新郵件...")
        except Exception:
            continue

    conn.commit()
    conn.close()
    
    print(f"✅ 數據化入完成！本次新增: {new_count} 封，總計: {len(existing_ids) + new_count} 封。")

if __name__ == "__main__":
    # 您可以調整 max_emails 來決定要掃描多少封最新的郵件
    build_emails_db(max_emails=1000)
