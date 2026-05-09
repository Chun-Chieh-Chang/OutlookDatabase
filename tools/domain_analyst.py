#!/usr/bin/env python3
"""
Domain Analyst (The Teacher)
Analyzes core reference documents to bootstrap the project's ontology and glossary.
"""

import os
import json
import sys
import io
from collections import Counter
import re

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REF_DIR = 'raw/reference_docs'
GLOSSARY_FILE = 'wiki/domain_glossary.md'

def extract_text_from_files():
    """Extract text from TXT, MD, and LOG files in the reference directory."""
    all_text = ""
    if not os.path.exists(REF_DIR):
        os.makedirs(REF_DIR)
        return ""
    
    files = [f for f in os.listdir(REF_DIR) if f.endswith(('.txt', '.md', '.log'))]
    for f in files:
        with open(os.path.join(REF_DIR, f), 'r', encoding='utf-8') as file:
            all_text += file.read() + "\n"
    return all_text

def run_analysis():
    print("🎓 Domain Analyst: Bootstrapping Industrial Knowledge from Reference Docs...")
    text = extract_text_from_files()
    
    if not text:
        print(f"ℹ️  請先將您的核心文件 (TXT/MD) 放入 {REF_DIR}。")
        return

    # Simple frequency analysis for preview
    words = re.findall(r'\b\w{2,}\b', text)
    common = Counter(words).most_common(50)
    
    print(f"📊 偵測到 {len(words)} 個詞彙。高頻詞預覽: {', '.join([w[0] for w in common[:10]])}")

    # In a real scenario, we would send the full text (or a summary) to AI 
    # to create a structured glossary. Here we generate a placeholder for the user.
    
    with open(GLOSSARY_FILE, 'w', encoding='utf-8') as f:
        f.write("# 📚 領域專業詞彙表 (Domain Glossary)\n")
        f.write(f"Generated: {os.path.basename(REF_DIR)} 資料庫預分析\n\n")
        f.write("## 核心高頻詞 (Top Keywords)\n")
        for word, count in common:
            f.write(f"- **{word}**: 出現 {count} 次\n")
        
        f.write("\n## 建議建構節點 (Suggested Nodes)\n")
        f.write("> [!TIP]\n")
        f.write("> 根據初步分析，建議將上述高頻詞作為 `ontology.json` 中的核心實體。\n")

    print(f"📝 領域詞彙表已更新於: {GLOSSARY_FILE}")
    print("💡 接下來您可以將這些詞彙手動加入 schema/ontology.json 以強化 AI 的識別率。")

if __name__ == "__main__":
    run_analysis()
