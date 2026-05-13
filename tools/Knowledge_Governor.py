import os
import json
import sqlite3
import time
import sys

# Fix pathing
sys.path.append(os.getcwd())

from email_analyzer import EmailAnalyzer

class KnowledgeGovernor:
    def __init__(self):
        self.analyzer = EmailAnalyzer()
        self.db_path = 'emails.db'
        self.audit_report = 'wiki/Audit_Report_QC3.json'

    def bridge_gaps(self, limit=20):
        """實體化審計報告中遺失的高頻節點"""
        print(f"--- 知識治理啟動: 正在補全前 {limit} 個遺失實體 ---")
        
        if not os.path.exists(self.audit_report):
            print("❌ 找不到審計報告，請先執行審計。")
            return

        with open(self.audit_report, 'r', encoding='utf-8') as f:
            targets = json.load(f).get('missing_entities', [])[:limit]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for target in targets:
            name = target['name']
            print(f"正在處理核心料號: {name} (頻率: {target['frequency']})")
            
            # 檢索上下文
            cursor.execute("SELECT subject, body FROM emails WHERE subject LIKE ? OR body LIKE ? ORDER BY received_time DESC LIMIT 10", (f'%{name}%', f'%{name}%'))
            rows = cursor.fetchall()
            
            if not rows: continue
            
            context = "\n".join([f"{r[0]} {r[1][:300]}" for r in rows])
            
            # AI 提取
            res = self.analyzer.extract_wiki_entities(subject=f"Synthesis: {name}", body=context)
            
            for ent in res.get('dimensions', []):
                # 強化命名與分類對齊
                if name.lower() in ent['name'].lower() or ent['name'].lower() in name.lower():
                    # 強制修正工業類別
                    if name.startswith('R') or name.startswith('V') or name.startswith('X'): ent['category'] = 'spec'
                    elif name.startswith('M'): ent['category'] = 'pqc'
                    
                    self.analyzer.save_wiki_entity(ent, frequency=target['frequency'])
                    print(f"✅ {name} 已成功實體化並歸類至 {ent['category']}")
                    break
            
            time.sleep(1) # 穩定性延遲

        conn.close()
        print("--- 補全任務完成 ---")

if __name__ == "__main__":
    governor = KnowledgeGovernor()
    governor.bridge_gaps()
