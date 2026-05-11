import sqlite3
import os
import re
from datetime import datetime

RAW_ROOT = "raw"

def export_to_raw():
    print(f"STARTING: Raw Data Exporter...")
    
    if not os.path.exists(RAW_ROOT):
        os.makedirs(RAW_ROOT)

    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute("SELECT entry_id, subject, sender_name, received_time, body FROM emails")
    
    count = 0
    for eid, sub, sender, time_str, body in c:
        try:
            # Parse time for directory structure
            try:
                dt = datetime.strptime(time_str[:10], '%Y-%m-%d')
                year, month, day = str(dt.year), f"{dt.month:02d}", f"{dt.day:02d}"
            except:
                year, month, day = "Unknown", "Unknown", "Unknown"
            
            target_dir = os.path.join(RAW_ROOT, year, month, day)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            file_path = os.path.join(target_dir, f"{eid}.txt")
            
            # Incremental Check
            if os.path.exists(file_path):
                continue
                
            # Write Content
            content = f"ID: {eid}\nSubject: {sub}\nFrom: {sender}\nDate: {time_str}\n\n---\n\n{body}"
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            
            count += 1
            if count % 1000 == 0:
                print(f"  [Progress] Processed {count} physical files...")
                
        except Exception as e:
            continue

    conn.close()
    print(f"SUCCESS: Raw export complete. {count} new files created.")

if __name__ == "__main__":
    export_to_raw()
