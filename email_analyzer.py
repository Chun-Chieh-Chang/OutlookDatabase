#!/usr/bin/env python3
"""
郵件 AI 分析器
使用本地 Ollama 模型進行智慧分析
"""

import json
import requests
import sqlite3
import pandas as pd
from datetime import datetime
import re
import os
import sys

# 修復 Windows 編碼問題
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class EmailAnalyzer:
    def __init__(self, config_file='ai_config.json'):
        """初始化分析器"""
        self.load_config(config_file)
        self.base_url = self.config['ollama']['url']
        self.model = self.config['ollama']['model']
        self.timeout = self.config['ollama']['timeout']
        
    def load_config(self, config_file):
        """載入設定檔"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 使用預設設定
            self.config = {
                "ollama": {
                    "url": "http://localhost:11434",
                    "model": "llama3:8b",
                    "timeout": 60
                },
                "analysis": {
                    "max_email_length": 1000,
                    "batch_size": 5,
                    "cache_results": True
                }
            }
    
    def check_ollama_connection(self):
        """檢查 Ollama 連接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
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
                return f"API 錯誤: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "請求超時，模型處理時間過長"
        except Exception as e:
            return f"連接錯誤: {str(e)}"
    
    def summarize_email(self, subject, body, sender):
        """生成郵件摘要"""
        # 簡化提示
        prompt = f"Email: {subject} by {sender}"
        system_prompt = "Summarize this email in one sentence."
        
        return self.call_ollama(prompt, system_prompt)
    
    def classify_email(self, subject, body, sender):
        """分類郵件類型"""
        # 簡化提示
        prompt = f"Email: {subject} by {sender}"
        system_prompt = "Classify this email. Respond with only one: Work, Client, Finance, HR, Tech, Marketing, Personal, or Other."
        
        result = self.call_ollama(prompt, system_prompt)
        
        # 簡化分類
        categories = {
            'work': {'id': 1, 'name': '工作相關'},
            'client': {'id': 2, 'name': '客戶溝通'}, 
            'finance': {'id': 3, 'name': '財務相關'},
            'hr': {'id': 4, 'name': '人事通知'},
            'tech': {'id': 5, 'name': '技術支援'},
            'marketing': {'id': 6, 'name': '行銷推廣'},
            'personal': {'id': 7, 'name': '個人郵件'},
            'other': {'id': 8, 'name': '其他'}
        }
        
        result_lower = result.lower()
        for key, value in categories.items():
            if key in result_lower:
                return {
                    'category_id': value['id'],
                    'category_name': value['name'],
                    'raw_result': result
                }
        
        return {
            'category_id': 8,
            'category_name': '其他',
            'raw_result': result
        }
    
    def extract_keywords(self, subject, body):
        """提取關鍵字"""
        # 簡化提示
        prompt = f"Email: {subject}"
        system_prompt = "Extract 3-5 keywords from this email. Respond with only keywords separated by commas."
        
        result = self.call_ollama(prompt, system_prompt)
        
        # 處理關鍵字
        if result and "連接錯誤" not in result and "請求超時" not in result:
            keywords = [kw.strip() for kw in result.split(',') if kw.strip()]
            return keywords[:5]  # 最多5個關鍵字
        else:
            return [result] if result else []
    
    def semantic_search(self, query, limit=10):
        """語意搜尋 - 使用 AI 理解搜尋意圖"""
        try:
            # 先進行基本關鍵字搜尋
            conn = sqlite3.connect('emails.db')
            query_sql = """
                SELECT id, subject, body, sender_name, received_time
                FROM emails
                WHERE subject LIKE ? OR body LIKE ?
                ORDER BY received_time DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query_sql, conn, params=(f'%{query}%', f'%{query}%', limit * 3))
            conn.close()
            
            if df.empty:
                return []
            
            # 使用 AI 重新評估相關性
            results = []
            for _, email in df.iterrows():
                # 準備評估提示
                prompt = f"""
搜尋查詢: "{query}"
郵件標題: "{email['subject']}"
郵件內容: "{email['body'][:200]}..."

