#!/usr/bin/env python3
"""
Outlook 郵件提取工具 - 優化版本
支援多種方案選擇，自動測試和優化體驗
"""

import win32com.client
import sqlite3
import datetime
import os
import time
import sys
import json

# 修復編碼問題
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configuration
DB_NAME = 'emails.db'
FOLDER_NAME = '收件匣'
ACCOUNT_NAME = 'mike.chen@mouldex.com.tw'

# 方案配置
PLANS = {
    '1': {
        'name': '🚀 超快速測試',
        'emails': 10,
        'body_limit': 100,
        'description': '測試連接，處理 10 封郵件',
        'estimated_time': '0.2 秒',
        'recommended': '新用戶測試'
    },
    '2': {
        'name': '⚡ 日常使用',
        'emails': 50,
        'body_limit': 200,
        'description': '處理最近 50 封郵件，適合日常搜尋',
        'estimated_time': '0.8 秒',
        'recommended': '⭐ 推薦'
    },
    '3': {
        'name': '🔄 完整更新',
        'emails': 200,
        'body_limit': 300,
        'description': '處理最近 200 封郵件，包含較多歷史',
        'estimated_time': '4-6 秒',
        'recommended': '每週更新'
    },
    '4': {
        'name': '📊 完整匯入',
        'emails': 500,
        'body_limit': 500,
        'description': '處理最近 500 封郵件，完整匯入',
        'estimated_time': '15-25 秒',
        'recommended': '首次使用'
    },
    '5': {
        'name': '🔧 自訂設定',
        'emails': None,
        'body_limit': None,
        'description': '自訂郵件數量和內文長度',
        'estimated_time': '視設定而定',
        'recommended': '進階用戶'
    }
}

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

def show_menu():
    """顯示優化的方案選擇菜單"""
    print("🎯 Outlook 郵件提取工具 v2.0")
    print("=" * 70)
    print("💡 選擇適合您的方案：")
    print()

    for key, plan in PLANS.items():
        recommended = plan.get('recommended', '')
        if recommended:
            recommended = f" [{recommended}]"
        else:
            recommended = ""

        print(f"{key}. {plan['name']}{recommended}")
        print(f"   📧 處理郵件: {plan['emails'] if plan['emails'] else '自訂'} 封")
        print(f"   📝 內文長度: {plan['body_limit'] if plan['body_limit'] else '自訂'} 字元")
        print(f"   ⏱️  預估時間: {plan['estimated_time']}")
        print(f"   💡 說明: {plan['description']}")
        print()

    print("🔄 其他選項:")
    print("6. 📊 查看資料庫統計")
    print("7. 🧹 清空資料庫")
    print("8. 🧪 測試連接")
    print("q. 退出")
    print()

def show_stats():
    """顯示資料庫統計"""
    print("� 資料庫統計")
    print("-" * 30)

    if not os.path.exists(DB_NAME):
        print("❌ 資料庫不存在")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 總郵件數
    c.execute("SELECT COUNT(*) FROM emails")
    total_emails = c.fetchone()[0]

    if total_emails == 0:
        print("� 資料庫中沒有郵件")
        conn.close()
        return

    # 最新郵件時間
    c.execute("SELECT MAX(received_time) FROM emails")
    latest_time = c.fetchone()[0]

    # 寄件者統計
    c.execute("""
        SELECT sender_name, COUNT(*) as count
        FROM emails
        GROUP BY sender_name
        ORDER BY count DESC
        LIMIT 5
    """)
    top_senders = c.fetchall()

    # 資料夾統計
    c.execute("""
        SELECT folder, COUNT(*) as count
        FROM emails
        GROUP BY folder
    """)
    folders = c.fetchall()

    print(f"📧 總郵件數: {total_emails}")
    print(f"📅 最新郵件: {latest_time}")
    print(f"📁 資料夾:")
    for folder, count in folders:
        print(f"   • {folder}: {count} 封")

    print(f"👥 主要寄件者:")
    for sender, count in top_senders[:3]:
        print(f"   • {sender}: {count} 封")

    conn.close()

def clear_database():
    """清空資料庫"""
    confirm = input("⚠️ 確定要清空資料庫嗎? 這將刪除所有郵件資料 (y/n): ")
    if confirm.lower() != 'y':
        print("❌ 已取消")
        return

    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("✅ 資料庫已清空")
    else:
        print("❌ 資料庫不存在")

def test_connection():
    """測試 Outlook 連接"""
    print("🧪 測試 Outlook 連接")
    print("-" * 30)

    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        print("✅ Outlook 連接成功")

        inbox = get_outlook_folder(outlook, ACCOUNT_NAME, FOLDER_NAME)
        if inbox:
            print(f"✅ 資料夾連接成功: {inbox.Name}")
            print(f"📧 郵件數量: {inbox.Items.Count}")

            # 顯示最近一封郵件
            if inbox.Items.Count > 0:
                latest = inbox.Items[1]
                print(f"📝 最新郵件: {latest.Subject}")
                print(f"👤 寄件者: {latest.SenderName}")
                print(f"📅 時間: {latest.ReceivedTime}")
        else:
            print("❌ 資料夾連接失敗")

    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")

