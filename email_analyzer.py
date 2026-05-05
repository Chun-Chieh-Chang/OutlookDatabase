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
import time
import sys

# 修復 Windows 編碼問題
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class EmailAnalyzer:
    def __init__(self, config_file='ai_config.json'):
        """初始化分析器"""
        self.load_config(config_file)
        self.provider = self.config.get('provider', 'ollama')
        
        # Ollama Config
        self.ollama_url = self.config['ollama']['url']
        self.ollama_model = self.config['ollama']['model']
        self.ollama_timeout = self.config['ollama']['timeout']
        
        # Google Config
        self.google_api_key = self.config.get('google', {}).get('api_key', '')
        self.google_model = self.config.get('google', {}).get('model', 'gemini-1.5-flash')
        
        # Current Active Model Info
        self.model = self.google_model if self.provider == 'google' else self.ollama_model
        
    def load_config(self, config_file):
        """載入設定檔"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {
                "provider": "ollama",
                "ollama": {"url": "http://localhost:11434", "model": "llama3.2:latest", "timeout": 60},
                "google": {"api_key": "", "model": "gemini-1.5-flash"}
            }
    
    def check_ollama_connection(self):
        """檢查 AI 連接 (相容舊介面)"""
        if self.provider == 'google':
            if not self.google_api_key or "YOUR_GEMINI" in self.google_api_key:
                print("[AI] Gemini Key not set or still using placeholder")
                return False
            
            # 嘗試清單
            candidate_models = [self.google_model, "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
            
            for i, model in enumerate(candidate_models):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.google_api_key}"
                    resp = requests.post(url, json={"contents": [{"parts":[{"text":"hi"}]}]}, timeout=8)
                    if resp.status_code == 200:
                        print(f"[AI] Gemini Connected successfully using model: {model}")
                        self.google_model = model
                        return True
                    elif i == 0:
                        # 第一次失敗，嘗試列出所有可用模型
                        print(f"[AI] Model {model} not found. Fetching available models...")
                        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.google_api_key}"
                        list_resp = requests.get(list_url, timeout=8)
                        if list_resp.status_code == 200:
                            available = [m['name'].replace('models/', '') for m in list_resp.json().get('models', [])]
                            print(f"[AI] Available models for this key: {available}")
                            # 如果列表中有 Flash，嘗試用列表中的正確名稱
                            for am in available:
                                if "flash" in am.lower() or "pro" in am.lower():
                                    print(f"[AI] Trying discovered model: {am}")
                                    test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{am}:generateContent?key={self.google_api_key}"
                                    if requests.post(test_url, json={"contents": [{"parts":[{"text":"hi"}]}]}, timeout=8).status_code == 200:
                                        self.google_model = am
                                        return True
                except Exception as e:
                    if i == 0: print(f"[AI] Connection Error: {str(e)}")
                    continue
            
            print("[AI] All Gemini attempts failed.")
            return False
            
            print("[AI] All Gemini candidate models failed to connect.")
            return False
        else:
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [m['name'] for m in models]
                    return self.ollama_model in model_names or f"{self.ollama_model}:latest" in model_names
                return False
            except:
                return False
    
    def call_ollama(self, prompt, system_prompt=None):
        """AI 呼叫調度器 (相容舊介面)"""
        if self.provider == 'google':
            return self.call_gemini(prompt, system_prompt)
        
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "top_p": 0.9}
            }
            if system_prompt: payload["system"] = system_prompt
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=self.ollama_timeout)
            if response.status_code == 200:
                return response.json().get('response', '').strip() or "模型回應為空"
            return f"Ollama API 錯誤: {response.status_code}"
        except Exception as e:
            return f"Ollama 連接錯誤: {str(e)}"

    def call_gemini(self, prompt, system_prompt=None):
        """呼叫 Google Gemini API (具備自動重試機制，429加強退避)"""
        if not self.google_api_key or "YOUR_GEMINI" in self.google_api_key:
            return "錯誤: 請先在 ai_config.json 中設定 Gemini API Key"
        
        max_retries = 5
        retry_delay = 10
        
        for attempt in range(max_retries):
            try:
                model_name = self.google_model
                if not model_name.startswith('models/'):
                    model_name = f"models/{model_name}"
                
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={self.google_api_key}"
                
                full_prompt = f"{system_prompt}\n\nUser Question: {prompt}" if system_prompt else prompt
                
                payload = {
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": 0.2, "topP": 0.8, "maxOutputTokens": 4096}
                }
                
                response = requests.post(url, json=payload, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    try:
                        return result['candidates'][0]['content']['parts'][0]['text'].strip()
                    except (KeyError, IndexError):
                        return "Gemini 回傳格式異常"
                elif response.status_code in [503, 429]:
                    # 伺服器忙碌或達到限流，指數退避
                    if attempt < max_retries - 1:
                        wait = retry_delay * (attempt + 1)
                        print(f"⚠️ Gemini 限流 (HTTP {response.status_code})，等待 {wait}s 後重試 ({attempt+1}/{max_retries-1})...")
                        time.sleep(wait)
                        continue
                    return f"Gemini 伺服器目前過於繁忙，請稍後再試。 ({response.text})"
                else:
                    return f"Gemini API 錯誤: {response.status_code} - {response.text}"
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return f"Gemini 連接錯誤: {str(e)}"
        
        return "Gemini 請求失敗"
    
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
        """為 Wiki 提取實體與概念 (v2: Decision Boundaries + Aliases + Relationships)"""
        prompt = f"""你是一個資深工業知識圖譜架構師。請從以下郵件中萃取高價值實體，嚴格遵循分類規則。

