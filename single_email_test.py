#!/usr/bin/env python3
"""
單一郵件 AI 分析測試
"""

import sqlite3
import json
from email_analyzer import EmailAnalyzer

def test_single_email():
    """測試單一郵件分析"""
    
    # 讀取一封測試郵件
    conn = sqlite3.connect('emails.db')
    query = "SELECT rowid, subject, body, sender_name FROM emails LIMIT 1"
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("❌ 找不到郵件資料")
        return
    
    email_id, subject, body, sender = row
    
    print(f"📧 分析郵件 ID: {email_id}")
    print(f"📝 主旨: {subject}")
    print(f"👤 寄件者: {sender}")
    print(f"📄 內文: {body[:100]}...")
    print("=" * 50)
    
    # 初始化 AI 分析器
    analyzer = EmailAnalyzer()
    
    if not analyzer.check_ollama_connection():
        print("❌ 無法連接到 Ollama 服務")
        return
    
    print("🤖 開始 AI 分析...")
    
    # 執行各種分析
    try:
        print("\n1️⃣ 生成摘要...")
        summary = analyzer.summarize_email(subject, body, sender)
        print(f"📝 摘要結果:\n{summary}")
        
        print("\n2️⃣ 分類分析...")
        classification = analyzer.classify_email(subject, body, sender)
        print(f"🏷️ 分類結果: {classification}")
        
        print("\n3️⃣ 關鍵字提取...")
        keywords = analyzer.extract_keywords(subject, body)
        print(f"🔍 關鍵字: {keywords}")
        
        print("\n4️⃣ 情感分析...")
        sentiment = analyzer.analyze_sentiment(subject, body)
        print(f"😊 情感分析:\n{sentiment}")
        
        # 儲存結果
        result = {
            'email_id': email_id,
            'subject': subject,
            'sender': sender,
            'summary': summary,
            'classification': classification,
            'keywords': keywords,
            'sentiment': sentiment
        }
        
        with open('single_email_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n✅ 分析完成！結果已儲存到 single_email_analysis.json")
        
    except Exception as e:
        print(f"❌ 分析過程發生錯誤: {e}")

def main():
    print("🤖 單一郵件 AI 分析測試")
    print("=" * 40)
    
    test_single_email()

if __name__ == "__main__":
    main()
