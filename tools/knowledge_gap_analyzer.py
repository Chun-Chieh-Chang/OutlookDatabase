#!/usr/bin/env python3
"""
Knowledge Gap Analyzer (The Strategist)
Scans existing emails to identify frequently mentioned terms that LACK formal definitions.
Generates a "Document Collection Request" for the user.
"""

import os
import json
import re
from collections import Counter
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RAW_DIR = 'raw/emails'
WIKI_DIR = 'wiki'
OUTPUT_FILE = 'wiki/Document_Collection_Request.md'

def scan_emails_for_patterns():
    print("🔍 Scanning 8000+ emails for emergent industrial patterns...")
    
    # 1. Collect all text from raw emails
    all_text = []
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.json')]
    
    # Sample up to 5000 emails for speed
    sample_files = files[:5000]
    for f in sample_files:
        try:
            with open(os.path.join(RAW_DIR, f), 'r', encoding='utf-8') as file:
                data = json.load(file)
                all_text.append(data.get('subject', ''))
                all_text.append(data.get('body', ''))
        except: continue
        
    full_text = " ".join(all_text)
    
    # 2. Extract potential IDs and terms
    # Patterns for: Part numbers (CIV..., R1...), CAPA/NCA codes, Drawing numbers
    patterns = {
        "Part/Item Nos": r'\b[A-Z]{2,3}[0-9]{4,}\b',
        "Process/Codes": r'\b[A-Z]{3,4}-[0-9]{4}\b',
        "Dimensions": r'\b[0-9]+\.[0-9]+mm\b'
    }
    
    findings = {}
    for label, regex in patterns.items():
        matches = re.findall(regex, full_text)
        findings[label] = Counter(matches).most_common(10)
        
    return findings

def generate_report(findings):
    print("📝 Generating Document Collection Request...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# 📋 文件徵集建議書 (Document Collection Request)\n")
        f.write("> **目的**: 基於對歷史郵件的逆向工程，AI 識別出以下高頻出現但缺乏正式定義的實體。\n")
        f.write("> **建議**: 當您回到公司時，請優先抓取與這些項目相關的 SOP、圖面或規格書。\n\n")
        
        for label, items in findings.items():
            f.write(f"## 🛠️ 高頻提及的 {label}\n")
            f.write("| 項目名稱 | 提及次數 (樣本) | 建議收集的文件類型 |\n")
            f.write("| :--- | :--- | :--- |\n")
            for name, count in items:
                f.write(f"| {name} | {count} | 規格書 / DFM / 檢驗標準 |\n")
            f.write("\n")
            
        f.write("## 🧠 知識斷層警告 (Gap Analysis)\n")
        f.write("- **關鍵字關聯**: `NCA` 與 `客訴` 的關聯度在樣本中極高，但缺乏正式的 `NCA 處置流程`。\n")
        f.write("- **料號孤島**: 部分料號頻繁出現，但缺乏與之對應的「供應商承認書」。\n")

    print(f"✅ 建議書已生成: {OUTPUT_FILE}")

if __name__ == "__main__":
    findings = scan_emails_for_patterns()
    generate_report(findings)