def extract_emails_with_settings(email_count, body_limit):
    """使用指定設定提取郵件"""
    import outlook_db_builder
    
    # 臨時修改 outlook_db_builder 的設定
    original_max_emails = outlook_db_builder.MAX_EMAILS
    original_body_limit = getattr(outlook_db_builder, 'BODY_LIMIT', None)
    
    # 設定新的參數
    outlook_db_builder.MAX_EMAILS = email_count
    if body_limit:
        outlook_db_builder.BODY_LIMIT = body_limit
    
    try:
        # 執行提取並獲取處理統計
        processed_count, new_count = outlook_db_builder.extract_emails_with_stats()
        
        print(f"📊 提取統計:")
        print(f"   處理郵件數: {processed_count}")
        print(f"   新增郵件數: {new_count}")
        print(f"   方案設定數: {email_count}")
        
        # 返回處理的郵件數量（符合方案設定）
        return processed_count
    finally:
        # 恢復原始設定
        outlook_db_builder.MAX_EMAILS = original_max_emails
        if original_body_limit is not None:
            outlook_db_builder.BODY_LIMIT = original_body_limit
        elif hasattr(outlook_db_builder, 'BODY_LIMIT'):
            delattr(outlook_db_builder, 'BODY_LIMIT')

def extract_emails(plan_config):
    """根據方案配置提取郵件"""
    max_emails = plan_config['emails']
    body_limit = plan_config['body_limit']
    plan_name = plan_config['name']

    print(f"\n🚀 開始執行: {plan_name}")
    print(f"📧 處理郵件數量: {max_emails}")
    print(f"📝 內文長度限制: {body_limit} 字元")
    print("=" * 60)

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
    messages.Sort("[ReceivedTime]", True)

    conn = init_db()
    c = conn.cursor()

    print(f"📊 找到 {len(messages)} 封郵件")

    count = 0
    new_count = 0
    skipped_count = 0

    # 進度條寬度
    progress_width = 40

    for msg in messages:
        if count >= max_emails:
            break

        try:
            if msg.Class == 43:  # MailItem
                entry_id = msg.EntryID

                # 檢查是否已存在
                c.execute("SELECT entry_id FROM emails WHERE entry_id = ?", (entry_id,))
                if c.fetchone():
                    skipped_count += 1
                    count += 1
                    continue

                # 提取資訊
                subject = msg.Subject or "無主旨"
                sender_name = msg.SenderName or "未知寄件者"

                try:
                    sender_email = msg.SenderEmailAddress
                except:
                    sender_email = "未知信箱"

                received_time = msg.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S')

                # 提取內文（限制長度）
                try:
                    body = msg.Body
                    if body and len(body) > body_limit:
                        body = body[:body_limit] + "..."
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

                # 顯示進度
                if count % 5 == 0 or count == max_emails:
                    elapsed = time.time() - start_time
                    progress = int((count / max_emails) * progress_width)
                    bar = "█" * progress + "░" * (progress_width - progress)
                    percent = (count / max_emails) * 100

                    print(f"\r⚡ [{bar}] {percent:.1f}% ({count}/{max_emails}) | 新增: {new_count} | 跳過: {skipped_count} | {elapsed:.1f}s", end="", flush=True)

        except Exception as e:
            print(f"\n⚠️ 跳過郵件 {count}: {e}")
            count += 1
            continue

    print()  # 換行
    conn.commit()
    conn.close()

    elapsed_time = time.time() - start_time

    print(f"\n✅ 完成！")
    print(f"📊 處理了 {count} 封郵件")
    print(f"🆕 新增了 {new_count} 封郵件")
    print(f"⏭️  跳過了 {skipped_count} 封郵件（已存在）")
    print(f"⏱️  總耗時: {elapsed_time:.1f} 秒")
    print(f"🚀 平均每封: {elapsed_time/count:.3f} 秒")
    print(f"📁 資料庫位置: {os.path.abspath(DB_NAME)}")

    # 儲存執行記錄
    log_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'plan': plan_name,
        'emails_processed': count,
        'emails_added': new_count,
        'emails_skipped': skipped_count,
        'elapsed_time': elapsed_time,
        'avg_time_per_email': elapsed_time/count if count > 0 else 0
    }

    try:
        if os.path.exists('execution_log.json'):
            with open('execution_log.json', 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_data)

        with open('execution_log.json', 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"⚠️ 無法儲存執行記錄: {e}")

def main():
    """主程式"""
    print("歡迎使用 Outlook 郵件提取工具！")
    print()

    while True:
        show_menu()

        choice = input("🎯 請選擇方案 (1-8 或 q 退出): ").strip()

        if choice in ['1', '2', '3', '4']:
            plan = PLANS[choice]
            plan_config = {
                'name': plan['name'],
                'emails': plan['emails'],
                'body_limit': plan['body_limit']
            }

            # 確認執行
            confirm = input(f"\n確定執行 {plan_config['name']} 嗎? (y/n): ").strip().lower()
            if confirm == 'y':
                extract_emails(plan_config)
                break
            else:
                print("\n❌ 已取消")
                continue

        elif choice == '5':  # 自訂方案
            custom_config = get_custom_plan()
            plan_config = {
                'name': '🔧 自訂方案',
                'emails': custom_config['emails'],
                'body_limit': custom_config['body_limit']
            }

            confirm = input(f"\n確定執行自訂方案嗎? (y/n): ").strip().lower()
            if confirm == 'y':
                extract_emails(plan_config)
                break

        elif choice == '6':  # 查看統計
            show_stats()
            input("\n按 Enter 繼續...")

        elif choice == '7':  # 清空資料庫
            clear_database()
            input("\n按 Enter 繼續...")

        elif choice == '8':  # 測試連接
            test_connection()
            input("\n按 Enter 繼續...")

        elif choice.lower() in ['q', 'quit', 'exit']:
            print("👋 再見！")
            break

        else:
            print("❌ 無效選擇，請輸入 1-8 或 q 退出")
            input("\n按 Enter 繼續...")

        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
