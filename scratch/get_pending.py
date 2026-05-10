import sqlite3
import json

conn = sqlite3.connect('emails.db')
cursor = conn.cursor()
# 抓取最新的 10 封郵件
cursor.execute("SELECT subject, sender_name, received_time, body FROM emails ORDER BY received_time DESC LIMIT 10")
emails = cursor.fetchall()
conn.close()

data = []
for e in emails:
    data.append({
        "subject": e[0],
        "sender": e[1],
        "date": e[2],
        "body": e[3]
    })

with open('scratch/pending_synthesis.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

import io
import sys

# Windows Console Defense
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ... (rest of code)
print(f"DONE: Extracted {len(data)} emails for synthesis.")