請評估這封郵件與搜尋查詢的相關性，回應 0-10 分數 (10為最相關)
"""
                
                system_prompt = "你是專業的郵件分析師，請評估郵件與搜尋查詢的相關性。只回應數字分數 0-10。"
                
                relevance_score = self.call_ollama(prompt, system_prompt)
                
                # 解析分數
                try:
                    score = int(relevance_score.strip())
                    if score >= 6:  # 只保留相關性 6 分以上的
                        email['relevance_score'] = score
                        results.append(email)
                except:
                    continue
            
            # 按相關性排序並限制結果數量
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"語意搜尋錯誤: {e}")
            return []

    def analyze_sentiment(self, subject, body):
        """情感分析"""
        # 簡化提示
        prompt = f"Email: {subject}"
        system_prompt = "Analyze sentiment. Respond with only one: Positive, Neutral, or Negative."
        
        result = self.call_ollama(prompt, system_prompt)
        
        # 簡化情感分析
        result_lower = result.lower()
        if 'positive' in result_lower:
            return "正面"
        elif 'negative' in result_lower:
            return "負面"
        else:
            return "中性"

    def extract_wiki_entities(self, subject, body):
        """為 Wiki 提取實體與概念 (Karpathy Pattern)"""
        prompt = f"""
分析以下郵件內容，提取關鍵的「實體 (Entities)」與「概念 (Concepts)」。
實體包括：專案名稱、人物、公司、產品、技術。
概念包括：開發流程、高層級目標、重要決策。

郵件主旨: {subject}
內容摘要: {body[:1000]}

請以 JSON 格式回應：
{{
  "entities": [
    {{"name": "名稱", "type": "類型(Person/Project/Company/Tech)", "description": "簡短描述"}}
  ],
  "concepts": [
    {{"name": "概念名稱", "description": "簡短描述"}}
  ]
}}
"""
        system_prompt = "你是一個資深架構師，擅長從混亂的訊息中提取結構化知識。只回應 JSON 內容。"
        
        result = self.call_ollama(prompt, system_prompt)
        
        # 嘗試解析 JSON
        try:
            # 尋找 JSON 區塊
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                return parsed
            else:
                # If no JSON braces, try to see if it's plain text that looks like JSON
                if result.strip().startswith('{'):
                    return json.loads(result.strip())
            return {"entities": [], "concepts": []}
        except Exception as e:
            return {"entities": [], "concepts": []}
    
    def analyze_email_batch(self, email_ids):
        """批次分析郵件"""
        results = []
        
        # 連接資料庫
        conn = sqlite3.connect('emails.db')
        
        for email_id in email_ids:
            try:
                # 讀取郵件資料
                query = "SELECT subject, body, sender_name FROM emails WHERE rowid = ?"
                cursor = conn.cursor()
                cursor.execute(query, (email_id,))
                row = cursor.fetchone()
                
                if row:
                    subject, body, sender = row
                    
                    # 執行各種分析
                    analysis = {
                        'email_id': email_id,
                        'timestamp': datetime.now().isoformat(),
                        'summary': self.summarize_email(subject, body, sender),
                        'classification': self.classify_email(subject, body, sender),
                        'keywords': self.extract_keywords(subject, body),
                        'sentiment': self.analyze_sentiment(subject, body)
                    }
                    
                    results.append(analysis)
                    print(f"✅ 已分析郵件 ID: {email_id}")
                
            except Exception as e:
                print(f"❌ 分析郵件 ID {email_id} 時發生錯誤: {e}")
                continue
        
        conn.close()
        return results
    
    def save_analysis_results(self, results, output_file='email_analysis.json'):
        """儲存分析結果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✅ 分析結果已儲存到 {output_file}")
            return True
        except Exception as e:
            print(f"❌ 儲存分析結果失敗: {e}")
            return False
    
    def generate_report(self, results):
        """生成分析報告"""
        if not results:
            return "沒有分析結果可生成報告"
        
        # 統計分類
        categories = {}
        for result in results:
            cat_name = result['classification']['category_name']
            categories[cat_name] = categories.get(cat_name, 0) + 1
        
        # 統計情感
        sentiments = {'正面': 0, '中性': 0, '負面': 0}
        for result in results:
            sentiment_line = result['sentiment']
            if '情感類型：正面' in sentiment_line:
                sentiments['正面'] += 1
            elif '情感類型：負面' in sentiment_line:
                sentiments['負面'] += 1
            else:
                sentiments['中性'] += 1
        
        # 生成報告
        report = f"""
📊 郵件分析報告
生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 統計資訊
- 分析郵件數量: {len(results)}
- 最多類別: {max(categories.items(), key=lambda x: x[1])[0]} ({max(categories.values())} 封)
- 主要情感: {max(sentiments.items(), key=lambda x: x[1])[0]} ({max(sentiments.values())} 封)

📋 分類統計
"""
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            report += f"- {cat}: {count} 封\n"
        
        report += f"\n😊 情感分析\n"
        for sentiment, count in sentiments.items():
            report += f"- {sentiment}: {count} 封\n"
        
        return report

    def query_knowledge_base(self, query):
        """知識庫問答 (RAG) - 核心邏輯：檢索 Wiki (知識圖譜) + 原始郵件"""
        # 1. 檢索 Wiki 實體 (Knowledge Graph Entities)
        wiki_context = ""
        entity_dir = 'wiki/entities'
        concept_dir = 'wiki/concepts'
        
        # 尋找關鍵詞匹配的 Wiki 頁面
        matched_pages = []
        if os.path.exists(entity_dir):
            for file in os.listdir(entity_dir):
                if file.endswith('.md'):
                    # 檢查文件名或內容是否匹配 query
                    if any(word.lower() in file.lower() for word in query.split()):
                        with open(os.path.join(entity_dir, file), 'r', encoding='utf-8') as f:
                            matched_pages.append(f"Entity [{file}]:\n{f.read()}")
                            
        if os.path.exists(concept_dir):
            for file in os.listdir(concept_dir):
                if file.endswith('.md'):
                    if any(word.lower() in file.lower() for word in query.split()):
                        with open(os.path.join(concept_dir, file), 'r', encoding='utf-8') as f:
                            matched_pages.append(f"Concept [{file}]:\n{f.read()}")

        wiki_context = "\n---\n".join(matched_pages[:5])

        # 2. 檢索原始郵件 (SQLite Vector-like Search)
        conn = sqlite3.connect('emails.db')
        # 擴大檢索範圍，尋找主旨或內容中的多個關鍵詞
        search_terms = [f"%{word}%" for word in query.split() if len(word) > 1]
        if not search_terms: search_terms = [f"%{query}%"]
        
        where_clause = " OR ".join(["subject LIKE ? OR body LIKE ?" for _ in search_terms])
        params = []
        for term in search_terms: params.extend([term, term])
        
        query_sql = f"""
            SELECT subject, body, sender_name, received_time
            FROM emails
            WHERE {where_clause}
            ORDER BY received_time DESC
            LIMIT 8
        """
        db_results = pd.read_sql_query(query_sql, conn, params=params)
        conn.close()

        # 3. 組合 Context
        context = "【知識圖譜相關實體/概念】\n" + (wiki_context if wiki_context else "無直接匹配實體")
        
        context += "\n\n【原始郵件記錄檢索】\n"
        for _, row in db_results.iterrows():
            context += f"- [{row['received_time']}] {row['subject']} (來自: {row['sender_name']}): {row['body'][:400]}\n"

        # 4. 呼叫最強模型進行深度分析
        prompt = f"""
你現在正在處理一個名為「Outlook Knowledge Brain」的知識庫。
使用者提出了以下問題：
{query}

以下是從「知識圖譜 (Wiki)」與「原始郵件庫」中檢索到的相關背景資料：
{context}

任務：
1. 整合以上資訊，給出準確且具備洞察力的回答。
2. 如果資料涉及多個專案或多個時間點，請整理出清晰的脈絡。
3. 如果資料不足以回答問題，請指出缺失的部分，並建議使用者可以嘗試哪些搜尋關鍵詞。

請以繁體中文回答，語氣專業且精煉。
"""
        system_prompt = "你是一個頂尖的企業智庫分析師，擅長從碎片化的郵件資訊中提取商業邏輯。請直接給出核心答案，不要廢話。"
        
        return self.call_ollama(prompt, system_prompt)

