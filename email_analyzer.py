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
        self.config_path = config_file
        self.refresh_config()
        
    def refresh_config(self):
        """[Hot-Reload] 動態重新載入配置，確保 UI 變更即時生效"""
        self.load_config(self.config_path)
        self.provider = self.config.get('provider', 'ollama')
        
        # Ollama Config
        self.ollama_url = self.config.get('ollama', {}).get('url', 'http://localhost:11434')
        self.ollama_model = self.config.get('ollama', {}).get('model', 'gemma4:e4b')
        self.ollama_timeout = self.config.get('ollama', {}).get('timeout') or 300
        
        # Google Config
        self.google_api_key = self.config.get('google', {}).get('api_key', '')
        self.google_model = self.config.get('google', {}).get('model', 'gemini-3-flash')
        
        # Current Active Model Info
        self.model = self.google_model if self.provider == 'google' else self.ollama_model
        print(f"  [Config Sync] Provider: {self.provider} | Model: {self.model} | Timeout: {self.ollama_timeout}s")
        
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
        """檢查 AI 連接"""
        if self.provider == 'google':
            return bool(self.google_api_key)
        try:
            # [i3 Optimization] Increased timeout to 30s for heavy model loading
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=30)
            return response.status_code == 200
        except:
            return False
    
    def call_ollama(self, prompt, system_prompt=None):
        """AI 呼叫調度器 (具備 Hot-Reload)"""
        self.refresh_config() # 每次呼叫前確保配置是最新的
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
                return response.json().get('response', '').strip()
            return f"Ollama API 錯誤: {response.status_code}"
        except Exception as e:
            return f"Ollama 連接錯誤: {str(e)}"

    def call_gemini(self, prompt, system_prompt=None):
        """呼叫 Google Gemini API"""
        if not self.google_api_key:
            return "錯誤: 未設定 Gemini API Key"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.google_model}:generateContent?key={self.google_api_key}"
        full_prompt = f"{system_prompt}\n\nUser Question: {prompt}" if system_prompt else prompt
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            return f"Gemini API 錯誤: {response.status_code}"
        except Exception as e:
            return f"Gemini 連接錯誤: {str(e)}"

    def summarize_email(self, subject, body, sender):
        prompt = f"Subject: {subject}\nBody: {body[:1000]}"
        system_prompt = "Summarize this email in one sentence."
        return self.call_ollama(prompt, system_prompt)

    def classify_email(self, subject, body, sender):
        prompt = f"Subject: {subject}"
        system_prompt = "Classify this email category (Work, Tech, Finance, HR, Client, Marketing, Personal, Other). Respond only with the category name."
        result = self.call_ollama(prompt, system_prompt).strip().lower()
        
        mapping = {
            "work": (1, "工作相關"), "client": (2, "客戶溝通"), "finance": (3, "財務相關"),
            "hr": (4, "人事通知"), "tech": (5, "技術支援"), "marketing": (6, "行銷推廣"),
            "personal": (7, "個人郵件"), "other": (8, "其他")
        }
        for k, v in mapping.items():
            if k in result: return {"category_id": v[0], "category_name": v[1], "raw_result": result}
        return {"category_id": 8, "category_name": "其他", "raw_result": result}

    def extract_keywords(self, subject, body):
        prompt = f"Subject: {subject}"
        system_prompt = "Extract 3 keywords. Respond only with keywords separated by commas."
        result = self.call_ollama(prompt, system_prompt)
        return [kw.strip() for kw in result.split(',') if kw.strip()]

    def analyze_sentiment(self, subject, body):
        prompt = f"Subject: {subject}"
        system_prompt = "Analyze sentiment (Positive, Neutral, Negative). Respond only with the category."
        result = self.call_ollama(prompt, system_prompt).lower()
        if 'positive' in result: return "正面"
        if 'negative' in result: return "負面"
        return "中性"

    def extract_entities(self, subject, body):
        """[V5.0] Antigravity Mimicry - 高保真工業分析指令"""
        prompt = f"Subject: {subject}\nBody: {body[:2000]}"
        system_prompt = """
你是 SkillsBuilder 系統的核心分析官 (Antigravity Mode)。
你的目標是執行「高顆粒度」的工業知識提取。

## 執行指令：
1. 識別實體：找出人名、物料代碼 (如 R1-xxx)、組織、關鍵流程、徵才資訊。
2. 語義分類：歸類至 [HR, QMS, Spec, Project, Recruitment, Admin] 之一。
   - 若涉及 104、人力銀行、履歷、面試，請歸類為 'Recruitment'。
3. 提取關聯：找出實體間的關係 (如 "隸屬於", "負責面試", "修正規格")。
4. 排除雜訊：過濾廣告、系統通知。

## 輸出格式：
必須回傳純 JSON 格式，包含 {"dimensions": [{"name": "...", "category": "...", "description": "...", "relationships": [{"target": "...", "type": "..."}]}]}
"""
        try:
            result = self.call_ai(prompt, system_prompt)
            if "error" not in result.lower():
                match = re.search(r'\{.*\}', result, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    if parsed.get("dimensions"):
                        return parsed
        except Exception as e:
            print(f"Extraction Error: {e}")
            pass

        # --- Phase 2: Heuristic Fallback (Regex) ---
        # 如果 AI 失敗，使用規則引擎確保系統不中斷
        print(f"  [Fallback] Using Heuristic Extraction for: {subject}")
        entities = []
        
        # 匹配 R/V/X 料號
        specs = re.findall(r'([RVX]\d{1,2}-\d{4,5}[A-Z]*)', f"{subject} {body}")
        for s in set(specs):
            entities.append({
                "name": s,
                "category": "spec",
                "description": f"技術規範/料號: {s} (由規則引擎自動提取)",
                "urgency": "normal",
                "tags": ["#automated", "#spec"]
            })
            
        # 匹配 CAPA/NCR
        capas = re.findall(r'(CAPA[-\s]\d+)', f"{subject} {body}", re.I)
        for c in set(capas):
            entities.append({
                "name": c.upper(),
                "category": "capa",
                "description": f"矯正預防措施: {c} (由規則引擎自動提取)",
                "urgency": "high",
                "tags": ["#capa", "#automated"]
            })
            
        return {"dimensions": entities}

    def is_noise_entity(self, name):
        """判斷是否為無效雜訊實體"""
        if not name or name.lower() in ['unknown', 'none', 'redacted', '未命名實體']:
            return True
        # 排除郵件地址
        if '@' in name or name.endswith(('.com', '.tw', '.net', '.org')):
            return True
        # 排除系統關鍵字
        noise_keywords = ['postmaster', 'suspicious', 'blocked', 'spam', 'notification', 'alert']
        if any(kw in name.lower() for kw in noise_keywords):
            return True
        # 排除過長標題 (可能是誤抓的主旨)
        if len(name) > 100:
            return True
        return False

    def save_wiki_entity(self, entity):
        """將提取的實體儲存為 Wiki 檔案 (v3: QC-Centric Structure)"""
        name = entity.get('name')
        if not name or name.lower() == 'unknown':
            name = entity.get('value') or entity.get('type', '未命名實體')
            
        # [PDCA] 執行雜訊過濾
        if self.is_noise_entity(name):
            return False
            
        name = name.strip().replace('/', '-').replace(':', '-')
        category = entity.get('category', 'others').lower()
        
        # Mapping to new directory structure
        wiki_root = 'wiki/dimensions'
        target_dir = os.path.join(wiki_root, category)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        file_path = os.path.join(target_dir, f"{name}.md")
        
        # Obsidian Frontmatter
        frontmatter = {
            "title": name,
            "category": category,
            "aliases": entity.get('aliases', []),
            "tags": entity.get('tags', []),
            "urgency": entity.get('urgency', 'normal'),
            "lifecycle": entity.get('lifecycle', 'none'),
            "improvement": entity.get('improvement', 'none'),
            "updated": datetime.now().strftime('%Y-%m-%d')
        }
        
        # Build Markdown content
        md_content = "---\n" + json.dumps(frontmatter, ensure_ascii=False, indent=2) + "\n---\n\n"
        md_content += f"# {name}\n\n"
        md_content += f"## 📝 技術描述\n{entity.get('description', '尚無描述')}\n\n"
        
        if entity.get('relationships'):
            md_content += "## 🔗 專業關聯\n"
            for rel in entity['relationships']:
                md_content += f"- **{rel.get('type', 'related')}**: [[{rel.get('target', 'Unknown')}]]\n"
        
        # Save file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            return True
        except Exception as e:
            print(f"Save Error: {e}")
            return False

    def get_entity_context(self, entity_name):
        """從資料庫中檢索實體的歷史上下文"""
        try:
            conn = sqlite3.connect('emails.db')
            cursor = conn.cursor()
            cursor.execute("SELECT subject, body, received_time FROM emails WHERE subject LIKE ? OR body LIKE ? ORDER BY received_time DESC LIMIT 10", (f'%{entity_name}%', f'%{entity_name}%'))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows: return ""
            
            context = f"--- 實體 [{entity_name}] 的歷史數據背景 ---\n"
            for sub, body, time in rows:
                context += f"時間: {time}\n主旨: {sub}\n摘要: {body[:300]}\n\n"
            return context
        except: return ""

    def synthesize_entity_report(self, entity_name, context):
        """呼叫 AI 對實體的歷史背景進行深度總結"""
        if not context:
            return "無法獲取足夠的歷史數據進行總結。"
            
        prompt = f"""請針對工業實體 [{entity_name}] 進行深度技術總結。
        
        以下是從 2.7 萬封郵件中檢索到的相關歷史片段：
        {context}
        
        請以「工業專家」的視角，從以下維度進行總結（使用 Markdown 格式）：
        1. **核心職責/功能**：此人或此項目在公司中的定位。
        2. **主要關聯項目/事件**：歷史郵件中頻繁出現的具體事件或項目代碼。
        3. **潛在風險或關鍵提醒**：根據郵件內容推斷出的異常、延誤或需要注意的技術細節。
        4. **因果關係與脈絡**：此實體在技術流或供應鏈中的上游與下游關係。
        
        【重要規範】：
        - 禁止使用 LaTeX 數學符號 (如 $\\rightarrow$ 或 $\\Rightarrow$)。
        - 表示流程或因果時，請直接使用純文字箭頭「→」或「=>」。
        - 回答請保持專業、精簡，且具備工業實務感。
        """
        system_prompt = "你是一位資深工業數據分析師，擅長從碎片化的溝通記錄中提取結構化洞察。"
        result = self.call_ai(prompt, system_prompt)
        
        # Post-processing: Convert LaTeX arrows to Unicode arrows
        result = result.replace('$\\rightarrow$', ' → ')
        result = result.replace('$\\Rightarrow$', ' ⇒ ')
        result = result.replace('\\rightarrow', ' → ')
        result = result.replace('\\Rightarrow', ' ⇒ ')
        
        return result

    def synthesize_wiki_page(self, existing_content, new_evidence, source_ref):
        """[Antigravity Mode] 執行高保真知識合成"""
        prompt = f"""You are the SkillsBuilder Digital Art Director & Lead Architect. 
SYNTHESIZE the existing wiki with new evidence into a PREMIUM Markdown page.

## 核心指令 (Core Instructions)：
1. 訊息顆粒化：優先使用 Markdown 表格 (Table) 呈現清單數據（如候選人、規格表）。
2. 動態重構：不要只是附加，要根據新證據重寫，確保反映最新狀態。
3. 高保真排版：使用 H1, H2, H3 建立清晰層次，並加入「工業語義關聯」區塊。
4. 關聯強化：對所有實體使用 [[Entity Name]] 語法進行雙向連結。
5. 視覺對齊：確保排版符合 Royal Blue 美學與 1.8x 行高渲染需求。

---
### 📚 既有內容 (EXISTING CONTENT)
{existing_content}

### 🔍 新證據 (NEW EVIDENCE)
Source: {source_ref}
Content: {new_evidence}

### 🚀 輸出要求：
僅輸出更新後的全量 Markdown。確保 YAML 前端 (Frontmatter) 的 `updated` 欄位為 {datetime.now().strftime('%Y-%m-%d')}。
"""
        return self.call_ollama(prompt, "You are a professional industrial knowledge synthesizer.")

    def query_knowledge_base(self, query):
        """知識庫問答 (RAG)"""
        wiki_context = ""
        matched_pages = []
        if os.path.exists('wiki'):
            for root, dirs, files in os.walk('wiki'):
                for file in files:
                    if file.endswith('.md') and any(kw.lower() in file.lower() for kw in query.split()):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            matched_pages.append(f"Entity [{file}]:\n{f.read()}")
                            if len(matched_pages) >= 5: break
                if len(matched_pages) >= 5: break
        wiki_context = "\n---\n".join(matched_pages)

        system_prompt = (
            f"你是資深工業專家智庫分析師。現在是 {datetime.now().strftime('%Y-%m-%d')}。\n"
            f"【檢索背景資料】:\n{wiki_context}\n"
            "請根據背景資料回答。如果資料不足，請建議關鍵字。"
        )
        return self.call_ai(f"Question: {query}", system_prompt)

    def call_ai(self, prompt, system_prompt=None):
        return self.call_ollama(prompt, system_prompt)

def main():
    analyzer = EmailAnalyzer()
    print("🤖 SkillsBuilder AI Analyzer Ready.")

if __name__ == "__main__":
    main()
