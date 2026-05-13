import os
import sqlite3
import json
import re
import time
from datetime import datetime

# Import guards
import sys
sys.path.append(os.getcwd())
try:
    import tools.encoding_guard
    from email_analyzer import EmailAnalyzer
    from tools.obsidian_graph_engine import build_obsidian_graph
except:
    pass

def omni_knowledge_extraction(min_freq=5):
    # Ensure stdout is robust and writes directly to a pulse file
    def log(msg):
        try:
            print(msg, flush=True)
            with open("wiki/extraction_pulse.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        except:
            pass

    # Clear pulse file at start
    with open("wiki/extraction_pulse.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Omni-Extractor v3.1 Session Start at {datetime.now()} ---\n")
    
    log(f"Omni-Extractor v3.1: No-Limit Strategy (Min Freq: {min_freq})")
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    
    # 1. 全球實體頻率掃描 (Optimized)
    log("Performing global frequency census...")
    cursor.execute("SELECT subject, body FROM emails")
    
    entity_freq = {}
    # 匹配 R/V/X 料號與技術特徵
    pattern = re.compile(r'[RVX]\d{1,2}-\d{4,5}[A-Z]*')
    
    count = 0
    for subject, body in cursor:
        text = (subject or "") + " " + (body or "")
        matches = pattern.findall(text)
        for m in matches:
            entity_freq[m] = entity_freq.get(m, 0) + 1
        count += 1
        if count % 10000 == 0:
            log(f"Census Progress: {count} emails scanned...")

    # 過濾門檻並排序
    eligible_entities = sorted(
        [(k, v) for k, v in entity_freq.items() if v >= min_freq],
        key=lambda x: x[1], reverse=True
    )
    
    # 閃電戰策略：延後處理超巨型實體，優先產出中小型節點
    giant_entities = [e for e in eligible_entities if e[1] > 5000]
    normal_entities = [e for e in eligible_entities if e[1] <= 5000]
    
    final_queue = normal_entities + giant_entities
    total_eligible = len(final_queue)
    log(f"Identified {total_eligible} entities. (Deferred {len(giant_entities)} giants to the end).")

    analyzer = EmailAnalyzer()
    
    processed_this_session = 0
    for ent_name, freq in final_queue:
        safe_name = ent_name.replace('/', '_')
        target_path = f"wiki/dimensions/spec/{safe_name}.md"
        
        # Checkpoint: Skip if exists
        if os.path.exists(target_path):
            continue
            
        log(f"[{processed_this_session + 1}/{total_eligible}] Synthesizing: {ent_name} (Hits: {freq})")
        
        # Optimization for i3: Smaller context window for faster inference
        cursor.execute("""
            SELECT subject, body, received_time, sender_name 
            FROM emails 
            WHERE body LIKE ? OR subject LIKE ? 
            ORDER BY received_time DESC LIMIT 10
        """, (f'%{ent_name}%', f'%{ent_name}%'))
        records = cursor.fetchall()
        
        context = ""
        for s, b, t, sender in records:
            context += f"T: {t} | S: {s}\nB: {b[:250]}\n---\n"
            
        try:
            res = analyzer.extract_wiki_entities(subject=f"Tech Archive: {ent_name}", body=context)
            for dim in res.get('dimensions', []):
                # 模糊匹配確保精確性
                if ent_name.lower() in dim['name'].lower() or dim['name'].lower() in ent_name.lower():
                    dim['category'] = 'spec'
                    analyzer.save_wiki_entity(dim, frequency=freq)
                    log(f"  -> Materialized: {ent_name}")
                    
                    # 閃電戰同步：每一點進展都立即呈現
                    build_obsidian_graph()
                    log(f"  -> Sync: 3D Graph Updated for {ent_name}")
                    break
        except Exception as e:
            log(f"  -> Error: {ent_name} failed: {e}")
            # Fault Sentinel: Auto-Record for RCA
            try:
                audit_dir = "wiki/audit"
                if not os.path.exists(audit_dir): os.makedirs(audit_dir)
                with open(f"{audit_dir}/{safe_name}.err", "w", encoding="utf-8") as f:
                    f.write(f"Timestamp: {datetime.now()}\n")
                    f.write(f"Entity: {ent_name}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"Context Sample: {context[:500]}\n")
            except:
                pass
            
        processed_this_session += 1
        time.sleep(0.3)

    conn.close()
    log(f"--- Omni-Extraction Task Finished. Total new nodes: {processed_this_session} ---")

if __name__ == "__main__":
    # 執行無上限挖掘
    omni_knowledge_extraction(min_freq=5)
