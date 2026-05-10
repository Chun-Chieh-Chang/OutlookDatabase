#!/usr/bin/env python3
"""
Obsidian-Style Graph Engine (v3)
Dynamically builds a knowledge graph by parsing [[Links]] and #Tags 
directly from Markdown files, mirroring Obsidian's emergent discovery logic.
"""

import os
import re
import json
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKI_DIR = 'wiki'
OUTPUT_FILE = 'wiki/graph_data.json'

# Color Master Palette (QC 3.0 Mapping)
COLOR_PALETTE = {
    "project": "#3B82F6",    # Royal Blue
    "capa": "#EF4444",       # Red (Quality Issues)
    "nca": "#F59E0B",        # Amber (Anomaly)
    "iqc": "#10B981",        # Emerald (Supply)
    "pqc": "#059669",        # Green (Process)
    "oqc": "#0891B2",        # Cyan (Shipment)
    "spec": "#2563EB",       # Blue (Technical Asset)
    "qms": "#8B5CF6",        # Violet (System)
    "msa": "#6366F1",        # Indigo (Metrology)
    "hr": "#F472B6",         # Pink (Human Resources)
    "unresolved": "#475569", # Slate (Gap)
    "default": "#94A3B8"     # Secondary Gray
}

def extract_metadata(content):
    """Extract YAML-like frontmatter."""
    meta = {}
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta

def build_obsidian_graph():
    print("🕸️  Obsidian Graph Engine: Scanning Library for Emergent Links...")
    
    nodes = []
    links = []
    node_set = {} # Map of title to node_id
    
    # 1. First Pass: Create nodes for all existing Markdown files
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md') and f.lower() not in ['index.md', 'log.md', 'nudge_list.md']:
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8-sig') as file:
                    content = file.read()
                    meta = extract_metadata(content)
                    
                    title = meta.get('title', f.replace('.md', ''))
                    node_id = f.replace('.md', '')
                    
                    # 優先從元數據讀取，若無則從目錄名稱判斷 (QC 3.0 Path-Aware Logic)
                    dir_name = os.path.basename(root).lower()
                    cat = (meta.get('type') or meta.get('category') or dir_name or 'default').lower()
                    
                    # 映射別名 (例如 spec -> blue)
                    if cat not in COLOR_PALETTE and dir_name in COLOR_PALETTE:
                        cat = dir_name
                        
                    node_set[title] = node_id
                    nodes.append({
                        "id": node_id,
                        "name": title,
                        "val": 10, # Base size
                        "color": COLOR_PALETTE.get(cat, COLOR_PALETTE['default']),
                        "type": cat,
                        "exists": True
                    })

    # 2. Second Pass: Parse links and tags
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md') and f.lower() not in ['index.md', 'log.md']:
                source_id = f.replace('.md', '')
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8-sig') as file:
                    content = file.read()
                    
                    # Find [[Links]]
                    found_links = re.findall(r'\[\[(.*?)\]\]', content)
                    # Find [MarkdownLinks](target)
                    found_md_links = re.findall(r'\[.*?\]\((.*?)\)', content)
                    
                    all_targets = found_links + found_md_links
                    
                    for target in all_targets:
                        # Handle potential display text [[Path|Display]]
                        target_name = target.split('|')[0].strip()
                        # Handle potential file extension/path in Markdown links
                        target_id = target_name.replace('.md', '').split('/')[-1]
                        
                        if target_id == source_id: continue # Skip self-links
                        
                        # Create link
                        links.append({"source": source_id, "target": target_id})
                        
                        # Handle Unresolved Links
                        if target_name not in node_set and target_id not in [n['id'] for n in nodes]:
                            nodes.append({
                                "id": target_id,
                                "name": target_name,
                                "val": 5,
                                "color": COLOR_PALETTE['unresolved'],
                                "type": "unresolved",
                                "exists": False
                            })
                            node_set[target_name] = target_id

    # 3. Clean up and Export
    graph = {"nodes": nodes, "links": links}
    
    # Save to Wiki directory for frontend to pick up
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        json.dump(graph, out, ensure_ascii=False, indent=2)
    
    print(f"✅ Obsidian-style graph generated with {len(nodes)} nodes and {len(links)} edges.")
    print(f"📍 File saved at: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_obsidian_graph()