def main():
    """主函數 - 測試 AI 分析功能"""
    print("🤖 郵件 AI 分析器測試")
    print("=" * 40)
    
    # 初始化分析器
    analyzer = EmailAnalyzer()
    
    # 檢查 Ollama 連接
    if not analyzer.check_ollama_connection():
        print("❌ 無法連接到 Ollama 服務")
        print("💡 請確保 Ollama 正在運行: http://localhost:11434")
        return
    
    print("✅ Ollama 連接正常")
    
    # 檢查資料庫
    if not os.path.exists('emails.db'):
        print("❌ 找不到郵件資料庫 emails.db")
        print("💡 請先執行 python outlook_db_builder.py")
        return
    
    # 讀取最近的郵件進行測試
    conn = sqlite3.connect('emails.db')
    query = "SELECT rowid, subject, body, sender_name FROM emails ORDER BY received_time DESC LIMIT 3"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ 資料庫中沒有郵件")
        return
    
    print(f"📧 找到 {len(df)} 封郵件，開始分析...")
    
    # 分析郵件
    email_ids = df['rowid'].tolist()
    results = analyzer.analyze_email_batch(email_ids)
    
    # 儲存結果
    analyzer.save_analysis_results(results)
    
    # 生成報告
    report = analyzer.generate_report(results)
    print("\n" + report)
    
    print("\n🎉 AI 分析測試完成！")
    print("📝 詳細結果請查看 email_analysis.json")

if __name__ == "__main__":
    main()
