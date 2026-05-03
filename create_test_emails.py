#!/usr/bin/env python3
"""
建立測試郵件資料
"""

import sqlite3
import datetime
import random

def create_test_emails():
    """建立測試郵件資料"""
    
    # 測試郵件資料
    test_emails = [
        {
            'entry_id': 'test_001',
            'subject': '專案進度會議通知',
            'sender_name': '張經理',
            'sender_email': 'zhang@company.com',
            'received_time': str(datetime.datetime.now() - datetime.timedelta(days=1)),
            'body': '各位同事好，\n\n我們將於明天下午2點召開專案進度會議，請準備相關資料。會議地點在3樓會議室A。\n\n議程：\n1. 專案現況報告\n2. 技術問題討論\n3. 下階段計畫\n\n請準時參加。\n\n張經理',
            'folder': 'Inbox'
        },
        {
            'entry_id': 'test_002', 
            'subject': '客戶回饋意見',
            'sender_name': '李小姐',
            'sender_email': 'li@client.com',
            'received_time': str(datetime.datetime.now() - datetime.timedelta(hours=6)),
            'body': '您好，\n\n關於我們上次討論的產品功能，我有一些回饋意想要分享。\n\n1. 使用者介面很直觀\n2. 回應速度可以再提升\n3. 希望增加更多自訂選項\n\n整體來說產品很不錯，期待後續更新。\n\n謝謝！\n李小姐',
            'folder': 'Inbox'
        },
        {
            'entry_id': 'test_003',
            'subject': '發票通知 #2024-0156',
            'sender_name': '財務部',
            'sender_email': 'finance@company.com', 
            'received_time': str(datetime.datetime.now() - datetime.timedelta(hours=12)),
            'body': '親愛的客戶，\n\n您的發票已經開立完成。\n\n發票號碼：2024-0156\n金額：NT$ 15,000\n到期日：2024-02-26\n\n請依時付款，如有問題請聯繫財務部。\n\n財務部',
            'folder': 'Inbox'
        },
        {
            'entry_id': 'test_004',
            'subject': '系統維護通知',
            'sender_name': 'IT部門',
            'sender_email': 'it@company.com',
            'received_time': str(datetime.datetime.now() - datetime.timedelta(days=2)),
            'body': '各位同仁，\n\n系統將於本週六凌晨1點至4點進行例行維護。\n\n維護期間以下服務將暫停：\n- 郵件系統\n- 內部OA\n- 檔案伺服器\n\n請提前做好相關準備。\n\nIT部門',
            'folder': 'Inbox'
        },
        {
            'entry_id': 'test_005',
            'subject': '生日快樂！',
            'sender_name': '王小明',
            'sender_email': 'wang@email.com',
            'received_time': str(datetime.datetime.now() - datetime.timedelta(days=3)),
            'body': '嗨！\n\n祝你生日快樂！🎂\n\n希望你在新的一歲裡一切順利，心想事成！\n\n我們找個時間一起慶祝吧！\n\n小明',
            'folder': 'Inbox'
        }
    ]
    
    # 連接資料庫
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    
    # 建立表格（如果不存在）
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
    
    # 插入測試資料
    inserted_count = 0
    for email in test_emails:
        try:
            c.execute('''
                INSERT OR REPLACE INTO emails 
                (entry_id, subject, sender_name, sender_email, received_time, body, folder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email['entry_id'],
                email['subject'],
                email['sender_name'], 
                email['sender_email'],
                email['received_time'],
                email['body'],
                email['folder']
            ))
            inserted_count += 1
        except Exception as e:
            print(f"插入郵件失敗: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 成功建立 {inserted_count} 封測試郵件")
    return inserted_count

def main():
    print("📧 建立測試郵件資料")
    print("=" * 30)
    
    count = create_test_emails()
    
    if count > 0:
        print(f"\n🎉 測試資料建立完成！")
        print(f"📊 現在可以執行: python email_analyzer.py")
        print(f"🌐 或啟動網頁介面: python web_app.py")
    else:
        print("❌ 測試資料建立失敗")

if __name__ == "__main__":
    main()