═══ 分類判定規則 (Decision Boundaries) ═══
按以下優先順序判定 category（遇到第一個符合的就停止）：

1. org    → 公司/組織/法人名稱（如: ICU Medical, Mouldex, 凱益, SGS, DNV, 東林易）
2. man    → 具體的自然人姓名（如: Abbie Tai, Wesley Chang, 張仁傑）。注意：公司名不是人名！
3. project → 包含 Part Number (R1-xxxx, CIV0000xxx) 或明確的專案代號
4. method  → SOP/流程/規範/標準/作業程序（如: IQ/OQ/PQ protocol, 進料檢驗流程, M08001）
5. measure → 量測/校正/檢驗活動或標準（如: FAI測量, CMM檢測, ISO 13485）
6. material → 具體物料/樹脂/零件/半成品（如: PVC resin, Filter Base, TEGO Housing）
7. machine → 模具/設備/儀器/工具（如: 顯微鏡, CNC, 射出機, 8-cavity mold）
8. env     → 廠區/地點/實驗室/產線環境（如: 龍潭廠, 新竹工業區, Cleanroom）
9. artifact → 文件/圖面/報告/PO/報價單（如: FAI Report, GOM Report, PO#7450, 2D Drawing）
10. domain  → 技術領域/專業知識域（如: 射出成型, 醫療器材法規, 供應商管理）
11. event   → 具體事件/會議/里程碑（如: T1試模, 客訴調查, 供應商稽核）

⚠️ 絕對禁止使用 "others" 作為 category！必須從以上 11 個選一個最接近的。

═══ Lifecycle (PDCA) 判定規則 ═══
- plan  → 設計/DFM/規劃/排程/報價/評估階段
- do    → 開模/試模(T1-T5)/生產/執行/交貨階段
- check → 檢驗/FAI/驗證(IQ/OQ/PQ)/審核/稽核階段
- act   → 改善/變更/矯正/SCAR/ECR/設計變更階段

═══ Improvement (CAPA) 判定規則 ═══
- problem    → 郵件描述了一個異常/缺陷/客訴/不合格
- rootcause  → 郵件分析了問題的原因
- correction → 郵件提出了立即矯正措施
- prevention → 郵件提出了預防再發措施或系統性改善

═══ 郵件內容 ═══
主旨: {subject}
內容: {body[:3000]}

═══ 回應格式 (嚴格 JSON) ═══
{{
  "dimensions": [
    {{
      "name": "標準化實體名稱 (英文優先，如 Abbie Tai 而非 abbie)",
      "aliases": ["別名1", "別名2"],
      "category": "從上述11個類別選一個",
      "lifecycle": "plan/do/check/act",
      "improvement": "problem/rootcause/correction/prevention/none",
      "urgency": "critical/high/normal/low",
      "tags": ["標籤1", "標籤2"],
      "domain": "所屬技術領域",
      "description": "不得為空！至少一句話描述 Who/What/When/Where/Why",
      "relationships": [
        {{"target": "關聯實體名稱", "type": "belongs_to/works_on/collaborates_with/supplies_to/references/produces/validates"}}
      ]
    }}
  ]
}}

