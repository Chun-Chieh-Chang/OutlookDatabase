#!/usr/bin/env python3
"""
簡化 AI 測試 - 修復超時問題
"""

import requests
import json
import sqlite3
import sys
import os

# 修復 Windows 編碼問題
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class SimpleAIAnalyzer:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3:8b"
        self.timeout = 120  # 增加到 2 分鐘
    
    def call_ollama(self, prompt, system_prompt=None):
        """呼叫 Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 降低隨機性
                    "top_p": 0.9,
                    "max_tokens": 100   # 限制回應長度
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            print(f"📝 發送提示: {prompt[:50]}...")
            print("⏳ 等待 AI 回應...")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                if response_text:
                    return response_text.strip()
                else:
                    return "模型回應為空"
            else:
                return f"API 錯誤: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "請求超時，模型處理時間過長"
        except Exception as e:
            return f"連接錯誤: {str(e)}"
    
    def analyze_email_simple(self, subject, body, sender):
        """簡化郵件分析"""
        # 大幅簡化提示
        prompt = f"Email: {subject} by {sender}"
        
        system_prompt = "You are an email classifier. Respond with only one category: Work, Client, Finance, HR, Tech, Marketing, Personal, or Other."
        
        result = self.call_ollama(prompt, system_prompt)
        
        # 簡化分類
        categories = {
            'work': '工作相關',
            'client': '客戶溝通', 
            'finance': '財務相關',
            'hr': '人事通知',
            'tech': '技術支援',
            'marketing': '行銷推廣',
            'personal': '個人郵件',
            'other': '其他'
        }
        
        result_lower = result.lower()
        for key, value in categories.items():
            if key in result_lower:
                return value
        
        return '其他'
    
    def test_with_database(self):
        """使用資料庫測試"""
        print("🤖 簡化 AI 分析測試")
        print("=" * 40)
        
        # 檢查服務
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                print("❌ Ollama 服務未運行")
                return
        except:
            print("❌ 無法連接到 Ollama 服務")
            return
        
        print("✅ Ollama 服務正常")
        
        # 讀取郵件
        conn = sqlite3.connect('emails.db')
        query = "SELECT rowid, subject, body, sender_name FROM emails LIMIT 3"
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("❌ 找不到郵件資料")
            return
        
        print(f"📧 找到 {len(rows)} 封郵件")
        
        results = []
        for i, (email_id, subject, body, sender) in enumerate(rows, 1):
            print(f"\n{i}. 分析郵件 ID: {email_id}")
            print(f"📝 主旨: {subject}")
            print(f"👤 寄件者: {sender}")
            
            # 簡化分析
            category = self.analyze_email_simple(subject, body, sender)
            
            result = {
                'email_id': email_id,
                'subject': subject,
                'sender': sender,
                'category': category
            }
            
            results.append(result)
            print(f"🏷️ 分類: {category}")
        
        # 儲存結果
        with open('simple_ai_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 分析完成！結果已儲存到 simple_ai_results.json")
        
        # 統計
        categories = {}
        for result in results:
            cat = result['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 分類統計:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} 封")

def main():
    analyzer = SimpleAIAnalyzer()
    analyzer.test_with_database()

if __name__ == "__main__":
    main()
