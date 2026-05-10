import sqlite3
import json
import sys
import io

# Windows Console Defense
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('emails.db')
cursor = conn.cursor()
# 撈取前 100 封尚未在 wiki 標記為 "AI 深度合成" 的郵件 (或最新的郵件)
cursor.execute("SELECT subject, sender_name, body FROM emails ORDER BY received_time DESC LIMIT 100")
data = cursor.fetchall()
conn.close()

results = []
for subject, sender, body in data:
    # 簡單過濾廣告噪音 (我會在合成時做更深度的過濾)
    if any(k in subject.lower() for k in ['canva', '104', 'edm', '取消訂閱']):
        continue
    results.append({"subject": subject, "sender": sender, "body": body[:2000]})

with open('scratch/agent_synthesis_batch.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"DONE: Identified {len(results)} high-value industrial emails for direct synthesis.")
