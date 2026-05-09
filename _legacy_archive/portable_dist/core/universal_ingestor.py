#!/usr/bin/env python3
"""
Universal Ingestor (Multi-Source Support)
Converts TXT, MD, and other text-based project data into Library Evidence.
"""

import os
import json
import uuid
from datetime import datetime

INCOMING_DIR = 'raw/incoming'
EVIDENCE_DIR = 'raw/emails' # Reuse the same evidence pool for the builder

def ensure_dirs():
    os.makedirs(INCOMING_DIR, exist_ok=True)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

def ingest_files():
    print(f"📂 Universal Ingestor: Scanning {INCOMING_DIR}...")
    ensure_dirs()
    
    files = [f for f in os.listdir(INCOMING_DIR) if f.endswith(('.txt', '.md', '.log'))]
    
    if not files:
        print("ℹ️ 沒有發現待處理的文件。請將專案資料夾、SOP 或報告放入 raw/incoming/")
        return

    count = 0
    for f in files:
        path = os.path.join(INCOMING_DIR, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Create a synthetic evidence object (compatible with our builder)
        evidence_id = f"file_{uuid.uuid4().hex[:12]}"
        evidence = {
            "entry_id": evidence_id,
            "subject": f"FILE: {f}",
            "body": content,
            "sender": "Local System",
            "received_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source_type": "file_ingestion"
        }
        
        target_path = os.path.join(EVIDENCE_DIR, f"{evidence_id}.json")
        with open(target_path, 'w', encoding='utf-8') as out:
            json.dump(evidence, out, ensure_ascii=False, indent=2)
        
        # Move processed file to a backup or archive (optional)
        # For now, just mark it as processed
        print(f"✅ 已轉換: {f} -> {evidence_id}")
        os.remove(path) # Remove from incoming to prevent double processing
        count += 1
        
    print(f"✨ 成功接入 {count} 份外部證據。現在請執行 [1] 進行知識合成。")

if __name__ == "__main__":
    ingest_files()
