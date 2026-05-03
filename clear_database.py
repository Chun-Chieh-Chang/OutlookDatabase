#!/usr/bin/env python3
"""
清除測試郵件資料的簡單腳本
"""

import sqlite3
import os

def clear_test_emails():
    """清除所有測試郵件資料"""
    db_path = 'emails.db'

    if not os.path.exists(db_path):
        print('❌ 資料庫不存在')
        return

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # 獲取當前郵件數量
        c.execute('SELECT COUNT(*) FROM emails')
        count_before = c.fetchone()[0]

        # 刪除所有郵件
        c.execute('DELETE FROM emails')
        deleted_count = c.rowcount

        # 重設自增 ID（如果有）
        try:
            c.execute('DELETE FROM sqlite_sequence WHERE name="emails"')
        except:
            pass  # 如果沒有 sequence 表就算了

        conn.commit()
        conn.close()

        print(f'✅ 已刪除 {deleted_count} 封測試郵件')
        print('📊 資料庫已清空，準備重新提取郵件')

    except Exception as e:
        print(f'❌ 清除資料時發生錯誤: {e}')

if __name__ == "__main__":
    clear_test_emails()