═══ 品質約束 ═══
1. description 不得為空字串，至少包含一句 5W1H 描述
2. category 禁止使用 "others"
3. relationships 至少包含 1 個關係
4. aliases 列出此實體的所有已知別名（中英文皆可）
5. lifecycle 必須判定，不要輕易填 "none"
6. 只提取有工業管理價值的實體，忽略郵件簽名檔中的電話/地址等雜訊
"""
        system_prompt = "你是資深工業知識圖譜架構師。只回應合法 JSON，不要加任何解釋文字或 markdown 格式。"
        
        result = self.call_ollama(prompt, system_prompt)
        
        try:
            # 清理可能的 markdown code fence
            cleaned = result.strip()
            if cleaned.startswith('```'):
                cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                cleaned = re.sub(r'\s*```$', '', cleaned)
            
            # 尋找 JSON 區塊
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if "dimensions" not in parsed:
                    return {"dimensions": []}
                
                # 欄位級品質防禦
                validated = []
                for dim in parsed["dimensions"]:
                    # 跳過無名稱的實體
                    if not dim.get("name", "").strip():
                        continue
                    # 強制修正 "others" → "event" (fallback)
                    if dim.get("category", "others").lower() == "others":
                        dim["category"] = "event"
                    # 空 description 防禦
                    if not dim.get("description", "").strip():
                        dim["description"] = f"(Auto) Entity extracted from: {subject}"
                    # 確保 aliases 是 list
                    if not isinstance(dim.get("aliases"), list):
                        dim["aliases"] = []
                    # 確保 relationships 是 list
                    if not isinstance(dim.get("relationships"), list):
                        dim["relationships"] = []
                    # 確保 tags 是 list
                    if not isinstance(dim.get("tags"), list):
                        dim["tags"] = []
                    # 預設值填充
                    dim.setdefault("urgency", "normal")
                    dim.setdefault("domain", "")
                    dim.setdefault("lifecycle", "do")
                    dim.setdefault("improvement", "none")
                    validated.append(dim)
                
                return {"dimensions": validated}
            return {"dimensions": []}
        except Exception as e:
            print(f"[AI] Knowledge Extraction Error: {e}")
            return {"dimensions": []}
    
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
        
        # 尋找關鍵詞匹配的 Wiki 頁面 (優化中文匹配邏輯)
        matched_pages = []
        clean_query = query.lower()
        
        def check_match(file_name, query_text):
            entity_name = file_name.replace('.md', '').lower()
            if not entity_name: return False
            # 邏輯 A: 實體名稱在提問中 (例如: 提問包含 "東林易")
            if entity_name in query_text: return True
            # 邏輯 B: 提問中的某個詞在實體名稱中
            if any(word.lower() in entity_name for word in query_text.split() if len(word) > 1): return True
            return False

        if os.path.exists(entity_dir):
            for file in os.listdir(entity_dir):
                if file.endswith('.md') and file != ".md":
                    if check_match(file, clean_query):
                        with open(os.path.join(entity_dir, file), 'r', encoding='utf-8') as f:
                            matched_pages.append(f"Entity [{file}]:\n{f.read()}")
                            
        if os.path.exists(concept_dir):
            for file in os.listdir(concept_dir):
                if file.endswith('.md') and file != ".md":
                    if check_match(file, clean_query):
                        with open(os.path.join(concept_dir, file), 'r', encoding='utf-8') as f:
                            matched_pages.append(f"Concept [{file}]:\n{f.read()}")

        # 如果匹配到的頁面太多，優先取內容最相關的
        wiki_context = "\n---\n".join(matched_pages[:10])

        # 2. 檢索原始郵件 (使用 AI 提取關鍵詞進行多重搜尋)
        conn = sqlite3.connect('emails.db')
        
        # 嘗試從提問中提取核心關鍵詞 (例如: 東林易, 品質異常, 2025)
        keywords = self.extract_keywords(query, "")
        if not keywords:
            search_terms = [f"%{query}%"]
        else:
            search_terms = [f"%{kw}%" for kw in keywords if len(kw) > 1]
            # 保留原始提問作為其中一個搜尋項
            search_terms.append(f"%{query}%")
        
        # 建立動態 SQL
        where_conditions = []
        params = []
        for term in search_terms:
            where_conditions.append("(subject LIKE ? OR body LIKE ?)")
            params.extend([term, term])
        
        where_clause = " OR ".join(where_conditions)
        
        query_sql = f"""
            SELECT subject, body, sender_name, received_time
            FROM emails
            WHERE {where_clause}
            ORDER BY received_time DESC
            LIMIT 12
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
